#!/usr/bin/env python2.6

from core import logger, var, decor
from core.decor import permissions
import smtplib, time, traceback
from email.mime.text import MIMEText

""" im going to try to provide a very extensible notification client
    for email and such, provided the host system has a 
    completely working sendmail setup or something similar.
    im going to use the api to attempt to let other methods borrow
    my notifier class. """
    
uplink, events = var.uplink, var.events

@events.api.register('notifier')
class Notifier(object):
    """" sent a notification to an address """
    class NotifyError(Exception):
        """ basically, this is raised if the message is already sent. """
        def __init__(self, error):
            self.error = error
        def __str__(self):
            return repr(self.error)
    def __init__(self):
        self.address = var.config.value('notifier', 'address')
        self._subject = 'ashiema system message'
        self._message = 'This is a notice from the ashiema instance on the IRC network: %s. The notifier message was not specified, which means that you are getting this message because there might be a bug in the system, a message is not defined inside the calling module, or some other unknown problem (of course, it could just be a simple test of the notifications system...). This message was sent at: %s' % (var.conf['server'], time.asctime())
        self._sender = 'ashiema@%s' % (var.conf['server'])
        self._sent = False
    def setmessage(self, message):
        if not self._sent: self._message = message
        else: raise NotifyError('Notification already sent.')
        return self
    def setaddress(self, address):
        if not self._sent: self.address = address
        else: raise NotifyError('Notification already sent.')
        return self
    def setsender(self, sender):
        if not self._sent: self._sender = sender
        else: raise NotifyError('Notification already sent.')
        return self
    def setsubject(self, subject):
        if not self._sent: self._subject = subject
        else: raise NotifyError('Notification already sent.')
        return self
    def send(self):
        if self._sent: raise NotifyError('Notification already sent.')
        p = MIMEText(self._message)
        p['Subject'] = self._subject
        p['From'] = self._sender
        p['To'] = self.address
        s = smtplib.SMTP('127.0.0.1', '25')
        s.sendmail(self._sender, [self.address], p.as_string())
        self._sent = True
        s.quit()