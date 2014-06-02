#!/usr/bin/env python
# -*- coding: utf-8
# -*- test-case-name: tests/test_server.py -*-

"""
server - All of the resources needed to run the file server
"""
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.server import NOT_DONE_YET
from twisted.python import log
from twisted.internet.defer import Deferred
from twisted.internet import threads

import json
import uuid

import backend.filerequest as filerequest


class Transfer(object):

    def __init__(self, transferId, filePath, userIp):
        self.transferId = transferId
        self.filePath = filePath
        self.userIp = userIp

    def toJson(self, root):
        uri = root + '/' + self.transferId
        return json.dumps({'url': uri.encode('utf-8'),
                           'transferId': self.transferId,
                           'path': self.filePath,
                           'userIp': self.userIp})


class OutboundRequests(object):

    def __init__(self):
        self._items = {}

    def add(self, url, transfer):
        self._items[url] = transfer

    def remove(self, url):
        del self._items[url]

    def get(self, url):
        return self._items.get(url)

    def listAll(self, root):
        """
        Return a list of machine readable urls.
        """
        combos = []
        for key, val in self._items.iteritems():
            combos.append(val.toJson(root))
        return combos


class MissingArgsError(Exception):
    pass


class FileServerResource(Resource):

    isLeaf = False

    def __init__(self, hosting, ip, getFilenames, submitFileRequest):
        Resource.__init__(self)
        self.hosting = hosting
        self.ip = ip
        self._getFilenames = getFilenames
        self._submitFileRequest = submitFileRequest

    def _addRequest(self, transfer):
        """
        Adds a new file resource for other users to access.
        """
        self.hosting.add(transfer.transferId, transfer)
        Resource.putChild(self, transfer.transferId, File(transfer.filePath))

    def _removeFile(self, url):
        """
        Remove the file being served at the `urlName`
        """
        self.hosting.remove(url)
        self.delEntity(url)

    def render_DELETE(self, request):
        """
        Removes a File resource that is currently being hosted.
        """
        url = request.args['url'][0]
        # XXX error check!
        self._removeFile(url)
        # XXX return an HTTP response code!
        request.setHeader("content-type", "application/json")
        return json.dumps({'status': 'removed url'})

    def render_GET(self, request):
        """
        Display the files currently being hosted.
        """
        request.setHeader("content-type", "application/json")
        url = request.URLPath().__str__()
        return json.dumps({'files': self.hosting.listAll(url)})

    def render_POST(self, request):
        """
        Initiate a file transfer to another user. This means, notify the other
        user that you are ready to transfer the file AND set that file up
        at a location that the client can find.
        """
        def parsePostData(request):
            log.msg('parsing request', request)
            files = request.args.get('filepath')
            target = request.args.get('user')
            if files is None or target is None:
                raise MissingArgsError()
            location = str(uuid.uuid4())
            transfer = Transfer(location, files[0], target[0])
            self._addRequest(transfer)
            return transfer

        def handleParseError(failure):
            failure.trap(MissingArgsError)
            msg = {'url': None,
                   'errors':'Error parsing url or target user'}
            request.write(json.dumps(msg))
            request.finish()
            return failure

        def processFilenames(transfer):
            d = threads.deferToThread(self._getFilenames, transfer.filePath)
            def returnArgs(filenames):
                return (filenames, transfer)
            d.addCallback(returnArgs)
            return d

        def createRequest(url, filenames):
            return json.dumps({'url': url,
                               'filenames': filenames})

        def requestTransfer(args):
            filenames, transfer = args
            userUrl = 'http://' + transfer.userIp + '/requests'
            data = createRequest(transfer.transferId, filenames)
            self._submitFileRequest(userUrl, data)
            return transfer

        def finish(transfer):
            url = request.URLPath().__str__()
            transfer = self.hosting.get(transfer.transferId)
            request.write(transfer.toJson(url))
            request.finish()

        def doNothing(failure):
            return failure

        def finalTrap(failure):
            failure.trap(MissingArgsError)

        d = Deferred()
        request.setHeader("content-type", "application/json")
        d.callback(request)
        d.addCallback(parsePostData)
        d.addCallbacks(processFilenames, handleParseError)
        d.addCallbacks(requestTransfer, doNothing)
        d.addCallbacks(finish, finalTrap)
        return NOT_DONE_YET


class FileRequestResource(Resource):
    """
    FileRequestResource fields requests for file transfers.

    Expose a simple endpoint where other users can post transfer requests.

    The resource accepts POSTed json data messages containing file location
    information.
    """
    isLeaf = True

    def __init__(self, transferRequests, downloadTo):
        Resource.__init__(self)
        self.transferRequests = transferRequests
        self.downloadTo = downloadTo

    def _parseForm(self, request):
        """
        Try parsing the request, if it fails, tell the requestor.
        """
        d = Deferred()
        d.addCallback(filerequest.parseFileRequest)

        def successfulParse(data):
            """ pass the request on if it parses """
            self.transferRequests.append(data)
            request.write("ok")
            request.finish()

        def parseFailure(failure):
            """ trap failures """
            request.write("error parsing request")
            request.finish()
        d.addCallbacks(successfulParse, parseFailure)
        d.callback((request.args, self.downloadTo,))

    def render_GET(self, request):
        """
        Shows all of the requests currently on the server.
        """
        # if request is local, show local file requests, otherwise, show a
        # message
        request.setHeader("content-type", "text/plain")
        return "Hi, welcome to teiler - here are the file requests."

    def render_POST(self, request):
        """
        respond to post requests. This is where the file sender processing
        will begin.

        File locations will be posted to this URL for the recipient to
        download later.
        """
        d = Deferred()
        d.addCallback(self._parseForm)
        d.callback(request)
        return NOT_DONE_YET


class UsersResource(Resource):
    """
    This resource exposes an endpoint that provides information
    about other users in the system. Basically, an HTTP endpoint for the
    PeerList.
    """
    isLeaf = True

    def __init__(self, peers):
        Resource.__init__(self)
        self.peers = peers

    def render_GET(self, request):
        """
        Return all of the users currently registered.
        """
        request.setHeader("content-type", "application/json")
        them = {"users": [x.serialize() for x in self.peers.all()]}
        return json.dumps(them)
