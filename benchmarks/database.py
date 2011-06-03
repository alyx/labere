#!/usr/bin/env python

import benchmarking, time

"""  this benchmark is for the database. its going to perform a list
     of database operations and time it, to see how long it will take. """

operations = {
    'load core': 'import core',
    'load var and database': 'from core import var, database',
    'initialize database': 'database.Database().close_db()',
    'register a single user': 'database.Database().register_user("user", "password")',
    'register two channels to user': 'database.Database().register_channel("#a", "password", "user"); database.Database().register_channel("#b", "password", "user")',
    'modify metadata for user': 'database.Database().__refero__()["users"]["user"]["metadata"]["email"] = "someone@gmail.com"',
    'register another channel': 'database.Database().register_channel("#c", "password", "user")',
    'remove #c': 'database.Database().deregister_channel("#c")',
    'deregister user': 'database.Database().deregister_user("user")',
    'sync and close the database': 'database.Database().close_db()'
}

def start():
    for msg, operation in operations.iteritems():
        benchmarking.start('%s' % (msg))
        eval('operation')
        benchmarking.stop('%s' % (msg))
    time.sleep(2)
    benchmarking.print_all()