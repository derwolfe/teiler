"""
File sending is now being done strictly through HTTP.

The process is as follows
1)  A wants to send file f to B
2)  A sends a form as a post request containing 
        a) url root
        b) session key
        c) filename
3)  B parses the form as part of the post request and decides whether to
    grab the file using a get request and the parameters supplied in the form.

"""

from ..http_file_transfer import SendFileRequest, FileRequest, createFileRequest
from twisted.trial import unittest


class SendFileReuqestTests(unittest.TestCase):
    
    
    def test_render_post_adds_files(self):
        files = []
        resource = SendFileRequest(files)
        request = createFileRequest('url', 'chris')
        result = resource.render_POST(request)
        self.assertEqual(result, 'url')
        self.assertTrue(len(files) > 0)

#class HttpFileGrabberTests(unittest.TestCase):

    # def setUp(self):

    #     self.queue = []
    #     # set up the resource page to which fileRequests
    #     # will be submitted
    #     root.putChild('test', SendFileRequest(self.queue))
    
    # def test_filerequest_server_understands_posts(self):
    #     pass

        
