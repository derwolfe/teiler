"""
server.py

All of the resources needed to run the file server
"""
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.client import getPage
from twisted.python import log, filepath
from urllib import urlencode

from twisted.internet.defer import Deferred
from twisted.web.server import NOT_DONE_YET

import backend.filerequest as filerequest

HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}


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

        self.hosting = hosting

    def addFile(self, urlName, path):
        """
        Adds a new file resource for other users to access.
        """
        log.msg('addFile:', path, urlName, system="FileServerResource")
        self.hosting.append(path)
        self.putChild(urlName, File(path))

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
        request.setHeader("content-type", "text/plain")
        # return the files being served
        return "Hi, welcome to teiler - here is the base file server"

    def render_POST(self, request):
        """
        The request should contain the information needed to host a new file.
        Only honor that request, if it originates from localhost.
        """
        # if request is from localhost, post the file
        self.addFile(request.location, request.path)
        filenames = createFilenames(request.path) # this could block!
        # files needs to be a list.
        postdata = createFileRequestData(request.location, filenames)
        request.setHeader("content-type", "text/plain")
        # return the link to the posted file
        return "you've posted a file"


## these are client requests
def submitFileRequest(recipient, postdata, headers):
    """
    Post the file request information to another user.
    """
    log.msg("submitFileRequest:: data:", recipient, system="httpFileTransfer")
    return getPage(recipient,
                   method='POST',
                   postdata=postdata,
                   headers=headers)


def createFileRequestData(url, files):
    """
    Propose a file transfer to a fellow user.

    The file request will contain the url where the files will be hosted,
    a session key, and the actual file names that can be found.
    """
    # XXX maybe the post data should be from a class containg url, session,
    # and file information. This class could then have an encode method.
    return urlencode({'url': url, 'files': files})

def createFilenames(path):
    """
    Get all of the filenames that are below this path. Basically if a directory
    is passed in, it can be assumed that the user wants to share the entire
    directory.

    :param applicationPath: a string that will be converted to a FilePath object
    """
    # XXX this could block
    path = filepath.FilePath(path)
    # this could be arbitrarily large, it might make sense to force the client to do this!
    return ['/'.join(subpath.segmentsFrom(path.parent())) for subpath in path.walk()]


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
        # if request is local, show local file requests, otherwise, show a message
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
