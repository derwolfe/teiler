import argparse
import os
import sys
from actions import server
from twisted.python import log

# the main entry point for the application
# for simplicity, let's decide that the user decides at runtime to listen
# and the server decides to serve

# location from which files should be served
_home = os.path.expanduser("~")
_app_directory = os.path.join(os.path.expanduser("~"), "blaster")


def main():
    log.startLogging(sys.stdout)
    parser = argparse.ArgumentParser(description="Exchange files!")
    args = parser.parse_args()

def _app_runner():
    if os.path.exists(_app_directory) == False:
            os.mkdir(_app_directory)
    server.main()
    

if __name__  == '__main__':
    main()
