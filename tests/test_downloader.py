from twisted.internet import reactor
from twisted.trial import unittest

from twisted.web import server
from twisted.protocols.policies import WrappingFactory
from twisted.python.compat import networkString, nativeString
from urlparse import urljoin
from twisted.python import log
from filecmp import cmp

import os

from teiler.downloadagent import DownloadAgent, FileWriter
from teiler.server import RootResource

class FileDownloaderTests(unittest.TestCase):

    """
    These tests assume that resource works as expected. The test is to see
    if your file download logic works.
    """
    def _listen(self, site):
        return reactor.listenTCP(0, site, interface="127.0.0.1")

    def setUp(self):
        self.toDownload = []
        self.hosting = []
        # don't use this to test... use something more verifiable.
        self.r = RootResource(self.toDownload, self.hosting, ".")
        self.site = server.Site(self.r, timeout=None)
        self.wrapper = WrappingFactory(self.site)
        self.port = self._listen(self.wrapper)
        self.portno = self.port.getHost().port
        self.session = 'a'
        self.downloadTo = './downloaded.txt'
        self.cleanupServerConnections = 0
        self.url = "example"
        self.fileText = "ja, ich bins"
        self.filename = "./file.txt"
        # add a folder to mainpage containing the file
        with open("./file.txt", "w") as f:
            f.write(self.fileText)
        # add the file resource
        self.r.addFile(self.url, "file.txt")


    def tearDown(self):
        connections = list(self.wrapper.protocols.keys())
        if connections:
            log.msg("Some left-over connections; this test is probably buggy.")
        return self.port.stopListening()

    def test_file_is_available(self):
        """
        make sure the resource is listed as availale
        """
        self.assertTrue(self.url in self.r.listNames())

    def getURL(self, path):
        """
        Each test here open and closes a new port, this way the port
        assignment is automatic
        """
        host = "http://127.0.0.1:%d/" % self.portno
        return networkString(urljoin(host, nativeString(path)))

    def test_gets_file(self):
        """
        check to see whether or not download data actually works
        """
        dler = DownloadAgent(reactor,
                             self.getURL(self.url),
                             self.downloadTo)
        d = dler.getFile()
        def check(response):
            self.assertTrue(cmp(self.filename, self.downloadTo))
        d.addCallback(check)
        return d

    def test_returns_status(self):
        # XXX - the status piece doesn't really have a very useful API at the
        #moment. It might make sense that this be broadcast, though i'm not
        # how to handle that at the moment.
        dler = DownloadAgent(reactor,
                             self.getURL(self.url),
                             self.downloadTo)
        d = dler.getFile()
        def check(ignored):
           self.assertTrue(True)
        d.addCallback(check)
        return d

