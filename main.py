from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log
from sys import stdout
from backend.server import FileServerResource, FileRequestResource

class IPResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "hey - you are from {0})".format(request.transport.getPeer())


if __name__ == '__main__':
    log.startLogging(stdout)
    filesServed = []
    transferRequests = []
    downloadDirectory = "."
    root = resource.Resource()
    root.putChild('', IPResource())
    # local only!
    root.putChild('files', FileServerResource(filesServed))
    # outside only!
    root.putChild('requests', FileRequestResource(transferRequests,
                                                    downloadDirectory))
    # the peer discovery system should start running as well
    reactor.listenTCP(8080, server.Site(root))
    reactor.run()
