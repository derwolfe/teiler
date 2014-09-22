#!/usr/bin/env python
# -*- coding: utf-8

"""
api tests
"""
from twisted.trial.unittest import SynchronousTestCase
from teiler import api


class ApiTests(SynchronousTestCase):
    """
    The APIs exist to create parent resources from the endpoints detailed
    in teiler.server.

    The funcionality of those elements is tested in tests/test_server.

    This set of tests will check only that the routes work as expected.
    """
    def test_internalApi_has_outboundRequestEndpoint_routes(self):
        app = api.InternalAPIFactory(None, None, None, None, None).app

        c = app.url_map.bind('files')

        self.assertEqual(c.match("/files"),
                         ("getOutboundRequestsEndpoint", {}))
        self.assertEqual(
            c.match("/files/plop"),
            ('getOutboundRequestsEndpoint_branch', {'__rest__': u'plop'})
        )

    def test_internalApi_has_userEndpoint_routes(self):
        app = api.InternalAPIFactory(None, None, None, None, None).app

        c = app.url_map.bind('users')

        self.assertEqual(c.match("/users"),
                         ("getUserEndpoint", {}))
        self.assertEqual(
            c.match("/users/plop"),
            ('getUserEndpoint_branch', {'__rest__': u'plop'})
        )

    def test_externalApi_has_files_routes(self):
        app = api.ExternalAPIFactory(None, None, None, None).app

        c = app.url_map.bind('requests')

        self.assertEqual(c.match("/requests"),
                         ("inboundRequest", {}))

    def test_externalApi_has_requests_route(self):
        app = api.ExternalAPIFactory(None, None, None, None).app

        c = app.url_map.bind('files')

        self.assertEqual(c.match("/files"),
                         ("getFiles", {}))
        self.assertEqual(
            c.match("/files/plop"),
            ('getFiles_branch', {'__rest__': u'plop'})
        )
