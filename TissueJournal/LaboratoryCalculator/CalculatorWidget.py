# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt

from TissueJournal.LaboratoryCalculator.LaboratoryCalculatorTable import CLaboratoryCalculatorTableModel

from Ui_CalculatorWidget import Ui_CalculatorWidget


class CCalculatorWidget(QtGui.QWidget, Ui_CalculatorWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.createButtonGroup()
        self._model = CLaboratoryCalculatorTableModel(self)
        self.tableView.setModel(self._model)
        rounding = forceInt(QtGui.qApp.preferences.appPrefs.get('calculatorRounding', 0))
        self.edtRounding.setValue(rounding)
        self._model.setRounding(rounding)
        
        
    def rounding(self):
        return self.edtRounding.value()
        
        
    def createButtonGroup(self):
        self.buttonGroup = QtGui.QButtonGroup(self)
        self.buttonGroup.addButton(self.btnZero)
        self.buttonGroup.addButton(self.btnOne)
        self.buttonGroup.addButton(self.btnTwo)
        self.buttonGroup.addButton(self.btnThree)
        self.buttonGroup.addButton(self.btnFour)
        self.buttonGroup.addButton(self.btnFive)
        self.buttonGroup.addButton(self.btnSix)
        self.buttonGroup.addButton(self.btnSeven)
        self.buttonGroup.addButton(self.btnEight)
        self.buttonGroup.addButton(self.btnNine)
        self.buttonGroup.addButton(self.btnDiv)
        self.buttonGroup.addButton(self.btnMultiply)
        self.buttonGroup.addButton(self.btnMinus)
        self.buttonGroup.addButton(self.btnPlus)
        self.buttonGroup.addButton(self.btnEnter)
        self.buttonGroup.addButton(self.btnReset)
        self.buttonGroup.addButton(self.btnCancel)
        self.buttonGroup.addButton(self.btnResetAdditional)
        self.connect(self.buttonGroup, QtCore.SIGNAL('buttonClicked(QAbstractButton*)'), self.on_buttonGroupClicked)
        
    def enabledKeys(self, keys):
        for btn in self.buttonGroup.buttons()[:-4]:
            btn.setEnabled(unicode(btn.text()) in keys)
        
    def resetButtons(self):
        additionalKeyList = self._model.additionalKeyList()
        for btn in self.buttonGroup.buttons()[:-4]:
            if not unicode(btn.text()) in additionalKeyList:
                btn.setEnabled(False)
        
    def clear(self):
        self.resetButtons()
        self._model.commands(['clear', 'reset'])
        
    def reset(self):
        self.resetButtons()
        self._model.command('resetData')
        
    def loadLastSetData(self):
        self._model.loadLastSetData()
        
    def load(self, data):
        self._model.load(data)
        
    def resetAdditional(self):
        additionalKeyList = self._model.additionalKeyList()
        for btn in self.buttonGroup.buttons()[:-4]:
            if unicode(btn.text()) in additionalKeyList:
                btn.setEnabled(False)
        self._model.resetAdditional()
        
    def on_buttonGroupClicked(self, button):
        btnText = unicode(button.text())
        if not self._model.done(btnText, self.edtRounding.value()):
            if btnText == 'E':
                self.sentData()
            elif btnText == '.':
                self.reset()
            elif btnText == u'Отменить':
                self.loadLastSetData()
#                self.sentData(minimized=False)
            elif btnText == u'Отменить назначения':
                self.resetAdditional()
                
    def sentData(self, minimized=True):
        data = self._model.formatData()
        mimeData = QtCore.QMimeData()
        mimeData.setData(QtGui.qApp.outputMimeDataType, 
                         QtCore.QString(data).toUtf8())
        QtGui.qApp.clipboard().setMimeData(mimeData)
        if self._model.hasOuterItems() and minimized:
            QtGui.qApp.mainWindow.showMinimized()
        


    def addButton(self, btn, group, name):
        btn.setEnabled(True)
        self._model.addAdditionalRow(unicode(btn.text()), group, name)


    def availableGroupList(self):
        return self._model.availableGroupList()


    @QtCore.pyqtSlot(int)
    def on_edtMaxGroupValue_valueChanged(self, value):
        self._model.setMaxGroupValue(value)
    
    @QtCore.pyqtSlot(int)
    def on_edtRounding_valueChanged(self, value):
        self._model.setRounding(value)
        self._model.recountPercentValueForGroup(value)
