from twisted.trial import unittest
import json

from .. import server
from ._dummyresource import DummyRootResource, DummySite


class FileServerResourceTests(unittest.TestCase):

    def setUp(self):
        self.hosting = server.Files()
        self._resourceToTest = server.FileServerResource(self.hosting)
        self._resource = DummyRootResource('files', self._resourceToTest)
        self.web = DummySite(self._resource)

    def test_posting_file_and_path_returns_new_location(self):
        d = self.web.post('files', {'serveat': 'foo', 'filepath': '/bar'},
                          headers=server.HEADERS)
        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp['url'] == u'http://localhost/files/foo')
        d.addCallback(check)
        return d

    def test_posting_file_adds_filename_and_path_to_hosts(self):
        d = self.web.post('files', {'serveat': 'foo', 'filepath': '/bar'},
                          headers=server.HEADERS)
        def check(ignored):
            self.assertTrue(self.hosting.get('foo') == '/bar')
        d.addCallback(check)
        return d

    def test_delete_request_removes_file_and_cleans_up(self):
        self._resourceToTest._addFile('foo', '.')
        d = self.web.delete('files', {'url': 'foo'}, headers=server.HEADERS)
        def check(response):
            self.assertTrue(self.hosting.get('foo') == None)
        d.addCallback(check)
        return d
