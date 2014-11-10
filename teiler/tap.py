"""
Tap file for teiler.
"""
from teiler import api
from teiler.server import OutboundRequests
from teiler.utils import getLiveInterface, getFilenames
from teiler.postagent import submitFileRequest
from teiler.peerdiscovery import PeerList, PeerDiscoveryProtocol
from teiler.filerequest import parseFileRequest

from twisted.application import internet, service
from twisted.python import log, usage
from twisted.web import server


class Options(usage.Options):
    optParameters = [
        ['username', 'u', 'chris', 'The username to display to others']
    ]


def makeService(config):
    """
    construct the teiler server and parse any options it might have
    """
    from twisted.internet import reactor
    ip = getLiveInterface()

    if ip is None:
        log.msg("Cannot start, no network connection found")
        return

    return _bootstrap(config['username'], reactor, ip)

def _bootstrap(username, reactor, ip):
    multicastAddress = '224.0.0.1'
    multicastPort = 8005

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
    peerDiscovery = PeerDiscoveryProtocol(
        reactor=reactor,
        peerList=peers,
        name=username,
        multiCastAddress=multicastAddress,
        multiCastPort=multicastPort,
        address=ip,
        port=externalPort
    )
    # set up the services - should these be plugins?

    p = service.MultiService()
    internet.TCPServer(internalPort,
                       server.Site(internal.app.resource()),
                       interface='127.0.0.1'
    ).setServiceParent(p)

    internet.TCPServer(externalPort,
                        server.Site(external.app.resource()),
                        interface='0.0.0.0'
    ).setServiceParent(p)

    internet.MulticastServer(multicastPort,
                             peerDiscovery
    ).setServiceParent(p)
    return p
