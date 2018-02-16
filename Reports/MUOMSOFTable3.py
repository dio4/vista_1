# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.MapCode        import createMapCodeToRowIdx
from library.Utils          import forceDouble, forceInt, forceRef, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport, normalizeMKB
from Reports.ReportBase     import createTable, CReportBase
from Reports.MUOMSOFTable1  import CMUOMSOFSetupDialog


def selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo):
    stmt="""
SELECT
    Event.client_id AS client_id,
    rbMedicalAidType.code AS medicalAidTypeCode,
    Diagnosis.MKB AS MKB,
    Account_Item.`sum` AS `sum`
FROM
    Account_Item
    LEFT JOIN Account    ON Account.id = Account_Item.master_id
    LEFT JOIN Event      ON Event.id = Account_Item.event_id
    LEFT JOIN EventType  ON EventType.id = Event.eventType_id
    LEFT JOIN Action     ON Action.id = Account_Item.action_id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
    LEFT JOIN Client     ON Client.id = Event.client_id
    LEFT JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Event.client_id, 1)
    LEFT JOIN Diagnosis  ON Diagnosis.id = getEventDiagnosis(Event.id)
WHERE
    (ActionType.isMES OR Event.MES_id) AND Account_Item.reexposeItem_id IS NULL AND Account_Item.deleted=0 AND Account.deleted=0 AND %s
    ORDER BY Event.client_id
"""
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableAccount = db.table('Account')
    tableClientPolicy = db.table('ClientPolicy')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(db.joinOr([tableEvent['execDate'].lt(endDate.addDays(1)), tableEvent['execDate'].isNull()]))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if contractIdList:
        cond.append(tableAccount['contract_id'].inlist(contractIdList))
    if insurerId:
        cond.append(tableClientPolicy['insurer_id'].eq(insurerId))
    return db.query(stmt % (db.joinAnd(cond)))


