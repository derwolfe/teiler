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
from twisted.internet.defer import Deferred
from twisted.python.filepath import FilePath
from urllib import urlencode
from twisted.python import log
from sys import stdout
import os

 
class FormArgsError(Exception):
    """
    Exception to be thrown when a form doesn't contain the 
    right arguments.
    """
    pass


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
        self.files = files
        self.downloadTo = downloadTo

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
        head = _prepFilepath(dir)
        if os.path.exists(head) == False and head != "" :
            os.makedirs(head, 0755)
            log.msg("FileRequest:: createFileDirs:", head)
        else:
            log.msg("FileRequest:: createFileDirs: exists", head)
    
    def getFiles(self):
        """
        Download all of the files listed in the request object.
        It's assumed that the file request will only be sending over filepaths.
        This means that directories will be created on the fly if the don't
        exist.
        """
        while self.files:
            # you need to make sure certain filenames do not allow travesal 
            # outside of the directory. That is strip all leading dots
            filename = self.files.pop()
            self.createFileDirs(filename)
            url = self.url + '/' + filename
            downloadTo = os.path.join(self.downloadTo, filename)
            log.msg("FileRequest:: getFiles:", url)
            log.msg("FileRequest:: getFiles:", downloadTo)
            #d = getFile(url, self.downloadTo + filename)


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
        self.putChild("request", SendFileRequest(toDownload, downloadTo))
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
        

class SendFileRequest(Resource):
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
        log.msg("SendFileRequest:: render_POST: data", request.args)
        d.addCallback(parseFileRequest)
        def error(ignored):
            return "<html>Error parsing form</html>"
        d.addErrback(error)
        d.addCallback(self.files.append)
        d.callback((request.args, self.downloadTo,))
        log.msg("SendFileRequest:: render_POST: files", self.files)
        return "<html>OK</html>" 

# used by recipient 
def _getFile(url, downloadDir):
    """
    Download the file located at te url into the new location.
    """
    log.msg("getFile:: from:", url)
    # returns a deferred!, you could attach callback
    # to remove the files from the list once the transfer is complete
    return downloadPage(url, downloadDir)

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

 
def _prepFilepath(filepath):
    """
    Remove leading slashes and dots
    """
    return filepath.strip(".").strip("/")

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
