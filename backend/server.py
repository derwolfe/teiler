"""
A host is a set of resources that exist in order to serve files.

These files will be requested at a known location by the client.
"""
from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.client import getPage
from twisted.python import log, filepath
from urllib import urlencode

HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}


# maybe call FileServerResource
class FileServerResource(Resource):
    """
    The `FileServerResource` is the base location for the system.

    `addFile` New files are served from a host by calling addFiles with both
    a location where the file should be served, relative to the root
    resource. E.g., /mysuperspecialfile/foo.jpg
    The file passed in will be served at the specified URL. Completely
    accessible to any other user on the network.

    `removeFile` is used when a user no longer wishes to serve a given file to
    other users at  given location.
    """
    isLeaf = False

    def __init__(self, hosting):
        Resource.__init__(self)
        self.hosting = hosting

    def addFile(self, urlName, path):
        """
        Adds a new file resource for other users to access.
        """
        log.msg('addFile:', path, urlName, system="FileServerResource")
        self.hosting.append(path)
        self.putChild(urlName, File(path))

    def removeFile(self, urlName):
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
