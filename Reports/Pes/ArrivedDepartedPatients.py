# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from Events.CreateEvent import editEvent
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Ui_ArrivedDepartedPatients import Ui_ArrivedDepartedPatients
from library.Utils import forceInt, forceString, forceLong, forceRef, forceBool
from library.vm_collections import OrderedDict

TRANSFER_QUERY = '''
SELECT
  c.ID AS cid,
  c.lastName AS lastName,
  c.firstName AS firstName,
  c.patrName AS patrName,
  UNIX_TIMESTAMP(movA.begDate) AS begDate,
  UNIX_TIMESTAMP(movA.endDate) AS endDate,
  movAPOS.VALUE AS currentOS,
  movAPOSFrom.VALUE AS fromOS,
  movAPOSTo.VALUE AS toOS,
  qt.class AS quotaClass,
  COALESCE(movA.finance_id, ctr.finance_id) AS financeID,
  ctr.ID AS contractId,
  e.eventType_id AS eventType,
  e.externalId AS externalId,
  e.ID AS eventId,
  actType.NAME,
  act.begDate AS beg,
  act.endDate AS end,
  UNIX_TIMESTAMP(act.begDate) AS begUNIX,
  UNIX_TIMESTAMP(act.endDate) AS endUNIX

FROM Client c
  INNER JOIN Event e ON c.id = e.client_id AND e.eventType_id IN ('{hospET}', '{dayHospET}')
  LEFT JOIN Contract ctr ON e.contract_id = ctr.id

  INNER JOIN Action movA ON e.id = movA.event_id AND movA.deleted = 0 AND movA.actionType_id = '{movingAT}'
  LEFT JOIN ActionProperty movAP ON movA.id = movAP.action_id AND movAP.type_id = '{movingCurOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOS ON movAP.id = movAPOS.id
  LEFT JOIN ActionProperty movAPFrom ON movA.id = movAPFrom.action_id AND movAPFrom.type_id = '{movingFromOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOSFrom ON movAPFrom.id = movAPOSFrom.id
  LEFT JOIN ActionProperty movAPTo ON movA.id = movAPTo.action_id AND movAPTo.type_id = '{movingToOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOSTo ON movAPTo.id = movAPOSTo.id

  INNER JOIN Action lastMovA ON lastMovA.id = (SELECT MAX(id) FROM Action WHERE event_id = e.id AND actionType_id = '{movingAT}')
  LEFT JOIN ActionProperty lastMovQuoteAP ON lastMovA.id = lastMovQuoteAP.action_id AND lastMovQuoteAP.type_id = '{quoteAP}'
  LEFT JOIN ActionProperty_Client_Quoting lastMovQuote ON lastMovQuoteAP.id = lastMovQuote.id
  LEFT JOIN Client_Quoting cq ON lastMovQuote.value = cq.id
  LEFT JOIN QuotaType qt ON cq.quotaType_id = qt.id
  INNER JOIN Event evt ON evt.id = e.id AND evt.deleted = 0
  INNER JOIN Action act ON evt.ID = act.event_id AND act.deleted = 0
  INNER JOIN ActionType actType ON act.actionType_id = actType.ID AND actType.deleted = 0 AND actType.flatCode = 'reanimation'

WHERE e.deleted = 0
AND c.deleted = 0
AND movA.begDate <= FROM_UNIXTIME('{endDate}') AND
(movA.endDate IS NULL OR movA.endDate >= FROM_UNIXTIME('{startDate}'))
'''

