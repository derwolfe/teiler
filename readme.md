Teiler
========================

Implementation
--------------
There are several pieces of this application
1. a file server
2. a pinging device to discover the server
3. some sort of client


Design
------
It should be simple -- the server starts, broadcasts it's address. The client picks up the address and grabs the files.

Testing levels
--------------
1. fileserver serves files
2. server seends out messages
3. client hears messages
4. client parses messages
5. client makes connection
6. client downloads file
7. Then gui
8. Then authenticate

Progress
--------
Todo:
1) tests for protocol, locate
2) early install using setup (not the package with GUI and frozen)
3) freeze for exe

