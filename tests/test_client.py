from twisted.trial import unittest

from teiler import server, client
from ._dummyresource import DummyRootResource, DummySite

class FileRequestResourceTests(unittest.TestCase):

    def setUp(self):
        self.requests = []
        self.downloadTo = "."
        self._resourceToTest = client.FileRequestResource(self.requests, 
                                                          self.downloadTo)
        self._resource = DummyRootResource('requests', self._resourceToTest)
        self.web = DummySite(self._resource)

    def test_post_good_file_request_returns_ok(self):
        d = self.web.post('requests', 
                          {'url': 'plop', 'files': 'fx' },
                          headers=server.HEADERS)
        def check(response):
            self.assertEqual(response.value(), "ok")
            # response code?
        d.addCallback(check)
        return d   

    def test_post_good_request_adds_file_request_to_queue(self): 
        d = self.web.post('requests',
                          {'url': 'plop', 'files': 'fx' },
                          headers=server.HEADERS)
        def check(response):
            self.assertEqual(self.requests[0].url, 'plop')
            self.assertEqual(self.requests[0].files, ['fx'])
            self.assertEqual(len(self.requests), 1)
        d.addCallback(check)
        return d   

    def test_post_bad_file_request_returns_error(self):
        d = self.web.post('requests',
                          {'urlzors' : 'ploppy' },
                          headers=server.HEADERS)
        def check(response):
            self.assertEqual(response.value(), "error parsing request")
        d.addCallback(check)
        return d   

    def test_post_bad_file_request_does_not_add_request_to_queue(self):
        d = self.web.post('requests',
                          {'urlzors' : 'ploppy' },
                          headers=server.HEADERS)
        def check(response):
            self.assertEqual(len(self.requests), 0)
        d.addCallback(check)
        return d   

        
