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
        'loglevel': c.get('logging', 'loglevel'),
        'fork': c.get('advanced', 'fork'),
        'logfile': c.get('logging', 'file')
    }

def setup_logger():
    logger.init()