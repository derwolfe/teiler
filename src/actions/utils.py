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

# the following two list functions should be condensed into one function
# it should provide a relative path instead of an absolute path from the home computer
# i.e. instead of /home/chris/Downloads/ the file list should use Downloads as root 
# and all files to should relative to root

def _list_files(home):
    file_list = []
    for root, dirs, files in os.walk(home):
        for name in files:       
            filename = os.path.join(root, name)
            file_list.append(filename)
    return file_list

def _list_dirs(home):
    """get the list of directories that need to exist for the new files"""
    dir_list = []
    for root, dirs, files in os.walk(home):
        # here the root is the directory name 
        dir_list.append(root)
    return dir_list

def make_file_list(serve_at):
    """Creates a formatted file containing the directories and the
    files that need to be created on the host system. Directories are listed 
    first in the **dirs section, followed by files, listed in the **files section
    """
    os.chdir(serve_at)
    home = './'
    files = _list_files(home)
    dirs = _list_dirs(home)
    print 'Working directory for application at ' + os.getcwd()
    with open(serve_at + '/teiler-list.txt', 'w') as f:
        f.write('**dirs\n')
        for foo in dirs:
            f.write(foo + '\n')
        f.write('**files\n')
        for thing in files:
            f.write(thing + '\n')

                
