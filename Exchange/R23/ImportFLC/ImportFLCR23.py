# -*- coding: utf-8 -*-

import Queue
import copy
import os
import threading
import time
from PyQt4 import QtCore, QtGui
from zipfile import ZipFile, is_zipfile

from Exchange.R23.ImportFLC.Ui_ImportFLCR23 import Ui_Dialog
from Exchange.R23.attach.Utils import CBookkeeperCode
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewOrientation
from library.DialogBase import CDialogBase
from library.Utils import databaseFormatSex, forceDate, forceDateTime, forceInt, forceRef, forceString, formatName, \
    formatSNILS, formatSex, getPref, nameCase, \
    setPref, toVariant, unformatSNILS
from library.dbfpy.dbf import CDbf

KRASNODAR_OKATO = '03000'
CHUNK_SIZE = 1000


class FLCStatus:
    FoundInRegionalSegment = 0
    NotFoundInRS_Incorrect = 1
    NotFoundInRS_SentToCS = 2
    FoundInCentralSegment = 3
    NotFoundInCS = 4


class FLCError:
    NoPolicy = 10
    NoInsurer = 11
    WrongClient = 12
    NonKrasnodar = 13
    IsLittleStranger = 14
    NoAttach_Or_AttachedToExternal = 15

    nameMap = {
        FLCStatus.FoundInRegionalSegment: u'Человек идентифицирован в РС ЕРЗ',
        FLCStatus.NotFoundInRS_Incorrect: u'Человек не идентифицирован в РС ЕРЗ, не отправлено в ЦС ЕРЗ (предоставлены неполные или некорректные персональные данные)',
        FLCStatus.NotFoundInRS_SentToCS : u'Человек не идентифицирован в РС ЕРЗ, отправлено в ЦС ЕРЗ',
        FLCStatus.FoundInCentralSegment : u'Человек идентифицирован в ЦС ЕРЗ',
        FLCStatus.NotFoundInCS          : u'Человек не идентифицирован в ЦС ЕРЗ',
        NonKrasnodar                    : u'Человек найден как инокраевой, в качестве СМО будет указан ТФОМС',
        NoPolicy                        : u'В обращении пациента не привязан полис',
        NoInsurer                       : u'В полисе пациента не указана страховая компания',
        WrongClient                     : u'Обращение принадлежит другому пациенту',
        IsLittleStranger                : u'Пациент является новорожденным, к обращению будет подвязан полис представителя',
        NoAttach_Or_AttachedToExternal  : u'У пациента не указано прикрепление; пациент прикреплен к другой МО',
    }


class FLCSpecialCase:
    LittleStranger = '2'


