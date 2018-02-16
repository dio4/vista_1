# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, formatShortName, \
                               formatSex, getPref, setPref, toVariant
from library.database   import addDateInRange

from Orgs.Utils         import getOrgStructureName, getOrgStructureDescendants

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportLeavedMovedDeadSetupDialog import Ui_ReportLeavedMovedDeadSetupDialog


def getClientRecord(clientId):
    db = QtGui.qApp.db

    stmt = u'''
    SELECT
      Client.lastName                AS lastName,
      Client.firstName               AS firstName,
      Client.patrName                AS patrName,
      Client.birthDate               AS birthDate,
      Client.sex                     AS sex,
      SocStatusType.name             AS socStatus,
      BenefitsType.name              AS benefits,
      getClientRegAddress(Client.id) AS regAddress
    FROM
      Client
      LEFT JOIN ClientSocStatus ON ClientSocStatus.id = (
        SELECT MAX(ClientSocStatus.id)
        FROM ClientSocStatus
        LEFT JOIN rbSocStatusClass AS SocStatus ON SocStatus.flatCode = 'socStatus' AND
                                                         SocStatus.id = ClientSocStatus.socStatusClass_id
        WHERE
          ClientSocStatus.client_id = Client.id AND
          ClientSocStatus.deleted = 0
      )
      LEFT JOIN rbSocStatusType AS SocStatusType ON SocStatusType.id = ClientSocStatus.socStatusType_id
      LEFT JOIN ClientSocStatus AS ClientBenefits ON ClientBenefits.id = (
        SELECT MAX(ClientSocStatus.id)
        FROM ClientSocStatus
        LEFT JOIN rbSocStatusClass AS Benefits ON Benefits.flatCode = 'benefits' AND
                                                        Benefits.id = ClientSocStatus.socStatusClass_id
        WHERE
          ClientSocStatus.client_id = Client.id AND
          ClientSocStatus.deleted = 0
      )
      LEFT JOIN rbSocStatusType AS BenefitsType ON BenefitsType.id = ClientBenefits.socStatusType_id
      WHERE Client.id = {clientId}
    '''.format(clientId=clientId)

    query = db.query(stmt)
    return query.record() if query.first() else None


def getActionPropertyString(actionId, propertyName):
    if not actionId:
        return u''

    db = QtGui.qApp.db
    AP = db.table('ActionProperty')
    APS = db.table('ActionProperty_String')
    APT = db.table('ActionPropertyType')

    queryTable = APT.leftJoin(AP, db.joinAnd([AP['type_id'].eq(APT['id']),
                                              AP['action_id'].eq(actionId)]))
    queryTable = queryTable.leftJoin(APS, APS['id'].eq(AP['id']))
    cond = [
        APT['name'].like(propertyName),
        APT['deleted'].eq(0),
        AP['deleted'].eq(0)
    ]
    record = db.getRecordEx(queryTable, APS['value'], cond)

    return forceString(record.value('value')) if not record is None else u''


def getActionPropertyOrgStructure(actionId, propertyName):
    if not actionId:
        return u''

    db = QtGui.qApp.db
    AP = db.table('ActionProperty')
    APOS = db.table('ActionProperty_OrgStructure')
    APS = db.table('ActionProperty_String')
    APT = db.table('ActionPropertyType')
    OrgStructure = db.table('OrgStructure')

    queryTable = APT.leftJoin(AP, db.joinAnd([AP['type_id'].eq(APT['id']),
                                              AP['action_id'].eq(actionId)]))
    queryTable = queryTable.leftJoin(APS, APS['id'].eq(AP['id']))
    queryTable = queryTable.leftJoin(APOS, APOS['id'].eq(AP['id']))
    queryTable = queryTable.leftJoin(OrgStructure, OrgStructure['id'].eq(APOS['value']))
    cols = [
        'if({orgStructureId} IS NULL, {orgStructureString}, {orgStructureName}) AS orgStructureName'.format(
            orgStructureId=OrgStructure['id'].name(),
            orgStructureString=APS['value'].name(),
            orgStructureName=OrgStructure['name'])
    ]
    cond = [
        APT['name'].eq(propertyName),
        APT['deleted'].eq(0),
        AP['deleted'].eq(0)
    ]
    record = db.getRecordEx(queryTable, cols, cond)

    return forceString(record.value('orgStructureName')) if not record is None else u''


