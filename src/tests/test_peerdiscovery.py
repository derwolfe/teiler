import os
import shutil

from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest

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

class BroadcastServerTests(unittest.TestCase):

    def setUp(self):
        self.protocol = server.Broadcaster('1.1.1.1')
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr
        
    def test_broadcast(self):
        self.protocol.sendHeartbeat()
        self.assertTrue(self.tr.msgs[0] == "'1.1.1.1:8888'")


