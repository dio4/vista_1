#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Events.Utils import CPayStatus, getPayStatusMask
from Accounting.Utils import updateAccounts, updateDocsPayStatus

from Ui_ImportPayRefuseR29 import Ui_Dialog
from Cimport import *


def ImportPayRefuseR29Native(widget, accountId, accountItemIdList):
    dlg = CImportPayRefuseR29Native(accountId, accountItemIdList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR29FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR29FileName'] = toVariant(dlg.edtFileName.text())


class CImportPayRefuseR29Native(QtGui.QDialog, Ui_Dialog, CDBFimport, CXMLimport):
    sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}
    zglvFields = ('VERSION', 'DATA', 'FILENAME')
    pacientFields = ('ID_PAC','VPOLIS', 'SPOLIS', 'NPOLIS', 'SMO', 'SMO_OGRN', 'SMO_OK', 'SMO_NAM', 'NOVOR')
    sluchFields = ('IDCASE','USL_OK', 'VIDPOM', 'NPR_MO', 'EXTR', 'PODR','LPU','PROFIL', 'DET','NHISTORY',
                        'DATE_1', 'DATE_2', 'DS1', 'DS2', 'RSLT', 'ISHOD', 'PRVS', 'IDSP','ED_COL', 'TARIF', 'SUMV')

    def __init__(self, accountId, accountItemIdList):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CDBFimport.__init__(self, self.log)
        CXMLimport.__init__(self)
        self.accountId=accountId
        self.accountItemIdList=accountItemIdList
        self.progressBar.setFormat('%p%')
        self.checkName()
        self.errorPrefix = ''
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0
        self.tblPayRefuseType = tbl('rbPayRefuseType')
        self.tableAccountItem = tbl('Account_Item')
        self.tableAccount = tbl('Account')
        self.tableAcc=self.db.join(self.tableAccountItem, self.tableAccount,
            'Account_Item.master_id=Account.id')
        self.prevContractId = None
        self.financeTypeOMS = forceRef(self.db.translate('rbFinance',
            'code', '2', 'id'))
        self.refuseTypeIdCache = {}
        self.insurerCache = {}
        self.policyKindIdCache = {}
        self.policyTypeTerritorial = forceRef(self.db.translate('rbPolicyType',
            'code', '1', 'id'))
        self.policyTypeIndustrial = forceRef(self.db.translate('rbPolicyType',
            'code', '2', 'id'))
        self.confirmation = ''


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы ELU, XML (*.elu *.xml)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)


    def err2log(self, e):
        self.log.append(self.errorPrefix+e)


    def checkHeader(self, txtStream):
        if txtStream.atEnd():
            return False

        header = forceString(txtStream.readLine())

        if len(header)<4:
            return False

        fields = header[4:].split(',')

        if len(fields)<5:
            return False

        if fields[3] == '1':
            txtStream.setCodec('CP866')
        elif fields[3] == '2':
            txtStream.setCodec('CP1251')

        if forceString(txtStream.readLine()) != '@@@':
            return False

        return True


    def readRecord(self, txtStream):
        result = {}
        s = ''

        while not txtStream.atEnd():
            s = forceString(txtStream.readLine())

            if s == '@@@':
                break

            list = s.split(':')

            if len(list)>1:
                result[list[0].strip()] = list[1].strip()

        return result


    def startImport(self):
        self.insurerCache = {}
        fileName = forceStringEx(self.edtFileName.text())
        self.confirmation = forceStringEx(self.edtConfirmation.text())
        (name,  fileExt) = os.path.splitext(fileName)
        isXML = (fileExt.lower() == '.xml')

        currentAccountOnly = self.chkOnlyCurrentAccount.isChecked()
        importPayed =self.chkImportPayed.isChecked()
        importRefused = self.chkImportRefused.isChecked()
        confirmation = self.edtConfirmation.text()
        if not confirmation:
            self.log.append(u'нет подтверждения')
            return

        self.prevContractId = None
        accountIdSet = set()

        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0

        fileName = unicode(self.edtFileName.text())
        txtFile = QFile(fileName)
        txtFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)

        self.labelNum.setText(u'размер источника: '+str(txtFile.size()))
        self.progressBar.setFormat('%p%')
        self.progressBar.setMaximum(txtFile.size()-1)

        if isXML:
            self.readFile(txtFile, accountIdSet)
        else:
            txtStream =  QTextStream(txtFile)
            if not self.checkHeader(txtStream):
                self.log.append(u'заголовок повреждён.')
                return

            while not txtStream.atEnd():
                row = self.readRecord(txtStream)
                QtGui.qApp.processEvents()
                if self.abort or row.get(u'КОН'):
                    break
                self.progressBar.setValue(txtStream.pos())
                self.stat.setText(
                    u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
                    (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))
                self.processRow(row, currentAccountOnly, importPayed, importRefused, confirmation, accountIdSet)

        self.stat.setText(
            u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
            (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))
        updateAccounts(list(accountIdSet))
        txtFile.close()


    def processRow(self,  row, currentAccountOnly, importPayed, importRefused, confirmation,  accountIdSet):
        lastName = nameCase(row.get(u'ФАМ', ''))
        firstName = nameCase(row.get(u'ИМЯ', ''))
        patrName = nameCase(row.get(u'ОТЧ', ''))
        refuseReasonCodeList =  forceString(row.get(u'ОШЛ', '')).split(',')
        refuseDate = QDate().currentDate() if refuseReasonCodeList != [u''] else None
        refuseComment = row.get(u'ЗАМ', '')
        accountItemId = forceInt(row.get(u'УКЛ'))/100
        recNum = accountItemId if accountItemId else 0
        payStatusMask = 0

        self.errorPrefix = u'Элемент №%d (%s %s %s): ' % (recNum, lastName,  firstName,  patrName)

        if not accountItemId:
            self.err2log(u'не найден в реестре.')
            self.nNotFound += 1
            return

        cond=[]
        cond.append(self.tableAccountItem['id'].eq(accountItemId))

        if currentAccountOnly:
            cond.append(self.tableAccount['id'].eq(toVariant(self.accountId)))

        fields = 'Account_Item.id, Account.date as Account_date, Account_Item.date as Account_Item_date, Account_Item.master_id as Account_id, Account.contract_id as contract_id'
        recordList = self.db.getRecordList(self.tableAcc, fields, where=cond)

        for record in recordList:
            accountIdSet.add(forceRef(record.value('Account_id')))
            contractId = forceRef(record.value('contract_id'))

            if self.prevContractId != contractId:
                self.prevContractId = contractId
                financeId = forceRef(self.db.translate('Contract', 'id', contractId, 'finance_id'))
                payStatusMask = getPayStatusMask(financeId)

            accDate = forceDate(record.value('Account_date'))
            accItemDate = forceDate(record.value('Account_Item_date'))

            if accItemDate or (refuseDate and (accDate > refuseDate)):
                self.err2log(u'счёт уже отказан')
                return

            self.nProcessed += 1

            accItem = self.db.getRecord(self.tableAccountItem, '*', accountItemId)
            accItem.setValue('date', toVariant(refuseDate if refuseDate else QDate.currentDate()))
            refuseTypeId = None

            if refuseDate:
                self.nRefused += 1
                refuseTypeId= self.getRefuseTypeId(refuseReasonCodeList[0])

                if not refuseTypeId:
                    refuseTypeId = self.addRefuseTypeId(refuseReasonCodeList[0], refuseComment)
                    self.refuseTypeIdCache[refuseReasonCodeList[0]] = refuseTypeId

                accItem.setValue('refuseType_id', toVariant(refuseTypeId))
                updateDocsPayStatus(accItem, payStatusMask, CPayStatus.refusedBits)
                self.err2log(u'отказан, код `%s`:`%s`' % (refuseReasonCodeList[0], refuseComment))
            else:
                self.err2log(u'подтверждён')
                self.nPayed += 1

            accItem.setValue('number', toVariant(confirmation))
            self.db.updateRecord(self.tableAccountItem, accItem)

        if recordList == []:
            self.nNotFound += 1
            self.err2log(u'счёт не найден')


    def addRefuseTypeId(self,  code,  name):
        record = self.tblPayRefuseType.newRecord()
        record.setValue('code', toVariant(code))
        record.setValue('name ', toVariant(name if name else u'неизвестная причина с кодом "%s"' % code))
        record.setValue('finance_id', toVariant(self.financeTypeOMS))
        record.setValue('rerun', toVariant(1))
        return self.db.insertRecord(self.tblPayRefuseType, record)


    def getRefuseTypeId(self, code):
        result = self.refuseTypeIdCache.get(code, -1)

        if result == -1:
            result =forceRef(self.db.translate(
                'rbPayRefuseType', 'code', code, 'id'))
            self.refuseTypeIdCache[code] = result

        return result

