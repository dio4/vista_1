# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceRef, forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportLifetimeCytology import Ui_ReportLifetimeCytology


category = {1:u'I', 2: u'II', 3:u'III', 4:u'IV', 5:u'V'}

def selectDataReport(params):

    begDate             = params.get('begDate', None)
    endDate             = params.get('endDate', None)
    complexityCategory  = params.get('complexityCategory', 0)

    db = QtGui.qApp.db

    tableEvent              = db.table('Event')
    tableClientAttach       = db.table('ClientAttach')
    tableAction             = db.table('Action')

    tableJobType            = db.table('rbJobType')
    tableJBActionType       = db.table('rbJobType_ActionType')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')

    tableActionProperty     = db.table('ActionProperty')
    tableAPString           = db.table('ActionProperty_String')
    tableAPOrganization     = db.table('ActionProperty_Organisation')

    queryTable = tableJobType.innerJoin(tableJBActionType, tableJBActionType['master_id'].eq(tableJobType['id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableJBActionType['actionType_id']))
    queryTable = queryTable.leftJoin(tableActionPropertyType, tableActionPropertyType['actionType_id'].eq(tableActionType['id']))

    queryTable = queryTable.innerJoin(tableAction, tableAction['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    attachJoinCond = [tableClientAttach['client_id'].eq(tableEvent['client_id']),
                      tableClientAttach['deleted'].eq(0)]
    queryTable = queryTable.leftJoin(tableClientAttach, db.joinAnd(attachJoinCond))

    propertyJoinCond = [tableActionProperty['action_id'].eq(tableAction['id']),
                        tableActionProperty['type_id'].eq(forceRef(db.translate('ActionPropertyType', 'name', 'Кем направлен', 'id')))]
    queryTable = queryTable.leftJoin(tableActionProperty, db.joinAnd(propertyJoinCond))
    queryTable = queryTable.leftJoin(tableAPString, tableAPString['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.leftJoin(tableAPOrganization, tableAPOrganization['id'].eq(tableActionProperty['id']))

    cols = [
            u'''count(DISTINCT if(Action.directionDate > ClientAttach.begDate OR ClientAttach.begDate IS NULL, Action.id, NULL)) AS appointed
              , count(DISTINCT if(Action.endDate > ClientAttach.begDate OR ClientAttach.begDate IS NULL, Action.id, NULL)) AS executed
              , count(DISTINCT if((Action.endDate > ClientAttach.begDate OR ClientAttach.begDate IS NULL) AND Event.isPrimary = 1 AND ActionProperty_Organisation.id IS NOT NULL, Action.id, NULL)) AS direction
              , count(DISTINCT if((Action.endDate > ClientAttach.begDate OR ClientAttach.begDate IS NULL) AND Event.isPrimary = 2, Action.id, NULL)) AS repeated''']

    cond = [tableEvent['execDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableJobType['code'].eq(u'2-1')]

    if complexityCategory:
        cond.append(tableAPString['value'].eq(category[complexityCategory]))

    stmt = db.selectStmt(queryTable, cols, cond)
    query = db.query(stmt)
    return query

def selectData(params):

    begDate      = params.get('begDate', None)
    endDate      = params.get('endDate', None)
    complexityCategory  = params.get('complexityCategory', 0)

    db = QtGui.qApp.db

    tableEvent              = db.table('Event')
    tableClientAttach       = db.table('ClientAttach')
    tableAction             = db.table('Action')

    tableJobType            = db.table('rbJobType')
    tableJBActionType       = db.table('rbJobType_ActionType')
    tableActionType         = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')

    tableActionProperty     = db.table('ActionProperty')
    tableAPString           = db.table('ActionProperty_String')
    tableAPInteger          = db.table('ActionProperty_Integer')

    queryTable = tableJobType.innerJoin(tableJBActionType, tableJBActionType['master_id'].eq(tableJobType['id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableJBActionType['actionType_id']))
    queryTable = queryTable.leftJoin(tableActionPropertyType, tableActionPropertyType['actionType_id'].eq(tableActionType['id']))

    queryTable = queryTable.innerJoin(tableAction, tableAction['actionType_id'].eq(tableActionType['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    attachJoinCond = [tableClientAttach['client_id'].eq(tableEvent['client_id']),
                      tableClientAttach['deleted'].eq(0)]
    queryTable = queryTable.leftJoin(tableClientAttach, db.joinAnd(attachJoinCond))

    queryTable = queryTable.innerJoin(tableActionProperty, tableActionProperty['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.innerJoin(tableAPString, tableAPString['id'].eq(tableActionProperty['id']))

    cols = [
            u'''sum(ActionProperty_Integer.value) AS countObject,
                sum(if(ActionProperty_String.value = 'I', ActionProperty_Integer.value, 0)) AS countObjectI,
                sum(if(ActionProperty_String.value = 'II', ActionProperty_Integer.value, 0)) AS countObjectII,
                sum(if(ActionProperty_String.value = 'III', ActionProperty_Integer.value, 0)) AS countObjectIII,
                sum(if(ActionProperty_String.value = 'IV', ActionProperty_Integer.value, 0)) AS countObjectIV,
                sum(if(ActionProperty_String.value = 'V', ActionProperty_Integer.value, 0)) AS countObjectV,
                count(DISTINCT ActionProperty.action_id) AS countResearch,
                count(DISTINCT if(ActionProperty_String.value = 'I', ActionProperty.action_id, NULL)) AS countResearchI,
                count(DISTINCT if(ActionProperty_String.value = 'II', ActionProperty.action_id, NULL)) AS countResearchII,
                count(DISTINCT if(ActionProperty_String.value = 'III',ActionProperty.action_id, NULL)) AS countResearchIII,
                count(DISTINCT if(ActionProperty_String.value = 'IV', ActionProperty.action_id, NULL)) AS countResearchIV,
                count(DISTINCT if(ActionProperty_String.value = 'V', ActionProperty.action_id, NULL)) AS countResearchV,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%', ActionProperty.action_id, NULL)) AS urgency,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%' AND ActionProperty_String.value = 'II', ActionProperty.action_id, NULL)) AS urgencyI,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%' AND ActionProperty_String.value = 'III', ActionProperty.action_id, NULL)) AS urgencyII,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%' AND ActionProperty_String.value = 'IV', ActionProperty.action_id, NULL)) AS urgencyIII,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%' AND ActionProperty_String.value = 'IV', ActionProperty.action_id, NULL)) AS urgencyIV,
                count(DISTINCT if(ActionType.name LIKE 'Срочное интраоперационное цитологическое исследова%' AND ActionProperty_String.value = 'V' , ActionProperty.action_id, NULL)) AS urgencyV''']

    cond = [tableEvent['execDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableJobType['code'].eq(u'2-1')]

    if complexityCategory:
        cond.append(tableAPString['value'].eq(category[complexityCategory]))

    stmt = db.selectStmt(queryTable, cols, cond)
    query = db.query(stmt)
    return query

class CReportLifetimeCytology(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Прижизненные цитологические диагностические исследования')

    def getSetupDialog(self, parent):
        result = CLifetimeCytology(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        query = selectDataReport(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20', [u'Наименование показателя'], CReportBase.AlignLeft),
                        ('%5',  [u'№ строки'], CReportBase.AlignCenter),
                        ('%5',  [u'Всего'], CReportBase.AlignCenter),
                        ('%5',  [u'из них: по прикрепленным медицинским организациям'], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)
        if query.first():
            record = query.record()
            appointed = forceInt(record.value('appointed'))
            executed  = forceInt(record.value('executed'))
            direction = forceInt(record.value('direction'))
            repeated  = forceInt(record.value('repeated'))
            i = table.addRow()
            while i < 4:
                if i == 1:
                    table.setText(i, 0, u'Число направлений на прижизненные цитологические диагностические исследования')
                    table.setText(i, 2, appointed)
                elif i == 2:
                    table.setText(i, 0, u'Число пациентов, которым выполнены прижизненные цитологические диагностические исследования')
                    table.setText(i, 2, executed)
                else:
                    table.setText(i, 0, u'    из них (стр. 02): по направлениям из амбулаторно-поликлинических организаций и подразделений')
                    table.setText(i, 2, direction)
                table.setText(i, 1, i)
                i = table.addRow()
            table.setText(i, 1, i)
            table.setText(i, 0, u'                      проведены повторные цитологические исследования для уточнения диагноза, оценки динамики развития патологического процесса и эффективности лечения')
            table.setText(i, 2, repeated)
        query = selectData(params)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Структура цитологических диагностических исследований по категориям сложности')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20', [u'Наименование показателя'], CReportBase.AlignLeft),
                        ('%5',  [u'№ строки'], CReportBase.AlignCenter),
                        ('%5',  [u'Всего'], CReportBase.AlignCenter),
                        ('%5',  [u'Цитологический материал по категориям сложности', u'I'], CReportBase.AlignCenter),
                        ('%5',  [u'',                                                u'II'], CReportBase.AlignCenter),
                        ('%5',  [u'',                                                u'III'], CReportBase.AlignCenter),
                        ('%5',  [u'',                                                u'IV'], CReportBase.AlignCenter),
                        ('%5',  [u'',                                                u'V'], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 5)
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)

        if query.first():
            record = query.record()
            countObject       = forceInt(record.value('countObject'))
            countObjectI      = forceInt(record.value('countObjectI'))
            countObjectII     = forceInt(record.value('countObjectII'))
            countObjectIII    = forceInt(record.value('countObjectIII'))
            countObjectIV     = forceInt(record.value('countObjectIV'))
            countObjectV      = forceInt(record.value('countObjectV'))
            countResearch     = forceInt(record.value('countResearch'))
            countResearchI    = forceInt(record.value('countResearchI'))
            countResearchII   = forceInt(record.value('countResearchII'))
            countResearchIII  = forceInt(record.value('countResearchIII'))
            countResearchIV   = forceInt(record.value('countResearchIV'))
            countResearchV    = forceInt(record.value('countResearchV'))
            urgency           = forceInt(record.value('urgency'))
            urgencyI          = forceInt(record.value('urgencyI'))
            urgencyII         = forceInt(record.value('urgencyII'))
            urgencyIII        = forceInt(record.value('urgencyIII'))
            urgencyIV         = forceInt(record.value('urgencyIV'))
            urgencyV          = forceInt(record.value('urgencyV'))

            i = table.addRow()

            while i < 4:
                if i == 2:
                    table.setText(i, 0, u'Число объектов цитологического материала')
                    table.setText(i, 2, countObject)
                    table.setText(i, 3, countObjectI)
                    table.setText(i, 4, countObjectII)
                    table.setText(i, 5, countObjectIII)
                    table.setText(i, 6, countObjectIV)
                    table.setText(i, 7, countObjectV)
                else:
                    table.setText(i, 0, u'Число исследований цитологического материала')
                    table.setText(i, 2, countResearch)
                    table.setText(i, 3, countResearchI)
                    table.setText(i, 4, countResearchII)
                    table.setText(i, 5, countResearchIII)
                    table.setText(i, 6, countResearchIV)
                    table.setText(i, 7, countResearchV)
                table.setText(i, 1, i-2)
                i = table.addRow()
            table.setText(i, 0, u'  из них (стр. 02): число срочных интраоперационных цитологических исследований')
            table.setText(i, 2, urgency)
            table.setText(i, 3, urgencyI)
            table.setText(i, 4, urgencyII)
            table.setText(i, 5, urgencyIII)
            table.setText(i, 6, urgencyIV)
            table.setText(i, 7, urgencyV)
            table.setText(i, 1, i-2)
        return doc

class CLifetimeCytology(QtGui.QDialog, Ui_ReportLifetimeCytology):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbComplexityCategory.setCurrentIndex(params.get('complexityCategory', 0))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['complexityCategory']  = self.cmbComplexityCategory.currentIndex()
        return params