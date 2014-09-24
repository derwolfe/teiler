from twisted.trial.unittest import SynchronousTestCase

from twisted.internet.defer import succeed
from twisted.web.resource import NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.python import filepath

from klein.resource import KleinResource
from klein.test_resource import requestMock

from mock import MagicMock, patch

from StringIO import StringIO

import json

from teiler import server, peerdiscovery, filerequest


class TransferTests(SynchronousTestCase):

    def test_byte_properties_encode_to_unicode(self):
        transfer = server.Transfer(b'1', b'/User/', b'1.1.1.1')
        self.assertEqual(transfer.transferId, u'1')
        self.assertEqual(transfer.filepath, u'/User/')
        self.assertEqual(transfer.userIp, u'1.1.1.1')

    def test_unicode_properties_encode_to_unicode(self):
        transfer = server.Transfer(u'1', u'/User/', u'1.1.1.1')
        self.assertEqual(transfer.transferId, u'1')
        self.assertEqual(transfer.filepath, u'/User/')
        self.assertEqual(transfer.userIp, u'1.1.1.1')

    def test_no_literal_properties_encode_to_unicode(self):
        transfer = server.Transfer('1', '/User/', '1.1.1.1')
        self.assertEqual(transfer.transferId, u'1')
        self.assertEqual(transfer.filepath, u'/User/')
        self.assertEqual(transfer.userIp, u'1.1.1.1')

    def test_toJsonReturnsAllProperties(self):
        transfer = server.Transfer('1', '/User/', '1.1.1.1')
        url = 'json.com'
        result = transfer.toJson(url)
        expected = '{"url": "json.com/1/", "transferId": "1",'\
                   ' "userIp": "1.1.1.1", "filepath": "/User/"}'
        self.assertEqual(result, expected)

    # XXX these seem like bad tests
    def test_encode_returns_object_with_byte_properties(self):
        transfer = server.Transfer('1', '/User/', '1.1.1.1')
        encoded = transfer.encode(b'')
        self.assertTrue(isinstance(encoded['url'], str))
        self.assertTrue(isinstance(encoded['transferId'], str))
        self.assertTrue(isinstance(encoded['filepath'], str))
        self.assertTrue(isinstance(encoded['userIp'], str))

    # XXX these seem like bad tests
    def test_encode_returns_object_with_correct_properties(self):
        transfer = server.Transfer('1', '/User/', '1.1.1.1')
        encoded = transfer.encode(b'')
        self.assertTrue(encoded['url'] is not None)
        self.assertTrue(encoded['transferId'] is not None)
        self.assertTrue(encoded['filepath'] is not None)
        self.assertTrue(encoded['userIp'] is not None)

    def test_to_json_returns_bytes(self):
        transfer = server.Transfer('1', '/User/', '1.1.1.1')
        url = 'json.com'
        result = transfer.toJson(url)
        self.assertTrue(isinstance(result, str))

    def test_to_json_returns_bytes_with_unicode_properties(self):
        transfer = server.Transfer('1', u'/Users/' + u'\u262D', '1.1.1.1')
        result = transfer.toJson("")
        self.assertTrue(isinstance(result, str))

    def test_to_json_encodes_unicode_properties(self):
        transfer = server.Transfer('1', u'/Users/' + u'\u262D', '1.1.1.1')
        result = transfer.toJson("")
        self.assertTrue(isinstance(result, str))
        expected = b'{"url": "/1/", "transferId": "1", ' \
                   b'"userIp": "1.1.1.1", "filepath": "/Users/\u262d"}'
        self.assertEqual(result, expected)

    def test_filename_bytes_returns_bytes_from_unicode_filename(self):
        asUnicode = unicode(b"/Users/\u262D")
        transfer = server.Transfer('1', asUnicode, '1.1.1.1')
        # what should this do?
        self.assertEqual(b'/Users/\u262D', transfer.filenameBytes())

    def test_filename_bytes_returns_bytes_from_byte_filename(self):
        transfer = server.Transfer('1', b'/Users/\u262D', '1.1.1.1')
        self.assertEqual(b'/Users/\u262D', transfer.filenameBytes())

    def test_url_returns_bytes(self):
        transfer = server.Transfer('1', b'plop', '1.1.1.1')
        self.assertEqual(b'json.com/1/', transfer.url(b'json.com'))


