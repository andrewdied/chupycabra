#!/usr/bin/python
# coding=utf-8

"""
    Chupycabra: A jabber python library
    Copyright (C) 2009, 2016 A. R. Diederich
    Much is based on jabberpy, (C) 2001 Matthew Allum

    See the file LICENSE for copying permission.

__intro__

Chupycabra is a python module for the jabber instant messaging protocol.
The library is forked from the jabberpy project, written by Matthew Allum.

The eventual aim is to produce an easy to use library for
creating both jabber clients and servers, especially for use in testing
and compliance suites.

Initial re-development is on python 2.7, and after it is cleaned up it will
move to python 3.x.

It is developed on opensuse tumbleweed, and may run on other *nix platforms.

__usage__

Chupycabra subclasses the xmlstream classs and provides the
processing of jabber protocol elements into object instances as well as
helper functions for parts of the protocol such as authentication
and roster management.

An example of usage for a simple client is:

<> Read documentation on jabber.org for the jabber protocol.
<> Instantiate a jabber.Client object with your jabber server's host
<> Define callback functions for the protocol elements you want to use
   and optionally a disconnection.
<> Authenticate with the server via auth method, or register via the
   reg methods to get an account.
<> Call requestRoster() and sendPresence()
<> loop over process(). Send Iqs, messages and presences by birthing
   them via their respective clients, manipulating them and using
   the Client's send() method.
<> Respond to incoming elements passed to your callback functions.
"""

import hashlib
import time
import warnings

import xmlstream

debug = xmlstream.debug

__version__ = xmlstream.__version__

timeout = 300

DBG_INIT, DBG_ALWAYS = debug.DBG_INIT, debug.DBG_ALWAYS
DBG_DISPATCH = 'jb-dispatch'
DBG_NODE = 'jb-node'
DBG_NODE_IQ = 'jb-node-iq'
DBG_NODE_MESSAGE = 'jb-node-message'
DBG_NODE_PRESENCE = 'jb-node-pressence'
DBG_NODE_UNKNOWN = 'jb-node-unknown'
debug.debug_flags.append(DBG_DISPATCH)
debug.debug_flags.append(DBG_NODE)
debug.debug_flags.append(DBG_NODE_IQ)
debug.debug_flags.append(DBG_NODE_MESSAGE)
debug.debug_flags.append(DBG_NODE_PRESENCE)
debug.debug_flags.append(DBG_NODE_UNKNOWN)

# JANA core namespaces
#  from http://www.jabber.org/jana/namespaces.php as of 2003-01-12
#  "myname" means that namespace didn't have a name in the jabberd headers
NS_AGENT = "jabber:iq:agent"
NS_AGENTS = "jabber:iq:agents"
NS_AUTH = "jabber:iq:auth"
NS_CLIENT = "jabber:client"
NS_DELAY = "jabber:x:delay"
NS_OOB = "jabber:iq:oob"
NS_REGISTER = "jabber:iq:register"
NS_ROSTER = "jabber:iq:roster"
NS_XROSTER = "jabber:x:roster"  # myname
NS_SERVER = "jabber:server"
NS_TIME = "jabber:iq:time"
NS_VERSION = "jabber:iq:version"

NS_COMP_ACCEPT = "jabber:component:accept"  # myname
NS_COMP_CONNECT = "jabber:component:connect"  # myname

# JANA JEP namespaces, ordered by JEP
#  from http://www.jabber.org/jana/namespaces.php as of 2003-01-12
#  all names by jaclu
_NS_PROTOCOL = "http://jabber.org/protocol"  # base for other
NS_PASS = "jabber:iq:pass"  # JEP-0003
NS_XDATA = "jabber:x:data"  # JEP-0004
NS_RPC = "jabber:iq:rpc"  # JEP-0009
NS_BROWSE = "jabber:iq:browse"  # JEP-0011
NS_LAST = "jabber:iq:last"  # JEP-0012
NS_PRIVACY = "jabber:iq:privacy"  # JEP-0016
NS_XEVENT = "jabber:x:event"  # JEP-0022
NS_XEXPIRE = "jabber:x:expire"  # JEP-0023
NS_XENCRYPTED = "jabber:x:encrypted"  # JEP-0027
NS_XSIGNED = "jabber:x:signed"  # JEP-0027
NS_P_MUC = _NS_PROTOCOL + "/muc"  # JEP-0045
NS_P_MUC_ADMIN = NS_P_MUC + "#admin"  # JEP-0045
NS_P_MUC_OWNER = NS_P_MUC + "#owner"  # JEP-0045
NS_P_MUC_USER = NS_P_MUC + "#user"  # JEP-0045
NS_VCARD = "vcard-temp"  # JEP-0054

# Non JANA aproved, ordered by JEP
#  all names by jaclu
_NS_P_DISCO = _NS_PROTOCOL + "/disco"  # base for other
NS_P_DISC_INFO = _NS_P_DISCO + "#info"  # JEP-0030
NS_P_DISC_ITEMS = _NS_P_DISCO + "#items"  # JEP-0030
NS_P_COMMANDS = _NS_PROTOCOL + "/commands"  # JEP-0050

# 2002-01-11 jaclu
#
# Defined in jabberd/lib/lib.h, but not JANA aproved and not used in jabber.py
# so commented out, should/could propably be removed...

# NS_ADMIN      = "jabber:iq:admin"
# NS_AUTH_OK    = "jabber:iq:auth:0k"
# NS_CONFERENCE = "jabber:iq:conference"
# NS_ENVELOPE   = "jabber:x:envelope"
# NS_FILTER     = "jabber:iq:filter"
# NS_GATEWAY    = "jabber:iq:gateway"
# NS_OFFLINE    = "jabber:x:offline"
# NS_PRIVATE    = "jabber:iq:private"
# NS_SEARCH     = "jabber:iq:search"
# NS_XDBGINSERT = "jabber:xdb:ginsert"
# NS_XDBNSLIST  = "jabber:xdb:nslist"
# NS_XHTML      = "http://www.w3.org/1999/xhtml"
# NS_XOOB       = "jabber:x:oob"
# NS_COMP_EXECUTE = "jabber:component:execute" # myname

# Possible constants for Roster class .... hmmm ##
# TODO ARD: These constants may be unnecessary.  Look at later.
RS_SUB_BOTH = 0
RS_SUB_FROM = 1
RS_SUB_TO = 2

RS_ASK_SUBSCRIBE = 1
RS_ASK_UNSUBSCRIBE = 0

RS_EXT_ONLINE = 2
RS_EXT_OFFLINE = 1
RS_EXT_PENDING = 0


