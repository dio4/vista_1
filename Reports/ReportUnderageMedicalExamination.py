# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import copy

from PyQt4 import QtCore, QtGui

from library.database                   import addDateInRange
from library.Utils                      import forceInt, forceRef, forceString
from Orgs.Utils                         import getOrgStructureDescendants, getOrgStructureFullName

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Ui_ReportUnderageMedicalExaminationSetup import Ui_ReportUnderageMedicalExaminationSetup


def selectData(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    eventTypeId = params.get('eventTypeId')
    countAttendant = params.get('countAttendant')
    orgStructureId = params.get('orgStructureId')
    orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableDispanser = db.table('rbDispanser')

    diagnosisTypes = ['1', '2', '9'] if countAttendant else ['1', '2']

    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(eventTypeId) if eventTypeId else '1', tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTable = queryTable.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableDiseaseCharacter, db.joinAnd([tableDiseaseCharacter['id'].eq(tableDiagnostic['character_id'])]))
    queryTable = queryTable.innerJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableDiagnosisType, db.joinAnd([tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']), tableDiagnosisType['code'].inlist(diagnosisTypes)]))
    queryTable = queryTable.leftJoin(tableDispanser, tableDispanser['id'].eq(tableDiagnosis['dispanser_id']))

    cols = [
        'COUNT(DISTINCT Event.id) AS cnt',
        'age(Client.birthDate, Event.setDate) as clientAge',
        tableDiagnosis['MKB'],
        tableDiseaseCharacter['code'].alias('characterCode'),
        tableDispanser['code'].alias('dispanserCode'),
        tableClient['sex']
    ]

    group = [
        tableClient['sex'],
        'age(Client.birthDate, Event.setDate)',
        tableDiagnosis['MKB'],
        tableDiseaseCharacter['code'],
        tableDispanser['code']
    ]

    cond = []

    cond.append('age(Client.birthDate, Event.setDate) <= 17')
    addDateInRange(cond, tableEvent['execDate'], begDate, endDate)

    if orgStructureId:
        tablePerson = db.table('Person')
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableDiagnosis['person_id']))
        # cond.append(tablePerson['orgStructure_id'].eq(orgStructureId))
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if orgStructureAttachTypeId:
        tableClientAttach = db.table('ClientAttach')
        attachTypeId1 = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
        attachTypeId2 = forceRef(db.translate('rbAttachType', 'code', u'2', 'id'))
        queryTable = queryTable.leftJoin(tableClientAttach, '''ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                FROM ClientAttach clAttach
                                                                                                                WHERE (clAttach.attachType_id = %s OR clAttach.attachType_id = %s)
                                                                                                                AND clAttach.client_id = Client.id)''' % (attachTypeId1, attachTypeId2))
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)

def selectDateChildAge(params) : #Запрос на вывод количества детей, прошедших профилактический осмотр, по заданным временным критериям
    eventTypeId = params.get('eventTypeId')
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId')
    orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')

    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(eventTypeId) if eventTypeId else '1', tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))

    cols = [
        'COUNT(DISTINCT Client.id) AS count_client_id',
        'age(Client.birthDate, Event.setDate) as clientAge'
    ]

    group = [
        'age(Client.birthDate, Event.setDate)',
    ]

    cond = []

    cond.append('age(Client.birthDate, Event.setDate) <= 17')
    addDateInRange(cond, tableEvent['execDate'], begDate, endDate)

    if orgStructureId:
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')

        queryTable = queryTable.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
        queryTable = queryTable.innerJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))

        tablePerson = db.table('Person')
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableDiagnosis['person_id']))
        # cond.append(tablePerson['orgStructure_id'].eq(orgStructureId))
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))

    if orgStructureAttachTypeId:
        tableClientAttach = db.table('ClientAttach')
        attachTypeId1 = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
        attachTypeId2 = forceRef(db.translate('rbAttachType', 'code', u'2', 'id'))
        queryTable = queryTable.leftJoin(tableClientAttach, '''ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                FROM ClientAttach clAttach
                                                                                                                WHERE (clAttach.attachType_id = %s OR clAttach.attachType_id = %s)
                                                                                                                AND clAttach.client_id = Client.id)''' % (attachTypeId1, attachTypeId2))
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)