QUERY_REANIMATIONDEPARTMENT = '''
  SELECT
  Client.lastName AS lastName,
  Client.firstName AS firstName,
  Client.patrName AS patrName,
  Client.id AS ClientId,
  IF (Action.endDate is NOT NULL, 1, 0) AS endDateIndicator,
  # IF((Action.endDate is not NULL and TIMEDIFF(Action.endDate, Action.begDate) / 3600 > 2), 1, 0) AS moreThan2H,
  ActionType.name,
  qt.class AS quotaClass,
  COALESCE(Action.finance_id, ctr.finance_id) AS financeID,
  ctr.id AS contractId,
  OrgStructure.name AS OrgName,
  OrgStructure.code,
  OrgStructure.id AS currentOS,
  ActionPropertyType.name,
  UNIX_TIMESTAMP(Action.begDate) AS begDate,
  UNIX_TIMESTAMP(Action.endDate) AS endDate,
  Event.eventType_id AS eventType,
  Event.externalId AS externalId,
  Event.id AS eventId

    FROM Event
      LEFT JOIN Contract ctr ON Event.contract_id = ctr.id
      INNER JOIN Client ON Event.client_id = Client.id and Client.deleted = 0
      INNER JOIN Action ON Event.id = Action.event_id AND Action.deleted = 0
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id AND ActionType.deleted = 0
      INNER JOIN ActionPropertyType ON ActionType.id = ActionPropertyType.actionType_id AND ActionPropertyType.deleted = 0
      INNER JOIN ActionProperty ON ActionPropertyType.id = ActionProperty.type_id AND Action.id = ActionProperty.action_id AND ActionProperty.deleted = 0
      INNER JOIN ActionProperty_OrgStructure ON ActionProperty.id = ActionProperty_OrgStructure.id
      INNER JOIN OrgStructure ON ActionProperty_OrgStructure.value = OrgStructure.id AND OrgStructure.deleted = 0

      INNER JOIN Action lastMovA ON lastMovA.id = (SELECT MAX(id) FROM Action WHERE event_id = Event.id AND actionType_id = '{movingAT}')
      LEFT JOIN ActionProperty lastMovQuoteAP ON lastMovA.id = lastMovQuoteAP.action_id AND lastMovQuoteAP.type_id = '{quoteAP}'
      LEFT JOIN ActionProperty_Client_Quoting lastMovQuote ON lastMovQuoteAP.id = lastMovQuote.id
      LEFT JOIN Client_Quoting cq ON lastMovQuote.value = cq.id
      LEFT JOIN QuotaType qt ON cq.quotaType_id = qt.id

WHERE (ActionType.id IN ('{allReanimationsId[0]}', '{allReanimationsId[1]}', '{allReanimationsId[2]}', '{allReanimationsId[3]}') or flatCode='reanimation'
      AND (TIMEDIFF(Action.endDate, Action.begDate)>=2 and ActionType.name LIKE 'Реанимация'))
      AND Event.eventType_id IN ('{hospET}', '{dayHospET}')
      AND OrgStructure.id = '{reanimationDepId}'
      AND Event.deleted = 0

      AND ((Action.endDate IS NULL OR Action.endDate >= FROM_UNIXTIME('{endDate}'))
      OR (Action.endDate BETWEEN FROM_UNIXTIME('{startDate}') AND FROM_UNIXTIME('{endDate}')))

GROUP BY Client.id, DATE(Action.begDate)
ORDER BY Event.id
'''


MOVING_QUERY = '''
SELECT
  c.id AS cid,
  c.lastName AS lastName,
  c.firstName AS firstName,
  c.patrName AS patrName,
  UNIX_TIMESTAMP(movA.begDate) AS begDate,
  UNIX_TIMESTAMP(movA.endDate) AS endDate,
  movAPOS.value AS currentOS,
  movAPOSFrom.value AS fromOS,
  movAPOSTo.value AS toOS,
  qt.class AS quotaClass,
  COALESCE(movA.finance_id, ctr.finance_id) AS financeID,
  ctr.id AS contractId,
  e.eventType_id AS eventType,
  e.externalId AS externalId,
  e.id AS eventId
FROM Client c
  INNER JOIN Event e ON c.id = e.client_id AND e.eventType_id IN ('{hospET}', '{dayHospET}')
  LEFT JOIN Contract ctr ON e.contract_id = ctr.id
  # moving
  INNER JOIN Action movA ON e.id = movA.event_id AND movA.deleted = 0 AND movA.actionType_id = '{movingAT}'
  LEFT JOIN ActionProperty movAP ON movA.id = movAP.action_id AND movAP.type_id = '{movingCurOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOS ON movAP.id = movAPOS.id
  LEFT JOIN ActionProperty movAPFrom ON movA.id = movAPFrom.action_id AND movAPFrom.type_id = '{movingFromOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOSFrom ON movAPFrom.id = movAPOSFrom.id
  LEFT JOIN ActionProperty movAPTo ON movA.id = movAPTo.action_id AND movAPTo.type_id = '{movingToOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure movAPOSTo ON movAPTo.id = movAPOSTo.id
  # last moving
  INNER JOIN Action lastMovA ON lastMovA.id = (SELECT MAX(id) FROM Action WHERE event_id = e.id AND actionType_id = '{movingAT}')
  LEFT JOIN ActionProperty lastMovQuoteAP ON lastMovA.id = lastMovQuoteAP.action_id AND lastMovQuoteAP.type_id = '{quoteAP}'
  LEFT JOIN ActionProperty_Client_Quoting lastMovQuote ON lastMovQuoteAP.id = lastMovQuote.id
  LEFT JOIN Client_Quoting cq ON lastMovQuote.value = cq.id
  LEFT JOIN QuotaType qt ON cq.quotaType_id = qt.id
WHERE
  e.deleted = 0 AND c.deleted = 0 AND
  movA.begDate <= FROM_UNIXTIME('{endDate}') AND
  (movA.endDate IS NULL OR movA.endDate >= FROM_UNIXTIME('{startDate}')) # OR
  # (movA.begDate BETWEEN FROM_UNIXTIME('{startDate}') AND FROM_UNIXTIME('{endDate}') OR
  #  movA.endDate IS NULL OR movA.endDate BETWEEN FROM_UNIXTIME('{startDate}') AND FROM_UNIXTIME('{endDate}'))
'''

