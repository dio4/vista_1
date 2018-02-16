# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.ActionInfo  import CActionInfo
from library.PrintInfo  import CInfoContext
from library.Utils      import forceInt, forceRef, forceString, getVal
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_EmergencyF40Setup import Ui_EmergencyF40SetupDialog
from Ui_EmergencyTalonSignal import Ui_EmergencyTalonSignalDialog


Rows2000 = [
            (u'Выполнено выездов', u'01'),
            (u'из них:\nк детям в возрасте 0-17 лет включительно', u'02'),
            (u'Число лиц, которым оказана медицинская помощь при выездах', u'03'),
            (u'из них:\nв сельских населенных пунктах', u'04'),
            (u'Число лиц, умерших в автомобиле скорой помощи(из стр. 3)', u'05'),
            (u'из них:\nдетей в возрасте 0-17 лет включительно', u'06'),
            (u'из них:\nв возрасте до 1 года', u'07'),
            (u'женщин в возрасте 55 лет и старше', u'08'),
            (u'мужчин в возрасте 60 лет и старше', u'09')
           ]

Rows2100 = [
            (u'Дети в возрасте 0-17 лет включительно', u'01'),
            (u'Взрослые(18 лет и старше)-всего', u'02'),
            (u'из них\nженщины в возрасте 55 лет и старше', u'03'),
            (u'мужчины в возрасте 60 лет и старше', u'04')
           ]

Rows2500 = [
            (u'-до 20 минут', u'01'),
            (u'-от 21 до 40 минут', u'02'),
            (u'-от 41 до 60 минут', u'03'),
            (u'-более 60 минут', u'04')
           ]

Rows2001 = [
            (u'Число больных с острым и повторным инфарктом миокарда (I21, I22)', u'1'),
            (u'с острыми цереброваскулярными болезнями, которым оказана скорая медицинская помощь (I60-I69)', u'2'),
            (u'Из числа больных с острым и повторным инфарктом миокарда и с острыми цереброваскулярными болезнями в автомобиле СМП проведено тромболизисов всего (I21, I22, I60-I69, Y44.5)', u'3'),
            (u'из них при остром и повторном инфаркте миокарда (I21, I22, Y44.5)', u'4'),
            (u'при острых цереброваскулярных болезнях (I60-I69, Y44.5)', u'5'),
            (u'Из числа больных с острым и повторным инфарктом миокарда и с острыми цереброваскулярнымиболезнями, число больных смерть которых наступила в автомобиле СМП (I21, I22, I60-I69)', u'6'),
            (u'Число безрезультатных выездов', u'7'),
            (u'Отказано за необоснованностью вызова', u'8'),
            (u'Число дорожно-транспортных происшествий(ДТП), на которые выезжали автомобили СМП', u'9'),
            (u'Число пострадавших в ДТП, которым оказана медицинская помощь', u'10'),
            (u'из них со смертельным исходом', u'11'),
            (u'из них смерть наступила в автомобиле СМП', u'12'),
            (u'Число выездов для медицинского обслуживания спортивных и культурно-массовых мероприятий(или общественных мероприятий)всего', u'13')
           ]

class CEmergencyF40SetupDialog(QtGui.QDialog, Ui_EmergencyF40SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))


    def params(self):
        result = {'begDate': self.edtBegDate.date(),
                  'endDate': self.edtEndDate.date()}
        return result


class CReportEmergencyF40(CReport):
    def __init__(self, parent = None):
        CReport.__init__(self, parent)
        self.clientDeath = 8


    def getSetupDialog(self, parent):
        result = CEmergencyF40SetupDialog(parent)
        result.setTitle(self.title())
        return result


