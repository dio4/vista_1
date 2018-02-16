#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, getPref, setPref
from library.TableModel import CTableModel, CDateCol, CRefBookCol, CTextCol

from Ui_PriceListComboBoxPopup import Ui_PriceListComboBoxPopup


class CPriceListComboBoxPopup(QtGui.QDialog, Ui_PriceListComboBoxPopup):
    __pyqtSignals__ = ('PriceListCodeSelected(int)',
                      )

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent, QtCore.Qt.Popup)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.tableModel = CPriceListTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblPriceList.setModel(self.tableModel)
        self.tblPriceList.setSelectionModel(self.tableSelectionModel)
        self.date = None
        self.code = None
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CPriceListComboBoxPopup', {})
        # self.tblPriceList.loadPreferences(preferences)


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
        QtGui.QDialog.mousePressEvent(self, event)


    # def closeEvent(self, event):
    #     preferences = self.tblPriceList.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CPriceListComboBoxPopup', preferences)
    #     QtGui.QDialog.closeEvent(self, event)


    def eventFilter(self, watched, event):
        if watched == self.tblPriceList:
            if event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                event.accept()
                index = self.tblPriceList.currentIndex()
                self.tblPriceList.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QDialog.eventFilter(self, watched, event)


    def setPriceListIdList(self, idList, posToId):
        if idList:
            self.tblPriceList.setIdList(idList, posToId)
            self.tblPriceList.setFocus(QtCore.Qt.OtherFocusReason)


    def getPriceListIdList(self, priceListOnly):
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        if priceListOnly:
            idList = db.getDistinctIdList(tableContract, tableContract['priceList_id'].name(), [tableContract['deleted'].eq(0), tableContract['priceList_id'].isNotNull()], u'finance_id, grouping, resolution, number, date')
        else:
            idList = db.getDistinctIdList(tableContract, tableContract['id'].name(), [tableContract['deleted'].eq(0)], u'finance_id, grouping, resolution, number, date')
        return idList


    def setDate(self, date):
        self.tableModel.date = date


    def setPriceListCode(self, id, priceListOnly):
        crIdList = self.getPriceListIdList(priceListOnly)
        self.setPriceListIdList(crIdList, id if id else None)


    def selectPriceListCode(self, code):
        self.code = code
        self.emit(QtCore.SIGNAL('PriceListCodeSelected(int)'), self.code)
        self.close()


    def getCurrentPriceListCode(self):
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        id = self.tblPriceList.currentItemId()
        code = None
        if id:
            record = db.getRecordEx(tableContract, [tableContract['id']], [tableContract['deleted'].eq(0), tableContract['id'].eq(id)])
            if record:
                code = forceInt(record.value(0))
            return code
        return None


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPriceList_doubleClicked(self, index):
        if index.isValid():
            if (QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index)):
                code = self.getCurrentPriceListCode()
                self.selectPriceListCode(code)


class CPriceListTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CRefBookCol(u'Источник финансирования', ['finance_id'], 'rbFinance', 30),
            CTextCol(u'Группа',                  ['grouping'],  30),
            CTextCol(u'Основание',               ['resolution'],20),
            CTextCol(u'Номер',                   ['number'],    20),
            CDateCol(u'Дата',                    ['date'],      10),
            CDateCol(u'Нач.дата',                ['begDate'],   10),
            CDateCol(u'Кон.дата',                ['endDate'],   10)
            ], 'Contract' )
        self.date = QtCore.QDate.currentDate()


    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable
