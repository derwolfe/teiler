import os
import uuid
import M2Crypto
import ntpath

def generateSessionID():
    return uuid.UUID(bytes = M2Crypto.m2.rand_bytes(16))

def getFilenameFromPath(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

                
