#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from KLADR.KLADRModel import getKladrTreeModel, getAllSelectableKladrTreeModel, CStreetModel, getInsuranceAreaTreeModel
from KLADR.KLADRTree  import CKLADRTreePopup
from library.CComboBox import CComboBox

from library.Utils    import forceString, CIncremetalFilterHelper


class CKLADRComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
#        self._searchString = ''
        self._popupView = CKLADRTreePopup(self)
        self._popupView.setObjectName('CKladrComboBoxPopupView')
#        self.setView(self._popupView)
#        self._popupView.installEventFilter(self)
#        self._popupView.viewport().installEventFilter(self)
#        self.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
#        self.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.connect(self._popupView, QtCore.SIGNAL('codeSelected(QString)'), self.setCode)
        self.connect(self._popupView, QtCore.SIGNAL('codeSelected(QModelIndex)'), self.setIndex)
        self.setModelColumn(2)
        self._model = getKladrTreeModel()
        self.setModel(self._model)


    def setAreaSelectable(self, value=True):
        self._model.areaSelectable = value


    def getChildrenCodeList(self, code=None):
        if code is None:
            return None
        return self._model.getChildrenCodeList(code)


    def showPopup(self):
        pos = self.mapToGlobal(self.rect().bottomLeft())
        pos2 = self.mapToGlobal(self.rect().topLeft())
        size=self._popupView.sizeHint()
#        size.setWidth(self.rect().width()+20) # magic. похоже, что sizeHint считается неправильно. русские буквы виноваты?
        size.setWidth(self.width()) # magic. похоже, что sizeHint считается неправильно. русские буквы виноваты?
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popupView.resize(size)
        self._popupView.move(pos)
        self._popupView.beforeShow()
        self._popupView.setCurrentIndex(self._model.index(self.currentIndex(), 0, self.rootModelIndex()))
        self._popupView.show()


    def setIndex(self, index):
        self.setCurrentIndex(index)


    def setCode(self, code):
        index = self._model.findCode(code)
        self.setIndex(index)


    def code(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        return self._model.code(modelIndex)

    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def setCurrentIndex(self, index):
        self.setRootModelIndex(index.parent())
        super(CKLADRComboBox, self).setCurrentIndex(index.row())
        self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Equal:
            kladr = QtGui.qApp.defaultKLADR()
            if kladr:
                self.setCode(kladr)
            event.accept()
        elif event.key() == QtCore.Qt.Key_Plus:
            kladr = QtGui.qApp.provinceKLADR()
            if kladr:
                self.setCode(kladr)
            event.accept()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress: # and obj == self._popupView :
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select):
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
        return False

class CAllSelectableKLADRComboBox(CKLADRComboBox):
    def __init__(self, parent):
        CKLADRComboBox.__init__(self, parent)
        self._model = getAllSelectableKladrTreeModel()
        self.setModel(self._model)
        self._popupView.treeModel = self._model
        self._popupView.treeView.setModel(self._model)

class CInsuranceAreaKLADRComboBox(CKLADRComboBox):
    def __init__(self, parent):
        CKLADRComboBox.__init__(self, parent)
        self._model = getInsuranceAreaTreeModel()
        self.setModel(self._model)
        self._popupView.treeModel = self._model
        self._popupView.treeView.setModel(self._model)

#######################################################################################



class CStreetComboBox(CComboBox):
    def __init__(self, parent):
        CComboBox.__init__(self, parent)

        self.setMinimumContentsLength(20)
        self._model = CStreetModel(self)
        self.setEditable(True)
        
        self._proxyModel = QtGui.QSortFilterProxyModel()
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._proxyModel.setFilterKeyColumn(0)
        self.setModel(self._model)
        
        self._filterHelper = CIncremetalFilterHelper()
        self.connect(self.lineEdit(), QtCore.SIGNAL('textEdited(QString)'), self._filterHelper.filteredStringChanged)
        self._filterHelper.filterApplied.connect(self.applyFilter)
        self._completer = QtGui.QCompleter(self._proxyModel, self)
        self._completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self._completer)
        self.connect(self._completer, QtCore.SIGNAL('activated(QModelIndex)'), self.on_completer_activated)

    def sizeHint(self):
        return QtCore.QSize(20, 20)
    
    
    def setAddNone(self, flag):
        self._model.setAddNone(flag)


    def setPrefix(self, prefix):
        self._model.setPrefix(prefix)


    def setCity(self, city):
        self.setPrefix(city[0:-2])


    def setCode(self, code):
        rowIndex = self._model.indexByCode(code)
        self.setCurrentIndex(rowIndex)


    def addNone(self, flag):
        self._model


    def code(self):
        rowIndex = self.currentIndex()
        return self._model.code(rowIndex)
    
    
    def focusOutEvent(self, event):
        QtGui.QComboBox.focusOutEvent(self, event)
        if self.currentText() != self.itemText(self.currentIndex()):
            completerIndex = self._completer.popup().currentIndex()
            if completerIndex.isValid():
                self.on_completer_activated(completerIndex)
            elif self._completer.popup().model().rowCount() > 0:
                self.on_completer_activated(self._completer.popup().model().index(0, 
                                                                                  self._completer.completionColumn()))
            else:
                self.setCurrentIndex(self.currentIndex())
        
    
    @QtCore.pyqtSlot()
    def applyFilter(self):
        self._proxyModel.setFilterFixedString(self.currentText())
        
    

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.setCode(None)
        else:
            QtGui.QComboBox.keyPressEvent(self, event)
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_completer_activated(self, index):
        sourceIndex = self._proxyModel.mapToSource(self._proxyModel.index(index.row(), index.column()))
        self.setCurrentIndex(sourceIndex.row())

class CMainRegionsKLADRComboBox(CComboBox):
    def __init__(self, parent):
        CComboBox.__init__(self, parent)
        self.cacheIndexByCode = {}
        self.loadKLADRItems()

    def loadKLADRItems(self):
        self.addItem('', QtCore.QVariant())
        records = QtGui.qApp.db.getRecordList('kladr.KLADR', 'NAME, CODE',
                                       'parent=\'\' AND RIGHT(CODE,2)=\'00\'',
                                       'NAME, SOCR, CODE')
        for record in records:
            self.addItem(forceString(record.value('NAME')), record.value('CODE'))
            self.cacheIndexByCode[forceString(record.value('CODE'))] = self.count()-1

    def getIndexByCode(self, code):
        return self.cacheIndexByCode.get(code, None)