class CReportUnderageMedicalExamination(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о профилактических медицинских отчетах несовершеннолетних.')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def processRow(self, row, sex, count, dispanserCode, characterCode):
        row[3] += count
        if sex == 1:
            row[4] += count
        if characterCode == u'2':
            row[5] += count
            if sex == 1:
                row[6] += count
        if dispanserCode in ['1', '2', '6']:
            row[7] += count
            if sex == 1:
                row[8] += count
            if dispanserCode == '2':
                row[9] += count
                if sex == 1:
                    row[10] += count

    def processRecordDifferential(self, record):
        MKB = forceString(record.value('MKB'))
        sex = forceInt(record.value('sex'))
        count = forceInt(record.value('cnt'))
        age = forceInt(record.value('clientAge'))
        dispanserCode = forceString(record.value('dispanserCode'))
        characterCode = forceString(record.value('characterCode'))
        if age <= 4:
            resultSet = self.resultSet
        elif age <= 9:
            resultSet = self.resultSet2
        elif age <= 14:
            resultSet = self.resultSet3
        elif age <= 17:
            resultSet = self.resultSet4

        MKBfound = False
        for row in resultSet[:-2]:
            if MKBinString(MKB, row[2]):
                MKBfound = True
                self.processRow(row, sex, count, dispanserCode, characterCode)
        if MKBinString(MKB, u'A00-T98'):
            if not MKBfound:
                self.processRow(resultSet[-2], sex, count, dispanserCode, characterCode)
            self.processRow(resultSet[-1], sex, count, dispanserCode, characterCode)

    def processRecordAll(self, record):
        MKB = forceString(record.value('MKB'))
        sex = forceInt(record.value('sex'))
        count = forceInt(record.value('cnt'))
        age = forceInt(record.value('clientAge'))
        dispanserCode = forceString(record.value('dispanserCode'))
        characterCode = forceString(record.value('characterCode'))
        resultSet = self.resultSet6


        MKBfound = False
        for row in resultSet[:-2]:
            if MKBinString(MKB, row[2]):
                MKBfound = True
                self.processRow(row, sex, count, dispanserCode, characterCode)
        if MKBinString(MKB, u'A00-T98'):
            if not MKBfound:
                self.processRow(resultSet[-2], sex, count, dispanserCode, characterCode)
            self.processRow(resultSet[-1], sex, count, dispanserCode, characterCode)

    def processRecord14(self, record):
        MKB = forceString(record.value('MKB'))
        sex = forceInt(record.value('sex'))
        count = forceInt(record.value('cnt'))
        age = forceInt(record.value('clientAge'))
        dispanserCode = forceString(record.value('dispanserCode'))
        characterCode = forceString(record.value('characterCode'))
        if age <= 14:
            resultSet = self.resultSet5

            MKBfound = False
            for row in resultSet[:-2]:
                if MKBinString(MKB, row[2]):
                    MKBfound = True
                    self.processRow(row, sex, count, dispanserCode, characterCode)
            if MKBinString(MKB, u'A00-T98'):
                if not MKBfound:
                    self.processRow(resultSet[-2], sex, count, dispanserCode, characterCode)
                self.processRow(resultSet[-1], sex, count, dispanserCode, characterCode)

    def numberChildren(self, minAge, maxAge, record): #Рассчитывается количество детей, прошедших профилактический осмотр
        age = forceInt(record.value('clientAge'))
        if age <= maxAge :
           if age >= minAge :
                return 1
        return 0



    def build(self, params):
        self.resultSet = [[u'1.', u'Некоторые инфекционные и паразитарные болезни,\nиз них:', u'A00-B99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'1.1.', u'туберкулез', u'A15-A19', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'1.2.', u'ВИЧ-инфекция, СПИД', u'B20-B24', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'2.', u'Новообразования', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'3.', u'Болезни крови и кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм, из них:', u'D50-D89', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'3.1.', u'анемии', u'D50-D53', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.', u'Болезни эндокринной систмы, расстройства питания и нарушения обмена веществ, из них:', u'E00-E90', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.1.', u'сахарный диабет', u'E10-E14', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.2.', u'недостаточность питания', u'E40-E46', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.3.', u'ожирение', u'E66', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.4.', u'задержка полового развития', u'E30.0', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'4.5.', u'преждевременное половое развитие', u'E30.1', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'5.', u'Психические расстройства и расстройства поведения, из них:', u'F00-F99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'5.1.', u'Умственная отсталость', u'F70-F79', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'6.', u'Болезни нервной системы, из них:', u'G00-G98', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'6.1', u'церебральный паралич и другие паралитические синдромы', u'G80-G83', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'7.', u'Болезни глаза и его придаточного аппарата', u'H00-H59', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'8.', u'Болезни уха и сосцевидного отростка', u'H60-H95', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'9.', u'Болезни системы кровообращения', u'I00-I99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'10.', u'Болезни органов дыхания, из них:', u'J00-J99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'10.1.', u'астма, астматический статус', u'J45-J46', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'11.', u'Болезни органов пищеварения', u'K00-K93', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'12.', u'Болезни кожи и подкожной клетчатки', u'L00-L99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'13.', u'Болезни костно-мышечной системы и соединительной ткани, из них:', u'M00-M99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'13.1.', u'кифоз, пордоз, сколиоз', u'M40-M41', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.', u'Болезни мочеполовой системы, из них:', u'N00-N99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.1', u'болезни мужских половых органов', u'N40-N51', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.2.', u'нарушения ритма и характера менструаций', u'N91-N94.5', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.3.', u'воспалительные болезни женских тазовых органов', u'N70-N77', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.4.', u'невоспалительные болезни женских половых органов', u'N83.0-N83.9', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'14.5.', u'болезни молочной железы', u'N60-N64', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'15.', u'Отдельные состояния, возникающие в перинатальном периоде', u'P00-P96', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.', u'Врожденные аномалии (пороки развития), деформации и хромосомные нарушения, из них:', u'Q00-Q99', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.1.', u'развития нервной системы', u'Q00-Q07', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.2.', u'системы кровообращения', u'Q20-Q28', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.3.', u'костно-мышечной ткани', u'Q65-Q679', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.4.', u'женских половых органов', u'Q50-Q52', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'16.5.', u'мужских половых органов', u'Q53-Q55', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'17.', u'Травмы, отравления и некоторые другие последствия воздействия внешних причин', u'S00-T98', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'',    u'Прочие', u'', 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'18.', u'Всего', u'A00-T98', 0, 0, 0, 0, 0, 0, 0, 0],
                     ]
        self.resultSet2 = copy.deepcopy(self.resultSet)
        self.resultSet3 = copy.deepcopy(self.resultSet)
        self.resultSet4 = copy.deepcopy(self.resultSet)
        self.resultSet5 = copy.deepcopy(self.resultSet)
        self.resultSet6 = copy.deepcopy(self.resultSet)

        number0_17 = 0
        number0_4 = 0
        number5_9 = 0
        number10_14 = 0
        number15_17 = 0

        query = selectData(params)
        while query.next():
            self.processRecordDifferential(query.record())
            self.processRecord14(query.record())
            self.processRecordAll(query.record())

        queryChildAge = selectDateChildAge(params) #Подсчёт количества детей, прошедших профилактический осмотр, по возрастным категориям
        self.setQueryText(forceString(queryChildAge.lastQuery()))
        while queryChildAge.next():
            record = queryChildAge.record()
            if self.numberChildren(0,17,record):
                number0_17 += forceInt(record.value('count_client_id'))
            if self.numberChildren(0,4,record):
                number0_4 += forceInt(record.value('count_client_id'))
            if self.numberChildren(5,9,record):
                number5_9 += forceInt(record.value('count_client_id'))
            if self.numberChildren(10,14,record):
                number10_14 += forceInt(record.value('count_client_id'))
            if self.numberChildren(15,17,record):
                number15_17 += forceInt(record.value('count_client_id'))

        # now text
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        pf = QtGui.QTextCharFormat()

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(bf)
        cursor.insertText('1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Число несовершеннолетних (далее - дети), подлежащих профилактическим медицинским осмотрам в отчетном периоде:\n')
        cursor.setCharFormat(bf)
        cursor.insertText('\t1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'всего в возрасте от 0 до 17 лет включительно: ________ (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t1.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 0 до 4 лет включительно ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t1.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 5 до 9 лет включительно ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t1.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 10 до 14 лет включительно ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t1.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 15 до 17 лет включительно ________ (человек).\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Число детей, прошедших профилактические медицинские осмотры (далее - профилактические осмотры) в отчетном периоде (от п.1.):\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t2.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Всего в возрасте от 0 до 17 лет включительно: ')
        cursor.insertText(forceString(number0_17))
        cursor.insertText(u' (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t2.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 0 до 4 лет включительно ')
        cursor.insertText(forceString(number0_4))
        cursor.insertText(u' (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t2.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 5 до 9 лет включительно ')
        cursor.insertText(forceString(number5_9))
        cursor.insertText(u' (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t2.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 10 до 14 лет включительно ')
        cursor.insertText(forceString(number10_14))
        cursor.insertText(u' (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t2.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'в возрасте от 15 до 17 лет включительно ')
        cursor.insertText(forceString(number15_17))
        cursor.insertText(u' (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Причины невыполнения плана профилактических осмотров в отчетном периоде:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'всего не прошли ________ (человек), ________ (удельный вес от п. 1.1.), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не явились ________ (человек), ________ (удельный вес от п.3.1.);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'отказались от медицинского вмешательства ________ (человек), ________ (удельный вес от п.3.1.);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'смена места жительства ________ (человек), ________ (удельный вес от п.3.1.);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не в полном объеме ________ (человек), ________ (удельный вес от п.3.1.);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'проблемы организации медицинской помощи ________ (человек), ________ (удельный вес от п.3.1.);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t3.1.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'прочие (указать причину сколько человек):\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t3.1.6.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'________(причина)________(человек), _________ (удельный вес от п.3.1.),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t3.1.6.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'________(причина)_________(человек), ________ (удельный вес от п.3.1.) и т.д.\n')

        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 0 до 4 лет включительно\n')

        tableColumns = [
            ( '2%', [u'№ п/п', u'', u'1'], CReportBase.AlignLeft),
            ( '30%', [u'Наименование заболеваний (по классам и отдельным нозологиям)', u'', u'2'], CReportBase.AlignCenter),
            ( '4%', [u'Код по МКБ', u'', u'3'], CReportBase.AlignCenter),
            ( '8%', [u'Всего зарегистрировано заболеваний', u'', u'4'], CReportBase.AlignRight),
            ( '8%', [u'в том числе у мальчиков (из графы 4)', u'', u'5'], CReportBase.AlignRight),
            ( '8%', [u'Выявлено впервые (из графы 4)', u'', u'6'], CReportBase.AlignRight),
            ( '8%', [u'в тои числе у мальчиков (из графы 6)', u'', u'7'], CReportBase.AlignRight),
            ( '8%', [u'Состоит под диспансерным наблюдением на конец отчетного периода', u'Всего', u'8'], CReportBase.AlignRight),
            ( '8%', [u'', u'в том числе мальчиков (из графы 8)', u'9'], CReportBase.AlignRight),
            ( '8%', [u'', u'взято по результатам данного осмотра (из графы 8)', u'10'], CReportBase.AlignRight),
            ( '8%', [u'', u'в том числе мальчиков (из графы 10)', u'11'], CReportBase.AlignRight),
        ]

        rowSize = 11
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 5 до 9 лет включительно\n')

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet2)):
            row = self.resultSet2[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])


        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 10 до 14 лет включительно\n')

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet3)):
            row = self.resultSet3[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n7. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 15 до 17 лет включительно\n')

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet4)):
            row = self.resultSet4[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n8. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 0 до 14 лет включительно\n')

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet5)):
            row = self.resultSet5[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n9. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Структура выявленных заболеваний (состояний) у детей в возрасте от 0 до 17 лет включительно\n')

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 1, 4)

        for z in range(len(self.resultSet6)):
            row = self.resultSet6[z]
            i = table.addRow()
            for j in range(rowSize):
                table.setText(i, j, row[j])

        return doc