class CCheckThread(threading.Thread):
    _clientPersonalCheckFields = [
        ('lastName', 'FIOF'),
        ('firstName', 'IMAF'),
        ('patrName', 'OTCHF'),
        ('birthDate', 'DATRF'),
        ('sex', 'POLF'),
        ('SNILS', 'SNILSF')
    ]

    _clientPolicyBaseCheckFields = [
        ('kindCode', 'SPVF'),
        ('serial', 'SPSF'),
        ('number', 'SPNF')
    ]

    def __init__(self, sqlDataQueue, clientUpdateQueue, littleStrangerQueue, insurerMap):
        threading.Thread.__init__(self, name='checkTthread')
        self.sqlDataQueue = sqlDataQueue
        self.clientUpdateQueue = clientUpdateQueue
        self.littleStrangerQueue = littleStrangerQueue
        self.insurerMap = insurerMap

    @staticmethod
    def _formatValue(field, value):
        if value and field in ('birthDate', 'begDate', 'endDate'):
            return forceDate(value) if value else QtCore.QDate()
        elif value and field == 'SNILS':
            return unformatSNILS(value)
        elif value and field in ('lastName', 'firstName', 'patrName'):
            return nameCase(forceString(value).strip())
        elif value and field == 'kindCode':
            return forceString(value)
        else:
            return forceString(value).strip()

    @staticmethod
    def getNameTuple(dict, fields):
        return tuple(map(lambda field: nameCase(dict[field].strip()), fields))

    def run(self):
        while True:
            checkData = self.sqlDataQueue.get()
            if checkData is not None:
                dbfEventMap, sqlDataList = checkData
                for eventId, clientData, policyData in sqlDataList:
                    dbfRecord = dbfEventMap[eventId]

                    client = ClientData(clientData,
                                        dbfRecord['OKATO_OMSF'] and dbfRecord['OKATO_OMSF'] != KRASNODAR_OKATO,
                                        FLCSpecialCase.LittleStranger in dbfRecord['Q_G'])
                    policy = ClientPolicyData(policyData, [eventId])

                    sqlName = self.getNameTuple(client, ('lastName', 'firstName', 'patrName'))
                    dbfName = self.getNameTuple(dbfRecord, ('FIO', 'IMA', 'OTCH'))
                    dbfNameF = self.getNameTuple(dbfRecord, ('FIOF', 'IMAF', 'OTCHF'))

                    if not (sqlName == dbfName and client['birthDate'] == forceDate(dbfRecord['DATR'])) and \
                            not (sqlName == dbfNameF and client['birthDate'] == forceDate(dbfRecord['DATRF'])):
                        client.setError(FLCError.WrongClient, {
                            'clientId': client['id'], 'eventId': eventId,
                            'sqlName' : formatName(*sqlName), 'sqlSex': client['sex'], 'sqlBDate': forceString(client['birthDate'].toString('dd.MM.yyyy')),
                            'sqlSNILS': formatSNILS(client['SNILS']),
                            'dbfName' : formatName(*dbfName), 'dbfSex': dbfRecord['POL'],
                            'dbfBDate': forceString(forceDate(dbfRecord['DATR']).toString('dd.MM.yyyy')), 'dbfSNILS': dbfRecord['SNILS']
                        })
                        self.clientUpdateQueue.put(client)
                        continue

                    clientHasPersonalChanges = dbfNameF != (u'', u'', u'')
                    for sqlField, dbfField in self._clientPersonalCheckFields:
                        sqlValue = self._formatValue(sqlField, client[sqlField])
                        dbfValue = self._formatValue(sqlField, dbfRecord[dbfField])
                        if (dbfValue and sqlValue != dbfValue) or \
                                (sqlField == 'patrName' and clientHasPersonalChanges and sqlValue and not dbfValue):
                            client.addChange(sqlField, dbfValue)

                    for sqlField, dbfField in self._clientPolicyBaseCheckFields:
                        sqlValue = self._formatValue(sqlField, policy[sqlField])
                        dbfValue = self._formatValue(sqlField, dbfRecord[dbfField])

                        if (sqlField == 'number' and dbfValue and sqlValue != dbfValue) or \
                                (sqlField == 'serial' and ((sqlValue and not dbfValue) or (dbfValue and dbfValue != sqlValue))) or \
                                (sqlField == 'kindCode' and not (sqlValue == '' and dbfValue == '0') and (sqlValue != dbfValue)):
                            policy.addChange(sqlField, dbfValue)

                    policyBaseFieldChangesCount = policy.changesCount

                    sqlBegDate, dbfBegDate = policy['begDate'], forceDate(dbfRecord['DATNP'])
                    changeBegDate = not dbfBegDate.isNull() and dbfBegDate != sqlBegDate
                    if changeBegDate:
                        policy.addChange('begDate', dbfBegDate)

                    sqlEndDate, dbfEndDate = policy['endDate'], forceDate(dbfRecord['DATOP'])
                    changeEndDate = (not dbfEndDate.isNull() and dbfEndDate != sqlEndDate) or \
                                    (not sqlEndDate.isNull() and dbfEndDate.isNull())
                    if changeEndDate:
                        policy.addChange('endDate', dbfEndDate)

                    sqlOGRN, dbfOGRN = policy['OGRN'], dbfRecord['PL_OGRNF']
                    changeOGRN = dbfOGRN and dbfOGRN != sqlOGRN or dbfRecord['PL_OGRN'] != dbfRecord['PL_OGRNF']
                    if changeOGRN:
                        policy.addChange('OGRN', dbfOGRN)

                    sqlOKATO = policy['OKATO']
                    dbfOKATO = dbfRecord['OKATO_OMSF'] or dbfRecord['OKATO_OMS']
                    policy.changeOKATO = (dbfOKATO and dbfOKATO != sqlOKATO)
                    if policy.changeOKATO:
                        policy.addChange('OKATO', dbfOKATO)

                    policy.changeInsurer = (changeOGRN or policy.changeOKATO) and (dbfOGRN, dbfOKATO) in self.insurerMap

                    if policy.changeInsurer or changeBegDate or policyBaseFieldChangesCount > 1:
                        policy.setNew()

                    if not (client.personalChanges or policy.changes):
                        continue

                    if policy.changes:
                        client.addPolicy(policy)

                    self.clientUpdateQueue.put(client)

                time.sleep(1)
            else:
                break

        self.clientUpdateQueue.put(None)


class ClientData(object):
    _checkMsg = {
        'lastName' : u'фамилии',
        'firstName': u'имени',
        'patrName' : u'отчества',
        'birthDate': u'даты рождения',
        'sex'      : u'пола',
        'SNILS'    : u'СНИЛС'
    }

    def __init__(self, sqlData, isExternal=False, isLittleStranger=False):
        self.id = sqlData.get('id')
        self.data = sqlData
        self.newData = copy.deepcopy(sqlData)
        self.changes = {}
        self.policies = []
        self.isExternal = isExternal
        self.isLittleStranger = isLittleStranger
        self.error = {}

    def addChange(self, sqlField, value):
        self.changes[sqlField] = value
        self.newData[sqlField] = value

    def setError(self, code, errorMsg):
        self.error[code] = errorMsg

    @property
    def personalChanges(self):
        return self.changes

    @property
    def changesMessage(self):
        return u'\n'.join(u'Несоответствие {field}: {old}/{new}'.format(
            field=self._checkMsg[field], old=forceString(self.data[field]), new=forceString(newValue)
        ) for field, newValue in self.changes.iteritems())

    def addPolicy(self, policy):
        self.policies.append(policy)

    def __iter__(self):
        return self.policies.__iter__()

    def __contains__(self, policy):
        if isinstance(policy, ClientPolicyData):
            for p in self.policies:
                if p.newData == policy.newData and p.data == policy.data:
                    return True
        return False

    def __getitem__(self, sqlField):
        return self.data[sqlField]


class ClientPolicyData(object):
    _checkMsg = {
        'OGRN'    : u'ОГРН',
        'OKATO'   : u'ОКАТО',
        'serial'  : u'серии полиса',
        'number'  : u'номера полиса',
        'kindCode': u'типа полиса',
        'begDate' : u'даты начала',
        'endDate' : u'даты окончания'
    }

    def __init__(self, sqlData, eventdIdList=None):
        self._id = sqlData.get('id')
        self.data = sqlData
        self.newData = copy.deepcopy(sqlData)
        self.changes = {}
        self.eventIdList = eventdIdList or []
        self.changeInsurer = False
        self.changeOKATO = False

    def setNew(self):
        self.id = None
        self.newData['id'] = None

    def addChange(self, sqlField, newValue):
        self.changes[sqlField] = newValue
        self.newData[sqlField] = newValue

    @property
    def changesCount(self):
        return len(self.changes)

    @property
    def changesMessage(self):
        changeList = [u'Новый полис:'] if self._id is None else []
        return u'\n'.join(changeList + [u'Несоответствие {field}: {oldValue}/{newValue}'.format(
            field=self._checkMsg[field], oldValue=forceString(self.data[field]), newValue=forceString(newValue)
        ) for field, newValue in self.changes.iteritems()])

    def appendEvent(self, eventId):
        self.eventIdList.append(eventId)

    def __getitem__(self, sqlField):
        return self.data[sqlField]


