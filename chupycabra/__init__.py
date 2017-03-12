#!/usr/bin/python2
from chupycabra import *

import logging
NullHandler = logging.NullHandler
logging.getLogger(__name__).addHandler(NullHandler())
del NullHandler
