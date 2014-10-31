"""
filerequest

Filerequests are used to transfer files from one user to another.
This file is mainly focused on parsing received file requests.
"""
from twisted.python import filepath


class FormArgsError(Exception):
    """
    Exception to be thrown when a form doesn"t contain correct arguments.
    """
    pass


class MissingFilesError(FormArgsError):
    pass


class MissingDirectoriesError(FormArgsError):
    pass


class MissingUrlError(FormArgsError):
    pass


def _getDirectories(request):
    """
    :param request: a request object containing a list of directories.
    :returns list: a list of directory names
    """
    return request["directories"][0].split(",")


def _getFileNames(request):
    """
    given a request, return the filenames listed in the request.
    """
    return request["files"][0].split(",")


#  this could just be a class method...
def _getFileUrl(rooturl, filename):
    """
    _getFileUrl creates a url from a base url and a filename.

    :param rooturl: the root url
    :param filename: a filename, relative to its base directory.
    :rtype: string
    """
    return rooturl + "/" + filename


# xxx this is gross, fixme.
def parseFileRequest(request, downloadDir):
    """
    Parse and create a new FileRequest object from a request.
    """
    if "url" not in request:
        raise MissingUrlError()
    if "filenames" not in request:
        raise MissingFilesError()
    if "directories" not in request:
        raise MissingDirectoriesError()

    url = request["url"][0]
    files = _getFileNames(request)
    dirs = _getDirectories(request)
    return FileRequest(url, files, dirs, downloadDir)


def _getNewFilePath(downloadTo, filename):
    """
    Get the absolute file name.
    :param downloadTo: the location where downloads are saved
    :paramtype: string

    :param filename: the new filename
    :paramtype string:

    :returns: a filepath
    """
    return filepath.FilePath(filepath.joinpath(downloadTo, filename))


# xxx fixme
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

    def __init__(self, url, files, directories, downloadTo):
        """
        :param url: the base url from which the file request originated
        :param files: a list of filenames
        :param directories: a list of directories
        :param downloadTo: the path where the files will be saved.
        """
        self.url = url
        # the files to download
        self.files = files
        # where the files should be downloaded to, root dir
        self.directories = directories
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
            # XXX this doesn"t work yet, you're not using the deferreds
            deferreds.append(d)
        return deferreds
