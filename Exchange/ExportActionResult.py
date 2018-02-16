#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Accounting.Utils import CContractTreeModel, getContractInfo
from Events.Action import CActionType
from Events.Utils import getWorkEventTypeFilter
from Ui_ExportActionResult_Wizard_1 import Ui_ExportActionResult_Wizard_1
from Ui_ExportActionResult_Wizard_2 import Ui_ExportActionResult_Wizard_2
from Utils import *
from library.DialogBase import CConstructHelperMixin
from library.SendMailDialog import sendMail
from library.subst import substFields


def ExportActionResult(parent = None):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionResultFileName', ''))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionResultCompressRAR', 'False'))
    dlg = CExportActionResult(fileName, compressRAR,  parent)
    dlg.page(1).addDateToFileName = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionResultAddDate', 'False'))
    dlg.page(1).addContractNumberToFileName = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionResultAddContractNumber', 'False'))
    dlg.page(1).verboseLog = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionResultVerboseLog', 'False'))

    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportActionResultFileName'] = toVariant(
                                                                            dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportActionResultCompressRAR'] = toVariant(
                                                                            dlg.compressRAR)
    QtGui.qApp.preferences.appPrefs['ExportActionResultAddDate'] = toVariant(
                                                                             dlg.page(1).addDateToFileName)
    QtGui.qApp.preferences.appPrefs['ExportActionResultAddContractNuumber'] = toVariant(
                                                                             dlg.page(1).addContractNumberToFileName)
    QtGui.qApp.preferences.appPrefs['ExportActionResultVerboseLog'] = toVariant(
                                                                             dlg.page(1).verboseLog)


def getMaxQuerySize():
    u""" Возвращает максимальную длину запроса в байтах для !MySQL!"""

    result = None
    db = QtGui.qApp.db

    if db.db.driverName() == 'QMYSQL':
        stmt = 'SHOW VARIABLES LIKE \'max_allowed_packet\';'
        query = db.query(stmt)

        while (query.next()):
            r = query.record()
            result = forceInt(r.value('max_allowed_packet'))

    return result



