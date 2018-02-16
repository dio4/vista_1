# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from Ui_EQPanelWidget import Ui_EQPanelWidget
from library.ElectronicQueue.EQPanel import CEQPanel, CSocketDEInterface
from library.ElectronicQueue.EQConfig import CEQConfigWidget

'''
Created on 05.11.2013

@author: atronah
'''

class CEQPanelWidget(QtGui.QWidget, Ui_EQPanelWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self._eqPanel = CEQPanel(panelAddr = None,
                                 expectAnswerMode=1)
        self.personId = None
        self.orgStructureIdList = [None]
        
        self._eqConfig = {}
#        self._eqConfig = {'isConfigured' : False,
#                          'port' : None,
#                          'panelAddress' : None,
#                          'dateControl' : True,
#                          'personControl' : True}
        
        self._eqConfigDialog = QtGui.QDialog(self)
        self._eqConfigWidget = CEQConfigWidget(self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._eqConfigWidget)
        self._eqConfigDialog.setLayout(layout)
        self._eqConfigDialog.setWindowTitle(u'Настройки связи с табло эл. очереди')
        
    
    
    def eqPanel(self):
        return self._eqPanel
        
        
        
#    def isWork(self):
#        if self._eqPanel:
#            return self._eqPanel.isWork()
#        
#        return False
        
    
    def configureEQPanel(self, personId, orgStructureIdList):
        if not personId:
            return False
        
        self.personId = personId
        self.orgStructureIdList = orgStructureIdList
        
        self._eqConfig = CEQConfigWidget.getEQConfig(personId)
        
        
        if not self._eqConfig['isConfigured']:
            isControl = QtGui.QMessageBox.Ok == QtGui.QMessageBox.question(self,
                                                                           u'Электронная очередь',
                                                                           u'Хотите использовать табло эл. очереди?',
                                                                           buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            self._eqConfigWidget.setPersonInfo(personId, orgStructureIdList)
            if self._eqConfigWidget.configure(isControl):
                self._eqConfig = CEQConfigWidget.getEQConfig(personId)
        
        if not self.isControl():
            return False
        
        
        if not self._eqConfig['panelAddress']:
            self._eqConfig.update(self._eqConfigWidget.setPersonInfo(personId, orgStructureIdList))
            
            officeDialog = self._eqConfigWidget.getOfficeSelectDialog(self)
            
            while True:
                address, office = officeDialog.getPanelAddressAndOffice() if officeDialog.exec_() else (-1, u'')
                
                if address:
                    self._eqPanel.setPanelAddres(address)
                    self.lblOffice.setText(office)
                    if officeDialog.isSaveSelect():
                        self._eqConfigWidget.setOfficeId(officeDialog.getOfficeId())
                        self._eqConfigWidget.configure(True)
                        self._eqConfig = CEQConfigWidget.getEQConfig(personId)
                    break
                else:
                    self.lblOffice.setText('---')
                    if QtGui.QMessageBox.Yes == QtGui.QMessageBox.warning(self, 
                                                                          u'Неверно указан кабинет',
                                                                          u'Кабинет указан неверно.\nОтключить работу с очередью?', 
                                                                          buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No):
                        self._eqConfigWidget.configure(False)
                        return True
            
        else:
            self._eqPanel.setPanelAddres(self._eqConfig['panelAddress'])
            self.lblOffice.setText(self._eqConfig['office'])
        
        
        self._eqPanel.setDataExchangeInterface(CSocketDEInterface((self._eqConfig['host'], 
                                                                   self._eqConfig['port'])))
        
    
    def showOnPanel(self, data, alwaysOn = False):
        if self.eqPanel().showOnPanel(data, alwaysOn):
            return self.eqGuiPanel.showOnPanel(data, alwaysOn)
        else:
            self.showError()
            QtGui.QMessageBox.warning(self, 
                                      u'Ошибка эл. очереди', 
                                      self.eqPanel().lastError() or '<Нет данных по ошибке>', 
                                      buttons=QtGui.QMessageBox.Ok,
                                      defaultButton=QtGui.QMessageBox.NoButton)
            return False
            
            
    def showError(self, message = ''):
        self.eqGuiPanel.setText('XXXX')
        self.eqGuiPanel.setToolTip(message)
        
    
    def isControl(self):
        return self._eqConfig.get('isControl', False)
        
    
    def isDateControl(self):
        self._eqConfig.get('dateControl', True)
        
    
    def isPersonControl(self):
        self._eqConfig.get('personControl', True)
    
    
    @QtCore.pyqtSlot()
    def on_btnConfig_clicked(self):
        if not self.isControl() and QtGui.QMessageBox.Yes == QtGui.QMessageBox.warning(self, 
                                                                          u'Электронная очередь',
                                                                          u'Включить работу с очередью?', 
                                                                          buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No):
            self._eqConfig['isControl'] = True
        if not self.isControl():
            return
        
        self._eqConfigWidget.setPersonInfo(self.personId, self.orgStructureIdList)
        self._eqConfigDialog.exec_()
        self.configureEQPanel(self.personId, self.orgStructureIdList)
        
        