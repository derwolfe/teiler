"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting.
"""
import netifaces
from twisted.python import filepath


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
    path = filepath.FilePath(path)
    names = ['/'.join(subpath.segmentsFrom(path.parent()))
             for subpath in path.walk()]
    return names

if __name__ == '__main__':
    address = getLiveInterface()
    print 'addr: %s' % address
