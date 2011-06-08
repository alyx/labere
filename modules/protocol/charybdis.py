#!/usr/bin/env python

from core import var, logger, database, protocol
import time, eventlet, re, traceback

class Protocol(object):
    """ TS6 protocol class """
    
    def __init__(self):
        """ config crap and initialize some variables """
        
        # uplink
        self.uplink = var.uplink
        self.protocol = var.uplink.protocol
        # what we're going to send for CAPAB
        self.capab_msg = 'QS EX IE KLN UNKLN TB SERVICES EUID EOPMOD MLOCK'
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
        
        pass
        
    def protocol_close(self):
        """ close the protocol """
        
        pass
        
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
        self.introduce(introstr, 'AAAABC', modes = 'S')
        self.sjoin(nick, channel)
            
    def parse(self):
        """ parse all incoming data
            all uplink recv calls will occur here. """
        
        try: 
            while True:
                data = eventlet.greenthread.spawn(self.uplink.connection.recv, 31337).wait()
                data = data.split('\r\n')
                for line in data:
                    try: 
                        parsed = Serialize(line)
                        if var.c.get('advanced', 'debug') == 'True' and line: logger.info('<- %s' % ('%s, %s, %s, %s' % (parsed.origin, parsed.command, parsed.params, parsed.longtoken)))
                        if parsed.command == 'PING' and parsed.params is None:
                            logger.debug('<- PING :%s' % (parsed.longtoken))
                            self.pong(parsed.longtoken)
                        elif parsed.command == 'EUID':
                            logger.debug('<- registering :%s' % (parsed.longtoken))
                            self.euid(parsed.params, parsed.longtoken)
                        elif parsed.command == 'PRIVMSG' and parsed.params not in var.bots:
                            # channel message
                            logger.debug('<- PRIVMSG %s:%s :%s' % (var.users[parsed.origin]['nick'], parsed.params, parsed.longtoken))
                        elif parsed.command == 'PRIVMSG' and parsed.params in var.bots:
                            # message to service bot
                            self.privmsg(parsed.params, parsed.origin, 'UNKNOWN')
                            logger.debug('<- PRIVMSG %s->%s :s' % (var.users[parsed.origin]['nick'], var.bots[parsed.params], parsed.longtoken))
                    except:
                        # logger.warning('%s' % (traceback.format_exc(4)))
                        pass
        except (KeyboardInterrupt, SystemExit):
            self.uplink.quit('received SIGINT.')
    
    # define functions for parsing
    
    def pong(self, token):
        """ respond to a uplink ping. """
        
        logger.debug('-> PONG :%s' % (token))
        self.uplink.send('PONG :%s' % (token))
        
    def euid(self, params, token):
        """ this will parse an EUID message 
        
            format: 
              :<SID> EUID <NICK> 1 <TS> <MODES> <IDENT> <VHOST> \
               <IP> <UID> <HOST> <ACCOUNT|* if none> :<GECOS> """
        
        params = params.split()
        users = var.users
        users.update({params[7]: {}})
        user = users[params[7]]
        user.update({'nick': params[0], 'hops': params[1], \
            'creation': params[2], 'modes': params[3], \
            'ident': params[4], 'vhost': params[5], \
            'ip': params[6], 'uid': params[7], \
            'host': params[8], 'account': params[9], \
            'gecos': token})
        if self.c('welcome') == 'True':
            nn = self.c('netname')
            message = "\x02Hello, %s! This is the %s IRC network, running labere IRC services! With this package, you can register nicks and channels for safe-keeping. Please do '/msg labere HELP' for more details, and have a nice day!" % (params[0], nn)
            self.notice(params[7], message)
    def introduce(self, service, id, modes = ''):
        """ parse the service arg, and introduce a new service bot. 
        
            use a format (nick!ident@host:gecos) and introduce a new user. """
        
        uid = self.numeric + id
        nick, ident, host, gecos = service.split('!')[0], service.split('!')[1].split('@')[0], service.split('@')[1].split(':')[0], service.split(':')[1]
        intromsg = ':%s UID %s 1 %s +%s %s %s 127.0.0.1 %s :%s' % (self.numeric, nick, self.__timestamp__(), modes, ident, host, uid, gecos)
        logger.debug('-> %s' % (intromsg[5:]))
        self.uplink.send('%s' % (str(intromsg)))
        self.db.register_service(service, uid)
        var.bots.update({uid: nick})
        
    def privmsg(self, uid, targetid, message):
        """ private message """
        
        if uid not in var.bots:
            try: uid = self.db.__refero__()['misc']['bots'][uid]['uid']
            except: return False
        else: 
            self.uplink.send(':%s PRIVMSG %s :%s' % (uid, targetid, message))
            return False
        if uid not in var.bots:
            # uid is not there.
            return False
        else:
            self.uplink.send(':%s PRIVMSG %s :%s' % (uid, targetid, message))
            return False
    
    def notice(self, targetid, message):
        """ send a service notice to a user. """
        
        self.uplink.send(':%s NOTICE %s :%s' % (self.numeric, targetid, message))
    
    def sjoin(self, service, channel):
        """ implemented sjoin, joins services bot to a channel after its introduced. """
        
        if service not in self.db.__refero__()['misc']['bots']:
            raise protocol.ProtocolError('Service bot %s does not exist.' % (service))
        uid = self.db.__refero__()['misc']['bots'][service]['uid']
        sjoinmsg = ':%s SJOIN %s %s +nt :%s' % (self.numeric, self.__timestamp__(), channel, uid)
        logger.debug('-> %s' % (sjoinmsg[5:]))
        self.uplink.send('%s' % (str(sjoinmsg)))
        self.db.__refero__()['misc']['bots'][service]['channels'].append(str(channel))
        
class Serialize(object):
    """ serialize the line sent by the uplink. """
    
    def __init__(self, line):
        """ do everything. """
        
        self.protocol = var.uplink.protocol
        self.pattern = self.protocol.pattern
        self.re = re.compile(self.pattern, re.VERBOSE)
        try: 
            self.origin, self.command, self.params, self.longtoken = self.re.match(line).groups()
        except (AttributeError): 
            pass
        