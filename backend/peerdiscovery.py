"""
Peer Discovery
--------------

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

from twisted.python import log
from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol

HEARTBEAT = "HEARTBEAT"
EXIT = "EXIT"


class Peer(object):
    """
    Meant to store information for the TCP based protocols to use, such as the
    IP address, and port

    Each peer needs some sort of unique identifier. For now, the combination
    of port, address, and name should suffice.
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


def parseDatagram(datagram):
    """
    Given a datagram formatted using JSON, return a new message object.
    """
    msg = json.loads(datagram)
    peerMsg = msg['message']
    peerName = msg['name']
    peerAddress = msg['address']
    peerPort = msg['port']
    return PeerDiscoveryMessage(peerMsg, peerName, peerAddress, peerPort)


class PeerDiscoveryProtocol(DatagramProtocol):
    """
    UDP protocol used to find others running the same program.
    The protocol will do several things, on program start, a connection
    message will be sent; basically announcing itself as a node to the network.
    Then the protocol will regularly send a heartbeat message at a defined
    interval.

    Once the peer has decided to disconnect, it will send an exit message to
    alert the other nodes of its demise.
    """
    def __init__(self, reactor, peers, name, multiCastAddress,
                 multiCastPort, address, port):
        """
        Set up an instance of the PeerDiscovery protocol by creating
        the message information needed to broadcast other instances
        of the protocol running on the same network.
        """
        self.peers = peers  # your list needs to implement append
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
        Handles how datagrams are read when they are received. Here,
        as this is a json serialised message, we are pulling out the
        peer information and placing it in a list.
        """
        log.msg("Decoding: " + datagram + " from ", address)
        parsed = parseDatagram(datagram)
        peerId = makePeerId(parsed.name, parsed.address, parsed.port)
        if parsed.message == EXIT:
            if self.isPeer(peerId):
                log.msg('dropping peer:', address)
                self.removePeer(peerId)
        elif parsed.message == HEARTBEAT:
            if self.isPeer(peerId) is False:
                newPeer = Peer(parsed.name, parsed.address, parsed.port)
                self.addPeer(newPeer)
                log.msg("new Peer: address: {0}", parsed.name)

    def isPeer(self, peerId):
        """
        Is the provided peer already known to this server.

        :param peerId: the peerId to check
        :returns: boolean
        """
        return peerId in self.peers.keys()

    def removePeer(self, peerId):
        """
        remove a peer from the server's known set of peers.
        """
        del self.peers[peerId]

    def addPeer(self, peer):
        """
        Add the given peer to the server's set of peers.

        :param peer: a Peer object.
        """
        self.peers[peer.peerId] = peer
