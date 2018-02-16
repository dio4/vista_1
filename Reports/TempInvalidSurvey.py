# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import copy

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.MapCode            import createMapCodeToRowIdx
from library.Utils              import forceInt, forceString
from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import normalizeMKB, CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.TempInvalidF16     import MainRows
from Reports.TempInvalidList    import CTempInvalidSetupDialog


def selectData(begDate, endDate, byPeriod, doctype, tempInvalidReasonId, onlyClosed, orgStructureId, personId, durationFrom, durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter, MKBFrom, MKBTo, insuranceOfficeMark):
    stmt="""
SELECT
   COUNT(*) AS cnt,
   SUM(DATEDIFF(TempInvalid.endDate, TempInvalid.caseBegDate)+1) AS duration,
   Diagnosis.MKB,
   rbTempInvalidReason.code AS reasonCode,
   rbTempInvalidReason.grouping AS reasonGroup
   FROM TempInvalid
   LEFT JOIN TempInvalid AS NextTempInvalid ON TempInvalid.id = NextTempInvalid.prev_id
   LEFT JOIN Diagnosis ON Diagnosis.id = TempInvalid.diagnosis_id
   LEFT JOIN Person    ON Person.id = TempInvalid.person_id
   LEFT JOIN rbTempInvalidReason ON rbTempInvalidReason.id = TempInvalid.tempInvalidReason_id
   LEFT JOIN Client    ON Client.id = TempInvalid.client_id
WHERE
   NextTempInvalid.id IS NULL AND
   %s
GROUP BY MKB, TempInvalid.tempInvalidReason_id
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
#        cond.append(table['duration'].ge(durationFrom))
#        cond.append(table['duration'].le(durationTo))
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

    return db.query(stmt % (db.joinAnd(cond)))


class CTempInvalidSurvey(CReport):
    name = u'Сводка ВУТ'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CTempInvalidSetupDialog(parent)
        result.setAnalysisMode(True)
        result.setTitle(self.title())
        return result


    def getRows(self):
        localRows = copy.copy(MainRows)
#        toRemove = [u'Всего по заболеваниям', u'ИТОГО ПО ВСЕМ ПРИЧИНАМ']
#        removeRows = [ i for (i, rowDescr) in enumerate(localRows) if rowDescr[0] in toRemove]
#        for i in reversed(removeRows):
#            del localRows[i]
        localRows.append(( u'Z-ки', u'Z00-Z99'))
        localRows.append(( u'НЕ ПОДЛЕЖИТ КЛАССИФИКАЦИИ', u''))
        return localRows


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

        localRows = self.getRows()

        mapMainRows = createMapCodeToRowIdx( [row[1] for row in localRows] )

        reportMainData = [{} for x in xrange(len(localRows))]
        outrangeRowIndex   = len(localRows)-1
        zRowIndex          = outrangeRowIndex-1
        pregnancyRowIndex  = zRowIndex-1
        totalRowIndex      = pregnancyRowIndex-1
        quarantineRowIndex = totalRowIndex-1
        sanatoriumRowIndex = quarantineRowIndex-1
        careRowIndex       = sanatoriumRowIndex-1
        diseaseRowIndex    = careRowIndex-2

        skipDetails = set([totalRowIndex, quarantineRowIndex, sanatoriumRowIndex, careRowIndex, diseaseRowIndex])

        query = selectData(begDate, endDate, byPeriod, doctype, tempInvalidReason, onlyClosed, orgStructureId, personId, durationFrom, durationTo, sex, ageFrom, ageTo, socStatusClassId, socStatusTypeId, MKBFilter, MKBFrom, MKBTo, insuranceOfficeMark)
        totalCnt  = 0
        totalDays = 0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record   = query.record()
            reasonGroup = forceInt(record.value('reasonGroup'))
            reasonCode = forceString(record.value('reasonCode'))
            cnt = forceInt(record.value('cnt'))
            duration = forceInt(record.value('duration'))
            MKB = forceString(record.value('MKB'))
            rows = []
            if reasonGroup == 0: ## заболевание
#                if MKB[:2] == 'N7':
#                    pass
                rows.extend(mapMainRows.get(normalizeMKB(MKB), []))
                if rows or MKB[:1] == 'Z':
                    rows.append(totalRowIndex)
            elif reasonGroup == 1: ## уход
                if reasonCode in (u'09', u'12', u'13', u'15'): # уход за больным
                    rows = [careRowIndex, totalRowIndex]
                elif reasonCode == u'03': # карантин
                    rows = [quarantineRowIndex, totalRowIndex]
                elif reasonCode == u'14': # поствакцинальное осложнение
                    rows = [quarantineRowIndex, totalRowIndex]
                elif reasonCode == u'08': # санкурлечение
                    rows = [sanatoriumRowIndex, totalRowIndex]
            elif reasonGroup == 2:
                    rows = [pregnancyRowIndex]
            if not rows:
                rows = [outrangeRowIndex]

            for row in rows:
                reportLineGroup = reportMainData[row]
                if row in skipDetails:
                    diagData = reportLineGroup.setdefault('', [0, 0])
                else:
                    diagData = reportLineGroup.setdefault(MKB, [0, 0])
                diagData[0] += cnt
                diagData[1] += duration
            totalCnt  += cnt
            totalDays += duration

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('25%', [u'Причина нетрудоспособности',    u'1' ], CReportBase.AlignLeft),
            ('10%', [u'Группировка по коду МКБ',       u'2' ], CReportBase.AlignLeft),
            ('10%', [u'код МКБ',                       u'3' ], CReportBase.AlignLeft),
            ('15%', [u'число случаев',                 u'4' ], CReportBase.AlignRight),
            ('15%', [u'число дней',                    u'5' ], CReportBase.AlignRight),
            ('15%', [u'средняя длительность',          u'6' ], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)

        for row, rowDescr in enumerate(localRows):
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            reportLineGroup = reportMainData[row]
            if reportLineGroup:
                diags = reportLineGroup.keys()
                diags.sort()
                diagTotalCnt  = 0
                diagTotalDays = 0
                for diagRow, MKB in enumerate(diags):
                    if diagRow != 0:
                        j = table.addRow()
                    else:
                        j = i
                    diagInfo = reportLineGroup[MKB]
                    table.setText(j, 2, MKB)
                    table.setText(j, 3, diagInfo[0])
                    table.setText(j, 4, diagInfo[1])
                    if diagInfo[0] :
                        table.setText(j, 5, '%1.2f'%(diagInfo[1]/diagInfo[0]))
                    diagTotalCnt  += diagInfo[0]
                    diagTotalDays += diagInfo[1]
                if len(diags)>1:
                    j = table.addRow()
                    table.setText(j, 2, u'всего', CReportBase.TableTotal)
                    table.setText(j, 3, diagTotalCnt, CReportBase.TableTotal)
                    table.setText(j, 4, diagTotalDays, CReportBase.TableTotal)
                    if diagTotalCnt:
                        table.setText(j, 5, '%1.2f'%(float(diagTotalDays)/diagTotalCnt), CReportBase.TableTotal)
                    table.mergeCells(i, 0, len(diags)+1, 1) # п.н.
                    table.mergeCells(i, 1, len(diags)+1, 1) # мкб
        i = table.addRow()
        table.setText(i, 0, u'ВСЕГО', CReportBase.TableTotal)
        table.mergeCells(i, 0, 1, 3)
        table.setText(i, 3, totalCnt, CReportBase.TableTotal)
        table.setText(i, 4, totalDays, CReportBase.TableTotal)
        if totalDays:
            table.setText(i, 5, '%1.2f'%(float(totalDays)/totalCnt), CReportBase.TableTotal)

        return doc
