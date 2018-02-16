# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceString, forceInt, formatName, calcAge
from Orgs.Utils         import getOrganisationInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportActirovaniaSetup import Ui_ReportActirovaniaSetupDialog


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    begTime = params.get('begTime', QtCore.QTime())
    endTime = params.get('endTime', QtCore.QTime())

    begDateTime = QtCore.QDateTime(begDate, begTime)
    endDateTime = QtCore.QDateTime(endDate, endTime)

    counterFrom = params.get('counterFrom', 0)
    counterTo = params.get('counterTo', 0)

    tableAction = db.table('Action').alias('a1')

    cond = [tableAction['endDate'].datetimeGe(begDateTime),
            tableAction['endDate'].datetimeLe(endDateTime)]

    stmt = u"""SELECT
    a1.counterValue,
    ev.externalId,
    a1.endDate,
    Client.lastName as cl_lastName,
    Client.firstName as cl_firstName,
    Client.patrName as cl_patrName,
    Client.birthDate as cl_birthDate,
    vrbPerson.name as person_name,
    AP_org.title as organisation,        /* Кем направлен */
    AP_delivered.value as delivered_by,  /* Кем доставлен */
    AP_struct.name as structure,         /* Направлен в отделение */
    ap1.isAssigned as amb,               /* АМБ */
    ap2.isAssigned as passport,          /* Сдан паспорт */
    ap3.isAssigned as policy,            /* Сдан полис */
    AP_worth.value as worth,             /* Кв. ценностей № */
    AP_money.value as money              /* Кв. денежная № */
FROM
    Event ev
        INNER JOIN
    ActionType at1 ON at1.flatCode = 'actirovania'
        INNER JOIN
    ActionType at2 ON at2.flatCode = 'received'
        INNER JOIN
    Action a1 ON a1.actionType_id = at1.id AND a1.event_id = ev.id
        INNER JOIN
    Action a2 ON a2.actionType_id = at2.id AND a2.event_id = ev.id
        LEFT JOIN
    Client ON ev.client_id = Client.id
        LEFT JOIN
    vrbPerson ON a1.person_id = vrbPerson.id
        LEFT JOIN
    ActionPropertyType apt1 ON apt1.actionType_id = at1.id AND apt1.name = 'АМБ'
        LEFT JOIN
        ActionProperty ap1 ON ap1.action_id = a1.id AND ap1.type_id = apt1.id
        LEFT JOIN
    ActionPropertyType apt2 ON apt2.actionType_id = at1.id AND apt2.name = 'Сдан паспорт'
        LEFT JOIN
        ActionProperty ap2 ON ap2.action_id = a1.id AND ap2.type_id = apt2.id
        LEFT JOIN
    ActionPropertyType apt3 ON apt3.actionType_id = at1.id AND apt3.name = 'Сдан полис'
        LEFT JOIN
        ActionProperty ap3 ON ap3.action_id = a1.id AND ap3.type_id = apt3.id
        LEFT JOIN
    ActionPropertyType apt4 ON apt4.actionType_id = at1.id AND apt4.name = 'Кв. ценностей №'
        LEFT JOIN
        ActionProperty ap4 ON ap4.action_id = a1.id AND ap4.type_id = apt4.id
        LEFT JOIN
        ActionProperty_String AP_worth ON AP_worth.id = ap4.id
        LEFT JOIN
    ActionPropertyType apt5 ON apt5.actionType_id = at1.id AND apt5.name = 'Кв. денежная №'
        LEFT JOIN
        ActionProperty ap5 ON ap5.action_id = a1.id AND ap5.type_id = apt5.id
        LEFT JOIN
        ActionProperty_String AP_money ON AP_money.id = ap5.id
        LEFT JOIN
    ActionPropertyType apt6 ON apt6.actionType_id = at2.id AND apt6.name = 'Кем направлен'
        LEFT JOIN
        ActionProperty ap6 ON ap6.action_id = a2.id AND ap6.type_id = apt6.id
        LEFT JOIN
        ActionProperty_Organisation APO ON APO.id = ap6.id
        LEFT JOIN
        Organisation AP_org ON AP_org.id = APO.value
        LEFT JOIN
    ActionPropertyType apt7 ON apt7.actionType_id = at2.id AND apt7.name = 'Кем доставлен'
        LEFT JOIN
        ActionProperty ap7 ON ap7.action_id = a2.id AND ap7.type_id = apt7.id
        LEFT JOIN
        ActionProperty_String AP_delivered ON AP_delivered.id = ap7.id
        LEFT JOIN
    ActionPropertyType apt8 ON apt8.actionType_id = at2.id AND apt8.name = 'Направлен в отделение'
        LEFT JOIN
        ActionProperty ap8 ON ap8.action_id = a2.id AND ap8.type_id = apt8.id
        LEFT JOIN
        ActionProperty_OrgStructure APOS ON APOS.id = ap8.id
        LEFT JOIN
        OrgStructure AP_struct ON AP_struct.id = APOS.value
WHERE %s AND (IFNULL(CAST(a1.counterValue as DECIMAL),0) BETWEEN %d AND %d)
AND ev.deleted = 0
AND a1.deleted = 0
AND a2.deleted = 0
ORDER BY CAST(a1.counterValue as DECIMAL)
    """ % (db.joinAnd(cond), int(counterFrom), int(counterTo))
    return db.query(stmt)


