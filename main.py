#!/usr/bin/env python
# -*- coding: utf-8

from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log
from sys import stdout
from backend.server import (FileServerResource, FileRequestResource,
                            OutboundRequests, UsersResource)
from backend.peerdiscovery import PeerList, PeerDiscoveryProtocol
from backend.utils import getLiveInterface, getFilenames
from backend.postagent import submitFileRequest

class IPResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        return "hey - you are from {0})".format(request.transport.getPeer())

def main():
    log.startLogging(stdout)
    outbound = OutboundRequests()
    peers = PeerList()
    transferRequests = []
    downloadDirectory = "."
    # username needs to be able to handle unicode!
    username = u"wölfe"  #"chris"
    multicastAddress = '224.0.0.1'
    multicastPort = 8005
    ip = getLiveInterface()
    if ip is None:
        log.msg("Cannot start, no network connection found")
        return
    port = 58888

    root = resource.Resource()
    root.putChild('', IPResource())
    root.putChild('files', FileServerResource(outbound,
                                              ip,
                                              getFilenames,
                                              submitFileRequest ))
    root.putChild('requests', FileRequestResource(transferRequests,
                                                    downloadDirectory))
    root.putChild('users', UsersResource(peers))
    # the peer discovery system should start running as well
    reactor.listenTCP(port, server.Site(root))
    # reactor.listenMulticast(multicastPort,
    #                         PeerDiscoveryProtocol(reactor,
    #                                               peers,
    #                                               username,
    #                                               multicastAddress,
    #                                               multicastPort,
    #                                               ip,
    #                                               port))

    reactor.run()


if __name__ == '__main__':
    main()
