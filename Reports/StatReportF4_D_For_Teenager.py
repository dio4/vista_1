# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceInt, forceRef, forceString
from Orgs.Utils                 import getOrgStructureFullName

from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach


def selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, orgStructureAttachTypeId):
    stmt="""
        SELECT
            Event.id AS eventId,
            Event.client_id,
            IF(rbDiagnosisType.code = '1', 1, 0) AS isDiagnosisType,
            rbHealthGroup.code AS isHealthGroup,
            IF(Event.execDate IS NOT NULL, 1, 0) AS eventClosedPayed,
            IF(Diagnostic.sanatorium > 0, 1, 0) AS isSanatorium,
            IF(rbDiseaseCharacter.code='1' OR rbDiseaseCharacter.code='2', 1, 0) AS isPrimary,
            IF(Diagnostic.hospital>1, 1, 0) AS isHospital,
            IF((Account_Item.date >= DATE(Event.setDate)) AND (Account_Item.date < DATE(Event.execDate)), 1, 0) AS payedEvent
        FROM
            Diagnostic
            INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            INNER JOIN Event     ON Event.id = Diagnostic.event_id
            INNER JOIN rbDiagnosisType    ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbHealthGroup      ON rbHealthGroup.id      = Diagnostic.healthGroup_id
            INNER JOIN Client             ON Client.id             = Event.client_id
            LEFT JOIN Account_Item       ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                            )
            %s
        WHERE
            %s
        ORDER BY
            rbDiagnosisType.code, rbHealthGroup.code, Diagnostic.sanatorium, Diagnostic.hospital DESC
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(begDate)]))
    cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].le(endDate)]))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    addisionalFrom = ''
    if orgStructureAttachTypeId:
        tableClientAttach = db.table('ClientAttach')
        attachTypeId = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
        addisionalFrom = '''LEFT JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                FROM ClientAttach clAttach
                                                                                                                WHERE clAttach.attachType_id = %s
                                                                                                                AND clAttach.client_id = Client.id)
                            LEFT JOIN OrgStructure ON OrgStructure.id = ClientAttach.orgStructure_id''' % (attachTypeId)
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    return db.query(stmt % (addisionalFrom, db.joinAnd(cond)))


class CStatReportF4_D_For_Teenager(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёты по ДД подростков',
                      u'Сведения о диспансеризации подростков (квартальная)')


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        result.setOrgStructureAttachTypeVisible(True)
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)

        reportRowSize = 6
        reportData = [0]*reportRowSize
        reportRowSize2 = 6
        reportData2 = [0]*reportRowSize2
        reportRowSize3 = 5
        reportData3 = [0]*reportRowSize3

        query = selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, orgStructureAttachTypeId)
        self.setQueryText(forceString(query.lastQuery()))
        eventClosed = 0
        eventClosedPayed = 0
        eventIdList = []
        clientIdList = []
        specialityIdCount = {}
        actionTypeIdCount = {}
        while query.next() :
            record = query.record()
            isSanatorium  = forceInt(record.value('isSanatorium'))
            isHospital    = forceInt(record.value('isHospital'))
            eventId = forceRef(record.value('eventId'))
            clientId = forceRef(record.value('client_id'))
            isPrimary = forceInt(record.value('isPrimary'))
            isDiagnosisType = forceInt(record.value('isDiagnosisType'))
            isHealthGroup = forceString(record.value('isHealthGroup'))
            payedEvent = forceInt(record.value('payedEvent'))
            eventClosedPayedRec = forceInt(record.value('eventClosedPayed'))
            if eventId and eventId not in eventIdList:
                eventIdList.append(eventId)
                if isHealthGroup:
                    if isHealthGroup == '3':
                        reportData[0] += 1
                        if eventClosedPayedRec:
                            reportData[1] += 1
                        #reportData[2] += 1
                        #reportData[3] += 1
                        #reportData[4] += 1
                        #reportData[5] += 1
                    if isHealthGroup == '3' or isHealthGroup == '4' or isHealthGroup == '5':
                        reportData2[0] += 1
                    if isHealthGroup == '3':
                        reportData2[1] += 1
                        if isHospital:
                            reportData2[2] += 1
                    if isHealthGroup == '4':
                        reportData2[3] += 1
                    if isHealthGroup == '5':
                        reportData2[4] += 1
                    if isSanatorium and isHealthGroup:
                        reportData2[5] += 1
                if isDiagnosisType:
                    reportData3[0] += 1
                    if isPrimary:
                        reportData3[1] += 1
                if isHealthGroup and clientId and clientId not in clientIdList:
                    clientIdList.append(clientId)
                    if isHealthGroup == '1':
                        reportData3[2] += 1
                    if isHealthGroup == '2':
                        reportData3[3] += 1
                    if isHealthGroup == '3' or isHealthGroup == '4' or isHealthGroup == '5':
                        reportData3[4] += 1
                eventClosed += 1
                if eventClosedPayedRec:
                    eventClosedPayed += 1

        if eventIdList:
            db = QtGui.qApp.db
            tableETA = db.table('EventType_Action')
            tableETD = db.table('EventType_Diagnostic')
            tableActionType = db.table('ActionType')
            tableRBSpeciality = db.table('rbSpeciality')
            tableAction = db.table('Action')
            tableVisit = db.table('Visit')
            tablePerson = db.table('Person')

            recordsETA = db.getRecordList(tableETA.innerJoin(tableActionType, tableActionType['id'].eq(tableETA['actionType_id'])), [tableActionType['id'], tableActionType['name']], [tableETA['eventType_id'].eq(eventTypeId), tableActionType['deleted'].eq(0)])
            actionTypeIdList = []
            specialityIdList = []
            actionIdList = []
            visitIdList = []
            for record in recordsETA:
                name = forceString(record.value('name'))
                actionTypeId = forceRef(record.value('id'))
                if actionTypeId and actionTypeId not in actionTypeIdCount.keys():
                    actionTypeIdCount[actionTypeId] = (name, 0)
                if actionTypeId and actionTypeId not in actionTypeIdList:
                    actionTypeIdList.append(actionTypeId)
            if actionTypeIdList and actionTypeIdCount:
                recordActions = db.getRecordListGroupBy(tableAction, [tableAction['id'], tableAction['actionType_id']], [tableAction['actionType_id'].inlist(actionTypeIdList), tableAction['event_id'].inlist(eventIdList), tableAction['deleted'].eq(0)], 'Action.id')
                for record in recordActions:
                    actionId = forceRef(record.value('id'))
                    if actionId and actionId not in actionIdList:
                        actionIdList.append(actionId)
                        actionTypeId = forceRef(record.value('actionType_id'))
                        result = actionTypeIdCount.get(actionTypeId, ())
                        if result:
                            nameAction = result[0]
                            actionTypeCount = result[1]
                            actionTypeCount += 1
                            actionTypeIdCount[actionTypeId] = (nameAction, actionTypeCount)
            recordsETD = db.getRecordList(tableETD.innerJoin(tableRBSpeciality, tableRBSpeciality['id'].eq(tableETD['speciality_id'])), [tableETD['speciality_id'], tableRBSpeciality['name']], [tableETD['eventType_id'].eq(eventTypeId)])
            for record in recordsETD:
                name = forceString(record.value('name'))
                specialityId = forceRef(record.value('speciality_id'))
                if specialityId and specialityId not in specialityIdCount.keys():
                    specialityIdCount[specialityId] = (name, 0)
                if specialityId and specialityId not in specialityIdList:
                    specialityIdList.append(specialityId)
            if specialityIdList and specialityIdCount:
                recordVisits = db.getRecordListGroupBy(tableVisit.innerJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id'])), [tableVisit['id'], tablePerson['speciality_id']], [tablePerson['speciality_id'].inlist(specialityIdList), tableVisit['event_id'].inlist(eventIdList), tableVisit['deleted'].eq(0), tablePerson['deleted'].eq(0)], 'Visit.id')
                for record in recordVisits:
                    visitId = forceRef(record.value('id'))
                    if visitId and visitId not in visitIdList:
                        visitIdList.append(visitId)
                        specialityId = forceRef(record.value('speciality_id'))
                        result = specialityIdCount.get(specialityId, ())
                        if result:
                            visitAction = result[0]
                            visitIdCount = result[1]
                            visitIdCount += 1
                            specialityIdCount[specialityId] = (visitAction, visitIdCount)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''1. Число детей подлежащих диспансеризации: %s (человек),'''%(str(eventClosed)))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''2. Число детей прошедших диспансеризацию: %s (человек)'''%(str(eventClosedPayed)))
        cursor.insertBlock()
        if specialityIdCount:
            cursor.insertText(u'''Осмотры:''')
            cursor.insertBlock()
            for value in specialityIdCount.values():
                if value:
                    cursor.insertText(value[0] + ' - ' + forceString(value[1]))
                    cursor.insertBlock()
        if actionTypeIdCount:
            cursor.insertText(u'''Мероприятия:''')
            cursor.insertBlock()
            for value in actionTypeIdCount.values():
                if value:
                    cursor.insertText('        - ' + value[0] + ' - ' + forceString(value[1]))
                    cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''3. Из числа прошедших диспансеризацию детей:''')
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''3.1. Дополнительное обследование детей по результатам диспансеризации (человек)''')
        cursor.insertBlock()

        tableColumns = [
            ('18%', [u'Нуждались(человек)', u'', u'1'], CReportBase.AlignLeft),
            ('16.5%', [u'Прошли (человек)', u'', u'2'], CReportBase.AlignCenter),
            ('16.5%', [u'на уровне субъекта Российской Федерации', u'Нуждались(человек)', u'3'], CReportBase.AlignRight),
            ('16.5%', [u'', u'Прошли (человек)', u'4'], CReportBase.AlignRight),
            ('16.5%', [u'на федеральном уровне', u'Нуждались(человек)', u'5'], CReportBase.AlignRight),
            ('16.5%', [u'', u'Прошли (человек)', u'6'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)

        i = table.addRow()
        for j in xrange(reportRowSize):
            table.setText(i, j, reportData[j])

        cursor.insertBlock()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'3.2. Рекомендовано лечение по результатам диспансеризации (человек)')
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'Всего (человек)' ], CReportBase.AlignLeft),
            ('18%', [u'в амбулаторно-поликлинической сети'], CReportBase.AlignLeft),
            ('18%', [u'в стационаре муниципального уровня'], CReportBase.AlignLeft),
            ('18%', [u'в стационаре субъекта Российской Федерации'], CReportBase.AlignRight),
            ('18%', [u'в стационаре федерального  уровня'], CReportBase.AlignRight),
            ('18%', [u'в санатории'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        i = table.addRow()
        for j in xrange(reportRowSize2):
            table.setText(i, j, reportData2[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'4. Результаты:')
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'Всего выявлено заболеваний', u''], CReportBase.AlignLeft),
            ('20%', [u'Из них выявлено впервые', u''], CReportBase.AlignLeft),
            ('20%', [u'Имеют группу здоровья', u'I'], CReportBase.AlignLeft),
            ('20%', [u'', u'II'], CReportBase.AlignRight),
            ('20%', [u'', u'III'], CReportBase.AlignRight)
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        i = table.addRow()
        for j in xrange(reportRowSize3):
            table.setText(i, j, reportData3[j])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        return doc