Rows = [
    (u'Всего', u'01',u'A00-Z99'),
    (u'некоторые инфекционные и паразитарные болезни', u'02',u'A00-B99'),
    (u'новообразования',u'03',u'C00-D48'),
    (u'болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'04',u'D50-D89'),
    (u'болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'05',u'E00-E90'),
    (u'психические расстройства и расстройства поведения', u'06',u'F00-F99'),
    (u'болезни нервной системы', u'07',u'G00-G99'),
    (u'болезни глаза и его придаточного аппарата', u'08',u'H00-H59'),
    (u'болезни уха и сосцевидного отростка', u'09',u'H60-H95'),
    (u'болезни системы кровообращения', u'10',u'I00-I99'),
    (u'ишемическая болезнь сердца', u'11',u'I20-I25'),
    (u'болезни, характеризующиеся повыщенным кровяным давлением', u'12',u'I10-I15'),
    (u'болезни органов дыхания', u'13',u'J00-J99'),
    (u'болезни органов пищеварения',u'14', u'K00-K93'),
    (u'болезни кожи и подкожной клетчатки', u'15',u'L00-L99'),
    (u'болезни костно-мышечной системы и соединительной ткани', u'16',u'M00-M99'),
    (u'болезни мочеполовой системы', u'17',u'N00-N99'),
    (u'беременность, роды и послеродовой период', u'18',u'O00-O99'),
    (u'отдельные состояния, возникающие в перинатальном периоде', u'19',u'P06-P96'),
    (u'врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'20',u'Q00-Q99'),
    (u'симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'21',u'R00-R99'),
    (u'травмы, отравления и некоторые другие последствия воздействия внешних причин',u'22',u'S00-T98'),
    (u'прочие, обычно не применяемые в ЗСЛ диагнозы',u'23',u'U00-Z99')
]


class CMUOMSOFTable3(CReport):
    name = u'Отчёт №1 МУОМС-ОФ, Таблица 3'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(self.name)


    def getSetupDialog(self, parent):
        result = CMUOMSOFSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        contractIdList = params.get('contractIdList', None)
        insurerId = params.get('insurerId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)

        mapRows = createMapCodeToRowIdx( [row[2] for row in Rows] )
        rowSize = 1 + 8*2
        reportData = [ [0]*rowSize for row in xrange(len(Rows)) ]

        query = selectData(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, specialityId, personId, contractIdList, insurerId, sex, ageFrom, ageTo)
        prevClientId = False
        clientRows = set([])
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            clientId = forceRef(record.value('client_id'))
            MKB = normalizeMKB(forceString(record.value('MKB')))
            medicalAidTypeCode = forceInt(record.value('medicalAidTypeCode'))
            sum = forceDouble(record.value('sum'))

            if prevClientId != clientId:
                for row in clientRows:
                    reportData[row][0] += 1
                prevClientId = clientId
                clientRows = set([])

            if 1<=medicalAidTypeCode<=8:
                if medicalAidTypeCode in [2, 3]:
                    cols = [1, medicalAidTypeCode]
                else:
                    cols = [medicalAidTypeCode]

                for row in mapRows.get(MKB, []):
                    clientRows.add(row)
                    reportLine = reportData[row]
                    for col in cols:
                        reportLine[1+(col-1)*2] += 1
                        reportLine[1+(col-1)*2+1] += sum
        for row in clientRows:
            reportData[row][0] += 1

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.name)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertText(u'Таблица 3. Стоимость нозологий по стандарту за законченный случай лечения')
        cursor.insertBlock()

        qnt = u'кол-во единиц учёта'
        sum = u'сумма (тыс.руб)'
        prc = u'стоимость случая (руб)'

        tableColumns = [
            ('8%',[u'Наименование классов по МКБ (в т.ч. заболевания)', '', '', '', '1'], CReportBase.AlignLeft),
            ('3%', [u'код МКБ',                                         '', '', '', '2'], CReportBase.AlignLeft),
            ('3%', [u'№ строки',                                        '', '', '', '3'], CReportBase.AlignRight),
            ('3%', [u'численность пролеченных граждан, человек',        '', '', '', '4'], CReportBase.AlignRight),

            ('3%', [u'Виды медицинской помощи', u'стационарная помощь',u'',  qnt, '5'], CReportBase.AlignRight),
            ('3%', [u'',                        u'', u'',                    sum, '6'], CReportBase.AlignRight),
            ('3%', [u'',                        u'', u'',                    prc, '7'], CReportBase.AlignRight),

            ('3%', [u'', u'в том числе', u'высокотехнологичная помощь', qnt, '8'], CReportBase.AlignRight),
            ('3%', [u'', u'',            u'',                           sum, '9'], CReportBase.AlignRight),
            ('3%', [u'', u'',            u'',                           prc,'10'], CReportBase.AlignRight),

            ('3%', [u'', u'',            u'специализированная стационарная помощь', qnt, '11'], CReportBase.AlignRight),
            ('3%', [u'', u'',            u'',                                       sum, '12'], CReportBase.AlignRight),
            ('3%', [u'', u'',            u'',                                       prc, '13'], CReportBase.AlignRight),

            ('3%', [u'', u'скорая помощь',                    u'', qnt, '14'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', sum, '15'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', prc, '16'], CReportBase.AlignRight),

            ('3%', [u'', u'скорая специализированная помощь', u'', qnt, '17'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', sum, '18'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', prc, '19'], CReportBase.AlignRight),

            ('3%', [u'', u'амбулаторная помощь',              u'', qnt, '20'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', sum, '21'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', prc, '22'], CReportBase.AlignRight),

            ('3%', [u'', u'дневной стационар',                u'', qnt, '23'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', sum, '24'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', prc, '25'], CReportBase.AlignRight),

            ('3%', [u'', u'санаторно-курортное лечение',      u'', qnt, '26'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', sum, '27'], CReportBase.AlignRight),
            ('3%', [u'', u'',                                 u'', prc, '28'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 4, 1) # Наименование
        table.mergeCells(0, 1, 4, 1) # Код МКБ
        table.mergeCells(0, 2, 4, 1) # № стр.
        table.mergeCells(0, 3, 4, 1) # Человеки
        table.mergeCells(0, 4, 1, 3*8) # виды
        table.mergeCells(1, 4, 2, 3) # стац
        table.mergeCells(1, 7, 1, 6) # в т.ч.
        table.mergeCells(2, 7, 1, 3) # ВТМП
        table.mergeCells(2,10, 1, 3) # СпСтП
        table.mergeCells(1,13, 2, 3) # СкП
        table.mergeCells(1,16, 2, 3) # СпСкП
        table.mergeCells(1,19, 2, 3) # АП
        table.mergeCells(1,22, 2, 3) # ДнС
        table.mergeCells(1,25, 2, 3) # СКП

        for row, rowDescr in enumerate(Rows):
            reportLine = reportData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[2])
            table.setText(i, 2, rowDescr[1])
            table.setText(i, 3, reportLine[0])
            for col in xrange(8):
                qnt = reportLine[1+col*2]
                sum = reportLine[1+col*2+1]
                prc = ('%.2f' % (sum/qnt)) if qnt else ''
                table.setText(i, 4+3*col, qnt)
                table.setText(i, 4+3*col+1, '%.2f'%(sum/1000))
                table.setText(i, 4+3*col+2, prc)
        return doc