class CReportEmergencyF402000(CReportEmergencyF40):
    def __init__(self, parent = None):
        CReportEmergencyF40.__init__(self, parent)


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        if begDate and endDate:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEmergencyCall = db.table('EmergencyCall')
            tableRBEventTypePurpose = db.table('rbEventTypePurpose')
            tableEventType = db.table('EventType')
            tableRBEmergencyDiseased = db.table('rbEmergencyDiseased')
            tableRBEmergencyDeath = db.table('rbEmergencyDeath')
            stmt13 = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(Event.id IS NOT NULL, 1, 0) AS A,
       IF(rbResult.code = '1' AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B,
       IF(rbResult.code = '1' AND EmergencyCall.disease = 1, 1, 0) AS C,
       IF(rbResult.code = '1' AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D,
       IF(Event.isPrimary = '4', 1, 0) AS E,
       IF(Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F,
       IF(EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G,

       IF(age(Client.birthDate, Event.setDate) <= 17, 1, 0) AS A2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND rbResult.code = '1' AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND rbResult.code = '1' AND EmergencyCall.disease = 1, 1, 0) AS C2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND rbResult.code = '1' AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND Event.isPrimary = '4', 1, 0) AS E2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F2,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G2,

       IF(rbResult.code = '1', 1, 0) AS A3,
       IF(rbResult.code = '1' AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B3,
       IF(rbResult.code = '1' AND EmergencyCall.disease = 1, 1, 0) AS C3,
       IF(rbResult.code = '1' AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D3,
       IF(rbResult.code = '1' AND Event.isPrimary = '4', 1, 0) AS E3,
       IF(rbResult.code = '1' AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F3,
       IF(rbResult.code = '1' AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G3
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
LEFT JOIN Client ON Client.id = Event.client_id
WHERE %s
GROUP BY Event.id'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate)
                    ]
            query13 = db.query(stmt13 % (db.joinAnd(cond)))
            eventIdList13 = []
            A = 0
            B = 0
            C = 0
            D = 0
            E = 0
            F = 0
            G = 0
            A2 = 0
            B2 = 0
            C2 = 0
            D2 = 0
            E2 = 0
            F2 = 0
            G2 = 0
            A3 = 0
            B3 = 0
            C3 = 0
            D3 = 0
            E3 = 0
            F3 = 0
            G3 = 0
            while query13.next():
                record = query13.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList13:
                    eventIdList13.append(eventId)
                    A += forceInt(record.value('A'))
                    B += forceInt(record.value('B'))
                    C += forceInt(record.value('C'))
                    D += forceInt(record.value('D'))
                    E += forceInt(record.value('E'))
                    F += forceInt(record.value('F'))
                    G += forceInt(record.value('G'))
                    A2 += forceInt(record.value('A2'))
                    B2 += forceInt(record.value('B2'))
                    C2 += forceInt(record.value('C2'))
                    D2 += forceInt(record.value('D2'))
                    E2 += forceInt(record.value('E2'))
                    F2 += forceInt(record.value('F2'))
                    G2 += forceInt(record.value('G2'))
                    A3 += forceInt(record.value('A3'))
                    B3 += forceInt(record.value('B3'))
                    C3 += forceInt(record.value('C3'))
                    D3 += forceInt(record.value('D3'))
                    E3 += forceInt(record.value('F3'))
                    G3 += forceInt(record.value('G3'))


            cond.append(tableRBEmergencyDiseased['code'].eq(3))
            stmt4 = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(rbResult.code = '1', 1, 0) AS A4,
       IF(rbResult.code = '1' AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B4,
       IF(rbResult.code = '1' AND EmergencyCall.disease = 1, 1, 0) AS C4,
       IF(rbResult.code = '1' AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D4,
       IF(rbResult.code = '1' AND Event.isPrimary = '4', 1, 0) AS E4,
       IF(rbResult.code = '1' AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F4,
       IF(rbResult.code = '1' AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G4

FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
LEFT JOIN Client ON Client.id = Event.client_id
LEFT JOIN rbEmergencyDiseased ON rbEmergencyDiseased.id = EmergencyCall.diseased_id
WHERE %s
GROUP BY Event.id'''
            query4 = db.query(stmt4 % (db.joinAnd(cond)))
            eventIdList4 = []
            A4 = 0
            B4 = 0
            C4 = 0
            D4 = 0
            E4 = 0
            F4 = 0
            G4 = 0
            queryTextParts = [forceString(query4.lastQuery())]
            while query4.next():
                record = query4.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList4:
                    eventIdList4.append(eventId)
                    A4 += forceInt(record.value('A4'))
                    B4 += forceInt(record.value('B4'))
                    C4 += forceInt(record.value('C4'))
                    D4 += forceInt(record.value('D4'))
                    E4 += forceInt(record.value('E4'))
                    F4 += forceInt(record.value('F4'))
                    G4 += forceInt(record.value('G4'))

            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableRBEmergencyDeath['code'].eq(3),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate)
                   ]
            stmt59 = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(Event.id IS NOT NULL, 1, 0) AS A5,
       IF(EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B5,
       IF(EmergencyCall.disease = 1, 1, 0) AS C5,
       IF((EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D5,
       IF(Event.isPrimary = '4', 1, 0) AS E5,
       IF(Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F5,
       IF(EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G5,

       IF(age(Client.birthDate, Event.setDate) <= 17, 1, 0) AS A6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND EmergencyCall.disease = 1, 1, 0) AS C6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND Event.isPrimary = '4', 1, 0) AS E6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F6,
       IF(age(Client.birthDate, Event.setDate) <= 17 AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G6,

       IF(age(Client.birthDate, Event.setDate) < 1, 1, 0) AS A7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND EmergencyCall.disease = 1, 1, 0) AS C7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND Event.isPrimary = '4', 1, 0) AS E7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F7,
       IF(age(Client.birthDate, Event.setDate) < 1 AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G7,

       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2, 1, 0) AS A8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND EmergencyCall.disease = 1, 1, 0) AS C8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND Event.isPrimary = '4', 1, 0) AS E8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F8,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2 AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G8,

       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1, 1, 0) AS A9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND EmergencyCall.accident_id IS NOT NULL, 1, 0) AS B9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND EmergencyCall.disease = 1, 1, 0) AS C9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND (EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS D9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND Event.isPrimary = '4', 1, 0) AS E9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND Event.isPrimary = '4' AND ( EmergencyCall.disease = 1 OR EmergencyCall.birth = 1 OR EmergencyCall.pregnancyFailure = 1), 1, 0) AS F9,
       IF(age(Client.birthDate, Event.setDate) >= 60 AND Client.sex = 1 AND EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS G9
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
LEFT JOIN Client ON Client.id = Event.client_id
LEFT JOIN rbEmergencyDeath ON rbEmergencyDeath.id = EmergencyCall.death_id
WHERE %s
GROUP BY Event.id
'''
            query59 = db.query(stmt59 % (db.joinAnd(cond)))
            queryTextParts.append(forceString(query59.lastQuery()))
            self.setQueryText(u'\n\n'.join(queryTextParts))
            eventIdList59 = []
            A5 = 0
            B5 = 0
            C5 = 0
            D5 = 0
            E5 = 0
            F5 = 0
            G5 = 0
            A6 = 0
            B6 = 0
            C6 = 0
            D6 = 0
            E6 = 0
            F6 = 0
            G6 = 0
            A7 = 0
            B7 = 0
            C7 = 0
            D7 = 0
            E7 = 0
            F7 = 0
            G7 = 0
            A8 = 0
            B8 = 0
            C8 = 0
            D8 = 0
            E8 = 0
            F8 = 0
            G8 = 0
            A9 = 0
            B9 = 0
            C9 = 0
            D9 = 0
            E9 = 0
            F9 = 0
            G9 = 0
            while query59.next():
                record = query59.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList59:
                    eventIdList59.append(eventId)
                    A5 += forceInt(record.value('A5'))
                    B5 += forceInt(record.value('B5'))
                    C5 += forceInt(record.value('C5'))
                    D5 += forceInt(record.value('D5'))
                    E5 += forceInt(record.value('E5'))
                    F5 += forceInt(record.value('F5'))
                    G5 += forceInt(record.value('G5'))
                    A6 += forceInt(record.value('A6'))
                    B6 += forceInt(record.value('B6'))
                    C6 += forceInt(record.value('C6'))
                    D6 += forceInt(record.value('D6'))
                    E6 += forceInt(record.value('E6'))
                    F6 += forceInt(record.value('F6'))
                    G6 += forceInt(record.value('G6'))
                    A7 += forceInt(record.value('A7'))
                    B7 += forceInt(record.value('B7'))
                    C7 += forceInt(record.value('C7'))
                    D7 += forceInt(record.value('D7'))
                    E7 += forceInt(record.value('E7'))
                    F7 += forceInt(record.value('F7'))
                    G7 += forceInt(record.value('G7'))
                    A8 += forceInt(record.value('A8'))
                    B8 += forceInt(record.value('B8'))
                    C8 += forceInt(record.value('C8'))
                    D8 += forceInt(record.value('D8'))
                    E8 += forceInt(record.value('E8'))
                    F8 += forceInt(record.value('F8'))
                    G8 += forceInt(record.value('G8'))
                    A9 += forceInt(record.value('A9'))
                    B9 += forceInt(record.value('B9'))
                    C9 += forceInt(record.value('C9'))
                    D9 += forceInt(record.value('D9'))
                    E9 += forceInt(record.value('E9'))
                    F9 += forceInt(record.value('F9'))
                    G9 += forceInt(record.value('G9'))

            callList3 = [A, A2, A3, A4, A5, A6, A7, A8, A9]
            callList4 = [B, B2, B3, B4, B5, B6, B7, B8, B9]
            callList5 = [C, C2, C3, C4, C5, C6, C7, C8, C9]
            callList6 = [D, D2, D3, D4, D5, D6, D7, D8, D9]
            callList7 = [E, E2, E3, E4, E5, E6, E7, E8, E9]
            callList8 = [F, F2, F3, F4, F5, F6, F7, F8, F9]
            callList9 = [G, G2, G3, G4, G5, G6, G7, G8, G9]
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Медицинская помощь при выездах\n(2000)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            self.Rows = [] + Rows2000
            cols = [('25%',[u'Показатели', u'', u'', u'1'], CReportBase.AlignLeft),
                    ('5%', [u'№ строки', u'', u'', u'2'], CReportBase.AlignLeft),
                    ('10%', [u'Всего', u'', u'', u'3'], CReportBase.AlignLeft),
                    ('10%', [u'из них:', u'оказание скорой медицинской помощи по поводу:', u'несчастных случаев', u'4'], CReportBase.AlignLeft),
                    ('10%', [u'', u'', u'внезапных заболеваний и состояний', u'5'], CReportBase.AlignLeft),
                    ('10%', [u'', u'', u'родов и патологии беременности', u'6'], CReportBase.AlignLeft),
                    ('10%', [u'', u'перевозка', u'всего', u'7'], CReportBase.AlignLeft),
                    ('10%', [u'', u'', u'из них больных, рожениц и родильниц', u'8'], CReportBase.AlignLeft),
                    ('10%', [u'Число госпитализированных(из гр.3)', u'', u'', u'9'], CReportBase.AlignLeft)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 3, 1) # 1
            table.mergeCells(0, 1, 3, 1) # 2
            table.mergeCells(0, 2, 3, 1) # 3
            table.mergeCells(0, 3, 1, 5) # 4
            table.mergeCells(1, 3, 1, 3) # 4
            table.mergeCells(1, 6, 1, 2) # 7
            for iRow, row in enumerate(self.Rows):
                i = table.addRow()
                for j in xrange(2):
                    table.setText(i, j, row[j])
                table.setText(i, 2, callList3[i - 4])
                table.setText(i, 3, callList4[i - 4])
                table.setText(i, 4, callList5[i - 4])
                table.setText(i, 5, callList6[i - 4])
                table.setText(i, 6, callList7[i - 4])
                table.setText(i, 7, callList8[i - 4])
                table.setText(i, 8, callList9[i - 4])
        return doc


class CReportEmergencyF402100(CReportEmergencyF40):
    def __init__(self, parent = None):
        CReportEmergencyF40.__init__(self, parent)


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        if begDate and endDate:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEmergencyCall = db.table('EmergencyCall')
            tableRBEventTypePurpose = db.table('rbEventTypePurpose')
            tableEventType = db.table('EventType')
            tableRBResult = db.table('rbResult')
            stmt = u'''SELECT Event.client_id AS clientId, Event.id AS eventId, IF(age(Client.birthDate, Event.setDate) <= 17, 1, 0) AS A,
       IF(age(Client.birthDate, Event.setDate) >= 18, 1, 0) AS B,
       IF(age(Client.birthDate, Event.setDate) >= 55 AND Client.sex = 2, 1, 0) AS C,
       IF(age(Client.birthDate, Event.setDate) >=60 AND Client.sex = 1, 1, 0) AS D
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
LEFT JOIN Client ON Client.id = Event.client_id
WHERE %s
GROUP BY Event.id'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableRBResult['code'].eq(1),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate)
                    ]
            query = db.query(stmt % (db.joinAnd(cond)))
            eventIdList = []
            A = 0
            B = 0
            C = 0
            D = 0
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList:
                    eventIdList.append(eventId)
                    A += forceInt(record.value('A'))
                    B += forceInt(record.value('B'))
                    C += forceInt(record.value('C'))
                    D += forceInt(record.value('D'))
            callList = [A, B, C, D]

            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Число лиц, которым оказана медицинская помощь при выездах\n(2100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            self.Rows = [] + Rows2100
            cols = [('45%',[u'Возрастные группы', u'1'], CReportBase.AlignLeft),
                    ('10%', [u'№ строки', u'2'], CReportBase.AlignLeft),
                    ('45%', [u'Число лиц, которым оказана медицинская помощь при выездах(из гр.3 стр.3 таб.2000)', u'3'], CReportBase.AlignLeft)
                   ]
            table = createTable(cursor, cols)
            for iRow, row in enumerate(self.Rows):
                i = table.addRow()
                for j in xrange(2):
                    table.setText(i, j, row[j])
                table.setText(i, 2, callList[i - 2])
        return doc


class CReportEmergencyF402500(CReportEmergencyF40):
    def __init__(self, parent = None):
        CReportEmergencyF40.__init__(self, parent)


    def build(self, params):
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        if begDate and endDate:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEmergencyCall = db.table('EmergencyCall')
            tableRBEventTypePurpose = db.table('rbEventTypePurpose')
            tableEventType = db.table('EventType')
            stmt = u'''SELECT
                            Event.id AS eventId,
                            IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '00:20:00', 1, 0) AS A,
                            IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '00:20:00'
                                    AND TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '00:40:00',
                                1, 0) AS B,
                            IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '00:40:00'
                                    AND TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '01:00:00',
                                1, 0) AS C,
                            IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '01:00:00', 1, 0) AS D,
                            IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '00:20:00', 1, 0) AS A2,
                            IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '00:20:00'
                                    AND TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '00:40:00',
                                1, 0) AS B2,
                            IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '00:40:00'
                                    AND TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '01:00:00',
                                1, 0) AS C2,
                            IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '01:00:00', 1, 0) AS D2
                        FROM Event
                        INNER JOIN EventType ON Event.eventType_id =  EventType.id
                        INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
                        INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
                        WHERE %s
                        GROUP BY Event.id'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    u'''(EmergencyCall.accident_id IS NULL
                            OR (EmergencyCall.accident_id IS NOT NULL
                                    AND EmergencyCall.accident_id IN (SELECT rbEmergencyAccident.id
                                                                        FROM rbEmergencyAccident
                                                                        WHERE rbEmergencyAccident.code != '3')
                                )
                        )''']
            query = db.query(stmt % (db.joinAnd(cond)))
            eventIdList = []
            A = 0
            B = 0
            C = 0
            D = 0
            A2 = 0
            B2 = 0
            C2 = 0
            D2 = 0
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList:
                    eventIdList.append(eventId)
                    A += forceInt(record.value('A'))
                    B += forceInt(record.value('B'))
                    C += forceInt(record.value('C'))
                    D += forceInt(record.value('D'))
                    A2 += forceInt(record.value('A2'))
                    B2 += forceInt(record.value('B2'))
                    C2 += forceInt(record.value('C2'))
                    D2 += forceInt(record.value('D2'))
            callList = [A, B, C, D]
            placeCallList = [A2, B2, C2, D2]
            stmtDTP = u'''SELECT Event.id AS eventId,
                                IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '00:20:00', 1, 0) AS A,
                                IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '00:20:00'
                                        AND TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '00:40:00',
                                    1, 0) AS B,
                                IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '00:40:00'
                                        AND TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) <= '01:00:00',
                                    1, 0) AS C,
                               IF(TIMEDIFF(EmergencyCall.arrivalDate, EmergencyCall.departureDate) > '01:00:00', 1, 0) AS D,
                               IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '00:20:00', 1, 0) AS A2,
                               IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '00:20:00'
                                        AND TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '00:40:00',
                                    1, 0) AS B2,
                               IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '00:40:00'
                                        AND TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) <= '01:00:00',
                                    1, 0) AS C2,
                               IF(TIMEDIFF(EmergencyCall.finishServiceDate, EmergencyCall.arrivalDate) > '01:00:00', 1, 0) AS D2
                        FROM Event
                        INNER JOIN EventType ON Event.eventType_id =  EventType.id
                        INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
                        INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
                        WHERE %s
                        GROUP BY Event.id'''
            condDTP = [tableRBEventTypePurpose['code'].eq(7),
                       tableEvent['deleted'].eq(0),
                       tableEmergencyCall['deleted'].eq(0),
                       tableEventType['deleted'].eq(0),
                       tableEvent['setDate'].isNotNull(),
                       tableEvent['execDate'].isNotNull(),
                       tableEvent['setDate'].ge(begDate),
                       tableEvent['setDate'].lt(endDate),
                       u'''(EmergencyCall.accident_id IS NOT NULL
                                AND EmergencyCall.accident_id IN (SELECT rbEmergencyAccident.id
                                                                    FROM rbEmergencyAccident
                                                                    WHERE rbEmergencyAccident.code = '3')
                            )''']
            queryDTP = db.query(stmtDTP % (db.joinAnd(condDTP)))
            eventIdDTPList = []
            ADTP = 0
            BDTP = 0
            CDTP = 0
            DDTP = 0
            ADTP2 = 0
            BDTP2 = 0
            CDTP2 = 0
            DDTP2 = 0
            while queryDTP.next():
                recordDTP = queryDTP.record()
                eventId = forceRef(recordDTP.value('eventId'))
                if eventId not in eventIdDTPList:
                    eventIdDTPList.append(eventId)
                    ADTP += forceInt(recordDTP.value('A'))
                    BDTP += forceInt(recordDTP.value('B'))
                    CDTP += forceInt(recordDTP.value('C'))
                    DDTP += forceInt(recordDTP.value('D'))
                    ADTP2 += forceInt(recordDTP.value('A2'))
                    BDTP2 += forceInt(recordDTP.value('B2'))
                    CDTP2 += forceInt(recordDTP.value('C2'))
                    DDTP2 += forceInt(recordDTP.value('D2'))
            callDTPList = [ADTP, BDTP, CDTP, DDTP]
            placeCallDTPList = [ADTP2, BDTP2, CDTP2, DDTP2]
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Число выездов бригад скорой медицинской помощи по времени доезда и затраченному на один выезд\n(2500)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            self.Rows = [] + Rows2500
            cols = [('35%',[u'Показатели', u'', u'', u'1'], CReportBase.AlignLeft),
                    ('5%',[u'№ строки', u'', u'', u'2'], CReportBase.AlignLeft),
                    ('15%',[u'Число выездов бригад скорой медицинской помощи по времени:', u'доезда', u'до места вызова', u'3'], CReportBase.AlignLeft),
                    ('15%',[u'', u'', u'до места дорожно-транспортного происшествия', u'4'], CReportBase.AlignLeft),
                    ('15%',[u'', u'затраченному на один выезд', u'на вызов', u'5'], CReportBase.AlignLeft),
                    ('15%',[u'', u'', u'на дорожно-транспортное происшествие', u'6'], CReportBase.AlignLeft)
                   ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 3, 1) # 1
            table.mergeCells(0, 1, 3, 1) # 2
            table.mergeCells(0, 2, 1, 4) # 3
            table.mergeCells(1, 2, 1, 2) # 3
            table.mergeCells(1, 4, 1, 2) # 5
            for iRow, row in enumerate(self.Rows):
                i = table.addRow()
                for j in xrange(2):
                    table.setText(i, j, row[j])
                table.setText(i, 2, callList[i - 4])
                table.setText(i, 4, placeCallList[i - 4])
                table.setText(i, 3, callDTPList[i - 4])
                table.setText(i, 5, placeCallDTPList[i - 4])
        return doc


class CReportEmergencyF402001(CReportEmergencyF40):
    def __init__(self, parent = None):
        CReportEmergencyF40.__init__(self, parent)


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        if begDate and endDate:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEmergencyCall = db.table('EmergencyCall')
            tableRBEventTypePurpose = db.table('rbEventTypePurpose')
            tableEventType = db.table('EventType')
            tableRBEmergencyAccident = db.table('rbEmergencyAccident')
            tableRBEmergencyCauseCall = db.table('rbEmergencyCauseCall')
            tableRBResult = db.table('rbResult')
            tableDiagnosis = db.table('Diagnosis')
            tableRBDiagnosisType = db.table('rbDiagnosisType')
            tableRBEmergencyDeath = db.table('rbEmergencyDeath')
            tableRBDiseaseCharacter = db.table('rbDiseaseCharacter')
            stmt = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(rbResult.code = '11', 1, 0) AS A,
       IF(rbResult.code = '4', 1, 0) AS B
FROM Event
INNER JOIN EventType ON Event.eventType_id =  EventType.id
INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
INNER JOIN rbResult ON rbResult.id = Event.result_id
WHERE %s
GROUP BY Event.id'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate)
                   ]
            query = db.query(stmt % (db.joinAnd(cond)))
            eventIdList = []
            A = 0
            B = 0
            C = 0
            D = 0
            E = 0
            F = 0
            self.setQueryText(forceString(query.lastQuery()))
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList:
                    eventIdList.append(eventId)
                    A += forceInt(record.value('A'))
                    B += forceInt(record.value('B'))
            stmt2 = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(Event.id IS NOT NULL, 1, 0) AS C,
       IF(rbResult.code = '1', 1, 0) AS D,
       IF(rbResult.code = '1'
AND EmergencyCall.death_id IN (SELECT DISTINCT rbEmergencyDeath.id FROM rbEmergencyDeath WHERE (rbEmergencyDeath.code = '2' OR rbEmergencyDeath.code = '3')), 1, 0) AS E,
       IF(rbResult.code = '1'
AND EmergencyCall.death_id IN (SELECT DISTINCT rbEmergencyDeath.id FROM rbEmergencyDeath WHERE (rbEmergencyDeath.code = '3')), 1, 0) AS F
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
LEFT JOIN rbEmergencyAccident ON rbEmergencyAccident.id = EmergencyCall.accident_id
WHERE %s
GROUP BY Event.id'''
            cond.append(tableRBEmergencyAccident['code'].eq(3))
            query2 = db.query(stmt2 % (db.joinAnd(cond)))
            eventIdList2 = []
            while query2.next():
                record = query2.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList2:
                    eventIdList2.append(eventId)
                    C += forceInt(record.value('C'))
                    D += forceInt(record.value('D'))
                    E += forceInt(record.value('E'))
                    F += forceInt(record.value('F'))

            stmt3 = u'''SELECT Event.client_id AS clientId, Event.id AS eventId,
       IF(Event.id IS NOT NULL, 1, 0) AS G
FROM Event
INNER JOIN EventType ON Event.eventType_id =  EventType.id
INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
INNER JOIN rbEmergencyCauseCall ON rbEmergencyCauseCall.id = EmergencyCall.causeCall_id
WHERE %s
GROUP BY Event.id'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBEmergencyCauseCall['typeCause'].eq(1)
                   ]
            query3 = db.query(stmt3 % (db.joinAnd(cond)))
            eventIdList3 = []
            G = 0
            while query3.next():
                record = query3.record()
                eventId = forceRef(record.value('eventId'))
                if eventId not in eventIdList3:
                    eventIdList3.append(eventId)
                    G += forceInt(record.value('G'))

            H = 0
            stmtIM = u'''SELECT COUNT(Event.id)
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
RIGHT JOIN Diagnostic ON Diagnostic.event_id = Event.id
LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBResult['code'].eq(1),
                    tableRBDiagnosisType['code'].eq(2),
                    db.joinOr([tableDiagnosis['MKB'].like(u'I21%'),
                               tableDiagnosis['MKB'].like(u'I22%')])]
            queryIM = db.query(stmtIM % (db.joinAnd(cond)))
            if queryIM.first():
                H = queryIM.value(0).toInt()[0]
            I = 0
            stmtZB = u'''SELECT COUNT(Event.id)
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBResult['code'].eq(1),
                    tableRBDiagnosisType['code'].eq(2),
                    tableDiagnosis['MKB'].like(u'I6%'),
                    db.joinOr([tableRBDiseaseCharacter['code'].eq(1),
                               tableRBDiseaseCharacter['code'].eq(4)])]
            queryZB = db.query(stmtZB % (db.joinAnd(cond)))
            if queryZB.first():
                I = queryZB.value(0).toInt()[0]
            J = 0
            stmtIMDeath = u'''SELECT COUNT(Event.id)
