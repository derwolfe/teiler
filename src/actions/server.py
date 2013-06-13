from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

from . import locate

# serves the files in the current directory 
resource = File('.') # serve the pwd
factory = Site(resource)

# Broadcast a message that the service is alive on this address
class Broadcaster(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self, address):
        self.ip = address # shouldn't this be passed in
        self.host = '224.0.0.5'
        self.port = 8005

    def startProtocol(self):
        
        # this should be a call to a logger not a print
        print "Serving on {0}:8888 and broadcasting IP on 224.0.0.5:8005".format(self.ip)
        # doesn't need to be in the group to send
        #self.transport.joinGroup(self.host)
        self._call = task.LoopingCall(self.sendHeartbeat)
        self._loop = self._call.start(5)

    def sendHeartbeat(self):
        message ='{0}:8888'.format(self.ip)
        self.transport.write(message, (self.host, self.port))

    def stopProtocol(self):
        self._call.stop()

    # helps to test?
    #def datagramReceived(self, datagram, address):
    #    print "Sent:{0} from {1}".format(repr(datagram), address)
    

def main():
    # file server
    serve_at = locate.get_live_interface()
    reactor.listenTCP(8888, factory) 
    # multicast UDP server
    reactor.listenMulticast(8005, Broadcaster(serve_at)) 
    reactor.run()


if __name__ == "__main__":
    main()
