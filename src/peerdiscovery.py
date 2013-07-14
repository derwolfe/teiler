import sys
from twisted.python import log
from twisted.internet import task, reactor
from twisted.internet.protocol import DatagramProtocol 

class PeerDiscovery(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self, teiler):
        self.teiler = teiler

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.teiler.multiCastAddress)
        self.transport.write("CONNECT", (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        reactor.callLater(5.0, self.sendHeartBeat)

    def sendHeartBeat(self):
        self.transport.write("ALIVE", (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("Heartbeat sent")
        reactor.callLater(5.0, self.sendHeartBeat)

    def stopProtocol(self):
        self.transport.write("EXIT", (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("EXIT")

    def datagramReceived(self, datagram, address):
        log.msg("Sending: HEARD")
        self.teiler.messages.append(datagram)

        if self.teiler.address != address:
            if address not in self.teiler.peers:
                self.teiler.peers.append(address)
                log.msg(address)
                