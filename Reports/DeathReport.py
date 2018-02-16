# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.MapCode    import createMapCodeToRowIdx
from library.Utils      import forceInt, forceString, getVal
from Orgs.Utils         import getOrgStructureDescendants

from Reports.DeathList  import addCondForDeathCurcumstance, CDeathReportSetupDialog
from Reports.Report     import CReport, normalizeMKB
from Reports.ReportBase import createTable, CReportBase


MainRows = [
    (u'Инфекционные болезни',u'A00-B99'),
    (u'  в т.ч.: туберкулез',u'A15-A19'),
    (u'Онкология',u'C00-C97'),
    (u'  в т.ч: рак губы,языка и др.отделов рта',u'C00-C03'),
    (u'         рак дна полости рта,неба и др.отд.',u'C04-C06'),
    (u'         рак глотки',u'C10-C14'),
    (u'         рак пищевода',u'C15'),
    (u'         рак желудка',u'C16'),
    (u'         рак тонкого кишечника',u'C17'),
    (u'         рак толстого кишечника',u'C18-C19'),
    (u'         рак прямой кишки и заднего прохода',u'C20-C21'),
    (u'         рак легкого',u'C34'),
    (u'         рак молочной железы',u'C50'),
    (u'         рак женских половых органов',u'C51-C58'),
    (u'Новообразования',u'D00-D48'),
    (u'Болезни крови и кроветв.орг.',u'D50-D89'),
    (u'Болезни эндокр. системы',u'E00-E90'),
    (u'Психические расстройства',u'F00-F99'),
    (u'Болезни нервной системы',u'G00-G99'),
    (u'  в т.ч.:дегенер.нервной системы,вызв.алког',u'G31.2'),
    (u'Болезни глаза и придаточного аппарата',u'H00-H59'),
    (u'Болезни уха и сосцевидного отростка',u'H60-H95'),
    (u'Болезни системы кровообращения',u'I00-I99'),
    (u'  в т.ч.: с гипертензией',u'I10-I13'),
    (u'          острый инфаркт миакарда',u'I21-I22'),
    (u'          острая коронар.недостат.или  недостат.кровообращ. IIIст.',u'I24.0'),
    (u'          хроническая ишемическая болезнь сердца',u'I25'),
    (u'          алкогольная кардиомиопатия',u'I42.6'),
    (u'          всего ОНМК',u'I60-I64'),
    (u'          в т.ч.: инфаркт мозга',u'I63'),
    (u'                  кровоизлияние в мозг',u'I61'),
    (u'                  ОНМК неуточненные как инфаркт или кровоизлияние',u'I64'),
    (u'          хрон.цереброваскулярная недостаточность',u'I67'),
    (u'Болезни органов дыхания',u'J00-J99'),
    (u'  в т.ч.: острая пневмония',u'J12-J18'),
    (u'          хрон.обструктивная болезнь легких',u'J44'),
    (u'          бронхиальная астма',u'J45-J46'),
    (u'Болезни органов пищеварения',u'K00-K93'),
    (u'  в т.ч.: фиброз и цирроз печени',u'K74'),
    (u'Болезни кожи и подкожной клетчатки',u'L00-L99'),
    (u'Болезни костно-мышечной системы',u'M00-M99'),
    (u'Болезни мочеполовой системы',u'N00-N99'),
    (u'  в т.ч.: хрон.пиелонефрит',u'N11'),
    (u'Беременность,роды и послерод.период',u'O00-O99'),
    (u'Врожденные аномалии',u'Q00-Q99'),
    (u'Симптомы,признаки отклонения от нормы',u'R00-R99'),
    (u'Травмы и отравления',u'S00-T98'),
    (u'Все заболевания', u'A00-T98'),
    (u'Прочие',u''),
    (u'Диагноз не ясен',u''),
    (u'Всего', u''),
    ]


