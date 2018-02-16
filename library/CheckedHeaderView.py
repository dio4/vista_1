# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

'''
Created on 02.04.2014

@author: atronah
'''


## Заголовок модели с поддержкой check state
class CCheckedHeaderView(QtGui.QHeaderView):
    _leftMargin = 23 #atronah: найденно опытным путем
    _rightMargin = 5
    
    toggled = QtCore.pyqtSignal(bool)
    
    def __init__(self, orientation, parent = None):
        super(CCheckedHeaderView, self).__init__(orientation, parent)
        self._checkStateDict = {}
        
    
    
    ## Возвращает информацию о возможности менять состояние секции
    def isCheckable(self, section):
        if section not in xrange(self.count()):
            return False
        
        if section not in self._checkStateDict.keys():
            return False
        
        return True
        
    
    
    ## Меняет состояние секции
    def setChecked(self, section, isChecked = True):
        if not self.isCheckable(section):
            return False
        
        self._checkStateDict[section] = isChecked
        self.updateSection(section)
        self.toggled.emit(isChecked)
        return True
    
    
    ## Возвращает состояние секции
    def isChecked(self, section):
        if self.isCheckable(section):
            return self._checkStateDict[section]
        
        return False
        
    
    ## Включает/выключает возможность менять состояние у секции заголовка 
    def setCheckable(self, section, isCheckable = True, isCheckedByDefault = True):
        if section not in xrange(self.count()):
            return False
        
        if isCheckable:
            self._checkStateDict[section] = isCheckedByDefault
            self.setChecked(section, isCheckedByDefault)
        elif self.isCheckable(section):
            self._checkStateDict.pop(section)
            self.updateSection(section)
        
    
    ## Отрисовывает секцию
    def paintSection(self, painter, rect, logicalIndex):
        checkBoxRect = self.checkBoxRect(rect)
        painter.save()
        rect.setLeft(checkBoxRect.x() + self._rightMargin)
        result = super(CCheckedHeaderView, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        if self.isCheckable(logicalIndex):
            option = QtGui.QStyleOptionViewItem()
            if self.isEnabled():
                option.state |= QtGui.QStyle.State_Enabled 
            option.state |= QtGui.QStyle.State_On if self.isChecked(logicalIndex) else QtGui.QStyle.State_Off
            option.rect = checkBoxRect
            self.style().drawPrimitive(QtGui.QStyle.PE_IndicatorViewItemCheck, option, painter) #TODO: atronah: debug
#            self.style().drawControl(QtGui.QStyle.CE_CheckBox, option, painter)
        return result
    
    
    ## Возвращает локальную область секции относительно всего представления заголовка
    def sectionRect(self, section):
        isHorisontal = self.orientation() == QtCore.Qt.Horizontal
        sectionSize = QtCore.QSize(self.sectionSize(section) if isHorisontal else self.size().width(),
                                   self.size().height() if isHorisontal else self.sectionSize(section))
        sectionRect = QtCore.QRect(QtCore.QPoint(self.sectionPosition(section), 0),
                                   sectionSize)
        return sectionRect
    
    
    ## Возвращает область для рисования checkBox на основании области рисования секции
    def checkBoxRect(self, sectionRect):
        checkBoxRect = self.style().subElementRect(QtGui.QStyle.SE_CheckBoxIndicator, QtGui.QStyleOptionButton())
        return QtCore.QRect(QtCore.QPoint(self._leftMargin, 
                                          sectionRect.y() + sectionRect.height() / 2 - checkBoxRect.height() / 2),
                            checkBoxRect.size())
        
# atronah: не вызываются представлением при смене размера   
#    ## Минимально допустимый размер для секции
#    def minimumSectionSize(self, section):
#        minimumSize = super(CCheckedHeaderView, self).minimumSectionSize()
#        checkBoxRect = self.checkBoxRect(self.sectionRect(section))
#        return minimumSize.width(minimumSize + checkBoxRect.width())
#
#    
#    ## Обработка изменения размера секции
#    def resizeSection(self, section, size):
#        if size >= self.minimumSectionSize(section):
#            super(CCheckedHeaderView, self).resizeSection(section, size)
    
    ## Обработка смены состояния
    def mousePressEvent(self, event):
        section = self.logicalIndexAt(event.pos())
        if self.isCheckable(section):
            sectionRect = self.sectionRect(section)
            sectionRect.setX(0) # atronah: так как позиция нажатия берется относительно текущей секции, а не всего заголовка
            if self.checkBoxRect(sectionRect).contains(event.pos()):
                self.setChecked(section, 
                                not self.isChecked(section))
                event.accept()
        super(CCheckedHeaderView, self).mousePressEvent(event)
    
    
    def sectionSizeHint(self, section):
        return super(CCheckedHeaderView, self).sectionSizeHint(section) + self._leftMargin + self.checkBoxRect(QtCore.QRect(0, 0, 0, 0)).width() + self._rightMargin