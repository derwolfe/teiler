
Teiler (sharer)
===============

|Build Status| |Coverage|

I am extremely tired of needing a USB stick to transfer files between
computers. Most of the time, I am on simple networks. A person has setup
a router in its simplest configuration. I and my friend have simple wifi
access to the network. We want to transfer files to one another, but
sadly have no thumb drive or disc.

The goal of this software is to make the above situation simple. We each
download the program and need only the basic knowledge needed to use a
web browser.

How will I use this?
--------------------

TBD - right now, I'm planning on having a simple browser interface.

You would download the program, execute it, and be presented with an
interface displaying other users on the network. To transfer a file, you
would drag the file on to the other user. If the other user wants to
receive the file (which of course they will) they will confirm the
transfer, allowing it to proceed.

How do I work on the project?
-----------------------------

1. Download the source

    ``git clone https://github.com/derwolfe/teiler.git``

2. Make a virtualenv for the application with:

    ``vitualenv venv``

3.  Install the dependencies with
   
    ``source ./venv/bin/activate``

    ``pip install -r requirements-dev.txt``

If you'd like to contribute, just fork the repository and submit a pull
request.

Thanks!

.. |Build Status| image:: https://travis-ci.org/derwolfe/teiler.png?branch=dev
   :target: https://travis-ci.org/derwolfe/teiler
.. |Coverage| image::https://coveralls.io/repos/derwolfe/teiler/badge.png?branch=master
  :target: https://coveralls.io/r/derwolfe/teiler?branch=master
