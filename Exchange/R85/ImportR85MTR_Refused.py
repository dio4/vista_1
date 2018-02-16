# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui
from Accounting.Utils import updateDocsPayStatus, getPayStatusMask
from Events.Utils import CPayStatus
from Exchange.R85.ExchangeEngine import CExchangeImportR85Engine
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer

from library.Utils import getPref, getClassName, setPref, forceRef, forceDate, forceStringEx, toVariant, \
    forceInt, CLogHandler, forceTr
from library.XML.XMLHelper import CXMLHelper
from library.database import CDatabase, connectDataBaseByInfo


def importR85MTR(widget, contractId):
    importWindow = CImport85MTR_Refused(QtGui.qApp.db, contractId)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), {})
    importWindow.setParams(params)
    importWindow.engine().setLastExceptionHandler(QtGui.qApp.logCurrentException)
    importWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), importWindow.params())


# noinspection PyShadowingBuiltins
class CImportR85MTREngine_Refused(CExchangeImportR85Engine):
    """"Движок" для импорта счетов по программе Межтерриториального обмена фондов.

        Описание формата импорта содержится в приложении
        "Информационное взаимодействие при осуществлении расчетов за медицинскую помощь, оказанную застрахованным лицам
        за пределами субъекта Российской Федерации, на территории которого выдан полис обязательного медицинского
        страхования, в формате XML"
        документа
        "ОБЩИЕ ПРИНЦИПЫ
        построения и функционирования информационных систем
        и порядок информационного взаимодействия
        в сфере обязательного медицинского страхования"
        утвержденного приказом ФОМС от "07" апреля 2011 г. №79 (в редакции приказа ФОМС от "26" декабря 2013 г. №276)

        :param db: экземпляр CDatabase, предоставляющий доступ к базе данных для импорта
        :param progressInformer: (опционально) ссылка на объект CProgressInformer для ифнормирования пользователя о прогресе импорта.
        """

    def __init__(self, db, contractId, progressInformer = None):
        super(CImportR85MTREngine_Refused, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self._contractId = contractId
        self._orgInfis = None
        self._currentOKATO = None

        self._contractIdByInfis = {}

        self._insurerCache = {}
        self._refuseIdCache = {}
        self.mapAccountIdToPayStatusMask = {}


    # ---- load\init\clear caches
    def initContractIdInfo(self):
        """Формирует кэш идентификаторов договоров для всех ТФ с учетом года действия.
        Делается выборка по всем договорам, дата окончания которых в этом или в предыдущем году,
        а также, у которых получателем является ТФ (5ти значный инфис код с 3 нулями на конце).
        Результаты выборки (id договоров) помещаются в словарь с ключом (инфис_код, год).

        Если год начала отличается от года окончания договора, то данный договор попадает в словарь столько раз,
        сколько лет охватывает его период действия.
        """
        self.nextPhase(1, u'Загрузка данных по договорам ТФ')
        self._contractIdByInfis.clear()
        tableContract = self._db.table('Contract')
        tableOrganisation = self._db.table('Organisation')
        queryTable = tableContract.innerJoin(tableOrganisation,
                                             tableOrganisation['id'].eq(tableContract['recipient_id']))

        recordList = self._db.getRecordList(table=queryTable,
                                            cols=[tableContract['id'].alias('contractId'),
                                                  tableContract['begDate'].alias('contractBegDate'),
                                                  tableContract['endDate'].alias('contractEndDate'),
                                                  tableOrganisation['infisCode']],
                                            where=[tableContract['deleted'].eq(0),
                                                   'YEAR(%s) >= (YEAR(CURRENT_DATE) - 1)' % tableContract['endDate'],
                                                   tableOrganisation['infisCode'].regexp('^[[:digit:]]{2}0{0,3}$')],
                                            order=tableContract['endDate'])
        self.nextPhase(len(recordList), u'Обработка данных по договорам ТФ')
        for record in recordList:
            sourceInfis = forceStringEx(record.value('infisCode'))[:2]
            begDate = forceDate(record.value('contractBegDate'))
            endDate = forceDate(record.value('contractEndDate'))
            contractId = forceRef(record.value('contractId'))
            for year in xrange(begDate.year(), endDate.year() + 1):
                self._contractIdByInfis[sourceInfis, year] = contractId
        self.finishPhase()


    def loadCurrentFundInfo(self):
        """Загружает информацию о текущем Фонде.

        """
        if len(self._contractId) != 1:
            self.logger().warning(u'Выбрано несколько TФ')
        self.nextPhase(1, u'Получение данных по текущему ТФ')
        tableOrganisation = self._db.table('Organisation')
        tableContract = self._db.table('Contract')
        record = self._db.getRecordEx(tableOrganisation.innerJoin(tableContract, tableContract['payer_id'].eq(tableOrganisation['id'])),
                                    cols=[tableOrganisation['infisCode'],
                                          tableOrganisation['OKATO']],
                                    where=tableContract['id'].eq(self._contractId[0]))
        self._orgInfis = forceStringEx(record.value('infisCode'))
        if not self._orgInfis:
            self.logger().warning(u'Не удалось получить инфис код текущего ТФ {%s}' % self._contractId)
        self._currentOKATO = self.formatOKATO(record.value('OKATO'), 2)
        self.finishPhase()


    def preloadInsurerCache(self):
        """Предварительная загрузка данных по Страховым компаниям.
        Формирует (обновляет) кэш страховых элементами вида *"Инфис код страховой"* = *ID страховой*
        """
        tableInsurer = self._db.table('Organisation')
        self._insurerCache.update([(forceStringEx(record.value('infisCode')), forceRef(record.value('id')))
                                   for record in self._db.getRecordList(tableInsurer,
                                                                        cols=[tableInsurer['id'],
                                                                              tableInsurer['infisCode']],
                                                                        where=[tableInsurer['isInsurer'].eq(1)],
                                                                        group='infisCode')])

    # ---- getters

    def getContractId(self, infisCode, year):
        """Возвращает ID договора, используемого для импорта по территории с указанным инфос кодом и на указанный год.
        Обрезает указанный инфис код до первых двух символов и ищет в кеше ID договора для такого инфис и года.

        :param infisCode: инфис территории, по которой производится импорт.
        :param year: год импорта.
        :return: ID договора, используемого для импорта указанной территории.
        """
        infisCode = forceStringEx(infisCode)[:2]
        contractId = self._contractIdByInfis.get((infisCode, year), None)
        if not contractId:
            self.logger().warning(u'Не удалось найти договор для импорта данных по территории с инфис "%s"' % infisCode)

        return contractId


    def getPayRefuseId(self, code):
        """Возвращает ID причины отказа {rbPayRefuseType}, соответсвующей указанному коду.
        Ищет в кеше или базе данных ID причины отказа, код которой соответствует указанному в *code*,
        после чего возвращает и кеширует это значение.
        Поиск производится по полю rbPayRefuseType.code.

        :param code: код отказа.
        :return: ID причины отказа {rbPayRefuseType}
        """
        if not self._refuseIdCache.has_key(code):
            refuseId = forceRef(self._db.translate('rbPayRefuseType', 'flatCode', code, 'id'))
            self._refuseIdCache[code] = refuseId
        return self._refuseIdCache[code]


    # ---- processing


    def process(self, fileName):
        """Запускает процесс импорта.

        :param fileName: имя файла для импорта
        :return: True
        """
        accInfo = {'countUpdate': 0}
        self.isAbort = False
        self.phaseReset(4)
        self.initContractIdInfo()
        self.loadCurrentFundInfo()
        self.preloadInsurerCache()
        self.processFile(fileName, accInfo)
        return accInfo['countUpdate']


    def parseFileName(self, fileName):
        """
        Вычленяет из имени файла важную информацию.
        Предполагается, что имя файла представлено в формате:
            R + код территориального фонда обязательного медицинского страхования, которому предъявлен счет
            +  код территориального фонда обязательного медицинского страхования, выставившего счет
            + две последние цифры года
            + четырехзначный порядковый номер представления основной части в текущем году
        :param fileName: имя обрабатываемого файла
        :return: isOk, isUpdate, sourceInfis, destInfis, year, number
        """
        try:
            name = os.path.splitext(os.path.basename(fileName))[0].lower()
            if name[0] == 'a' and len(name) == 11:
                return True, forceStringEx(name[1:3]), forceStringEx(name[3:5]), 2000 + int(name[5:7], 10), int(name[7:11], 10)
        except Exception, e:
            self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
            self.onException()

        return False, False, u'', u'', None, None


    def processFile(self, fileName, accInfo):
        """Импортирует указанный файл

        :param fileName: имя файла для импорта (A)<SS><DD><YY><NNNN>.(oms|xml) (описание имени см в `parseFileName`)
        :return: True, если импорт файла прошел успешно, False в ином случа
        :raise: Exception("архив пуст"), если архив пуст
        """
        docFile = None
        try:
            isOk, destInfis, sourceInfis,   year, number = self.parseFileName(fileName)
            if destInfis[:2] != self._orgInfis[:2]:
                self.logger().info(u'Пропуск обработки файла "%s": территория назначения (%s) не соответствует текущей (%s)' % (fileName, destInfis, self._orgInfis))
                return False

            if zipfile.is_zipfile(fileName):
                zipFile = zipfile.ZipFile(fileName, 'r')
                zipItems = zipFile.namelist()
                if not zipItems:
                    raise Exception(u'oms-архив "%s" пуст' % fileName)
                docFile = zipFile.open(zipItems[0])
            else:
                docFile = open(fileName, 'r')

            self.processDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))),
                                 sourceInfis,
                                 year, accInfo)

            self.logger().info(u'Импорт окончен %s\nОбновлено записей: %s' % (QtCore.QTime.currentTime().toString('hh:mm'), accInfo['countUpdate']))

        except Exception, e:
            self.logger().warning(u'Не удалось импортировать файл "%s" (%s)' % (fileName, e.message))
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

        return True


    def processDocument(self, document, sourceInfis, year, accInfo):
        """Анализирует и импортирует DOM-документ.

        :param document: документ, подлежащий анализу и импорту (QDomDocument)
        :param sourceInfis: инфис тер. фонда, предоставившего данные
        :param year: год формирования данного документа
        :return: True в случае успеха и False в ином случае
        """
        self.nextPhase(document.elementsByTagName('SLUCH').length(), u'Обработка файла')

        rootElement = self.getElement(document, 'ZL_LIST', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'ZGLV', isRequired=True)
        if not headerElement:
            return False


        if not self.parseHeaderElement(headerElement, sourceInfis):
            return False

        self._db.transaction(checkIsInit=True)
        try:
            accountElement = self.getElement(rootElement, 'SCHET', isRequired=True)
            self.processAccountElement(accountElement, sourceInfis, year, accInfo)

            entityElement = accountElement.nextSiblingElement('ZAP')
            while not entityElement.isNull():
                self.processEntity(entityElement, accInfo)
                entityElement = entityElement.nextSiblingElement('ZAP')

            self._db.commit()
        except Exception, e:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True


    def parseHeaderElement(self, headerElement, sourceInfis):
        """Анализирует заголовочный узел импортируемого документа.
        Производит проверку ОКАТО фондов отправления и назначения.

        :param headerElement: DOM-узел заголовочных данных (<ZGLV>).
        :param sourceInfis: не используется
        :return: True в случае успеха и False в ином случае
        """
        targetOKATO = self.formatOKATO(self.getElementValue(headerElement,
                                                            'OKATO_OMS',
                                                            isRequired=True),
                                       2)
        if targetOKATO != self._currentOKATO:
            self.logger().warning(u'Целевой ОКАТО (OKATO_OMS) {%s} файла не соответствует ОКАТО текущего ТФ {%s}' % (targetOKATO, self._currentOKATO))
            return False

        return True


    def processAccountElement(self, accountElement, sourceInfis, year, accInfo):
        """Обрабатывает узел с описанием импортируемого счета.

        :param accountElement: узел с описанием импортируемого счета.
        :param sourceInfis: инфис код фонда, приславшего данные
        :param year: год счета
        :param accInfo: словарь для сохранения некоторых данных по счету.
        :return: результат обработки (True или False)
        :raise Exception:
        """
        contractId = self.getContractId(sourceInfis, year)
        if not contractId:
            return False

        mekErrorList = []

        accNumber = self.getElementValue(accountElement, 'NSCHET', isRequired=True, mekErrorList=mekErrorList)
        accExposeDateString = self.getElementValue(accountElement, 'DSCHET', isRequired=True, mekErrorList=mekErrorList)
        accExposeDate = self.convertValue(accExposeDateString, 'date')

        accInfo.setdefault('mekErrorList', []).extend(mekErrorList)

        tableAccount = self._db.table('Account')
        recordAccount = self._db.getRecordEx(tableAccount,
                                             '*',
                                             [tableAccount['number'].eq(accNumber),
                                              tableAccount['exposeDate'].eq(accExposeDate),
                                              'YEAR(%s) = %s' % (tableAccount['settleDate'], year),
                                              'Account.date'])

        if not recordAccount:
            raise Exception(u'Счёт %s от %s не найден' % (accNumber, accExposeDateString))

        recordAccount.setValue('sum', toVariant(self.getElementValue(accountElement, 'SUMMAV', isRequired=True)))
        recordAccount.setValue('payedSum', toVariant(self.getElementValue(accountElement, 'SUMMAP', isRequired=True)))
        recordAccount.setValue('refusedSum', toVariant(self.getElementValue(accountElement, 'SANK_MEK')))
        self._db.updateRecord(tableAccount.name(), recordAccount)
        accInfo['countUpdate'] += 1

        accInfo['year'] = year
        accInfo['number'] = accNumber
        accInfo['exposeDate'] = accExposeDate


        return True


    def processEntity(self, entityElement, accInfo):
        """Обрабывает узел с данными о случаях обращения конкретного пациента.

        :param entityElement: узел с данными о случаях обращения конкретного пациента (<ZAP>).
        :param accInfo: словарь с данными по обрабатываемому счету
        :return: результат обработки (True или False)
        :raise Exception:
        """
        entityKey = self.getElementValue(entityElement, 'N_ZAP', isRequired=True)
        if not entityKey:
            return False

        self._db.transaction()
        try:
            MEKErrorList = []
            eventElement = self.getElement(entityElement, 'SLUCH', isRequired=True, mekErrorList=MEKErrorList)
            processedEventKeys = []
            while not eventElement.isNull():
                eventKey = self.getElementValue(eventElement, 'IDCASE', isRequired=True, mekErrorList=MEKErrorList)
                if eventKey and eventKey not in processedEventKeys:
                    self.processAccountItem(eventKey, eventElement, accInfo, MEKErrorList)
                    processedEventKeys.append(eventKey)
                eventElement = eventElement.nextSiblingElement('SLUCH')
                self.nextPhaseStep()
            self._db.commit()
        except Exception, e:
            self._db.rollback()
            self.onException()
            self.logger().warning(u'Не удалось обработать запись N_ZAP=%s (%s)' % (entityKey, e.message))
            return False
        if self.isAbort:
            raise Exception(u'Прервано пользователем')
        return True

    def processAccountItem(self, eventKey, eventElement, accInfo, MEKErrorList):

        eventId = self.getElementValue(eventElement, 'NHISTORY', isRequired=True, mekErrorList=MEKErrorList)
        oplata = forceInt(self.getElementValue(eventElement, 'OPLATA', isRequired=True, mekErrorList=MEKErrorList))

        tableAccount = self._db.table('Account')
        tableAccountItem = self._db.table('Account_Item')
        tableEvent = self._db.table('Event')

        queryTable = tableAccount.innerJoin(tableAccountItem, tableAccountItem['master_id'].eq(tableAccount['id']))
        queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAccountItem['event_id']))

        recordList = self._db.getRecordList(queryTable, 'Account_Item.*', [tableAccount['number'].eq(accInfo['number']),
                                                                           tableAccount['exposeDate'].eq(accInfo['exposeDate']),
                                                                           'YEAR(%s) = %s' % (tableAccount['settleDate'], accInfo['year']),
                                                                           tableEvent['id'].eq(eventId)])

        recordEvent = self._db.getRecordEx(tableEvent, 'Event.*', tableEvent['id'].eq(eventId))

        externalId = forceStringEx(recordEvent.value('externalId'))
        partsExternalId = externalId.strip().split('#')
        if len(partsExternalId) == 0:
            partsExternalId = [""] * 3
        if len(partsExternalId) == 1:
            partsExternalId.extend([""] * 2)
        partsExternalId[2] = eventKey

        recordEvent.setValue('externalId', toVariant("#".join([forceStringEx(part) for part in partsExternalId])))
        # self._db.updateRecord(tableEvent.name(), recordEvent)


        sankElement = self.getElement(eventElement, 'SANK', isRequired=False)
        for record in recordList:
            # noinspection PyArgumentList
            record.setValue('date', toVariant(QtCore.QDate.currentDate()))
            accountId = forceRef(record.value('master_id'))
            payStatusMask = self.getPayStatusMask(accountId)
            if oplata > 1:
                refuseTypeId = self.getPayRefuseId(self.getElementValue(sankElement, 'S_OSN', isRequired=True, mekErrorList=MEKErrorList))
                record.setValue('refuseType_id', toVariant(refuseTypeId))
                record.setValue('number', toVariant(u'Отказ по МЭК'))
                updateDocsPayStatus(record, payStatusMask, CPayStatus.refusedBits)
            elif sankElement.isNull():
                record.setValue('refuseType_id', toVariant(None))
                record.setValue('number', toVariant(u'Оплачено'))
                updateDocsPayStatus(record, payStatusMask, CPayStatus.payedBits)
            self._db.updateRecord(tableAccountItem.name(), record)
            accInfo['countUpdate'] += 1

    def getPayStatusMask(self, accountId):
        result = self.mapAccountIdToPayStatusMask.get(accountId, None)
        if result is None:
            tblAccount = self._db.table('Account')
            tblContract = self._db.table('Contract')
            tbl = tblAccount.join(tblContract, tblContract['id'].eq(tblAccount['contract_id']))
            record = self._db.getRecordEx(tbl, tblContract['finance_id'], tblAccount['id'].eq(accountId))
            if record:
                result = getPayStatusMask(forceRef(record.value('finance_id')))
            self.mapAccountIdToPayStatusMask[accountId] = result
        return result


