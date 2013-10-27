"""
Tests for the httpFileTransfer classes/methods.
"""
from twisted.trial import unittest
from twisted.web.test.test_web import DummyRequest
from twisted.internet.defer import succeed, Deferred
from twisted.web import server, client
from twisted.web.static import File
from twisted.python import log
from twisted.protocols.policies import WrappingFactory
from twisted.python.compat import networkString, nativeString
from twisted.internet import reactor
from urlparse import urljoin
from filecmp import cmp
from os import remove, path, makedirs
from shutil import rmtree

from ..httpFileTransfer import FileRequestResource, FileRequest, createFileRequest
from ..httpFileTransfer import MainPage, _getFile, isSecurePath
from ..httpFileTransfer import  _parseFileNames

## code used to test resources  
class SmartDummyRequest(DummyRequest):
    def __init__(self, method, url, args=None, headers=None):
        DummyRequest.__init__(self, url.split('/'))
        self.method = method
        self.headers.update(headers or {})

        args = args or {}
        for k, v in args.items():
            self.addArg(k, v)

    def value(self):
        return "".join(self.written)


class DummySite(server.Site):
    def get(self, url, args=None, headers=None):
        return self._request("GET", url, args, headers)

    def post(self, url, args=None, headers=None):
        return self._request("POST", url, args, headers)

    def _request(self, method, url, args, headers):
        request = SmartDummyRequest(method, url, args, headers)
        resource = self.getResourceFor(request)
        result = resource.render(request)
        return self._resolveResult(request, result)

    def _resolveResult(self, request, result):
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return succeed(request)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return succeed(request)
            else:
                return request.notifyFinish().addCallback(lambda _: request)
        else:
            raise ValueError("Unexpected return value: %r" % (result,))

# actual test code
class FileRequestResourceTests(unittest.TestCase):

    def setUp(self):
        self.toDownload = []
        self.hosting = []
        self.downloadTo = "."
        self.web = DummySite(MainPage(self.toDownload, 
                                      self.hosting, 
                                      self.downloadTo))
        
        
    def test_get_response(self):
        d = self.web.get("request")
        def check(response):
            self.assertEqual(response.value(), "<html>ja, ich bins</html>")
        d.addCallback(check)
        return d

    def test_post_adds_files(self):        
        postdata, headers = createFileRequest('url', 
                                              'chris', 
                                              'decker, decker/fun')
        d = self.web.post("request", 
                          {'url':'url', 
                           'session': 'chris', 
                           'files': 'decker,decker/fun'}, 
                          headers=headers)
        def check(response):
            self.assertEqual(response.value(), "<html>OK</html>")
            self.assertEqual(len(self.toDownload), 1)
        d.addCallback(check)
        return d

class UtilityMethodTests(unittest.TestCase):
    
    def setUp(self):
        self.downloadTo = path.abspath(path.curdir)

    def test_filename_parser_works(self):
        files = 'decker,decker/fun,decker/fun.txt'
        parsed = _parseFileNames(files)
        expected = ['decker', 'decker/fun', 'decker/fun.txt']
        self.assertTrue(parsed == expected)

    def test_securefilepath_with_traversing_path(self):
        requestPath = "../../../foo/bar/baz.txt"
        downloadPath = path.join(self.downloadTo, requestPath)
        self.assertFalse(isSecurePath(downloadPath, self.downloadTo))

    def test_securefilepath_with_ok_path(self):
        requestPath = "foo/bar/baz.txt"
        downloadPath = path.join(self.downloadTo, requestPath)
        self.assertTrue(isSecurePath(downloadPath, self.downloadTo))

class FileRequestObjectTests(unittest.TestCase):
    
    def setUp(self):
        self.url = "http://localhost:9000"
        self.session = "a"
        self.testFilesDir = "decker"
        self.files = ['decker', 'decker/fun.txt', 'decker/foo/bar.txt']
        self.downloadTo = "."
        self.request = FileRequest(self.url, 
                                   self.session, 
                                   self.files, 
                                   self.downloadTo)
        
    def tearDown(self):
        """
        delete the files and directories that have been created
        """
        if path.exists("./decker"):
            rmtree("./decker", ignore_errors=True)

    def test_removes_file_from_queue_on_download(self):
        """
        Does it remove files from the queue during processing?
        """
        self.assertTrue(len(self.request.files) > 0)
        def check(ignored):
            self.assertTrue(len(self.request.files) == 0)
        d = self.request.getFiles()
        d.addCallback(check)
        return d

    def test_file_downloading_begins(self):
        d = self.request.getFiles()
        def check(ignored):
            self.assertTrue(len(self.request.downloading) == 3)
        d.addCallback(check)
        return d

    # XXX does not test anything yet!
    def test_can_check_download_status(self):
        """
        get status returns a dictionary containing the status of each
        Each deferred object return inside of downloading is able to provide its current
        status. This is provided by getPage from twisted.
        """
        d = self.request.getFiles()
        def check(ignored):
            status = self.request.getStatus()
        d.addCallback(check)
        return d


