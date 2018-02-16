# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox import CRBComboBox
from library.InDocTable  import CRBInDocTableCol

from Ui_TestComboBoxPopup import Ui_TestComboBoxPopupForm


class CTestPopup(QtGui.QFrame, Ui_TestComboBoxPopupForm):
    __pyqtSignals__ = ('testRowSelected(int)',
                       'updateTestFilter()'
                      )
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setupUi(self)
        self.cmbTestGroup.setTable('rbTestGroup', addNone=True)
        
    def setModels(self, model, selectionModel):
        self.tblTests.setModel(model)
        self.tblTests.setSelectionModel(selectionModel)
        self.tblTests.hideColumn(2)
        
    def view(self):
        return self.tblTests
        
    def testGroupId(self):
        return self.cmbTestGroup.value()
        
    def emitUpdateTestFilter(self):
        self.emit(QtCore.SIGNAL('updateTestFilter()'))
        
    def emitTestRowSelected(self, row):
        if not row is None:
            self.emit(QtCore.SIGNAL('testRowSelected(int)'), row)
        
    @QtCore.pyqtSlot(int)
    def on_cmbTestGroup_currentIndexChanged(self, index):
        self.emitUpdateTestFilter()
        
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTests_clicked(self, index):
        if index.isValid():
            self.emitTestRowSelected(index.row())
        
        
class CTestComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self.popupView  = CTestPopup(self)
        self.popupView.setModels(self._model, self._selectionModel)
        self._tableName = 'rbTest'
        self._additionalFilter = None
        CRBComboBox.setTable(self, self._tableName, addNone=False)
        self.connect(self.popupView, QtCore.SIGNAL('testRowSelected(int)'), self.on_popupView_testRowSelected)
        self.connect(self.popupView, QtCore.SIGNAL('updateTestFilter()'), self.on_popupView_updateTestFilter)
        
    def setAdditionalFilter(self, additionalFilter):
        self._additionalFilter = additionalFilter
        
    def showPopup(self):
        totalItems = self._model.rowCount()
        if totalItems>0:
            self._searchString = ''
            view = self.popupView.view()
            selectionModel = view.selectionModel()
            selectionModel.setCurrentIndex(self._model.index(self.currentIndex(), 1),
                                                 QtGui.QItemSelectionModel.ClearAndSelect)
            sizeHint = view.sizeHint()
            maxVisibleItems = self.maxVisibleItems()
            visibleItems = min(maxVisibleItems, totalItems)
            if visibleItems>0:
                view.setFixedHeight( view.rowHeight(0)*visibleItems )

            prefferedWidth = sizeHint.width()
            if self.prefferedWidth:
                prefferedWidth = max(self.prefferedWidth, prefferedWidth)
            prefferedWidth = max(prefferedWidth, self.width())
            frame = view.parent()
            frame.resize( prefferedWidth, view.height())
            # выравниваем по месту
            comboRect = self.rect()
            popupTop = 0
            popupLeft = 0
            screen = QtGui.qApp.desktop().screenGeometry(self)
            below = self.mapToGlobal(comboRect.bottomLeft())
            above = self.mapToGlobal(comboRect.topLeft())
            if screen.bottom() - below.y() >= view.height():
                popupTop = below.y()
            elif above.y() - screen.y() >= view.height():
                popupTop = above.y()-view.height()-2*frame.frameWidth()
            else:
                popupTop = max(screen.top(), screen.bottom()-view.height()-frame.frameWidth())
            if screen.right() - below.x() >= view.width():
                popupLeft = below.x()
            else:
                popupLeft = max(screen.left(), screen.right()-view.width()-frame.frameWidth())
            frame.move(popupLeft, popupTop)
            frame.show()
            view.setFocus()
            scrollBar = view.horizontalScrollBar()
            scrollBar.setValue(0)
            
    def setTable(self, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True):
        self._tableName = tableName
        self._addNone   = addNone
        self._filier    = filter
        self._order     = order
        self._needCache = needCache
        self._specialValues = specialValues
        _filter = []
        if self._filier:
            _filter.append(self._filier)
        if self._additionalFilter:
            _filter.append(self._additionalFilter)
        filter = QtGui.qApp.db.joinAnd(_filter)
        self._model.setTable(tableName, addNone, filter, order, specialValues, needCache)
            
    def on_popupView_testRowSelected(self, row):
        self.setCurrentIndex(row)
        self.popupView.hide()
        
    def on_popupView_updateTestFilter(self):
        testGroupId = self.popupView.testGroupId()
        filter = 'testGroup_id=%d'%testGroupId if testGroupId else None
        self.setFilter(filter)
        
class CRBTestCol(CRBInDocTableCol):
    def createEditor(self, parent):
        editor = CTestComboBox(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order = self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor
