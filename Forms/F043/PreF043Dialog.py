# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

"""
F043 planer
"""


from Forms.F025.PreF025Dialog import CPreF025Dialog, CPreF025DagnosticAndActionPresets

CPreF043DagnosticAndActionPresets = CPreF025DagnosticAndActionPresets

class CPreF043Dialog(CPreF025Dialog):
    def __init__(self, parent, contractTariffCache):
        CPreF025Dialog.__init__(self, parent, contractTariffCache)
        self.setWindowTitleEx(u'Планирование осмотра Ф.043')
