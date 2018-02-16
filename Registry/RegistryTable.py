# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import datetime
from PyQt4 import QtCore, QtGui, QtSql
from itertools import chain

from PyQt4.QtCore import QVariant

from Events.Action import CActionType
from Events.ActionTypeCol import CActionTypeCol
from Events.ContractTariffCache import CContractTariffCache
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Recommendations import CAnalysesRecommendationMixin
from Events.Utils import EventIsPrimary, EventOrder, getPayStatusMask, payStatusText, recommendationIsActual, \
    recordAcceptable, getMainActionTypesAnalyses
from Registry.Utils import canRemoveEventWithTissue, canRemoveEventWithJobTicket, hasUnpaidMXActions
from Reports.ReportBase import CReportBase, createTable
from Users.Rights import urDeleteNotOwnEvents, urDeleteOwnEvents
from library.TableModel import CBoolCol, CCol, CDateCol, CDesignationCol, CEnumCol, CNameCol, CNumCol, CRefBookCol, \
    CTableModel, CTextCol
from library.TableView import CTableView
from library.Utils import calcAgeTuple, forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, \
    forceStringEx, forceTr, formatName, formatSNILS, formatSex, pyDate, toVariant
from library.crbcombobox import CRBComboBox
from library.database import CDocumentTable, CRecordCache, CTableRecordCache


class CSNILSCol(CTextCol):
    def format(self, values):
        val = unicode(values[0].toString())
        return QtCore.QVariant(formatSNILS(val))


class CDiagnosisCol(CTextCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment)

    def load(self, diagnosisId):
        record = QtGui.qApp.db.getRecord('Diagnosis', 'MKB, MKBEx', diagnosisId)
        if record:
            MKB = forceString(record.value('MKB'))
            MKBEx = forceString(record.value('MKBEx'))
            self.putIntoCache(diagnosisId, MKB + '+' + MKBEx if MKBEx else MKB)
        else:
            self.putIntoCache(diagnosisId, '')


class CMKBTextCol(CTextCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment)

    def load(self, diagnosisId):
        db = QtGui.qApp.db
        tblDiagnosis = db.table('Diagnosis')
        tblMKB = db.table('MKB')
        record = db.getRecord(tblDiagnosis, tblDiagnosis['MKB'], diagnosisId)
        if record:
            record = db.getRecordEx(tblMKB, tblMKB['DiagName'], tblMKB['DiagID'].eq(forceString(record.value('MKB'))))
            if record:
                self.putIntoCache(diagnosisId, forceString(record.value('DiagName')))
                return
        self.putIntoCache(diagnosisId, '')


class CMorphologyMKBCol(CTextCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment)

    def load(self, diagnosisId):
        morphologyMKB = forceString(QtGui.qApp.db.translate('Diagnosis', 'id', diagnosisId, 'morphologyMKB'))
        self.putIntoCache(diagnosisId, morphologyMKB)


class CClientVIPCol(CTextCol):
    def __init__(self, title, fields, defaultWidth, alignment='l'):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment)

    def load(self, clientId):
        db = QtGui.qApp.db
        tableClientVIP = db.table('ClientVIP')
        isVIP = db.getRecordEx(tableClientVIP, tableClientVIP['id'], [tableClientVIP['deleted'].eq(0), tableClientVIP['client_id'].eq(clientId)])  # ('Diagnosis', 'id', clientId, 'morphologyMKB')
        if isVIP and forceRef(isVIP.value('id')) is not None:
            isVIP = u'ДА'
        else:
            isVIP = u'НЕТ'
        self.putIntoCache(clientId, isVIP)


class CClientEvalCol(CTextCol):
    def __init__(self, title, fields, expr, defaultWidth, alignment='l'):
        CTextCol.__init__(self, title, fields, defaultWidth, alignment)
        self.expr = expr

    def load(self, itemId):
        self.putIntoCache(itemId, forceString(QtGui.qApp.db.translate('Client', 'id', itemId, self.expr)))

    def invalidateRecordsCache(self):
        self._cacheDict.clear()


class CLastVisitCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment='l', highlightRedDate=True):
        CCol.__init__(self, title, fields, defaultWidth, alignment, highlightRedDate)

    def load(self, clientId):
        tableVisit = QtGui.qApp.db.table('Visit')
        tableEvent = QtGui.qApp.db.table('Event')
        queryTable = tableVisit.innerJoin(tableEvent,
                                          [tableEvent['deleted'].eq(0),
                                           tableVisit['deleted'].eq(0),
                                           tableEvent['id'].eq(tableVisit['event_id'])])
        record = QtGui.qApp.db.getRecordEx(queryTable, 'MAX(Visit.date)', tableEvent['client_id'].eq(clientId))
        self.putIntoCache(clientId, forceDate(record.value(0)).toString(QtCore.Qt.LocalDate))


class CClientEvalExCol(CDesignationCol):
    def __init__(self, title, fields, designationChain, defaultWidth, alignment='l', isRTF = False):
        CDesignationCol.__init__(self, title, fields, designationChain, defaultWidth, alignment, isRTF)
        self.color = None

    def format(self, values):
        values = self.getValues(values)
        if CCol.invalid in values or len(values) < 2:
            self.color = None
            return u''
        self.color = values[0]
        code = '' if values[1] == CCol.invalid else values[1]
        return code

    def getCodeNameToolTip(self, values):
        values = self.getValues(values)
        if CCol.invalid not in values:
            code = forceString(values[1])
            name = forceString(values[2])
            return QtCore.QVariant(u'%s-%s' % (code, name))
        return CCol.invalid

    def getBackgroundColor(self, values):
        val = self.color
        if val:
            colorName = forceString(val)
            if colorName:
                return QtCore.QVariant(QtGui.QColor(colorName))
        return CCol.invalid


