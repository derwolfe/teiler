"""
peerdiscovery.py

The process is simple.
1) Start up the client and broadcast a UDP datagram on a defined interval.
2) Listen for other datagrams
3) When another datagram is heard, pull it into the list of the peers.
    But, if the peer is already in the list, do nothing.
4) On disconnect, the client sends an exit message, letting the other
    users know that they are no longer online; making it safe for the
    client to disconnect
"""
import json

from zope import interface
from twisted.python import log
from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol


HEARTBEAT = "HEARTBEAT"
EXIT = "EXIT"


class IPeerList(interface.Interface):

    def add(peer):
        """
        Add a peer to the list.
        """

    def remove(peerId):
        """
        Remove a peer from the list.
        """

    def exists(peerId):
        """
        Tell whether a peer is in the list.
        """

    def count():
        """
        Return the number of peers in the list.
        """


class PeerList(object):
    """
    A simple structure meant to manage the other peers. Supports a limited
    set of operations, such as add, remove, exists, and count.
    """

    interface.implements(IPeerList)

    def __init__(self):
        self._peers = {}

    def add(self, peer):
        self._peers[peer.peerId] = peer

    def remove(self, peerId):
        del self._peers[peerId]

    def exists(self, peerId):
        return self._peers.get(peerId) is not None

    def count(self):
        return len(self._peers.keys())


def makePeerId(name, address, port):
    """
    Create a unique peerId for a peer.

    :param name: the name of a peer
    :param address: the ip address of a peer
    :param port: the port being used

    :returns string: an peerId
    """
    return name + '_' + address + '_' + str(port)


class PeerDiscoveryMessage(object):
    """
    Contains basic location information for clients to use to initiate a
    connection with this peer. Basically, just the user is, what ip they
    are using, and what port to connect on
    """
    def __init__(self, message, name, address, port):
        self.message = str(message)
        self.name = str(name)
        self.address = str(address)
        self.port = str(port)

    def serialize(self):
        return json.dumps({
            "message": self.message,
            "name": self.name,
            "address": self.address,
            "port": self.port
        })

    @classmethod
    def parseDatagram(klass, datagram):
        """
        Given a datagram formatted using JSON, return a new message object.
        """
        msg = json.loads(datagram)
        peerMsg = msg['message']
        peerName = msg['name']
        peerAddress = msg['address']
        peerPort = msg['port']
        return klass(peerMsg, peerName, peerAddress, peerPort)


class Peer(object):
    """
    A peer is another user located on a different system. Maintains the user's
    peerId, username, IP address, and port.
    """
    def __init__(self, name, address, port):
        self.peerId = makePeerId(name, address, port)
        self.name = name
        self.address = address
        self.port = port

    def __str__(self):
        return self.peerId

    def __eq__(self, other):
        return self.peerId == other.peerId


class PeerDiscoveryProtocol(DatagramProtocol):
    """
    UDP protocol used to find others running the same program.
    The protocol will do several things, on program start, a connection
    message will be sent; basically announcing itself as a node to the network.
    Then the protocol will regularly send a heartbeat message at a defined
    interval.

    Once the peer has decided to disconnect, it will send an exit message to
    alert the other nodes of its demise.

    :param reactor: the reactor being used.
    :param peers: a data structure in which peers can be stored, implements
    IPeerList
    :param name: the username you'd like to broadcast.
    :param multiCastAddress: the multicast address to broadcast.
    :param multiCastPort: the port on which to broadcast.
    :param address: the IP address to broadcast. This is for the current user.
    :param port: the Port to broadcast where other users can connect.
    """
    def __init__(self, reactor, peerList, name, multiCastAddress,
                 multiCastPort, address, port):
        """
        Set up an instance of the PeerDiscovery protocol by creating
        the message information needed to broadcast other instances
        of the protocol running on the same network.
        """
        interface.verify.verifyObject(IPeerList, peerList)

        self.peers = peerList
        self.peerId = makePeerId(name, address, port)
        self.reactor = reactor
        self.name = name
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.address = address
        self.port = port
        self.loop = None

    def sendMessage(self, message):
        self.transport.write(message,
                             (self.multiCastAddress, self.multiCastPort))

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.multiCastAddress)
        self.loop = task.LoopingCall(self.sendHeartBeat)
        self.loop.start(5)

    def sendHeartBeat(self):
        """
        Sends message alerting other peers to your presence.
        """
        message = PeerDiscoveryMessage(HEARTBEAT,
                                       self.name,
                                       self.address,
                                       self.port).serialize()
        self.sendMessage(message)
        log.msg("Sent " + message)

    def stopProtocol(self):
        """
        Gracefully tell peers to remove you.
        """
        message = PeerDiscoveryMessage(EXIT,
                                       self.name,
                                       self.address,
                                       self.port).serialize()
        self.sendMessage(message)
        self.loop.stop()
        log.msg("Exit " + message)

    def datagramReceived(self, datagram, address):
        """
        Handles how datagrams are read when they are received. Here, as this
        is a json serialised message, we are pulling out the peer information
        and placing it in a list.
        """
        log.msg("Decoding: " + datagram + " from ", address)
        parsed = PeerDiscoveryMessage.parseDatagram(datagram)
        peerId = makePeerId(parsed.name, parsed.address, parsed.port)
        if parsed.message == EXIT:
            if self.peers.exists(peerId):
                log.msg('dropping peer:', address)
                self.peers.remove(peerId)
        elif parsed.message == HEARTBEAT:
            if not self.peers.exists(peerId):
                newPeer = Peer(parsed.name, parsed.address, parsed.port)
                self.peers.add(newPeer)
                log.msg("new Peer: address: {0}", parsed.name)
