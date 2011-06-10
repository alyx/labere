#!/usr/bin/env python

import core, etc, inspect
from core import var, logger

class API(object):
    def __init__(self):
        self._db = {}
    def __refero__(self):
        return self._db
    def register_method(self, name, func):
        """ this is a stand-up method for registering a class or function with the bots api to allow module developers to use it without having
            to import the other module. once a class/function is registered, its not unregistered unless an API().deregister_method(name) is called.
            of course, this module will not have to be imported into your own module. an instance of it will exist in var.store as
            var.store.api. to use the api, simply source it, or use the remote.
            
            either: 
            
                api = events.api
                
            or, call it directly:
            
                events.api.register_method(...)
                -----------or------------------
                @events.api.register('name')
                
            i will also provide decorators to decorate your class/function and streamline your code. """
        if inspect.isclass(func) is True:
            type = 'class'
        elif inspect.isfunction(func) is True:
            type = 'function'
        else: logger.error('api(): registered object is not function or class')
        if name in self._db:
            logger.info('api(): \'%s\' already exists in api' % (name))
            return False
        self._db.update({name: {'object': func, 'type': type}})
        logger.info('api(): \'%s\' registered in api database' % (name))
    def deregister_method(self, name):
        """ opposite of the register_method function, removes a function from the api. """
        if name not in self._db:
            logger.error('api(): \'%s\' does not exist in the api database' % (name))
            return False
        self._db[name].clear()
        self._db.__delitem__(name)
        logger.info('api(): \'%s\' deregistered from api database' % (name))
    def register(self, name):
        def wrap(func):
            if inspect.isclass(func) is True:
                type = 'class'
            elif inspect.isfunction(func) is True:
                type = 'function'
            else: logger.info('api(): registered object is not a function or class')
            if name in self._db:
                logger.info('api(): \'%s\' already exists in api, updating object.' % (name))
                self._db[name]['object'] = func
            elif name not in self._db:
                self._db.update({name: {'object': func, 'type': type}})
                logger.info('api(): \'%s\' registered in api database' % (name))
            return func
        return wrap