class OutboundRequestsTests(SynchronousTestCase):

    def setUp(self):
        self.transfer = server.Transfer('1', '/User/', '1.1.1.1')

    def test_add_adds_item(self):
        backend = dict()
        outbound = server.OutboundRequests(backend)
        outbound.add(self.transfer)
        self.assertTrue(self.transfer.transferId in backend.keys())

    def test_remove_removes_item(self):
        backend = {self.transfer.transferId: self.transfer}
        outbound = server.OutboundRequests(backend)
        outbound.remove(self.transfer.transferId)
        self.assertFalse(self.transfer.transferId in backend.keys())

    def test_remove_with_key_removes_item_returns_true(self):
        backend = {self.transfer.transferId: self.transfer}
        outbound = server.OutboundRequests(backend)
        self.assertTrue(outbound.remove(self.transfer.transferId))

    def test_remove_without_key_returns_false(self):
        outbound = server.OutboundRequests()
        self.assertFalse(outbound.remove('Nonexistant'))

    def test_get_existing_item_returns_item(self):
        backend = {self.transfer.transferId: self.transfer}
        outbound = server.OutboundRequests(backend)
        item = outbound.get(self.transfer.transferId)
        self.assertEqual(item, self.transfer)

    def test_get_nonexistant_item_returns_none(self):
        outbound = server.OutboundRequests()
        item = outbound.get(self.transfer.transferId)
        self.assertEqual(item, None)

    def test_all_returns_all_transfers(self):
        backend = {self.transfer.transferId: self.transfer}
        outbound = server.OutboundRequests(backend)
        self.assertEqual(outbound.all(), [self.transfer])


def _render(resource, request, notifyFinish=True):
    """
    Internal method used to render twisted resources for tests.
    """
    result = resource.render(request)

    if isinstance(result, str):
        request.write(result)
        request.finish()
        return succeed(None)
    elif result is NOT_DONE_YET:
        if request.finished or not notifyFinish:
            return succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class MockMixin(object):
    """
    A set of assertions that can be used to check if a deferred has
    fired or not.

    Must be used with a test implmementing TestCase
    """

    def assertFired(self, deferred, result=None):
        """
        Assert that the given deferred has fired with the given result.
        """
        self.assertEqual(self.successResultOf(deferred), result)

    def assertNotFired(self, deferred):
        """
        Assert that the given deferred has not fired with a result.
        """
        _pawn = object()
        result = getattr(deferred, 'result', _pawn)
        if result != _pawn:
            self.fail("Expected deferred not to have fired, "
                      "but it has: %r" % (deferred,))


class FileEndpointLogicTests(SynchronousTestCase, MockMixin):

    def test_with_non_existing_file_request_returns_no_resource(self):
        mockOb = MagicMock(server.OutboundRequests)
        mockOb.get.return_value = None
        outbound = mockOb
        app = server.FileEndpoint(outbound).app
        kr = KleinResource(app)

        request = requestMock('/nonexistant/', 'GET')

        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(mockOb.get.called)

        self.assertEqual(request.getWrittenData(),
                         NoResource().render(request))

    def test_with_existing_file_request_returns_directory_listing(self):
        transfer = server.Transfer('1', '.', '1.1.1.1')
        mockOb = MagicMock(server.OutboundRequests)
        mockOb.get.return_value = transfer

        outbound = mockOb
        app = server.FileEndpoint(outbound).app
        kr = KleinResource(app)

        url = u'/' + transfer.transferId + u'/'
        request = requestMock(url.encode('ascii', 'ignore'), 'GET')

        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(mockOb.get.called)
        self.assertIn(b'Directory listing',
                      request.getWrittenData())

    def test_with_filename_returns_entire_enclosing_directory(self):

        # make a temporary file
        path = self.mktemp()
        filepath.FilePath(path).create()

        transfer = server.Transfer('1', path, '1.1.1.1')
        mockOb = MagicMock(server.OutboundRequests)
        mockOb.get.return_value = transfer

        outbound = mockOb
        app = server.FileEndpoint(outbound).app
        kr = KleinResource(app)

        url = u'/' + transfer.transferId + u'/'
        request = requestMock(url.encode('ascii', 'ignore'), 'GET')

        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(mockOb.get.called)
        self.assertIn(b'Directory listing',
                      request.getWrittenData())

    def test_returns_no_resource_when_transfer_not_in_outbound_requests(self):
        mockOb = MagicMock(server.OutboundRequests)
        mockOb.get.return_value = None

        endpoint = server.FileEndpoint(mockOb)

        self.assertTrue(
            endpoint.getFile(request=None, transferId=b'bilbobaggins'),
            NoResource()
        )
        self.assertTrue(mockOb.get.called)


