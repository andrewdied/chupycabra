"""\
jabber.py provides a library for 

"""

# $Id$

import XMLStream
import sha
from string import split,find,replace

False = 0;
True  = 1;

NS_CLIENT     = "jabber:client"
NS_SERVER     = "jabber:server"
NS_AUTH       = "jabber:iq:auth"
NS_REGISTER   = "jabber:iq:register"
NS_ROSTER     = "jabber:iq:roster"
NS_OFFLINE    = "jabber:x:offline"
NS_AGENT      = "jabber:iq:agent"
NS_AGENTS     = "jabber:iq:agents"
NS_DELAY      = "jabber:x:delay"
NS_VERSION    = "jabber:iq:version"
NS_TIME       = "jabber:iq:time"
NS_VCARD      = "vcard-temp"
NS_PRIVATE    = "jabber:iq:private"
NS_SEARCH     = "jabber:iq:search"
NS_OOB        = "jabber:iq:oob"
NS_XOOB       = "jabber:x:oob"
NS_ADMIN      = "jabber:iq:admin"
NS_FILTER     = "jabber:iq:filter"
NS_AUTH_0K    = "jabber:iq:auth:0k"
NS_BROWSE     = "jabber:iq:browse"
NS_EVENT      = "jabber:x:event"
NS_CONFERENCE = "jabber:iq:conference"
NS_SIGNED     = "jabber:x:signed"
NS_ENCRYPTED  = "jabber:x:encrypted"
NS_GATEWAY    = "jabber:iq:gateway"
NS_LAST       = "jabber:iq:last"
NS_ENVELOPE   = "jabber:x:envelope"
NS_EXPIRE     = "jabber:x:expire"
NS_XHTML      = "http://www.w3.org/1999/xhtml"
NS_XDBGINSERT = "jabber:xdb:ginsert"
NS_XDBNSLIST  = "jabber:xdb:nslist"

## Possible constants for Roster class .... hmmm ##
RS_SUB_BOTH    = 0
RS_SUB_FROM    = 1
RS_SUB_TO      = 2

RS_ASK_SUBSCRIBE   = 1
RS_ASK_UNSUBSCRIBE = 0

RS_EXT_ONLINE   = 2
RS_EXT_OFFLINE  = 1
RS_EXT_PENDING  = 0


