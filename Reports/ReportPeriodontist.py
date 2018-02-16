# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportPeriodontist import Ui_ReportPeriodontist
from library.Utils import forceDouble, forceInt, forceString


def oldSelectData(params):
    begDate      = params.get('begDate', None).toString(QtCore.Qt.ISODate)
    endDate      = params.get('endDate', None).toString(QtCore.Qt.ISODate)
    eventTypeId  = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    personId     = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detailPerson   = params.get('detailPerson', False)

    db = QtGui.qApp.db
    tablePerson    = db.table('Person')
    tableAction    = db.table('Action')
    tableEvent     = db.table('Event')
    tableEventType = db.table('EventType')

    cond = [tableAction['endDate'].dateLe(endDate),
            tableAction['endDate'].dateGe(begDate)]
    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'

    stmt = u'''SELECT  CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                        COUNT(IF(ActionType.code = 'з103', Action.id, NULL)) AS countPrimary,
                        COUNT(IF(ActionType.code = 'з101', Action.id, NULL)) AS countRepeat,
                        COUNT(IF(ActionType.code = 'заксл' AND Diagnosis.MKB LIKE 'K05%%', Action.id, NULL)) AS countFinished,
                        sum(IF(ActionType.code IN ('з20513', 'з20514'), Action.amount, 0)) AS countDrugTreatment,
                        SUM(IF(ActionType.code IN ('з20501', 'з125'), Action.amount, 0)) AS countRemoval,
                        SUM(IF(ActionType.code = 'з20510', Action.amount, 0)) AS countCurettage,
                        COUNT(IF(ActionType.code = 'з20503', Action.id, NULL)) AS countTherapy,
                        SUM(IF(ActionType.code IN('з11101', 'з11102'), Action.amount, 0)) AS countInjection,
                        SUM(IF(ActionType.code IN('з20517', 'з20518', 'з20519'), Action.amount, 0)) AS countOperation,
                        count(if(ActionType.code = 'заксл' AND Diagnosis.MKB IN ('K12.0', 'K12.1', 'K13.0', 'K13.2', 'K13.3', 'K14.6', 'K14.9'), Action.id, NULL)) AS countMucosa,
                        ROUND(SUM(Action.uet * Action.amount), 2) AS uet,
                        ROUND(SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20517', 'з20518', 'з20519'), Action.uet * Action.amount,0)), 2) AS uetOperation
                FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    INNER JOIN Person ON Person.id  = Action.person_id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                WHERE %s AND age(Client.birthDate, Event.setDate) >= 18 AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                %s
                %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)


def newSelectData(params):
    begDate      = params.get('begDate', None).toString(QtCore.Qt.ISODate)
    endDate      = params.get('endDate', None).toString(QtCore.Qt.ISODate)
    eventTypeId  = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    personId     = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detailPerson   = params.get('detailPerson', False)

    db = QtGui.qApp.db
    tablePerson    = db.table('Person')
    tableAction    = db.table('Action')
    tableEvent     = db.table('Event')
    tableEventType = db.table('EventType')

    cond = [tableAction['endDate'].dateLe(endDate),
            tableAction['endDate'].dateGe(begDate)]
    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'

    stmt = u'''SELECT  CONCAT_WS(' ', Person.lastName , Person.firstName, Person.patrName) AS person,
                        COUNT(DISTINCT IF(ActionType.code = 'стт005', Action.id, NULL)) AS countPrimary,
                        COUNT(DISTINCT IF(ActionType.code = 'стт006', Action.id, NULL)) AS countRepeat,
                        COUNT(DISTINCT IF(ActionType.code = 'заксл' AND Diagnosis.MKB LIKE 'K05%%', Action.id, NULL)) AS countFinished,
                        SUM(IF(ActionType.code IN ('стт018', 'стт019'), Action.amount, 0)) AS countDrugTreatment,
                        SUM(IF(ActionType.code = 'стт041', Action.amount, 0)) AS countRemoval,
                        SUM(IF(ActionType.code = 'стт047', Action.amount, 0)) AS countCurettage,
                        COUNT(DISTINCT IF(ActionType.code IN ('сто016', 'стф009'), Action.id, NULL)) AS countTherapy,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN('сто001', 'сто002', 'сто003', 'сто010'), Action.amount, 0)) AS countInjection,
                        COUNT(DISTINCT IF(Action.person_id = Person.id AND act_operation.id , Event.id, NULL)) AS countOperation,
                        COUNT(DISTINCT IF(ActionType.code = 'заксл' AND Diagnosis.MKB IN (
                            'K12.0', 'K12.1', 'K12.2',
                            'K13.0', 'K13.1', 'K13.2', 'K13.3', 'K13.4', 'K13.5', 'K13.6', 'K13.7', 'K13.8', 'K13.9',
                            'K14.0', 'K14.1', 'K14.2', 'K14.3', 'K14.4', 'K14.5', 'K14.6', 'K14.7', 'K14.8', 'K14.9'
                        ), Action.id, NULL)) AS countMucosa,
                        ROUND(SUM(Action.uet * Action.amount), 2) AS uet,
                        ROUND(SUM(IF(Action.person_id = Person.id AND act_operation.id, Action.uet * Action.amount,0)), 2) AS uetOperation,
                        COUNT(DISTINCT IF(prim_operation.id, prim_operation.event_id, 0)) AS countPrimaryVisits
                FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    -- LEFT JOIN ActionPropertyType apt_s ON apt_s.actionType_id = ActionType.id AND apt_s.deleted = 0
                    -- LEFT JOIN ActionProperty ap_s ON ap_s.action_id = Action.id AND ap_s.type_id = apt_s.id AND ap_s.deleted = 0
                    -- LEFT JOIN ActionProperty_String AP_String ON AP_String.id = ap_s.id
                    LEFT JOIN (SELECT Action.event_id, Action.id
                       FROM Action
                       INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode IN ('permanentTeeth','calfTeeth')
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE '%%о%%'
                       WHERE Action.deleted =0) act_operation ON act_operation.event_id = Event.id
                    LEFT JOIN (SELECT Action.event_id, Action.id
                       FROM Action
                       INNER JOIN ActionType at ON Action.actionType_id AND at.flatCode IN ('permanentTeeth','calfTeeth')
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String ON ActionProperty_String.id = ap.id AND ActionProperty_String.value LIKE '%%п%%'
                       WHERE Action.deleted =0) prim_operation ON prim_operation.event_id = Event.id
                    INNER JOIN Person ON Person.id  = Action.person_id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                WHERE %s AND age(Client.birthDate, Event.setDate) >= 18 AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                %s
                %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)

