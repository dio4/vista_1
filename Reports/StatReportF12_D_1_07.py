# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.Utils              import forceBool, forceInt, forceString

from Reports                    import OKVEDList
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportSetupDialog  import CReportSetupDialog
from Reports.StatReport1NPUtil  import havePermanentAttach



def countDispensariable(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Organisation.OKVED as OKVED,
            COUNT(Event.id) as cnt
        FROM
            Event
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientWork    ON (    ClientWork.client_id = Client.id
                                        AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                       )
            LEFT JOIN Organisation  ON Organisation.id = ClientWork.org_id
            LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                      )
        WHERE
                IF( execDate IS NULL,
                    STR_TO_DATE(CONCAT(YEAR(setDate), '-12-31'), '%%Y-%%m-%%d'),
                    DATE(execDate)
                  ) >= %s
            AND setDate <= %s
            %s
        GROUP BY
            Organisation.OKVED
    """
    db = QtGui.qApp.db
    cond = []
    if cond:
        tableEvent = db.table('Event')
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    cond = db.joinAnd(cond)
    if cond:
        cond = ' AND '+ cond
#    print stmt % ( db.formatDate(begDate), db.formatDate(endDate), cond)
    return db.query(stmt % ( db.formatDate(begDate), db.formatDate(endDate), cond))


def countByGroups(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Organisation.OKVED as OKVED,
            rbHealthGroup.code as `group`,
            IF ( rbDiseaseCharacter.code='2'
                 OR (rbDiseaseCharacter.code='1' AND rbDiseaseStage.code='1'),
                 1,
                 0 ) AS DOD,
            Event.isPrimary as isPrimary,
            COUNT(Event.id) as cnt
        FROM
            Event
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientWork    ON (    ClientWork.client_id = Client.id
                                        AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                       )
            LEFT JOIN Organisation  ON Organisation.id = ClientWork.org_id
            LEFT JOIN Diagnostic    ON (     Diagnostic.event_id = Event.id
                                         AND Diagnostic.diagnosisType_id = (SELECT id FROM rbDiagnosisType WHERE code = '1')
                                       )
            LEFT JOIN rbHealthGroup ON rbHealthGroup.id = Diagnostic.healthGroup_id
            LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
            LEFT JOIN rbDiseaseStage     ON rbDiseaseStage.id     = Diagnostic.stage_id
            LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                      )
        WHERE
            %s
        GROUP BY
            OKVED, `group`, DOD, Event.isPrimary
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


def countBySanatoriumAndHospital(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate):
    stmt="""
        SELECT
            Organisation.OKVED as OKVED,
               IF(
                   EXISTS (
                           SELECT
                               DS.id
                           FROM
                               Diagnostic AS DS
                           WHERE
                                   DS.event_id = Event.id
                               AND DS.sanatorium>0
                               AND DS.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1','2'))
                          ), 1, 0
                 ) as sanatorium,
               IF(
                   EXISTS (
                           SELECT
                               DH.id
                           FROM
                               Diagnostic AS DH
                           WHERE
                                   DH.event_id = Event.id
                               AND DH.hospital>1
                               AND DH.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1','2'))
                          ), 1, 0
                 ) as hospital,
               IF(
                   EXISTS (
                           SELECT
                               DHTA.id
                           FROM
                               Diagnostic AS DHTA
                               LEFT JOIN rbHealthGroup ON rbHealthGroup.id = DHTA.healthGroup_id
                           WHERE
                                   DHTA.event_id = Event.id
                               AND DHTA.hospital>1
                               AND DHTA.diagnosisType_id IN (SELECT id FROM rbDiagnosisType WHERE code IN ('1','2'))
                               AND rbHealthGroup.code = '5'
                         ), 1, 0
                 ) as highTechAid,
            COUNT(Event.id) as cnt
        FROM
            Event
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientWork   ON (    ClientWork.client_id = Client.id
                                       AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id)
                                      )
            LEFT JOIN Organisation ON Organisation.id = ClientWork.org_id
            LEFT JOIN Account_Item ON ( Account_Item.id = (SELECT max(AI.id) FROM Account_Item AS AI WHERE AI.event_id = Event.id AND AI.deleted=0 AND AI.date IS NOT NULL AND AI.refuseType_id IS NULL AND AI.reexposeItem_id IS NULL AND AI.visit_id IS NULL AND AI.action_id IS NULL)
                                      )
        WHERE
            %s
        GROUP BY
            OKVED, sanatorium, hospital, highTechAid
    """
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    cond = []
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if onlyPermanentAttach:
        cond.append(havePermanentAttach(endDate))
    if onlyPayedEvents:
        cond.append('isEventPayed(Event.id)')
        tableAccountItem = db.table('Account_Item')
        addDateInRange(cond, tableAccountItem['date'], begPayDate, endPayDate)
    return db.query(stmt % (db.joinAnd(cond)))


class CStatReportF12_D_1_07(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сведения о дополнительной диспансеризации работающих граждан, Ф.№ 12-Д-1-07',
                      u'Сведения о дополнительной диспансеризации работающих граждан')


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setTitle(self.title())
        result.setEventTypeVisible(True)
        result.setPayPeriodVisible(True)
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeId = params.get('eventTypeId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', False)
        begPayDate = params.get('begPayDate', QtCore.QDate())
        endPayDate = params.get('endPayDate', QtCore.QDate())

        reportRowSize = 12
        reportData = [ [0] * reportRowSize for row in OKVEDList.rows ]
        query = countDispensariable(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okved  = forceString(record.value('OKVED'))
            cnt    = forceInt(record.value('cnt'))
            for i in OKVEDList.dispatch(okved):
                reportData[i][0] += cnt

        query = countByGroups(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okved  = forceString(record.value('OKVED'))
            cnt    = forceInt(record.value('cnt'))
            group  = forceString(record.value('group'))
            DOD    = forceBool(record.value('DOD'))
            isPrimary = forceInt(record.value('isPrimary')) == 1
            columns = []
            if group == '2':
                columns = [1, 4]
            elif group == '3':
                if DOD:
                    columns = [1, 5, 6]
                else:
                    columns = [1, 5]
            elif group == '4':
                columns = [1, 7]
            elif group == '5' or group == '6':
                columns = [1, 8]
            else:
                columns = [1, 3]
            if isPrimary:
                columns.append(2)
            for i in OKVEDList.dispatch(okved):
                reportLine = reportData[i]
                for j in columns:
                    reportLine[j] += cnt

        query = countBySanatoriumAndHospital(begDate, endDate, eventTypeId, onlyPermanentAttach, onlyPayedEvents, begPayDate, endPayDate)
        while query.next() :
            record = query.record()
            okved       = forceString(record.value('OKVED'))
            sanatorium  = forceBool(record.value('sanatorium'))
            hospital    = forceBool(record.value('hospital'))
            highTechAid = forceBool(record.value('highTechAid'))
            cnt         = forceInt(record.value('cnt'))
            columns = []
            if sanatorium:
                columns.append(9)
            if hospital:
                columns.append(10)
            if highTechAid:
                columns.append(11)

            for i in OKVEDList.dispatch(okved):
                reportLine = reportData[i]
                for j in columns:
                    reportLine[j] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)


        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
#        cursor.setCharFormat(CReportBase.ReportBody)

        self.dumpParams(cursor, params)
        tableColumns = [
            ('18%', [u'Наименование вида экономической деятельности гражданина, прошедшего диспансеризацию',
                     u'',
                     u'',
                     u'1'],            CReportBase.AlignLeft),
            ('5%', [u'№ строки',
                     u'',
                     u'',
                     u'2'],            CReportBase.AlignCenter),
            ('10%', [u'Код вида экономической деятельности по ОКВЭД',
                     u'',
                     u'',
                     u'3'],            CReportBase.AlignCenter),
            ('5%', [u'Число лиц',
                     u'под-\nле-\nжа-\nщих ДД',
                     u'',
                     u'4'],              CReportBase.AlignRight),
            ('5%', [u'',
                     u'про-\nшед-\nших ДД',
                     u'все-\nго',
                     u'5.1'],              CReportBase.AlignRight),
            ('5%', [u'',
                     u'',
                     u'впе-\nрвые',
                     u'5.2'],              CReportBase.AlignRight),
            ('5%', [u'Распределение прошедших дополнительную диспансеризацию (ДД) граждан по группам состояния здоровья',
                     u'I гр.',
                     u'',
                     u'6'],              CReportBase.AlignRight),
            ('5%', [u'',
                     u'II гр.',
                     u'',
                     u'7'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'III гр.',
                     u'все-\nго',
                     u'8'
                     ],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'',
                     u'в т.ч. выя-\nвле-\nнные при ДД',
                     u'9'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'IV гр.',
                     u'',
                     u'10'],              CReportBase.AlignRight),
            ('5%',  [u'',
                     u'V гр.',
                     u'',
                     u'11'],              CReportBase.AlignRight),
            ('5%',  [u'из числа прошедших ДД (графа 5) нуждалось в санаторно- курортном лечении',
                     u'',
                     u'',
                     u'12'],              CReportBase.AlignRight),
            ('5%',  [u'Направлено граждан',
                     u'на гос-\nпита-\nлизацию в ста-\nцио-\nнар',
                     u'',
                     u'13'],              CReportBase.AlignRight),
            ('5%' , [u'',
                     u'в ОУЗ суб. РФ на ВМП',
                     u'',
                     u'14'],              CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 3)

        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)

        table.mergeCells(0, 6, 1, 6)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 1, 2)
        table.mergeCells(1,10, 2, 1)
        table.mergeCells(1,11, 2, 1)
        table.mergeCells(0,12, 3, 1)
        table.mergeCells(0,13, 1, 2)
        table.mergeCells(1,13, 2, 1)
        table.mergeCells(1,14, 2, 1)

        for iRow, row in enumerate(OKVEDList.rows):
            i = table.addRow()
            for j in xrange(3):
                table.setText(i, j, row[j])
            for j in xrange(11):
                table.setText(i, 3+j, reportData[iRow][j])
        return doc