#############################################################################


def ustr(text):
    """return a unicode string"""
    if isinstance(text, unicode):
        return text
    elif isinstance(text, str):
        return text.decode(xmlstream.ENCODING)
    else:
        return str(text).decode(xmlstream.ENCODING, errors='replace')


xmlstream.ustr = ustr


class NodeProcessed(Exception):
    """Currently only for Connection._expectedIqHandler"""
    pass


class Connection(xmlstream.Client):
    """Forms the base for both Client and Component Classes"""

    def __init__(self, host, port, namespace,
                 debug=[], log=False, connection=xmlstream.TCP, hostIP=None,
                 proxy=None):

        xmlstream.Client.__init__(self, host, port, namespace,
                                  debug=debug, log=log,
                                  connection=connection,
                                  hostIP=hostIP, proxy=proxy)
        self.handlers = {}
        self.registerProtocol('unknown', Protocol)
        self.registerProtocol('iq', Iq)
        self.registerProtocol('message', Message)
        self.registerProtocol('presence', Presence)

        self.registerHandler('iq', self._expectedIqHandler, system=True)

        self._expected = {}

        self._id = 0 # used for a 1-up counter, see getAnID() below

        self.lastErr = ''
        self.lastErrCode = 0

    def header(self):
        self.DEBUG("stream: sending initial header", DBG_INIT)
        # header = u"<?xml version='1.0' encoding='UTF-8' ?>   \
        header = u"<?xml version='1.0'?>   \
            <stream:stream to='%s' xmlns='%s' xml:lang='en' version='1.0'" % (self._host, self._namespace)

        if self._outgoingID:
            header = header + " id='%s' " % self._outgoingID
        header = header + " xmlns:stream='http://etherx.jabber.org/streams'>"
        self.send(header)
        self.process(timeout)

    def send(self, what):
        """Sends a jabber protocol element (Node) to the server"""
        xmlstream.Client.write(self, ustr(what))

    def _expectedIqHandler(self, conn, iq_obj):
        if iq_obj.getAttr('id') and iq_obj.getAttr('id') in self._expected:
            self._expected[iq_obj.getAttr('id')] = iq_obj
            raise NodeProcessed('No need for further Iq processing.')

    def dispatch(self, stanza):
        """Called internally when a 'protocol element' is received.
           Builds the relevant jabber.py object and dispatches it
           to a relevant function or callback."""
        name = stanza.getName()
        if not name in self.handlers:
            self.DEBUG("whats a tag -> " + name, DBG_NODE_UNKNOWN)
            name = 'unknown'
        else:
            self.DEBUG("Got %s stanza" % name, DBG_NODE)

        stanza = self.handlers[name][type](node=stanza)

        typ = stanza.getType()
        if not typ:
            typ = ''
        try:
            ns = stanza.getQuery()
            if not ns:
                ns = ''
        except:
            ns = ''
        self.DEBUG("dispatch called for: name->%s ns->%s" % (name, ns),
                   DBG_DISPATCH)

        if typ and ns:
            typns = typ + ns
        else:
            typns = ''
        if not ns in self.handlers[name]:
            ns = ''
        if not typ in self.handlers[name]:
            typ = ''
        if not typns in self.handlers[name]:
            typns = ''

        chain = []
        for key in ['default', typ, ns, typns]:
            # we will use all handlers: from very common to very particular
            if key:
                chain += self.handlers[name][key]

        output = ''
        user = True
        for handler in chain:
            try:
                if user or handler['system']:
                    if handler['chain']:
                        output = handler['func'](self, stanza, output)
                    else:
                        handler['func'](self, stanza)
            except NodeProcessed:
                user = False

    def registerProtocol(self, tag_name, Proto):
        """Registers a protocol in protocol processing chain. You MUST register
           a protocol before you register any handler function for it.
           First parameter, that passed to this function is the tag name that
           belongs to all protocol elements. F.e.: message, presence, iq, 
           xdb, ...
           Second parameter is the [ancestor of] Protocol class, which 
           instance will
           built from the received node with call

                if received_packet.getName()==tag_name:
                    stanza = Proto(node = received_packet)
        """
        self.handlers[tag_name] = {type: Proto, 'default': []}


    def registerHandler(self, name, handler, type_='', ns='', chained=False,
                        makefirst=False, system=False):
        """Sets the callback func for processing incoming stanzas.
           Multiple callback functions can be set which are called in
           succession. Callback can optionally raise an NodeProcessed error to
           stop stanza from further processing. A type and namespace 
           attributes can
           also be optionally passed so the callback is only called when a 
           stanza of
           this type is received. Namespace attribute MUST be omitted if you
           registering an Iq processing handler.

           If 'chainOutput' is set to False (the default), the given function
           should be defined as follows:

                def myCallback(c, p)

           Where the first parameter is the Client object, and the second
           parameter is the [ancestor of] Protocol object representing the 
           stanza which was received.

           If 'chainOutput' is set to True, the output from the various
           handler functions will be chained together.  In this case,
           the given callback function should be defined like this:

                def myCallback(c, p, output)

           Where 'output' is the value returned by the previous
           callback function.  For the first callback routine, 'output' will be
           set to an empty string.

           'makefirst' argument gives you control over handler prioriy in its 
           type and namespace scope. Note that handlers for particular type or 
           namespace always have lower priority than common handlers.
        """
        if not type_ and not ns:
            type_ = 'default'
        #if not self.handlers[name].has_key(type_ + ns):
        if not type_ + ns in self.handlers[name]:
            self.handlers[name][type_ + ns] = []
        if makefirst:
            self.handlers[name][type_ + ns].insert({'chain': chained,
                                                    'func': handler, 'system': system})
        else:
            self.handlers[name][type_ + ns].append({'chain': chained,
                                                    'func': handler, 'system': system})


    def setDisconnectHandler(self, func):
        """Set the callback for a disconnect.
           The given function will be called with a single parameter (the
           connection object) when the connection is broken unexpectedly (eg,
           in response to sending badly formed XML).  self.lastErr and
           self.lastErrCode will be set to the error which caused the
           disconnection, if any.
        """
        self.disconnectHandler = func

    ## functions for sending element with ID's ##

    def waitForResponse(self, ID, timeout=timeout):
        """Blocks untils a protocol element with the given id is received.
           If an error is received, waitForResponse returns None and
           self.lastErr and self.lastErrCode is set to the received error.  If
           the operation times out (which only happens if a timeout value is
           given), waitForResponse will return None and self.lastErr will be
           set to "Timeout".
           Changed default from timeout=0 to timeout=300 to avoid hangs in
           scripts and such.
           If you _really_ want no timeout, just set it to 0"""
        ID = ustr(ID)
        self._expected[ID] = None
        has_timed_out = False

        abort_time = time.time() + timeout
        if timeout:
            self.DEBUG("waiting with timeout:%s for %s" % (timeout, ustr(ID)),
                       DBG_NODE_IQ)
        else:
            self.DEBUG("waiting for %s" % ustr(ID), DBG_NODE_IQ)

        while (not self._expected[ID]) and not has_timed_out:
            if not self.process(0.2):
                return None
            if timeout and (time.time() > abort_time):
                has_timed_out = True
        if has_timed_out:
            self.lastErr = "Timeout"
            return None
        response = self._expected[ID]
        del self._expected[ID]
        if response.getErrorCode():
            self.lastErr = response.getError()
            self.lastErrCode = response.getErrorCode()
            return None
        return response

    def SendAndWaitForResponse(self, obj, ID=None, timeout=timeout):
        """Sends a protocol element object and blocks until a response with
           the same ID is received.  The received protocol object is returned
           as the function result.

        """
        if ID is None:
            ID = obj.getID()
            if ID is None:
                ID = self.getAnID()
                obj.setID(ID)
        ID = ustr(ID)
        self.send(obj)
        return self.waitForResponse(ID, timeout)

    def getAnID(self):
        """Returns a unique ID to the connection. This is a one-up counter.

        :return: unicode text integer
        """
        self._id = self._id + 1
        return ustr(self._id)


