# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import hashlib


def calcCheckSum(fileName):
    sum = hashlib.md5()
    f = open(fileName, 'rb')
    while True:
        s = f.read(65536)
        if not s:
            break
        sum.update(s)
    return sum.hexdigest()
