"""
Have a file server accepting post requests.
"""
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.client import getPage
from twisted.internet.defer import Deferred

from urllib import urlencode, unquote, quote
from twisted.python import log
from sys import stdout
## 1 have the ability to post a file
## 2 serve the file at the url

# file uploads suck in twisted, downloads don't   
# each drop event should just use a sessionId and a filename
# i.e. add resource root.putChild(sessionId + filename, File(filename))
# a '' client '' will grab urls that it wants
# a '' server '' will host the files it wants to send, and send posts


class SendFileRequest(Resource):
    """
    Resource meant to process file sending requests.
    To transfer a file, the sender of the file must post a form to this resource.
    Currently this server only supports having urls posted to it.
    """
    def render_POST(self, request):
        log.msg('hit')
        d = Deferred()
        d.addCallback(parseFileRequest)
        d.addErrback(parseError)
        d.addCallback(makeFileUrl)
        d.addCallback(getPage)
        d.addErrback(log.msg)
        # go do my bidding
        d.callback(request.args)
        return d
    
    # def render_GET(self, request):
    #     log.msg("get request")
    #     return "<html><h1>hi</h1></html>"


def parseFileRequest(data):
    """
    Expects a dict like object with the correct keys, this is provided 
    by request.args
    """
    log.msg('parsefilerequest: raw data:', data)

    if "senderAddress" in data and "session" in data and "filename" in data:
        senderAddress = unquote(data["senderAddress"][0])
        session = unquote(data["session"][0])
        filename = unquote(data["filename"][0])
        log.msg("parsefilerequest: parsed data:", senderAddress, session, filename)
    return senderAddress, session, filename


#def makeFileUrl(address, senderAddress, session, filename):
def makeFileUrl(results):
    """
    Use the information passed in from the posted message to create a url.
    """
    log.msg("makeFileUrl:", results)
    address = results[0]
    session = results[1]
    filename = results[2]
    pieces = address + '/' + session + '/' + filename
    log.msg("makeFileUrl: pieces:", pieces)
    return pieces # you will need t encode pieces


def parseError(reason):
    log.msg("error parsing message", reason)


# used by the file sender
def createFileRequest(sender, session, filename):
    """
    This function expects a network address, a session id, and a  
    filename. Using this it will post a request a user.

    The data contained in this request, will be used to download
    the file from the sender.
    """
    postdata = urlencode({'senderAddress': sender,
                          'session': session,
                          'filename': filename })
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    return postdata, headers

# used by the file sender
def submitFileRequest(recipient, postdata, headers):
    """
    use twisted.web.client.getpage to grab post the file push
    request.

    returns a deferred.
    """
    return getPage(recipient,
                   method='POST', 
                   postdata=postdata,
                   headers=headers)


if __name__ == '__main__':
    log.startLogging(stdout)
    root = Resource()
    root.putChild('request', SendFileRequest())
    server = 'http://localhost:8880/request'
    p, h = createFileRequest(sender='http://localhost:8880',
                             session='a', 
                             filename='1')
    # post a test message to the fileResource
    reactor.callLater(10, 
                      submitFileRequest, 
                      recipient=server, 
                      postdata=p, 
                      headers=h)
    
    # factory sets up the actual site root
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
