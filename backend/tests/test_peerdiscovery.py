#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.trial import unittest
from twisted.internet import task

from ..peerdiscovery import (
    PeerDiscoveryMessage, Peer, PeerDiscoveryProtocol, HEARTBEAT, EXIT,
    makePeerId, PeerList)


class FakeUdpTransport(object):
    """
    Instead of connecting through the network, this transport
    writes the broadcast messages to a variable that can be
    checked.
    """

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
        self.myAddr = "1.1.1.1"
        self.myAddrPort = 9203
        self.myUdpPort = 8000
        self.user = "test"
        self.peers = PeerList()
        self.protocol = PeerDiscoveryProtocol(self.clock,
                                              self.peers,
                                              self.user,
                                              self.myAddr,
                                              self.myAddrPort,
                                              self.myAddr,
                                              self.myUdpPort)
        self.tr = FakeUdpTransport()
        self.protocol.transport = self.tr

    def test_writes_message(self):
        self.protocol.sendMessage("bob")
        self.assertTrue(self.protocol.transport.msgs[0] == "'bob'")

    def test_received_message_from_self_do_not_add(self):
        """The new peer should not be added as it is equal to the host."""
        dg = PeerDiscoveryMessage(self.user,
                                  self.user,
                                  self.myAddr,
                                  self.myUdpPort).serialize()
        self.protocol.datagramReceived(dg, "192.168.1.1")
        self.assertTrue(self.peers.count() == 0)

    def test_received_message_from_peer_add(self):
        dg = PeerDiscoveryMessage(HEARTBEAT,
                                  "bob",
                                  "192.168.1.2",
                                  1232).serialize()
        self.protocol.datagramReceived(dg, ("192.168.1.2", 1232))
        self.assertTrue(self.peers.count() > 0)

    def test_remove_peer_on_receipt_of_exit_message(self):
        dg = PeerDiscoveryMessage(EXIT, "bob", "192.168.1.1", 8000).serialize()
        p = Peer("bob", "192.168.1.1", 8000)
        self.peers.add(p)
        self.protocol.datagramReceived(dg, "192.168.1.1")
        self.assertTrue(self.peers.count() == 0)

    def test_sends_messages_on_loop(self):
        self.protocol.startProtocol()
        self.protocol.reactor.advance(10)
        # there should be two messages delivered over the
        # dinterval of 10 seconds
        self.protocol.stopProtocol()  # this keeps the reactor clean
        self.assertTrue(len(self.protocol.transport.msgs) == 2)

    def test_different_peer_is_added(self):
        p = Peer("jeff", "192.168.1.1", 8000)
        peerId = makePeerId(p.name, p.address, p.port)
        self.peers.add(p)
        self.assertTrue(self.peers.exists(peerId))

    def test_sends_exit_message_on_exit(self):
        # check that stop protocol sends an exit message
        self.protocol.startProtocol()  # needed to get a loop object to cancel
        self.protocol.stopProtocol()
        self.assertTrue("EXIT" in self.protocol.transport.msgs[1])

    def test_kills_looping_call(self):
        self.protocol.startProtocol()  # loop started, could this be mocked?
        self.assertTrue(self.protocol.loop.running is True)
        self.protocol.stopProtocol()
        self.assertTrue(self.protocol.loop.running is False)


class UnicodePeerName(unittest.TestCase):

    def setUp(self):
        self.peer = Peer("wölfe", "192.168.1.1", 8000)

    def test_utf8_name_sent_as_bytes(self):
        self.assertEquals(self.peer.name, u"w\xf6lfe")


class UnicodePeerMessageTests(unittest.TestCase):

    def setUp(self):
        self.message = PeerDiscoveryMessage(EXIT, "wölfe", "192.168.1.1", 8000)

    def test_utf8_peer_message_sent_as_bytes(self):
        self.assertEquals(self.message.name, u"w\xf6lfe")
