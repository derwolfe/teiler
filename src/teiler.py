import argparse
import os
import sys
import utils
from actions import server
from twisted.python import log
from twisted.internet import reactor
import filetransfer
from filetransfer import FileReceiverFactory
from peerdiscovery import PeerDiscovery
    
# the main entry point for the application
# for simplicity, let's decide that the user decides at runtime to listen
# and the server decides to serve

class Teiler:
    def __init__(self):
        self.address = utils.getLiveInterface()
        self.sessionID = utils.generateSessionID()
        self.peers = []
        self.messages = []
        self.multiCastAddress = '230.0.0.30'
        self.multiCastPort = 8005
        self.tcpPort = 9988
        self.downloadPath = "/home/armin/Downloads"
        
def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()
    
    # Initialize peer discovery using UDP multicast
    multiCastPort = 8006
    teiler = Teiler()
    teiler.multiCastPort = multiCastPort
    reactor.listenMulticast(multiCastPort, PeerDiscovery(teiler), listenMultiple=True)
    log.msg("Initiating Peer Discovery")
    
    #Initialize file transfer service
    fileReceiver = FileReceiverFactory(teiler)
    reactor.listenTCP(teiler.tcpPort, fileReceiver)
    log.msg("Starting file listener on ", teiler.tcpPort)
    
    filetransfer.sendFile("/home/armin/tempzip.zip",port=teiler.tcpPort,address=teiler.address)
    reactor.run()
    
if __name__  == '__main__':
    main()