class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, contractIdList,  filterEvent=None,  filterAction=None):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._contractIdList = contractIdList
        self._filterEvent = filterEvent
        self._filterAction = filterAction
        self.currentClientId = None
        self.currentEventId = None
        self.clientInfoCache = {}
        self.eventInfoCache = {}
        self.actionPropertyTemplateCodeCache = {}
        self.getActionPropertyTemplateCodeRecursionLevel = 0
        self.db = QtGui.qApp.db
        self.tableEvent  = self.db.table('Event')
        self.querySize = 0 # количество выгружаемых записей

    def getActionPropertyValue(self, id,  typeName):
        u""" Возвращает строку со значением свойства действия"""

        if typeName in ('Text',  'Constructor', u'Жалобы'):
            typeName = 'String'

        if typeName == 'RLS':
            typeName = 'Integer'

        stmt = 'SELECT value FROM ActionProperty_%s WHERE id = %s' % (typeName, id)

        result = ''
        query = self.db.query(stmt)

        while (query.next()):
            record = query.record()
            result = forceString(record.value('value'))

        return result


    def getActionPropertyTemplateCode(self,  id):
        u""" Рекурсивная функция, ограничение по глубине - 30 вызовов.
            При выгрузке кода действия значение следует уточнять:
            класс-группа(ы)-код
            Например: Диагностика//1-1//01 - соответствует действию
            из класса "Диагностика", группы "Лабораторные исследования",
            тип "Холестерин". В качестве разделителей "//" """

        result = self.actionPropertyTemplateCodeCache.get(id,  None)

        if not result:
            record = self.db.getRecordEx('ActionPropertyTemplate', \
                'id, group_id, code',  'id=%d' % (forceInt(id)))
            if record:
                code = forceString(record.value('code'))
                groupId = forceInt(record.value('group_id'))

                if groupId and \
                    self.getActionPropertyTemplateCodeRecursionLevel < 30:
                    self.getActionPropertyTemplateCodeRecursionLevel += 1
                    # Рекурсивный вызов
                    result = u'%s//%s' % (self.getActionPropertyTemplateCode(groupId), code)
                    self.getActionPropertyTemplateCodeRecursionLevel -= 1
                else:
                    result = code

            self.actionPropertyTemplateCodeCache[id] = result

        return result

    def getEventInfo(self,  eventId):
        u""" Запрашивает данные о событие: код и название,
            ответственный, даты начала и выполнения, результат"""

        result = self.eventInfoCache.get(eventId,  None)

        if not result:
            stmt = '''
            SELECT  Event.setDate AS `setDate`,
                        Event.execDate AS `execDate`,
                        rbResult.code AS `result_code`,
                        rbResult.name AS `result_name`,
                        EventType.name AS `name`,
                        EventType.code AS `code`,
                        setPersonInfo.code AS `setPerson_code`,
                        setPersonInfo.name AS `setPerson_name`,
                        execPersonInfo.code AS `execPerson_code`,
                        execPersonInfo.name AS `execPerson_name`
            FROM Event
            LEFT JOIN rbResult ON Event.result_id = rbResult.id
            LEFT JOIN EventType ON Event.eventType_id = EventType.id
            LEFT JOIN vrbPerson setPersonInfo ON setPersonInfo.id = Event.setPerson_id
            LEFT JOIN vrbPerson execPersonInfo ON execPersonInfo.id = Event.execPerson_id
            WHERE Event.id = %d AND Event.deleted = 0
            ''' % eventId

            result = {}
            query = self.db.query(stmt)

            while(query.next()):
                record = query.record()
                for x in ('code','name',  'setDate', 'execDate',  'result_code',
                            'result_name',  'setPerson_code',  'setPerson_name',
                            'execPerson_code',  'execPerson_name'):
                    result[x] = forceString(record.value(x))

            self.eventInfoCache[eventId] = result

        return result


    def getEventIdList(self,  contractIdList,  cond=None):
        stmt = '''
        SELECT  Event.id AS `id`
        FROM Event
        LEFT JOIN EventType ON Event.eventType_id =EventType.id
        '''
        stmt += ' WHERE Event.contract_id in ('+ \
                    ', '.join([str(et) for et in contractIdList])+ \
                    ') AND Event.deleted = 0'

        if cond:
            stmt += ' AND '+cond

        query = self.db.query(stmt)
        result = []
        while query.next():
            result.append(query.value(0).toInt()[0])
        return result


    def createActionQueryList(self,  eventIdList,  cond=None):
        maxQuerySize = getMaxQuerySize()
        result = []

        stmt = '''
        SELECT  Action.id AS `id`,
                    Action.event_id AS `event_id`,
                    Action.setPerson_id,
                    Action.directionDate,
                    Action.status,
                    Action.begDate,
                    Action.endDate,
                    Action.note,
                    Action.office,
                    Action.amount,
                    Action.expose,
                    Action.payStatus,
                    Event.client_id AS `client_id`,
                    ActionType.code AS `actionType_code`,
                    ActionType.name AS `actionType_name`,
                    Organisation.OGRN AS `org_OGRN`,
                    vrbPerson.code AS `person_code`,
                    vrbPerson.name AS `person_name`
        FROM Action
        LEFT JOIN Event ON Action.event_id = Event.id
        LEFT JOIN Organisation ON Event.org_id = Organisation.id
        LEFT JOIN vrbPerson ON Action.person_id = vrbPerson.id
        LEFT JOIN ActionType ON Action.actionType_id =ActionType.id
        '''
        stmtOrderBy = ' ORDER BY client_id, event_id' if not self.parent.parent.includeClientEventInfo else ' ORDER BY event_id'

        if eventIdList:
            # если количество событий очень большое,
            # длина запроса может превысить максимально допустимую
            # надо разбить запрос на несколько.

            strIdList = []
            stmtLen = len(stmt) + len(stmtOrderBy)
            wherePrefix = ' WHERE Action.event_id in ('
            wherePrefixLen = len(wherePrefix)
            whereInfix = ', '
            whereInfixLen = len(whereInfix)
            wherePostfix = ') AND Action.deleted = 0'
            wherePostfixLen = len(wherePostfix)
            filterLen = (len(cond) + len(' AND ')) if cond else 0
            # длина запроса
            queryLen = wherePrefixLen + wherePostfixLen + stmtLen + filterLen

            for et in eventIdList:
                e= str(et)
                queryLen += len(e) + whereInfixLen

                if maxQuerySize and (queryLen  > maxQuerySize):
                    assert len(strIdList) > 0
                    s = stmt + wherePrefix + whereInfix.join(strIdList) +\
                        wherePostfix

                    if cond:
                        s += ' AND ' + cond

                    s += stmtOrderBy
                    result.append(self.db.query(s))
                    QtGui.qApp.processEvents()
                    strIdList = []
                    queryLen = wherePrefixLen + wherePostfixLen +\
                        stmtLen + filterLen + len(e) + whereInfixLen


                strIdList.append(e)

            stmt+= wherePrefix +whereInfix.join(strIdList)+ wherePostfix

        if cond:
            stmt += ' AND ' + cond

        stmt += stmtOrderBy

        if maxQuerySize and (maxQuerySize<len(stmt)):
            raise CException(u'Превышен максимальный размер запроса.'+ \
                u'Максимальный размер: %d байт. Размер запроса: %d байт' \
                % (maxQuerySize, len(stmt)))

        result.append(self.db.query(stmt))
        return result


    def writeClientInfoHeader(self,  id,  OGRN):
        self.writeStartElement('Client')
        self.writeAttribute('id', '%s-%d' % (OGRN, id))
        clientInfo = self.clientInfoCache.get(id,  None)
        if not clientInfo:
            clientInfo = getClientInfo(id)
            self.clientInfoCache[id] = clientInfo

        for x in ('lastName', 'firstName', 'patrName', 'sexCode',
                    'birthDate', 'SNILS', 'notes', 'compulsoryPolicy',
                    'voluntaryPolicy'):
            if clientInfo.has_key(x):
                self.writeAttribute(x, forceString(clientInfo[x]))

        if clientInfo.has_key('attaches'):
            for a in clientInfo['attaches']:
                self.writeStartElement('Attach')
                for x in ('code','name'):
                    self.writeAttribute(x, forceString(a[x]))
                self.writeEndElement()


