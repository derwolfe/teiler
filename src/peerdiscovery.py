"""
This module is resposible for peer discovery over UDP only.

The process is simple. 
1) Start up the client and broadcast a UDP datagram on a defined interval.
2) Listen for other packets
3) When another packet is heard, pull it into the list of the peers. 
    But, if the peer is already in the list, do nothing.
4) On disconnect, the client sends an exit message, letting the other 
    users know that they are no longer online; making it safe for the 
    client to disconnect
"""

import sys, json
from twisted.python import log
from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol 

connectMsg = "CONNECT"
heartbeatMsg = "HEARTBEAT"
exitMsg = "EXIT"

class Message(object):
    """Contains basic location information for clients to use
    to initiate a connection with this peer. Basically, just the user is,
    what ip they are using, and what port to connect on
    """
    def __init__(self, message, name, address, tcpPort)
        self.message = str(message)
        self.name = str(name)
        self.address = str(address)
        self.tcpPort = str(tcpPort)
        # is this session id being used to transfer a file over a TCP socket, or to differentiate
        # a set of peers from another? This seems like a token that should be PROVIDED after the connection
        # has been established
        # self.sessionID = str(sessionID)

    def serialize(self):
        return json.dumps({
                "message": self.message,
                "name": self.name,
                "address" : self.address,
                "tcpPort" : self.tcpPort,
                })

class Peer(object):
    """Meant to store information for the TCP based protocols to use, such as the 
    IP address, and port"""
    def __init__(self, name, address, port):
        self.name = name
        self.address = address
        self.port = port

class PeerDiscovery(DatagramProtocol):
    """
    UDP protocol used to find others running the same program. 
    The protocol will do several things, on program start, a connection
    message will be sent; basically announcing itself as a node to the network.
    Then the protocol will regularly send a heartbeat message at a defined interval.
    Once the peer has decided to disconnect, it will send an exit message to alert 
    the other nodes of its demise.
    """
    def __init__(self):
        """Set up a list into which peers can be placed."""
        self.peers = []

    def sendMessage(self, message):
        self.transport.write(message, self.multiCastAddress, self.multiCastPort)

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.teiler.multiCastAddress)
        log.msg("Sent message: {0}".format(message))      
        # you could send the connect message first THEN send the heart beat if need be
        # using self.sendMessage(self.sendMessage...)
        # then set up the looping call to use an arg with self.sendMessage, (hbMessage))
        self._call = task.LoopingCall(self.sendHeartBeat)
        self._loop = self._call.start(5)

    def sendHeartBeat(self):
        message = Message(heartbeatMsg, 
                          self.teiler.name, 
                          self.teiler.address, 
                          self.teiler.tcpPort, 
                          self.teiler.sessionID
                          ).serialize()
        self.sendMessage(message)
        log.msg("Sent {0} message: {1}".format(heartbeatMsg, message))


    def stopProtocol(self):
        message = Message(exitMsg, 
                          self.teiler.name, 
                          self.teiler.address, 
                          self.teiler.tcpPort, 
                          self.teiler.sessionID
                          ).serialize()
        self.sendMessage(message)
        log.msg("Sent {0} message: {1}".format(exitMsg, message))

    def datagramReceived(self, datagram, address):
        """Handles how datagrams are read when they are received. Here, as this is a json
        serialised message, we are pulling out the peer information and placing it in a 
        list. """
        log.msg("Decoding: {0}".format(datagram))
        msg = json.loads(datagram)
        name = msg['name']
        address = msg['address']
        log.msg("Peer: Address: {0} Name: {1}".format(address, name))

        if peerName not in self.peers and not self.:
            newPeer = Peer(name, address)
            self.peers.append(newPeer)
            log.msg("Added new Peer: address: {0}, name: {1}".format(peerAddress, peerName))
            
