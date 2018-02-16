# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from PyQt4.QtCore import QVariant, Qt, QSize
from library.Utils import forceInt, forceString

from library.crbcombobox import CRBComboBox, CRBModel, CRBSelectionModel, CRBPopupView


class CMealComboBoxModel(CRBModel):
    def __init__(self, parent):
        CRBModel.__init__(self, parent)

        db = QtGui.qApp.db
        tableRBMeal = db.table('rbMeal')
        records = db.getRecordList(tableRBMeal)
        self.mealMap = {}
        for record in records:
            mealId = forceInt(record.value('id'))
            mealName = forceString(record.value('name'))
            mealAmount = forceString(record.value('amount'))
            mealUnit = forceString(record.value('unit'))
            self.mealMap[mealId] = mealName + u', ' + mealAmount + u' ' + mealUnit

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole or role == Qt.EditRole:
            row = index.row()
            if row < self.d.getCount():
                if index.column() == 1 and row > 0:
                    return QVariant(self.mealMap[self.d.getId(row)])
                return QVariant(self.d.getString(row, index.column()))
        elif role == Qt.SizeHintRole:
            font = QtGui.QFont()
            fontMetric = QtGui.QFontMetrics(font)
            row = index.row()
            valueSize = fontMetric.size(Qt.TextExpandTabs, self.d.getString(row, index.column())) + QSize(16, 0)
            return valueSize
        return QVariant()


class CMealComboBox(CRBComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self._searchString = ''
        self.showFields = CRBComboBox.showName
        self._model = CMealComboBoxModel(self)
        self._selectionModel = CRBSelectionModel(self._model)
        self._tableName = ''
        self._addNone   = True
        self._needCache = True
        self._filter    = ''
        self._order     = ''
        self._specialValues = None
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = None
        self.popupView = CRBPopupView(self)
        self.setShowFields(self.showFields)
        self.setView(self.popupView)
        self.setModel(self._model)
        self.popupView.setSelectionModel(self._selectionModel)
        self.popupView.setFrameShape(QtGui.QFrame.NoFrame)
        self._isRTF = False

