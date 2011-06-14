#!/usr/bin/env python

from core import var, logger

uplink, events = var.core

def init(msg):
    events.command.add('HELP', help)
def close(msg):
    events.command.delete('HELP')
    
def help(msg, args = None):
    """ displays help for various bot commands. """
    bot = var.bots[msg.params]
    oper = str(msg.origin) in var.database.__refero__()['misc']['labop_extended']
    if args is None:
        bot.privmsg(str(msg.origin), "\x02The following commands are available:\x02")
        for ob, hash in var.help.iteritems():
            if hash['p'] == 1:
                if oper is True:
                    message = " \x02%s\x02  %s" % (ob, hash['f'])
                else: message = ""
            elif hash['p'] == 0:
                message = " \x02%s\x02  %s" % (ob, hash['f'])
            bot.privmsg(str(msg.origin), message)
    elif args:
        command = args.split()[0]
        if command.upper() in var.help or command.lower() in var.help or command in var.help:
            try:
                try: 
                    doc = var.help[command]['f']
                    command = command
                except: 
                    doc = var.help[command.upper()]['f']
                    command = command.upper()
            except: 
                doc = var.help[command.lower()]['f']
                command = command.lower()
            bot.privmsg(str(msg.origin), " \x02%s\x02:" % (command))
            [bot.privmsg(str(msg.origin), line) for line in var.help[command]['f'].split('\n')]
        else:
            bot.privmsg(str(msg.origin), " \x02%s\x02 is non-existent." % (command))
            return False