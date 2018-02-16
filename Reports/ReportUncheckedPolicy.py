# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceRef, forceString
from Registry.Utils     import formatPolicy
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Orgs.Utils         import  getOrgStructureDescendants

from Ui_ReportUncheckedPolicy import Ui_ReportUncheckedPolicy

def selectDate(params):
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    orgStructureId = params.get('orgStructureId')
    db = QtGui.qApp.db

    tableClientPolicy = db.table('ClientPolicy')
    tableActionType   = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableOrgStructure = db.table('OrgStructure')
    tableEvent = db.table('Event')

    cond = [tableClientPolicy['isSearchPolicy'].le(1),
            tableActionType['flatCode'].eq('moving'),
            tableActionPropertyType['name'].eq(u'Отделение пребывания'),
            tableClientPolicy['createDatetime'].between(begDate,endDate.addDays(1)),
            db.joinOr([tableEvent['setDate'].between(begDate,endDate.addDays(1)), tableEvent['execDate'].between(begDate, endDate.addDays(1))])]

    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    cond.extend([tableClientPolicy['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableActionPropertyType['deleted'].eq(0)])

    stmt = u'''SELECT group_concat(Event.externalId) as external
                    , trim(concat(Client.lastName, ' ', Client.firstName, ' ', Client.patrName)) AS clientName
                    , OrgStructure.code
                    , ClientPolicy.insurer_id
                    , ClientPolicy.serial
                    , ClientPolicy.number
                    , ClientPolicy.begDate
                    , ClientPolicy.endDate
                FROM
                    Client
                    INNER JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Client.id, 1) AND ClientPolicy.client_id = Client.id
                    INNER JOIN Event ON Event.client_id = ClientPolicy.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                    INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                    LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value AND OrgStructure.deleted = 0
                WHERE
                    %s
                GROUP BY
                    ClientPolicy.id''' % db.joinAnd(cond)
    return db.query(stmt)

class CReportUncheckedPolicy(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Отчет по пациентам, не прошедших проверку по полису ОМС')


    def getSetupDialog(self, parent):
        result = CUncheckedPolicy(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        query = selectDate(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [('2%',   [u'№ п/п'],               CReportBase.AlignLeft),
                        ('10%',  [u'№ ИБ'],                CReportBase.AlignLeft),
                        ('25%',  [u'ФИО'],                  CReportBase.AlignLeft),
                        ('5%',   [u'Код отд.'],             CReportBase.AlignLeft),
                        ('35%',  [u'данные о полисе ОМС'],  CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)

        while query.next():
            record = query.record()
            external = forceString(record.value('external'))
            clientName = forceString(record.value('clientName'))
            code = forceString(record.value('code'))
            insurerId = forceRef(record.value('insurer_id'))
            serial = forceString(record.value('serial'))
            number = forceString(record.value('number'))
            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))

            i = table.addRow()
            table.setText(i, 0, i)
            table.setText(i, 1, external.replace(',', '\n'))
            table.setText(i, 2, clientName)
            table.setText(i, 3, code)
            table.setText(i, 4, formatPolicy(insurerId, serial, number, begDate, endDate))
        return doc

class CUncheckedPolicy(QtGui.QDialog, Ui_ReportUncheckedPolicy):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        return params