# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.crbcombobox    import CRBComboBox
from library.InDocTable     import CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol


class CWorkHurtsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientWork_Hurt', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Вредность', 'hurtType_id', 30, 'rbHurtType', showFields = CRBComboBox.showNameAndCode ))
        self.addCol(CIntInDocTableCol(u'Стаж',   'stage', 4, low=0, high=99))
        self._editable = True

    def flags(self,  index = QtCore.QModelIndex()):
        if self._editable:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled


class CWorkHurtFactorsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientWork_Hurt_Factor', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Фактор', 'factorType_id', 34, 'rbHurtFactorType', showFields = CRBComboBox.showNameAndCode))
        self._editable = True
   

    def flags(self,  index = QtCore.QModelIndex()):
        if self._editable:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
