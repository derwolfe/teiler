from src.server import Broadcaster
from twisted.trial import unittest
#from twisted.test import proto_helpers


class BroadcastServerTests(unittest.TestCase):
    def setUp(self):
        broadcaster = Broadcaster()
    #     d = server.startedDeferred = defer.Deferred()
    #     p = reactor.listenUDP(0, server, interface="127.0.0.1")
    #             def cbStarted(ignored):
    #         addr = p.getHost()
    #         self.assertEquals(addr, ('INET_UDP', addr.host, addr.port))
    #         return p.stopListening()
    #     return d.addCallback(cbStarted)
    # testOldAddress.suppress = [
    #     util.suppress(message='IPv4Address.__getitem__',
    #                   category=DeprecationWarning)]

    def test_broadcasting(self):
        self.fail


class FileServerTests(unittest.TestCase):
    def test_Fileserver(self):
        self.fail
