Teiler
======
[![Build
Status](https://travis-ci.org/derwolfe/teiler.png?branch=dev)](https://travis-ci.org/derwolfe/teiler)

** this is not usable software at the moment **

Basically, make it simple to share files amongst different computers behind the same router.

It is meant to solve the problem of having a friend come over to your house who wants to share a large
set of files with you. He uses Windows, you use linux. Neither of you has any idea how to start up a file server or use SSH. 

How to install
--------------
1. Download the source

    `git clone https://github.com/derwolfe/teiler.git`

2. Make a virtualenv for the application ** this will be replaced with a distutils install **

    `mkvirtualenv teiler`

3. Install the dependencies with  

    `workon teiler && pip install  -r teilerpy/requirements.txt`



How to use
---------
The application is setup to launch an inteface from which the user can send and receive files. The user will be shown a list of other users. To share a file or directory with another user, you need only drag and drop a file from your favorite file manager or desktop. 

Once dropped, the other user will be presented with message checking whether or not she wants the file.

To run teiler, CD into the directory `teiler` then

`python src/teiler.py` 
