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

from ..http_file_transfer import SendFileRequest, FileRequest, createFileRequest
from ..http_file_transfer import MainPage
from twisted.trial import unittest
from twisted.web.test.test_web import DummyRequest
from twisted.internet.defer import succeed, inlineCallbacks
from twisted.web import server
from twisted.python import log


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
        self.files = []
        self.web = DummySite(MainPage(self.files))

    def test_get_response(self):
        d = self.web.get("request")
        def check(response):
            self.assertEqual(response.value(), "<html>ja, ich bins</html>")
        d.addCallback(check)
        return d


    def test_post_adds_files(self):        
        postdata, headers = createFileRequest('url', 'chris')
        #d = self.web.post("request", {'postdata': postdata} , headers=headers)
        d = self.web.post("request", {'url':'url', 'session': 'chris'}, headers=headers)
        def check(response):
            self.assertTrue(len(self.files) == 1)
        d.addCallback(check)
