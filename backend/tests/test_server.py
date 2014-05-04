from twisted.trial import unittest

from .. import server
from ._dummyresource import DummyRootResource, DummySite


class FileRequestResourceTests(unittest.TestCase):

    def setUp(self):
        self.hosting = []
        self._resourceToTest = server.FileServerResource(self.hosting)
        self._resource = DummyRootResource('files', self._resourceToTest)
        self.web = DummySite(self._resource)

    def test_posting_file_and_path_returns_new_location(self):
        d = self.web.post('files', {'serveat': 'foo', 'filepath': '/bar'}, headers=server.HEADERS)
        def check(response):
            resp = response.Value()
            print resp
        return d
