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
from twisted.internet import task, reactor
from twisted.internet.protocol import DatagramProtocol 
from peerlist import TeilerPeer

connectMsg = "CONNECT"
heartbeatMsg = "HEARTBEAT"
exitMsg = "EXIT"

class Message(object):
    """mesage to be sent across the wire"""
    def __init__(self, message, name, address, tcpPort, sessionID):
        self.message = str(message)
        self.name = str(name)
        self.address = str(address)
        self.tcpPort = str(tcpPort)
        self.sessionID = str(sessionID)

    def serialize(self):
        return json.dumps({
                "message": self.message,
                "name": self.name,
                "address" : self.address,
                "tcpPort" : self.tcpPort,
                "sesionID" : self.sessionID
                })

class PeerDiscovery(DatagramProtocol):
    """
    UDP protocol used to find others running the same program.
    """
    def __init__(self, teiler):
        """Set up a list into which peers can be placed."""
        self.peers = []

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.teiler.multiCastAddress)
        message = Message(connectMsg,
                          self.teiler.name, 
                          self.teiler.address, 
                          self.teiler.tcpPort, 
                          self.teiler.sessionID
                          ).serialize()
        
        self.transport.write(message, (self.teiler.multiCastAddress, 
                                       self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(connectMsg, message))      
        
        self._call = task.LoopingCall(self.sendHeartBeat)
        self._loop = self._call.start(5)

    def sendHeartBeat(self):
        message = Message(heartbeatMsg, 
                          self.teiler.name, 
                          self.teiler.address, 
                          self.teiler.tcpPort, 
                          self.teiler.sessionID
                          ).serialize()

        self.transport.write(message, 
                             (self.teiler.multiCastAddress, 
                              self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(heartbeatMsg, message))

    def stopProtocol(self):
        message = Message(exitMsg, 
                          self.teiler.name, 
                          self.teiler.address, 
                          self.teiler.tcpPort, 
                          self.teiler.sessionID
                          ).serialize()

        self.transport.write(message, 
                             (self.teiler.multiCastAddress, 
                              self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(exitMsg, message))

    def datagramReceived(self, datagram, address):
        log.msg("Decoding: {0}".format(datagram))
        message = json.loads(datagram)
        peerName = message['name']
        peerAddress = message['address']
        log.msg("Peer: Address: {0} Name: {1}".format(peerAddress, peerName))

        log.msg("Does the list contain? {0}".format(self.teiler.peerList.contains(peerName)))    
        if peerName not in self.peers:
            newPeer = TeilerPeer(peerAddress, peerName)
            self.peers.append(newPeer)
            log.msg("Added new Peer: address: {0}, name: {1}".format(peerAddress, peerName))
            
