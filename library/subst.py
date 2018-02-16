# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


def substFields(text, fields):
    r = re.compile(r'\{([^}]*)\}')

    text = '%%'.join(text.split('%'))
    while True:
        m = r.search(text)
        if m:           
            text = text[:m.start(1)-1]+'%('+m.group(1)+')s'+text[m.end(1)+1:]
        else:
            break
    return text % CSubst(fields)


class CSubst(object):      
    def __init__(self, data):
        self.data = data
        self.now = QDateTime.currentDateTime()

    def __getitem__(self, key):
        if key == 'currentDate':
            return formatDate(self.now.date())
        if key == 'currentTime':
            return formatTime(self.now.time())
            
        seq = key.split('.')
        data = self.data
        for name in seq:
            if hasattr(data, 'has_key') and data.has_key(name):
                data = data[name]
            else:
                return '['+key+']'
        return unicode(data)

#        
#def escape(s):
#    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    
    