#!/usr/bin/env python

from core import var, logger, database, protocol, module, MParse
import time, eventlet, re, traceback

class Protocol(protocol.Protocol):
    """ TS6 protocol class """
    
    def __init__(self):
        """ config crap and initialize some variables """
        
        # uplink
        self.uplink, self.events = var.core
        self.protocol = self.uplink.protocol
        self.bursting = True
        # what we're going to send for CAPAB
        self.capab_msg = 'QS EX IE KLN UNKLN TB EUID RSFNC EOPMOD SERVICES'
        # numeric
        self.numeric = var.c.get('uplink', 'SID')
        # description and server info
        self.desc = var.c.get('uplink', 'description')
        self.name = var.c.get('uplink', 'host')
        self.needs_sid = var.c.get('uplink', 'needs_sid')
        # database
        self.db = var.database
        
    def __timestamp__(self):
        """ get the current time with my time.time() hack. """
        
        return int(str(time.time()).split('.')[0])
        
    def protocol_init(self):
        """ initialize protocol... """
        
        # setup events for module loading.
        self.events.command.add('LOAD', module.load, 1)
        self.events.command.add('UNLOAD', module.unload, 1)
        self.events.command.add('RELOAD', module.reload, 1)
        # clean the misc:labop_extendes permissions dict
        var.database.__refero__()['misc']['labop_extended'].clear()
        
    def protocol_close(self):
        """ close the protocol """
        
        self.events.command.delete('LOAD')
        self.events.command.delete('UNLOAD')
        self.events.command.delete('RELOAD')
        
    def negotiate(self):
        """ negotiate with the uplink and send the server introduction. """
        
        if self.needs_sid == 'False':
            self.uplink.send('PASS %s :TS' % (self.uplink.conf['password']))
        else:
            self.uses_uid = True
            self.uplink.send('PASS %s TS 6 :%s' % (self.uplink.conf['password'], self.numeric))
        self.uplink.send('CAPAB :%s' % (self.capab_msg))
        self.uplink.send('SERVER %s 1 :%s' % (self.name, self.desc))
        self.uplink.send('SVINFO %d 3 0 :%d' % (6 if self.uses_uid else 5, self.__timestamp__()))
        
        # prepare to introduce one main user and sjoin it.
        self.c = lambda value: var.c.get('main', '%s' % (value))
        nick, ident, host, gecos, channel = self.c('nick'), self.c('ident'), self.c('host'), self.c('gecos'), self.c('logchan')
        introstr = '%s!%s@%s:%s' % (nick, ident, host, gecos)
        bot = self.introduce(introstr, 'AAAABC', modes = 'S')
        bot.sjoin(channel)
            
    def parse(self):
        """ parse all incoming data
            all uplink recv calls will occur here. """
        
        try: 
            while True:
                data = eventlet.greenthread.spawn(self.uplink.connection.recv, 35000).wait()
                data = data.split('\r\n')
                for line in data:
                    try: 
                        parsed = Serialize(line)
                        if var.c.get('advanced', 'debug') == 'True' and line: logger.info('<- %s' % ('%s, %s, %s, %s' % (str(parsed.origin), parsed.command, parsed.params, parsed.longtoken)))
                        if parsed.command == 'PING' and parsed.params is None:
                            logger.debug('<- PING :%s' % (parsed.longtoken))
                            if self.bursting == True:
                                # burst is complete!
                                self.bursting = False
                                logger.debug('<- End of burst.')
                            self.pong(parsed.longtoken)
                        elif parsed.command == 'PASS':
                            self.hub = parsed.longtoken
                            var.servers.update({self.hub: {}})
                        elif parsed.command == 'SERVER':
                            var.servers.update({self.hub: {'name': parsed.params.split()[0], 'desc': parsed.longtoken, 'users': []}})
                        elif parsed.command == 'SID':
                            params = parsed.params.split()
                            var.servers.update({params[2]: {}})
                            var.servers[params[2]].update({'name': params[0], 'desc': parsed.longtoken, 'users': []})
                            self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, self.c('logchan'), "\x02new server introduced: \x0307%s [%s] {%s}" % (params[0], parsed.longtoken, params[2])))
                        elif parsed.command == 'SQUIT':
                            params = parsed.params.split()
                            name = var.servers[params[0]]['name']
                            users = var.servers[params[0]]['users']
                            self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, self.c('logchan'), "\x02!! QUITSTORMING ACTIVE: \x0307%s users dead during split with %s" % (len(users), name)))
                            logger.debug('!! QUITSTORMING ACTIVATED: %s users dead on delinked: %s' % (len(users), name))
                            [self.deluser(user) for user in users]
                            self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, self.c('logchan'), "\x02!! QUITSTORMING FINISHED: \x0307split with %s" % (name)))
                            var.servers[params[0]].clear()
                            self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, self.c('logchan'), "\x02server destroyed: \x0307%s [%s] {%s}" % (name, params[0], parsed.longtoken)))
                            del var.servers[params[0]]
                        elif parsed.command == 'EUID':
                            self.euid(str(parsed.origin), parsed.params, parsed.longtoken)
                        elif parsed.command == 'JOIN':
                            # someone joined a channel...
                            self.events.join.parse(parsed)
                            user = var.users[str(parsed.origin)]
                            logger.info('<- JOIN %s -> %s' % (user['nick'], parsed.params))
                        elif parsed.command == 'PART':
                            # someone parted a channel...
                            self.events.part.parse(parsed)
                            user = var.users[parsed.origin]
                            logger.info('<- PART %s -> %s' % (user['nick'], parsed.params))
                        elif parsed.command == 'PRIVMSG' and parsed.params in var.bots:
                            # message to service bot
                            logger.debug('<- PRIVMSG %s -> %s :%s' % (var.users[str(parsed.origin)]['nick'], var.bots[parsed.params].data['nick'], parsed.longtoken))
                            self.events.command.parse(parsed)
                            # self.events.message.parse(parsed)
                        elif parsed.command == 'QUIT':
                            # a user just quit. remove from var.users
                            self.events.quit.parse(parsed)
                            self.deluser(str(parsed.origin))
                        elif parsed.command == 'CHGHOST':
                            # someone just opered up, or theres another set of services, or an oper changed someones host.
                            bot = var.bots[var.database.getbotid(self.c('nick'))]
                            bot.privmsg(self.c('logchan'), "\x02chghost for %s [%s]:\x02\x0310 %s -> %s" % (var.users[parsed.params]['nick'], parsed.params, var.users[parsed.params]['vhost'], parsed.longtoken))
                            var.users[parsed.params]['vhost'] = parsed.longtoken
                        elif parsed.command == 'NICK':
                            bot = var.bots[var.database.getbotid(self.c('nick'))]
                            bot.privmsg(self.c('logchan'), "\x02nick change:\x02\x0310 %s -> %s" % (var.users[str(parsed.origin)]['nick'], parsed.params))
                            var.users[str(parsed.origin)]['nick'] = parsed.params
                        elif parsed.command == 'MODE':
                            self.parse_modes(parsed)
                        elif parsed.command == 'TMODE':
                            # mode changes...
                            params = parsed.params.split()
                            logger.info('mode change: %s -> %s :%s' % (params[1], params[2], parsed.longtoken))
                        elif str(parsed) == 'None,None,None,None': pass 
                    except Exception, e:
                        if var.c.get('advanced', 'warnings') == 'True': logger.warning('%s' % (traceback.format_exc(4)))
                        pass
        except (KeyboardInterrupt, SystemExit):
            self.uplink.quit('received SIGINT.')
    
    # define functions for parsing
    
    def pong(self, token):
        """ respond to a uplink ping. """
        
        logger.debug('-> PONG :%s' % (token))
        self.notice(self.c('logchan'), '\x036uplink: ping received.')
        self.uplink.send('PONG :%s' % (token))
        
    def euid(self, origin, params, token):
        """ this will parse an EUID message 
        
            format: 
              :<SID> EUID <NICK> 1 <TS> <MODES> <IDENT> <VHOST> \
               <IP> <UID> <HOST> <ACCOUNT|* if none> :<GECOS> """
        
        params = params.split()
        regstring = '%s!%s@%s [%s] {%s} (%s)' % (params[0], params[4], params[5], token, params[8], params[7])
        logger.info('<- registering: %s' % (regstring))
        bot = var.bots[var.database.getbotid(self.c('nick'))]
        bot.privmsg(self.c('logchan'), "\x02new user:\x0310 %s" % (regstring))
        host = regstring.split(' ')[0]
        users = var.users
        var.servers[origin]['users'].append(params[7])
        users.update({params[7]: {}})
        user = users[params[7]]
        user.update({'nick': params[0], 'hops': params[1], \
            'creation': params[2], 'modes': params[3], \
            'ident': params[4], 'vhost': params[5], \
            'ip': params[6], 'uid': params[7], \
            'host': params[8], 'account': params[9], \
            'gecos': token, 'asmhost': host, 'server': origin})
        # this is dependent on if TS6/chary's oper usermode /is/ +o
        if 'o' in params[3]:
            # user is an oper, let them operate labere
            var.database.__refero__()['misc']['labop_extended'].update({user['uid']: user['nick']})
            bot.privmsg(self.c('logchan'), "\x02OPER: %s (%s)" % (user['nick'], var.servers[origin]['name']))
        if self.c('welcome') == 'True':
            nn = self.c('netname')
            message = "\x02Hello, %s! This is the %s IRC network, running labere IRC services! With this package, you can register nicks and channels for safe-keeping. Please do '/msg labere HELP' for more details, and have a nice day!" % (params[0], nn)
            self.notice(params[7], message)
     
    def parse_modes(self, parsed):
        user = var.users[parsed.params]
        modes = MParse.UModeParse(parsed.longtoken)
        added, removed, params = modes.parse()
        bot = var.bots[var.database.getbotid(self.c('nick'))]
        if 'o' in added:
            bot.privmsg(self.c('logchan'), "\x02OPER: %s (%s)" % (user['nick'], var.servers[str(parsed.origin)[0:3]]['name']))
            var.database.__refero__()['misc']['labop_extended'].update({user['uid']: user['nick']})
        elif 'o' in removed:
            bot.privmsg(self.c('logchan'), "\x02DEOPER: %s (%s)" % (user['nick'], var.servers[str(parsed.origin)[0:3]]['name']))
            var.database.__refero__()['misc']['labop_extended'].pop(user['uid'])
            
    def deluser(self, uid):
        """ destroy a user that was registered in var.users """
        
        bot = var.bots[var.database.getbotid(self.c('nick'))]
        user = var.users[uid]
        if uid in var.database.__refero__()['misc']['labop_extended']:
            var.database.__refero__()['misc']['labop_extended'].pop(uid)
        bot.privmsg(self.c('logchan'), "\x02destroying user: \x034%s {%s}" % (user['asmhost'], uid))
        logger.debug('<-X deregistering %s' % (user['asmhost']))
        del user
            
    def introduce(self, service, id, modes = ''):
        """ parse the service arg, and introduce a new service bot. 
        
            use a format (nick!ident@host:gecos) and introduce a new user. """
        
        uid = self.numeric + id
        nick, ident, host, gecos = service.split('!')[0], service.split('!')[1].split('@')[0], service.split('@')[1].split(':')[0], service.split(':')[1]
        intromsg = ':%s UID %s 1 %s +%s %s %s 127.0.0.1 %s :%s' % (self.numeric, nick, self.__timestamp__(), modes, ident, host, uid, gecos)
        self.notice(self.c('logchan'), 'introducing service `%s` with id %s' % (service.split(':')[0], uid))
        logger.debug('-> %s' % (intromsg[5:]))
        self.uplink.send('%s' % (str(intromsg)))
        bot = Service(service, uid)
        return bot
        
    def privmsg(self, targetid, message):
        """ private message """
        
        self.uplink.send(':%s PRIVMSG %s :%s' % (self.numeric, targetid, message))
    
    def notice(self, targetid, message):
        """ send a service notice to a user. """
        
        self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, targetid, message))
    
