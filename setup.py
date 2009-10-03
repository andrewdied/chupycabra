#!/usr/bin/env python
import sys

try:
    from distutils.core import setup
except:
    if sys.version[0] < 2:
        print "chupycabra requires at least python 2.0"
        print "Setup cannot continue."
        sys.exit(1)
    print "You appear not to have the Python distutils modules"
    print "installed. Setup cannot continue."
    print "You can manually install jabberpy by coping the jabber"
    print "directory to your /python-libdir/site-packages"    
    print "directory."
    sys.exit(1)
    
setup(name="chupycabra",
      version="0.1",
      #py_modules=["xmlstream","jabber"],
      packages=["chupycabra"],
      description="Python XMPP library",
      author="A. R. Diederich",
      author_email="andrewdied@gmail.com",
      url="https://launchpad.net/chupycabra",
      license="LGPL"
      )
