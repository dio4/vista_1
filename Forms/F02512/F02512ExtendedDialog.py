# -*- coding: utf-8 -*-


#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

from Forms.F02512.F02512Dialog import CF02512Dialog
from library.InDocTable import CRBInDocTableCol
from library.crbcombobox import CRBComboBox

'''
Created on 10.10.2013

@author: atronah
'''


class CF02512ExtendedDialog(CF02512Dialog):
    formTitle = u'Ф.025-12/р'
    
    def __init__(self, parent):
        CF02512Dialog.__init__(self, parent)
        self.modelFinalDiagnostics.insertCol(self.modelFinalDiagnostics.columnCount() - 2,
                                             CRBInDocTableCol(    u'Травма',        'traumaType_id', 10, 'rbTraumaType', addNone=True, showFields=CRBComboBox.showName, prefferedWidth=150))
        self.modelFinalDiagnostics.reset()
        self.grpBase.setTitle(self.formTitle.lower())
