# these should test twisted specific code ONLY
from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest

# should these contain src?
from .. import server
from .. import utils 
from .. import client

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
        self.assertTrue(len(self.tr.msgs) > 0)
        self.assertTrue(self.tr.msgs[0] == "'1.1.1.1:8888'")

class ClientTests(unittest.TestCase):
    pass
        

class FileServerTests(unittest.TestCase):

    def test_Fileserver(self):
        self.assertTrue(True)

class FileWalkerTests(unittest.TestCase):
   
    def test_list_files(self):
        f = utils.list_files()
        # make dirs in temp
        self.assertTrue(True)
        # check they exist
        # clean them up

    def test_creates_json():
        pass
