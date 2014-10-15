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
        if link:
            subaddr = link[0]
            octet = subaddr['addr']
            if octet[:3] != '127':
                return subaddr['addr']


def getFilenames(path):
    """
    Given a path, find all of the file and directory names that are
    the path's children.

    This function expects that path is a directory and not a single
    file path.

    :returns: a list of directories and a list of filenames
    :rtype: list, list
    """
    path = filepath.FilePath(path)
    filenames = []
    dirs = set()
    for subpath in path.walk():
        name = '/'.join(subpath.segmentsFrom(path.parent()))
        if subpath.isfile():
            filenames.append(name)
        if subpath.isdir():
            dirs.add(name)
    return list(dirs), filenames



def sortedDump(data):
    """
    return the data object as serialized json, with the keys sorted
    alphabetically.

    :param data: any data structure that can be serialized.
    :returns: a serialized object encoded in utf-8 with all keys sorted
    alphabetically.
    """
    return json.dumps(data, sort_keys=True)


if __name__ == '__main__':
    address = getLiveInterface()
    print 'addr: %s' % address
