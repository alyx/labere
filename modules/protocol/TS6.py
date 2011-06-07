#!/usr/bin/env python

from core import var, logger
import time

class Protocol(object):
    """ TS6 protocol class """
    
    def __init__(self):
        """ config crap and initialize some variables """
        
        # uplink
        self.uplink = var.uplink
        # what we're going to send for CAPAB
        self.capab_msg = 'QS EX IE KLN UNKLN TB SERVICES EUID EOPMOD MLOCK'
        # numeric
        self.numeric = var.c.get('uplink', 'SID')
        # description and server info
        self.desc = var.c.get('uplink', 'description')
        self.name = var.c.get('uplink', 'host')
        self.needs_sid = var.c.get('uplink', 'needs_sid')

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
        self.uplink.send('SVINFO %d 3 0 :%d' % (6 if self.uses_uid else 5, int(str(time.time()).split('.')[0])))
        
    def parse(self):
        """ parse all incoming data """
        
        pass
    
    def introduce(self, service):
        """ parse the service arg, and introduce a new service bot. """
        
        pass