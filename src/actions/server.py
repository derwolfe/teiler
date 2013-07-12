import sys

from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol

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
    from twisted.internet import reactor, thread
    log.startLogging(sys.stdout)
    log.msg("Broadcasting")

    reactor.listenMulticast(8005, Broadcaster(serve_at)) 
    reactor.run()


