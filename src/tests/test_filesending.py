# There needs to be a good set of tests validating how the file sender protocol 
# works. They will be here

# test for the filesender client

from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport
import json

from ..filetransfer import FileReceiverProtocol


class FileSenderClientTests(unittest.TestCase):
    
    def setUp(self):
        self.proto = FileReceiverProtocol(".")
        self.transport = StringTransport()
        self.proto.transport = self.transport

    def test_line_received(self):
        "line received needs valid json"
        line = json.dumps({"file_size" : 0, 
                           "original_file_path": "./crap.txt"
                           })
        self.proto.lineReceived(line)
        self.proto.instruction = line 
        # has raw mode been set?
        self.assertTrue(self.proto.line_mode == 0)
        # suppress some of the prints