#############################################################################

class Client(Connection):
    """Class for managing a client connection to a jabber server."""

    def __init__(self, host, port=5222, debug=[], log=False,
                 connection=xmlstream.TCP, hostIP=None, proxy=None):

        Connection.__init__(self, host, port, NS_CLIENT, debug, log,
                            connection=connection, hostIP=hostIP, proxy=proxy)

        self.registerHandler('iq', self._IqRosterManage, 'result',
                             NS_ROSTER, system=True)
        self.registerHandler('iq', self._IqRosterManage, 'set',
                             NS_ROSTER, system=True)
        self.registerHandler('iq', self._IqRegisterResult, 'result',
                             NS_REGISTER, system=True)
        self.registerHandler('iq', self._IqAgentsResult, 'result',
                             NS_AGENTS, system=True)
        self.registerHandler('presence', self._presenceHandler, system=True)

        self._roster = Roster()
        self._agents = {}
        self._reg_info = {}
        self._reg_agent = ''

    def disconnect(self):
        """Safely disconnects from the connected server"""
        self.send(Presence(type='unavailable'))
        xmlstream.Client.disconnect(self)

    def sendPresence(self, type=None, priority=None, show=None, status=None,
                     signedStatus=None):
        """Sends a presence protocol element to the server.
           Used to inform the server that you are online"""
        presence = Presence(type=type, priority=priority, show=show,
                            status=status)
        if signedStatus:
            presence.setX(NS_XSIGNED).insertData(signedStatus)
        self.send(presence)

    sendInitPresence = sendPresence

    def _presenceHandler(self, conn, pres_obj):
        who = ustr(pres_obj.getFrom())
        type_ = pres_obj.getType()
        self.DEBUG("presence type is %s" % type_, DBG_NODE_PRESENCE)
        if type_ == 'available' or not type_:
            self.DEBUG("roster setting %s to online" % who, DBG_NODE_PRESENCE)
            self._roster._setOnline(who, 'online')
        elif type_ == 'unavailable':
            self.DEBUG("roster setting %s to offline" % who, DBG_NODE_PRESENCE)
            self._roster._setOnline(who, 'offline')
        self._roster._setShow(who, pres_obj.getShow())
        self._roster._setStatus(who, pres_obj.getStatus())

    def _IqRosterManage(self, conn, iq_obj):
        "NS_ROSTER and type in [result,set]"
        for item in iq_obj.getQueryNode().getChildren():
            jid = item.getAttr('jid')
            name = item.getAttr('name')
            sub = item.getAttr('subscription')
            ask = item.getAttr('ask')

            groups = []
            for group in item.getTags("group"):
                groups.append(group.getData())

            if jid:
                if sub == 'remove' or sub == 'none':
                    self._roster._remove(jid)
                else:
                    self._roster._set(jid=jid, name=name,
                                      groups=groups, sub=sub,
                                      ask=ask)
            else:
                self.DEBUG("roster - jid not defined ?", DBG_NODE_IQ)

    def _IqRegisterResult(self, conn, iq_obj):
        "NS_REGISTER and type==result"
        self._reg_info = {}
        for item in iq_obj.getQueryNode().getChildren():
            self._reg_info[item.getName()] = item.getData()

    def _IqAgentsResult(self, conn, iq_obj):
        "NS_AGENTS and type==result"
        self.DEBUG("got agents result", DBG_NODE_IQ)
        self._agents = {}
        for agent in iq_obj.getQueryNode().getChildren():
            if agent.getName() == 'agent':  ## hmmm
                self._agents[agent.getAttr('jid')] = {}
                for info in agent.getChildren():
                    self._agents[agent.getAttr('jid')][info.getName()] = \
                        info.getData()

    def auth(self, username, passwd, resource):
        """Authenticates and logs in to the specified jabber server
           Automatically selects the 'best' authentication method
           provided by the server.
           Supports plain text, digest and zero-k authentication.

           Returns True if the login was successful, False otherwise.
        """
        auth_get_iq = Iq(type='get')
        auth_get_iq.setID('auth-get')
        q = auth_get_iq.setQuery(NS_AUTH)
        q.insertTag('username').insertData(username)
        self.send(auth_get_iq)

        auth_response = self.waitForResponse("auth-get")
        if auth_response == None:
            return False  # Error
        else:
            auth_ret_node = auth_response

        auth_ret_query = auth_ret_node.getTag('query')
        self.DEBUG("auth-get node arrived!", (DBG_INIT, DBG_NODE_IQ))

        auth_set_iq = Iq(type='set')
        auth_set_iq.setID('auth-set')

        q = auth_set_iq.setQuery(NS_AUTH)
        q.insertTag('username').insertData(username)
        q.insertTag('resource').insertData(resource)

        if auth_ret_query.getTag('token'):

            token = auth_ret_query.getTag('token').getData()
            seq = auth_ret_query.getTag('sequence').getData()
            self.DEBUG("zero-k authentication supported", (DBG_INIT,
                                                           DBG_NODE_IQ))
            hash_ = hashlib.sha1(hashlib.sha1(passwd).hexdigest() +
                                 token).hexdigest()
            for item in xrange(int(seq)):
                hash_ = hashlib.sha1(hash_).hexdigest()
            q.insertTag('hash').insertData(hash)

        elif auth_ret_query.getTag('digest'):

            self.DEBUG("digest authentication supported", (DBG_INIT,
                                                           DBG_NODE_IQ))
            digest = q.insertTag('digest')
            digest.insertData(hashlib.sha1(
                self.getIncomingID() + passwd).hexdigest())
        else:
            self.DEBUG("plain text authentication supported", (DBG_INIT,
                                                               DBG_NODE_IQ))
            q.insertTag('password').insertData(passwd)

        iq_result = self.SendAndWaitForResponse(auth_set_iq)

        if iq_result is None:
            return False

        elif iq_result.getError() is None:
            return True

        else:
            self.lastErr = iq_result.getError()
            self.lastErrCode = iq_result.getErrorCode()
            # raise error(iq_result.getError()) ?
            return False

    ## Roster 'helper' func's - also see the Roster class ##

    def requestRoster(self):
        """Requests the roster from the server and returns a
           Roster() class instance."""
        rost_iq = Iq(type='get')
        rost_iq.setQuery(NS_ROSTER)
        self.SendAndWaitForResponse(rost_iq)
        self.DEBUG("got roster response", DBG_NODE_IQ)
        self.DEBUG("roster -> %s" % ustr(self._roster), DBG_NODE_IQ)
        return self._roster

    def getRoster(self):
        """Returns the current Roster() class instance. Does
           not contact the server."""
        return self._roster

    def addRosterItem(self, jid):
        """ Send off a request to subscribe to the given jid.
        """
        self.send(Presence(to=jid, type="subscribe"))

    def updateRosterItem(self, jid, name=None, groups=None):
        """ Update the information stored in the roster about a roster item.

            'jid' is the Jabber ID of the roster entry; 'name' is the value to
            set the entry's name to, and 'groups' is a list of groups to which
            this roster entry can belong.  If either 'name' or 'groups' is not
            specified, that value is not updated in the roster.
        
        """
        iq = Iq(type='set')
        item = iq.setQuery(NS_ROSTER).insertTag('item')
        item.putAttr('jid', ustr(jid))
        if name != None:
            item.putAttr('name', name)
        if groups != None:
            for group in groups:
                item.insertTag('group').insertData(group)
        dummy = self.SendAndWaitForResponse(iq)  # Do we need to wait??

    def removeRosterItem(self, jid):
        """Removes an item with Jabber ID jid from both the
           server's roster and the local internal Roster()
           instance"""
        rost_iq = Iq(type='set')
        q = rost_iq.setQuery(NS_ROSTER).insertTag('item')
        q.putAttr('jid', ustr(jid))
        q.putAttr('subscription', 'remove')
        self.SendAndWaitForResponse(rost_iq)
        return self._roster

    ## Registration 'helper' funcs ##

    def requestRegInfo(self, agent=''):
        """Requests registration info from the server.
           Returns the Iq object received from the server."""
        if agent.find('.') == -1:
            if agent: agent += '.'
            agent += self._host
        self._reg_info = {}
        reg_iq = Iq(type='get', to=agent)
        reg_iq.setQuery(NS_REGISTER)
        self.DEBUG("Requesting reg info from %s:" % agent, DBG_NODE_IQ)
        self.DEBUG(ustr(reg_iq), DBG_NODE_IQ)
        return self.SendAndWaitForResponse(reg_iq)

    def getRegInfo(self):
        """Returns a dictionary of fields requested by the server for a
           registration attempt.  Each dictionary entry maps from the name of
           the field to the field's current value (either as returned by the
           server or set programmatically by calling self.setRegInfo(). """
        return self._reg_info

    def setRegInfo(self, key, val):
        """Sets a name/value attribute. Note: requestRegInfo must be
           called before setting."""
        self._reg_info[key] = val

    def sendRegInfo(self, agent=''):
        """Sends the populated registration dictionary back to the server"""
        if agent.find('.') == -1:
            if agent: agent += '.'
            agent += self._host
        reg_iq = Iq(to=agent, type='set')
        q = reg_iq.setQuery(NS_REGISTER)
        for info in self._reg_info.keys():
            q.insertTag(info).putData(self._reg_info[info])
        return self.SendAndWaitForResponse(reg_iq)

    def deregister(self, agent=''):
        """ Send off a request to deregister with the server or with the given
            agent.  Returns True if successful, else False.

            Note that you must be authorised before attempting to deregister.
        """
        if agent:
            if agent.find('.') == -1:
                agent += '.' + self._host
            self.send(Presence(to=agent, type='unsubscribed'))
            # This is enough f.e. for icqv7t or jit
        else:
            agent = self._host
        q = self.requestRegInfo()
        kids = q.getQueryPayload()
        keyTag = kids.getTag("key")

        iq = Iq(to=agent, type="set")
        iq.setQuery(NS_REGISTER)
        iq.setQueryNode("")
        q = iq.getQueryNode()
        if keyTag != None:
            q.insertXML("<key>" + keyTag.getData() + "</key>")
        q.insertXML("<remove/>")

        result = self.SendAndWaitForResponse(iq)

        if result == None:
            return False
        elif result.getType() == "result":
            return True
        else:
            return False

    ## Agent helper funcs ##

    def requestAgents(self):
        """Requests a list of available agents.  Returns a dictionary
           containing information about each agent; each entry in the
           dictionary maps the agent's JID to a dictionary of attributes
           describing what that agent can do (as returned by the
           NS_AGENTS query)."""
        self._agents = {}
        agents_iq = Iq(type='get')
        agents_iq.setQuery(NS_AGENTS)
        self.SendAndWaitForResponse(agents_iq)
        self.DEBUG("agents -> %s" % ustr(self._agents), DBG_NODE_IQ)
        return self._agents

    def _discover(self, ns, jid, node=None):
        iq = Iq(to=jid, type='get', query=ns)
        if node:
            iq.putAttr('node', node)
        rep = self.SendAndWaitForResponse(iq)
        if rep:
            ret = rep.getQueryPayload()
        else:
            ret = []
        if not ret:
            ret = []
        return ret

    def discoverItems(self, jid, node=None):
        """ According to JEP-0030: jid is mandatory, name, node, action is 
        optional. 
        """
        ret = []
        disco = self._discover(NS_P_DISC_ITEMS, jid, node)
        for i in disco:
            ret.append(i.attrs)
        return ret

    def discoverInfo(self, jid, node=None):
        """ According to JEP-0030:
            For identity: category, name is mandatory, type is optional.
            For feature: var is mandatory
        """
        identities, features = [], []
        disco = self._discover(NS_P_DISC_INFO, jid, node)
        for i in disco:
            if i.getName() == 'identity':
                identities.append(i.attrs)
            elif i.getName() == 'feature':
                features.append(i.getAttr('var'))
        return identities, features

    def browseAgents(self, jid, node=None):
        identities, features, items = [], [], []
        iq = Iq(to=jid, type='get', query=NS_BROWSE)
        rep = self.SendAndWaitForResponse(iq)
        if not rep:
            return identities, features, items
        q = rep.getTag('service')
        if q:
            identities = [q.attrs]
        else:
            identities = []
        if not q:
            return identities, features, items
        for node in q.kids:
            if node.getName() == 'ns':
                features.append(node.getData())
            else:
                infos = node.attrs
                infos['category'] = node.getName()
                items.append(node.attrs)
        return identities, features, items


