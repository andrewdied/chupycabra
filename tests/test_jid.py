from chupycabra.chupycabra import JID

full_jid = u'romeo@example.net/resource1'
full_jid_obj = JID(jid=full_jid)
bare_jid = 'juliet@example.com'
domain_jid = 'im.example.com'


def test_full_jid_creation():
    full_jid_created = JID(jid='romeo@example.net/resource1')
    assert full_jid_created == full_jid


def test_full_jid_creation_parts():
    full_jid_created_parts = JID(node='romeo', domain='example.net', resource='resource1')
    assert full_jid_created_parts == full_jid


def test_bare_jid_creation():
    bare_jid_created = JID(jid=bare_jid)
    assert bare_jid_created == bare_jid


def test_bare_jid_creation_parts():
    bare_jid_created_parts = JID(node='juliet', domain='example.com')
    assert bare_jid_created_parts == bare_jid


def test_domain_jid_creation():
    domain_jid_created = JID(jid=domain_jid)
    assert domain_jid_created == domain_jid


def test_domain_jid_creation_parts():
    domain_jid_created_parts = JID(domain='im.example.com')
    assert domain_jid_created_parts == domain_jid


def test_get_node():
    full_jid_obj_get_node = JID(jid=full_jid)
    assert full_jid_obj_get_node.getNode() == 'romeo'


def test_set_node():
    full_jid_obj_set_node = JID(jid=full_jid)
    full_jid_obj_set_node.setNode('Montague')
    assert full_jid_obj_set_node.getNode() == 'Montague'


def test_get_domain():
    full_jid_obj_get_domain = JID(jid=full_jid)
    assert full_jid_obj_get_domain.getDomain() == 'example.net'


def test_set_domain():
    full_jid_obj_set_domain = JID(jid=full_jid)
    full_jid_obj_set_domain.setDomain('example.org')
    assert full_jid_obj_set_domain.getDomain() == 'example.org'


def test_get_resoure():
    full_jid_obj_get_resource = JID(jid=full_jid)
    assert full_jid_obj_get_resource.getResource() == 'resource1'


def test_set_resource():
    full_jid_obj_set_resource = JID(jid=full_jid)
    assert full_jid_obj_set_resource.getResource() == 'resource1'
    full_jid_obj_set_resource.setResource('resource2')
    assert full_jid_obj_set_resource.getResource() == 'resource2'


def test_get_stripped():
    full_jid_obj_stripped = JID(jid=full_jid)
    assert full_jid_obj_stripped.getStripped() == 'romeo@example.net'
    bare_jid_obj_stripped = JID(jid=bare_jid)
    assert bare_jid_obj_stripped.getStripped() == 'juliet@example.com'


def test_bare():
    full_jid_obj_bare = JID(jid=full_jid)
    assert full_jid_obj_bare.bare() == 'romeo@example.net'
    bare_jid_obj_bare = JID(jid=bare_jid)
    assert bare_jid_obj_bare.bare() == 'juliet@example.com'
    domain_jid_obj_bare = JID(jid=domain_jid)
    assert domain_jid_obj_bare.bare() == 'im.example.com'