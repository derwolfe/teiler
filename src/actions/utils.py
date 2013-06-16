import os
import netifaces

"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting. As windows, linux/mac 
handle their interfaces differently, we want the correct IP address found and used.
"""

def get_live_interface():
    """will return a list of possible IPv4 addresses"""
    addresses = []
    local_network = ['127.0.0.1', '127.0.1.1', '127.1.1.1']

    # loop over the available network interfaces and try to get the LAN level IP
    for iface in netifaces.interfaces():
        test_iface = netifaces.ifaddresses(iface).get(netifaces.AF_INET) 
        if test_iface is not None:
            for i in test_iface:
                if i['addr'] not in local_network:
                    addresses.append(i['addr'])
    # return the address to broadcast out
    return addresses[0] 


def list_files():
    file_list = []
    for root, dirs, files in os.walk('./'):
        for name in files:       
            filename = os.path.join(root, name)
            file_list.append(filename[2:])
    return file_list

def list_dirs():
    """get the list of directories that need to exist for the new files"""
    dir_list = []
    for root, dirs, files in os.walk('./'):
        # here the root is the directory name 
        dir_list.append(root[2:])
    return dir_list

def make_file_list(files, dirs):
    with open('teiler-list.txt', 'w') as f:
        f.write('**dirs')
        for foo in dirs:
            f.write(foo + '\n')
        f.write('**files')
        for thing in files:
            f.write(thing + '\n')

                