def getActionPropertyOrganisation(actionId, propertyName):
    if not actionId:
        return u''

    db = QtGui.qApp.db
    AP = db.table('ActionProperty')
    APO = db.table('ActionProperty_Organisation')
    APS = db.table('ActionProperty_String')
    APT = db.table('ActionPropertyType')
    Organisation = db.table('Organisation')

    queryTable = APT.leftJoin(AP, db.joinAnd([AP['type_id'].eq(APT['id']),
                                              AP['action_id'].eq(actionId)]))
    queryTable = queryTable.leftJoin(APS, APS['id'].eq(AP['id']))
    queryTable = queryTable.leftJoin(APO, APO['id'].eq(AP['id']))
    queryTable = queryTable.leftJoin(Organisation, Organisation['id'].eq(APO['value']))
    cols = [
        'if({orgId} IS NULL, {orgString}, {orgName}) AS orgName'.format(orgId=Organisation['id'].name(),
                                                                        orgString=APS['value'].name(),
                                                                        orgName=Organisation['shortName'])
    ]
    cond = [
        APT['name'].eq(propertyName),
        APT['deleted'].eq(0),
        AP['deleted'].eq(0)
    ]
    record = db.getRecordEx(queryTable, cols, cond)

    return forceString(record.value('orgName')) if not record is None else u''


def selectDataByEvents(byPeriod, leavedDate,
                       byReceivedDate, receivedBegDate, receivedEndDate,
                       byLeavedDate, leavedBegDate, leavedEndDate, orgStructureId):
    db = QtGui.qApp.db

    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableLeavedAction = db.table('Action').alias('LeavedAction')
    tableReceivedAction = db.table('Action').alias('ReceivedAction')

    cond = [
        # tableLeavedAction['id'].isNotNull(),
        tableEvent['deleted'].eq(0),
        tableClient['deleted'].eq(0)
    ]

    if byPeriod: # за период
        if byReceivedDate:
            addDateInRange(cond, tableReceivedAction['begDate'], receivedBegDate, receivedEndDate)
        if byLeavedDate:
            addDateInRange(cond, tableLeavedAction['endDate'], leavedBegDate, leavedEndDate)
    else: # по дате выписки
        cond.append(tableLeavedAction['endDate'].dateEq(leavedDate))

    if not orgStructureId is None:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    stmt = u'''
    SELECT
      Client.id                                              AS clientId,
      Event.id                                               AS eventId,
      Event.externalId                                       AS eventExternalId,
      Event.order                                            AS eventOrder,
      Event.isPrimary                                        AS eventIsPrimary,
      Person.orgStructure_id                                 AS orgStructureId,
      ReceivedAction.begDate                                 AS begDate,
      LeavedAction.endDate                                   AS leavedDate,
      datediff(LeavedAction.endDate, ReceivedAction.begDate) AS bedDays,
      ReceivedAction.id                                      AS receivedActionId,
      LeavedAction.id                                        AS leavedActionId,

      (
        SELECT MIN(Action.id)
        FROM Action
        INNER JOIN ActionType AS StatCardActionType ON (StatCardActionType.id = Action.actionType_id) AND
                                                       (StatCardActionType.name = 'Статистическая карта') AND
                                                       (StatCardActionType.deleted = 0)
        WHERE Action.event_id = Event.id AND
              Action.deleted = 0
      ) AS statCardActionId,

      (
        SELECT MIN(Action.id)
        FROM Action
        INNER JOIN ActionType AS ExaminationActionType ON (ExaminationActionType.id = Action.actionType_id) AND
                                                         (ExaminationActionType.name LIKE '%осмотр%') AND
                                                         (ExaminationActionType.deleted = 0)
        WHERE Action.event_id = Event.id AND
              Action.deleted = 0
      ) AS firstExaminationActionId,

      (
        SELECT MIN(Action.id)
        FROM Action
        INNER JOIN ActionType AS TraumatologistActionType ON (TraumatologistActionType.id = Action.actionType_id) AND
                                                             (TraumatologistActionType.`name` LIKE '%Осмотр отделения травматолога%') AND
                                                             (TraumatologistActionType.deleted = 0)
        WHERE Action.event_id = Event.id AND
              Action.deleted = 0
      ) AS traumatologistActionId,

      (
        SELECT MAX(Action.id)
        FROM Action
        INNER JOIN ActionType AS EpicrisisActionType ON (EpicrisisActionType.id = Action.actionType_id) AND (
                                                        (EpicrisisActionType.name LIKE '%Выписной эпикриз%') OR
                                                        (EpicrisisActionType.name LIKE '%Посмертный эпикриз%') OR
                                                        (EpicrisisActionType.name LIKE '%Переводной эпикриз%')) AND
                                                        (EpicrisisActionType.deleted = 0)
        WHERE Action.event_id = Event.id AND
              Action.deleted = 0
      ) AS epicrisisActionId,

      (
        SELECT MAX(Action.id)
        FROM Action
        INNER JOIN ActionType AS AutopsyActionType ON (AutopsyActionType.id = Action.actionType_id) AND
                                                      (AutopsyActionType.name LIKE 'Протокол патолого-анатомического вскрытия%') AND
                                                      (AutopsyActionType.deleted = 0)
        WHERE Action.event_id = Event.id AND
              Action.deleted = 0
      ) AS autopsyActionId

    FROM Event
      INNER JOIN Client ON Client.id = Event.client_id
      LEFT JOIN Person ON Person.id = Event.execPerson_id

      INNER JOIN Action AS ReceivedAction ON ReceivedAction.id = (
        SELECT MAX(Action.id)
        FROM
          Action
          INNER JOIN ActionType ON ActionType.flatCode = 'received' AND ActionType.id = Action.actionType_id AND ActionType.deleted = 0
        WHERE
          Action.event_id = Event.id AND Action.deleted = 0
      )

      INNER JOIN Action AS LeavedAction ON LeavedAction.id = (
        SELECT MAX(Action.id)
        FROM
          Action
          INNER JOIN ActionType ON ActionType.flatCode = 'leaved' AND ActionType.id = Action.actionType_id AND ActionType.deleted = 0
        WHERE
          Action.event_id = Event.id AND Action.deleted = 0
      )

      INNER JOIN Action FirstMoving ON FirstMoving.id = (
        SELECT min(A.id)
        FROM Action A
          INNER JOIN ActionType MovingAT ON MovingAT.flatCode = 'moving' AND A.actionType_id = MovingAT.id AND MovingAT.deleted = 0
        WHERE A.event_id = Event.id AND A.deleted = 0
      )

    WHERE
      {cond}
    ORDER BY
      Client.lastName,
      Client.firstName,
      Client.patrName
    '''.format(cond=db.joinAnd(cond))

    return db.query(stmt)


def getOperationsInfo(eventId):
    u"""
        Все операции (ActionType.serviceType = 4)  в рамках обращения {eventId}
    """

    db = QtGui.qApp.db
    OperationAction = db.table('Action')
    OperationActionType = db.table('ActionType')
    OperationPerson = db.table('Person')
    OperationOrgStructure = db.table('OrgStructure')

    queryTable = OperationAction.leftJoin(OperationActionType, OperationActionType['id'].eq(OperationAction['actionType_id']))
    queryTable = queryTable.leftJoin(OperationPerson, OperationPerson['id'].eq(OperationAction['person_id']))
    queryTable = queryTable.leftJoin(OperationOrgStructure, OperationOrgStructure['id'].eq(OperationPerson['orgStructure_id']))

    cols = [
        OperationAction['begDate'].alias('date'),
        OperationOrgStructure['name'].alias('orgStructure'),
        OperationActionType['name'].alias('operationName'),
        OperationAction['amount'].alias('amount'),
        OperationAction['isUrgent'].alias('isUrgent')
    ]
    cond = [
        OperationAction['event_id'].eq(eventId),
        OperationAction['deleted'].eq(0),
        OperationActionType['serviceType'].eq(4),
        OperationActionType['deleted'].eq(0)
    ]
    order = [
        OperationAction['id']
    ]

    stmt = db.selectStmt(queryTable, cols, cond, order=order)
    return db.query(stmt)


