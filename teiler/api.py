#!/usr/bin/env python
# -*- coding: utf-8
# -*- test-case-name: tests.test_api -*-

"""
api

This exists to build the resource structure necessary for the application.
The internal api is meant for resources that run on localhost only. This is
because these resource allow users to expose files on their system.

The external api exists to allow fellow users to propose new transfer requests
and to download the files they have accepted.
"""

from teiler.server import (
    UsersEndpoint,
    FileEndpoint,
    OutboundRequestEndpoint,
    InboundRequestEndpoint
)
from teiler.utils import getFilenames
from teiler.postagent import submitFileRequest
from teiler.filerequest import parseFileRequest
from teiler.peerdiscovery import PeerList

from klein import Klein


class InternalAPIFactory(object):
    """
    Create the internal resources needed to start the internal API.

    The applications used on the internal API are:
    1. UsersEndpoint
    2. OutboundRequestsEndpoint
    """
    app = Klein()

    def __init__(self,
                 rootUrl,
                 outboundRequests,
                 fileNameGetter=getFilenames,
                 fileRequestSubmitter=submitFileRequest,
                 peerList=PeerList()):
        self._usersEndpoint = UsersEndpoint(peerList)
        self._outboundRequestsEndpoint = OutboundRequestEndpoint(
            outboundRequests,
            getFilenames,
            fileRequestSubmitter,
            rootUrl)

    @app.route('/files', branch=True)
    def getOutboundRequestsEndpoint(self, request):
        return self._outboundRequestsEndpoint.app.resource()

    @app.route('/users', branch=True)
    def getUserEndpoint(self, request):
        return self._usersEndpoint.app.resource()


class ExternalAPIFactory(object):
    """
    Create an application object that contains all of the necessary
    resources for the external HTTP api.

    The applications used on the external API are:
    1. InboundRequestsEndPoint
    2. FileEndpoint
    """
    app = Klein()

    def __init__(self,
                 outbound,
                 inbound=[],
                 downloadTo=".",
                 requestParser=parseFileRequest):
        self._fileEndpoint = FileEndpoint(outbound)
        self._inboundRequestEndpoint = InboundRequestEndpoint(
            inbound,
            downloadTo,
            requestParser
        )

    @app.route('/files', branch=True)
    def getFiles(self, request):
        return self._fileEndpoint.app.resource()

    @app.route('/requests')
    def inboundRequest(self, request):
        return self._inboundRequestEndpoint.app.resource()
