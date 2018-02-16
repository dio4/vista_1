# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils       import forceBool, forceDate, forceInt, forceString
from Reports.Report      import CReport
from Reports.ReportBase  import createTable, CReportBase

from Ui_ReportRegisterSickLeaveSetup import Ui_ReportRegisterSickLeaveSetupDialog

def selectData(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    chkWithoutExternal = forceBool(params.get('chkWithoutExternal'))
    short  = forceBool(params.get('short'))
    result = []
    number = 1
    where = ''
    joinPeriod = ' INNER JOIN TempInvalid_Period ON TempInvalid.id = TempInvalid_Period.master_id ' \
                 ' AND TempInvalid_Period.isExternal = 0' if chkWithoutExternal else ''
    stmtMain = '''
        SELECT
            DISTINCT TempInvalid.id,
            TempInvalid.number AS invalidNumber,
            Event.externalId,
            Person.lastName AS personLastName,
            Person.firstName AS personFirstName,
            Person.patrName AS personPatrName,
            Client.lastName AS clientLastName,
            Client.firstName AS clientFirstName,
            Client.patrName AS clientPatrName,
            TempInvalid.placeWork,
            TempInvalid.begDate AS tempInvalidDate,
            tempInvalidLast.Number AS invalidNumberLast,
            TempInvalid.busyness,
            Organisation.title
        FROM TempInvalid
        %s
        LEFT JOIN Diagnosis ON TempInvalid.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0
        LEFT JOIN Diagnostic ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnostic.deleted = 0
        LEFT JOIN Event ON Diagnostic.event_id = Event.id AND Event.deleted = 0
        LEFT JOIN Person ON TempInvalid.person_id = Person.id AND Person.deleted = 0
        LEFT JOIN Organisation ON Person.org_id = Organisation.id AND Organisation.deleted = 0
        LEFT JOIN Client ON TempInvalid.client_id = Client.id AND Client.deleted = 0
        LEFT JOIN TempInvalid AS tempInvalidLast ON TempInvalid.prev_id = tempInvalidLast.id AND tempInvalidLast.deleted = 0
        WHERE TempInvalid.doctype = 0 AND TempInvalid.deleted = 0
    ''' % joinPeriod
    if begDate:
        where += ''' AND DATE(TempInvalid.begDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(TempInvalid.begDate) <= DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    stmtMain += where

    joinPeriod = ' INNER JOIN TempInvalid_Period ON TempInvalidDuplicate.tempInvalid_id = TempInvalid_Period.master_id ' \
                 ' AND TempInvalid_Period.isExternal = 0' if chkWithoutExternal else ''

    stmtDuplicate = '''
        SELECT
            DISTINCT TempInvalidDuplicate.id,
            TempInvalidDuplicate.number AS invalidNumber,
            Event.externalId,
            Person.lastName AS personLastName,
            Person.firstName AS personFirstName,
            Person.patrName AS personPatrName,
            Client.lastName AS clientLastName,
            Client.firstName AS clientFirstName,
            Client.patrName AS clientPatrName,
            TempInvalid.placeWork,
            TempInvalidDuplicate.date AS tempInvalidDate,
            tempInvalidLast.Number AS invalidNumberLast,
            TempInvalid.busyness,
            Organisation.title
        FROM TempInvalidDuplicate
        %s
        LEFT JOIN TempInvalid ON TempInvalidDuplicate.tempInvalid_id = TempInvalid.id AND TempInvalid.doctype = 0 AND TempInvalid.deleted = 0
        LEFT JOIN Diagnosis ON TempInvalid.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0
        LEFT JOIN Diagnostic ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnostic.deleted = 0
        LEFT JOIN Event ON Diagnostic.event_id = Event.id AND Event.deleted = 0
        LEFT JOIN Person ON TempInvalid.person_id = Person.id AND Person.deleted = 0
        LEFT JOIN Organisation ON Person.org_id = Organisation.id AND Organisation.deleted = 0
        LEFT JOIN Client ON TempInvalid.client_id = Client.id AND Client.deleted = 0
        LEFT JOIN TempInvalid AS tempInvalidLast ON TempInvalid.prev_id = tempInvalidLast.id AND tempInvalidLast.deleted = 0
        WHERE TempInvalidDuplicate.deleted = 0
    ''' % joinPeriod
    where = ''
    if begDate:
        where += ''' AND DATE(TempInvalidDuplicate.date) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += ''' AND DATE(TempInvalidDuplicate.date) <= DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    stmtDuplicate += where

    flagMain = True
    for stmt in [stmtMain, stmtDuplicate]:
        if flagMain:
            first = '1'
            duplicate = '0'
            flagMain = False
        else:
            first = '0'
            duplicate = '1'
        query = db.query(stmt)
        while query.next():
            record = query.record()
            main = '0'
            side = '0'
            busyness = forceInt(record.value('busyness'))
            if busyness == 1:
                main = '1'
            elif busyness == 2:
                side = '1'
            if short:
                result.append([number,
                               forceString(record.value('title')),
                               forceString(record.value('invalidNumber')),
                               forceString(record.value('clientLastName')).lower() + ' ' + forceString(record.value('clientFirstName')).lower() + ' ' + forceString(record.value('clientPatrName')).lower(),
                               forceString(record.value('placeWork')),
                               forceDate(record.value('tempInvalidDate')).toString('dd.MM.yyyy')])
            else:
                result.append([number,
                               forceString(record.value('invalidNumber')),
                               forceString(record.value('externalId')),
                               forceString(record.value('personLastName')) + ' ' + forceString(record.value('personFirstName')) + ' ' + forceString(record.value('personPatrName')),
                               forceString(record.value('clientLastName')) + ' ' + forceString(record.value('clientFirstName')) + ' ' + forceString(record.value('clientPatrName')),
                               forceString(record.value('placeWork')),
                               forceDate(record.value('tempInvalidDate')).toString('dd.MM.yyyy'),
                               first,
                               duplicate,
                               forceString(record.value('invalidNumberLast')),
                               main,
                               side])
            number += 1

    return result, stmtMain, stmtDuplicate


class CReportRegisterSickLeave(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Реестр корешков листков нетрудоспособности')

    def getSetupDialog(self, parent):
        result = CReportRegisterSickLeaveSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        short = forceBool(params.get('short', False))
        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        if short:
            tableColumns = [
                ( '5%', [u'№ п/п'], CReportBase.AlignCenter),
                ( '20%', [u'Наименование медицинской организации, выдавшей листок нетрудоспособности (или ОГРН)'], CReportBase.AlignCenter),
                ( '20%', [u'№ листка нетрудоспособности'], CReportBase.AlignCenter),
                ( '20%', [u'Фамилия, имя, отчество пациента'], CReportBase.AlignCenter),
                ( '20%', [u'Место работы - наименование организации пациента'], CReportBase.AlignCenter),
                ( '15%', [u'Дата выдачи листка нетрудоспособности'], CReportBase.AlignCenter)]
        else:
            tableColumns = [
                ( '5%', [u'№ п/п'], CReportBase.AlignCenter),
                ( '8%', [u'№ листка нетрудоспособности'], CReportBase.AlignCenter),
                ( '8%', [u'№ амбулаторной карты'], CReportBase.AlignCenter),
                ( '20%', [u'ФИО врача'], CReportBase.AlignCenter),
                ( '20%', [u'ФИО пациента'], CReportBase.AlignCenter),
                ( '8%', [u'Место работы пациента'], CReportBase.AlignCenter),
                ( '8%', [u'Дата выдачи'], CReportBase.AlignCenter),
                ( '8%', [u'Первичный'], CReportBase.AlignCenter),
                ( '8%', [u'Дубликат'], CReportBase.AlignCenter),
                ( '8%', [u'Продолжение №'], CReportBase.AlignCenter),
                ( '8%', [u'Основное'], CReportBase.AlignCenter),
                ( '8%', [u'По совместительству'], CReportBase.AlignCenter)
            ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        result, stmtMain, stmtDuplicate = selectData(params)
        self.setQueryText(stmtMain + ';\n' + stmtDuplicate + ';\n')

        for row in result:
            i = table.addRow()
            for j in range(len(tableColumns)):
                table.setText(i, j, row[j])

        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignLeft)
        table = createTable(cursor, [('50%', [], CReportBase.AlignLeft), ('50%', [], CReportBase.AlignRight)], 0, 0, 0)
        i = table.addRow()
        table.setText(i, 0, u'Главный врач')
        table.setText(i, 1, forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'chief')))
        return doc

class CReportRegisterSickLeaveSetupDialog(QtGui.QDialog, Ui_ReportRegisterSickLeaveSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.chkShort.setChecked(params.get('short', False))
        self.chkWithoutExternal.setChecked(params.get('chkWithoutExternal', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['short']   = self.chkShort.isChecked()
        result['chkWithoutExternal'] = self.chkWithoutExternal.isChecked()
        return result