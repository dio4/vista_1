# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


import os.path
import shutil

from library.dbfpy.dbf import *
from library.Utils     import *
from Orgs.Utils import getOrganisationInfo

from Ui_ExportR77NativePage1 import Ui_ExportPage1
from Ui_ExportR77NativePage2 import Ui_ExportPage2


def getAccountInfo(accountId):
    accountRecord = None
    db = QtGui.qApp.db
    stmt = """SELECT
            Account.settleDate AS date,
            Account.number,
            Contract.number AS contractNum,
            Contract.date AS contractDate,
            rbFinance.code AS financeCode,
            Organisation.infisCode AS orgCode,
            Organisation.shortName AS orgName,
            Organisation.Address AS orgAddr,
            Organisation.chief AS orgChief
        FROM Account
        LEFT JOIN Contract ON Account.contract_id = Contract.id
        LEFT JOIN rbFinance ON Contract.finance_id = rbFinance.id
        LEFT JOIN Organisation ON Contract.payer_id = Organisation.id
        WHERE Account.id = %d
    """ % accountId
    query = db.query(stmt)

    if query:
        query.first()
        accountRecord = query.record()

    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        number = forceString(accountRecord.value('number'))
        orgCode = forceString(accountRecord.value('orgCode'))
        orgName = forceString(accountRecord.value('orgName'))
        financeCode = forceString(accountRecord.value('financeCode'))
        contractNum = forceString(accountRecord.value('contractNum'))
        contractDate = forceDate(accountRecord.value('contractDate'))
        orgAddr = forceString(accountRecord.value('orgAddr'))
    else:
        date = None
        number = ''
        orgCode = ''
        orgName = ''
        financeCode = None
        contractDate = None
        contractNum = ''
        orgAddr = ''

    fileName = orgCode
    dirName = u'%s_%s' % (orgCode,  orgName)

    for ch in u'?#\"\':\\\/!$%@~(){}^&+=[]|':
        dirName = dirName.replace(ch,  u'')
        fileName = fileName.replace(ch,  u'')

    return date, number, fileName,  dirName,  financeCode,  contractNum, \
        contractDate,  orgName,  orgAddr


def splitStrByLen(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]


def exportR77Native(widget, accountId, accountItemIdList):
    wizard = CExportR77NativeWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportR77NativeWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта для Москвы')
        self.dbfFileName = ''
        self.dbfDirName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date,  number, fileName,  dirName, financeCode, contractNum, \
            contractDate, orgName, orgAddr = getAccountInfo(accountId)
        self.dbfFileName = fileName
        self.dbfDirName = dirName
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла "%s.dbf"' %(self.dbfFileName))
        self.page1.accNumber = number
        self.page1.financeCode = financeCode
        self.page1.contractNum = contractNum
        self.page1.contractDate = contractDate
        self.page1.payerAddr = orgAddr
        self.page1.payerName = orgName
        self.page1.accDate =date


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('native')
        return self.tmpDir


    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), 'basusl' + self.dbfFileName + '.dbf')

    def getFullTxtFileName(self):
        return os.path.join(self.getTmpDir(), 'sf'+ self.dbfFileName + '.txt')

    def getFullTxt2FileName(self):
        return os.path.join(self.getTmpDir(), 'pac'+ self.dbfFileName + '.txt')

    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()
        QtGui.qApp.preferences.appPrefs['ExportR77GroupByMKB'] = toVariant(
                self.page1.chkGroupByMKB.isChecked())


