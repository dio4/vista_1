# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database           import addDateInRange
from library.MapCode            import createMapCodeToRowIdx
from library.Utils              import forceDate, forceInt, forceString, calcAgeInYears
from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import normalizeMKB, CReport
from Reports.ReportBase         import createTable, CReportBase
from Reports.TempInvalidList    import CTempInvalidSetupDialog

MainRows = [
    ( u'Некоторые инфекционные и паразитарные болезни', u'A00-B99', ('02', '01')),
    ( u'в том числе: кишечные инфекции', u'A00-A09', ('04', '03')),
    ( u'туберкулез', u'A15-A19', ('06', '05')),
    ( u'вирусный гепатит', u'B15-B19', ('08', '07')),
    ( u'Новообразования', u'C00-D48', (10, '09')),
    ( u'из них злокачественные новообразования', u'C00-D09', (12, 11)),
    ( u'Болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'D50-D89', (14, 13)),
    ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'E00-E90', (16, 15)),
    ( u'в том числе: сахарный диабет', u'E10-E14', (18, 17)),
    ( u'из него инсулинзависимый сахарный диабет', u'E10', (20, 19)),
    ( u'Психические расстройства и расстройства поведения', u'F00-F99', (22, 21)),
    ( u'Болезни нервной системы', u'G00-G99', (24, 23)),
    ( u'из них болезни периферической нервной системы', u'G50-G72', (26, 25)),
    ( u'Болезни глаза и его придаточного аппарата', u'H00-H59', (28, 27)),
    ( u'Болезни уха и сосцевидного отростка', u'H60-H95', (30, 29)),
    ( u'Болезни системы кровообращения', u'I00-I99', (32, 31)),
    ( u'в том числе: острая ревматическая лихорадка, хронические ревматические болезни сердца', u'I00-I09', (34, 33)),
    ( u'Болезни, характеризующиеся повышенным кровяным давлением', u'I10-I13', (36, 35)),
    ( u'ишемическая болезнь сердца', u'I20-I25', (38, 37)),
    ( u'цереброваскулярные болезни', u'I60-I69', (40, 39)),
    ( u'Болезни органов дыхания', u'J00-J99', (42, 41)),
    ( u'в том числе: острые респираторные инфекции верхних дыхательных путей', u'J00, J01, J04, J05, J06', (44, 43)),
    ( u'острый фарингит, острый тонзиллит', u'J02, J03', (46, 45)),
    ( u'грипп', u'J10, J11', (48, 47)),
    ( u'пневмония', u'J12-J18', (50, 49)),
    ( u'бронхиты, эмфизема', u'J40-J43', (52, 51)),
    ( u'астма, астматический статус', u'J45, J46', (54, 53)),
    ( u'пневмокониозы', u'J60, J66', (56, 55)),
    ( u'Болезни органов пищеварения', u'K00-K93', (58, 57)),
    ( u'в том числе: язва желудка и 12-перстной кишки', u'K25-K26', (60, 59)),
    ( u'гастрит и дуоденит', u'K29', (62, 61)),
    ( u'болезни печени, желчного пузыря, желчевыводящих путей и поджелудочной железы', u'K70-K86', (64, 63)),
    ( u'Болезни кожи и подкожной клетчатки', u'L00-L99', (66, 65)),
    ( u'из них инфекции кожи и подкожной клетчатки', u'L00-L08', (68, 67)),
    ( u'Болезни костномышечной и соединительной ткани', u'M00-M99', (70, 69)),
    ( u'из них серопозитивный ревматоидный, другие ревматоидные артриты', u'M05-M06, M08.0', (72, 71)),
    ( u'Болезни мочеполовой системы', u'N00-N99', (74, 73)),
    ( u'в том числе: болезни почек и мочевыделительных путей', u'N00-N39', (76, 75)),
    ( u'воспалительные болезни женских тазовых органов', u'N70-N76', (77, -1)),
    ( u'Беременность, роды и послеродовой период', u'O00-O99', (78, -1)),
    ( u'Врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'Q00-Q99', (80, 79)),
    ( u'Симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'R00-R99', (82, 81)),
    ( u'Травмы, отравления и некоторые другие последствия воздействия внешних причин', u'S00-T98', (84, 83)),
    ( u'в том числе: поверхностные травмы', u'S00, S10, S20, S30, S40, S50, S60, S70, S80, S90, T00, T09.0, T11.0, T13.0, T14.0', (86, 85)),
    ( u'переломы черепа и лицевых костей, внутричерепные травмы', u'S02, S06', (88, 87)),
    ( u'переломы костей верхних и нижних конечностей', u'S42, S52, S62, S72, S82, S92, T02.2 - 6, T10, T12', (90, 89)),
    ( u'вывихи, растяжения и перенапряжения капсульно-связочного аппарата', u'S03, S13, S23, S33, S43, S53, S63, S73, S83, S93, T03, T09.2, T11.2, T13.2, T14.3', (92, 91)),
    ( u'Всего по заболеваниям', u'A00-T98', (94, 93)),
    ( u'в том числе аборты (из стр. 78)', u'O03-O07', (95, -1)),
    ( u'Уход за больным', u'', (97, 96)),
    ( u'Отпуск в связи с санаторно-курортным лечением (без туберкулеза и долечивания инфаркта миокарда)', u'', (99, 98)),
    ( u'Освобождение от работы в связи с карантином и бактерионосительством', u'', (101, 100)),
    ( u'ИТОГО ПО ВСЕМ ПРИЧИНАМ', u'', (103, 102)),
    ( u'Отпуск по беременности и родам (неосложненным)', u'', (104, -1)),
    ]

newMainRows = [
    ( u'Некоторые инфекционные и паразитарные болезни', u'A00-B99', ('02', '01')),
    ( u'туберкулез', u'A15-A19', ('04', '03')),
    ( u'Новообразования', u'C00-D48', ('06', '05')),
    ( u'из них злокачественные новообразования', u'C00-C97', ('08', '07')),
    ( u'Болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'D50-D89', (10, '09')),
    ( u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'E00-E89, E90', (12, 11)),
    ( u'из них: сахарный диабет', u'E10-E14', (14, 13)),
    ( u'Психические расстройства и расстройства поведения', u'F00-F99', (16, 15)),
    ( u'Болезни нервной системы', u'G00-G98, G99', (18, 17)),
    ( u'Болезни глаза и его придаточного аппарата', u'H00-H59', (20, 19)),
    ( u'Болезни уха и сосцевидного отростка', u'H60-H95', (22, 21)),
    ( u'Болезни системы кровообращения', u'I00-I99', (24, 23)),
    ( u'ишемическая болезнь сердца', u'I20-I25', (26, 25)),
    ( u'цереброваскулярные болезни', u'I60-I69', (28, 27)),
    ( u'Болезни органов дыхания', u'J00-J98, J99', (30, 29)),
    ( u'из них: острые респираторные инфекции верхних дыхательных путей', u'J00, J01, J04, J05, J06', (32, 31)),
    ( u'грипп', u'J10, J11', (34, 33)),
    ( u'пневмония', u'J12-J18', (36, 35)),
    ( u'Болезни органов пищеварения', u'K00-K92, K93', (38, 37)),
    ( u'Болезни кожи и подкожной клетчатки', u'L00-L99', (40, 39)),
    ( u'Болезни костномышечной и соединительной ткани', u'M00-M99', (42, 41)),
    ( u'Болезни мочеполовой системы', u'N00-N99', (44, 43)),
    ( u'Беременность, роды и послеродовой период', u'O00-O99', (45, -1)),
    ( u'Врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'Q00-Q99', (47, 46)),
    ( u'Травмы, отравления и некоторые другие последствия воздействия внешних причин', u'S00-T98', (49, 48)),
    ( u'Всего по заболеваниям (стр.01-50), (стр.02-51)', u'A00-T98', (51, 50)),
    ( u'из них аборты (из стр. 45)', u'O03-O07', (52, -1)),
    ( u'Уход за больным', u'', (54, 53)),
    ( u'Отпуск в связи с санаторно-курортным лечением (без туберкулеза и долечивания инфаркта миокарда)', u'', (56, 55)),
    ( u'Освобождение от работы в связи с карантином и бактерионосительством', u'', (58, 57)),
    ( u'ИТОГО ПО ВСЕМ ПРИЧИНАМ', u'', (60, 59)),
    ( u'Отпуск по беременности и родам', u'', (61, -1)),
    ]


def selectData(begDate, endDate, byPeriod, doctype, tempInvalidReasonId, onlyClosed, orgStructureId, personId, insuranceOfficeMark):
    stmt="""
SELECT
   Client.birthDate,
   Client.sex,
   TempInvalid.caseBegDate,
   TempInvalid.endDate,
   TempInvalid.sex AS tsex,
   TempInvalid.age AS tage,
   DATEDIFF(TempInvalid.endDate, TempInvalid.caseBegDate)+1 AS duration,
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
    """
    db = QtGui.qApp.db
    table = db.table('TempInvalid')
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
    if insuranceOfficeMark in [1, 2]:
        cond.append(table['insuranceOfficeMark'].eq(insuranceOfficeMark-1))
    return db.query(stmt % (db.joinAnd(cond)))


class CTempInvalidF16(CReport):
    name = u'Сведения о причинах временной нетрудоспособности (Ф.16ВН)'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CTempInvalidSetupDialog(parent)
        result.setTitle(self.title())
        result.chkOldForm.setVisible(True)
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
        insuranceOfficeMark = params.get('insuranceOfficeMark', 0)
        oldForm = params.get('oldForm', 0)
        tableRows = MainRows if oldForm else newMainRows

        mapMainRows = createMapCodeToRowIdx( [row[1] for row in tableRows if row[1]] )

        db = QtGui.qApp.db

        rowSize = 12
        reportMainData = [ [0]*rowSize for row in xrange(len(tableRows)*2) ]
        pregnancyRowIndex  = len(tableRows)-1
        totalRowIndex      = pregnancyRowIndex-1
        quarantineRowIndex = totalRowIndex-1
        sanatoriumRowIndex = quarantineRowIndex-1
        careRowIndex       = sanatoriumRowIndex-1

        query = selectData(begDate, endDate, byPeriod, doctype, tempInvalidReason, onlyClosed, orgStructureId, personId, insuranceOfficeMark)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record   = query.record()
            reasonGroup = forceInt(record.value('reasonGroup'))
            reasonCode = forceString(record.value('reasonCode'))
            duration = forceInt(record.value('duration'))
            if reasonGroup == 1: ## уход
#                sex = forceInt(record.value('sex'))
#                age = calcAgeInYears(forceDate(record.value('birthDate')), forceDate(record.value('begDate')))
                sex = forceInt(record.value('tsex'))
                age = forceInt(record.value('tage'))
            else:
                sex = forceInt(record.value('sex'))
                age = calcAgeInYears(forceDate(record.value('birthDate')), forceDate(record.value('caseBegDate')))

            rows = []
            if reasonGroup == 0: ## заболевание
                MKB = forceString(record.value('MKB'))
                if MKB[:2] == 'N7':
                    pass
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
            # if age <15:
            #     continue
            if sex not in [1, 2]:
                continue
            ageCol = min(max(age, 15), 60)/5-1
            for row in rows:
                reportLine = reportMainData[row*2+(1 if sex == 1 else 0)]
                reportLine[0] += duration
                reportLine[1] += 1
                reportLine[ageCol] += 1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('15%', [u'Причина нетрудоспособности',    u'',            u'1' ], CReportBase.AlignLeft),
            ('10%', [u'Код по МКБ X',                  u'',            u'2' ], CReportBase.AlignLeft),
            ( '5%', [u'Пол',                           u'',            u'3' ], CReportBase.AlignCenter),
            ( '5%', [u'№ строки',                      u'',            u'4' ], CReportBase.AlignRight),
            ('10%', [u'число дней',                    u'',            u'5' ], CReportBase.AlignRight),
            ( '5%', [u'число случаев',                 u'',            u'6' ], CReportBase.AlignRight),
            ( '5%', [u'в т.ч. по возрастам',           u'15-19',       u'7' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'20-24',       u'8' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'25-29',       u'9' ], CReportBase.AlignRight),
            ( '5%', [u'',                              u'30-34',       u'10'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'35-39',       u'11'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'40-44',       u'12'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'45-49',       u'13'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'50-54',       u'14'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'55-59',       u'15'], CReportBase.AlignRight),
            ( '5%', [u'',                              u'60 и старше', u'16'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1) # п.н.
        table.mergeCells(0, 1, 2, 1) # мкб
        table.mergeCells(0, 2, 2, 1) # пол
        table.mergeCells(0, 3, 2, 1) # N
        table.mergeCells(0, 4, 2, 1) # дней
        table.mergeCells(0, 5, 2, 1) # случаев
        table.mergeCells(0, 6, 1,10) # по возрастам

        for row, rowDescr in enumerate(tableRows) :
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            rowSep = rowDescr[2]
            if rowSep[0]>0 and rowSep[1]>0:
                i1 = table.addRow()
                table.mergeCells(i, 0, 2, 1) # п.н.
                table.mergeCells(i, 1, 2, 1) # мкб
                mTableRow = i
                wTableRow = i1
            elif rowSep[0]>0:
                mTableRow = -1
                wTableRow = i
            else:
                mTableRow = i
                wTableRow = -1
            if wTableRow>=0:
                table.setText(wTableRow, 2, u'ж')
                table.setText(wTableRow, 3, rowSep[0])
                reportLine = reportMainData[row*2]
                for col in xrange(rowSize):
                    table.setText(wTableRow, 4+col, reportLine[col])
            if mTableRow>=0:
                table.setText(mTableRow, 2, u'м')
                table.setText(mTableRow, 3, rowSep[1])
                reportLine = reportMainData[row*2+1]
                for col in xrange(rowSize):
                    table.setText(mTableRow, 4+col, reportLine[col])
        return doc