def putTask(dbfFileName, dbfDataQueue, clientErrorQueue):
    notFoundMap = {
        FLCStatus.NotFoundInRS_Incorrect       : {},
        FLCStatus.NotFoundInRS_SentToCS        : {},
        FLCStatus.NotFoundInCS                 : {},
        FLCError.NonKrasnodar                  : {},
        FLCError.NoAttach_Or_AttachedToExternal: {}
    }
    with CDbf(dbfFileName, 'r', encoding='cp866') as dbf:
        for dbfRecord in dbf:
            if dbfRecord.deleted:
                continue

            status = dbfRecord['CS']  # статус
            eventId = dbfRecord['SN']  # eventId

            if not status in (FLCStatus.FoundInRegionalSegment,
                              FLCStatus.FoundInCentralSegment):
                notFoundMap[status][eventId] = dbfRecord
                continue

            TF_OKATO = dbfRecord['OKATO_OMSF']
            if TF_OKATO and TF_OKATO != KRASNODAR_OKATO:
                notFoundMap[FLCError.NonKrasnodar][eventId] = dbfRecord

            attachOrgCode = dbfRecord['PRIK_MO']
            if not attachOrgCode or CBookkeeperCode.isExternalOrgCode(attachOrgCode):
                notFoundMap[FLCError.NoAttach_Or_AttachedToExternal][eventId] = dbfRecord

            dbfDataQueue.put(dbfRecord)

    dbfDataQueue.put(None)

    for errCode, errDict in notFoundMap.iteritems():
        clientErrorQueue.put((errCode, errDict))


def query(db, fileCount, dbfDataQueue, sqlDataQueue):
    def selectEventDataList(eventIdList):
        Client = db.table('Client')
        ClientPolicy = db.table('ClientPolicy')
        Event = db.table('Event')
        Insurer = db.table('Organisation').alias('Insurer')
        PolicyKind = db.table('rbPolicyKind')
        PolicyType = db.table('rbPolicyType')

        cols = [
            Client['id'].alias('clientId'),
            Client['lastName'], Client['firstName'], Client['patrName'],
            Client['birthDate'],
            Client['sex'],
            Client['SNILS'],
            Client['notes'],
            ClientPolicy['id'].alias('policyId'),
            ClientPolicy['serial'], ClientPolicy['number'],
            ClientPolicy['begDate'], ClientPolicy['endDate'],
            ClientPolicy['createDatetime'].alias('createDatetime'),
            PolicyKind['code'].alias('kindCode'),
            ClientPolicy['insurer_id'].alias('insurerId'),
            Insurer['OGRN'],
            Insurer['OKATO'],
            Event['id'].alias('eventId')
        ]

        table = Event.innerJoin(Client, Client['id'].eq(Event['client_id']))
        table = table.leftJoin(ClientPolicy, [ClientPolicy['id'].eq(Event['clientPolicy_id']),
                                              ClientPolicy['deleted'].eq(0)])
        table = table.leftJoin(PolicyKind, PolicyKind['id'].eq(ClientPolicy['policyKind_id']))
        table = table.leftJoin(PolicyType, [PolicyType['id'].eq(ClientPolicy['policyType_id']),
                                            db.joinOr([PolicyType['name'].like(u'ОМС%%'),
                                                       PolicyType['id'].isNull()])])
        table = table.leftJoin(Insurer, Insurer['id'].eq(ClientPolicy['insurer_id']))

        cond = [
            Event['id'].inlist(eventIdList),
            Event['deleted'].eq(0)
        ]

        order = [
            Client['id'],
            Event['id'],
            ClientPolicy['id'].desc(),
            ClientPolicy['begDate']
        ]

        return db.iterRecordList(table, cols, cond, order=order)

    def getEventDataList(eventIdList):
        return [
            (
                forceInt(record.value('eventId')),
                {
                    'id'       : forceInt(record.value('clientId')),
                    'lastName' : forceString(record.value('lastName')),
                    'firstName': forceString(record.value('firstName')),
                    'patrName' : forceString(record.value('patrName')),
                    'birthDate': forceDate(record.value('birthDate')),
                    'sex'      : formatSex(forceInt(record.value('sex'))),
                    'SNILS'    : forceString(record.value('SNILS')),
                    'notes'    : forceString(record.value('notes'))
                },
                {
                    'id'            : forceRef(record.value('policyId')),
                    'createDatetime': forceDateTime(record.value('createDatetime')),
                    'number'        : forceString(record.value('number')),
                    'serial'        : forceString(record.value('serial')),
                    'kindCode'      : forceString(record.value('kindCode')),
                    'begDate'       : forceDate(record.value('begDate')),
                    'endDate'       : forceDate(record.value('endDate')),
                    'insurerId'     : forceRef(record.value('insurerId')),
                    'OGRN'          : forceString(record.value('OGRN')),
                    'OKATO'         : forceString(record.value('OKATO'))
                }
            )
            for record in selectEventDataList(eventIdList)
        ]

    dbfEventMap = {}

    i = 0
    while i < fileCount:
        dbfRecord = dbfDataQueue.get()
        if dbfRecord is not None:
            if len(dbfEventMap.keys()) >= CHUNK_SIZE:
                sqlDataQueue.put((dbfEventMap, getEventDataList(dbfEventMap.keys())))
                dbfEventMap = {}
            dbfEventMap[dbfRecord['SN']] = dbfRecord
            continue
        if dbfEventMap:
            sqlDataQueue.put((dbfEventMap, getEventDataList(dbfEventMap.keys())))
        i += 1

    for _ in xrange(4):
        sqlDataQueue.put(None)


