#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CTextCol

from Ui_ActionTypeDialog import Ui_ActionTypeDialog


class CActionTypeDialog(CDialogBase, Ui_ActionTypeDialog):

    def __init__(self, parent, cols, tableName, order, forSelect=False, filterClass=None, idList=None):
        if not idList:
            idList = []
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.filterClass = filterClass
        self.props = {}
        self.order = order
        self.model = CTableModel(self, cols, tableName)
        self.model.setIdList(idList)
        self.tblActionType.setModel(self.model)
        if idList:
            self.tblActionType.selectRow(0)


    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblActionType.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblActionType.currentItemId()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblListWidget_doubleClicked(self, index):
        pass


class CActionTypeDialogTableModel(CActionTypeDialog):
    def __init__(self, parent, idList):
        CActionTypeDialog.__init__(self, parent, [
            CTextCol(u'Код', ['code'],  20),
            CTextCol(u'Наименование действия', ['name'], 40),
            CTextCol(u'"Плоский" код', ['flatCode'], 10)
            ], 'ActionType', ['id'], False, None, idList)

