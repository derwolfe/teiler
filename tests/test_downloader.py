from twisted.trial import unittest
from teiler.downloadagent import FileWriter, DownloadProgress
from twisted.internet.defer import Deferred

class FakeIoHandler(object):
    """
    Mock out file operations.
    """
    def __init__(self):
        self.buffer = []

    def open(self, filename):
        return
    
    def close(self):
        return

    def write(self, bytes):
        self.buffer.append(bytes)
    
class FileWriterTests(unittest.TestCase):
    
    def setUp(self):
        self.io = FakeIoHandler()
        self.progress = DownloadProgress()
        self.protocol = FileWriter(Deferred(), 100, "plop", 
                            self.io, self.progress)

    def test_receiving_data_writes_data_to_a_bufferlike_object(self):
        self.protocol.dataReceived(b'I have been written')
        self.assertTrue(self.io.buffer == [b'I have been written'])

    def test_receving_17_percent_of_a_file_yields_17_percent_progress(self):
        self.protocol.dataReceived(b'this was 17 bytes')
        self.assertTrue(self.protocol.currentProgress() == 17.0)

class FileWriterProgressTests(unittest.TestCase):
    
    def test_internal_progress_accessible(self):
        self.io = FakeIoHandler()
        self.progress = DownloadProgress() 
        self.protocol = FileWriter(Deferred(), 100, "plop", 
                                   self.io, self.progress)
        self.protocol.dataReceived(b'zehn zehn ')
        self.assertTrue(self.progress.current() == 10)
        #self.assertTrue(self.progress is self.protocol._progress)

class DownloadProgressTests(unittest.TestCase):
    
    def test_can_update_progress(self):
        progress = DownloadProgress()
        progress.add(10.0)
        self.assertTrue(10 == progress.current())

    def test_progress_initialized_to_zero(self):
        progress = DownloadProgress()
        self.assertTrue(0 == progress.current())
