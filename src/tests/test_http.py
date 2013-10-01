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

from ..http_file_transfer import parseFileRequest
from twisted.trial import unittest
from urllib import urlencode

class HttpFileGrabberTests(unittest.TestCase):
    

    def test_parses_form(self):
        """
        Given a properly formatted form, can i parse it
        """
        address = 'a'
        session = '1'
        filename = '/bar'
        senderAddress = 'b'
        data = {'address': [address,], 'senderAddress': [senderAddress,], 'session': [session,], 'filename': [filename,]}
        addr, senderAddr, sess, fname = parseFileRequest(data)
        self.assertEqual(address, addr)
        self.assertEqual(session, sess)
        self.assertEqual(filename, fname)
        self.assertEqual(senderAddress, senderAddr)


    def posts_form(self):
        """
        server is able to post form to a client
        """
        pass
