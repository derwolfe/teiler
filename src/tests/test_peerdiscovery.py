import os
import shutil

from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest
from twisted.internet import task

from ..peerdiscovery import Message, Peer, PeerDiscovery, heartbeatMsg, exitMsg, makeId

class FakeUdpTransport(object):
    """ Instead of connecting through the network, this transport 
    writes the broadcast messages to a variable that can be 
    checked. """

    implements(IUDPTransport)

    def __init__(self):
        self.msgs = []

    def write(self, packet, addr=None):
        self.msgs.append(repr(packet))

    def connect(host, port):
        pass

    def getHost():
        pass

    def stopListening():
        pass

    def setTTL(self, num):
        pass

    def joinGroup(self, address):
        pass

class PeerDiscoveryTests(unittest.TestCase):

    def setUp(self):
        self.clock = task.Clock()
        self.myAddr = "1.1.1.1"
        self.myAddrPort = 9203
        self.myUdpPort = 8000
        self.user = "test"
        self.protocol = PeerDiscovery(self.clock, 
                                      list(), 
                                      self.user, 
                                      self.myAddr, 
                                      self.myAddrPort, 
                                      self.myAddr, 
                                      self.myUdpPort)
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr

    def test_writes_message(self):
        self.protocol.sendMessage('bob')
        self.assertTrue(self.protocol.transport.msgs[0] == "'bob'")

    def test_received_message_from_self_do_not_add(self):
        """The new peer should not be added as it is equal to the host."""
        dg = Message(self.user, self.user, self.myAddr, self.myUdpPort).serialize()
        self.protocol.datagramReceived(dg, "192.168.1.1")
        self.assertTrue(len(self.protocol.peers) == 0)

    def test_received_message_from_peer_add(self):
        dg = Message("tester", "bob", "192.168.1.2", 8000).serialize()
        self.protocol.datagramReceived(dg, ("192.168.1.1", 8000))
        self.assertTrue(self.protocol.peers[0].name == 'bob')
        
    def test_sends_messages_on_loop(self):
        self.protocol.startProtocol()
        self.protocol.reactor.advance(10)
        # there should be two messages delivered over the interval of 10 seconds
        self.protocol.stopProtocol() # this keeps the reactor clean
        self.assertTrue(len(self.protocol.transport.msgs) == 2)
        
    def test_different_peer_is_added(self):
        p = Peer("jeff", "192.168.1.1", 8000)
        id = makeId(p.name, p.address, p.tcpPort)
        self.protocol.peers.append(p)
        self.assertTrue(self.protocol.isPeer(id))

    def test_sends_exit_message_on_exit(self):
        # check that stop protocol sends an exit message
        self.protocol.startProtocol() # needed to get a loop object to cancel
        self.protocol.stopProtocol() # 
        self.assertTrue('EXIT' in self.protocol.transport.msgs[1])

    def test_kills_looping_call(self):
        self.protocol.startProtocol() # loop started, could this be mocked?
        self.assertTrue(self.protocol.loop.running == True) 
        self.protocol.stopProtocol()
        self.assertTrue(self.protocol.loop.running == False)
