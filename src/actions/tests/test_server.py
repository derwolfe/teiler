import os
import shutil

from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest

from .. import server



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
        self.protocol = server.Broadcaster()
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr
        
        
    def test_broadcast(self):
        self.protocol.sendMessage('hi')
        self.assertTrue(len(self.tr.msgs) > 0)
        self.assertTrue(self.tr.msgs[0] == "'hi'")

    def test_datagram_received(self):
        self.protocol.sendMessage("kowabunga")
        # you are testing what happens when a msg is REC by the protocol.
        # meaning you have to SEND the protocol to the client.
        # i.e. self.tr.send...
        


        
        


