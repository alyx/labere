#!/usr/bin/env python

from imp import load_source
import logger, var, traceback, warnings

def load(msg = None, module = None):
    """ load a module into labere """
    
    if msg is not None and str(msg.origin) not in var.database.__refero__()['misc']['labop_extended']:
        msg.origin.privmsg(msg.params, 'You do not have the misc:labop_extended privilege')
        return False
    if module is None:
        msg.origin.privmsg(msg.params, "Insufficient parameters for \x02LOAD\x02")
        msg.origin.privmsg(msg.params, 'Syntax: /msg %s LOAD <module>' % (var.bots[msg.params].data['nick']))
        return False
    uplink, events = var.core
    mod = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            mod = load_source(module, module)
        if mod.__name__ in var.modules:
            logger.error('load(): module %s already loaded' % (mod.__name__))
            return False
    except:
        logger.error('load(): unable to load module %s' % (module))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    if not hasattr(mod, 'init'):
        logger.error('load(): unable to use module %s: no entry point has been defined' % (mod.__name__))
        return False
    if not hasattr(mod, 'close'):
        logger.error('load(): unable to use module %s: no exit point has been defined' % (mod.__name__))
        return False
    try: mod.init(msg)
    except:
        logger.info('load(): error initializing %s' % (mod.__name__))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    var.modules.update({mod.__name__: mod})
    if msg: msg.origin.privmsg(msg.params, '%s has been loaded.' % (mod.__name__))
    events.onmodload.parse(module)
        
def unload(msg = None, module = None):
    """ unload a module from labere """
    
    if msg is not None and str(msg.origin) not in var.database.__refero__()['misc']['labop_extended']:
        msg.origin.privmsg(msg.params, 'You do not have the misc:labop_extended privilege')
        return False
    if module is None:
        msg.origin.privmsg(msg.params, "Insufficient parameters for \x02UNLOAD\x02")
        msg.origin.privmsg(msg.params, 'Syntax: /msg %s UNLOAD <module>' % (var.bots[msg.params].data['nick']))
        return False
    uplink, events = var.core
    try: 
        if module not in var.modules:
            logger.warning('unload(): %s is not in the loaded modules list' % (module))
            return False
    except: 
        logger.error('unload(): unknown error occurred')
        return False
    mod = var.modules[module]
    try: mod.close(msg)
    except:
        logger.info('unload(): error uninitializing %s' % (mod.__name__))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    var.modules.pop(module)
    if msg: msg.origin.privmsg(msg.params, '%s has been unloaded.' % (mod.__name__))
    events.onmodunload(module)
    
def reload(msg = None, module = None):
    """ reload a module in labere's hashtable """
    
    if msg is not None and str(msg.origin) not in var.database.__refero__()['misc']['labop_extended']:
        msg.origin.privmsg(msg.params, 'You do not have the misc:labop_extended privilege')
        return False
    if module is None:
        msg.origin.privmsg(msg.params, "Insufficient parameters for \x02RELOAD\x02")
        msg.origin.privmsg(msg.params, 'Syntax: /msg %s RELOAD <module>' % (var.bots[msg.params].data['nick']))
        return False
    uplink, events = var.core
    try: 
        if module not in var.modules:
            logger.warning('unload(): %s is not in the loaded modules list' % (module))
            if msg: msg.origin.privmsg(msg.params, "\x02%s\x02 is not loaded." % (module))
            return False
    except: 
        logger.error('unload(): unknown error occurred')
        return False
    try: mod = var.modules[module]
    except (KeyError): return False
    try: mod.close(msg)
    except:
        logger.info('unload(): error uninitializing %s' % (mod.__name__))
        if msg: msg.origin.privmsg(msg.params, "could not unload \x02%s\x02." % (mod.__name__))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    var.modules.pop(module)
    mod = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            mod = load_source(module, module)
    except:
        logger.error('load(): unable to load module %s' % (module))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    if not hasattr(mod, 'init'):
        logger.error('load(): unable to use module %s: no entry point has been defined' % (mod.__name__))
        return False
    if not hasattr(mod, 'close'):
        logger.error('load(): unable to use module %s: no exit point has been defined' % (mod.__name__))
        return False
    try: mod.init(msg)
    except:
        logger.info('load(): error initializing %s' % (mod.__name__))
        logger.info('%s' % (traceback.format_exc(4)))
        return False
    var.modules.update({mod.__name__: mod})
    events.onmodreload.parse(module)
    if msg: msg.origin.privmsg(msg.params, '%s has been reloaded.' % (mod.__name__))
