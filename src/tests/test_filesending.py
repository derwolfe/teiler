# There needs to be a good set of tests validating how the file sender protocol 
# works. They will be here

# test for the filesender client

from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport

#from filecmp import cmp

from ..filetransfer import FileReceiverProtocol, FileTransferMessage
from ..utils import get_file_string_length


def make_garbage_file():
    """create junk file and return its size"""
    with open("./garbage.txt", "w") as f:
        for x in xrange(100000):
             f.write("number mumber " + str(x) + "\n")
    # get the string lenth of the file by looping over it
    return get_file_string_length("./garbage.txt")
    

class FileReceiverProtocolTests(unittest.TestCase):
    
    def setUp(self):
        self.proto = FileReceiverProtocol(".")
        self.transport = StringTransport()
        self.proto.transport = self.transport
        self.data = "YOUR mother was a hamster\n" 
        self.size = len(self.data) # use as a buffer
        self.fname = "crap.txt"
        # something is wrong here
        self.instruct = FileTransferMessage(self.size, 
                                            self.fname).serialize()

    def tearDown(self):
        """delete some the test garbage files for each test"""
        pass

    def test_line_received_sets_raw_mode(self):
        """
        line received needs valid json
        """
        self.proto.lineReceived(self.instruct)
        # has raw mode been set?
        self.assertTrue(self.proto.line_mode == 0)

# these could have better setup methods!
#
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
