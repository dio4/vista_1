# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_FinanceSummaryByLoadOnDoctorSetupDialog import Ui_FinanceSummaryByLoadOnDoctorSetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceDouble, forceString, forceDate
from library.database import addDateInRange


def getCond(params, additionalCondType=0):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableVisit = db.table('Visit')

    cond = [tableAccountItem['reexposeItem_id'].isNull()]

    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    serviceDate = [tableEvent['execDate'], tableVisit['date'], tableAction['endDate']][additionalCondType]
    addDateInRange(cond, serviceDate, begDate, endDate)

    if params.get('orgStructureId', None):
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(params['orgStructureId'])))
    else:
        cond.append(db.joinOr([
            tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()),
            tablePerson['org_id'].isNull()
        ]))

    eventTypeId = params.get('eventTypeId', None)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    return db.joinAnd(cond)


def selectDataByEvents(params):
    stmt = """
    SELECT
        Person.id as personId,
        CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS personName,
        IF(Visit.id IS NULL, 1, (SELECT COUNT(1) FROM Visit WHERE Visit.event_id = Event.id AND Visit.deleted = 0)) AS sumDivider,
        Account_Item.amount AS amount,
        Account_Item.sum AS sum,
        Event.execDate as date
    FROM
        Account_Item
        LEFT JOIN Account ON Account.id = Account_Item.master_id AND Account.deleted = 0
        LEFT JOIN Event ON Event.id = Account_Item.event_id
        LEFT JOIN EventType ON EventType.id = Event.eventType_id
        LEFT JOIN Visit ON Visit.event_id = Event.id AND Visit.deleted = 0
        LEFT JOIN Person ON Person.id = IF(Visit.id IS NULL, Event.execPerson_id, Visit.person_id)
        LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
    WHERE
        Account_Item.visit_id IS NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NULL
        AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 0))

def selectDataByVisits(params):
    stmt = """
    SELECT
        Person.id as personId,
        CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS personName,
        1 AS sumDivider,
        Account_Item.amount AS amount,
        Account_Item.sum AS sum,
        Visit.date AS date
    FROM
        Account_Item
        LEFT JOIN Account ON Account.id = Account_Item.master_id AND Account.deleted = 0
        LEFT JOIN Visit ON Visit.id = Account_Item.visit_id
        LEFT JOIN Person ON Person.id = Visit.person_id
        LEFT JOIN Event ON Event.id = Visit.event_id
        LEFT JOIN EventType ON EventType.id = Event.eventType_id
        LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
    WHERE
        Account_Item.visit_id IS NOT NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NULL
        AND Visit.deleted = 0
        AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 1))

def selectDataByActions(params):
    stmt = """
    SELECT
        Person.id as personId,
        CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS personName,
        1 AS sumDivider,
        Account_Item.amount AS amount,
        Account_Item.sum AS sum,
        Action.endDate AS date
    FROM
        Account_Item
        LEFT JOIN Account ON Account.id = Account_Item.master_id AND Account.deleted = 0
        LEFT JOIN Action ON Action.id = Account_Item.action_id
        LEFT JOIN Person ON Person.id = Action.person_id
        LEFT JOIN Event ON Event.id = Action.event_id
        LEFT JOIN EventType ON EventType.id = Event.eventType_id
        LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
    WHERE
        Account_Item.visit_id IS NULL
        AND Account_Item.deleted = 0
        AND Account_Item.action_id IS NOT NULL
        AND %s
    """
    db = QtGui.qApp.db
    return db.query(stmt % getCond(params, 2))


class CReportFinanceSummaryByLoadOnDoctorSetupDialog(CDialogBase, Ui_FinanceSummaryByLoadOnDoctorSetupDialog):

    MAX_LENGTH_OF_PERIOD = 3 # месяца

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.rbtnByMoney.setChecked(params.get('byMoney', True))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))

    def params(self):
        params = {}
        params['byMoney'] = self.rbtnByMoney.isChecked()
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['eventTypeId'] = self.cmbEventType.value()
        return params

    def checkDataEntered(self):
        result = True
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        if endDate < begDate:
            result = result and self.checkValueMessage(u'Дата окончания раньше даты начала', False, self.edtBegDate)
        if begDate.addMonths(self.MAX_LENGTH_OF_PERIOD) < endDate:
            result = result and self.checkValueMessage(u'Максимальный период: 3 месяца', False, self.edtEndDate)
        return result

    def saveData(self):
        return self.checkDataEntered()


class CReportFinanceSummaryByLoadOnDoctor(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Финансовая сводка по нагрузке на врача')

    def getDescription(self, params):
        rows = CReport.getDescription(self, params)
        byMoney = params.get('byMoney', True)
        rows.append(u'сводка: по ' + (u'денежным суммам' if byMoney else u'количеству услуг'))
        return rows

    def getSetupDialog(self, parent):
        result = CReportFinanceSummaryByLoadOnDoctorSetupDialog(parent)
        result.setTitle(self.title())
        return  result

    def formatDouble(self, value, locale = QtCore.QLocale()):
        if QtGui.qApp.region() == '23':
            return u'{0:.2f}'.format(value)
        else:
            return locale.toString(value, 'f', 2)

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        isByMoney = params.get('byMoney', True)

        daysCount = begDate.daysTo(endDate) + 1
        doctorsData = {}

        def processQuery(query, isByMoney):
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                personId = forceInt(record.value('personId'))
                personName = forceString(record.value('personName'))
                date = forceDate(record.value('date'))
                sumDivider = forceInt(record.value('sumDivider'))
                amount = forceDouble(record.value('amount')) / sumDivider
                sum = forceDouble(record.value('sum')) / sumDivider
                if amount == int(amount):
                    amount = int(amount)

                doctorData = doctorsData.setdefault(personId, {'name': personName, 'data': [0] * daysCount})
                doctorData['data'][begDate.daysTo(date)] += (sum if isByMoney else amount)

        processQuery(selectDataByActions(params), isByMoney)
        processQuery(selectDataByEvents(params), isByMoney)
        processQuery(selectDataByVisits(params), isByMoney)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('15?', [u'Врач'], CReportBase.AlignLeft)] + \
                       [('{percent}%'.format(percent=85.0/daysCount), [begDate.addDays(i).toString('dd.MM')], CReportBase.AlignRight) for i in xrange(daysCount)]
        table = createTable(cursor, tableColumns)

        for id in sorted(doctorsData.keys(), key=lambda id: doctorsData[id]['name']):
            i = table.addRow()
            table.setText(i, 0, doctorsData[id]['name'])
            for j in xrange(daysCount):
                text = doctorsData[id]['data'][j]
                table.setText(i, j + 1, self.formatDouble(float(text)) if isByMoney else text)

        return doc
