#!/usr/bin/env python
# -*- coding: utf-8

from twisted.internet import reactor
from twisted.web import server, resource
from twisted.python import log
from sys import stdout
from teiler.server import (FileHostResource,
                            FileServerResource,
                            FileRequestResource,
                            OutboundRequests,
                            UsersResource)
from teiler.peerdiscovery import PeerList, PeerDiscoveryProtocol
from teiler.utils import getLiveInterface, getFilenames
from teiler.postagent import submitFileRequest

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
    username = "chris"
    multicastAddress = '224.0.0.1'
    multicastPort = 8005
    ip = getLiveInterface()
    if ip is None:
        log.msg("Cannot start, no network connection found")
        return
    # set up ports
    internalPort = 58889
    externalPort = 58888
    fileHost = FileHostResource()

    # build the internal API
    internal = resource.Resource()
    internal.putChild('', IPResource())
    internal.putChild('files', FileServerResource(outbound,
                                                  getFilenames,
                                                  submitFileRequest,
                                                  fileHost))
    internal.putChild('users', UsersResource(peers))

    # build the external API
    external = resource.Resource()
    external.putChild('', IPResource())
    external.putChild('requests', FileRequestResource(transferRequests,
                                                      downloadDirectory))
    external.putChild('files', fileHost)

    # start listening for connections
    reactor.listenTCP(externalPort, server.Site(external))
    reactor.listenTCP(internalPort, server.Site(internal), interface='127.0.0.1')
    # reactor.listenMulticast(multicastPort,
    #                         PeerDiscoveryProtocol(reactor,
    #                                               peers,
    #                                               username,
    #                                               multicastAddress,
    #                                               multicastPort,
    #                                               ip,
    #                                               externalPort))
    reactor.run()


if __name__ == '__main__':
    main()
