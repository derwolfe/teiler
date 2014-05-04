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


# XXX not tested!
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
        Resource.__init__(self) # is this necessary?
        self.hosting = hosting

    def _addFile(self, urlName, path):
        """
        Adds a new file resource for other users to access.
        """
        log.msg('addFile:', path, urlName, system="FileServerResource")
        self.hosting.append((urlName, path))
        # needs to call super!
        Resource.putChild(self, urlName, File(path))
        # file could fail and say, 'file not found!'
        # it could also not have sufficient permissions to serve

    def render_DELETE(self, urlName):
        """
        Removes a File resource that is currently being hosted.
        """
        log.msg('removeFile:', urlName, system="MainPage")
        self.delEntity(urlName)

    def render_GET(self, request):
        """
        Display the files currently being hosted.
        """
        request.setHeader("content-type", "application/json")
        # return the files being served
        # return the either the file, or the top level directory of th
        # file being served. Basically, return a list of those paths
        # that are saved in the `hosting` datastructure.
        files = [', '.join(x) for x in self.hosting]
        return json.dumps({'files': files})

    def render_POST(self, request):
        """
        Posting a new file request should result in either the new file
        being successfully added to the system or an error message being
        returned to the user.
        """
        serveAt = request.args['serveat']
        filepath = request.args['filepath']
        # both of these could happen, result in a bad request
        if not serveAt:
            return json.dumps({'url': None, 'errors': 'No serve path provided'})
        if not filepath:
            return json.dumps({'url': None, 'errors': 'No filepath provided'})
        # if this location is already being served, what to do?
        self._addFile(serveAt[0], filepath[0])
        # filenames = createFilenames(filepath)  # this could block!
        # filenames is ALL of the files being hosted for the client
        # broadcast the file being available to another user
        #postdata = createFileRequestData(request.location, filenames)
        # if it can be added, return a link to the file resource,
        # otherwise, return an error
        url = request.URLPath().netloc  + '/' + serveAt[0]
        request.setHeader("content-type", "application/json")
        return json.dumps({ 'url': url, 'error': None })

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