#        if clientInfo.has_key('socStatuses'):
#            for s in clientInfo['socStatuses']:
#                self.writeStartElement('SocialStatus')
#                self.writeEndElement()


        if self.parent.parent.includeClientWorkInfo:
            if clientInfo.has_key('work'):
                self.writeAttribute('work',  forceString(clientInfo['work']))


        if self.parent.parent.includeClientDocumentInfo:
            if clientInfo.has_key('document'):
                self.writeAttribute('document',  forceString(clientInfo['document']))

        if self.parent.parent.includeClientAddressInfo:
            for x in ('locAddress', 'regAddress'):
                if clientInfo.has_key(x):
                    self.writeAttribute(x, forceString(clientInfo[x]))

        if self.parent.parent.includeClientContactInfo:
            clientContact = getClientPhones(id)
            # for (typeCode, typeName, contact, notes, isPrimary) in clientContact:
            for (typeCode, typeName, contact, notes) in clientContact:
                self.writeStartElement('Contact')
                self.writeAttribute('typeName',  forceString(typeName))
                self.writeAttribute('contact',  forceString(contact))
                self.writeAttribute('notes',  forceString(notes))
                self.writeEndElement()


    def writeClientInfoFooter(self,  id):
        self.writeEndElement()


    def writeEventInfoHeader(self,  id):
        self.writeStartElement("Event")
        eventInfo = self.getEventInfo(id)
        for x in ('code','name',  'setDate', 'execDate',  'result_code',
                    'result_name',  'setPerson_code',  'setPerson_name',
                    'execPerson_code',  'execPerson_name'):
            if eventInfo.has_key(x) and eventInfo[x] != '':
                self.writeAttribute(x,  eventInfo[x])


    def writeEventInfoFooter(self,  id):
        self.writeEndElement()


    def writeActionPropertyList(self,  actionId,  OGRN):
        u"""Пишет следующие свойства действия в XML:
            Идентификатор (ОГРН ЛПУ и через "-" actionproperty.id),
            название (если связан с шаблоном, то код шаблона),
            значение, ед.измерения, норма."""

        stmt = '''
            SELECT  ActionProperty.id AS `id`,
                        ActionPropertyType.name AS `name`,
                        ActionPropertyType.typeName AS `typeName`,
                        ActionProperty.norm AS `norm`,
                        rbUnit.code AS `unit_code`,
                        rbUnit.name AS `unit_name`,
                        ActionPropertyType.template_id AS `template_id`
            FROM ActionProperty
            LEFT JOIN ActionPropertyType ON ActionPropertyType.id = ActionProperty.type_id
            LEFT JOIN rbUnit ON rbUnit.id = ActionProperty.unit_id
            WHERE ActionProperty.action_id = %d
                AND ActionProperty.deleted = 0
        ''' % actionId

        query = self.db.query(stmt)
        while (query.next()):
            record = query.record()
            self.writeStartElement('ActionProperty')
            self.writeAttribute('id',  '%s-%d' % (OGRN,  forceInt(record.value('id'))))
            for x in ('name',  'norm',  'typeName', 'unit_code',  'unit_name'):
                v = forceString(record.value(x))
                if v and v != '':
                    self.writeAttribute(x, v)

            templateId = forceInt(record.value('template_id'))
            if templateId and templateId != 0:
                templateCode = self.getActionPropertyTemplateCode(templateId)
                if templateCode:
                    self.writeAttribute('template_code',  templateCode)

            typeName = forceString(record.value('typeName'))

            if typeName and typeName != '':
                value = self.getActionPropertyValue(forceInt(record.value('id')), typeName)
                if value and value != '':
                    self.writeAttribute('value',  value)

            self.writeEndElement()


    def writeRecord(self, record):
        clientId = forceInt(record.value('client_id'))
        OGRN = forceString(record.value('org_OGRN'))

        if self.parent.parent.includeClientEventInfo:
            eventId = forceInt(record.value('event_id'))

            if eventId != self.currentEventId:
                if self.currentEventId:
                    self.writeEventInfoFooter(eventId)
                self.writeEventInfoHeader(eventId)
                self.writeClientInfoHeader(clientId,  OGRN)
                self.writeClientInfoFooter(clientId)
                self.currentEventId = eventId
        else:
            if clientId != self.currentClientId:
                if self.currentClientId:
                    self.writeClientInfoFooter(clientId)
                self.writeClientInfoHeader(clientId,  OGRN)
                self.currentClientId = clientId

        self.writeStartElement('ActionResult')
        # все свойства результата действия экспортируем как атрибуты
        # Выгружаем:
        #   Идентификатор (ОГРН ЛПУ и через "-" action.id), название,
        #   код (полный от корня класса через "-"), примечание,
        #   ФИО и код исполнителя, даты начала и выполнения, статус.
        self.writeAttribute('id', '%s-%d' % (OGRN,  forceInt(record.value('id'))))

        for x in ('actionType_code', 'actionType_name', 'directionDate',
                    'status', 'begDate', 'endDate', 'note',  'person_code',
                    'person_name'):
            self.writeAttribute(x,forceString(record.value(x)))

        # запись свойств действия
        self.writeActionPropertyList(forceInt(record.value('id')),  OGRN)

        self.writeEndElement()


    def writeFile(self,  device,  progressBar):
        global lastChangedRev
        global lastChangedDate
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        try:
            self.parent.stat.setText(u' Договоров выбрано: %d.' % len(self._contractIdList))
            progressBar.setText(u'Запрос событий по выбранным договорам')
            QtGui.qApp.processEvents()
            eventIdList = self.getEventIdList(self._contractIdList,  self._filterEvent)

            if eventIdList != []:
                self.parent.stat.setText(u' Договоров выбрано: %d, событий найдено: %d.' \
                    % (len(self._contractIdList), len(eventIdList)))
                progressBar.setText(u'Запрос результатов действий')
                QtGui.qApp.processEvents()
                queryList = self.createActionQueryList(eventIdList,  self._filterAction)
                self.querySize = 0

                for x in queryList:
                    self.querySize += x.size()


                self.parent.stat.setText(u' Договоров выбрано: %d. Найдено: событий - %d,' \
                    u' результатов действий - %d.'
                    % (len(self._contractIdList), len(eventIdList), self.querySize))

                self.setDevice(device)
                progressBar.setMaximum(max(self.querySize, 1))
                progressBar.reset()
                progressBar.setValue(0)

                if self.querySize > 0:
                    self.writeStartDocument()
                    self.writeDTD('<!DOCTYPE xActionResult>')
                    self.writeStartElement('ActionResultExport')
                    self.writeAttribute('SAMSON',
                                '2.0 revision(%s, %s)' %(lastChangedRev, lastChangedDate))
                    self.writeAttribute('version', '1.00')
                    for query in queryList:
                        while (query.next()):
                            self.writeRecord(query.record())
                            QtGui.qApp.processEvents()

                            if self.parent.aborted:
                                return False

                            progressBar.step()

                    if self.parent.parent.includeClientEventInfo:
                        self.writeEventInfoFooter(self.currentEventId)
                    else:
                        self.writeClientInfoFooter(self.currentClientId)

                    self.currentEventId = None
                    self.currentClientId = None
                    self.writeEndDocument()
                else:
                    QtGui.QMessageBox.critical (self.parent,
                        u'Экспорт результатов действий',
                        u'По выбранному договору действий не найдено.\n' +\
                        u'Отсутствует информация для выгрузки.',
                        QtGui.QMessageBox.Close)
                    return False

            else:
                QtGui.QMessageBox.critical (self.parent,
                    u'Экспорт результатов действий',
                    u'По выбранному договору событий не найдено.\n' +\
                    u'Отсутствует информация для выгрузки.', QtGui.QMessageBox.Close)
                return False


        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True

