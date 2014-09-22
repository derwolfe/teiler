#!/usr/bin/env python
# -*- coding: utf-8

from twisted.internet import reactor
from twisted.web import server
from twisted.python import log

from sys import stdout

from teiler import api
from teiler.server import OutboundRequests
from teiler.utils import getLiveInterface  # , getFilenames
# from teiler.postagent import submitFileRequest
# from teiler.peerdiscovery import PeerList, PeerDiscoveryProtocol


def main():
    log.startLogging(stdout)
    # username = "chris"
    # multicastAddress = '224.0.0.1'
    # multicastPort = 8005
    ip = getLiveInterface()
    if ip is None:
        log.msg("Cannot start, no network connection found")
        return

    outbound = OutboundRequests()
    # inbound = []
    # downloadTo = "."
    internalPort = 58888
    externalPort = 58889
    rootUrl = "http://" + ip + ":" + str(externalPort) + "/files"
    internal = api.InternalAPIFactory(rootUrl, outbound)
    external = api.ExternalAPIFactory(outbound)

    log.msg(internal)
    log.msg(external)

    reactor.listenTCP(internalPort, server.Site(internal.app.resource()),
                      interface='127.0.0.1')
    reactor.listenTCP(externalPort, server.Site(external.app.resource()),
                      interface='0.0.0.0')
    reactor.run()
    # reactor.listenTCP(internalPort,
    #                   server.Site(internal),
    #                   interface='127.0.0.1')
    # reactor.listenMulticast(multicastPort,
    #                         PeerDiscoveryProtocol(reactor,
    #                                               peers,
    #                                               username,
    #                                               multicastAddress,
    #                                               multicastPort,
    #                                               ip,
    #                                               externalPort))
    # reactor.run()


if __name__ == '__main__':
    main()
