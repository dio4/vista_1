#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Events.Utils import CPayStatus, getPayStatusMask
from Accounting.Utils import updateAccounts, updateDocsPayStatus

from Ui_ImportPayRefuseR23 import Ui_Dialog
from Cimport import *
from library.dbfpy import dbf


def ImportPayRefuseR23Native(widget, accountId, accountItemIdList, exportFormat):
    dlg = CImportPayRefuseR23Native(widget, accountId, accountItemIdList, exportFormat)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR23FileName', '')))
    dlg.chkRefreshPolicyInfo.setChecked(forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR23RefreshPolicy', False)))
    dlg.chkDeleteAccount.setChecked(forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR23DeleteAccount', False)))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR23FileName'] = toVariant(dlg.edtFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR23RefreshPolicy'] = toVariant(dlg.chkRefreshPolicyInfo.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR23DeleteAccount'] = toVariant(dlg.chkDeleteAccount.isChecked())


class CImportPayRefuseR23Native(QtGui.QDialog, Ui_Dialog, CDBFimport):
    sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}

    def __init__(self, parent, accountId, accountItemIdList, exportFormat):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.parent = parent
        CDBFimport.__init__(self, self.log)
        self.accountId=accountId
        self.accountItemIdList=accountItemIdList
        self.checkName()
        self.errorPrefix = ''
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0
        self.tblPayRefuseType = tbl('rbPayRefuseType')
        self.tableAccountItem = tbl('Account_Item')
        self.tableEvent = tbl('Event')
        self.tableAccount = tbl('Account')
        self.tableClientPolicy = tbl('ClientPolicy')
        self.tableAcc=self.db.join(self.tableAccountItem, self.tableAccount,
            'Account_Item.master_id=Account.id').join(self.tableEvent,
            'Account_Item.event_id=Event.id')
        self.prevContractId = None
        self.financeTypeOMS = forceRef(self.db.translate('rbFinance',
            'code', '2', 'id'))
        self.orgCache = {}
        self.deleteAccount = False
        self.isStationary = exportFormat in ('R23NATIVES', 'R23DKKBS')
        self.isDKKB = exportFormat in ('R23DKKB', 'R23DKKBS')


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы ZIP (*.zip)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            fileName = unicode(forceStringEx(self.edtFileName.text()))
            dbfR23 = self.dbfFromZIP(fileName)
            if dbfR23 is not None:
                self.btnImport.setEnabled(True)
                self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfR23)))

    def err2log(self, e):
        self.log.append(self.errorPrefix+e)

    def dbfFromZIP(self, zipFileName):
        result = None
        if is_zipfile(forceString(zipFileName)):
            archive = ZipFile(forceString(zipFileName), "r")
            names = archive.namelist()
            fileName = ''
            for fN in names:
                if fN[-4:].lower() == '.dbf' and fN[0].upper() == 'P':
                    fileName = fN
            if fileName:
                tmpFile = QtCore.QTemporaryFile()

                if not tmpFile.open(QtCore.QFile.WriteOnly):
                    self.log.append(u'Не удаётся открыть файл для записи %s:\n%s.' % (tmpFile, tmpFile.errorString()))
                    self.log.update()

                data = archive.read(fileName)  # read the binary data
                tmpFile.write(data)
                tmpFile.close()
                fileInfo = QtCore.QFileInfo(tmpFile)
                result = dbf.Dbf(forceString(fileInfo.filePath()), encoding='cp866')
            else:
                self.log.append(u'В архиве нет файла подходящего под маску P*.dbf')
                self.log.update()

        return result

    def startImport(self):
        self.deleteAccount = False
        self.progressBar.setFormat('%p%')
        self.currentAccountOnly = self.chkOnlyCurrentAccount.isChecked()
        self.updateClientPolicy = self.chkRefreshPolicyInfo.isChecked()