class Connection(XMLStream.Client):
    """Class for managing a connection to a jabber server.
    Inherits from the XMLStream Client class"""    
    def __init__(self, host, port=5222, debug=False, log=False):
    
        self.msg_hdlr  = None
        self.pres_hdlr = None
        self.iq_hdlr   = None

        self._roster = Roster()
        self._agents = {}
        self._reg_info = {}
        self._reg_agent = ''

        self._id = 0;
        self._expected = {}
        
        self.lastErr = ''
        self.lastErrCode = 0

        XMLStream.Client.__init__(self, host, port,
                                  'jabber:client', debug, log)

    def connect(self):
        """Attempts to connect to the specified jabber server.
           Raises an IOError on failiure"""
        try:
            XMLStream.Client.connect(self)
        except XMLStream.error, e:
            raise IOError

    def disconnect(self):
        """Safely disconnects from the connected server"""
        self.send(Presence(type='unavailable'));
        XMLStream.Client.disconnect(self)

    def send(self, what):
        """Sends a jabber protocol element to the server"""
        XMLStream.Client.write(self,str(what))

    def sendInitPresence(self):
        """Sends an empty presence protocol element to the
           server. Used to 'tell' the server your online"""
        p = Presence()
        self.send(p);
        
    def dispatch(self, root_node ):
        """Called internally when a 'protocol element' is recieved.
           builds the relevant jabber.py object and dispatches it
           to a relevant function or callback.
           Also does some processing for roster and authentication
           helper fuctions"""
        
        self.DEBUG("dispatch called")
        if root_node.name == 'message':
    
            self.DEBUG("got message dispatch")
            msg_obj = Message(node=root_node)
            self.messageHandler(msg_obj) 
            
        elif root_node.name == 'presence':

            self.DEBUG("got presence dispatch")
            pres_obj = Presence(node=root_node)

            who = str(pres_obj.getFrom())
            type = pres_obj.getType()
            if type == 'available' or type == None:
                self._roster._setOnline(who,'online')
                self._roster._setShow(who,pres_obj.getShow())
                self._roster._setStatus(who,pres_obj.getStatus())
            elif type == 'unavailable':
                self._roster._setOnline(who,'online')
                self._roster._setShow(who,pres_obj.getShow())
                self._roster._setStatus(who,pres_obj.getStatus())
            else:
                pass
            self.presenceHandler(pres_obj)

            
        elif root_node.name == 'iq':

            self.DEBUG("got an iq");
            iq_obj = Iq(node=root_node)
            queryNS = iq_obj.getQuery()

            if queryNS and root_node.getAttr('type') == 'result':

                if queryNS == NS_ROSTER: 

                    for item in iq_obj.getQueryNode().getChildren():
                        jid  = item.getAttr('jid')
                        name = item.getAttr('name')
                        sub  = item.getAttr('subscription')
                        ask  = item.getAttr('ask')
                        if jid:
                            if sub == 'remove':
                                self._roster._remove(jid)
                            else:
                                self._roster._set(jid=jid,name=name,
                                                  sub=sub,ask=ask)
                        else:
                            self.DEBUG("roster - jid not defined ?")
                        
                elif queryNS == NS_REGISTER:

                        self._reg_info = {}
                        for item in iq_obj.getQueryNode().getChildren():
                            self._reg_info[item.getName()] = item.getData() 
                    
                elif queryNS == NS_AGENTS:

                        self.DEBUG("got agents result")
                        self._agents = {}
                        for agent in iq_obj.getQueryNode().getChildren():
                            if agent.getName() == 'agent': ## hmmm
                                self._agents[agent.getAttr('jid')] = {}
                                for info in agent.getChildren():
                                    self._agents[agent.getAttr('jid')]\
                                         [info.getName()] = info.getData()
                else:
                    pass
                
            if root_node.getAttr('id') and \
               self._expected.has_key(root_node.getAttr('id')):
                self._expected[root_node.getAttr('id')] = iq_obj
            else:
                self.iqHandler(iq_obj)

        else:
            self.DEBUG("whats a tag -> " + root_node.name)


    def auth(self,username,passwd,resource):
        """Authenticates and logs in to the specified jabber server
           Automatically selects the 'best' authentication method
           provided by the server.
           Supports plain text, deigest and zero-k authentication"""

        auth_get_iq = Iq(type='get')
        auth_get_iq.setID('auth-get')
        q = auth_get_iq.setQuery('jabber:iq:auth')
        q.insertTag('username').insertData(username)
        self.send(auth_get_iq)
        auth_ret_node = self.waitForResponse("auth-get").asNode()
        auth_ret_query = auth_ret_node.getTag('query')
        self.DEBUG("auth-get node arrived!")

        auth_set_iq = Iq(type='set')
        auth_set_iq.setID('auth-set')
        
        q = auth_set_iq.setQuery('jabber:iq:auth')
        q.insertTag('username').insertData(username)
        q.insertTag('resource').insertData(resource)

        if auth_ret_query.getTag('token'):
            
            token = auth_ret_query.getTag('token').getData()
            seq = auth_ret_query.getTag('sequence').getData()
            self.DEBUG("zero-k authentication supported")
            hash = sha.new(sha.new(passwd).hexdigest()+token).hexdigest()
            for foo in xrange(int(seq)): hash = sha.new(hash).hexdigest()
            q.insertTag('hash').insertData(hash)

        elif auth_ret_query.getTag('digest'):

            self.DEBUG("digest authentication supported")
            digest = q.insertTag('digest')
            digest.insertData(sha.new(
                self.getStreamID() + passwd).hexdigest() )
        else:
            self.DEBUG("plain text authentication supported")
            q.insertTag('password').insertData(passwd)
            
        iq_result = self.SendAndWaitForResponse(auth_set_iq)
        if iq_result.getError() is None:
            return True
        else:
           self.lastErr     = iq_result.getError()
           self.lastErrCode = iq_result.getErrorCode()
           return False

    ## Roster 'helper' func's - also see the Roster class ##

    def requestRoster(self):
        #self._roster = {} 
        rost_iq = Iq(type='get')
        rost_iq.setQuery('jabber:iq:roster')
        self.SendAndWaitForResponse(rost_iq)
        self.DEBUG("got roster response")
        self.DEBUG("roster -> %s" % str(self._agents))
        return self._roster

    def getRoster(self):
        return self._roster

    def removeRosterItem(self,jid):        
        rost_iq = Iq(type='set')
        q = rost_iq.setQuery('jabber:iq:roster').insertTag('item')
        q.putAtrr('jid', str(jid))
        q.putAtrr('subscription', 'remove')
        self.SendAndWaitForResponse(rost_iq)
        return self._roster

    ## Registration 'helper' funcs ##
    
    def requestRegInfo(self,agent=''):
        if agent: agent = agent + '.'
        self._reg_info = {}
        reg_iq = Iq(type='get', to = agent + self._host)
        reg_iq.setQuery('jabber:iq:register')
        self.DEBUG("got reg response")
        self.DEBUG("roster -> %s" % str(self._agents))
        return self.SendAndWaitForResponse(reg_iq)        

    def getRegInfo(self):
        return self._reg_info

    def setRegInfo(self,key,val):
        self._reg_info[key] = val

    def sendRegInfo(self, agent=''):
        if agent: agent = agent + '.'
        reg_iq = Iq(to = agent + self._host, type='set')
        q = reg_iq.setQuery('jabber:iq:register')
        for info in self._reg_info.keys():
            q.insertTag(info).putData(self._reg_info[info])
        return self.SendAndWaitForResponse(reg_iq)

    ## Agent helper funcs ##

    def requestAgents(self):
        self._agents = {}
        agents_iq = Iq(type='get')
        agents_iq.setQuery('jabber:iq:agents')
        self.SendAndWaitForResponse(agents_iq)
        self.DEBUG("got agents response")
        self.DEBUG("agents -> %s" % str(self._agents))
        return self._agents

    ## Call back stuff ###

    def setMessageHandler(self, func):
        self.msg_hdlr = func

    def setPresenceHandler(self, func):
        self.pres_hdlr = func

    def setIqHandler(self, func):
        self.iq_hdlr = func

    def messageHandler(self, msg_obj):   ## Overide If You Want ##
        """Called when a message protocol element is recieved - can be
           overidden"""
        if self.msg_hdlr != None: self.msg_hdlr(self, msg_obj)
        
    def presenceHandler(self, pres_obj): ## Overide If You Want ##
        """Called when a pressence protocol element is recieved - can be
           overidden"""
        if self.pres_hdlr != None: self.pres_hdlr(self, pres_obj)
 
    def iqHandler(self, iq_obj):         ## Overide If You Want ##
        """Called when an iq protocol element is recieved - can be
           overidden"""
        if self.iq_hdlr != None: self.iq_hdlr(self, iq_obj)


    ## functions for sending element with ID's ##

    def waitForResponse(self, ID):
        """Blocks untils a protocol element with ID id is recieved"""
        ID = str(ID)
        self._expected[ID] = None
        while not self._expected[ID]:
            self.DEBUG("waiting on %s" % str(ID))
            self.process(0)
        response = self._expected[ID]
        del self._expected[ID]
        return response 

    def SendAndWaitForResponse(self, obj, ID=None):
        """Sends a protocol object and blocks until a response with
           the same ID is recieved"""
        if ID is None :
            ID = obj.getID()
            if ID is None:
                ID = self.getAnID()
                obj.setID(ID)
        ID = str(ID)
        self.send(obj)
        return self.waitForResponse(ID)

    def getAnID(self):

        self._id = self._id + 1
        return str(self._id)


