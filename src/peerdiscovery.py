import sys

from twisted.python import log

from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol

class PeerDiscovery(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self, teiler):
        self.teiler = teiler
        #self.host = teiler.multiCastAddress
        #self.port = teiler.multiCastAddress
        #self.peers = []
        #self.messages = []

    def startProtocol(self):
        self.transport.joinGroup(self.teiler.multiCastAddress)
        self.sendMessage("CONNECT")
        self._call = task.LoopingCall(self.sendMessage("HERE"))
        self._loop = self._call.start(5)

    def sendMessage(self, msg):
        self.transport.write(msg, (self.teiler.multiCastAddress, self.teiler.multiCastPort))

    def stopProtocol(self):
        self.sendMessage("EXIT")
        self._call.stop()

    def datagramReceived(self, datagram, address):
        # being developed
        #self.sendMessage("HEARD")
        print "HEARD"
        self.teiler.messages.append(datagram)

        if self.teiler.address != address:
            if address not in self.teiler.peers:
                self.teiler.peers.append(address)
                log.msg(address)
                