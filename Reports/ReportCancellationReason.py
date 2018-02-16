# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ReportCancellationReason import Ui_Dialog
from library.Utils import getVal, forceString

def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)

    stmt = '''
SELECT
    Client.id AS clientId,
    CONCAT_WS(" ", Client.lastName, Client.firstName, Client.patrName) AS fio,
    ActionType.name AS usl,
    rbRefusalReasons.name AS reason
FROM
    Event
    INNER JOIN Client ON Event.client_id = Client.id
    INNER JOIN Action ON Action.event_id = Event.id AND Action.status = 3
    INNER JOIN ActionType ON Action.actionType_id = ActionType.id
    INNER JOIN ActionProperty ON ActionProperty.action_id = Action.id
    INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id AND ActionPropertyType.penalty = 666
    INNER JOIN ActionProperty_Reference ON ActionProperty_Reference.id = ActionProperty.id
    INNER JOIN rbRefusalReasons ON rbRefusalReasons.id = ActionProperty_Reference.value
    INNER JOIN Person ON Person.id = Action.setPerson_id
    INNER JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
WHERE
    Action.deleted = 0
    AND Person.deleted = 0
    AND Event.deleted = 0
    AND Client.deleted = 0
    AND %s
ORDER BY
    clientId
'''

    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tblAction = db.table('Action')

    cond = []
    cond.append(tblAction['createDatetime'].dateBetween(begDate, endDate))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    # else:
    #     cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if personId:
        cond.append(tablePerson['id'].eq(personId))

    return db.query(stmt % (db.joinAnd(cond)))



class CReportCancellationReason(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Отчет по причинам отказов в оказании услуг (предварительный)')


    def getSetupDialog(self, parent):
        result = CReportCancelationReasonDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()


        tableColumns = [
                        ('10%', [u'Код клиента', u''], CReportBase.AlignLeft),
                        ('20%', [u'ФИО', u''], CReportBase.AlignLeft),
                        ('15%', [u'Услуга', u''], CReportBase.AlignLeft),
                        ('15%', [u'Причина отказа', u''], CReportBase.AlignLeft)
                        ]
        table = createTable(cursor, tableColumns)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                forceString(record.value('clientId')),
                forceString(record.value('fio')),
                forceString(record.value('usl')),
                forceString(record.value('reason')),
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc

class CReportCancelationReasonDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStruct.setValue(QtGui.qApp.currentOrgStructureId)
        self.dtFrom.setDate(QtCore.QDate.currentDate())
        self.dtTo.setDate(QtCore.QDate.currentDate())

    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.dtFrom.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.dtTo.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbOrgStruct.setValue(getVal(params, 'orgStructureId', None))

    def params(self):
        result = {}
        result['begDate'] = self.dtFrom.date()
        result['endDate'] = self.dtTo.date()
        result['personId'] = self.cmbPerson.value()
        result['orgStructureId'] = self.cmbOrgStruct.value()
        return result