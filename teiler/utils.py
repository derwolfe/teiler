"""
The module is intended to be an abstraction that helps the user find the
local ip address that will be used for broadcasting. As windows, linux/mac
handle their interfaces differently, we want the correct IP address found 
and used.
"""

# come up with way to get the best interface to use to communicate
# with your peers
def getLiveInterface():
    # XXX this obviously needs real code, twisted, I believe has a function
    # that returns your ip
    return '127.0.0.1'

