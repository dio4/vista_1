#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Events.Utils import CPayStatus, getPayStatusMask
from Accounting.Utils import updateAccounts, updateDocsPayStatus

from Utils import *
from Ui_ImportPayRefuseR53 import Ui_Dialog
from Import131XML import CXMLimport


def ImportPayRefuseR53Native(widget, accountId, accountItemIdList):
    dlg = CImportPayRefuseR53Native(accountId, accountItemIdList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR53FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR53FileName'] = toVariant(dlg.edtFileName.text())


class CImportPayRefuseR53Native(QtGui.QDialog, Ui_Dialog, CXMLimport):
    version = '1,02'
    version201112 = '1.0'
    headerFields = ('Version', 'Sender', 'C_OGRN', 'Addressee',
                            'M_OGRN', 'Theme', 'Accounting_period', 'NUM_S', 'DATE_S')
    accountItemFields = ('N_PP', 'DEP_ID', 'VID_P', 'SN_POL', 'FAM', 'IM', 'OT',
                                    'DR', 'W', 'PR_PR', 'DRP', 'WP', 'Q_G', 'Q_V',
                                    'Q_U', 'V_ED', 'V_V', 'DS', 'DS_S', 'PRMP', 'C_LC',
                                    'NUM_CAR', 'DATE_1', 'DATE_2', 'IDRB', 'MED_ST',
                                    'PRVS', 'RSLT', 'IDSP', 'TARIF', 'S_ALL', 'S_OPL',
                                    'I_TYPE', 'C_OGRN', 'C_OKATO', 'SS', 'C_P', 'SN_DOC',
                                    'DATE_DOC', 'NAME_VP', 'ADS_B', 'C_SHIP', 'ATTACH_SIGN', 'Q_R',
                                    'NUM_CARD', 'RES_CTRL')

    importNormal = 0
    import201112 = 1

    zglvFields = ('VERSION', 'DATA', 'C_OKATO1', 'FILENAME')
    schetFields = ('CODE', 'CODE_MO', 'YEAR', 'MONTH', 'NSCHET', 'DSCHET', 'SUMMAV',
                            'COMENTS', 'SUMMAP', 'SANK_MEK', 'SANK_MEE', 'SANK_EKMP', 'PLAT', )
    pacientFields = ('ID_PAC', 'SMO', 'OKATO_OMS', 'VPOLIS', 'SPOLIS', 'NPOLIS', 'FAM', 'IM',
                            'OT', 'W', 'DR', 'FAM_P', 'IM_P', 'OT_P', 'W_P', 'DR_P', 'MR',
                            'DOCTYPE', 'DOCSER', 'DOCNUM', 'SNILS', 'OKATOG', 'OKATOP', 'NOVOR',
                            'COMENTP')
    sluchFields = ('PODR', 'IDDOKT', 'IDCASE', 'USL_OK', 'VIDPOM', 'EXTR', 'LPU', 'PROFIL', 'DET', 'NHISTORY',
                            'DATE_1', 'DATE_2', 'DS0', 'DS1', 'DS2', 'CODE_MES1', 'CODE_MES2', 'RSLT',
                            'ISHOD', 'PRVS', 'IDSP', 'ED_COL', 'TARIF', 'SUMV', 'PROFIL_FOMS', 'PRVS_FOMS',
                            'PREPARE_ACC', 'PREPARE_DATE', 'PREPARE_NUM', 'OPLATA', 'SUMP', 'REFREASON',
                            'REFREASON_FOMS', 'SANK_MEK', 'SANK_MEE', 'SANK_EKMP', 'USL', 'COMENTSL')
    uslFields = ('IDSERV', 'LPU', 'PROFIL', 'DET', 'DATE_IN', 'DATE_OUT', 'DS', 'USL', 'KOL_USL',
                        'TARIF', 'SUMV_USL', 'PRVS', 'COMENTU')

    sexMap = {u'М':1,  u'Ж':2}

    def __init__(self, accountId, accountItemIdList):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CXMLimport.__init__(self, self.log)
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
        self.tableClient = tbl('Client')
        self.tableAcc=self.db.join(self.tableAccountItem, self.tableAccount,
            'Account_Item.master_id=Account.id')
        self.prevContractId = None
        self.financeTypeOMS = forceRef(self.db.translate('rbFinance',
            'code', '2', 'id'))
        self.policyTypeTerritorial = forceRef(self.db.translate('rbPolicyType',
            'code', '1', 'id'))
        self.policyTypeIndustrial = forceRef(self.db.translate('rbPolicyType',
            'code', '2', 'id'))
        self.currentAccountOnly = False
        self.confirmation = ''
        self.serviceCache = {}
        self.accountItemIdListCache = {}
        self.clientCache = {}
        self.clientByAccountItemIdCache = {}
        self.accountIdSet = set()
        self.refuseTypeIdCache = {}
        self.insurerArea = QtGui.qApp.defaultKLADR()[:2]
        self.insurerCache = {}
        self.policyKindIdCache = {}


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML, DBF (*.xml *.dbf)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)


    def err2log(self, e):
        self.log.append(self.errorPrefix+e)


    def startImport(self):
        self.progressBar.setFormat('%p%')
        n=0
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0

        fileName = forceStringEx(self.edtFileName.text())
        (name,  fileExt) = os.path.splitext(fileName)
        isDBF = (fileExt.lower() == '.dbf')
        self.currentAccountOnly = self.chkOnlyCurrentAccount.isChecked()
        self.confirmation = self.edtConfirmation.text()
        self.accountIdSet = set()

        if not self.confirmation:
            self.log.append(u'нет подтверждения')
            return

        if isDBF:
            inFile = dbf.Dbf(fileName, readOnly=True, encoding='cp866')
        else:
            inFile = QtCore.QFile(fileName)

            if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'Не могу открыть файл для чтения %s:\n%s.' \
                                      % (fileName, inFile.errorString()))
                return

        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.progressBar.setFormat(u'%v записей' if isDBF else u'%v байт')
        self.stat.setText("")
        size = max(len(inFile) if isDBF else inFile.size(), 1)
        self.progressBar.setMaximum(size)
        self.labelNum.setText(u'размер источника: '+str(size))
        self.btnImport.setEnabled(False)
        proc = self.readDbf if isDBF else self.readFile
        if (not proc(inFile)):
            if self.abort:
                self.err2log(u'! Прервано пользователем.')
            else:
                self.err2log(u'! Ошибка: файл %s, %s' % (fileName,
                                            self.errorString()))

        if isDBF:
            inFile.close()

        self.stat.setText(
            u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
            (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))
        updateAccounts(list(self.accountIdSet))


    def readDbf(self, dbf):
        for row in dbf:
            self.processRow(row.asDict(), True)
            QtGui.qApp.processEvents()
            self.progressBar.step()

            if self.abort:
                return False

        return True


    def readFile(self, device):
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'root':
                    self.readData()
                elif self.name() == 'ZL_LIST':
                    self.readList() # Новый формат
                else:
                    self.raiseError(u'Неверный формат экспорта данных.')
            print self.name()
            if self.hasError():
                return False

        return True


    def readData(self):
        assert self.isStartElement() and self.name() == 'root'

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'heading':
                    result = self.readGroup('heading', self.headerFields)
                    if not self.hasError():
                        self.processHeader(result, self.import201112)
                elif self.name() == 'Rendering_assistance':
                    result = self.readGroup('Rendering_assistance', self.accountItemFields)
                    if not self.hasError():
                        self.processRow(result)
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readList(self):
        assert self.isStartElement() and self.name() == 'ZL_LIST'

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'ZGLV':
                    result = self.readGroup('ZGLV', self.zglvFields)
                    if not self.hasError():
                        self.processHeader(result, self.import201112)
                elif self.name() == 'SCHET':
                    result = self.readGroup('SCHET', self.schetFields)
