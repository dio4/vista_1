# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceDouble, forceRef, forceString, toVariant

from Ui_IntroducePercentDialog import Ui_IntroducePercentDialog


class CIntroducePercentDialog(CDialogBase, Ui_IntroducePercentDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()


    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('IntroducePercent', CIntroducePercentModel(self))


    def postSetupUi(self):
        self.setModels(self.tblIntroducePercent,   self.modelIntroducePercent, self.selectionModelIntroducePercent)


    def selectItem(self):
        return self.exec_()


class CIntroducePercentModel(QtCore.QAbstractTableModel):
    headerText = [u'Затрата', u'Процент']

    def __init__(self,  parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()):
        return 2


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsEditable


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        return QtCore.QVariant()


    def loadData(self):
        db = QtGui.qApp.db
        table = db.table('rbExpenseServiceItem')
        records = db.getRecordList(table, '*')
        for record in records:
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            id = forceRef(record.value('id'))
            item = [code + u'-' + name,
                    forceDouble(0),
                    id
                    ]
            self.items.append(item)
        self.reset()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row < len(self.items):
                if column == 1:
                    self.items[row][1] = forceString(forceDouble(value))
                    #self.emitCellChanged(row, column)
                    return True
        return False


#    def flags(self, index):
#        result = CInDocTableModel.flags(self, index)
#        column = index.column()
#        row = index.row()
#        expenseTypeId = None
#        if row < len(self.items()):
#            record = self.items()[row]
#            expenseTypeId = forceRef(record.value('rbTable_id'))
#        if expenseTypeId and column != 0:
#            result |= Qt.ItemIsEditable
#        return result