class CIINCol(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')

    def format(self, values):
        return toVariant(values[0])


class CClientsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        #TODO: Если будете добавлять колонки — обратите внимание на
        #TODO: RegistryWindow: self.registryWidget().viewWidget().setColumnHidden()
        #TODO: и def registryContentDoubleClicked(self, index):
        #TODO: Надо как-нибудь избавиться от этого безобразия
        self.addColumn(CNameCol(u'Фамилия',    ['lastName'], 15))
        self.addColumn(CNameCol(u'Имя',        ['firstName'], 15))
        self.addColumn(CNameCol(u'Отчество',   ['patrName'], 15))
        self.addColumn(CDateCol(u'Дата рожд.', ['birthDate'], 12, highlightRedDate=False))
        self.addColumn(CEnumCol(u'Пол',        ['sex'], [u'-', u'М', u'Ж'], 6, 'c'))
        if QtGui.qApp.defaultKLADR().startswith('90'):  self.addColumn(CIINCol(u'ИИН',     ['IIN'], 10))
        else:                                           self.addColumn(CSNILSCol(u'СНИЛС',     ['SNILS'], 10))
        self.addColumn(CClientEvalCol(u'Документ',          ['id'], 'getClientDocument(id)',   30))
        self.addColumn(CClientEvalCol(u'Полис ОМС',         ['id'], 'getClientPolicy(id,1)',   30))
        self.addColumn(CClientEvalCol(u'Полис ДМС',         ['id'], 'getClientPolicy(id,0)',   30))
        self.addColumn(CClientEvalCol(u'Занятость',         ['id'], 'getClientWork(id)',       30))
        self.addColumn(CClientEvalCol(u'Контакты',          ['id'], 'getClientContacts(id)',   30))
        self.addColumn(CClientEvalExCol(u'С',               ['id'], [('Client_StatusObservation', 'statusObservationType_id', 'master_id'),
                                                                     ('rbStatusObservationClientType', ['color', 'code', 'name'])], 10)).setToolTip(u'Статус наблюдения пациента')
        self.addColumn(CClientEvalExCol(u'К',               ['id'], [('Client_LocationCard', 'locationCardType_id', 'master_id'),
                                                                     ('rbLocationCardType', ['color', 'code', 'name'])], 10)).setToolTip(u'Место нахождения амбулаторной карты')
        self.addColumn(CClientEvalCol(u'Адрес регистрации', ['id'], 'getClientRegAddress(id)', 30))
        self.addColumn(CEnumCol(u'БС', ['isUnconscious'], [u'НЕТ', u'ДА'], 6, 'c')).setToolTip(u'Прибыл без сознания')
        self.addColumn(CClientVIPCol(u'VIP',                ['id'],                            6)).setToolTip(u'VIP пациент')
        self.addColumn(CClientEvalCol(u'Адрес проживания',  ['id'], 'getClientLocAddress(id)', 30))

        if forceBool(QtGui.qApp.preferences.appPrefs.get('showVisitDateInRegistry', QtCore.QVariant())):
            self.addColumn(CLastVisitCol(u'Последнее посещение', ['id'], 30))

        self.addColumn(CDateCol(u'Следующая дата', ['nextEventDate'], 10))
        self.addColumn(CRefBookCol(u'Вид наблюдения', ['lastMonKindId'], 'rbClientMonitoringKind', 10))
        self.addColumn(CRefBookCol(u'Частота посещений', ['lastMonFrequenceId'], 'rbClientMonitoringFrequence', 10))

        self.setTable('Client')
        self.unconsciousPatientRowColor = u'red'
        # from HospitalBeds.models.MonitoringModel import CMonitoringModel
        # self.vipClientColor = CMonitoringModel.vipClientColor
        self.vipList = dict()
        self.fillVIPClients()

    def fillVIPClients(self):
        self.vipList = dict()
        if u'онко' in forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
            for x in QtGui.qApp.db.getRecordList(
                    QtGui.qApp.db.table('ClientVIP'),
                    [QtGui.qApp.db.table('ClientVIP')['client_id'], QtGui.qApp.db.table('ClientVIP')['color']],
                    [QtGui.qApp.db.table('ClientVIP')['deleted'].eq(0)]
            ):
                self.vipList[forceInt(x.value('client_id'))] = forceString(x.value('color'))

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableClientMonitoring = db.table('ClientMonitoring')
        tableEvent = db.table('Event')
        tableLastMonitoring = tableClientMonitoring.alias('LastMonitoring')
        tableLastEvent = tableEvent.alias('LastEvent')

        table = tableClient

        table = table.leftJoin(tableLastEvent, tableLastEvent['id'].eqStmt(
            db.selectMax(tableEvent,
                         tableEvent['id'],
                         [tableEvent['client_id'].eq(tableClient['id']),
                          tableEvent['deleted'].eq(0)])
        ))
        table = table.leftJoin(tableLastMonitoring, tableLastMonitoring['id'].eqStmt(
            db.selectMax(tableClientMonitoring,
                         tableClientMonitoring['id'],
                         [tableClientMonitoring['client_id'].eq(tableClient['id']),
                          tableClientMonitoring['deleted'].eq(0)])
        ))
        cols = [
            tableClient['id'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableClient['sex'],
            tableClient['IIN'],
            tableClient['SNILS'],
            tableClient['isUnconscious'],
            tableLastEvent['id'].alias('lastEventId'),
            tableLastEvent['nextEventDate'].alias('nextEventDate'),
            tableLastMonitoring['kind_id'].alias('lastMonKindId'),
            tableLastMonitoring['frequence_id'].alias('lastMonFrequenceId')
        ]
        self._table = table
        self._recordsCache = CTableRecordCache(db, table, cols, capacity=recordCacheCapacity)


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        column = index.column()
        row    = index.row()
        if role == QtCore.Qt.DisplayRole:  ### or role == Qt.EditRole:
            (col, values) = self.getRecordValues(column, row)
            return col.format(values)
        elif role == QtCore.Qt.TextAlignmentRole:
            col = self._cols[column]
            return col.alignment()
        elif role == QtCore.Qt.CheckStateRole:
            (col, values) = self.getRecordValues(column, row)
            return col.checked(values)
        elif role == QtCore.Qt.ForegroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getForegroundColor(values)
        elif role == QtCore.Qt.BackgroundRole:
            (col, values) = self.getRecordValues(column, row)
            idx = forceInt(self.getRecordByRow(row).value('id'))
            if idx in self.vipList:
                return QtCore.QVariant(QtGui.QColor(self.vipList[idx]))
            elif forceInt(self.getRecordByRow(row).value('isUnconscious')):
                col.color = self.unconsciousPatientRowColor
                return col.paintCell(values)
            return col.getBackgroundColor(values)
        elif role == QtCore.Qt.ToolTipRole:
            if column == 11 or column == 12:
                (col, values) = self.getRecordValues(column, row)
                return col.getCodeNameToolTip(values)
        return QtCore.QVariant()


class CClientsTableView(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            event.setAccepted(True)
            self.emit(QtCore.SIGNAL('requestNewEvent'))
            return
        CTableView.keyPressEvent(self, event)


class CEventsTableModel(CTableModel):
    class CLocClientColumn(CCol):
        def __init__(self, title, fields, defaultWidth, clientCache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.clientCache = clientCache

        def format(self, values):
            val = values[0]
            clientId  = forceRef(val)
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                name  = formatName(clientRecord.value('lastName'),
                                   clientRecord.value('firstName'),
                                   clientRecord.value('patrName'))
                return toVariant(name)
            return CCol.invalid

    class CLocClientBirthDateColumn(CCol):
        def __init__(self, title, fields, defaultWidth, clientCache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.clientCache = clientCache

        def getVariant(self, values):
            val = values[0]
            clientId = forceRef(val)
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return clientRecord.value('birthDate')
            return None

        def format(self, values):
            val = self.getVariant(values)
            if val is None:
                return CCol.invalid
            return toVariant(forceString(val))

        def formatNative(self, values):
            val = self.getVariant(values)
            if val is None:
                return CCol.invalid
            return forceDate(val)

    class CLocClientSexColumn(CCol):
        def __init__(self, title, fields, defaultWidth, clientCache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.clientCache = clientCache

        def format(self, values):
            val = values[0]
            clientId  = forceRef(val)
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return toVariant(formatSex(clientRecord.value('sex')))
            return CCol.invalid

    class CLocFinalDiagnosisColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

        def load(self, eventId):
            db = QtGui.qApp.db
            Diagnostic = db.table('Diagnostic')
            Diagnosis = db.table('Diagnosis')
            DiagnosisType = db.table('rbDiagnosisType')
            queryTable = Diagnostic.leftJoin(Diagnosis, Diagnosis['id'].eq(Diagnostic['diagnosis_id']))
            queryTable = queryTable.leftJoin(DiagnosisType, DiagnosisType['id'].eq(Diagnostic['diagnosisType_id']))
            cols = [
                Diagnosis['MKB'],
                DiagnosisType['name'].alias('type'),
                DiagnosisType['code']
            ]
            cond = [
                DiagnosisType['code'].inlist(['1', '2']),  # if not self.isFinally else DiagnosisType['code'].eq('1'),
                # заключительный, основной диагнозы
                Diagnostic['event_id'].eq(eventId),
                Diagnostic['deleted'].eq(0),
                Diagnosis['deleted'].eq(0)
            ]

            record = db.getRecordList(queryTable, cols, cond)
            if record:
                if len(record) > 1:
                    for x in record:
                        if forceString(x.value('code')) == '1':
                            self.putIntoCache(eventId, forceStringEx(x.value('MKB')))
                self.putIntoCache(eventId, forceStringEx(record[0].value('MKB')))
            else:
                self.putIntoCache(eventId, '')


    def __init__(self, parent, clientCache):
        CTableModel.__init__(self, parent, allowColumnsHiding=True)
        self.unpaidMXCache = {}
        self.dataChanged.connect(self.onDataChanged)
        self.connect(self, QtCore.SIGNAL('itemsCountChanged(int)'), self.onItemsCountChanged)
        clientCol   = CEventsTableModel.CLocClientColumn( u'Ф.И.О.', ['client_id'], 60, clientCache)
        clientBirthDateCol = CEventsTableModel.CLocClientBirthDateColumn(u'Дата рожд.', ['client_id'], 20, clientCache)
        clientSexCol = CEventsTableModel.CLocClientSexColumn(u'Пол', ['client_id'], 5, clientCache)
        finalMKBCol = CEventsTableModel.CLocFinalDiagnosisColumn(u'Код МКБ', ['id'], 5)
        address = CClientEvalCol(u'Адрес проживания', ['client_id'], 'getClientLocAddress(id)', 30)

        #3706
        if QtGui.qApp.isPNDDiagnosisMode():
            self.addColumn(clientCol)
            self.addColumn(clientBirthDateCol)
            self.addColumn(clientSexCol)
            self.addColumn(address)
            self.addColumn(CDateCol(u'Назначен', ['setDate'],  10))
            self.addColumn(CDateCol(u'Выполнен', ['execDate'], 10))
            self.addColumn(CRefBookCol(u'Тип',  ['eventType_id'], 'EventType', 15))
            self.addColumn(finalMKBCol)
            self.addColumn(CRefBookCol(u'Врач', ['execPerson_id'], 'vrbPersonWithSpeciality', 15))
            self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbResult', 40))
            self.loadField('createPerson_id')
            self.setTable('Event')
            self.diagnosisIdList = None
        else:
            self.addColumn(clientCol)
            self.addColumn(clientBirthDateCol)
            self.addColumn(clientSexCol)
            self.addColumn(address)
            self.addColumn(CDateCol(u'Назначен', ['setDate'],  10))
            self.addColumn(CDateCol(u'Выполнен', ['execDate'], 10))
            self.addColumn(CRefBookCol(u'Тип',  ['eventType_id'], 'EventType', 15))
            self.addColumn(finalMKBCol)
            self.addColumn(CRefBookCol(forceTr(u'МЭС', u'RegistryTable'),  ['MES_id'], 'mes.MES', 15, CRBComboBox.showCode))
            self.addColumn(CRefBookCol(u'Врач', ['execPerson_id'], 'vrbPersonWithSpeciality', 15))
            self.addColumn(CEnumCol(u'Первичный', ['isPrimary'], EventIsPrimary.nameList, 8))
            self.addColumn(CEnumCol(u'Порядок', ['order'], EventOrder().orderNameList, 8))
            # self.addColumn(CRefBookCol(u'Порядок', ['order'], 'rbEventOrder', 8))
            self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbResult', 40))
            self.addColumn(CTextCol(u'Внешний идентификатор', ['externalId'], 30))
            self.addColumn(CPayStatusColumn(u'Статус оплаты',  ['payStatus'],  20, 'l'))
            self.loadField('createPerson_id')
            self.setTable('Event')
            self.diagnosisIdList = None

    def onDataChanged(self, tl, br, roles):
        self.unpaidMXCache = {}

    def onItemsCountChanged(self, count):
        self.unpaidMXCache = {}

    def removeRow(self, row, parent = QtCore.QModelIndex()):
        if self._idList and 0<=row<len(self._idList):
            itemId = self._idList[row]
            if self.canRemoveEvent(itemId):
                return CTableModel.removeRow(self, row, parent)
        return False

    def canRemoveEvent(self, itemId):
        result = True
        if self.hasActionsWithTissue(itemId):
            result = result and canRemoveEventWithTissue()
        elif self.hasActionsWithJobTicket(itemId):
            result = result and canRemoveEventWithJobTicket()
        return result

    def canRemoveItem(self, eventId):
        userId = QtGui.qApp.userId
        canRemoveAll = QtGui.qApp.userHasRight(urDeleteNotOwnEvents)
        canRemoveMineRight = QtGui.qApp.userHasRight(urDeleteOwnEvents)
        record = self.getRecordById(eventId)
        canRemoveMine = (userId == forceRef(record.value('createPerson_id')) \
                            or userId == forceRef(record.value('execPerson_id'))) \
                        and canRemoveMineRight
        tableAccountItem = QtGui.qApp.db.table('Account_Item')
        accountItemCond = [
            tableAccountItem['event_id'].eq(eventId),
            tableAccountItem['deleted'].eq(0)
        ]
        notAccounts = QtGui.qApp.db.getCount(tableAccountItem, 'id', accountItemCond) == 0
        return (canRemoveAll or canRemoveMine) and notAccounts

    def hasActionsWithTissue(self, itemId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        cond = [tableAction['event_id'].eq(itemId),
                tableAction['takenTissueJournal_id'].isNotNull()]
        return bool(db.getCount(tableAction, where=cond))

    def hasActionsWithJobTicket(self, itemId):
        db = QtGui.qApp.db
        cnt = db.getCount(stmt=u'''SELECT COUNT(*) 
                                   FROM Action a 
                                     INNER JOIN ActionProperty ap ON a.id = ap.action_id
                                     INNER JOIN ActionProperty_Job_Ticket apjt ON ap.id = apjt.id
                                   WHERE a.event_id = %d''' % itemId)
        return bool(cnt)


    def afterRemoveItem(self, itemId):
        QtGui.qApp.emitCurrentClientInfoChanged()

    def deleteRecord(self, table, itemId):
        record = self.getRecordById(itemId)
        if record.indexOf(CDocumentTable.dtfDeleted)<0:
            record.append(QtSql.QSqlField(CDocumentTable.dtfDeleted, QtCore.QVariant.Int))

        record.setValue(CDocumentTable.dtfDeleted, 1)
        QtGui.qApp.db.updateRecord(table, record)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundRole:
            rec = self.getRecordByRow(index.row())
            eventId = forceRef(rec.value('id'))
            if eventId in self.unpaidMXCache:
                if self.unpaidMXCache[eventId]:
                    return QtGui.QBrush(QtGui.QColor(232, 189, 230))
            else:
                if eventId:
                    if hasUnpaidMXActions(eventId):
                        self.unpaidMXCache[eventId] = True
                        return QtGui.QBrush(QtGui.QColor(232, 189, 230))
                    else:
                        self.unpaidMXCache[eventId] = False
                else:
                    self.unpaidMXCache[eventId] = False
        return super(CEventsTableModel, self).data(index, role)


class CEventsTableView(CTableView):
    def __init__(self, parent):
        CTableView.__init__(self, parent)

    def removeCurrentRow(self):
        def removeCurrentRowInternal():
            index = self.currentIndex()
            itemIdList = self.model().idList()
            row = self.currentIndex().row()
            if itemIdList:
                eventId = itemIdList[row]
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                if db.getRecordEx(tableEvent, [tableEvent['id']], [tableEvent['prevEvent_id'].eq(eventId), tableEvent['deleted'].eq(0)]):
                    QtGui.QMessageBox.warning(self, u'Внимание!', u'Событие имеет продолжение, поэтому не может быть удалено.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return
                tableDrugRecipe = db.table('DrugRecipe')
                if db.getRecordEx(tableDrugRecipe, [tableDrugRecipe['id']], [tableDrugRecipe['event_id'].eq(eventId), tableDrugRecipe['sentToMiac'].eq(1)]):
                    QtGui.QMessageBox.warning(self, u'Внимание!', u'Удаление невозможно. В обращении присутствует льготный рецепт, синхронизированный с ПЦ МИАЦ.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return
                if index.isValid() and self.confirmRemoveRow(row):
                    row = self.currentIndex().row()
                    self.model().removeRow(row)
                    self.setCurrentRow(row)
        QtGui.qApp.call(self, removeCurrentRowInternal)


class CEventDiagnosticsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        # 3706
        if QtGui.qApp.isPNDDiagnosisMode():
            col = self.addColumn(CDateCol(u'Установлен', ['endDate'], 10))
            self.addColumn(CRefBookCol(u'Тип', ['diagnosisType_id'], 'rbDiagnosisType', 6))
            col.setToolTip(u'Группа здоровья')
            self.addColumn(CDiagnosisCol(u'Диагноз', ['diagnosis_id'], 6))
            col = self.addColumn(CMKBTextCol(u'Расш. МКБ', ['diagnosis_id'], 10))
            col.setToolTip(u'Расшифровка МКБ')
            self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPerson', 6))
            self.addColumn(CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 6))
            self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbDiagnosticResult', 6))
            self.addColumn(CTextCol(u'Примечания', ['notes'], 6))
            self.setTable('Diagnostic')
        else:
            col = self.addColumn(CDateCol(u'Установлен', ['endDate'], 10))
            self.addColumn(CRefBookCol(u'Тип', ['diagnosisType_id'], 'rbDiagnosisType', 6))
            col = self.addColumn(CRefBookCol(u'ГpЗд', ['healthGroup_id'], 'rbHealthGroup', 2, CRBComboBox.showCode))
            col.setToolTip(u'Группа здоровья')
            self.addColumn(CDiagnosisCol(u'Диагноз', ['diagnosis_id'], 6))
            if QtGui.qApp.defaultMorphologyMKBIsVisible():
                col = self.addColumn(CMorphologyMKBCol(u'Морф.', ['diagnosis_id'], 8))
                col.setToolTip(u'Морфология диагноза МКБ')
            col = self.addColumn(CRefBookCol(u'Хар', ['character_id'], 'rbDiseaseCharacter', 6))
            col.setToolTip(u'Характер')
            col = self.addColumn(CRefBookCol(u'Фаза', ['phase_id'], 'rbDiseasePhases', 6))
            col.setToolTip(u'Фаза')
            col = self.addColumn(CRefBookCol(u'Ст', ['stage_id'], 'rbDiseaseStage', 6))
            col.setToolTip(u'Стадия')
            col = self.addColumn(CRefBookCol(
                u'ДН', ['dispanser_id'], 'rbDispanser', 6, CRBComboBox.showCode))
            col.setToolTip(u'Диспансерное наблюдение')
            col = self.addColumn(CTextCol(u'Госп', ['hospital'], 4))
            col.setToolTip(u'Госпитализация')
            col = self.addColumn(CRefBookCol(
                u'Тр', ['traumaType_id'], 'rbTraumaType', 6, CRBComboBox.showCode))
            col.setToolTip(u'Тип травмы')
            self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPerson', 6))
            self.addColumn(CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 6))
            self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbDiagnosticResult', 6))
            self.addColumn(CTextCol(u'Примечания', ['notes'], 6))
            self.setTable('Diagnostic')


class CPayStatusColumn(CCol):
    def format(self, values):
        payStatus = forceInt(values[0])
        return toVariant(payStatusText(payStatus))


class CMKBDesignationCol(CDesignationCol):
    def getValues(self, values):
        if values[0] is None:
            return [CCol.invalid] * len(values)
        for cache in self._caches:
            itemId  = forceString(values[0])
            if not itemId:
                itemId = None
            record = cache.get(itemId)
            if not record:
                return [CCol.invalid] * len(values)
            else:
                values = [record.value(idx) for idx in xrange(record.count())]
        return values


class CEventActionsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CDateCol(u'Назначено',      ['directionDate'], 15))
        self.addColumn(CBoolCol(u'Срочно',         ['isUrgent'],      15))
        self.addColumn(CDateCol(u'План',           ['plannedEndDate'],15))
        self.addColumn(CDateCol(u'Начато',         ['begDate'],       15))
        self.addColumn(CDateCol(u'Окончено',       ['endDate'],       15))
        self.addColumn(CActionTypeCol(u'Тип',                         15))
        self.addColumn(CEnumCol(u'Состояние',      ['status'], CActionType.retranslateClass(False).statusNames, 4))
        self.addColumn(CRefBookCol(u'Назначил',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],    'vrbPersonWithSpeciality', 20))
        self.addColumn(CTextCol(u'Каб',            ['office'],                                6))
        self.addColumn(CTextCol(u'Примечания',     ['note'],                                  6))
        self.addColumn(CTextCol(u'МКБ',            ['MKB'],            5))
        self.addColumn(CMKBDesignationCol(u'Название диагноза', ['MKB'], ('MKB', 'DiagName', 'DiagID'), 20))
        self.addColumn(CRefBookCol(u'Стандарт',    ['MES_id'], 'mes.MES', 20, showFields=CRBComboBox.showCodeAndName))
        self.addColumn(CPayStatusColumn(u'Оплата', ['payStatus'], 20, 'l'))
        self.setTable('Action')


class CEventVisitsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CRefBookCol(u'Место',       ['scene_id'],         'rbScene',    15))
        self.addColumn(CDateCol(u'Дата',           ['date'],                           15))
        self.addColumn(CRefBookCol(u'Тип',         ['visitType_id'],    'rbVisitType', 15))
        self.addColumn(CRefBookCol(u'Услуга',      ['service_id'],      'rbService',   15))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],     'vrbPersonWithSpeciality', 20))
        self.addColumn(CEnumCol(u'Первичный', ['isPrimary'], EventIsPrimary.nameList, 4, 'l'))
        self.addColumn(CPayStatusColumn(u'Оплата', ['payStatus'], 20, 'l'))
        self.setTable('Visit')


class CEventAccActionsTableModel(CTableModel):
    class CLocContractCol(CCol):
        def __init__(self, title, fields, defaultWidth, alignment='l'):
            CCol.__init__(self, title, fields, defaultWidth, alignment)

        def format(self, values):
            contractId = forceRef(values[0])
            if contractId:
                names = ['number', 'date', 'resolution']
                record = QtGui.qApp.db.getRecord('Contract', names, contractId)
                string = ' '.join([forceString(record.value(name)) for name in names])
            else:
                string = u'не задано'
            return QtCore.QVariant(string)

    class CLocPriceSumCol(CCol):
        def __init__(self, pricesAndSums, title, fields, defaultWidth, alignment='r', isPriceCol = True):
            CCol.__init__(self, title, fields, defaultWidth, alignment)
            self.pricesAndSums = pricesAndSums
            self.colNumber = 0 if isPriceCol else 1

        def format(self, values):
            id = forceRef(values[0])
            return QtCore.QVariant('%.2f' % self.pricesAndSums[id][self.colNumber])

    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.pricesAndSums = {}
        self.totalSum = 0.0
        self.paymentSum = 0.0
        self.eventTypeId = None
        self.clientAge = None
        self.clientSex = None
        self.contractTariffCache = CContractTariffCache()
        self.addColumn(CActionTypeCol(u'Тип', 15))
        self.addColumn(CRefBookCol(u'Тип финансирования',  ['finance_id'],  'rbFinance', 10))
        self.addColumn(CEventAccActionsTableModel.CLocContractCol(u'Договор', ['contract_id'], 20))
        self.addColumn(CNumCol(u'Кол-во', ['amount'], 10))
        self.addColumn(CEventAccActionsTableModel.CLocPriceSumCol(self.pricesAndSums, u'Цена', ['id'], 10))
        self.addColumn(CEventAccActionsTableModel.CLocPriceSumCol   (self.pricesAndSums, u'Сумма', ['id'], 10, isPriceCol=False))
        self.addColumn(CPayStatusColumn(u'Оплата', ['payStatus'], 10, 'l'))
        self.addColumn(CTextCol(u'Примечания', ['note'], 20))
        self.loadField('person_id')
        self.loadField('event_id')
        self.setTable('Action')
        self.isChangeItems = False

    def setIdList(self, idList, realItemCount=None, **params):
        eventId = params.get('eventId', 0)

        if eventId > 0 and not self.isChangeItems:
            db = QtGui.qApp.db
            self.payedActionIdList = [
                forceRef(x.value('id'))
                for x in db.getRecordList(table=None, stmt=u"""
                            SELECT
                              a.id
                            FROM
                              Action a
                              INNER JOIN ActionType at ON a.actionType_id = at.id
                              INNER JOIN Account_Item ai ON a.id = ai.action_id
                              INNER JOIN Account ac ON ac.id = ai.master_id
                            WHERE
                              a.event_id = %s
                              AND ac.sum = ac.payedSum
                              AND ai.deleted = 0 
                              AND a.deleted = 0 
                              AND ac.deleted = 0
                              AND ai.refuseType_id IS NULL
                        """ % eventId
                        )
            ]
        else:
            self.isChangeItems = False
            self.payedActionIdList = None

        self.getAdditionalInfo(eventId)
        CTableModel.setIdList(self, idList, realItemCount)
        self.totalSum = 0
        self.paymentSum = 0.0
        self.getPricesAndSums(idList)

    def getPricesAndSums(self, idList):
        for id in idList:
            record = self.getRecordById(id)
            actionTypeId = forceRef(record.value('actionType_id'))
            if actionTypeId:
                personId = forceRef(record.value('person_id'))
                contractId = forceRef(record.value('contract_id'))
                tariffCategoryId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'tariffCategory_id'))
                if not contractId:
                    eventId = forceRef(record.value('event_id'))
                    contractId = forceRef(QtGui.qApp.db.translate('Event', 'id', eventId, 'contract_id'))
                financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
                serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
                tariffMap = self.contractTariffCache.getTariffDescr(contractId, self).actionTariffMap
                price = CContractTariffCache.getPrice(tariffMap, serviceIdList, tariffCategoryId)
            else:
                price = 0.0
            amount = forceDouble(record.value('amount'))
            sum = price * amount
            self.pricesAndSums[id] = (price, sum)
            self.totalSum += sum

            # z
            if self.payedActionIdList is None:
                if getPayStatusMask(financeId) == forceInt(record.value('payStatus')):
                    self.paymentSum += sum
            else:
                if id in self.payedActionIdList:
                    self.paymentSum += sum
                    if getPayStatusMask(financeId) != forceInt(record.value('payStatus')):
                        stmt = u'UPDATE Action SET payStatus = %s WHERE id=%d''' % \
                               (getPayStatusMask(financeId),  id)
                        QtGui.qApp.db.query(stmt)
                        self.isChangeItems = True

    def getAdditionalInfo(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableClient = db.table('Client')
            tableEvent = db.table('Event')
            table = tableClient.innerJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableEvent['id'].eq(eventId)]
            cols = [tableClient['birthDate'], tableClient['sex'], tableEvent['eventType_id'], tableEvent['setDate']]
            record = db.getRecordEx(table, cols, cond)
            clientBirthDate = forceDate(record.value('birthDate'))
            eventDate = forceDate(record.value('setDate'))
            self.clientSex = forceInt(record.value('sex'))
            self.eventTypeId = forceRef(record.value('eventType_id'))
            self.clientAge = calcAgeTuple(clientBirthDate, eventDate)
        else:
            self.eventTypeId = None
            self.clientAge = None
            self.clientSex = None

    def getEventTypeId(self):
        return self.eventTypeId

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)

    def sum(self):
        return self.totalSum

    def getPaymentSum(self):
        return self.paymentSum


class CAmbCardDiagnosticsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPerson', 6))
        self.addColumn(CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 6))
        self.addColumn(CDateCol(u'Установлен', ['endDate'], 10))
        self.addColumn(CRefBookCol(u'Тип', ['diagnosisType_id'], 'rbDiagnosisType', 6))
        col = self.addColumn(CRefBookCol(u'ГpЗд', ['healthGroup_id'], 'rbHealthGroup', 2, CRBComboBox.showCode))
        col.setToolTip(u'Группа здоровья')
        self.addColumn(CDiagnosisCol(u'Диагноз', ['diagnosis_id'], 6))
        col = self.addColumn(CRefBookCol(u'Хар', ['character_id'], 'rbDiseaseCharacter', 6))
        col.setToolTip(u'Характер')
        col = self.addColumn(CRefBookCol(u'Фаза', ['phase_id'], 'rbDiseasePhases', 6))
        col.setToolTip(u'Фаза')
        col = self.addColumn(CRefBookCol(u'Ст', ['stage_id'], 'rbDiseaseStage', 6))
        col.setToolTip(u'Стадия')
        col = self.addColumn(CRefBookCol(u'ДН', ['dispanser_id'], 'rbDispanser', 6, CRBComboBox.showCode))
        col.setToolTip(u'Диспансерное наблюдение')
        col = self.addColumn(CTextCol(u'Госп', ['hospital'], 4))
        col.setToolTip(u'Госпитализация')
        col = self.addColumn(CRefBookCol(u'Тр', ['traumaType_id'], 'rbTraumaType', 6, CRBComboBox.showCode))
        col.setToolTip(u'Тип травмы')
        self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbDiagnosticResult', 6))
        self.addColumn(CTextCol(u'Примечания', ['notes'], 6))
        self.setTable('Diagnostic')


class CAmbCardDiagnosticsVisitsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CRefBookCol(u'Место',       ['scene_id'],         'rbScene',    15))
        self.addColumn(CDateCol(u'Дата',           ['date'],                           15))
        self.addColumn(CRefBookCol(u'Тип',         ['visitType_id'],    'rbVisitType', 15))
        self.addColumn(CRefBookCol(u'Услуга',      ['service_id'],      'rbService',   15))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],     'vrbPersonWithSpeciality', 20))
        self.addColumn(CEnumCol(u'Первичный', ['isPrimary'], EventIsPrimary.nameList, 4, 'l'))
        self.addColumn(CDateCol(u'Дата ввода',     ['createDatetime'],                 15))
        self.addColumn(CDateCol(u'Дата изменения', ['modifyDatetime'],                 15))
        self.setTable('Visit')


class CAmbCardDiagnosticsAccompDiagnosticsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPerson', 6))
        self.addColumn(CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 6))
        self.addColumn(CDateCol(u'Установлен', ['endDate'], 10))
        self.addColumn(CRefBookCol(u'Тип', ['diagnosisType_id'], 'rbDiagnosisType', 6))
        col = self.addColumn(CRefBookCol(u'ГpЗд', ['healthGroup_id'], 'rbHealthGroup', 2, CRBComboBox.showCode))
        col.setToolTip(u'Группа здоровья')
        self.addColumn(CDiagnosisCol(u'Диагноз', ['diagnosis_id'], 6))
        col = self.addColumn(CRefBookCol(u'Хар', ['character_id'], 'rbDiseaseCharacter', 6))
        col.setToolTip(u'Характер')
        col = self.addColumn(CRefBookCol(u'Фаза', ['phase_id'], 'rbDiseasePhases', 6))
        col.setToolTip(u'Фаза')
        col = self.addColumn(CRefBookCol(u'Ст', ['stage_id'], 'rbDiseaseStage', 6))
        col.setToolTip(u'Стадия')
        col = self.addColumn(CRefBookCol(u'ДН', ['dispanser_id'], 'rbDispanser', 6, CRBComboBox.showCode))
        col.setToolTip(u'Диспансерное наблюдение')
        col = self.addColumn(CTextCol(u'Госп', ['hospital'], 4))
        col.setToolTip(u'Госпитализация')
        col = self.addColumn(CRefBookCol(u'Тр', ['traumaType_id'], 'rbTraumaType', 6, CRBComboBox.showCode))
        col.setToolTip(u'Тип травмы')
        self.addColumn(CRefBookCol(u'Результат', ['result_id'], 'rbDiagnosticResult', 6))
        self.addColumn(CTextCol(u'Примечания', ['notes'], 6))
        self.setTable('Diagnostic')


