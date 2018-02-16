#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.database   import CTableRecordCache
from library.TableModel import CTableModel, CDateCol, CEnumCol, CTextCol
from library.Utils      import forceInt, getPref, setPref
from Registry.Utils     import codeToTextForBlank

from Ui_BlankComboBoxPopup import Ui_BlankComboBoxPopup


class CBlankComboBoxPopup(QtGui.QFrame, Ui_BlankComboBoxPopup):
    __pyqtSignals__ = ('BlankCodeSelected(int)',
                      )

    def __init__(self, parent = None, docTypeActions = False):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.tableModel = CBlankActionsTableModel(self) if docTypeActions else CBlankTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblBlank.setModel(self.tableModel)
        self.tblBlank.setSelectionModel(self.tableSelectionModel)
        self.code = None
        self.tblBlank.installEventFilter(self)
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CBlankComboBoxPopup', {})
        self.tblBlank.loadPreferences(preferences)
        self.docTypeActions = docTypeActions


    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent!=None:
            opt=QtGui.QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox, opt, QtGui.QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)


    # def closeEvent(self, event):
    #     preferences = self.tblBlank.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CBlankComboBoxPopup', preferences)
    #     QtGui.QFrame.closeEvent(self, event)


    def eventFilter(self, watched, event):
        if watched == self.tblBlank:
            if event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                event.accept()
                index = self.tblBlank.currentIndex()
                self.tblBlank.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QFrame.eventFilter(self, watched, event)


    def setBlankIdList(self, idList, posToId):
        self.tblBlank.setIdList(idList, posToId)
        self.tblBlank.setFocus(QtCore.Qt.OtherFocusReason)


    def selectBlankCode(self, code):
        self.code = code
        self.emit(QtCore.SIGNAL('BlankCodeSelected(int)'), code)
        self.close()


    def getCurrentBlankCode(self):
        db = QtGui.qApp.db
        if self.docTypeActions:
            table = db.table('BlankActions_Moving')
        else:
            table = db.table('BlankTempInvalid_Moving')
        id = self.tblBlank.currentItemId()
        code = None
        if id:
            record = db.getRecordEx(table, [table['id']], [table['deleted'].eq(0), table['id'].eq(id)])
            if record:
                code = forceInt(record.value(0))
            return code
        return None


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblBlank_doubleClicked(self, index):
        if index.isValid():
            if (QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index)):
                code = self.getCurrentBlankCode()
                self.selectBlankCode(code)


class CBlankComboBoxActionsPopup(QtGui.QFrame, Ui_BlankComboBoxPopup):
    __pyqtSignals__ = ('BlankCodeSelected(String)',
                      )

    def __init__(self, parent = None, docTypeActions = False):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.tableModel = CBlankActionsTableModel(self) if docTypeActions else CBlankTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblBlank.setModel(self.tableModel)
        self.tblBlank.setSelectionModel(self.tableSelectionModel)
        self.code = None
        self.tblBlank.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CBlankComboBoxPopup', {})
        # self.tblBlank.loadPreferences(preferences)
        self.docTypeActions = docTypeActions


    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent!=None:
            opt=QtGui.QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox, opt, QtGui.QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)


    # def closeEvent(self, event):
    #     preferences = self.tblBlank.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CBlankComboBoxPopup', preferences)
    #     QtGui.QFrame.closeEvent(self, event)


    def eventFilter(self, watched, event):
        if watched == self.tblBlank:
            if event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                event.accept()
                index = self.tblBlank.currentIndex()
                self.tblBlank.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QFrame.eventFilter(self, watched, event)


    def setBlankIdList(self, idList, posToId):
        self.tblBlank.setIdList(idList, posToId)
        self.tblBlank.setFocus(QtCore.Qt.OtherFocusReason)


    def selectBlankCode(self, code):
        result = codeToTextForBlank(code, True)
        self.code = result
        self.emit(QtCore.SIGNAL('BlankCodeSelected(String)'), result)
        self.close()


    def getCurrentBlankCode(self):
        db = QtGui.qApp.db
        if self.docTypeActions:
            table = db.table('BlankActions_Moving')
            tableBlankTempInvalidParty = db.table('BlankActions_Party')
        else:
            table = db.table('BlankTempInvalid_Moving')
            tableBlankTempInvalidParty = db.table('BlankTempInvalid_Party')
        queryTable = tableBlankTempInvalidParty.innerJoin(table, table['blankParty_id'].eq(tableBlankTempInvalidParty['id']))
        id = self.tblBlank.currentItemId()
        code = None
        if id:
            record = db.getRecordEx(queryTable, [table['id']], [table['deleted'].eq(0), tableBlankTempInvalidParty['deleted'].eq(0), table['id'].eq(id)])
            if record:
                code = forceInt(record.value(0))
            return code
        return None


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblBlank_doubleClicked(self, index):
        if index.isValid():
            if (QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index)):
                code = self.getCurrentBlankCode()
                self.selectBlankCode(code)


class CBlankTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Серия', ['serial'], 30))
        self.addColumn(CTextCol(u'Номер с', ['numberFrom'], 20))
        self.addColumn(CTextCol(u'Номер по', ['numberTo'], 20))
        self.addColumn(CDateCol(u'Дата', ['date'], 10))
        self.addColumn(CTextCol(u'Получено', ['received'], 10))
        self.addColumn(CTextCol(u'Использовано', ['used'], 10))
        self.addColumn(CTextCol(u'Возврат', ['returnAmount'], 10))
        self.addColumn(CEnumCol(u'Контроль серии', ['checkingSerial'], [u'нет', u'мягко', u'жестко'], 5))
        self.addColumn(CEnumCol(u'Контроль номера', ['checkingNumber'], [u'нет', u'мягко', u'жестко'], 5))
        self.addColumn(CEnumCol(u'Контроль количества', ['checkingAmount'], [u'нет', u'использовано'], 5))
        self.setTable('BlankTempInvalid_Moving')


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable


    def setTable(self, tableName):
        db = QtGui.qApp.db
        tableRBBlankTempInvalids = db.table('rbBlankTempInvalids')
        tableBlankTempInvalidParty = db.table('BlankTempInvalid_Party')
        tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        loadFields = []
        loadFields.append(u'''DISTINCT BlankTempInvalid_Moving.id, BlankTempInvalid_Party.serial, BlankTempInvalid_Moving.numberFrom, BlankTempInvalid_Moving.numberTo, BlankTempInvalid_Moving.date, BlankTempInvalid_Moving.received, BlankTempInvalid_Moving.used, BlankTempInvalid_Moving.returnAmount, rbBlankTempInvalids.checkingSerial, rbBlankTempInvalids.checkingNumber, rbBlankTempInvalids.checkingAmount''')
        queryTable = tableBlankTempInvalidMoving.innerJoin(tableBlankTempInvalidParty, tableBlankTempInvalidParty['id'].eq(tableBlankTempInvalidMoving['blankParty_id']))
        queryTable = queryTable.innerJoin(tableRBBlankTempInvalids, tableBlankTempInvalidParty['doctype_id'].eq(tableRBBlankTempInvalids['id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, loadFields)


class CBlankActionsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Серия', ['serial'], 30))
        self.addColumn(CTextCol(u'Номер с', ['numberFrom'], 20))
        self.addColumn(CTextCol(u'Номер по', ['numberTo'], 20))
        self.addColumn(CDateCol(u'Дата', ['date'], 10))
        self.addColumn(CTextCol(u'Получено', ['received'], 10))
        self.addColumn(CTextCol(u'Использовано', ['used'], 10))
        self.addColumn(CTextCol(u'Возврат', ['returnAmount'], 10))
        self.addColumn(CEnumCol(u'Контроль серии', ['checkingSerial'], [u'нет', u'мягко', u'жестко'], 5))
        self.addColumn(CEnumCol(u'Контроль номера', ['checkingNumber'], [u'нет', u'мягко', u'жестко'], 5))
        self.addColumn(CEnumCol(u'Контроль количества', ['checkingAmount'], [u'нет', u'использовано'], 5))
        self.setTable('BlankActions_Moving')


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable


    def setTable(self, tableName):
        db = QtGui.qApp.db
        tableRBBlankActions = db.table('rbBlankActions')
        tableBlankActionsParty = db.table('BlankActions_Party')
        tableBlankActionsMoving = db.table('BlankActions_Moving')
        loadFields = []
        loadFields.append(u'''DISTINCT BlankActions_Moving.id, BlankActions_Party.serial, BlankActions_Moving.numberFrom, BlankActions_Moving.numberTo, BlankActions_Moving.date, BlankActions_Moving.received, BlankActions_Moving.used, BlankActions_Moving.returnAmount, rbBlankActions.checkingSerial, rbBlankActions.checkingNumber, rbBlankActions.checkingAmount''')
        queryTable = tableBlankActionsMoving.innerJoin(tableBlankActionsParty, tableBlankActionsParty['id'].eq(tableBlankActionsMoving['blankParty_id']))
        queryTable = queryTable.innerJoin(tableRBBlankActions, tableBlankActionsParty['doctype_id'].eq(tableRBBlankActions['id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, loadFields)

