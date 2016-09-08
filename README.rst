Chupycabra  0.1 README A. R. Diederich <andrewdied@gmail.com>

Introduction
############
Chupycabra is a Python module for the XMPP instant messaging protocol.
The library is forked from the jabberpy project, 
http://jabberpy.sourceforge.net/, and https://github.com/andrewdied/jabberpy-archive,
written by Matthew Allum <breakfast@10.am>.  

While the goal is XMPP compliance, some old jabber elements will remain.
The eventual aim is to produce a fully featured easy to use library for
creating both jabber clients and servers, especially for use in testing
and compliance sweets. 

Development is made on 2.7, and after a while it will be ported to 3.x.
After it is reasonably complete on 2.7, the 2.7 branch will only get
bug fixes.  The intent is to quickly move to 3.5 once tests are added
for coverage, and the original code is cleaned up.

It is developed on Linux but may run on other Unix's and win32.

For more infomation see https://github.com/andrewdied/chupycabra.

Installation
------------
From the untared distrubution directory, as root run:

    python setup.py install

If you want to develop the library, create a virtualenv environment
and use pip to install a development setup for it.

    pip virtualenv ~/chupy/venv
    cd ~/chupy
    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install pytest

(In your git clone chupycabra directory)

    pip install -e .

The examples directory contains some simple jabber based programs which 
use the library. See examples/README

Documentaion
-------------
The modules contain embedded docmentation, use pydoc to present this is 
a nice readable format. 

Also see the protocol documentation on jabber.org and the source code for
the scripts in examples/* . 


Notes
-----
* The library should run fine on windows. Unfortunatly the test 
   client will not as it 'selects' on a file handle and 
   windows does not support this. If anyone knows a workaround
   for this please then inform me.

* Name.  I like Red Vs Blue (http://redvsblue.com) and I've lived in a CHU
(containerised housing unit).
