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


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    where = ''
    if begDate:
        where += u"AND DATE(Event.execDate) >= DATE('%s') " % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += u"AND DATE(Event.execDate) <= DATE('%s') " % endDate.toString('yyyy-MM-dd')
    stmt = u'''
        SELECT DISTINCT eHBLC.id,
               Event.execDate,
               Client.lastName,
               Client.firstName,
               Client.patrName,
               Client.birthDate,
               Event.externalId,
               movingAction.begDate AS movingBegDate,
               leavedAction.begDate AS leavedBegDate,
               Person.lastName AS personLastName,
               Person.firstName AS personFirstName,
               Person.patrName AS personPatrName,
               OrgStructure.name AS orgStructName,
               insurerOrg.shortName AS insurerOrgName,
               eHBLC.moveDate,
               eHBLC.returnDate,
               rbResult.regionalCode,
               HBLC.name,
               OrgStructure.hasDayStationary

        FROM Event_HospitalBedsLocationCard AS eHBLC
        INNER JOIN Event ON Event.id = eHBLC.event_id AND Event.deleted = 0 %s
        INNER JOIN Client ON Event.client_id = Client.id AND Client.deleted = 0
        LEFT JOIN Action AS leavedAction ON leavedAction.id = (SELECT MAX(tempLeavedAction.id)
                                                                FROM Action AS tempLeavedAction
                                                                INNER JOIN ActionType AS leavedActionType ON tempLeavedAction.actionType_id = leavedActionType.id AND leavedActionType.deleted = 0 AND leavedActionType.flatCode LIKE 'leaved%%'
                                                                WHERE tempLeavedAction.event_id = Event.id)
        LEFT JOIN Person ON Person.id = Event.execPerson_id
            AND Person.deleted = 0
        LEFT JOIN OrgStructure ON OrgStructure.id = (SELECT tempActPropOS.value
                                                     FROM Action AS tempAct
                                                     INNER JOIN ActionType AS tempActType ON tempActType.id = tempAct.actionType_id AND tempActType.flatCode = 'leaved' AND tempActType.deleted = 0
                                                     INNER JOIN ActionPropertyType AS tempActPropType ON tempActPropType.actionType_id = tempActType.id AND tempActPropType.deleted = 0 AND tempActPropType.name LIKE 'Отделение%%'
                                                     INNER JOIN ActionProperty AS tempActProp ON tempActProp.type_id = tempActPropType.id AND tempActProp.action_id = tempAct.id AND tempActProp.deleted = 0
                                                     INNER JOIN ActionProperty_OrgStructure AS tempActPropOS ON tempActPropOS.id = tempActProp.id
                                                     WHERE tempAct.id = leavedAction.id
                                                     LIMIT 1)
                                  AND OrgStructure.deleted = 0
        LEFT JOIN Action AS movingAction ON movingAction.id = (SELECT MAX(tempMovingAction.id)
                                                                FROM Action AS tempMovingAction
                                                                INNER JOIN ActionType AS movingActionType ON tempMovingAction.actionType_id = movingActionType.id AND movingActionType.deleted = 0 AND movingActionType.flatCode LIKE 'moving%%'
                                                                WHERE tempMovingAction.event_id = Event.id)

        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.deleted = 0
        LEFT JOIN Organisation AS insurerOrg ON insurerOrg.id = ClientPolicy.insurer_id AND insurerOrg.deleted = 0
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        LEFT JOIN rbHospitalBedsLocationCardType AS HBLC ON HBLC.id = eHBLC.locationCardType_id
        WHERE eHBLC.deleted = 0
    ''' % where
    return db.query(stmt)


class CReportArchiveHistory(CReport):
    def __init__(self, parent = None, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Архив истории болезни')

    def getSetupDialog(self, parent):
        result = CReportArchiveHistorySetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):

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
            ( '9%', [u'Дата выставления счёта / дата поступления в архив'], CReportBase.AlignCenter),
            ( '5%', [u'Фамилия'], CReportBase.AlignCenter),
            ( '9%', [u'Имя'], CReportBase.AlignCenter),
            ( '9%', [u'Отчество'], CReportBase.AlignCenter),
            ( '5%', [u'Год рождения'], CReportBase.AlignCenter),
            ( '5%', [u'№ истории болезни'], CReportBase.AlignCenter),
            ( '5%', [u'Дата поступления'], CReportBase.AlignCenter),
            ( '5%', [u'Дата выписки'], CReportBase.AlignCenter),
            ( '5%', [u'Отделение'], CReportBase.AlignCenter),
            ( '5%', [u'Лечащий врач'], CReportBase.AlignCenter),
            ( '5%', [u'Страховая компания'], CReportBase.AlignCenter),
            ( '5%', [u'Место в архиве'], CReportBase.AlignCenter),
            ( '5%', [u'Дата выдачи истории болезни'], CReportBase.AlignCenter),
            ( '5%', [u'Куда и кем забрана история болезни'], CReportBase.AlignCenter),
            ( '5%', [u'Срок возврата'], CReportBase.AlignCenter),
            ( '5%', [u'Дата возврата'], CReportBase.AlignCenter),
            ( '4%', [u'Примечание №1'], CReportBase.AlignCenter),
            ( '4%', [u'Примечание №2'], CReportBase.AlignCenter),
        ]

        pf = QtGui.QTextCharFormat()

        cursor.insertBlock()
        cursor.setCharFormat(pf)

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, forceDate(record.value('execDate')).toString('dd.MM.yyyy'))
            table.setText(i, 1, forceString(record.value('lastName')))
            table.setText(i, 2, forceString(record.value('firstName')))
            table.setText(i, 3, forceString(record.value('patrName')))
            table.setText(i, 4, forceDate(record.value('birthDate')).toString('dd.MM.yyyy'))
            table.setText(i, 5, forceString(record.value('externalId')))
            table.setText(i, 6, forceDate(record.value('movingBegDate')).toString('dd.MM.yyyy'))
            table.setText(i, 7, forceDate(record.value('leavedBegDate')).toString('dd.MM.yyyy'))
            table.setText(i, 8, forceString(record.value('orgStructName')))
            table.setText(i, 9, forceString(record.value('personLastName')) + ' ' + forceString(record.value('personFirstName')) + ' ' + forceString(record.value('personPatrName')))
            table.setText(i, 10, forceString(record.value('insurerOrgName')))

            table.setText(i, 12, forceDate(record.value('moveDate')).toString('dd.MM.yyyy'))

            table.setText(i, 14, forceDate(record.value('moveDate')).addDays(14).toString('dd.MM.yyyy'))
            table.setText(i, 15, forceDate(record.value('returnDate')).toString('dd.MM.yyyy'))
            if forceString(record.value('regionalCode')) == '006':
                table.setText(i, 16, u'умер')
            elif forceString(record.value('name')):
                table.setText(i, 16, forceString(record.value('name')))
            else:
                table.setText(i, 16, u'на дооформление')
            if forceInt(record.value('hasDayStationary')) == 1:
                table.setText(i, 17, u'д/с')

        return doc

from Ui_ReportArchiveHistorySetup import Ui_ReportArchiveHistorySetupDialog

class CReportArchiveHistorySetupDialog(QtGui.QDialog, Ui_ReportArchiveHistorySetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        return result