from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol

# serves the files in the current directory 
resource = File('.') # serve the pwd
factory = Site(resource)

# Broadcast a message that the service is alive on this address
class BroadcastAddress(DatagramProtocol):

    def startProtocol(self):
        """
        Gets called once the listener has begun, handles configuration.
        """
        self.transport.setTTL(1)
        # set the multicast group
        self.transport.joinGroup("224.0.0.1") # this is the all hosts address

    

reactor.listenTCP(8888, factory)
reactor.listenMulticast(8005, 
                        BroadcastAddress(), 
                        listenMultiple=false) #don't listen for responses, just broadcast
reactor.run()
