# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.ReportsGenerator.Ui_TextAppearanceEditor import Ui_TextAppearanceEditor

'''
Created on 11.03.2013

@author: atronah
'''

class CTextAppearanceEditor(QtGui.QWidget, Ui_TextAppearanceEditor):
    
    fontChanged = QtCore.pyqtSignal(QtGui.QFont)
    alignmentChanged = QtCore.pyqtSignal(QtCore.Qt.Alignment)
    
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.alignmentButtonGroup = QtGui.QButtonGroup(self)
        self.alignmentButtonGroup.addButton(self.btnLeftAlignment, QtCore.Qt.AlignLeft)
        self.alignmentButtonGroup.addButton(self.btnCenterAlignment, QtCore.Qt.AlignCenter)
        self.alignmentButtonGroup.addButton(self.btnRightAlignment, QtCore.Qt.AlignRight)
        
        self.setAlignment(QtCore.Qt.AlignLeft)
    
    
    def font(self):
        currentFont = self.fcmbFontFamily.currentFont()
        currentFont.setPointSizeF(self.sbFontSize.value())
        currentFont.setBold(self.btnFontBold.isChecked())
        currentFont.setItalic(self.btnFontItalic.isChecked())
        currentFont.setUnderline(self.btnFontUnderline.isChecked())
        return currentFont
        
    
    def alignment(self):
        return self.alignmentButtonGroup.checkedId()


    @QtCore.pyqtSlot(QtGui.QFont)
    def setFont(self, font):
        cmbFont = self.fcmbFontFamily.currentFont()
        cmbFont.setFamily(font.family())
        self.fcmbFontFamily.setFont(cmbFont)
        self.sbFontSize.setValue(font.pointSize())
        self.btnFontBold.setChecked(font.bold())
        self.btnFontItalic.setChecked(font.italic())
        self.btnFontUnderline.setChecked(font.underline())
        
    
    @QtCore.pyqtSlot(int)
    def setAlignment(self, alignment):
        if alignment not in [QtCore.Qt.AlignLeft, QtCore.Qt.AlignCenter, QtCore.Qt.AlignRight]:
            alignment = QtCore.Qt.AlignLeft
        self.alignmentButtonGroup.button(alignment).setChecked(True)
    
    
    @QtCore.pyqtSlot(bool)
    def on_btnLeftAlignment_clicked(self, checked):
        self.emitAlignmentChanged()
        
    
    @QtCore.pyqtSlot(bool)
    def on_btnCenterAlignment_clicked(self, checked):
        self.emitAlignmentChanged()
        
    
    @QtCore.pyqtSlot(bool)
    def on_btnRightAlignment_clicked(self, checked):
        self.emitAlignmentChanged()
        

    @QtCore.pyqtSlot(QtGui.QFont)
    def on_fcmbFontFamily_currentFontChanged(self, font):
        self.emitFontChanged()
        
    
    @QtCore.pyqtSlot(int)
    def on_sbFontSize_valueChanged(self, value):
        self.emitFontChanged()
        
    
    @QtCore.pyqtSlot(bool)
    def on_btnFontBold_clicked(self, checked):
        self.emitFontChanged()
        
    
    @QtCore.pyqtSlot(bool)
    def on_btnFontItalic_clicked(self, checked):
        self.emitFontChanged()
        
        
    @QtCore.pyqtSlot(bool)
    def on_btnFontUnderline_clicked(self, checked):
        self.emitFontChanged()
        
     
    @QtCore.pyqtSlot()
    def emitFontChanged(self):
        self.fontChanged.emit(self.font())
    
    
    @QtCore.pyqtSlot()
    def emitAlignmentChanged(self):
        self.alignmentChanged.emit(self.alignment())