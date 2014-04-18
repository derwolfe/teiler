from twisted.trial import unittest
from twisted.web.test.test_web import DummyRequest
from twisted.web import resource
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

from teiler.client import FileRequestResource
from teiler import server as tserver

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

class DummyRootResource(resource.Resource):
    def __init__(self, requests, downloadTo):
        resource.Resource.__init__(self)
        self.putChild('requests', FileRequestResource(requests, downloadTo)) 

# actual test code
class FileRequestResourceTests(unittest.TestCase):

    def setUp(self):
        self.requests = []
        self.downloadTo = "."
        self._resource = DummyRootResource(self.requests, self.downloadTo)
        self.web = DummySite(self._resource)

    def test_post_file_request_returns_ok_200(self):
        # create a request, and post it
        d = self.web.post('requests', 
                          {'url': 'plop', 'files': 'fx' },
                          headers=tserver.HEADERS)
        def check(response):
            self.assertEqual(response.value(), "ok")
        d.addCallback(check)
        return d   

    def test_good_request_adds_file_request_to_queue(self): 
        d = self.web.post('requests',
                          {'url': 'plop', 'files': 'fx' },
                          headers=tserver.HEADERS)
        def check(response):
            self.assertEqual(self.requests[0].url, 'plop')
            self.assertEqual(self.requests[0].files, ['fx'])
            self.assertEqual(len(self.requests), 1)
        d.addCallback(check)
        return d   

    def test_post_bad_file_request_returns_error(self):
        d = self.web.post('requests',
                          {'urlzors' : 'ploppy' },
                          headers=tserver.HEADERS)
        def check(response):
            self.assertEqual(response.value(), "error parsing request")
        d.addCallback(check)
        return d   

    def test_post_bad_file_request_does_not_add_request_to_queue(self):
        d = self.web.post('requests',
                          {'urlzors' : 'ploppy' },
                          headers=tserver.HEADERS)
        def check(response):
            self.assertEqual(len(self.requests), 0)
        d.addCallback(check)
        return d   

        
