Teiler (sharer)
===============

|Build Status| |Coverage|

I am extremely tired of needing a USB stick to transfer files between
computers. While netcat, scp, dropbox, and other tools solve this problem,
I'd like the solution to be a bit simpler.

Often, a person wants to transfer files to another person on the same network.
This network doesn't have any special configuration. Each user is able to see
the other on the network.

The goal of this software is to make the above situation simple. Both users
download the program, open the application, and can transfer files to one
another without needing to be connected to the internet.

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

    ``make install-dev``

If you'd like to contribute, just fork the repository and submit a pull
request.

You can run tests by using:

    ``make test``

If you'd like to see coverage information:

    ``make cover``

Lastly, lint can be run using:

    ``make lint``

For a final check, tox can be used. As long as you have it available in your
path, you can run the tests and linters using:

    ``tox``

Thanks!

.. |Build Status| image:: https://travis-ci.org/derwolfe/teiler.png?branch=dev
   :target: https://travis-ci.org/derwolfe/teiler

.. |Coverage| image:: https://coveralls.io/repos/derwolfe/teiler/badge.png?branch=master
  :target: https://coveralls.io/r/derwolfe/teiler?branch=master