class Protocol:
    """Base class for jabber 'protocol elements' - messages, presences and iqs.
       Implements methods that are common to all these"""
    def __init__(self):
        self._node = None

    def asNode(self):
        """returns an XMLStreamnode representation of the protocol element"""
        return self._node
    
    def __str__(self):
        return self._node.__str__()

    def getTo(self):
        "Returns a JID object of the to attr of the element" 
        try: return JID(self._node.getAttr('to'))
        except: return None
        
    def getFrom(self):
        "Returns a JID object of the from attribute of the element"
        try: return JID(self._node.getAttr('from'))
        except: return None

    def getType(self):
        "Returns the type attribute of the protocol element"
        try: return self._node.getAttr('type')
        except: return None

    def getID(self):
        "Returns the ID attribute of the protocol element"
        try: return self._node.getAttr('id')
        except: return None

    def setTo(self,val):
        self._node.putAttr('to', str(val))

    def setFrom(self,val):
        self._node.putAttr('from', str(val))

    def setType(self,val):
        self._node.putAttr('type', val)

    def setID(self,val):
        self._node.putAttr('id', val)

    def getX(self):
        "returns the x namespace"
        try: return self._node.getTag('x').namespace
        except: return None

    def setX(self,namespace):   
        x = self._node.getTag('x')
        if x:
            x.namespace = namespace
        else:
            x = self._node.insertTag('x')
            x.setNamespace(namespace)
        return x

    def setXPayload(self, payload):
        x = self.getXNode()

        if x is None:
            x = self._node.insertTag('x')

        if type(payload) == type('') or type(payload) == type(u''):
                payload = XMLStream.XMLStreamNodeBuilder(payload).getDom()

        x.kids = [] # should be a method for this realy 
        x.insertNode(payload)
                
    def getXPayload(self):
        x = self.getXNode()
        if x:
            return x.kids[0]
        return None
    
    def getXNode(self):
        try: return self._node.getTag('x')
        except: return None

    def setXNode(self, val=''):
        x = self._node.getTag('x')
        if x:
            x.putData(val)
        else:
            self._node.insertTag('x').putData(val)


