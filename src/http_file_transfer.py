"""
Have a file server accepting post requests.
"""
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.client import getPage

from urllib import urlencode

## file server

## 1 have the ability to post a file
## 2 serve the file at the url

# file uploads suck in twisted, downloads don't   
# each drop event should just use a sessionId and a filename
# i.e. add resource root.putChild(sessionId + filename, File(filename))
# a '' client '' will grab urls that it wants
# a '' server '' will host the files it wants to send, and send posts


def sendFile(address, session, filename):
    """
    This function expects a network address, a session id, and a  
    filename. Using this it will post a request a user.

    The data contained in this request, will be used to download
    the file from the sender.
    """
    postdata = urllib.urlencode({
            'address': address,
            'session': session,
            'filename': filename
            })
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    return getPage(address, 
                    method='POST', 
                    postdata=postdata,
                    headers=headers
                )

if __name__ == '__main__':
    #root = Resource()
    #root.putChild('r1', File("/Users/chris/Code/rust"))
    #root.putChild('r2', File("/Users/chris/Code/fun/rust"))

    ## your gui will basically construct this set of paths at runtime
    ## this does not work...why?    
    c = Content()
    c.add_file("r1", "/Users/chris/Code/rust")
    c.add_file("r2", "/Users/chris/Code/fun/rust")
    factory = Site(c.root)

    # factory sets up the actual site root
    #factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()
