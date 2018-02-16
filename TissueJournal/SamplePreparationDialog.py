# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.ItemsListDialog            import CItemEditorBaseDialog
from library.Utils                      import forceDate, forceInt, forceRef, forceString

from Registry.Utils                     import getClientBanner

from TissueJournal.TissueJournalModels  import CSamplePreparationInDocTableModel
from TissueJournal.Utils                import CSamplingApplyDialog

from Ui_SamplePreparationDialog         import Ui_SamplePreparationDialog


AUTO_EQUIPMENT = -1

class CSamplePreparationDialog(CItemEditorBaseDialog, Ui_SamplePreparationDialog):
    lastLoadedEquipment = None
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'TakenTissueJournal')
        self.setupUi(self)
        
        self.addModels('SamplePreparation', CSamplePreparationInDocTableModel(self))
        self.setModels(self.tblSamplePreparation, self.modelSamplePreparation, self.selectionModelSamplePreparation)
        
        self.cmbEquipment.setTable('rbEquipment', addNone=True)
        self.cmbTestGroup.setTable('rbTestGroup', addNone=True)
        
        self.loadLastEquipment()
        
        self.setWindowTitleEx(u'Пробоподготовка')
        
#        self.setupDirtyCather([self.cmbEquipment, self.cmbTestGroup])
#        self.setIsDirty(False)
        
        self._tissueIdentifier = None
        self._tissueTypeId     = None
        self._datetimeTaken    = QtCore.QDate()

        self.actUncheckItems = QtGui.QAction(u'Снять отметки', self)
        self.connect(self.actUncheckItems, QtCore.SIGNAL('triggered()'), self.on_uncheckItems)
        self.tblSamplePreparation.createPopupMenu([self.actUncheckItems])
        
        
    def on_uncheckItems(self):
        self.modelSamplePreparation.uncheckItems()
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self._tissueTypeId  = forceRef(record.value('tissueType_id'))
        self._datetimeTaken = forceDate(record.value('datetimeTaken'))
        self.setInfo(record)
        self.modelSamplePreparation.loadItems(self.itemId())
        
    def setInfo(self, record):
        self.setClientBanner(forceRef(record.value('client_id')))
        self.setTissueRecordInfo(record)
        
    def setClientBanner(self, clientId):
        clientBanner = getClientBanner(clientId)
        self.textBrowser.setHtml(clientBanner)
        
    def checkDataEntered(self):
        result = True
        if self.modelSamplePreparation.hasSelected():
            result = result and self.checkValueMessage(u'Остались выбранные не зарегистрированные пробы\nВернуться?', True, self.tblSamplePreparation)
        return result
        
        
    def saveProbes(self, takenTissueJournalId):
        self.modelSamplePreparation.saveItems(takenTissueJournalId)
        
    
    def loadLastEquipment(self):
        self.cmbEquipment.setValue(CSamplePreparationDialog.lastLoadedEquipment)
    
    
    def setTissueRecordInfo(self, record):
        db = QtGui.qApp.db
        tissueType = forceString(db.translate('rbTissueType', 'id', record.value('tissueType_id'), 'name'))
        self._tissueIdentifier = forceString(record.value('externalId'))
        status = [u'В работе',
                  u'Начато',
                  u'Ожидание',
                  u'Закончено',
                  u'Отменено',
                  u'Без результата',
                  u'Назначено'][forceInt(record.value('status'))]
        date = forceString(record.value('datetimeTaken'))
        rows = []
        rows.append(u'Тип биоматериала: <B>%s</B>'%tissueType)
        rows.append(u'Идентификатор: <B>%s</B>'%self._tissueIdentifier)
        rows.append(u'Статус: <B>%s</B>'%status)
        rows.append(u'Дата забора: <B>%s</B>'%date)
        self.lblTissueRecordInfo.setText(u', '.join(rows))
    
    
        
    
    
    def selectItemsByFilter(self, equipmentId, testGroupId):
        self.modelSamplePreparation.selectItemsByFilter(equipmentId, testGroupId, force=equipmentId==-1 )

    def selectAll(self):
        self.modelSamplePreparation.selectAll()

    def selectItems(self, equipmentId=None, testGroupId=None):
        if not(equipmentId or testGroupId):
            self.selectAll()
        else:
            self.selectItemsByFilter(equipmentId, testGroupId)
            
            
    def automaticalSaveProbes(self, tissueJournalIdList, isSilent = False):
        if isSilent:
            equipmentIdList = QtGui.qApp.db.getIdList('rbEquipment', 'id')
            if len(equipmentIdList) != 1:
                isSilent = False
            else:
                equipmentId, testGroupId = equipmentIdList[0], None

        if not isSilent:
            dlg = CSamplingApplyDialog(self, '', None, testGroupVisible=True, autoEquipment=True)
            if dlg.exec_():
                equipmentId, testGroupId = dlg.equipmentId(), dlg.testGroupId()
            else:
                return

        for tissueJournalId in tissueJournalIdList:
            self.emit(QtCore.SIGNAL('samplePreparationPassed()'))
            self.modelSamplePreparation.loadItems(tissueJournalId)
            self.selectItems(equipmentId, testGroupId)
            externalId = forceString(QtGui.qApp.db.translate('TakenTissueJournal', 'id', tissueJournalId, 'externalId'))
            self.modelSamplePreparation.setValuesForSelected(externalId, equipmentId)
            self.saveProbes(tissueJournalId)

    
    @QtCore.pyqtSlot()
    def on_btnSelectItems_clicked(self):
        self.selectItemsByFilter(self.cmbEquipment.value(), self.cmbTestGroup.value())


    @QtCore.pyqtSlot()
    def on_btnApply_clicked(self):
        if self.modelSamplePreparation.hasSelected():
            dlg = CSamplingApplyDialog(self, self._tissueIdentifier, self.cmbEquipment.value())
            dlg.setSettings(self.itemId(), self._tissueTypeId, self._datetimeTaken)
            if dlg.exec_():
                externalId, equipmentId = dlg.externalId(), dlg.equipmentId()
                self.modelSamplePreparation.setValuesForSelected(externalId, equipmentId)
                self.saveProbes(self.itemId())
                self.modelSamplePreparation.loadItems(self.itemId())
                self.setIsDirty(False)


    @QtCore.pyqtSlot()
    def on_btnSetEquipment_clicked(self):
        externalId = forceString(QtGui.qApp.db.translate('TakenTissueJournal', 'id', self.itemId(), 'externalId'))
        self.modelSamplePreparation.setValuesForSelected(None, AUTO_EQUIPMENT)
        