#        self.importPayed =self.chkImportPayed.isChecked()
#        self.importRefused = self.chkImportRefused.isChecked()
        self.confirmation = self.edtConfirmation.text()
        importPolicyInfo = self.tabImportType.currentIndex() == 1
        if not self.confirmation:
            self.log.append(u'нет подтверждения')
            return

        self.prevContractId = None
        self.accountIdSet = set()

        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0

        fileName = unicode(self.edtFileName.text())
        dbfR23 = self.dbfFromZIP(fileName)
        self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfR23)))
        requiredFields = ['FIO', 'IMA', 'OTCH', 'POL', 'DATR', 'PV', 'DVOZVRAT',  'VS',  'SN']

        # if importPolicyInfo:
        #     requiredFields += ['KSMOF', 'SPSF', 'SPNF', 'Q_OGRNF', 'CS']
        #     self.policyTypeId = forceRef(self.db.translate('rbPolicyType', 'code', '1', 'id'))
        #     self.policyKindId = forceRef(self.db.translate('rbPolicyKind', 'code', '1', 'id'))
        #     self.log.append(u'Режим предварительной проверки счетов.')
        #     self.accountNumber = forceString(self.db.translate('Account', 'id', self.accountId, 'number'))

        assert dbfCheckNames(dbfR23, requiredFields)
        self.progressBar.setMaximum(len(dbfR23)-1)
        process = self.processRow #self.processPolicyRow if importPolicyInfo else self.processRow

        for row in dbfR23:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.progressBar.step()
            self.stat.setText(
                u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
                (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))
            process(row)


        self.stat.setText(
            u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
            (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))

        # if importPolicyInfo:
        #     if self.deleteAccount and self.chkDeleteAccount.isChecked():
        #         self.log.append(u'Территория страхования одного из пациентов изменилась, текущий счет будет удалён.')
        #         self.parent.tblAccounts.removeSelectedRows()
        #         self.parent.updateAccountsPanel(self.parent.modelAccounts.idList())
        # else:
        updateAccounts(list(self.accountIdSet))


    def processRow(self,  row):
        lastName = forceString(row['FIO'])
        firstName = forceString(row['IMA'])
        patrName = forceString(row['OTCH'])
        sex = self.sexMap.get(forceString(row['POL']))
        birthDate = QDate(row['DATR']) if row['DATR'] else QDate()
        refuseDate = QDate(row['DVOZVRAT']) if row['DVOZVRAT'] else QDate()
        refuseReasonCodeList =  forceString(row['PV']).split(' ')
        eventId = forceRef(row['SN'])
        payStatusMask = 0
        accDate = QDate(row['DATS'])#QDate(row['DATPS']) if row['DATPS'] else QDate()
        accNumber = forceString(row['NS'])

        self.errorPrefix = u'Строка %d (%s %s %s): ' % (self.progressBar.value(), lastName,  firstName,  patrName)

        accountType = forceString(row['VS'])
        if accountType not in ('3', '7', 'b', 'f', 'j', 'n'):
            self.err2log(u'тип счёта не возвратный, код "%s"' % accountType)
            return

        if refuseDate.isValid() and refuseReasonCodeList == []:
            self.err2log(u'нет кода отказа')
            return

        if not refuseDate.isValid() and refuseReasonCodeList != []:
            self.err2log(u'нет даты отказа')
            return

        if not eventId:
            self.err2log(u'отсутствует идентификатор случая')

        cond=[]
        if self.isStationary:
            cond.append(self.db.joinOr([self.tableEvent['externalId'].eq(eventId), self.tableEvent['id'].eq(eventId)]))
        else:
            # Пытаемся восстановить старую логику ДККБ
            cond.append(self.tableEvent['client_id' if self.isDKKB else 'id'].eq(toVariant(eventId)))

        if accDate.isValid():
            cond.append(self.tableAccount['settleDate'].eq(toVariant(accDate)))

        # if accNumber:
        #     cond.append(self.tableAccount['number'].eq(toVariant(accNumber)))

        # if self.currentAccountOnly:
        cond.append(self.tableAccount['id'].eq(toVariant(self.accountId)))

        fields = 'Account_Item.id, Account.date as Account_date, Account_Item.date as Account_Item_date, Account_Item.master_id as Account_id, Account.contract_id as contract_id'
        recordList = self.db.getRecordList(self.tableAcc, fields, where=cond)

        if recordList != []:
            for record in recordList:
                self.accountIdSet.add(forceRef(record.value('Account_id')))
                contractId = forceRef(record.value('contract_id'))

                if self.prevContractId != contractId:
                    self.prevContractId = contractId
                    financeId = forceRef(self.db.translate('Contract', 'id', contractId, 'finance_id'))
                    payStatusMask = getPayStatusMask(financeId)

                accDate = forceDate(record.value('Account_date'))
                accItemDate = forceDate(record.value('Account_Item_date'))

                if accItemDate:
                    self.err2log(u'счёт уже отказан')
                    return

                if accDate > refuseDate:
                    self.err2log(u'счёт уже отказан')
                    return

                self.nProcessed += 1
                accountItemId = forceRef(record.value('id'))

                accItem = self.db.getRecord(self.tableAccountItem, '*', accountItemId)
                accItem.setValue('date', toVariant(refuseDate))
                refuseTypeId = None

                if refuseDate:
                    self.nRefused += 1
                    refuseTypeId=forceRef(self.db.translate(
                    'rbPayRefuseType', 'code', refuseReasonCodeList[0], 'id'))

                if not refuseTypeId:
                    refuseTypeId = self.addRefuseTypeId(refuseReasonCodeList[0])

                accItem.setValue('refuseType_id', toVariant(refuseTypeId))
                updateDocsPayStatus(accItem, payStatusMask, CPayStatus.refusedBits)

                accItem.setValue('number', toVariant(self.confirmation))
                self.db.updateRecord(self.tableAccountItem, accItem)
        else:
            self.nNotFound += 1
            self.err2log(u'счёт не найден')


    def addRefuseTypeId(self,  code):
        record = self.tblPayRefuseType.newRecord()
        record.setValue('code', toVariant(code))
        record.setValue('name ', toVariant(u'неизвестная причина с кодом "%s"' % code))
        record.setValue('finance_id', toVariant(self.financeTypeOMS))
        record.setValue('rerun', toVariant(1))
        return self.db.insertRecord(self.tblPayRefuseType, record)


    def processPolicyRow(self, row):
        lastName = forceString(row['FIO'])
        firstName = forceString(row['IMA'])
        patrName = forceString(row['OTCH'])

        self.errorPrefix = u'Строка %d (%s %s %s): ' % (self.progressBar.value(), lastName,  firstName,  patrName)

        clientId = forceRef(row['SN'])
        serial = forceString(row['SPSF'])
        number = forceString(row['SPNF'])
        insurerInfis = forceString(row['KSMOF'])
        (insurerId, insurerArea) = self.findOrgByInfis(insurerInfis)

        if not insurerInfis:
            self.err2log(u'отсутствует информация о страховой компании')

        if not (serial and number):
            self.err2log(u'отсутствует информация о полисе')

        if not clientId:
            self.err2log(u'отсутствует идентификатор пациента')

        if not insurerId and insurerInfis:
            self.err2log(u'Страховая компания с инфис кодом `%s` не найдена.' % insurerInfis)

        if clientId and serial and number:
            recordList = getClientPolicyList(clientId, True)
            record = recordList[-1] if recordList else None

            if record:
                oldSerial = forceString(record.value('serial'))
                oldNumber = forceString(record.value('number'))
                oldInsurerId = forceRef(record.value('insurer_id'))

                if oldSerial != serial or oldNumber != number \
                    or oldInsurerId != insurerId:

                    if self.updateClientPolicy:
                        if insurerId and insurerId != oldInsurerId:
                            self.err2log(u'<b><font color=green>Добавляем</font></b>'
                                u' новый полис %sN%s (%d) -> %sN%s (%d).' %
                                 (oldSerial,  oldNumber, oldInsurerId if oldInsurerId else 0, serial, number, insurerId))
                            self.addClientPolicy(clientId, insurerId, serial, number)
                        else:
                            self.err2log(u'<b><font color=blue>Обновляем</font></b>'
                                u' полис %sN%s -> %sN%s.' %
                                 (oldSerial,  oldNumber, serial, number))

                            record.setValue('serial', toVariant(serial))
                            record.setValue('number',  toVariant(number))
                            record.remove(record.indexOf('compulsoryServiceStop'))
                            record.remove(record.indexOf('voluntaryServiceStop'))
                            self.db.updateRecord(self.tableClientPolicy, record)

                    oldInsurerArea = forceString(self.db.translate('Organisation', 'id', oldInsurerId, 'area'))

                    if insurerArea and oldInsurerArea != insurerArea:
                        self.err2log(u'изменилась территория страхования пациента: `%s` -> `%s`'\
                                     % (oldInsurerArea, insurerArea))
                        if self.accountNumber == forceString(row['NS']):
                            self.err2log(u'территория изменилась для текущего счета')
                            self.deleteAccount = True
        else:
            self.nNotFound += 1

        self.nProcessed += 1


    def findOrgByInfis(self, infis):
        u"""Возвращает id и область страховой"""
        if not infis:
            return (None,  None)

        result = self.orgCache.get(infis,  -1)

        if result == -1:
            result = (None,  None)
            table = QtGui.qApp.db.table('Organisation')
            record = QtGui.qApp.db.getRecordEx(table, 'id, area',  [table['deleted'].eq(0),
                                                          table['infisCode'].eq(infis)], 'id')

            if record:
                result = (forceRef(record.value(0)), forceString(record.value(1)))
                self.orgCache[infis] = result

        return result


    def addClientPolicy(self, clientId, insurerId, serial, number):
        record = self.tableClientPolicy.newRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('insurer_id', toVariant(insurerId))
        record.setValue('policyType_id', toVariant(self.policyTypeId))
        record.setValue('policyKind_id', toVariant(self.policyKindId))
        record.setValue('serial', toVariant(serial))
        record.setValue('number', toVariant(number))
        self.db.insertRecord(self.tableClientPolicy, record)
