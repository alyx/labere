#!/usr/bin/env python

from core import var, logger

uplink, events = var.core
protocol = var.protocol
database = var.database
config = lambda section, item: var.c.get(section, item)

def init(msg):
    var.failed_logins = {}
    events.command.add('REGISTER', register)
    events.command.add('LOGIN', login)
    events.command.add('IDENTIFY', identify)
    events.command.add('LOGOUT', logout)
    events.command.add('GROUP', group)
    events.command.add('UNGROUP', ungroup)

def close(msg):
    events.command.delete('REGISTER')
    events.command.delete('LOGIN')
    events.command.delete('IDENTIFY')
    events.command.delete('LOGOUT')
    events.command.delete('GROUP')
    events.command.delete('UNGROUP')

def register(msg, args = None):
    """ register a user with services 
        syntax: REGISTER <password> <email>
        email may or may not be used for validation depending on services configuration. """
    if args is None or len(args.split()) < 2:
        msg.origin.privmsg(msg.params, "Syntax: /msg %s \x02REGISTER\x02 <password> <email>" % (var.bots[msg.params].data['nick']))
        return False
    # set the variables required to register a user
    username = msg.origin.nick
    try:
        args = args.split()
        password = args[0]
        email = args[1]
    except:
        # this shouldn't happen because of the condition above
        return False
    user = database.register_user(username, password, email)
    if user['data']['acname'] == username:
        msg.origin.privmsg(msg.params, "You are now registered and logged in as \x02%s\x02." % (username))
        var.protocol.notice(config('main', 'logchan'), "\x02register: \x02\x034 username %s, email %s to %s" % (username, email, var.users[str(msg.origin)]['asmhost']))
        msg.origin.login(username)
        database.sync_db()
        
def login(msg, args = None):
    """ allow a user to login to services and alert the uplink that the user logged in.
        syntax: LOGIN <accountname> <password>
        an alias for this is IDENTIFY which takes only password and uses the current nick as the username """
    
    if args is None or len(args.split()) < 2:
        msg.privmsg(msg.params, "Syntax: /msg %s \x02LOGIN\x02 <accountname> <password>" % (var.bots[msg.params].data['nick']))
        return False
    if var.users[str(msg.origin)]['account'] != '*':
        msg.origin.privmsg(msg.params, "You are already logged in as \x02%s\x02." % (var.users[str(msg.origin)]['account']))
        return False
    # set the variables required to allow a user to login
    try:
        args = args.split()
        username = args[0]
        password = args[1]
    except:
        # this shouldn't happen because of the conditional above
        return False
    if username not in database.__refero__()['users']:
        msg.origin.privmsg(msg.params, "Username \x02%s\x02 has not been registered yet." % (username))
        return False
    valid = database.validate_pass(username, password)
    if valid is False:
        var.failed_logins.update({username: []})
        var.failed_logins[username].append(var.users[str(msg.origin)]['asmhost'])
        msg.origin.privmsg(msg.params, "Login for \x02%s\x02 failed and has been logged." % (username))
        var.protocol.notice(config('main', 'logchan'), "\x02failed login attempt: \x02\x034 username %s from %s" % (username, var.users[str(msg.origin)]['asmhost']))
        return False
    elif valid is True:
        msg.origin.login(username)
        msg.origin.privmsg(msg.params, "You are now logged in as \x02%s\x02." % (username))
        if username in var.failed_logins:
            msg.origin.privmsg(msg.params, "There has/have been %s failed logins since your last login." % (len(var.failed_logins[username])))
            [msg.origin.privmsg(msg.params, " - Attempt from \x02%s\x02" % (host)) for host in var.failed_logins[username]]
        var.protocol.notice(config('main', 'logchan'), "\x02login: \x02\x034 username %s from %s" % (username, var.users[str(msg.origin)]['asmhost']))
        return False

