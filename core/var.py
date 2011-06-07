#!/usr/bin/env python

import config, logger, database

""" this module is here only to store various things that necessary 
    to the runtime functions of the services package. """
    
help = {}
modules = {}
Configuration = {}
c = config.parsercore()

users = {'uid': {}, 'users': {}}

def get_config():
    global Configuration
    Configuration = {
        # uplink
        'server': c.get('uplink', 'server'),
        'port': c.get('uplink', 'port'),
        'password': c.get('uplink', 'password'),
        'ssl': c.get('uplink', 'ssl'),
        'protocol': c.get('uplink', 'protocol'),
        # main
        'nick': c.get('main', 'nick'),
        'ident': c.get('main', 'ident'),
        'gecos': c.get('main', 'gecos'),
        'host': c.get('main', 'host'),
        # advanced
        'fork': c.get('advanced', 'fork'),
        # logging
        'loglevel': c.get('logging', 'loglevel'),
        'logfile': c.get('logging', 'file')
    }

def setup_logger():
    logger.init()
    
get_config()
setup_logger()