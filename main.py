from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log
from sys import stdout
from backend.server import (FileServerResource, FileRequestResource, Files,
                            UsersResource)
from backend.peerdiscovery import PeerList

class IPResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "hey - you are from {0})".format(request.transport.getPeer())


if __name__ == '__main__':
    log.startLogging(stdout)
    filesServed = Files()
    peers = PeerList()
    transferRequests = []
    downloadDirectory = "."
    root = resource.Resource()
    root.putChild('', IPResource())
    root.putChild('files', FileServerResource(filesServed))
    root.putChild('requests', FileRequestResource(transferRequests,
                                                    downloadDirectory))
    root.putChild('users', UsersResource(peers))
    # the peer discovery system should start running as well
    reactor.listenTCP(58888, server.Site(root))
    reactor.run()
