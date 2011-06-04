#!/usr/bin/env python

import benchmarking, time, os

"""  this benchmark is for the database. its going to perform a list
     of database operations and time it, to see how long it will take. """

def run():
    print 'generating 50,000 users...'
    iusers = []
    [iusers.append(i) for i in range(0, 50000, 1)]
    print 'users generated...benchmarking.'
    print 'loading modules..'
    benchmarking.start('load modules')
    import core
    from core import var, database
    benchmarking.stop('load modules')
    print 'initializing db..'
    benchmarking.start('init db')
    db = database.Database()
    benchmarking.stop('init db')
    print 'registering a user..'
    benchmarking.start('reg one user')
    db.register_user('user', 'pasword')
    benchmarking.stop('reg one user')
    print 'modifying user metadata..'
    benchmarking.start('modify user metadata')
    db.__refero__()['users']['user']['metadata']['email'] = 'someone@example.com'
    db.__refero__()['users']['user']['metadata']['soper'] = True
    benchmarking.stop('modify user metadata')
    print 'registering two channels..'
    benchmarking.start('reg two chans')
    db.register_channel('#a', 'password', 'user')
    db.register_channel('#b', 'password', 'user')
    benchmarking.stop('reg two chans')
    print 'registering one channel..'
    benchmarking.start('reg one chan')
    db.register_channel('#c', 'password', 'user')
    benchmarking.stop('reg one chan')
    print 'deregistering one channel..'
    benchmarking.start('dereg one chan')
    db.deregister_channel('#c')
    benchmarking.stop('dereg one chan')
    print 'deregistering one user..'
    benchmarking.start('dereg user')
    db.deregister_user('user')
    benchmarking.stop('dereg user')
    print 'synching database..'
    benchmarking.start('sync db')
    db.sync_db()
    benchmarking.stop('sync db')
    print '[INTENSE] registering 50,000 users..'
    benchmarking.start('register 50000 users')
    [db.register_user('%s' % (user), 'password') for user in iusers]
    benchmarking.stop('register 50000 users')
    print 'closing database..'
    benchmarking.start('close db')
    db.close_db()
    benchmarking.stop('close db')
    print 'benchmarked.'
    f = open('benchmarks/results/database-results.txt', 'w')
    f.write(benchmarking.format_all())
    f.close()
    print 'database benchmark is in benchmarks/results/database-results.txt'
    os.system('rm etc/labere.db')