class CReportPeriodontist(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет врача пародонтолога')

    def getSetupDialog(self, parent):
        result = CPeriodontist(parent)
        result.setTitle(self.title())
        return result

    def oldBuildFormat(self, params):
        detailPerson = params.get('detailPerson', False)
        query = oldSelectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%2', [u'№ п/п'], CReportBase.AlignRight),
            ('%30', [u'Фамилия, Имя, Отчество'], CReportBase.AlignLeft),
            ('%5', [u'Всего'], CReportBase.AlignLeft),
            ('%5', [u'Формы пародонтоза', u'Первичный'], CReportBase.AlignLeft),
            ('%5', [u'', u'Повторный'], CReportBase.AlignLeft),
            ('%5', [u'', u'Законченное лечение'], CReportBase.AlignLeft),
            ('%5', [u'Лечение', u'Медикаментозная обработка'], CReportBase.AlignLeft),
            ('%5', [u'', u'Снятие зубн.отл.'], CReportBase.AlignLeft),
            ('%5', [u'', u'Кюретаж'], CReportBase.AlignLeft),
            ('%5', [u'', u'Вакуумтерапия'], CReportBase.AlignLeft),
            ('%5', [u'', u'Иньекции'], CReportBase.AlignLeft),
            ('%5', [u'', u'Слизистая оболочка полости рта'], CReportBase.AlignLeft),
            ('%5', [u'', u'Трудовые ед.'], CReportBase.AlignLeft),
            ('%5', [u'Операции'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ на операции'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 6, 1, 7)
        table.mergeCells(0, 13, 2, 1)
        table.mergeCells(0, 14, 2, 1)

        total = [0] * 13
        while query.next():
            record = query.record()
            person = forceString(record.value('person'))
            countPrimary = forceInt(record.value('countPrimary'))
            countRepeat = forceInt(record.value('countRepeat'))
            countFinished = forceInt(record.value('countFinished'))
            countDrugTreatment = forceInt(record.value('countDrugTreatment'))
            countRemoval = forceInt(record.value('countRemoval'))
            countCurettage = forceInt(record.value('countCurettage'))
            countTherapy = forceInt(record.value('countTherapy'))
            countInjection = forceInt(record.value('countInjection'))
            uet = forceDouble(record.value('uet'))
            countMucosa = forceInt(record.value('countMucosa'))
            countOperation = forceInt(record.value('countOperation'))
            uetOperation = forceDouble(record.value('uetOperation'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, i - 1)
                table.setText(i, 1, person)
                table.setText(i, 2, countPrimary + countRepeat)
                table.setText(i, 3, countPrimary)
                table.setText(i, 4, countRepeat)
                table.setText(i, 5, countFinished)
                table.setText(i, 6, countDrugTreatment)
                table.setText(i, 7, countRemoval)
                table.setText(i, 8, countCurettage)
                table.setText(i, 9, countTherapy)
                table.setText(i, 10, countInjection)
                table.setText(i, 11, countMucosa)
                table.setText(i, 12, uet)
                table.setText(i, 13, countOperation)
                table.setText(i, 14, uetOperation)
            total[0] += countPrimary + countRepeat
            total[1] += countPrimary
            total[2] += countRepeat
            total[3] += countFinished
            total[4] += countDrugTreatment
            total[5] += countRemoval
            total[6] += countCurettage
            total[7] += countTherapy
            total[8] += countInjection
            total[9] += countMucosa
            total[10] += uet
            total[11] += countOperation
            total[12] += uetOperation
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 2, value, CReportBase.TableTotal)
        return doc

    def newBuildFormat(self, params):
        detailPerson = params.get('detailPerson', False)
        query = newSelectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('%2', [u'№ п/п'], CReportBase.AlignRight),
            ('%30', [u'Фамилия, Имя, Отчество'], CReportBase.AlignLeft),
            ('%5', [u'Всего'], CReportBase.AlignLeft),
            ('%5', [u'Формы пародонтоза', u'Первичный'], CReportBase.AlignLeft),
            ('%5', [u'', u'Повторный'], CReportBase.AlignLeft),
            ('%5', [u'', u'Законченное лечение'], CReportBase.AlignLeft),
            ('%5', [u'Лечение', u'Медикаментозная обработка'], CReportBase.AlignLeft),
            ('%5', [u'', u'Снятие зубн.отл.'], CReportBase.AlignLeft),
            ('%5', [u'', u'Кюретаж'], CReportBase.AlignLeft),
            ('%5', [u'', u'Вакуумтерапия'], CReportBase.AlignLeft),
            ('%5', [u'', u'Иньекции'], CReportBase.AlignLeft),
            ('%5', [u'', u'Слизистая оболочка полости рта'], CReportBase.AlignLeft),
            # ('%5', [u'', u'Трудовые ед.'], CReportBase.AlignLeft),
            ('%5', [u'Операции'], CReportBase.AlignLeft),
            ('%5', [u'УЕТ на операции'], CReportBase.AlignLeft),
            ('%5', [u'Всего УЕТ'], CReportBase.AlignLeft),
            ('%5', [u'Первичный прием'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 6, 1, 6)
        table.mergeCells(0, 12, 2, 1)
        table.mergeCells(0, 13, 2, 1)
        table.mergeCells(0, 14, 2, 1)
        table.mergeCells(0, 15, 2, 1)

        total = [0] * 14
        while query.next():
            record = query.record()
            person = forceString(record.value('person'))
            countPrimary = forceInt(record.value('countPrimary'))
            countRepeat = forceInt(record.value('countRepeat'))
            countFinished = forceInt(record.value('countFinished'))
            countDrugTreatment = forceInt(record.value('countDrugTreatment'))
            countRemoval = forceInt(record.value('countRemoval'))
            countCurettage = forceInt(record.value('countCurettage'))
            countTherapy = forceInt(record.value('countTherapy'))
            countInjection = forceInt(record.value('countInjection'))
            uet = forceDouble(record.value('uet'))
            countMucosa = forceInt(record.value('countMucosa'))
            countOperation = forceInt(record.value('countOperation'))
            uetOperation = forceDouble(record.value('uetOperation'))
            countPrimaryVisits = forceInt(record.value('countPrimaryVisits'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, i - 1)
                table.setText(i, 1, person)
                table.setText(i, 2, countPrimary + countRepeat)
                table.setText(i, 3, countPrimary)
                table.setText(i, 4, countRepeat)
                table.setText(i, 5, countFinished)
                table.setText(i, 6, countDrugTreatment)
                table.setText(i, 7, countRemoval)
                table.setText(i, 8, countCurettage)
                table.setText(i, 9, countTherapy)
                table.setText(i, 10, countInjection)
                table.setText(i, 11, countMucosa)
                # table.setText(i, 12, uet)
                table.setText(i, 12, countOperation)
                table.setText(i, 13, uetOperation)
                table.setText(i, 14, uet)
                table.setText(i, 15, countPrimaryVisits)
            total[0] += countPrimary + countRepeat
            total[1] += countPrimary
            total[2] += countRepeat
            total[3] += countFinished
            total[4] += countDrugTreatment
            total[5] += countRemoval
            total[6] += countCurettage
            total[7] += countTherapy
            total[8] += countInjection
            total[9] += countMucosa
            # total[10] += uet
            total[10] += countOperation
            total[11] += uetOperation
            total[12] += uet
            total[13] += countPrimaryVisits
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 2, value, CReportBase.TableTotal)
        return doc

    def build(self, params):
        if params['actionType'] == 0:  # 0 - з, 1 - стх
            return self.oldBuildFormat(params)
        else:
            return self.newBuildFormat(params)


class CPeriodontist(QtGui.QDialog, Ui_ReportPeriodontist):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkDetailPerson.setChecked(params.get('detailPerson', False))
        self.cmbActionType.setCurrentIndex(params.get('actionType', 0))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['eventTypeId'] = self.cmbEventType.value()
        params['specialityId'] = self.cmbSpeciality.value()
        params['personId'] = self.cmbPerson.value()
        params['eventPurposeId'] = self.cmbEventPurpose.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['detailPerson'] = self.chkDetailPerson.isChecked()
        params['actionType'] = self.cmbActionType.currentIndex()
        return params

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
            self.cmbResult.setFilter('eventPurpose_id=%d' % eventPurposeId)
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pz12',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportPeriodontist(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