def selectData(params):
    begDate = getVal(params, 'begDate', QtCore.QDate())
    endDate = getVal(params, 'endDate', QtCore.QDate())
    place = params.get('deathPlace', '')
    cause = params.get('deathCause', '')
    foundBy = params.get('deathFoundBy', '')
    foundation = params.get('deathFoundation', '')
    attachmentOrgStructureId = params.get('attachmentOrgStructureId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    
    stmt="""
SELECT
  count(*) AS cnt,
  age(Client.birthDate, Event.setDate) AS clientAge,
  Client.sex AS clientSex,
  IF(FDiagnosis.MKB IS NULL, PDiagnosis.MKB, FDiagnosis.MKB) AS MKB
FROM
  Event
  LEFT JOIN EventType ON EventType.id = Event.eventType_id
  LEFT JOIN Client ON Client.id = Event.client_id
  LEFT JOIN Diagnostic AS PDiagnostic ON PDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS PDiagnosisType ON PDiagnosisType.id = PDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS PDiagnosis ON PDiagnosis.id = PDiagnostic.diagnosis_id
  LEFT JOIN Diagnostic AS FDiagnostic ON FDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS FDiagnosisType ON FDiagnosisType.id = FDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS FDiagnosis ON FDiagnosis.id = FDiagnostic.diagnosis_id
  LEFT JOIN Person ON Person.id = Event.execPerson_id
WHERE
  EventType.code = '15'
  AND PDiagnosisType.code = '8'
  AND FDiagnosisType.code = '4'
  AND %s
GROUP BY clientAge, clientSex, MKB
    """
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if place or cause or foundBy or foundation:
        addCondForDeathCurcumstance(cond, tableEvent, place, cause, foundBy, foundation)
    if attachmentOrgStructureId:
        tableClientAttach = db.table('ClientAttach')
        tableClient = db.table('Client')
        cond.append(db.existsStmt(tableClientAttach, [tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(attachmentOrgStructureId)),
                                                      tableClientAttach['client_id'].eq(tableClient['id']),
                                                      tableClientAttach['begDate'].le(tableEvent['setDate']),
                                                      db.joinOr([tableClientAttach['endDate'].isNull(),
                                                                 tableClientAttach['endDate'].ge(tableEvent['setDate'])])
                                                      ]))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    return db.query(stmt % (db.joinAnd(cond)))


class CDeathReport(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Отчёт по летальности')


    def getSetupDialog(self, parent):
        result = CDeathReportSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        # rowSize = 8
        rowSize = 9
        reportMainData = [ [0]*rowSize for row in xrange(len(MainRows)*2) ]
        mapMainRows = createMapCodeToRowIdx( [row[1] for row in MainRows if row[1]] )
        totalRowIndex      = len(MainRows)-1
        unknownDiagRowIndex= totalRowIndex-1
        otherDiagRowIndex  = unknownDiagRowIndex

#        QtGui.qApp.beep()

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record   = query.record()
            cnt = forceInt(record.value('cnt'))
            age = forceInt(record.value('clientAge'))
            sex = forceInt(record.value('clientSex'))
            MKB = normalizeMKB( forceString(record.value('MKB')) )
            rows = []

            if MKB:
                rows.extend(mapMainRows.get(MKB, []))
                if not rows:
                    rows.append(otherDiagRowIndex)
            else:
                rows.append(unknownDiagRowIndex)
            rows.append(totalRowIndex)

            ageCol = (min(max(age, 20), 71)-11)/10
            if ageCol == 4:
                if age > 55:
                    ageCol += 1
            elif ageCol > 4:
                ageCol += 1

            for row in rows:
                reportLine = reportMainData[row*2+(1 if sex == 1 else 0)]
                reportLine[ageCol] += cnt
                # reportLine[7] += cnt
                reportLine[rowSize - 1] += cnt

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('40%', [u'Нозология',    u''     ], CReportBase.AlignLeft),
            ('10%', [u'Код по МКБ X', u''     ], CReportBase.AlignLeft),
            ( '5%', [u'Пол',          u''     ], CReportBase.AlignCenter),
            ( '5%', [u'Возраст, лет', u'до 21'], CReportBase.AlignRight),
            ( '5%', [u'',             u'21-30'], CReportBase.AlignRight),
            ( '5%', [u'',             u'31-40'], CReportBase.AlignRight),
            ( '5%', [u'',             u'41-50'], CReportBase.AlignRight),
            # ( '5%', [u'',             u'51-60'], CReportBase.AlignRight),
            ( '5%', [u'',             u'51-55'], CReportBase.AlignRight),
            ( '5%', [u'',             u'56-60'], CReportBase.AlignRight),
            ( '5%', [u'',             u'61-70'], CReportBase.AlignRight),
            ( '5%', [u'',             u'от 71'], CReportBase.AlignRight),
            ( '5%', [u'Всего',        u''     ], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1) # н.
        table.mergeCells(0, 1, 2, 1) # мкб
        table.mergeCells(0, 2, 2, 1) # пол
        # table.mergeCells(0, 3, 1, 7) # по возрастам
        table.mergeCells(0, 3, 1, 8)
        table.mergeCells(0, 11, 2, 1)

        for row, rowDescr in enumerate(MainRows) :
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.addRow()
            table.addRow()
            table.mergeCells(i, 0, 3, 1)
            table.mergeCells(i, 1, 3, 1)

            table.setText(i, 2, u'ж')
            table.setText(i+1, 2, u'м')
            table.setText(i+2, 2, u'всего')

            reportLine0 = reportMainData[row*2]
            reportLine1 = reportMainData[row*2+1]
            for col in xrange(rowSize):
                table.setText(i,   3+col, reportLine0[col])
                table.setText(i+1, 3+col, reportLine1[col])
                table.setText(i+2, 3+col, reportLine0[col]+reportLine1[col])

        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pacs',
        'port': 3306,
        'database': 's11vm',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CDeathReport(None)
    w.exec_()
    sys.exit(QtGui.qApp.exec_())


if __name__ == '__main__':
    main()
