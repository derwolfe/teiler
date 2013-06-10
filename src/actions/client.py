from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

from BeautifulSoup import BeautifulSoup, SoupStrainer
import requests

fileserver = ''
urls = []

def get_file_urls(self, url):
    f = requests.get("http://" + url)
    for link in BeautifulSoup(f, parseOnlyThese=SoupStrainer('a')):
        self.urls.append(link)
        print link

class MulticastClientUDP(DatagramProtocol):
    
    def __init__(self):
        self.host = '224.0.0.5'

    def startProtocol(self):
        # this could be placed in a config
        self.transport.joinGroup(self.host)

    def datagramReceived(self, datagram, address):
        print "Received: " + repr(datagram)
        fileserver = repr(datagram).replace("'", "")

        # this will need more checking - it is killing the conn once it receives the address
        self.transport.loseConnection()
        reactor.stop()    

    
# once you receive the message then add it to the 

def main():
    print "Listening"
    reactor.listenMulticast(8005, 
                            MulticastClientUDP(),
                            listenMultiple = True)
    
    reactor.run()
    # is the reactor done?
    get_file_urls(fileserver)
    

if __name__ == '__main__':
    main()
