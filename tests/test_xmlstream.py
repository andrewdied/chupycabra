import chupycabra.xmlstream
import pytest

plain_node = chupycabra.xmlstream.Node()


def test_node_getName():
    assert plain_node.getName() == 'tag'
    assert plain_node.name == 'tag'


def test_node_getNamespace():
    assert plain_node.getNamespace() == ''
    assert plain_node.namespace == ''


def test_node_setName():
    plain_node.setName('changedTag')
    assert plain_node.getName() == 'changedTag'
    plain_node.name = 'againChangedTag'
    assert plain_node.name == 'againChangedTag'



def test_node_set_parent():
    child_node = chupycabra.xmlstream.Node()
    child_node.name = 'child_node'
    parent_node = chupycabra.xmlstream.Node()
    parent_node.name = 'parent_node'
    child_node.parent = parent_node
    assert child_node.parent.name == 'parent_node'
