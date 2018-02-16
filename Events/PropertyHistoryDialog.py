# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from Events.Action      import CActionType

from library.DialogBase import CDialogBase
from library.InDocTable import CInDocTableModel, CInDocTableCol, CDateInDocTableCol, CEnumInDocTableCol, \
                               CRBInDocTableCol
from library.Utils      import toVariant

from Reports.ReportView import CReportViewDialog
from Registry.Utils     import getClientBanner

from Ui_PropertyHistoryDialog import Ui_PropertyHistoryDialog


class CPropertyHistoryDialog(CDialogBase, Ui_PropertyHistoryDialog):
    def __init__(self, clientId, actionPropertyList, parent):
        CDialogBase.__init__(self, parent)
        self.clientId = clientId
        self.actionPropertyList = actionPropertyList
        self.addModels('Values', CPropertyHistoryModel(clientId, actionPropertyList, self))
        self.btnPrint = QtGui.QPushButton(u'Печать', self)
        self.btnPrint.setObjectName('btnPrint')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Журнал значения свойства')
        self.setModels(self.tblValues, self.modelValues, self.selectionModelValues)
        self.tblValues.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)
        self.modelValues.loadItems()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()
        format.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(2))
        format.setFontWeight(QtGui.QFont.Bold)
        cursor.setCharFormat(format)
        if len(self.actionPropertyList) == 1:
            title = u'Журнал значения свойства "' + self.actionPropertyList[0][0].type().name + '"'
        else:
            names = ['"'+actionProperty[0].type().name+'"' for actionProperty in self.actionPropertyList]
            title = u'Журнал значения свойств ' + ', '.join(names[:-1])+u' и '+names[-1]
        cursor.insertText(title)
        cursor.insertBlock()
        cursor.setCharFormat(QtGui.QTextCharFormat())
        cursor.insertText(u'пациент:')
        cursor.insertBlock()
        cursor.insertHtml(getClientBanner(self.clientId))
        self.tblValues.addContentToTextCursor(cursor)
        view = CReportViewDialog(self)
        view.setWindowTitle(u'Журнал значения свойства')
        view.setText(doc)
        view.exec_()


class CPropertyHistoryModel(CInDocTableModel):
    def __init__(self, clientId, actionPropertyList, parent):
        CInDocTableModel.__init__(self, 'ActionProperty', 'id', '', parent)
        self.clientId = clientId
        self.actionPropertyList = actionPropertyList
        self.addCol(CDateInDocTableCol(u'Начато',   'begDate', 10, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Окончено', 'endDate', 10, canBeEmpty=True))
        self.addCol(CEnumInDocTableCol(u'Состояние', 'status', 10, CActionType.retranslateClass(False).statusNames))

        for i, (actionProperty, showUnit, showNorm) in enumerate(self.actionPropertyList):
            seq = '_'+str(i+1)
            self.addCol(CActionPropertyValueTableCol(actionProperty.type().name, 'value'+seq, 30, actionProperty))
            if showUnit:
                self.addCol(CRBInDocTableCol(u'Ед.изм.', 'unit_id'+seq, 10, 'rbUnit', isRTF = True))
            if showNorm:
                self.addCol(CInDocTableCol(u'Норма', 'norm'+seq, 30))
        self.setEnableAppendLine(False)


    def loadItems(self):
        db = QtGui.qApp.db
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')

        table = tableAction
        table = table.leftJoin(tableEvent,   tableEvent['id'].eq(tableAction['event_id']))
        cols = [tableAction['id'], tableAction['begDate'], tableAction['endDate'], tableAction['status']]
        cond = [tableEvent['client_id'].eq(self.clientId), tableEvent['deleted'].eq(0)]
        subcond = []
        for i, (actionProperty, showUnit, showNorm) in enumerate(self.actionPropertyList):
            seq = '_'+str(i+1)
            propertyType = actionProperty.type()
            tableActionProperty = db.table('ActionProperty').alias('AP'+seq)
            tableActionPropertyType  = db.table('ActionPropertyType').alias('APT'+seq)
            tableActionPropertyValue = db.table(propertyType.tableName).alias('APV'+seq)
            table = table.leftJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
            table = table.join(tableActionPropertyType, [tableActionPropertyType['id'].eq(tableActionProperty['type_id']),
                                                         tableActionPropertyType['typeName'].eq(propertyType.typeName),
                                                         tableActionPropertyType['name'].eq(propertyType.name)
                                                        ])
            table = table.leftJoin(tableActionPropertyValue, tableActionPropertyValue['id'].eq(tableActionProperty['id']))
            cols.append(tableActionPropertyValue['value'].alias('value'+seq))
            if showUnit:
                cols.append(tableActionProperty['unit_id'].alias('unit_id'+seq))
            if showNorm:
                cols.append(tableActionProperty['norm'].alias('norm'+seq))
            subcond.append(tableActionProperty['id'].isNotNull())
        cond.append(db.joinOr(subcond))

        order= [# tableAction['begDate'].name()+' DESC',
                tableAction['endDate'].name()+' DESC',
                tableAction['id'].name()
               ]

        items = db.getRecordList(table, cols, cond, order)
        self.setItems(items)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return CInDocTableModel.data(self, index, role)
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        return QtCore.QVariant()



class CActionPropertyValueTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, actionProperty):
        CInDocTableCol.__init__(self, title, fieldName, width)
        self.actionPropertyValueType = actionProperty.type().valueType
        self.cache = {}


    def toString(self, val, record):
        key = val.toPyObject() if val else None # т.к. hash(QVariant()) зависит от адреса QVariant-а и не зависит от значения
        if key in self.cache:
            return self.cache[key]
        else:
            result = toVariant(self.actionPropertyValueType.toText(val))
            self.cache[key] = result
            return result

