# -*- coding: utf-8 -*-&DirtyCrypt.py

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


import base64
import zlib
import random

def encryptPassword(pwd):
    pwd = pwd.encode('utf-8')
    usedChars = list(set([c for c in pwd if not c.isspace()]))
    if usedChars:
        random.shuffle(usedChars)
        salt = usedChars[:2]
    else:
        salt = []
    while len(salt)<3:
        c = chr(random.randint(0, 127))
        if not c.isspace():
            salt.insert(0, c)
    salt = ''.join(salt)
    compessed = zlib.compress(salt+'\n'+pwd, 9)
    while len(compessed)%3:
        compessed += chr(random.randint(0, 127)) # добавка для удаления '=' в конце
    return '#1##'+ base64.b64encode(compessed)


def decryptPassword(pwd):
    if pwd[:4] != '#1##':
        raise ValueError('bad encrypted password')
    return zlib.decompress(base64.b64decode(pwd[4:])).split('\n', 1)[-1].decode('utf-8')

