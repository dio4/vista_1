# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.CComboBox import CComboBox, CComboBoxPopupTreeView
from library.TreeModel import CDBTreeModel


class CSocStatusTreeView(CComboBoxPopupTreeView):
    def __init__(self, parent):
        CComboBoxPopupTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
        self.searchString = ''
        self.searchParent = None

    def setModel(self, model):
        CComboBoxPopupTreeView.setModel(self, model)
        self.expandAll()

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        CComboBoxPopupTreeView.setRootIndex(self, index)

    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Minus:
            current = self.currentIndex()
            if self.isExpanded(current) and self.model().rowCount(current):
                self.collapse(current)
            else:
                self.setCurrentIndex(current.parent())
                current = self.currentIndex()
                self.collapse(current)
                self.scrollTo(current, QtGui.QAbstractItemView.PositionAtTop)
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
            return
        return CComboBoxPopupTreeView.keyPressEvent(self, event)


class CSocStatusPopup(QtGui.QFrame):
    __pyqtSignals__ = ('templateSelected(int)',
                       'closePopup()',
                       )

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.treeView = CSocStatusTreeView(self)
        self.connect(self.treeView, QtCore.SIGNAL('hide()'), self.hideEvent)
        self.widgetLayout = QtGui.QVBoxLayout(self)
        self.widgetLayout.setMargin(0)
        self.widgetLayout.setSpacing(0)
        self.widgetLayout.addWidget(self.treeView)
        self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
        self.setLayout(self.widgetLayout)
        self.treeView.setFocus()

    def on_doubleClicked(self, index):
        item = index.internalPointer()
        self.emit(QtCore.SIGNAL('templateSelected(int)'), item.id())
        self.close()

    def mousePressEvent(self, event):
        p = self.parentWidget()
        if p is not None:
            rect = p.rect()
            rect.moveTo(p.mapToGlobal(rect.topLeft()))
            if rect.contains(event.globalPos()) or self.rect().contains(event.pos()):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        # self.emit(QtCore.SIGNAL('resetButton()'))
        self.parent().mouseReleaseEvent(event)
        pass

    # def event(self, event):
    #     if event.type()==QEvent.KeyPress:
    #         if event.key()==Qt.Key_Escape:
    #             self.dateChanged = False
    #     return QFrame.event(self, event)

    def hideEvent(self, event):
        self.emit(QtCore.SIGNAL('closePopup()'))


# ===================================================================================

class CSocStatusComboBox(CComboBox):
    def __init__(self, parent):
        CComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._model = CDBTreeModel(self, 'rbSocStatusClass', 'id', 'group_id', 'name', ['code', 'name', 'id'])
        self._model.setLeavesVisible(True)
        self._model.setOrder('code')
        self.setModel(self._model)
        self._popupView = CSocStatusTreeView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.connect(self._popupView, QtCore.SIGNAL('hide()'), self.hidePopup)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.prefferedWidth = 0

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def update(self):
        self._model.update()

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
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def showPopup(self):
        # self.__searchString = ''
        # modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())

        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        self._popupView.expandAll()
        # prefferedWidth = self._popupView.sizeHint().width()
        prefferedWidth = max(self.prefferedWidth if self.prefferedWidth else 0, self._popupView.sizeHint().width())
        if prefferedWidth:
            if self.width() < prefferedWidth:
                self._popupView.setFixedWidth(prefferedWidth)
        QtGui.QComboBox.showPopup(self)
        scrollBar = self._popupView.horizontalScrollBar()
        scrollBar.setValue(0)

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            self.setRootModelIndex(index.parent())
            QtGui.QComboBox.setCurrentIndex(self, index.row())

        # self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:  # and obj == self.__popupView :
            if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select]:
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        # return QtGui.QComboBox.eventFilter(self, obj, event)
        return False
