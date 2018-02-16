# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.ItemsListDialog  import CItemEditorBaseDialog 
from library.Utils            import forceDateTime, forceInt, forceString

from Ui_ClientQuotaDiscussionEditor import Ui_ClientQuotaDiscussionEditor


class CQuotingEditorDialog(CItemEditorBaseDialog, Ui_ClientQuotaDiscussionEditor):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Client_QuotingDiscussion')
        self.setupUi(self)
        self.setWindowTitle(u'Переговоры по квоте(редактирвоание)')
        self.cmbAgreementType.setTable('rbAgreementType')
        self.cmbResponsiblePerson.setTable('vrbPersonWithSpeciality', True, 'speciality_id IS NOT NULL AND retireDate IS NULL AND org_id=%d'%QtGui.qApp.currentOrgId())
        dt = QtCore.QDateTime().currentDateTime()
        self.edtDateMessage.setMinimumDateTime(dt)
        self.edtDateMessage.setDateTime(dt)
        self.master_id = None
        
    def setMaster_id(self, master_id):
        self.master_id = master_id
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        dt = forceDateTime(record.value('dateMessage'))
        self.edtDateMessage.setMinimumDateTime(dt)
        self.edtDateMessage.setDateTime(dt)
        self.cmbAgreementType.setValue(forceInt(record.value('agreementType_id')))
        self.cmbResponsiblePerson.setValue(forceInt(record.value('responsiblePerson_id')))
        self.edtCosignatory.setText(forceString(record.value('cosignatory')))
        self.edtCosignatoryPost.setText(forceString(record.value('cosignatoryPost')))
        self.edtCosignatoryName.setText(forceString(record.value('cosignatoryName')))
        self.edtRemark.setPlainText(forceString(record.value('remark')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('dateMessage', QtCore.QVariant(self.edtDateMessage.dateTime()))
        record.setValue('agreementType_id', QtCore.QVariant(self.cmbAgreementType.value()))
        record.setValue('responsiblePerson_id', QtCore.QVariant(self.cmbResponsiblePerson.value()))
        record.setValue('cosignatory', QtCore.QVariant(self.edtCosignatory.text()))
        record.setValue('cosignatoryPost', QtCore.QVariant(self.edtCosignatoryPost.text()))
        record.setValue('cosignatoryName', QtCore.QVariant(self.edtCosignatoryName.text()))
        record.setValue('remark', QtCore.QVariant(self.edtRemark.toPlainText()))
        
        if self.master_id:
            record.setValue('master_id', QtCore.QVariant(self.master_id))
        return record
        
    def canBeEdit(self):
        responsiblePersonId = self.cmbResponsiblePerson.value()
        if responsiblePersonId:
            if responsiblePersonId == QtGui.qApp.userId:
                return True
            else:
                return False
        return True
        
    def checkDataEntered(self):
        result            = True
        responsiblePerson = self.cmbResponsiblePerson.value()
        cosignatory = self.edtCosignatory.text()
        result = result and (responsiblePerson or self.checkInputMessage(u'ответвственное лицо ЛПУ', False, self.cmbResponsiblePerson))
        result = result and (cosignatory or self.checkInputMessage(u'контрагента', False, self.edtCosignatory))
        return result