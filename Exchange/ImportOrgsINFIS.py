# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт данных об ЛПУ из справочника ИНФИС
"""
from Ui_ImportOrgsINFIS import Ui_Dialog
from Cimport import *

# *****************************************************************************************

def ImportOrgsINFIS(widget):
    dlg=CImportOrgsINFIS(widget)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportOrgsINFISFileName',  '')))
    dublicates = forceInt(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportOrgsINFISgbDublicates',  1))
    if dublicates == 0:
        dlg.chkUpdate.setChecked(True)
    elif dublicates == 1:
        dlg.chkSkip.setChecked(True)
    else:
        dlg.chkAskUser.setChecked(True)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportOrgsINFISFileName'] = toVariant(dlg.edtFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportOrgsINFISgbDublicates'] = \
        toVariant(0 if dlg.chkUpdate.isChecked() else (1 if dlg.chkSkip.isChecked() else 2))

# *****************************************************************************************

class CImportOrgsINFIS(QtGui.QDialog, Ui_Dialog, CDBFimport):
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
        self.table = self.db.table('Organisation')
        self.tableAccount = self.db.table('Organisation_Account')
        self.tableBank = self.db.table('Bank')

# *****************************************************************************************

    def startImport(self):
        self.ok = False
        db = QtGui.qApp.db

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbfOrgs = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        self.progressBar.reset()
        self.progressBar.setMaximum(len(dbfOrgs)-1)
        self.progressBar.setFormat('%v')

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.dupAskUser = self.chkAskUser.isChecked()
        self.dupUpdate = self.chkUpdate.isChecked()
        self.dupSkip = self.chkSkip.isChecked()


        self.process(dbfOrgs, self.processRow)
        self.ok = not self.aborted

        dbfOrgs.close()
        self.log.append(u'добавлено: %d; изменено: %d' % (self.nAdded, self.nUpdated))
        self.log.append(u'пропущено: %d; обработано: %d' % (self.nSkipped, self.nProcessed))
        self.log.append(u'готово')

# *****************************************************************************************

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

# *****************************************************************************************

    def processRow(self,  row):
        INN = forceString(row['INN'])

        if INN == '':
            self.log.append(u'<b><font color=orange>ОШИБКА:</b> '\
                u'ИНН пуст, пропуск строки %d.' % (self.progressBar.value()+1))
            self.nSkipped += 1
            return

        infisCode = forceString(row['CODE'])
        KPP = forceString(row['KPP'])
        isMain = (forceString(row['FTMO']) != '')
        fullName = forceString(row['DOCNAME'])
        shortName = forceString(row['NAME'])
        mailCode = forceString(row['MAILCODE'])
        OKATO = forceString(row['OKATO'])
        OKPO = forceString(row['OKPO'])
        address = forceString(row['ADDRESS'])
        phone = forceString(row['PHONE'])
        MFO = forceString(row['MFO'])
        account = forceString(row['PC'])
        corrAccount = forceString(row['PC2'])
        subAccount = forceString(row['PC3'])
        notesList = []

        for (str,  param) in (
                (u'КБК: %s', 'KBK'),
                (u'ОКОНХ: %s', 'OKONH'),
                (u'email: %s', 'MAILADDR'),
                (u'%s', 'PAY_REM1'),
                (u'%s', 'PAY_REM2')):
            val = forceString(row[param])

            if val != '':
                notesList.append(str % val)

        notes = u', '.join([k for k in notesList])
        accounts = []

        bank = u'%s %s' % (forceString(row['BANK']),  forceString(row['CITY']))
        branchName = forceString(row['FILIAL'])

        self.log.append(u'ЛПУ: "%s", код ИНФИС: "%s", ИНН "%s", является головной: "%s"' % \
            (fullName,  infisCode,  INN, u'да' if isMain else u'нет'))

        self.addOrUpdateOrg(isMain, shortName, fullName, INN, KPP, \
            OKPO, OKATO, address, phone,  infisCode,  notes,  account,
            corrAccount, subAccount, bank,  branchName,  MFO)
        self.nProcessed += 1

# *****************************************************************************************

    def addOrUpdateOrg(self, isMain, shortName, fullName, INN, KPP,
            OKPO, OKATO, address, phone,  infisCode,  notes,  account,
            corrAccount, subAccount, bank,  branchName,  MFO):

        orgId = self.infis2orgId(infisCode)

        if orgId:
            self.log.append(u'В БД найдено ЛПУ с' \
                u' совпадающим ИНФИС кодом (id=%d).' % orgId)
            self.updateLPU(orgId, isMain,  shortName, fullName, INN,
                KPP, OKPO, OKATO, address, phone,  infisCode,  notes, account,
                corrAccount, subAccount, bank,  branchName,  MFO)
        else:
            orgId = self.findOrgByINNandKPP(INN, KPP)

            if orgId:
                self.log.append(u'В БД найдено ЛПУ с' \
                    u' совпадающим ИНН и КПП (id=%d).' % orgId)
                self.updateLPU(orgId, isMain,  shortName, fullName, INN,
                    KPP, OKPO, OKATO, address, phone,  infisCode,  notes, account,
                    corrAccount, subAccount, bank,  branchName,  MFO)
            else:
                orgId = self.findOrgByName(fullName)

                if orgId:
                    self.log.append(u'В БД найдено ЛПУ с' \
                        u' совпадающим наименованием (id=%d).' % orgId)
                    self.updateLPU(orgId, isMain,  shortName, fullName, INN,
                        KPP, OKPO, OKATO, address, phone,  infisCode,  notes, account,
                        corrAccount, subAccount, bank,  branchName,  MFO)
                else:
                    self.log.append(u'Добавляем.')
                    orgId = self.addOrg(shortName, fullName, INN, KPP, OKPO, OKATO,
                        address, phone,  infisCode,  notes)
                    self.addBankAccount(orgId, account, corrAccount, subAccount, bank, branchName,  MFO)
                    self.nAdded += 1

# *****************************************************************************************

    def updateLPU(self,  id,  isMain,  shortName, fullName, INN, KPP, OKPO, OKATO,
                        address, phone,  infisCode,  notes, account, corrAccount, subAccount,
                        bank,  branchName,  MFO):
        if isMain:
            update = False

            if self.dupAskUser:
                update = (QtGui.QMessageBox.question(
                    self, u'Совпадающее ЛПУ',
                    u'Обновить?',
                    QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes)

            if self.dupUpdate or update:
                self.log.append(u'Обновляем')
                self.updateOrg(id, shortName, fullName, INN, KPP, OKPO, OKATO,
                        address, phone,  infisCode,  notes)

                if account == '' or bank == '' and MFO == '':
                    self.log.append(u'<b><font color=red>ОШИБКА:</b>'
                    u' неверные банковские реквизиты, строка "%d" в dbf.' % \
                    (self.progressBar.value()+1))
                else:
                    if not self.findBankAccount(id, account, corrAccount, subAccount,
                                                            bank, branchName, MFO):
                        self.log.append(u'Р/C %s не найден, добавляем.' % account)
                        self.addBankAccount(id, account, corrAccount, subAccount,
                                                        bank, branchName, MFO)
                    else:
                        self.log.append(u'Р/C %s уже задан, пропускаем.' % account)

                self.nUpdated += 1
            else:
                self.log.append(u'Пропускаем')
                self.nSkipped += 1
        else:
            self.log.append(u'Организация не является основной,' \
                u' добавляем только инфис код.')
            self.addObsoleteInfisCode(id, infisCode)
            self.nAdded += 1

# *****************************************************************************************

    def addOrg(self, shortName, fullName, INN, KPP, OKPO, OKATO,
                        address, phone,  infisCode,  notes):
        record = self.table.newRecord()
        record.setValue('fullName', toVariant(fullName))
        record.setValue('shortName', toVariant(shortName))
        record.setValue('title', toVariant(shortName))
        record.setValue('INN', toVariant(INN))
        record.setValue('KPP', toVariant(KPP))
        record.setValue('OKPO', toVariant(OKPO))
        record.setValue('OKVED', toVariant(OKATO))
        record.setValue('address', toVariant(address))
        record.setValue('phone', toVariant(phone))
#        record.setValue('net_id',  toVariant(self.matureNetId))
        record.setValue('notes', toVariant(notes))
        record.setValue('infisCode',  toVariant(infisCode))
        return self.db.insertRecord(self.table, record)

# *****************************************************************************************

    def updateOrg(self, orgId, shortName, fullName, INN, KPP, OKPO, OKATO,
                        address, phone,  infisCode,  notes):
        record = self.db.getRecord(self.table, '*', orgId)
        record.setValue('fullName', toVariant(fullName))
        record.setValue('shortName', toVariant(shortName))
        record.setValue('title', toVariant(shortName))
        record.setValue('INN', toVariant(INN))
        record.setValue('KPP', toVariant(KPP))
        record.setValue('OKPO', toVariant(OKPO))
        record.setValue('OKVED', toVariant(OKATO))
        record.setValue('address', toVariant(address))
        record.setValue('phone', toVariant(phone))
#        record.setValue('net_id',  toVariant(self.matureNetId))

        if notes != '':
            record.setValue('notes', toVariant(notes))

        record.setValue('infisCode',  toVariant(infisCode))
        return self.db.updateRecord(self.table, record)

# *****************************************************************************************

    def addBankAccount(self, orgId, account, corrAccount, subAccount,  bank, branchName, MFO):
        if orgId and account != '':
            bankId = self.findBank(corrAccount, subAccount, bank,  branchName, MFO)

            if not bankId:
                self.addBank(corrAccount, subAccount, bank,  branchName, MFO)

            if bankId:
                record = self.tableAccount.newRecord()
                record.setValue('organisation_id', toVariant(orgId))
                record.setValue('bank_id',  toVariant(bankId))
                record.setValue('name',  toVariant(account))
                return self.db.insertRecord(self.tableAccount, record)

        return None

# *****************************************************************************************

    def addBank(self, corrAccount, subAccount, bank,  branchName,  MFO):
        record = self.tableBank.newRecord()
        record.setValue('BIK',  toVariant(MFO))
        record.setValue('name',  toVariant(bank))

        if branchName != '':
            record.setValue('branchName', toVariant(branchName))

        if corrAccount != '':
            record.setValue('corrAccount',  toVariant(corrAccount))

        if subAccount != '':
            record.setValue('subAccount',  toVariant(subAccount))

        return self.db.insertRecord(self.tableBank, record)

# *****************************************************************************************

    def addObsoleteInfisCode(self,  id, newInfisCode):
        if id and newInfisCode != '':
            record = self.db.getRecord(self.table, 'id, infisCode, obsoleteInfisCode', id)

            if record:
                infisCode = forceString(record.value('infisCode'))

                if infisCode == newInfisCode:
                    return

                obsoleteInfisCode = forceString(record.value('obsoleteInfisCode')).split(',')

                for x in obsoleteInfisCode:
                    if x == newInfisCode:
                        return

                obsoleteInfisCode.append(newInfisCode)
                str = u','.join(obsoleteInfisCode)
                record.setValue('obsoleteInfisCode',  toVariant(str))
                self.db.updateRecord(self.table, record)


# *****************************************************************************************

    def findOrgByINNandKPP(self, INN, KPP):
        record = self.db.getRecordEx(self.table, 'id',  [self.table['deleted'].eq(0),
                                                          self.table['INN'].eq(INN),
                                                          self.table['KPP'].eq(KPP)
                                                         ], 'id')
        if record:
            return forceRef(record.value(0))
        else:
            return None

# *****************************************************************************************

    def findOrgByName(self, fullName):
        record = self.db.getRecordEx(self.table, 'id',  [self.table['deleted'].eq(0),
                                                          self.table['fullName'].eq(fullName)], 'id')
        if record:
            return forceRef(record.value(0))
        else:
            return None

# *****************************************************************************************

    bankCache = {}

    def findBank(self, corrAccount, subAccount, bank,  branchName,  MFO):
        key = (corrAccount, subAccount, bank,  branchName,  MFO)
        result = self.bankCache.get(key)

        if not result:
            cond = []

            cond.append(self.tableBank['deleted'].eq(0))
            cond.append(self.tableBank['name'].eq(bank))
            cond.append(self.tableBank['BIK'].eq(MFO))
            if branchName != '':
                cond.append(self.tableBank['branchName'].eq(branchName))

            if corrAccount != '':
                cond.append(self.tableBank['corrAccount'].eq(corrAccount))

            if subAccount != '':
                cond.append(self.tableBank['subAccount'].eq(subAccount))

            record = self.db.getRecordEx(self.tableBank, 'id', cond,  'id')

            if record:
                result = forceRef(record.value(0))
                self.bankCache[key] = result

        return result

# *****************************************************************************************

    bankAccountCache = {}

    def findBankAccount(self, orgId, account, corrAccount, subAccount,  bank, branchName, MFO):
        bankId = self.findBank(corrAccount, subAccount, bank, branchName, MFO)

        if bankId:
            key = (orgId,  bankId,  account)
            result = self.bankAccountCache.get(key)

            if not result:
                cond = []

                cond.append(self.tableAccount['organisation_id'].eq(orgId))
                cond.append(self.tableAccount['bank_id'].eq(bankId))
                cond.append(self.tableAccount['name'].eq(account))

                record = self.db.getRecordEx(self.tableAccount, 'id', cond,  'id')

                if record:
                    result = forceRef(record.value(0))
                    self.bankAccountCache[key] = result

            return result
        return None

# *****************************************************************************************

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbfOrgs = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfOrgs)))