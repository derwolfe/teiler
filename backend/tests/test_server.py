#!/usr/bin/env python
# -*- coding: utf-8

from twisted.trial import unittest

import json
from .. import server, peerdiscovery
from ._dummyresource import DummyRootResource, DummySite


def fakeProcessFilenames(path):
    return ['/plop', '/foo/bar']


def fakeSubmitFileRequest(recipient, data):
    """
    doesn't send a real network request on file submission
    """
    pass


class FileServerResourceTests(unittest.TestCase):

    def setUp(self):

        self.hosting = server.OutboundRequests()
        self._ip = '192.168.1.1'
        self._resourceToTest = server.FileServerResource(self.hosting,
                                                         self._ip,
                                                         fakeProcessFilenames,
                                                         fakeSubmitFileRequest)

        self._resource = DummyRootResource('files', self._resourceToTest)
        self.web = DummySite(self._resource)
        self.urlStub = "http://localhost/files/"

    def test_valid_posting_returns_file_url_in_response(self):
        d = self.web.post('files', {'filepath': '/bar', 'user': '1.1.1.1'},
                          None)

        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp['url'] == self.urlStub + resp['transferId'])
        d.addCallback(check)
        return d

    def test_valid_posting_returns_path_in_response(self):
        d = self.web.post('files', {'filepath': '/bar', 'user': '1.1.1.1'},
                          None)

        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp['path'] == u'/bar')
        d.addCallback(check)
        return d

    def test_valid_posting_returns_userIp_in_response(self):
        d = self.web.post('files', {'filepath': '/bar', 'user': '1.1.1.1'},
                          None)

        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp['userIp'] == u'1.1.1.1')
        d.addCallback(check)
        return d

    def test_posting_file_adds_transfer_to_outbound_requests(self):
        d = self.web.post('files', {'filepath': '/bar', 'user': '1.1.1.1'},
                          None)

        def check(response):
            resp = json.loads(response.value())
            transfer = self.hosting.get(resp["transferId"])
            self.assertTrue(transfer.filePath == '/bar')
            self.assertTrue(transfer.userIp == '1.1.1.1')
        d.addCallback(check)
        return d

    def test_posting_request_without_serveat_returns_useful_message(self):
        d = self.web.post('files', {'filepath': '/bar'}, None)

        def check(response):
            resp = json.loads(response.value())
            errorMsg = u'Error parsing url or target user'
            self.assertTrue(resp['errors'] == errorMsg)
            self.assertTrue(resp['url'] is None)
        d.addCallback(check)
        return d

    def test_posting_request_without_filepath_returns_useful_message(self):
        d = self.web.post('files', {}, None)

        def check(response):
            resp = json.loads(response.value())
            errorMsg = u'Error parsing url or target user'
            self.assertTrue(resp['errors'] == errorMsg)
            self.assertTrue(resp['url'] is None)
        d.addCallback(check)
        return d

    def test_delete_request_removes_file_and_cleans_up(self):
        transfer = server.Transfer('foo', '.', '1.1.1.1')
        self._resourceToTest._addRequest(transfer)
        d = self.web.delete('files', {'url': 'foo', 'user': '1.1.1.1'},
                            None)

        def check(response):
            resp = json.loads(response.value())
            self.assertTrue(resp["status"] == "removed url")
            self.assertTrue(self.hosting.get("foo") is None)
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
        d = self.web.post('requests', {'url': 'plop', 'files': 'fx'},
                          None)

        def check(response):
            self.assertEqual(response.value(), "ok")
            # response code?
        d.addCallback(check)
        return d

    def test_post_good_request_adds_file_request_to_queue(self):
        d = self.web.post('requests', {'url': 'plop', 'files': 'fx'},
                          None)

        def check(response):
            self.assertEqual(self.requests[0].url, 'plop')
            self.assertEqual(self.requests[0].files, ['fx'])
            self.assertEqual(len(self.requests), 1)
        d.addCallback(check)
        return d

    def test_post_bad_file_request_returns_error(self):
        d = self.web.post('requests', {'urlzors': 'ploppy'},
                          None)

        def check(response):
            self.assertEqual(response.value(), "error parsing request")
        d.addCallback(check)
        return d

    def test_post_bad_file_request_does_not_add_request_to_queue(self):
        d = self.web.post('requests', {'urlzors': 'ploppy'},
                          None)

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
        d = self.web.get('users', {}, None)

        def check(response):
            parsed = json.loads(response.value())
            parsedUser = parsed['users'][0]
            self.assertEqual(parsedUser['peerId'] == self.peer.peerId)
        return d
