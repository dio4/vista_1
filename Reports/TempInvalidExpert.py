# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from library.database           import addDateInRange
from library.Utils              import forceInt, forceString
from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.TempInvalidList    import CTempInvalidSetupDialog


def selectData(begDate, endDate, byPeriod, doctype, tempInvalidReasonId, onlyClosed, orgStructureId, personId, durationFrom, durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter, MKBFrom, MKBTo, insuranceOfficeMark):
    stmt="""
SELECT
    SUM(d1) AS s1,
    SUM(d2) AS s2,
    SUM(d3) AS s3,
    SUM(d4) AS s4,
    SUM(d5) AS s5,
    SUM(d6) AS s6,
    SUM(d7) AS s7,
    SUM(d8) AS s8,
    SUM(d9) AS s9

FROM (
SELECT
   BIT_OR( TempInvalid.caseBegDate >= %(begDate)s AND TempInvalid.caseBegDate <= %(endDate)s) AS d1,
   BIT_OR( TempInvalid.caseBegDate >= %(begDate)s AND TempInvalid.caseBegDate <= %(endDate)s AND rbTempInvalidReason.code in ('04', '07')) AS d2,

   BIT_OR( DATEDIFF(%(begDate)s, TempInvalid.caseBegDate) >= 30 ) AS d3,
   BIT_OR( DATEDIFF(%(begDate)s, TempInvalid.caseBegDate) >= 30 AND rbTempInvalidReason.code in ('04', '07')) AS d4,

   BIT_OR( rbTempInvalidResult.status = 5 ) AS d5,
   BIT_OR( rbTempInvalidResult.status = 5  AND rbTempInvalidReason.code in ('04', '07')) AS d6,

   BIT_OR( rbTempInvalidResult.status = 3 ) AS d7,
   BIT_OR( rbTempInvalidResult.status = 3  AND rbTempInvalidReason.code in ('04', '07')) AS d8,

   BIT_OR( rbTempInvalidResult.closed = 1 AND rbTempInvalidResult.able = 1 ) AS d9

FROM TempInvalid
LEFT JOIN rbTempInvalidDocument ON rbTempInvalidDocument.id = TempInvalid.doctype_id
LEFT JOIN rbTempInvalidReason   ON rbTempInvalidReason.id = TempInvalid.tempInvalidReason_id
LEFT JOIN TempInvalid AS TI     ON TI.client_id = TempInvalid.client_id AND TI.caseBegDate = TempInvalid.caseBegDate
LEFT JOIN TempInvalid_Period    ON TempInvalid_Period.master_id = TI.id
LEFT JOIN rbTempInvalidResult   ON rbTempInvalidResult.id = TempInvalid_Period.result_id
LEFT JOIN Diagnosis             ON Diagnosis.id = TempInvalid.diagnosis_id
LEFT JOIN Person                ON Person.id = TempInvalid.person_id
LEFT JOIN Client                ON Client.id = TempInvalid.client_id

WHERE
 %(mainCond)s
GROUP BY TempInvalid.client_id
) ByClient;
    """
    db = QtGui.qApp.db
    table = db.table('TempInvalid')
    tableClient = db.table('Client')
    cond = []
    if doctype:
        cond.append(table['doctype_id'].eq(doctype))
    else:
        cond.append(table['type'].eq(0))
    cond.append(table['deleted'].eq(0))
    if tempInvalidReasonId:
        cond.append(table['tempInvalidReason_id'].eq(tempInvalidReasonId))
    if byPeriod:
        cond.append(table['caseBegDate'].le(endDate))
        cond.append(table['endDate'].ge(begDate))
    else:
        addDateInRange(cond, table['endDate'], begDate, endDate)
    if onlyClosed:
        cond.append(table['closed'].eq(1))
    if orgStructureId:
        tablePerson = db.table('Person')
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if personId:
        cond.append(table['person_id'].eq(personId))
    if durationTo:
        cond.append('DATEDIFF(TempInvalid.endDate, TempInvalid.caseBegDate)+1 BETWEEN %d AND %d'%(durationFrom, durationTo))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('TempInvalid.caseBegDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('TempInvalid.casebegDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
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
    if MKBFilter == 1:
        tableDiagnosis = db.table('Diagnosis')
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    elif MKBFilter == 2:
        tableDiagnosis = db.table('Diagnosis')
        cond.append(db.joinOr([tableDiagnosis['MKB'].eq(''), tableDiagnosis['MKB'].isNull()]))
    if insuranceOfficeMark in [1, 2]:
        cond.append(table['insuranceOfficeMark'].eq(insuranceOfficeMark-1))

    return db.query(stmt % { 'begDate' : table['begDate'].formatValue(begDate),
                             'endDate' : table['endDate'].formatValue(endDate),
                             'mainCond': db.joinAnd(cond)
                           })


class CTempInvalidExpert(CReport):
    name = u'Экспертный отчет по ВУТ'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CTempInvalidSetupDialog(parent)
        result.setAnalysisMode(True)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        byPeriod = params.get('byPeriod', False)
        doctype = params.get('doctype', 0)
        tempInvalidReason = params.get('tempInvalidReason', None)
        onlyClosed = params.get('onlyClosed', True)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        durationFrom = params.get('durationFrom', 0)
        durationTo = params.get('durationTo', 0)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom   = params.get('MKBFrom', '')
        MKBTo     = params.get('MKBTo', '')
        insuranceOfficeMark = params.get('insuranceOfficeMark', 0)

        query = selectData(begDate, endDate, byPeriod, doctype, tempInvalidReason, onlyClosed, orgStructureId, personId, durationFrom, durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter, MKBFrom, MKBTo, insuranceOfficeMark)
        self.setQueryText(forceString(query.lastQuery()))
        if query.next():
            record = query.record()
        else:
            record = QtSql.QSqlRecord()

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('10%', [u'Количество лиц, у которых установлена временная нетрудоспособность',
                     u'всего',
                     u'1'
                    ], CReportBase.AlignRight),
            ('10%', [u'',
                     u'в т.ч. в результате несчастных случаев на производстве и профессиональных заболеваний',
                     u'2'
                    ], CReportBase.AlignRight),

            ('10%', [u'Количество лиц, у которых временная нетрудоспособность установлена врачебной комиссией (сроком свыше 30 дней)',
                     u'всего',
                     u'3'
                    ], CReportBase.AlignRight),
            ('10%', [u'',
                     u'в т.ч. в результате несчастных случаев на производстве и профессиональных заболеваний',
                     u'4'
                    ], CReportBase.AlignRight),

            ('10%', [u'Количество лиц направленных на госпитализацию',
                     u'всего',
                     u'5'
                    ], CReportBase.AlignRight),
            ('10%', [u'',
                     u'в т.ч. в результате несчастных случаев на производстве и профессиональных заболеваний',
                     u'6'
                    ], CReportBase.AlignRight),

            ('10%', [u'Количество лиц направленных на медико-социальную экспертную комиссию',
                     u'всего',
                     u'7'
                    ], CReportBase.AlignRight),
            ('10%', [u'',
                     u'в т.ч. в результате несчастных случаев на производстве и профессиональных заболеваний',
                     u'8'
                    ], CReportBase.AlignRight),

            ('10%', [u'Количество лиц вернувшихся в трудоспособное состояние',
                     u'',
                     u'9'
                    ], CReportBase.AlignRight),

            ('10%', [u'Количество выданных заключений независимой экспертизы',
                     u'',
                     u'10'
                    ], CReportBase.AlignRight),

            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)

        i = table.addRow()
        for j in range(10):
            table.setText(i, j, forceInt(record.value(j)))

        return doc
