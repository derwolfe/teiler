#!/usr/bin/env python
# -*- coding: utf-8
# -*- test-case-name: tests/test_downloader.py -*-

"""
downloadagent

This download agent makes it possible to return the current status of a file
transfer.
"""
from __future__ import division

from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.python import log
from twisted.web.http_headers import Headers
from twisted.internet.defer import Deferred


class FileWriter(Protocol):
    """
    FileWriter writes the data to a file like object and can report the
    progress of a file transfer.
    """
    def __init__(self, finished, filesize, filename, ioHandler, progress):
        """
        :param finished: a callback to be called when transmission has finished
        :param filesize: the expected length of the file
        :param filepath: the path to where the new file should be saved.
        :param ioHandler: an object can open, write to, and close file-like
                          objects.
        :param progress: an object that can
        """
        self._finished = finished
        self._written = 0
        self._filesize = filesize
        self._remaining = filesize
        self._ioHandler = ioHandler
        self._openedFile = self._ioHandler.open(filename)
        self._progress = progress

    def currentProgress(self):
        """
        Return the current percentage of the file transferred.
        """
        return (self._written / self._filesize) * 100

    def dataReceived(self, data):
        """
        Write received data to file-like object and update progress counters.
        """
        if self._remaining > 0:
            self._written += len(data)
            self._remaining -= len(data)
            self._ioHandler.write(data)
            self._progress.add(self.currentProgress())
        else:
            self.connectionLost()

    def connectionLost(self, reason):
        """
        Connection closed
        """
        log.msg('Finished receiving body:', reason.getErrorMessage(),
                system="FileWriter")
        self._ioHandler.close()
        self._finished.callback(None)


class DownloadProgress(object):
    """
    DownloadProgress reports the progress of a download. It does
    this by maintaining an internal progress counter.
    """
    def __init__(self):
        self._progress = [0.0]

    def add(self, increase):
        self._progress.append(increase)

    def current(self):
        """
        current returns the most recently received progress state.
        :returns: an int
        """
        return int(self._progress[-1])


def getFile(reactor, url, filename, ioHandler, progress):
    """
    Download file is similar to web.client.getPage except it is able
    the progress of the download in real time.

    :param reactor: the reactor being used by the system
    :param url: the url where the file is located
    :param filename: the filename to write the file to.
    :param ioHandler: an object that performs open, write, close on file-
                      like objects.
    :param progress: an object to which period progress updates can be added.

    :returns: a deferred object.
    """
    d = Agent(reactor).request('GET', url,
                               Headers({'User-Agent': ['Teiler']}),
                               None)

    def cbRequest(response):
        """
        This callback fires when the response headers have been received.
        """
        finished = Deferred()
        response.deliverBody(FileWriter(finished, response.length,
                                        filename, ioHandler,
                                        progress))
        return finished
    d.addCallback(cbRequest)
    return d


class IOHandler(object):
    """
    IOHandler opens files, writes to them, and closes them.
    """
    def __init__(self):
        self._openedFile = None

    def open(self, path):
        """
        Open a file like object
        """
        self._openedFile = open(path, 'w')

    def close(self):
        """
        Close a file like object.
        """
        self._openedFile.close()

    def write(self, data):
        """
        Write to the file held in self.
        :param data: the data to write
        """
        self._openedFile.write(data)
