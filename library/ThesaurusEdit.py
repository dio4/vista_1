# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.Utils           import *
from Events.Action import *

class CTreeView(QtGui.QTreeView):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.emit(SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
        else:
            QtGui.QTreeView.keyPressEvent(self, event)


class CThesaurusEditor(QtGui.QWidget):
    __pyqtSignals__ = ('editingFinished()',
                       'commit()',
                      )
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.gridlayout = QtGui.QGridLayout(self)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName('gridlayout')

        self.splitter = QtGui.QSplitter(self)
        self.splitter.setObjectName('splitter')
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setAutoFillBackground(True)

        self.treeView = CTreeView(self.splitter)
        self.treeView.setObjectName('treeView')
        self.domain = u''


    def getThesaurus(self, propertyType):
        db = QtGui.qApp.db
        table = db.table('rbThesaurus')
        tableAPT = db.table('ActionPropertyType')
        if propertyType == 1:
            name = u'Объективность'
        elif propertyType == 2:
            name = u'Слизистая'
        record = db.getRecordEx(tableAPT, [tableAPT['valueDomain']], [tableAPT['deleted'].eq(0), tableAPT['name'].like(name), tableAPT['typeName'].like(u'Constructor')])
        if record:
            self.domain = forceString(record.value('valueDomain'))
        rootItemIdCandidates = db.getIdList(table, 'id', [table['group_id'].isNull(), table['code'].eq(self.domain)], 'id')
        # если в корне не нашлось, ищем в прочих.
        if not rootItemIdCandidates:
            rootItemIdCandidates = db.getIdList(table, 'id', table['code'].eq(self.domain), 'id')
        rootItemId = rootItemIdCandidates[0] if rootItemIdCandidates else None
        self.treeModel = CDBTreeModel(self, 'rbThesaurus', 'id', 'group_id', 'name', order='code')
        self.treeModel.setRootItem(CDBTreeItem(None, self.domain, rootItemId, self.treeModel))
        self.treeModel.setRootItemVisible(False)
        self.treeModel.setLeavesVisible(True)
        self.treeView.setModel(self.treeModel)
        self.treeView.header().setVisible(False)
        self.textEdit = QtGui.QTextEdit(self.splitter)
        self.textEdit.setObjectName('textEdit')
        self.textEdit.setFocusPolicy(Qt.StrongFocus)
        self.textEdit.setTabChangesFocus(True)
        self.gridlayout.addWidget(self.splitter,0,0,1,1)
        self.setFocusProxy(self.treeView)
        self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
        self.textEdit.installEventFilter(self)
        self.treeView.installEventFilter(self)


    def eventFilter(self, widget, event):
        et = event.type()
        if et == QtCore.QEvent.FocusOut:
            fw = QtGui.qApp.focusWidget()
            if not (fw and self.isAncestorOf(fw)):
                self.emit(SIGNAL('editingFinished()'))
        elif et == QtCore.QEvent.Hide and widget == self.textEdit:
            self.emit(SIGNAL('commit()'))
        return QtGui.QWidget.eventFilter(self, widget, event)


    def focusNextPrevChild(self, next):
        if self.treeView.hasFocus() and next:
            self.textEdit.setFocus(Qt.TabFocusReason)
            return True
        elif self.textEdit.hasFocus() and not next:
            self.treeView.setFocus(Qt.BacktabFocusReason)
            return True
        # self.emit(SIGNAL('commit()'))
        self.setFocusProxy(self.textEdit if next else self.treeView)
        r = QtGui.QWidget.focusNextPrevChild(self, next)
        return True


    def setValue(self, value):
        v = forceString(value)
        self.textEdit.setPlainText(v)
        self.textEdit.moveCursor(QtGui.QTextCursor.End)

    def value(self):
        return unicode(self.textEdit.toPlainText())

    def setReadOnly(self, val):
        self.textEdit.setReadOnly(val)
        self.treeView.setEnabled(not val)

    def isReadOnly(self):
        return self.textEdit.isReadOnly()

    def on_doubleClicked(self, index):
        db = QtGui.qApp.db
        table = db.table('rbThesaurus')
        parts = []
        item = index.internalPointer()
        text = '%s'
        while item and item.id():
            template = forceString(db.translate(table, 'id', item.id(), 'template'))
            try:
                text = text % template
            except:
                break
            item = item.parent()
        try:
            text = text % ''
        except:
            pass
        cursor = self.textEdit.textCursor()
        if cursor.hasSelection():
            pos = cursor.selectionStart()
            cursor.removeSelectedText()
            cursor.setPosition(pos)
        elif cursorInPlaceholder(cursor):
            pass
        elif not cursor.atBlockStart():
            moveCursorToEndOfWord(cursor)
            if separatorBeforeCursor(cursor):
                cursor.insertText(' ')
            else:
                cursor.insertText(', ')
        cursor.insertText(removeUsedPrefix(cursor, text))
        self.textEdit.setTextCursor(cursor)