#                    if not self.hasError():
#                        self.processRow(result, self.import201112)
                elif self.name() == 'ZAP':
                    self.readZap()
                else:
                    self.readUnknownElement()

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
                elif self.name() == 'PR_NOV':
                    result['PR_NOV'] = forceString(self.readElementText())
                elif self.name() == 'PACIENT':
                    result = self.readGroup('PACIENT', self.pacientFields,  result)
                elif self.name() == 'SLUCH':
                    result = self.readGroup('SLUCH', self.sluchFields,  result)
                    if not self.hasError():
                        self.processRowImport201112(result)
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readGroup(self, name, fields, result=None):
        if not result:
            result = {}
        r = CXMLimport.readGroup(self, name, fields)

        for key, val in r.iteritems():
            result[key] = val

        return result


    def processHeader(self, row, importType):
        if importType == self.importNormal:
            ver = row.get('Version', '')

            if ver != self.version:
                self.err2log(u'Формат версии `%s` не поддерживается.'
                                    u' Должен быть `%s`.' % (ver, self.version))
        elif importType == self.import201112:
            ver = row.get('VERSION', '')

            if ver != self.version201112:
                self.err2log(u'Формат версии `%s` не поддерживается.'
                                    u' Должен быть `%s`.' % (ver, self.version201112))


    def findInsurerByOGRN(self, OGRN):
        u"""Поиск по ОГРН с учётом области страхования"""

        result = self.insurerCache.get(OGRN, -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrganisation, 'id',
                                      [self.tableOrganisation['OGRN'].eq(OGRN),
                                      self.tableOrganisation['area'].like(self.insurerArea+'...')])
            result = forceRef(record.value(0)) if record else self.OGRN2orgId(OGRN)
            self.insurerCache[OGRN] = result

        return result


    def findInsurerByOGRNandOKATO(self, OGRN, OKATO):
        u"""Поиск по ОГРН и ОКАТО с учётом области страхования"""

        key = (OGRN,  OKATO)
        result = self.insurerCache.get(key, -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrganisation, 'id',
                                      [self.tableOrganisation['OGRN'].eq(OGRN),
                                      self.tableOrganisation['OKATO'].eq(OKATO),
                                      self.tableOrganisation['area'].like(self.insurerArea+'...')])
            result = forceRef(record.value(0)) if record else self.findInsurerByOGRN(OGRN)
            self.insurerCache[key] = result

        return result


    def processRow(self,  row,  isDBF=False,  importType = import201112):
        lastName = nameCase(row.get('FAM', ''))
        firstName = nameCase(row.get('IM', ''))
        patrName = nameCase(row.get('OT', ''))
        sex = self.sexMap.get(row.get('W'), 0) if isDBF else forceInt(row.get('W'))
        if isDBF:
            birthDate = QDate(row.get('DR')) if row.has_key('DR') else QDate()
        else:
            birthDate = QDate().fromString(row['DR'], Qt.ISODate) if row.has_key('DR') else QDate()
        policySN = row.get('SN_POL')
        policyKindId = self.getPolicyKindId(row.get('VID_P'))

        if isDBF:
            sum = row.get('S_ALL', 0.0)
            accNum = row.get('NUM_S', '')
            accDate = QDate(row.get('DATE_S')) if row.has_key('DATE_S') else QDate()
            accountItemId = self.findAccountItemId(lastName, firstName,
                patrName, sum, accNum, accDate)
        else:
            accountItemId = forceInt(row.get('NUM_CARD'))

        refuseReasonCodeList =  forceString(row.get('I_TYPE', '')).split(' ')
        refuseDate = QDate().currentDate() if refuseReasonCodeList != [u''] else None
        refuseComment = row.get('COMMENT' if isDBF else 'RES_CTRL', '')
        accountItemIdList = self.getAccountItemIdList(accountItemId)
        recNum = forceInt(row.get('N_PP', 0))

        self.errorPrefix = u'Элемент №%d (%s %s %s): ' % (recNum, lastName,  firstName,  patrName)

        if accountItemIdList == []:
            self.err2log(u'не найден в реестре.')
            self.nNotFound += 1
            return

        cond=[]
        cond.append(self.tableAccountItem['id'].inlist(accountItemIdList))

        if self.currentAccountOnly:
            cond.append(self.tableAccount['id'].eq(toVariant(self.accountId)))

        fields = 'Account_Item.id, Account.date as Account_date, Account_Item.date as Account_Item_date, Account_Item.master_id as Account_id, Account.contract_id as contract_id'
        recordList = self.db.getRecordList(self.tableAcc, fields, where=cond)

        if (not isDBF) and policySN and recordList != []:
            clientId = self.getClientId(accountItemId)

            if not clientId:
                clientId = self.findClientByNameSexAndBirthDate(lastName, firstName,
                    patrName, sex, birthDate)

            if clientId:
                self.checkClientPolicy(clientId, policySN, row.get('C_OGRN'), row.get('C_OKATO'), policyKindId)
            else:
                self.err2log(u'пациент не найден в БД')

        self.processAccountItemIdList(recordList, refuseDate, refuseReasonCodeList, refuseComment)


    def processAccountItemIdList(self, recordList, refuseDate, refuseReasonCodeList, refuseComment = ''):
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

            if accItemDate or (refuseDate and (accDate > refuseDate)):
                self.err2log(u'счёт уже отказан')
                return

            self.nProcessed += 1

            accountItemId = forceRef(record.value('Account_Item.id'))
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

            accItem.setValue('number', toVariant(self.confirmation))
            self.db.updateRecord(self.tableAccountItem, accItem)

        if recordList == []:
            self.nNotFound += 1
            self.err2log(u'счёт не найден')


    def processRowImport201112(self, row):
        eventId = forceRef(row.get('NHISTORY', None))
        federalServiceCode = forceString(row.get('PROFIL', ''))
        serviceId = forceRef(self.db.translate('rbService', 'infis', federalServiceCode, 'code'))
        refuseCode = forceString(row.get('REFREASON_FOMS', ''))
        refuseDate = QDate.currentDate() if refuseCode else None
        refuseCodeList = []

        if refuseCode:
            refuseCodeList.append(refuseCode)

        if eventId and federalServiceCode:
            accountItemIdList = self.getAccountItemIdListByEventAndService(eventId, serviceId)
            self.processAccountItemIdList(accountItemIdList, refuseDate, refuseCodeList)
        else:
            self.err2log(u'Для записи `%d` не заполнено поле NHISTORY либо PROFIL' % forceInt(row.get('N_ZAP', 0)))


    def getAccountItemIdListByEventAndService(self, eventId, serviceId):
        return self.db.getRecordList(self.tableAccountItem, where  = [
                    self.tableAccountItem['service_id'].eq(serviceId),
                    self.tableAccountItem['event_id'].eq(eventId),
                ])


    def findAccountItemId(self, lastName, firstName, patrName, sum, accNum, accDate):
        stmt = """SELECT Account_Item.id
            FROM Account_Item
            LEFT JOIN Account ON Account.id = Account_Item.master_id
            LEFT JOIN Event ON Account_Item.event_id = Event.id
            LEFT JOIN Client ON Event.client_id = Client.id
            WHERE %s
            LIMIT 1
        """ % self.db.joinAnd([
                    self.tableAccountItem['sum'].eq(sum),
#                    self.tableAccount['number'].eq(accNum),
#                    self.tableAccount['settleDate'].eq(accDate),
                    self.tableClient['lastName'].eq(lastName),
                    self.tableClient['firstName'].eq(firstName),
                    self.tableClient['patrName'].eq(patrName),
                ])
        query = self.db.query(stmt)

        if query and query.first():
            record = query.record()

            if record:
                return forceRef(record.value(0))

        return None


    def addRefuseTypeId(self, code, name):
        s = name if name else u'неизвестная причина с кодом "%s"' % code
        record = self.tblPayRefuseType.newRecord()
        record.setValue('code', toVariant(code))
        record.setValue('name ', toVariant(s))
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


    def getPolicyKindId(self, code):
        result = self.policyKindIdCache.get(code, -1)

        if result == -1:
            result =forceRef(self.db.translate(
                'rbPolicyKind', 'regionalCode', code, 'id'))
            self.policyKindIdCache[code] = result

        return result


    def getAccountItemIdList(self, accountItemId):
        result =  self.accountItemIdListCache.get(accountItemId)

        if not result and accountItemId:
            result=[accountItemId, ]
            serviceId = self.getServiceId(accountItemId)

            if serviceId:
                stmt = """SELECT Account_Item.id,
                    IF(Account_Item.service_id IS NOT NULL,
                        Account_Item.service_id,
                        IF(Account_Item.visit_id IS NOT NULL,
                            Visit.service_id,
                            EventType.service_id)
                        ) AS serviceId
                    FROM Account_Item
                    LEFT JOIN Visit ON Visit.id  = Account_Item.visit_id
                    LEFT JOIN Event ON Event.id  = Account_Item.event_id
                    LEFT JOIN EventType ON EventType.id = Event.eventType_id
                    WHERE (Account_Item.service_id=%d
                        OR Visit.service_id=%d
                        OR EventType.service_id=%d)
                      AND Account_Item.event_id = (
                        SELECT AI.event_id
                        FROM Account_Item AS AI
                        WHERE AI.id=%d
                    )""" % (serviceId, serviceId, serviceId, accountItemId)

                query = self.db.query(stmt)

                if query:
                    while query.next():
                        record = query.record()

                        if not record:
                            break

                        result.append(forceRef(record.value(0)))

        return result


    def getServiceId(self, accountItemId):
        result = self.serviceCache.get(accountItemId, -1)

        if result == -1:
            result = None

            stmt = """SELECT
            IF(Account_Item.service_id IS NOT NULL,
                Account_Item.service_id,
                IF(Account_Item.visit_id IS NOT NULL,
                    Visit.service_id,
                    EventType.service_id)
                ) AS serviceId
            FROM Account_Item
            LEFT JOIN Visit ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            WHERE %s""" % self.tableAccountItem['id'].eq(accountItemId)
            query = self.db.query(stmt)

            if query.first():
                record = query.record()

                if record:
                    result = forceRef(record.value(0))

            self.serviceCache[accountItemId] = result

        return result


    def findClientByNameSexAndBirthDate(self, lastName, firstName, patrName, sex, birthDate):
        key = (lastName, firstName, patrName, sex, birthDate)
        result = self.clientCache.get(key, -1)

        if result == -1:
            result = None
            table = self.db.table('Client')
            filter = [table['deleted'].eq(0),
                        table['lastName'].eq(lastName),
                        table['firstName'].eq(firstName),
                        table['patrName'].eq(patrName),
                        table['birthDate'].eq(birthDate)]

            if sex != 0:
                filter.append(table['sex'].eq(sex))

            record = self.db.getRecordEx(table, 'id',  filter, 'id')

            if record:
                result = forceRef(record.value(0))

            self.clientCache[key] = result

        return result


    def getClientId(self,  accountItemId):
        result = self.clientByAccountItemIdCache.get(accountItemId, -1)

        if result == -1:
            result = None
            stmt = """SELECT Event.client_id
            FROM Account_Item
            LEFT JOIN Event ON Event.id = Account_Item.event_id
            WHERE %s""" % self.tableAccountItem['id'].eq(accountItemId)

            query = self.db.query(stmt)

            if query and query.first():
                record = query.record()

                if record:
                    result = forceRef(record.value(0))

            self.clientByAccountItemIdCache[accountItemId] = result

        return result


    def addClientPolicy(self, clientId, insurerId, serial, number, policyTypeId, policyKindId):
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
        self.db.insertRecord(table, record)


    def updateClientPolicy(self, clientId, insurerId, serial, number, newInsurerOGRN, policyKindId):
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
            self.addClientPolicy(clientId, insurerId, serial, number,  forceRef(record.value('policyType_id')), policyKindId)
            self.err2log(u'обновлен полис: `%s№%s (%d)` на `%s№%s (%d)`' % (
                         newSerial if newSerial else '', newNumber if newNumber else '',
                         newInsurer if newInsurer else 0, serial, number, insurerId if insurerId else 0))


    def checkClientPolicy(self, clientId, policySN, OGRN, OKATO, policyKindId):
        policy = policySN.split(u'№')
        insurerId = self.findInsurerByOGRNandOKATO(OGRN, OKATO) if OGRN else None

        if policy == []:
            return

        policySerial = ''
        policyNumber = policy[0].strip()

        if len(policy)>1:
            policySerial = policy[0].strip()
            policyNumber = policy[1].strip()

        self.updateClientPolicy(clientId, insurerId, policySerial, policyNumber, OGRN, policyKindId)
