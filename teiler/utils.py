"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting.
"""
import netifaces
from twisted.python import filepath
import json


def getLiveInterface():
    """
    Return the LAN address of this machine.
    """
    ifaces = netifaces.interfaces()
    for layer in ifaces:
        addrs = netifaces.ifaddresses(layer)
        link = addrs.get(netifaces.AF_INET)
        # this bit needs cleaning up. It doesn't cover enough cases
        # how can you test this??
        if link:
            subaddr = link[0]
            octet = subaddr['addr']
            if octet[:3] != '127':
                return subaddr['addr']


def getFilenames(path):
    """
    Given a path, find all of the file and directory names that are
    the path's children.

    :returns: a Paths object containing filenames and directories.
    :rtype:  Paths object
    """
    path = filepath.FilePath(path)
    if path.isfile():
        # get the filename only
        print str(path.basename())
        return Paths(path.basename(), [])
    else:
        filenames = []
        dirs = set()
        for subpath in path.walk():
            name = '/'.join(subpath.segmentsFrom(path.parent()))
            if subpath.isfile():
                filenames.append(name)
                if subpath.isdir():
                    dirs.add(name)
        return Paths(filenames, list(dirs))


class Paths(object):
    """
    Files and paths as an object
    """
    def __init__(self, filenames, directories):
        self.filenames = filenames
        self.directories = directories


def sortedDump(data):
    """
    return the data object as serialized json, with the keys sorted
    alphabetically.

    :param data: any data structure that can be serialized.
    :returns: a serialized object encoded in utf-8 with all keys sorted
    alphabetically.
    """
    return json.dumps(data, sort_keys=True)
