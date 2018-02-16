# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.ReportsConstructor.RCTreeView import CRCTreeView


class CRCFieldTreeView(CRCTreeView):
    def __init__(self, parent):
        CRCTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
        self.searchString = ''
        self.searchParent = None

        self.actConnect = QtGui.QAction(u'Подключить', self)
        self.actConnectLeft = QtGui.QAction(u'Подключить (left)', self)
        self.actAddSubTable = QtGui.QAction(u'Добавить дополнительную таблицу', self)
        self.actDisconnect = QtGui.QAction(u'Отключить', self)
        self.actChangeSubTable = QtGui.QAction(u'Изменить дополнительную таблицу', self)

        self.connect(self.actConnect, QtCore.SIGNAL('triggered()'), self.on_actConnect_triggered)
        self.connect(self.actConnectLeft, QtCore.SIGNAL('triggered()'), self.on_actConnectLeft_triggered)
        self.connect(self.actAddSubTable, QtCore.SIGNAL('triggered()'), self.on_actAddSubTable_triggered)
        self.connect(self.actDisconnect, QtCore.SIGNAL('triggered()'), self.on_actDisconnect_triggered)
        self.connect(self.actChangeSubTable, QtCore.SIGNAL('triggered()'), self.on_actChangeSubTable_triggered)

        self.createPopupMenu([self.actConnect, self.actConnectLeft, self.actDisconnect, self.actAddSubTable, self.actChangeSubTable])
        self.controlPress = False


    def setModel(self, model):
        QtGui.QTreeView.setModel(self, model)
        self.expandAll()

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()

    def popupMenuAboutToShow(self):
        hasReference = self.checkItemHasReference(self.currentIndex())
        hasChild = self.checkItemHasChildren(self.currentIndex())
        self.actConnect.setVisible(hasReference and not hasChild)
        self.actConnectLeft.setVisible(hasReference and not hasChild)
        self.actDisconnect.setVisible(hasReference and hasChild)
        self.actAddSubTable.setVisible(True)

    def checkItemHasReference(self, index):
        item = index.internalPointer()
        if not item:
            return False
        currentItemId = item.baseId()
        return self.model().checkItemHasReference(currentItemId)

    def checkItemHasChildren(self, index):
        item = index.internalPointer()
        if not item:
            return False
        return bool(item._items)


    def on_actConnect_triggered(self):
        currentIndex = self.currentIndex()
        self.model().extendItem(currentIndex)
        self.reset()

    def on_actConnectLeft_triggered(self):
        currentIndex = self.currentIndex()
        self.model().extendItem(currentIndex, type='left')
        self.reset()

    def on_actDisconnect_triggered(self):
        currentIndex = self.currentIndex()
        self.model().diconnectChildItem(currentIndex)
        self.reset()

    def on_actAddSubTable_triggered(self):
        from Reports.ReportsConstructor.RCQueryEdit import CRCQueryEditorDialog
        dialog = CRCQueryEditorDialog(self, self.model(), self.currentIndex())
        if dialog.exec_():
            self.model().addSubQuery(dialog._id)

    def on_actChangeSubTable_triggered(self):
        from Reports.ReportsConstructor.RCQueryEdit import CRCQueryEditorDialog
        currentIndex = self.currentIndex()
        dialog = CRCQueryEditorDialog(self, self.model(), currentIndex)
        item = currentIndex.internalPointer()
        if item:
            dialog.load(item.tableId())
        if dialog.exec_():
            self.model().changeSubQuery(dialog._id, currentIndex)


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
        if event.key() == QtCore.Qt.Key_Control:
            self.controlPress = True

        return QtGui.QTreeView.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.controlPress = False
        return QtGui.QTreeView.keyReleaseEvent(self, event)

    def mousePressEvent(self, event):
        if self.controlPress:
            self.emit(QtCore.SIGNAL('AdvanceSelection()'))
        else:
            self.emit(QtCore.SIGNAL('AdvanceSelectionClear()'))

