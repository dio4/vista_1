# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.interchange        import getDateEditValue, getLineEditValue, getRBComboBoxValue, setDateEditValue, \
                                       setLineEditValue, setRBComboBoxValue, setComboBoxValue, setCheckBoxValue, \
                                       getCheckBoxValue, getComboBoxValue
from library.ItemsListDialog    import CItemEditorBaseDialog
from library.Utils              import forceInt, toVariant

from Orgs                  import selectOrganisation

from Ui_PaymentSchemeEditor import Ui_PaymentSchemeEditor

class CPaymentSchemeEditor(CItemEditorBaseDialog, Ui_PaymentSchemeEditor):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'PaymentScheme')
        db = QtGui.qApp.db
        self.type = parent.contractType - 1
        self.cmbStructureCodeItems = [u'%.2d' %i for i in range(1, 31)]
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.cmbPerson.setIsInvestigator(True)
        self.setVisibleContractType(self.type)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.type = forceInt(record.value('type'))
        setLineEditValue(self.edtNumber, record, 'number')
        setRBComboBoxValue(self.cmbOrgId, record, 'org_id')
        setLineEditValue(self.edtContractNumber, record, 'numberProtocol')
        setLineEditValue(self.edtContractName, record, 'nameProtocol')
        setDateEditValue(self.edtDate, record, 'begDate')
        setDateEditValue(self.edtEndDate, record, 'endDate')
        self.edtEndDate.setMinimumDate(self.edtDate.date())
        setLineEditValue(self.edtContractSum, record, 'total')
        setRBComboBoxValue(self.cmbPerson, record, 'person_id')
        setLineEditValue(self.edtSubjectContract, record, 'subjectContract')
        setLineEditValue(self.edtPostAddress, record, 'postAddress')
        setRBComboBoxValue(self.cmbOrgStructure, record, 'orgStructure_id')
        setComboBoxValue(self.cmbStatus, record, 'status')
        setCheckBoxValue(self.chkEnrollment, record, 'enrollment')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('type', toVariant(self.type))
        getLineEditValue(self.edtNumber, record, 'number')
        getRBComboBoxValue(self.cmbOrgId, record, 'org_id')
        getDateEditValue(self.edtDate, record, 'begDate')
        getDateEditValue(self.edtEndDate, record, 'endDate')
        getLineEditValue(self.edtContractSum, record, 'total')

        if self.type:
            getLineEditValue(self.edtSubjectContract, record, 'subjectContract')
            getLineEditValue(self.edtPostAddress, record, 'postAddress')
            getComboBoxValue(self.cmbStatus, record, 'status')
        else:
            getLineEditValue(self.edtContractNumber, record, 'numberProtocol')
            getLineEditValue(self.edtContractName, record, 'nameProtocol')
            getRBComboBoxValue(self.cmbPerson, record, 'person_id')
            getCheckBoxValue(self.chkEnrollment, record, 'enrollment')
            getRBComboBoxValue(self.cmbOrgStructure, record, 'orgStructure_id')
        return record

    def checkDataEntered(self):
        msg = None
        if self.edtDate.text() == '':
            msg = u'дату заключеня договора'
        elif not self.cmbOrgId.value():
            msg = u'наименование организации'
        elif not self.type:
            if not self.edtContractNumber.text():
                msg = u'номер протокола'
            elif not self.edtContractName.text():
                msg = u'наименование протокола'
        if msg:
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести %s.' % msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return False
        return True

    def setVisibleContractType(self, bool):
        self.lblContractNumber.setVisible(not bool)
        self.edtContractNumber.setVisible(not bool)
        self.lblContractName.setVisible(not bool)
        self.edtContractName.setVisible(not bool)
        self.lblPerson.setVisible(not bool)
        self.cmbPerson.setVisible(not bool)
        self.lblOrgStructure.setVisible(not bool)
        self.cmbOrgStructure.setVisible(not bool)
        self.chkEnrollment.setVisible(not bool)
        self.lblSubjectContract.setVisible(bool)
        self.edtSubjectContract.setVisible(bool)
        self.lblPostAddress.setVisible(bool)
        self.edtPostAddress.setVisible(bool)
        self.lblStatus.setVisible(bool)
        self.cmbStatus.setVisible(bool)


    @QtCore.pyqtSlot()
    def on_btnSelectOrgName_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrgId.value(), False)
        self.cmbOrgId.update()
        if orgId:
            self.cmbOrgId.setValue(orgId)


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDate_dateChanged(self, date):
        self.edtEndDate.setMinimumDate(date)