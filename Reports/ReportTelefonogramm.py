# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceString, formatName, calcAge
from Orgs.Utils         import getOrganisationInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportTelefonogrammSetup import Ui_ReportTelefonogrammSetupDialog


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

    tableAction = db.table('Action').alias('a_tele')
    tableViewTelefono = db.table('ActionProperty_String').alias('aps_view_telefono')

    cond = [tableAction['begDate'].datetimeGe(begDateTime),
            tableAction['begDate'].datetimeLe(endDateTime)]

    if params.get('viewTeleChecked'):
        cond.append(tableViewTelefono['value'].eq(params.get('viewTele')))

    stmt = u"""SELECT
    a_tele.counterValue,
    ev.externalId,                                      /* № истории болезни */
    a_rece.begDate as date_received,                    /* Дата поступления */
    a_tele.begDate as date_give,                        /* Дата и время передачи */
    person_giver.name as person_giver,                  /* кто передал */
    person_doctor.name as person_doctor,                /* кто назначил */
    Client.lastName as cl_lastName,
    Client.firstName as cl_firstName,
    Client.patrName as cl_patrName,
    Client.birthDate as cl_birthDate,
    os.name as org_structure,                           /* Направлен в отделение */
    org.title as organisation,                          /* Кем направлен */
    aps_courier.value as courier,                       /* Кем доставлен */
    aps_diagnosis.value as diagnosis,                   /* Диагноз приемного отделения */
    aps_state.value as state,                           /* Cостояние пациента */
    getClientRegAddress(ev.client_id) as client_address,
    getClientWork(ev.client_id) as client_work,
    aps_n_tele.value as n_tele,                         /* № Телефонограммы */
    aps_militia.value as militia,                       /* Отделение милиции */
    aps_taker.value as who_took,                        /* Кто принял */
    aps_telefonogramma.value as telefonogramma,         /* Телефонограмма */
    aps_view_telefono.value as view_telefono            /* Вид телефонограммы */
FROM
    Event ev
        INNER JOIN
    ActionType at_tele ON at_tele.flatCode = 'telefonogramma'
        INNER JOIN
    ActionType at_rece ON at_rece.flatCode = 'received'
        INNER JOIN
    Action a_tele ON a_tele.actionType_id = at_tele.id AND a_tele.event_id = ev.id
        INNER JOIN
    Action a_rece ON a_rece.actionType_id = at_rece.id AND a_rece.event_id = ev.id
        LEFT JOIN
    Client ON ev.client_id = Client.id
        LEFT JOIN
    vrbPerson person_giver ON person_giver.id = a_tele.person_id
        LEFT JOIN
    vrbPerson person_doctor ON person_doctor.id = a_rece.setPerson_id
        LEFT JOIN
    ActionPropertyType apt1 ON apt1.actionType_id = at_rece.id AND apt1.name = 'Направлен в отделение'
        LEFT JOIN
        ActionProperty ap1 ON ap1.type_id = apt1.id AND ap1.action_id = a_rece.id
        LEFT JOIN
        ActionProperty_OrgStructure apos ON apos.id = ap1.id
        LEFT JOIN
        OrgStructure os ON os.id = apos.value
        LEFT JOIN
    ActionPropertyType apt2 ON apt2.actionType_id = at_rece.id AND apt2.name = 'Кем направлен'
        LEFT JOIN
        ActionProperty ap2 ON ap2.type_id = apt2.id AND ap2.action_id = a_rece.id
        LEFT JOIN
        ActionProperty_Organisation apo ON apo.id = ap2.id
        LEFT JOIN
        Organisation org ON org.id = apo.value
        LEFT JOIN
    ActionPropertyType apt3 ON apt3.actionType_id = at_rece.id AND apt3.name = 'Кем доставлен'
        LEFT JOIN
        ActionProperty ap3 ON ap3.type_id = apt3.id AND ap3.action_id = a_rece.id
        LEFT JOIN
        ActionProperty_String aps_courier ON aps_courier.id = ap3.id
        LEFT JOIN
    ActionPropertyType apt4 ON apt4.actionType_id = at_rece.id AND apt4.name = 'Диагноз приемного отделения'
        LEFT JOIN
        ActionProperty ap4 ON ap4.type_id = apt4.id AND ap4.action_id = a_rece.id
        LEFT JOIN
        ActionProperty_String aps_diagnosis ON aps_diagnosis.id = ap4.id
        LEFT JOIN
    ActionPropertyType apt5 ON apt5.actionType_id = at_rece.id AND apt5.name = 'Cостояние пациента'
        LEFT JOIN
        ActionProperty ap5 ON ap5.type_id = apt5.id AND ap5.action_id = a_rece.id
        LEFT JOIN
        ActionProperty_String aps_state ON aps_state.id = ap5.id
        LEFT JOIN
    ActionPropertyType apt6 ON apt6.actionType_id = at_tele.id AND apt6.name = '№ Телефонограммы'
        LEFT JOIN
        ActionProperty ap6 ON ap6.type_id = apt6.id AND ap6.action_id = a_tele.id
        LEFT JOIN
        ActionProperty_String aps_n_tele ON aps_n_tele.id = ap6.id
        LEFT JOIN
    ActionPropertyType apt7 ON apt7.actionType_id = at_tele.id AND apt7.name = 'Отделение милиции'
        LEFT JOIN
        ActionProperty ap7 ON ap7.type_id = apt7.id AND ap7.action_id = a_tele.id
        LEFT JOIN
        ActionProperty_String aps_militia ON aps_militia.id = ap7.id
        LEFT JOIN
    ActionPropertyType apt8 ON apt8.actionType_id = at_tele.id AND apt8.name = 'Кто принял'
        LEFT JOIN
        ActionProperty ap8 ON ap8.type_id = apt8.id AND ap8.action_id = a_tele.id
        LEFT JOIN
        ActionProperty_String aps_taker ON aps_taker.id = ap8.id
        LEFT JOIN
    ActionPropertyType apt9 ON apt9.actionType_id = at_tele.id AND apt9.name = 'Телефонограмма'
        LEFT JOIN
        ActionProperty ap9 ON ap9.type_id = apt9.id AND ap9.action_id = a_tele.id
        LEFT JOIN
        ActionProperty_String aps_telefonogramma ON aps_telefonogramma.id = ap9.id
        LEFT JOIN
    ActionPropertyType apt10 ON apt10.actionType_id = at_tele.id AND apt10.name = 'Вид телефонограммы'
        LEFT JOIN
        ActionProperty ap10 ON ap10.type_id = apt10.id AND ap10.action_id = a_tele.id
        LEFT JOIN
        ActionProperty_String aps_view_telefono ON aps_view_telefono.id = ap10.id
    WHERE %s AND (IFNULL(CAST(a_tele.counterValue as DECIMAL),0) BETWEEN %d AND %d)
    AND ev.deleted = 0
    AND a_tele.deleted = 0
    AND a_rece.deleted = 0
    ORDER BY CAST(a_tele.counterValue as DECIMAL)
    """ % (db.joinAnd(cond), int(counterFrom), int(counterTo))
    return db.query(stmt)


