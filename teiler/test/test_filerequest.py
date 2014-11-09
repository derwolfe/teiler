"""
Tests for the FileRequest module.
"""

from teiler import filerequest

from twisted.internet.defer import Deferred
from twisted.trial import unittest


class ParseFileRequestTests(unittest.SynchronousTestCase):

    def test_parse_file_req_ret(self):
        request = {
            'url': ['192.168.1.1'],
            'filenames': ['foo/plop,foo/bar/baz.txt'],
            'directories': ['foo,foo/bar']
        }
        downdir = "."
        result = filerequest.parseFileRequest(request, downdir)
        self.assertEqual(2, len(result.files))
        self.assertEqual('foo/plop', result.files[0])
        self.assertEqual('foo/bar/baz.txt', result.files[1])

        self.assertEqual(2, len(result.directories))
        self.assertEqual('foo', result.directories[0])
        self.assertEqual('foo/bar', result.directories[1])

    def test_malformed_request_raises_missing_url_exception(self):
        request = {
            'filenames': ['plop', 'foo/bar/baz.txt'],
            'directories': ['foo/bar'],
        }
        downdir = "."
        self.assertRaises(
            filerequest.MissingUrlError,
            filerequest.parseFileRequest,
            request,
            downdir
        )

    def test_malformed_request_raises_missing_files_exception(self):
        request = {
            'url': 'foo://foo',
            'directories': [],
        }
        downdir = "."
        self.assertRaises(
            filerequest.MissingFilesError,
            filerequest.parseFileRequest,
            request,
            downdir
        )

    def test_malformed_request_raises_missing_dir_exception(self):
        request = {
            'url': 'foo//foo',
            'filenames': ['imafile']
        }
        downdir = "."
        self.assertRaises(
            filerequest.MissingDirectoriesError,
            filerequest.parseFileRequest,
            request,
            downdir
        )


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


class FileRequestTests(unittest.SynchronousTestCase):

    def setUp(self):
        self.url = 'here'
        self.files = ['file1']
        self.directories = ['home']
        self.downloadTo = '.'
        self.frequest = filerequest.FileRequest(self.url,
                                                self.files,
                                                self.directories,
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
