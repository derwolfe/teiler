"""
A FileRequest object contains all of the information needed to transmit (that
is to grab) a set of of files from one user to another.
"""
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
    # newpath likely contains a filename, so we need to make the parentdirs
    toCreate.parent().makedirs()

def getClientFileName(downloadTo, filename):
    """
    Get the fully qualified file name.
    :param downloadTo: the location where downloads are saved
    :paramtype: string

    :param filename: the new filename
    :paramtype string:
    
    :returns: a filepath
    """
    return filepath.FilePath(filepath.joinpath(downloadTo, newPath))

# this file receiver has a lot of overlap with file request, they shoud be
# unified into a single class, this way the progress of the entire filerequest
# can be managed as a whole.
class FileRequest(object):
    def __init__(self, url, files, downloadTo):
        self.url = url
        # the files to download
        self.files = files
        # where the files should be downloaded to, root dir
        self._downloadTo = downloadTo
        # initialilly no files are being downloaded
        self._downloading = []

    def __repr__(self):
        return "{0}".format(self.url)

    def getFiles(self):
        # this basically makes a request for each file in rapid succession
        # and does NOT await the result (use semaphore if you need to)
        deferreds = []
        while self.files:
            filename = self.files.pop()
            self._downloading.append(filename)
            # make the directories where the file should live.
            _createFileDirs(self.downloadTo, filename)
            url = self.url + '/' + filename
            # make a new filepath where the file should live
            # use filepath.FilePath
            #clientFileName = os.path.join(self.downloadTo, filename)
            clientFileName = getClientFileName(self.downloadTo, filename)
            # sets up the transfer, downloads into clientFileName
            fileDownload = DownloadAgent(reactor, url, clientFileName) 
            self._downloading.append(fileDownload)
            deferred = fileDownload.getFile()
            deferreds.append(deferred)
