#!/usr/bin/env python

import eventlet, logger, var, protocol, random, database, event
from eventlet.green import socket, os, ssl
from protocol import ProtocolError

class Uplink(object):
    """ begin the connection to the upstream server """
    
    def __init__(self):
        """ initialize a bunch of config crap. """

        logger.info('initializing uplink and protocol..')        
        self.protocol = protocol.Protocol()
        self.conf = {
            'server': var.Configuration['server'],
            'port': int(var.Configuration['port']),
            'ssl': var.Configuration['ssl'],
            'password': var.Configuration['password'],
            'host': var.c.get('uplink', 'host'),
            'bind': var.c.get('main', 'bind'),
            'serverid': var.c.get('uplink', 'SID'),
            'mnick': var.Configuration['nick'],
            'mident': var.Configuration['ident'],
            'mgecos': var.Configuration['gecos'],
            'mhost': var.Configuration['host'] }
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ssl and self.conf['ssl'] == 'True':
            self.connection = ssl.wrap_socket(self.socket)
            logger.info('<-> connection type: ssl')
        else:
            self.connection = self.socket
            logger.info('<-> conection type: plain')
        var.core = ((self, event.Events()))
        var.protocol = self.protocol
        var.database = database.Database()

    def __repr__(self):
        """ represent, brother. """
        
        return '<labere.uplink <%s>>' % (self.conf['host'])
    
    def connect(self):
        """ connect to the upstream. """
        
        if self.protocol.loaded() is False:
            raise ProtocolError('No protocol module loaded.')
        elif self.protocol.loaded() is True:
            self.connection.bind((self.conf['bind'], int(random.randint(50000, 60000))))
            logger.debug('<- bound to %s' % (self.conf['bind']))
            self.connection.connect((str(self.conf['server']), int(self.conf['port'])))
            logger.debug('-> connected to %s' % (self.conf['server']))
            self.uplink_id = '00A' if var.c.get('uplink', 'needs_sid') == 'True' else None
    
    def send(self, data):
        """ send raw data to the uplink. """
        
        data = data + '\r\n'
        self.connection.send(data)
        
    def quit(self, reason):
        """ squit away from the hub and die """
        
        self.send('WALLOPS :shutting down: %s' % (reason))
        var.database.sync_db()
        var.database.close_db()
        self.send('WALLOPS :synchronised database, shutting down..')
        self.send(':%s SQUIT %s :%s' % (self.protocol.gate().numeric, self.conf['host'], reason))
        self.protocol.unload()
        exit()