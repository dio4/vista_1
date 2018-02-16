# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrganisationInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog
from library.Utils import forceInt, forceString, getVal
from library.database import addDateInRange


def compareMKBHigh(MKBHigh, MKBReferenceHigh):
    if MKBReferenceHigh[1:] == 'xx':
        return MKBHigh[0] == MKBReferenceHigh[0]
    elif MKBReferenceHigh[2:] == 'x':
        return MKBHigh[:2] == MKBReferenceHigh[:2]
    else:
        return MKBHigh == MKBReferenceHigh

def compareMKBLow(MKBLow, MKBReferenceLow):
    if MKBReferenceLow and not MKBLow:          # A00 != A00.1
        return False
    elif not MKBReferenceLow:                   # A00.1 == A00
        return True
    elif QtGui.qApp.isAllowedExtendedMKB():     # A00.12345 - МКБ психов
        state = 0                               # 0 - значения МКБ, 1 - указание количества символов: x4
        for s in MKBReferenceLow:
            # Посимвольно проверяем на сходство. Если в какой-то момент не сошлись - значит разные
            # Если обнаружена маска, то сравниваем количество непроверенных символов в расширении МКБ со значением в маске
            # на точное совпадение.
            if s.isdigit():
                if state == 0:
                    if MKBLow and MKBLow[0] == s:
                        MKBLow = MKBLow[1:]
                    else:
                        return False
                else:
                    return len(MKBLow) == int(s)
            elif s == 'x':
                state = 1
    else:
        return MKBReferenceLow == MKBLow        # A00.01 - нормальные МКБ

def compareMKB(MKB, MKBReference):
    # Возвращает истину, если
    # MKB = A00, MKBReference = A00
    # MKB = A00.0, MKBReference = A00
    # MKB = A00.0, MKBReference = A00.0
    # Остальные сочетания - ложь.
    dotsReference = MKBReference.count('.')
    if dotsReference == 1:
        MKBReferenceHigh, MKBReferenceLow = MKBReference.split('.')
    elif dotsReference == 0:
        MKBReferenceHigh = MKBReference
        MKBReferenceLow = ''
    else:
        raise Exception(u'Код МКБ не может содержать несколько точек (%s)' % MKBReference)
    dotsMKB = MKB.count('.')
    if dotsMKB == 1:
        MKBHigh, MKBLow = MKB.split('.')
    elif dotsMKB == 0:
        MKBHigh = MKB
        MKBLow = ''
    else:
        raise Exception(u'Код МКБ не может содержать несколько точек (%s)' % MKB)

    if compareMKBHigh(MKBHigh, MKBReferenceHigh):
        return compareMKBLow(MKBLow, MKBReferenceLow)
    return False

class CMKB:
    def __init__(self, MKB):
        self.MKB = MKB.strip()

    def __repr__(self):
        return self.MKB

    def __eq__(self, other):
        if other.split('.') and self.MKB.split('.'):
            return self.MKB == other
        else:
            return self.MKB[:3] == other

    def __ge__(self, other):
        other = other.strip()
        if self.MKB[0] < other[0]:
            return False
        elif self.MKB[0] > other[0]:
            return True
        else:
            if self.MKB[1:3] != other[1:3]:
                return int(self.MKB[1:3]) > int(other[1:3])
            else:
                if len(other.split('.')) == 1:
                    return True
                elif len(self.MKB.split('.')) == 1:
                    return False
                else:
                    return int(self.MKB[4:]) >= int(other[4:])

    def __le__(self, other):
        other = other.strip()
        if not other:
            return False
        if self.MKB[0] > other[0]:
            return False
        elif self.MKB[0] < other[0]:
            return True
        else:
            if self.MKB[1:3] != other[1:3]:
                return int(self.MKB[1:3]) < int(other[1:3])
            else:
                if len(other.split('.')) == 1:
                    return True
                elif len(self.MKB.split('.')) == 1:
                    return False
                else:
                    return int(self.MKB[4:]) <= int(other[4:])


def MKBinRange(MKBVal, MKBRange):
    MKBRangeList = MKBRange.split('-')
    if not MKBVal:
        return False
    if len(MKBRangeList) == 1:
        return compareMKB(MKBVal, MKBRange.strip())
    elif len(MKBRangeList) == 2:
        # Обрабатываются диапазоны A00-A99, A00.01-A00.99. Теоретически допустимы извращения типа A00.99-A99
        # Также возможен вариант A00.0-9, обрабатывается как A00.0-A00.9
        bottom, top = MKBRangeList
        if top.isdigit():
            top = bottom.split('.')[0] + '.' + top
        MKB = CMKB(MKBVal)
        if MKB <= top and MKB >= bottom:
            return True
        return False
    else:           # Диапазон указан некорректно
        return False

def MKBinString(MKBVal, MKBRangeString):
    MKBRangeList = MKBRangeString.split(',')
    for MKBRange in MKBRangeList:
        if MKBinRange(MKBVal, MKBRange):
            return True
    return False



