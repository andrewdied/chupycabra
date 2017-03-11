import chupycabra.chupycabra
import chupycabra.xmlstream

# iq is pretty staightforward
thing = '''class Iq(Protocol):
    """Class for creating and managing jabber <iq> protocol
       elements"""

    def __init__(self, to=None, type=None, query=None, attrs=None,
                 frm=None, payload=[], node=None):
        Protocol.__init__(self, 'iq', to=to, type=type, attrs=attrs,
                          frm=frm, payload=payload, node=node)
        if query:
            self.setQuery(query)
'''

iq_example = """
>>> auth_get_iq = chupycabra.Iq(type='get')
>>> auth_get_iq
<iq type='get' />
>>> auth_get_iq.setID('auth-get')
>>> auth_get_iq
<iq type='get' id='auth-get' />
>>> query = auth_get_iq.setQuery(chupycabra.NS_AUTH)
>>> chupycabra.NS_AUTH
'jabber:iq:auth'
>>> query
<xmlstream.Node instance at 0x7f239dcea680>
>>> print(query)
<query />
>>> auth_get_iq
<iq type='get' id='auth-get'><query xmlns = 'jabber:iq:auth'  /></iq>
>>> query.insertTag('username').insertData('romeo')
>>> print(query)
<query><username>romeo</username></query>
>>> auth_get_iq
<iq type='get' id='auth-get'><query xmlns = 'jabber:iq:auth' ><username>romeo</username></query></iq>
"""

def test_create_protocol():
    ard_protocol = chupycabra.chupycabra.Protocol('ard', to=None, type=None, attrs=None,
                            frm=None, payload=[], node=None)