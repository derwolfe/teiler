# There needs to be a good set of tests validating how the file sender protocol 
# works. They will be here

# test for the filesender client

from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport

#from filecmp import cmp

from ..filetransfer import FileReceiverProtocol, FileTransferMessage
from ..filetransfer import CREATE_NEW_FILE, UnknownMessageError
from ..filetransfer import ParsingMessageError
from os import stat, path

def make_garbage_file():
    """create junk file and return its size"""
    with open("./garbage.txt", "w") as f:
        for x in xrange(100000):
             f.write("number mumber " + str(x) + "\n")
    return stat("./garbage.txt").st_size

class FileReceiverProtocolTests(unittest.TestCase):
    
    def setUp(self):
        self.proto = FileReceiverProtocol(".")
        self.transport = StringTransport()
        self.proto.transport = self.transport
        self.data = "YOUR mother was a hamster\n" 
        self.size = len(self.data) # use as a buffer
        self.fname = "crap.txt"
        self.instruct = FileTransferMessage(self.size, 
                                            self.fname,
                                            CREATE_NEW_FILE).serialize()


    def test_line_received_sets_raw_mode(self):
        """
        line received needs valid json
        """
        self.proto.lineReceived(self.instruct)
        # has raw mode been set?
        self.assertTrue(self.proto.line_mode == 0)

    def test_writes_to_file(self):
        """test to see if it actually writes the data to a file, 
        FIXME The test expects an open file handle."""
        self.proto.size = self.size
        self.proto.remain = self.size
        self.proto.outfile = open("crap.txt", "wb")
        self.proto.rawDataReceived(self.data)
        self.assertTrue(self.proto.remain == 0)
        # it finished writing so switch back to line mode
        self.assertTrue(self.proto.line_mode == 1)
        
    def test_mulitple_writes(self):
        """line mode should not be switched back on if there is
        more data to be written to the pipe
        """
        self.proto.setRawMode() # test to see if this changes
        self.proto.size = self.size
        self.proto.remain = self.size + 10
        self.proto.outfile = open("crap.txt", "wb")
        self.proto.rawDataReceived(self.data)
        self.assertTrue(self.proto.remain > 0)
        # it finished writing so switch back to line mode
        self.assertTrue(self.proto.line_mode == 0)

    def test_enormous_line(self):
        """test reading a file that is bigger than a normal frame.
        This is more to test a theory, less a test of code
        """
        size = make_garbage_file()
        self.proto.setRawMode()
        self.proto.size = size
        self.proto.remain = size
        self.proto.outfile = open("./garbage2.txt", "wb")
        with open("garbage.txt", "r") as f:
            for line in f.readlines(): 
                self.proto.rawDataReceived(line)
        self.assertTrue(self.proto.remain == 0)
        self.assertTrue(self.proto.line_mode == 1)

    def test_once_remain_zero_switch_to_line(self):
        self.proto.setRawMode()
        self.proto.size = 0
        self.proto.remain = 0
        self.proto.outfile = open("./garbage2.txt", "wb")
        self.proto.rawDataReceived("12")
        self.assertTrue(self.proto.line_mode == 1)

    def test_handle_message_error_called_with_bad_command(self):
        """
        Make sure _handleMessageError is called when a non existent 
        command is sent.
        """
        # make a message
        msg = str(FileTransferMessage(10, "nope.txt", "DNE"))
        # should line received return d?
        d = self.proto.lineReceived(msg)
        # not sure why yield solves the problem
        yield self.assertFailure(d, UnknownMessageError)
       
    def test_with_good_command(self):
        """
        Make sure _handleMessageError is called when a non existent 
        command is sent.
        """
        # make a message
        msg = str(FileTransferMessage(10, "nope.txt", CREATE_NEW_FILE))
        # should line received return d?
        self.proto.lineReceived(msg)
        # not sure why yield solves the problem

    def test_handleMessageError_catches_except(self):
        """
        XXX not sure how to test if failure.trap works
        """

    def test_clearing_command(self):
        """
        does clear command clear?
        """
        self.proto._clearCommand()
        self.assertTrue(self.proto.line_mode == 1)
        self.assertTrue(self.proto.remain == 0)
        self.assertTrue(self.proto.outfile == None)
        

    def test_connectionLost_closes_file(self):
        # requires an open file to close!
        self.proto.out_fname = "./garbage-close.txt"
        self.proto.outfile = open(self.proto.out_fname, 'w')
        self.assertFalse(self.proto.outfile.closed)
        self.proto.connectionLost("reason") # significance of reason?, seems to be for passing of exception
        self.assertTrue(self.proto.outfile.closed)

    def test_connectioLost_removes_file(self):
        self.proto.out_fname = "./garbage-close.txt"
        self.proto.remain = 1
        self.proto.outfile = open(self.proto.out_fname, 'w')
        self.assertFalse(self.proto.outfile.closed)
        self.proto.connectionLost("reason") 
        # check that the file is deleted
        self.assertFalse(path.exists(self.proto.out_fname))


class FileTransferMessageTests(unittest.TestCase):
    
    def test_message_with_incorrect_keys(self):
        """
        If a message contains the incorrect keys, it should 
        throw a ParsingMessageError
        """
        args = '{"thing": "thing"}'
        d = FileTransferMessage.from_str(args)
        yield self.assertFailure(d, ParsingMessageError) 
