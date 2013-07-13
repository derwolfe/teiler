import sys

from twisted.python import log

from twisted.internet import task
from twisted.internet.protocol import DatagramProtocol

class Broadcaster(DatagramProtocol):
    """
    Broadcast the ip to all of the listeners on the channel
    """
    def __init__(self):
        self.host = '224.0.0.5'
        self.port = 8005
        self.peers = []
        self.messages = []

    def startProtocol(self):
        self.transport.joinGroup(self.host)
        self._call = task.LoopingCall(self.sendMessage)
        self._loop = self._call.start(5)

    def sendMessage(self, msg):
        self.transport.write(msg, (self.host, self.port))

    def stopProtocol(self):
        self._call.stop()

    def datagramReceived(self, datagram, address):
        # being developed
        self.sendMessage("heard")
        self.messages.append(datagram)

        if self.address != address:
            if address not in self.peers:
                self.peers.append(address)
                log.msg(msg)

def main(serve_dir):
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    log.msg("Broadcasting")

    reactor.listenMulticast(8005, 
                            Broadcaster(serve_at),
                            listenMultiple=True) 
    reactor.run()

if __name__ == '__main__':
    main()
