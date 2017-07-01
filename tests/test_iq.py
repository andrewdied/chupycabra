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
    NS_TIME, NS_VERSION, NS_PASS, NS_BROWSE, NS_LAST, NS_PRIVACY
import pytest

iq_namespaces = [NS_AGENT, NS_AGENTS, NS_AUTH, NS_OOB, NS_REGISTER, NS_XROSTER,
                 NS_TIME, NS_VERSION, NS_PASS, NS_BROWSE, NS_LAST, NS_PRIVACY]


def test_create_iq():
    iq = chupycabra.Iq()
    assert iq.__str__() == '<iq />'

@pytest.mark.parametrize('iq_namespace', iq_namespaces)
def test_iq_create_query(iq_namespace):
    iq = chupycabra.Iq(type='get', query=iq_namespace)
    assert iq.getQuery() == iq_namespace