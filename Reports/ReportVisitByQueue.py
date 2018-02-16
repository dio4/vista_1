# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceRef, forceString, getVal, formatName
from Orgs.Utils         import getOrgStructureFullName
from Reports.Report     import CReportOrientation
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportVisitByQueueDialog import Ui_ReportVisitByQueueDialog


def getDataVisitByQueue(params, orgStructureIdList):
    etcQueue = 'queue'
    atcQueue = 'queue'
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableOrg = db.table('Organisation')
    tableOrgStructure = db.table('OrgStructure')
    tableVisit = db.table('Visit')
    tablePerson = db.table('Person')
    tableEventType = db.table('EventType')
    tableActionType = db.table('ActionType')
    tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableActionProperty_Action = db.table('ActionProperty_Action')

    begDate = params.get('begDateVisitBeforeRecord', QtCore.QDate())
    endDate = params.get('endDateVisitBeforeRecord', QtCore.QDate())
    specialityId = params.get('specialityId', None)
    personId = params.get('personId', None)
    noVisit = params.get('noVisit', False)
    visitOtherSpeciality = params.get('visitOtherSpeciality', False)
    visitSorting = params.get('visitSorting', 0)
    cols = [tableAction['id'],
            tableActionType['name'],
            tableAction['directionDate'],
            tableAction['person_id'],
            tablePerson['speciality_id'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate']
            ]

    cols.append('''age(Client.birthDate, DATE(Action.`directionDate`)) AS ageClient''')
    cols.append('''(SELECT ClientContact.contact FROM ClientContact INNER JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id WHERE ClientContact.deleted = 0 AND ClientContact.client_id = Client.id AND (rbContactType.code = 1 OR rbContactType.code = 2 OR rbContactType.code = 3) LIMIT 1) AS telefone''')
    if not noVisit:
        cols.append('''(%s) AS visitDate'''%(getVisit(visitOtherSpeciality)))
    accountingSystemId = QtGui.qApp.defaultAccountingSystemId()
    if accountingSystemId:
        cols.append('''(SELECT ClientIdentification.identifier FROM ClientIdentification WHERE ClientIdentification.client_id = Client.id AND ClientIdentification.accountingSystem_id = %s AND ClientIdentification.deleted = 0 LIMIT 1) AS clientId'''%(forceString(accountingSystemId)))
    else:
        cols.append(tableClient['id'].alias('clientId'))
    tableQuery = tableAction
    tableQuery = tableQuery.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    tableQuery = tableQuery.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    tableQuery = tableQuery.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
    tableQuery = tableQuery.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))

    cond = [tableEventType['code'].eq(etcQueue),
            tableActionType['code'].eq(atcQueue),
            tableEventType['deleted'].eq(0),
            tableActionType['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0)
            ]
    if begDate:
        cond.append(tableAction['directionDate'].dateGe(begDate))
    if endDate:
        cond.append(tableAction['directionDate'].dateLe(endDate))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureIdList:
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if noVisit:
        cond.append(u'''NOT EXISTS(%s)'''%(getVisit(visitOtherSpeciality)))
#    else:
#        cond.append(u'''EXISTS(%s)'''%(getVisit(visitOtherSpeciality)))

    return db.getRecordList(tableQuery, cols, cond, [u'Action.directionDate', u'Client.lastName, Client.firstName, Client.patrName', u'Client.Id'][visitSorting])


def getDataVisitByQueueNext(params, orgStructureIdList):
    etcQueue = 'queue'
    atcQueue = 'queue'
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tableOrg = db.table('Organisation')
    tableOrgStructure = db.table('OrgStructure')
    tableVisit = db.table('Visit')
    tablePerson = db.table('Person')
    tableEventType = db.table('EventType')
    tableActionType = db.table('ActionType')
    tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableActionProperty_Action = db.table('ActionProperty_Action')

    begDate = params.get('begDateVisitBeforeRecord', QtCore.QDate())
    endDate = params.get('endDateVisitBeforeRecord', QtCore.QDate())
    specialityId = params.get('specialityId', None)
    personId = params.get('personId', None)
    nextVisit = params.get('nextVisit', False)
    visitSorting = params.get('visitSorting', 0)

    cols = [tableAction['id'],
            tableActionType['name'],
            tableAction['directionDate'],
            tableAction['person_id'],
            tablePerson['speciality_id'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['id'].alias('clientId'),
            tableClient['birthDate']
            ]

    cols.append('''age(Client.birthDate, DATE(Action.`directionDate`)) AS ageClient''')
    cols.append('''(SELECT ClientContact.contact FROM ClientContact INNER JOIN rbContactType ON rbContactType.id = ClientContact.contactType_id WHERE ClientContact.deleted = 0 AND ClientContact.client_id = Client.id AND (rbContactType.code = 1 OR rbContactType.code = 2 OR rbContactType.code = 3) LIMIT 1) AS telefone''')
    cols.append('''(%s) AS visitDate'''%(getVisitNextCols()))
    accountingSystemId = QtGui.qApp.defaultAccountingSystemId()
    if accountingSystemId:
        cols.append('''(SELECT ClientIdentification.identifier FROM ClientIdentification WHERE ClientIdentification.client_id = Client.id AND ClientIdentification.accountingSystem_id = %s AND ClientIdentification.deleted = 0 LIMIT 1) AS clientId'''%(forceString(accountingSystemId)))
    else:
        cols.append(tableClient['id'].alias('clientId'))
    tableQuery = tableAction
    tableQuery = tableQuery.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    tableQuery = tableQuery.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    tableQuery = tableQuery.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
    tableQuery = tableQuery.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    cond = [tableEventType['code'].eq(etcQueue),
            tableActionType['code'].eq(atcQueue),
            tableEventType['deleted'].eq(0),
            tableActionType['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableClient['deleted'].eq(0)
            ]
    if begDate:
        cond.append(tableAction['directionDate'].dateGe(begDate))
    if endDate:
        cond.append(tableAction['directionDate'].dateLe(endDate))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if orgStructureIdList:
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    cond.append(getVisitNext())
    return db.getRecordList(tableQuery, cols, cond, [u'Action.directionDate', u'Client.lastName, Client.firstName, Client.patrName', u'Client.Id'][visitSorting] + u', Client.Id')


def getVisit(visitOtherSpeciality):
    return u'''SELECT Visit.date FROM Event AS E INNER JOIN Visit ON Visit.event_id = E.id INNER JOIN Person AS P ON P.id = Visit.person_id WHERE E.client_id = Client.id AND %sAction.person_id IS NOT NULL AND (Action.directionDate IS NOT NULL AND DATE(Visit.date) = DATE(Action.directionDate)) AND E.deleted = 0 AND Visit.deleted = 0 AND P.deleted = 0 AND (P.speciality_id = Person.speciality_id) LIMIT 1'''%(u'(Visit.person_id = Action.person_id) AND ' if visitOtherSpeciality else u'')


def getVisitNext():
    return u'''SELECT E.nextEventDate IS NOT NULL AND (DATE(Visit.date) < DATE(E.nextEventDate)) FROM Event AS E INNER JOIN Visit ON Visit.event_id = E.id INNER JOIN Person AS P ON P.id = Visit.person_id WHERE E.client_id = Client.id AND (Visit.person_id = Action.person_id) AND Action.person_id IS NOT NULL AND (Action.directionDate IS NOT NULL AND DATE(Visit.date) = DATE(Action.directionDate)) AND E.deleted = 0 AND Visit.deleted = 0 AND P.deleted = 0 AND (P.speciality_id = Person.speciality_id) ORDER BY Visit.date DESC LIMIT 1'''


def getVisitNextCols():
    return u'''SELECT E.nextEventDate FROM Event AS E INNER JOIN Visit ON Visit.event_id = E.id INNER JOIN Person AS P ON P.id = Visit.person_id WHERE E.client_id = Client.id AND (Visit.person_id = Action.person_id) AND Action.person_id IS NOT NULL AND (Action.directionDate IS NOT NULL AND DATE(Visit.date) = DATE(Action.directionDate)) AND E.deleted = 0 AND Visit.deleted = 0 AND P.deleted = 0 AND (P.speciality_id = Person.speciality_id) ORDER BY Visit.date DESC LIMIT 1'''


class CReportVisitByQueueDialog(QtGui.QDialog, Ui_ReportVisitByQueueDialog):
    def __init__(self, parent=None, val=0):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructureVisitBeforeRecordClient.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructureVisitBeforeRecordClient.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSpecialityVisitBeforeRecordClient.setTable('rbSpeciality', order='name')
        if val:
            self.chkNextVisitBeforeRecordClient.setVisible(False)
            self.chkNoVisitBeforeRecordClient.setVisible(False)
            self.chkVisitOtherSpeciality.setVisible(False)
        else:
            self.chkNextVisitBeforeRecordClient.setVisible(False)
            self.chkNoVisitBeforeRecordClient.setVisible(True)
            self.chkVisitOtherSpeciality.setVisible(True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBeginDateVisitBeforeRecordClient.setDate(getVal(params, 'begDateVisitBeforeRecord', QtCore.QDate.currentDate()))
        self.edtEndDateVisitBeforeRecordClient.setDate(getVal(params, 'endDateVisitBeforeRecord', QtCore.QDate.currentDate()))
        self.cmbOrgStructureVisitBeforeRecordClient.setValue(getVal(params, 'orgStructureId', None))
        self.cmbSpecialityVisitBeforeRecordClient.setValue(getVal(params, 'specialityId', None))
        self.cmbPersonVisitBeforeRecordClient.setValue(getVal(params, 'personId', None))
        self.chkNextVisitBeforeRecordClient.setChecked(getVal(params, 'nextVisit', False))
        self.chkNoVisitBeforeRecordClient.setChecked(getVal(params, 'noVisit', False))
        self.chkVisitOtherSpeciality.setChecked(getVal(params, 'visitOtherSpeciality', False))
        self.cmbSorting.setCurrentIndex(getVal(params, 'visitSorting', 0))


    def params(self):
        result = {}
        result['begDateVisitBeforeRecord'] = self.edtBeginDateVisitBeforeRecordClient.date()
        result['endDateVisitBeforeRecord'] = self.edtEndDateVisitBeforeRecordClient.date()
        result['orgStructureId'] = self.cmbOrgStructureVisitBeforeRecordClient.value()
        result['specialityId'] = self.cmbSpecialityVisitBeforeRecordClient.currentIndex()
        result['personId'] = self.cmbPersonVisitBeforeRecordClient.value()
        result['nextVisit'] = self.chkNextVisitBeforeRecordClient.isChecked()
        result['noVisit'] = self.chkNoVisitBeforeRecordClient.isChecked()
        result['visitOtherSpeciality'] = self.chkVisitOtherSpeciality.isChecked()
        result['visitSorting'] = self.cmbSorting.currentIndex()
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructureVisitBeforeRecordClient_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructureVisitBeforeRecordClient.value()
        self.cmbPersonVisitBeforeRecordClient.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpecialityVisitBeforeRecordClient_currentIndexChanged(self, index):
        specialityId = self.cmbSpecialityVisitBeforeRecordClient.value()
        self.cmbPersonVisitBeforeRecordClient.setSpecialityId(specialityId)


class CReportVisitByQueue(CReportOrientation):
    def __init__(self, parent, val):
        CReportOrientation.__init__(self, parent, QtGui.QPrinter.Landscape)
        self.setTitle(u'Выполнение предварительной записи')
        self.reportVisitByQueueDialog = None
        self.clientDeath = 8
        self.val = val


    def getSetupDialog(self, parent):
        result = CReportVisitByQueueDialog(parent, self.val)
        self.reportVisitByQueueDialog = result
        return result


    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []


    def dumpParams(self, cursor, params):
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        description = []
        begDate = params.get('begDateVisitBeforeRecord', QtCore.QDate())
        endDate = params.get('endDateVisitBeforeRecord', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        nextVisit = params.get('nextVisit', False)
        noVisit = params.get('noVisit', False)
        visitOtherSpeciality = params.get('visitOtherSpeciality', False)
        visitSorting = params.get('visitSorting', 0)
        if begDate or endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if specialityId:
            specialityName = forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            description.append(u'Специальность ' + specialityName)
        if personId:
            personName = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            description.append(u'Врач ' + personName)
        if nextVisit:
           description.append(u'Учитывать назначение следующей явки')
        if noVisit:
           description.append(u'Учитывать только не явившихся на прием')
        if visitOtherSpeciality:
           description.append(u'Не учитывать явившихся к другому врачу данной специальности')
        description.append(u'Сортировка ' + [u'по дате', u'по ФИО пациента', u'по идентификатору пациента'][visitSorting])

        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


class CReportVisitByQueueMoving(CReportVisitByQueue):
    def __init__(self, parent):
        CReportVisitByQueue.__init__(self, parent, 0)
        self.setTitle(u'Выполнение предварительной записи')


    def build(self, params):
        orgStructureId = getVal(params, 'orgStructureId', None)
        orgStructureIndex = self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient._model.index(self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient.currentIndex(), 0, self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Отчет о выполнении предварительной записи к врачу')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('5%',[u'№ п/п'], CReportBase.AlignLeft),
                ('19%', [u'Идентификатор пациента'], CReportBase.AlignLeft),
                ('19%', [u'ФИО'], CReportBase.AlignLeft),
                ('19%', [u'Д/р и возраст'], CReportBase.AlignLeft),
                ('19%', [u'Дата явки'], CReportBase.AlignLeft),
                ('19%', [u'Телефон'], CReportBase.AlignLeft)
               ]
        table = createTable(cursor, cols)
        records = getDataVisitByQueue(params, orgStructureIdList)
        cnt = 0
        for record in records:
            i = table.addRow()
            cnt += 1
            table.setText(i, 0, cnt)
            table.setText(i, 1, forceRef(record.value('clientId')))
            table.setText(i, 2, formatName(record.value('lastName'), record.value('firstName'), record.value('patrName')))
            table.setText(i, 3, forceString(forceDate(record.value('birthDate'))) + u'(' + forceString((forceInt(record.value('ageClient')))) + u')')
            table.setText(i, 4, forceDate(record.value('visitDate')).toString('dd.MM.yyyy'))
            table.setText(i, 5, forceString(record.value('telefone')))
        return doc


class CReportVisitByQueueNext(CReportVisitByQueue):
    def __init__(self, parent):
        CReportVisitByQueue.__init__(self, parent, 1)
        self.setTitle(u'Следующая явка не выполнена')


    def build(self, params):
        orgStructureId = getVal(params, 'orgStructureId', None)
        orgStructureIndex = self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient._model.index(self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient.currentIndex(), 0, self.reportVisitByQueueDialog.cmbOrgStructureVisitBeforeRecordClient.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Отчет следующая явка не выполнена')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('5%',[u'№ п/п'], CReportBase.AlignLeft),
                ('19%', [u'Идентификатор пациента'], CReportBase.AlignLeft),
                ('19%', [u'ФИО'], CReportBase.AlignLeft),
                ('19%', [u'Д/р и возраст'], CReportBase.AlignLeft),
                ('19%', [u'Дата явки'], CReportBase.AlignLeft),
                ('19%', [u'Телефон'], CReportBase.AlignLeft)
               ]
        table = createTable(cursor, cols)
        records = getDataVisitByQueueNext(params, orgStructureIdList)
        cnt = 0
        for record in records:
            i = table.addRow()
            cnt += 1
            table.setText(i, 0, cnt)
            table.setText(i, 1, forceRef(record.value('clientId')))
            table.setText(i, 2, formatName(record.value('lastName'), record.value('firstName'), record.value('patrName')))
            table.setText(i, 3, forceString(forceDate(record.value('birthDate'))) + u'(' + forceString((forceInt(record.value('ageClient')))) + u')')
            table.setText(i, 4, forceDate(record.value('visitDate')).toString('dd.MM.yyyy'))
            table.setText(i, 5, forceString(record.value('telefone')))
        return doc
