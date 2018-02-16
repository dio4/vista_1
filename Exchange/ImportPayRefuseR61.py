#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Accounting.Utils import updateAccountTotals
from Events.Utils import CPayStatus, getPayStatusMask
from KLADR.Utils import fixLevel

from Ui_ImportPayRefuseR23 import Ui_Dialog
from Cimport import *

from os import path

def ImportPayRefuseR61Native(widget, accountId, accountItemIdList):
    if not accountId:
        return
    dlg = CImportPayRefuseR61Native(widget, accountId, accountItemIdList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR61FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR61FileName'] = toVariant(dlg.edtFileName.text())


class CImportPayRefuseR61Native(QtGui.QDialog, Ui_Dialog, CDBFimport):
    """
        Импорт отказов для Ростовской области. Работает с 3 типами файлов:
            *kontrol.dbf - непосредственно отказы по счетам.
            dekszak.dbf - результаты какой-то проверки. Процедура импорта
                          такая же, как и для *kontrol.dbf, разница в
                          названиях полей.
            patientp.dbf - информация о полисах.
        Описание файлов и их структура находятся в задаче 705 в mantis'е.
    """
    sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}

    def __init__(self, parent, accountId, accountItemIdList):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.parent = parent
        CDBFimport.__init__(self, self.log)
        #self.accountId=accountId
        #self.accountItemIdList=accountItemIdList

        self.accountId = accountId
        self.process = None
        self.processedEvents = []
        self.checkName()
        self.errorPrefix = ''
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0

        self.tabImportType.setVisible(False)
        self.label_3.setVisible(False)

        self.processedEvents = []

        self.tblPayRefuseType = tbl('rbPayRefuseType')
        self.tableAccountItem = tbl('Account_Item')
        self.tableEvent = tbl('Event')
        self.tableAccount = tbl('Account')
        self.tableClientPolicy = tbl('ClientPolicy')
        self.tableVisit = tbl('Visit')
        self.tableAction = tbl('Action')
        self.tableAcc=self.db.join(self.tableAccountItem, self.tableAccount,
            'Account_Item.master_id=Account.id').join(self.tableEvent,
            'Account_Item.event_id=Event.id')
        self.prevContractId = None
        self.financeTypeOMS = forceRef(self.db.translate('rbFinance',
            'code', '2', 'id'))
        self.orgCache = {}
        self.deleteAccount = False
        self.setWindowTitle(u'Загрузка отказов оплаты для Ростовской области')
        self.labelNum.setText(u'')

        # Получаем тип финансирования и маску
        if accountId:
            tempQ = QtGui.qApp.db.query('SELECT Contract.finance_id FROM Account LEFT JOIN Contract ON Contract.id = Account.contract_id WHERE Account.id = %s' % accountId)
            if tempQ.next():
                rec = tempQ.record()
                self.financeId = forceRef(rec.value('finance_id'))
                self.payStatusMask = getPayStatusMask(self.financeId)
            else:
                self.financeId = 0
                self.payStatusMask = 0
        else:
            self.financeId = 0
            self.payStatusMask = 0
        self.requiredFields = {#self.processKontrol: ['NSCHT', 'KODP', 'ER_COD', 'COMENT'],         # Должно быть по стандарту, но в Ростове - мудаки.
                               self.processKontrol: ['NSCHT', 'KODP', 'ER_COD', 'ER_MESSAGE'],
                               self.processPolicy: ['KODST', 'SERIA', 'NPOLI', 'VPOLIS', 'NSTRA', 'KTERR'],
                               self.processExpertise: ['NSCHT', 'KOTK', 'PRIM']}


    def checkName(self):
        result = self._checkName()
        self.btnImport.setEnabled(result)

    def _checkName(self):
        name = self.edtFileName.text()
        name = path.split(unicode(name))[-1]
        if name.lower() == u'pacientp.dbf':
            self.process = self.processPolicy
            return True
        elif name.lower() == u'dekszak.dbf':
            self.process = self.processExpertise
            return True
        elif u'kontrol.dbf' in name.lower():
            self.process = self.processKontrol
            return True
        self.process = None
        return False


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.processedEvents = []
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            #self.btnImport.setEnabled(True)
            self.checkName()
            if not self.btnImport.isEnabled():
                return
            dbfFileName = unicode(forceStringEx(self.edtFileName.text()))
            dbfR61 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            #self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfR61)))


    def err2log(self, e):
        self.log.append(self.errorPrefix+e)


    def startImport(self):
        self.deleteAccount = False
        self.progressBar.setFormat('%p%')

        self.prevContractId = None
        self.accountIdSet = set()

        self.nProcessed = 0
        self.nNotFound = 0


        self.log.clear()
        dbfFileName = unicode(self.edtFileName.text())
        dbfR61 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        #self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfR61)))

        assert dbfCheckNames(dbfR61, self.requiredFields[self.process])
        self.progressBar.setMaximum(len(dbfR61))

        #self.process(dbfR61)

        for row in dbfR61:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.progressBar.step()
            self.stat.setText(
                u'обработано: %d;  не найдено: %d' % \
                (self.nProcessed, self.nNotFound))
            self.process(row)

        updateAccountTotals(self.accountId)
        self.stat.setText(
            u'обработано: %d; не найдено: %d' % \
            (self.nProcessed, self.nNotFound))


    def processKontrol(self, row):

        refuseTypeCode = forceString(row['ER_COD'])
        eventId = forceRef(row['NSCHT'])
        note = forceString(row['ER_MESSAGE'])
        self.processEventsInt(eventId, refuseTypeCode, note, row)
        self.updateAccountRefusedTotals(self.accountId)
        self.updateAccountPayedTotals(self.accountId)

    def processExpertise(self, row):
        eventId = forceRef(row['NSCHT'])
        refuseTypeCode = forceString(row['KOTK'])
        note = forceString(row['PRIM'])
        self.processEventsInt(eventId, refuseTypeCode, note, row)
        self.updateAccountRefusedTotals(self.accountId)
        self.updateAccountPayedTotals(self.accountId)


    def processEventsInt(self, eventId, refuseTypeCode, note, row):
        db = QtGui.qApp.db
        tbl = self.tableAccountItem
        tblVisit = self.tableVisit
        tblAction = self.tableAction
        now = toVariant(QDate.currentDate())

        # Проверяем наличие типа отказа
        refuseTypeId = db.translate('rbPayRefuseType', 'code', refuseTypeCode, 'id')
        if not refuseTypeId:
            self.err2log(u'Тип отказа с кодом %s не найден. Пропускаем.' % refuseTypeCode)
            self.nNotFound += 1
            return

        # Если указан тип обращения
        if eventId:
            # и обращение еще не обработано
            if not eventId in self.processedEvents:
                # Получаем запись обращения
                eventRecord = db.getRecordEx('Event', 'deleted', 'id=%s' % eventId)

                # Проверяем, что обращение существует
                if not eventRecord:
                    self.err2log(u'Обращение с номером %s не найдено. Пропускаем.' % eventId)
                    self.nNotFound += 1
                    return

                # Проверяем, что обращение не удалено
                if forceBool(eventRecord.value('deleted')):
                    self.err2log(u'Обновляем удаленное обращение с номером %s' % eventId)

                # Выражение для получения всех AccountItem'ов данного обращения по выбранному счету
                if self.accountId:
                    stmt = u'''SELECT id, visit_id, action_id FROM Account_Item WHERE event_id = %s AND master_id = %s''' % (eventId, self.accountId)
                #else:
                #    stmt = u'''SELECT id, visit_id, action_id FROM Account_Item WHERE event_id = %s AND master_id = (SELECT MAX(master_id) FROM Account_Item WHERE event_id = %s)''' % (eventId, eventId)
                #accountId = forceRef(db.translate('Account_Item', 'event_id', eventId, 'MAX(master_id)'))


                idList = []
                visitIdList = []
                actionIdList = []
                changeEventPayStatus = False

                # Получаем список посещений и действий, PayStatus которых необходимо обновить.
                # В случае отсуствия посещения или действия меняем payStatus обращения.
                query = db.query(stmt)
                while query.next():
                    record = query.record()
                    idList.append(forceRef(record.value('id')))
                    visitId = forceRef(record.value('visit_id'))
                    actionId = forceRef(record.value('action_id'))
                    if visitId:
                        visitIdList.append(visitId)
                    elif actionId:
                        actionIdList.append(visitId)
                    else:
                        changeEventPayStatus = True


                if idList:
                    # Обновляем все Account_Item'ы, подлежащие изменению.
                    sets = [tbl['number'].eq(u'Отказано'),
                            tbl['note'].eq(note),
                            tbl['date'].eq(now),
                            tbl['refuseType_id'].eq(refuseTypeId)]
                    cond = tbl['id'].inlist(idList)
                    count = db.updateRecords(tbl, sets, cond)

                    # Обновляем соответствующие payStatus'ы
                    if visitIdList:
                        visitCond = tblVisit['id'].inlist(visitIdList)
                        stmt = u'UPDATE Visit SET payStatus = ((payStatus & ~%d) | %d) WHERE %s' % \
                               (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, visitCond)
                        db.query(stmt)
                    if actionIdList:
                        actionCond = tblAction['id'].inlist(actionIdList)
                        stmt = u'UPDATE Action SET payStatus = ((payStatus & ~%d) | %d) WHERE %s' % \
                               (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, actionCond)
                        db.query(stmt)
                    if changeEventPayStatus and eventId:
                        stmt = u'UPDATE Event SET payStatus = ((payStatus & ~%d | %s) WHERE id = %d' % \
                               (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, eventId)
                        db.query(stmt)
                self.processedEvents.append(eventId)
                self.nProcessed += len(idList)
            else:
                #self.nProcessed += 1
                self.err2log(u'Обращение с номером %s уже обработано. Пропускаем.' % eventId)
        elif not eventId:
            clientId = forceRef(row['KODP'])
            tblEvent = self.tableEvent

            # Проверяем существование типа отказа
            refuseTypeId = db.translate('rbPayRefuseType', 'code', refuseTypeCode, 'id')
            if not refuseTypeId:
                self.err2log(u'Тип отказа с кодом %s не найден. Пропускаем.' % refuseTypeCode)
                self.nNotFound += 1
                return

            eventIdList = []
            # if not self.accountId:
            #     cond = tblEvent['client_id'].eq(clientId)
            #     queryTable = tbl.innerJoin(tblEvent, tblEvent['id'].eq(tbl['event_id']))
            #     #record = db.getRecordEx(queryTable, 'MAX(Account_Item.master_id) as accountId', cond)
            #     #accountId = forceRef(record.value('accountId'))
            #     accountId = 0
            #
            #     recordList = db.getRecordList(queryTable, 'Event.id, Account_Item.master_id', cond)
            #     for record in recordList:
            #         newAccountId = forceRef(record.value('master_id'))
            #         eventId = forceRef(record.value('id'))
            #         if newAccountId > accountId:
            #             accountId = newAccountId
            #             eventIdList = [eventId]
            #         elif newAccountId == accountId:
            #             eventIdList.append(eventId)
            #
            # else:
            accountId = self.accountId
            cond = [tblEvent['client_id'].eq(clientId),
                    tbl['master_id'].eq(accountId)]
            queryTable = tbl.innerJoin(tblEvent, tblEvent['id'].eq(tbl['event_id']))
            #eventIdList = db.getIdList(queryTable, where = db.joinAnd(cond))
            eventRecords = db.getRecordList(queryTable, 'Account_Item.event_id, Account_Item.visit_id, Account_Item.action_id', cond)
            visitIdList = []
            actionIdList = []
            payStatusEventIdList = []
            for record in eventRecords:
                visitId = forceRef(record.value('visit_id'))
                actionId = forceRef(record.value('action_id'))
                eventId = forceRef(record.value('event_id'))
                if visitId:
                    visitIdList.append(visitId)
                elif actionId:
                    actionIdList.append(actionId)
                elif not eventId in payStatusEventIdList:
                    payStatusEventIdList.append(eventId)
                eventIdList.append(eventId)
            eventIdList = list(set(eventIdList))

            if not eventIdList:
                self.err2log(u'Не найдено выставленных счетов по обращениям пациента с кодом %s. Пропускаем.' % clientId)
                self.nNotFound += 1
                return

            visitCond = tblVisit['id'].inlist(visitIdList)
            actionCond = tblAction['id'].inlist(actionIdList)
            eventCond = tblEvent['id'].inlist(payStatusEventIdList)
            db.transaction()
            stmt = u'UPDATE Visit SET payStatus = ((payStatus & ~%d) | %d) WHERE %s' % \
                   (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, visitCond)
            db.query(stmt)
            stmt = u'UPDATE Action SET payStatus = ((payStatus & ~%d) | %d) WHERE %s' % \
                   (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, actionCond)
            db.query(stmt)
            if eventCond != '0':
                stmt = u'UPDATE Event SET payStatus = ((payStatus & ~%d | %s) WHERE %s' % \
                       (self.payStatusMask, self.payStatusMask & CPayStatus.refusedBits, eventCond)

                db.query(stmt)

            sets = [tbl['number'].eq(u'Отказано'),
                    tbl['note'].eq(note),
                    tbl['date'].eq(now),
                    tbl['refuseType_id'].eq(refuseTypeId)]
            cond = tbl['master_id'].eq(accountId)
            count = db.updateRecords(tbl, sets, cond).numRowsAffected()
            if count == -1:
                count = 0
            db.commit()
            self.processedEvents += eventIdList
            self.nProcessed += count


    def updateAccountRefusedTotals(self, accountId):
        stmt = '''
        UPDATE Account,
               (SELECT
                  SUM(amount) AS totalAmount,
                  SUM(sum)    AS totalSum
                FROM Account_Item
                WHERE  Account_Item.master_id = %d AND refuseType_id IS NOT NULL
                 ) AS tmp

        SET Account.refusedAmount = tmp.totalAmount,
            Account.refusedSum = tmp.totalSum
        WHERE Account.id = %d'''%(accountId, accountId)
        db = QtGui.qApp.db
        db.query(stmt)

    def updateAccountPayedTotals(self, accountId):
        stmt = '''
        UPDATE Account,
               (SELECT
                  SUM(amount) AS totalAmount,
                  SUM(sum)    AS totalSum
                FROM Account_Item
                WHERE  Account_Item.master_id = %d AND
                        date IS NOT NULL AND
                        number != '' AND
                        refuseType_id IS NULL
                 ) AS tmp

        SET Account.payedAmount = tmp.totalAmount,
            Account.payedSum = tmp.totalSum
        WHERE Account.id = %d'''%(accountId, accountId)
        db = QtGui.qApp.db
        db.query(stmt)



    def processPolicy(self, row):
        db = QtGui.qApp.db
        insurerInfis = forceString(row['KODST'])
        insurerInfisFromDBF = insurerInfis
        policySerial = forceString(row['SERIA'])
        policyNumber = forceString(row['NPOLI'])
        policyKind = forceString(row['VPOLIS'])
        policyKindId = forceRef(db.translate('rbPolicyKind', 'code', policyKind, 'id'))
        clientId = forceRef(row['KODP'])
        kterr = forceString(row['KTERR'])
        insurerName = forceString(row['NSTRA'])

        # Try to find insurer org by infis code
        tblClientPolicy = self.tableClientPolicy
        tblOrganisation = self.tableOrganisation
        insurerId = None
        if not insurerInfis:
            cond = [tblOrganisation['shortName'].eq(insurerName),
                    tblOrganisation['OKATO'].like('%s%%' % kterr),
                    tblOrganisation['deleted'].eq(0),
                    tblOrganisation['isInsurer'].eq(1)]
            rec = db.getRecordEx(tblOrganisation, 'id', cond)
            #print db.selectStmt(tblOrganisation, 'infisCode', cond)
            if rec:
                insurerId = forceRef(rec.value('id'))
            else:
                self.err2log(u'Для пациента %s не найдена страховая компания с названием \'%s\'' % (clientId, insurerName))
        else:
            # Будет работать, пока infisCode уникальны и соответствуют организациям с isInsurer = 1 AND isDeleted = 0
            insurerCond = [tblOrganisation['infisCode'].eq(insurerInfis),
                            tblOrganisation['deleted'].eq(0),
                            tblOrganisation['isInsurer'].eq(1)]
            insurerRecord = db.getRecordEx('Organisation', 'id', insurerCond)
            insurerId = forceRef(insurerRecord.value('id'))
            #insurerId = forceRef(db.translate('Organisation', 'infisCode', insurerInfis, 'id'))
            if not insurerId:
                self.err2log(u'Для пациента %s не найдена страховая компания с ИНФИС кодом %s' % (clientId, insurerInfisFromDBF))

        insuranceArea = self.getInsuranceArea(kterr)
        # Check only territorial compulsory policies
        policyTypeId = forceString(db.translate('rbPolicyType', 'code', '1', 'id'))
        policyRecord = selectLatestRecord('ClientPolicy', clientId, 'Main.policyType_id = %s' % policyTypeId)
        if policyRecord:
            currentInsurerId = forceRef(policyRecord.value('insurer_id'))
        #
        # print 'policySerial', policySerial, forceString(policyRecord.value('serial')), policySerial == forceString(policyRecord.value('serial'))
        # print 'policyNumber', policyNumber, forceString(policyRecord.value('number')), policyNumber == forceString(policyRecord.value('number'))
        # print 'policyKind', policyKindId, forceRef(policyRecord.value('policyKind_id')), policyKindId == forceRef(policyRecord.value('policyKind_id'))
        # print 'area', insuranceArea, forceString(policyRecord.value('insuranceArea')), insuranceArea == forceString(policyRecord.value('insuranceArea'))
        # print type(insurerId), type(currentInsurerId), insurerId == currentInsurerId
        # print



        if (policyRecord and not (policySerial == forceString(policyRecord.value('serial'))
                and policyNumber == forceString(policyRecord.value('number'))
                and policyKindId == forceRef(policyRecord.value('policyKind_id'))
                and insuranceArea == forceString(policyRecord.value('insuranceArea'))
                and insurerId == currentInsurerId)) or not policyRecord:

            record = tblClientPolicy.newRecord()
            if policySerial:
                record.setValue('serial', toVariant(policySerial))
            if policyNumber:
                record.setValue('number', toVariant(policyNumber))
            if policyKindId:
                record.setValue('policyKind_id', toVariant(policyKindId))
            if insurerId:
                record.setValue('insurer_id', toVariant(insurerId))
            record.setValue('insuranceArea', toVariant(insuranceArea))
            record.setValue('client_id', toVariant(clientId))
            record.setValue('policyType_id', toVariant(policyTypeId))
            db.insertRecord(tblClientPolicy, record)
            self.err2log(u'У клиента с id %s полис изменился. Обновляем.' % clientId)
            self.nProcessed += 1

    def getInsuranceArea(self, kterr):
        db = QtGui.qApp.db
        if kterr[:2] != u'60':
            insuranceArea = forceString(db.getRecordEx('kladr.KLADR', 'CODE', 'OCATD LIKE \'%s%%\'' % kterr).value('CODE'))
        else:
            insuranceAreaList = db.getRecordList('kladr.KLADR', 'CODE', 'OCATD LIKE \'%s%%\'' % kterr)

            insuranceArea = ''
            if len(insuranceAreaList) == 1:
                insuranceArea = forceString(insuranceAreaList[0].value('CODE'))
            elif len(insuranceAreaList) > 1:
                level = 4
                for code in insuranceAreaList:
                    code = forceString(code.value(0))
                    if not insuranceArea:
                        insuranceArea = code
                        level = fixLevel(code, 0)
                    else:
                        newLevel = fixLevel(code, 0)
                        if level > newLevel:
                            level = newLevel
                            insuranceArea = code
        return insuranceArea
