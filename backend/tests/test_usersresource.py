from twisted.trial import unittest
import json

from .. import server, peerdiscovery
from ._dummyresource import DummyRootResource, DummySite


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
