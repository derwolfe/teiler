"""

"""

from json import dumps, loads
from math import fabs
from os import path, stat, remove
from twisted.python import log
from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols.basic import FileSender, LineReceiver
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from utils import getFilenameFromPath

# commands
CREATE_NEW_FILE = "NEW_FILE"

# possible errors that can be returned by FileReceiver/TransferProtocol
class UnknownMessageError(Exception):
    """
    Exception raised when a non existent command is called.
    """
    pass

class ParsingMessageError(Exception):
    """
    Exception raised when a message doesn't contain the required
    keys.
    """
    pass

class FileTransferMessage(object):
    """
    This contains all of the information that will be exchanged to
    send a file. It will be sent for each file that is to be exchanged.
    """
    def __init__(self,
                 file_size,
                 write_to,
                 command):
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
        keys = from_msg.keys()
        if "file_size" in keys and "write_to" in keys and "command" in keys:
            cls.file_size = from_msg["file_size"]
            cls.write_to = from_msg["write_to"]
            cls.command = from_msg["command"]
            return cls
        else:
            raise ParsingMessageError()

class FileReceiverProtocol(LineReceiver):
    """
    protocol that will be used to receive files/raw data.
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
        d = Deferred()
        log.msg("lineReceived: " + line)
        msg = FileTransferMessage.from_str(line)
        d.addCallback(self._handleReceivedMessage)
        d.addErrback(self._handleMessageError)
        d.callback(msg)
        return d

    def _handleMessageError(self, error):
        """
        Clean up after the mess that may have occurred with the latest
        file transfer message. 
        """
        failure.trap(error)
        log.err(reason, "Failed to parse file transfer message")
        _clearCommand()
        
    def _clearCommand(self):
        """
        Reset the varaiables of the current protocol. This should set it up to
        start over again.
        """
        self.setLineMode() #make sending of commands possible
        self.remain = 0
        self.outfile = None

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
            self.out_fname = path.join(self.downloadPath, self.write_to)
            log.msg("Receiving into file @" + self.out_fname)
        # should use twisted.python.FilePath?
            try:
                self.outfile = open(self.out_fname,'wb')
            except Exception, value:
                log.err("Unable to open file {0} {1}".format(self.out_fname,
                                                               value))
                return
            log.msg("Entering raw mode. {0} {1}".format(self.outfile,
                                                        self.remain))
            self.setRawMode()
        else:
            raise UnknownMessageError

    def rawDataReceived(self, data):
        """
        As long as it is believed that a buffer needs further writes, 
        write to that buffer. Once the buffer has been filled up,
        which is determined by `remain` counter equaling 0, then
        switch back to line mode.

        :param data: the raw strings of data sent over the wire
        :type data: character string
        """
        #rem_no = self._over_shot_length(len(data))
        #make sure self.outfile is not None
        if self.remain > 0:
            if self.remain % 10000 == 0:
                log.msg("remaining {0}/{1}".format(self.remain, self.size))
            self.remain -= len(data)
            # write the current amount of data to the file
            self.outfile.write(data)
        # this use of if is intentional. Remain needs to be checked
        # again after having written data
        if self.remain <= 0:
            log.msg("writing of file finished. Total len: {0}/{1}"\
                    .format(self.remain, self.size))
            self.outfile.close()
            # basically, if you overshoot by 7, self.remain == -7
            if self.remain < 0:
                self.setLineMode(data[remain:])
            else:
                self.setLineMode()

    def connectionMade(self):
        basic.LineReceiver.connectionMade(self)

    def connectionLost(self, reason):
        basic.LineReceiver.connectionLost(self, reason)
        if self.outfile:
            self.outfile.close()
        # Problem uploading - tmpfile will be discarded
        if self.remain != 0:
            remove(self.out_fname)
        # Success uploading - tmpfile will be saved to disk.
        else:
            log.msg("--> finished saving upload@ " + self.out_fname)
        # cleanup the protocol
        
        #self._clearCommand()

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

    def connectionMade(self):
        # this will be the message sent across the wire.
        # use the fileMessageClass
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
    controller = type('test',(object,),
                      {'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileSenderClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed
