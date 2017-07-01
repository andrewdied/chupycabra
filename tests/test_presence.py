import chupycabra
import pytest

"""        RFC 6121, section 3, describes managing presence subscriptions, and
        section 4 describes exchanging presence information.
        """

show_values = ['away', 'chat', 'dnd', 'xa']

def test_create_presence():
    presence = chupycabra.Presence()
    assert presence.__str__() == '<presence />'


def test_presence_create_status():
    presence = chupycabra.Presence(status='away')
    assert presence.getStatus() == 'away'


@pytest.mark.parametrize('show_item', show_values)
def test_presence_create_show(show_item):
    presence = chupycabra.Presence(show=show_item)
    assert presence.getShow() == show_item

@pytest.mark.xfail()
def test_presence_create_priority():
    '''There's something deeply wrong in the code. This will need to be fixed.
    >>> spam = chupycabra.Presence(priority=1)
>>> spam
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "chupycabra.py", line 797, in __repr__
    return self.__str__()
  File "xmlstream.py", line 165, in __str__
    return self._xmlnode2str()
  File "xmlstream.py", line 183, in _xmlnode2str
    s = s + a._xmlnode2str(parent=self)
  File "xmlstream.py", line 186, in _xmlnode2str
    s = s + escape(self.data[cnt])
  File "/usr/lib64/python2.7/xml/sax/saxutils.py", line 32, in escape
    data = data.replace("&", "&amp;")
AttributeError: 'int' object has no attribute 'replace'
>>> spam = chupycabra.Presence(priority='one')
>>> spam
<presence><priority>one</priority></presence>
'''
    presence = chupycabra.Presence(priority=123)
    assert presence.getPriority() == 123


#TODO: Add groupchat tests