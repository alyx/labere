#!/usr/bin/env python

import eventlet, os, time, datetime, var, logger, imp
from imp import load_source
from eventlet.green import socket

class Protocol(object):
    """  protocol wrapper
           protocol modules should use this model
           to correctly handle events. """
    
    def __init__(self):
        """ initialize the connection objects
            do NOT overwrite this """
        
        # protocol options
        
        self.uid = False
        self.euid = False
        self.rserv = False
        self.tburst = False
        self.eopmod = False
        self.mlock = False
        
        # default re
        
        self.pattern = "^(?:\:([^\s]+)\s)?([A-Za-z0-9]+)\s(?:([^\s\:]+)\s)?(?:\:?(.*))?$" 
    
    def load_protocol(self):
        modu = var.c.get('uplink', 'protocol')
        self.mod = load_source(modu, modu)
        self.protocol = self.mod.Protocol()
        if not hasattr(self.protocol, 'negotiate'):
            logger.critical('protocol: invalid protocol module: missing negotiation block')
            exit(1)
        if not hasattr(self.protocol, 'parse'):
            logger.critical('protocol: invalid protocol module: missing parse block')
            exit(1)
        if not hasattr(self.protocol, 'introduce'):
            logger.critical('protocol: invalid protocol module: missing introduce block')
            exit(1)
        if not hasattr(self.protocol, 'protocol_init'):
            logger.critical('protocol: invalid protocol module: missing protocol_init block')
            exit(1)
        if not hasattr(self.protocol, 'protocol_close'):
            logger.critical('protocol: invalid protocol module: missing protocol_close block')
            exit(1)
        self.protocol.protocol_init()
        logger.init('protocol: loaded %s' % (self.mod.protocol_info))
        
    def unload(self):
        self.protocol.protocol_close()
        logger.init('protocol: unloaded %s' % (self.mod.__name__))
    
    def negotiate(self):
        """ negotiatiate with the uplink """
        
        self.protocol.negotiate()
    
    def parse(self, data):
        """ parse data coming from the uplink """
        
        self.protocol.parse(data)
        
    def introduce(self, service):
        """ this is a little different. service is going to be a tuple
            or possibly a dict. not sure. unless its simply a sort of
            thing that gets split up..(nick!ident@host:gecos)
            this user that gets introduced is most likely a service
            bot, so in the actual protocol, it needs to be written to
            the database """
        
        self.protocol.introduce(service)