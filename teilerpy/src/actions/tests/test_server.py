# these should test twisted specific code ONLY

from .. import server
from twisted.internet.interfaces import IMulticastTransport
from twisted.trial import unittest

#class Listener(DatagramProtocol):
#    
#    def __init__(self):
#        # hold the messages
#        self.reads = []
#
#    def datagramReceived(self, datagram, address):
#        self.reads.append(repr(datagram))


class BroadcastServerTests(unittest.TestCase):
    def setUp(self):
        broadcaster = server.Broadcaster('1.1.1.1')
        
    def test_broadcasting(self):
        """ does it broadcast correctly?"""
        self.fail()


class FileServerTests(unittest.TestCase):
    def test_Fileserver(self):
        self.fail()


