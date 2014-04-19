"""
A FileRequest object contains all of the information needed to transmit (that
is to grab) a set of of files from one user to another.
"""
from twisted.internet import reactor
from twisted.python import filepath
from twisted.internet.defer import Deferred

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

def getFileUrl(rooturl, filename):
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

def getNewFilePath(downloadTo, filename):
    """
    Get the fully qualified file name.
    :param downloadTo: the location where downloads are saved
    :paramtype: string

    :param filename: the new filename
    :paramtype string:

    :returns: a filepath
    """
    return filepath.FilePath(filepath.joinpath(downloadTo, filename))

class IOHandler(object):
    """
    IOHandler is responsible for creating changes to a file system,
    i.e. creating or destroying files.
    """

    def createFileDirs(self, downloadTo, newPath):
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
    def __init__(self, url, files, downloadTo):
        self.url = url
        # the files to download
        self.files = files
        # where the files should be downloaded to, root dir
        self._downloadTo = downloadTo
        # initialilly no files are being downloaded
        self._downloading = []
        self._history = []
        
    def __repr__(self):
        return "{0}".format(self.url)

    def getFiles(self, downloader, IOHandler):
        """
        getFiles downloads all of the files listed ina fileRequest. It
        handles building the necessary directories.
        
        :param downloader: a DownloadAgent object is necessary to download files.
        The object must have a method getFiles that returns a deferred.
        """
        # this basically makes a request for each file in rapid succession
        # and does NOT await the result (use semaphore if you need to)
        # pass in a DownloadAgent with a getFile method
        deferreds = []
        while self.files:
            filename = self.files.pop()
            self._downloading.append(filename)
            IOHandler.createFileDirs(self._downloadTo, filename)
            url = getFileUrl(self.url, filename)
            self._history.append(url)
            newFile = getNewFilePath(self._downloadTo, filename)
            d = downloader.getFile(url, filename)
            deferreds.append(d)
        return deferreds
