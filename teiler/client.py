"""
A FileRequestResource receives POSTed file requests. To be clear these are
requests from the person wanting to share the file with the client. This is
important. The system is assuming that the driver of the system is the user who
wants to SEND a file to another user.

However, the recipient of the file transfer can decline a transfer request.
"""
from twisted.web.resource import Resource
from twisted.internet.defer import Deferred

from twisted.web.server import NOT_DONE_YET

import filerequest

# this is basically the TransferRequestEndpoint
class FileRequestResource(Resource):
    """
    FileRequestResource fields requests for file transfers.
    
    Expose a simple endpoint where other users can post transfer requests.

    The resource accepts POSTed json data messages containing file location
    information.
    """
    def __init__(self, transferRequests, downloadTo):
        """
        """
        Resource.__init__(self)
        # list of files that others want to transfer to you
        self.transferRequests = transferRequests
        # top level directory into which files will be saved
        self.downloadTo = downloadTo

    def _parseForm(self, request):
        d = Deferred()
        d.addCallback(filerequest.parseFileRequest)
        # can you save it
        def successfulParse(data):
            self.transferRequests.append(data)
            request.write("ok") # this is not being returned outside
            request.finish()
        def parseFailure(failure):
            request.write("error parsing request")
            request.finish()
        d.addCallbacks(successfulParse, parseFailure)
        d.callback((request.args, self.downloadTo,))

    def render_GET(self, request):
        """
        The resource has no need to render GET requests.
        """
        pass

    def render_POST(self, request):
        """
        respond to post requests. This is where the file sender processing
        will begin.

        File locations will be posted to this URL for the recipient to
        download later.
        """
        d = Deferred()
        d.addCallback(self._parseForm)
        d.callback(request)
        return NOT_DONE_YET