class UsersEndpointTests(SynchronousTestCase, MockMixin):
    """
    Tests for the UsersEndpoint.
    """
    def test_get_all_peers_returns_json_object(self):

        peerlist = MagicMock(peerdiscovery.PeerList)
        peerlist.all.return_value = iter([])
        app = server.UsersEndpoint(peerlist).app
        kr = KleinResource(app)

        request = requestMock('/', 'GET')
        d = _render(kr, request)

        self.assertFired(d)
        self.assertEqual(
            json.dumps({"users": []}),
            request.getWrittenData()
        )

    def test_get_all_peers_returns_peer_in_list(self):

        peerlist = MagicMock(peerdiscovery.PeerList)
        peer = peerdiscovery.Peer(b'paul', b'1.1.1.1', b'58673')
        peerlist.all.return_value = iter([peer])

        app = server.UsersEndpoint(peerlist).app
        kr = KleinResource(app)

        request = requestMock('/', 'GET')
        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(peerlist.all.called)

        self.assertEqual(
            json.dumps({"users": [peer.serialize()]}),
            request.getWrittenData()
        )

    def test_get_all_peers_returns_json(self):

        peerlist = MagicMock(peerdiscovery.PeerList)
        peerlist.all.return_value = iter([])

        app = server.UsersEndpoint(peerlist).app
        kr = KleinResource(app)

        request = requestMock('/', 'GET')
        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(peerlist.all.called)

        headers = request.responseHeaders.getRawHeaders('content-type')
        self.assertEqual(['application/json'], headers)


class OutboundRequestEndpointTests(SynchronousTestCase, MockMixin):

    def test_get_all_peers_returns_peer_in_list(self):

        transfer = server.Transfer('1', '.', '1.1.1.1')
        rootUrl = b'piazza.org'
        mockOb = MagicMock(server.OutboundRequests)
        mockOb.all.return_value = iter([transfer])

        app = server.OutboundRequestEndpoint(outboundRequests=mockOb,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=rootUrl).app
        kr = KleinResource(app)

        request = requestMock('/', 'GET')
        d = _render(kr, request)

        self.assertFired(d)
        self.assertTrue(mockOb.all.called)

        expected = json.dumps(
            {"files": [{
                "url": "piazza.org/1/",
                "transferId": "1",
                "userIp": "1.1.1.1",
                "filepath": "."
            }]})
        self.assertEqual(expected, request.getWrittenData())

    def test_parse_incoming_post_request_returns_new_transfer(self):
        app = server.OutboundRequestEndpoint(outboundRequests=None,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=None)
        request = json.dumps(
            {"filepath": "/Users/chris/Documents", "user": "1.1.1.1"}
        )
        body = StringIO(request)
        result = app.parse(body)
        self.assertTrue(result.transferId is not None)

    def test_parse_incoming_post_request_without_user(self):
        app = server.OutboundRequestEndpoint(outboundRequests=None,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=None)
        request = json.dumps(
            {"filepath": "/Users/chris/Documents"}
        )
        body = StringIO(request)
        self.assertRaises(server.MissingFormDataError, app.parse, body)

    def test_parse_incoming_post_request_without_filepath(self):
        app = server.OutboundRequestEndpoint(outboundRequests=None,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=None)
        request = json.dumps({"user": "1.1.1.1"})
        body = StringIO(request)
        self.assertRaises(server.MissingFormDataError, app.parse, body)

    def test_add_outbound_adds_new_transfer(self):
        mockOb = MagicMock(server.OutboundRequests)
        app = server.OutboundRequestEndpoint(outboundRequests=mockOb,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=None)
        app.addOutbound(server.Transfer('1', '.', '1.1.1.1'))
        self.assertTrue(mockOb.add.called)

    def test_add_outbound_returns_transfer(self):
        mockOb = MagicMock(server.OutboundRequests)
        app = server.OutboundRequestEndpoint(outboundRequests=mockOb,
                                             getFileNames=None,
                                             submitFileRequest=None,
                                             rootUrl=None)
        transfer = server.Transfer('1', '.', '1.1.1.1')
        result = app.addOutbound(transfer)
        self.assertEqual(result, transfer)

    def test_get_filenames(self):
        """
        This only tests that given a transfer, getFilenames returns that
        transfer and a set of filenames.
        """
        fakeResults = [b'/plop', b'/plop/foo']

        def fake(*args):
            return fakeResults
        app = server.OutboundRequestEndpoint(outboundRequests=None,
                                             getFileNames=fake,
                                             submitFileRequest=None,
                                             rootUrl=None)
        transfer = server.Transfer('1', '.', '1.1.1.1')
        deferred = app.getFilenames(transfer)

        def check(result):
            self.assertTrue(result[0], fakeResults)
            self.assertTrue(result[1], transfer)
        return deferred

    def test_requestTransfer_returns_transfer(self):
        """
        This function finishes up the new request. Test that it returns
        the transfer object it will send to the target user to the sending
        user as well.

        As of right now, this contains the file names and the root url.
        """
        fakeResults = [b'/plop', b'/plop/foo']

        def fakeSubmitter(*args):
            return

        app = server.OutboundRequestEndpoint(outboundRequests=None,
                                             getFileNames=None,
                                             submitFileRequest=fakeSubmitter,
                                             rootUrl='')

        transfer = server.Transfer('1', '.', '1.1.1.1')
        response = app.requestTransfer((fakeResults, transfer,))
        expected = '{"transfer": "/1/", "filenames": ["/plop", "/plop/foo"]}'

        self.assertEqual(expected, response)


