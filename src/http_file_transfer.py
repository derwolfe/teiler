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
        log.msg("SendFileRequest:: render_post : data", request.args)
        url = parseFileRequest(request.args)
        return url
    
def parseFileRequest(data):
    """
    Expects a dict like object with the correct keys, this is provided 
    by request.args
    """
    log.msg('parsefilerequest: raw data:', data)
    if "url" in data:
        url = data["url"]
    return url


# used by the file sender
def createFileRequest(url):
    """
    The data contained in this request, will be used to download
    the file from the sender.
    """
    postdata = urlencode({'url': url })
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    return postdata, headers

# used by the file sender
def submitFileRequest(recipient, postdata, headers):
    """
    use twisted.web.client.getpage to grab post the file push
    request.

    returns a deferred.
    """
    log.msg("submitFileRequest:: data:", recipient)
    return getPage(recipient,
                   method='POST', 
                   postdata=postdata,
                   headers=headers)


if __name__ == '__main__':
    log.startLogging(stdout)
    root = Resource()
    root.putChild('request', SendFileRequest())
    server = 'http://localhost:8880/request'
    url = 'http://localhost:8000/filemestupid'

    p, h = createFileRequest(url)
    # post a test message to the fileResource
    reactor.callLater(1, 
                      submitFileRequest, 
                      recipient=server, 
                      postdata=p, 
                      headers=h)
    
    # factory sets up the actual site root
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
