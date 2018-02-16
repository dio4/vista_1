# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


_prefixLens = (0, 3, 5, 8, 11)

def prefixLen(level):
    return _prefixLens[level] if 0<=level<=4 else 13


def fixLevel(code, level):
    while level<4:
        if code.endswith('0'*(len(code)-prefixLen(level))):
            return level
        level += 1
    return level


def getProvinceKLADRCode(KLADRCode):
    prefix = KLADRCode[:2]
    if prefix == '77':
        return '5000000000000'
    elif prefix == '78':
        return '4700000000000'
    elif prefix:
        return prefix+'00000000000'
    else:
        return ''


def KLADRMatch(KLADRCode, regionKLADRCode):
    level = fixLevel(regionKLADRCode, 1)
    return KLADRCode.startswith(regionKLADRCode[:prefixLen(level)])

