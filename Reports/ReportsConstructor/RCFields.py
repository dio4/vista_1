# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.Utils                       import forceBool
from library.DialogBase                  import CDialogBase
from Reports.ReportsConstructor.models.RCFieldsTreeModel import CQueryFieldsTreeModel
from Ui_RCFieldsItemTreeDialog           import Ui_Dialog
from s11main import CS11mainApp

class CQueryFieldsList(CDialogBase, Ui_Dialog):
    def __init__(self, parent, model):
        CDialogBase.__init__(self, parent)
        self.addModels('Tree', model)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Структура полей')
        self.expandedItemsState = {}


    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.modelTree.setLeavesVisible(True)

        self.actExtend = QtGui.QAction(u'Подключить', self)

        self.actExtend.setObjectName('actExtend')
        self.actTest =   QtGui.QAction(u'Test', self)
        self.actTest.setObjectName('actTest')


    def postSetupUi(self):
        self.setModels(self.treeItems,  self.modelTree,  self.selectionModelTree)
        self.treeItems.header().hide()
        # tree popup menu
        self.treeItems.createPopupMenu([self.actExtend, self.actTest])
        self.connect(self.treeItems.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)

        self.connect(self.modelTree, QtCore.SIGNAL('saveExpandedState()'),  self.saveExpandedState)
        self.connect(self.modelTree, QtCore.SIGNAL('restoreExpandedState()'),  self.restoreExpandedState)


    def popupMenuAboutToShow(self):
        currentItemId = self.getCurrentItemId()
        enable = forceBool(self.modelTree._items.get(currentItemId, {}).get('refId', ''))
        self.actExtend.setEnabled(enable)

    def getCurrentItemId(self):
        return self.treeItems.currentIndex().internalPointer().id()

    def saveExpandedState(self):
        def saveStateInternal(model,  parent=QtCore.QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.treeItems.isExpanded(index)
                        self.expandedItemsState[prefix] = isExpanded
                        if isExpanded:
                            saveStateInternal(model,  index, prefix)
        self.expandedItemsState = {}
        saveStateInternal(self.modelTree)


    def restoreExpandedState(self):
        def restoreStateInternal(model,  parent=QtCore.QModelIndex(),  prefix=''):
            for column in xrange(model.columnCount(parent)):
                for row in xrange(model.rowCount(parent)):
                    index = model.index(row, column,  parent)
                    if index.isValid():
                        prefix += index.internalPointer().name() + '_'
                        isExpanded = self.expandedItemsState.get(prefix,  False)
                        if isExpanded:
                            self.treeItems.setExpanded(index, isExpanded)
                            restoreStateInternal(model,  index, prefix)
        restoreStateInternal(self.modelTree)
        self.expandedItemsState.clear()

    def getCurrentItem(self):
        return self.modelTree.getItem(self.treeItems.currentIndex())

    def setCurrentIndex(self, row):
        self.treeItems.model().createIndex(row, 0, None)

    @QtCore.pyqtSlot()
    def on_actExtend_triggered(self):
        currentIndex = self.treeItems.currentIndex()
        idx = self.modelTree.parent(currentIndex)
        self.modelTree.extendItem(currentIndex)
        self.saveExpandedState()
        self.treeItems.reset()
        self.restoreExpandedState()
        self.treeItems.setCurrentIndex(idx)

    @QtCore.pyqtSlot()
    def on_actTest_triggered(self):
        currentIndex = self.treeItems.currentIndex()
        self.modelTree.getItem(currentIndex)


def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 229917

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pes',
                      'port' : 3306,
                      'database' : 's12',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CQueryFieldsList(None, CQueryFieldsTreeModel(None)).exec_()


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()