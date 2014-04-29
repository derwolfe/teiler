from twisted.trial import unittest
from twisted.internet.defer import Deferred

from .. import filerequest


class ParseFileRequestTests(unittest.TestCase):

    def test_parse_file_req_returns_two_files_and_url(self):
        request = {'url': ['192.168.1.1'], 'files': ['plop,foo/bar/baz.txt']}
        downdir = "."
        result = filerequest.parseFileRequest((request, downdir,))
        self.assertTrue(len(result.files) == 2)
        self.assertTrue(result.files[0] == 'plop')
        self.assertTrue(result.files[1] == 'foo/bar/baz.txt')

    def test_malformed_request_raises_form_args_exception(self):
        request = {'urls': [], 'files': ['plop,foo/bar/baz.txt']}
        downdir = "."
        self.assertRaises(filerequest.FormArgsError,
                          filerequest.parseFileRequest,
                          (request, downdir,))


class FakeDownloader(object):
    """
    Fake download agent object
    """
    def __init__(self):
        self.called = 0
        self.requests = []

    def getFile(self, url, filepath):
        d = Deferred()
        self.requests.append(url)
        self.called += 1

        def finish(ignored):
            return True
        d.addBoth(finish)
        return d


def fakeCreateFileDirs(downloadTo, newPath):
    """
    Stand in for createFileDirs. Same args, no side effect.
    """
    return True


class FileRequestTests(unittest.TestCase):

    def setUp(self):
        self.url = 'here'
        self.files = ['file1']
        self.downloadTo = '.'
        self.frequest = filerequest.FileRequest(self.url,
                                                self.files,
                                                self.downloadTo)

    def test_get_files_adds_files_to_downloading(self):
        self.frequest.getFiles(FakeDownloader(), fakeCreateFileDirs)
        self.assertTrue(self.frequest.downloading == ['file1'])
        self.assertTrue(len(self.frequest.downloading) == 1)

    def test_get_files_removes_files_from_files(self):
        self.frequest.getFiles(FakeDownloader(), fakeCreateFileDirs)
        self.assertTrue(len(self.frequest.files) == 0)

    def test_get_files_with_url_and_filename(self):
        self.frequest.getFiles(FakeDownloader(), fakeCreateFileDirs)
        self.assertTrue(len(self.frequest.history) == 1)
        self.assertTrue(self.frequest.history == ['here/file1'])
