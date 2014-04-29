from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log

import sys

from teiler.server import FileServerResource
from teiler.client import FileRequestResource


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    filesServed = []
    transferRequests = []
    downloadDirectory = "."
    root = resource.Resource()
    root.putChild('files', FileServerResource(filesServed))
    root.putChild('requests', FileRequestResource(transferRequests, 
                                                    downloadDirectory))
# the peer discovery system should start running as well
    reactor.listenTCP(8080, server.Site(root))
    reactor.run()


