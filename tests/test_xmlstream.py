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
body_text = 'My ears have not yet drunk a hundred words'
thread_text = 'e0ffe42b28561960c6b12b944a092794b9683a38'
message_attrs = {'from': 'juliet@example.com', 'to': 'romeo@example.net', 'type':'chat', 'xml:lang': 'en'}
presence_example = '''<presence
           from='romeo@example.net/orchard'
           to='nurse@example.com'
           xml:lang='en'>
         <show>dnd</show>
         <status>courting Juliet</status>
         <priority>0</priority>
       </presence>
       '''
presence_attrs = {'from': 'romeo@example.net/orchard', 'to': 'nurse@example.com', 'xml:lang': 'en'}
presence_example_no_int = '''<presence
           to='nurse@example.com'>
         <show>dnd</show>
         <status>courting Juliet</status>
       </presence>
       '''

pretty_xml_example = '''

import xml.dom.minidom

xml = xml.dom.minidom.parse(xml_fname) # or xml.dom.minidom.parseString(xml_string)
pretty_xml_as_string = xml.toprettyxml()

Or:
import lxml.etree as etree

x = etree.parse("filename")
print etree.tostring(x, pretty_print = True)

'''

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


def test_xmlstream_node_create_data():
    node = chupycabra.xmlstream.Node(tag='body')
    node.putData(body_text)
    assert node.getData() == body_text

def test_xmlstream_node_create_2x_data():
    node = chupycabra.xmlstream.Node(tag='body')
    node.putData(body_text)
    node.putData(body_text)
    assert node.getData() == body_text + body_text


def test_xmlstream_node_insert_tag():
    """It seems a little chintzy to just do isinstance for this test"""
    node = chupycabra.xmlstream.Node(tag='message', attrs=message_attrs)
    node.insertTag('body')
    thread_node = node.insertTag(name='thread')
    hide_text = '''
    #assert node.__str__() == "<message from='{}' to='{}' type='{}' xml:lang='{}'<body /><thread /></message>".format(message_attrs['from'],
     #                           message_attrs['to'], message_attrs['type'], message_attrs['xml:lang'])
    et_node = ET.fromstring("<message from='{}' to='{}' type='{}' xml:lang='{}'><body /><thread /></message>".format(message_attrs['from'], message_attrs['to'], message_attrs['type'], message_attrs['xml:lang']))
    generated_text = "<message from='juliet@example.com' to='romeo@example.net' type='chat' xml:lang='en'><body /><thread /></message>"
"<message from='juliet@example.com' to='romeo@example.net' type='chat' xml:lang='en'<body /><thread /></message>"
    '''
    assert isinstance(thread_node, chupycabra.xmlstream.Node)


def test_xmlstream_node_insert():
    node = chupycabra.xmlstream.Node(tag='message', attrs=message_attrs)
    body_node = chupycabra.xmlstream.Node(tag='body')
    body_node.putData(body_text)
    node_plus_body = node.insertNode(body_node)
    assert node_plus_body == body_node


def test_xmlstream_insert_xml():
    node = chupycabra.xmlstream.Node(tag='message', attrs=message_attrs)
    jid_node = chupycabra.xmlstream.Node(tag='item')
    jid_node.putAttr('jid', 'juliet@example.com')
    jid_string = u"<item jid='juliet@example.com' />"
    node_inserted = node.insertXML(jid_string)
    assert jid_node.__str__() == node_inserted.__str__()


@pytest.mark.xfail(reason='_xmlnode2str chokes on integers')
def test_xmlstream_x2str_full():
    full_node = chupycabra.xmlstream.Node(tag='presence', attrs=presence_attrs)
    show_node = chupycabra.xmlstream.Node(tag='show')
    show_node.putData('dnd')
    full_node.insertNode(show_node)
    priority_node = chupycabra.xmlstream.Node(tag='priority')
    priority_node.putData(0)
    full_node.insertNode(priority_node)
    full_node_text = full_node._xmlnode2str()
    full_node_text_et = ET.fromstring(full_node_text)
    presence_node_example_et = ET.fromstring(presence_example)
    assert full_node_text_et == presence_node_example_et


def test_xmlstream_x2str_no_int():
    full_node = chupycabra.xmlstream.Node(tag='presence', attrs={'to': 'nurse@example.com'})
    show_node = chupycabra.xmlstream.Node(tag='show')
    show_node.putData('dnd')
    full_node.insertNode(show_node)
    full_node_text = full_node._xmlnode2str()
    assert full_node_text == "<presence to='nurse@example.com'><show>dnd</show></presence>"

@pytest.mark.xfail(reason='_xmlnode2str chokes on integers')
def test_xmlstream_x2str_int():
    full_node = chupycabra.xmlstream.Node(tag='presence', attrs={'to': 'nurse@example.com'})
    show_node = chupycabra.xmlstream.Node(tag='show')
    show_node.putData('dnd')
    full_node.insertNode(show_node)
    priority_node = chupycabra.xmlstream.Node(tag='priority')
    priority_node.putData(0)
    full_node.insertNode(priority_node)
    full_node_text = full_node._xmlnode2str()
    assert full_node_text == "<presence to='nurse@example.com'><show>dnd</show><priority>0</priority></presence>"