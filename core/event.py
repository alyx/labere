#!/usr/bin/env python

import logger, var, traceback, rfc, eventlet

class Commands(object):
    def __init__(self):
        var.help = {}
    def add(self, command, function):
        var.commands.update({command: function})
        var.help.update({command: getattr(function, '__doc__', 'No help available for %s' % (command))})
    def delete(self, command):
        var.commands.pop(command)
        var.help.pop(command)
    def parse(self, msg):
        line = msg.message.split()
        command = line[0]
        try: args = " ".join(line[1:])
        except: pass
        try:
            if command in var.commands:
                f = var.commands[command]
                try:
                    if args:
                        try: f(msg, args)
                        except: 
                            logger.info('commands.parse(): magical function error? (%s)' % (f))
                            logger.info('%s' % (traceback.format_exc(4)))
                            # [msg.target.privmsg('%s' % (tb)) for tb in traceback.format_exc(1).split('\n')]
                            pass
                    elif not args:
                        try: f(msg)
                        except: 
                            logger.info('commands.parse(): magical function error? (%s)' % (f))
                            logger.info('%s' % (traceback.format_exc(4)))
                            # [msg.target.privmsg('%s' % (tb)) for tb in traceback.format_exc(1).split('\n')]
                            pass
                except (RuntimeWarning): pass
        except:
            [logger.error('%s' % (tb)) for tb in traceback.format_exc(5).split('\n')]
class Message(object):
    def __init__(self):
        pass
    def add(self, hook, function):
        var.hooks.update({function: hook})
    def delete(self, function):
        var.hooks.pop(function)
    def parse(self, msg):
        line = msg.message.split()
        try: args = " ".join(line[0:])
        except: pass
        try:
            for function, message in var.hooks.iteritems():
                if message in msg.message:
                    try: function(msg)
                    except:
                        logger.error('hooking.parse(): magical function error? (%s)' % (function))
                        logger.info('%s' % (traceback.format_exc(1)))
                        # [msg.target.privmsg('%s' % (tb)) for tb in traceback.format_exc(1)]
                        return False
                else:
                    pass
        except:
            logger.info('hooking.parse(): error in hooking loop')
            pass
class Channel(object):
    class Join(object):
        def __init__(self):
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            uplink, events = var.uplink, var.events
            try:
                logger.debug('channel.join(): processing join event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.join(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]
            finally:
                self._lock.release()
    class part(object):
        def __init__(self):
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            uplink, events = var.uplink, var.events
            try:
                self._lock.acquire()
                logger.debug('channel.part(): processing part event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.part(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]
            finally:
                self._lock.release()
    class kick(object):
        def __init__(self):
            self._lock = threading.Lock()
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            conn, h = var.core
            try:
                self._lock.acquire()
                logger.debug('channel.kick(): processing kick event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.kick(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]
            finally:
                self._lock.release()
    class quit(object):
        def __init__(self):
            self._lock = threading.Lock()
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            conn, h = var.core
            try:
                self._lock.acquire()
                logger.debug('channel.quit(): processing quit event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.quit(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]
            finally:
                self._lock.release()
class rfc(object):
   def __init__(self):
       self._lock = threading.Lock()
       self.processors = {}
   def add(self, numeric, function):
       self.processors.update({function: numeric})
   def delete(self, function):
       self.processors.__delitem__(function)
   def parse(self, msg):
       conn, events = var.core
       if msg.type.get_type() != 'rfc_num':
           return False
       try:
           self._lock.acquire()
           for function, rfc_numeric in self.processors.iteritems():
               if str(msg.type) == rfc_numeric: 
                   try: function(msg)
                   except: 
                       [logger.error(tb) for tb in traceback.format_exc(2).split('\n')]
       finally:
           self._lock.release()