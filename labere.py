#!/usr/bin/env python2.6

import core, time, eventlet
from core import var, uplink
u = uplink.Uplink()
u.protocol.load_protocol()
u.connect()
time.sleep(2)
u.protocol.negotiate()
time.sleep(.5)
u.protocol.parse()