class Serialize(object):
    """ serialize the line sent by the uplink. """
    
    def __init__(self, line):
        """ do everything. """
        
        self.uplink, self.events = var.core
        self.protocol = self.uplink.protocol
        self.pattern = self.protocol.pattern
        self.re = re.compile(self.pattern, re.VERBOSE)
        # self.origin, self.command, self.params, self.longtoken = None, None, None, None
        try: 
            self.raw_origin, self.command, self.params, self.longtoken = self.re.match(line).groups()
            try: self.origin = User(self.raw_origin) if len(self.raw_origin) == 9 else self.raw_origin
            except: self.origin = self.raw_origin
        except (AttributeError): 
            self.origin, self.command, self.params, self.longtoken = None, None, None, None
            pass

    def __repr__(self):
        string = "%s,%s,%s,%s" % (self.origin, self.command, self.params, self.longtoken)
        return string

class User(object):
    """ represents a user... """
    
    def __init__(self, uid):
        self.uid = uid
        self.uplink, self.events = var.core
        self.data = var.users[uid]
        self.protocol = var.protocol
        self.nick = self.data['nick']
        self.registered = var.database.userexists(self.nick)
    
    def __repr__(self):
        return "%s" % (self.uid)
        
    def privmsg(self, service, message):
        sid = self.protocol.gate().numeric
        self.uplink.send(':%s PRIVMSG %s :%s' % (service, self.uid, message))

    def notice(self, service, message):
        sid = self.protocol.gate().numeric
        self.uplink.send(':%s NOTICE %s :%s' % (service, self.uid, message))
        
    def kill(self, reason = 'Killed by labere'):
        sid = self.protocol.gate().numeric
        self.uplink.send('%s KILL %s :%s' % (sid, self.uid, message))
        self.protocol.deluser(self.uid)
        del self

