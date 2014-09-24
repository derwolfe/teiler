"""
server - All of the resources needed to run the file server
"""
from twisted.web.resource import NoResource
from twisted.web.static import File
from twisted.python import log, filepath
from twisted.internet.defer import Deferred
from twisted.internet import threads

from klein import Klein

import json
import uuid


__all__ = ('Transfer', 'OutboundRequests', 'UsersEndpoint',
           'FileEndpoint', 'OutboundRequestEndpoint',
           'InboundRequestEndpoint')


class Transfer(object):
    """
    A transfer is an outbound request for a file transfer.
    """
    def __init__(self, transferId, filepath, userIp):
        if isinstance(transferId, unicode):
            self.transferId = transferId
        else:
            self.transferId = unicode(transferId, 'utf-8')
        if isinstance(filepath, unicode):
            self.filepath = filepath
        else:
            self.filepath = unicode(filepath, 'utf-8')
        if isinstance(userIp, unicode):
            self.userIp = userIp
        else:
            self.userIp = unicode(userIp, 'utf-8')

    def filenameBytes(self):
        """
        return the filename as bytes.
        """
        return self.filepath.encode('utf-8', 'ignore')

    def url(self, root):
        words = root + '/' + self.transferId + '/'
        return words.encode('utf-8', 'ignore')

    # XXX bad name?
    def encode(self, root):
        return {'url': self.url(root),
                'transferId': self.transferId.encode('utf-8'),
                'filepath': self.filepath.encode('utf-8'),
                'userIp': self.userIp.encode('utf-8')}

    def toJson(self, root):
        """
        Serialize the transfer as json data
        """
        return json.dumps(self.encode(root))


class OutboundRequests(object):
    """
    Manages all of the outbound requests (transfers).
    """
    def __init__(self, items=dict()):
        self._items = items

    def add(self, transfer):
        """
        Add a new transfer at the specified url.
        """
        self._items[transfer.transferId] = transfer

    def remove(self, url):
        """
        Remove a transfer being hosted at the provided url.
        """
        if url in self._items:
            del self._items[url]
            return True
        return False

    def get(self, url):
        """
        Get the tranfer object at the given url.
        If none is present, this returns None.
        """
        return self._items.get(url)

    def all(self):
        """
        Return all of the outbound request objects as a list.
        """
        return self._items.values()


class FileEndpoint(object):

    app = Klein()

    def __init__(self, outboundRequests):
        self._outboundRequests = outboundRequests

    @app.route('/<string:transferId>/', methods=['GET'], branch=True)
    def getFile(self, request, transferId):
        """
        Get the file objects located at transfer id.
        """
        transfer = self._outboundRequests.get(transferId)

        if transfer is None:
            return NoResource()

        path = filepath.FilePath(transfer.filenameBytes())
        if path.isdir():
            return File(path.dirname())

        else:  # path.isfile():
            # XXX serving the parent directory, instead of the file itself
            # You SHOULD only serve the file that you want to share.
            # the following serves the directory where the
            # file is found and *not* the single file.
            # This will need to be changed!
            return File(path.dirname())


class UsersEndpoint(object):
    """
    HTTP interface for the peerlist.
    """
    app = Klein()

    def __init__(self, peers):
        """
        :ivar peers: an instance of `teiler.peerdiscover.PeerList`
        """
        self._peers = peers

    @app.route('/', methods=['GET'])
    def getAllPeers(self, request):
        """
        Get all of the peers in the system peer list.
        """
        request.setHeader("Content-Type", "application/json")
        them = {"users": [p.serialize() for p in self._peers.all()]}
        return json.dumps(them)


class MissingFormDataError(Exception):
    """
    Exception to be raised when a form/request does not contain
    necessary data.
    """
    pass


class OutboundRequestEndpoint(object):
    """
    The internal HTTP api for outbound file requests.
    """
    app = Klein()

    def __init__(self,
                 outboundRequests,
                 getFileNames,
                 submitFileRequest,
                 rootUrl):
        self._outboundRequests = outboundRequests
        self._getFileNames = getFileNames
        self._submitFileRequest = submitFileRequest
        self._rootUrl = rootUrl

    @app.route('/', methods=['GET'])
    def getFiles(self, request):
        """
        Display the files currently being hosted.
        """
        request.setHeader("Content-Type", "application/json")
        return json.dumps(
            {'files': [
                t.encode(self._rootUrl) for t in self._outboundRequests.all()
            ]}
        )

    def parse(self, body):
        """
        Parse incoming post data into a new `Transfer`
        """
        loaded = json.loads(body.read())
        log.msg("parsing request", json.dumps(loaded)[:100])
        # what if the args are not present in the data?
        filepath = loaded.get('filepath')
        user = loaded.get('user')
        if filepath is None or user is None:
            raise MissingFormDataError()
        transfer = Transfer(str(uuid.uuid4()), filepath, user)
        return transfer

    def addOutbound(self, transfer):
        """
        Add a transfer to the outboundRequests object.
        """
        log.msg('adding outbound request', transfer)
        self._outboundRequests.add(transfer)
        return transfer

    def getFilenames(self, transfer):
        """
        get the filenames that the transfer contains.
        """
        log.msg("getting file names")
        d = threads.deferToThread(self._getFileNames, transfer.filepath)
        d.addCallback(lambda filenames: (filenames, transfer))
        return d

    def requestTransfer(self, args):
        """
        send the transfer request and file names to the recipient named
        in the transfer.
        """
        log.msg('requesting transfer')
        filenames, transfer = args
        userUrl = 'http://{0}/requests'.format(transfer.userIp).encode('utf-8')
        requestBody = json.dumps({'transfer': transfer.url(self._rootUrl),
                                  'filenames': filenames})
        self._submitFileRequest(userUrl, requestBody)
        return requestBody

    @app.route('/', methods=['POST'])
    def newTransfer(self, request):
        """
        Initiate a file transfer to another user.

        1. Notify user that you are ready to transfer the file
        2. Add the path to the outbound_transfers object.
        """
        request.setHeader(b"Content-Type", b"application/json")
        deferred = Deferred()
        deferred.callback(request)
        deferred.addCallback(lambda request: request.content)
        deferred.addCallback(self.parse)
        deferred.addCallback(self.addOutbound)
        deferred.addCallback(self.getFilenames)
        deferred.addCallback(self.requestTransfer)
        # several errors could occur
        # 1. parsing request
        # 2. unable to contact peer
        # 3. getting filenames
        return deferred


class InboundRequestEndpoint(object):
    """
    Other users that would like to send files use this endpoint.
    New file requests are posted here.
    """

    app = Klein()

    def __init__(self, inboundRequests, downloadTo, fileRequestParser):
        self._inboundRequests = inboundRequests
        self._downloadTo = downloadTo
        self._fileRequestParser = fileRequestParser

    @app.route('/', methods=['POST'])
    def parseTransferRequest(self, request):

        def successfulParse(data):
            self._inboundRequests.append(data)
            return json.dumps({'error': None, 'status': 'ok'})

        def parseFailure(fail):
            log.msg(fail)
            return json.dumps({'error': 'error parsing request',
                               'status': 'error'})

        deferred = Deferred()
        deferred.addCallback(self._fileRequestParser)
        deferred.addCallbacks(successfulParse, parseFailure)
        deferred.callback((request.args, self._downloadTo,))
        # was returning not done yet
        return deferred
