# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceDate, forceInt, forceString
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase


def selectData(params, condition, diagnosActMKB, diagnosMKB, dead=False):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    eventTypeId = forceInt(params.get('eventTypeId'))
    personId = forceInt(params.get('personId', None))
    orgStructureId = forceInt(params.get('orgStructureId'))
    where = '''AND (%s)''' % condition
    if begDate:
        where += ''' AND DATE(Event.execDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(Event.execDate) < DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    if eventTypeId:
        where += ''' AND Event.eventType_id = %s''' % eventTypeId
    if personId:
        where += ''' AND Event.execPerson_id = %s''' % personId
    if dead:
        where += ''' AND Event.id = (SELECT MAX(eventTemp.id)
                                     FROM Event AS eventTemp
                                     WHERE eventTemp.client_id = Client.id AND eventTemp.deleted = 0)'''
    join = ''
    columnQuery = [0, 14,
                   15, 19,
                   15, 17,
                   20, 24,
                   25, 29,
                   30, 34,
                   35, 39,
                   40, 44,
                   45, 49,
                   50]
    select = '''COUNT(DISTINCT Event.id) AS countAll, '''
    j = 0
    while j < len(columnQuery) - 1:
        select += '''\nCOUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') >= %s
            AND TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') < %s, Event.id, NULL)) AS count%s, ''' % (QtCore.QDate.currentDate().toString('yyyy-MM-dd'), columnQuery[j], QtCore.QDate.currentDate().toString('yyyy-MM-dd'), columnQuery[j + 1], columnQuery[j + 1])
        j += 2
    select += '''\nCOUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') >= %s, Event.id , NULL)) AS count50 ''' % (QtCore.QDate.currentDate().toString('yyyy-MM-dd'), columnQuery[j])
    if orgStructureId:
        join += ''' \nINNER JOIN Person ON Person.id = Event.execPerson_id AND Person.orgStructure_id = %s AND Person.deleted = 0''' % orgStructureId
    if dead:
        join += ''' \nINNER JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.deleted = 0
                    INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id AND rbAttachType.code = 8'''
    stmt = u'''
        SELECT %s
        FROM Event
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
        %s
        LEFT JOIN Action AS actMain ON actMain.id = (SELECT MAX(actTempMain.id)
                                                     FROM Action AS actTempMain
                                                     WHERE actTempMain.deleted = 0
                                                     AND actTempMain.id = (SELECT MAX(actTempMainLow.id)
                                                                           FROM Action AS actTempMainLow
                                                                           INNER JOIN ActionType AS atTempMain ON atTempMain.id = actTempMainLow.actionType_id AND atTempMain.deleted = 0 AND atTempMain.flatCode LIKE 'moving'
                                                                           WHERE actTempMainLow.deleted = 0 AND actTempMainLow.event_id = Event.id)
                                                     %s)
        LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0 %s
        WHERE Event.deleted = 0 %s
    ''' % (select, join, diagnosActMKB, diagnosMKB, where)
    return db.query(stmt)


def selectData2(params, dead=False):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    eventTypeId = forceInt(params.get('eventTypeId'))
    personId = forceInt(params.get('personId', None))
    orgStructureId = forceInt(params.get('orgStructureId'))
    if dead:
        select = '''COUNT(DISTINCT IF(Event.pregnancyWeek <= 12, Event.id, NULL)) AS count1,
                    COUNT(DISTINCT IF(Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21, Event.id, NULL)) AS count2 '''
    else:
        select = '''COUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') <= 14, Event.id, NULL)) AS count14,
                    COUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') <= 13, Event.id, NULL)) AS count13,
                    COUNT(DISTINCT IF(TIMESTAMPDIFF(YEAR, Client.birthDate, '%s') <= 12, Event.id, NULL)) AS count12 ''' % (QtCore.QDate.currentDate().toString('yyyy-MM-dd'), QtCore.QDate.currentDate().toString('yyyy-MM-dd'), QtCore.QDate.currentDate().toString('yyyy-MM-dd'))
    where = ''
    if begDate:
        where += ''' AND DATE(Event.execDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(Event.execDate) < DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    if eventTypeId:
        where += ''' AND Event.eventType_id = %s''' % eventTypeId
    if personId:
        where += ''' AND Event.execPerson_id = %s ''' % personId
    if dead:
        where += ''' AND Event.id = (SELECT MAX(eventTemp.id)
                                     FROM Event AS eventTemp
                                     WHERE eventTemp.client_id = Client.id AND eventTemp.deleted = 0)'''
    join = ''
    if orgStructureId:
        join += ''' INNER JOIN Person ON Person.id = Event.execPerson_id AND Person.orgStructure_id = %s AND Person.deleted = 0''' % orgStructureId
    if dead:
        join += ''' \nINNER JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.deleted = 0
                    INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id AND rbAttachType.code = 8'''
    stmt = u'''
        SELECT %s
        FROM Event
        INNER JOIN Client ON Client.id = Event.client_id AND Client.deleted = 0
        %s
        LEFT JOIN Action AS actMain ON actMain.id = (SELECT MAX(actTempMain.id)
                                                     FROM Action AS actTempMain
                                                     WHERE actTempMain.deleted = 0
                                                     AND actTempMain.id = (SELECT MAX(actTempMainLow.id)
                                                                           FROM Action AS actTempMainLow
                                                                           INNER JOIN ActionType AS atTempMain ON atTempMain.id = actTempMainLow.actionType_id AND atTempMain.deleted = 0 AND atTempMain.flatCode LIKE 'moving'
                                                                           WHERE actTempMainLow.deleted = 0 AND actTempMainLow.event_id = Event.id)
                                                     AND (actTempMain.MKB LIKE 'O02%%'
                                                     OR actTempMain.MKB LIKE 'O03%%'
                                                     OR actTempMain.MKB LIKE 'O04%%'
                                                     OR actTempMain.MKB LIKE 'O05%%'
                                                     OR actTempMain.MKB LIKE 'O06%%'
                                                     OR actTempMain.MKB LIKE 'O07%%'))
        LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
        LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
        AND Diagnosis.deleted = 0
        AND (Diagnosis.MKB LIKE 'O02%%'
        OR Diagnosis.MKB LIKE 'O03%%'
        OR Diagnosis.MKB LIKE 'O04%%'
        OR Diagnosis.MKB LIKE 'O05%%'
        OR Diagnosis.MKB LIKE 'O06%%'
        OR Diagnosis.MKB LIKE 'O07%%')
        WHERE Event.deleted = 0 %s
    ''' % (select, join, where)
    return db.query(stmt)


class CReportF13(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о прерывании беременности \n(в сроки до 22 недель)')

    def getSetupDialog(self, parent):
        result = CReportF13SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        self.rowNameSet = [[u'Всего прерываний беременности', u'1', u'O02-O07'],
                     [u'из них:\nу первобеременных (всего)', u'1.1', u'O02-O07'],
                     [u'у ВИЧ-инфицированных женщин', u'1.2', u'O02-O07'],
                     [u'Преривыний беременности в сроки до 12 недель (всего)', u'2', u'O02-O07'],
                     [u'из них:\nсамопроизвольный аборт', u'2.1', u'O02-O03'],
                     [u'медицинский аборт (легальный)', u'2.2', u'O04-часть'],
                     [u'из них:\nв ранние срок', u'2.2.1', u''],
                     [u'из них:\nмедикаментозным методом', u'2.2.1.1', u''],
                     [u'из них:\nу первобеременных', u'2.2.1.1.1', u''],
                     [u'аборт по медицинским показаниям', u'2.3', u'О04-часть'],
                     [u'другие виды аборта (криминальный)', u'2.4', u'О05'],
                     [u'аборт неуточнённый (внебольничный)', u'2.5', u'О06'],
                     [u'Прерываний беременности в сроки 12 - 21 неделя включительно (всего)', u'3', u'О02-О03, О04-часть, О05-О07'],
                     [u'из них:\nсамопроизвольный аборт', u'3.1', u'О02, О03'],
                     [u'аборт по медицинским показаниям', u'3.2', u'О04-часть'],
                     [u'из них:\nв связи с выявленными врождёнными пороками (аномалиями) развития плода', u'3.2.1', u'О04-часть'],
                     [u'аборт по социальным показаниям', u'3.3', u''],
                     [u'другие виды аборта (криминальный)', u'3.4', u'О05'],
                     [u'аборт неуточнённый (внебольничный)', u'3.5', u'О06'],
                     [u'Число женщин, умерших после прерывания беременности (всего)', u'4', u''],
                     [u'в том числе от аборта:\nсамопроизвольного', u'4.1', u'O02-O03'],
                     [u'медицинского (легального)', u'4.2', u'О04-часть'],
                     [u'по медицинским показаниям', u'4.3', u''],
                     [u'по социальным показаниям', u'4.4', u''],
                     [u'других видов (криминального)', u'4.5', u'О05'],
                     [u'неуточнённого (внебольничного)', u'4.6', u'О06'],
                     [u'от причин, не связанных с беременностью', u'4.7', u'']]

        self.rowQuery = ['''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%' OR actTempMain.MKB LIKE 'O04%%' OR actTempMain.MKB LIKE 'O05%%' OR actTempMain.MKB LIKE 'O06%%' OR actTempMain.MKB LIKE 'O07%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%' OR Diagnosis.MKB LIKE 'O04%%' OR Diagnosis.MKB LIKE 'O05%%' OR Diagnosis.MKB LIKE 'O06%%' OR Diagnosis.MKB LIKE 'O07%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 12''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%' OR actTempMain.MKB LIKE 'O04%%' OR actTempMain.MKB LIKE 'O05%%' OR actTempMain.MKB LIKE 'O06%%' OR actTempMain.MKB LIKE 'O07%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%' OR Diagnosis.MKB LIKE 'O04%%' OR Diagnosis.MKB LIKE 'O05%%' OR Diagnosis.MKB LIKE 'O06%%' OR Diagnosis.MKB LIKE 'O07%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 12''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 12''',
                         '''AND actTempMain.MKB LIKE 'O04%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O04%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 4''',
                         '''AND actTempMain.MKB LIKE 'O04%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O04%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 12''',
                         '''AND actTempMain.MKB LIKE 'O05%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O05%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 12''',
                         '''AND actTempMain.MKB LIKE 'O06%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O06%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%' OR actTempMain.MKB LIKE 'O04%%' OR actTempMain.MKB LIKE 'O05%%' OR actTempMain.MKB LIKE 'O06%%' OR actTempMain.MKB LIKE 'O07%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%' OR Diagnosis.MKB LIKE 'O04%%' OR Diagnosis.MKB LIKE 'O05%%' OR Diagnosis.MKB LIKE 'O06%%' OR Diagnosis.MKB LIKE 'O07%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O04%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O04%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O05%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O05%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek > 12 AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O06%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O06%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%' OR actTempMain.MKB LIKE 'O04%%' OR actTempMain.MKB LIKE 'O05%%' OR actTempMain.MKB LIKE 'O06%%' OR actTempMain.MKB LIKE 'O07%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%' OR Diagnosis.MKB LIKE 'O04%%' OR Diagnosis.MKB LIKE 'O05%%' OR Diagnosis.MKB LIKE 'O06%%' OR Diagnosis.MKB LIKE 'O07%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND (actTempMain.MKB LIKE 'O02%%' OR actTempMain.MKB LIKE 'O03%%')''',
                         '''AND (Diagnosis.MKB LIKE 'O02%%' OR Diagnosis.MKB LIKE 'O03%%')''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O04%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O04%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O05%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O05%%' ''',

                         '''(actMain.MKB IS NOT NULL OR Diagnosis.MKB IS NOT NULL) AND Event.pregnancyWeek <= 21''',
                         '''AND actTempMain.MKB LIKE 'O06%%' ''',
                         '''AND Diagnosis.MKB LIKE 'O06%%' '''
                        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '15%', [u'Наименование', u'', u'', u'1'], CReportBase.AlignCenter),
            ( '5%', [u'№ строки', u'', u'', u'2'], CReportBase.AlignCenter),
            ( '10%', [u'Код МКБ пересмотра', u'', u'', u'3'], CReportBase.AlignCenter),
            ( '10%', [u'Всего', u'', u'', u'4'], CReportBase.AlignCenter),
            ( '6%', [u'из них у женщин в возрасте', u'до 14 лет', u'включительно', u'5'], CReportBase.AlignCenter),
            ( '6%', [u'', u'15 - 19 лет', u'всего', u'6'], CReportBase.AlignCenter),
            ( '6%', [u'', u'', u'из них 15 - 17 лет', u'7'], CReportBase.AlignCenter),
            ( '6%', [u'', u'20 - 24 годп', u'', u'8'], CReportBase.AlignCenter),
            ( '6%', [u'', u'25 - 29 лет', u'', u'9'], CReportBase.AlignCenter),
            ( '6%', [u'', u'30 - 34 года', u'', u'10'], CReportBase.AlignCenter),
            ( '6%', [u'', u'35 - 39 лет', u'', u'11'], CReportBase.AlignCenter),
            ( '6%', [u'', u'40 - 44 года', u'', u'12'], CReportBase.AlignCenter),
            ( '6%', [u'', u'45 - 49 лет', u'', u'13'], CReportBase.AlignCenter),
            ( '6%', [u'', u'50 лет и старше', u'', u'14'], CReportBase.AlignCenter),
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)
        pf = QtGui.QTextCharFormat()

        cursor.insertBlock()
        cursor.setCharFormat(bf)
        cursor.insertText(u'(1000) ')
        cursor.setCharFormat(pf)

        table = createTable(cursor, tableColumns)

        columnQuery = [14, 19, 17, 24, 29, 34, 39, 44, 49, 50]
        numRowQuery = 0
        flagDead = False

        for z in range(len(self.rowNameSet)):
            row = self.rowNameSet[z]
            if row[1] == u'4':
                flagDead = True
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            j = 3
            numColumnQuery = 0
            if row[1] not in (u'1.1', u'1.2', u'2.2.1.1', u'2.2.1.1.1', u'2.3', u'3.2.1', u'3.3', u'4.3', u'4.4', u'4.7'):
                query = selectData(params,
                                   self.rowQuery[numRowQuery],
                                   self.rowQuery[numRowQuery + 1],
                                   self.rowQuery[numRowQuery + 2],
                                   flagDead)
                if query.first():
                    record = query.record()
                    table.setText(i, j, forceString(record.value('countAll')))
                    j += 1
                    while numColumnQuery < len(columnQuery):
                        table.setText(i, j, forceString(record.value('count%s' % columnQuery[numColumnQuery])))
                        numColumnQuery += 1
                        j += 1
                    numRowQuery += 3
                else:
                    while j <= 13:
                        table.setText(i, j, '0')
                        j += 1
            else:
                while j <= 13:
                    table.setText(i, j, '0')
                    j += 1

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 3, 1)
        table.mergeCells(0, 4, 1, 10)
        table.mergeCells(1, 5, 1, 2)
        table.mergeCells(1, 7, 2, 1)
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)
        table.mergeCells(1, 12, 2, 1)
        table.mergeCells(1, 13, 2, 1)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setCharFormat(bf)
        cursor.insertText(u'(2000) ')
        cursor.setCharFormat(pf)
        query2 = selectData2(params, True)
        if query2.first():
            record2 = query2.record()
            cursor.insertText(u'Из числа женщин, умерших посбе прерывания беременности (стр. 4), умерло в сроки беременности: до 12 недель 1 - %s' % forceString(record2.value('count1')))
            cursor.insertText(u', 12-21 неделя 2 - %s' % forceString(record2.value('count2')))
            cursor.insertText(u', из общего числа умерших умерло первобеременных 3 - 0')
        else:
            cursor.insertText(u'Из числа женщин, умерших посбе прерывания беременности (стр. 4), умерло в сроки беременности: до 12 недель 1 - 0')
            cursor.insertText(u', 12-21 неделя 2 - 0')
            cursor.insertText(u', из общего числа умерших умерло первобеременных 3 - 0')
        query2 = selectData2(params)
        if query2.first():
            record2 = query2.record()
            cursor.insertText(u'.\n')
            cursor.setCharFormat(bf)
            cursor.insertText(u'аборты до 14 лет включительно:')
            cursor.setCharFormat(pf)
            cursor.insertText(u' 14 лет - %s' % forceString(record2.value('count14')))
            cursor.insertText(u', 13 лет - %s' % forceString(record2.value('count13')))
            cursor.insertText(u', 12 лет - %s' % forceString(record2.value('count12')))
        else:
            cursor.insertText(u'.\n')
            cursor.setCharFormat(bf)
            cursor.insertText(u'аборты до 14 лет включительно:')
            cursor.setCharFormat(pf)
            cursor.insertText(u' 14 лет - 0')
            cursor.insertText(u', 13 лет - 0')
            cursor.insertText(u', 12 лет - 0')

        return doc

from Ui_ReportF13Setup import Ui_ReportF13SetupDialog

class CReportF13SetupDialog(QtGui.QDialog, Ui_ReportF13SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbPerson.setValue(params.get('personId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['personId'] = self.cmbPerson.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        return result