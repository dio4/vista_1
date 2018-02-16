# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Moscow.Dispatching.DispatchingSetupDialog import CDispatchingSetupDialog
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceInt, forceRef, forceString


def selectData(date, begTime, orgStructureIdList):
    db = QtGui.qApp.db

    begDateTime = QtCore.QDateTime(date.addDays(-1), begTime)
    endDateTime = QtCore.QDateTime(date, begTime)

    OrgStructure = db.table('OrgStructure')

    maintTableStmt = db.selectStmt(OrgStructure, OrgStructure['id'], [OrgStructure['id'].inlist(orgStructureIdList)])

    subQueryTypes = {
        'moving'    : ('moving',   u'Отделение пребывания'),
        'received'  : ('received', u'Направлен в отделение'),
        'movingInto': ('moving',   u'Переведен в отделение'),
        'movingFrom': ('moving',   u'Переведен из отделения'),
        'leaved'    : ('leaved',   u'Отделение')
    }

    def subQueryStmt(queryType):
        actionTypeFlatCode, actionPropertyName = subQueryTypes[queryType]

        Action = db.table('Action')
        ActionType = db.table('ActionType')
        ActionProperty = db.table('ActionProperty')
        ActionPropertyType = db.table('ActionPropertyType')
        ActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
        ActionPropertyString = db.table('ActionProperty_String')
        Client = db.table('Client')
        Event = db.table('Event')
        Finance = db.table('rbFinance')

        cond = [
            ActionType['flatCode'].eq(actionTypeFlatCode),
            ActionType['deleted'].eq(0)
        ]

        queryTable = ActionType.innerJoin(Action, [Action['actionType_id'].eq(ActionType['id']),
                                                   Action['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(Event, [Event['id'].eq(Action['event_id']),
                                                  Event['deleted'].eq(0)])

        queryTable = queryTable.innerJoin(Client, Client['id'].eq(Event['client_id']))

        queryTable = queryTable.innerJoin(ActionPropertyType, [ActionPropertyType['actionType_id'].eq(ActionType['id']),
                                                               ActionPropertyType['name'].eq(actionPropertyName),
                                                               ActionPropertyType['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(ActionProperty, [ActionProperty['action_id'].eq(Action['id']),
                                                           ActionProperty['type_id'].eq(ActionPropertyType['id']),
                                                           ActionProperty['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(ActionPropertyOrgStructure, ActionPropertyOrgStructure['id'].eq(ActionProperty['id']))
        queryTable = queryTable.innerJoin(OrgStructure, OrgStructure['id'].eq(ActionPropertyOrgStructure['value']))

        cols = [
            ActionPropertyOrgStructure['value'].alias('id'),
            u'count({propertyId}) AS {alias}'.format(propertyId=ActionProperty['id'], alias=queryType)
        ]

        if queryType == 'moving':
            queryTable = queryTable.innerJoin(Finance, Finance['id'].eq(Action['finance_id']))
            cond.extend([
                Action['begDate'].datetimeLt(begDateTime),
                db.joinOr([Action['endDate'].datetimeGe(begDateTime),
                           Action['endDate'].isNull()])
            ])
        elif queryType == 'received':
            deliveredByPropertyName = u'Кем доставлен'
            deliveredByAPT = ActionPropertyType.alias('DelveredByAPT')
            deliveredByAP = ActionProperty.alias('DelveredByAP')
            deliveredByAPS = ActionPropertyString.alias('DelveredByAPS')

            queryTable = queryTable.leftJoin(deliveredByAPT, [deliveredByAPT['name'].eq(deliveredByPropertyName),
                                                              deliveredByAPT['actionType_id'].eq(ActionType['id']),
                                                              deliveredByAPT['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(deliveredByAP, [deliveredByAP['action_id'].eq(Action['id']),
                                                             deliveredByAP['type_id'].eq(deliveredByAPT['id']),
                                                             deliveredByAP['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(deliveredByAPS, deliveredByAPS['id'].eq(deliveredByAP['id']))

            isUrgentCond = Action['isUrgent'].eq(0)
            byHimselfCond = deliveredByAPS['value'].like(u'%самотёк%')
            byEmergencyCond = deliveredByAPS['value'].like(u'%скорая помощь%')

            cols.extend([
                u'count(if({isUrgentCond}, {propertyId}, NULL)) AS isUrgent'.format(isUrgentCond=isUrgentCond, propertyId=ActionProperty['id']),
                u'count(if({byHimselfCond}, {propertyId}, NULL)) AS byHimself'.format(byHimselfCond=byHimselfCond, propertyId=ActionProperty['id']),
                u'count(if({byEmergencyCond}, {propertyId}, NULL)) AS byEmergency'.format(byEmergencyCond=byEmergencyCond, propertyId=ActionProperty['id'])
            ])

            cond.extend([
                Action['begDate'].datetimeGe(begDateTime),
                Action['begDate'].datetimeLt(endDateTime)
            ])
        elif queryType == 'movingInto':
            cond.extend([
                Action['endDate'].datetimeGe(begDateTime),
                Action['endDate'].datetimeLt(endDateTime)
            ])
        elif queryType == 'movingFrom':
            cond.extend([
                Action['begDate'].datetimeGe(begDateTime),
                Action['begDate'].datetimeLt(endDateTime)
            ])
        elif queryType == 'leaved':
            resultPropertyName = u'Исход госпитализации'
            resultAPT = ActionPropertyType.alias('ResultAPT')
            resultAP = ActionProperty.alias('ResultAP')
            resultAPS = ActionPropertyString.alias('ResultAPS')

            queryTable = queryTable.leftJoin(resultAPT, [resultAPT['name'].eq(resultPropertyName),
                                                         resultAPT['actionType_id'].eq(ActionType['id']),
                                                         resultAPT['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(resultAP, [resultAP['action_id'].eq(Action['id']),
                                                        resultAP['type_id'].eq(resultAPT['id']),
                                                        resultAP['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(resultAPS, resultAPS['id'].eq(resultAP['id']))

            deathCond = resultAPS['value'].eq('death')
            # toHomeCond = resultAPS['value'].eq('toHome')
            toOtherOrgCond = resultAPS['value'].eq('toOtherOrg')

            cols.extend([
                'count(if({deathCond}, {propertyId}, NULL)) AS death'.format(deathCond=deathCond, propertyId=ActionProperty['id']),
                'count(if({toOtherOrgCond}, {propertyId}, NULL)) AS toOtherOrg'.format(toOtherOrgCond=toOtherOrgCond, propertyId=ActionProperty['id']),
            ])

            cond.extend([
                Action['begDate'].datetimeGe(begDateTime),
                Action['begDate'].datetimeLt(endDateTime)
            ])

        return db.selectStmt(queryTable, cols, cond, group=ActionPropertyOrgStructure['value'])

    mainTable = db.table(maintTableStmt).alias('mainTable')
    moving = db.table(subQueryStmt('moving')).alias('moving')
    received = db.table(subQueryStmt('received')).alias('received')
    movingInto = db.table(subQueryStmt('movingInto')).alias('movingInto')
    movingFrom = db.table(subQueryStmt('movingFrom')).alias('movingFrom')
    leaved = db.table(subQueryStmt('leaved')).alias('leaved')

    queryTable = mainTable.leftJoin(moving, moving['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(received, received['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(movingInto, movingInto['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(movingFrom, movingFrom['id'].eq(mainTable['id']))
    queryTable = queryTable.leftJoin(leaved, leaved['id'].eq(mainTable['id']))

    cols = [
        mainTable['id'].alias('id'),
        moving['moving'].alias('moving'),
        received['received'].alias('received'),
        received['byHimself'].alias('byHimself'),
        received['byEmergency'].alias('byEmergency'),
        received['isUrgent'].alias('isUrgent'),
        movingInto['movingInto'].alias('movingInto'),
        movingFrom['movingFrom'].alias('movingFrom'),
        leaved['leaved'].alias('leaved'),
        leaved['death'].alias('leavedDeath'),
        leaved['toOtherOrg'].alias('leavedToOtherOrg')
    ]

    stmt = db.selectStmt(queryTable, cols)

    return db.query(stmt)


class CDispathingByOrgStructureReport(CReport):
    u"""
        Диспетчерские по отделениям
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Диспетчерские по отделениям')


    def getSetupDialog(self, parent):
        result = CDispatchingSetupDialog(parent)
        result.setTitle(self.title())
        return result


    @staticmethod
    def createTable(cursor, charFormar, orgStructureNames):
        columnCount = 1 + len(orgStructureNames)
        columnWidthPercent = '%.1f%%' % (100.0 / columnCount,)

        tableColumns = [(columnWidthPercent, u'', CReportBase.AlignLeft)]
        for name in orgStructureNames:
            tableColumns.append((columnWidthPercent, name, CReportBase.AlignRight))
        table = createTable(cursor, tableColumns, charFormat=charFormar)

        return table


    def build(self, params):
        date = params.get('date', QtCore.QDate())
        begTime = params.get('begTime', QtCore.QTime())

        orgStructures = [
            (u'3т/о',      [106]),
            (u'2ко',       [37]),
            (u'ОНК',       [118]),
            (u'невр. отд', [36]),
            (u'2хо',       [13]),
            (u'энд. отд',  [107]),
            (u'ОСХ',       [39]),
            (u'НХО',       [15]),
            (u'НХО 2',     [38]),
            (u'1тр + 2тр', [17, 18]),
            (u'ожог. отд', [32]),
            (u'ЛОР',       [16]),
            (u'МХГ',       [12, 9]),
            (u'ЧЛХ',       [19, 20]),
            (u'н.о. бит',  [28]),
            (u'НРО',       [26]),
            (u'РАО общ',   [25]),
            (u'ожог. бит', [108]),
            (u'КРО',       [27]),
            (u'Г/О',       [68])
        ]
        orgStructureIds = reduce(lambda x,y: x+y, [ids for name, ids in orgStructures])

        reportData = {}
        query = selectData(date, begTime, orgStructureIds)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            id = forceRef(record.value('id'))
            moving = forceInt(record.value('moving'))
            received = forceInt(record.value('received'))
            byHimself = forceInt(record.value('byHimself'))
            byEmergency = forceInt(record.value('byEmergency'))
            isUrgent = forceInt(record.value('isUrgent'))
            movingInto = forceInt(record.value('movingInto'))
            movingFrom = forceInt(record.value('movingFrom'))
            leaved = forceInt(record.value('leaved'))
            leavedDeath = forceInt(record.value('leavedDeath'))
            # leavedToOtherOrg = forceInt(record.value('leavedToOtherOrg'))

            inHospital = moving + received + movingInto - movingFrom - leaved

            reportData[id] = (
                moving,
                received,
                byEmergency,
                0,
                isUrgent,
                byHimself,
                movingInto,
                0,
                leaved,
                movingFrom,
                leavedDeath,
                inHospital
            )

        tableData = [[sum(data) for data in zip(*[reportData[id] for id in orgStructureIds if id in reportData])] for orgStructureName, orgStructureIds in orgStructures]

        rowNames = [u'сост', u'пост', u'ск', u'Ф2', u'план', u'сам.', u'пер +', u'проч', u'выб', u'пер -', u'умер', u'сост']

        fontSize = 8
        fontSizeHeader = 9
        charFormatHeader = CReportBase.TableHeader
        charFormatHeader.setFontWeight(QtGui.QFont.Bold)
        charFormatBody = CReportBase.TableBody
        charFormatBody.setFontPointSize(fontSize)
        charFormatBodyBold = CReportBase.TableBody
        charFormatBodyBold.setFontWeight(QtGui.QFont.Bold)
        charFormatBodyBold.setFontPointSize(fontSize)

        doc = QtGui.QTextDocument()

        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignLeft)
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(charFormatHeader)
        cursor.setBlockFormat(bf)
        cursor.insertText(u'Дата {date}'.format(date=forceString(date.toString('dd.MM.yyyy'))))
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        table = self.createTable(cursor, charFormatBodyBold, [name for name, ids in orgStructures])

        for rowNumber, rowName in enumerate(rowNames):
            i = table.addRow()
            table.setText(i, 0, rowName, charFormat=charFormatBodyBold)
            for colNumber in xrange(len(tableData)):
                value = tableData[colNumber][rowNumber] if len(tableData[colNumber]) > rowNumber else 0
                table.setText(i, colNumber+1, value, charFormat=charFormatBody)


        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignRight)
        cursor.setCharFormat(charFormatHeader)
        cursor.setBlockFormat(bf)
        cursor.insertText(u'Не транспортаб.:' + u'_' * 10 + u'   ' + u'Передал(а)' + u'_' * 20)

        return doc
