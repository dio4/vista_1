# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceDouble, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportAccountingWork import Ui_ReportAccountingWork


def oldSelectData(params):
    begDate      = params.get('begDate', None)
    endDate      = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    personId     = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detailPerson = params.get('detailPerson', None)

    db = QtGui.qApp.db

    tablePerson           = db.table('Person')
    tableEvent            = db.table('Event')
    tableAction           = db.table('Action')
    tableEventType        = db.table('EventType')

    cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(endDate), tableAction['endDate'].dateGe(begDate)]),
                       db.joinAnd([tableAction['begDate'].isNull(), tableEvent['setDate'].dateLe(endDate), tableEvent['setDate'].dateGe(begDate)])])]
    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'


    stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                        count(if(Action.person_id = Person.id AND ActionType.code IN ('з103', 'з101'), Action.id, NULL)) AS countVisits,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'з103', Action.id, NULL)) AS countPrimary,
                        count(if(at_typeTeeth.code = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB LIKE 'K02%%', ActionProperty_String.id, NULL)) AS countCaries,
                        count(if(at_typeTeeth.code = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB LIKE 'K04%%', ActionProperty_String.id, NULL)) AS countComplicationCaries,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'p1' AND Diagnosis.MKB LIKE 'K04%%', Action.id, NULL)) AS countComplicationCariesSan,
                        sum(if(Action.person_id = Person.id AND ActionType.code IN ('з20105', 'з20106', 'з20107'), Action.amount, 0)) AS countCement,
                        sum(if(Action.person_id = Person.id AND ActionType.code IN ('з20108', 'з20109', 'з20110'), Action.amount, 0)) AS countComposite,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'заксл' AND Diagnosis.MKB LIKE 'K05%%', Action.id, NULL)) AS countPeriodontitis,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'заксл' AND Diagnosis.MKB IN ('K12.0', 'K12.1', 'K13.0', 'K13.2', 'K13.3', 'K14.6', 'K14.9'), Action.id, NULL)) AS countMucosa,
                        sum(if(Action.person_id = Person.id AND ActionType.code IN ('оЖ001ж', 'нстх030', 'нстх031', 'оЖ001и', 'оЖ001к', 'оЖ001з'), Action.amount, NULL)) AS countRemoved,
                        sum(if(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з318', 'з323', 'з324', 'з20517', 'з20518', 'з20519'), Action.amount, NULL)) AS operation,
                        count(if(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII'), Action.id, NULL)) AS countSan,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'СанI', Action.id, NULL)) AS countSanI,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('з20501', 'з125', 'з124'), Action.amount, 0)) AS countRemoval,
                        ROUND(SUM(IF(Action.person_id = Person.id, Action.uet * Action.amount,0)), 2) AS uet,
                        ROUND(SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з318', 'з323', 'з324', 'з20517', 'з20518', 'з20519'), Action.uet * Action.amount,0)), 2) AS uetOperation
                FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    LEFT JOIN ActionType at_typeTeeth ON at_typeTeeth.id = Action.actionType_id AND at_typeTeeth.flatCode = 'permanentTeeth' AND at_typeTeeth.deleted = 0
                    LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = at_typeTeeth.id AND ActionPropertyType.deleted = 0
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                    INNER JOIN Person ON Person.id IN (Action.person_id, Event.setPerson_id)
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id  AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                WHERE %s AND age(Client.birthDate, Event.setDate) >= 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                %s
                %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)


def newSelectData(params):
    begDate      = params.get('begDate', None)
    endDate      = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)
    specialityId = params.get('specialityId', None)
    personId     = params.get('personId', None)
    eventPurposeId = params.get('eventPurposeId', None)
    orgStructureId = params.get('orgStructureId', None)
    detailPerson = params.get('detailPerson', None)

    db = QtGui.qApp.db

    tablePerson           = db.table('Person')
    tableEvent            = db.table('Event')
    tableAction           = db.table('Action')
    tableEventType        = db.table('EventType')

    cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(endDate), tableAction['endDate'].dateGe(begDate)]),
                       db.joinAnd([tableAction['begDate'].isNull(), tableEvent['setDate'].dateLe(endDate), tableEvent['setDate'].dateGe(begDate)])])]
    group = ''
    order = ''

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if detailPerson:
        group = 'GROUP BY person'
        order = 'ORDER BY person'

    stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('стт005', 'стт006', 'стт007', 'стт08', 'стт010', 'стт011', 'стт012', 'стх001', 'стх002', 'нстх001','нстх002'), Action.id, NULL)) AS countVisits,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code IN ('стт005', 'стх001', 'настх001'), Action.id, NULL)) AS countPrimary,
                        COUNT(IF(at_typeTeeth.code = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB IN ('K02.0', 'K02.1', 'K02.3', 'K02.2', 'K02.8', 'K02.9'), ActionProperty_String.id, NULL)) AS countCaries,
                        COUNT(IF(at_typeTeeth.code = 'permanentTeeth' AND ActionProperty_String.value LIKE 'л%%' AND Diagnosis.MKB IN ('K04.0', 'K04.1', 'K04.4', 'K04.5', 'K05.2', 'K05.3'), ActionProperty_String.id, NULL)) AS countComplicationCaries,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'p1', Action.id, NULL)) AS countComplicationCariesSan,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('стт026', 'стт029', 'стт032'), Action.amount, 0)) AS countCement,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('стт027', 'стт030', 'стт033'), Action.amount, 0)) AS countComposite,
                        COUNT(IF(Action.person_id = Person.id AND ActionType.code = 'заксл' AND Diagnosis.MKB IN ('K05.3', 'K05.4', 'K05.5', 'K05.6'), Action.id, NULL)) AS countPeriodontitis,
                        count(IF(Action.person_id = Person.id AND ActionType.code = 'заксл' AND Diagnosis.MKB IN (
                            'K12.0', 'K12.1', 'K12.2',
                            'K13.0', 'K13.1', 'K13.2', 'K13.3', 'K13.4', 'K13.5', 'K13.6', 'K13.7', 'K13.8', 'K13.9',
                            'K14.0', 'K14.1', 'K14.2', 'K14.3', 'K14.4', 'K14.5', 'K14.6', 'K14.7', 'K14.8', 'K14.9'
                        ), Action.id, NULL)) AS countMucosa,
                        sum(if(Action.person_id = Person.id AND ActionType.code IN ('стх030', 'стх031', 'стх034', 'нстх030','нстх031'), Action.amount, NULL)) AS countRemoved,
                        count( distinct IF(Action.person_id = Person.id ,(SELECT Action1.id
                       FROM Action Action1
                       INNER JOIN ActionType at ON Action1.actionType_id
                          INNER JOIN Person ON Person.speciality_id = 98
                       INNER JOIN ActionPropertyType apt ON apt.actionType_id = at.id AND apt.deleted = 0
                       INNER JOIN ActionProperty ap ON ap.action_id = Action1.id AND ap.type_id = apt.id AND ap.deleted = 0
                       INNER JOIN ActionProperty_String aps ON aps.id = ap.id AND aps.value LIKE 'о'
                       WHERE Person.id = Event.execPerson_id AND Action1.deleted =0 AND Event.id = Action1.event_id), NULL)) AS operation,
                       count(if(Action.person_id = Person.id AND ActionType.code IN ('СанI', 'СанII'), Action.id, NULL)) AS countSan,
                        count(if(Action.person_id = Person.id AND ActionType.code = 'СанI', Action.id, NULL)) AS countSanI,
                        SUM(IF(Action.person_id = Person.id AND ActionType.code LIKE 'стт041', Action.amount, 0)) AS countRemoval,
                        ROUND(SUM(IF(Action.person_id = Person.id, Action.uet * Action.amount,0)), 2) AS uet,
                        ROUND(SUM(IF(Action.person_id = Person.id AND ( ( Diagnosis.MKB IN ('K01.0', 'K01.1') AND ActionType.code IN ('стх034') ) OR ( ActionType.code IN ('стх019', 'стх028', 'стх032', 'стх033', 'стх020', 'стх021', 'стх022', 'стх023', 'стх024') ) ), Action.uet * Action.amount,0)), 2) AS uetOperation
                FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    LEFT JOIN ActionType at_typeTeeth ON at_typeTeeth.id = Action.actionType_id AND at_typeTeeth.flatCode = 'permanentTeeth' AND at_typeTeeth.deleted = 0
                    LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.deleted = 0
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                    INNER JOIN Person ON Person.id = Action.person_id OR Event.setPerson_id = Person.id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                WHERE %s AND age(Client.birthDate, Event.setDate) >= 18  AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                %s
                %s''' % (db.joinAnd(cond), group, order)

    return db.query(stmt)


class CReportAccountingWork(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сводная ведомость учета рабочего времени(ф.39)')

    def getSetupDialog(self, parent):
        result = CAccountingWork(parent)
        result.setTitle(self.title())
        result.chkGroup.setVisible(False)
        return result

    def build(self, params):
        detailPerson = params.get('detailPerson', False)
        if params['actionTypeCode'] == 0:  # 0 - з, 1 - стх
            query = oldSelectData(params)
        else:
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
                        ('%10', [u'ФИО'                                                                                                      ], CReportBase.AlignRight),
                        ('%5',  [u'Принято больных (всего)'                                                                                  ], CReportBase.AlignLeft),
                        ('%5',  [u'Принято первичных больных',                                                                               ], CReportBase.AlignLeft),
                        ('%5',  [u'Запломбировано зубов',                                   u'всего'                                         ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'в том числе по поводу',       u'кариеса'       ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'',                            u'его осложнений'], CReportBase.AlignLeft),
                        ('%5',  [u'Вылечено зубов в одно посещ. по поводу осложн. кариеса'                                                   ], CReportBase.AlignLeft),
                        ('%5',  [u'Количество пломб',                                       u'всего'                                         ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'цемент'                                        ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'композит'                                      ], CReportBase.AlignLeft),
                        ('%5',  [u'Проведен курс лечения',                                  u'заболеваний пародонтита'                       ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'слизистой оболочки полости рта'                ], CReportBase.AlignLeft),
                        ('%5',  [u'Удалено зубов постоянного прикуса (всего)'                                                                ], CReportBase.AlignLeft),
                        ('%5',  [u'Произведено операций'                                                                                     ], CReportBase.AlignLeft),
                        ('%5',  [u'Cанировано',                                             u'всего'                                         ], CReportBase.AlignLeft),
                        ('%5',  [u'',                                                       u'Санация I'                                     ], CReportBase.AlignLeft),
                        ('%5',  [u'Снятие зубн.отл.'                                                                                         ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ по операции'                                                                                          ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'                                                                                                      ], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 3, 1)
        table.mergeCells(0, 7, 1, 3)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(0, 10, 1, 2)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(0, 12, 3, 1)
        table.mergeCells(0, 13, 3, 1)
        table.mergeCells(0, 14, 1, 2)
        table.mergeCells(1, 14, 2, 1)
        table.mergeCells(1, 15, 2, 1)
        table.mergeCells(0, 16, 3, 1)
        table.mergeCells(0, 17, 3, 1)
        table.mergeCells(0, 18, 3, 1)

        total = [0] * (len(tableColumns) - 1)

        while query.next():
            record = query.record()
            countVisits = forceInt(record.value('countVisits'))
            countPrimary = forceInt(record.value('countPrimary'))
            countCaries= forceInt(record.value('countCaries'))
            countComplicationCaries = forceInt(record.value('countComplicationCaries'))
            countComplicationCariesSan = forceInt(record.value('countComplicationCariesSan'))
            countCement = forceInt(record.value('countCement'))
            countComposite = forceInt(record.value('countComposite'))
            countPeriodontitis = forceInt(record.value('countPeriodontitis'))
            countMucosa = forceInt(record.value('countMucosa'))
            countRemoved = forceInt(record.value('countRemoved'))
            operation = forceInt(record.value('operation'))
            countSan = forceInt(record.value('countSan'))
            countSanI = forceInt(record.value('countSanI'))
            countRemoval = forceInt(record.value('countRemoval'))
            uetOperation = forceDouble(record.value('uetOperation'))
            uet = forceDouble(record.value('uet'))

            if detailPerson:
                i = table.addRow()
                table.setText(i, 0, forceString(record.value('person')))
                table.setText(i, 1, countVisits)
                table.setText(i, 2, countPrimary)
                table.setText(i, 3, countCaries + countComplicationCaries)
                table.setText(i, 4, countCaries)
                table.setText(i, 5, countComplicationCaries)
                table.setText(i, 6, countComplicationCariesSan)
                table.setText(i, 7, countCement + countComposite)
                table.setText(i, 8, countCement)
                table.setText(i, 9, countComposite)
                table.setText(i, 10, countPeriodontitis)
                table.setText(i, 11, countMucosa)
                table.setText(i, 12, countRemoved)
                table.setText(i, 13, operation)
                table.setText(i, 14, countSan)
                table.setText(i, 15, countSanI)
                table.setText(i, 16, countRemoval)
                table.setText(i, 17, uetOperation)
                table.setText(i, 18, uet)

            total[0] += countVisits
            total[1] += countPrimary
            total[2] += countCaries + countComplicationCaries
            total[3] += countCaries
            total[4] += countComplicationCaries
            total[5] += countComplicationCariesSan
            total[6] += countCement + countComposite
            total[7] += countCement
            total[8] += countComposite
            total[9] += countPeriodontitis
            total[10] += countMucosa
            total[11] += countRemoved
            total[12] += operation
            total[13] += countSan
            total[14] += countSanI
            total[15] += countRemoval
            total[16] += uetOperation
            total[17] += uet

        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for index, value in enumerate(total):
            table.setText(i, index + 1, value, CReportBase.TableTotal)

        return doc


class CAccountingWork(QtGui.QDialog, Ui_ReportAccountingWork):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpetiality.setTable('rbSpeciality', True)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSpetiality.setValue(params.get('rbSpeciality', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkGroup.setChecked(params.get('group', False))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkDetailPerson.setChecked(params.get('detailPerson', False))
        self.cmbActionType.setCurrentIndex(params.get('actionTypeCode', 0))


    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['eventTypeId'] = self.cmbEventType.value()
        params['personId']    = self.cmbPerson.value()
        params['specialityId'] = self.cmbSpetiality.value()
        params['group']       = self.chkGroup.isChecked()
        params['eventPurposeId'] = self.cmbEventPurpose.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['detailPerson'] = self.chkDetailPerson.isChecked()
        params['actionTypeCode'] = self.cmbActionType.currentIndex()
        return params

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbSpetiality_currentIndexChanged(self, index):
        specialityId = self.cmbSpetiality.value()
        self.cmbPerson.setSpecialityId(specialityId)

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)