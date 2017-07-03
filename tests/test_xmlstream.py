import chupycabra.xmlstream
import pytest
import xml.etree.ElementTree as ET

plain_node = chupycabra.xmlstream.Node()
jid_item = """<item jid='juliet@example.com' name='Juliet' subscription='both'> <group>Friends</group> </item>"""
iq_stanza = """<iq id='hf61v3n7'
           to='romeo@example.net/orchard'
           type='result'>
         <query xmlns='jabber:iq:roster'>
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
       </iq>
       """


def test_node_get_name():
    assert plain_node.name == 'tag'


def test_node_get_namespace():
    assert plain_node.getNamespace() == ''
    assert plain_node.namespace == ''


def test_node_set_name():
    plain_node.name = 'againChangedTag'
    assert plain_node.name == 'againChangedTag'


def test_node_set_parent():
    child_node = chupycabra.xmlstream.Node()
    child_node.name = 'child_node'
    parent_node = chupycabra.xmlstream.Node()
    parent_node.name = 'parent_node'
    child_node.parent = parent_node
    assert child_node.parent.name == 'parent_node'


def test_xmlstream_change_node_name():
    """setName and getName are depricated. Change this once they're
    pulled from the examples.
    """
    simple_node = chupycabra.xmlstream.Node()
    simple_node.setName('new_tag')
    assert simple_node.getName() == 'new_tag'


def test_xmlstream_putAttr():
    jid_node = chupycabra.xmlstream.Node(tag='item')
    jid_node.putAttr('jid', 'juliet@example.com')
    jid_node.putAttr('name', 'Juliet')
    jid_node.putAttr('group', 'Friends')
    assert (jid_node.getAttr('jid'), jid_node.getAttr('name'), jid_node.getAttr('group')) == (
        'juliet@example.com', 'Juliet', 'Friends')


def test_etree_node():
    jid_node = chupycabra.xmlstream.Node(tag='item')
    jid_node.putAttr('jid', 'juliet@example.com')
    jid_node.putAttr('name', 'Juliet')
    jid_node.putAttr('group', 'Friends')
    et_jid_node = ET.fromstring("<item jid='juliet@example.com' name='Juliet' group='Friends' />")
    assert ET.fromstring(jid_node.__str__()).attrib == et_jid_node.attrib