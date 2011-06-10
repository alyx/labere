#!/usr/bin/env python

class UModeParse(object):
    """ this is a class to do mode parsing of any modestring.
        this should technically work for any IRC protocol, since all
        that is required is the modestring. """
    
    def __init__(self, modestr, params = None):
        # modestring and switch array vals
        self.modestr = modestr
        self.params = None if params is None else params
        self.switch = False
        self.parsed_yet = False
        # lists for storage
        self.added = []
        self.removed = []
        
    def parse(self):
        """ actually parse the modes. """
        
        modes = []
        [modes.append(char) for char in self.modestr]
        for item in modes:
            if item == '+':
                self.switch = False
            elif item == '-':
                self.switch = True
            else:
                if self.switch == False:
                    self.added.append(item)
                elif self.switch == True:
                    self.removed.append(item)
        return ((self.added, self.removed, self.params))