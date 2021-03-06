"""
>>> import chupycabra
>>> import sys
>>> Username = "ardiederich"
>>> Password = "throttle"
>>> Resource = "chupycabra"
>>> Server = "chupycabra.com"
>>> con = chupycabra.Client(host=Server, debug=chupycabra.DBG_ALWAYS, log=sys.stderr)
***
*** Invalid or oldformat debug param given: always
*** please correct your param, should be of [] type!
*** Due to this, full debuging is enabled
DEBUG: client connect called to chupycabra.com 5222 type 1
DEBUG: Jabber server connected
DEBUG: stream: sending initial header
Sat Sep 26 22:24:52 2009 - SENT: - <?xml version='1.0' encoding='UTF-8' ?>               <stream:stream to='chupycabra.com' xmlns='jabber:client' xmlns:stream='http://etherx.chupycabra.org/streams'>
DEBUG: sent <?xml version='1.0' encoding='UTF-8' ?>               <stream:stream to='chupycabra.com' xmlns='jabber:client' xmlns:stream='http://etherx.chupycabra.org/streams'>

>>> con.connect()
>>> con.disconnect()
"""

"""
>>> con.requestRoster()
>>> con.process()
'0'
>>> con.process(1)
'0'
>>> con.disconnect()
Sat Sep 26 19:33:44 2009 - SENT: - <presence type='unavailable' />
DEBUG: sent <presence type='unavailable' />
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
