# these should test twisted specific code ONLY

from src.server import Broadcaster
from twisted.trial import unittest
#import unittest

"""
Make a broadcaster and add a listener?
"""
class Listener(DatagramProtocol):
    
    def __init__(self):
        # hold the messages
        self.reads = []

    def datagramReceived(self, datagram, address):
        self.reads.append(repr(datagram))


class BroadcastServerTests(unittest.TestCase):
    def setUp(self):
        broadcaster = Broadcaster('1.1.1.1')
        listener = Listener()
        
    def test_broadcasting(self):
        """ does it broadcast correctly?"""
        self.fail


class FileServerTests(unittest.TestCase):
    def test_Fileserver(self):
        self.fail


