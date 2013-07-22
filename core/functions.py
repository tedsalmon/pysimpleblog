#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta

# Base project URL
BASE = '%s/..' % os.path.dirname(os.path.realpath(__file__))

# Make UTC Timestamps
# @param int delta Time in seconds to subtract from the current time
UTCDate = lambda delta=0: datetime.utcnow() - timedelta(seconds=delta)

def b36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
    base36, sign = '', ''
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36

# Mock Up dictionary that stores/updates settings
class Settings(dict):
    FILE = '%s/settings.json' % BASE

    def __init__(self, *args, **kw):
        super(Settings, self).__init__()
        self.itemlist = super(Settings, self).keys()
        self._last_edited = 0
        self._fileLoad()
    
    def _fileLoad(self, ):
        edited = int(os.path.getctime(self.FILE))
        if self._last_edited < edited:
            self._last_edited = edited
            data = open(self.FILE,'r').read()
            self.settings = json.loads(data)
        for key, val in self.settings.iteritems():
            super(Settings, self).__setitem__(key, val)
            
    def __iter__(self):
        return iter(self.itemlist)
    
    def __getitem__(self, key, ):
        self._fileLoad()
        data = super(Settings, self).__getitem__(key)
        return data

    def __setitem__(self, key, item, ):
        self.itemlist.append(key)
        super(Settings, self).__setitem__(key, item)
        self._fileLoad()
        self.settings[key] = item
        data = open(self.FILE,'w')
        data.write(json.dumps(self.settings))
        data.close()

    def keys(self):
        return self.itemlist
    
    def values(self):
        return [self[key] for key in self]
    
    def itervalues(self):
        return (self[key] for key in self)