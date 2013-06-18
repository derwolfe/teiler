import os
import shutil

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
        self.assertTrue(False)

class UtilsTests(unittest.TestCase):
    
    def setUp(self):
        self.home = "./"
        self.test_dir = "./test_dir"
        self.test_file= "./test_dir/test_file"
        os.chdir(self.home)
        os.mkdir(self.test_dir)
        open(self.test_file, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_lists_files(self):
        results = utils._list_files(self.test_dir)
        self.assertTrue(results[0] == self.test_file)

    def test_lists_dirs(self):
        results = utils._list_dirs(self.test_dir)
        self.assertTrue(results[0] == self.test_dir)

    def test_make_file_list(self):
        result = utils.make_file_list(self.home).replace("\n", " ")
        file_list = "**dirs ./ ./test_dir **files ./_trial_marker ./test.log ./test_dir/test_file "
        self.assertTrue(file_list == result)



        
        


