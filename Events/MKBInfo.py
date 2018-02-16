# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from Events.Utils      import getMKBClassName, getMKBBlockName, getMKBName
from library.PrintInfo import CInfo


class CMKBInfo(CInfo):
    def __init__(self, context, code):
        CInfo.__init__(self, context)
        self.code = code
        self._descr = None
        self._class = None
        self._block = None
        self._ok = bool(self.code)
        self._loaded = True


    def getClass(self):
        if self._class is None:
            self._class = getMKBClassName(self.code) if self.code else ''
        return self._class


    def getBlock(self):
        if self._block is None:
            self._block = getMKBBlockName(self.code) if self.code else ''
        return self._block


    def getDescr(self):
        if self._descr is None:
            self._descr = getMKBName(self.code) if self.code else ''
        return self._descr


    class_ = property(getClass)
    block = property(getBlock)
    descr = property(getDescr)

    def __str__(self):
        return self.code
        
     
     
class CMorphologyMKBInfo(CInfo):
    def __init__(self, context, code):
        CInfo.__init__(self, context)
        self.code = code
        self._ok = bool(self.code)
        self._loaded = True

    def __str__(self):
        return self.code
        
        