def selectData(params, suspicions):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    payStatusCode = params.get('payStatusCode', None)
    eventTypeId  = params.get('eventTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')

    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTable = queryTable.innerJoin(tableEventType, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEventType['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']),tableEventKind['code'].inlist(['01', '02', '04'])]))
    queryTable = queryTable.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableDiseaseCharacter, db.joinAnd([tableDiseaseCharacter['id'].eq(tableDiagnostic['character_id']),  tableDiseaseCharacter['code'].eq(5 if suspicions else 2)]))
    queryTable = queryTable.innerJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))

    cols = ['COUNT(DISTINCT Event.id) as count,'
            'age(Client.birthDate, Event.setDate) as clientAge',
            tableDiagnosis['MKB'],
            tableClient['sex']
    ]

    group = [tableClient['sex'],
            'age(Client.birthDate, Event.setDate)',
            tableDiagnosis['MKB']
            ]

    cond = []

    if not params.get('countUnfinished', False):
        addDateInRange(cond, tableEvent['execDate'], begDate, endDate)
    else:
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append(u'Event.setDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append(u'Event.setDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if payStatusCode is not None:
        tableContract = db.table('Contract')
        queryTable = queryTable.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        cond.append('getPayCode(%s, %s) = %d' % (tableContract['finance_id'],
                                                 tableEvent['payStatus'],
                                                 payStatusCode)
                    )
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


class CReportDDFoundIllnesses(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        if suspicions:
            self.setTitle(u'Сведения о выявленных подозрениях на наличие заболеваний (случаев)')
        else:
            self.setTitle(u'Сведения о выявленных заболеваниях (случаев)')



    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, age, count):
        if age >= 21 and age <= 36:
            row[9] += count
            if sex:
                row[sex*3] += count
        elif age >= 39 and age <= 60:
            row[10] += count
            if sex:
                row[sex*3 + 1] += count
        elif age > 60:
            row[11] += count
            if sex:
                row[sex*3 + 2] += count

    def processRecord(self, record):
        MKB = forceString(record.value('MKB'))
        sex = forceInt(record.value('sex'))
        count = forceInt(record.value('count'))
        age = forceInt(record.value('clientAge'))

        for row in self.resultSet:
            MKBfound = False
            if MKBinString(MKB, row[2]):
                MKBfound = True
                self.processRow(row, sex, age, count)
        if not MKBfound:
            self.processRow(self.resultSet[-2], sex, age, count)
        self.processRow(self.resultSet[-1], sex, age, count)

    def build(self, params):
        self.resultSet = [[u'Некоторые инфекционные и паразитарные болезни', u'01', u'A00-B99', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'в том числе:\nтуберкулез', u'02', u'A15-A19', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Новообразования', u'03', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tзлокачественные новообразования', u'04', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tв том числе:\n\t\tпищевода', u'05', u'C15', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tжелудка', u'06', u'C16', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tободочной кишки', u'07', u'C18', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tпрямой кишки, ректосигмоидного соединения, заднего прохода (ануса) и анального канала', u'08', u'C19-C21', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tподжелудочной железы', u'09', u'C25', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tтрахеи, бронхов и легкого', u'10', u'C33, 34', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tмолочной железы', u'11', u'C50', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tшейки матки', u'12', u'C53', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tтела матки', u'13', u'C54', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tяичника', u'14', u'C56', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tпредстательной железы', u'15', u'C61', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tпочки (кроме почечной лоханки)', u'16', u'C64', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни крови, проветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'17', u'D50-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tанемии', u'18', u'D50-D64', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'19', u'E00-E89', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tсахарный диабет', u'20', u'E00-E14', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tожирение', u'21', u'E66', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни нервной системы', u'22', u'G00-G98', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tпреходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', u'23', u'G45', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни глаза и его придаточного аппарата', u'24', u'H00-H59', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tкатаракта', u'25', u'H25, H26', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tглаукома', u'26', u'H40', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tслепота и пониженное зрение', u'27', u'H54', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни системы кровообращения', u'28', u'I00-I99', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tболезни, характеризующиеся повышенным кровяным давлением', u'29', u'I10-I13', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tишемическая болезнь сердца', u'30', u'I20-I25', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tв том числе:\n\t\tстенокардия (грудная жаба)', u'31', u'I20', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\t\tв том числе нестабильная стенокардия', u'32', u'I20.0', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tхроническая ишемическая болезнь сердца', u'33', u'I25', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tдругие болезни сердца', u'34', u'I30-I52', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tцереброваскулярные болезни', u'35', u'I60-I69', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tв том числе:\n\t\tзакупорка и стеноз прецеребральных, церебральных артерий, не приводящие к инфаркту мозга', u'36', u'I65, I66', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\t\tдругие цереброваскулярные болезни', u'37', u'I67', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни органов дыхания', u'38', u'J00-J98', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tпневмония', u'39', u'J12-J18', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tбронхит хронический и неуточненный, эмфизема', u'40', u'J40-J43', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tдругая хроническая обструктивная легочная болезнь, бронхоэктатическая болезнь', u'41', u'J44-J47', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни органов пищеварения', u'42', u'K00-K92', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tязва желудка, двенадцатиперстной кишки', u'43', u'K25, K26', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tгастрит и дуоденит', u'44', u'K29', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tнеинфекционный энтерит и колит', u'45', u'K50-K52', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tдругие болезни кишечника', u'46', u'K55-K63', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Болезни мочеполовой системы', u'47', u'N00-N99', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tв том числе:\n\tболезни предстательной железы', u'48', u'N40-N42', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tдоброкачественная дисплазия молочной железы', u'49', u'N60', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'\tВоспалительные болезни женских тазовых органов', u'50', u'N77', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Прочие заболевания', u'51', u'', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'ИТОГО', u'52', u'', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     ]


        query = selectData(params, self.suspicions)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            self.processRecord(query.record())

        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ( '38%', [u'Заболевание (подозрение на заболевание)', u''], CReportBase.AlignLeft),
            ( '3%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '5%', [u'Код по МКБ-10', u''], CReportBase.AlignCenter),
            ( '6%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '6%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '6%', [u'Всего', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '6%', [u'', u'Старше 60 лет'], CReportBase.AlignRight)
        ]

        rowSize = 12
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(0, 6, 1, 3)
        table.mergeCells(0, 9, 1, 3)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        return doc
