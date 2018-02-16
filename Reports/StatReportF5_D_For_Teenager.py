# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.MapCode            import createMapCodeToRowIdx
from library.Utils              import forceInt, forceRef, forceString
from Orgs.Utils                 import getOrgStructureFullName

from Reports.Report             import CReport, normalizeMKB
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach


Rows = [
          ( u'Некоторые инфекционные и паразитарные заболевания, из них:', u'1.0', u'A00-B99'),
          ( u'туберкулез,', u'1.1', u'A15-A19'),
          ( u'ВИЧ, СПИД,', u'1.2', u'B20 - B24'),
          ( u'Новообразования', u'2.0', u'C00-D48'),
          ( u'Болезни крови и кроветворных органов и отдельные нарушения, вовлекающие иммунные механизмы, из них:', u'3.0', u'D50-D89'),
          ( u'анемии', u'3.1', u'D50-D53'),
          ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ, из них:', u'4.0', u'E00 - E90'),
          ( u'сахарный диабет', u'4.1', u'E10 - E14'),
          ( u'недостаточность питания', u'4.2', u'E40-E46'),
          ( u'ожирение', u'4.3', u'E66'),
          ( u'задержка полового развития', u'4.4', u'E30.0'),
          ( u'преждевременное половое развитие', u'4.3', u'E30.1'),
          ( u'Психические расстройства и расстройства поведения, из них:', u'5.0', u'F00 - F99'),
          ( u'умственная отсталость', u'5.1', u'F70 - F79'),
          ( u'Болезни нервной системы, из них:', u'6.0', u'G00 - G98'),
          ( u'церебральный паралич и другие паралитические синдромы ', u'6.1', u'G80 - G83'),
          ( u'Болезни глаза и его придаточного аппарата', u'7.0', u'H00 - H59'),
          ( u'Болезни уха и сосцевидного отростка', u'8.0', u'H60 - H95'),
          ( u'Болезни системы кровообращения', u'9.0', u'I00 - I99'),
          ( u'Болезни органов дыхания, из них:', u'10.0', u'J00 - J99'),
          ( u'астма, астматический статус', u'10.1', u'J45 - J46'),
          ( u'Болезни органов пищеварения', u'11.0', u'K00 - K93'),
          ( u'Болезни кожи и подкожной клетчатки', u'12.0', u'L00 - L99'),
          ( u'Болезни костно-мышечной системы и соединительной ткани, из них:', u'13.0', u'M00 - M99'),
          ( u'кифоз, лордоз, сколиоз', u'13.1', u'M40-M41'),
          ( u'Болезни мочеполовой системы, из них:', u'14.0', u'N00 - N99'),
          ( u'болезни мужских половых органов', u'14.1', u'N40 - N51'),
          ( u'нарушения ритма и характера менструаций:', u'14.2', u'N91-N94.5'),
          ( u'воспалительные заболевания женских тазовых органов', u'14.3', u'N70-N77'),
          ( u'невоспалительные болезни женских половых органов', u'14.4', u'N83-N83.9'),
          ( u'болезни молочной железы', u'14.5', u'N60-N64'),
          ( u'Отдельные состояния, возникающие в перинатальном периоде', u'15.0', u'P00 - P96'),
          ( u'Врожденные аномалии, из них:', u'16.0', u'Q00 - Q99'),
          ( u'развития нервной системы,', u'16.1', u'Q00 - Q07'),
          ( u'системы кровообращения,', u'16.2', u'Q20 - Q28'),
          ( u'костно-мышечной системы', u'16.3', u'Q65 - Q79'),
          ( u'врожденные аномалии (пороки) женских половых органов', u'16.4', u'Q50 - Q52'),
          ( u'врожденные аномалии (пороки) мужских половых органов', u'16.5', u'Q53 - Q55'),
          ( u'Травмы, отравления и некоторые другие последствия воздействия внешних причин', u'17.0', u'S00 - T98'),
          ( u'Прочие', u'18.0', u'O00-O99,Q00-Q99'),
          ( u'Всего', u'19.0', u'A00-T98')
       ]


def selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, diagnosisType, orgStructureAttachTypeId):
    stmt="""
        SELECT
            Event.id AS eventId,
            Event.client_id,
            Diagnosis.MKB,
            Client.sex,
            IF(age(Client.birthDate, Event.execDate) = 14, 1, 0) AS ageTeenager,
            IF(rbDiseaseCharacter.code IN ('1', '2'), 1, 0) AS isPrimary,
            IF(Event.execDate IS NOT NULL, 1, 0) AS eventClosedPayed,
            IF((Account_Item.date >= DATE(Event.setDate)) AND (Account_Item.date < DATE(Event.execDate)), 1, 0) AS payedEvent
        FROM
            Diagnostic
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN Event     ON Event.id = Diagnostic.event_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            LEFT JOIN Client    ON Client.id = Event.client_id
            LEFT JOIN Account_Item ON (Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL))
            %s
        WHERE
            %s
        ORDER BY
            Event.client_id, Diagnosis.mkb, Diagnostic.diagnosisType_id, Diagnostic.id
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableRBDiagnosisType = db.table('rbDiagnosisType')
    cond = []
    cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(begDate)]))
    cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].le(endDate)]))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if not diagnosisType:
        cond.append('''rbDiagnosisType.code = '1' OR rbDiagnosisType.code = '2' ''')
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


class CStatReportF5_D_For_Teenager(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёты по ДД подростков',
                      u'Сведения о диспансеризации детей (годовая)')


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        result.setDiagnosisType(True)
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
        diagnosisType = params.get('diagnosisType', False)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)

        db = QtGui.qApp.db
        mapRows = createMapCodeToRowIdx( [row[2] for row in Rows] )
        reportRowSize = 4
        reportData = [ [0] * reportRowSize for row in Rows ]
        query = selectDiagnostics(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate, diagnosisType, orgStructureAttachTypeId)
        self.setQueryText(forceString(query.lastQuery()))
        eventClosed = 0
        eventClosedTeenager = 0
        eventClosedPayed = 0
        eventClosedPayedTeenager = 0
        eventIdList = []
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            clientId = forceRef(record.value('client_id'))
            isPrimary = forceInt(record.value('isPrimary'))
            MKBRec = normalizeMKB(forceString(record.value('MKB')))
            ageTeenager = forceInt(record.value('ageTeenager'))
            sex = forceInt(record.value('sex'))
            payedEvent = forceInt(record.value('payedEvent'))
            eventClosedPayedRec = forceInt(record.value('eventClosedPayed'))
            for row in mapRows.get(MKBRec, []):
                reportLine = reportData[row]
                reportLine[0] += 1
                if sex == 1:
                    reportLine[1] += 1
                    if isPrimary:
                        reportLine[3] += 1
                reportLine[2] += isPrimary
            if eventId and eventId not in eventIdList:
                eventIdList.append(eventId)
                eventClosed += 1
                eventClosedTeenager += ageTeenager
                if eventClosedPayedRec:
                    eventClosedPayed += 1
                    eventClosedPayedTeenager += ageTeenager

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''1. Число детей подлежащих диспансеризации: %s (человек), из них:
                                                        14-ти летних: %s (человек),'''%(str(eventClosed), str(eventClosedTeenager)))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''2. Число детей прошедших диспансеризацию: %s (человек), из них:
                                                       14-ти летних: %s (человек)'''%(str(eventClosedPayed), str(eventClosedPayedTeenager)))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'''3. Структура выявленной патологии у подростков:''')
        cursor.insertBlock()
        tableColumns = [
            ('18%', [u'Наименование заболевания (по классам и отдельным нозологиям)', u'1'], CReportBase.AlignLeft),
            ('2%',  [u'№ строки', u'2'], CReportBase.AlignCenter),
            ('16%', [u'Код по МКБ-10', u'3'], CReportBase.AlignCenter),
            ('16%', [u'Всего зарегистрировано заболеваний', u'4'], CReportBase.AlignRight),
            ('16%', [u'в том числе у юношей (из графы 4)', u'5'], CReportBase.AlignRight),
            ('16%', [u'Из числа зарегистрированных заболеваний выявлено впервые (из графы 4)', u'6'], CReportBase.AlignRight),
            ('16%', [u'в том числе у юношей (из графы 6)', u'7'], CReportBase.AlignRight)
            ]
        table = createTable(cursor, tableColumns)
        for iRow, row in enumerate(Rows):
            i = table.addRow()
            for j in xrange(3):
                table.setText(i, j, row[j])
            for j in xrange(reportRowSize):
                table.setText(i, 3+j, reportData[iRow][j])
        return doc

