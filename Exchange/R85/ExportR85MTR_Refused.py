# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015Vista Software. All rights reserved.
##
#############################################################################

import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui, QtXml
from library.ProgressBar import CProgressBar

from library.ProgressInformer import CProgressInformer
from library.Utils import getClassName, forceStringEx, forceInt, forceDate, forceTr, \
    CLogHandler, forceDouble, forceRef, getPref, setPref
from library.XML.XMLHelper import CXMLHelper
from library.database import connectDataBaseByInfo, CDatabase

from ExchangeEngine import CExchangeR85Engine

def exportR85MTR(widget, accountId):
    exportWindow = CExport85MTR_Refused(QtGui.qApp.db, accountId, widget)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), {})
    exportWindow.setParams(params)
    exportWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(exportWindow), exportWindow.params())


class CExportR85MTREngine_Refused(CExchangeR85Engine):

    def __init__(self, db, progressInformer = None):
        super(CExportR85MTREngine_Refused, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self.orgForDeferredFilling = {}
        self.personSpecialityForDeferredFilling = {}
        self.accCodeToAccountItemId = {}
        self.documents = {}
        self.fileNames = {}
        self.notIdCase = []

        self.counterId = None


#----- XML struct makers and fillers -----
    def addHeaderElement(self, rootElement, destOKATO):
        header = CXMLHelper.addElement(rootElement, 'ZGLV')
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'VERSION'),   # Версия взаимодействия
                            self.version[:5])
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'DATA'),      # Дата
                            QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate))
        CXMLHelper.setValue(CXMLHelper.addElement(header, 'OKATO_OMS'), # Код ОКАТО территории страхования по ОМС (территория, в которую выставляется счет)
                            self.formatOKATO(destOKATO))
        return header


    def addAccountElement(self, rootElement, record):
        account = CXMLHelper.addElement(rootElement, 'SCHET')
        accDate = forceDate(record.value('settleDate'))

        CXMLHelper.setValue(CXMLHelper.addElement(account, 'YEAR'),     # отчетный год
                            accDate.year())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'MONTH'),    # отчетный месяц
                            accDate.month())
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'NSCHET'),   # номер счета
                            forceStringEx(record.value('number')).split(u'/п')[0][:15])
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'DSCHET'),   # дата выставления счёта
                            forceDate(record.value('exposeDate')).toString(QtCore.Qt.ISODate))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'SUMMAV'),   # сумма, выставленная на оплату
                            '%.2f' % forceDouble(record.value('sum')))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'SUMMAP'),   # сумма, принятая к оплате
                            '%.2f' % forceDouble(record.value('summap')))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_MEK'), # финансовые санкции (МЭК)
                            '%.2f' % forceDouble(record.value('sank_mek')))
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_MEE'), # финансовые санкции (МЭЭ)
                            '%.2f' % 0.0)
        CXMLHelper.setValue(CXMLHelper.addElement(account, 'SANK_EKMP'),# финансовые санции (ЭКМП)
                            '%.2f' % 0.0)
        return account


    def addEntryElement(self, rootElement, record, entryNumber):
        entryElement = CXMLHelper.addElement(rootElement, 'ZAP')

        CXMLHelper.setValue(CXMLHelper.addElement(entryElement, 'N_ZAP'), # номер позиции записи
                            entryNumber)
        patientElement = CXMLHelper.addElement(entryElement, 'PACIENT')   # сведения о пациенте
        self.fillPacient(patientElement, record)
        return entryElement, patientElement


    def fillPacient(self, patientElement, record):
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'VPOLIS'), # тип полиса
                            forceInt(record.value('policyKindCode')))

        policySerial = forceStringEx(record.value('policySerial'))

        if policySerial.lower() != u'еп' and len(policySerial) > 0:
            CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'SPOLIS'), # серия полиса
                                policySerial [:10])
        CXMLHelper.setValue(CXMLHelper.addElement(patientElement, 'NPOLIS'), # номер полиса
                            forceStringEx(record.value('policyNumber'))[:20])


    def addEventElement(self, entryElement, idCase, record):
        eventElement = CXMLHelper.addElement(entryElement, 'SLUCH')

        idCaseElement = CXMLHelper.addElement(eventElement, 'IDCASE')
        if idCase is not None:
            CXMLHelper.setValue(idCaseElement, idCase)   # номер запси в случае реестров
        else:
            self.notIdCase.append(idCaseElement)
        externalId = forceStringEx(record.value('externalId'))
        partsExternalId = externalId.strip().split('#')
        externalId = partsExternalId[0] if len(partsExternalId) > 0 else ""

        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'NHISTORY'),    # номер истории болезни
                            externalId[:50])
        if forceInt(record.value('eventAidUnitCode')) > 0:
            CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'IDSP'),        # Код способа оплаты медицинской помощи
                                forceInt(record.value('eventAidUnitCode')))
        #atronah: принято решение, что для случая кол-во всегда 1, а цена и сумма равны суммарной стоимости всех услуг
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'ED_COL'),      # количество единиц оплаты медицинской помощи
                            '%.2f' % 1.0)
        CXMLHelper.setValue(CXMLHelper.addElement(eventElement, 'TARIF'),       # тариф
                            '%.2f' % forceDouble(record.value('price')))
        CXMLHelper.addElement(eventElement, 'SUMV')        # сумма, выставленная к оплате
        CXMLHelper.addElement(eventElement, 'OPLATA')      # тип оплаты  # 0 - не принято решение об оплате, 1 - полная оплата, 2 - полный отказ, 3 - частичный отказ
        CXMLHelper.addElement(eventElement, 'SUMP')        # сумма, принятая к оплате
        CXMLHelper.addElement(eventElement, 'SANK_IT')     # сумма санкций по случаю

        return eventElement

    def addSankElement(self, entryElement, idCase, record):
        sankElement = CXMLHelper.addElement(entryElement, 'SANK')

        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_CODE'),      # идентификатор санкции
                            idCase)
        CXMLHelper.addElement(sankElement, 'S_SUM')       # финансовая санкция
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_TIP'),       # тип санкции
                            1)    # 1 - МЭК, 2 - МЭЭ, 3 - ЭКМП
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_OSN'),       # Код причины отказа (частичной) оплаты
                            forceStringEx(record.value('refuseTypeCode')))
        CXMLHelper.setValue(CXMLHelper.addElement(sankElement, 'S_IST'),       # источник
                            2)                                                 # 1 – ТФОМС1 к МО,
                                                                               # 2 – ТФОМС2 к ТФОМС1 (только в протоколе обработ-ки основной части),
                                                                               # 3 – уточнённые санкции ТФОМС1 к МО (только в ис-правленной части и далее),
                                                                               # 4 – итоговые санк-ции ТФОМС2 к ТФОМС1 (только в протоколе обработ-ки исправленной части),
                                                                               # где:
                                                                               # ТФОМС1 – ТФОМС террито-рии оказания меди-цинской помощи;
                                                                               # ТФОМС2 – ТФОМС террито-рии страхования;
                                                                               # МО – МО, оказав-шая медицинскую помощь.

        return sankElement


    def createXMLDocument(self, accountRecord, destOKATO):
        doc = CXMLHelper.createDomDocument(rootElementName='ZL_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        self.addHeaderElement(rootElement, destOKATO)
        accountElement = self.addAccountElement(rootElement, accountRecord)
        return doc, accountElement


    def process(self, accountId):
        self.isAbort = False
        self.phaseReset(11)

        db = QtGui.qApp.db

        tableOrganisation = self._db.table('Organisation')

        tableAccount = self._db.table('Account')
        tableContract = self._db.table('Contract')
        tableContractPayer = tableOrganisation.alias('ContractPayer') # Сторонний фонд, в который происходит выгрузка
        tableContractRecipient = tableOrganisation.alias('ContractRecipient') # Текущий фонд, откуда происходит выгрузка

        queryTable = tableAccount.innerJoin(tableContract, tableContract['id'].eq(tableAccount['contract_id']))
        queryTable = queryTable.innerJoin(tableContractPayer, tableContractPayer['id'].eq(tableContract['payer_id']))
        queryTable = queryTable.innerJoin(tableContractRecipient, tableContractRecipient['id'].eq(tableContract['recipient_id']))

        cols = [
                tableAccount['settleDate'],
                tableAccount['number'],
                tableAccount['exposeDate'],
                tableAccount['sum'],
                tableContractPayer['OKATO'].alias('payerOKATO'),
                tableContractPayer['infisCode'].alias('payerInfis'),
                tableContractPayer['area'].alias('payerArea'),
                tableContractRecipient['OKATO'].alias('recipientOKATO'),
                tableContractRecipient['infisCode'].alias('recipientInfis')
        ]

        self.nextPhase(3, u'Загрузка данных по счету')
        accountRecord = self._db.getRecordEx(queryTable,
                                             cols,
                                             where=tableAccount['id'].eq(accountId))

        currentInfis = forceStringEx(accountRecord.value('recipientInfis'))

        insuranceArea = forceStringEx(accountRecord.value('payerArea'))
        insurerFundOKATO = forceStringEx(accountRecord.value('payerOKATO'))
        insurerFundInfis = forceStringEx(accountRecord.value('payerInfis'))

        tableAccount = db.table('Account')
        tableAccountItem = db.table('Account_Item')
        tablePayRefuseType = db.table('rbPayRefuseType')

        tableEvent = db.table('Event')
        tableMedicalAidUnit = db.table('rbMedicalAidUnit')

        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')

        cols = [# account
                tableAccount['settleDate'],
                tableAccount['number'],
                tableAccount['exposeDate'],
                tableAccount['sum'],
                tableAccount['payedSum'].alias('summap'),
                tableAccount['refusedSum'].alias('sank_mek'),

                # client
                tableClientPolicy['id'].alias('clientPolicyId'),
                tablePolicyKind['federalCode'].alias('policyKindCode'),
                tableClientPolicy['serial'].alias('policySerial'),
                tableClientPolicy['number'].alias('policyNumber'),

                # event
                tableEvent['id'].alias('eventId'),
                tableEvent['externalId'],
                tableMedicalAidUnit['federalCode'].alias('eventAidUnitCode'),
                tableAccountItem['price'],
                tableAccountItem['sum'].alias('sumv'),
                u'''IF(Account_Item.date IS NULL AND Account_Item.refuseType_id IS NULL, 0,
                       IF(Account_Item.date IS NOT NULL AND Account_Item.refuseType_id IS NULL, 1, 2)) AS oplata''',
                'if(%s IS NULL, Account_Item.sum, 0) AS sump' % tablePayRefuseType['id'],
                'if(%s IS NOT NULL, Account_Item.sum, 0) AS sank_it' % tablePayRefuseType['id'],

                # sank
                tablePayRefuseType['flatCode'].alias('refuseTypeCode')
        ]

        queryTable = tableAccount.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
        queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, [tableClientPolicy['client_id'].isNotNull(),
                                                             '''ClientPolicy.id = (SELECT MAX(cp.id)
                                                                                   FROM ClientPolicy cp
                                                                                   WHERE cp.client_id = Event.client_id AND cp.deleted = 0)'''])
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tableClientPolicy['policyKind_id']))
        queryTable = queryTable.leftJoin(tableMedicalAidUnit, tableMedicalAidUnit['id'].eq(tableAccountItem['unit_id']))
        queryTable = queryTable.leftJoin(tablePayRefuseType, [tablePayRefuseType['id'].eq(tableAccountItem['refuseType_id']),
                                                              tableAccountItem['date'].isNotNull()])

        cond = [tableAccount['id'].eq(accountId),
                tableAccountItem['deleted'].eq(0)]

        self.nextPhaseStep(u'Загрузка данных по счету')
        recordList = self._db.getRecordList(queryTable, cols, where=cond)
        self.nextPhaseStep(u'Загрузка данных завершена')

        self.accCodeToAccountItemId.clear()
        entries = {}
        events = {}
        idCaseCounter = 0
        entryCounter = {}
        sankCounter = {}
        self.orgForDeferredFilling.clear()
        self.personSpecialityForDeferredFilling.clear()
        eventsTotal = {}
        oplataTotal = {}
        sankTotal = {}
        accountTotal = {}
        self.nextPhase(len(recordList), u'Обработка позиций счета')
        for record in recordList:
            if self.isAbort:
                self.onAborted()
                return False

            if not self.fileNames.has_key(insuranceArea):
                self.fileNames[insuranceArea] = (insurerFundInfis, currentInfis)

            if not self.documents.has_key(insuranceArea):
                self.documents[insuranceArea] = self.createXMLDocument(accountRecord, insurerFundOKATO)

            doc, accountElement = self.documents[insuranceArea]

            rootElement = CXMLHelper.getRootElement(doc)

            clientPolicyId = forceRef(record.value('clientPolicyId'))
            if not entries.has_key(clientPolicyId):
                entryCounter[insuranceArea] = entryCounter.setdefault(insuranceArea, 0) + 1
                entries[clientPolicyId] = self.addEntryElement(rootElement, record, entryCounter[insuranceArea])

            entryElement, _ = entries[clientPolicyId]

            eventId = forceStringEx(record.value('eventId'))

            if not events.has_key(eventId):
                sankTotal[eventId] = {}
                partsExternalId = forceStringEx(record.value('externalId')).strip().split('#')
                if len(partsExternalId) >= 3:
                    idCaseCounter = max(idCaseCounter, partsExternalId[2])
                events[eventId] = self.addEventElement(entryElement,
                                                       partsExternalId[2] if len(partsExternalId) >= 3 else None,
                                                       record)
            eventElement = events[eventId]

            refuseTypeCode = forceStringEx(record.value('refuseTypeCode'))
            if refuseTypeCode:
                if not sankTotal[eventId].has_key(refuseTypeCode):
                    sankCounter[eventId] = sankCounter.setdefault(eventId, 0) + 1
                    sankTotal[eventId][refuseTypeCode] = [self.addSankElement(eventElement,
                                                                  sankCounter[eventId],
                                                                  record=record), 0]
                sankTotal[eventId][refuseTypeCode][1] += forceDouble(record.value('sumv'))
            if not eventsTotal.has_key(eventId):
                eventsTotal[eventId] = [0] * 3
                oplataTotal[eventId] = [0, 1]
            eventsTotal[eventId][0] += forceDouble(record.value('sumv'))
            eventsTotal[eventId][1] += forceDouble(record.value('sump'))
            eventsTotal[eventId][2] += forceDouble(record.value('sank_it'))
            oplataTotal[eventId][0] += 1
            oplataTotal[eventId][1] *= forceInt(record.value('oplata'))
            self.nextPhaseStep()

        for elementIdCase in self.notIdCase:
            idCaseCounter = forceInt(idCaseCounter) + 1
            CXMLHelper.setValue(elementIdCase, idCaseCounter)
        self.nextPhase(len(eventsTotal), u'Заполнение данных о стоимости случаев')
        for eventId, total in eventsTotal.iteritems():
            eventElement = events[eventId]
            element = eventElement.firstChildElement('OPLATA')
            CXMLHelper.setValue(element, 0 if oplataTotal[eventId][1] == 0 else 1 if oplataTotal[eventId][1] == 1 else 2 if oplataTotal[eventId][1] % oplataTotal[eventId][0] == 0 else 3)
            if self.isAbort:
                self.onAborted()
                return False
            for index, elemName in enumerate(['SUMV', 'SUMP', 'SANK_IT']):
                element = eventElement.firstChildElement(elemName)
                CXMLHelper.setValue(element, '%.2f' % total[index])
                if not accountTotal.has_key(insuranceArea):
                    accountTotal[insuranceArea] = [0] * 3
                accountTotal[insuranceArea][index] += total[index]
            for refuseTypeCode, total in sankTotal[eventId].iteritems():
                sankElement = sankTotal[eventId][refuseTypeCode][0]
                element = sankElement.firstChildElement('S_SUM')
                CXMLHelper.setValue(element, '%.2f' % total[1])
            self.nextPhaseStep()

        self.nextPhase(len(accountTotal), u'Заполнение данных об общей стоимости счетов')
        for insuranceArea, total in accountTotal.iteritems():
            if self.isAbort:
                self.onAborted()
                return False
            _, accountElement = self.documents[insuranceArea]
            for index, elemName in enumerate(['SUMMAV', 'SUMMAP', 'SANK_MEK']):
                element = accountElement.firstChildElement(elemName)
                CXMLHelper.setValue(element, '%.2f' % total[index])
            self.nextPhaseStep()

        self.logger().info(u'Завершено')
        if self.isAbort:
            self.onAborted()
            return False
        return True

    def save(self, outDir, exportNumber):
        self.phaseReset(2)
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.documents), u'Сохранение файлов')
        for destArea in self.documents.keys():
            doc, _ = self.documents[destArea]
            insurerFundInfis, currentInfis = self.fileNames[destArea]
            fileName = u''.join([u'A',
                                 self.formatOKATO(insurerFundInfis, 2),
                                 self.formatOKATO(currentInfis, 2),
                                 u'%s' % QtCore.QDate.currentDate().toString('yy'),
                                 u'%.4d' % exportNumber])

            zipFilePath = forceStringEx(unicode(os.path.join(outDir, u'%s.oms' % fileName)))
            try:
                xmlFileName = QtCore.QTemporaryFile(u'%s.xml' % fileName)
                if not xmlFileName.open(QtCore.QFile.WriteOnly):
                    self.logger().critical(u'Не удалось открыть временный файл для записи')
                    break
                doc.save(QtCore.QTextStream(xmlFileName), 4, QtXml.QDomNode.EncodingFromDocument)
                xmlFileName.close()
                zf = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                zf.write(forceStringEx(QtCore.QFileInfo(xmlFileName).absoluteFilePath()), u'%s.xml' % fileName)
                zf.close()
                self.logger().info(u'Создан файл: "%s.oms"' % zipFilePath)
                self.documents.pop(destArea)
            except Exception, e:
                self.logger().critical(u'Не удалось сохранить файл "%s" (%s)' % (e.message, zipFilePath))
                self.onException()


