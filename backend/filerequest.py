#!/usr/bin/env python
# -*- coding: utf-8
# -*- test-case-name: tests/test_filerequest.py -*-

"""
filerequest

A FileRequest object contains all of the information needed to transmit (that
is to grab) a set of of files from one user to another.
"""
from twisted.python import filepath


class FormArgsError(Exception):
    """
    Exception to be thrown when a form doesn't contain correct arguments.
    """
    pass


def _getFileNames(request):
    """
    given a request, return the filenames listed in the request.
    """
    return request["files"][0].split(',')


def _getFileUrl(rooturl, filename):
    """
    _getFileUrl creates a url from a base url and a filename.

    :param rooturl: the root url
    :param filename: a filename, relative to its base directory.
    :rtype: string
    """
    return rooturl + '/' + filename


def parseFileRequest(args):
    """
    Parse and create a new FileRequest object from a request.
    """
    request, downloadDir = args
    if "url" not in request or "files" not in request:
        raise FormArgsError()
    url = request["url"][0]
    files = _getFileNames(request)
    return FileRequest(url, files, downloadDir)


def _getNewFilePath(downloadTo, filename):
    """
    Get the fully qualified file name.
    :param downloadTo: the location where downloads are saved
    :paramtype: string

    :param filename: the new filename
    :paramtype string:

    :returns: a filepath
    """
    return filepath.FilePath(filepath.joinpath(downloadTo, filename))


def createFileDirs(downloadTo, newPath):
    """
    Make the directories that live between downloadTo and newPath. This only
    createsFiles and returns no information.

    :param downloadTo: where downloads are saved
    :paramtype: string

    :param newPath: where the new file will be saved
    :paramtype: string

    :returns: None
    """
    toCreate = filepath.FilePath(filepath.joinpath(downloadTo, newPath))
    parentDir = toCreate.parent()
    if not parentDir.exists():
        parentDir.makedirs()


class FileRequest(object):
    """
    A FileRequest contains all of the information need to download the
    files proposed by another user.
    """
    def __init__(self, url, files, downloadTo):
        """
        :param url: the base url from which the file request originated
        :paramtype url: string

        :param files: a list of filenames
        :paramtype files: list

        :param downloadTo: the path where the files will be saved.
        :paramtype downloadTo: string
        """
        self.url = url
        # the files to download
        self.files = files
        # where the files should be downloaded to, root dir
        self._downloadTo = downloadTo
        self.downloading = []
        self.history = []

    def __repr__(self):
        return "{0}".format(self.url)

    def getFiles(self, downloader, dirCreator):
        """
        getFiles downloads all of the files listed ina fileRequest. It
        handles building the necessary directories.

        :param downloader: a file downloader object.

        :param dirCreator: a function that can create directories
        """
        # this basically makes a request for each file in rapid succession
        # and does NOT await the result (use semaphore if you need to)
        # pass in a DownloadAgent with a getFile method
        deferreds = []
        while self.files:
            filename = self.files.pop()
            self.downloading.append(filename)
            dirCreator(self._downloadTo, filename)
            url = _getFileUrl(self.url, filename)
            self.history.append(url)
            newFile = _getNewFilePath(self._downloadTo, filename)
            d = downloader.getFile(url, newFile)
            # XXX this doesn't work yet, you're not using the deferreds
            deferreds.append(d)
        return deferreds
