#!/usr/bin/env python

import shelve, os, logger, hashlib, time

"""  this implements the first revision of pirogoeth's database
     storage structure and format.
     
     for those wondering, the proposal is at ../docs/database.txt  """
     
class database(object):
    """ handle the database with care: it may be fragile. """
    def __init__(self):
        self._db = shelve.open('etc/labere._db', writeback = True) # writeback always needs to be true for any case here...
        if self._db == {}:
            logger.info('labere._db is non-existent! creating...')
            self.initialize_db()
    
    def __repr__(self):
        return "<labere.database>"
        
    __str__ == __repr__
    
    def initialize_db(self):
        """ initialize the db for the very first time... """
        self._db.update({'users': {}, 'channels': {}, 'misc': {}})
        self._db['misc'].update({'service_bots': {}, 'services_settings': {}, 'labop_extended': {}})
    
    def close_db(self):
        """ close the db safely... """
        self._db.sync()
        self._db.close()
        
    def sync_db(self):
        """ sync the database... """
        self._db.sync()
        
    def register_user(self, username, password):
        """ register a user in the database and create all the
            necessary metadata 
            
            we're also using apscheduler for verification helping
            if so specified in the config
            
            ^^ not going to worry about this now, but later. """
        userdb = {}
        creation = int(str(time.time()).split('.')[0])
        userdb.update({'data': {}, 'metadata': {}, 'flags': {}})
        userdb['data'].update({'acname': username, \
            'password': hashlib.md5().update(password).hexdigest(), \
            'grouped': []})
        userdb['metadata'].update({'regtime': int(creation), \
            'email': None, \
            'soper': False})
        userdb['flags'].update({'private': False, \
            'hidemail': True})
        self._db['users'].update({username: userdb})
        del userdb
        self.sync_db()