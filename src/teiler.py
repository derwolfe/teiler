import argparse
import os
import sys
import utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
 
import qt4reactor

qt_app = QApplication(sys.argv)
qt4reactor.install()

from twisted.python import log
from twisted.internet import reactor
import filetransfer
from filetransfer import FileReceiverFactory
from peerdiscovery import PeerDiscovery
from peerlist import TeilerPeer, TeilerPeerList
        
# Class to maintain the state of the program
class TeilerState():
    def __init__(self):
        self.address = utils.getLiveInterface()
        self.sessionID = utils.generateSessionID()
        self.name = "name@%s" % self.address
        self.peerList = TeilerPeerList()
        self.messages = []
        self.multiCastAddress = '230.0.0.30'
        self.multiCastPort = 8005
        self.tcpPort = 9988


# Class for the GUI
class TeilerWindow(QWidget):

    def __init__(self, teiler):
        # Initialize the object as a QWidget and
        # set its title and minimum width
        QWidget.__init__(self)
        self.teiler = teiler
        self.setWindowTitle('BlastShare')
        self.setMinimumSize(240, 480)
        self.connect(self.teiler.peerList, SIGNAL("dropped"), self.sendFileToPeers)

        shareFilesAction = QAction(QIcon('exit.png'), '&Share File(s)', self)
        shareFilesAction.setShortcut('Ctrl+O')
        shareFilesAction.setStatusTip('Share File(s)')
        shareFilesAction.triggered.connect(quitApp)

        preferencesAction = QAction(QIcon('exit.png'), '&Preferences', self)
        preferencesAction.setShortcut('Ctrl+P')
        preferencesAction.setStatusTip('Preferences')
        preferencesAction.triggered.connect(quitApp)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(quitApp)

        menubar = QMenuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(shareFilesAction)
        fileMenu.addAction(preferencesAction)
        fileMenu.addAction(exitAction)

        # Create the QVBoxLayout that lays out the whole form
        # self.teiler.peerList.setAcceptDrops(True)
        # self.teiler.peerList.setDragEnabled(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(layout)
        
        statusBar = QStatusBar()
        statusBar.showMessage('Ready')
        
        layout.addWidget(menubar)
        layout.addWidget(self.teiler.peerList)
        layout.addWidget(statusBar)

    def sendFileToPeers(self, fileName):
        log.msg("OMG Dropped {0}".format(fileName))

    def run(self):
        self.show()
        qt_app.exec_()

def quitApp():
    reactor.stop()
    qApp.quit()

def download_path_exists():
    downloadPath = os.path.join(os.path.expanduser("~"), "blaster")
    if os.path.exists() == False:
        os.mkdir(downloadPath)


def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()
    
    # Initialize peer discovery using UDP multicast
    multiCastPort = 8006
    teiler = TeilerState()
    teiler.multiCastPort = multiCastPort
    reactor.listenMulticast(multiCastPort, 
                            PeerDiscovery(teiler), 
                            listenMultiple=True)
    log.msg("Initiating Peer Discovery")
    
    # Initialize file transfer service
    fileReceiver = FileReceiverFactory(teiler)
    reactor.listenTCP(teiler.tcpPort, fileReceiver)
    log.msg("Starting file listener on ", teiler.tcpPort)
    
    # qt4reactor requires runReturn() in order to work
    reactor.runReturn()
    
    # filetransfer.sendFile("/home/armin/tempzip.zip",port=teiler.tcpPort,address=teiler.address)
    # Create an instance of the application window and run it
    app = TeilerWindow(teiler)
    app.run()

if __name__ == '__main__':
    download_path_exists()
    main()
