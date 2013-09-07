from json import dumps, loads
from math import fabs
from os import path, stat
from twisted.python import log
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from utils import getFilenameFromPath

# commands

CREATE_NEW_FILE = "NEW_FILE"

class FileTransferMessage(object):
    """
    This contains all of the information that will be exchanged to 
    send a file. It will be sent for each file that is to be exchanged.
    """
    def __init__(self, 
                 file_size, 
                 write_to,
                 command
                 ):
        """
        :param file_size: the string lenth of a file to be sent
        :type file_size: int

        :param write_to: the file name, including its relative path on the 
        senders machine. E.g. ``/movies/evil\ dead 2.avi``. This allows
        the directory structure to be preserved.
        :type write_to: string
        """
        self.file_size = file_size
        self.write_to = write_to
        self.command = command

    def serialize(self):
        """
        returns a json serialized version of a L{Message} object.
        """
        return dumps({
            "file_size" : self.file_size,
            "write_to" : self.write_to,
            "command": self.command
            })

    def __str__(self):
        return self.serialize()

    @classmethod
    def from_str(cls, line):
        """
        A class method that returns a new L{Message} instance.

        :param line: a json formatted line of a message
        :type line: string
        """
        from_msg = loads(line)
        cls.file_size = from_msg["file_size"]
        cls.write_to = from_msg["write_to"]
        cls.command = from_msg["command"]
        return cls
    

class FileReceiverProtocol(LineReceiver):
    """
    protocol that will be used to transfer files/raw data.
    """

    def __init__(self, downloadPath):
        self.outfile = None
        self.remain = 0
        self.downloadPath = downloadPath
        
    def lineReceived(self, line):
        """
        Line received takes a message line, creates a message from it that 
        the system understand, then sends it along to the a function
        that knows what to do next
        """
        # NEW_FILE : send new file
        # VALIDATE: check file with crc
        d = Deferred()
        log.msg("lineReceived: " + line) 
        msg = FileTransferMessage.from_str(line)
        
        d.addCallback(self._handleReceivedMessage)
        d.addErrback(self._handleError)
        # invoke the callback...this might be right
        d.callback(msg)

    def _handleError(self):
        print "SHIT\n"
        log.msg("tried to handle the message, but, rut ro, i'm dead")
        
    def _handleReceivedMessage(self, _fromSender):
        """
        Parse the message sent from a FileSender and figure out 
        which of the commands it would like you to run.
        
        :param fromSender: a FileTransferMessage containing a command
        :type fromSender: FileTransferMessage
        """
        command = _fromSender.command
        if command == CREATE_NEW_FILE:
            self.size = _fromSender.file_size
            self.write_to = _fromSender.write_to
            self.out_fname = path.join(self.downloadPath, 
                                       self.write_to)
            log.msg("* Receiving into file @" + self.out_fname)
            # could you use a callback to open the file, then attach a callback 
            # to it to begin consuming?
            try:
                self.outfile = open(self.out_fname,'wb')
            except Exception, value:
                log.msg("! Unable to open file {0} {1}".format(self.out_fname, 
                                                               value))
                # for now just return
                return
            log.msg("Entering raw mode. {0} {1}".format(self.outfile, 
                                                        self.remain))
            self.setRawMode()
        else: 
            return

    def rawDataReceived(self, data):
        # check for overwrite of buffer
        rem_no = self._over_shot_length(len(data))
        if self.remain > 0:
            if self.remain % 10000 == 0:
                log.msg("remaining {0}/{1}".format(self.remain, self.size))
            self.remain -= len(data)
            # write the current amount of data to the file            
            self.outfile.write(data)
        # it is possible the file is finished being written to at this point
        if self.remain <= 0:
            log.msg("writing of file finished. Total len: {0}/{1}"\
                    .format(self.remain, self.size))
            # closing the file and seting line mode might be better done 
            # with the event, finishedWriting being triggered
            self.outfile.close()
            # also pass the remainder to line mode
            self.setLineMode(data[rem_no:])

    def _over_shot_length(self, data_length):
        """
        Use this to find out how much you have over shot the buffer
        always returns a positive number
        """
        return int(fabs(self.remain - data_length))
            

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
            print remove_base + self.out_fname + reason
            remove(self.out_fname)

        # Success uploading - tmpfile will be saved to disk.
        else:
            log.msg("--> finished saving upload@ " + self.out_fname)
            client = self.instruction.get('client', 'anonymous') #? what is this

class FileReceiverFactory(ServerFactory):

    protocol = FileReceiverProtocol

    def __init__(self, downloadPath):
        self.downloadPath = downloadPath
        
    def buildProtocol(self, addr):
        p = self.protocol(self.downloadPath)
        p.factory = self
        return p

class FileSenderClient(basic.LineReceiver):
    """ 
    file sender 
    """
    def __init__(self, path, controller):
        """ """
        self.path = path
        self.controller = controller
        self.infile = open(self.path, 'rb')
        self.insize = stat(self.path).st_size
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
