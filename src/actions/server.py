import sys

from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol

from . import utils 

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
        
def main(serve_dir):
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    resource = File(serve_dir) 
    factory = Site(resource)
    serve_at = utils.get_live_interface()
    # file list work
    file_list = utils.make_file_list(serve_dir)
    # file name should be created at startup
    utils.save_file_list(file_list, serve_dir, "teiler-list.txt")

    log.msg("Starting fileserver on{0}:8888".format(serve_at))
    reactor.listenTCP(8888, factory) 
    log.msg("Broadcasting")
    reactor.listenMulticast(8005, Broadcaster(serve_at)) 
    reactor.run()

if __name__ == "__main__":
    main('./')
