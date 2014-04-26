from twisted.internet import reactor
from twisted.web import server, resource
from teiler.server import FileServerResource
from teiler.client import FileRequestResource

import sys

from twisted.python import log

class HelloResource(resource.Resource):
    isLeaf = False
    numberRequests = 0
    
    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader("content-type", "text/plain")
        return "I am request #" + str(self.numberRequests) + "\n"


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    root = resource.Resource()
    root.putChild('', HelloResource())
    root.putChild('files', FileServerResource([]))
    root.putChild('requests', FileRequestResource([], "."))
    reactor.listenTCP(8080, server.Site(root))
    reactor.run()


