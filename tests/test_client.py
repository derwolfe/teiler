from twisted.trial import unittest
from teiler import server as tserver
from ._dummyresource import DummyRootResource, DummySite

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

        
