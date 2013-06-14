# these should test twisted specific code ONLY
from zope.interface import implements

from twisted.internet.interfaces import IMulticastTransport, IUDPTransport
from twisted.trial import unittest

# should these contain src?
from .. import server
from .. import utils 
from .. import client

class FakeUdpTransport(object):
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

# do you test that it broadcasts or that its broadcasts can be heard?
class BroadcastServerTests(unittest.TestCase):
    def setUp(self):
        self.protocol = server.Broadcaster('1.1.1.1')
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr
        
    def test_broadcast(self):
        """ does it broadcast correctly?"""
        self.protocol.sendHeartbeat()
        self.assertTrue(len(self.tr.msgs) > 0)
        self.assertTrue(self.tr.msgs[0] == "'1.1.1.1:8888'")

class ClientTests(unittest.TestCase):
    pass
        

class FileServerTests(unittest.TestCase):

    def test_Fileserver(self):
        self.assertTrue(True)

class FileWalkerTests(unittest.TestCase):
   
    def test_dir(self):
        f = utils.list_files()
        # you should make fake files and call them. this should be absolute
        self.assertTrue(True)
