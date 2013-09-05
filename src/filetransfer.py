from binascii import crc32
import os, json

from twisted.python import log
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from utils import getFilenameFromPath

class FileReceiverMessage(object):
    """
    This contains all of the information that will be exchanged to send a file.
    """
    def __init__(self, 
                 file_size, 
                 read_from,
                 write_to
                 ):
        self.file_size = file_size
        self.read_from = read_from
        self.write_to = write_to

    def serialize(self):
        return json.dumps({
            "file_size" : self.file_size,
            "read_from" : self.read_from,
            "write_to" : self.write_to
            })

    @classmethod
    def from_str(self, line):
        """alternate construct for a message, makes properties a 
        bit simpler to read
        """
        # possible use attr.get instead of direct access!
        from_msg = json.loads(line)
        self.file_size = from_msg.file_size
        self.read_from = from_msg.read_from
        self.write_to = from_msg.write_to


class FileReceiverProtocol(LineReceiver):
    """protocol that will be used to transfer files/raw data."""

    def __init__(self, downloadPath):
        self.outfile = None
        self.remain = 0
        # self.crc = 0
        self.downloadPath = downloadPath
        
    def lineReceived(self, line):
        # maybe you need to explicitly check for the keys before running
        log.msg("lineReceived: " + line)
        msg = Message(line)
        #self.instruction.update(dict(client=self.transport.getPeer().host))
        ## parse the instruction
        self.size = msg.file_size
        self.original_fname = msg.read_from
        self.outfilename = os.path.join(self.downloadPath, self.original_fname)
        log.msg("* Receiving into file @" + self.outfilename)
        try:
            self.outfile = open(self.outfilename,'wb')
        except Exception, value:
            log.msg("! Unable to open file {0} {1}".format(self.outfilename, 
                                                           value))
            # might be a good place for an errback
            self.transport.loseConnection()
            return
        self.remain = int(self.size)
        log.msg("Entering raw mode. {0} {1}".format(self.outfile, 
                                                      self.remain))
        self.setRawMode()


    def rawDataReceived(self, data):
        if self.remain % 10000 == 0:
            log.msg("remaining {0}/{1}".format(self.remain, self.size))
        self.remain -= len(data)
        # worry about this later, it should be sent as well so you can
        # compare the hashes before and after
        #self.crc = crc32(data, self.crc)
        self.outfile.write(data)
        # does this drop off once all data has been received? 
        # you could probably switch back to message mode after this is finished
        if self.remain == 0:
            # close the file handle as you are no longer using it
            self.outfile.close()
            self.setLineMode()
        
    def connectionMade(self):
        basic.LineReceiver.connectionMade(self)

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        if self.outfile:
            self.outfile.close()
        # Problem uploading - tmpfile will be discarded
        if self.remain != 0:
            print str(self.remain) + ')!=0'
            remove_base = '--> removing tmpfile@'
            if self.remain < 0:
                reason = ' .. file moved too much'
            if self.remain > 0:
                reason = ' .. file moved too little'
            print remove_base + self.outfilename + reason
            os.remove(self.outfilename)

        # Success uploading - tmpfile will be saved to disk.
        else:
            print '\n--> finished saving upload@ ' + self.outfilename
            client = self.instruction.get('client', 'anonymous')

class FileReceiverFactory(ServerFactory):

    protocol = FileReceiverProtocol

    def __init__(self, downloadPath):
        self.downloadPath = downloadPath
        
    def buildProtocol(self, addr):
        p = self.protocol(self.downloadPath)
        p.factory = self
        return p

class FileSenderClient(basic.LineReceiver):
    """ file sender """
    def __init__(self, path, controller):
        """ """
        self.path = path
        self.controller = controller
        self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size
        self.result = None
        self.completed = False
        self.controller.file_sent = 0
        self.controller.file_size = self.insize

    def _monitor(self, data):
        self.controller.file_sent += len(data)
        self.controller.total_sent += len(data)
        # Check with controller to see if we've been cancelled and abort
        # if so.
        if self.controller.cancel:
            print 'FileSenderClient._monitor Cancelling'
            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()
            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')
        return data

    def cbTransferCompleted(self, lastsent):
        self.completed = True
        #self.transport.loseConnection()

    def connectionMade(self):
        # this will be the message sent across the wire.
        instruction = dict(file_size=self.insize,
                           original_file_path=self.path)
        self.transport.write(instruction+'\r\n')
        sender = FileSender()
        sender.CHUNK_SIZE = 2 ** 16
        d = sender.beginFileTransfer(self.infile, self.transport,
                                     self._monitor)
        d.addCallback(self.cbTransferCompleted)

    def connectionLost(self, reason):
        from twisted.internet.error import ConnectionDone
        
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost\n  * ', reason.getErrorMessage()
        print ' * finished with',self.path
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)

class FileSenderClientFactory(ClientFactory):
    """ file sender factory """
    protocol = FileSenderClient

    def __init__(self, path, controller):
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        print ' + building protocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p
    
def sendFile(path, address='localhost', port=1234,):
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileSenderClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed
