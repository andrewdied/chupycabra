
"""
Test various aspects of the JID class against allowed JID constructions.

To run interactive:
import doctest
doctest.testfile("jid.py")
"""

# Bare domain JID
>>> import jabber
>>> domain_jid = jabber.JID(domain="example.com")
>>> domain_jid.node
''
>>> domain_jid.domain
'example.com'
>>> domain_jid.resource
''
>>> domain_jid
example.com

# Pass in a full JID
>>> fulljid = "login@example.com/chupycabra"
>>> jid_fulljid = jabber.JID(jid=fulljid)
>>> jid_fulljid
login@example.com/chupycabra
>>> jid_fulljid.node
'login'
>>> jid_fulljid.domain
'example.com'
>>> jid_fulljid.resource
'chupycabra'
>>> fulljid == jid_fulljid
True

# Should return node as string.  Since JID.node already does this, why
# bother?
>>> fulljid = "login@example.com/chupycabra"
>>> jid_fulljid = jabber.JID(jid=fulljid)
>>> jid_fulljid.getNode
<bound method JID.getNode of login@example.com/chupycabra>

# Test with bare jid
>>> barejid = "login@example.com"
>>> jid_barejid = jabber.JID(jid=barejid)
>>> jid_barejid
login@example.com
>>> barejid
'login@example.com'
>>> jid_barejid == barejid
True
>>> jid_barejid is barejid
False
>>> jid_barejid.node
'login'
>>> jid_barejid.domain
'example.com'
>>> jid_barejid.resource
''

if __name__ == "__main__":
    import doctest
    doctest.testmod()
