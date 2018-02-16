# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils  import forceString
from Orgs.Orgs      import selectOrganisation

from Reports        import OKVEDList

from Ui_ReportSetup import Ui_ReportSetupDialog


class CReportSetupDialog(QtGui.QDialog, Ui_ReportSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbEventType.setTable('EventType', True)
        self.cmbStage.setTable('rbDiseaseStage', True)
        self.cmbFinance.setTable('rbFinance', True)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True)
        self.cmbSpeciality.setValue(0)
        self.setStageVisible(False)
        self.setDiagnosisType(False)
        self.setPayPeriodVisible(False)
        self.setWorkTypeVisible(False)
        self.edtBegPayDate.setDate(QtCore.QDate())
        self.edtEndPayDate.setDate(QtCore.QDate())
        self.setOwnershipVisible(False)
        self.setWorkOrganisationVisible(False)
        self.setSexVisible(False)
        self.setAgeVisible(False)
        self.setActionTypeVisible(False)
        self.cmbActionType.setAllSelectable(True)
        self.setMKBFilterVisible(False)
        self.setInsurerVisible(False)
        self.setOrgStructureVisible(False)
        self.setSpecialityVisible(False)
        self.setPersonVisible(False)
        self.setFinanceVisible(False)
        self.setContractVisible(False)
        self.setOnlyNotPayedVisible(False)
        self.setOnlyEmployeeVisible(False)
        self.setGroupByClients(False)
        self.setEventPurposeVisible(False)
        self.setSourceFileVisible(False)
        self.setOrgStructureAttachTypeVisible(False)
        
        self.sourceFileFilter = u'All files (*.*)'


    def setSourceFileFilter(self, filter):
        self.sourceFileFilter = filter
        
    
    def setSourceFileVisible(self, value):
        self.sourceFileVisible = value
        self.chkIsDataFromFile.setVisible(value)
        self.edtSourceDataFileName.setVisible(value)
        self.btnBrowseSourceDataFile.setVisible(value)
  
        
    def setOnlyNotPayedVisible(self, value):
        self.onlyNotPayedVisible = value
        self.chkOnlyNotPayedEvents.setVisible(value)
        
    def setOnlyEmployeeVisible(self, value):
        self.onlyEmployeeVisible = value
        self.chkOnlyEmployee.setVisible(value)
        
    def setGroupByClients(self, value):
        self.groupByClients = value
        self.chkGroupByClients.setVisible(value)
        
    def setEventTypeVisible(self, value):
        self.cmbEventType.setVisible(value)
        self.lblEventType.setVisible(value)
    
    def setOnlyPermanentAttachVisible(self, value):
        self.chkOnlyPermanentAttach.setVisible(value)
        
    def setContractVisible(self, value):
        self.contractVisible = value
        self.lblContract.setVisible(value)
        self.cmbContract.setVisible(value)

    def setFinanceVisible(self, value):
        self.financeVisible = value
        self.lblFinance.setVisible(value)
        self.cmbFinance.setVisible(value)

    def setPersonVisible(self, value):
        self.personVisible = value
        self.lblPerson.setVisible(value)
        self.cmbPerson.setVisible(value)
        self.chkDetailPerson.setVisible(value)
        
    def setPersonWithoutDetailCheckboxVisible(self, value):
        self.personVisible = value
        self.lblPerson.setVisible(value)
        self.cmbPerson.setVisible(value)
        

    def setSpecialityVisible(self, value):
        self.specialityVisible = value
        self.lblSpeciality.setVisible(value)
        self.cmbSpeciality.setVisible(value)

    def setOrgStructureVisible(self, value):
        self.orgStructureVisible = value
        self.lblOrgStructure.setVisible(value)
        self.cmbOrgStructure.setVisible(value)

    def setInsurerVisible(self, value):
        self.insurerVisible = value
        self.lblInsurer.setVisible(value)
        self.cmbInsurer.setVisible(value)

    def setStageVisible(self, value):
        self.stageVisible = value
        self.lblStage.setVisible(value)
        self.cmbStage.setVisible(value)


    def setPayPeriodVisible(self, value):
        self.payPeriodVisible = value
        for w in [self.lblBegPayDate, self.edtBegPayDate,
                  self.lblEndPayDate, self.edtEndPayDate,
                  self.chkOnlyPayedEvents
                 ]:
            w.setVisible(value)


    def setWorkTypeVisible(self, value):
        if value and not self.cmbWorkType.count():
            for row in OKVEDList.rows:
                self.cmbWorkType.addItem(row[0])
        self.workTypeVisible = value
        self.lblWorkType.setVisible(value)
        self.cmbWorkType.setVisible(value)


    def setOwnershipVisible(self, value):
        self.ownershipVisible = value
        self.lblOwnership.setVisible(value)
        self.cmbOwnership.setVisible(value)


    def setWorkOrganisationVisible(self, value):
        self.workOrganisationVisible = value
        self.lblWorkOrganisation.setVisible(value)
        self.cmbWorkOrganisation.setVisible(value)
        self.btnSelectWorkOrganisation.setVisible(value)


    def setSexVisible(self, value):
        self.lblSex.setVisible(value)
        self.cmbSex.setVisible(value)


    def setDiagnosisType(self, value):
        self.chkDiagnosisType.setVisible(value)


    def setAgeVisible(self, value):
        self.ageVisible = value
        self.lblAge.setVisible(value)
        self.edtAgeFrom.setVisible(value)
        self.lblAgeTo.setVisible(value)
        self.edtAgeTo.setVisible(value)
        self.lblAgeYears.setVisible(value)


    def setActionTypeVisible(self, value):
        self.actionTypeVisible = value
        for w in [self.lblActionTypeClass, self.cmbActionTypeClass,
                  self.lblActionType,      self.cmbActionType,
                  self.chkActionClass]:
            w.setVisible(value)
        if value:
            self.on_cmbActionTypeClass_currentIndexChanged(self.cmbActionTypeClass.currentIndex())


    def setMKBFilterVisible(self, value):
        self.MKBFilterVisible = value
        for w in [self.lblMKBFilter, self.cmbMKBFilter,
                  self.edtMKBFrom,   self.edtMKBTo]:
            w.setVisible(value)
        if value:
            self.on_cmbActionTypeClass_currentIndexChanged(self.cmbActionTypeClass.currentIndex())
            
    def setEventPurposeVisible(self, value):
        self.eventPurposeVisible = value
        self.lblEventPurpose.setVisible(value)
        self.cmbEventPurpose.setVisible(value)

    def setOrgStructureAttachTypeVisible(self, value):
        self.lblOrgStrucutreAttachType.setVisible(value)
        self.cmbOrgStructureAttachType.setVisible(value)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        if self.stageVisible:
            self.cmbStage.setValue(params.get('stageId', None))
        self.chkOnlyPermanentAttach.setChecked(params.get('onlyPermanentAttach', False))
        self.chkDiagnosisType.setChecked(params.get('diagnosisType', False))
        self.chkOnlyPayedEvents.setChecked(params.get('onlyPayedEvents', False))
        self.edtBegPayDate.setDate(params.get('begPayDate', QtCore.QDate.currentDate()))
        self.edtEndPayDate.setDate(params.get('endPayDate', QtCore.QDate.currentDate()))
        self.cmbWorkType.setCurrentIndex(params.get('workType', 0))
        if self.ownershipVisible:
            self.cmbOwnership.setCurrentIndex(params.get('ownership', 0))
        self.cmbWorkOrganisation.setValue(params.get('workOrgId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        if self.ageVisible:
            self.edtAgeFrom.setValue(params.get('ageFrom', 0))
            self.edtAgeTo.setValue(params.get('ageTo', 150))
        if self.actionTypeVisible:
            if not params.get('chkActionTypeClass', False):
                self.cmbActionTypeClass.setCurrentIndex(params.get('actionTypeClass', 0))
                self.cmbActionType.setValue(params.get('actionTypeId', None))
        if self.MKBFilterVisible:
            MKBFilter = params.get('MKBFilter', 0)
            self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
            self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
            self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        self.cmbContract.setPath(params.get('contractPath', u''))
        self.chkGroupByClients.setChecked(params.get('groupByClients', False))
        self.chkOnlyEmployee.setChecked(params.get('onlyEmployee', False))
        self.chkOnlyNotPayedEvents.setChecked(params.get('onlyNotPayedEvents', False))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbOrgStructureAttachType.setValue(params.get('orgStructureAttachTypeId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        if self.stageVisible:
            result['stageId'] = self.cmbStage.value()
        result['onlyPermanentAttach'] = self.chkOnlyPermanentAttach.isChecked()
        result['onlyPayedEvents'] = self.chkOnlyPayedEvents.isChecked()
        result['diagnosisType'] = self.chkDiagnosisType.isChecked()
        result['begPayDate'] = self.edtBegPayDate.date()
        result['endPayDate'] =self.edtEndPayDate.date()
        result['workType'] =self.cmbWorkType.currentIndex()
        if self.ownershipVisible:
            result['ownership'] = self.cmbOwnership.currentIndex()
        result['workOrgId'] = self.cmbWorkOrganisation.value()
        result['sex'] = self.cmbSex.currentIndex()
        if self.ageVisible:
            result['ageFrom'] = self.edtAgeFrom.value()
            result['ageTo'] = self.edtAgeTo.value()
        if self.actionTypeVisible:
            chkActionTypeClass = self.chkActionClass.isChecked()
            result['chkActionTypeClass'] = chkActionTypeClass
            if chkActionTypeClass:
                result['actionTypeClass'] = None
                result['actionTypeId'] = None
            else:
                result['actionTypeClass'] = self.cmbActionTypeClass.currentIndex()
                result['actionTypeId'] = self.cmbActionType.value()
        if self.MKBFilterVisible:
            result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
            result['MKBFrom']   = forceString(self.edtMKBFrom.text())
            result['MKBTo']     = forceString(self.edtMKBTo.text())
        if self.personVisible:
            result['detailPerson'] = self.chkDetailPerson.isChecked()
            result['personId'] = self.cmbPerson.value()
        if self.specialityVisible:
            result['specialityId'] = self.cmbSpeciality.value()
        if self.orgStructureVisible:
            result['orgStructureId'] = self.cmbOrgStructure.value()
        if self.insurerVisible:
            result['insurerId'] = self.cmbInsurer.value()
        if self.financeVisible:
            result['financeId'] = self.cmbFinance.value()
            result['financeCode'] = self.cmbFinance.code()
        if self.contractVisible:
            result['contractIdList'] = self.cmbContract.getIdList()
            result['contractPath'] = self.cmbContract.getPath()
        if self.onlyNotPayedVisible:
            result['onlyNotPayedEvents'] = self.chkOnlyNotPayedEvents.isChecked()
        if self.onlyEmployeeVisible:
            result['onlyEmployee'] = self.chkOnlyEmployee.isChecked()
        if self.groupByClients:
            result['groupByClients'] = self.chkGroupByClients.isChecked()
        if self.eventPurposeVisible:
            result['eventPurposeId'] = self.cmbEventPurpose.value()
        if self.sourceFileVisible and self.chkIsDataFromFile.isChecked():
            result['dataFileName'] = self.edtSourceDataFileName.text()
        result['orgStructureAttachTypeId'] = self.cmbOrgStructureAttachType.value()
        return result


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)

    @QtCore.pyqtSlot(int)
    def on_cmbActionTypeClass_currentIndexChanged(self, classCode):
        self.cmbActionType.setClass(classCode)

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)
    
    @QtCore.pyqtSlot(bool)
    def on_chkIsDataFromFile_toggled(self, checked):
        notProcessedWidgets = [self.chkIsDataFromFile, self.buttonBox, self.lblBegDate, self.edtBegDate]
        for child in self.children():
            if isinstance(child, QtGui.QWidget) and child not in notProcessedWidgets:
                child.setEnabled(not checked)
        self.edtSourceDataFileName.setEnabled(checked)
        self.btnBrowseSourceDataFile.setEnabled(checked)
        self.lblBegDate.setText(u'Дата отчета' if checked else u'Дата &начала периода')
    
    @QtCore.pyqtSlot()
    def on_btnBrowseSourceDataFile_clicked(self):
        self.edtSourceDataFileName.setText(QtGui.QFileDialog.getOpenFileName(parent = self, caption= u'Укажите файл исходных данных отчета', filter = self.sourceFileFilter))