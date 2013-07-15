import argparse
import os
import sys
import utils
from PySide.QtCore import *
from PySide.QtGui import *

import qt4reactor

qt_app = QApplication(sys.argv)
qt4reactor.install()

from actions import server
from twisted.python import log
from twisted.internet import reactor
import filetransfer
from filetransfer import FileReceiverFactory
from peerdiscovery import PeerDiscovery

# Class to maintain the state of the program
class TeilerState():
    def __init__(self):
        self.address = utils.getLiveInterface()
        self.sessionID = utils.generateSessionID()
        self.peers = []
        self.messages = []
        self.multiCastAddress = '230.0.0.30'
        self.multiCastPort = 8005
        self.tcpPort = 9988
        self.downloadPath = "/home/armin/Downloads"

# Class for the GUI
class TeilerWindow(QWidget):

    def __init__(self):
        # Initialize the object as a QWidget and
        # set its title and minimum width
        QWidget.__init__(self)
        self.setWindowTitle('BlastShare')
        self.setMinimumSize(240, 480)

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
        self.peerList = QListWidget(self)
        self.peerList.setAcceptDrops(True)
        self.peerList.setDragEnabled(True)
        self.peerList.addItem("Peer 1")
        self.peerList.addItem("Peer 2")
        self.peerList.addItem("Peer 3")

        layout = QVBoxLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(layout)
        
        statusBar = QStatusBar()
        statusBar.showMessage('Ready')
        
        layout.addWidget(menubar)
        layout.addWidget(self.peerList)
        layout.addWidget(statusBar)

    def run(self):
        self.show()
        qt_app.exec_()

def quitApp():
    reactor.stop()
    qApp.quit()

def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()
    
    # Initialize peer discovery using UDP multicast
    multiCastPort = 8006
    teiler = TeilerState()
    teiler.multiCastPort = multiCastPort
    reactor.listenMulticast(multiCastPort, PeerDiscovery(teiler), listenMultiple=True)
    log.msg("Initiating Peer Discovery")
    
    #Initialize file transfer service
    fileReceiver = FileReceiverFactory(teiler)
    reactor.listenTCP(teiler.tcpPort, fileReceiver)
    log.msg("Starting file listener on ", teiler.tcpPort)
    
    #qt4reactor requires runReturn() in order to work
    reactor.runReturn()
    
    #filetransfer.sendFile("/home/armin/tempzip.zip",port=teiler.tcpPort,address=teiler.address)
    # Create an instance of the application window and run it
    app = TeilerWindow()
    app.run()

if __name__  == '__main__':
    main()
