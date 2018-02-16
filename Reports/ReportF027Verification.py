# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from library.DialogBase import CDialogBase
from library.Utils      import forceInt, forceString, forceDate
from library.database import addDateInRange

from Ui_ReportF027VerificationSetupDialog import Ui_ReportF027VerificationSetupDialog


def selectData(begDate, endDate, orgStructureId, eventTypeId):
    db = QtGui.qApp.db
    Action = db.table('Action')
    ActionType = db.table('ActionType')
    Event = db.table('Event')
    EventType = db.table('EventType')
    OrgStructure = db.table('OrgStructure')
    Person = db.table('Person')

    queryTable = Action.leftJoin(ActionType, ActionType['id'].eq(Action['actionType_id']))
    queryTable = queryTable.leftJoin(Event, Event['id'].eq(Action['event_id']))
    queryTable = queryTable.leftJoin(Person, Person['id'].eq(Action['setPerson_id']))
    queryTable = queryTable.leftJoin(OrgStructure, OrgStructure['id'].eq(Person['orgStructure_id']))

    cols = [
        Event['id'].alias('eventId'),
        Event['setDate'].alias('eventSetDate'),
        Action['begDate'].alias('actionLeavedBegDate'),
        "concat_ws(' ', %s, %s, %s) AS personName" % (Person['lastName'].name(), Person['firstName'].name(), Person['patrName'].name()),
        OrgStructure['name'].alias('orgStructureName')
    ]

    cond = [
        ActionType['flatCode'].eq('leaved'),
        ActionType['code'].like(u'ф27'),
        Action['deleted'].eq(0),
        ActionType['deleted'].eq(0),
        Event['deleted'].eq(0),
        OrgStructure['deleted'].eq(0),
        Person['deleted'].eq(0)
    ]
    addDateInRange(cond, Action['endDate'], begDate, endDate)

    if not orgStructureId is None:
        cond.append(OrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if not eventTypeId is None:
        cond.append(Event['eventType_id'].eq(eventTypeId))

    order = [
        'DATE(%s)' % Event['setDate'].name(),
        'DATE(%s)' % Action['begDate'].name(),
        Person['lastName'],
        Person['firstName'],
        Person['patrName']
    ]

    stmt = db.selectStmt(queryTable, cols, cond, order=order)
    return db.query(stmt)


class CReportF027SetupDialog(CDialogBase, Ui_ReportF027VerificationSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))


    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['eventTypeId'] = self.cmbEventType.value()
        params['eventTypeText'] = self.cmbEventType.currentText()
        return params


class CReportF027Verification(CReport):

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Проверка формы 027')


    def getSetupDialog(self, parent):
        result = CReportF027SetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        eventTypeId = params.get('eventTypeId', None)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'Номер истории болезни'], CReportBase.AlignLeft),
            ('20%', [u'Дата поступления'], CReportBase.AlignLeft),
            ('20%', [u'Дата выписки'], CReportBase.AlignLeft),
            ('20%', [u'Лечащий врач'], CReportBase.AlignLeft),
            ('20%', [u'Отделение'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        query = selectData(begDate, endDate, orgStructureId, eventTypeId)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            eventId = forceInt(record.value('eventId'))
            eventSetDate = forceDate(record.value('eventSetDate'))
            actionLeavedBegDate = forceDate(record.value('actionLeavedBegDate'))
            personName = forceString(record.value('personName'))
            orgStructureName = forceString(record.value('orgStructureName'))

            i = table.addRow()
            table.setText(i, 0, '%d' % eventId)
            table.setText(i, 1, eventSetDate.toString('dd.MM.yyyy'))
            table.setText(i, 2, actionLeavedBegDate.toString('dd.MM.yyyy'))
            table.setText(i, 3, personName)
            table.setText(i, 4, orgStructureName)

        return doc
