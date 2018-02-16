# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   13.05.2015
'''

import logging
import os
import zipfile

from PyQt4 import QtCore, QtGui
from Exchange.R85.ExchangeEngine import CExchangeImportR85Engine
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer

from library.Utils import getPref, getClassName, setPref, forceRef, forceStringEx, toVariant, \
    CLogHandler, forceTr
from library.XML.XMLHelper import CXMLHelper
from library.database import CDatabase



def importR85ERZCentral(widget):
    importWindow = CImportDialog(QtGui.qApp.db)
    params = getPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), {})
    importWindow.setParams(params)
    importWindow.engine().setLastExceptionHandler(QtGui.qApp.logCurrentException)
    importWindow.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, getClassName(importWindow), importWindow.params())


#atronah: В идеале должно работать так:
# С помощью "умного" парсера XML пробегаемся первый раз по всему файлу (желательно без полной его загрузки в оперативку),
# проверяем на наличие данных, необходимых для создания счета и элементов и запоминаем их позицию (или ссылки на них).
# Все записи (sluch), не проедшие проверку исключаются из дальнейшего анализа
# (и, возможно, помечаются отказанными либо в файле либо в доп. месте в базе).
# Второй пробег определяет, какие данные необходимо закэшировать (чтобы потом исключить чтение из базы)
# (серии+номера полисов/документов, коды ЛПУ, коды назначений событий и видов помощи и т.п.) ....
# После формируются/обновляются кэши. Третий пробег анализирует данные порционно (например, по ZAP) и, используя кэши,
# формирует порцию данных для записи в базу (записи в несколько этапов, так как потребуется получать id-шки
# и дозаписывать их в другие данные перед их вставкой).

# noinspection PyShadowingBuiltins
class CImportR85ERZCentralEngine(CExchangeImportR85Engine):
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

    def __init__(self, db, progressInformer = None):
        super(CImportR85ERZCentralEngine, self).__init__(progressInformer)
        self._db = db if isinstance(db, CDatabase) else None

        self._logger.setLevel(logging.INFO)

        self._policyTypeId = None # Тип полиса для всех создаваемых полисов (ОМС)

        self._insurerCache = {}

        self._policyKindIdByCode = {}

        self._mapRemoteIdToLocal = {}

        self.nAdded = 0
        self.nUpdated = 0
        self.nSkipped = 0


    def preloadInsurerCache(self):
        """Предварительная загрузка данных по Страховым компаниям.
        Формирует (обновляет) кэш страховых элементами вида *"Инфис код страховой"* = *ID страховой*


        """
        tableInsurer = self._db.table('Organisation')
        self._insurerCache.update([((forceStringEx(record.value('OGRN')), forceStringEx(record.value('OKATO'))), forceRef(record.value('id')))
                                   for record in self._db.getRecordList(tableInsurer,
                                                                        cols=[tableInsurer['id'],
                                                                              tableInsurer['OGRN'],
                                                                              tableInsurer['OKATO']],
                                                                        where=[tableInsurer['isInsurer'].eq(1)],
                                                                        # limit=1000,
                                                                        group='OGRN, OKATO')
                                   ])



    def clearAll(self):
        """Очищает все временные хранилища данных.
        """
        self._mapRemoteIdToLocal.clear()

        self._policyKindIdByCode.clear()

        self._insurerCache.clear()

        self._policyTypeId = None

        self.nAdded = 0
        self.nUpdated = 0
        self.nSkipped = 0



    # ---- getters
    def getElement(self, parentNode, elementName, isRequired=False, mekErrorList=None):
        """Получение DOM-элемента по имени с проверкой его необходимости и заполнением лога ошибок.
        Пытается найти элемент (QDomElement) с именем *elementName* в узле *parentNode*. Если элемент не был найден,
         но при этом указан, как обязательный, то в *mekErrorList* заносятся данные об ошибке.

        :param parentNode: родительский DOM-узел (QDomNode), в котором необходимо искать элемент
        :param elementName: имя искомого элемента
        :param isRequired: искомый элемент является обязательным и его отсутствие - признак ошибки
        :param mekErrorList: список для занесения в него возможных ошибок
        :return: найденный элемент
        """
        element = parentNode.firstChildElement(elementName)
        if element.isNull() and isRequired:
            self.logger().warning(u'Ошибка формата файла. Ожидаемый узел: "%s" не был найден [%s:%s]' % (elementName, parentNode.lineNumber(), parentNode.columnNumber()))
        return element



    def getPolicyKindByCode(self, code):
        """Возвращает ID вида полиса {rbPolicyKind}, соответствующего коду *code*
        Ищет в кеше или базе данных ID причины отказа, код которой соответствует указанному в *code*,
        после чего возвращает и кеширует это значение.
        Поиск производится по полю rbPolicyKind.federalCode.

        :param code: код вида полиса.
        :return: ID вида полиса {rbPolicyKind}
        """
        if not self._policyKindIdByCode.has_key(code):
            self._policyKindIdByCode[code] = forceRef(self._db.translate('rbPolicyKind', 'federalCode', code, 'id'))
        return self._policyKindIdByCode[code]



    # ---- processing


    def process(self, reqFileName, respFileName):
        """Запускает процесс импорта.

        :param reqFileName: имя исходного файла для синхронизации
        :param respFileName: имя файла с ответом
        :return: True
        """
        self.isAbort = False
        self.phaseReset(2)
        self.clearAll()
        self.preloadInsurerCache()
        self._policyTypeId = forceRef(self._db.translate('rbPolicyType', 'code', '1', 'id'))
        self.processReqFile(reqFileName)
        self.processRespFile(respFileName)
        if self.isAbort:
            self.logger().info(u'Импорт прерван пользователем.')
        else:
            self.logger().info(u'Добавлено: %s, обновлено: %s, пропущено: %s.' % (self.nAdded, self.nUpdated, self.nSkipped))
        return True


    # def parseFileName(self, fileName):
    #     """
    #     Вычленяет из имени файла важную информацию.
    #     Предполагается, что имя файла представлено в формате:
    #         R + код территориального фонда обязательного медицинского страхования, выставившего счет
    #         + код территориального фонда обязательного медицинского страхования, которому предъявлен счет
    #         + две последние цифры года
    #         + четырехзначный порядковый номер представления основной части в текущем году
    #     :param fileName: имя обрабатываемого файла
    #     :return: isOk, isUpdate, sourceInfis, destInfis, year, number
    #     """
    #     try:
    #         name = os.path.splitext(os.path.basename(fileName))[0].lower()
    #         if name[0] in ['r', 'd'] and len(name) == 11:
    #             return True, name.startswith('d'), forceStringEx(name[1:3]), forceStringEx(name[3:5]), 2000 + int(name[5:7], 10), int(name[7:11], 10)
    #     except Exception, e:
    #         self.logger().critical(u'Некорректное имя файла "%s" (%s)' % (fileName, e.message))
    #         self.onException()
    #
    #     return False, False, u'', u'', None, None


    def processReqFile(self, fileName):
        """Импортирует указанный файл

        :param fileName: имя файла для импорта (R|D)<SS><DD><YY><NNNN>.(oms|xml) (описание имени см в `parseFileName`)
        :return: True, если импорт файла прошел успешно, False в ином случа
        :raise: Exception("архив пуст"), если архив пуст
        """
        docFile = None
        try:
            if zipfile.is_zipfile(fileName):
                zipFile = zipfile.ZipFile(fileName, 'r')
                zipItems = zipFile.namelist()
                if not zipItems:
                    raise Exception(u'zip-архив "%s" пуст' % fileName)
                docFile = zipFile.open(zipItems[0])
            else:
                docFile = open(fileName, 'r')

            self.processReqDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))))


        except Exception, e:
            self.logger().warning(u'Не удалось импортировать файл "%s" (%s)' % (fileName, e.message))
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

        return True

    def processReqDocument(self, document):
        """Анализирует и импортирует DOM-документ.

        :param document: документ, подлежащий анализу и импорту (QDomDocuement)
        :return: True в случае успеха и False в ином случае
        """
        self.nextPhase(document.elementsByTagName('QBP_ZP1').length(), u'Обработка файла персональных данных')
        # self.clearDocumentCache()
        # self.updateRBCaches(document)
        # self.updateMKBCache(document)

        self._mapRemoteIdToLocal.clear()

        rootElement = self.getElement(document, 'UPRMessageBatch', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'BHS', isRequired=True)
        if not headerElement:
            return False


        # if not self.parseHeaderElement(headerElement):
        #     return False


        entityElement = headerElement.nextSiblingElement('QBP_ZP1')
        while not entityElement.isNull():
            if self.isAbort:
                return False
            mshElement = self.getElement(entityElement, 'MSH', isRequired=True)
            qpdElement = self.getElement(entityElement, 'QPD', isRequired=True)
            remoteId = self.getElementValue(mshElement, 'MSH.10', isRequired=True)

            if remoteId:
                self.processRegData(qpdElement, remoteId)
            self.nextPhaseStep()
            entityElement = entityElement.nextSiblingElement('QBP_ZP1')

        return True

    def processRegData(self, qpdElement, remoteId):
        credentialsElement = self.getElement(qpdElement, 'QPD.6', isRequired=True)
        identElement = self.getElement(qpdElement, 'QPD.6')
        snils = ''
        if self.getElementValue(identElement, 'CX.5') == 'PEN':
            snils = self.getElementValue(identElement, 'CX.1', isRequired=True)
        lastName = self.getElementValue(
            self.getElement(credentialsElement, 'XPN.1', isRequired=True),
            'FN.1', isRequired=True)
        firstName = self.getElementValue(credentialsElement, 'XPN.2', isRequired=True)
        patrName = self.getElementValue(credentialsElement, 'XPN.3')
        birthDate = QtCore.QDate.fromString(self.getElementValue(qpdElement, 'QPD.7'), QtCore.Qt.ISODate)
        sex = self.getElementValue(qpdElement, 'QPD.8')

        tblClient = self._db.table('Client') # TODO: вынести в атрибуты класса - не айс создавать этот объект на каждом пациенте
        cond = [
            tblClient['lastName'].eq(lastName),
            tblClient['firstName'].eq(firstName),
            tblClient['patrName'].eq(patrName),
            tblClient['birthDate'].dateEq(birthDate),
            tblClient['sex'].eq(sex)
                ]

        clientIdList = self._db.getIdList(tblClient, where=cond)
        if len(clientIdList) > 1 and snils:
            # Выборка не однозначна, добавляем проверку по СНИЛС
            cond.append(tblClient['SNILS'].eq(snils))
        elif not clientIdList:
            if snils:
                # Ничего не найдено, пробуем найти по СНИЛС
                cond = [tblClient['SNILS'].eq(snils)]
            else:
                # Ничего не найдено и нет других опций. Завершаем обработку
                self._mapRemoteIdToLocal[remoteId] = None
                return
        else:
            # Найден подходящий пациент. Завершаем обработку.
            self._mapRemoteIdToLocal[remoteId] = clientIdList[0]
            return

        clientIdList = self._db.getIdList(tblClient, where=cond)
        self._mapRemoteIdToLocal[remoteId] = clientIdList[0] if clientIdList else None
        return

    def processRespFile(self, fileName):
        """Импортирует указанный файл

        :param fileName: имя файла для импорта (R|D)<SS><DD><YY><NNNN>.(oms|xml) (описание имени см в `parseFileName`)
        :return: True, если импорт файла прошел успешно, False в ином случа
        :raise: Exception("архив пуст"), если архив пуст
        """
        docFile = None
        try:
            if zipfile.is_zipfile(fileName):
                zipFile = zipfile.ZipFile(fileName, 'r')
                zipItems = zipFile.namelist()
                if not zipItems:
                    raise Exception(u'zip-архив "%s" пуст' % fileName)
                docFile = zipFile.open(zipItems[0])
            else:
                docFile = open(fileName, 'r')

            self.processRespDocument(CXMLHelper.loadDocument(QtCore.QString(docFile.read().decode(self.encoding))))


        except Exception, e:
            self.logger().warning(u'Не удалось импортировать файл "%s" (%s)' % (fileName, e.message))
            self.onException()
            return False
        finally:
            if docFile:
                docFile.close()

        return True

    def processRespDocument(self, document):
        """Анализирует и импортирует DOM-документ.

        :param document: документ, подлежащий анализу и импорту (QDomDocuement)
        :return: True в случае успеха и False в ином случае
        """
        self.nextPhase(document.elementsByTagName('RSP_ZK1').length(), u'Обработка файла полисов')
        # self.clearDocumentCache()
        # self.updateRBCaches(document)
        # self.updateMKBCache(document)

        rootElement = self.getElement(document, 'UPRMessageBatch', isRequired=True)
        if not rootElement:
            return False

        headerElement = self.getElement(rootElement, 'BHS', isRequired=True)
        if not headerElement:
            return False


        # if not self.parseHeaderElement(headerElement):
        #     return False


        self._db.transaction(checkIsInit=True)
        try:

            entityElement = headerElement.nextSiblingElement('RSP_ZK1')
            while not entityElement.isNull():
                if self.isAbort:
                    self._db.rollback()
                    return
                msaElement = self.getElement(entityElement, 'MSA', isRequired=True)
                rspElement = self.getElement(entityElement, 'RSP_ZK1.QUERY_RESPONSE')
                remoteId = self.getElementValue(msaElement, 'MSA.2', isRequired=True)
                clientId = self._mapRemoteIdToLocal.get(remoteId, None)
                if clientId and not rspElement.isNull():
                    self.processPolicyElement(rspElement, clientId, remoteId)
                elif not clientId:
                    self.logger().warning(u'Не удалось найти пациента для записи %s' % remoteId)
                    self.nSkipped += 1
                self.nextPhaseStep()
                entityElement = entityElement.nextSiblingElement('RSP_ZK1')

            self._db.commit()
        except Exception, e:
            self._db.rollback()
            raise
        finally:
            self.finishPhase()

        return True

    # def refuseClient(self, clientId):
    #     db = self._db
    #
    #     stmt = u'UPDATE ' \
    #            u'Account_Item ai ' \
    #            u'INNER JOIN Account a ON a.id = ai.master_id ' \
    #            u'INNER JOIN Event e ON e.id = ai.event_id ' \
    #            u'INNER JOIN rbPayRefuseType prt ON prt.code = \'5.2.3.\' ' \
    #            u'SET ai.number = \'Отказ по МЭК\', ai.refuseType_id = prt.id, ai.note = IF(ai.note, ai.note, \'цс ерз\') ' \
    #            u'WHERE MONTH(a.settleDate) IN (4, 5) and e.client_id = %d' % clientId
    #
    #     db.query(stmt)



    def processPolicyElement(self, rspElement, clientId, remoteId):
        isFirst = False
        inElement = self.getElement(rspElement, 'IN1', isRequired=True)
        while not isFirst or inElement.isNull():
            if self.getElementValue(inElement, 'IN1.1', isRequired=True) == '1':
                isFirst = True
            else:
                inElement = inElement.nextSiblingElement('IN1')

        if inElement.isNull():
            # self.refuseClient(clientId)
            self.logger().error(u'Не найден сегмент с актуальными полисными данными для записи %s' % remoteId)
            self.nSkipped += 1
            return

        insurerOGRN = ''
        in3 = self.getElement(inElement, 'IN1.3', isRequired=True)
        if self.getElementValue(in3, 'CX.5', isRequired=True) == 'NII':
            insurerOGRN = self.getElementValue(in3, 'CX.1', isRequired=True)

        policyBegDate = QtCore.QDate.fromString(self.getElementValue(inElement, 'IN1.12', isRequired=True), QtCore.Qt.ISODate)
        policyEndDate = QtCore.QDate.fromString(self.getElementValue(inElement, 'IN1.13', isRequired=True), QtCore.Qt.ISODate)
        insurerOKATO = self.getElementValue(inElement, 'IN1.15', isRequired=True)

        policyKind = self.getElementValue(inElement, 'IN1.35', isRequired=True)
        policySN = self.getElementValue(inElement, 'IN1.36', isRequired=True)

        policySerial = ''
        if policyKind == u'Х':
            return
        elif policyKind == u'С':
            policySNParts = policySN.split(u' № ')
            if len(policySNParts) == 2:
                policySerial, policyNumber = policySNParts
            else:
                policyNumber = policySNParts[0]
        else:
            policyNumber = policySN

        policyKindId = self.getPolicyKindByCode({u'С': 1, u'В': 2, u'П': 3, u'Э': 4, u'К': 5}.get(policyKind, 3))

        tblClientPolicy = self._db.table('ClientPolicy')
        tblInsurer = self._db.table('Organisation')
        cond = [tblClientPolicy['client_id'].eq(clientId),
                tblClientPolicy['deleted'].eq(0),
                tblClientPolicy['policyType_id'].eq(self._policyTypeId),
                tblClientPolicy['number'].eq(policyNumber),
                tblInsurer['OKATO'].eq(insurerOKATO)]
        cols = [tblClientPolicy['id'],
                tblClientPolicy['serial'],
                tblClientPolicy['number'],
                tblClientPolicy['policyType_id'],
                tblClientPolicy['policyKind_id'],
                tblClientPolicy['begDate'],
                tblClientPolicy['endDate'],
                tblClientPolicy['insurer_id'],
                #tblInsurer['OGRN'],
                ]

        policyRecord = self._db.getRecordEx(table=tblClientPolicy.innerJoin(tblInsurer, tblInsurer['id'].eq(tblClientPolicy['insurer_id'])),
                             cols=cols,
                             where=cond)
        insurerRecord = self._db.getRecordEx(tblInsurer,
                                             tblInsurer['id'],
                                             where=[tblInsurer['OGRN'].eq(insurerOGRN),
                                                    tblInsurer['OKATO'].eq(insurerOKATO),
                                                    tblInsurer['isInsurer'].eq(1),
                                                    tblInsurer['deleted'].eq(0)])
        if not insurerRecord:
            insurerRecord = self._db.getRecordEx(tblInsurer,
                                                 tblInsurer['id'],
                                                 where=[tblInsurer['OKATO'].eq(insurerOKATO),
                                                        tblInsurer['isInsurer'].eq(1),
                                                        tblInsurer['deleted'].eq(0)])
        if not policyRecord:
            newPolicyRecord = tblClientPolicy.newRecord()
            newPolicyRecord.setValue('client_id', toVariant(clientId))
            newPolicyRecord.setValue('serial', toVariant(policySerial))
            newPolicyRecord.setValue('number', toVariant(policyNumber))
            newPolicyRecord.setValue('policyType_id', toVariant(self._policyTypeId))
            newPolicyRecord.setValue('policyKind_id', toVariant(policyKindId))
            newPolicyRecord.setValue('begDate', toVariant(policyBegDate))
            newPolicyRecord.setValue('endDate', toVariant(policyEndDate))
            newPolicyRecord.setValue('note', toVariant('erz_central'))

            if insurerRecord:
                newPolicyRecord.setValue('insurer_id', insurerRecord.value('id'))
            self._db.insertRecord(tblClientPolicy, newPolicyRecord)
            self.nAdded += 1

        else:
            #TODO: craz: обновлять записи только если есть различие, не плодить лишние запросы
            policyRecord.setValue('policyKind_id', toVariant(policyKindId))
            policyRecord.setValue('begDate', toVariant(policyBegDate))
            policyRecord.setValue('endDate', toVariant(policyEndDate))
            #TODO: craz: проверять СМО по ОГРН
            self._db.updateRecord(tblClientPolicy, policyRecord)

            self.nUpdated += 1


# noinspection PyShadowingBuiltins
class CImportDialog(QtGui.QDialog):
    InitState = 0
    ImportState = 1

    def __init__(self, db, parent = None):
        super(CImportDialog, self).__init__(parent = parent)
        self._db = db
        self._pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self._engine = CImportR85ERZCentralEngine(db, progressInformer=self._pi)
        self._engine.setUserConfirmationFunction(self.userConfirmation)
        self._loggerHandler = CLogHandler(self._engine.logger(), self)
        self._loggerHandler.setLevel(logging.INFO)
        self._currentState = self.InitState

        self.setupUi()

        self.onStateChanged()


    def setParams(self, params):
        if isinstance(params, dict):
            reqFileName = forceStringEx(getPref(params, 'reqFile', u''))
            if os.path.isfile(reqFileName ):
                self.edtReqFileName.setText(reqFileName )
            respFileName = forceStringEx(getPref(params, 'respFile', u''))
            if os.path.isfile(respFileName):
                self.edtRespFileName.setText(respFileName)


    def engine(self):
        return self._engine


    def params(self):
        params = {}
        setPref(params, 'reqFile', forceStringEx(self.edtReqFileName.text()))
        setPref(params, 'respFile', forceStringEx(self.edtRespFileName.text()))
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
        # self.btnSave.setEnabled(bool(self._engine.documents))
        QtCore.QCoreApplication.processEvents()


    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        # init block
        self.gbInit = QtGui.QGroupBox()
        gbLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtReqFileName = QtGui.QLineEdit()
        self.edtReqFileName.setReadOnly(True)
        lineLayout.addWidget(self.edtReqFileName)
        self.btnBrowseReqFile = QtGui.QToolButton()
        self.btnBrowseReqFile.clicked.connect(self.onBrowseReqFileClicked)
        lineLayout.addWidget(self.btnBrowseReqFile)
        gbLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        self.edtRespFileName = QtGui.QLineEdit()
        self.edtRespFileName.setReadOnly(True)
        lineLayout.addWidget(self.edtRespFileName)
        self.btnBrowseRespFile = QtGui.QToolButton()
        self.btnBrowseRespFile.clicked.connect(self.onBrowseRespFileClicked)
        lineLayout.addWidget(self.btnBrowseRespFile)
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
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranslateUi()


    # noinspection PyAttributeOutsideInit
    def retranslateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Импорт. Крым. ЦС ЕРЗ.', context))
        self.gbInit.setTitle(forceTr(u'Параметры импорта', context))

        self.gbImport.setTitle(forceTr(u'Импорт', context))

        self._actionNames = {self.InitState: forceTr(u'Импорт',context),
                             self.ImportState: forceTr(u'Прервать', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))


    def userConfirmation(self, title, message):
        # noinspection PyTypeChecker,PyCallByClass
        return QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(self,
                                                                   title,
                                                                   message,
                                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                   QtGui.QMessageBox.No)



    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ImportState
            try:
                self._engine.process(forceStringEx(self.edtReqFileName.text()),
                forceStringEx(self.edtRespFileName.text()))
            except Exception, e:
                self.currentState = self.InitState
                raise
            self.currentState = self.InitState

        elif self.currentState == self.ImportState:
            self._engine.abort()
            self.currentState = self.InitState
        self.onStateChanged()


    # noinspection PyMethodMayBeStatic
    def canClose(self):
        return True
        # not self._engine.documents or \
        #        QtGui.QMessageBox.warning(self,
        #                                  u'Внимание',
        #                                  u'Остались несохраненные файлы выгрузок,\n'
        #                                  u'которые будут утеряны.\n'
        #                                  u'Уверены, что хотить выйти из экспорта?\n',
        #                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        #                                  QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes


    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()


    def done(self, result):
        if self.canClose():
            super(CImportDialog, self).done(result)



    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()


    @QtCore.pyqtSlot()
    def onBrowseReqFileClicked(self):
        # noinspection PyTypeChecker,PyCallByClass
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                   u'Укажите файл с персональными данными',
                                                                   self.edtReqFileName.text()))
        if os.path.isfile(fileName):
            self.edtReqFileName.setText(fileName)

    @QtCore.pyqtSlot()
    def onBrowseRespFileClicked(self):
        # noinspection PyTypeChecker,PyCallByClass
        fileName = forceStringEx(QtGui.QFileDialog.getOpenFileName(self,
                                                                   u'Укажите файл с полисными данными',
                                                                   self.edtRespFileName.text()))
        if os.path.isfile(fileName):
            self.edtRespFileName.setText(fileName)

