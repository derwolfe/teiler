from twisted.python import log
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        self.transport.joinGroup(self.host)

    def stopProtocol(self):
        pass

    def datagramReceived(self, datagram, address):
        log.msg("Received: " + repr(datagram))
        


def main():
    log.msg("Starting listener")
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    reactor.run()

if __name__ == '__main__':
    main()
