# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from Events.Action import CActionType
from RefBooks.Utils import CServiceTypeModel

from library.DialogBase  import CDialogBase
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.Utils       import forceRef, forceString, forceStringEx, toVariant
from library.interchange import setCheckBoxValue, setComboBoxValue, setLineEditValue, setRBComboBoxValue, \
                                setSpinBoxValue

from Ui_GroupActionTypeEditor import Ui_GroupActionTypeEditorDialog


class CGroupActionTypeEditor(CDialogBase, Ui_GroupActionTypeEditorDialog):
    def __init__(self, parent, actionTypeIdList=None, patternActionTypeId=None):
        if not actionTypeIdList:
            actionTypeIdList = []
        self._actionTypeIdList = actionTypeIdList
        self._table = QtGui.qApp.db.table('ActionType')
        
        CDialogBase.__init__(self,  parent)
        
        self.setupUi(self)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbDefaultStatus.clear()
        self.cmbDefaultStatus.addItems(CActionType.retranslateClass(False).statusNames)
        
        self._load(patternActionTypeId)
        
        self.setWindowTitle(u'Групповой редактор')

        self.addModels('ServiceType', CServiceTypeModel(1))
        self.cmbServiceType.setModel(self.modelServiceType)
        
    def _load(self, actionTypeId):
        record = QtGui.qApp.db.getRecord(self._table, '*', actionTypeId)
        
        setComboBoxValue(self.cmbSex, record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))
        setComboBoxValue(   self.cmbDefaultStatus,              record,     'defaultStatus')
        setComboBoxValue(   self.cmbDefaultDirectionDate,       record,     'defaultDirectionDate')
        setComboBoxValue(   self.cmbDefaultPlannedEndDate,      record,     'defaultPlannedEndDate')
        setComboBoxValue(   self.cmbDefaultBeginDate,           record,     'defaultBeginDate')
        setComboBoxValue(   self.cmbDefaultEndDate,             record,     'defaultEndDate')
        setRBComboBoxValue( self.cmbDefaultExecPerson,          record,     'defaultExecPerson_id')
        setComboBoxValue(   self.cmbDefaultPersonInEvent,       record,     'defaultPersonInEvent')
        setComboBoxValue(   self.cmbDefaultPersonInEditor,      record,     'defaultPersonInEditor')
        self.cmbDefaultOrg.setValue(forceRef(record.value('defaultOrg_id')))
        setComboBoxValue(   self.cmbDefaultMKB,                 record,     'defaultMKB')
        setComboBoxValue(   self.cmbDefaultMorphology,          record,     'defaultMorphology')
        setComboBoxValue(   self.cmbIsMorphologyRequired,       record,     'isMorphologyRequired')
        setLineEditValue(   self.edtOffice,                     record,     'office')
        setCheckBoxValue(   self.chkShowInForm,                 record,     'showInForm')
        setCheckBoxValue(   self.chkShowTime,                   record,     'showTime')
        setCheckBoxValue(   self.chkShowAPOrg,                  record,     'showAPOrg')
        setCheckBoxValue(   self.chkShowAPNotes,                record,     'showAPNotes')
        setCheckBoxValue(   self.chkRequiredCoordination,       record,     'isRequiredCoordination')
        setComboBoxValue(   self.cmbAssistantRequired,          record,     'hasAssistant')
        setLineEditValue(   self.edtContext,                    record,     'context')
        setCheckBoxValue(   self.chkIsPreferable,               record,     'isPreferable')
        setSpinBoxValue(    self.edtAmount,                     record,     'amount')
        setSpinBoxValue(    self.edtMaxOccursInEvent,           record,     'maxOccursInEvent')
        setComboBoxValue(   self.cmbServiceType,                record,     'serviceType')
        setCheckBoxValue(   self.chkPropertyAssignedVisible,    record,     'propertyAssignedVisible')
        setCheckBoxValue(   self.chkPropertyUnitVisible,        record,     'propertyUnitVisible')
        setCheckBoxValue(   self.chkPropertyNormVisible,        record,     'propertyNormVisible')
        setCheckBoxValue(   self.chkPropertyEvaluationVisible,  record,     'propertyEvaluationVisible')
        setSpinBoxValue(    self.edtRecommendationExpirePeriod, record,     'recommendationExpirePeriod')
        setCheckBoxValue(   self.chkRecommendationControl,      record,     'recommendationControl')
        setCheckBoxValue(   self.chkExecRequiredForEventExec,   record,     'isExecRequiredForEventExec')
        setCheckBoxValue(   self.chkIgnoreEventEndDate,         record,     'isIgnoreEventExecDate')

    def saveData(self):
        if not self.confirm():
            return False
        fields = {'id':None}
        if self.chkSex.isChecked():
            fields['sex'] = self.cmbSex.currentIndex()
        if self.chkAge.isChecked():
            fields['age'] = composeAgeSelector(self.cmbBegAgeUnit.currentIndex(),  forceStringEx(self.edtBegAgeCount.text()),
                                               self.cmbEndAgeUnit.currentIndex(),  forceStringEx(self.edtEndAgeCount.text()))
        if self.chkChkShowTime.isChecked():
            fields['showTime'] = self.chkShowTime.isChecked()
        if self.chkChkShowAPOrg.isChecked():
            fields['showAPOrg'] = self.chkShowAPOrg.isChecked()
        if self.chkChkShowAPNotes.isChecked():
            fields['showAPNotes'] = self.chkShowAPNotes.isChecked()
        if self.chkChkRequiredCoordination.isChecked():
            fields['isRequiredCoordination'] = self.chkRequiredCoordination.isChecked()
        if self.chkChkShowInForm.isChecked():
            fields['showInForm'] = self.chkShowInForm.isChecked()
        if self.chkAssistant.isChecked():
            fields['hasAssistant'] = self.cmbAssistantRequired.currentIndex()
        if self.chkContext.isChecked():
            fields['context'] = forceStringEx(self.edtContext.text())
        if self.chkPreferable.isChecked():
            fields['isPreferable'] = self.chkIsPreferable.isChecked()
        if self.chkMaxOccursInEvent.isChecked():
            fields['maxOccursInEvent'] = self.edtMaxOccursInEvent.value()
        if self.chkServiceType.isChecked():
            fields['serviceType'] = self.cmbServiceType.currentIndex()
        if self.chkDefaultStatus.isChecked():
            fields['defaultStatus'] = self.cmbDefaultStatus.currentIndex()
        if self.chkDefaultPlannedEndDate.isChecked():
            fields['defaultPlannedEndDate'] = self.cmbDefaultPlannedEndDate.currentIndex()
        if self.chkDefaultBeginDate.isChecked():
            fields['defaultBeginDate'] = self.cmbDefaultBeginDate.currentIndex()
        if self.chkDefaultEndDate.isChecked():
            fields['defaultEndDate'] = self.cmbDefaultEndDate.currentIndex()
        if self.chkDefaultDirectionDate.isChecked():
            fields['defaultDirectionDate'] = self.cmbDefaultDirectionDate.currentIndex()
        if self.chkDefaultExecPerson.isChecked():
            fields['defaultExecPerson_id'] = self.cmbDefaultExecPerson.value()
        if self.chkDefaultPersonInEvent.isChecked():
            fields['defaultPersonInEvent'] = self.cmbDefaultPersonInEvent.currentIndex()
        if self.chkDefaultPersonInEditor.isChecked():
            fields['defaultPersonInEditor'] = self.cmbDefaultPersonInEditor.currentIndex()
        if self.chkDefaultMKB.isChecked():
            fields['defaultMKB'] = self.cmbDefaultMKB.currentIndex()
        if self.chkDefaultMorphology.isChecked():
            fields['defaultMorphology'] = self.cmbDefaultMorphology.currentIndex()
        if self.chkIsMorphologyRequired.isChecked():
            fields['isMorphologyRequired'] = self.cmbIsMorphologyRequired.currentIndex()
        if self.chkDefaultOrg.isChecked():
            fields['defaultOrg_id'] = self.cmbDefaultOrg.value()
        if self.chkAmount.isChecked():
            fields['amount'] = self.edtAmount.value()
        if self.chkOffice.isChecked():
            fields['office'] = forceStringEx(self.edtOffice.text())
        if self.grpPropertiesFields.isChecked():
            fields['propertyAssignedVisible'] = self.chkPropertyAssignedVisible.isChecked()
            fields['propertyUnitVisible'] = self.chkPropertyUnitVisible.isChecked()
            fields['propertyNormVisible'] = self.chkPropertyNormVisible.isChecked()
            fields['propertyEvaluationVisible'] = self.chkPropertyEvaluationVisible.isChecked()
        if self.chkChkRecommendationControl.isChecked():
            fields['recommendationControl'] = self.chkRecommendationControl.isChecked()
        if self.chkRecommendationExpirePeriod.isChecked():
            fields['recommendationExpirePeriod'] = self.edtRecommendationExpirePeriod.value()
        if self.chkChkExecRequiredForEventExec.isChecked():
            fields['isExecRequiredForEventExec'] = self.chkExecRequiredForEventExec.isChecked()
        if self.chkChkIgnoreEventEndDate.isChecked():
            fields['isIgnoreEventExecDate'] = self.chkIgnoreEventEndDate.isChecked()

        record = self._table.newRecord(fields.keys())
        for key, value in fields.items():
            record.setValue(key, toVariant(value))
        for actionTypeId in self._actionTypeIdList:
            record.setValue('id', QtCore.QVariant(actionTypeId))
            QtGui.qApp.db.updateRecord(self._table, record)
            
        return True
            
        
    def confirm(self):
        return QtGui.QMessageBox.question(self, 
                                          u'Внимание!', 
                                          u'Вы уверены что хотите сохранить изменения?', 
                                          QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, 
                                          QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok
        
        
    