# *****************************************************************************************
#  XML
# *****************************************************************************************

    def readFile(self, device, accountIdSet):
        self.setDevice(device)
        self.accountIdSet = accountIdSet

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'ZL_LIST':
                    self.readList()
                else:
                    self.raiseError(u'Неверный формат данных.')

            if self.hasError():
                return False

        return True


    def readList(self):
        assert self.isStartElement() and self.name() == 'ZL_LIST'

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'ZGLV':
                    result = self.readGroup('ZGLV', self.zglvFields)
                elif self.name() == 'ZAP':
                    self.readZap()
                else:
                    self.readUnknownElement(True)

            if self.hasError():
                break


    def readZap(self):
        assert self.isStartElement() and self.name() == 'ZAP'
        result = {}

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'N_ZAP':
                    result['N_ZAP'] = forceString(self.readElementText())
                elif self.name() == 'PACIENT':
                    result = self.readGroup('PACIENT', self.pacientFields,  result, True)
                elif self.name() == 'SLUCH':
                    result = self.readGroup('SLUCH', self.sluchFields,  result, True)
                    if not self.hasError():
                        self.processXMLImport(result)
                else:
                    self.readUnknownElement(True)

            if self.hasError():
                break


    def processXMLImport(self, row):
        clientId = forceInt(row.get('ID_PAC', None))

        if not clientId:
            self.err2log(u'Поле ID_PAC не заполнено.')
            return

        self.errorPrefix = u'Элемент ID_PAC=%d: ' % clientId
        policyNumber = forceString(row.get('NPOLIS',  None))
        policySerial = forceString(row.get('SPOLIS', None))
        policyKindId = self.getPolicyKindId(forceString(row.get('VPOLIS', None)))
        dateStr = forceString(row.get('DATE_1'))
        policyBegDate = QDate.fromString(dateStr, Qt.ISODate) if dateStr else QDate.currentDate()

        if not policySerial and not policyNumber:
            self.err2log(u'Отсутствуют данные о полисе, ID_PAC=%d' % clientId)
            return

        insurerOGRN = forceString(row.get('SMO_OGRN'))
        insurerOKATO = forceString(row.get('SMO_OK'))

        insurerId = self.findInsurerByOGRNandOKATO(insurerOGRN, insurerOKATO)

        if insurerId:
            refuseDate = QDate.currentDate() if  self.updateClientPolicy(clientId, insurerId, policySerial,
                                                                         policyNumber, policyBegDate, insurerOGRN,
                                                                         policyKindId) \
                                                                else None
            refuseId = self.getRefuseTypeId('400')
        else:
            self.err2log(u'СМО с ОГРН `%s` и ОКАТО `%s`  не найдена' % insurerOGRN, insurerOKATO)
            refuseId = self.getRefuseTypeId('401')
            refuseDate = QDate.currentDate()

        accountItemIdList = self.getAccountItemIdListByClientId(clientId)
        self.processAccountItemIdList(accountItemIdList, refuseDate, refuseId)


    def getAccountItemIdListByClientId(self, clientId):
        s = 'AND Account_Item.master_id=%d'  % self.accountId  if self.chkOnlyCurrentAccount.isChecked() else ''

        stmt = """SELECT  Account_Item.id,
            Account.date as Account_date,
            Account_Item.date as Account_Item_date,
            Account_Item.master_id as Account_id,
            Account.contract_id as contract_id
        FROM Account_Item
        LEFT JOIN Event ON Event.id = Account_Item.event_id
        LEFT JOIN Account ON Account_Item.master_id = Account.id
        WHERE Event.client_id = %d %s""" % (clientId,  s)

        res = []
        query = self.db.query(stmt)
        while query.next():
            res.append(query.record())

        return res


    def findInsurerByOGRNandOKATO(self, OGRN, OKATO):
        u"""Поиск по ОГРН и ОКАТО"""

        key = (OGRN,  OKATO)
        result = self.insurerCache.get(key, -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrganisation, 'id',
                                      [self.tableOrganisation['OGRN'].eq(OGRN),
                                      self.tableOrganisation['OKATO'].eq(OKATO)])
            result = forceRef(record.value(0)) if record else self.OGRN2orgId(OGRN)
            self.insurerCache[key] = result

        return result


    def getPolicyKindId(self, code):
        result = self.policyKindIdCache.get(code, -1)

        if result == -1:
            result =forceRef(self.db.translate(
                'rbPolicyKind', 'regionalCode', code, 'id'))
            self.policyKindIdCache[code] = result

        return result


    def updateClientPolicy(self, clientId, insurerId, serial, number, begDate,  newInsurerOGRN, policyKindId):
        record = selectLatestRecord('ClientPolicy', clientId,
            '(Tmp.`policyType_id` IN (%d,%d))' % \
              (self.policyTypeIndustrial, self.policyTypeTerritorial))

        oldInsurerId = forceRef(record.value('insurer_id'))
        oldInsurerOGRN = forceString(self.db.translate('Organisation', 'id', oldInsurerId, 'OGRN'))

        if not record or (
                (insurerId and (forceRef(record.value('insurer_id')) != insurerId)
                    and (oldInsurerOGRN != newInsurerOGRN)) or
                (forceString(record.value('serial')) != serial) or
                (forceString(record.value('number')) != number)
            ):
            newInsurer = forceRef(record.value('insurer_id'))
            newSerial = forceString(record.value('serial'))
            newNumber = forceString(record.value('number'))
            self.addClientPolicy(clientId, insurerId, serial, number, begDate, forceRef(record.value('policyType_id')), policyKindId)
            if record:
                record.setValue('endDate', toVariant(begDate.addDays(-1)))
                self.db.updateRecord('ClientPolicy', record)
            self.err2log(u'обновлен полис: `%s№%s (%d)` на `%s№%s (%d)`' % (
                         newSerial if newSerial else '', newNumber if newNumber else '',
                         newInsurer if newInsurer else 0, serial, number, insurerId if insurerId else 0))
            return True

        return False


    def addClientPolicy(self, clientId, insurerId, serial, number, begDate, policyTypeId, policyKindId):
        table = self.db.table('ClientPolicy')
        record = table.newRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('insurer_id', toVariant(insurerId))

        if policyTypeId:
            record.setValue('policyType_id', toVariant(policyTypeId))

        if policyKindId:
            record.setValue('policyKind_id', toVariant(policyKindId))

        record.setValue('serial', toVariant(serial))
        record.setValue('number', toVariant(number))
        record.setValue('begDate', toVariant(begDate))
        self.db.insertRecord(table, record)


    def processAccountItemIdList(self, recordList, refuseDate, refuseTypeId):
        payStatusMask = 0

        for record in recordList:
            QtGui.qApp.processEvents()
            self.accountIdSet.add(forceRef(record.value('Account_id')))
            contractId = forceRef(record.value('contract_id'))

            if self.prevContractId != contractId:
                self.prevContractId = contractId
                financeId = forceRef(self.db.translate('Contract', 'id', contractId, 'finance_id'))
                payStatusMask = getPayStatusMask(financeId)

            accDate = forceDate(record.value('Account_date'))
            accItemDate = forceDate(record.value('Account_Item_date'))
            accountItemId = forceRef(record.value('id'))

            if accItemDate or (refuseDate and (accDate > refuseDate)):
                self.err2log(u'счёт уже отказан')
                return

            self.nProcessed += 1

            accItem = self.db.getRecord(self.tableAccountItem, '*', accountItemId)
            accItem.setValue('date', toVariant(refuseDate if refuseDate else QDate.currentDate()))

            if refuseDate:
                self.nRefused += 1
                accItem.setValue('refuseType_id', toVariant(refuseTypeId))
                updateDocsPayStatus(accItem, payStatusMask, CPayStatus.refusedBits)
                self.err2log(u'отказан, id=`%d`' % refuseTypeId)
            else:
                self.err2log(u'подтверждён')
                self.nPayed += 1

            accItem.setValue('number', toVariant(self.confirmation))
            self.db.updateRecord(self.tableAccountItem, accItem)

        if recordList == []:
            self.nNotFound += 1
            self.err2log(u'счёт не найден')


    def readGroup(self, name, fields, result=None, silent=False):
        if not result:
            result = {}
        r = CXMLimport.readGroup(self, name, fields, silent)

        for key, val in r.iteritems():
            result[key] = val

        return result
