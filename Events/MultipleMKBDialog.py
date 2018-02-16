#-*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4          import QtCore, QtGui

from library.ICDCodeEdit import CICDCodeEditEx
from library.ItemsListDialog import CItemEditorBaseDialog
from library.Utils import forceString, toVariant

from Ui_MultipleMKBDialog import Ui_MultipleMKBDialog


class CMultipleMKBListModel(QtCore.QAbstractTableModel):
    __pyqtSignals__ = ('amountChanged(int)',
                      )
    def __init__(self, data,  parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.arrayData = data

    def setData(self,  data,  index,  role=QtCore.Qt.EditRole, presetAction=None):
        if role==QtCore.Qt.EditRole:
            if index.row() == len(self.arrayData) and data.toString():
                self.addRow()
                self.arrayData.append(data.toString())
            elif data.toString():
                self.arrayData[index.row()] = data.toString()
            elif index.row() < len(self.arrayData):
                
                self.arrayData.removeAt(index.row())
                self.removeRows(index.row(),  1)
            self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
            self.emitItemsCountChanged()
        return True
        
    def emitItemsCountChanged(self):
        self.emit(QtCore.SIGNAL('itemsCountChanged()'))
        
    def setArrayData(self,  array):
        self.arrayData = array
        for i in range(len(array)):
            self.addRow()
        index = QtCore.QModelIndex()
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
        self.emitItemsCountChanged()
    
    def addRow(self, presetAction=None):
        index = QtCore.QModelIndex()
        cnt = len(self.arrayData)+1
        self.beginInsertRows(index, cnt, cnt)
        self.insertRows(cnt, 1, index)
        self.endInsertRows()
        return cnt-1
        
    def removeRows(self, row, count,  parentIndex = QtCore.QModelIndex()):
        self.beginRemoveRows(parentIndex, row, row+count-1)
        #if not count:
         #   self.arrayData.removeAt(row)
        #else:
        #    pass
        #del self._items[row:row+count]
        self.endRemoveRows()
        return True
        
    def getData(self):
        return self.arrayData
    
    def rowCount(self,  parent):
        return len(self.arrayData) + 1
    
    def columnCount(self,  parent):
        return 1
        
    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(u'Код МКБ')
        return QtCore.QVariant()
        
    def data(self,  index,  role):
        row = index.row()
        if row<len(self.arrayData):
            if role == QtCore.Qt.EditRole:
                return QtCore.QVariant(self.arrayData[index.row()])
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.arrayData[index.row()])
        else:
            return QtCore.QVariant()
            
    def flags(self, index = QtCore.QModelIndex()):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
    

class CMKBTableDelegate(QtGui.QItemDelegate):
    class CMKBPropEditor(CICDCodeEditEx):
        pyqtSignals__ = ('editingFinished()',
                           'commit()',
                          )
                          
        def __init__(self, parent):
            CICDCodeEditEx.__init__(self, parent)
            self._lineEdit.installEventFilter(self)
            
        def setValue(self, value):
            v = forceString(value)
            self.setText(v)
            
        def value(self):
            return unicode(self.text())
            
        def eventFilter(self, widget, event):
            et = event.type()
            if et == QtCore.QEvent.FocusOut:
                fw = QtGui.qApp.focusWidget()
                if not (fw and self.isAncestorOf(fw)):
                    self.emit(QtCore.SIGNAL('editingFinished()'))
            elif et == QtCore.QEvent.Hide and widget == None: # == self.textEdit:
                self.emit(QtCore.SIGNAL('commit()'))
            return QtGui.QWidget.eventFilter(self, widget, event)
    
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)
        self.parent = parent
        
    def createEditor(self, parent, option, index):
        model = index.model()
        row = index.row()
        editor = self.CMKBPropEditor(parent)
        return editor
        
        
    def setEditorData(self, editor, index):
        model = index.model()
        value = model.data(index, QtCore.Qt.EditRole)
        editor.setValue(value)
        
    def setModelData(self, editor, model, index):
        model = index.model()
        value = editor.value()
        model.setData(toVariant(value),  index)

class CMultipleMKBDialog(CItemEditorBaseDialog,  Ui_MultipleMKBDialog):
    def __init__(self, action=None,  valueType=None,  parent=None,  *args):
        CItemEditorBaseDialog.__init__(self, parent,  'Event')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.tableData = []
        self.delegate = CMKBTableDelegate(self)
        self.addModels('MKBTable', CMultipleMKBListModel(self.tableData,  self))
        self.tblMultipleMKB.setModel(self.modelMKBTable)
        self.tblMultipleMKB.setItemDelegate(self.delegate)
        self.tblMultipleMKB.setColumnWidth(0,  self.tblMultipleMKB.size().width()-15)
        self.setFixedSize(251, 314)
       # self.tblMultipleMKB.installEventFilter(self)
        
    def setTitle(self, title):
        self.setWindowTitle(title)

    def eventFilter(self, widget, event):
        et = event.type()
        if et == QtCore.QEvent.FocusOut:
            fw = QtGui.qApp.focusWidget()
        if not (fw and self.isAncestorOf(fw)):
            self.emit(QtCore.SIGNAL('editingFinished()'))
        elif et == QtCore.QEvent.Hide and widget == None: # == self.textEdit:
            self.emit(QtCore.SIGNAL('commit()'))
        return QtGui.QWidget.eventFilter(self, widget, event)
    
    def setValue(self, value):
        v = value.toString()
        if v:
            self.tableData = v.split(',')
        else:
            self.tableData = QtCore.QStringList()
        self.modelMKBTable.setArrayData(self.tableData)
        #self.modelMKBTable.reset()
        
    def value(self):
        self.tableData = QtCore.QStringList(self.modelMKBTable.getData())
        self.tableData.removeDuplicates()
        if self.tableData:
            return unicode(self.tableData.join(','))
        else: 
            return unicode('')
       
        
    def setStatusTip(self,  string):
        pass
