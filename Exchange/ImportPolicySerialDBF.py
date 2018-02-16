# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт серий полисов из DBF
"""

from Ui_ImportPolicySerialDBF import Ui_Dialog
from Cimport import *


def ImportPolicySerialDBF(widget):
    dlg=CImportPolicySerialDBF(widget)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPolicySerialDBFFileName',  '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPolicySerialDBFFileName'] = toVariant(dlg.edtFileName.text())


class CImportPolicySerialDBF(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.parent = parent

        self.ok = False
        self.aborted = False
        self.dupAskUser = False
        self.dupUpdate = False
        self.dupSkip = False

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.cachePolicySerial = {}
        self.table = self.db.table('Organisation_PolicySerial')
        self.tablePolicyType = self.db.table('rbPolicyType')

        self.policyTypeDMSId = None
        self.policyTypeFactId = None
        self.policyTypeTerId = None

        self.mapPolicyType = {}


    def startImport(self):
        self.ok = False
        db = QtGui.qApp.db

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbfPolicySerial = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        self.progressBar.reset()
        self.progressBar.setMaximum(len(dbfPolicySerial)-1)
        self.progressBar.setFormat('%v')

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.dupAskUser = self.chkAskUser.isChecked()
        self.dupUpdate = self.chkUpdate.isChecked()
        self.dupSkip = self.chkSkip.isChecked()

        self.policyTypeTerId = forceRef(QtGui.qApp.db.translate(self.tablePolicyType, 'code',
            '1', 'id'))

        if not self.policyTypeTerId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найден тип полиса (rbPolicyType) с кодом "1"(ОМС территориальный).')
            return

        self.policyTypeFactId = forceRef(QtGui.qApp.db.translate(self.tablePolicyType, 'code',
            '2', 'id'))

        if not self.policyTypeFactId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найден тип полиса (rbPolicyType) с кодом "2"(ОМС производственный).')
            return

        self.policyTypeDMSId = forceRef(QtGui.qApp.db.translate(self.tablePolicyType, 'code',
            '3', 'id'))

        if not self.policyTypeDMSId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найден тип полиса (rbPolicyType) с кодом "3"(ДМС).')
            return

        self.mapPolicyType = {' ': self.policyTypeTerId, u'т' : self.policyTypeTerId,
            u'п' : self.policyTypeFactId, u'д' : self.policyTypeDMSId}

        self.process(dbfPolicySerial, self.processTariff)
        self.ok = not self.aborted

        dbfPolicySerial.close()
        self.log.append(u'добавлено: %d; изменено: %d' % (self.nAdded, self.nUpdated))
        self.log.append(u'пропущено: %d; обработано: %d' % (self.nSkipped, self.nProcessed))
        self.log.append(u'готово')


    def process(self, dbf, step):
        try:
            for row in dbf:
                QtGui.qApp.processEvents()
                if self.aborted:
                    self.reject()
                    return
                self.progressBar.setValue(self.progressBar.value()+1)
                step(row)

        except ValueError:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
                    u' неверное значение строки "%d" в dbf.' % \
                    (self.progressBar.value()+1))
            self.nSkipped += 1
            self.aborted = True


    def processTariff(self,  row):
        infisCode = forceString(row['PAYER'])
        serial = forceString(row['CODE'])
        typeCode = forceString(row['TYPEINS'])

        if infisCode == '':
            self.log.append(u'<b><font color=orange>ОШИБКА:</b> '\
                u'Инфис код пуст, пропуск строки %d.' % (self.progressBar.value()+1))
            self.nSkipped += 1
            return

        orgId = self.infis2orgId(infisCode)

        if not orgId:
            self.log.append(u'<b><font color=orange>ОШИБКА:</b> '\
                u'Организация с инфис кодом "%s" не найдена.' % infisCode)
            self.nSkipped += 1
            return


        if not (typeCode in ['',' ', u'т', u'п', u'д']):
            self.log.append(u'<b><font color=orange>ОШИБКА:</b> '\
                u'Тип страхователя "%s" не поддерживается.' % typeCode)
            self.nSkipped += 1
            return

        self.log.append(u'Инфис код: "%s", серия "%s", тип "%s"' % (infisCode,  serial,  typeCode))

        self.addOrUpdatePolicySerial(orgId,  serial,  self.mapPolicyType.get(typeCode))
        self.nProcessed += 1


    def addOrUpdatePolicySerial(self, orgId,  serial,  typeId):
        policySerialId = self.findPolicySerial(orgId,  serial,  typeId)

        if policySerialId:
            self.log.append(u'Пропускаем: Найдена совпадающая серия (id=%d).'%policySerialId)
            self.nSkipped += 1
        else:
            self.log.append(u'Добавляем.')
            self.addPolicySerial(orgId, serial, typeId)
            self.nAdded += 1


    def findPolicySerial(self, orgId,  serial,  typeId):
        key = (orgId, serial, typeId)
        id = self.cachePolicySerial.get(key)

        if not id:
            cond = []
            cond.append(self.table['organisation_id'].eq(orgId))
            cond.append(self.table['serial'].eq(serial))
            if typeId:
                cond.append(self.table['policyType_id'].eq(typeId))
            else:
                cond.append(self.table['policyType_id'].isNull())

            record = self.db.getRecordEx(self.table, 'id',  cond)

            if record:
                id = forceRef(record.value(0))
                self.cachePolicySerial[key] = id

        return id


    def addPolicySerial(self,  orgId,  serial,  typeId):
        record = self.table.newRecord()
        record.setValue('organisation_id',  toVariant(orgId))
        record.setValue('serial',  toVariant(serial))

        if typeId:
            record.setValue('policyType_id',  toVariant(typeId))

        self.cachePolicySerial[(orgId, serial, typeId)] = self.db.insertRecord(self.table, record)


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbfPolicySerial = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfPolicySerial)))