FROM Event
INNER JOIN EventType ON Event.eventType_id =  EventType.id
INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
INNER JOIN rbEmergencyDeath ON rbEmergencyDeath.id = EmergencyCall.death_id
INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
INNER JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBDiagnosisType['code'].eq(2),
                    tableRBEmergencyDeath['code'].eq(3),
                    db.joinOr([tableDiagnosis['MKB'].like(u'I21%'),
                               tableDiagnosis['MKB'].like(u'I22%'),
                               db.joinAnd([tableDiagnosis['MKB'].like(u'I6%'),
                                           db.joinOr([tableRBDiseaseCharacter['code'].eq(1),
                                                      tableRBDiseaseCharacter['code'].eq(4)])])])]
            queryIMDeath  = db.query(stmtIMDeath % (db.joinAnd(cond)))
            if queryIMDeath.first():
                J = queryIMDeath.value(0).toInt()[0]

            K = 0
            stmtTL = u'''SELECT COUNT(Event.id)
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBResult['code'].eq(1), tableRBDiagnosisType['code'].eq(2),
                    tableDiagnosis['MKBEx'].like(u'Y44.5'),
                    db.joinOr([tableDiagnosis['MKB'].like(u'I21%'),
                               tableDiagnosis['MKB'].like(u'I22%'),
                               db.joinAnd([tableDiagnosis['MKB'].like(u'I6%'),
                                           db.joinOr([tableRBDiseaseCharacter['code'].eq(1),
                                                      tableRBDiseaseCharacter['code'].eq(4)])])])]
            queryTL = db.query(stmtTL % (db.joinAnd(cond)))
            if queryTL.first():
                K = queryTL.value(0).toInt()[0]

            K1 = 0
            stmtTL1 = u'''SELECT COUNT(Event.id)
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBResult['code'].eq(1),
                    tableRBDiagnosisType['code'].eq(2),
                    tableDiagnosis['MKBEx'].like(u'Y44.5'),
                    db.joinOr([tableDiagnosis['MKB'].like(u'I21%'),
                               tableDiagnosis['MKB'].like(u'I22%')])]
            queryTL1 = db.query(stmtTL1 % (db.joinAnd(cond)))
            if queryTL1.first():
                K1 = queryTL1.value(0).toInt()[0]

            K2 = 0
            stmtTL2 = u'''SELECT COUNT(Event.id)
FROM Event
LEFT JOIN EventType ON Event.eventType_id =  EventType.id
LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
LEFT JOIN rbResult ON rbResult.id = Event.result_id
INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id
LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id
LEFT JOIN rbDiseaseCharacter ON rbDiseaseCharacter.id = Diagnostic.character_id
WHERE %s'''
            cond = [tableRBEventTypePurpose['code'].eq(7),
                    tableEvent['deleted'].eq(0),
                    tableEmergencyCall['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableDiagnosis['deleted'].eq(0),
                    tableEvent['setDate'].isNotNull(),
                    tableEvent['execDate'].isNotNull(),
                    tableEvent['setDate'].ge(begDate),
                    tableEvent['setDate'].lt(endDate),
                    tableRBResult['code'].eq(1), tableRBDiagnosisType['code'].eq(2),
                    tableDiagnosis['MKBEx'].like(u'Y44.5'),
                    db.joinAnd([tableDiagnosis['MKB'].like(u'I6%'),
                                db.joinOr([tableRBDiseaseCharacter['code'].eq(1),
                                           tableRBDiseaseCharacter['code'].eq(4)])])]
            queryTL2 = db.query(stmtTL2 % (db.joinAnd(cond)))
            if queryTL2.first():
                K2 = queryTL2.value(0).toInt()[0]

            callList = [H, I, K, K1, K2, J, A, B, C, D, E, F, G]
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Медицинская помощь при выездах\n(2001)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            self.Rows = [] + Rows2001
            cols = [('70%',[u'Показатели', u'1'], CReportBase.AlignLeft),
                    ('10%',[u'№ строки', u'2'], CReportBase.AlignLeft),
                    ('20%',[u'', u'3'], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            for iRow, row in enumerate(self.Rows):
                i = table.addRow()
                for j in xrange(2):
                    table.setText(i, j, row[j])
                table.setText(i, 2, callList[i - 2])
        return doc


class CReportEmergencyAdditionally(CReportEmergencyF40):
    def __init__(self, parent = None):
        CReportEmergencyF40.__init__(self, parent)


    def build(self, params):
        db = QtGui.qApp.db
        begDate = getVal(params, 'begDate', QtCore.QDate())
        endDate = getVal(params, 'endDate', QtCore.QDate())
        if begDate and endDate:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEmergencyCall = db.table('EmergencyCall')
            tableRBEventTypePurpose = db.table('rbEventTypePurpose')
            tableEventType = db.table('EventType')
            tableRBEmergencyCauseCall = db.table('rbEmergencyCauseCall')
            def getDataCauseCall(causeCallId):
                A = 0
                B = 0
                C = 0
                D = 0
                if causeCallId:
                    stmt = u'''SELECT EmergencyCall.causeCall_id, rbEmergencyCauseCall.code, rbEmergencyCauseCall.name, rbEmergencyCauseCall.typeCause,
               IF(Event.id IS NOT NULL, 1, 0) AS A,
               IF(rbResult.code = '1', 1, 0) AS B,
               IF(EmergencyCall.resultCall_id IN (SELECT DISTINCT rbEmergencyResult.id FROM rbEmergencyResult WHERE rbEmergencyResult.code = '4'), 1, 0) AS C,
               IF(EmergencyCall.death_id IN (SELECT DISTINCT rbEmergencyDeath.id FROM rbEmergencyDeath WHERE (rbEmergencyDeath.code = '1' OR rbEmergencyDeath.code = '2' OR rbEmergencyDeath.code = '3')), 1, 0) AS D
        FROM Event
        LEFT JOIN EventType ON Event.eventType_id =  EventType.id
        LEFT JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
        LEFT JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
        LEFT JOIN rbResult ON rbResult.id = Event.result_id
        LEFT JOIN rbEmergencyCauseCall ON rbEmergencyCauseCall.id = EmergencyCall.causeCall_id
        WHERE %s
        GROUP BY Event.id
        ORDER BY EmergencyCall.causeCall_id'''
                    cond = [tableRBEventTypePurpose['code'].eq(7),
                            tableEvent['deleted'].eq(0),
                            tableEmergencyCall['deleted'].eq(0),
                            tableEventType['deleted'].eq(0),
                            tableRBEmergencyCauseCall['id'].eq(causeCallId),
                            tableEvent['setDate'].isNotNull(),
                            tableEvent['execDate'].isNotNull(),
                            tableEvent['setDate'].ge(begDate),
                            tableEvent['setDate'].lt(endDate)
                           ]
                    query = db.query(stmt % (db.joinAnd(cond)))
                    eventIdList = []
                    while query.next():
                        record = query.record()
                        eventId = forceRef(record.value('eventId'))
                        if eventId not in eventIdList:
                            eventIdList.append(eventId)
                            A += forceInt(record.value('A'))
                            B += forceInt(record.value('B'))
                            C += forceInt(record.value('C'))
                            D += forceInt(record.value('D'))
                    return [A, B, C, D]
                return None

            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Сводка о вызовах СМП\n')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('30%',[u'Повод к вызову', u'1'], CReportBase.AlignLeft),
                    ('10%',[u'№ строки', u'2'], CReportBase.AlignLeft),
                    ('15%',[u'Кол-во вызовов всего', u'3'], CReportBase.AlignLeft),
                    ('15%',[u'Обслужено', u'4'], CReportBase.AlignLeft),
                    ('15%',[u'Госпитализированно', u'5'], CReportBase.AlignLeft),
                    ('15%',[u'Умерло', u'6'], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            stmtCauseCall = u'''SELECT rbEmergencyCauseCall.* FROM rbEmergencyCauseCall'''
            queryCauseCall = db.query(stmtCauseCall)
            causeCallIdList = []
            cnt = 1
            self.setQueryText(forceString(queryCauseCall.lastQuery()))
            while queryCauseCall.next():
                recordCauseCall = queryCauseCall.record()
                causeCallId = forceRef(recordCauseCall.value('id'))
                if causeCallId not in causeCallIdList:
                    causeCallIdList.append(causeCallId)
                    dataCauseCall = getDataCauseCall(causeCallId)
                    if dataCauseCall and (1 in dataCauseCall):
                        causeCallCode = forceString(recordCauseCall.value('code'))
                        causeCallName = forceString(recordCauseCall.value('name'))
                        causeCallType = forceInt(recordCauseCall.value('typeCause'))
                        i = table.addRow()
                        table.setText(i, 0, u'обслуживание общ.мероприятия: ' if causeCallType else u'вызов: ' +causeCallCode + u' ' + causeCallName)
                        table.setText(i, 1, cnt)
                        table.setText(i, 2, dataCauseCall[0])
                        table.setText(i, 3, dataCauseCall[1])
                        table.setText(i, 4, dataCauseCall[2])
                        table.setText(i, 5, dataCauseCall[3])
                        cnt += 1
        return doc


class CEmergencyTalonSignalDialog(QtGui.QDialog, Ui_EmergencyTalonSignalDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(currentDate.addDays(-1))
        self.edtBegTime.setTime(QtCore.QTime(0, 0))
        self.edtEndTime.setTime(QtCore.QTime(23, 59))


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(getVal(params, 'begDateTalonSignal', currentDate.addDays(-1)))
        self.edtBegTime.setTime(getVal(params, 'begTime', QtCore.QTime(0, 0)))
        self.edtEndTime.setTime(getVal(params, 'endTime', QtCore.QTime(23, 59)))
        self.cmbTypeOrder.setCurrentIndex(getVal(params, 'emergencyOrder', None))
        self.chkWriteMKB.setChecked(params.get('isWriteMKB', False))


    def params(self):
        result = {'begDateTalonSignal': self.edtBegDate.date(),
                  'begTime': self.edtBegTime.time(),
                  'endTime': self.edtEndTime.time(),
                  'emergencyOrder': self.cmbTypeOrder.currentIndex(),
                  'isWriteMKB': self.chkWriteMKB.isChecked()}
        return result


class CReportEmergencyTalonSignal(CReport):
    def __init__(self, parent = None):
        CReport.__init__(self, parent)
        self.clientDeath = 8


    def getSetupDialog(self, parent):
        result = CEmergencyTalonSignalDialog(parent)
        result.setTitle(self.title())
        return result


    def dumpParams(self, cursor, params):
        description = []
        typeOrder = [u'не задано', u'первичный', u'повторный', u'активное посещение', u'перевозка', u'амбулаторно']
        currentDate = QtCore.QDate.currentDate()
        begDateReport = params.get('begDateTalonSignal', currentDate.addDays(-1))
        begTime = params.get('begTime', QtCore.QTime())
        endTime = params.get('endTime', QtCore.QTime())
        if begDateReport:
           description.append(u'за дату: ' + forceString(begDateReport))

        timeRangeString = u''
        if begTime:
            timeRangeString += u' с '+forceString(begTime.toString('hh:mm'))
        if endTime:
            timeRangeString += u' по '+forceString(endTime.toString('hh:mm'))
        description.append(u'за период' + timeRangeString)
        emergencyOrder = params.get('emergencyOrder', 0)
        description.append(u'Вызов: ' + forceString(typeOrder[emergencyOrder]))
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableEmergencyCall = db.table('EmergencyCall')
        tableRBEventTypePurpose = db.table('rbEventTypePurpose')
        tableEventType = db.table('EventType')
        tableClient = db.table('Client')
        currentDate = QtCore.QDate.currentDate()
        begDateReport = getVal(params, 'begDateTalonSignal', currentDate.addDays(-1))
        begTime = getVal(params, 'begTime', QtCore.QTime())
        begDateTime = QtCore.QDateTime(begDateReport, begTime)
        endTime = getVal(params, 'endTime', QtCore.QTime())
        endDateTime = QtCore.QDateTime(begDateReport, endTime)
        emergencyOrder = getVal(params, 'emergencyOrder', 0)
        isWriteMKB = params.get('isWriteMKB', False)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сигнальный талон')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        stmt = u'''SELECT Event.id AS eventId,
                            vrbPersonWithSpeciality.name AS personName,
                            EmergencyCall.numberCardCall,
                            EmergencyCall.begDate AS begDateCall,
                            Client.id AS clientId,
                            Client.lastName,
                            Client.firstName,
                            Client.patrName,
                            Client.birthDate,
                            age(Client.birthDate, Event.setDate) AS clientAge,
                            Client.SNILS,
                            getClientPolicy(Client.id, 1) AS policyName,
                            getClientLocAddress(Client.id) AS locAddress,
                            getClientRegAddress(Client.id) AS regAddress
                    FROM Event
                    INNER JOIN EventType ON Event.eventType_id =  EventType.id
                    INNER JOIN rbEventTypePurpose ON EventType.purpose_id = rbEventTypePurpose.id
                    INNER JOIN EmergencyCall ON EmergencyCall.event_id = Event.id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
                    WHERE %s
                    GROUP BY Event.id'''
        cond = [tableRBEventTypePurpose['code'].eq(7),
                tableEvent['deleted'].eq(0),
                tableEmergencyCall['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tableClient['deleted'].eq(0),
                tableEvent['setDate'].isNotNull(),
                tableEvent['setDate'].ge(begDateTime),
                tableEvent['setDate'].lt(endDateTime),
                tableEmergencyCall['begDate'].isNotNull(),
                tableEmergencyCall['begDate'].ge(begDateTime),
                tableEmergencyCall['begDate'].lt(endDateTime)
               ]
        if emergencyOrder:
            cond.append(tableEvent['isPrimary'].eq(emergencyOrder))
        query = db.query(stmt % (db.joinAnd(cond)))
        cols = [('25%',[u'Вызов'], CReportBase.AlignLeft),
                ('25%',[u'Пациент'], CReportBase.AlignLeft),
                ('25%',[u'Диагноз'], CReportBase.AlignLeft),
                ('25%',[u'Лечение'], CReportBase.AlignLeft),
               ]
        table = createTable(cursor, cols)
        eventIdList = []
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            if eventId not in eventIdList:
                eventIdList.append(eventId)
                i = table.addRow()
                numberCardCall = forceString(record.value('numberCardCall'))
                begDateCall = forceString(record.value('begDateCall'))
                personName = forceString(record.value('personName'))
                gr1 = u'номер карты: %s, время приема вызова: %s, ФИО врача: %s'%(numberCardCall, begDateCall, personName)
                table.setText(i, 0, gr1)
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                birthDate = forceString(record.value('birthDate'))
                clientAge = forceString(record.value('clientAge'))
                locAddress = forceString(record.value('locAddress'))
                regAddress = forceString(record.value('regAddress'))
                policyName = forceString(record.value('policyName'))
                clientId = forceString(record.value('clientId'))
                FIO = lastName + u' ' + firstName + u' ' + patrName
                gr2 = u'ФИО пациента: %s, д/р %s(%s), адреса: регистрации %s и проживания %s, полис: %s, код: %s'%(FIO, birthDate, clientAge, regAddress, locAddress, policyName, clientId)
                table.setText(i, 1, gr2)

                stmtDiagnosisEmergency = u'''SELECT Event.id AS eventId,
                                                    Action.id AS actionId
                                            FROM Event
                                            INNER JOIN Action ON Action.event_id = Event.id
                                            INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                                            WHERE Event.id = %d AND ActionType.flatCode LIKE 'diagnosisEmergency\''''% eventId

                stmtAction = u"""SELECT Event.id AS eventId,
                                        Action.id AS actionId
                                    FROM Event
                                    INNER JOIN Action ON Action.event_id = Event.id
                                    INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                                    WHERE ActionType.class = 2 AND Event.id = %d AND ActionType.flatCode NOT LIKE 'diagnosisEmergency'
                                    """ % eventId

                for column, stmt in [(2, stmtDiagnosisEmergency),
                                     (3, stmtAction)]:
                    gr3 = u''
                    if column == 2 and isWriteMKB:
                        stmtMKB = u'''SELECT
                                            Event.id AS eventId,
                                            Diagnosis.MKB, Diagnosis.MKBEx,
                                            rbDiagnosisType.name,
                                            Diagnosis.diagnosisType_id,
                                            (SELECT DISTINCT DiagName FROM MKB_Tree WHERE DiagID LIKE SUBSTR(Diagnosis.MKB, 1, 5)) AS nameMKB,
                                            (SELECT DISTINCT DiagName FROM MKB_Tree WHERE DiagID LIKE SUBSTR(Diagnosis.MKBEx, 1, 5)) AS nameMKBEx
                                        FROM Event
                                        INNER JOIN Diagnostic ON Event.`id`=Diagnostic.`event_id`
                                        INNER JOIN Diagnosis ON Diagnostic.`diagnosis_id`=Diagnosis.`id`
                                        INNER JOIN rbDiagnosisType ON Diagnostic.`diagnosisType_id`=rbDiagnosisType.`id`
                                        WHERE Event.deleted = 0 AND Event.id = %d
                                        GROUP BY Event.id
                                        ORDER BY Diagnosis.diagnosisType_id'''% eventId
                        queryMKB = db.query(stmtMKB)
                        strMKB = u''
                        while queryMKB.next():
                            recordMKB = queryMKB.record()
                            MKB = forceString(recordMKB.value('MKB'))
                            MKBEx = forceString(recordMKB.value('MKBEx'))
                            nameMKB = forceString(recordMKB.value('nameMKB'))
                            nameMKBEx = forceString(recordMKB.value('nameMKBEx'))
                            name = forceString(recordMKB.value('name'))
                            if MKBEx:
                                mkbString = u' + %s(%s + %s)'%(MKBEx, nameMKB, nameMKBEx)
                            else:
                                mkbString = u'(%s)'% nameMKB
                            strMKB += u'%s %s %s\n'%(name, MKB, mkbString)
                        gr3 = u'%s'% strMKB
                    queryAction = db.query(stmt)
                    context = CInfoContext()
                    strAction = u''
                    while queryAction.next():
                        recordAction = queryAction.record()
                        actionId = forceRef(recordAction.value('actionId'))
                        actionInfo = CActionInfo(context, actionId)
                        nameAction = u' ' + forceString(actionInfo.name)
                        strAction += nameAction + u': '
                        for props in actionInfo:
                            strAction += u' ' + forceString(props.name)
                            strAction += u' - ' + forceString(props.value)
                        strAction += u'\n'
                    table.setText(i, column, strAction + gr3)
        return doc