RECEIVED_QUERY = '''
SELECT
  c.id AS cid,
  c.lastName AS lastName,
  c.firstName AS firstName,
  c.patrName AS patrName,
  IF(c.sex = 1 AND age(c.birthDate, e.setDate) >= 60 OR c.sex = 2 AND age(c.birthDate, e.setDate) >= 55, 1, 0) AS isPensioner,
  IF(LEFT(ah.KLADRCode, 2) != '78' OR dt.isForeigner = 1, 1, 0) AS isForeigner,
  IF(ca.isVillager = 1 OR isClientVillager(c.id) = 1, 1, 0) AS isVillager,
  UNIX_TIMESTAMP(recvA.endDate) AS endDate,
  recvAPOS.value AS currentOS,
  qt.class AS quotaClass,
  COALESCE(recvA.finance_id, ctr.finance_id) AS financeID,
  ctr.id AS contractId,
  e.eventType_id AS eventType,
  e.externalId AS externalId,
  e.id AS eventId
FROM Client c
  LEFT JOIN ClientAddress ca ON ca.id = getClientRegAddressId(c.id)AND ca.deleted = 0
  LEFT JOIN Address addr ON ca.address_id = addr.id AND addr.deleted = 0
  LEFT JOIN AddressHouse ah ON addr.house_id = ah.id AND ah.deleted = 0
  LEFT JOIN ClientDocument cd ON cd.id = getClientDocumentID(c.id)
  LEFT JOIN rbDocumentType dt ON dt.id = cd.documentType_id

  INNER JOIN Event e ON c.id = e.client_id AND e.eventType_id IN ('{hospET}', '{dayHospET}')
  LEFT JOIN Contract ctr ON e.contract_id = ctr.id
  # received
  INNER JOIN Action recvA ON e.id = recvA.event_id AND recvA.deleted = 0 AND recvA.actionType_id = '{receivedAT}'
  LEFT JOIN ActionProperty recvAP ON recvA.id = recvAP.action_id AND recvAP.type_id = '{receivedCurOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure recvAPOS ON recvAP.id = recvAPOS.id
  # last moving
  INNER JOIN Action lastMovA ON lastMovA.id = (SELECT MAX(id) FROM Action WHERE event_id = e.id AND actionType_id = '{movingAT}')
  LEFT JOIN ActionProperty lastMovQuoteAP ON lastMovA.id = lastMovQuoteAP.action_id AND lastMovQuoteAP.type_id = '{quoteAP}'
  LEFT JOIN ActionProperty_Client_Quoting lastMovQuote ON lastMovQuoteAP.id = lastMovQuote.id
  LEFT JOIN Client_Quoting cq ON lastMovQuote.value = cq.id
  LEFT JOIN QuotaType qt ON cq.quotaType_id = qt.id
WHERE
  e.deleted = 0 AND c.deleted = 0 AND
  (recvA.endDate BETWEEN FROM_UNIXTIME('{startDate}') AND FROM_UNIXTIME('{endDate}'))
'''

LEAVED_QUERY = '''
SELECT
  c.id AS cid,
  c.lastName AS lastName,
  c.firstName AS firstName,
  c.patrName AS patrName,
  UNIX_TIMESTAMP(leaveA.begDate) AS begDate,
  leaveAPOS.value AS currentOS,
  leaveAPSResult.value AS outcome,
  qt.class AS quotaClass,
  COALESCE(leaveA.finance_id, ctr.finance_id) AS financeID,
  ctr.id AS contractId,
  e.eventType_id AS eventType,
  e.externalId AS externalId,
  e.id AS eventId
FROM Client c
  INNER JOIN Event e ON c.id = e.client_id AND e.eventType_id IN ('{hospET}', '{dayHospET}')
  LEFT JOIN Contract ctr ON e.contract_id = ctr.id
  # leaved
  INNER JOIN Action leaveA ON e.id = leaveA.event_id AND leaveA.deleted = 0 AND leaveA.actionType_id = '{leavedAT}'
  LEFT JOIN ActionProperty leaveAP ON leaveA.id = leaveAP.action_id AND leaveAP.type_id = '{leavedCurOSAPT}'
  LEFT JOIN ActionProperty_OrgStructure leaveAPOS ON leaveAP.id = leaveAPOS.id
  LEFT JOIN ActionProperty leaveAPResult ON leaveA.id = leaveAPResult.action_id AND leaveAPResult.type_id = '{leavedOutcomeAPT}'
  LEFT JOIN ActionProperty_String leaveAPSResult ON leaveAPResult.id = leaveAPSResult.id
  # last moving
  INNER JOIN Action lastMovA ON lastMovA.id = (SELECT MAX(id) FROM Action WHERE event_id = e.id AND actionType_id = '{movingAT}')
  LEFT JOIN ActionProperty lastMovQuoteAP ON lastMovA.id = lastMovQuoteAP.action_id AND lastMovQuoteAP.type_id = '{quoteAP}'
  LEFT JOIN ActionProperty_Client_Quoting lastMovQuote ON lastMovQuoteAP.id = lastMovQuote.id
  LEFT JOIN Client_Quoting cq ON lastMovQuote.value = cq.id
  LEFT JOIN QuotaType qt ON cq.quotaType_id = qt.id
WHERE
  e.deleted = 0 AND c.deleted = 0 AND
  (leaveA.begDate BETWEEN FROM_UNIXTIME('{startDate}') AND FROM_UNIXTIME('{endDate}'))
'''