class Message(Protocol):
    """Builds on the Protocol class to provide an interface for sending
       message protol elements"""
    def __init__(self, to=None, body=None, node=None):
        if node:
            self._node = node
        else:
            self._node = XMLStream.XMLStreamNode(tag='message')
        if to: self.setTo(str(to))
        if body: self.setBody(body)
        
    def getBody(self):
        body = self._node.getTag('body')
        try: return self._node.getTag('body').data
        except: return None

    def getType(self):
        try: return self._node.getAttr('type')
        except: return None

    def getSubject(self): 
        try: return self._node.getTag('subject').data
        except: return None

    def getThread(self):
        try: return self._node.getTag('thread').data
        except: return None
        
    def getError(self):
        try: return self._node.getTag('error').data
        except: return None

    def getErrorCode(self):
        try: return self._node.getTag('error').getAttr('code')
        except: return None

    def getTimestamp(self):
        pass

    def setBody(self,val):
        body = self._node.getTag('body')
        if body:
            body.putData(val)
        else:
            body = self._node.insertTag('body').putData(val)
            
    def setSubject(self,val):
        subj = self._node.getTag('subject')
        if subj:
            subj.putData(val)
        else:
            self._node.insertTag('subject').putData(val)

    def setThread(self,val): 
        thread = self._node.getTag('thread')
        if thread:
            thread.putData(val)
        else:
            self._node.insertTag('thread').putData(val)

    def setError(self,val,code): 
        err = self._node.getTag('error')
        if err:
            err.putData(val)
        else:
            err = self._node.insertTag('thread').putData(val)
        err.setAttr('code',str(code))

    def setTimestamp(self,val): pass

    def build_reply(self, reply_txt=''):
        m = Message(to=self.getFrom(), body=reply_txt)
        if not self.getType() == None:
            m.setType(self.getType())  
        t = self.getThread()
        if t: m.setThread(t)
        return m



class Presence(Protocol):
    def __init__(self, to=None, type=None, node=None):
        ##self.frm = 'mallum@jabber.com'
        if node:
            self._node = node
        else:
            self._node = XMLStream.XMLStreamNode(tag='presence')
        if to: self.setTo(str(to))
        if type: self.setType(type)


    def getStatus(self):
        try: return self._node.getTag('status').getData()
        except: return None

    def getShow(self):
        try: return self._node.getTag('show').getData()
        except: return None

    def getPriority(self):
        try: return self._node.getTag('priority').getData()
        except: return None
    
    def setShow(self,val):
        show = self._node.getTag('show')
        if show:
            show.putData(val)
        else:
            self._node.insertTag('show').putData(val)

    def setStatus(self,val):
        status = self._node.getTag('status')
        if status:
            status.putData(val)
        else:
            self._node.insertTag('status').putData(val)

    def setPriority(self,val):
        pri = self._node.getTag('priority')
        if pri:
            pri.putData(val)
        else:
            self._node.insertTag('priority').putData(val)


class Iq(Protocol): 
    def __init__(self, to='', type=None, node=None):
        if node:
            self._node = node
        else:
            self._node = XMLStream.XMLStreamNode(tag='iq')
        if to: self.setTo(to)
        if type: self.setType(type)

    def getError(self):
        try: return self._node.getTag('error').data
        except: return None

    def getErrorCode(self):
        try: return self._node.getTag('error').getAttr('code')
        except: return None

    def setError(self,val,code): 
        err = self._node.getTag('error')
        if err:
            err.putData(val)
        else:
            err = self._node.insertTag('thread').putData(val)
        err.setAttr('code',str(code))

    def getQuery(self):
        "returns the query namespace"
        try: return self._node.getTag('query').namespace
        except: return None

    def setQuery(self,namespace):   
        q = self._node.getTag('query')
        if q:
            q.namespace = namespace
        else:
            q = self._node.insertTag('query')
            q.setNamespace(namespace)
        return q

    def setQueryPayload(self, payload):
        q = self.getQueryNode()

        if q is None:
            q = self._node.insertTag('query')

        if type(payload) == type('') or type(payload) == type(u''):
                payload = XMLStream.XMLStreamNodeBuilder(payload).getDom()

        q.kids = [] # should be a method for this realy 
        q.insertNode(payload)
                
    def getQueryPayload(self):
        q = self.getQueryNode()
        if q:
            return q.kids[0]
        return None
    
    def getQueryNode(self):
        try: return self._node.getTag('query')
        except: return None

    def setQueryNode(self):
        q = self._node.getTag('query')
        if q:
            q.putData(val)
        else:
            self._node.insertTag('query').putData(val)