class OutboundRequestEndpointIntegrationTests(SynchronousTestCase, MockMixin):

    def setUp(self):
        self.transfer = server.Transfer('1', '.', '1.1.1.1')
        self.patcher = patch(
            'teiler.server.OutboundRequestEndpoint.getFilenames',
            return_value=([b'/plop.txt'], self.transfer,)
        )
        self.patcher.start()

        def fakeSubmitter(*args):
            return

        self.outbound = server.OutboundRequests()
        self.endpoint = server.OutboundRequestEndpoint(
            outboundRequests=self.outbound,
            # getFilenames uses getFileNames. This will be patched; so the
            # method passed in will not be used.
            getFileNames=None,
            submitFileRequest=fakeSubmitter,
            rootUrl='')

        self.kr = KleinResource(self.endpoint.app)

    def tearDown(self):
        self.patcher.stop()

    def test_patch(self):
        self.assertEqual(
            self.endpoint.getFilenames(),
            ([b'/plop.txt'], self.transfer,)
        )

    def test_newTransfer_succeeds(self):

        body = json.dumps(
            {
                "filepath": "/plop.txt",
                "user": "1.1.1.1"
            }
        )
        request = requestMock('/', 'POST', body=body)

        d = _render(self.kr, request)
        self.assertFired(d)
        self.assertEqual(
            request.getWrittenData(),
            b'{"transfer": "/1/", "filenames": ["/plop.txt"]}'
        )


class InboundRequestEndpointTests(SynchronousTestCase, MockMixin):

    def test_parseTransferRequest_failure(self):
        downloadTo = "."
        requests = []

        def fakeParser(*args):
            raise filerequest.FileRequestError()

        endpoint = server.InboundRequestEndpoint(
            requests,
            downloadTo,
            fakeParser
        )

        kr = KleinResource(endpoint.app)

        body = json.dumps({})
        request = requestMock('/', 'POST', body=body)
        d = _render(kr, request)

        self.assertFired(d)

        self.assertEqual(
            request.getWrittenData(),
            b'{"status": "error", "error": "error parsing request"}'
        )

    def test_parseTransferRequest_success(self):
        downloadTo = "."
        requests = []

        def fakeParser(*args):
            return ['it worked. this is a weak fake']

        endpoint = server.InboundRequestEndpoint(
            requests,
            downloadTo,
            fakeParser
        )

        kr = KleinResource(endpoint.app)

        body = json.dumps({"type": "good request"})
        request = requestMock('/', 'POST', body=body)
        d = _render(kr, request)

        self.assertFired(d)

        self.assertEqual(
            request.getWrittenData(),
            b'{"status": "ok", "error": null}'
        )
