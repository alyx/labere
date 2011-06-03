#!/usr/bin/env python

import logging, var
from logging import handlers

debug, info, warning, error, critical = None, None, None, None, None

def _getlevel(var):
    if var.Configuration['loglevel']  == 'info':
        return logging.INFO
    elif var.Configuration['loglevel']  == 'warning':
        return logging.WARNING
    elif var.Configuration['loglevel']  == 'debug':
        return logging.DEBUG
    elif var.Configuration['loglevel']  == 'error':
        return logging.ERROR
    elif var.Configuration['loglevel']  == 'critical':
        return logging.CRITICAL
    return logging.INFO
def init():
    global debug, info, warning, error, critical
    var.log = logging.getLogger('labere')
    if var.Configuration['fork'] == 'False':
        stream = logging.StreamHandler()
    else:
        stream = None
    handler = handlers.RotatingFileHandler(filename=var.Configuration['logfile'], maxBytes=10000, backupCount=5)
    formatter = logging.Formatter('[%(asctime)s] -- %(levelname)s -- %(message)s')
    handler.setFormatter(formatter)
    if stream:
        stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
        stream.setFormatter(stream_formatter)
        var.log.addHandler(stream)
    var.log.addHandler(handler)
    var.log.setLevel(_getlevel(var))
    debug, info, warning = var.log.debug, var.log.info, var.log.warning
    error, critical = var.log.error, var.log.critical