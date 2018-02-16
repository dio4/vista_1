# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *

class CColorComboBoxModel(QAbstractTableModel):
    colorNameList = [
                     '#FFFFFF', # белый
                     '#C0C0C0', # серебряный
                     '#964B00', # коричневый
                     '#FAF0BE', # blonde
                     '#FF0000', # красный 
                     '#FFA500', # оранжевый
                     '#FFFF00', # желтый
                     '#66FF00', # ярко-зеленый
                     '#8DB600', # зеленый
                     '#00BFFF', # голубой
                     '#0000FF', # синий
                     '#8B00FF', # фиолетовый
                     '#000000', # черный
                     ]
    colorDict = {}
    
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self._colorList = self._colors()
        
    def columnCount(self, index=QtCore.QModelIndex()):
        return 1
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._colorList)
        
    def data(self, index, role=Qt.BackgroundRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.BackgroundRole:
            result = self._colorList[index.row()]
            return result
        return QVariant()
            

    def color(self, row):
        colorName = unicode(self.data(self.index(row, 0)).toString()).upper()
        return self.colorDict.get(colorName, QtGui.QColor())
        
    def colorName(self, color):
        return unicode(color.name()).upper()
        
    def setColor(self, cmb, color):
        if type(color) == QtGui.QColor:
            color = unicode(color.name()).upper()
        if not color.isupper():
            color = color.upper()
        if color in self.colorNameList:
            cmb.setStyleSheet('QComboBox { background-color: %s; }' % color)
            return self.colorNameList.index(color)
        else:
            cmb.setStyleSheet('')
            return -1

    @classmethod
    def _colors(cls):
        result = []
        for colorName in cls.colorNameList:
            color = QtGui.QColor(colorName)
            cls.colorDict[colorName] = color
            result.append(QVariant(color))
        return result

    def changeColorList(self, colors):
        self.colorNameList = colors
        self.colorDict = dict()
        self._colorList = []
        for colorName in self.colorNameList:
            color = QtGui.QColor(colorName)
            self.colorDict[colorName] = color
            self._colorList.append(QVariant(color))
            
class CColorComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self._model = CColorComboBoxModel(self)
        self.setModel(self._model)
        self.connect(self, SIGNAL('currentIndexChanged(int)'), self.on_currentIndexChanged)
        
        
    def color(self):
        rowIndex = self.currentIndex()
        return self._model.color(rowIndex)
        
    def setColor(self, color):
        rowIndex = self._model.setColor(self, color)
        self.setCurrentIndex(rowIndex)
        
    def value(self):
        return self.color()
        
    def setValue(self, value):
        self.setColor(value)
        
    def colorName(self):
        color = self.color()
        return self._model.colorName(color)
        
        
    def on_currentIndexChanged(self, index):
        color = self._model.color(index)
        self.setColor(color)
        
if __name__ == u'__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    wgt = CColorComboBox()
    wgt.show()
    app.exec_()

