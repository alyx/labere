#!/usr/bin/env python

import eventlet, logger, var, protocol, random
from eventlet.green import socket, os, ssl

class Uplink(object):
    """ begin the connection to the upstream server """
    
    def __init__(self):
        """ initialize a bunch of config crap. """
        
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
        var.uplink = self
    
    def connect(self):
        """ connect to the upstream. """
        
        self.connection.bind((self.conf['bind'], int(random.randint(50000, 60000))))
        self.connection.connect((str(self.conf['server']), int(self.conf['port'])))
    
    def send(self, data):
        """ send raw data to the uplink. """
        
        data = data + '\r\n'
        self.connection.send(data)