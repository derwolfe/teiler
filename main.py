#!/usr/bin/env python
# -*- coding: utf-8

from twisted.web import server
from twisted.python import log

from sys import stdout

from teiler import api
from teiler.server import OutboundRequests
from teiler.utils import getLiveInterface, getFilenames
from teiler.postagent import submitFileRequest
from teiler.peerdiscovery import PeerList, PeerDiscoveryProtocol
from teiler.filerequest import parseFileRequest


def main():
    from twisted.internet import reactor
    log.startLogging(stdout)
    username = "chris"
    multicastAddress = '224.0.0.1'
    multicastPort = 8005

    ip = getLiveInterface()
    if ip is None:
        log.msg("Cannot start, no network connection found")
        return

    outbound = OutboundRequests()
    inbound = []
    downloadTo = "."
    internalPort = 58888
    externalPort = 58889
    rootUrl = "http://" + ip + ":" + str(externalPort) + "/files"
    peers = PeerList()

    internal = api.InternalAPIFactory(
        rootUrl,
        outbound,
        fileNameGetter=getFilenames,
        fileRequestSubmitter=submitFileRequest,
        peerList=PeerList()
    )

    external = api.ExternalAPIFactory(
        outbound=outbound,
        inbound=inbound,
        downloadTo=downloadTo,
        requestParser=parseFileRequest
    )

    log.msg(internal)
    log.msg(external)
    log.msg(peers)

    reactor.listenTCP(internalPort,
                      server.Site(internal.app.resource()),
                      interface='127.0.0.1')

    reactor.listenTCP(externalPort,
                      server.Site(external.app.resource()),
                      interface='0.0.0.0')

    peerDiscovery = PeerDiscoveryProtocol(
        reactor=reactor,
        peerList=peers,
        name=username,
        multiCastAddress=multicastAddress,
        multiCastPort=multicastPort,
        address=ip,
        port=externalPort
    )

    reactor.listenMulticast(multicastPort, peerDiscovery)
    reactor.run()


if __name__ == '__main__':
    main()