class Service(object):
    """ an object to represent a service bot. """
    
    def __init__(self, service, uid):
        """ setup the bot's internals. """

        # do some stuff to make this bot known
        var.database.register_service(service, uid)
        var.bots.update({uid: self})

        # other stuff necessary for bound methods
        self.uid = uid
        self.uplink, self.events = var.core
        self.protocol = var.protocol
        self.hub = self.protocol.gate().numeric
        self.data = {
            'nick': service.split('!')[0],
            'ident': service.split('!')[1].split('@')[0],
            'host': service.split('@')[1].split(':')[0],
            'gecos': service.split(':')[1] }
        self.hash = var.database.__refero__()['misc']['bots'][self.data['nick']]
        self.creation = int(str(time.time()).split('.')[0])
    
    def __timestamp__(self):
        """ get the current time with my time.time() hack. """
        
        return int(str(time.time()).split('.')[0])
        
    def privmsg(self, targetid, message):
        """ send a private message """
        
        self.uplink.send(':%s PRIVMSG %s :%s' % (self.uid, targetid, message))
        
    def notice(self, targetid, message):
        """ send a notice """
        
        self.uplink.send(':%s NOTICE %s :%s' % (self.uid, targetid, message))
    
    def op(self, channel):
        """ op myself in channel """
        
        self.uplink.send('%s MODE %s +o %s' % (self.hub, channel, self.uid))
    
    def mode(self, target, modes, targetid = None):
        """ set modes. """
        
        if not targetid:
            self.uplink.send(':%s MODE %s %s' % (self.hub, target, modes))
        elif targetid:
            self.uplink.send(':%s MODE %s %s %s' % (self.hub, target, modes, targetid))
    
    def sjoin(self, channel):
        """ implemented sjoin, joins services bot to a channel after its introduced. """
        
        sjoinmsg = ':%s SJOIN %s %s + :%s' % (self.hub, self.__timestamp__(), channel, self.uid)
        logger.debug('-> %s' % (sjoinmsg[5:]))
        self.uplink.send('%s' % (str(sjoinmsg)))
        self.mode(channel, '+o', self.uid)
        self.hash['channels'].append(str(channel))
