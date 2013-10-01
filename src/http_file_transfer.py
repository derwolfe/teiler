"""
Have a file server accepting post requests.
"""
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.internet.defer import Deferred

from urllib import urlencode, unquote
## 1 have the ability to post a file
## 2 serve the file at the url

# file uploads suck in twisted, downloads don't   
# each drop event should just use a sessionId and a filename
# i.e. add resource root.putChild(sessionId + filename, File(filename))
# a '' client '' will grab urls that it wants
# a '' server '' will host the files it wants to send, and send posts


def sendFileRequest(address, session, filename):
    """
    This function expects a network address, a session id, and a  
    filename. Using this it will post a request a user.

    The data contained in this request, will be used to download
    the file from the sender.
    """
    postdata = urlencode({
            'address': address,
            'session': session,
            'filename': filename
            })
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    # request the page by posting the form
    return getPage(address, 
                    method='POST', 
                    postdata=postdata,
                    headers=headers
                )


def parseFileRequest(data):
    """
    Expects a dict like object with the correct keys, this is provided 
    by request.args
    """
    # you want the address, the session Id and the file name

    if "address" in data and "session" in data and "filename" in data:
        addr = data["address"]
        session = data["session"]
        filename = data["filename"]
    return addr, session, filename
    

def getFile(address, session, filename):
    """
    Get the file at the specific address, session, filename url
    """
    return getPage(url) #download the file from the location

def makeFileUrl(address, session, filename):
    pieces = address + '/' + session + '/' + filename
    return pieces # you will need t encode pieces

class FileSubmission(Resource):
    
    def render_POST(self, request):
        """
        parse a file send request.
        """
        addr, session, filename = parseFileRequest(request.args)
        log.msg("file", filename[0],)
        url = makeFileUrl(addr[0], session[0], filename[0])
###        log.msg("url:", url)

if __name__ == '__main__':
    from twisted.python import log
    from sys import stdout
    log.startLogging(stdout)
    root = Resource()
    #root.putChild('r1', File("/Users/chris/Code/rust"))
    #root.putChild('r2', File("/Users/chris/Code/fun/rust"))
    root.putChild('request', FileSubmission())
    reactor.callLater(2, 
                      sendFileRequest, 
                      address='http://localhost:8880/request', 
                      session='a', 
                      filename='1')
    # factory sets up the actual site root
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
