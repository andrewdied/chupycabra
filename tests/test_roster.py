"""Roster items can have a JID, groups, ask, name, and subscription.

>>> roster = chupycabra.Roster()
>>> dir(roster)
['__doc__', '__init__', '__module__', '_data', '_listener', '_lut', '_remove', '_set', '_setOnline', '_setShow', '_setStatus', 'getAsk', 'getGroups', 'getJIDs', 'getName', 'getOnline', 'getRaw', 'getShow', 'getStatus', 'getSub', 'getSummary', 'isOnline', 'setListener']
>>> roster._set(jid='romeo@example.com', name='Romeo', groups='friends', sub='both', ask=None)
>>> roster
<chupycabra.Roster instance at 0x7f239dceac20>
>>> roster.getSummary()
{u'romeo@example.com': 'offline'}
>>> roster.getAsk('romeo@example.com')
>>> roster.getGroups('romeo@example.com')
'friends'
>>> roster.getRaw()
{u'romeo@example.com': {'status': None, 'name': 'Romeo', 'show': None, 'groups': 'friends', 'online': 'offline', 'ask': None, 'sub': 'both'}}
>>> roster.isOnline('romeo@example.com')
False
>>> roster.getJIDs()
[romeo@example.com]
>>> roster._set(jid='juliet@example.org', name='Juliet', groups='friends', sub='both', ask=None)
>>> roster.getJIDs()
[romeo@example.com, juliet@example.org]
>>> roster._set(jid='romeo@example.com', name='Romeo', groups='enemies', sub='both', ask=None)
>>> roster.getJIDs()
[romeo@example.com, juliet@example.org]
>>> roster.getRaw()
{u'romeo@example.com': {'status': None, 'name': 'Romeo', 'show': None, 'groups': 'enemies', 'online': 'offline', 'ask': None, 'sub': 'both'}, u'juliet@example.org': {'status': None, 'name': 'Juliet', 'show': None, 'groups': 'friends', 'online': 'offline', 'ask': None, 'sub': 'both'}}
"""
import chupycabra.chupycabra

roster = chupycabra.Roster()

def test_add_roster():
    roster._set(jid='romeo@example.com', name='Romeo', groups=u'friends', sub='both', ask=None)
    assert roster.getRaw() == {u'romeo@example.com': {'status': None, 'name': 'Romeo', 'show': None,
                                                      'groups': 'friends', 'online': 'offline',
                                                      'ask': None, 'sub': 'both'}}

def test_add_second_jid():
    roster._set(jid='juliet@example.org', name='Juliet', groups='friends', sub='both', ask=None)
    assert roster.getRaw() == {u'romeo@example.com': {'status': None, 'name': 'Romeo',
                                                      'show': None, 'groups': 'friends', 'online': 'offline',
                                                      'ask': None, 'sub': 'both'},
                               u'juliet@example.org': {'status': None, 'name': 'Juliet', 'show': None,
                                                       'groups': 'friends', 'online': 'offline', 'ask': None,
                                                       'sub': 'both'}}


def test_get_jid_list():
    """Returns a list of JIDs of type JID from the roster"""
    assert roster.getJIDs() == [chupycabra.JID(jid='romeo@example.com'),
                                               chupycabra.JID(jid='juliet@example.org')]


def test_getSummary_jid():
    """Returns a list of JIDs and their status"""
    assert roster.getSummary() == {u'romeo@example.com': 'offline', u'juliet@example.org': 'offline'}


def test_jid_info():
    """Replaces the various getShow... methods in JID"""
    assert roster.jid_info('romeo@example.com', 'status') == None
    assert roster.jid_info('romeo@example.com', 'show') == None
    assert roster.jid_info('romeo@example.com', 'online') == 'offline'
    assert roster.jid_info('romeo@example.com', 'sub') == 'both'
    assert roster.jid_info('romeo@example.com', 'name') == 'Romeo'
    assert roster.jid_info('romeo@example.com', 'groups') == 'friends'
    assert roster.jid_info('romeo@example.com', 'ask') == None