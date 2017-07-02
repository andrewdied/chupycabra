"""Testing the IQ stanzas.
       IQ stanzas are described at http://xmpp.org/rfcs/rfc6120.html#stanzas-semantics-iq
       type attribute must be one of get, set, result, or error.
       id attribute is mandatory.

       The exciting parts are in the <query> sub element.
       Example:
           <iq from="alice@wonderland.lit/pda"
                id="ld823itz"
                to="alice@wonderland.lit"
                type="get">
              <query xmlns="jabber:iq:roster"/>
           </iq>

        iq = Iq(from="alice@wonderland.lit/pda", to="alice@wonderland.lit",
                type="get", query="jabber:iq:roster")
        FIXME: that is likely wrong.

        IQ is covered in section 6, Exchanging IQ Stanzas, in RFC 6121.

"""


import chupycabra
from chupycabra import NS_AGENT, NS_AGENTS, NS_AUTH, NS_OOB, NS_REGISTER, NS_XROSTER, \
    NS_TIME, NS_VERSION, NS_PASS, NS_BROWSE, NS_LAST, NS_PRIVACY, NS_ROSTER
import pytest

iq_namespaces = [NS_AGENT, NS_AGENTS, NS_AUTH, NS_OOB, NS_REGISTER, NS_XROSTER,
                 NS_TIME, NS_VERSION, NS_PASS, NS_BROWSE, NS_LAST, NS_PRIVACY]

query_payload = """<query xmlns='jabber:iq:roster'>
           <item jid='juliet@example.com'
                 name='Juliet'
                 subscription='both'>
             <group>Friends</group>
           </item>
           <item jid='benvolio@example.org'
                 name='Benvolio'
                 subscription='to'/>
           <item jid='mercutio@example.org'
                 name='Mercutio'
                 subscription='from'/>
         </query>
         """

def test_create_iq():
    iq = chupycabra.Iq()
    assert iq.__str__() == '<iq />'

@pytest.mark.parametrize('iq_namespace', iq_namespaces)
def test_iq_create_query_namepace(iq_namespace):
    """This just returns the namespace text."""
    iq = chupycabra.Iq(type='get', query=iq_namespace)
    assert iq.getQuery() == iq_namespace


def test_iq_create_queryPayload():
    """I think setQueryPayload is broken. It's always making a new query element, not modifying it.
    The example client doesn't modify it, so I think it's always been broken.
    >>> otherquery = chupycabra.Iq(type='result')
>>> otherquery
<iq type='result' />
>>> otherquery.setQueryPayload(query_payload)
>>> otherquery
<iq type='result'><query><query xmlns = 'jabber:iq:roster' >
           <item jid='juliet@example.com' name='Juliet' subscription='both'>
             <group>Friends</group>
           </item>
           <item jid='benvolio@example.org' name='Benvolio' subscription='to' />
           <item jid='mercutio@example.org' name='Mercutio' subscription='from' />
         </query></query></iq>
"""
    iq = chupycabra.Iq(type='result')
    iq.setQuery(NS_ROSTER)
    iq.setQueryPayload(query_payload)


def test_iq_create_queryNode():
    pass


def test_iq_create_roster_result():
    """I'd think this would work, but there are some bugs to fix. I need to
    look more in the xmlstream code.

    >>> q = chupycabra.Iq(to='romeo@example.net/orchard', type='result')
>>> q.setQuery(chupycabra.NS_ROSTER)
<xmlstream.Node instance at 0x7f99e0268368>
>>> q.setQueryPayload(query_payload)
>>> q
<iq to='romeo@example.net/orchard' type='result'><query xmlns = 'jabber:iq:roster' ><query>
           <item jid='juliet@example.com' name='Juliet' subscription='both'>
             <group>Friends</group>
           </item>
           <item jid='benvolio@example.org' name='Benvolio' subscription='to' />
           <item jid='mercutio@example.org' name='Mercutio' subscription='from' />
         </query></query></iq>
"""
    pass