class CReportLeavedMovedDeadSetupDialog(CDialogBase, Ui_ReportLeavedMovedDeadSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())


    def setTitle(self, title):
        self.setWindowTitle(title)


    def saveData(self):
        result = True
        if self.rbByPeriod.isChecked() and not (self.chkByReceivedDate.isChecked() or self.chkByLeavedDate.isChecked()):
            result = result and self.checkInputMessage(u'период для даты поступления и/или даты выписки', False, self.chkByReceivedDate)
        return result


    def setParams(self, params):
        self.rbByPeriod.setChecked(params.get('byPeriod', False))
        self.edtLeavedDate.setDate(params.get('leavedDate', QtCore.QDate.currentDate()))
        self.chkByReceivedDate.setChecked(params.get('byReceivedDate', False))
        self.edtReceivedBegDate.setDate(params.get('receivedBegDate', QtCore.QDate.currentDate()))
        self.edtReceivedEndDate.setDate(params.get('receivedEndDate', QtCore.QDate.currentDate()))
        self.chkByLeavedDate.setChecked(params.get('byLeavedDate', True))
        self.edtLeavedBegDate.setDate(params.get('leavedBegDate', QtCore.QDate.currentDate()))
        self.edtLeavedEndDate.setDate(params.get('leavedEndDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', QtGui.qApp.currentOrgStructureId()))
        self.chkExternalId.setChecked(params.get('showExternalId', True))
        self.chkName.setChecked(params.get('showName', True))
        self.chkBirthDate.setChecked(params.get('showBirthDate', False))
        self.chkSex.setChecked(params.get('showSex', False))
        self.chkSocStatus.setChecked(params.get('showSocStatus', False))
        self.chkBenefits.setChecked(params.get('showBenefits', False))
        self.chkRegAddress.setChecked(params.get('showRegAddress', False))
        self.chkDeliveredBy.setChecked(params.get('showDeliveredBy', False))
        self.chkDeliveredTime.setChecked(params.get('showDeliveredTime', False))
        self.chkEventOrder.setChecked(params.get('showEventOrder', False))
        self.chkBegDate.setChecked(params.get('showBegDate', True))
        self.chkPrimary.setChecked(params.get('showPrimary', False))
        self.chkOrgStructure.setChecked(params.get('showOrgStructure', True))
        self.chkResult.setChecked(params.get('showResult', False))
        self.chkStatus.setChecked(params.get('showStatus', False))
        self.chkDiagnosis.setChecked(params.get('showDiagnosis', False))
        self.chkAutopsyDiagnosis.setChecked(params.get('showAutopsyDiagnosis', False))
        self.chkTrauma.setChecked(params.get('showTrauma', False))
        self.chkLeavedDate.setChecked(params.get('showLeavedDate', True))
        self.chkBedDays.setChecked(params.get('showBedDays', False))
        self.chkOperations.setChecked(params.get('showOperations', False))


    def params(self):
        return {
            'byPeriod': self.rbByPeriod.isChecked(),
            'leavedDate': self.edtLeavedDate.date(),
            'byReceivedDate': self.chkByReceivedDate.isChecked(),
            'receivedBegDate': self.edtReceivedBegDate.date(),
            'receivedEndDate': self.edtReceivedEndDate.date(),
            'byLeavedDate': self.chkByLeavedDate.isChecked(),
            'leavedBegDate': self.edtLeavedBegDate.date(),
            'leavedEndDate': self.edtLeavedEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'showExternalId': self.chkExternalId.isChecked(),
            'showName': self.chkName.isChecked(),
            'showBirthDate': self.chkBirthDate.isChecked(),
            'showSex': self.chkSex.isChecked(),
            'showSocStatus': self.chkSocStatus.isChecked(),
            'showBenefits': self.chkBenefits.isChecked(),
            'showRegAddress': self.chkRegAddress.isChecked(),
            'showDeliveredBy': self.chkDeliveredBy.isChecked(),
            'showDeliveredTime': self.chkDeliveredTime.isChecked(),
            'showEventOrder': self.chkEventOrder.isChecked(),
            'showBegDate': self.chkBegDate.isChecked(),
            'showPrimary': self.chkPrimary.isChecked(),
            'showOrgStructure': self.chkOrgStructure.isChecked(),
            'showResult': self.chkResult.isChecked(),
            'showStatus': self.chkStatus.isChecked(),
            'showDiagnosis': self.chkDiagnosis.isChecked(),
            'showAutopsyDiagnosis': self.chkAutopsyDiagnosis.isChecked(),
            'showTrauma': self.chkTrauma.isChecked(),
            'showLeavedDate': self.chkLeavedDate.isChecked(),
            'showBedDays': self.chkBedDays.isChecked(),
            'showOperations': self.chkOperations.isChecked()
        }


    def loadPreferences(self, preferences):
        CDialogBase.loadPreferences(self, preferences)
        self.rbByPeriod.setChecked(forceBool(getPref(preferences, 'byPeriod', False)))
        self.edtLeavedDate.setDate(forceDate(getPref(preferences, 'leavedDate', QtCore.QDate.currentDate())))
        self.chkByReceivedDate.setChecked(forceBool(getPref(preferences, 'byReceivedDate', False)))
        self.edtReceivedBegDate.setDate(forceDate(getPref(preferences, 'receivedBegDate', QtCore.QDate.currentDate())))
        self.edtReceivedEndDate.setDate(forceDate(getPref(preferences, 'receivedEndDate', QtCore.QDate.currentDate())))
        self.chkByLeavedDate.setChecked(forceBool(getPref(preferences, 'byLeavedDate', True)))
        self.edtLeavedBegDate.setDate(forceDate(getPref(preferences, 'leavedBegDate', QtCore.QDate.currentDate())))
        self.edtLeavedEndDate.setDate(forceDate(getPref(preferences, 'leavedEndDate', QtCore.QDate.currentDate())))
        self.cmbOrgStructure.setValue(forceRef(getPref(preferences, 'orgStructureId', QtGui.qApp.currentOrgStructureId())))


    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'byPeriod', toVariant(self.rbByPeriod.isChecked()))
        setPref(result, 'leavedDate', toVariant(self.edtLeavedDate.date()))
        setPref(result, 'byReceivedDate', toVariant(self.chkByReceivedDate.isChecked()))
        setPref(result, 'receivedBegDate', toVariant(self.edtReceivedBegDate.date()))
        setPref(result, 'receivedEndDate', toVariant(self.edtReceivedEndDate.date()))
        setPref(result, 'byLeavedDate', toVariant(self.chkByLeavedDate.isChecked()))
        setPref(result, 'leavedBegDate', toVariant(self.edtLeavedBegDate.date()))
        setPref(result, 'leavedEndDate', toVariant(self.edtLeavedEndDate.date()))
        setPref(result, 'orgStructureId', toVariant(self.cmbOrgStructure.value()))
        return result


    @QtCore.pyqtSlot(bool)
    def on_rbByLeavedDate_toggled(self, checked):
        self.stkFilterDate.setCurrentIndex(0)


    @QtCore.pyqtSlot(bool)
    def on_rbByPeriod_toggled(self, checked):
        self.stkFilterDate.setCurrentIndex(1)


