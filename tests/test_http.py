"""
Tests for the httpFileTransfer classes/methods.
"""
#from twisted.trial import unittest
#from twisted.web.test.test_web import DummyRequest
#from twisted.internet.defer import succeed, Deferred
#from twisted.web import server, client
#from twisted.web.static import File
#from twisted.python import log
#from twisted.protocols.policies import WrappingFactory
#from twisted.python.compat import networkString, nativeString
#from twisted.internet import reactor
#from urlparse import urljoin
#from filecmp import cmp
#from os import remove, path, makedirs
#from shutil import rmtree
#
### code used to test resources
#class SmartDummyRequest(DummyRequest):
#    def __init__(self, method, url, args=None, headers=None):
#        DummyRequest.__init__(self, url.split('/'))
#        self.method = method
#        self.headers.update(headers or {})
#
#        args = args or {}
#        for k, v in args.items():
#            self.addArg(k, v)
#
#    def value(self):
#        return "".join(self.written)
#
#
#class DummySite(server.Site):
#    def get(self, url, args=None, headers=None):
#        return self._request("GET", url, args, headers)
#
#    def post(self, url, args=None, headers=None):
#        return self._request("POST", url, args, headers)
#
#    def _request(self, method, url, args, headers):
#        request = SmartDummyRequest(method, url, args, headers)
#        resource = self.getResourceFor(request)
#        result = resource.render(request)
#        return self._resolveResult(request, result)
#
#    def _resolveResult(self, request, result):
#        if isinstance(result, str):
#            request.write(result)
#            request.finish()
#            return succeed(request)
#        elif result is server.NOT_DONE_YET:
#            if request.finished:
#                return succeed(request)
#            else:
#                return request.notifyFinish().addCallback(lambda _: request)
#        else:
#            raise ValueError("Unexpected return value: %r" % (result,))
#
## actual test code
#class FileRequestResourceTests(unittest.TestCase):
#
#    def setUp(self):
#        self.toDownload = []
#        self.hosting = []
#        self.downloadTo = "."
#        self.web = DummySite(MainPage(self.toDownload,
#                                      self.hosting,
#                                      self.downloadTo))
#
#
#    def test_post_adds_files(self):
#        postdata, headers = createFileRequest('url',
#                                              'chris',
#                                              'decker, decker/fun')
#        d = self.web.post("request",
#                          {'url':'url',
#                           'session': 'chris',
#                           'files': 'decker,decker/fun'},
#                          headers=headers)
#        def check(response):
#            self.assertEqual(response.value(), "<html>OK</html>")
#            self.assertEqual(len(self.toDownload), 1)
#        d.addCallback(check)
#        return d
#
#class UtilityMethodTests(unittest.TestCase):
#
#    def setUp(self):
#        self.downloadTo = path.abspath(path.curdir)
#
#    def test_filename_parser_works(self):
#        files = 'decker,decker/fun,decker/fun.txt'
#        parsed = _parseFileNames(files)
#        expected = ['decker', 'decker/fun', 'decker/fun.txt']
#        self.assertTrue(parsed == expected)
#
#    def test_securefilepath_with_traversing_path(self):
#        requestPath = "../../../foo/bar/baz.txt"
#        downloadPath = path.join(self.downloadTo, requestPath)
#        self.assertFalse(isSecurePath(downloadPath, self.downloadTo))
#
#    def test_securefilepath_with_ok_path(self):
#        requestPath = "foo/bar/baz.txt"
#        downloadPath = path.join(self.downloadTo, requestPath)
#        self.assertTrue(isSecurePath(downloadPath, self.downloadTo))
#
#class MainPageMethodsTests(unittest.TestCase):
#
#    def setUp(self):
#        self.toDownload = []
#        self.hosting = []
#        self.downloadTo = '.'
#        self.web = DummySite(MainPage(self.toDownload, self.hosting, self.downloadTo))
#        self.name = "here"
#
#    def test_add_file_creates_reachable_url(self):
#        self.web.resource.addFile(self.name, ".")
#        entities = self.web.resource.listNames()
#        self.assertTrue(self.name in entities)
#
#    def test_remove_file_removes_url(self):
#        self.web.resource.putChild(self.name, File(".")) # put file using twisted syntax
#        entities = self.web.resource.listNames()
#        self.assertTrue(self.name in entities)
#
#        self.web.resource.removeFile(self.name)
#        entities = self.web.resource.listNames()
#        self.assertTrue(self.name not in entities)
#
#
#class FileRequestIntegrationTests(unittest.TestCase):
#
#    def _listen(self, site):
#        return reactor.listenTCP(0, site, interface="127.0.0.1")
#
#    def getURL(self, path):
#        host = "http://127.0.0.1:%d/" % self.portno
#        return networkString(urljoin(host, nativeString(path)))
#
#    def setUp(self):
#        self._createTestFiles()
#        self.toDownload = []
#        self.hosting = []
#        self.downloadTo = "."
#        self.r = MainPage(self.toDownload,
#                          self.hosting,
#                          self.downloadTo) # host the files in trial temp including decker
#        self.url = 'test'
#        self.r.addFile(self.url, "./test")
#        self.site = server.Site(self.r, timeout=3)
#        self.wrapper = WrappingFactory(self.site)
#        self.port = self._listen(self.wrapper)
#        self.portno = self.port.getHost().port
#        self.cleanupServerConnections = 0
#        # file name to download
#        self.fname = 'decker/fun.txt'
#        self.files = [self.fname]
#        self.session = "a"
#        # create a file resource!
#        self.fileURL = self.getURL(self.url + '/' + self.fname)
#        self.request = FileRequest(self.getURL(self.url),
#                                   self.session,
#                                   self.files,
#                                   self.downloadTo)
#
#        # create the needed files
#    def _createTestFiles(self):
#        makedirs("./test/decker")
#        with open("./test/decker/fun.txt", "w") as f:
#            f.write("ich")
#
#    def _deleteTestFiles(self):
#        if path.exists("./test"):
#            rmtree("./test", ignore_errors=True)
#        if path.exists("./decker"):
#            rmtree("./decker", ignore_errors=True)
#
#    def tearDown(self):
#        self._deleteTestFiles()
#        connections = list(self.wrapper.protocols.keys())
#        if connections:
#            log.msg("Some left-over connections; this test is probably buggy.")
#        return self.port.stopListening()
#
#    def test_resource_active(self):
#        """
#        make sure the file is available for the integration test to use.
#        IF this fails, then no tests in this object should pass
#        """
#        self.assertTrue(self.url in self.r.listNames())
#        def check(data):
#            self.assertTrue(data == "ich")
#        d = client.getPage(self.fileURL)
#        d.addCallback(check)
#        return d
#
#    def test_calling_getFiles_adds_files_to_downloads(self):
#        d = self.request.getFiles()
#        def check(ignored):
#            self.assertTrue(len(self.request.downloads) == 1)
#        d.addCallback(check)
#        return d
#
#    def test_downloads_files(self):
#        """
#        This is definitely an integration test, as the test requires the creation
#        of several resources, from which files can be downloaded
#        """
#        d = self.request.getFiles()
#        def check(data):
#            self.assertTrue(path.exists("./decker/fun.txt"))
#        d.addCallback(check)
#        return d