class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.accSystemId = None
        self.financeCode = None
        self.currentClientId = None
        self.currentClientMKB = None
        self.clientOldRecord = ''
        self.clientSum = 0
        self.clientMKBSum = 0
        self.clientAmount = 0
        self.pageNum = 0
        self.contractNum = ''
        self.contractDate = None
        self.payerAddr = ''
        self.payerName = ''
        self.accDate = None
        self.totalSum = 0
        self.clientCount = 0
        self.appendixStr = QString(u'')
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.chkGroupByMKB.setChecked(
            forceBool(getVal(QtGui.qApp.preferences.appPrefs,
            'ExportR77GroupByMKB', True)))


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.chkGroupByMKB.setEnabled(not flag)


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        txt,  txtStream, appendixStream, txt2, txt2Stream = self.createTxt()
        self.accSystemId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', \
                'code', '77',  'id'))
        query = self.createQuery()
        serviceQuery = self.createServiceQuery()
        self.progressBar.setMaximum(max(query.size()+serviceQuery.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.pageNum = 0
        self.currentClientId = None
        self.currentClientMKB = None
        return dbf, txt, txtStream, appendixStream,  query, txt2, txt2Stream,  serviceQuery


    def export(self):
        QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def exportInt(self):
        dbf, txt, txtStream, appendixStream,  query, txt2, txt2Stream, serviceQuery = self.prepareToExport()
        if self.idList:
            self.writeTextHeader(txtStream,  appendixStream, txt2Stream)
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, txtStream, appendixStream, query.record())

            if self.currentClientId:
                self.writeClientFooter(txtStream,  appendixStream)

            self.writeText2Header(txt2Stream)
            while serviceQuery.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.processServices(txt2Stream, serviceQuery.record())

            self.writeTextFooter(txtStream,  txt2Stream)
        else:
            self.progressBar.step()

        dbf.close()
        txt.close()
        txt2.close()


    def createDbf(self):
        dbf = Dbf(self.wizard().getFullDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
            ('SPOLIS', 'C', 0x11),    # Серия полиса
            ('NPOLIS', 'N',  0x0A),       # Номер полиса
            ('FAM', 'C', 0x14),         # Фамилия
            ('IMJA', 'C', 0x0A),  #  Имя
            ('OTSCH', 'C', 0x0F),  # Отчество
            ('KHYS', 'N', 3),  #  Врач
            ('DATTAL', 'D' ),  # Дата оказания услуги
            ('KDDIAG', 'C', 5),  # Диагноз
            ('SCODE', 'N', 6),  # Код услуги
            ('KOLVO', 'N', 7),  # Количество услуг
            ('PRICE', 'N', 0x0A,  2),  # Стоимость одной услуги
            ('SUMMA', 'N', 0x0C,  2),  # Сумма
            ('NN', 'N', 6),  # Номер истории болезни пациента (московский идентификатор)
            )
        return dbf


    def createTxt(self):
        txt = QFile(self.wizard().getFullTxtFileName())
        txt.open(QIODevice.WriteOnly | QIODevice.Text)
        txtStream =  QTextStream(txt)
        txtStream.setCodec('CP866')
        self.appendixStr = QString(u"")
        appendixStream =  QTextStream(self.appendixStr)
        appendixStream.setCodec('CP866')
        txt2 = QFile(self.wizard().getFullTxt2FileName())
        txt2.open(QIODevice.WriteOnly | QIODevice.Text)
        txt2Stream =  QTextStream(txt2)
        txt2Stream.setCodec('CP866')
        return txt,  txtStream, appendixStream, txt2, txt2Stream

# *****************************************************************************************

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        if self.financeCode == '3': #ДМС
            policyType_id = forceRef(db.translate('rbPolicyType', \
                'code', '3',  'id'))
            policyFilter = 'CP.policyType_id = %d' % policyType_id
        else:
            policyFilter = '1'

        accSysFilter = 'ClientIdentification.accountingSystem_id = %d' % \
            self.accSystemId if self.accSystemId else '1'

        stmt = """
            SELECT
                Client.id               AS clientId,
                ClientPolicy.serial    AS policySerial,
                ClientPolicy.number   AS policyNumber,
                Client.lastName        AS lastName,
                Client.firstName       AS firstName,
                Client.patrName       AS patrName,
                Person.regionalCode AS personRegionalCode,
                vrbPerson.name  AS personName,
                Event.execDate         AS execDate,
                IF(Action.MKB != '', Action.MKB, Diagnosis.MKB) AS MKB,
                IF(Action.MKB != '', ActionMKB.DiagName, MKB_Tree.DiagName) AS diagName,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.infis,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                  ) AS serviceCode,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.name,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.name, rbEventService.name)
                  ) AS serviceName,
                Account_Item.price    AS price,
                Account_Item.amount    AS amount,
                Account_Item.`sum`     AS `sum`,
                ClientIdentification.identifier AS identifier,
                IF(work.title IS NOT NULL,
                    work.title, ClientWork.freeInput) AS `workName`
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND
                      ClientPolicy.id = (SELECT MAX(CP.id)
                                         FROM   ClientPolicy AS CP
                                         WHERE  CP.client_id = Client.id AND %s)
            LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
            LEFT JOIN Person       ON Person.id = Event.execPerson_id
            LEFT JOIN vrbPerson ON vrbPerson.id = Event.execPerson_id
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN MKB_Tree       ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN MKB_Tree AS ActionMKB ON ActionMKB.DiagID = Action.MKB
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN ClientIdentification ON Client.id = ClientIdentification.client_id AND
                    ClientIdentification.deleted = 0 AND %s
            LEFT JOIN ClientWork ON ClientWork.client_id=Client.id AND
                        ClientWork.id = (SELECT max(CW.id)
                                         FROM ClientWork AS CW
                                         WHERE CW.client_id=Client.id AND CW.deleted = 0)
            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id AND work.deleted = 0
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            ORDER BY Client.id, Diagnosis.MKB, execDate, serviceCode
        """ % (policyFilter, accSysFilter, tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)
        return query


    def createServiceQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """
            SELECT
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.infis,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.infis, rbEventService.infis)
                  ) AS serviceCode,
                IF(Account_Item.service_id IS NOT NULL,
                   rbItemService.name,
                   IF(Account_Item.visit_id IS NOT NULL, rbVisitService.name, rbEventService.name)
                  ) AS serviceName,
                Account_Item.price       AS price,
                SUM(Account_Item.amount) AS amount,
                SUM(Account_Item.`sum`)  AS `sum`
            FROM Account_Item
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN Diagnostic ON Diagnostic.id = (
              SELECT MAX(D.id)
              FROM Diagnostic AS D
              WHERE D.event_id = Account_Item.event_id
                AND ((D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code ='2')
                        AND D.person_id = Event.execPerson_id) OR (
                          D.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code='1')))
                          AND D.deleted = 0)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
            LEFT JOIN MKB_Tree       ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            GROUP BY serviceCode
            ORDER BY serviceCode
        """ % tableAccountItem['id'].inlist(self.idList)
        query = db.query(stmt)
        return query


    def process(self, dbf, txt, appendixStream, record):
        dbfRecord = dbf.newRecord()

        clientId = forceRef(record.value('clientId'))
        MKB = forceString(record.value('MKB'))

        if clientId != self.currentClientId:
            if self.currentClientId:
                self.writeClientFooter(txt, appendixStream)

            self.writeClientHeader(txt,  record)
            self.currentClientId = clientId
            self.currentClientMKB = MKB
            self.writeMKBHeader(txt,  record)

        if self.chkGroupByMKB.isChecked() and MKB != self.currentClientMKB:
            self.writeMKBFooter(txt,  record)
            self.writeMKBHeader(txt,  record)
            self.currentClientMKB = MKB

        self.writeClientStr(txt, appendixStream, record)
        dbfRecord['SPOLIS'] = forceString(record.value('policySerial'))    # Серия полиса
        dbfRecord['NPOLIS'] = forceInt(record.value('policyNumber')) % 10**10  # Номер полиса
        dbfRecord['FAM'] = forceString(record.value('lastName')) # Фамилия
        dbfRecord['IMJA'] = forceString(record.value('firstName'))  #  Имя
        dbfRecord['OTSCH'] = forceString(record.value('patrName'))  # Отчество
        dbfRecord['KHYS'] = forceInt(record.value('personRegionalCode')) % 10**3 #  Врач
        dbfRecord['DATTAL'] = pyDate(forceDate(record.value('execDate')))  # Дата оказания услуги
        dbfRecord['KDDIAG'] = MKB  # Диагноз
        dbfRecord['SCODE'] = forceInt(record.value('serviceCode')) % 10**6 # Код услуги
        dbfRecord['KOLVO'] = forceInt(record.value('amount')) # Количество услуг
        dbfRecord['PRICE'] = forceDouble(record.value('price')) # Стоимость одной услуги
        dbfRecord['SUMMA'] = forceDouble(record.value('sum')) # Сумма
        # Номер истории болезни пациента (московский идентификатор)
        dbfRecord['NN'] = forceInt(record.value('identifier')) % 10**6
        dbfRecord.store()


    def processServices(self,  txtStream,  record):
        format = u'%6.6s│%40.40s│%4.4s │%10.10s│%12.12s\n'
        serviceName = splitStrByLen(forceString(record.value('serviceName')), 40)

        for i in range(len(serviceName)):
            txtStream << format % (
                forceString(record.value('serviceCode')) if i == 0 else '',
                serviceName[i].ljust(40),
                    (u'%3d' % forceInt(record.value('amount'))) if i == 0 else '',
                    (u'%10.2f' % forceDouble(record.value('price'))) if i == 0 else '',
                    (u'%12.2f' % forceDouble(record.value('sum'))) if i == 0 else ''
                )

    def writeTextHeader(self,  txtStream, appendixStream,  txt2Stream):
        self.totalSum = 0
        self.clientCount = 0
        orgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        contractNum = self.contractNum if self.contractNum != '' else u'б/н'
        contractDate = self.contractDate.toString('dd.MM.yy') if self.contractDate else u'б\д'
        header = (u'%s'% orgInfo.get('title')).center(76)+ '\n\n'
        header += (u'Перечень медицинских услуг к договору N %s от %s' % (contractNum, \
                            contractDate)).center(76)+ '\n'
        header += self.payerName.center(76)+ '\n'
        header += self.payerAddr.center(76)+ '\n'
        dateStr = forceString(self.accDate.toString('MM.yy'))
        header += (u'с 01.%s по %2d.%s' % (dateStr,
                            self.accDate.day(),  dateStr)).center(76) + '\n\n'

        txtStream << header

        header = (u'%s'% orgInfo.get('title')).center(76)+ '\n\n'
        header += (u'Приложение N 1 к договору N %s от %s' % (contractNum, \
                            contractDate)).center(76)+ '\n'
        header += self.payerName.center(76)+ '\n'
        header += self.payerAddr.center(76)+ '\n'
        dateStr = forceString(self.accDate.toString('MM.yy'))
        header += (u'с 01.%s по %2d.%s' % (dateStr,
                            self.accDate.day(),  dateStr)).center(76) + '\n\n'

        appendixStream << header
        appendixStream << u"""____________________________________________________________________________
 N и/б │      Пациент       │  Полис N   │Место работы│Кол│Сумма за лечение │
____________________________________________________________________________
"""


    def writeText2Header(self,  txt2Stream):
        orgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        contractNum = self.contractNum if self.contractNum != '' else u'б/н'
        contractDate = self.contractDate.toString('dd.MM.yy') if self.contractDate else u'б\д'
        dateStr = forceString(self.accDate.toString('MM.yy'))
        header = (u'%s'% orgInfo.get('title')).center(76)+ '\n\n'
        header += (u'Счет-фактура').center(76)+ '\n'
        header += (u'к договору N %s от %s' % (contractNum, \
                            contractDate)).center(76)+ '\n'
        header += self.payerName.center(76)+ '\n'
        dateStr = forceString(self.accDate.toString('MM.yy'))
        header += (u'с 01.%s по %2d.%s' % (dateStr,
                            self.accDate.day(),  dateStr)).center(76) + '\n\n'

        header += (u'Количество обратившихся - %5d' % self.clientCount).center(76)+'\n'
        txt2Stream << header
        txt2Stream << u"""_____________________________________________________________________________
 Код  │     Вид выполненных  работ             │ Кол │Договорная│    Сумма
      │                                        │  -  │   цена   │  к оплате
      │                                        │ во  │вып. работ│
      │                                        │     │за единицу│
──────┼────────────────────────────────────────┼─────┼──────────┼────────────
"""

    def writeTextFooter(self,  txtStream, txt2Stream):
        self.pageNum += 1
        orgName = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'title'))
        orgChief = forceString(QtGui.qApp.db.translate('Organisation', \
            'id',  QtGui.qApp.currentOrgId(), 'chief'))
        date = (u'с 01.%s по %s' % (forceString(self.accDate.toString('MM.yy')),
                            forceString(self.accDate.toString('dd.MM.yy'))))

        txtStream << u"""____________________________________________________________________________\n"""
        footer = u"""         За период %s            ИТОГО: %12.2f

Генеральный директор
%s                                     %s
\n%76d\x0C\x0D
"""
        txtStream << footer % (date,  self.totalSum,  orgName,  orgChief, self.pageNum)
        txtStream << self.appendixStr
        txtStream << footer % (date,  self.totalSum,  orgName,  orgChief, 1)
        txt2Stream << u"""____________________________________________________________________________\n"""
        txt2Stream << footer % (date,  self.totalSum,  orgName,  orgChief, 1)


    def writeClientHeader(self, txtStream, record):
        identifier = forceString(record.value('identifier'))
        self.clientSum = 0
        self.clientMKBSum = 0
        self.clientAmount = 0
        self.clientOldRecord = record
        self.clientCount += 1
        workName = forceString(record.value('workName'))

        if not workName:
            workName = u'ФИЗ. ЛИЦО'

        header = u"""Лицевой счет %s

Пациент %s %s %s
полис N %12.12s серия %10.10s место работы %24.24s
N истории болезни %s
с об'емом медицинской помощи Пол-ка+стом
""" % (
            identifier,
            forceString(record.value('lastName')).upper(),
            forceString(record.value('firstName')).upper(),
            forceString(record.value('patrName')).upper(),
            forceString(record.value('policyNumber')),
            forceString(record.value('policySerial')),
            workName,
            identifier
        )
        txtStream << header


    def writeClientFooter(self, txtStream, appendixStream):
        self.pageNum += 1
        footer = u"""\n
____________________________________________________________________________
 За пациента %s ИТОГО:\t%12.2f
\n%76d\x0C\x0D
""" % (
            forceString(self.clientOldRecord.value('lastName')).ljust(42).upper(),
            self.clientSum,
            self.pageNum
       )
        self.totalSum += self.clientSum
        txtStream << footer
        workName = forceString(self.clientOldRecord.value('workName'))
        if not workName:
            workName = u'ФИЗ.ЛИЦО'

        appendixFmtStr = u"""       │                    │            │            │   │                 │
 %6.6s│%s│%12.12s│%12.12s│%3d│  %13.2f  │
       │                    │%s│            │   │                 │
____________________________________________________________________________\n"""
        appendixStream << appendixFmtStr % (forceString(self.clientOldRecord.value('identifier')),
            formatShortName(forceString(self.clientOldRecord.value('lastName')).upper(),
                                    forceString(self.clientOldRecord.value('firstName')).upper(),
                                    forceString(self.clientOldRecord.value('patrName')))[:20].ljust(20).upper(),
            forceString(self.clientOldRecord.value('policyNumber')),
            workName[:12].ljust(12).upper(),
            self.clientAmount,
            self.clientSum,
            forceString(self.clientOldRecord.value('policySerial')).rjust(12)    # Серия полиса
            )


    def writeClientStr(self,  txtStream, appendixStream,  record):
        header = u"""%s
____________________________________________________________________________
Дата    │ Код  │  Вид выполненных   │Исполнитель│Кол│Договорная│   Сумма
        │      │       работ        │           │ - │   цена   │      к
        │      │                    │           │во │вып.работ │   оплате
        │      │                    │           │   │за единицу│
────────┼──────┼────────────────────┼───────────┼───┼──────────┼────────────\n"""
        fmtStr = u'%8.8s│%6.6s│%20.20s│%11.11s│%3.3s│%10.10s│%12.12s\n'
        footer = u""" ___________________________________________________________________________
          ИТОГО:\t\t\t\t\t\t%12.2f\n"""
        serviceName = splitStrByLen(forceString(record.value('serviceName')), 20)
        personName = splitStrByLen(forceString(record.value('personName')).upper(), 11)
        maxLen = max(len(serviceName),  len(personName))
        sum = forceDouble(record.value('sum'))
        amount = forceInt(record.value('amount'))
        diagName = u'\n'.join(splitStrByLen(
            u' диагноз: %s %s' % (
                forceString(record.value('MKB')),
                forceString(record.value('diagName'))
            ), 76))
        self.clientSum += sum
        self.clientMKBSum += sum
        self.clientAmount += amount

