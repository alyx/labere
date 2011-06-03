#!/usr/bin/env python

import eventlet, var, logger, ConfigParser

class parsercore:
    def __init__(self):
        self.c = ConfigParser.ConfigParser()
        ck = self.c.read('etc/labere.conf')
        if not ck:
            logger.critical('labere configuration file is non-existant!')
            logger.critical('please rename etc/labere.conf.example to' + \
                           ' etc/labere.conf and configure it.')
            exit(1)
            
    def __repr__(self):
        return "<labere.config <%s>>" % (self.c)
    
    __str__ = __repr__
        
    def __refero__(self):
        return self.c

    def get(self, section, value, quiet = True):
        try:
            if quiet is False: logger.info('CONFIG: fetching %s::%s' % (section, value))
            configpair = self.c.get(section, value)
        except: 
            logger.error('CONFIG: could not get %s::%s' % (section, value))
            configpair = None
        finally:
            return configpair