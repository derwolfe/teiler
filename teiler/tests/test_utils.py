"""
Tests for teiler utilities.
"""

from twisted.trial.unittest import SynchronousTestCase
from twisted.python import filepath
# from teiler import utils


class TestSortedDump(SynchronousTestCase):
    pass

    def test_sorts(self):
        data = {'z': '1', 'a': 'strano'}
        result = utils.sortedDump(data)
        self.assertEqual(
            '{"a": "strano", "z": "1"}',
            result
        )

class TestGetFilenames(SynchronousTestCase):

    def setUp(self):
        self.path = self.mktemp()
        filepath.FilePath(self.path).create()

    def test_returns_files(self):
        self.fail()

    def test_returns_directories(self):
        self.fail()

    def test_paths_are_relative_to_application(self):
        self.fail()
