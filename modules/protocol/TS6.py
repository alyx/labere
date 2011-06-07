#!/usr/bin/env python

from core import var, logger, database
import time, eventlet, re

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
    
    def parse(self):
        """ parse all incoming data
            all uplink recv calls will occur here. """
        
        try: 
            self.pattern = self.protocol.pattern
            sub = re.compile(self.pattern, re.VERBOSE)
            while True:
                data = eventlet.greenthread.spawn(self.uplink.connection.recv, 31337).wait()
                data = data.split('\r\n')
                for line in data:
                    try: line = sub.match(line).groups()
                    except (AttributeError): pass
                    if var.c.get('advanced', 'debug') == 'True' and line: logger.info('<- %s' % (line))
        except (KeyboardInterrupt, SystemExit):
            self.uplink.quit('received SIGINT.')
    
    def introduce(self, service, id, modes = ''):
        """ parse the service arg, and introduce a new service bot. 
        
            use a format (nick!ident@host:gecos) and introduce a new user. """
        
        uid = self.numeric + id
        nick, ident, host, gecos = service.split('!')[0], service.split('!')[1].split('@')[0], service.split('@')[1].split(':')[0], service.split(':')[1]
        intromsg = ':%s UID %s 1 %s +%s %s %s 127.0.0.1 %s :%s' % (self.numeric, nick, self.__timestamp__(), modes, ident, host, uid, gecos)
        self.uplink.send('%s' % (str(intromsg)))
        self.db.register_service(service, uid)
        
    def sjoin(self, service, channel):
        """ implemented sjoin, joins services bot to a channel after its introduced. """
        
        if service not in self.db.__refero__()['misc']['service_bots']:
            raise ProtocolError('Service bot %s does not exist.' % (service))
        uid = self.db.__refero__()['misc']['service_bots'][service]['uid']
        sjoinmsg = ':%s SJOIN %s %s +nt :%s' % (self.numeric, self.__timestamp__(), channel, uid)
        self.uplink.send('%s' % (str(sjoinmsg)))
        self.db.__refero__()['misc']['service_bots'][service]['channels'].append(str(channel))