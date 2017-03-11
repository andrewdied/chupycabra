Chupycabra  0.1 README A. R. Diederich <andrewdied@gmail.com>

Introduction
############
Chupycabra is a Python module for the XMPP instant messaging protocol.
The library is forked from the jabberpy project, 
http://jabberpy.sourceforge.net/, and https://github.com/andrewdied/jabberpy-archive,
written by Matthew Allum <breakfast@10.am>.  

While the goal is XMPP compliance, some old jabber elements will remain, such
as the ability to use xdb stanzas. Let's not get all doctrinaire here.
The eventual aim is to produce a fully featured easy to use library for
creating both jabber clients and servers, especially for use in testing
and compliance sweets. 

Development is made on 2.7, with no attempt to make it modern 3.x code. This
is solely to make the transition to 3.x easier. After that is complete, the
2.7 branch will be abandoned, and the porting to the latest 3.x branch will
start up. As much as anything, this is an attempt to practice porting code and
trying out python features. Others are more than welcome to participate! No
attempt will be made to run on windows until the 3.x port is complete.

For more infomation see https://github.com/andrewdied/chupycabra.

Installation
------------


If you want to develop the library, create a virtualenv environment
and use pip to install a development setup for it.

    pip virtualenv ~/chupy/venv
    cd ~/chupy
    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install pytest

    git clone https://github.com/andrewdied/chupycabra.git
    (In your git clone chupycabra directory)
    pip install -e .

The virtualenv environment is relatively slim right now. It may even stay that way.
(chupyenv) ~/chupycabra/tests> pip list
chupycabra (0.1, ~/chupycabra)
dnspython (1.14.0)
pip (8.1.2)
py (1.4.31)
pytest (3.0.1)
setuptools (26.0.0)
wheel (0.29.0)

The examples directory contains some simple jabber based programs which 
use the library. See examples/README

Documentaion
------------
The modules contain embedded docmentation, use pydoc to present this is 
a nice readable format. 

Also see the protocol documentation on jabber.org and the source code for
the scripts in examples/* . 

Notes
-----
* Name.  I like Red Vs Blue (http://redvsblue.com) and I've lived in a CHU
(containerised housing unit).