# noinspection PyShadowingBuiltins
class CImport85MTR_Refused(QtGui.QDialog):
    InitState = 0
    ImportState = 1

    def __init__(self, db, contractId, parent = None):
        # noinspection PyArgumentList
        super(CImport85MTR_Refused, self).__init__(parent = parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = CImportR85MTREngine_Refused(db, contractId, progressInformer=self._pi)
        self._engine.setUserConfirmationFunction(self.userConfirmation)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()


    def setParams(self, params):
        if isinstance(params, dict):
            fileName = forceStringEx(getPref(params, 'inputFile', u''))
            if os.path.isfile(fileName):
                self.edtFileName.setText(fileName)


    def engine(self):
        return self._engine


    def params(self):
        params = {}
        setPref(params, 'inputFile', forceStringEx(self.edtFileName.text()))
        return params


    @property
    def currentState(self):
        return self._currentState


    @currentState.setter
    def currentState(self, value):
        if value in [self.InitState, self.ImportState]:
            self._currentState = value
            self.onStateChanged()

    def onStateChanged(self):
        self.btnNextAction.setText(self._actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ImportState)
        self.gbInit.setEnabled(self.currentState == self.InitState)
        self.gbImport.setEnabled(self.currentState == self.ImportState)
        QtCore.QCoreApplication.processEvents()

    # noinspection PyAttributeOutsideInit
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtFileName = QtGui.QLineEdit()
        self.edtFileName.setReadOnly(True)
        lineLayout.addWidget(self.edtFileName)
        self.btnBrowseFile = QtGui.QToolButton()
        # noinspection PyUnresolvedReferences
        self.btnBrowseFile.clicked.connect(self.onBrowseFileClicked)
        lineLayout.addWidget(self.btnBrowseFile)
        gbLayout.addLayout(lineLayout)
        self.gbInit.setLayout(gbLayout)
        layout.addWidget(self.gbInit)

        # import block
        self.gbImport = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self._pi.progressChanged.connect(self.progressBar.setProgress)
        gbLayout.addWidget(self.progressBar)
        self.gbImport.setLayout(gbLayout)
        layout.addWidget(self.gbImport)

        # log block
        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        self._loggerHandler.logged.connect(self.logInfo.append)

        # buttons block
        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        # noinspection PyUnresolvedReferences
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        # noinspection PyUnresolvedReferences
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()

    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Импорт. Крым. МежТер. Возвраты', context))
        self.gbInit.setTitle(forceTr(u'Параметры импорта', context))

        self.gbImport.setTitle(forceTr(u'Импорт', context))

        self._actionNames = {self.InitState: forceTr(u'Импорт',context),
                             self.ImportState: forceTr(u'Прервать', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))

    def userConfirmation(self, title, message):
        # noinspection PyCallByClass,PyTypeChecker
        return QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(self,
                                                                   title,
                                                                   message,
                                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                   QtGui.QMessageBox.No)

    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ImportState
            countUpdate = 0
            try:
                self.logInfo.append(u'Импорт начат %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
                self.logInfo.update()
                countUpdate = self._engine.process(forceStringEx(self.edtFileName.text()))
            except Exception, e:
                self.currentState = self.InitState
                raise
            finally:
                self.logInfo.append(u'Импорт окончен %s\nОбновлено записей %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss'), countUpdate))
                self.logInfo.update()
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self._engine.abort()
            self.currentState = self.InitState
        self.onStateChanged()

    # noinspection PyMethodMayBeStatic
    def canClose(self):
        return True

    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()

    def done(self, result):
        if self.canClose():
            super(CImport85MTR_Refused, self).done(result)

    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def onBrowseFileClicked(self):
        # noinspection PyTypeChecker,PyCallByClass
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                       u'Выберите импортируемый файл',
                                                                       self.edtFileName.text(),
                                                                       u'Файлы (*.xml *.oms)'))
        if os.path.isfile(fileName):
            self.edtFileName.setText(fileName)


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

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

    w = CImport85MTR_Refused(QtGui.qApp.db, 66)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()