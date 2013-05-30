from twisted.internet.protocol import protocol

class Echo(Protocol):
    
    def dataReceived(self, data):
        self.transport.write(data)

    

