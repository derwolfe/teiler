"""
server.py

All of the resources needed to run the file server
"""
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.server import NOT_DONE_YET
from twisted.python import log, filepath
from twisted.internet.defer import Deferred
from urllib import urlencode

import json
import backend.filerequest as filerequest


HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}


class Files(object):
    """
    Data structure that maintains the current files being served by
    the application.

    Supports add, remove, and listall
    """
    def __init__(self):
        self._items = {}

    def add(self, url, path):
        self._items[url] = path

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
            uri = root + '/' + key
            combos.append({'url': uri, 'path': val})
        return combos


class FileServerResource(Resource):
    """
    The `FileServerResource` is the base location for the system.

    :param addFile: New files are served from a host by calling addFiles with
    both a location where the file should be served, relative to the root
    resource. E.g., /mysuperspecialfile/foo.jpg. The file passed in will be
    served at the specified URL. Completely accessible to any other user on
    the network.

    :param removeFile: is used when a user no longer wishes to serve a given
    file to other users at  given location.
    """
    isLeaf = False

    def __init__(self, hosting):
        Resource.__init__(self)
        self.hosting = hosting

    def _addFile(self, urlName, path):
        """
        Adds a new file resource for other users to access.
        """
        log.msg('addFile:', path, urlName, system="FileServerResource")
        self.hosting.add(urlName, path)
        Resource.putChild(self, urlName, File(path))

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
        self._removeFile(url)
        # return an HTTP response code!
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
        serveAt = request.args['serveat']
        fileloc = request.args['filepath']
        # both of these could happen, result in a bad request
        if not serveAt:
            return json.dumps({'url': None, 'errors': 'No url provided'})
        if not filepath:
            return json.dumps({'url': None, 'errors': 'No filepath provided'})
        # if this location is already being served, what to do?
        self._addFile(serveAt[0], fileloc[0])
        url = request.URLPath().__str__() + '/' + serveAt[0]
        # filenames = createFilenames(filepath)  # this could block!
        # while posting, make a request to another server, saying
        # ADD THIS FILE TO YOUR DOWNLOADS
        # postdata = createFileRequestData(request.location, filenames)
        request.setHeader("content-type", "application/json")
        return json.dumps({'url': url})


def createFileRequestData(url, files):
    """
    Create the data needed to send a file request to another users.

    The file request will contain the url where the files will be hosted,
    a session key, and the actual file names that can be found.
    """
    # XXX maybe the post data should be from a class containg url, session,
    # and file information. This class could then have an encode method.
    return urlencode({'url': url, 'files': files})


# XXX not tested
def createFilenames(path):
    """
    Get all of the filenames that are below this path. Basically if a directory
    is passed in, it can be assumed that the user wants to share the entire
    directory.

    :param applicationPath: a string that will be converted to a FilePath
    object
    """
    # XXX this could block
    path = filepath.FilePath(path)
    # this could be arbitrarily large, it might make sense to force the client
    # to do this!
    return ['/'.join(subpath.segmentsFrom(path.parent()))
            for subpath in path.walk()]


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
        # list of files that others want to transfer to you
        self.transferRequests = transferRequests
        # top level directory into which files will be saved
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
            request.write("ok")  # this is not being returned outside
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
