import os
import errno
import sys

from twisted.python import log
from twisted.internet.protocol import DatagramProtocol

from twisted.application.internet import MulticastServer

import requests

# should be limited to this module only
_fileserver = ''

"""
There are several ways you could go about getting the directory objects.
The easiest might be to make teiler-data be a json object. In the json object
you could have a directory tree containing all of the dirs that need to be 
created

Further, the client should use some sort of class instead of a global file server
variable

"""

def get_file_urls(url):
    r = requests.get("http://" + url + '/teiler-list.txt')
    if r.status_code == 200:
        save(r.content, 'teiler-list.txt')
    else:
        print "Fileserver not at specified address"
            
# def _get_file(handle):
#     """Download all fo the files specified in the file provided by teiler-list.txt"""
#     # make sure the path exists into which the file will be downloaded
#     check_path(handle)
#     r = requests.get('http://' + _fileserver + '/' + handle)
#     if r.status_code == 200:
#         with open(handle, 'rb') as f:
#             for chuck in r.iter_content(1024):
#                 f.write(chunk)
                
#def get_files(files):
#    with open('teiler-list.txt', 'r') as f:
#        for line in f:
#            _get_file(line)
            
def save(stuff, name):
    with open(name, 'w') as f:
        f.write(stuff)
            
class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        # this could be placed in a config
        self.transport.joinGroup(self.host)

    def datagramReceived(self, datagram, address):
        log.msg("Received: " + repr(datagram))
        global _fileserver
        _fileserver = repr(datagram).replace("'", "")
        
        # kill connection 
        self.transport.loseConnection()
        reactor.stop()    

def main():
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    log.msg("Starting listener")
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    
    reactor.run()
    # async **should** be over
    # reactor is closed at this point.
    get_file_urls(_fileserver)
    #get_files('teiler-list.txt')

if __name__ == '__main__':
    main()