class CExport85MTR_Refused(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2

    def __init__(self, db, accountId, parent=None):
        super(CExport85MTR_Refused, self).__init__(parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._accountId = accountId
        self._engine = CExportR85MTREngine_Refused(db, progressInformer=self._pi)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()
        self.onStateChanged()

    def engine(self):
        return self._engine

    def setParams(self, params):
        if isinstance(params, dict):
            outDir = forceStringEx(getPref(params, 'outDir', u''))
            if os.path.isdir(outDir):
                self.edtSaveDir.setText(outDir)
            accNumber = forceInt(getPref(params, 'accNumber', 0)) + 1
            self.spbAccountNumber.setValue(accNumber)

    def params(self):
        params = {}
        setPref(params, 'outDir', forceStringEx(self.edtSaveDir.text()))
        setPref(params, 'accNumber', self.spbAccountNumber.value())
        return params

    @property
    def currentState(self):
        return self._currentState

    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ExportState, self.SaveState]:
            self._currentState = value
            self.onStateChanged()

    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ExportState)
        self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbExport.setEnabled(self.currentState == self.ExportState)
        self.gbSave.setEnabled(self.currentState == self.SaveState)
        self.btnSave.setEnabled(bool(self._engine.documents))
        QtCore.QCoreApplication.processEvents()

    # noinspection PyAttributeOutsideInit
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QHBoxLayout()
        self.lblAccountNumber = QtGui.QLabel()
        gbLayout.addWidget(self.lblAccountNumber)
        self.spbAccountNumber = QtGui.QSpinBox()
        self.spbAccountNumber.setRange(1, 9999)
        gbLayout.addWidget(self.spbAccountNumber)
        self.gbInit.setLayout(gbLayout)
        layout.addWidget(self.gbInit)

        # export block
        self.gbExport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbExport.setLayout(gbLayout)
        layout.addWidget(self.gbExport)

        # save block
        self.gbSave = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtSaveDir = QtGui.QLineEdit(QtCore.QDir.homePath())
        self.edtSaveDir.setReadOnly(True)
        lineLayout.addWidget(self.edtSaveDir)
        self.btnBrowseDir = QtGui.QToolButton()
        self.btnBrowseDir.clicked.connect(self.onBrowseDirClicked)
        lineLayout.addWidget(self.btnBrowseDir)
        gbLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        # self.chkZipping = QtGui.QCheckBox()
        # lineLayout.addWidget(self.chkZipping)
        self.btnSave = QtGui.QPushButton()
        self.btnSave.clicked.connect(self.onSaveClicked)
        lineLayout.addWidget(self.btnSave)
        gbLayout.addLayout(lineLayout)
        self.gbSave.setLayout(gbLayout)
        layout.addWidget(self.gbSave)

        # log block
        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()

    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Экспорт. Крым. МежТер. Возврат.', context))
        self.gbInit.setTitle(forceTr(u'Параметры экспорта', context))
        self.lblAccountNumber.setText(forceTr(u'Номер выгрузки по счету', context))

        self.gbExport.setTitle(forceTr(u'Экспорт', context))

        self.gbSave.setTitle(forceTr(u'Сохранение результата', context))
        self.btnSave.setText(forceTr(u'Сохранить', context))

        self._actionNames = {self.InitState: forceTr(u'Экспорт', context),
                             self.ExportState: forceTr(u'Прервать', context),
                             self.SaveState: forceTr(u'Повторить', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))

    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ExportState
            try:
                result = self._engine.process(self._accountId)
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.SaveState if result else self.InitState

        elif self.currentState == self.ExportState:
            self._engine.abort()
        elif self.currentState == self.SaveState:
            self.currentState = self.InitState
        self.onStateChanged()

    def canClose(self):
        return not self._engine.documents or \
               QtGui.QMessageBox.warning(self,
                                         u'Внимание',
                                         u'Остались несохраненные файлы выгрузок,\n'
                                         u'которые будут утеряны.\n'
                                         u'Уверены, что хотить выйти из экспорта?\n',
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                         QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes

    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()

    def done(self, result):
        if self.canClose():
            super(CExport85MTR_Refused, self).done(result)

    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def onBrowseDirClicked(self):
        saveDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                                       u'Укажите директорию для сохранения файлов выгрузки',
                                                                       self.edtSaveDir.text()))
        if os.path.isdir(saveDir):
            self.edtSaveDir.setText(saveDir)

    @QtCore.pyqtSlot()
    def onSaveClicked(self):
        self.btnClose.setEnabled(False)
        self._engine.save(self.edtSaveDir.text(), self.spbAccountNumber.value())
        self.onStateChanged()



def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    isTestExport = True

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'crimeaMtr_1105',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    if isTestExport:
        accountId = 498
        w = CExport85MTR_Refused(QtGui.qApp.db, accountId)
        w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()