(START_COUNT, RECEIVED_TOTAL, RECEIVED_PENSIONER, RECEIVED_FOREIGN, RECEIVED_VILLAGER,
 MOVED_TO_CURRENT, MOVED_FROM_CURRENT, LEAVED_ALIVE, LEAVED_DEAD, END_COUNT) = xrange(10)


def loadIds():
    db = QtGui.qApp.db
    hospET = db.getIdList(stmt=u"SELECT id FROM EventType WHERE code = '03'")[0]
    dayHospET = db.getIdList(stmt=u"SELECT id FROM EventType WHERE code = '05'")[0]
    movingAT = db.getIdList(stmt=u"SELECT id FROM ActionType WHERE flatCode = 'moving'")[0]
    receivedAT = db.getIdList(stmt=u"SELECT id FROM ActionType WHERE flatCode = 'received'")[0]
    leavedAT = db.getIdList(stmt=u"SELECT id FROM ActionType WHERE flatCode = 'leaved'")[0]
    movingCurOSAPT = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Отделение пребывания' "
                                       u"AND actionType_id = %d" % movingAT)[0]
    movingFromOSAPT = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Переведен из отделения' "
                                        u"AND actionType_id = %d" % movingAT)[0]
    movingToOSAPT = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Переведен в отделение' "
                                      u"AND actionType_id = %d" % movingAT)[0]
    receivedCurOSAPT = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Направлен в отделение' "
                                         u"AND actionType_id = %d" % receivedAT)[0]
    leavedCurOSAPT = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Отделение' "
                                       u"AND actionType_id = %d" % leavedAT)[0]
    leavedOutcomeAPT = db.getIdList('', stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Исход госпитализации' "
                                             u"AND actionType_id = %d" % leavedAT)[0]
    quotaAP = db.getIdList(stmt=u"SELECT id FROM ActionPropertyType WHERE name = 'Квота' "
                                u"AND actionType_id = %d" % movingAT)[0]
    omsFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'ОМС'")[0]
    pmuFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'ПМУ'")[0]
    dmsFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'ДМС'")[0]
    omsVmpFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'ВМП из ОМС'")[0]
    omsLtFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'ОМС ЛТ'")[0]
    akiFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'АКИ'")[0]
    budgetFinance = db.getIdList(stmt=u"SELECT id FROM rbFinance WHERE name = 'бюджет'")[0]
    reanimationDepId = db.getIdList(stmt=u"SELECT id FROM s11.OrgStructure WHERE "
                                         u"(name = 'Отделение анестезиологии-реанимации' OR code='09 Отд')")[0]
    allReanimationsId = db.getIdList(stmt=u"SELECT id FROM ActionType WHERE name ='Реанимация'")
    return (hospET, dayHospET, movingAT, receivedAT, leavedAT, movingCurOSAPT, movingFromOSAPT, movingToOSAPT,
            receivedCurOSAPT, leavedCurOSAPT, leavedOutcomeAPT, quotaAP, omsFinance, pmuFinance, dmsFinance,
            omsVmpFinance, omsLtFinance, akiFinance, budgetFinance, reanimationDepId, allReanimationsId)