class CExportActionResultWizardPage1(QtGui.QWizardPage, Ui_ExportActionResult_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор договора и установка фильтров для экспорта результатов действий')
        self.parent.selectedContractIdList = self.getContractIdList(self.treeContracts.currentIndex())
        db = QtGui.qApp.db
        self.tableEvent  = db.table('Event')
        self.tableEventType  = db.table('EventType')
        self.tableAction = db.table('Action')
        self.tableActionType = db.table('ActionType')


    def preSetupUi(self):
        self.addModels('Tree', CContractTreeModel(self))


    def postSetupUi(self):
        self.setModels(self.treeContracts,  self.modelTree,  self.selectionModelTree)
        self.treeContracts.header().hide()
        self.treeContracts.setAlternatingRowColors(True)
        self.treeContracts.expandAll()
        self.cmbEventPurpose.setTable('rbEventTypePurpose', False, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', False, filter=getWorkEventTypeFilter())
        self.cmbActionSetPerson.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbActionSetPerson.setAddNone(False)


    def isComplete(self):
        return self.parent.selectedContractIdList != []


    def getContractIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.idList if treeItem else []


    def updateFilterEvent(self):
        cond = []

        if self.chkEventExecDate.isChecked():
            cond.append(self.tableEvent['execDate'].between( \
                forceString(self.edtEventExecBegDate.date().toString(Qt.ISODate)),
                forceString(self.edtEventExecEndDate.date().toString(Qt.ISODate))))

        if self.chkEventSetDate.isChecked():
            cond.append(self.tableEvent['setDate'].between( \
                forceString(self.edtEventSetBegDate.date().toString(Qt.ISODate)),
                forceString(self.edtEventSetEndDate.date().toString(Qt.ISODate))))

        if self.chkEventType.isChecked():
            cond.append(self.tableEvent['eventType_id'].eq( \
                forceInt(self.cmbEventType.value())))

        if self.chkEventPurpose.isChecked():
            cond.append(self.tableEventType['purpose_id'].eq( \
                forceInt(self.cmbEventPurpose.value())))

        if self.chkEventLPU.isChecked():
            cond.append(self.tableEvent['org_id'].eq( \
                forceInt(self.cmbEventLPU.value())))

        self.parent.filterEvent = QtGui.qApp.db.joinAnd(cond)


    def updateFilterAction(self):
        cond = []

        if self.chkActionDate.isChecked():
            cond.append(self.tableAction['begDate'].ge( \
                forceString(self.edtActionBegDate.date().toString(Qt.ISODate))))
            cond.append(self.tableAction['endDate'].le( \
                forceString(self.edtActionEndDate.date().toString(Qt.ISODate))))

        if self.chkActionStatus.isChecked():
            cond.append(self.tableAction['status'].eq( \
                forceInt(self.cmbActionStatus.currentIndex())))

        if self.chkActionSetPerson.isChecked():
            cond.append(self.tableAction['setPerson_id'].eq ( \
                forceInt(self.cmbActionSetPerson.value())))

        if self.chkActionClass.isChecked():
            cond.append(self.tableActionType['class'].eq( \
                forceInt(self.cmbActionClass.currentIndex())))

        if self.chkActionType.isChecked():
            cond.append(self.tableAction['actionType_id'].eq( \
                forceInt(self.cmbActionType.value())))

        self.parent.filterAction = QtGui.qApp.db.joinAnd(cond)


    @pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        # сохраняем индексы выбранных элементов в таблице
        self.parent.selectedContractIdList = self.getContractIdList( \
            self.treeContracts.currentIndex())

        if self.parent.selectedContractIdList != []:
            contractInfo = getContractInfo(self.parent.selectedContractIdList[0])

            if not self.chkEventSetDate.isChecked():
                self.edtEventSetBegDate.setDate(contractInfo.begDate)
                self.edtEventSetEndDate.setDate(contractInfo.endDate)

            if not self.chkEventExecDate.isChecked():
                self.edtEventExecBegDate.setDate(contractInfo.begDate)
                self.edtEventExecEndDate.setDate(contractInfo.endDate)

            if not self.chkActionDate.isChecked():
                self.edtActionBegDate.setDate(contractInfo.begDate)
                self.edtActionEndDate.setDate(contractInfo.endDate)

        self.emit(SIGNAL('completeChanged()'))

    # Event Filter
    @pyqtSlot()
    def on_chkEventExecDate_clicked(self):
        self.edtEventExecBegDate.setEnabled(self.chkEventExecDate.isChecked())
        self.edtEventExecEndDate.setEnabled(self.chkEventExecDate.isChecked())
        self.updateFilterEvent()


    @pyqtSlot(QDate)
    def on_edtEventExecBegDate_dateChanged(self, date):
        self.updateFilterEvent()


    @pyqtSlot(QDate)
    def on_edtEventExecEndDate_dateChanged(self, date):
        self.updateFilterEvent()


    def on_chkEventSetDate_clicked(self):
        self.edtEventSetBegDate.setEnabled(self.chkEventSetDate.isChecked())
        self.edtEventSetEndDate.setEnabled(self.chkEventSetDate.isChecked())
        self.updateFilterEvent()


    @pyqtSlot(QDate)
    def on_edtEventSetBegDate_dateChanged(self, date):
        self.updateFilterEvent()


    @pyqtSlot(QDate)
    def on_edtEventSetEndDate_dateChanged(self, date):
        self.updateFilterEvent()


    @pyqtSlot()
    def on_chkEventPurpose_clicked(self):
        self.cmbEventPurpose.setEnabled(self.chkEventPurpose.isChecked())
        self.updateFilterEvent()


    @pyqtSlot()
    def on_chkEventType_clicked(self):
        self.cmbEventType.setEnabled(self.chkEventType.isChecked())
        self.updateFilterEvent()


    @pyqtSlot(int)
    def on_cmbEventType_currentIndexChanged(self, index):
        self.updateFilterEvent()


    @pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        self.updateFilterEvent()


    @pyqtSlot()
    def on_chkEventLPU_clicked(self):
        self.cmbEventLPU.setEnabled(self.chkEventLPU.isChecked())
        self.updateFilterEvent()


    @pyqtSlot(int)
    def on_cmbEventLPU_currentIndexChanged(self, index):
        self.cmbEventPerson.setOrgId(self.cmbEventLPU.value())
        self.updateFilterEvent()


    # Action Filter
    @pyqtSlot()
    def on_chkActionDate_clicked(self):
        self.edtActionBegDate.setEnabled(self.chkActionDate.isChecked())
        self.edtActionEndDate.setEnabled(self.chkActionDate.isChecked())
        self.updateFilterAction()


    @pyqtSlot(QDate)
    def on_edtActionBegDate_dateChanged(self, date):
        self.updateFilterAction()


    @pyqtSlot(QDate)
    def on_edtActionEndDate_dateChanged(self, date):
        self.updateFilterAction()


    @pyqtSlot()
    def on_chkActionSetPerson_clicked(self):
        self.cmbActionSetPerson.setEnabled(self.chkActionSetPerson.isChecked())
        self.updateFilterAction()


    @pyqtSlot(int)
    def on_cmbActionSetPerson_currentIndexChanged(self, index):
        self.updateFilterAction()


    @pyqtSlot()
    def on_chkActionStatus_clicked(self):
        self.cmbActionStatus.setEnabled(self.chkActionStatus.isChecked())
        self.updateFilterAction()


    @pyqtSlot(int)
    def on_cmbActionStatus_currentIndexChanged(self, index):
        self.updateFilterAction()


    @pyqtSlot()
    def on_chkActionClass_clicked(self):
        self.cmbActionClass.setEnabled(self.chkActionClass.isChecked())
        if self.chkActionClass.isChecked():
            self.cmbActionType.setClass(self.cmbActionClass.currentIndex())
        else:
            self.cmbActionType.setClasses([0, 1, 2, 3])
        self.updateFilterAction()


    @pyqtSlot(int)
    def on_cmbActionClass_currentIndexChanged(self, index):
        self.cmbActionType.setClass(self.cmbActionClass.currentIndex())
        self.updateFilterAction()


    @pyqtSlot()
    def on_chkActionType_clicked(self):
        self.cmbActionType.setEnabled(self.chkActionType.isChecked())
        self.updateFilterAction()


    @pyqtSlot(int)
    def on_cmbActionType_currentIndexChanged(self, index):
        self.updateFilterAction()


    @pyqtSlot()
    def on_chkIncludeClientEventInfo_clicked(self):
        self.parent.includeClientEventInfo = \
                self.chkIncludeClientEventInfo.isChecked()


    @pyqtSlot()
    def on_chkIncludeClientWorkInfo_clicked(self):
        self.parent.includeClientWorkInfo = \
                self.chkIncludeClientWorkInfo.isChecked()


    @pyqtSlot()
    def on_chkIncludeClientAddressInfo_clicked(self):
        self.parent.includeClientAddressInfo = \
                self.chkIncludeClientAddressInfo.isChecked()


    @pyqtSlot()
    def on_chkIncludeClientDocumentInfo_clicked(self):
        self.parent.includeClientDocumentInfo = \
                self.chkIncludeClientDocumentInfo.isChecked()


    @pyqtSlot()
    def on_chkIncludeClientContactInfo_clicked(self):
        self.parent.includeClientContactInfo = \
                self.chkIncludeClientContactInfo.isChecked()


    @pyqtSlot()
    def on_btnResetFilter_clicked(self):
        # Event Filters
        self.chkEventExecDate.setChecked(False)
        self.edtEventExecBegDate.setEnabled(False)
        self.edtEventExecEndDate.setEnabled(False)
        self.chkEventSetDate.setChecked(False)
        self.edtEventSetBegDate.setEnabled(False)
        self.edtEventSetEndDate.setEnabled(False)
        self.chkEventPurpose.setChecked(False)
        self.cmbEventPurpose.setEnabled(False)
        self.chkEventType.setChecked(False)
        self.cmbEventType.setEnabled(False)
        self.chkEventLPU.setChecked(False)
        self.cmbEventLPU.setEnabled(False)
        self.updateFilterEvent()
        # Action Filters
        self.chkActionDate.setChecked(False)
        self.edtActionBegDate.setEnabled(False)
        self.edtActionEndDate.setEnabled(False)
        self.chkActionStatus.setChecked(False)
        self.cmbActionStatus.setEnabled(False)
        self.chkActionSetPerson.setChecked(False)
        self.cmbActionSetPerson.setEnabled(False)
        self.chkActionClass.setChecked(False)
        self.cmbActionClass.setEnabled(False)
        self.chkActionType.setChecked(False)
        self.cmbActionType.setEnabled(False)
        self.updateFilterAction()
        # Additional
        self.chkIncludeClientEventInfo.setChecked(False)
        self.chkIncludeClientWorkInfo.setChecked(False)
        self.chkIncludeClientAddressInfo.setChecked(False)
        self.chkIncludeClientDocumentInfo.setChecked(False)
        self.chkIncludeClientContactInfo.setChecked(False)
        self.parent.includeClientEventInfo = False
        self.parent.includeClientWorkInfo = False
        self.parent.includeClientAddressInfo = False
        self.parent.includeClientDocumentInfo = False
        self.parent.includeClientContactInfo = False


class CExportActionResultWizardPage2(QtGui.QWizardPage, Ui_ExportActionResult_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.aborted = False
        self.done = False
        self.connect(self, SIGNAL('rejected()'), self.abort)
        # имя файла в которое записан результат экспорта.
        self.writtenFileName = None
        self.addDateToFileName = False
        self.addContractNumberToFileName = False
        self.verboseLog = False
        self.recordsNumber = 0
        self.clientsNumber = 0


    def initializePage(self):
        self.progressBar.setFormat('%v')
        self.progressBar.setValue(0)
        self.edtFileName.setText(self.parent.fileName)
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.btnAbort.setEnabled(False)
        self.btnSend.setEnabled(False)
        self.checkRAR.setChecked(self.parent.compressRAR)
        self.chkAddContractNumberToFileName.setChecked(self.addContractNumberToFileName)
        self.chkAddDateToFileName.setChecked(self.addDateToFileName)
        self.chkVerboseLog.setChecked(self.verboseLog)
        self.aborted = False
        self.done = False
        self.writtenFileName = None
        self.recordsNumber = 0
        self.clientsNumber = 0


    def abort(self):
        self.aborted = True
        self.done = False
        self.emit(SIGNAL('completeChanged()'))


    def log(self, str,  forceLog = False):
        if self.verboseLog or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def isComplete(self):
        return self.done


    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getSaveFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.parent.fileName = fileName
            self.btnExport.setEnabled(True)


    @pyqtSlot()
    def on_btnExport_clicked(self):
        fileName = self.edtFileName.text()
        self.aborted = False

        if fileName.isEmpty():
            return

        if self.parent.selectedContractIdList == []:
            self.log(u'! Не выбрано ни одного договора для выгрузки',  True)
            QtGui.QMessageBox.warning(self, u'Экспорт результатов действий',
                                      u'Не выбрано ни одного договора для выгрузки')
            self.parent.back() # вернемся на пред. страницу. пусть выбирают
            return

        if self.addContractNumberToFileName:
            self.log(u'К имени файла добавлен номер договора.')
            contractInfo = getContractInfo(self.parent.selectedContractIdList[0])
            fileInfo = QFileInfo(fileName)
            fileName = fileInfo.path()+'/'+fileInfo.baseName() + '_' + \
                        contractInfo.number + '.' +fileInfo.suffix()

        if self.addDateToFileName:
            self.log(u'К имени файла добавлена дата выгрузки.')
            fileInfo = QFileInfo(fileName)
            fileName = fileInfo.path()+'/'+fileInfo.baseName() + '_' + \
                        QDate.currentDate().toString(Qt.ISODate)+ \
                        '.' +fileInfo.suffix()

        outFile = QFile(fileName)
        if not outFile.open(QFile.WriteOnly | QFile.Text):
            self.log(u'! Не могу открыть файл для записи %s:\n%s' \
                        % (fileName, outFile.errorString()),  True)
            QtGui.QMessageBox.warning(self,  u'Экспорт результатов действий',
                                      u'Не могу открыть файл для записи %s:\n%s'  \
                                      % (fileName, outFile.errorString()))

        self.log(u'Экспорт результатов в файл:"%s"' % fileName, True)
        myXmlStreamWriter = CMyXmlStreamWriter(self,
                                               self.parent.selectedContractIdList,
                                               self.parent.filterEvent,
                                               self.parent.filterAction)
        self.btnAbort.setEnabled(True)
        self.btnExport.setEnabled(False)
        self.parent.button(QtGui.QWizard.BackButton).setEnabled(False)
        self.parent.button(QtGui.QWizard.FinishButton).setEnabled(False)
        self.parent.button(QtGui.QWizard.CancelButton).setEnabled(False)
        self.chkAddContractNumberToFileName.setEnabled(False)
        self.chkAddDateToFileName.setEnabled(False)

        if (myXmlStreamWriter.writeFile(outFile,  self.progressBar)):
            self.progressBar.setText(u'Готово')
            self.recordsNumber = myXmlStreamWriter.querySize
            self.clientsNumber = len(myXmlStreamWriter.clientInfoCache)
            outFile.close()

            if self.checkRAR.isChecked():
                cmdLine = u'rar mf -ep -m5 -o+ -y -- "%s" "%s"' % \
                    (fileName+'.rar', fileName)

                self.progressBar.setText(u'Сжатие')
                self.log(u'Сжатие в RAR.')
                self.log(u'Запуск внещней программы "%s"' % cmdLine)
                self.checkRAR.setEnabled(False)

                try:
                    compressFileInRar(fileName, fileName+'.rar')
                    self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
                    self.checkRAR.setEnabled(True)
                    self.writtenFileName = fileName +'.rar'
                except CRarException as e:
                    self.progressBar.setText(unicode(e))
                    QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)
            else:
                self.writtenFileName = fileName

            self.done = True
            self.btnSend.setEnabled(True)
        else:
            self.progressBar.setText(u'Прервано')
            outFile.close()

        self.btnAbort.setEnabled(False)
        self.btnExport.setEnabled(True)
        self.parent.button(QtGui.QWizard.BackButton).setEnabled(True)
        self.parent.button(QtGui.QWizard.FinishButton).setEnabled(True)
        self.parent.button(QtGui.QWizard.CancelButton).setEnabled(True)
        self.chkAddContractNumberToFileName.setEnabled(True)
        self.chkAddDateToFileName.setEnabled(True)
        self.emit(SIGNAL('completeChanged()'))


    @pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()


    @pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


    @pyqtSlot()
    def on_chkAddDateToFileName_clicked(self):
        self.addDateToFileName = self.chkAddDateToFileName.isChecked()


    @pyqtSlot()
    def on_chkAddContractNumberToFileName_clicked(self):
        self.addContractNumberToFileName = self.chkAddContractNumberToFileName.isChecked()


    @pyqtSlot()
    def on_chkVerboseLog_clicked(self):
        self.verboseLog = self.chkVerboseLog.isChecked()


    @pyqtSlot(QString)
    def on_edtFileName_textChanged(self,  text):
        self.emit(SIGNAL('completeChanged()'))
        self.parent.fileName = str(text)


    @pyqtSlot()
    def on_btnSend_clicked(self):
        if self.writtenFileName:
            db = QtGui.qApp.db
            record = None

            for x in self.parent.selectedContractIdList:
                record = db.getRecord('Contract',  'format_id',  forceInt(x))
                if record:
                    formatId = forceInt(record.value('format_id'))
                    if formatId:
                        record = db.getRecordEx('rbAccountExportFormat', '*', \
                            'id=%d' % formatId)
                        if record:
                            break

                    record = None

            if not record:
                record = db.getRecordEx('rbAccountExportFormat', '*', 'prog=\'XML\'')

            if record:
                emailTo = forceString(record.value('emailTo'))
                subject = forceString(record.value('subject'))
                message = forceString(record.value('message'))
            else:
                emailTo = u'<введите адрес эл.почты>'
                subject = u'Результаты действий'
                message = u'Уважаемые господа,\n'                       \
                        u'Высылаем Вам результаты действий в формате XML\n' \
                        u'в {shortName}, ОГРН: {OGRN}\n'              \
                        u'за период с {actBegDate} по {actEndDate}\n'       \
                        u'в приложении {NR} записей\n'                \
                        u'для {NC} пациентов\n' \
                        u'фильтр статуса действий {actStatus}\n' \
                        u'номера договора(ов): {contractNumber}\n' \
                        u'\n'                                         \
                        u'--\n'                                       \
                        u'WBR\n'                                      \
                        u'{shortName}\n'

            orgRec=QtGui.qApp.db.getRecord(
                'Organisation', 'INN, OGRN, shortName', QtGui.qApp.currentOrgId())
            data = {}
            data['INN'] = forceString(orgRec.value('INN'))
            data['OGRN'] = forceString(orgRec.value('OGRN'))
            data['shortName'] = forceString(orgRec.value('shortName'))

            filtersPage = self.parent.page(0) # qwizardpage с фильтрами по экспорту

            data['actBegDate'] = forceString(filtersPage.edtActionBegDate.date().toString(Qt.ISODate))
            data['actEndDate'] = forceString(filtersPage.edtActionEndDate.date().toString(Qt.ISODate))

            if filtersPage.chkActionStatus.isChecked():
                data['actStatus'] = CActionType.retranslateClass(False).statusNames[filtersPage.cmbActionStatus.currentIndex()]
            else:
                data['actStatus'] = u'любой'

            data['NR'] = self.recordsNumber
            data['NC'] = self.clientsNumber

            contractNumberList = []
            for x in self.parent.selectedContractIdList:
                contractInfo = getContractInfo(x)
                contractNumberList.append(forceString(contractInfo.number))

            data['contractNumber'] = u', '.join([str(et) for et in contractNumberList])
            subject = substFields(subject, data)
            message = substFields(message, data)

            sendMail(self, emailTo, subject, message, [self.writtenFileName])



class CExportActionResult(QtGui.QWizard):
    def __init__(self, fileName,  compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт результатов действий')
        self.selectedContractIdList = []
        self.fileName= fileName
        self.compressRAR = compressRAR
        self.filterEvent = ''
        self.filterAction = ''
        self.includeClientEventInfo = False
        self.includeClientWorkInfo = False
        self.includeClientAddressInfo = False
        self.includeClientContactInfo = False
        self.includeClientDocumentInfo = False
        self.addPage(CExportActionResultWizardPage1(self))
        self.addPage(CExportActionResultWizardPage2(self))
