#!/usr/bin/env python

import logger, var, traceback, eventlet, apscheduler
from apscheduler import scheduler

class Command(object):

    def __init__(self):
        var.help = {}
        var.commands = {}
    def add(self, command, function, permission = 0):
        var.commands.update({command: function})
        var.help.update({command: {'f': getattr(function, '__doc__', 'No help available for %s' % (command)), 'p': permission}})
    def delete(self, command):
        var.commands.pop(command)
        var.help.pop(command)
    def parse(self, msg):
        line = msg.longtoken.split()
        command = line[0]
        try: args = " ".join(line[1:])
        except: pass
        try:
            if command in var.commands or command.upper() in var.commands or command.lower() in var.commands:
                try:
                    try:
                        f = var.commands[command]
                    except:
                        f = var.commands[command.upper()]
                except:
                    f = var.commands[command.lower()]
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
        line = msg.longtoken.split()
        try: args = " ".join(line[0:])
        except: pass
        try:
            for function, message in var.hooks.iteritems():
                if message in msg.longtoken:
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
            uplink, events = var.core
            try:
                logger.debug('channel.join(): processing join event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.join(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]

    class Part(object):
        def __init__(self):
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            uplink, events = var.core
            try:
                logger.debug('channel.part(): processing part event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.part(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]

    class Kick(object):
        def __init__(self):
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            uplink, events = var.core
            try:
                logger.debug('channel.kick(): processing kick event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.kick(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]
    class Quit(object):
        def __init__(self):
            self.channels = []
        def add(self, function):
            self.channels.append(function)
        def delete(self, function):
            self.channels.remove(function)
        def parse(self, msg):
            uplink, events = var.core
            try:
                logger.debug('channel.quit(): processing quit event')
                [function(msg) for function in self.channels]
            except:
                logger.info('channel.quit(): magical function error.')
                logger.info('traceback: %s' % \
                     (traceback.format_exc(1)))
                # [msg.target.privmsg('%s' % (tb)) \
                #     for tb in traceback.format_exc(1).split('\n')]

class Modules(object):
    """ handles onmodload, onmodunload, and onmodreload """
    
    class modloaded(object):
        """ module was loaded """
        def __init__(self):
            self.handlers = []
        def add(self, f):
            self.handlers.append(f)
        def delete(self, f):
            self.handlers.remove(f)
        def parse(self, module):
            try:
                [f(module) for f in self.handlers]
            except: logger.warning('%s' % (traceback.format_exc(4)))

    class modunloaded(object):
        """ module was unloaded """
        def __init__(self):
            self.handlers = []
        def add(self, f):
            self.handlers.append(f)
        def delete(self, f):
            self.handlers.remove(f)
        def parse(self, module):
            try:
                [f(module) for f in self.handlers]
            except:  logger.warning('%s' % (traceback.format_exc(4))) 
   
    class modreloaded(object):
        """ module was reloaded """
        def __init__(self):
            self.handlers = []
        def add(self, f):
            self.handlers.append(f)
        def delete(self, f):
            self.handlers.remove(f)
        def parse(self, module):
            try:
                [f(module) for f in self.handlers]
            except: logger.warning('%s' % (traceback.format_exc(4)))

class Events(object):
    def __init__(self):
        self.command = Command()
        self.message = Message()
        self.kick = Channel().Kick()
        self.join = Channel().Join()
        self.part = Channel().Part()
        self.quit = Channel().Quit()
        self.scheduler = scheduler.Scheduler()
        self.onmodload = Modules().modloaded()
        self.onmodreload = Modules().modreloaded()
        self.onmodunload = Modules().modunloaded()