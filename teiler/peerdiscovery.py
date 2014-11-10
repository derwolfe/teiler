"""
peerdiscovery

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

from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log


HEARTBEAT = "HEARTBEAT"


class PeerList(object):
    """
    A simple structure meant to manage the other peers. Supports a limited
    set of operations, such as add, remove, exists, and count.
    """

    def __init__(self):
        self._peers = {}

    def add(self, peer):
        self._peers[peer.peerId] = peer

    def get(self, peerId):
        return self._peers.get(peerId)

    def remove(self, peerId):
        del self._peers[peerId]

    def exists(self, peerId):
        return self._peers.get(peerId) is not None

    def count(self):
        return len(self._peers.keys())

    def all(self):
        """ return an iterable """
        return self._peers.itervalues()


class PeerDiscoveryMessage(object):
    """
    Contains basic location information for clients to use to initiate a
    connection with this peer. Basically, just the user is, what ip they
    are using, and what port to connect on
    """
    def __init__(self, message, name, address, port):
        if isinstance(message, str):
            message = unicode(message, "utf-8")
        if isinstance(name, str):
            name = unicode(name, "utf-8")
        if isinstance(message, str):
            address = unicode(address, "utf-8")
        self.message = message
        self.name = name
        self.address = address
        self.port = port

    def serialize(self):
        return json.dumps({
            "message": self.message.encode("utf-8"),
            "name": self.name.encode("utf-8"),
            "address": self.address.encode("utf-8"),
            "port": self.port
        })

    @classmethod
    def parseDatagram(cls, datagram):
        """
        Given a datagram formatted using JSON, return a new message object.
        """
        msg = json.loads(datagram)
        peerMsg = msg["message"]
        peerName = msg["name"]
        peerAddress = msg["address"]
        peerPort = msg["port"]
        return cls(peerMsg, peerName, peerAddress, peerPort)


class Peer(object):
    """
    A peer is another user located on a different system. Maintains the user"s
    peerId, username, IP address, and port.
    """
    def __init__(self, name, address, port):
        self.peerId = makePeerId(name, address, port)
        if isinstance(name, str):
            name = unicode(name, "utf-8")
        if isinstance(address, str):
            address = unicode(address, "utf-8")
        self.name = name
        self.address = address
        self.port = port

    def serialize(self):
        return json.dumps({
            "peerId": self.peerId.encode("utf-8"),
            "name": self.name.encode("utf-8"),
            "address": self.address.encode("utf-8"),
            "port": self.port
            })

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
    if isinstance(name, str):
        name = unicode(name, "utf-8")
    if isinstance(name, str):
        address = unicode(name, "utf-8")
    return u"{0}_{1}_{2}".format(name, address, port)


# xxx - https://twistedmatrix.com/documents/14.0.0/_downloads/udpbroadcast.py
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
    :param name: the username you"d like to broadcast.
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
        self._peers = peerList
        self.peerId = makePeerId(name, address, port)
        self.name = name
        self.reactor = reactor
        # these need to be strings
        self.multiCastAddress = multiCastAddress
        self.multiCastPort = multiCastPort
        self.address = address
        self.port = port
        self.loop = None

    def sendMessage(self, message):
        self.transport.write(message,
                             (self.multiCastAddress, self.multiCastPort))

    # XXX some of this belongs in a service that uses the protocol.
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

    # XXX this could be implemented as a looping call check on the client.
    # every X seconds check if the client has posted in the last five seconds.
    # if no, remove, otherwise keep.
    def stopProtocol(self):
        pass

    def datagramReceived(self, datagram, address):
        """
        Handles how datagrams are read when they are received. Here, as this
        is a json serialised message, we are pulling out the peer information
        and placing it in a list.
        """
        parsed = PeerDiscoveryMessage.parseDatagram(datagram)
        peerId = makePeerId(parsed.name, parsed.address, parsed.port)
        # ignore those messages from yourself
        if parsed.address == self.address:
            return
        log.msg("Decoding:{0} from {1}", datagram, address)
        if parsed.message == HEARTBEAT:
            # if the user is culled, then the code to update timestamps
            # might fit well here...
            if not self._peers.exists(peerId):
                newPeer = Peer(parsed.name, parsed.address, parsed.port)
                self._peers.add(newPeer)
                log.msg("new Peer: address: {0}", parsed.name)
