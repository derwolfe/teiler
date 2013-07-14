import argparse
import os
import sys
import utils
from actions import server
from twisted.python import log
from twisted.internet import reactor

from peerdiscovery import PeerDiscovery
    
# the main entry point for the application
# for simplicity, let's decide that the user decides at runtime to listen
# and the server decides to serve

# location from which files should be served
_home = os.path.expanduser("~")
_app_directory = os.path.join(os.path.expanduser("~"), "blaster")

class Teiler:
    def __init__(self):
        self.address = utils.getLiveInterface()
        self.sessionID = utils.generateSessionID()
        self.peers = []
        self.messages = []
        self.multiCastAddress = '230.0.0.30'
        self.multiCastPort = 8005
        
def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()
    multiCastPort = 8006
    teiler = Teiler()
    teiler.multiCastPort = multiCastPort
    log.startLogging(sys.stdout)
    log.msg("Initiating Peer Discovery")

    broadcaster = PeerDiscovery(teiler)
    
    reactor.listenMulticast(multiCastPort, broadcaster, listenMultiple=True) 
    reactor.run()

def _app_runner():
    if os.path.exists(_app_directory) == False:
            os.mkdir(_app_directory)
    server.main()
    
if __name__  == '__main__':
    main()
