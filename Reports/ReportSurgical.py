# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils          import forceDouble, forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from ReportAccountingWork import CAccountingWork

class CReportData():
    def __init__(self, params):
        self.begDate      = params.get('begDate', None)
        self.endDate      = params.get('endDate', None)
        self.eventTypeId  = params.get('eventTypeId', None)
        self.specialityId = params.get('specialityId', None)
        self.personId     = params.get('personId', None)
        self.eventPurposeId = params.get('eventPurposeId', None)
        self.orgStructureId = params.get('orgStructureId', None)
        self.detailPerson   = params.get('detailPerson', False)
        self.actionTypeCode = params.get('actionTypeCode', None)

    def selectData(self):

        db = QtGui.qApp.db

        tablePerson           = db.table('Person')
        tableEvent            = db.table('Event')
        tableAction           = db.table('Action')
        tableEventType        = db.table('EventType')

        cond = [db.joinOr([db.joinAnd([tableAction['endDate'].dateLe(self.endDate), tableAction['endDate'].dateGe(self.begDate)]),
                           db.joinAnd([ tableEvent['setDate'].dateLe(self.endDate), tableEvent['setDate'].dateGe(self.begDate)])])]
        group = ''
        order = ''

        if self.eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(self.eventTypeId))
        if self.specialityId:
            cond.append(tablePerson['speciality_id'].eq(self.specialityId))
        if self.personId:
            cond.append(tablePerson['id'].eq(self.personId))
        if self.eventPurposeId:
            cond.append(tableEventType['purpose_id'].eq(self.eventPurposeId))
        if self.orgStructureId:
            cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(self.orgStructureId)))
        if self.detailPerson:
            group = 'GROUP BY person'
            order = 'ORDER BY person'

        if self.actionTypeCode:
            stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                count(if(Action.person_id = Person.id AND ActionType.code IN ('стх001', 'нстх001'), Action.id, NULL)) AS primaryVisit,
                count(if(Action.person_id = Person.id AND ActionType.code IN ('стх002', 'нстх002'), Action.id, NULL)) AS repeated,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K10.2' , Action.event_id, NULL)) AS osteomyelitisDiagnosis,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K05.2', Action.event_id, NULL)) AS perekoronoritDiagnosis,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9'), Action.event_id, NULL)) AS ptDiagnosis,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K05.3', 'K05.4', 'K05.5', 'K05.6') , Action.event_id, NULL)) AS pzDiagnosis,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K01.0', 'K01.1') , Action.event_id, NULL)) AS MKB,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('стх029', 'стх030', 'стх031', 'стх034', 'нстх029', 'нстх030', 'нстх031'), Action.amount, 0)) AS osteomyelitisTreatment,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB = 'K05.2' AND ActionType.code IN ('стх029', 'стх030', 'стх031', 'стх034', 'нстх029', 'нстх030', 'нстх031'), Action.amount, 0)) AS perekoronoritTreatment,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9') AND ActionType.code IN ('стх029', 'стх030', 'стх031', 'стх034', 'нстх029', 'нстх030', 'нстх031'), Action.amount,0)) AS ptTreatment,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K05.3', 'K05.4', 'K05.5', 'K05.6') AND ActionType.code IN ('стх029', 'стх030', 'стх031', 'стх034', 'нстх029', 'нстх030', 'нстх031'), Action.amount, 0)) AS pzTreatment,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K01.0', 'K01.1') AND ActionType.code IN ('стх034'), Action.amount, 0)) AS Treatment,
                sum(if(Action.person_id = Person.id AND Diagnosis.MKB NOT IN ('K10.2', 'K00.7', 'K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9', 'K05.2', 'K05.3', 'K05.4', 'K05.5', 'K05.6', 'K01.0', 'K01.1') AND ActionType.code IN ('стх029', 'стх030', 'стх031', 'стх034', 'нстх029', 'нстх030', 'нстх031'), Action.amount, 0)) AS otherTreatment,
                count(if(Action.person_id = Person.id AND ActionType.code IN ('стх015', 'стх016', 'нстх015', 'нстх016'),  Action.id, NULL)) AS cutting,
                count(if(Action.person_id = Person.id AND ActionType.code IN ('стх009', 'стх012', 'нстх009', 'нстх012'),  Action.id, NULL)) AS bandaging,
                sum(if(Action.person_id = Person.id AND ActionType.code IN ('сто001', 'сто002', 'сто003', 'нстх001', 'нстх002', 'нстх003'), Action.amount, 0)) AS anesthesia,
                count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K10.3', Action.event_id, NULL)) AS alveolitis,
                count(DISTINCT if(Action.person_id = Person.id AND ActionType.code IN ('стх035'), Action.id, NULL)) AS oas,
                sum(if(Action.person_id = Person.id AND ActionType.code IN ('стх010', 'стх011'),  Action.amount, 0)) AS bleeding,
                ROUND(SUM(IF(Action.person_id = Person.id, Action.uet * Action.amount,0)), 2) AS uet,
                ROUND(SUM(IF(Action.person_id = Person.id AND ActionProperty_String.value LIKE 'О', Action.uet * Action.amount,0)), 2) AS uetOperation,
                ROUND(SUM(IF(Action.person_id = Person.id AND Diagnosis.MKB IN ('K01.0', 'K01.1') AND ActionType.code = 'стх034', Action.uet * Action.Amount,0)), 2) AS uetDiag,
                count(if(Action.person_id = Person.id AND ActionProperty_String.value LIKE 'О', ActionProperty_String.value, NULL)) AS operation
             FROM Event
                INNER JOIN EventType ON EventType.id = Event.eventType_id
                INNER JOIN Client ON Client.id = Event.client_id
                INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                INNER JOIN Person ON Person.id IN (Action.person_id, Event.setPerson_id)
                LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id
                LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
            WHERE %s AND age(Client.birthDate, Event.setDate) >= 18 AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
            %s
            %s''' % (db.joinAnd(cond), group, order)
        else:
            stmt = u'''SELECT CONCAT_WS(' ', Person.lastName, Person.firstName, Person.patrName) AS person,
                            count(if(Action.person_id = Person.id AND ActionType.code = 'з103', Action.id, NULL)) AS primaryVisit,
                            count(if(Action.person_id = Person.id AND ActionType.code = 'з101', Action.id, NULL)) AS repeated,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K10.2' , Action.event_id, NULL)) AS osteomyelitisDiagnosis,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K00.7', Action.event_id, NULL)) AS perekoronoritDiagnosis,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9'), Action.event_id, NULL)) AS ptDiagnosis,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K05.2', 'K05.3', 'K05.4', 'K05.5', 'K05.6') , Action.event_id, NULL)) AS pzDiagnosis,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB IN ('K01.0', 'K01.1') , Action.event_id, NULL)) AS MKB,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB = 'K10.2' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount, 0)) AS osteomyelitisTreatment,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB = 'K00.7' AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount, 0)) AS perekoronoritTreatment,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount,0)) AS ptTreatment,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K05.2', 'K05.3', 'K05.4', 'K05.5', 'K05.6') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount, 0)) AS pzTreatment,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB IN ('K01.0', 'K01.1') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount, 0)) AS Treatment,
                            sum(if(Action.person_id = Person.id AND Diagnosis.MKB NOT IN ('K10.2', 'K00.7', 'K04.4', 'K04.5', 'K04.6', 'K04.7', 'K04.8', 'K04.9', 'K05.2', 'K05.3', 'K05.4', 'K05.5', 'K05.6', 'K01.0', 'K01.1') AND ActionType.code IN ('оЖ001ж', 'оЖ001и', 'оЖ001з', 'оЖ001к'), Action.amount, 0)) AS otherTreatment,
                            count(if(Action.person_id = Person.id AND ActionType.code = 'з311',  Action.id, NULL)) AS cutting,
                            count(if(Action.person_id = Person.id AND ActionType.code = 'з308',  Action.id, NULL)) AS bandaging,
                            sum(if(Action.person_id = Person.id AND ActionType.code IN ('з11101', 'з11102'), Action.amount, 0)) AS anesthesia,
                            count(DISTINCT if(Event.setPerson_id = Person.id AND Diagnosis.MKB = 'K10.3', Action.event_id, NULL)) AS alveolitis,
                            sum(if(Action.person_id = Person.id AND ActionType.code = 'з310',  Action.amount, 0)) AS bleeding,
                            ROUND(SUM(IF(Action.person_id = Person.id, Action.uet * Action.amount,0)), 2) AS uet,
                            ROUND(SUM(IF(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з318', 'з323', 'з324'), Action.uet * Action.amount,0)), 2) AS uetOperation,
                            count(if(Action.person_id = Person.id AND ActionType.code IN ('оЖ018к', 'оЖ018и', 'оЖ018л', 'оЖ018м', 'з318', 'з323', 'з324'), Action.id, NULL)) AS operation
                         FROM Event
                            INNER JOIN EventType ON EventType.id = Event.eventType_id
                            INNER JOIN Client ON Client.id = Event.client_id
                            INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                            INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                            INNER JOIN Person ON Person.id IN (Action.person_id, Event.setPerson_id)
                            LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id AND rbDiagnosisType.code IN ('1', '2')
                        WHERE %s AND age(Client.birthDate, Event.setDate) >= 18 AND rbDiagnosisType.id IS NOT NULL AND Event.deleted = 0
                        %s
                        %s''' % (db.joinAnd(cond), group, order)

        return db.query(stmt)

class CReportSurgical(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет врача хирурга')

    def getSetupDialog(self, parent):
        result = CAccountingWork(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        self.actionTypeCode = params.get('actionTypeCode', None)
        detailPerson = params.get('detailPerson', False)
        reportData = CReportData(params)
        query = reportData.selectData()
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%2',  [u'№'], CReportBase.AlignRight),
                        ('%5',  [u'Врач'], CReportBase.AlignLeft),
                        ('%5',  [u'Всего'], CReportBase.AlignLeft),
                        ('%5',  [u'Порядок. № обращения',   u'I'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'II'], CReportBase.AlignLeft),
                        ('%5',  [u'Диагноз',                u'остеомиелит'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'перекоронорит'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'Пт'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'Пз'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'ретенция'], CReportBase.AlignLeft),
                        ('%5',  [u'Проведено лечение',      u'удалено зубов',   u'остеомиелит'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'',                u'перекоронорит'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'',                u'Пт'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'',                u'Пз'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'',                u'ретенция'], CReportBase.AlignLeft),
                        ('%5',  [u'', u'', u'другие диагнозы'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'',                u'всего'], CReportBase.AlignLeft),
                        ('%5',  [u'Разрез'], CReportBase.AlignLeft),
                        ('%5',  [u'Перевязка'], CReportBase.AlignLeft),
                        ('%5',  [u'Анестезия'], CReportBase.AlignLeft),
                        ('%5',  [u'Осложнения',             u'альвеолит'], CReportBase.AlignLeft),
                        ('%5',  [u'',                       u'кровотечения'], CReportBase.AlignLeft),
                        ('%5',  [u'Операции'                               ], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ на операции'], CReportBase.AlignLeft),
                        ('%5',  [u'УЕТ'], CReportBase.AlignLeft)]
        if self.actionTypeCode:
            tableColumns.insert(21, ('%5',[u'',             u'ОАС'], CReportBase.AlignLeft))
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(0, 5, 1, 5)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(0, 10, 1, 7)
        table.mergeCells(1, 10, 1, 7)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(1, 12, 2, 1)
        table.mergeCells(1, 13, 2, 1)
        table.mergeCells(1, 14, 2, 1)
        table.mergeCells(1, 15, 2, 1)
        table.mergeCells(1, 16, 2, 1)
        table.mergeCells(0, 17, 3, 1)
        table.mergeCells(0, 18, 3, 1)
        table.mergeCells(0, 19, 3, 1)
        table.mergeCells(0, 20, 1, 3)
        table.mergeCells(1, 20, 2, 1)
        if self.actionTypeCode:
            table.mergeCells(1, 21, 2, 1)
            table.mergeCells(1, 22, 2, 1)
            table.mergeCells(1, 23, 2, 1)
            table.mergeCells(0, 24, 3, 1)
            table.mergeCells(0, 25, 3, 1)
        else:
            table.mergeCells(1, 21, 2, 1)
            table.mergeCells(0, 22, 3, 1)
            table.mergeCells(0, 23, 3, 1)
            table.mergeCells(0, 24, 3, 1)
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        total = [0]*len(tableColumns)
        value = [0]*len(tableColumns)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            value[1]  = forceString(record.value('person'))
            value[3]  = forceInt(record.value('primaryVisit'))
            value[4]  = forceInt(record.value('repeated'))
            value[5]  = forceInt(record.value('osteomyelitisDiagnosis'))
            value[6]  = forceInt(record.value('perekoronoritDiagnosis'))
            value[7]  = forceInt(record.value('ptDiagnosis'))
            value[8]  = forceInt(record.value('pzDiagnosis'))
            value[9]  = forceInt(record.value('MKB'))
            value[10] = forceInt(record.value('osteomyelitisTreatment'))
            value[11] = forceInt(record.value('perekoronoritTreatment'))
            value[12] = forceInt(record.value('ptTreatment'))
            value[13] = forceInt(record.value('pzTreatment'))
            value[14] = forceInt(record.value('Treatment'))
            value[15] = forceInt(record.value('otherTreatment'))
            value[16] = value[10] + value[11] + value[12] + value[13] + value[14] + value[15]
            value[17] = forceInt(record.value('cutting'))
            value[18] = forceInt(record.value('bandaging'))
            value[19] = forceInt(record.value('anesthesia'))
            value[20] = forceInt(record.value('alveolitis'))
            if self.actionTypeCode:
                value[21] = forceInt(record.value('oas'))
                value[22] = forceInt(record.value('bleeding'))
                value[23] = forceInt(record.value('operation')) + value[14]
                value[24] = forceInt(record.value('uetOperation')) + forceInt(record.value('uetDiag'))
                value[25] = forceDouble(record.value('uet'))
            else:
                value[21] = forceInt(record.value('bleeding'))
                value[22] = forceInt(record.value('operation'))
                value[23] = forceDouble(record.value('uetOperation'))
                value[24] = forceDouble(record.value('uet'))

            value[2] = value[4] + value[3]
            if detailPerson:
                i = table.addRow()
                value[0] = i-2
                self.fillTable(table, i, value)
            total[0] = ''
            for index in xrange(len(tableColumns)-2):
                total[index+2] += value[index+2]
        i = table.addRow()
        total[1] = u'Всего'
        self.fillTable(table, i, total)
        return doc

    def fillTable(self, table, i, array):
        if self.actionTypeCode:
            for index in xrange(25):
                if array[1] == u'Всего':
                    table.setText(i, index, array[index], CReportBase.TableTotal)
                else:
                    table.setText(i, index, array[index])
            if array[1] == u'Всего':
                table.setText(i, 25, '%.2f' % array[25], CReportBase.TableTotal)
            else:
                table.setText(i, 25, '%.2f' % array[25])
        else:
            for index in xrange(24):
                if array[1] == u'Всего':
                    table.setText(i, index, array[index], CReportBase.TableTotal)
                else:
                    table.setText(i, index, array[index])
            if array[1] == u'Всего':
                table.setText(i, 24, '%.2f' % array[24], CReportBase.TableTotal)
            else:
                table.setText(i, 24, '%.2f' % array[24])


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo
    from PyQt4 import QtCore

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

    w = CReportSurgical(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()