class CArrivedDepartedPatients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет по поступлению и выписке пациентов')
        self.db = QtGui.qApp.db

        self.boldFormat = QtGui.QTextCharFormat()
        self.boldFormat.setFontWeight(QtGui.QFont.Bold)

    def getSetupDialog(self, parent):
        result = CArrivedDepartedPatientsSettingsDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        noFinanceDetail = params.get('noFinanceDetail', False)

        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('5%', [u'', u'', u'', u'', u''], CReportBase.AlignLeft),
            ('10%', [u'', u'', u'', u'', u''], CReportBase.AlignLeft),
            ('10%', [u'Движение больных за истекшие сутки',
                      u'Состояло больных на начало текущих суток', u'', u'', u'1'], CReportBase.AlignLeft),
            ('10%', [u'', u'Поступило больных', u'Всего', u'', u'2'], CReportBase.AlignLeft),
            ('10%', [u'', u'', u'из них', u'пенсионеров', u'3'], CReportBase.AlignLeft),
            ('10%', [u'', u'', u'из иногородних', u'всего', u'4'], CReportBase.AlignLeft),
            ('10%', [u'', u'', u'', u'жителей села', u'5'], CReportBase.AlignLeft),
            ('10%', [u'', u'Переведено больных внутри больницы', u'из других отделений', u'', u'6'],
             CReportBase.AlignLeft),
            ('10%', [u'', u'', u'в другие отделения', u'', u'7'], CReportBase.AlignLeft),
            ('5%', [u'', u'Выписано больных', u'', u'', u'8'], CReportBase.AlignLeft),
            ('5%', [u'', u'Умерло', u'', u'', u'9'], CReportBase.AlignLeft),
            ('10%', [u'Состоит больных на начало текущего дня', u'', u'', u'', u'10'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 5, 1)
        table.mergeCells(0, 1, 5, 1)
        table.mergeCells(0, 2, 1, 9)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 1, 4)
        table.mergeCells(2, 3, 2, 1)
        table.mergeCells(2, 5, 1, 2)
        table.mergeCells(1, 7, 1, 2)
        table.mergeCells(2, 7, 2, 1)
        table.mergeCells(2, 8, 2, 1)
        table.mergeCells(1, 9, 3, 1)
        table.mergeCells(1, 10, 3, 1)
        table.mergeCells(0, 11, 4, 1)

        (hospET, dayHospET, movingAT, receivedAT, leavedAT, movingCurOSAPT, movingFromOSAPT, movingToOSAPT,
         receivedCurOSAPT, leavedCurOSAPT, leavedOutcomeAPT, quoteAP, omsFinance, pmuFinance, dmsFinance, omsVmpFinance,
         omsLtFinance, akiFinance, budgetFinance, reanimationDepId, allReanimationsId) = loadIds()

        def getFinanceRow(rec):
            quotaClass = forceInt(rec.value('quotaClass')) if not rec.value('quotaClass').isNull() else None
            financeID = forceInt(rec.value('financeID')) if not rec.value('financeId').isNull() else None
            if quotaClass == 0:
                return 'vmp'
            if quotaClass == 1:
                return 'smp'
            if quotaClass == 7 or financeID == akiFinance:
                return 'aki'
            if financeID == omsFinance:
                return 'oms'
            if financeID == pmuFinance:
                return 'pmu'
            if financeID == dmsFinance:
                return 'dms'
            if financeID == omsVmpFinance and quotaClass == 5:
                return 'oms_vmp'
            if financeID == omsLtFinance:
                return 'oms_lt'
            if financeID == budgetFinance:
                return 'budget'
            QtGui.qApp.restoreOverrideCursor()
            res = QtGui.QMessageBox().warning(
                None,
                u'Не удалось определить тип финансирования',
                u'Код клиента: %s\nВнешний код: %s\nfinanceId: %s\nquotaClass: %s\n\n'
                u'Открыть обращение?' % (forceString(rec.value('cid')), forceString(rec.value('externalId')),
                                         financeID, quotaClass),
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.Retry | QtGui.QMessageBox.Cancel
            )
            if res == QtGui.QMessageBox.Yes:
                editEvent(None, forceRef(rec.value('eventId')))
            elif res == QtGui.QMessageBox.Retry:
                CArrivedDepartedPatients(None).exec_()
            raise ValueError

        def getEventType(rec):
            return 'ks' if forceRef(rec.value('eventType')) == hospET else 'ds'

        def getClientItem(rec):
            return '%s %s.%s. (%s)' % (
                forceString(rec.value('lastName')),
                forceString(rec.value('firstName'))[:1],
                forceString(rec.value('patrName'))[:1],
                forceString(rec.value('externalId'))
            )

        # strType = '(type = 1 or type = 5)' if params['reanimation'] else 'type = 1'
        os_ids = params['LPU'] if not params['allLPU'] else \
            QtGui.qApp.db.getIdList('OrgStructure',
                                    where='(type = 1 or type = 5) AND hasHospitalBeds = 1 AND deleted = 0 AND '
                                          'EXISTS(SELECT oshb.id '
                                          '         FROM OrgStructure_HospitalBed oshb '
                                          '         WHERE oshb.master_id = OrgStructure.id)', order='code')

        finances = lambda: {
            'vmp': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'smp': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'oms': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'pmu': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'dms': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'oms_vmp': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'oms_lt': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'aki': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'budget': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'total': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }

        types = lambda: {
            'ks': finances(),
            'ds': finances(),
            'total': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }

        names = lambda: {'ks': set(), 'ds': set()}

        OSdata = OrderedDict((os_id, types()) for os_id in os_ids)
        OSdata['total'] = types()

        received = names()
        leaved_alive = names()
        leaved_dead = names()
        moved_to_current = names()  # Переведено из других
        moved_from_current = names()  # Переведено в другие

        startDate = params[
            'begDate'].toTime_t()  # int(time.mktime(datetime.strptime('2017-04-04 00:00:00', '%Y-%m-%d %H:%M:%S').timetuple()))
        endDate = params[
            'endDate'].toTime_t()  # int(time.mktime(datetime.strptime('2017-04-04 23:59:59', '%Y-%m-%d %H:%M:%S').timetuple()))

        moving_sql = MOVING_QUERY.format(
            hospET=hospET, dayHospET=dayHospET, movingAT=movingAT, movingCurOSAPT=movingCurOSAPT, quoteAP=quoteAP,
            movingFromOSAPT=movingFromOSAPT, movingToOSAPT=movingToOSAPT, startDate=startDate, endDate=endDate)

        queryReanimation_sql = QUERY_REANIMATIONDEPARTMENT.format(
            hospET=hospET, dayHospET=dayHospET, movingAT=movingAT, quoteAP=quoteAP, startDate=startDate,
            endDate=endDate, reanimationDepId=reanimationDepId, allReanimationsId=allReanimationsId)

        transfer_sql = TRANSFER_QUERY.format(
            hospET=hospET, dayHospET=dayHospET, movingAT=movingAT, movingCurOSAPT=movingCurOSAPT, quoteAP=quoteAP,
            movingFromOSAPT=movingFromOSAPT, movingToOSAPT=movingToOSAPT, startDate=startDate, endDate=endDate)

        received_sql = RECEIVED_QUERY.format(
            hospET=hospET, dayHospET=dayHospET, receivedAT=receivedAT, receivedCurOSAPT=receivedCurOSAPT,
            movingAT=movingAT, quoteAP=quoteAP, startDate=startDate, endDate=endDate)

        leaved_sql = LEAVED_QUERY.format(
            hospET=hospET, dayHospET=dayHospET, leavedAT=leavedAT, leavedCurOSAPT=leavedCurOSAPT,
            leavedOutcomeAPT=leavedOutcomeAPT, movingAT=movingAT, quoteAP=quoteAP, startDate=startDate, endDate=endDate)

        self.setQueryText(';\n'.join((moving_sql, received_sql, leaved_sql, transfer_sql, queryReanimation_sql)) + ';')

        def inc(os, rec, column):
            financeRow = getFinanceRow(rec)
            eventType = getEventType(rec)
            OSdata[os]['total'][column] += 1
            OSdata[os][eventType]['total'][column] += 1
            OSdata[os][eventType][financeRow][column] += 1
            OSdata['total']['total'][column] += 1
            OSdata['total'][eventType]['total'][column] += 1
            OSdata['total'][eventType][financeRow][column] += 1

        try:
            if params['reanimation']:
                for rec in db.iterRecordList(stmt=transfer_sql):
                    recBegDate = forceLong(rec.value('begUNIX'))
                    recEndDate = forceLong(rec.value('endUNIX'))
                    recCurrentOS = forceRef(rec.value('currentOS'))
                    if startDate <= recBegDate <= endDate and recCurrentOS in OSdata.keys():
                        moved_to_current[getEventType(rec)].add(getClientItem(rec))
                        inc(recCurrentOS, rec, MOVED_TO_CURRENT)
                    if startDate <= recEndDate <= endDate and recCurrentOS in OSdata.keys():
                        moved_from_current[getEventType(rec)].add(getClientItem(rec))
                        inc(recCurrentOS, rec, MOVED_FROM_CURRENT)

            for rec in db.iterRecordList(stmt=queryReanimation_sql):
                recBegDate = forceLong(rec.value('begDate'))
                recEndDate = forceLong(rec.value('endDate'))
                recCurrentOS = forceRef(rec.value('currentOS'))
                endDateIndicator = forceInt(rec.value('endDateIndicator'))
                # moreThan2H = forceInt(rec.value('moreThan2H'))
                # if endDateIndicator == moreThan2H:
                if (rec.value('endDate').isNull() or recEndDate > recBegDate) and recBegDate < startDate and recCurrentOS in OSdata.keys():
                    #startDate <= recBegDate <= endDate
                    inc(recCurrentOS, rec, START_COUNT)
                if startDate <= recBegDate <= endDate and recCurrentOS in OSdata.keys():
                    moved_to_current[getEventType(rec)].add(getClientItem(rec))
                    inc(recCurrentOS, rec, MOVED_TO_CURRENT)
                if (startDate <= recEndDate <= endDate) and recCurrentOS in OSdata.keys():
                    moved_from_current[getEventType(rec)].add(getClientItem(rec))
                    inc(recCurrentOS, rec, MOVED_FROM_CURRENT)
                if (rec.value('endDate').isNull() or recEndDate > endDate) and recBegDate <= endDate and recCurrentOS in OSdata.keys():
                    inc(recCurrentOS, rec, END_COUNT)

            for rec in db.iterRecordList(stmt=moving_sql):
                recBegDate = forceLong(rec.value('begDate'))
                recEndDate = forceLong(rec.value('endDate'))
                recCurrentOS = forceRef(rec.value('currentOS'))
                recFromOS = forceRef(rec.value('fromOS'))
                recToOS = forceRef(rec.value('toOS'))
                if (recBegDate <= startDate and
                        (recEndDate >= startDate or rec.value('endDate').isNull()) and
                            recCurrentOS in OSdata.keys()):
                    inc(recCurrentOS, rec, START_COUNT)
                if (recBegDate <= endDate and
                        (recEndDate >= endDate or rec.value('endDate').isNull()) and
                            recCurrentOS in OSdata.keys()):
                    inc(recCurrentOS, rec, END_COUNT)
                # переведены в указанные отделения
                if (startDate <= recEndDate <= endDate and
                            recCurrentOS is not None and
                            recToOS in OSdata.keys()):
                    moved_to_current[getEventType(rec)].add(getClientItem(rec))
                    inc(recToOS, rec, MOVED_TO_CURRENT)
                # переведены из указанных отделений
                if (startDate <= recBegDate <= endDate and
                            recCurrentOS is not None and
                            recFromOS in OSdata.keys()):
                    moved_from_current[getEventType(rec)].add(getClientItem(rec))
                    inc(recFromOS, rec, MOVED_FROM_CURRENT)

            for rec in db.iterRecordList(stmt=received_sql):
                recIsVillager = forceBool(rec.value('isVillager'))
                recIsForeigner = forceBool(rec.value('isForeigner'))
                recIsPensioner = forceBool(rec.value('isPensioner'))
                recCurrentOS = forceRef(rec.value('currentOS'))
                recEndDate = forceLong(rec.value('endDate'))
                if (startDate <= recEndDate <= endDate and
                            recCurrentOS in OSdata.keys()):
                    inc(recCurrentOS, rec, RECEIVED_TOTAL)
                    received[getEventType(rec)].add(getClientItem(rec))
                    if recIsPensioner:
                        inc(recCurrentOS, rec, RECEIVED_PENSIONER)
                    if recIsForeigner:
                        inc(recCurrentOS, rec, RECEIVED_FOREIGN)
                    if recIsVillager:
                        inc(recCurrentOS, rec, RECEIVED_VILLAGER)

            for rec in db.iterRecordList(stmt=leaved_sql):
                recBegDate = forceLong(rec.value('begDate'))
                recCurrentOS = forceRef(rec.value('currentOS'))
                recIsDeath = forceString(rec.value('outcome')) == u'умер'
                if startDate <= recBegDate <= endDate and recCurrentOS in OSdata.keys():
                    if recIsDeath:
                        leaved_dead[getEventType(rec)].add(getClientItem(rec))
                        inc(recCurrentOS, rec, LEAVED_DEAD)
                    else:
                        leaved_alive[getEventType(rec)].add(getClientItem(rec))
                        inc(recCurrentOS, rec, LEAVED_ALIVE)
        except ValueError:
            return None

        def write_event_type(os_id, is_ks=True):
            et = 'ks' if is_ks else 'ds'
            if not noFinanceDetail:
                row = table.addRowWithContent(u'', u'ВМП', *OSdata[os_id][et]['vmp'])
                table.addRowWithContent(u'', u'СМП', *OSdata[os_id][et]['smp'])
                table.addRowWithContent(u'', u'ОМС', *OSdata[os_id][et]['oms'])
                table.addRowWithContent(u'', u'ПМУ', *OSdata[os_id][et]['pmu'])
                table.addRowWithContent(u'', u'ДМС', *OSdata[os_id][et]['dms'])
                table.addRowWithContent(u'', u'ВМП из ОМС', *OSdata[os_id][et]['oms_vmp'])
                table.addRowWithContent(u'', u'ОМС ЛТ', *OSdata[os_id][et]['oms_lt'])
                table.addRowWithContent(u'', u'АКИ', *OSdata[os_id][et]['aki'])
                table.addRowWithContent(u'', u'Донор/Прочее', *OSdata[os_id][et]['budget'])
            table.addRowWithContent(u'КС' if is_ks else u'ДС', u'Итого', *OSdata[os_id][et]['total'],
                                    charFormat=self.boldFormat)
            if not noFinanceDetail:
                table.mergeCells(row, 0, 10, 1)

        for os_id in OSdata.keys():
            if os_id == 'total':
                if len(os_ids) == 1:
                    continue
                os_code = u'все подразделения'
            else:
                os_code = forceString(db.translate('OrgStructure', 'id', os_id, 'code'))
            row = table.addRowWithContent(os_code)
            table.mergeCells(row, 0, 1, 12)
            write_event_type(os_id)
            write_event_type(os_id, False)
            row = table.addRowWithContent(u'Итого ' + os_code, u'', *OSdata[os_id]['total'], charFormat=self.boldFormat)
            table.mergeCells(row, 0, 1, 2)

        if noFinanceDetail:
            table.table.removeColumns(1, 1)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'\nДежурная медсестра: _____________________________________')
        cursor.insertBlock()

        if not params['allLPU']:
            def insertClientList(lst, row, col):
                table.setHtml(row, col, u'<ol><li>' + u'</li><li>'.join(lst) + u'</li></ol>')

            def insertClientsRow(et):
                table.addRow()
                insertClientList(received[et], 1, 0)
                insertClientList(leaved_alive[et], 1, 1)
                insertClientList(leaved_dead[et], 1, 2)
                insertClientList(moved_to_current[et], 1, 3)
                insertClientList(moved_from_current[et], 1, 4)

            tableColumns = [
                ('20%', [u'Поступило:'], CReport.AlignLeft),
                ('20%', [u'Выписано:'], CReport.AlignLeft),
                ('20%', [u'Умерло:'], CReport.AlignLeft),
                ('20%', [u'Переведено из:'], CReport.AlignLeft),
                ('20%', [u'Переведено в:'], CReport.AlignLeft),
            ]

            cursor.insertText(u'\n\nГоспитализация', CReport.ReportSubTitle)
            textFormat = QtGui.QTextBlockFormat()
            textFormat.setPageBreakPolicy(QtGui.QTextBlockFormat.PageBreak_AlwaysBefore)
            cursor.setBlockFormat(textFormat)
            cursor.insertBlock()
            textFormat.setPageBreakPolicy(QtGui.QTextBlockFormat.PageBreak_Auto)
            cursor.setBlockFormat(textFormat)

            table = createTable(cursor, tableColumns, border=0, cellPadding=0)
            insertClientsRow('ks')
            cursor.movePosition(QtGui.QTextCursor.End)

            cursor.insertBlock()
            cursor.insertText(u'\n\nДС Госпитализация', CReport.ReportSubTitle)
            cursor.insertBlock()
            table = createTable(cursor, tableColumns, border=0, cellPadding=0)
            table.table.format().setAlignment(QtCore.Qt.AlignTop)
            insertClientsRow('ds')

        return doc


