from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

from BeautifulSoup import BeautifulSoup, SoupStrainer
import requests

# should be limited to this module only
_fileserver = ''
_urls = []

def get_file_urls(url):
    r = requests.get("http://" + url)
    if r.status_code == 200:
        for link in BeautifulSoup(f, parseOnlyThese=SoupStrainer('a')):
            global _urls
            _urls.append(link)
    print "Fileserver not at specified address"
    return

def get_files():
    print urls
    #for handle in _urls:
    #    r = requests.get('http://' + filserver + '/' + handle)
    #    if r.status_code == 200:
    #        with open(handle, 'rb') as f:
    #            for chuck in r.iter_content(1024):
    #                f.write(chunk)


class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        # this could be placed in a config
        self.transport.joinGroup(self.host)

    def datagramReceived(self, datagram, address):
        print "Received: " + repr(datagram)
        global _fileserver
        _fileserver = repr(datagram).replace("'", "")

        # this will need more checking - it is killing the conn 
        # once it receives the address
        self.transport.loseConnection()
        reactor.stop()    

def main():
    print "Listening"
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    
    reactor.run()
    # async **should** be over
    # reactor is closed at this point.
    get_file_urls(_fileserver)
    

if __name__ == '__main__':
    main()