class CReportActirovania(CReport):
    def __init__(self, parent):
        super(CReportActirovania, self).__init__(parent)
        self.setTitle(u'Журнал актирования')

    def getSetupDialog(self, parent):
        result = CReportActirovaniaSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)

        org_id = QtGui.qApp.currentOrgId()
        org_info = getOrganisationInfo(org_id)

        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(org_info.get('fullName'))
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(self.title())

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('4%',   [u'№ п/п'],                        CReportBase.AlignCenter),
            ('16%',  [u'Отделение,\n№ ИБ'],             CReportBase.AlignCenter),
            ('5%',   [u'Дата актирования'],             CReportBase.AlignCenter),
            ('15%',  [u'Фамилия Имя Отчество'],         CReportBase.AlignCenter),
            ('5%',   [u'Возраст,\nДата рождения'],      CReportBase.AlignCenter),
            ('20%',  [u'Кем направлен, доставлен'],     CReportBase.AlignCenter),
            ('15%',  [u'Наличие предметов подлежащих актированию'], CReportBase.AlignCenter),
            ('10%',  [u'Сдал'],                         CReportBase.AlignCenter),
            ('10%',  [u'Принял'],                       CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        total = 0
        total_passport = 0
        total_policy = 0
        while query.next():
            record = query.record()
            counterValue = forceString(record.value('counterValue'))
            externalId = forceString(record.value('externalId'))
            structure = forceString(record.value('structure'))
            date = forceString(record.value('endDate'))
            cl_lastName = record.value('cl_lastName')
            cl_firstName = record.value('cl_firstName')
            cl_patrName = record.value('cl_patrName')
            cl_birthDate = record.value('cl_birthDate')
            organisation = forceString(record.value('organisation'))
            delivered_by = forceString(record.value('delivered_by'))

            passport = u'Сдан паспорт' if forceInt(record.value('passport')) else u''
            policy = u'Сдан полис' if forceInt(record.value('policy')) else u''
            amb = u'АМБ' if forceInt(record.value('amb')) else u''
            total_passport += 1 if passport else 0
            total_policy += 1 if policy else 0

            worth = forceString(record.value('worth'))
            money = forceString(record.value('money'))
            person_name = forceString(record.value('person_name'))
            i = table.addRow()
            FIO = formatName(cl_lastName, cl_firstName, cl_patrName)
            table.setText(i, 0, counterValue)
            table.setText(i, 1, u'%s,\nиб: %s' % (structure, externalId))
            table.setText(i, 2, date)
            table.setText(i, 3, FIO)
            table.setText(i, 4, '%s\n%s' % (calcAge(cl_birthDate), forceString(cl_birthDate)))
            table.setText(i, 5, '%s\n%s' % (organisation, delivered_by))
            table.setText(i, 6, '\n'.join(filter(None, (passport,
                                                        policy,
                                                        amb,
                                                        u'Кв. ценностей № %s' % worth if worth else u'',
                                                        u'Кв. денежная № %s' % money if money else u''))))
            table.setText(i, 7, FIO)
            table.setText(i, 8, person_name)
            total += 1
        i = table.addRow()
        table.setText(i, 0, u'Итого: %d' % total, CReport.TableTotal, CReport.AlignLeft)
        table.setText(i, 6, u'Сдано паспортов: %d\nСдано полисов: %d' % (total_passport, total_policy), CReport.TableTotal, CReport.AlignLeft)
        table.mergeCells(i, 0, 1, 6)
        table.mergeCells(i, 6, 1, 3)
        return doc


class CReportActirovaniaSetup(QtGui.QDialog, Ui_ReportActirovaniaSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['begTime'] = self.edtBegTime.time()
        result['endTime'] = self.edtEndTime.time()
        result['counterFrom'] = self.edtCounterFrom.value()
        result['counterTo'] = self.edtCounterTo.value()
        return result

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime(8, 00)))
        self.edtEndTime.setTime(params.get('endTime', QtCore.QTime(7, 59)))
        self.edtCounterFrom.setValue(params.get('counterFrom', 0))
        self.edtCounterTo.setValue(params.get('counterTo', 999))
