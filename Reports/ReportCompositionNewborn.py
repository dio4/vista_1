# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils          import forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Reports.ReportF14Children import CF14Children

def selectData(params, lstOrgStructure):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    order           = params.get('order')
    eventTypeId     = params.get('eventTypeId')
    eventPurposeId  = params.get('eventPurposeId')
    financeId       = params.get('financeId')
    cmbOrgStructure = params.get('cmbOrgStructure')
    orgStructureId  = params.get('orgStructureId')

    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableAPOrgStructure = db.table('ActionProperty_OrgStructure')

    cond = [tableAction['begDate'].dateGe(begDate),
            tableAction['begDate'].dateLe(endDate)]

    if order:
        cond.append(tableEvent['order'].eq(order))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if financeId:
        cond.append(tableAction['finance_id'].eq(financeId))
    if lstOrgStructure and cmbOrgStructure:
        cond.append(tableAPOrgStructure['value'].inlist(lstOrgStructure))
    if orgStructureId and not cmbOrgStructure:
        cond.append(tableAPOrgStructure['value'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = u'''SELECT act_moving.MKB,
                      aps_leavedResult.id AS dead,
                      DATEDIFF(act_leaved.endDate, Client.birthDate) AS deadAge
               FROM Event
                    INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0
                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.flatCode = 'received'
                    INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.name = 'Направлен в отделение' AND ActionPropertyType.deleted = 0
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ActionProperty.id
                    INNER JOIN Action act_moving ON act_moving.id = (SELECT MAX(a.id)
                                                                     FROM Action a
                                                                        INNER JOIN ActionType AT ON AT.id = a.actionType_id
                                                                     WHERE AT.flatCode = 'moving' AND a.event_id = Event.id AND a.deleted = 0 AND AT.deleted = 0)
                    LEFT JOIN Action act_leaved ON act_leaved.event_id = Event.id AND act_leaved.actionType_id = (SELECT at.id
                                                                                                                  FROM ActionType at
                                                                                                                  WHERE at.flatCode = 'leaved' AND at.deleted = 0) AND act_leaved.deleted = 0
                    LEFT JOIN ActionPropertyType apt_leavedResult ON apt_leavedResult.actionType_id = act_leaved.actionType_id AND apt_leavedResult.name = 'Исход госпитализации' AND apt_leavedResult.deleted = 0
                    LEFT JOIN ActionProperty ap_leavedResult ON ap_leavedResult.action_id = act_leaved.id AND ap_leavedResult.type_id = ActionPropertyType.id AND ap_leavedResult.deleted = 0
                    LEFT JOIN ActionProperty_String aps_leavedResult ON aps_leavedResult.id = ActionProperty.id AND aps_leavedResult.value = 'умер'
               WHERE %s AND DATEDIFF(Action.begDate, Client.birthDate) <= 6 AND Event.deleted = 0''' % (db.joinAnd(cond))

    return db.query(stmt)

class CReportCompositionNewborn(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Состав новорожденных с заболеваниями, поступивших в возрасте 0-6 дней жизни, исходы их лечения')

    def getSetupDialog(self, parent):
        result = CF14Children(parent)
        result.setTitle(self.title())
        result.lstOrgStructure.setTable('OrgStructure')
        result.lblTypeHosp.setVisible(False)
        result.cmbTypeHosp.setVisible(False)
        return result

    def build(self, params):
        resultSet = [
            [u'Всего новорожденных с заболеваниями', u'1', u'', 0, 0, 0, 0, 0, 0],
            [u'острые респираторные инфекции верхних дыхательных путей', u'2', u'J00-J06, J09-J11', 0, 0, 0, 0, 0, 0],
            [u'пневмонии', u'3', u'J12-J18', 0, 0, 0, 0, 0, 0],
            [u'инфекции кожи и подкожной клетчатки', u'4', u'L00-L08', 0, 0, 0, 0, 0, 0],
            [u'отдельные состояния, возникающие в перинатальном периоде', u'5', u'P05-P96', 0, 0, 0, 0, 0, 0],
            [u'из них: замедленный рост и недостаточность питания', u'5.1', u'P05', 0, 0, 0, 0, 0, 0],
            [u'родовая травма - всего', u'5.2', u'P10-P15', 0, 0, 0, 0, 0, 0],
            [u'в том числе разрыв внутричерепных тканей и кровоизлияние вследствие родовой травмы', u'5.2.1', u'P10', 0, 0, 0, 0, 0, 0],
            [u'дыхательные нарушения, характерные для перинатального периода - всего', u'5.3', u'P20-P28', 0, 0, 0, 0, 0, 0],
            [u'из них: внутриутробная гипоксия, асфиксия при родах', u'5.3.1', u'P20, P21', 0, 0, 0, 0, 0, 0],
            [u'дыхательно расстройство у новорожденных', u'5.3.2', u'P22', 0, 0, 0, 0, 0, 0],
            [u'врожденная пневмония', u'5.3.3,', u'P23', 0, 0, 0, 0, 0, 0],
            [u'неонатальные аспирационные синдромы', u'5.3.4', u'', 0, 0, 0, 0, 0, 0],
            [u'инфекционные болезни, специфичные для перинатального периода - всего', u'5.4', u'P35-P39', 0, 0, 0, 0, 0, 0],
            [u'из них: бактериальный сепсис новорожденного', u'5.4.1', u'P36', 0, 0, 0, 0, 0, 0],
            [u'гемолитическая болезнь плода и новорожденного, водянка плода, обусловленная гемолитической болезнью; ядерная желтуха', u'5.5', u'P55-P57', 0, 0, 0, 0, 0, 0],
            [u'неонатальная желтуха, обусловленная чрезмерным гемолизом, другими и неуточненными причинами', u'5.6', u'P58-P59', 0, 0, 0, 0, 0, 0],
            [u'геморрагическая болезнь, диссеминированное внутрисосудистое свертывание у плода и новорожденного, другие перинатальные гематологические нарушения', u'5.7', u'P53, P60, P61', 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'6', u'Q00-Q99', 0, 0, 0, 0, 0, 0],
            [u'Прочие болезни', u'7', u'', 0, 0, 0, 0, 0, 0]
        ]

        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        query = selectData(params, lstOrgStructure)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                ( '38%', [u'Наименование заболевания'                                                                                                                              ], CReportBase.AlignLeft),
                ( '4%',  [u'№ строки'                                                                                                                                             ], CReportBase.AlignCenter),
                ( '10%', [u'Код по МКБ-10 пересмотра'                                                                                                                              ], CReportBase.AlignCenter),
                ( '5%',  [u'Массой тела при рождении до 1000г (500-999г)',  u'Поступило пациентов в первые 0-6 дней после рождения'                                                ], CReportBase.AlignCenter),
                ( '5%',  [u'',                                              u'Из них умерло',                                       u'всего'                                       ], CReportBase.AlignCenter),
                ( '6%',  [u'',                                              u'',                                                    u'в том числе в первые 0-6 дней после рождения'], CReportBase.AlignCenter),
                ( '5%',  [u'Массой тела при рождении 1000г и более',        u'Поступило пациентов в первые 0-6 дней после рождения'                                                ], CReportBase.AlignCenter),
                ( '5%',  [u'',                                               u'Из них умерло',                                      u'всего'                                       ], CReportBase.AlignCenter),
                ( '6%',  [u'',                                              u'',                                                    u'в том числе в первые 0-6 дней после рождения'], CReportBase.AlignCenter)]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(0, 6, 1, 3)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 1, 2)

        while query.next():
            record = query.record()
            code    = forceString(record.value('MKB'))
            dead    = forceInt(record.value('dead'))
            deadAge = forceInt(record.value('deadAge'))

            for row in resultSet:
                if MKBinString(code, row[2]):
                    row[6] += 1
                    if dead:
                        row[7] += 1
                        if deadAge <= 6:
                            row[8] += 1

        for list in resultSet:
            i = table.addRow()
            for index, value in enumerate(list):
                table.setText(i, index, value)
        return doc