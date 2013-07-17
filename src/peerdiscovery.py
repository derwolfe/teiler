import sys, json
from twisted.python import log
from twisted.internet import task, reactor
from twisted.internet.protocol import DatagramProtocol 
from peerlist import TeilerPeer

connectMsg = "CONNECT"
heartbeatMsg = "HEARTBEAT"
exitMsg = "EXIT"

''' Class for message object '''
class Message():
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
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self, teiler):
        self.teiler = teiler

    def startProtocol(self):
        self.transport.setTTL(5)
        self.transport.joinGroup(self.teiler.multiCastAddress)
        message = Message(connectMsg,
                                     self.teiler.name, 
                                     self.teiler.address, 
                                     self.teiler.tcpPort, 
                                     self.teiler.sessionID).serialize()

        self.transport.write(message, (self.teiler.multiCastAddress, 
                                       self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(connectMsg, message))      
        reactor.callLater(5.0, self.sendHeartBeat)

    def sendHeartBeat(self):
        message = Message(heartbeatMsg, 
                                     self.teiler.name, 
                                     self.teiler.address, 
                                     self.teiler.tcpPort, 
                                     self.teiler.sessionID).serialize()

        self.transport.write(message, 
                             (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(heartbeatMsg, message))
        reactor.callLater(5.0, self.sendHeartBeat)

    def stopProtocol(self):
        message = Message(exitMsg, 
                                     self.teiler.name, 
                                     self.teiler.address, 
                                     self.teiler.tcpPort, 
                                     self.teiler.sessionID).serialize()

        self.transport.write(message, (self.teiler.multiCastAddress, self.teiler.multiCastPort))
        log.msg("Sent {0} message: {1}".format(exitMsg, message))

    def datagramReceived(self, datagram, address):
        log.msg("Decoding: {0}".format(datagram))
        message = json.loads(datagram)
        peerName = message['name']
        peerAddress = message['address']
        log.msg("Peer: Address: {0} Name: {1}".format(peerAddress, peerName))

        log.msg("Does the list contain? {0}".format(self.teiler.peerList.contains(peerName)))    
        if not self.teiler.peerList.contains(peerName):
            newPeer = TeilerPeer(peerAddress, peerName)
            self.teiler.peerList.addItem(newPeer)
            log.msg("Added new Peer: address: {0}, name: {1}".format(peerAddress, peerName))
            
