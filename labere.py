#!/usr/bin/env python2.6

import core, time
from core import var, uplink
u = uplink.Uplink()
u.protocol.load_protocol()
u.connect()
time.sleep(2)
u.protocol.negotiate()
time.sleep(1)
u.protocol.introduce('labere!labere@labere.maio.me:labere irc services', 'AAAABC', modes = 'SoZw' if var.c.get('uplink', 'ssl') == 'True' else 'Sow')
u.protocol.gate().sjoin('labere', '#maiome.lobby')
u.send('PONG :47Q')
u.protocol.parse()
