# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore
from PyQt4 import QtGui

from Events.Action import CActionTypeCache, CAction, ensureActionTypePresence
from Forms.F025.F025Dialog import CF025Dialog

__author__ = 'atronah'

'''
    author: atronah
    date:   23.12.2014
    reason: Dental version of F025.
    issue: 1618
'''

class CF025DentalModel(QtCore.QAbstractTableModel):
    def __init__(self, isCalf, parent = None):
        super(CF025DentalModel, self).__init__(parent)
        self._isCalf = isCalf
        self._dentalNotationAction = None


    #--- re-implement
    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        return 4

    def columnCount(self, parentIndex = QtCore.QModelIndex()):
        return 10 if self._isCalf else 16


    def flags(self, index):
        flags = QtCore.Qt.NoItemFlags

        if self._dentalNotationAction and index.isValid():
            row = index.row()
            column = index.column()
            if column in xrange(self.columnCount()):
                if row in [0, 3]:
                    flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
                    propertyName = self.getPropertyName(row, column)
                    prop = self._dentalNotationAction.getProperty(propertyName)
                    if prop.type().isAssignable:
                        flags += QtCore.Qt.ItemIsUserCheckable
                elif row in [1, 2]:
                    flags = QtCore.Qt.ItemIsEnabled
        return flags


    def data(self, index, role = QtCore.Qt.DisplayRole):
        if self._dentalNotationAction and index.isValid():
            row = index.row()
            column = index.column()
            if column in xrange(self.columnCount()):
                if row in [0, 3]:
                    propertyName = self.getPropertyName(row, column)
                    prop = self._dentalNotationAction.getProperty(propertyName)
                    if role == QtCore.Qt.DisplayRole:
                        return QtCore.QVariant(prop.getText())
                    elif role == QtCore.Qt.CheckStateRole:
                        if prop.type().isAssignable:
                            QtCore.QVariant(QtCore.Qt.Checked if prop.isAssigned() else QtCore.Qt.Unchecked)
                    elif role == QtCore.Qt.EditRole:
                        return QtCore.QVariant(prop.getValue())
                    elif role == QtCore.Qt.DecorationRole:
                        return QtCore.QVariant(prop.getImage())
                    elif role == QtCore.Qt.ForegroundRole:
                        if prop.getEvaluation():
                            return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    elif role == QtCore.Qt.FontRole:
                        evaluation = prop.getEvaluation()
                        if evaluation and abs(evaluation) == 2:
                            font = QtGui.QFont()
                            font.setBold(True)
                            return QtCore.QVariant(font)
                elif row in [1, 2]:
                    if role == QtCore.Qt.DisplayRole:
                        return QtCore.QVariant(self.getPropertyName(0 if row == 1 else 3, column))
                    elif role == QtCore.Qt.FontRole:
                        font = QtGui.QFont()
                        font.setBold(True)
                        return QtCore.QVariant(font)
                    elif role == QtCore.Qt.TextAlignmentRole:
                        return QtCore.QVariant(QtCore.Qt.AlignCenter)



        return QtCore.QVariant()


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if self._dentalNotationAction and index.isValid():
            row = index.row()
            column = index.column()
            if column in xrange(self.columnCount()):
                if row in [0, 3]:
                    propertyName = self.getPropertyName(row, column)
                    prop = self._dentalNotationAction.getProperty(propertyName)
                    if role == QtCore.Qt.EditRole:
                        prop.setValue(prop.type().convertQVariantToPyValue(value))
                        self.dataChanged.emit(index, index)
                        return True
                    elif role == QtCore.Qt.CheckStateRole:
                        prop.setAssigned(value == QtCore.Qt.Checked)
                        self.dataChanged.emit(index, index)
                        return True
            return False

    #--- working
    def getPropertyName(self, row, column):
        if row not in (0, self.rowCount() - 1):
            return None

        if (column * 2) < self.columnCount():
            quadrant = 1 if row == 0 else 4
            number = (self.columnCount() / 2) - column
        else:
            quadrant = 2 if row == 0 else 3
            number = column  - (self.columnCount() / 2) + 1

        if self._isCalf:
            quadrant += 4

        return u'%s%s' % (quadrant, number)


    def loadData(self, eventId):
        record = None
        db = QtGui.qApp.db
        tableAction = db.table('Action')

        propertyDefList = []
        for row in xrange(self.rowCount()):
            for column in xrange(self.columnCount()):
                propertyName = self.getPropertyName(row, column)
                if propertyName is not None:
                    propertyDefList.append({'name' : propertyName,
                                         'descr' : None,
                                         'unit' : None,
                                         'typeName' : 'String',
                                         'valueDomain' : None,
                                         'isVector' : False,
                                         'norm' : None,
                                         'sex' : None,
                                         'age' : None
                                         })

        actionTypeFlatCode = u'calfTeeth' if self._isCalf else u'permanentTeeth'
        ensureActionTypePresence(actionTypeFlatCode, propTypeList = propertyDefList, isUseFlatCode=True)
        actionType = CActionTypeCache.getByFlatCode(actionTypeFlatCode)
        if eventId:
            cond  = [tableAction['deleted'].eq(0),
                     tableAction['event_id'].eq(eventId),
                     tableAction['actionType_id'].eq(actionType.id)]

            record = db.getRecordEx(tableAction,
                                    '*',
                                    cond,
                                    order = 'idx')
        self._dentalNotationAction = CAction(record = record if record else None,
                                             actionType = actionType)


    def saveData(self, eventId):
        if self._dentalNotationAction:
            self._dentalNotationAction.save(eventId = eventId)




class CF025DentalDialog(CF025Dialog):
    def __init__(self, parent):
        super(CF025DentalDialog, self).__init__(parent)
        self.updateUi()
        self.addModels('PermanentTeeth', CF025DentalModel(isCalf = False, parent = self))
        self.addModels('CalfTeeth', CF025DentalModel(isCalf = True, parent = self))
        self.tblPermanentTeeth.setModel(self.modelPermanentTeeth)
        self.tblCalfTeeth.setModel(self.modelCalfTeeth)
        

    def updateUi(self):
        if hasattr(self, 'groupBox'):
            self.tabDental = QtGui.QTabWidget()
            self.tblPermanentTeeth = QtGui.QTableView()
            self.tabDental.addTab(self.tblPermanentTeeth, u'Постоянные зубы')

            self.tblCalfTeeth = QtGui.QTableView()
            self.tabDental.addTab(self.tblCalfTeeth, u'Молочные зубы')

            for w in [self.tblPermanentTeeth, self.tblCalfTeeth]:
                w.horizontalHeader().hide()
                w.verticalHeader().hide()
                w.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
                w.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

            layout = self.groupBox.layout()
            layout.addWidget(self.tabDental, layout.rowCount(), 0, 1, layout.columnCount())
            self.groupBox.setTitle(self.groupBox.title() + u' и зубная формула')


    def loadDentalData(self):
        self.modelPermanentTeeth.loadData(self.itemId())
        self.modelCalfTeeth.loadData(self.itemId())


    def saveDentalData(self, eventId):
        self.modelPermanentTeeth.saveData(eventId)
        self.modelCalfTeeth.saveData(eventId)

    
    def prepare(self, *args, **kwargs):
        result = super(CF025DentalDialog, self).prepare(*args, **kwargs)
        self.loadDentalData()
        return result


    def setRecord(self, record):
        super(CF025DentalDialog, self).setRecord(record)
        self.loadDentalData()


    def saveInternals(self, eventId):
        super(CF025DentalDialog, self).saveInternals(eventId)
        self.saveDentalData(eventId)



def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()