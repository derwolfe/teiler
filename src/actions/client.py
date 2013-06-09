from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

fileserver = ''

class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        # this could be placed in a config
        self.transport.joinGroup(self.host)

    def datagramReceived(self, datagram, address):
        print "Received: " + repr(datagram)
        fileserver = repr(datagram)
        print fileserver

        # this will need more checking - it is killing the conn once it receives the address
        self.transport.loseConnection()
            
def downloadFiles():
    """connect to the fileserver and download all files listed under the host.
    This is a good candidate for requests!
    """
    pass
    
# once you receive the message then add it to the 

def main():
    print "Listening"
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    
    reactor.run()

if __name__ == '__main__':
    main()
