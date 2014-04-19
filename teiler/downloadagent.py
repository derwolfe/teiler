"""
downloadAgent

This download agent makes it possible to return the current status of a file
transfer.
"""
from __future__ import division

from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.python.filepath import FilePath
from twisted.python import log
from twisted.web.http_headers import Headers
from twisted.internet.defer import Deferred

class FileWriter(Protocol):
    """
    FileWriter writes the bytes of a response to a given file.
    """
    def __init__(self, finished, filesize, filename):
        self.finished = finished
        self.written = 0
        self.filesize = filesize
        self.remaining = filesize
        self.openedFile = open(filename, "w")

    def getProgress(self):
        """
        Return the current percentage of the file transferred.
        """
        return (self.written / self.filesize) * 100

    def dataReceived(self, bytes):
        """
        Write the bites to a supplied file and update progress in the log.
        """
        if self.remaining > 0:
            self.written += len(bytes)
            self.remaining -= len(bytes)
            self.openedFile.write(bytes)
            log.msg('progress',
                    self.getProgress(),
                    system="DownloadAgent, FileWriter")
        else:
            self.connectionLost()


    def connectionLost(self, reason):
        log.msg('Finished receiving body:',
                reason.getErrorMessage(),
                system="DownloadAgent, FileWriter")
        self.openedFile.close()
        self.finished.callback(None)


class DownloadAgent(object):
    """
    Downloads files making the data available to a protocol.
    """
    # XXX why did i do it this way, is there a reason I need these instance
    # variables.
    def __init__(self, reactor, url, filename):
        self.reactor = reactor
        self.url = url
        self.filename = filename

    def getFile(self):
        """
        Download file is similar to web.client.getPage except it is able
        the progress of the download in real time.

        url - where the file is located
        filename - the path where the file should be saved.
        """
        agent = Agent(self.reactor)
        d = agent.request('GET',
                          self.url,
                          Headers({'User-Agent': ['Twisted Web Client']}),
                          None)

        # this gets called on the response from the request.
        # it will then pass through the specified transport
        def cbRequest(response):
            """
            consume the response data
            """
            finished = Deferred()
            # delivery body basically handles receiving the
            # entire response body, so no further cbs needed
            # in order to read the progress from this object, you need to
            # pass in all of the download information.
            response.deliverBody(FileWriter(finished,
                                            response.length,
                                            self.filename))
            return finished
        d.addCallback(cbRequest)
        return d
