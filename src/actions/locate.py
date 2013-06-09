import netifaces

# the module is intended to be an abstraction that helps the user find the
# local ip address that will be used for broadcasting. As windows, linux/mac 
# handle their interfaces differently, we want the correct IP address found and used.
# eth0 will be given precedence over broadcast(wifi).

