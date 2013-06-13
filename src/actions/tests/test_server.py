# these should test twisted specific code ONLY

from .. import server
from .. import utils 
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

# do you test that it broadcasts or that its broadcasts can be heard?
class BroadcastServerTests(unittest.TestCase):
    def setUp(self):
        self.protocol = server.Broadcaster('1.1.1.1')
        self.transport.protocol = self.protocol
        
    def test_broadcasting(self):
        """ does it broadcast correctly?"""
        self.fail()


class FileServerTests(unittest.TestCase):

    def test_Fileserver(self):
        self.fail()

class FileWalkerTests(unittest.TestCase):
   
    def test_dir(self):
        f = utils.list_files()
        print f
        self.assertTrue(f[0] == 'fakeDir/file1')

