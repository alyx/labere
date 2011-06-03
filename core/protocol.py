#!/usr/bin/env python

import eventlet, os, time, datetime, var, logger
from eventlet.green import socket

class Protocol(object):
    """  protocol wrapper
           protocol modules should use this model
           to correctly handle events. """
    
    def __init__(self, conn):
        """ initialize the connection objects
            do NOT overwrite this """
        
        self.conn = conn
        
        # protocol options
        
        self.uid = False
        self.euid = False
        self.rserv = False
        self.tburst = False
        self.eopmod = False
        self.mlock = False
        
        # default re
        
        self.pattern = "^(?:\:([^\s]+)\s)?([A-Za-z0-9]+)\s(?:([^\s\:]+)\s)?(?:\:?(.*))?$" 
    
    def modes(self):
        """ set the modes usable by the protocol
              overwrite this function """
              
        pass
        
    def negotiate(self):
        """ negotiate with the server
              overwrite this function """
 
        pass
    
    def parse(self, data):
        """ parse incoming server data
              overwrite this function """
              
        pass