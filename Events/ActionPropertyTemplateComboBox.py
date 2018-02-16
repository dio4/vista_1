# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui
from library.TreeModel import CTreeItemWithId, CTreeModel
from library.Utils import forceInt, forceString


class CActionPropertyTemplateTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, name):
        CTreeItemWithId.__init__(self, parent, name, id)


    def loadChildren(self):
        result = []
        db = QtGui.qApp.db
        table = db.table('ActionPropertyTemplate')
        cond = [table['group_id'].eq(self._id)]
        query = db.query(db.selectStmt(table, 'id, name', where=cond, order='name'))
        while query.next():
            record = query.record()
            id   = forceInt(record.value('id'))
            name = forceString(record.value('name'))
            result.append(CActionPropertyTemplateTreeItem(self, id, name))
        return result


class CActionPropertyTemplateRootTreeItem(CActionPropertyTemplateTreeItem):
    def __init__(self):
        CActionPropertyTemplateTreeItem.__init__(self, None, None, u'-')




class CActionPropertyTemplateModel(CTreeModel):
    def __init__(self, parent=None):
        CTreeModel.__init__(self, parent, CActionPropertyTemplateRootTreeItem())


#    def headerData(self, section, orientation, role):
#        if role == QtCore.Qt.DisplayRole:
#            return QtCore.QVariant(u'Шаблоны свойств')
#        return QtCore.QVariant()


class CActionPropertyTemplatePopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
#        self.connect(self, QtCore.SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None


#    def setModel(self, model):
#        QtGui.QTreeView.setModel(self, model)
#        self.expandAll()

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)
#        self.searchString = ''

#    def onCollapsed(self, index):
#        self.searchString = ''


#    def resizeEvent(self, event):
#        QtGui.QTreeView.resizeEvent(self, event)
#        self.resizeColumnToContents(0)

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Left or event.key() == Qt.Key_Minus:
#            current = self.currentIndex()
#            if self.isExpanded(current) and self.model().rowCount(current):
#                self.collapse(current)
#            else:
#                self.setCurrentIndex(current.parent())
#                current = self.currentIndex()
#                self.collapse(current)
#                self.scrollTo(current, QtGui.QAbstractItemView.PositionAtTop)
#            event.accept()
#            return
#        if event.key() == Qt.Key_Back:
#            self.searchString = self.searchString[:-1]
#            event.accept()
#            return
#
#        return QtGui.QTreeView.keyPressEvent(self, event)


#    def keyboardSearch(self, search):
#        current = self.currentIndex()
#        if current.parent() != self.searchParent:
#            self.searchString = u''
#        searchString = self.searchString + unicode(search)
#        QtGui.QTreeView.keyboardSearch(self, searchString)
#        if current != self.currentIndex():
#            self.searchString = searchString
#        self.searchParent = self.currentIndex().parent()
##        rowIndex = self.model().searchCode(search)
##        if rowIndex>=0 :
##            index = self.model().index(rowIndex, 1)
##            self.setCurrentIndex(index);


class CActionPropertyTemplateComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
#        self.__searchString = ''
        self._model = CActionPropertyTemplateModel(self)
        self.setModel(self._model)
        self._popupView = CActionPropertyTemplatePopupView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)


    def setValue(self, id):
        index = self._model.findItemId(id)
        self.setCurrentIndex(index)


    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))


    def showPopup(self):
#        self.__searchString = ''
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        self._popupView.expandToDepth(0)
        QtGui.QComboBox.showPopup(self)
#        self._popupView.setCurrentIndex(modelIndex)


    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        QtGui.QComboBox.setCurrentIndex(self, index.row())
#        self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress: # and obj == self.__popupView :
            if event.key() in [ QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
#        return QtGui.QComboBox.eventFilter(self, obj, event)
        return False
