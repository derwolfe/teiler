"""
Each client will have a server to which requests can be posted.

Once a user posts a request to another user's application, that request for a file
transfer will join the queue with other file transfer requests.

If the user (or recipient of the transfer request in this case) wants the file,
the user will somehow confirm the transfer request. 

This will trigger the application to use getFile, which really is a just a twisted
getPage command.
"""
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.client import getPage, downloadPage
from twisted.internet.defer import Deferred
from urllib import urlencode
from twisted.python import log
from sys import stdout


class FileRequest(object):
    """
    Store the information relating to a single transfer request.
    """
    
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def __repr__(self):
        return "File::{0}:{1}".format(self.url, self.session)
        
class FormArgsError(Exception):
    """
    Exception to be thrown when a form doesn't contain the 
    right arguments. Overkill?
    """
    pass


class MainPage(Resource):
    """
    Creating a main page should pull together all of the children
    resources.
    
    Files to be 'sent' will be hosted here as static files at a url
    to be provided by the user at runtime.
    """

    def __init__(self, toDownload, hosting):
        Resource.__init__(self)
        self.putChild("request", SendFileRequest(toDownload))
        

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
        self.delEntity(urlName)
        

class SendFileRequest(Resource):
    """
    Used by the recipient of a file transfer. 

    This resource will always be present in the application. It is
    used to receive file transfer requests from other users.
    """
    def __init__(self, files):
        """
        Pass in a list or some other object to which you
        can append files to download.
        """
        Resource.__init__(self)
        self.files = files

    def render_GET(self, request):
        """
        silly little test method.
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
        d.addErrback(log.msg)
        d.addCallback(self.files.append)
        d.callback(request.args)
        log.msg("SendFileRequest:: render_POST: files", self.files)
        return "<html>OK</html>" 


# used by the recipient of a file transfer
def parseFileRequest(data):
    """
    Expects a dict like object with the correct keys, this is provided 
    by request.args
    """
    log.msg('parseFileRequest: raw data:', data)
    if "url" not in data or "session" not in data:
        raise FormArgsError()
    elif "url" in data and "session" in data:
        url = data["url"][0]
        session = data["session"][0]
        log.msg('parseFileRequest: parsed url:', url)
        return FileRequest(url, session)


# used by the file sender
def createFileRequest(url, session):
    """
    Used by the file sender to propose a file transfer to 
    a fellow user.

    Basically, prepare a form to be posted to a url.
    """
    postdata = urlencode({'url': url, 'session': session })
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

def getFile(url, session, downloadDir):
    """
    Download the file located at te url into the new location.
    """
    log.msg("getFile:: data:", url, session)
    # returns a deferred!, you could attach callback
    # to remove the files from the list once the transfer is complete
    return downloadPage(url, downloadDir)




if __name__ == '__main__':
    log.startLogging(stdout)
    # to download 
    state = []
    toDownload = []
    hosting = []
    
    # to host for upload create another list of file names
    root = MainPage(hosting, toDownload)

    # to add new folders
    ## new files
    root.putChild('meme', File('./'))
    ## use to remove files
    root.delEntity('meme')

    server = 'http://localhost:8880/request'
    url = 'http://localhost:8000/filemestupid'
    session = 'chris'
    p, h = createFileRequest(url, session)
    reactor.callLater(1, 
                      submitFileRequest, 
                      recipient=server, 
                      postdata=p, 
                      headers=h)


    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
## part of initial test