class CArrivedDepartedPatientsSettingsDialog(QtGui.QDialog, Ui_ArrivedDepartedPatients):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstLPU.setTable('OrgStructure')
        self.lstLPU.setFilter('(type = 1 or type = 5) AND hasHospitalBeds = 1 AND deleted = 0 AND '
                              'EXISTS(SELECT oshb.id '
                              '         FROM OrgStructure_HospitalBed oshb '
                              '         WHERE oshb.master_id = OrgStructure.id)')

        self.edtBegDate.setDate(QtCore.QDate().currentDate().addDays(-1))
        self.edtBegTime.setTime(QtCore.QTime(0, 0))
        self.edtEndDate.setDate(QtCore.QDate().currentDate().addDays(-1))
        self.edtEndTime.setTime(QtCore.QTime(23, 59))

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.lstLPU.setValues(params.get('LPU', []))
        self.chkAllLPU.setChecked(params.get('allLPU', False))
        self.chkNoFinanceDetail.setChecked(params.get('noFinanceDetail', False))
        self.chkReanimation.setChecked(params.get('reanimation', False))

    def params(self):
        params = {
            'allLPU': self.chkAllLPU.isChecked(),
            'begDate': QtCore.QDateTime(self.edtBegDate.date(), self.edtBegTime.time()),
            'endDate': QtCore.QDateTime(self.edtEndDate.date(), self.edtEndTime.time()),
            'LPU': self.lstLPU.values(),
            'noFinanceDetail': self.chkNoFinanceDetail.isChecked(),
            'reanimation': self.chkReanimation.isChecked()
        }
        return params

    def accept(self):
        if not len(self.lstLPU.values()) and not self.chkAllLPU.isChecked():
            QtGui.QMessageBox().warning(self, u'Внимание', u'Не выбрано ни одного подразделения')
        else:
            super(CArrivedDepartedPatientsSettingsDialog, self).accept()
