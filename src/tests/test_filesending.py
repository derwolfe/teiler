# There needs to be a good set of tests validating how the file sender protocol 
# works. They will be here

# test for the filesender client

from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport
import json

from sys import getsizeof

from ..filetransfer import FileReceiverProtocol


class FileSenderClientTests(unittest.TestCase):
    
    def setUp(self):
        self.proto = FileReceiverProtocol(".")
        self.transport = StringTransport()
        self.proto.transport = self.transport
        self.data = "YOUR mother was a hamster\n" 
        self.size = len(self.data) # use as a buffer
        self.fname = "crap.txt"
        self.instruct = json.dumps({"file_size" : self.size,
                                    "original_file_path": self.fname
                                }) 

    def test_line_received_sets_raw_mode(self):
        """line received needs valid json"""
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
