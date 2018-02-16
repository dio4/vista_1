# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Events.Utils import getPayStatusMaskByCode, payStatusText
from library.PrintInfo  import CInfo
from Accounting.Utils   import *


class CPayStatusInfo(CInfo):
    def __init__(self, context, payStatus, defaultFinance=None):
        CInfo.__init__(self, context)
        self._loaded = True
        self._ok = True
        self.payStatus = payStatus
        self._mask = -1
        self._finance = defaultFinance


    def _getFinanceCode(self, finance):
        if finance is None:
            financeCode = 0
        if isinstance(finance, int):
            financeCode = finance
        elif isinstance(finance, basestring):
            financeCode = int(finance)
        else:
            financeCode = int(finance.code)
        return financeCode


    def _getMask(self, finance):
        financeCode = self._getFinanceCode(finance)
        return getPayStatusMaskByCode(financeCode)


    def _checkBits(self, bits):
        if self._mask == -1 and self._finance:
            self._mask = self._getMask(self._finance)
        return (self.payStatus & self._mask) == (bits & self._mask)


    def __getitem__(self, finance):
        return self.getInstance(CPayStatusInfo, self.payStatus, finance)


    def __str__(self):
        return payStatusText(self.payStatus)


    initial = property(lambda self: self._checkBits(CPayStatus.initialBits))
    exposed = property(lambda self: self._checkBits(CPayStatus.exposedBits))
    refused = property(lambda self: self._checkBits(CPayStatus.refusedBits))
    payed   = property(lambda self: self._checkBits(CPayStatus.payedBits))