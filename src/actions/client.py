from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

class MulticastClientUDP(DatagramProtocol):
    
    def startProtocol(self):
        self.transport.joinGroup('228.0.0.5')

    def datagramReceived(self, datagram, address):
        print "Received: " + repr(datagram)

def main():
    print "Listening for an IP on 224.0.0.1:8005"
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listen_multiple = True)
    reactor.run()

if __name__ == '__main__':
    main()