#        txtStream << header % diagName
        for i in range(0,  maxLen):
            txtStream << (fmtStr % (
                forceDate(record.value('execDate')).toString('dd.MM.yy') if i == 0 else '',
                (u'%6.6s' % forceString(record.value('serviceCode'))) if i == 0 else '',
                serviceName[i].ljust(20) if i < len(serviceName) else '',
                personName[i].ljust(11) if i < len(personName) else '',
                (u'%3d' % amount) if i == 0 else '',
                (u'%10.2f' % forceDouble(record.value('price'))) if i == 0 else '',
                (u'%12.2f' % sum) if i == 0 else ''
            ))

#        txtStream<< footer % sum


    def writeMKBHeader(self, txtStream, record):
        header = u"""%s
____________________________________________________________________________
Дата    │ Код  │  Вид выполненных   │Исполнитель│Кол│Договорная│   Сумма
        │      │       работ        │           │ - │   цена   │      к
        │      │                    │           │во │вып.работ │   оплате
        │      │                    │           │   │за единицу│
────────┼──────┼────────────────────┼───────────┼───┼──────────┼────────────\n"""
        diagName = u'\n'.join(splitStrByLen(
            u' диагноз: %s %s' % (
                forceString(record.value('MKB')),
                forceString(record.value('diagName'))
            ), 76))
        txtStream << header % diagName
        self.clientMKBSum = 0


    def writeMKBFooter(self, txtStream, record):
        footer = u""" ___________________________________________________________________________
          ИТОГО:\t\t\t\t\t\t%12.2f\n"""
        txtStream<< footer % self.clientMKBSum


    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R77NativeExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        srcDbf = self.wizard().getFullDbfFileName()
        srcTxt = self.wizard().getFullTxtFileName()
        srcTxt2 = self.wizard().getFullTxt2FileName()
        dstDir = os.path.join(forceStringEx(self.edtDir.text()), self.wizard().dbfDirName)

        if not os.path.exists(dstDir):
            os.makedirs(dstDir)

        dstDbf = os.path.join(dstDir, os.path.basename(srcDbf))
        dstTxt = os.path.join(dstDir, os.path.basename(srcTxt))
        dstTxt2 = os.path.join(dstDir, os.path.basename(srcTxt2))
        success, result = QtGui.qApp.call(self, shutil.move, (self.wizard().getFullDbfFileName(), dstDbf))

        if success:
            success, result = QtGui.qApp.call(self, shutil.move, (self.wizard().getFullTxtFileName(), dstTxt))

        if success:
            success, result = QtGui.qApp.call(self, shutil.move, (srcTxt2, dstTxt2))

        if success:
            QtGui.qApp.preferences.appPrefs['R77NativeExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()
        return success


    @QtCore.pyqtSlot(QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
