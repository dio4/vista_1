# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2014 ООО "Виста". All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

'''
Created on 20.03.2014

@author: atronah
'''


#TODO: atronah: переделать из List model в табле или более универсальную
class CCheckableModel(QtGui.QStringListModel):
    def __init__(self, strings=None, defaultCheckState=False, parent=None):
        if not strings:
            strings = []
        super(CCheckableModel, self).__init__(strings, parent)
        self._defaultCheckState = defaultCheckState
        self._checkStates = [defaultCheckState] * self.rowCount()
        self._enabled = [True] * self.rowCount()
    
    
    
    def flags(self, index):
        flags = super(CCheckableModel, self).flags(index) | QtCore.Qt.ItemIsUserCheckable
        if not self._enabled[index.row()]:
            flags ^= QtCore.Qt.ItemIsEnabled
        return  flags
    
    
    
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.QVariant(QtCore.Qt.Checked if self._checkStates[index.row()] else QtCore.Qt.Unchecked)
        
        return super(CCheckableModel, self).data(index, role)
    
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            self._checkStates[index.row()] = value == QtCore.Qt.Checked
            self.dataChanged.emit(index, index)
            return True 
        
        return super(CCheckableModel, self).setData(index, value, role)
    
    
    
    def setStringList(self, strings):
        super(CCheckableModel, self).setStringList(strings)
        self._checkStates = [False] * self.rowCount()
    
    
    
    def beginInsertRows(self, parent, first, last):
        super(CCheckableModel, self).beginInsertRows(parent, first, last)
        while last >= first:
            last -= 1
            self._checkStates.insert(first, False)
            
            
    
    def beginRemoveRows(self, parent, first, last):
        super(CCheckableModel, self).beginRemoveRows(parent, first, last)
        while last >= first:
            last -= 1
            self._checkStates.pop(first)
            
    
    def checkStateList(self):
        return self._checkStates[:]
    
    
    def setCheckStateList(self, checkStateList):
        newLen = len(checkStateList)
        currentLen = len(self._checkStates)
        if currentLen > newLen: 
            checkStateList.extend([self._defaultCheckState] * (currentLen - newLen))
        else:
            checkStateList = checkStateList[0:currentLen]
        self._checkStates = checkStateList
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, 0))

    def setEnabled(self, index, value):
        if index < 0 and index > self.rowCount() - 1:
            return False
        self._enabled[index] = value
        return True
            


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    
    
    m = CCheckableModel([u'test1', u'test2', u'тест3'])
    lv = QtGui.QListView()
    lv.setModel(m)
    lv.show()
    
    return app.exec_()
        
if __name__ == '__main__':
    main()
        
        
        