class CReportLeavedMovedDead(CReport):
    u"""
        Отчёт по выписанным, переведённым в другой стационар и умершим пациентам (отчет для Абрамова О.Е.)
        Территориальная принадлежность: Москва
        Объект: МСК Б36
    """

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по выписанным, переведённым в другой стационар и умершим пациентам')


    def getSetupDialog(self, parent):
        result = CReportLeavedMovedDeadSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def getDescription(self, params):
        byPeriod = params.get('byPeriod', False)
        leavedDate = params.get('leavedDate', QtCore.QDate())
        byReceivedDate = params.get('byReceivedDate', False)
        receivedBegDate = params.get('receivedBegDate', QtCore.QDate())
        receivedEndDate = params.get('receivedEndDate', QtCore.QDate())
        byLeavedDate = params.get('byLeavedDate', True)
        leavedBegDate = params.get('leavedBegDate', QtCore.QDate())
        leavedEndDate = params.get('leavedEndDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)

        rows = []
        if byPeriod:
            if byReceivedDate:
                rows.append(u'Период поступления: с {begDate} по {endDate}'.format(begDate=receivedBegDate.toString('dd/MM/yyyy'),
                                                                                   endDate=receivedEndDate.toString('dd/MM/yyyy')))
            if byLeavedDate:
                rows.append(u'Период выписки: с {begDate} по {endDate}'.format(begDate=leavedBegDate.toString('dd/MM/yyyy'),
                                                                               endDate=leavedEndDate.toString('dd/MM/yyyy')))
        else:
            rows.append(u'Дата выписки: {date}'.format(date=leavedDate.toString('dd/MM/yyyy')))

        if not orgStructureId is None:
            rows.append(u'Отделение: {orgStructure}'.format(orgStructure=getOrgStructureName(orgStructureId)))

        return rows


    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        cursor.setCharFormat(QtGui.QTextCharFormat())

        columnNames = [
            'showExternalId', 'showName', 'showBirthDate', 'showSex', 'showSocStatus', 'showBenefits', 'showRegAddress',
            'showDeliveredBy', 'showDeliveredTime', 'showEventOrder', 'showBegDate', 'showPrimary', 'showOrgStructure',
            'showResult', 'showStatus', 'showDiagnosis', 'showAutopsyDiagnosis','showTrauma', 'showLeavedDate', 'showBedDays'
        ]
        operationColumn = 'showOperations'

        showColumn = dict([(showColumn, params.get(showColumn, False)) for showColumn in columnNames + [operationColumn]])

        baseColumnsDescription = [
            ('5?', [u'№ ИБ'], CReportBase.AlignLeft),
            ('5?', [u'Фамилия И.О.'], CReportBase.AlignLeft),
            ('5?', [u'Дата рождения'], CReportBase.AlignLeft),
            ('5?', [u'Пол'], CReportBase.AlignCenter),
            ('5?', [u'Социальный статус'], CReportBase.AlignLeft),
            ('5?', [u'Категория'], CReportBase.AlignLeft),
            ('5?', [u'Постоянная регистрация'], CReportBase.AlignLeft),
            ('5?', [u'Направлен (канал госпитализации)'], CReportBase.AlignLeft),
            ('5?', [u'Срок'], CReportBase.AlignLeft),
            ('5?', [u'Вид поступления'], CReportBase.AlignLeft),
            ('5?', [u'Дата, время поступления'], CReportBase.AlignLeft),
            ('5?', [u'Повторно'], CReportBase.AlignLeft),
            ('5?', [u'Отделение поступления'], CReportBase.AlignLeft),
            ('5?', [u'Исход'], CReportBase.AlignLeft),
            ('5?', [u'Состояние'], CReportBase.AlignLeft),
            ('5?', [u'Диагноз клинический'], CReportBase.AlignLeft),
            ('5?', [u'Диагноз патологоанатомический'], CReportBase.AlignLeft),
            ('5?', [u'Травма\nОбстоятельства'], CReportBase.AlignLeft),
            ('5?', [u'Дата выписки'], CReportBase.AlignLeft),
            ('5?', [u'Койко-дней'], CReportBase.AlignLeft)
        ]
        operationColumnsDescription = [
            ('5?', [u'Дата операции'], CReportBase.AlignLeft),
            ('5?', [u'Отделение'], CReportBase.AlignLeft),
            ('5?', [u'Операция'], CReportBase.AlignLeft),
            ('5?', [u'Количество'], CReportBase.AlignLeft),
            ('5?', [u'Экстренно'], CReportBase.AlignLeft)
        ]

        tableColumns = [baseColumnsDescription[i] for i, colName in enumerate(columnNames) if showColumn[colName]]
        if showColumn[operationColumn]:
            tableColumns.extend(operationColumnsDescription)

        table  = createTable(cursor, tableColumns)

        columnIndex = {}
        for col in columnNames + [operationColumn]:
            columnIndex[col] = len(columnIndex)

        byPeriod = params.get('byPeriod', False)
        leavedDate = params.get('leavedDate', QtCore.QDate())
        byReceivedDate = params.get('byReceivedDate', False)
        receivedBegDate = params.get('receivedBegDate', QtCore.QDate())
        receivedEndDate = params.get('receivedEndDate', QtCore.QDate())
        byLeavedDate = params.get('byLeavedDate', True)
        leavedBegDate = params.get('leavedBegDate', QtCore.QDate())
        leavedEndDate = params.get('leavedEndDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)

        # detailByOrgStructure = orgStructureId is None

        eventOrderMap = {
            1: u'плановый',
            2: u'экстренный',
            3: u'самотеком',
            4: u'принудительный',
            5: u'неотложный'
        }

        eventIsPrimaryMap = {
            1: u'первичный',
            2: u'повторный',
            3: u'активное посещение',
            4: u'перевозка'
        }

        query = selectDataByEvents(byPeriod, leavedDate, byReceivedDate, receivedBegDate, receivedEndDate, byLeavedDate, leavedBegDate, leavedEndDate, orgStructureId)
        self.setQueryText(forceString(query.lastQuery()))

        reportData = []

        while query.next():
            record = query.record()
            # orgStructureId = forceRef(record.value('orgStructureId'))
            # leavedActionId = forceRef(record.value('leavedActionId'))

            clientId = forceRef(record.value('clientId'))
            eventId = forceRef(record.value('eventId'))
            eventExternalId = forceString(record.value('eventExternalId'))
            order = forceInt(record.value('eventOrder'))
            isPrimary = forceInt(record.value('eventIsPrimary'))
            # result = forceString(record.value('result'))
            # receivedOrgStructure = forceString(record.value('receivedOrgStructure'))

            begDate = forceDateTime(record.value('begDate'))
            leavedDate = forceDate(record.value('leavedDate'))
            bedDays = forceInt(record.value('bedDays'))

            receivedActionId = forceRef(record.value('receivedActionId'))
            statCardActionId = forceRef(record.value('statCardActionId'))
            firstExaminationActionId = forceRef(record.value('firstExaminationActionId'))
            traumatologistActionId = forceRef(record.value('traumatologistActionId'))

            epicrisisId = forceRef(record.value('epicrisisActionId'))

            autopsyActionId = forceRef(record.value('autopsyActionId'))

            clientRecord = getClientRecord(clientId)
            lastName = forceString(clientRecord.value('lastName'))
            firstName = forceString(clientRecord.value('firstName'))
            patrName = forceString(clientRecord.value('patrName'))
            birthDate = forceDate(clientRecord.value('birthDate'))
            sex = clientRecord.value('sex')
            regAddress = forceString(clientRecord.value('regAddress'))

            rowData = [
                eventExternalId if showColumn['showExternalId'] else None,
                formatShortName(lastName, firstName, patrName) if showColumn['showName'] else None,
                birthDate.toString('dd/MM/yyyy') if showColumn['showBirthDate'] else None,
                formatSex(sex) if showColumn['showSex'] else None,
                getActionPropertyString(statCardActionId, u'Социальный статус:') if showColumn['showSocStatus'] else None,
                getActionPropertyString(statCardActionId, u'Категория льготности:') if showColumn['showBenefits'] else None,
                regAddress if showColumn['showRegAddress'] else None,
                getActionPropertyOrganisation(receivedActionId, u'Кем доставлен') if showColumn['showDeliveredBy'] else None,
                getActionPropertyString(receivedActionId, u'Доставлен') if showColumn['showDeliveredTime'] else None,
                eventOrderMap.get(order, u'') if showColumn['showEventOrder'] else None,
                begDate.toString('dd/MM/yyyy hh:mm') if showColumn['showBegDate'] else None,
                eventIsPrimaryMap.get(isPrimary, u'') if showColumn['showPrimary'] else None,
                getActionPropertyOrgStructure(receivedActionId, u'Направлен в отделение') if showColumn['showOrgStructure'] else None,
                getActionPropertyString(statCardActionId, u'Исход госпитализации:') if showColumn['showResult'] else None,
                getActionPropertyString(firstExaminationActionId, u'Status praesens:%Общее состояние:') if showColumn['showStatus'] else None,
                getActionPropertyString(epicrisisId, u'Основное заболевание:') if showColumn['showDiagnosis'] else None,
                getActionPropertyString(autopsyActionId, u'Патолого-Анатомический диагноз%') if showColumn['showAutopsyDiagnosis'] else None,
                getActionPropertyString(traumatologistActionId, u'Травма:') if showColumn['showTrauma'] else None,
                leavedDate.toString('dd/MM/yyyy') if showColumn['showLeavedDate'] else None,
                bedDays if showColumn['showBedDays'] else None
            ]

            eventRow = [data for colName, data in zip(columnNames, rowData) if showColumn[colName]]

            operations = []
            if showColumn[operationColumn]:
                operationsQuery = getOperationsInfo(eventId)
                while operationsQuery.next():
                    operation = operationsQuery.record()
                    operationRow = [
                        forceDate(operation.value('date')).toString('dd/MM/yyyy'),
                        forceString(operation.value('orgStructure')),
                        forceString(operation.value('operationName')),
                        forceInt(operation.value('amount')),
                        u'экстренно' if forceBool(operation.value('isUrgent')) else u''
                    ]
                    operations.append(operationRow)

            reportData.append({
                'row': eventRow,
                'operations': operations
            })


        for event in reportData:
            eventRow = event['row']
            eventOperations = event['operations']
            row = table.addRow()
            for col, text in enumerate(eventRow):
                table.setText(row, col, text)

            for i, operationRow in enumerate(eventOperations):
                if i != 0:
                    row = table.addRow()
                for col, text in enumerate(operationRow):
                    table.setText(row, len(eventRow) + col, text)

            operationsCount = len(eventOperations)
            for col in xrange(len(eventRow)):
                table.mergeCells(row - operationsCount + 1, col, operationsCount, 1)

        return doc