class MainPageMethodsTests(unittest.TestCase):

    def setUp(self):
        self.toDownload = []
        self.hosting = []
        self.downloadTo = '.'
        self.web = DummySite(MainPage(self.toDownload, self.hosting, self.downloadTo))
        self.name = "here"

    def test_add_file_creates_reachable_url(self):
        self.web.resource.addFile(self.name, ".")
        entities = self.web.resource.listNames()
        self.assertTrue(self.name in entities)

    def test_remove_file_removes_url(self):
        self.web.resource.putChild(self.name, File(".")) # put file using twisted syntax
        entities = self.web.resource.listNames()
        self.assertTrue(self.name in entities)

        self.web.resource.removeFile(self.name)
        entities = self.web.resource.listNames()
        self.assertTrue(self.name not in entities)

        
class FileRequestIntegrationTests(unittest.TestCase):
    
    def _listen(self, site):
        return reactor.listenTCP(0, site, interface="127.0.0.1")
    
    def getURL(self, path):
        host = "http://127.0.0.1:%d/" % self.portno
        return networkString(urljoin(host, nativeString(path)))

    def setUp(self):
        self._createTestFiles()
        self.toDownload = []
        self.hosting = []
        self.downloadTo = "."
        self.r = MainPage(self.toDownload, 
                          self.hosting, 
                          self.downloadTo) # host the files in trial temp including decker
        self.url = 'test'
        self.r.addFile(self.url, "./test")
        self.site = server.Site(self.r, timeout=3)
        self.wrapper = WrappingFactory(self.site)
        self.port = self._listen(self.wrapper)
        self.portno = self.port.getHost().port
        self.cleanupServerConnections = 0
        # file name to download
        self.fname = 'decker/fun.txt'
        self.files = [self.fname]
        self.session = "a"
        # create a file resource!
        self.fileURL = self.getURL(self.url + '/' + self.fname)
        self.request = FileRequest(self.getURL(self.url), 
                                   self.session, 
                                   self.files, 
                                   self.downloadTo)

        # create the needed files
    def _createTestFiles(self):
        makedirs("./test/decker")
        with open("./test/decker/fun.txt", "w") as f:
            f.write("ich")

    def _deleteTestFiles(self):
        if path.exists("./test"):
            rmtree("./test", ignore_errors=True)
        if path.exists("./decker"):
            rmtree("./decker", ignore_errors=True)
    
    def tearDown(self):
        self._deleteTestFiles()
        connections = list(self.wrapper.protocols.keys())
        if connections:
            log.msg("Some left-over connections; this test is probably buggy.")
        return self.port.stopListening()
    
    def test_resource_active(self):
        """
        make sure the file is available for the integration test to use.
        IF this fails, then no tests in this object should pass
        """
        self.assertTrue(self.url in self.r.listNames())
        def check(data):
            self.assertTrue(data == "ich")
        d = client.getPage(self.fileURL)
        d.addCallback(check)
        return d

    def test_downloads_files(self):
        """
        This is definitely an integration test, as the test requires the creation
        of several resources, from which files can be downloaded
        """
        # this should download and create the files?
        d = self.request.getFiles()
        def check(data):
            self.assertTrue(len(self.request.downloading) == 1)
            self.assertTrue(path.exists("./decker/fun.txt"))
        d.addCallback(check)
        return d
        

class FileDownloadTests(unittest.TestCase):
    
    """
    These tests assume that resource works as expected. The test is to see 
    if your file download logic works.
    """
    def _listen(self, site):
        return reactor.listenTCP(0, site, interface="127.0.0.1")
        
    def setUp(self):
        self.toDownload = []
        self.hosting = []
        self.r = MainPage(self.toDownload, self.hosting, ".")
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
        d = _getFile(self.getURL(self.url), self.downloadTo)
        log.msg(self.getURL(self.url))
        def check(ignored):
            self.assertTrue(cmp(self.filename, self.downloadTo))
            remove(self.downloadTo)
        d.addCallback(check)
        return d
        
