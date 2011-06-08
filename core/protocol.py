#!/usr/bin/env python

import eventlet, os, time, datetime, var, logger, imp, warnings
from imp import load_source
from eventlet.green import socket

class ProtocolError(Exception):
    def __init__(self, error):
        self.error = error
    def __str__(self):
        return repr(self.error)

class Protocol(object):
    """  protocol wrapper
           protocol modules should use this model
           to correctly handle events. """
    
    def __init__(self):
        """ initialize the connection objects
            do NOT overwrite this """
        
        # is a protocol module loaded?
        
        self.proto_loaded = False
        
        # default re
        
        self.pattern = '^(?:\:(\S+)\s)?(\S+)\s(?:([^:]+)\s)?(?:\:(.+)?)?$'
    
    def __repr__(self):
        """ change representation. """
        
        return '<labere.protocol <%s>>' % (var.c.get('uplink', 'protocol'))

    def load_protocol(self):
        """ hook a protocol module into the framework """
        
        modu = var.c.get('uplink', 'protocol')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
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
        logger.info('protocol: loaded %s' % (self.mod.__name__))
        self.proto_loaded = True

    def loaded(self):
        """ is loaded? """
        
        return self.proto_loaded
    
    def unload(self):
        """ unload the protocol module """

        self.protocol.protocol_close()
        logger.info('protocol: unloaded %s' % (self.mod.__name__))
        self.proto_loaded = False
        
    def negotiate(self):
        """ negotiatiate with the uplink """
        
        if not self.proto_loaded:
            raise ProtocolError('No protocol module loaded.')
        elif self.proto_loaded:
            self.protocol.negotiate()
    
    def parse(self):
        """ parse data coming from the uplink """
        
        if not self.proto_loaded:
            raise ProtocolError('No protocol module loaded.')
        elif self.proto_loaded:
            self.protocol.parse()
        
    def introduce(self, service, id = None, modes = ''):
        """ this is a little different. service is going to be a tuple
            or possibly a dict. not sure. unless its simply a sort of
            thing that gets split up..(nick!ident@host:gecos)
            this user that gets introduced is most likely a service
            bot, so in the actual protocol, it needs to be written to
            the database """
        
        if not self.proto_loaded:
            raise ProtocolError('No protocol module loaded.')
        elif self.proto_loaded:
            if self.protocol.uses_uid is True:
                self.protocol.introduce(service, id, modes = modes)
            else:
                self.protocol.introduce(service, modes = modes)
            
    def gate(self):
        """ gateway to speaking directly to the protocol module without having
            to have a definition here. """
            
        return self.protocol