#############################################################################

class Protocol(xmlstream.Node):
    """Base class for jabber 'protocol elements': message, presence, and iq.
       xdb and log are semi-frequent extensions to this list.
       Protocol implements methods that are common to all of these.
       """

    def __init__(self, name=None, to=None, type=None, attrs=None, frm=None,
                 payload=[], node=None):
        if not attrs:
            attrs = {}
        if to:
            attrs['to'] = to
        if frm:
            attrs['from'] = frm
        if type:
            attrs['type'] = type
        self._node = self
        xmlstream.Node.__init__(self, tag=name, attrs=attrs, payload=payload,
                                node=node)

    def __repr__(self):
        return self.__str__()

    def getError(self):
        """Returns the error string, if any"""
        try:
            return self.getTag('error').getData()
        except:
            return None

    def getErrorCode(self):
        """Returns the error code, if any"""
        try:
            return self.getTag('error').getAttr('code')
        except:
            return None

    def setError(self, val, code):
        """Sets an error string and code
        TODO: I think this isn't used anywhere, and may not follow
        xmpp error guidelines
        """
        err = self.getTag('error')
        if not err:
            err = self.insertTag('error')
        err.putData(val)
        err.putAttr('code', str(code))

    def get(self, attr, default_return):
        """Eventual replacement of the various get() methods.
        attr -> str, values of to, type, id, from.
        to and from need a little more work (JID magic)
        Wait, I should just use getAttr, since it's in the base class. Or maybe
        use get, which uses getAttr sometimes and the fancy JID thing
        other times. Ponder.
        TODO: replace the other get methods of Protocol.
        """
        try:
            return self.getAttr(attr)
        except:
            return None

    def getTo(self):
        """Returns the 'to' attribute as a JID object."""
        try:
            return JID(self.getAttr('to'))
        except:
            return None

    def getFrom(self):
        """Returns the 'from' attribute as a JID object."""
        try:
            return JID(self.getAttr('from'))
        except:
            return None

    def getType(self):
        """Returns the 'type' attribute of the protocol element."""
        return self.getAttr('type')

    def getID(self):
        """Returns the 'id' attribute of the protocol element."""
        return self.getAttr('id')

    def setTo(self, val):
        """Sets the 'to' element to the given JID.
        I suspect this and setFrom just use the unicode text version of the
        JID to not embed objects in the xml. That makes sense. The automated
        tests check using both JID objects and unicode strings.
        TODO: add some checking for JID strings.
        """
        self.putAttr('to', ustr(val))

    def setFrom(self, val):
        """Sets the 'from' element to the given JID.
        TODO: add some checking for valid JIDs."""
        self.putAttr('from', ustr(val))

    def setType(self, val):
        """Sets the 'type' attribute of the protocol element.
        'error' is the only valid type for all three defined protocol types
        RFC6120-core, section 8.1.3
        TODO: add checking for the valid types.
        """
        self.putAttr('type', val)

    def setID(self, val):
        """Sets the ID of the protocol element"""
        self.putAttr('id', val)

    def getX(self, index=0):
        """Returns the x namespace, optionally passed an index if there are
           multiple tags."""
        try:
            return self.getXNodes()[index].namespace
        except:
            return None

    def setX(self, namespace, index=0):
        """Sets the name space of the x tag. It also creates the node
           if it doesn't already exist."""
        x = self.getTag('x', index)
        if not x:
            x = self.insertTag('x')
        x.namespace = namespace
        return x

    def setXPayload(self, payload, namespace=''):
        """Sets the Child of an 'x' tag. Can be a Node instance or an
           XML document"""
        x = self.setX(namespace)

        if isinstance(payload, str) or isinstance(payload, unicode):
            payload = xmlstream.NodeBuilder(payload).getDom()

        x.kids = []  # should be a method for this realy
        x.insertNode(payload)

    def getXPayload(self, val=None):
        """Returns the x tags' payload as a list of Node instances."""
        nodes = []
        if val is not None:
            if isinstance(val, str):
                for xnode in self.getTags('x'):
                    if xnode.getNamespace() == val:
                        nodes.append(xnode.kids[0])
                return nodes
            else:
                try:
                    return self.getTags('x')[val].kids[0]
                except:
                    return None

        for xnode in self.getTags('x'):
            nodes.append(xnode.kids[0])
        return nodes

    def getXNode(self, val=None):
        """Returns the x Node instance. If there are multiple tags
           the first Node is returned. For multiple X nodes use getXNodes
           or pass an index integer value or namespace string to getXNode
           and if a match is found it will be returned."""
        if val is not None:
            nodes = []
            if isinstance(val, str):
                for xnode in self.getTags('x'):
                    if xnode.getNamespace() == val: nodes.append(xnode)
                return nodes
            else:
                try:
                    return self.getTags('x')[val]
                except:
                    return None
        else:
            try:
                return self.getTag('x')
            except:
                return None

    def getXNodes(self):
        """Returns a list of X nodes."""
        return self.getTags('x')

    def setXNode(self, val=''):
        """Sets the x tag's data to the given textual value."""
        self.insertTag('x').putData(val)

    def swap_from_to(self):
        """Swaps the element's from and to attributes.
           Note that this is only useful for writing components; if you are
           writing a Jabber client you shouldn't use this, because the Jabber
           server will set the 'from' field automatically.
           """
        tmp = self.getTo()
        self.setTo(self.getFrom())
        self.setFrom(tmp)


