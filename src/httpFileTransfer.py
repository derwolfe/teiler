"""
Each client will have a server to which requests can be posted.

Once a user posts a request to another user's application, that request for a file
transfer will join the queue with other file transfer requests.

If the user (or recipient of the transfer request in this case) wants the file,
the user will somehow confirm the transfer request. 

This will trigger the application to use getFile, which really 
is a just a twisted  getPage command.
"""
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.client import getPage, downloadPage
from twisted.internet.defer import Deferred, DeferredList
from twisted.python.filepath import FilePath
from urllib import urlencode
from twisted.python import log
from sys import stdout
# secure file names
import os
 
class FormArgsError(Exception):
    """
    Exception to be thrown when a form doesn't contain the 
    right arguments.
    """
    pass

def isSecurePath(pathToCheck, downloadPath):
    """
    IsSecurePath checks to see whether a provided path is actually 
    operating inside of the application.

    The goal is to stop directory traversal from paths passed in by users.
    """
    # get the absolute path of the application downlowd folder
    downloadTo = os.path.abspath(downloadPath)
    joinedPath = os.path.join(downloadPath, pathToCheck)
    requestedPath = os.path.abspath(joinedPath)
    commonPath = os.path.commonprefix([requestedPath, downloadTo])
    return commonPath == downloadPath 
##

class FileRequest(object):
    """
    Stores the state of each file request. 

    Contains all of the files to be downloaded and the relavent session 
    information.

    Also handles downloading the files it contains.
    """
    
    def __init__(self, url, session, files, downloadTo):
        # should this really be the list of file names and the base url?
        self.url = url
        self.session = session
        ## this is the list of file names
        self.files = files
        # why is this here?
        self.downloadTo = downloadTo
        self.downloading = []

    def __repr__(self):
        return "Files::{0}:{1}".format(self.url, self.session)
    
    def createFileDirs(self, filepath):
        """
        given a path like "./foo/bar/baz.txt" check if ./foo/bar exists.
        If it does not exists, create it.
        """
        path = os.path.join(self.downloadTo, filepath)
        # strip leading slashes, dots
        log.msg("FileRequest:: createFileDirs:", path)
        # do the mkdirs -p with all but the filename
        dir, _ = os.path.split(path)
        head = dir # here is where the security check should happen
        if os.path.exists(head) == False and head != "" :
            os.makedirs(head, 0755)
            log.msg("FileRequest:: createFileDirs:", head)
        else:
            log.msg("FileRequest:: createFileDirs: exists", head)
    
    def getFiles(self):
        """
        Download all of the files listed in the request object.
        It's assumed that the file request will only be sending over filepaths.
        This means that directories will be created on the fly if they don't
        exist.

        This also will occur concurrently, though in the same thread.
        Each file request will spawn a new deferred, which the reactor will
        schedule accordingly.
        """
        # if self.downloads is not empty, getFiles should exit
        if len(self.downloading) > 0:
            return
        # proceed
        while self.files: 
            # each request will really just return a deferred, so the 
            # so it will be popped immediately, and go through the list, 
            # not exctly what you want...
            # get the files one by one
            filename = self.files.pop()
            # create that files directories
            self.createFileDirs(filename)
            # form the address
            url = self.url + '/' + filename
            downloadTo = os.path.join(self.downloadTo, filename)
            log.msg("FileRequest:: getFiles:%s, %s" %(url, downloadTo))
            # one concern doing it this way is that the network could
            # be overloaded, as all of the http requests will be issued 
            # at basically the same time. not sure this is the case
            # also, how to access the content length header for progress?
            toGet = _getFile(url, self.downloadTo + filename)
            self.downloading.append(toGet)
        log.msg("FileRequest::getFiles:: downloads begun")
        return DeferredList(self.downloading)


    def getStatus(self):
        """
        Check the status of each of the downloads in the self.downloading
        list.
        """
        return 
        

