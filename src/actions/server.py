from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

# serves the files in the current directory 
resource = File('.') # serve the pwd
factory = Site(resource)

# Broadcast a message that the service is alive on this address
class Broadcaster(DatagramProtocol):

    def startProtocol(self):
        """
        Gets called once the listener has begun, handles configuration.
        """
        # only the local network, no jumping to another router level
        self.transport.setTTL(1)
        # set the multicast group
        self.transport.joinGroup("224.0.0.1") # this is the all hosts address

    # def datagramReceived(self, datagram, address):
    #     if datagram == "UniqueID":
    #         print "Server received:" + repr(datagram)
    #         self.transport.write("data", address)

def main():
    print "Serving on {0}:8888 and broadcasting IP on 224.0.0.1:8005".format(0)
    #get_ip()
    # file server
    reactor.listenTCP(8888, factory) 
    # multicast UDP server
    reactor.listenMulticast(8005,    
                            Broadcaster(), 
                            listenMultiple=False) #don't listen for responses, just broadcast
    reactor.run()


if __name__ == "__main__":
    main()
