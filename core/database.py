#!/usr/bin/env python

import shelve, os, logger, hashlib, time, var, traceback

"""  this implements the first revision of pirogoeth's database
     storage structure and format.
     
     for those wondering, the proposal is at ../docs/database.txt  """
     
class Database(object):
    """ handle the database with care: it may be fragile. """
    
    def __init__(self):
        
        self._db = shelve.open('etc/labere.db', writeback = True) # writeback always needs to be true for any case here...
        if self._db == {}:
            logger.info('labere.db is non-existent! creating...')
            self.initialize_db()
    
    def __repr__(self):
        return "<labere.database>"
        
    __str__ = __repr__
    
    def __refero__(self):
        """ return the database instance so that settings and such
            can be modified on user requests. """
        
        return self._db
    
    def initialize_db(self):
        """ initialize the db for the very first time... """
        
        self._db.update({'users': {}, 'channels': {}, 'misc': {}})
        self._db['misc'].update({'bots': {}, 'services_settings': {}, 'labop_extended': {}})
    
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
            
            ^^ handling for this will be inside the registration
               handlers, only because it makes sense. """
        
        self._db['users'].update({username: {}})
        userdb = self._db['users'][username]
        q = hashlib.md5()
        q.update(password)
        creation = int(str(time.time()).split('.')[0])
        userdb.update({'data': {}, 'metadata': {}, 'flags': {}, 'channels': []})
        userdb['data'].update({'acname': username, \
            'password': q.hexdigest(), \
            'grouped': []})
        userdb['metadata'].update({'regtime': int(creation), \
            'email': None, \
            'soper': False})
        userdb['flags'].update({'private': False, \
            'hidemail': True})
        del q
        # i dont think we should sync after ever user registration... it makes it slower.
        #  self.sync_db()
        
    def deregister_user(self, username):
        """ deregister a user from the database, for a DROP or FDROP
            a soper. """
        
        prerm = []
        for channel, cdata in self._db['channels'].iteritems():
             if cdata['metadata']['owner'] == username:
                 prerm.append(channel)
             else: pass
        [self.deregister_channel(channel) for channel in prerm]
        self._db['users'][username].clear()
        del self._db['users'][username], prerm
        # i dont think we should sync after ever user deregistration...it slows things down
        #  self.sync_db()
        
    def register_channel(self, channel, password, user, description = None):
        """ register a channel according to the labere database
            proposal in docs/database.txt """
        
        self._db['channels'].update({channel: {}})
        chandb = self._db['channels'][channel]
        q = hashlib.md5()
        q.update(password)
        creation = int(str(time.time()).split('.')[0])
        chandb.update({'flags': {}, 'metadata': {}, 'settings': {}, \
            'topic': ''})
        chandb['flags'].update({str(user): ['f', 'o', 't', 'p']})
        chandb['metadata'].update({'owner': user, \
            'password': q.hexdigest(), \
            'regtime': int(creation), \
            'email': str(self._db['users'][user]['metadata']['email']), \
            'mlock_def': '+nt'}) # default mlock mode
        chandb['settings'].update({'keeptopic': True, \
            'mlock': False, \
            'fantasy': True, \
            'f_prefix': '.'})
        chandb['topic'] = []
        self._db['users'][user]['channels'].append(channel)
        del q
        # i dont think we should sync after ever channel registration...it slows things down
        #  self.sync_db()
    
    def deregister_channel(self, channel):
        """ deregister a user's channel from a DROP or a soper's FDROP. """
        
        user = self._db['channels'][channel]['metadata']['owner']
        self._db['users'][user]['channels'].remove(channel)
        self._db['channels'][channel].clear()
        del self._db['channels'][channel], user
        # i dont think we should sync after ever channel deregistration...it slows things down
        #  self.sync_db()
    
    # important stuff with service bots
    
    def register_service(self, service, uid):
        """ register a service bot in the db. should be called during
            protocol.introduce() """
        
        nick, ident, host, gecos = service.split('!')[0], service.split('!')[1].split('@')[0], service.split('@')[1].split(':')[0], service.split(':')[1]
        self._db['misc']['bots'].update({nick: {}})
        botdb = self._db['misc']['bots'][nick]
        botdb.update({'channels': [], 'metadata': {}, 'uid': uid})
        botdb['metadata'].update({'nick': nick, 'ident': ident, 'host': host, 'gecos': gecos, 'regtime': int(str(time.time()).split('.')[0])})
    
    def deregister_service(self, service):
        """ deregister a service bot. we only need the nick. """
        
        self._db['misc']['bots'][nick].clear()
        del self._db['misc']['bots'][nick]
    
    def getbotid(self, service):
        """ get the bots UID from its nick. """
        
        return self._db['misc']['bots'][service]['uid']