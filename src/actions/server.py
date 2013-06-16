import sys

from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

from . import utils 

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
        log.msg("Serving on {0}:8888 and broadcasting IP on 224.0.0.5:8005".format(self.ip))
        self.transport.joinGroup(self.host)
        self._call = task.LoopingCall(self.sendHeartbeat)
        self._loop = self._call.start(5)

    def sendHeartbeat(self):
        message ='{0}:8888'.format(self.ip)
        self.transport.write(message, (self.host, self.port))

    def stopProtocol(self):
        self._call.stop()

def main():
    # XXX this should be injected
    log.startLogging(sys.stdout)
    serve_at = utils.get_live_interface()

    utils.make_file_list(utils.list_files, utils.list_dirs))
    
    log.msg("Starting fileserver on{0}:8888".format(serve_at))
    reactor.listenTCP(8888, factory) 

    log.msg("Broadcasting")
    reactor.listenMulticast(8005, Broadcaster(serve_at)) 
    reactor.run()

if __name__ == "__main__":
    main()
