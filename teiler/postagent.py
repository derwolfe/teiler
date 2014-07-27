#!/usr/bin/env python
# -*- coding: utf-8
# -*- test-case-name: tests.test_postagent -*-

"""
postagent - Handles POSTing file requests to other users
"""
from twisted.internet import reactor, defer
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from twisted.python import log

from zope.interface import implements


JSONHEADERS = {'Content-type': 'application/json'}


class StringProducer(object):
    """
    Stringproducer is used to send in memory post data.
    """
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def submitFileRequest(recipient, data, producer=StringProducer):
    """
    This is a generic agent meant to make post requests.

    :param recipient: a web or IP address and port combination.
    :param data: all of the data, packaged, and ready to be sent as request.

    :returns: a deferred that will fire when a response body is available.
    """
    log.msg("submitFileRequest:: data:", recipient, system="httpFileTransfer")
    headers = Headers()
    headers.setRawHeaders('Content-type', ['application/json'])
    return Agent(reactor).request("POST",
                                  recipient,
                                  headers,
                                  producer(data))