#############################################################################

class Message(Protocol):
    """Builds on the Protocol class to provide an interface for sending
       message protocol elements
       <message> objects require a type="thing", where thing is one of
       normal, chat, groupcat, headline, or error.
       http://xmpp.org/rfcs/rfc6120.html#schemas-client, section A.5.
       The <message> attributes are to, from, id, and type.
       It can contain sub-elements of <body>, <subject>. and <thread>.

       <message /> stanzas are described in section 5.2. Messaging in general
       is in section 5.

       example:
       <message from"madhatter@wonderland.lit/foo"
                to="alice@wonderland.lit"
                type="chat">
            <body>Who are you?</body>
            <subject>Query</subject>
        </message>

        is generated by
        message = Message(to="alice@wonderland.lit", type="chat",
            frm="madhatter@wonderland.lit/foo", body="Who are you?",
             subject="Query")
       """

    def __init__(self, to=None, body=None, type=None, subject=None,
                 attrs=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'message', to=to, type=type, attrs=attrs,
                          frm=frm, payload=payload, node=node)
        if body:
            self.setBody(body)
        if subject:
            self.setSubject(subject)
        # examine x tag and set timestamp if present
        try:
            self.setTimestamp(self.getTag('x').getAttr('stamp'))
        except:
            self.setTimestamp()

    def getBody(self):
        """Returns the message body."""
        try:
            return self.getTag('body').getData()
        except:
            return None

    def getSubject(self):
        """Returns the message's subject."""
        try:
            return self.getTag('subject').getData()
        except:
            return None

    def getThread(self):
        """Returns the message's thread ID."""
        try:
            return self.getTag('thread').getData()
        except:
            return None

    def setBody(self, val):
        """Sets the message body text.
        FIXME: I don't know why appending to the body is a good idea.
        """
        body = self.getTag('body')
        if body:
            body.putData(val)
        else:
            body = self.insertTag('body').putData(val)

    def setSubject(self, val):
        """Sets the message subject text.
        FIXME: I don't know why appending to the subject is a good idea.
        """
        subj = self.getTag('subject')
        if subj:
            subj.putData(val)
        else:
            self.insertTag('subject').putData(val)

    def setThread(self, val):
        """Sets the message thread ID."""
        thread = self.getTag('thread')
        if thread:
            thread.putData(val)
        else:
            self.insertTag('thread').putData(val)

    def setTimestamp(self, val=None):
        if not val:
            val = time.strftime('%Y%m%dT%H:%M:%S', time.gmtime(time.time()))
        self.time_stamp = val

    def build_reply(self, reply_txt=''):
        """Returns a new Message object as a reply to itself.
           The reply message has the 'to', 'type' and 'thread' attributes
           automatically set."""
        m = Message(to=self.getFrom(), body=reply_txt)
        if not self.getType() == None:
            m.setType(self.getType())
        t = self.getThread()
        if t:
            m.setThread(t)
        return m


