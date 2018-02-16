# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

"""
F110 planer
"""

from Forms.F025.PreF025Dialog import CPreF025Dialog, CPreF025DagnosticAndActionPresets


CPreF110DagnosticAndActionPresets = CPreF025DagnosticAndActionPresets


class CPreF110Dialog(CPreF025Dialog):
    def __init__(self, parent, contractTariffCache):
        CPreF025Dialog.__init__(self,  parent, contractTariffCache)
        self.setWindowTitleEx(u'Планирование осмотра Ф.110')
