#!/usr/bin/env python

from imp import load_source
import logger, var, traceback, warnings, decor

def load(module = None):
    uplink, events = var.uplink, var.events
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

def unload(module = None):
    uplink, events = var.uplink, var.events
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

def reload(msg, module):
    """ reload a module """
    uplink, events = var.uplink, var.events
    try: 
        if module not in var.modules:
            logger.warning('unload(): %s is not in the loaded modules list' % (module))
            return False
    except: 
        logger.error('unload(): unknown error occurred')
        return False
    try: mod = var.modules[module]
    except (KeyError): return False
    try: mod.close(msg)
    except:
        logger.info('unload(): error uninitializing %s' % (mod.__name__))
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