class MainPage(Resource):
    """
    Creating a main page should pull together all of the children
    resources.
    
    Files to be 'sent' will be hosted here as static files at a url
    to be provided by the user at runtime.
    """

    def __init__(self, toDownload, hosting, downloadTo):
        Resource.__init__(self)
        # post against the resource to create a new file request
        self.putChild("request", FileRequestResource(toDownload, downloadTo))
        # contains files currently being hosted and their urls
        self.hosting = hosting

    def addFile(self, urlName, path):
        """
        Adds a new file resrurce 
        """
        log.msg('MainPage:: addFile:', path)
        self.hosting.append(path)
        self.putChild(urlName, File(path))

    def removeFile(self, urlName):
        """
        Removes a File resource that is currently being hosted.
        """
        log.msg('MainPage:: removeFile:', urlName)
        self.delEntity(urlName)
        

class FileRequestResource(Resource):
    """
    Used by the recipient of a file transfer. 

    This resource will always be present in the application. It is
    used to receive file transfer requests from other users.
    """
    def __init__(self, files, downloadTo):
        """
        Pass in a list or some other object to which you
        can append files to download.
        """
        Resource.__init__(self)
        self.files = files
        self.downloadTo = downloadTo

    def render_GET(self, request):
        """
        silly little test method. Meant to show that a resource is alive 
        by issuing a get aginst it.
        """
        return "<html>ja, ich bins</html>"
    
    def render_POST(self, request):
        """
        respond to post requests. This is where the file sender processing
        will begin.
        """
        d = Deferred()
        log.msg("FileRequestResource:: render_POST: data", request.args)
        d.addCallback(parseFileRequest)
        def error(ignored):
            return "<html>Error parsing form</html>"
        d.addErrback(error)
        d.addCallback(self.files.append)
        d.callback((request.args, self.downloadTo,))
        log.msg("FileRequestResource:: render_POST: files", self.files)
        return "<html>OK</html>" 

# used by recipient 
def _getFile(url, downloadDir):
    """
    Download the file located at te url into the new location.
    """
    log.msg("getFile:: from:", url)
    # returns a deferred!, you could attach callback
    # to remove the files from the list once the transfer is complete
    d = downloadPage(url, downloadDir)
    return d

# used by the recipient of a file transfer
def parseFileRequest(data, _downloadTo):
    """
    Expects a dict like object with the correct keys, this is provided 
    by request.args
    """
    log.msg('parseFileRequest: raw data:', data)
    if "url" not in data or "session" not in data or "files" not in data:
        raise FormArgsError()
    elif "url" in data and "session" in data and "files" in data:
        url = data["url"][0]
        session = data["session"][0]
        files = _parseFileNames(data["files"][0])
        log.msg('parseFileRequest: parsed url:', url)
        log.msg('parseFileRequest: parsed files:', files)
        return FileRequest(url, session, files, _downloadTo)

#used by file receiver
def _parseFileNames(files):
    """
    Used by the recipient of a file transfer request. 
    Pass in a list of filenames, seperated by commas. 
    Returns a list of filenames.
    """
    # maybe need to escape
    names = files.split(',')
    log.msg("_parseFileNames::", names)
    return names

# used by the file sender
def createFileRequest(url, session, files):
    """
    Used by the file sender to propose a file transfer to a fellow user.

    The file request will contain the url where the files will be hosted,
    a session key, and the actual file names that can be found.
    
    Only actually filenames will be listed, not directories. The responsibility
    to create directories will fall on the person downloading the file.
    """
    postdata = urlencode({'url': url, 
                          'session': session, 
                          'files': files })
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    return postdata, headers

# used by the file sender
def submitFileRequest(recipient, postdata, headers):
    """
    use twisted.web.client.getpage to post the file push
    request.

    returns a deferred.
    """
    log.msg("submitFileRequest:: data:", recipient)
    return getPage(recipient,
                   method='POST', 
                   postdata=postdata,
                   headers=headers)