class CAmbCardDiagnosticsActionsTableModel(CTableModel):
    ActionTypeColIndex = 1

    def __init__(self, parent):
        CTableModel.__init__(self, parent,  cols=[
            CDateCol(u'Назначено', ['directionDate'], 15),
            CActionTypeCol(u'Тип', 15),
            CBoolCol(u'Срочно', ['isUrgent'], 15),
            CEnumCol(u'Состояние', ['status'], CActionType.retranslateClass(False).statusNames, 4),
            CDateCol(u'План', ['plannedEndDate'], 15),
            CDateCol(u'Начато', ['begDate'], 15),
            CDateCol(u'Окончено', ['endDate'], 15),
            CRefBookCol(u'Назначил', ['setPerson_id'], 'vrbPersonWithSpeciality', 20),
            CRefBookCol(u'Выполнил', ['person_id'], 'vrbPersonWithSpeciality', 20),
            CTextCol(u'Каб', ['office'], 6),
            CTextCol(u'Примечания', ['note'], 6)
        ], tableName='Action')


class CAmbCardStatusActionsTableModel(CAmbCardDiagnosticsActionsTableModel):
    pass


class CAnalysesActionsMixin(object):
    def __init__(self):
        self._actionMap = {}
        self._mainActionTypes = set(getMainActionTypesAnalyses())
        boldFont = QtGui.QFont()
        boldFont.setWeight(QtGui.QFont.Bold)
        self._boldFontVariant = toVariant(boldFont)

    def isMainActionType(self, actionTypeId):
        return actionTypeId in self._mainActionTypes

    @staticmethod
    def getActionChildrenMap(actionIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')

        actionMap = {}
        if actionIdList:
            for rec in db.iterRecordList(tableAction, ['id', 'parent_id'], tableAction['id'].inlist(actionIdList)):
                actionId = forceRef(rec.value('id'))
                parentId = forceRef(rec.value('parent_id'))
                if actionId and parentId:
                    actionMap.setdefault(parentId, []).append(actionId)
        return actionMap


class CAmbCardAnalysesActionsTableModel(CAmbCardDiagnosticsActionsTableModel, CAnalysesActionsMixin):
    u""" Отображение анализов аналогично ActionsAnalysesModel """

    def __init__(self, parent):
        CAnalysesActionsMixin.__init__(self)
        CAmbCardDiagnosticsActionsTableModel.__init__(self, parent)
        self.loadField('parent_id')

    def formatActionTypeAnalyses(self, values):
        actionTypeId = forceRef(values[0])
        specifiedName = forceString(values[1])
        if actionTypeId:
            col = self.cols()[self.ActionTypeColIndex]
            prefix = '' if self.isMainActionType(actionTypeId) else ' ' * 10
            actionName = col.data.getStringById(actionTypeId, col.showFields) + (' ' + specifiedName if specifiedName else '')
            return QtCore.QVariant(prefix + actionName)
        return CCol.invalid

    def setIdList(self, idList, realItemCount=None, resetCache=True):
        super(CAmbCardAnalysesActionsTableModel, self).setIdList(idList, realItemCount, resetCache)
        self._actionMap = self.getActionChildrenMap(idList)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, column = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            return self.formatActionTypeAnalyses(values)

        elif role == QtCore.Qt.FontRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            actionTypeId = forceRef(values[0])
            if self.isMainActionType(actionTypeId):
                return self._boldFontVariant

        return super(CAmbCardAnalysesActionsTableModel, self).data(index, role)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        u""" Сортировка главных действий, сортировка внутри группы """
        id2row = dict((id, idx) for idx, id in enumerate(self._idList))

        def sortHelper(row):
            col, values = self.getRecordValues(column, row)
            return col.formatNative(values)

        def sortedIdList(idList, order):
            return sorted(idList,
                          key=lambda id: sortHelper(id2row[id]),
                          reverse=order==QtCore.Qt.DescendingOrder)

        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self._idList and not self._isSorted:
            sortedList = list(chain.from_iterable(
                [parentId] + sortedIdList(self._actionMap[parentId], order)
                for parentId in sortedIdList(self._actionMap.keys(), order)
            ))
            self.setIdList(sortedList, resetCache=False)
            self._isSorted = True


class CRegistryActionsTableView(CTableView):

    def setClientInfoHidden(self, hideClientInfo):
        verticalHeaderView = self.verticalHeader()
        h = self.fontMetrics().height()
        if hideClientInfo:
            verticalHeaderView.setDefaultSectionSize(3*h/2)
            verticalHeaderView.hide()
        else:
            verticalHeaderView.setDefaultSectionSize(3*h)
            verticalHeaderView.show()

    def contentToHTML(self, columnRoleList=None, titles = None, fontSize = 8):
        model = self.model()
        cols = model.cols()
        if columnRoleList is None:
            columnRoleList = [None]*(len(cols)+1)
        _showMask = [ not self.isColumnHidden(iCol) if v is None else v
                      for iCol, v in enumerate(columnRoleList)
                    ]
        QtGui.qApp.startProgressBar(model.rowCount())
        try:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            cursor.setCharFormat(CReportBase.ReportTitle)
            header = self.reportHeader()
            if QtCore.Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            description = self.reportDescription()
            if QtCore.Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            colWidths  = [ self.columnWidth(i) for i in xrange(len(cols)+1) ]
            colWidths.insert(0,10)
            totalWidth = sum(colWidths)
            tableColumns = []
            for iCol, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth*90/totalWidth))+'%'
                if iCol == 0:
                    tableColumns.append((widthInPercents, [u'№'], CReportBase.AlignRight))
                elif iCol == 1:
                    tableColumns.append((widthInPercents, [u'ФИО'], CReportBase.AlignLeft))
                else:
                    if not _showMask[iCol-2]:
                        continue
                    col = cols[iCol-2]
                    colAlingment = QtCore.Qt.AlignHorizontal_Mask & forceInt(col.alignment())
                    format = QtGui.QTextBlockFormat()
                    format.setAlignment(QtCore.Qt.AlignmentFlag(colAlingment))
                    tableColumns.append((widthInPercents, [forceString(col.title())], format))

            table = createTable(cursor, tableColumns)
            for iModelRow in xrange(model.rowCount()):
                QtGui.qApp.stepProgressBar()
                QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                iTableRow = table.addRow()
                table.setText(iTableRow, 0, iModelRow+1)
                headerData = model.headerData(iTableRow-1, QtCore.Qt.Vertical)
                table.setText(iTableRow, 1, forceString(headerData))
                iTableCol = 2
                for iModelCol in xrange(len(cols)):
                    if not _showMask[iModelCol]:
                        continue
                    index = model.createIndex(iModelRow, iModelCol)
                    text = forceString(model.data(index))
                    table.setText(iTableRow, iTableCol, text)
                    iTableCol += 1
            return doc
        finally:
            QtGui.qApp.stopProgressBar()


