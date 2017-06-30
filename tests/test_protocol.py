import chupycabra
import pytest


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


def test_create_protocol_xdb():
    xdb_protocol = chupycabra.Protocol('xdb', to=None, type=None, attrs=None,
                                                  frm=None, payload=[], node=None)
    assert xdb_protocol.__str__() == '<xdb />'

def test_create_protocol_iq_get():
    iq_get_protocol = chupycabra.Iq(type='get')
    assert iq_get_protocol.__str__() == "<iq type='get' />"

protocols = ['iq', 'message', 'presence', 'xdb', 'log']

@pytest.mark.parametrize('protocol', protocols)
def test_create_protocols_bare(protocol):
    protocol_bare = chupycabra.Protocol(name=protocol)
    assert protocol_bare.__str__() == "<%s />" % protocol