Teiler
======
Basically, make it simple to share files amongst different computers behind the same router.

It is meant to solve the problem of having a friend come over to your house who wants to share a large
set of files with you. He uses Windows, you use linux. Neither of you has any idea how to start up a 
file server or use SSH. 

How to use
----------
Currently, the application is pretty raw. 

To use it
1. Download the source
2. Make a virtualenv for the application
   ** this will be replaced with a distutils install **
3. Activate the new virtualenv and pip install requirements -r teilerpr/requirements.txt
4. Once the above steps are done, to act as a server, use:
   
   python teilerpy/src/app.py serve 
   
   or to run in client mode:

   python teilerpy/src/app.py listen
   


Implementation
--------------
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