class RCRFieldsPopup(QtGui.QFrame):
    __pyqtSignals__ = ('templateSelected(int)',
                       'closePopup()',
                      )

    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.treeView=CRCFieldTreeView(self)
        self.widgetLayout = QtGui.QVBoxLayout(self)
        self.widgetLayout.setMargin(0)
        self.widgetLayout.setSpacing(0)
        self.widgetLayout.addWidget(self.treeView)
        self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
        self.setLayout(self.widgetLayout)
        self.treeView.setFocus()


    def setModel(self, model):
        self._model = model
        self.treeView.setModel(self._model)

    def on_doubleClicked(self, index):
        item = index.internalPointer()
        self.emit(QtCore.SIGNAL('templateSelected(int)'), item.id())
        self.close()


    def mousePressEvent(self, event):
        p = self.parentWidget()
        if p!=None:
            rect = p.rect()
            rect.moveTo(p.mapToGlobal(rect.topLeft()))
            if (rect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
#        self.emit(QtCore.SIGNAL('resetButton()'))
        self.parent().mouseReleaseEvent(event)
        pass


#    def event(self, event):
#        if event.type()==QEvent.KeyPress:
#            if event.key()==Qt.Key_Escape:
#                self.dateChanged = False
#        return QFrame.event(self, event)

    def hideEvent(self, event):
        self.emit(QtCore.SIGNAL('closePopup()'))


# ===================================================================================

class CRCFieldsComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._popupView = CRCFieldTreeView(self)
        self._popupView.setObjectName('popupView')
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('AdvanceSelection()'), self.on_AdvanceSelection)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('AdvanceSelectionClear()'), self.on_AdvanceSelectionClear)
        self.prefferedWidth = 0
        self._checkIndexes = set()

    def setModel(self, model):
        self._model = model
        QtGui.QComboBox.setModel(self, self._model)
        self._popupView.setModel(self._model)

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def update(self):
        self._model.update()

    def on_AdvanceSelection(self):
        index = self._popupView.currentIndex()
        if not index.isValid():
            return
        item = index.internalPointer()
        if index in self._checkIndexes:
            item.setSelected(False)
            self._checkIndexes.discard(index)
        else:
            item.setSelected(True)
            self._checkIndexes.add(index)

    def on_AdvanceSelectionClear(self):
        for index in self._checkIndexes:
            index.internalPointer().setSelected(False)
        if self._checkIndexes:
            self._popupView.reset()
            self._checkIndexes = set()

    def setValue(self, value):
        #TODO исправить
        index = self._model.getIndexByPath(value)
        self.setCurrentIndex(index)
        self._popupView.setCurrentIndex(index)

    def getValue(self, index):
        if index.isValid():
            return self._model.forceString(self._model.getItem(index))
        return None

    def value(self):
        if self._checkIndexes:
            self._checkIndexes = list(self._checkIndexes)
            self._checkIndexes.sort(key=lambda index: index.row())
            value = [self.getValue(index) for index in self._checkIndexes]
            self.on_AdvanceSelectionClear()
        else:
            value = [self.getValue(self._popupView.currentIndex())]
        return value

    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
#                print self.__popupView.isExpanded(index)
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def showPopup(self):
#        self.__searchString = ''
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())

        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        self._popupView.expandAll()
        prefferedWidth = self._popupView.sizeHint().width()
        prefferedWidth = max(self.prefferedWidth if self.prefferedWidth else 0, self._popupView.sizeHint().width())
        if prefferedWidth:
            if self.width() < prefferedWidth:
                self._popupView.setFixedWidth(prefferedWidth)
        self._popupView.setFixedHeight(400)
        QtGui.QComboBox.showPopup(self)
        scrollBar = self._popupView.horizontalScrollBar()
        scrollBar.setValue(0)

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
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
#            print 'default for ',event.key()
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
#        return QtGui.QComboBox.eventFilter(self, obj, event)
        return False

class CRCComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self._model = None

    def setModel(self, model):
        self._model = model
        QtGui.QComboBox.setModel(self, self._model)

    def value(self):
        index = self.currentIndex()
        return self._model.getItemId(index)

    def setValue(self, value):
        self.setCurrentIndex(self._model.getIndexById(value))

    def index(self):
        return self.currentIndex()

    def setIndex(self, row):
        self.setCurrentIndex(row)