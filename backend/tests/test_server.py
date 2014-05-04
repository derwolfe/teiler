from twisted.trial import unittest
import json

from .. import server
from ._dummyresource import DummyRootResource, DummySite


class FileServerResourceTests(unittest.TestCase):

    def setUp(self):
        self.hosting = []
        self._resourceToTest = server.FileServerResource(self.hosting)
        self._resource = DummyRootResource('files', self._resourceToTest)
        self.web = DummySite(self._resource)

    def test_posting_file_and_path_returns_new_location(self):
        d = self.web.post('files', {'serveat': 'foo', 'filepath': '/bar'}, headers=server.HEADERS)
        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp['url'] == 'localhost/foo')
        d.addCallback(check)
        return d
