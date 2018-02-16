# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceString

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportHospitalBeds import Ui_ReportHospitalBegs


def setDateAllBeds(begDate, endDate):

    db = QtGui.qApp.db
    tableEvent = db.table('Event')

    cond = [tableEvent['setDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate)]

    stmt = u'''SELECT count(ReceivedAction.id) AS received
             , count(ReceivedEvent.id) AS receivedDS
             , sum(if(ReceivedClientAddress.isVillager = 1 OR isClientVillager(ReceivedClient.id) = 1, 1, 0)) AS receivedVillager
             , count(if(timestampdiff(YEAR, ReceivedClient.`birthDate`, date(ReceivedEvent.setDate)) < 17, ReceivedClient.id, NULL)) AS receivedBefore17
             , count(if(timestampdiff(YEAR, ReceivedClient.`birthDate`, date(ReceivedEvent.setDate)) >= 60, ReceivedEvent.client_id, NULL)) AS receivedAfter60
             , count(apt_movingFrom.id) AS movingFrom
             , count(apt_movingInto.id) AS movingInto
             , count(DISTINCT LeavedAction.id) AS leaved
             , count(LeavedEvent.id) AS leavedDS
             , count(DISTINCT rbResult.id) AS death
             , count(ConsidedAction.id) AS consided
             , sum(datediff(Event.execDate, Event.setDate)) AS days
             , count(Event.execDate) AS execDays
             , count(DISTINCT if(Event.order = 2, Event.id, NULL)) orde
        FROM
          Event
        INNER JOIN EventType
        ON Event.eventType_id = EventType.id AND EventType.code = '01'
        INNER JOIN Action
        ON Action.event_id = Event.id AND Action.deleted = 0

        LEFT JOIN ActionType act_received
        ON act_received.id = Action.actionType_id AND act_received.flatCode LIKE 'received%%'
        LEFT JOIN Action ReceivedAction
        ON ReceivedAction.event_id = Action.event_id AND ReceivedAction.deleted = 0 AND ReceivedAction.actionType_id = act_received.id
        LEFT JOIN Event ReceivedEvent
        ON ReceivedAction.event_id = ReceivedEvent.id AND ReceivedEvent.deleted = 0 AND ReceivedEvent.externalId LIKE 'д%%'
        LEFT JOIN Client ReceivedClient
        ON ReceivedClient.id = ReceivedEvent.client_id
        LEFT JOIN ClientAddress ReceivedClientAddress
        ON ReceivedClient.id = ReceivedClientAddress.client_id

        LEFT JOIN ActionType act_moving
        ON act_moving.id = Action.actionType_id AND act_moving.flatCode LIKE 'moving%%'
        LEFT JOIN Action MovingAction
        ON MovingAction.event_id = Action.event_id AND MovingAction.deleted = 0 AND MovingAction.actionType_id = act_moving.id
        LEFT JOIN ActionProperty ap_movingFrom
        ON ap_movingFrom.action_id = MovingAction.id
        LEFT JOIN ActionPropertyType apt_movingFrom
        ON apt_movingFrom.id = ap_movingFrom.type_id AND apt_movingFrom.name = 'Переведен из отделения'
        LEFT JOIN ActionProperty ap_movingInto
        ON ap_movingInto.action_id = MovingAction.id
        LEFT JOIN ActionPropertyType apt_movingInto
        ON apt_movingInto.id = ap_movingInto.type_id AND apt_movingInto.name = 'Переведен в отделение'

        LEFT JOIN ActionType act_leaved
        ON act_leaved.id = Action.actionType_id AND act_leaved.flatCode LIKE 'leaved%%'
        LEFT JOIN Action LeavedAction
        ON LeavedAction.event_id = Action.event_id AND LeavedAction.deleted = 0 AND LeavedAction.actionType_id = act_leaved.id
        LEFT JOIN Event LeavedEvent
        ON LeavedAction.event_id = LeavedEvent.id AND LeavedEvent.deleted = 0 AND LeavedEvent.externalId LIKE 'д%%'

        LEFT JOIN rbResult
        ON Event.result_id = rbResult.id AND rbResult.code IN ('105', '106')

        LEFT JOIN ActionType act_consided
        ON act_consided.id = Action.actionType_id AND act_consided.flatCode LIKE 'received%%'
        LEFT JOIN Action ConsidedAction
        ON ConsidedAction.event_id = Action.event_id AND ConsidedAction.actionType_id = act_consided.id AND ConsidedAction.deleted = 0 AND ConsidedAction.id NOT IN (
        SELECT act.id
        FROM
          Action act
        INNER JOIN ActionType actType
        WHERE
          act.deleted = 0
          AND actType.flatCode = 'leaved')

        WHERE
          %s
    ''' % db.joinAnd(cond)

    return db.query(stmt)

class CReportHospitalBeds(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Коечный фонд')

    def getSetupDialog(self, parent):
        result = CHospitalBeds(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        query = setDateAllBeds(begDate, endDate)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('20%',  [u'Профиль'                                          ], CReportBase.AlignLeft),
            ('10%',  [u'Число коек',             u'На конец периода'      ], CReportBase.AlignRight),
            ( '10%', [u'',                       u'Среднеежемесечно'      ], CReportBase.AlignRight),
            ( '10%', [u'Поступило больных всего'                          ], CReportBase.AlignRight),
            ( '10%', [u'В том числе',            u'Из дневного стационара'], CReportBase.AlignRight),
            ( '10%', [u'',                       u'Сельских жителей'      ], CReportBase.AlignRight),
            ( '10%', [u'',                       u'Детей до 17'           ], CReportBase.AlignRight),
            ( '10%', [u'',                       u'60 лет и старше'       ], CReportBase.AlignRight),
            ( '10%', [u'Переведено',             u'Из др. отделений      '], CReportBase.AlignRight),
            ( '10%', [u'',                       u'В др.отделения'        ], CReportBase.AlignRight),
            ( '10%', [u'Выписано больных всего'                           ], CReportBase.AlignRight),
            ( '10%', [u'В т.ч. дневной стационар'                         ], CReportBase.AlignRight),
            ( '10%', [u'Умерло'                                           ], CReportBase.AlignRight),
            ( '10%', [u'Состоит больных на конец периода'                 ], CReportBase.AlignRight),
            ( '10%', [u'Проведено койко дней'                             ], CReportBase.AlignRight),
            ( '10%', [u'Число койкодней закрытия'                         ], CReportBase.AlignRight),
            ( '10%', [u'Поступило иногородних больных'                    ], CReportBase.AlignRight),
            ( '10%', [u'Поступило экстренных больных'                     ], CReportBase.AlignRight)]
        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1) #Профиль
        table.mergeCells(0, 1, 1, 2) #Число коек
        table.mergeCells(0, 3, 2, 1) #Поступило больных всего
        table.mergeCells(0, 4, 1, 4) #В том числе
        table.mergeCells(0, 8, 1, 2) #Переведено
        table.mergeCells(0, 10, 2, 1) #Выписано больных всего
        table.mergeCells(0, 11, 2, 1) #В т.ч. дневной стационар
        table.mergeCells(0, 12, 2, 1) #Умерло
        table.mergeCells(0, 13, 2, 1) #Состоит больных на конец периода
        table.mergeCells(0, 14, 2, 1) #Проведено койкодней
        table.mergeCells(0, 15, 2, 1) #Число койкодней закрытия
        table.mergeCells(0, 16, 2, 1) #Поступило иногородних больных
        table.mergeCells(0, 17, 2, 1) #Поступило экстренных больных

        return doc


class CHospitalBeds(QtGui.QDialog, Ui_ReportHospitalBegs):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbTypeHospitalization.setCurrentIndex(params.get('typeHospitalization', 0))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['typeHospitalization'] = self.cmbTypeHospitalization.currentIndex()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        return params

