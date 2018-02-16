# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database               import addDateInRange
from library.Utils                  import forceInt, forceString, getVal
from Orgs.Utils                     import getOrganisationInfo
from Reports.Report                 import CReport
from Reports.ReportBase             import createTable, CReportBase
from Reports.StatReportDD2013Weekly import CReportDD2013WeeklySetupDialog


def selectData(params):
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventKind = db.table('rbEventKind')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableAPS = db.table('ActionProperty_String')


    queryTable = tableClient.innerJoin(tableEventType, db.joinAnd([tableEventType['deleted'].eq(0), tableClient['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableEventKind, db.joinAnd([tableEventType['eventKind_id'].eq(tableEventKind['id']), tableEventKind['code'].inlist(['01', '04'])]))
    queryTable = queryTable.innerJoin(tableEvent, db.joinAnd([tableEvent['eventType_id'].eq(tableEventType['id']), tableEvent['deleted'].eq(0), tableEvent['client_id'].eq(tableClient['id'])]))
    queryTable = queryTable.innerJoin(tableActionType, db.joinAnd([tableActionType['code'].eq(u'др'), tableActionType['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableAction, db.joinAnd([tableAction['event_id'].eq(tableEvent['id']), tableAction['actionType_id'].eq(tableActionType['id']), tableAction['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableActionProperty, db.joinAnd([tableActionProperty['action_id'].eq(tableAction['id']), tableActionProperty['deleted'].eq(0)]))
    queryTable = queryTable.innerJoin(tableActionPropertyType, db.joinAnd([tableActionPropertyType['id'].eq(tableActionProperty['type_id']), tableActionPropertyType['deleted'].eq(0), tableActionPropertyType['actionType_id'].eq(tableActionType['id'])]))
    queryTable = queryTable.innerJoin(tableAPS, tableAPS['id'].eq(tableActionProperty['id']))


    cols = [tableClient['sex'],
            'age(Client.birthDate, Event.setDate) as clientAge',
            tableActionPropertyType['idx'],
            tableAPS['value'].alias('APS_value'),
            'COUNT(DISTINCT Client.id) as cnt'
            ]
    group = [tableClient['sex'],
            'age(Client.birthDate, Event.setDate)',
            tableActionPropertyType['idx'],
            tableAPS['value']
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
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    
    stmt = db.selectStmt(queryTable, cols, cond, group=group)
    return db.query(stmt)


class CReportDDRiskFactors(CReport):
    mapIdxToRow = {9: 0,
                   5: 1,
                   7: 2,
                   10: 3,
                   13: 4,
                   14: 5,
                   12: 6,
                   11: 7,
                   3: 8,
                   17: 10
    }

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сведения о распространенности факторов риска развития хронических неинфекционных заболеваний, являющихся основной причиной инвалидности и преждевременной смертности населения Российской Федерации (человек)')


    def getSetupDialog(self, parent):
        result = CReportDD2013WeeklySetupDialog(parent)
        result.setTitle(self.title())
        result.setPayStatusVisible(False)
        return result

    def getRow(self, idx, apsValue):
        if idx in self.mapIdxToRow and apsValue == u'да':
            return self.mapIdxToRow[idx]
        if idx == 16 and len(apsValue) > 0:
            return 9        # Отягощенная наследственность по хроническим неинфекционным заболеваниям
        if idx == 15:
            if apsValue == u'умеренный':
                return 11
            if apsValue == u'высокий':
                return 12
            if apsValue == u'очень высокий':
                return 13
        return None

    def build(self, params):
        rowSize = 9
        self.resultSet = [[u'Повышенный уровень артериального давления', u'01', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Дислипидемия', u'02', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Повышенный уровень глюкозы в крови', u'03', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Курение табака', u'04', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Риск пагубного потребления алкоголя', u'05', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Риск потребления наркотических средств и психотропных веществ без назначения врача', u'06', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Нерациональное питание', u'07', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Низкая физическая активность', u'08', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Избыточная масса тела (ожирение)', u'09', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Отягощенная наследственность по хроническим неинфекционным заболеваниям', u'10', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Высокий уровень стресса', u'11', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Умеренный суммарный сердечно-сосудистый риск', u'12', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Высокий суммарный сердечно-сосудистый риск', u'13', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     [u'Очень высокий суммарный сердечно-сосудистый риск', u'14', 0, 0, 0, 0, 0, 0, 0, 0, 0],
                     ]



        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            idx = forceInt(record.value('idx'))
            apsValue = forceString(record.value('APS_value')).lower()
            rowNum = self.getRow(idx, apsValue)
            if rowNum == None:
                continue
            age = forceInt(record.value('clientAge'))
            cnt = forceInt(record.value('cnt'))
            sex = forceInt(record.value('sex'))

            row = self.resultSet[rowNum]
            if age > 20 and age < 37:
                row[8] += cnt
                if sex:
                    row[(sex)*3 - 1] += cnt
            elif age > 38 and age <= 60:
                row[9] += cnt
                if sex:
                    row[(sex)*3] += cnt
            elif age > 60:
                row[10] += cnt
                if sex:
                    row[(sex)*3 + 1] += cnt

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
            ( '20%', [u'Фактор риска развития заболеваний', u''], CReportBase.AlignCenter),
            ( '5%', [u'№ строки', u''], CReportBase.AlignCenter),
            ( '9%', [u'Мужчины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'Женщины', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'Старше 60 лет'], CReportBase.AlignRight),
            ( '9%', [u'Всего', u'21 - 36 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'39 - 60 лет'], CReportBase.AlignRight),
            ( '8%', [u'', u'Старше 60 лет'], CReportBase.AlignRight)
        ]

        rowSize = 11
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)
        table.mergeCells(0, 8, 1, 3)

        i = table.addRow()

        for j in xrange(rowSize):
            table.setText(i, j, j+1, blockFormat = bf)

        for z in range(len(self.resultSet)):
            row = self.resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            table.setText(i, 3, row[3])
            table.setText(i, 4, row[4])
            table.setText(i, 5, row[5])
            table.setText(i, 6, row[6])
            table.setText(i, 7, row[7])
            table.setText(i, 8, row[8])
            table.setText(i, 9, row[9])
            table.setText(i, 10, row[10])


        return doc
