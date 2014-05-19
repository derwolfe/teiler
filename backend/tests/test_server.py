from twisted.trial import unittest
import json

from .. import server, peerdiscovery
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


class FileRequestResourceTests(unittest.TestCase):

    def setUp(self):
        self.requests = []
        self.downloadTo = "."
        self._resourceToTest = server.FileRequestResource(self.requests,
                                                          self.downloadTo)
        self._resource = DummyRootResource('requests', self._resourceToTest)
        self.web = DummySite(self._resource)

    def test_post_good_file_request_returns_ok(self):
        d = self.web.post('requests',
                          {'url': 'plop', 'files': 'fx'},
                          headers=server.HEADERS)

        def check(response):
            self.assertEqual(response.value(), "ok")
            # response code?
        d.addCallback(check)
        return d

    def test_post_good_request_adds_file_request_to_queue(self):
        d = self.web.post('requests',
                          {'url': 'plop', 'files': 'fx'},
                          headers=server.HEADERS)

        def check(response):
            self.assertEqual(self.requests[0].url, 'plop')
            self.assertEqual(self.requests[0].files, ['fx'])
            self.assertEqual(len(self.requests), 1)
        d.addCallback(check)
        return d

    def test_post_bad_file_request_returns_error(self):
        d = self.web.post('requests',
                          {'urlzors': 'ploppy'},
                          headers=server.HEADERS)

        def check(response):
            self.assertEqual(response.value(), "error parsing request")
        d.addCallback(check)
        return d

    def test_post_bad_file_request_does_not_add_request_to_queue(self):
        d = self.web.post('requests',
                          {'urlzors': 'ploppy'},
                          headers=server.HEADERS)

        def check(response):
            self.assertEqual(len(self.requests), 0)
        d.addCallback(check)
        return d


class UsersResourceTests(unittest.TestCase):

    def setUp(self):
        self.peers = peerdiscovery.PeerList()
        self._resourceToTest = server.UsersResource(self.peers)
        self._resource = DummyRootResource('files', self._resourceToTest)
        self.web = DummySite(self._resource)
        self.peer = peerdiscovery.Peer("natalie", "192.168.1.2", 80000)

    def test_getting_users_returns_single_user_with_one_present(self):
        self.peers.add(self.peer)
        d = self.web.get('users', {}, headers=server.HEADERS)
        def check(response):
            parsed = json.loads(response.value())
            parsedUser = peerdiscovery.parsed['users'][0]
            self.assertEqual(parsedUser['peerId'] == self.peer.peerId)
        return d
