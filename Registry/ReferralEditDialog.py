# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Exchange.R23.netrica.services import NetricaServices
from library.DialogBase     import CDialogBase
from library.RecordLock     import CRecordLockMixin
from library.Utils          import forceInt, forceRef, forceString, toVariant, forceDate, forceDateTime

from Ui_ReferralEditDialog  import Ui_EdtReferralDialog


class CReferralEditDialog(CDialogBase, CRecordLockMixin, Ui_EdtReferralDialog):
    idFieldName = 'id'
    def __init__(self, referralId=None, referralNumber=None, parent=None):
        CDialogBase.__init__(self, parent)
        CRecordLockMixin.__init__(self)
        self.setupUi(self)
        self.db = QtGui.qApp.db
        self.tblReferral = self.db.table('Referral')
        if referralId:
            self.recReferral = self.db.getRecordEx(self.tblReferral, '*', self.tblReferral['id'].eq(referralId))
        elif referralNumber:
            self.recReferral = self.db.getRecordEx(self.tblReferral, '*', [self.tblReferral['number'].eq(referralNumber),
                                                                           self.tblReferral['isSend'].eq(1)])
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не удалось получить направление')
            return
        self.cmbRelegateMo.setFilter('NOT isMedical = 0')
        self.cmbReferralType.setTable('rbReferralType')
        self.cmbSpeciality.setTable('rbMedicalAidProfile', True, filter='netrica_Code IS NOT NULL')
        self.cmbBedProfile.setTable('rbHospitalBedProfile', order='name')
        self.cmbOrgStructure.setTable('rbOrgStructureProfile')
        self.edtReferralNumber.setReadOnly(True)
        if self.recReferral:
            self.setRecord(self.recReferral)

    def checkData(self):
        record = self.recReferral
        if QtGui.qApp.defaultKLADR().startswith('23'):
            if forceInt(record.value('type')) == 1 and not forceDate(record.value('date')) == QtCore.QDate.currentDate():
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Данные по направлению отправлены в ТФОМС и не могут быть изменены')
                return False
        if forceInt(record.value('isCancelled')):
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Направление было аннулировано и не может быть изменено')
            return False
        if forceInt(record.value('deleted')):
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Направление было удалено')
            return False
        return True

    def beforeSave(self):
        if forceInt(self.cmbReferralType.code()) == 1:
            if not forceString(self.edtReferralNumber.text()):
                self.checkInputMessage(u'Не введен номер направления', False, self.edtReferralNumber)
                return False
            if self.edtReferralDate.date().isNull():
                self.checkInputMessage(u'Не верная дата направления', False, self.edtReferralDate)
                return False
            if self.edtReferralPlanedDate.date().isNull():
                self.checkInputMessage(u'Не верная дата плановой госпитализации', False, self.edtReferralPlanedDate)
                return False
            if not self.edtReferralPlanedDate.date().isNull() and self.edtReferralPlanedDate.date() < self.edtReferralDate.date():
                self.checkInputMessage(u'Плановая дата не может быть меньше даты выдачи направления', False, self.edtReferralPlanedDate)
                return False
            if not self.cmbClinicType.currentIndex():
                self.checkInputMessage(u'Не выбран тип стационара', False, self.cmbClinicType)
                return False
            if not forceString(self.cmbReferralMKB.text()):
                self.checkInputMessage(u'Не выбран код МКБ', False, self.cmbReferralMKB)
                return False
            if not self.cmbRelegateMo.value():
                self.checkInputMessage(u'Не выбрано целевое МО', False, self.cmbRelegateMo)
                return False
            if not self.cmbPerson.value():
                self.checkInputMessage(u'Не выбран врач', False, self.cmbPerson)
                return False
            if not self.cmbBedProfile.value():
                self.checkInputMessage(u'Не выбран профиль койки', False, self.cmbBedProfile)
                return False
            if not self.cmbOrgStructure.value():
                self.checkInputMessage(u'Не выбран профиль отделения', False, self.cmbOrgStructure)
        else:
            if not forceString(self.edtReferralNumber.text()):
                self.checkInputMessage(u'Не введен номер направления', False, self.edtReferralNumber)
                return False
            if self.edtReferralDate.date().isNull():
                self.checkInputMessage(u'Не верная дата направления', False, self.edtReferralDate)
                return False
            if self.edtReferralPlanedDate.date().isNull():
                self.checkInputMessage(u'Не верная дата плановой госпитализации', False, self.edtReferralPlanedDate)
                return False
            if not self.edtReferralPlanedDate.date().isNull() and self.edtReferralPlanedDate.date() < self.edtReferralDate.date():
                self.checkInputMessage(u'Плановая дата не может быть меньше даты выдачи направления', False, self.edtReferralPlanedDate)
                return False
            # if not self.cmbSpeciality.value():
            #     self.checkInputMessage(u'Не выбрана специальность', False, self.cmbSpeciality)
            #     return False
            if not forceString(self.cmbReferralMKB.text()):
                self.checkInputMessage(u'Не выбран код МКБ', False, self.cmbReferralMKB)
                return False
            if not self.cmbRelegateMo.value():
                self.checkInputMessage(u'Не выбрано целевое МО', False, self.cmbRelegateMo)
                return False
            # if not self.cmbPerson.value():
            #     self.checkInputMessage(u'Не выбран врач', False, self.cmbPerson)
            #     return False
        return True

    def getRecord(self):
        if self.beforeSave():
            self.recReferral.setValue('number', toVariant(forceString(self.edtReferralNumber.text())))
            self.recReferral.setValue('date', toVariant(forceDate(self.edtReferralDate.date())))
            self.recReferral.setValue('hospDate', toVariant(forceDate(self.edtReferralPlanedDate.date())))
            self.recReferral.setValue('relegateOrg_id', toVariant(forceInt(self.cmbRelegateMo.value())))
            self.recReferral.setValue('MKB', toVariant(forceString(self.cmbReferralMKB.text())))
            self.recReferral.setValue('clinicType', toVariant(forceInt(self.cmbClinicType.currentIndex())))
            self.recReferral.setValue('medProfile_id', toVariant(forceInt(self.cmbSpeciality.value())))
            if forceInt(self.cmbPerson.value()):
                self.recReferral.setValue('person', toVariant(forceInt(self.cmbPerson.value())))
            else:
                self.recReferral.setValue('person', toVariant(forceInt(self.cmbPerson.currentText())))
            self.recReferral.setValue('hospBedProfile_id', toVariant(forceInt(self.cmbBedProfile.value())))
            self.recReferral.setValue('orgStructure', toVariant(forceInt(self.cmbOrgStructure.value())))
            if self.db.updateRecord(self.tblReferral, self.recReferral):
                return True
            else:
                return False
        else:
            return False



    def setRecord(self, record):
        if not forceInt(record.value('type')) == 1:
            self.lblBedProfile.setVisible(False)
            self.cmbBedProfile.setVisible(False)
            self.lblOrgStructureProfile.setVisible(False)
            self.cmbOrgStructure.setVisible(False)
            self.lblClinicType.setVisible(False)
            self.cmbClinicType.setVisible(False)

        self.cmbReferralType.setValue(forceInt(record.value('type')))
        self.edtReferralNumber.setText(forceString(record.value('number')))
        self.edtReferralDate.setDate(forceDate(record.value('date')))
        self.edtReferralPlanedDate.setDate(forceDate(record.value('hospDate')))
        self.cmbRelegateMo.setValue(forceInt(record.value('relegateOrg_id')))
        self.cmbReferralMKB.setText(forceString(record.value('MKB')))
        self.cmbClinicType.setCurrentIndex(forceInt(record.value('clinicType')))
        self.cmbSpeciality.setValue(forceInt(record.value('medProfile_id')))
        if forceInt(record.value('person')):
            self.cmbPerson.setValue(forceInt(record.value('person')))
        else:
            self.cmbPerson.setEditText(forceString(record.value('person')))
        self.cmbBedProfile.setValue(forceInt(record.value('hospBedProfile_id')))
        self.cmbOrgStructure.setValue(forceInt(record.value('orgStructure')))

    def updReferral(self):
        refInfo = {}
        refInfo['type'] = self.cmbReferralType.value()
        refInfo['number'] = self.edtReferralNumber.text()
        refInfo['refDate'] = forceDateTime(self.edtReferralDate.date()).toPyDateTime()
        refInfo['MKB'] = forceString(self.cmbReferralMKB.text())
        refInfo['plannedDate'] = forceDateTime(self.edtReferralPlanedDate.date()).toPyDateTime()
        refInfo['relegateMO'] = forceString(self.cmbRelegateMo.value())
        refInfo['medProfile'] = forceString(self.cmbSpeciality.value())
        refInfo['netrica_id'] = forceString(self.recReferral.value('netrica_id'))
        service = NetricaServices()
        responce = service.updateReferral(refInfo)
        if responce:
            return True
        else:
            return False