def identify(msg, args = None):
    """ allow a user to login to services and alert the uplink that the user logged in.
        syntax: IDENTIFY <password>
        an alias for this is IDENTIFY which takes only password and uses the current nick as the username """
    
    if args is None or len(args.split()) < 1:
        msg.privmsg(msg.params, "Syntax: /msg %s \x02IDENTIFY\x02 <password>" % (var.bots[msg.params].data['nick']))
        return False
    if var.users[str(msg.origin)]['account'] != '*':
        msg.origin.privmsg(msg.params, "You are already logged in as \x02%s\x02." % (var.users[str(msg.origin)]['account']))
        return False
    # set the variables required to allow a user to login
    try:
        args = args.split()
        username = msg.origin.nick
        password = args[0]
    except:
        # this shouldn't happen because of the conditional above
        return False
    if username not in database.__refero__()['users']:
        msg.origin.privmsg(msg.params, "Username \x02%s\x02 has not been registered yet." % (username))
        return False
    valid = database.validate_pass(username, password)
    if valid is False:
        var.failed_logins.update({username: []})
        var.failed_logins[username].append(var.users[str(msg.origin)]['asmhost'])
        msg.origin.privmsg(msg.params, "Login for \x02%s\x02 failed and has been logged." % (username))
        var.protocol.notice(config('main', 'logchan'), "\x02failed login attempt: \x02\x034 username %s from %s" % (username, var.users[str(msg.origin)]['asmhost']))
        return False
    elif valid is True:
        msg.origin.login(username)
        msg.origin.privmsg(msg.params, "You are now logged in as \x02%s\x02." % (username))
        if username in var.failed_logins:
            msg.origin.privmsg(msg.params, "There has/have been %s failed logins since your last login." % (len(var.failed_logins[username])))
            [msg.origin.privmsg(msg.params, " - Attempt from \x02%s\x02" % (host)) for host in var.failed_logins[username]]
        var.protocol.notice(config('main', 'logchan'), "\x02login: \x02\x034 username %s from %s" % (username, var.users[str(msg.origin)]['asmhost']))
        return False

def logout(msg):
    """ log a user out of services and alert the uplink """
    
    if not msg.origin.logged_in or var.users[str(msg.origin)]['account'] == '*':
        msg.origin.privmsg(msg.params, "You are not currently logged in.")
        return False
    var.protocol.notice(config('main', 'logchan'), "\x02logout: \x02\x034 account %s from %s" % (var.users[str(msg.origin)]['account'], var.users[str(msg.origin)]['asmhost']))
    msg.origin.privmsg(msg.params, "You have been logged out of the account \x02%s\x02." % (var.users[str(msg.origin)]['account']))
    msg.origin.logout()
    return False
    
def group(msg, args = None):
    """ group an extra nick to user """
    
    # setup variables
    try: 
        nick = args.split()[0]
        account = var.users[str(msg.origin)]['account']
    except: msg.privmsg(msg.params, "Syntax: /msg %s \x02GROUP\x02 <nick>" % (var.bots[msg.params].data['nick']))
    if not msg.origin.logged_in or var.users[str(msg.origin)]['account'] == '*':
        msg.origin.privmsg(msg.params, "You are not currently logged in.")
        return False
    if nick in var.database.__refero__()['users']['grouped']:
        msg.origin.privmsg(msg.params, "%s is already grouped to another account." % (nick))
        return False
    var.protocol.notice(config('main', 'logchan'), "\x02group: \x02\x034 nick %s to %s" % (nick, account))
    var.database.__refero__()['users'][account]['grouped'].append(nick)
    
def ungroup(msg, args = None):
    """ ungroup a nick from user """
    
    # setup variables
    try: 
        nick = args.split()[0]
        account = var.users[str(msg.origin)]['account']
    except: msg.privmsg(msg.params, "Syntax: /msg %s \x02UNGROUP\x02 <nick>" % (var.bots[msg.params].data['nick']))
    if not msg.origin.logged_in or var.users[str(msg.origin)]['account'] == '*':
        msg.origin.privmsg(msg.params, "You are not currently logged in.")
        return False
    if nick in var.database.__refero__()['users']['grouped'] and nick not in var.database.__refero__()['users'][account]['grouped']:
        msg.origin.privmsg(msg.params, "%s is not owned by you and is grouped to another account." % (nick))
        return False
    if nick not in var.database.__refero__()['users']['grouped'] and nick not in var.database.__refero__()['users'][account]['grouped']:
        msg.origin.privmsg(msg.params, "%s is not grouped to any account, and therefore cannot be removed." % (nick))
        return False
    var.protocol.notice(config('main', 'logchan'), "\x02ungroup: \x02\x034 nick %s from %s" % (nick, account))
    userdb = var.database.__refero__()['users'][account]['grouped'].remove(nick)
    