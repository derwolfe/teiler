from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log

import sys

from teiler.server import FileServerResource
from teiler.client import FileRequestResource


class HelloResource(resource.Resource):
    isLeaf = False
    numberRequests = 0

    def render_GET(self, request):
        request.setHeader("content-type", "text/plain")
        return "Welcome to teiler\n"

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    filesServed = []
    transferRequests = []
    downloadDirectory = "."
    root = resource.Resource()
    root.putChild('', HelloResource())
    root.putChild('files', FileServerResource(filesServed))
    root.putChild('requests', FileRequestResource(transferRequests, 
                                                    downloadDirectory))
    reactor.listenTCP(8080, server.Site(root))
    reactor.run()