class CImportFLC(CDialogBase, Ui_Dialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.setupUi(self)

        self.db = QtGui.qApp.db

        self.policyKindCodeMap = {}
        self.clientUpdateMap = {}
        self.insurerMap = self.getInsurerMap()

        self.CompulsoryPolicyTypeId = forceRef(self.db.translate('rbPolicyType', 'code', u'1', 'id'))

        self.ImportNote = u'Импорт ФЛК от {0}'.format(forceString(QtCore.QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm:ss')))
        self.ImportNoteUpdate = u'{0} (обновлён)'.format(self.ImportNote)
        self.ImportNoteNew = u'{0} (новый)'.format(self.ImportNote)

        self.CheckThreadCount = 4

        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.resetRecordCount()
        self.logBrowser.setVisible(False)

        self._kladr_okato_map = {}

    def loadPreferences(self, preferences):
        self.edtFileName.setText(forceString(getPref(preferences, 'ImportFLCFileName', '')))
        return CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        preferences = CDialogBase.savePreferences(self)
        setPref(preferences, 'ImportFLCFileName', toVariant(self.edtFileName.text()))
        return preferences

    def getInsurerMap(self):
        u""" map: (OGRN, OKATO) -> Organisation.id """
        tableInsurer = self.db.table('Organisation')
        cols = [
            tableInsurer['id'],
            tableInsurer['OGRN'],
            tableInsurer['OKATO']
        ]
        cond = [
            tableInsurer['isInsurer'].eq(1),
            tableInsurer['compulsoryServiceStop'].eq(0),
            tableInsurer['OGRN'].ne(u''),
            tableInsurer['OKATO'].ne(u''),
            self.db.joinOr([
                tableInsurer['head_id'].isNull(),
                tableInsurer['head_id'].eq(tableInsurer['id'])
            ]),
            tableInsurer['deleted'].eq(0),
        ]
        order = [
            tableInsurer['head_id']
        ]

        return dict(
            ((forceString(rec.value('OGRN')), forceString(rec.value('OKATO'))),
             forceRef(rec.value('id')))
            for rec in self.db.iterRecordList(tableInsurer, cols, cond, order=order)
        )

    @staticmethod
    def createErrorTable(cursor):
        tableColumns = [
            ('5?', [u'Код обращения'], CReportBase.AlignLeft),
            ('5?', [u'Код пациента'], CReportBase.AlignLeft),
            ('25?', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('5?', [u'Пол'], CReportBase.AlignCenter),
            ('10?', [u'Дата рождения'], CReportBase.AlignCenter),
            ('10?', [u'СНИЛС'], CReportBase.AlignLeft),
            ('15?', [u'Код МО прикрепления'], CReportBase.AlignCenter),
            ('15?', [u'Дата прикрепления'], CReportBase.AlignCenter)
        ]
        table = createTable(cursor, tableColumns)
        return table

    @staticmethod
    def createClientErrorTable(cursor, errorCode, errorList):
        if errorCode == FLCError.WrongClient:
            tableColumns = [
                ('5?', [u'Код обращения'], CReportBase.AlignLeft),
                ('5?', [u'Код пациента'], CReportBase.AlignLeft),
                ('15?', [u'Пациент в базе данных', u'ФИО'], CReportBase.AlignLeft),
                ('5?', [u'', u'Пол'], CReportBase.AlignLeft),
                ('5?', [u'', u'Дата рождения'], CReportBase.AlignLeft),
                ('5?', [u'', u'СНИЛС'], CReportBase.AlignLeft),
                ('15?', [u'Пациент в файле импорта', u'ФИО'], CReportBase.AlignLeft),
                ('5?', [u'', u'Пол'], CReportBase.AlignLeft),
                ('5?', [u'', u'Дата рождения'], CReportBase.AlignLeft),
                ('5?', [u'', u'СНИЛС'], CReportBase.AlignLeft)
            ]
            table = createTable(cursor, tableColumns)
            table.mergeCells(0, 0, 2, 1)
            table.mergeCells(0, 1, 2, 1)
            table.mergeCells(0, 2, 1, 4)
            table.mergeCells(0, 6, 1, 4)

            rows = {}
            for error in errorList:
                rows[error['eventId']] = (error['eventId'], error['clientId'],
                                          error['sqlName'], error['sqlSex'], error['sqlBDate'], error['sqlSNILS'],
                                          error['dbfName'], error['dbfSex'], error['dbfBDate'], error['dbfSNILS'])
            for eventId in sorted(rows.keys()):
                i = table.addRow()
                for j, text in enumerate(rows[eventId]):
                    table.setText(i, j, text)

        cursor.movePosition(cursor.End)
        cursor.insertBlock(CReportBase.AlignLeft)

    def createProtocol(self, krasnodarClientsRows, externalClientsRows, clientWithErrors, clientErrorQueue):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        format = QtGui.QTextCharFormat()

        charFormatTitle = QtGui.QTextCharFormat()
        charFormatTitle.setFontPointSize(16)
        charFormatTitle.setFontWeight(QtGui.QFont.Bold)

        charFormatSubTitle = QtGui.QTextCharFormat()
        charFormatSubTitle.setFontPointSize(12)
        charFormatSubTitle.setFontWeight(QtGui.QFont.Bold)

        charFormatBody = QtGui.QTextCharFormat()
        charFormatBody.setFontWeight(8)

        charFormatBodyBold = QtGui.QTextCharFormat()
        charFormatBodyBold.setFontWeight(8)
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)

        cursor.setCharFormat(charFormatTitle)
        cursor.insertText(u'Протокол форматно-логического контроля')
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.setCharFormat(charFormatBody)
        cursor.insertBlock()

        tableColumns = [
            ('5?', [u'№'], CReportBase.AlignCenter),
            ('10?', [u'Код пациента'], CReportBase.AlignLeft),
            ('25?', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('10?', [u'Дата рождения'], CReportBase.AlignRight),
            ('25?', [u'Изменения в паспортной части'], CReportBase.AlignLeft),
            ('10?', [u'SN'], CReportBase.AlignLeft),
            ('25?', [u'Изменения полисов'], CReportBase.AlignLeft)
        ]
        cursor.setCharFormat(charFormatBody)

        if krasnodarClientsRows or externalClientsRows:
            table = createTable(cursor, tableColumns, charFormat=charFormatBodyBold)

            def printClientRow(idx, row):
                clientId, name, birthDate, personalChanges, policies = row
                rowCount = max(1, sum(len(policyEvents) for policyChanges, policyEvents in policies))

                lastRow = 0
                for _ in xrange(rowCount):
                    lastRow = table.addRow()
                firstRow = lastRow - rowCount + 1

                table.setText(firstRow, 0, idx + 1)
                table.setText(firstRow, 1, clientId)
                table.setText(firstRow, 2, name)
                table.setText(firstRow, 3, birthDate)
                table.setText(firstRow, 4, personalChanges)

                for col in xrange(5):
                    table.mergeCells(firstRow, col, rowCount, 1)

                policyRow = firstRow
                for policyChanges, policyEvents in policies:
                    table.setText(policyRow, 6, policyChanges)
                    table.mergeCells(policyRow, 6, len(policyEvents), 1)

                    for eventId in policyEvents:
                        table.setText(policyRow, 5, eventId)
                        policyRow += 1

            if krasnodarClientsRows:
                i = table.addRow()
                table.mergeCells(i, 0, 1, len(tableColumns))
                table.setText(i, 0, u'Краевые пациенты', charFormat=charFormatSubTitle)

                cursor.setCharFormat(charFormatBody)

                for idx, row in enumerate(krasnodarClientsRows):
                    printClientRow(idx, row)

            if externalClientsRows:
                i = table.addRow()
                table.mergeCells(i, 0, 1, len(tableColumns))
                table.setText(i, 0, u'Инокраевые пациенты', charFormat=charFormatSubTitle)

                cursor.setCharFormat(charFormatBody)

                for idx, row in enumerate(externalClientsRows):
                    printClientRow(idx, row)

            format.setFontWeight(QtGui.QFont.Normal)
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock(CReportBase.AlignLeft)

            for errCode, errList in clientWithErrors.iteritems():
                if errList and errCode in FLCError.nameMap:
                    cursor.insertBlock()
                    cursor.insertBlock()
                    cursor.setCharFormat(charFormatBodyBold)
                    cursor.insertText(FLCError.nameMap[errCode])
                    cursor.insertBlock()
                    self.createClientErrorTable(cursor, errCode, errList)

            while clientErrorQueue.qsize():
                errCode, eventErrorMap = clientErrorQueue.get()
                if eventErrorMap:
                    cursor.insertBlock()
                    cursor.insertBlock()

                    cursor.setCharFormat(charFormatBodyBold)
                    cursor.insertText(FLCError.nameMap[errCode])

                    cursor.insertBlock()
                    cursor.setCharFormat(charFormatBody)

                    errorTableData = []

                    eventClientMap = self.selectEventClientMap(eventErrorMap.keys())
                    for eventId in eventErrorMap:
                        dbfRecord = eventErrorMap[eventId]
                        clientId = eventClientMap.get(eventId)
                        try:
                            attachDate = forceDate(dbfRecord['PRIK_DATE'])
                        except KeyError:
                            attachDate = QtCore.QDate()
                        errorTableData.append((
                            eventId,
                            clientId or '-',
                            formatName(dbfRecord['FIO'], dbfRecord['IMA'], dbfRecord['OTCH']),
                            dbfRecord['POL'],
                            forceString(forceDate(dbfRecord['DATR']).toString('dd.MM.yyyy')),
                            dbfRecord['SNILS'],
                            dbfRecord['PRIK_MO'],
                            forceString(attachDate.toString('dd.MM.yyyy'))
                        ))

                    if errorTableData:
                        errorTable = self.createErrorTable(cursor)
                        errorTable.addRows(sorted(errorTableData, key=lambda row: (row[2], row[0])), isHtml=True)

                    cursor.movePosition(cursor.End)
                    cursor.insertBlock(CReportBase.AlignLeft)
        return doc

    def showProtocol(self, doc):
        viewDialog = CReportViewOrientation(None, self.orientation)
        viewDialog.setWindowTitle(u'Протокол ФЛК')
        viewDialog.setRepeatButtonVisible()

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            viewDialog.txtReport.setUpdatesEnabled(False)
            viewDialog.setText(doc)
            viewDialog.txtReport.setUpdatesEnabled(True)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        viewDialog.exec_()

    def updateLog(self, msg):
        if not self.logBrowser.isVisible():
            self.logBrowser.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            self.logBrowser.setVisible(True)
        self.logBrowser.append(msg)
        self.logBrowser.update()

    def loadArchive(self, zipFileName):
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        if not is_zipfile(zipFileName):
            self.updateLog(u'Файл не является архивом')
            return

        dbfFileNames = []
        isDBFFile = False

        zipFile = ZipFile(zipFileName, "r")
        for fileName in zipFile.namelist():
            if not unicode(fileName.lower()).endswith('.dbf'):
                continue
            isDBFFile = True
            outFile = QtCore.QTemporaryFile()

            if not outFile.open(QtCore.QFile.WriteOnly):
                self.updateLog(u'Не удаётся открыть файл для записи %s:\n%s.' % (outFile, outFile.errorString()))
                return

            outFile.write(zipFile.read(fileName))
            outFile.close()
            fileInfo = QtCore.QFileInfo(outFile)
            dbfFileNames.append(forceString(fileInfo.filePath()))
            while not os.path.exists(dbfFileNames[-1]):
                time.sleep(2)

        if not isDBFFile:
            self.updateLog(u'В архиве нет dbf-файлов')
            return

        dbfDataQueue = Queue.Queue()
        sqlDataQueue = Queue.Queue()
        clientUpdateQueue = Queue.Queue()
        littleStrangerQueue = Queue.Queue()
        clientErrorQueue = Queue.Queue()

        runList = []
        for fileName in dbfFileNames:
            putTaskThread = threading.Thread(target=putTask, args=(fileName, dbfDataQueue, clientErrorQueue), name='putTask')
            runList.append(putTaskThread)
            putTaskThread.start()

        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        queryThread = threading.Thread(target=query, args=(self.db, len(dbfFileNames), dbfDataQueue, sqlDataQueue), name='query')
        queryThread.start()

        for _ in xrange(self.CheckThreadCount):
            checkThread = CCheckThread(sqlDataQueue, clientUpdateQueue, littleStrangerQueue, self.insurerMap)
            runList.append(checkThread)
            checkThread.start()

        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        self.progressBar.setText(u'Считываем информацию из файла...')

        clientsCount = 0
        clientsTotal = 0
        externalClientsCount = 0
        clientWithErrors = {}

        checkThreadCount = self.CheckThreadCount
        while checkThreadCount:
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
            client = clientUpdateQueue.get()
            clientsTotal += 1

            self.progressBar.setText(u'Обработано всего {0}, инокраевых {1} из {2}'.format(clientsCount, externalClientsCount, clientsTotal))

            if client is not None:
                if isinstance(client, ClientData):
                    if not client.error:
                        clientsCount += 1
                        if client.isExternal:
                            externalClientsCount += 1

                        if client.id in self.clientUpdateMap:
                            existsClient = self.clientUpdateMap[client.id]
                            if client.policies:
                                policy = client.policies[0]

                                policyFound = False
                                for existsPolicy in existsClient:
                                    if existsPolicy.data == policy.data and existsPolicy.newData == policy.newData:
                                        policyFound = True
                                        for eventId in policy.eventIdList:
                                            existsPolicy.appendEvent(eventId)

                                if not policyFound:
                                    existsClient.addPolicy(policy)
                        else:
                            if client.id:
                                self.clientUpdateMap[client.id] = client
                    else:
                        for errCode, errMessage in client.error.iteritems():
                            clientWithErrors.setdefault(errCode, []).append(errMessage)
            else:
                checkThreadCount -= 1

        self.progressBar.setText(u'Обработка файла успешно завершена')
        self.lblNum.setText(u'Обработано всего {count}, инокраевых {extCount}'.format(count=clientsCount, extCount=externalClientsCount))

        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        krasnodarClientsRows = []
        externalClientsRows = []
        for clientId in sorted(self.clientUpdateMap.iterkeys(),
                               key=lambda id: (self.clientUpdateMap[id]['lastName'],
                                               self.clientUpdateMap[id]['firstName'],
                                               self.clientUpdateMap[id]['patrName'])):
            client = self.clientUpdateMap[clientId]
            row = (
                clientId,
                formatName(client['lastName'], client['firstName'], client['patrName']),
                client['birthDate'].toString('dd.MM.yyyy'),
                client.changesMessage,
                [(policy.changesMessage, policy.eventIdList) for policy in client]
            )
            if client.isExternal:
                externalClientsRows.append(row)
            else:
                krasnodarClientsRows.append(row)

        self.progressBar.setText(u'Формирование протокола ФЛК ...')
        self.progressBar.update()
        self.resetRecordCount(clientsCount)
        QtGui.qApp.processEvents()

        doc = self.createProtocol(krasnodarClientsRows, externalClientsRows, clientWithErrors, clientErrorQueue)
        self.showProtocol(doc)

        if self.clientUpdateMap:
            self.chkAgree.setEnabled(True)
            self.chkImportExternal.setEnabled(True)
        self.progressBar.setValue(0)

    def resetRecordCount(self, cnt=0):
        self.lblNum.setText(u'Всего обновлённых записей в источнике: {0}'.format(cnt))

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        self.clientUpdateMap = {}
        self.chkAgree.setEnabled(False)
        self.chkImportExternal.setEnabled(False)
        zipFileName = QtGui.QFileDialog.getOpenFileName(self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы ZIP (*.zip)')
        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
        if zipFileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(zipFileName))
            self.resetRecordCount()
            self.loadArchive(forceString(zipFileName))

    def selectEventClientMap(self, eventIdList):
        Client = self.db.table('Client')
        Event = self.db.table('Event')

        queryTable = Event.innerJoin(Client, Client['id'].eq(Event['client_id']))
        cols = [
            Event['id'].alias('eventId'),
            Event['client_id'].alias('clientId')
        ]
        return dict((forceRef(rec.value('eventId')), forceRef(rec.value('clientId')))
                    for rec in self.db.iterRecordList(queryTable, cols, Event['id'].inlist(eventIdList)))

    def updateClientPersonalInfo(self, clientValues):
        self.db.insertFromDictList('Client', clientValues, keepOldFields=['id'], chunkSize=CHUNK_SIZE)

    def updateOrInsertClientPolicy(self, policyValues):
        self.db.insertFromDictList('ClientPolicy', policyValues, keepOldFields=['id'], chunkSize=CHUNK_SIZE)

    def getExistsPolicyId(self, policyDct):
        tableCP = self.db.table('ClientPolicy')
        cond = [
            tableCP['client_id'].eq(policyDct['client_id']),
            tableCP['serial'].eq(policyDct['serial']),
            tableCP['number'].eq(policyDct['number']),
            tableCP['policyKind_id'].eq(policyDct['policyKind_id']),
            tableCP['policyType_id'].eq(policyDct['policyType_id']),
            tableCP['deleted'].eq(0)
        ]
        if policyDct['begDate']:
            cond.append(tableCP['begDate'].eq(policyDct['begDate']))
        if policyDct['endDate']:
            cond.append(tableCP['endDate'].eq(policyDct['endDate']))
        rec = self.db.getRecordEx(tableCP, ['id'], cond, order=tableCP['id'].desc())
        return forceRef(rec.value('id')) if rec is not None else None

    def excludeExistsPolicies(self, policyValues):
        result = []
        existsPolicyIds = []

        for policyDct in policyValues:
            policyId = self.getExistsPolicyId(policyDct)
            if policyId:
                existsPolicyIds.append(policyId)
            else:
                result.append(policyDct)

        tableCP = self.db.table('ClientPolicy')
        self.db.updateRecords(tableCP, tableCP['note'].eq(self.ImportNote), tableCP['id'].inlist(existsPolicyIds))

        return result

    def updateEvents(self, eventIdList):
        u"""
        Переподвязка полисов в обращениях, для которых при импорте был создан новый полис
        :param eventIdList: {list of Event.id]
        """
        stmt = u'''UPDATE `Event` SET `Event`.`clientPolicy_id` = (
            SELECT CP.id
            FROM ClientPolicy CP
            LEFT JOIN rbPolicyType PT ON PT.id = CP.policyType_id
            LEFT JOIN rbPolicyKind PK ON PK.id = CP.policyKind_id
            WHERE
                CP.client_id = Event.client_id AND
                CP.deleted = 0 AND
                CP.note LIKE '{importNote}%' AND
                (Event.execDate IS NULL OR CP.begDate IS NULL OR if(PK.code = '2',
                                                                    date(CP.begDate) <= date_add(Event.execDate, INTERVAL 30 DAY),
                                                                    date(CP.begDate) <= date(Event.execDate))) AND
                (CP.endDate IS NULL OR date(CP.endDate) >= date(ifnull(Event.execDate, Event.setDate)))
            ORDER BY PK.code = '2'
            LIMIT 0, 1
        )
        WHERE `Event`.`id` IN ({eventIdList})'''.format(eventIdList=u','.join(map(str, eventIdList)),
                                                        importNote=self.ImportNote)
        self.db.query(stmt)

    def updateClientPolicyInsurerFromPrevious(self, eventIdList):
        u"""
        Для добавленных полисов без указания СМО (СМО == ТФОМС)
        копируем СМО из предыдущего полиса того же типа и той же территории страхования
        :param eventIdList: [list of Event.id]: обращения, в котрых необходимо обновить привязанные полисы
        :type eventIdList: list
        """
        db = self.db
        tableEvent = db.table('Event')
        tablePolicy = db.table('ClientPolicy')
        tableNewPolicy = tablePolicy.alias('NewPolicy')
        tableOldPolicy = tablePolicy.alias('OldPolicy')

        table = tableEvent
        table = table.innerJoin(tableNewPolicy, [tableNewPolicy['id'].eq(tableEvent['clientPolicy_id']),
                                                 tableNewPolicy['note'].eq(self.ImportNoteNew)])
        table = table.innerJoin(tableOldPolicy,
                                tableOldPolicy['id'].eqStmt(db.selectMax(
                                    tablePolicy,
                                    tablePolicy['id'],
                                    [
                                        tablePolicy['client_id'].eq(tableNewPolicy['client_id']),
                                        tablePolicy['insuranceArea'].eq(tableNewPolicy['insuranceArea']),
                                        tablePolicy['policyType_id'].eq(tableNewPolicy['policyType_id']),
                                        tablePolicy['insurer_id'].isNotNull(),
                                        tablePolicy['deleted'].eq(0),
                                        tablePolicy['id'].lt(tableNewPolicy['id'])
                                    ])))

        db.insertFromSelect(tablePolicy,
                            table,
                            {
                                'id'        : tableNewPolicy['id'],
                                'insurer_id': tableOldPolicy['insurer_id']
                            },
                            tableEvent['id'].inlist(eventIdList),
                            updateFields=['insurer_id'])

    def selectInsurerId(self, OGRN, OKATO, isHead=True):
        u"Головная СМО с заданными ОГРН, ОКАТО"
        Organisation = self.db.table('Organisation')
        cond = [
            Organisation['OGRN'].eq(OGRN),
            Organisation['OKATO'].eq(OKATO),
            Organisation['isInsurer'].eq(1),
            Organisation['compulsoryServiceStop'].eq(0),
            Organisation['deleted'].eq(0)
        ]
        if isHead:
            cond.append(self.db.joinOr([Organisation['head_id'].isNull(),
                                        Organisation['head_id'].eq(Organisation['id'])]))
        record = self.db.getRecordEx(Organisation, Organisation['id'], cond)
        return forceRef(record.value('id')) if not record is None else None

    def getInsuranceArea(self, OKATO):
        if not OKATO: return ''
        if OKATO not in self._kladr_okato_map:
            self._kladr_okato_map[OKATO] = forceString(
                self.db.getRecordEx('kladr.KLADR', 'CODE', where='OCATD like \'%s%%\'' % OKATO, order='CODE').value('CODE'))
        return self._kladr_okato_map[OKATO]

    def getInsurerId(self, OGRN, OKATO):
        if (OGRN, OKATO) not in self.insurerMap:
            self.insurerMap[(OGRN, OKATO)] = self.selectInsurerId(OGRN, OKATO, False)
        return self.insurerMap[(OGRN, OKATO)]

    def getPolicyKindId(self, kindCode):
        if not kindCode: return None
        if kindCode not in self.policyKindCodeMap:
            self.policyKindCodeMap[kindCode] = forceRef(self.db.translate('rbPolicyKind', 'code', kindCode, 'id'))
        return self.policyKindCodeMap[kindCode]

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        importExternalClients = self.chkImportExternal.isChecked()

        self.btnImport.setEnabled(False)
        self.progressBar.setText(u'Обновление персональной информации...')

        personalUpdateValues = []
        for clientId, client in self.clientUpdateMap.iteritems():
            if not client.personalChanges:
                continue

            if client.isExternal and not importExternalClients:
                continue

            data = client.newData
            personalUpdateValues.append({'id'       : client.id,
                                         'lastName' : data['lastName'],
                                         'firstName': data['firstName'],
                                         'patrName' : data['patrName'],
                                         'birthDate': data['birthDate'],
                                         'sex'      : databaseFormatSex(data['sex']),
                                         'SNILS'    : data['SNILS'],
                                         'notes'    : u';'.join([data['notes'], self.ImportNoteUpdate])})
        self.updateClientPersonalInfo(personalUpdateValues)

        self.progressBar.setText(u'Обновление информации о полисах пользователей...')

        clientPolicyUpdates = []
        newClientPolicies = []

        policyCount = 0
        policyTotal = sum(len(client.policies) for id, client in self.clientUpdateMap.iteritems())

        self.progressBar.setMaximum(policyTotal)

        # обращения, в котрых нужно привязать добавленный полис
        eventsForUpdate = []

        # обращения с новыми полисами, в которых СМО не найдена и будет подставлена из старого полиса
        # (касается инокраевых, территории страхования у нового и старого полисов должны совпадать)
        eventsForFixInsurerFromPrevPolicy = []

        db = self.db
        for clientId, client in self.clientUpdateMap.iteritems():
            if client.isExternal and not importExternalClients:
                continue

            for policy in client.policies:
                policyCount += 1

                data = policy.newData
                policyId = data['id']
                serial = data['serial']
                number = data['number']
                OGRN = data['OGRN']
                OKATO = data['OKATO']
                begDate = data['begDate']
                endDate = data['endDate']

                kindId = self.getPolicyKindId(data['kindCode'])
                insurerId = self.getInsurerId(OGRN, OKATO) if policy.changeInsurer else policy['insurerId']
                area = self.getInsuranceArea(OKATO)

                if not policyId:
                    eventsForUpdate.extend(policy.eventIdList)
                    if not insurerId and client.isExternal and not policy.changeOKATO:
                        eventsForFixInsurerFromPrevPolicy.extend(policy.eventIdList)

                    newClientPolicies.append({
                        'createDatetime' : db.makeField('NOW()'),
                        'modifyDatetime' : db.makeField('NOW()'),
                        'createPerson_id': QtGui.qApp.userId,
                        'modifyPerson_id': QtGui.qApp.userId,
                        'client_id'      : clientId,
                        'policyType_id'  : self.CompulsoryPolicyTypeId,
                        'policyKind_id'  : kindId,
                        'insurer_id'     : insurerId,
                        'serial'         : serial,
                        'number'         : number,
                        'begDate'        : begDate,
                        'endDate'        : endDate,
                        'insuranceArea'  : area,
                        'note'           : self.ImportNoteNew
                    })
                else:
                    clientPolicyUpdates.append({
                        'id'             : policyId,
                        'modifyDatetime' : db.makeField('NOW()'),
                        'modifyPerson_id': QtGui.qApp.userId,
                        'policyType_id'  : self.CompulsoryPolicyTypeId,
                        'policyKind_id'  : kindId,
                        'insurer_id'     : insurerId,
                        'serial'         : serial,
                        'number'         : number,
                        'begDate'        : begDate,
                        'endDate'        : endDate,
                        'insuranceArea'  : area,
                        'note'           : self.ImportNoteUpdate
                    })

            self.progressBar.setValue(policyCount)
            self.progressBar.setText(u'Обработано записей: {count}/{total}'.format(count=policyCount, total=policyTotal))
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

        self.updateOrInsertClientPolicy(clientPolicyUpdates)
        self.updateOrInsertClientPolicy(self.excludeExistsPolicies(newClientPolicies))

        if eventsForUpdate:
            self.updateEvents(eventsForUpdate)

        if eventsForFixInsurerFromPrevPolicy:
            self.updateClientPolicyInsurerFromPrevious(eventsForFixInsurerFromPrevPolicy)

        self.progressBar.setValue(policyTotal)
        self.progressBar.setText(u'Информация успешно обновлена')
        self.resetRecordCount(policyTotal)

        self.chkAgree.setChecked(False)
        self.chkAgree.setEnabled(False)
        self.chkImportExternal.setChecked(False)
        self.chkImportExternal.setEnabled(False)

        self.clientUpdateMap = {}

        QtGui.qApp.processEvents()

# if __name__ == '__main__':
#     import sys
#     from library.database import connectDataBaseByInfo
#     from s11main import CS11mainApp
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#     connectionInfo = {'driverName'      : 'mysql',
#                       'host'            : 'pacs',
#                       'port'            : 3306,
#                       'database'        : 's11vm',
#                       'user'            : 'dbuser',
#                       'password'        : 'dbpassword',
#                       'connectionName'  : 'vista-med',
#                       'compressData'    : True,
#                       'afterConnectFunc': None}
#     db = connectDataBaseByInfo(connectionInfo)
#
#     QtGui.qApp = app
#     QtGui.qApp.db = db
#     QtGui.qApp.currentOrgId = lambda: 230226
#
#     dlg = CImportFLC()
#     dlg.exec_()
