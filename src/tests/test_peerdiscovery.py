import os
import shutil

from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest
from twisted.internet import task

# classes to test
from ..peerdiscovery import Message, Peer, PeerDiscovery, heartbeatMsg, exitMsg

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
        self.protocol = PeerDiscovery(self.clock, "test", "1.1.1.1", "9203", "1.1.1.1", "8000")
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr

    def test_writes_message(self):
        self.protocol.sendMessage('bob')
        self.assertTrue(self.protocol.transport.msgs[0] == "'bob'")
        
    def test_sends_connect_on_start(self):
        self.protocol.startProtocol()
        self.protocol.reactor.advance(5)
        self.assertTrue(len(self.protocol.transport.msgs) > 0)

    # def test_sends_hearbeat_on_interval(self):
    #     self.assertTrue(False)

    # def test_sends_exit_message_on_exit(self):
    #     self.assertTrue(False)

    # def test_decodes_received_datagram(self):
    #     self.assertTrue(False)