#############################################################################

class Presence(Protocol):
    """Class for creating and managing jabber <presence> protocol
       elements. Presence is used to show your presence, or to request or respond
       to presence requests.

       Example:
           <presence from="alice@wonderland.lit/pda">
               <show>xa</show>
               <status>down the rabbit hole!</status>
            </presence>

        by:
        presence = Presence(frm="alice@wonderland.lit/pda",
            show="xa", status="down the rabbit hole!")

        http://xmpp.org/rfcs/rfc6120.html#schemas-client. This is section A.5,
        look for <xs:element name='presence'> in the text file for the Client
        namespace.

        RFC 6121, section 3, describes managing presence subscriptions, and
        section 4 describes exchanging presence information.

        'type' attributes for presence may be any of error, probe, subscribe,
        subscribed, unavailable, unsubscribe, or unsubscribed.
       """

    def __init__(self, to=None, type=None, priority=None, show=None,
                 status=None, attrs=None, frm=None, payload=[], node=None):
        Protocol.__init__(self, 'presence', to=to, type=type, attrs=attrs,
                          frm=frm, payload=payload, node=node)
        if priority:
            self.setPriority(priority)
        if show:
            self.setShow(show)
        if status:
            self.setStatus(status)

    def getStatus(self):
        """Returns the presence status"""
        try:
            return self.getTag('status').getData()
        except:
            return None

    def getShow(self):
        """Returns the presence show"""
        try:
            return self.getTag('show').getData()
        except:
            return None

    def getPriority(self):
        """Returns the presence priority"""
        try:
            return self.getTag('priority').getData()
        except:
            return None

    def _muc_getItemAttr(self, tag, attr):
        for xtag in self.getTags('x'):
            for child in xtag.getTags(tag):
                return child.getAttr(attr)

    def _muc_getSubTagDataAttr(self, tag, attr):
        for xtag in self.getTags('x'):
            for child in xtag.getTags('item'):
                for cchild in child.getTags(tag):
                    return cchild.getData(), cchild.getAttr(attr)
        return None, None

    def getRole(self):
        """Returns the presence role (for groupchat)"""
        return self._muc_getItemAttr('item', 'role')

    def getAffiliation(self):
        """Returns the presence affiliation (for groupchat)"""
        return self._muc_getItemAttr('item', 'affiliation')

    def getJid(self):
        """Returns the presence jid (for groupchat)"""
        return self._muc_getItemAttr('item', 'jid')

    def getReason(self):
        """Returns the reason of the presence (for groupchat)"""
        return self._muc_getSubTagDataAttr('reason', '')[0]

    def getActor(self):
        """Returns the reason of the presence (for groupchat)"""
        return self._muc_getSubTagDataAttr('actor', 'jid')[1]

    def getStatusCode(self):
        """Returns the status code of the presence (for groupchat)"""
        return self._muc_getItemAttr('status', 'code')

    def setShow(self, val):
        """Sets the presence show"""
        show = self.getTag('show')
        if show:
            show.putData(val)
        else:
            self.insertTag('show').putData(val)

    def setStatus(self, val):
        """Sets the presence status"""
        status = self.getTag('status')
        if status:
            status.putData(val)
        else:
            self.insertTag('status').putData(val)

    def setPriority(self, val):
        """Sets the priority of the resource. Description is found in RFC 6121,
        section 4.7.2.3. It is an OPTIONAL parameter, with integer values
        between -128 and +127. While servers MUST assume resources without
        a priority are priority 0, do not blindly set blanks to 0.

        Section 8 of RFC 6121 describes how to use priority in detail.
        """
        #TODO: check that it's an integer in the correct range.
        #FIXME: Using integers gets AttributeErrors in sax. There's something deeply wrong here.
        pri = self.getTag('priority')
        if pri:
            pri.putData(val)
        else:
            self.insertTag('priority').putData(val)


#############################################################################

