"""
File sending is now being done strictly through HTTP.

The process is as follows
1)  A wants to send file f to B
2)  A sends a form as a post request containing 
        a) url root
        b) session key
        c) filename
3)  B parses the form as part of the post request and decides whether to
    grab the file using a get request and the parameters supplied in the form.

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
from os import remove

from ..http_file_transfer import SendFileRequest, FileRequest, createFileRequest
from ..http_file_transfer import MainPage, _getFile, _parseFileNames

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
class SendFileRequestTests(unittest.TestCase):

    def setUp(self):
        self.toDownload = []
        self.hosting = []
        self.downloadTo = "."
        self.web = DummySite(MainPage(self.toDownload, self.hosting, self.downloadTo))
        
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
                          {'url':'url', 'session': 'chris', 'files':'decker,decker/fun'}, 
                          headers=headers)
        def check(response):
            self.assertEqual(response.value(), "<html>OK</html>")
            self.assertEqual(len(self.toDownload), 1)
        d.addCallback(check)
        return d

class UtilityMethodTests(unittest.TestCase):
    
    def test_filename_parser_works(self):
        files = 'decker,decker/fun,decker/fun.txt'
        parsed = _parseFileNames(files)
        expected = ['decker', 'decker/fun', 'decker/fun.txt']
        self.assertTrue(parsed == expected)

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
        