class CReportResultAdditionalConsultation(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''10. Результаты   дополнительных  консультаций,  исследований,  лечения  и
            медицинской  реабилитации  детей по результатам проведения профилактических
            осмотров в отчетном году''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'от 0 до 4 лет включительно',
                          u'от 5 до 9 лет включительно',
                          u'от 10 до 14 лет включительно',
                          u'от 15 до 17 лет включительно']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet2 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.resultSet3 = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet4 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.resultSet5 = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet6 = [[strName[0], 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0]]

        self.resultSet7 = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet8 = [[strName[0], 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '15%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Нуждались в дополнительных консультациях и исследованиях в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'2'], CReportBase.AlignRight),
            ( '20%', [u'', u'в муниципальных медицинских организациях', u'3'], CReportBase.AlignRight),
            ( '20%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'4'], CReportBase.AlignRight),
            ( '20%', [u'', u'в государственных (федеральных) медицинских организациях', u'5'], CReportBase.AlignRight),
            ( '20%', [u'', u'в частных медицинских организациях', u'6'], CReportBase.AlignRight)
        ]

        tableColumns2 = [
            ( '10%', [u'Возраст детей', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Прошли дополнительные консультации и исследования в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'% (из гр. 2 п. 10.1)', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'в муниципальных медицинских организациях', u'абс.', u'4'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 3 п. 10.1)', u'5'], CReportBase.AlignRight),
            ( '10%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'абс.', u'6'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 4 п. 10.1)', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'в государственных (федеральных) медицинских организациях', u'абс.', u'8'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 5 п. 10.1)', u'9'], CReportBase.AlignRight),
            ( '10%', [u'', u'в частных медицинских организациях', u'абс.', u'10'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 6 п. 10.1)', u'11'], CReportBase.AlignRight)
        ]

        tableColumns3 = [
            ( '15%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Рекомендованое лечение в стационарных условиях (человек)', u'Всего', u'2'], CReportBase.AlignRight),
            ( '16%', [u'', u'в муниципальных медицинских организациях', u'3'], CReportBase.AlignRight),
            ( '16%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'4'], CReportBase.AlignRight),
            ( '16%', [u'', u'в государственных (федеральных) медицинских организациях', u'5'], CReportBase.AlignRight),
            ( '16%', [u'', u'в частных медицинских организациях', u'6'], CReportBase.AlignRight),
            ( '16%', [u'', u'в санаторно-курортных организациях', u'7'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        pf = QtGui.QTextCharFormat()

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Нуждались в дополнительных консультациях и исследованиях в амбулаторных условиях и в условиях дневного стационара\n')

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Прошли дополнительные консультации и исследования в амбулаторных условиях и в условиях дневного стационара\n')

        table = createTable(cursor, tableColumns2)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)

        for z in range(len(self.resultSet2)):
            row = self.resultSet2[z]
            i = table.addRow()
            for j in range(11):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Нуждались в дополнительных консультациях и исследованиях в стационарных условиях\n')
        tableColumns[1] = ( '5%', [u'Нуждались в дополнительных консультациях и исследованиях в стационарных условиях (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet3)):
            row = self.resultSet3[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Прошли дополнительные консультации и исследования в стационарных условиях\n')
        tableColumns2[1] = ( '5%', [u'Прошли дополнительные консультации и исследования в стационарных условиях (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight)
        tableColumns2[2] = ( '5%', [u'', u'', u'% (из гр. 2 п. 10.3)', u'3'], CReportBase.AlignRight)
        tableColumns2[4] = ( '10%', [u'', u'', u'% (из гр. 3 п. 10.3)', u'5'], CReportBase.AlignRight)
        tableColumns2[6] = ( '10%', [u'', u'', u'% (из гр. 4 п. 10.3)', u'7'], CReportBase.AlignRight)
        tableColumns2[8] = ( '10%', [u'', u'', u'% (из гр. 5 п. 10.3)', u'9'], CReportBase.AlignRight)
        tableColumns2[10] = ( '10%', [u'', u'', u'% (из гр. 6 п. 10.3)', u'11'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns2)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)

        for z in range(len(self.resultSet4)):
            row = self.resultSet4[z]
            i = table.addRow()
            for j in range(11):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендовано лечение в амбулаторных условиях дневного стационара\n')
        tableColumns[1] = ( '5%', [u'Рекомендовано лечение в амбулаторных условиях дневного стационара (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet5)):
            row = self.resultSet5[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендовано лечение в стационарных условиях\n')

        table = createTable(cursor, tableColumns3)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 6)

        for z in range(len(self.resultSet6)):
            row = self.resultSet6[z]
            i = table.addRow()
            for j in range(7):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.7. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендована медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара\n')
        tableColumns[1] = ( '5%', [u'Рекомендована медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet7)):
            row = self.resultSet7[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n10.8. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендованы медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях\n')
        tableColumns3[1] = ( '5%', [u'Рекомендованы медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns3)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 6)

        for z in range(len(self.resultSet8)):
            row = self.resultSet8[z]
            i = table.addRow()
            for j in range(7):
                table.setText(i, j, row[j])

        return doc

class CReportResultMedicationBeforeInspection(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''Результаты   лечения, медицинской реабилитация и (или) санаторно-курортного лечения детей до проведения настоящего профилактического осмотра''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'от 0 до 4 лет включительно',
                          u'от 5 до 9 лет включительно',
                          u'от 10 до 14 лет включительно',
                          u'от 15 до 17 лет включительно']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet2 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.resultSet3 = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet4 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.resultSet5 = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        self.resultSet6 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.resultSet7 = [[strName[0], 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0]]

        self.resultSet8 = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '15%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Рекомендовано лечение в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'2'], CReportBase.AlignRight),
            ( '20%', [u'', u'в муниципальных медицинских организациях', u'3'], CReportBase.AlignRight),
            ( '20%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'4'], CReportBase.AlignRight),
            ( '20%', [u'', u'в государственных (федеральных) медицинских организациях', u'5'], CReportBase.AlignRight),
            ( '20%', [u'', u'в частных медицинских организациях', u'6'], CReportBase.AlignRight)
        ]

        tableColumns2 = [
            ( '10%', [u'Возраст детей', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Проведено лечение в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'% (из гр. 2 п. 11.1)', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'в муниципальных медицинских организациях', u'абс.', u'4'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 3 п. 11.1)', u'5'], CReportBase.AlignRight),
            ( '10%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'абс.', u'6'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 4 п. 11.1)', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'в государственных (федеральных) медицинских организациях', u'абс.', u'8'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 5 п. 11.1)', u'9'], CReportBase.AlignRight),
            ( '10%', [u'', u'в частных медицинских организациях', u'абс.', u'10'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'% (из гр. 6 п. 11.1)', u'11'], CReportBase.AlignRight)
        ]

        tableColumns3 = [
            ( '10%', [u'Возраст детей', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Проведено лечение в стационарных условиях (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight),
            ( '5%', [u'', u'', u'% (из гр. 2 п. 11.4)', u'3'], CReportBase.AlignRight),
            ( '8%', [u'', u'в муниципальных медицинских организациях', u'абс.', u'4'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'% (из гр. 3 п. 11.4)', u'5'], CReportBase.AlignRight),
            ( '8%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'абс.', u'6'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'% (из гр. 4 п. 11.4)', u'7'], CReportBase.AlignRight),
            ( '8%', [u'', u'в государственных (федеральных) медицинских организациях', u'абс.', u'8'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'% (из гр. 5 п. 11.4)', u'9'], CReportBase.AlignRight),
            ( '8%', [u'', u'в частных медицинских организациях', u'абс.', u'10'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'% (из гр. 6 п. 11.4)', u'11'], CReportBase.AlignRight),
            ( '8%', [u'', u'в санаторно-курортных организациях', u'абс.', u'12'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'% (из гр. 7 п. 11.4)', u'13'], CReportBase.AlignRight)
        ]

        tableColumns4 = [
            ( '15%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '5%', [u'Рекомендована медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях (человек)', u'Всего', u'2'], CReportBase.AlignRight),
            ( '16%', [u'', u'в муниципальных медицинских организациях', u'3'], CReportBase.AlignRight),
            ( '16%', [u'', u'в государственных (субъекта Российской Федерации) медицинских организациях', u'4'], CReportBase.AlignRight),
            ( '16%', [u'', u'в государственных (федеральных) медицинских организациях', u'5'], CReportBase.AlignRight),
            ( '16%', [u'', u'в частных медицинских организациях', u'6'], CReportBase.AlignRight),
            ( '16%', [u'', u'в санаторно-курортных организациях', u'7'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        pf = QtGui.QTextCharFormat()

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендовано лечение в амбулаторных условиях и в условиях дневного стационара\n')

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Проведено лечение в амбулаторных условиях и в условиях дневного стационара\n')

        table = createTable(cursor, tableColumns2)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)

        for z in range(len(self.resultSet2)):
            row = self.resultSet2[z]
            i = table.addRow()
            for j in range(11):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Причины невыполнения рекомендаций по лечению в амбулаторных условиях и в условиях дневного стационара:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не прошли всего: ________ (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не явились ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'отказались от медицинского вмешательства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'смена места жительства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не в полном объёме ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'проблемы организации медицинской помощи ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.3.1.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'прочие (указать причину, сколько человек:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.3.1.6.1 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'___________________ (причина) ___________ (человек);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.3.1.6.2 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'_______________ (причина) _________ (человек) и т.д.\n')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендовано лечение в стационарных условиях\n')
        tableColumns[1] = ( '5%', [u'Рекомендовано лечение в стационарных условиях (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet3)):
            row = self.resultSet3[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Проведено лечение в стационарных условиях\n')

        table = createTable(cursor, tableColumns3)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 12)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)
        table.mergeCells(1, 11, 1, 2)

        for z in range(len(self.resultSet4)):
            row = self.resultSet4[z]
            i = table.addRow()
            for j in range(13):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Причины невыполнения рекомендаций по лечению в стационарных условиях:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не прошли всего: ________ (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не явились ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'отказались от медицинского вмешательства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'смена места жительства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не в полном объёме ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'проблемы организации медицинской помощи ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.6.1.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'прочие (указать причину, сколько человек:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.6.1.6.1 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'___________________ (причина) ___________ (человек);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.6.1.6.2 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'_______________ (причина) _________ (человек) и т.д.\n')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.7. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендована медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара\n')
        tableColumns[1] = ( '5%', [u'Рекомендована медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'2'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 5)

        for z in range(len(self.resultSet5)):
            row = self.resultSet5[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.8. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Проведена медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара\n')
        tableColumns2[1] = ( '5%', [u'Проведена медицинская реабилитация в амбулаторных условиях и в условиях дневного стационара (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight)
        tableColumns2[2] = ( '5%', [u'', u'', u'% (из гр. 2 п. 11.7)', u'3'], CReportBase.AlignRight)
        tableColumns2[4] = ( '10%', [u'', u'', u'% (из гр. 3 п. 11.7)', u'5'], CReportBase.AlignRight)
        tableColumns2[6] = ( '10%', [u'', u'', u'% (из гр. 4 п. 11.7)', u'7'], CReportBase.AlignRight)
        tableColumns2[8] = ( '10%', [u'', u'', u'% (из гр. 5 п. 11.7)', u'9'], CReportBase.AlignRight)
        tableColumns2[10] = ( '10%', [u'', u'', u'% (из гр. 6 п. 11.7)', u'11'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns2)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)

        for z in range(len(self.resultSet6)):
            row = self.resultSet6[z]
            i = table.addRow()
            for j in range(11):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.9. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Причины невыполнения рекомендаций по медицинской реабилитации в амбулаторных условиях и в условиях дневного стационара:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не прошли всего: ________ (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не явились ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'отказались от медицинского вмешательства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'смена места жительства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не в полном объёме ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'проблемы организации медицинской помощи ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.9.1.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'прочие (указать причину, сколько человек:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.9.1.6.1 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'___________________ (причина) ___________ (человек);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.9.1.6.2 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'_______________ (причина) _________ (человек) и т.д.\n')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.10. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Рекомендованы медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях\n')

        table = createTable(cursor, tableColumns4)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 6)

        for z in range(len(self.resultSet7)):
            row = self.resultSet7[z]
            i = table.addRow()
            for j in range(7):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.11. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Проведена медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях\n')
        tableColumns3[1] = ( '5%', [u'Проведена медицинская реабилитация и (или) санаторно-курортное лечение в стационарных условиях (человек)', u'Всего', u'абс.', u'2'], CReportBase.AlignRight)
        tableColumns3[2] = ( '5%', [u'', u'', u'% (из гр. 2 п. 11.10)', u'3'], CReportBase.AlignRight)
        tableColumns3[4] = ( '8%', [u'', u'', u'% (из гр. 3 п. 11.10)', u'5'], CReportBase.AlignRight)
        tableColumns3[6] = ( '8%', [u'', u'', u'% (из гр. 4 п. 11.10)', u'7'], CReportBase.AlignRight)
        tableColumns3[8] = ( '8%', [u'', u'', u'% (из гр. 5 п. 11.10)', u'9'], CReportBase.AlignRight)
        tableColumns3[10] = ( '8%', [u'', u'', u'% (из гр. 6 п. 11.10)', u'11'], CReportBase.AlignRight)
        tableColumns3[12] = ( '8%', [u'', u'', u'% (из гр. 7 п. 11.10)', u'13'], CReportBase.AlignRight)

        table = createTable(cursor, tableColumns3)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 1, 2)
        table.mergeCells(1, 3, 1, 2)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(1, 9, 1, 2)

        for z in range(len(self.resultSet8)):
            row = self.resultSet8[z]
            i = table.addRow()
            for j in range(11):
                table.setText(i, j, row[j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n11.12. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Причины невыполнения рекомендаций по медицинской реабилитации и (или) санаторно-курортному лечению в стационарных условиях:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не прошли всего: ________ (человек), из них:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не явились ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'отказались от медицинского вмешательства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.3. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'смена места жительства ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.4. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'не в полном объёме ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.5. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'проблемы организации медицинской помощи ________ (человек),\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t11.12.1.6. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'прочие (указать причину, сколько человек:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.12.1.6.1 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'___________________ (причина) ___________ (человек);\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t\t11.12.1.6.2 ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'_______________ (причина) _________ (человек) и т.д.\n')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(bf)
        cursor.insertText(u'\n\n12. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'Оказание высокотехнологичной медицинской помощи:\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t12.1. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'рекомендована  (по  итогам  настоящих осмотров): _______________ чел., в том числе _______________ мальчикам;\n')
        cursor.setCharFormat(bf)
        cursor.insertText(u'\t12.2. ')
        cursor.setCharFormat(pf)
        cursor.insertText(u'оказана  (по  итогам осмотров в предыдущем году) _______________ чел., в том числе _______________ мальчикам.\n')

        return doc

class CReportNumberChildrenDisabilities(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''13. Число детей-инвалидов из числа детей, прошедших профилактические осмотры в отчетном периоде''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'от 0 до 4 лет включительно',
                          u'от 5 до 9 лет включительно',
                          u'от 10 до 14 лет включительно',
                          u'от 15 до 17 лет включительно']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '20%', [u'Возраст детей', u'', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '10%', [u'Инвалидность', u'установлена до проведения настоящего осмотра', u'с рождения', u'всего (человек)', u'2'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'', u'процент от общего числа прошедших осмотры', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'приобретённая', u'всего (человек)', u'4'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'', u'процент от общего числа прошедших осмотры', u'5'], CReportBase.AlignRight),
            ( '10%', [u'', u'установлена впервые в отчётном периоде', u'', u'всего (человек)', u'6'], CReportBase.AlignRight),
            ( '10%', [u'', u'', u'', u'процент от общего числа прошедших осмотры', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'всего детей-инвалидов (человек)', u'', u'', u'8'], CReportBase.AlignRight),
            ( '10%', [u'', u'процент детей-инвалидов от общего числа прошедших осмотры', u'', u'', u'9'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 1, 8)
        table.mergeCells(1, 1, 1, 4)
        table.mergeCells(1, 5, 2, 2)
        table.mergeCells(1, 7, 3, 1)
        table.mergeCells(1, 8, 3, 1)
        table.mergeCells(2, 1, 1, 2)
        table.mergeCells(2, 3, 1, 2)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(9):
                table.setText(i, j, row[j])

        return doc

class CReportIndividualProgram(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''14. Выполнение индивидуальных программ реабилитации (ИПР) детей-инвалидов в отчетном периоде''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'от 0 до 4 лет включительно',
                          u'от 5 до 9 лет включительно',
                          u'от 10 до 14 лет включительно',
                          u'от 15 до 17 лет включительно']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '10%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '10%', [u'Назначено ИПР', u'всего (человек)', u'2'], CReportBase.AlignRight),
            ( '10%', [u'ИПР выполнена полностью', u'всего (человек)', u'3'], CReportBase.AlignRight),
            ( '10%', [u'', u'процент от назначенного (%)', u'4'], CReportBase.AlignRight),
            ( '10%', [u'ИПР выполнена частично', u'всего (человек)', u'5'], CReportBase.AlignRight),
            ( '10%', [u'', u'процент от назначенного (%)', u'6'], CReportBase.AlignRight),
            ( '10%', [u'ИПР начата', u'всего (человек)', u'7'], CReportBase.AlignRight),
            ( '10%', [u'', u'процент от назначенного (%)', u'8'], CReportBase.AlignRight),
            ( '10%', [u'ИПР не выполнена', u'всего (человек)', u'9'], CReportBase.AlignRight),
            ( '10%', [u'', u'процент от назначенного (%)', u'10'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 8, 1, 2)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(10):
                table.setText(i, j, row[j])

        return doc

class CReportImmunizations(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''15. Охват профилактическими прививками в отчетном периоде''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'от 0 до 4 лет включительно',
                          u'от 5 до 9 лет включительно',
                          u'от 10 до 14 лет включительно',
                          u'от 15 до 17 лет включительно']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '10%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '30%', [u'Привито в соответствии с национальным календарём профилактических прививок (человек)', u'', u'2'], CReportBase.AlignRight),
            ( '15%', [u'Не привиты по медицинским показаниям', u'полностью (человек)', u'3'], CReportBase.AlignRight),
            ( '15%', [u'', u'частично (человек)', u'4'], CReportBase.AlignRight),
            ( '15%', [u'Не привиты по другим причинам', u'полностью (человек)', u'5'], CReportBase.AlignRight),
            ( '15%', [u'', u'частично (человек)', u'6'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 1, 2)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(6):
                table.setText(i, j, row[j])

        return doc

class CReportUnderagePhysicalDevelopment(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''16. Распределение детей по уровню физического развития''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 0 до 4 лет включительно',
                          u'в том числе мальчиков',
                          u'от 5 до 9 лет включительно',
                          u'в том числе мальчиков',
                          u'от 10 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 15 до 17 лет включительно',
                          u'в том числе мальчиков']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0],
                          [strName[6], 0, 0, 0, 0, 0, 0],
                          [strName[7], 0, 0, 0, 0, 0, 0],
                          [strName[8], 0, 0, 0, 0, 0, 0],
                          [strName[9], 0, 0, 0, 0, 0, 0],
                          [strName[10], 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '20%', [u'Возраст детей', u'', u'1'], CReportBase.AlignLeft),
            ( '20%', [u'Число прошедших осмотры в отчётном периоде (человек)', u'', u'2'], CReportBase.AlignRight),
            ( '20%', [u'Нормально физическое развитие (человек) (из графы 2)', u'', u'3'], CReportBase.AlignRight),
            ( '10%', [u'Нарушения физического развития (человек) (из графы 2)', u'дефицит массы тела', u'4'], CReportBase.AlignRight),
            ( '10%', [u'', u'избыток массы тела', u'5'], CReportBase.AlignRight),
            ( '10%', [u'', u'низкий рост', u'6'], CReportBase.AlignRight),
            ( '10%', [u'', u'высокий рост', u'7'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 4)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(7):
                table.setText(i, j, row[j])

        return doc

class CReportMedicalGroups(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''17. Распределение детей по медицинским группам для занятий физической культурой''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setSpecialityVisible(False)
        result.setTitle(self.title())
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 0 до 4 лет включительно',
                          u'в том числе мальчиков',
                          u'от 5 до 9 лет включительно',
                          u'в том числе мальчиков',
                          u'от 10 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 15 до 17 лет включительно',
                          u'в том числе мальчиков']

        self.resultSet = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[6], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[7], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[8], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[9], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[10], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '10%', [u'Возраст детей', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '10%', [u'Число прошедших профилактические осмотры в отчётном периоде (человек)', u'', u'2'], CReportBase.AlignRight),
            ( '8%', [u'Медицинская группа для занятия физической культурой', u'По результатам ранее проведённых медицинских осмотров (человек)', u'I', u'3'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'II', u'4'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'III', u'5'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'IV', u'6'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'не допущен', u'7'], CReportBase.AlignRight),
            ( '8%', [u'', u'По результатам профилактических осмотров в данном отчётном периоде (человек)', u'I', u'8'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'II', u'9'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'III', u'10'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'IV', u'11'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'не допущен', u'12'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 10)
        table.mergeCells(1, 2, 1, 5)
        table.mergeCells(1, 7, 1, 5)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(12):
                table.setText(i, j, row[j])

        return doc

def selectDataHealthGroups(params):
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    orgStructureId = params.get('orgStructureId')
    orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
    specialityId = params.get('specialityId', None)
    eventTypeId = params.get('eventTypeId', None)
    eventType = u'80/4'

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableHealthGroup = db.table('rbHealthGroup')
    tableEventEarlier = db.table('Event').alias('eventEarlier')
    tableEventTypeEarlier = db.table('EventType').alias('eventTypeEarlier')
    tableDiagnosticEarlier = db.table('Diagnostic').alias('diagnosticEarlier')
    tableDiagnosisTypeEarlier = db.table('rbDiagnosisType').alias('diagnosisTypeEarlier')
    tableHealthGroupEarlier = db.table('rbHealthGroup').alias('healthGroupEarlier')

    queryTable = tableClient.innerJoin(tableEvent, db.joinAnd([tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTable = queryTable.innerJoin(tableDiagnostic, db.joinAnd([tableDiagnostic['event_id'].eq(tableEvent['id']), tableDiagnostic['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableDiagnosis, db.joinAnd([tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableDiagnosisType, db.joinAnd([tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']), tableDiagnosisType['code'].inlist(['1', '2'])]))
    queryTable = queryTable.innerJoin(tableHealthGroup, tableHealthGroup['id'].eq(tableDiagnostic['healthGroup_id']))
    queryTable = queryTable.leftJoin(tableEventEarlier, db.joinAnd([tableEventEarlier['deleted'].eq(0), tableEventEarlier['client_id'].eq(tableClient['id']), tableEventEarlier['execDate'].ge(begDate) if begDate else '1', tableEventEarlier['execDate'].lt(endDate.addDays(1)) if endDate else '1']))
    queryTable = queryTable.leftJoin(tableDiagnosticEarlier, db.joinAnd([tableDiagnosticEarlier['event_id'].eq(tableEventEarlier['id']), tableDiagnosticEarlier['deleted'].eq(0)]))
    queryTable = queryTable.leftJoin(tableDiagnosisTypeEarlier, db.joinAnd([tableDiagnosisTypeEarlier['id'].eq(tableDiagnosticEarlier['diagnosisType_id']), tableDiagnosisTypeEarlier['code'].inlist(['1', '2'])]))
    queryTable = queryTable.leftJoin(tableHealthGroupEarlier, tableHealthGroupEarlier['id'].eq(tableDiagnosticEarlier['healthGroup_id']))
    cols = [
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17, Client.id, NULL)) AS clientAll017',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI017',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII017',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII017',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI017Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII017Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 17 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII017Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14, Client.id, NULL)) AS clientAll014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI014Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII014Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII014Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1, Client.id, NULL)) AS clientAll014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI014MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII014MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII014MEarlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4, Client.id, NULL)) AS clientAll04',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI04',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII04',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII04',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI04Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII04Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII04Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1, Client.id, NULL)) AS clientAll04M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI04M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII04M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII04M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI04MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII04MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) <= 4 AND Client.sex = 1 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII04MEarlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9, Client.id, NULL)) AS clientAll59',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI59',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII59',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII59',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI59Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII59Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII59Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1, Client.id, NULL)) AS clientAll59M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI59M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII59M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII59M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI59MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII59MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 5 AND age(Client.birthDate, Event.setDate) <= 9 AND Client.sex = 1 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII59MEarlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14, Client.id, NULL)) AS clientAll1014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI1014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII1014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII1014',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI1014Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII1014Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII1014Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1, Client.id, NULL)) AS clientAll1014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI1014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII1014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII1014M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI1014MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII1014MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 10 AND age(Client.birthDate, Event.setDate) <= 14 AND Client.sex = 1 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII1014MEarlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17, Client.id, NULL)) AS clientAll1517',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI1517',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII1517',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII1517',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI1517Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII1517Earlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII1517Earlier',

        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1, Client.id, NULL)) AS clientAll1517M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND rbHealthGroup.code = 1, Client.id, NULL)) AS clientI1517M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND rbHealthGroup.code = 2, Client.id, NULL)) AS clientII1517M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND (rbHealthGroup.code = 3 OR rbHealthGroup.code = 4 OR rbHealthGroup.code = 5), Client.id, NULL)) AS clientIII1517M',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND healthGroupEarlier.code = 1, Client.id, NULL)) AS clientI1517MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND healthGroupEarlier.code = 2, Client.id, NULL)) AS clientII1517MEarlier',
        'COUNT(DISTINCT IF(age(Client.birthDate, Event.setDate) >= 15 AND age(Client.birthDate, Event.setDate) <= 17 AND Client.sex = 1 AND (healthGroupEarlier.code = 3 OR healthGroupEarlier.code = 4 OR healthGroupEarlier.code = 5), Client.id, NULL)) AS clientIII1517MEarlier'
    ]

    group = []

    cond = []

    cond.append('age(Client.birthDate, Event.setDate) <= 17')
    addDateInRange(cond, tableEvent['execDate'], begDate, endDate)

    if orgStructureId:
        tablePerson = db.table('Person')
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableDiagnosis['person_id']))
        orgStructureIdList = getOrgStructureDescendants(orgStructureId)
        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if orgStructureAttachTypeId:
        tableClientAttach = db.table('ClientAttach')
        attachTypeId1 = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
        attachTypeId2 = forceRef(db.translate('rbAttachType', 'code', u'2', 'id'))
        queryTable = queryTable.leftJoin(tableClientAttach, '''ClientAttach.client_id = Client.id AND ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                FROM ClientAttach clAttach
                                                                                                                WHERE (clAttach.attachType_id = %s OR clAttach.attachType_id = %s)
                                                                                                                AND clAttach.client_id = Client.id)''' % (attachTypeId1, attachTypeId2))
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
        cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
        cond.append(db.joinOr([tableEventEarlier['id'].isNull(), tableEventEarlier['eventType_id'].eq(eventTypeId)]))

    else:
        queryTable = queryTable.innerJoin(tableEventType, db.joinAnd([tableEventType['deleted'].eq(0), tableEventType['id'].eq(tableEvent['eventType_id']), tableEventType['code'].like(eventType)]))
        queryTable = queryTable.leftJoin(tableEventTypeEarlier, db.joinAnd([tableEventTypeEarlier['deleted'].eq(0), tableEventTypeEarlier['id'].eq(tableEventEarlier['eventType_id']), tableEventTypeEarlier['code'].like(eventType)]))

    if specialityId:
        tableExecPerson = db.table('Person').alias('EventExecPerson')
        queryTable = queryTable.innerJoin(tableExecPerson, tableExecPerson['id'].eq(tableEvent['execPerson_id']))
        cond.append(tableExecPerson['speciality_id'].eq(specialityId))

    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)

class CReportHealthGroups(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'''18. Распределение детей по группам состояния здоровья''')

    def getSetupDialog(self, parent):
        result = CReportUnderageMedicalExaminationSetupDialog(parent)
        result.setTitle(self.title())
        result.setAttendantVisible(False)
        return result

    def build(self, params):
        strName = [u'Всего детей в возрасте до 17 лет включительно, из них:',
                          u'от 0 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 0 до 4 лет включительно',
                          u'в том числе мальчиков',
                          u'от 5 до 9 лет включительно',
                          u'в том числе мальчиков',
                          u'от 10 до 14 лет включительно',
                          u'в том числе мальчиков',
                          u'от 15 до 17 лет включительно',
                          u'в том числе мальчиков']
        query = selectDataHealthGroups(params)
        if query.next():
            record = query.record()
            self.resultSet = [[strName[0], forceInt(record.value('clientAll017')), forceInt(record.value('clientI017')), forceInt(record.value('clientII017')), forceInt(record.value('clientIII017')), 0, 0, forceInt(record.value('clientI017Earlier')), forceInt(record.value('clientII017Earlier')), forceInt(record.value('clientIII017Earlier')), 0, 0],
                          [strName[1], forceInt(record.value('clientAll014')), forceInt(record.value('clientI014')), forceInt(record.value('clientII014')), forceInt(record.value('clientIII014')), 0, 0, forceInt(record.value('clientI014Earlier')), forceInt(record.value('clientII014Earlier')), forceInt(record.value('clientIII014Earlier')), 0, 0],
                          [strName[2], forceInt(record.value('clientAll014M')), forceInt(record.value('clientI014M')), forceInt(record.value('clientII014M')), forceInt(record.value('clientIII014M')), 0, 0, forceInt(record.value('clientI014MEarlier')), forceInt(record.value('clientII014MEarlier')), forceInt(record.value('clientIII014MEarlier')), 0, 0],
                          [strName[3], forceInt(record.value('clientAll04')), forceInt(record.value('clientI04')), forceInt(record.value('clientII04')), forceInt(record.value('clientIII04')), 0, 0, forceInt(record.value('clientI04Earlier')), forceInt(record.value('clientII04Earlier')), forceInt(record.value('clientIII04Earlier')), 0, 0],
                          [strName[4], forceInt(record.value('clientAll04M')), forceInt(record.value('clientI04M')), forceInt(record.value('clientII04M')), forceInt(record.value('clientIII04M')), 0, 0, forceInt(record.value('clientI04MEarlier')), forceInt(record.value('clientII04MEarlier')), forceInt(record.value('clientIII04MEarlier')), 0, 0],
                          [strName[5], forceInt(record.value('clientAll59')), forceInt(record.value('clientI59')), forceInt(record.value('clientII59')), forceInt(record.value('clientIII59')), 0, 0, forceInt(record.value('clientI59Earlier')), forceInt(record.value('clientII59Earlier')), forceInt(record.value('clientIII59Earlier')), 0, 0],
                          [strName[6], forceInt(record.value('clientAll59M')), forceInt(record.value('clientI59M')), forceInt(record.value('clientII59M')), forceInt(record.value('clientIII59M')), 0, 0, forceInt(record.value('clientI59MEarlier')), forceInt(record.value('clientII59MEarlier')), forceInt(record.value('clientIII59MEarlier')), 0, 0],
                          [strName[7], forceInt(record.value('clientAll1014')), forceInt(record.value('clientI1014')), forceInt(record.value('clientII1014')), forceInt(record.value('clientIII1014')), 0, 0, forceInt(record.value('clientI1014Earlier')), forceInt(record.value('clientII1014Earlier')), forceInt(record.value('clientIII1014Earlier')), 0, 0],
                          [strName[8], forceInt(record.value('clientAll1014M')), forceInt(record.value('clientI1014M')), forceInt(record.value('clientII1014M')), forceInt(record.value('clientIII1014M')), 0, 0, forceInt(record.value('clientI1014MEarlier')), forceInt(record.value('clientII1014MEarlier')), forceInt(record.value('clientIII1014MEarlier')), 0, 0],
                          [strName[9], forceInt(record.value('clientAll1517')), forceInt(record.value('clientI1517')), forceInt(record.value('clientII1517')), forceInt(record.value('clientIII1517')), 0, 0, forceInt(record.value('clientI1517Earlier')), forceInt(record.value('clientII1517Earlier')), forceInt(record.value('clientIII1517Earlier')), 0, 0],
                          [strName[10], forceInt(record.value('clientAll1517M')), forceInt(record.value('clientI1517M')), forceInt(record.value('clientII1517M')), forceInt(record.value('clientIII1517M')), 0, 0, forceInt(record.value('clientI1517MEarlier')), forceInt(record.value('clientII1517MEarlier')), forceInt(record.value('clientIII1517MEarlier')), 0, 0]]
        else:
            self.resultSet = [[strName[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[3], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[4], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[5], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[6], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[7], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[8], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[9], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                          [strName[10], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        tableColumns = [
            ( '10%', [u'Возраст детей', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '10%', [u'Число прошедших профилактические осмотры в отчётном периоде (человек)', u'', u'2'], CReportBase.AlignRight),
            ( '8%', [u'Группы состояния здоровья', u'По результатам ранее проведённых медицинских осмотров (человек)', u'I', u'3'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'II', u'4'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'III', u'5'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'IV', u'6'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'не допущен', u'7'], CReportBase.AlignRight),
            ( '8%', [u'', u'По результатам профилактических осмотров в данном отчётном периоде (человек)', u'I', u'8'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'II', u'9'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'III', u'10'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'IV', u'11'], CReportBase.AlignRight),
            ( '8%', [u'', u'', u'не допущен', u'12'], CReportBase.AlignRight)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        cursor.insertText(u'подразделение: ' + getOrgStructureFullName(orgStructureAttachTypeId))
        cursor.insertBlock()
        cursor.insertBlock()

        cursor.movePosition(QtGui.QTextCursor.End)

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 1, 10)
        table.mergeCells(1, 2, 1, 5)
        table.mergeCells(1, 7, 1, 5)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            for j in range(12):
                table.setText(i, j, row[j])

        return doc

class CReportUnderageMedicalExaminationSetupDialog(QtGui.QDialog, Ui_ReportUnderageMedicalExaminationSetup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)
        self.cmbSpeciality.setTable('rbSpeciality', True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.chkAttendant.setChecked(params.get('countAttendant', False))
        self.cmbOrgStructureAttachType.setValue(params.get('orgStructureAttachTypeId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['chkAttendant'] = self.chkAttendant.isChecked()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['orgStructureAttachTypeId'] = self.cmbOrgStructureAttachType.value()
        return result

    def setAttendantVisible(self, value):
        self.chkAttendant.setVisible(value)

    def setEventTypeVisible(self, value):
        self.lblEventType.setVisible(value)
        self.cmbEventType.setVisible(value)

    def setSpecialityVisible(self, value):
        self.lblSpeciality.setVisible(value)
        self.cmbSpeciality.setVisible(value)