class Iq(Protocol):
    """Class for creating and managing jabber <iq> protocol
       elements

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

        'type' can be error, get, result, set. RFC 6120, search for
        element name='iq'. Type is required.
       """

    def __init__(self, to=None, type=None, query=None, attrs=None,
                 frm=None, payload=[], node=None):
        Protocol.__init__(self, 'iq', to=to, type=type, attrs=attrs,
                          frm=frm, payload=payload, node=node)
        if query:
            self.setQuery(query)
        # FIXME: type is required by RFC 6120 for iq stanzas.
        # FIXME: Iq doesn't support id, and it must.

    def _getTag(self, tag):
        try:
            return self.getTag(tag).namespace
        except:
            return None

    def _setTag(self, tag, namespace):
        q = self.getTag(tag)
        if q:
            q.namespace = namespace
        else:
            q = self.insertTag(tag)
            q.namespace = namespace
        return q

    def getList(self):
        "returns the list namespace"
        return self._getTag('list')

    def setList(self, namespace):
        #FIXME: I don't see a list namespace in the RFCs.
        return self._setTag('list', namespace)

    def getQuery(self):
        '''returns the query namespace. Really, just the namespace, like
        'jabber:iq:privacy'.
        '''
        return self._getTag('query')

    def setQuery(self, namespace):
        """Sets a query's namespace, and inserts a query tag if
           one doesn't already exist.  The resulting query tag
           is returned as the function result."""
        return self._setTag('query', namespace)

    def setQueryPayload(self, payload, add=False):
        """Sets a Iq's query payload.  'payload' can be either a Node
           structure or a valid xml document. The query tag is automatically
           inserted if it doesn't already exist."""
        q = self.getQueryNode()

        if q is None:
            q = self.insertTag('query')

        if isinstance(payload, str) or isinstance(payload, unicode):
            payload = xmlstream.NodeBuilder(payload).getDom()

        if not add:
            q.kids = []
        q.insertNode(payload)

    def getQueryPayload(self):
        """Returns the query's payload as a Node list"""
        q = self.getQueryNode()
        if q:
            return q.kids

    def getQueryNode(self):
        """Returns any textual data contained by the query tag"""
        try:
            return self.getTag('query')
        except:
            return None

    def setQueryNode(self, val):
        """Sets textual data contained by the query tag"""
        q = self.getTag('query')
        if q:
            q.putData(val)
        else:
            self.insertTag('query').putData(val)


#############################################################################