class CReportTelefonogramm(CReport):
    def __init__(self, parent):
        super(CReportTelefonogramm, self).__init__(parent)
        self.setTitle(u'Журнал телефонограмм')

    def getSetupDialog(self, parent):
        result = CReportTelefonogrammSetup(parent)
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
            ('4%',  [u'№ по журналу, Отделение, № телефонограммы, № истории болезни'],  CReportBase.AlignCenter),
            ('6%',  [u'Дата поступления,\nВремя'],                                      CReportBase.AlignCenter),
            ('13%', [u'Кем направлен\nКем доставлен'],                                  CReportBase.AlignCenter),
            ('13%', [u'Диагноз приемного отделения / тяж.сост.'],                       CReportBase.AlignCenter),
            ('10%', [u'Фамилия Имя Отчество'],                                          CReportBase.AlignCenter),
            ('5%',  [u'Возраст, Дата рождения'],                                        CReportBase.AlignCenter),
            ('15%', [u'Домашний адрес; Место работы, должность'],                       CReportBase.AlignCenter),
            ('10%', [u'Телефонограмма'],                                                CReportBase.AlignCenter),
            ('7%',  [u'ФИО врача'],                                                     CReportBase.AlignCenter),
            ('7%',  [u'Кто передал, Куда передавал'],                                   CReportBase.AlignCenter),
            ('10%',  [u'Кто принял; Дата, время передачи'],                             CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        total = 0
        while query.next():
            record = query.record()

            counterValue = forceString(record.value('counterValue'))
            externalId = forceString(record.value('externalId'))
            date_received = forceString(record.value('date_received'))
            date_give = forceString(record.value('date_give'))

            cl_lastName = record.value('cl_lastName')
            cl_firstName = record.value('cl_firstName')
            cl_patrName = record.value('cl_patrName')
            cl_birthDate = record.value('cl_birthDate')

            person_giver = forceString(record.value('person_giver'))
            person_doctor = forceString(record.value('person_doctor'))
            org_structure = forceString(record.value('org_structure'))
            organisation = forceString(record.value('organisation'))
            courier = forceString(record.value('courier'))
            diagnosis = forceString(record.value('diagnosis'))
            state = forceString(record.value('state'))
            client_address = forceString(record.value('client_address'))
            client_work = forceString(record.value('client_work'))
            n_tele = forceString(record.value('n_tele'))
            militia = forceString(record.value('militia'))
            who_took = forceString(record.value('who_took'))
            telefonogramma = forceString(record.value('telefonogramma'))
            view_telefono = forceString(record.value('view_telefono'))

            i = table.addRow()

            table.setText(i, 0, u'Жур.№%s\nОтд: %s\n№%s\nиб: %s' % (counterValue, org_structure, n_tele, externalId))
            table.setText(i, 1, '%s' % date_received)
            table.setText(i, 2, '%s\n%s' % (organisation, courier))
            table.setText(i, 3, '%s\n/%s' % (diagnosis, state))
            table.setText(i, 4, formatName(cl_lastName, cl_firstName, cl_patrName))
            table.setText(i, 5, '%s\n%s' % (calcAge(cl_birthDate), forceString(cl_birthDate)))
            table.setText(i, 6, '%s\n%s' % (client_address, client_work))
            table.setText(i, 7, '%s\n(%s)' % (telefonogramma, view_telefono))
            table.setText(i, 8, '%s' % person_doctor)
            table.setText(i, 9, '%s\n%s' % (person_giver, militia))
            table.setText(i, 10, '%s\n%s' % (who_took, date_give))
            total += 1
        i = table.addRow()
        table.setText(i, 0, u'Итого: %d' % total, CReport.TableTotal, CReport.AlignLeft)
        table.mergeCells(i, 0, 1, 11)
        return doc


class CReportTelefonogrammSetup(QtGui.QDialog, Ui_ReportTelefonogrammSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        valueDomain = QtGui.qApp.db.translate('ActionPropertyType', 'name', u'Вид телефонограммы', 'valueDomain')
        self.cmbTelefonoView.setDomain(forceString(valueDomain))

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

        isChecked = self.chkTelefonoView.isChecked()
        self.cmbTelefonoView.setEnabled(isChecked)
        result['viewTeleChecked'] = isChecked
        result['viewTele'] = self.cmbTelefonoView.currentText() if isChecked else ''

        return result

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime(8, 00)))
        self.edtEndTime.setTime(params.get('endTime', QtCore.QTime(7, 59)))
        self.edtCounterFrom.setValue(params.get('counterFrom', 0))
        self.edtCounterTo.setValue(params.get('counterTo', 999))
        self.chkTelefonoView.setChecked(params.get('viewTeleChecked', False))
        self.cmbTelefonoView.setEnabled(params.get('viewTeleChecked', False))

    @QtCore.pyqtSlot(bool)
    def on_chkTelefonoView_toggled(self, checked):
        self.cmbTelefonoView.setEnabled(checked)
