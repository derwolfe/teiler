from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

from actions import locate

# serves the files in the current directory 
resource = File('.') # serve the pwd
factory = Site(resource)

# Broadcast a message that the service is alive on this address
class Broadcaster(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self):
        self.ip = locate.get_live_interface()

    def sendHeartbeat(self):
        self.transport.write(self.ip)

    def startProtocol(self):
        print "Serving on {0}:8888 and broadcasting IP on 224.0.0.1:8005".format(self.ip)
        self._call = task.LoopingCall(self.sendHeartbeat)
        self._loop = self._call.start(15)
        
    def stopProtocol(self):
        self._call.stop
    
        

def main():
    # file server
    reactor.listenTCP(8888, factory) 
    # multicast UDP server
    reactor.listenMulticast(8005, Broadcaster()) #don't listen for responses, just broadcast
    reactor.run()


if __name__ == "__main__":
    main()
