#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import sys
import os

builtinListDir = os.listdir

def myListDir(path):
    if isinstance(path, unicode):
        encoding = sys.getfilesystemencoding()
        return [ f if isinstance(f, unicode) else unicode(f, encoding) for f in builtinListDir(path)]
    else:
        return builtinListDir(path)

os.listdir = myListDir

# =================================================

builtinUnlink = os.unlink

def myUnlink(path):
    if isinstance(path, unicode):
        try:
            builtinUnlink(path)
        except UnicodeError:
            encoding = sys.getfilesystemencoding()
            builtinUnlink(path.encode(encoding))
    else:
        builtinUnlink(path)

os.unlink = myUnlink
os.remove = myUnlink

# =================================================

if os.name == 'nt':
    builtinExpanduser = os.path.expanduser
    builtinExpandvars = os.path.expandvars

    def myExpanduser(path):
        if isinstance(path, unicode):
            try:
                return builtinExpanduser(path)
            except UnicodeError:
                encoding='cp1251'
                return builtinExpanduser(path.encode(encoding)).decode(encoding)
        else:
            return builtinExpanduser(path)

    def myExpandvars(path):
        if isinstance(path, unicode):
            try:
                return builtinExpandvars(path)
            except UnicodeError:
                encoding='cp1251'
                return builtinExpandvars(path.encode(encoding)).decode(encoding)
        else:
            return builtinExpandvars(path)

    os.path.expanduser = myExpanduser
    os.path.expandvars = myExpandvars
