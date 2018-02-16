# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceInt, toVariant

from Ui_ActionPropertyChooser import Ui_ActionPropertyChooserDialog

class CActionPropertyChooser(CDialogBase, Ui_ActionPropertyChooserDialog):
    def __init__(self, parent, actionPropertyTypeList):
        CDialogBase.__init__(self, parent)
        self.addModels('Choose', CActionChooseModel(self, actionPropertyTypeList))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Выбор свойств для отчёта')
        self.setModels(self.tblChoose, self.modelChoose, self.selectionModelChoose)
        self.tblChoose.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


    def getSelectedPropertyTypeList(self):
        return self.modelChoose.getSelectedPropertyTypeList()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelChoose_dataChanged(self, topLeft, bottomRight):
        left = topLeft.column()
        right = bottomRight.column()
        if  left <= 1 <= right:
            self.chkShowUnit.setCheckState(self.modelChoose.getUnitCheckState())
        if  left <= 2 <= right:
            self.chkShowNorm.setCheckState(self.modelChoose.getNormCheckState())


    @QtCore.pyqtSlot(int)
    def on_chkShowUnit_stateChanged(self, state):
        if state in [QtCore.Qt.Unchecked, QtCore.Qt.Checked]:
            self.modelChoose.setShowUnit(state == QtCore.Qt.Checked)


    @QtCore.pyqtSlot(int)
    def on_chkShowNorm_stateChanged(self, state):
        if state in [QtCore.Qt.Unchecked, QtCore.Qt.Checked]:
            self.modelChoose.setShowNorm(state == QtCore.Qt.Checked)



class CActionChooseModel(QtCore.QAbstractTableModel):
    headers = [u'Наименование', u'Ед.изм.', u'Норма']

    def __init__(self, parent, actionPropertyTypeList):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.actionPropertyTypeList = actionPropertyTypeList
        self.selected = [True]*len(self.actionPropertyTypeList)
        self.showUnit = [False]*len(self.actionPropertyTypeList)
        self.showNorm = [False]*len(self.actionPropertyTypeList)


    def columnCount(self, index = QtCore.QModelIndex()):
        return 3


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.actionPropertyTypeList)


    def flags(self, index = QtCore.QModelIndex()):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(CActionChooseModel.headers[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if column == 0:
            if role == QtCore.Qt.DisplayRole:
                return toVariant(self.actionPropertyTypeList[row].name)
            elif role == QtCore.Qt.CheckStateRole:
                return QtCore.QVariant(QtCore.Qt.Checked if self.selected[row] else QtCore.Qt.Unchecked)
        elif column == 1:
            if role == QtCore.Qt.CheckStateRole:
                return QtCore.QVariant(QtCore.Qt.Checked if self.showUnit[row] else QtCore.Qt.Unchecked)
        elif column == 2:
            if role == QtCore.Qt.CheckStateRole:
                return QtCore.QVariant(QtCore.Qt.Checked if self.showNorm[row] else QtCore.Qt.Unchecked)
        return QtCore.QVariant()


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.CheckStateRole:
            if column == 0:
                self.selected[row] = forceInt(value) == QtCore.Qt.Checked
            elif column == 1:
                self.showUnit[row] = forceInt(value) == QtCore.Qt.Checked
            elif column == 2:
                self.showNorm[row] = forceInt(value) == QtCore.Qt.Checked
            self.emitDataChanged(row, column)
            return True
        return False


    def getSelectedPropertyTypeList(self):
        result = [(actionProperty, showUnit, showNorm)
                  for selected, actionProperty, showUnit, showNorm in zip(self.selected, self.actionPropertyTypeList, self.showUnit, self.showNorm)
                  if selected]
        return result


    def setChkColumn(self, data, checked, column):
        for i in xrange(len(data)):
            if data[i] != checked:
                data[i] = checked
                self.emitDataChanged(i, column)


    def getCheckState(self, data):
        numChecked = sum(data)
        if numChecked == len(data):
            return QtCore.Qt.Checked
        elif numChecked:
            return QtCore.Qt.PartiallyChecked
        else:
            return QtCore.Qt.Unchecked


    def setShowUnit(self, checked):
        self.setChkColumn(self.showUnit, checked, 1)


    def setShowNorm(self, checked):
        self.setChkColumn(self.showNorm, checked, 2)


    def getUnitCheckState(self):
        return self.getCheckState(self.showUnit)


    def getNormCheckState(self):
        return self.getCheckState(self.showNorm)


    def emitDataChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
