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
        self.assertEqual(result.filenames, ['temp'])

    def test_returns_directories(self):
        """
        All directories that are children of the root directory are returned.
        """
        path = self.mktemp()
        os.mkdir(path)
        result = utils.getFilenames(path)
        self.assertEqual(['temp'], result.directories)

    def test_paths_are_relative_to_root_of_file(self):
        """
        Filepaths are all relative to the target directory
        passed in.
        """
        targetpath = self.mktemp()
        # create a directory at root named temp
        os.mkdir(targetpath)
        # create a file inside of 'temp' named 'newtmp'
        filepath.FilePath(targetpath).child('newtmp').touch()

        result = utils.getFilenames(targetpath)
        self.assertEqual(['temp'], result.directories)
        self.assertEqual(['temp/newtmp'], result.filenames)
