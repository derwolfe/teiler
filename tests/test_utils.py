"""
Tests for teiler utilities.
"""
from twisted.trial.unittest import SynchronousTestCase
from twisted.python import filepath
from teiler import utils

import os


class TestSortedDump(SynchronousTestCase):

    def test_sorts(self):
        data = {'z': '1', 'a': 'strano'}
        result = utils.sortedDump(data)
        self.assertEqual(
            '{"a": "strano", "z": "1"}',
            result
        )


class TestGetFilenames(SynchronousTestCase):

    def test_returns_files(self):
        """
        All filenames under a given path are returned.
        """
        path = self.mktemp()
        filepath.FilePath(path).create()
        result = utils.getFilenames(path)
        self.assertEqual(['temp'], result.filenames)

    def test_returns_directories(self):
        """
        All directories that are children of the root directory are returned.
        """
        path = self.mktemp()
        os.mkdir(path)
        child = filepath.FilePath(path).child('child')
        os.mkdir(child.path)

        result = utils.getFilenames(path)
        self.assertIn('temp/child', result.directories)
        self.assertIn('temp', result.directories)

    def test_returns_no_directories_when_no_child_dirs(self):
        """
        All directories that are children of the root directory are returned.
        """
        path = self.mktemp()
        filepath.FilePath(path).create()
        result = utils.getFilenames(path)
        self.assertEqual([], result.directories)
