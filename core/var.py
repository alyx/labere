#!/usr/bin/env python

import config, logger

""" this module is here only to store various things that necessary 
    to the runtime functions of the services package. """
    
help = {}
modules = {}
Configuration = {}

c = config.parsercore()

def get_config():
    global Configuration
    Configuration = {
        # uplink
        'server': var.c.get('uplink', 'server'),
        'port': var.c.get('uplink', 'port'),
        'password': var.c.get('uplink', 'password'),
        'ssl': var.c.get('uplink', 'ssl'),
        'protocol': var.c.get('uplink', 'protocol'),
        # main
        'nick': var.c.get('main', 'nick'),
        'ident': var.c.get('main', 'ident'),
        'gecos': var.c.get('main', 'gecos'),
        'host': var.c.get('main', 'host'),
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