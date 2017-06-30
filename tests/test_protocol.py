import chupycabra
import pytest
import uuid


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


def test_protocol_setFrom_string():
    protocol = chupycabra.Protocol('protocol')
    full_jid_string = 'user@example.com/resourcepart'
    protocol.setFrom(full_jid_string)
    assert full_jid_string == protocol.getFrom()

def test_protocol_setFrom_JID():
    protocol = chupycabra.Protocol('protocol')
    full_jid_JID = chupycabra.JID('user@example.com/resourcepart')
    protocol.setFrom(full_jid_JID)
    assert full_jid_JID == protocol.getFrom()

def test_protocol_setID():
    """IDs need to be unique o nthe server and in the stream, but these tests
    do not check for that. Heck, the code doesn't now, either.
    """
    protocol = chupycabra.Protocol('protocol')
    id = uuid.uuid4()
    protocol.setID(id)
    assert protocol.getID() == id

def test_setTo_string():
    protocol = chupycabra.Protocol('protocol')
    full_jid_string = 'user@example.com/resourcepart'
    protocol.setTo(full_jid_string)
    assert full_jid_string == protocol.getTo()

def test_protocol_setTo_JID():
    protocol = chupycabra.Protocol('protocol')
    full_jid_JID = chupycabra.JID('user@example.com/resourcepart')
    protocol.setTo(full_jid_JID)
    assert full_jid_JID == protocol.getTo()

def test_protocol_setType():
    protocol = chupycabra.Protocol('protocol')
    protocol.setType('error')
    assert protocol.getType() == 'error'

def test_protocol_swap_from_to():
    protocol = chupycabra.Protocol('protocol')
    protocol.setFrom('original_from@example.com')
    protocol.setTo('original_to@example.org')
    to, from_ = protocol.getTo(), protocol.getFrom()
    protocol.setFrom(to)
    protocol.setTo(from_)
    assert (protocol.getFrom(), protocol.getTo()) == (to, from_)

def test_protocol_swap_from_to2():
    protocol = chupycabra.Protocol('protocol')
    original_from = 'original_from@example.com'
    original_to = 'original_to@example.org'
    protocol.setFrom(original_from)
    protocol.setTo(original_to)
    protocol.swap_from_to()
    assert (protocol.getFrom(), protocol.getTo()) == (original_to, original_from)