class Roster:
    """A Class for simplifying roster management. Also tracks roster
       items availability"""
    def __init__(self):
        self._data = {}
        ## unused for now ... ##
        self._lut = { 'both':RS_SUB_BOTH,
                      'from':RS_SUB_FROM,
                      'to':RS_SUB_TO }

    def getStatus(self, jid): ## extended
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['status']
        return None

    def getShow(self, jid):   ## extended
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['show']
        return None

    def getOnline(self,jid):  ## extended
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['online']
        return None
    
    def getSub(self,jid):
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['sub']
        return None

    def getName(self,jid):
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['name']
        return None

    def getAsk(self,jid):
        jid = str(jid) 
        if self._data.has_key(jid):
            return self._data[jid]['ask']
        return None

    def getSummary(self):
        """Returns a list of basic ( no resource ) JID's with there
           'availability' - online, offline, pending """
        to_ret = {}
        for jid in self._data.keys():
            to_ret[jid] = self._data[jid]['online']
        print "hello", to_ret
        return to_ret

    def getJIDs(self):
        to_ret = [];
        for jid in self._data.keys():
            to_ret.append(JID(jid))
        return to_ret

    def getRaw(self):
        return self._data

    def isOnline(self,jid):
        jid = str(jid)
        if self.getOnline(jid) != 'online':
            return False
        else:
            return True
    
    def _set(self,jid,name,sub,ask): # meant to be called by actual iq tag
        jid = str(jid) # just in case
        online = 'offline'
        if ask: online = 'pending' ## DJ - should this be To? ##
        if self._data.has_key(jid): # update it
            self._data[jid]['name'] = name
            self._data[jid]['ask'] = ask
            self._data[jid]['sub'] = sub
        else:
            self._data[jid] = { 'name': name, 'ask': ask, 'sub': sub,
                                'online': online, 'status': None, 'show': None} 

    def _setOnline(self,jid,val):
        jid = str(jid) 
        if self._data.has_key(jid):
            self._data[jid]['online'] = val
        else:                      ## fall back 
            jid_basic = JID(jid).getBasic()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['online'] = val

    def _setShow(self,jid,val):
        jid = str(jid) 
        if self._data.has_key(jid):
            self._data[jid]['show'] = val 
        else:                      ## fall back 
            jid_basic = JID(jid).getBasic()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['show'] = val


    def _setStatus(self,jid,val):
        jid = str(jid) 
        if self._data.has_key(jid):
            self._data[jid]['status'] = val
        else:                      ## fall back 
            jid_basic = JID(jid).getBasic()
            if self._data.has_key(jid_basic):
                self._data[jid_basic]['status'] = val


    def _remove(self,jid):
        if self._data.has_key(jid): del self._data[jid]

class JID:
    """A Simple calss for managing Jabber id's"""
    def __init__(self, jid='', node='', domain='', resource=''):
        if jid:
            if find(jid, '@') == -1:
                self.node = ''
            else:
                bits = split(jid, '@')
                self.node = bits[0]
                jid = bits[1]
                
            if find(jid, '/') == -1:
                self.domain = jid
                self.resource = ''
            else:
                self.domain, self.resource = split(jid, '/') 

        else:
            self.node = node
            self.domain = domain
            self.resource = resource

    def __str__(self):
        try:
            jid_str = ''
            if self.node: jid_str = jid_str + self.node + '@'
            if self.domain: jid_str = jid_str + self.domain
            if self.resource: jid_str = jid_str +'/'+ self.resource
            return jid_str
        except:
            return ''

    __repr__ = __str__

    def getNode(self): return self.node
    def getDomain(self): return self.domain
    def getResource(self): return self.resource

    def setNode(self,val): self.node = val
    def getDomain(self,val): self.domain = val
    def getResource(self,val): self.resource = val

    def getBasic(self): ## find beter name ##
        jid_str = ''
        if self.node: jid_str = jid_str + self.node + '@'
        if self.domain: jid_str = jid_str + self.domain
        return jid_str