class CActionsTableModel(CTableModel):
    class CLocClientColumn(CEventsTableModel.CLocClientColumn):
        def __init__(self, title, fields, defaultWidth, clientCache, eventCache):
            CEventsTableModel.CLocClientColumn.__init__(self, title, fields, defaultWidth, clientCache)
            self.eventCache = eventCache

        def formatShortNameInt(self, lastName, firstName, patrName):
            return forceStringEx(lastName + ' ' +((firstName[:1]) if firstName else '') + ((patrName[:1]) if patrName else ''))

        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                clientValues = [eventRecord.value('client_id')]
                clientVal = clientValues[0]
                clientId  = forceRef(clientVal)
                clientRecord = self.clientCache.get(clientId)
                if clientRecord:
                    name  = self.formatShortNameInt(forceString(clientRecord.value('lastName')),
                                       forceString(clientRecord.value('firstName')),
                                       forceString(clientRecord.value('patrName')))
                    return toVariant(name)
                return CCol.invalid
            return CCol.invalid

    class CLocClientIdentifierColumn(CCol):
        def __init__(self, title, fields, defaultWidth, eventCache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.eventCache = eventCache
            self.identifiersCache = CRecordCache()


        def getClientIdentifier(self, clientId):
            identifier = self.identifiersCache.get(clientId)
            if identifier is None:
                accountingSystemId = QtGui.qApp.defaultAccountingSystemId()
                if accountingSystemId is None:
                    identifier = clientId
                else:
                    db = QtGui.qApp.db
                    tableClientIdentification = db.table('ClientIdentification')
                    cond = [tableClientIdentification['client_id'].eq(clientId),
                            tableClientIdentification['accountingSystem_id'].eq(accountingSystemId)]
                    record = db.getRecordEx(tableClientIdentification, tableClientIdentification['identifier'], cond)
                    identifier = forceString(record.value(0)) if record else ''
                self.identifiersCache.put(clientId, identifier)
            return identifier

        def format(self, values):
            val = values[0]
            eventId = forceRef(val)
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                clientId = forceRef(eventRecord.value('client_id'))
                return toVariant(self.getClientIdentifier(clientId))
            return CCol.invalid

    class CLocClientBirthDateColumn(CEventsTableModel.CLocClientBirthDateColumn):
        def __init__(self, title, fields, defaultWidth, clientCache, eventCache):
            CEventsTableModel.CLocClientBirthDateColumn.__init__(self, title, fields, defaultWidth, clientCache)
            self.eventCache = eventCache

        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                return CEventsTableModel.CLocClientBirthDateColumn.format(self, [eventRecord.value('client_id')])
            return CCol.invalid

    class CLocClientSexColumn(CEventsTableModel.CLocClientSexColumn):
        def __init__(self, title, fields, defaultWidth, clientCache, eventCache):
            CEventsTableModel.CLocClientSexColumn.__init__(self, title, fields, defaultWidth, clientCache)
            self.eventCache = eventCache

        def format(self, values):
            val = values[0]
            eventId  = forceRef(val)
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                return CEventsTableModel.CLocClientSexColumn.format(self, [eventRecord.value('client_id')])
            return CCol.invalid

    ActionTypeColIndex = 1

    def __init__(self, parent, clientCache, eventCache):
        CTableModel.__init__(self, parent)
        self.clientCol   = CActionsTableModel.CLocClientColumn( u'Ф.И.О.', ['event_id'], 60, clientCache, eventCache)
        self.clientIdentifierCol = CActionsTableModel.CLocClientIdentifierColumn(u'Идентификатор', ['event_id'], 30, eventCache)
        self.clientBirthDateCol = CActionsTableModel.CLocClientBirthDateColumn(u'Дата рожд.', ['event_id'], 20, clientCache, eventCache)
        self.clientSexCol = CActionsTableModel.CLocClientSexColumn(u'Пол', ['event_id'], 5, clientCache, eventCache)
        self.addColumn(CDateCol(u'Назначено',      ['directionDate'], 15))
        self.addColumn(CActionTypeCol(u'Тип',                         15))
        self.addColumn(CBoolCol(u'Срочно',         ['isUrgent'],      15))
        self.addColumn(CEnumCol(u'Состояние',      ['status'], CActionType.retranslateClass(False).statusNames, 4))
        self.addColumn(CDateCol(u'План',           ['plannedEndDate'],15))
        self.addColumn(CDateCol(u'Начато',         ['begDate'],       15))
        self.addColumn(CDateCol(u'Окончено',       ['endDate'],       15))
        self.addColumn(CRefBookCol(u'Назначил',    ['setPerson_id'], 'vrbPersonWithSpeciality', 20))
        self.addColumn(CRefBookCol(u'Выполнил',    ['person_id'],    'vrbPersonWithSpeciality', 20))
        self.addColumn(CTextCol(u'Каб',            ['office'],                                6))
        self.addColumn(CTextCol(u'Примечания',     ['note'],                                  6))
        self.loadField('id')
        self.loadField('event_id')
        self.loadField('amount')
        self.setTable('Action')

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                id = self._idList[section]
                self._recordsCache.weakFetch(id, self._idList[max(0, section-self.fetchSize):(section+self.fetchSize)])
                record = self._recordsCache.get(id)
                clientValues   = self.clientCol.extractValuesFromRecord(record)
                clientValue = forceString(self.clientCol.format(clientValues))
                clientIdentifierValues = self.clientIdentifierCol.extractValuesFromRecord(record)
                clientIdentifier = forceString(self.clientIdentifierCol.format(clientIdentifierValues))
                clientBirthDateValues = self.clientBirthDateCol.extractValuesFromRecord(record)
                clientBirthDate = forceString(self.clientBirthDateCol.format(clientBirthDateValues))
                clientSexValues = self.clientSexCol.extractValuesFromRecord(record)
                clientSex = forceString(self.clientSexCol.format(clientSexValues))
                clientFIOSex = u', '.join([clientValue, clientSex])
                birthDateSex = u', '.join([clientIdentifier, clientBirthDate])
                result =  u'\n'.join([clientFIOSex, birthDateSex])
                return QtCore.QVariant(result)
        return CTableModel.headerData(self, section, orientation, role)

    def getAmountSum(self):
        result = 0
        for id in self.idList():
            record = self.recordCache().get(id)
            result += forceDouble(record.value('amount'))
        return result


class CActionsAnalysesTableModel(CActionsTableModel, CAnalysesActionsMixin):
    u""" Отображение анализов аналогично CAmbCardAnalysesActionsTableModel """

    def __init__(self, parent, clientCache, eventCache):
        CAnalysesActionsMixin.__init__(self)
        CActionsTableModel.__init__(self, parent, clientCache, eventCache)
        self.loadField('parent_id')

    def formatActionTypeAnalyses(self, values):
        actionTypeId = forceRef(values[0])
        specifiedName = forceString(values[1])
        if actionTypeId:
            col = self.cols()[self.ActionTypeColIndex]
            prefix = '' if self.isMainActionType(actionTypeId) else ' ' * 10
            actionName = col.data.getStringById(actionTypeId, col.showFields) + (' ' + specifiedName if specifiedName else '')
            return QtCore.QVariant(prefix + actionName)
        return CCol.invalid

    def setIdList(self, idList, realItemCount=None, resetCache=True):
        super(CActionsAnalysesTableModel, self).setIdList(idList, realItemCount, resetCache)
        self._actionMap = self.getActionChildrenMap(idList)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, column = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            return self.formatActionTypeAnalyses(values)

        elif role == QtCore.Qt.FontRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            actionTypeId = forceRef(values[0])
            if self.isMainActionType(actionTypeId):
                return self._boldFontVariant

        return super(CActionsAnalysesTableModel, self).data(index, role)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        u""" Сортировка главных действий, сортировка внутри группы """
        id2row = dict((id, idx) for idx, id in enumerate(self._idList))

        def sortHelper(row):
            col, values = self.getRecordValues(column, row)
            return col.formatNative(values)

        def sortedIdList(idList, order):
            return sorted(idList,
                          key=lambda id: sortHelper(id2row[id]),
                          reverse=order==QtCore.Qt.DescendingOrder)

        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self._idList and not self._isSorted:
            sortedList = list(chain.from_iterable(
                [parentId] + sortedIdList(self._actionMap[parentId], order)
                for parentId in sortedIdList(self._actionMap.keys(), order)
            ))
            self.setIdList(sortedList, resetCache=False)
            self._isSorted = True


class CExpertTempInvalidTableModel(CTableModel):
    class CPrevCol(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.recordCache = None

        def format(self, values):
            id = forceRef(values[0])
            record = self.recordCache.get(id) if self.recordCache and id else None
            if record:
                return QtCore.QVariant(forceString(record.value('number')))
            return CCol.invalid

    def __init__(self, parent, clientCache):
        CTableModel.__init__(self, parent)
        clientCol   = CEventsTableModel.CLocClientColumn( u'Ф.И.О.', ['client_id'], 60, clientCache)
        clientBirthDateCol = CEventsTableModel.CLocClientBirthDateColumn(u'Дата рожд.', ['client_id'], 20, clientCache)
        clientSexCol = CEventsTableModel.CLocClientSexColumn(u'Пол', ['client_id'], 5, clientCache)
        self.addColumn(clientCol)
        self.addColumn(clientBirthDateCol)
        self.addColumn(clientSexCol)
        self.addColumn(CBoolCol(u'СтСт',      ['insuranceOfficeMark'],                  6))
        # self.addColumn(CTextCol(u'Серия',     ['serial'],                               6))
        self.addColumn(CTextCol(u'Номер',     ['number'],                               6))
        self.addColumn(CRefBookCol(u'Причина нетрудоспособности',    ['tempInvalidReason_id'], 'rbTempInvalidReason', 15))
        self.addColumn(CDateCol(u'Дата начала ВУТ', ['caseBegDate'],                 10))
        self.addColumn(CDateCol(u'Начало',    ['begDate'],                           12))
        self.addColumn(CDateCol(u'Окончание', ['endDate'],                           12))
        self.addColumn(CRefBookCol(u'Врач',   ['person_id'], 'vrbPerson',             6))
        self.addColumn(CDesignationCol(u'МКБ',['diagnosis_id'], ('Diagnosis', 'MKB'), 6))
        colPrevDoc = CExpertTempInvalidTableModel.CPrevCol(u'Предыдущий документ', ['prev_id'], 15)
        self.addColumn(colPrevDoc)
        self.addColumn(CEnumCol(u'Состояние', ['closed'], [u'открыт', u'закрыт', u'продлён', u'передан'], 4))
        self.addColumn(CNumCol(u'Длительность', ['duration'],                        10))
        self.addColumn(CTextCol(u'Примечания',['notes'],                               6))
        # self.addColumn(CRefBookCol(u'Тип',    ['doctype_id'], 'rbTempInvalidDocument', 15))
        self.setTable('TempInvalid')
        colPrevDoc.recordCache = self.recordCache()


class CExpertTempInvalidPeriodsTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CRefBookCol(u'Открыл',           ['begPerson_id'], 'vrbPerson', 6))
        self.addColumn(CDateCol(   u'Дата открытия',    ['begDate'], 10))
        self.addColumn(CRefBookCol(u'Закрыл',           ['endPerson_id'], 'vrbPerson', 6))
        self.addColumn(CDateCol(   u'Дата закрытия',    ['endDate'], 10))
        self.addColumn(CBoolCol(   u'Внешний',          ['isExternal'], 10))
        self.addColumn(CRefBookCol(u'Режим',            ['regime_id'], 'rbTempInvalidRegime', 15))
        self.addColumn(CRefBookCol(u'Результат периода',['result_id'], 'rbTempInvalidResult', 15))
        self.addColumn(CTextCol(   u'Примечания',       ['note'], 6))
        self.setTable('TempInvalid_Period')


class CExpertTempInvalidDuplicatesTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CBoolCol(u'СтСт',      ['insuranceOfficeMark'],                6))
        # self.addColumn(CTextCol(u'Серия',     ['serial'],                             6))
        self.addColumn(CTextCol(u'Номер',     ['number'],                             6))
        self.addColumn(CDateCol(u'Дата',      ['date'],                              12))
        self.addColumn(CRefBookCol(u'Выдал',  ['person_id'], 'vrbPerson',             6))
        self.setTable('TempInvalidDuplicate')


class CClientFilesTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Название файла', ['name'],    50))
        self.setTable('ClientFile')

    def updateContents(self):
        clientId = QtGui.qApp.currentClientId()
        idList = QtGui.qApp.db.getIdList('ClientFile', where = 'client_id = %d' % clientId) if clientId else []
        self.setIdList(idList)


class CIsActualCol(CCol):
    def format(self, values):
        record = values[-1]
        return toVariant(u'да' if recommendationIsActual(record) else u'')


class CSumCol(CNumCol):
    def format(self, values):
        return toVariant(forceDouble(values[0]) * forceDouble(values[1]))

class CFIOClientCol(CTextCol):
    def format(self, values):
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        record = db.getRecordEx(tblClient,'*', tblClient['id'].eq(forceInt(values[0])))
        if record:
            return toVariant(forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')))

class CFIOPersonCol(CTextCol):
    def format(self, values):
        db = QtGui.qApp.db
        tblClient = db.table('Person')
        record = db.getRecordEx(tblClient,'*', tblClient['id'].eq(forceInt(values[0])))
        if record:
            return toVariant(forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')))

class CBirthDateCol(CCol):
    def formatNative(self, values):
        val = values[0]
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        record = db.getRecordEx(tblClient,tblClient['birthDate'], tblClient['id'].eq(forceInt(val)))
        if record and record.value('birthDate').type() in (QVariant.Date, QVariant.DateTime):
            return pyDate(record.value('birthDate').toDate())
        return datetime.date(datetime.MINYEAR, 1, 1)

    def format(self, values):
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        record = db.getRecordEx(tblClient,tblClient['birthDate'], tblClient['id'].eq(forceInt(values[0])))
        if record:
            return toVariant(forceString(record.value('birthDate')))

class COrgCol(CCol):
    def format(self, values):
        db = QtGui.qApp.db
        tblOrganisation = db.table('Organisation')
        record = db.getRecordEx(tblOrganisation, tblOrganisation['shortName'], tblOrganisation['id'].eq(forceInt(values[0])))
        if record:
            return toVariant(record.value('shortName'))


class CRecommendationsModel(CTableModel, CAnalysesRecommendationMixin):
    ActionTypeColIndex = 4

    def __init__(self, parent):
        CAnalysesRecommendationMixin.__init__(self)
        CTableModel.__init__(self, parent)
        self.addColumn(CIsActualCol(u'Актуально', ['amount_left', 'expireDate', 'person2_id'], 13, alignment='l'))
        self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPersonWithSpeciality', 35))
        self.addColumn(CRefBookCol(u'Снял актуальность', ['person2_id'], 'vrbPersonWithSpeciality', 35))
        self.addColumn(CDateCol(u'Дата рекомендации', ['setDate'], 20))
        self.addColumn(CRefBookCol(u'Рекомендация', ['actionType_id'], 'ActionType', 70, showFields=CRBComboBox.showCodeAndName))
        self.addColumn(CNumCol(u'Цена', ['price'], 20))
        self.addColumn(CNumCol(u'Количество', ['amount'], 20))
        self.addColumn(CNumCol(u'Осталось', ['amount_left'], 20))
        self.addColumn(CSumCol(u'Сумма', ['amount', 'price'], 20))
        self.addColumn(CDateCol(u'Актуально до', ['expireDate'], 20))
        self.setTable('Recommendation')

    def formatActionTypeAnalyses(self, values):
        actionTypeId = forceRef(values[0])
        if actionTypeId:
            col = self.cols()[self.ActionTypeColIndex]
            prefix = '' if self.isMainActionTypeAnalyses(actionTypeId) else ' ' * 10
            actionName = col.data.getStringById(actionTypeId, col.showFields)
            return QtCore.QVariant(prefix + actionName)
        return CCol.invalid

    def setIdList(self, idList, realItemCount=None, resetCache=True):
        idList = self.resetAnalyses(idList, resetCache)
        super(CRecommendationsModel, self).setIdList(idList, realItemCount, resetCache)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        id2row = dict((id, idx) for idx, id in enumerate(self._idList))

        def sortHelper(row):
            col, values = self.getRecordValues(column, row)
            return col.formatNative(values)

        def sortedIdList(idList, order):
            return sorted(idList,
                          key=lambda id: sortHelper(id2row[id]),
                          reverse=order == QtCore.Qt.DescendingOrder) if idList else []

        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False

        if self._idList and not self._isSorted:
            nonAnalysesIdList = list(set(self._idList).difference(self._analysesRecommendations))
            groupedAnalyses = set(chain.from_iterable([groupId] + children
                                                      for groupId, children in self._analysesRecommendationMap.iteritems()))
            notGroupedAnalyses = list(self._analysesRecommendations.difference(groupedAnalyses))

            sortedList = list(chain.from_iterable(
                [recId] + sortedIdList(self._analysesRecommendationMap.get(recId, []), order)
                for recId in sortedIdList(nonAnalysesIdList + notGroupedAnalyses + self._analysesRecommendationMap.keys(), order)
            ))

            self.setIdList(sortedList, resetCache=False)
            self._isSorted = True

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, column = index.row(), index.column()
        if role == QtCore.Qt.DisplayRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            recommendationId = self.idList()[row]
            if self.isAnalysesRecommendation(recommendationId):
                return self.formatActionTypeAnalyses(values)

        elif role == QtCore.Qt.FontRole and column == self.ActionTypeColIndex:
            (col, values) = self.getRecordValues(column, row)
            actionTypeId = forceRef(values[0])
            if self.isMainActionTypeAnalyses(actionTypeId):
                return self._mainAnalysesActionTypeFont

        return super(CRecommendationsModel, self).data(index, role)

    def flags(self, index = QtCore.QModelIndex()):
        flags = super(CRecommendationsModel, self).flags(index)
        if index.isValid():
            record = self.getRecordByRow(index.row())
            if flags & QtCore.Qt.ItemIsSelectable:
                flags ^= QtCore.Qt.ItemIsSelectable
            if recommendationIsActual(record):
                flags |= QtCore.Qt.ItemIsSelectable
        return flags

    def updateContents(self):
        clientId = QtGui.qApp.currentClientId()
        idList = QtGui.qApp.db.getIdList('Recommendation', where='setEvent_id in (SELECT id FROM Event WHERE client_id = %d) and deleted = 0' % clientId, order='setDate DESC') if clientId else []
        self.setIdList(idList)


class CInputReferralsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)

        self.addColumn(CTextCol(u'Номер', ['number'], 13))
        self.addColumn(CDateCol(u'Дата выдачи', ['date'], 35))
        self.addColumn(CDateCol(u'Планируемая дата', ['hospDate'], 35))
        self.addColumn(CRefBookCol(u'Тип направления', ['type'], 'rbReferralType', 40))
        self.addColumn(COrgCol(u'Направившая МО', ['relegateOrg_id'], 20, 'l'))
        self.addColumn(CRefBookCol(u'Профиль койки', ['hospBedProfile_id'], 'rbHospitalBedProfile', 70, showFields=CRBComboBox.showCodeAndName))
        self.addColumn(CFIOClientCol(u'ФИО пациента', ['client_id'], 20, 'l'))
        self.addColumn(CBirthDateCol(u'Дата рождения', ['client_id'], 20, 'l'))
        self.addColumn(CBoolCol(u'Аннулировано', ['isCancelled'], 20))
        self.addColumn(CDateCol(u'Дата аннулирования', ['cancelDate'], 20))
        self.addColumn(CRefBookCol(u'Причина аннулирования', ['cancelReason'], 'rbCancellationReason', 30))
        self.addColumn(CBoolCol(u'Имеет обращение', ['event_id'], 20))
        self.setTable('Referral')

    def updateContents(self):
        idList = QtGui.qApp.db.getIdList('Referral', where='isSend = 0 and deleted = 0', order='date DESC')
        self.setIdList(idList)

    def setFilter(self, filter):
        tblRef = QtGui.qApp.db.table('Referral')
        tblClient = QtGui.qApp.db.table('Client')
        tblReferral = tblRef.innerJoin(tblClient, tblRef['client_id'].eq(tblClient['id']))
        idList = QtGui.qApp.db.getIdList(tblReferral, idCol=tblRef['id'], where=filter, order='date DESC')
        self.setIdList(idList)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            record = self.getRecordByRow(row)
            if record:
                if forceInt(self.getRecordByRow(row).value('isCancelled')):
                    return toVariant(QtGui.QColor(255, 204, 204))
        return CTableModel.data(self, index, role)

class COutgoingReferralsModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Номер', ['number'], 13))
        self.addColumn(CDateCol(u'Дата выдачи', ['date'], 35))
        self.addColumn(CDateCol(u'Планируемая дата', ['hospDate'], 35))
        self.addColumn(CRefBookCol(u'Тип направления', ['type'], 'rbReferralType', 40))
        self.addColumn(COrgCol(u'Направлен в', ['relegateOrg_id'], 20, 'l'))
        self.addColumn(CRefBookCol(u'Профиль койки', ['hospBedProfile_id'], 'rbHospitalBedProfile', 70, showFields=CRBComboBox.showCodeAndName))
        self.addColumn(CFIOClientCol(u'ФИО пациента', ['client_id'], 20, 'l'))
        self.addColumn(CBirthDateCol(u'Дата рождения', ['client_id'], 20, 'l'))
        self.addColumn(CBoolCol(u'Аннулировано', ['isCancelled'], 20))
        self.addColumn(CDateCol(u'Дата аннулирования', ['cancelDate'], 20))
        self.addColumn(CRefBookCol(u'Причина аннулирования', ['cancelReason'], 'rbCancellationReason', 30))
        self.addColumn(CDateCol(u'Дата госпитализации', ['relMoHospDate'], 20))
        self.setTable('Referral')

    def updateContents(self):
        idList = QtGui.qApp.db.getIdList('Referral', where='isSend = 1 and deleted = 0', order='date DESC')
        self.setIdList(idList)

    def setFilter(self, filter):
        tblRef = QtGui.qApp.db.table('Referral')
        tblClient = QtGui.qApp.db.table('Client')
        tblReferral = tblRef.innerJoin(tblClient, tblRef['client_id'].eq(tblClient['id']))
        idList = QtGui.qApp.db.getIdList(tblReferral, idCol=tblRef['id'], where=filter, order='date DESC')
        self.setIdList(idList)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = self.cols()[index.column()]
        row = index.row()
        if role == QtCore.Qt.BackgroundColorRole:
            record = self.getRecordByRow(row)
            if record:
                if forceInt(self.getRecordByRow(row).value('isCancelled')):
                    return toVariant(QtGui.QColor(255, 204, 204))
        return CTableModel.data(self, index, role)