class Roster:
    """A Class for simplifying roster management. Also tracks roster
       item availability."""

    def __init__(self):
        self._data = {}
        self._listener = None
        ## unused for now ... ##
        self._lut = {'both': RS_SUB_BOTH,
                     'from': RS_SUB_FROM,
                     'to': RS_SUB_TO}

    def setListener(self, listener):
        """ Set a listener function to be called whenever the roster changes.

            The given function will be called whenever the contents of the
            roster changes in response to a received <presence> or <iq> packet.
            The listener function should be defined as follows:

                def listener(action, jid, info)

            'action' is a string indicating what type of change has occurred:

                "add"     A new item has been added to the roster.
                "update"  An existing roster item has been updated.
                "remove"  A roster entry has been removed.

            'jid' is the Jabber ID (as a string) of the affected roster entry.

            'info' is a dictionary containing the information that has been
            added or updated for this roster entry.  This dictionary may
            contain any combination of the following:

                "name"    The associated name of this roster entry.
                "groups"  A list of groups associated with this roster entry.
                "online"  The roster entry's "online" value ("online",
                          "offline" or "pending").
                "sub"     The roster entry's subscription value ("none",
                          "from", "to" or "both").
                "ask"     The roster entry's ask value, if any (None,
                          "subscribe", "unsubscribe").
                "show"    The roster entry's show value, if any (None, "away",
                          "chat", "dnd", "normal", "xa").
                "status"  The roster entry's current 'status' value, if
                          specified.
        """
        self._listener = listener


    def jid_info(self, jid, info=None):
        """Returns the name, groups, online, subscription (sub), ask, presence (show)
        or status value. Returns None if the item is not present.

        Input is a JID string and a string of name, groups, online, sub, ask, show,
        or status."""

        jid = ustr(jid)
        try:
            return self._data[jid][info]
        except KeyError:
            return None

    def getStatus(self, jid):  ## extended
        """Returns the 'status' value for a Roster item with the given jid."""
        warnings.warn('getStatus should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['status']
        return None

    def getShow(self, jid):  ## extended
        """Returns the 'show' value for a Roster item with the given jid."""
        warnings.warn('getShow should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['show']
        return None

    def getOnline(self, jid):  ## extended
        """Returns the 'online' status for a Roster item with the given jid.
           """
        warnings.warn('getOnline should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['online']
        return None

    def getSub(self, jid):
        """Returns the 'subscription' status for a Roster item with the given
           jid."""
        warnings.warn('getSub should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['sub']
        return None

    def getName(self, jid):
        """Returns the 'name' for a Roster item with the given jid."""
        warnings.warn('getName should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['name']
        return None

    def getGroups(self, jid):
        """ Returns the list of groups associated with the given 
        roster item.
        """
        warnings.warn('getGroups should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['groups']
        return None

    def getAsk(self, jid):
        """Returns the 'ask' status for a Roster item with the given jid."""
        warnings.warn('getAsk should not be called, use Roster.jid_info(jid, info).', DeprecationWarning)
        jid = ustr(jid)
        if jid in self._data:
            return self._data[jid]['ask']
        return None


    def online_summary(self):
        """Returns a summary of the roster's contents.  The returned value is a
           dictionary mapping the basic (no resource) JID string to their current
           availability status (online, offline, pending). """
        return {key: self._data[key]['online'] for key in self._data.keys()}


    def getJIDs(self):
        """Returns a list of JIDs stored within the roster.  Each entry in the
           list is a JID object."""
        to_ret = []
        for jid in self._data.keys():
            to_ret.append(JID(jid))
        return to_ret


    def getRaw(self):
        """Returns the internal data representation of the roster."""
        return self._data


    def isOnline(self, jid):
        """Returns True if the given jid is online, False if not."""
        jid = ustr(jid)
        if self.getOnline(jid) != 'online':
            return False
        else:
            return True


    def _set(self, jid, name, groups, sub, ask):
        # meant to be called by actual iq tag
        """Used internally - private"""
        jid = ustr(jid)  # just in case
        online = 'offline'
        if ask:
            online = 'pending'
        if jid in self._data:  # update it
            self._data[jid]['name'] = name
            self._data[jid]['groups'] = groups
            self._data[jid]['ask'] = ask
            self._data[jid]['sub'] = sub
            if self._listener is not None:
                self._listener("update", jid, {'name': name,
                                               'groups': groups,
                                               'sub': sub, 'ask': ask})
        else:
            self._data[jid] = {'name': name, 'groups': groups, 'ask': ask,
                               'sub': sub, 'online': online, 'status': None,
                               'show': None}
            if self._listener is not None:
                self._listener("add", jid, {'name': name, 'groups': groups,
                                            'sub': sub, 'ask': ask,
                                            'online': online})

    def _setOnline(self, jid, val):
        """Used internally - private"""
        jid = ustr(jid)
        if jid in self._data:
            self._data[jid]['online'] = val
            if self._listener != None:
                self._listener("update", jid, {'online': val})
        else:  ## fall back
            jid_basic = JID(jid).getStripped() #_data wants to use the bare JID as a hash key
            #jid_basic = JID(jid).bare()
            if jid_basic in self._data:
                self._data[jid_basic]['online'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'online': val})

    def _setShow(self, jid, val):
        """Used internally - private"""
        jid = ustr(jid)
        if jid in self._data:
            self._data[jid]['show'] = val
            if self._listener != None:
                self._listener("update", jid, {'show': val})
        else:  ## fall back
            jid_basic = JID(jid).getStripped()
            #jid_basic = JID(jid).bare()
            if jid_basic in self._data:
                self._data[jid_basic]['show'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'show': val})

    def _setStatus(self, jid, val):
        """Used internally - private"""
        jid = ustr(jid)
        if jid in self._data:
            self._data[jid]['status'] = val
            if self._listener != None:
                self._listener("update", jid, {'status': val})
        else:  ## fall back
            jid_basic = JID(jid).getStripped() #_data wants to use the bare JID as a hash key
            #jid_basic = JID(jid).bare()
            if jid_basic in self._data:
                self._data[jid_basic]['status'] = val
                if self._listener != None:
                    self._listener("update", jid_basic, {'status': val})

    def _remove(self, jid):
        """Used internally - private"""
        if jid in self._data:
            del self._data[jid]
            if self._listener != None:
                self._listener("remove", jid, {})


#############################################################################

class JID:
    """A simple class for managing jabber IDs.

    Normative reference: http://xmpp.org/rfcs/rfc6122.html,
    Extensible Messaging and Presence Protocol (XMPP): Address Format

    The terms "localpart", "domainpart", and "resourcepart" are defined in [XMPP-ADDR].
    jid = [ localpart "@" ] domainpart [ "/" resourcepart ]

The term "bare JID" refers to an XMPP address of the form <localpart@domainpart>
 (for an account at a server) or of the form <domainpart> (for a server).

The term "full JID" refers to an XMPP address of the form <localpart@domainpart/resourcepart>
(for a particular authorized client or device associated with an account) or
of the form <domainpart/resourcepart> (for a particular resource or
script associated with a server).
"""

    def __init__(self, jid='', node='', domain='', resource=''):
        # if isinstance(jid, self):
        if type(jid) is type(self):
            self.localpart = jid.localpart
            self.domainpart = jid.domainpart
            self.resourcepart = jid.resourcepart
        elif jid:
            if jid.find('@') == -1:
                self.localpart = ''
            else:
                bits = jid.split('@', 1)
                self.localpart = bits[0]
                jid = bits[1]

            if jid.find('/') == -1:
                self.domainpart = jid
                self.resourcepart = ''
            else:
                self.domainpart, self.resourcepart = jid.split('/', 1)
        else:
            self.localpart = node
            self.domainpart = domain
            self.resourcepart = resource

        #self.localpart = self.node
        #self.domainpart = self.domain
        #self.resourcepart = self.resource

        # FIXME: Add one check that domainpart exists -- you must have at least domain for a valid JID

    def __str__(self):
        jid_str = self.domainpart
        if self.localpart:
            jid_str = self.localpart + '@' + jid_str
        if self.resourcepart:
            jid_str += '/' + self.resourcepart
        return jid_str

    __repr__ = __str__


    def getStripped(self):
        """Returns a JID string with no resource"""
        warnings.warn('getStripped should not be called, just use JID.bare(). Nuts, someone is using this as a dictionary key.', DeprecationWarning)
        if self.localpart:
            return self.localpart + '@' + self.domainpart
        else:
            return self.domainpart

    def bare(self):
        """Returns a bare JID object"""
        return JID(node=self.localpart, domain=self.domainpart)

    def __eq__(self, other):
        """Returns whether this JID is identical to another one.
           The "other" can be a JID object or a string."""
        return str(self) == str(other)


#############################################################################

## component types

## Accept  NS_COMP_ACCEPT
## Connect NS_COMP_CONNECT
## Execute NS_COMP_EXECUTE

class Component(Connection):
    """docs to come soon... """

    def __init__(self, host, port, connection=xmlstream.TCP,
                 debug=[], log=False, ns=NS_COMP_ACCEPT, hostIP=None,
                 proxy=None):
        Connection.__init__(self, host, port, namespace=ns, debug=debug,
                            log=log, connection=connection, hostIP=hostIP,
                            proxy=proxy)
        self._auth_OK = False
        self.registerProtocol('xdb', XDB)

    def auth(self, secret):
        """will disconnect on failure"""
        self.send(u"<handshake id='1'>%s</handshake>"
                  % hashlib.sha1(self.getIncomingID() + secret).hexdigest())
        while not self._auth_OK:
            self.DEBUG("waiting on handshake")
            self.process(1)

        return True

    def dispatch(self, root_node):
        """Catch the <handshake/> here"""
        if root_node.name == 'handshake':  # check id too ?
            self._auth_OK = True
        Connection.dispatch(self, root_node)


#############################################################################

## component protocol elements

class XDB(Protocol):
    def __init__(self, attrs=None, type=None, frm=None, to=None, payload=[],
                 node=None):
        Protocol.__init__(self, 'xdb', attrs=attrs, type=type, frm=frm,
                          to=to, payload=payload, node=node)


#############################################################################

class Log(Protocol):
    ## eg: <log type='warn' from='component'>Hello Log File</log>
    def __init__(self, attrs=None, type=None, frm=None, to=None, payload=[],
                 node=None):
        Protocol.__init__(self, 'log', attrs=attrs, type=type, frm=frm,
                          to=to, payload=payload, node=node)

    def setBody(self, val):
        "Sets the log message text."
        self.getTag('log').putData(val)

    def getBody(self):
        "Returns the log message text."
        return self.getTag('log').getData()


#############################################################################

class Server:
    pass
