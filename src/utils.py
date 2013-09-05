"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting. As windows, linux/mac 
handle their interfaces differently, we want the correct IP address found and used.
"""
import os
import pwd
import netifaces
import uuid
import M2Crypto
import ntpath

def getLiveInterface():
    """will return a list of possible IPv4 addresses"""
    addresses = []
    local_network = ['127.0.0.1', '127.0.1.1', '127.1.1.1']

    # loop over the available network interfaces and try to get the LAN level IP
    for iface in netifaces.interfaces():
        test_iface = netifaces.ifaddresses(iface).get(netifaces.AF_INET) 
        if test_iface is not None:
            for i in test_iface:
                # you need to make sure it is a local
                if i['addr'] not in local_network and '192.' in i['addr']:
                    addresses.append(i['addr'])
    return addresses[0] 

def generateSessionID():
    return uuid.UUID(bytes = M2Crypto.m2.rand_bytes(16))

def getUsername():
    """get the username by accessing env vars"""
    return pwd.getpwuid(os.getuid()).pw_name.title()

def getFilenameFromPath(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_file_string_length(file):
    """Get the string length of a file. Since we are using a string/line
    based protocol we are more concerned with the length of file in characters,
    and less with its size as a file...I think"""
    ct = 0
    with open(file, "r") as f:
        for line in f.readlines():
            ct = len(line) + ct
    return ct
