# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants, getOrganisationInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportReceivedAndRefusalClients import Ui_ReportReceivedAndRefusalClientsSetupDialog
from library.DialogBase import CDialogBase
from library.Utils import forceDate, forceDateTime, forceRef, forceString, forceInt
from library.database import CUnionTable


def getClientRelations(clientId):
    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableClientRelation = db.table('ClientRelation')
    tableRelationType = db.table('rbRelationType')

    queryTableD = tableClientRelation.leftJoin(tableClient, tableClient['id'].eq(tableClientRelation['relative_id']))
    queryTableD = queryTableD.leftJoin(tableRelationType, tableRelationType['id'].eq(tableClientRelation['relativeType_id']))
    colsD = [
        "concat_ws(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName",
        "concat_ws(' ', rbRelationType.leftName, rbRelationType.rightName) AS relationType"
    ]
    condD = [
        tableClientRelation['deleted'].eq(0),
        tableClientRelation['client_id'].eq(clientId)
    ]
    stmtD = db.selectStmt(queryTableD, colsD, condD)

    queryTableB = tableClientRelation.leftJoin(tableClient, tableClient['id'].eq(tableClientRelation['client_id']))
    queryTableB = queryTableB.leftJoin(tableRelationType, tableRelationType['id'].eq(tableClientRelation['relativeType_id']))
    colsB = [
        "concat_ws(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName",
        "concat_ws(' ', rbRelationType.rightName, rbRelationType.leftName) AS relationType"
    ]
    condB = [
        tableClientRelation['deleted'].eq(0),
        tableClientRelation['relative_id'].eq(clientId)
    ]
    stmtB = db.selectStmt(queryTableB, colsB, condB)

    stmt = db.selectStmt(CUnionTable(db, stmtD, stmtB, 'T')) # Direct + Backward relation+s
    query = db.query(stmt)

    relations = []
    while query.next():
        record = query.record()
        clientName = forceString(record.value('clientName'))
        relationType = forceString(record.value('relationType'))
        relations.append(relationType + ': ' + clientName)

    return  relations


def selectData(params):
    def getPropertyStringStmt(name, actionId):
        qTable = tableAP.leftJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        qTable = qTable.leftJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
        return db.selectStmt(qTable, tableAPS['value'], db.joinAnd([tableAP['action_id'].eq(actionId),
                                                                    tableAP['deleted'].eq(0),
                                                                    tableAPT['name'].like(name)]), order='', limit=1)

    def getPropertyOrganisationStmt(name):
        qTable = tableAP.leftJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        qTable = qTable.leftJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
        qTable = qTable.leftJoin(tableAPO, tableAPO['id'].eq(tableAP['id']))
        qTable = qTable.leftJoin(tableOrganisation, db.joinAnd([tableOrganisation['id'].eq(tableAPO['value']),
                                                                tableOrganisation['deleted'].eq(0)]))
        field = 'if(%s IS NOT NULL, %s, %s)' % (tableOrganisation['id'], tableOrganisation['shortName'], tableAPS['value'])
        return db.selectStmt(qTable, field, db.joinAnd([tableAP['action_id'].eq(tableAction['id']),
                                                        tableAP['deleted'].eq(0),
                                                        tableAPT['name'].like(name)]), order='', limit=1)

    def getPropertyOrgStructureStmt(name):
        qTable = tableAP.leftJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        qTable = qTable.leftJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
        qTable = qTable.leftJoin(tableOrgStructure, db.joinAnd([tableOrgStructure['id'].eq(tableAPOS['value']),
                                                                tableOrgStructure['deleted'].eq(0)]))
        return db.selectStmt(qTable, tableOrgStructure['name'], db.joinAnd([tableAP['action_id'].eq(tableAction['id']),
                                                                            tableAP['deleted'].eq(0),
                                                                            tableAPT['name'].like(name)]), order='', limit=1)

    def getPropertyHospitalBedProfileStmt(name):
        qTable = tableAP.leftJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        qTable = qTable.leftJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
        qTable = qTable.leftJoin(tableHospitalBed, db.joinAnd([tableHospitalBed['id'].eq(tableAPHB['value'])]))
        # extracting profile
        qTable = qTable.leftJoin(tableHospitalBedProfile,
                                 tableHospitalBed['profile_id'].eq(tableHospitalBedProfile['id']))
        return db.selectStmt(qTable, tableHospitalBedProfile['name'], db.joinAnd([
            tableAP['action_id'].eq(tableMovingAction['id']),
            tableAPT['name'].like(name)
        ]), order='', limit=1)

    # фантазии нехватило эту функцию обозвать как-то иначе
    def getPropertyBedProfileStmt(name):
        qTable = tableAP.leftJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        qTable = qTable.leftJoin(tableAPR, tableAPR['id'].eq(tableAP['id']))
        qTable = qTable.leftJoin(tableAPHBP, tableAPHBP['id'].eq(tableAP['id']))
        # extracting profile
        qTable = qTable.leftJoin(
            tableHospitalBedProfile,
            tableHospitalBedProfile['id'].eq(
                db.if_(tableAPR['id'].isNull(), tableAPHBP['value'], tableAPR['value'])
            )
        )
        return db.selectStmt(qTable, tableHospitalBedProfile['name'], db.joinAnd([
            tableAP['action_id'].eq(tableMovingAction['id']),
            tableAPT['name'].like(name)
        ]), order='', limit=1)

    begDateTime = QtCore.QDateTime(params.get('begDate', QtCore.QDate.currentDate()), params.get('begTime', QtCore.QTime.currentTime()))
    endDateTime = QtCore.QDateTime(params.get('endDate', QtCore.QDate.currentDate()), params.get('endTime', QtCore.QTime.currentTime()))
    orgStructureId = params.get('orgStructureId', None)
    orderBy = params.get('orderBy', 0)

    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAP = db.table('ActionProperty').alias('AP')
    tableAPT = db.table('ActionPropertyType').alias('APT')
    tableAPO = db.table('ActionProperty_Organisation').alias('APO')
    tableAPOS = db.table('ActionProperty_OrgStructure').alias('APOS')
    tableAPS = db.table('ActionProperty_String').alias('APS')
    tableAPHB = db.table('ActionProperty_HospitalBed').alias('APHB')
    tableAPHBP = db.table('ActionProperty_rbHospitalBedProfile').alias('APHBP')
    tableAPR = db.table('ActionProperty_Reference').alias('APR')
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableOrganisation = db.table('Organisation')
    tableOrgStructure = db.table('OrgStructure')
    tablePerson = db.table('Person')
    tableHospitalBed = db.table('OrgStructure_HospitalBed')
    tableHospitalBedProfile = db.table('rbHospitalBedProfile')

    tableClientDocument = db.table('ClientDocument')
    tableDocumentType = db.table('rbDocumentType')

    tableCompulsoryPolicy = db.table('ClientPolicy').alias('CompulsoryPolicy')
    tableCompulsoryPK = db.table('rbPolicyKind').alias('CompulsoryPK')

    tableVoluntaryPolicy = db.table('ClientPolicy').alias('VoluntaryPolicy')
    tableVoluntaryPK = db.table('rbPolicyKind').alias('VoluntaryPK')

    tableLeavedAction = tableAction.alias('LeavedAction')
    tableLeavedActionType = tableActionType.alias('LeavedActionType')

    tableMovingAction = tableAction.alias('MovingAction')
    tableMovingActionType = tableActionType.alias('MovingActionType')

    queryTable = tableAction.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
    queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))

    queryTable = queryTable.leftJoin(tableClientDocument, '%s = getClientDocumentId(%s)' % (tableClientDocument['id'].name(), tableClient['id'].name()))
    queryTable = queryTable.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableClientDocument['documentType_id']))

    queryTable = queryTable.leftJoin(tableCompulsoryPolicy, '%s = getClientPolicyId(%s, 1)' % (tableCompulsoryPolicy['id'].name(), tableClient['id'].name()))
    queryTable = queryTable.leftJoin(tableCompulsoryPK, tableCompulsoryPK['id'].eq(tableCompulsoryPolicy['policyKind_id']))

    queryTable = queryTable.leftJoin(tableVoluntaryPolicy, '%s = getClientPolicyId(%s, 0)' % (tableVoluntaryPolicy['id'].name(), tableClient['id'].name()))
    queryTable = queryTable.leftJoin(tableVoluntaryPK, tableVoluntaryPK['id'].eq(tableVoluntaryPolicy['policyKind_id']))

    queryTable = queryTable.leftJoin(tableLeavedActionType, tableLeavedActionType['flatCode'].eq('leaved'))
    queryTable = queryTable.leftJoin(tableLeavedAction, db.joinAnd([tableLeavedAction['event_id'].eq(tableEvent['id']),
                                                                    tableLeavedAction['actionType_id'].eq(tableLeavedActionType['id'])]))

    queryTable = queryTable.leftJoin(tableMovingActionType, tableMovingActionType['flatCode'].eq('moving'))
    queryTable = queryTable.leftJoin(tableMovingAction,
                                     db.joinAnd([
                                         tableMovingAction['event_id'].eq(tableEvent['id']),
                                         tableMovingAction['actionType_id'].eq(tableMovingActionType['id'])
                                     ]))

    cols = [
        tableAction['begDate'].alias('actionDateTime'),

        tableClient['id'].alias('clientId'),
        "concat_ws(' ', %s, %s, %s) AS clientName" % (tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name()),
        tableClient['sex'].alias('clientSex'),
        tableClient['birthDate'].alias('clientBirthDate'),
        'TIMESTAMPDIFF(YEAR, %s, CURDATE()) AS clientAge' % tableClient['birthDate'].name(),
        'getClientLocAddress(%s) AS clientLocAddress' % tableClient['id'].name(),
        'getClientRegAddress(%s) AS clientRegAddress' % tableClient['id'].name(),
        'getClientContacts(%s) AS clientContacts' % tableClient['id'].name(),

        u"concat_ws(' ', %s, 'серия:', %s, '№', %s) AS clientDocument" % (tableDocumentType['name'].name(),
                                                                          tableClientDocument['serial'].name(),
                                                                          tableClientDocument['number'].name()),
        tableClientDocument['date'].alias('clientDocumentDate'),

        u"concat_ws(' ', %s, 'серия:', %s, '№', %s) AS clientCompulsoryPolicy" % (tableCompulsoryPK['name'].name(),
                                                                                  tableCompulsoryPolicy['serial'].name(),
                                                                                  tableCompulsoryPolicy['number'].name()                                                                                                ),
        tableCompulsoryPolicy['begDate'].alias('clientCompulsoryPolicyDate'),

        u"concat_ws(' ', %s, 'серия:', %s, '№', %s) AS clientVoluntaryPolicy" % (tableVoluntaryPK['name'].name(),
                                                                                 tableVoluntaryPolicy['serial'].name(),
                                                                                 tableVoluntaryPolicy['number'].name()),
        tableVoluntaryPolicy['begDate'].alias('clientVoluntaryPolicyDate'),

        '(%s) AS relegateOrg' % getPropertyOrganisationStmt(u'Кем направлен'),
        '(%s) AS deliveredOrg' % getPropertyOrganisationStmt(u'Кем доставлен'),
        '(%s) AS otherRelegateOrg' % getPropertyOrganisationStmt(u'Прочие направители'),
        '(%s) AS receivedOrgStructure' % getPropertyOrgStructureStmt(u'Направлен в отделение'),

        tableEvent['externalId'].alias('cardNumber'),

        '(%s) AS relegateOrgDiagnosis' % getPropertyStringStmt(u'Диагноз направителя', tableAction['id']),
        '(%s) AS receivedOrgDiagnosis' % getPropertyStringStmt(u'Диагноз приемного отделения', tableAction['id']),

        tableLeavedAction['endDate'].alias('leavedDate'),
        '(%s) AS leavedResult' % getPropertyStringStmt(u'Исход госпитализации', tableLeavedAction['id']),
        '(%s) AS leavedTo' % getPropertyStringStmt(u'Переведен в стационар', tableLeavedAction['id']),

        '(%s) AS msgToRelatives' % getPropertyStringStmt(u'Сообщено родственникам', tableAction['id']),
        '(%s) AS reason' % getPropertyStringStmt(u'Причина отказа от госпитализации', tableAction['id']),
        '(%s) AS takenMeasures' % getPropertyStringStmt(u'Принятые меры при отказе в госпитализации', tableAction['id']),
        '(%s) AS notes' % getPropertyStringStmt(u'Примечание', tableAction['id']),
        tableEvent['order'].alias('eventOrder'),
        '(%s) AS hospitalBedProfile' % getPropertyBedProfileStmt(u'профиль койки'),  # getPropertyHospitalBedProfileStmt(u'койка'),
        '(%s) AS bedProfile' % getPropertyStringStmt(u'Профиль', tableAction['id']),
    ]

    cond = [
        tableActionType['flatCode'].eq('received'),
        tableAction['begDate'].datetimeGe(begDateTime),
        tableAction['begDate'].datetimeLe(endDateTime),
        tableAction['deleted'].eq(0),
        tableLeavedAction['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        tableClient['deleted'].eq(0),
        db.joinOr([tableClientDocument['id'].isNull(), tableClientDocument['deleted'].eq(0)]),
        db.joinOr([tableCompulsoryPolicy['id'].isNull(), tableCompulsoryPolicy['deleted'].eq(0)]),
        db.joinOr([tableVoluntaryPolicy['id'].isNull(), tableVoluntaryPolicy['deleted'].eq(0)])
    ]

    if not orgStructureId is None:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if orderBy == 0:  # по ФИО клиента
        order = [
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableAction['begDate']
        ]
    elif orderBy == 1:  # по времени поступления в стационар
        order = [
            tableAction['begDate'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName']
        ]
    else:
        order = []

    stmt = db.selectStmt(queryTable, cols, cond, order=order, isDistinct=True)
    return db.query(stmt)


class CReportReceivedAndRefusalClientsSetupDialog(CDialogBase, Ui_ReportReceivedAndRefusalClientsSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    @QtCore.pyqtSlot(bool)
    def on_chkHospitalBedProfile_clicked(self, checked):
        if checked and self.chkBedProfile.isChecked():
            self.chkBedProfile.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_chkBedProfile_clicked(self, checked):
        if checked and self.chkHospitalBedProfile.isChecked():
            self.chkHospitalBedProfile.setChecked(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime.currentTime()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtEndTime.setTime(params.get('endTime', QtCore.QTime.currentTime()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        self.chkRegAddress.setChecked(params.get('chkRegAddress', True))
        self.chkLocAddress.setChecked(params.get('chkLocAddress', True))
        self.chkContacts.setChecked(params.get('chkContacts', True))
        self.chkRelations.setChecked(params.get('chkRelations', True))
        self.chkDocument.setChecked(params.get('chkDocument', True))
        self.chkCompulsoryPolicy.setChecked(params.get('chkCompulsoryPolicy', True))
        self.chkVoluntaryPolicy.setChecked(params.get('chkVoluntaryPolicy', True))
        self.chkRelegateOrg.setChecked(params.get('chkRelegateOrg', True))
        self.chkDeliveredOrg.setChecked(params.get('chkDeliveredOrg', True))
        self.chkRelegateOrgDiagnosis.setChecked(params.get('chkRelegateOrgDiagnosis', True))
        self.chkReceivedOrgDiagnosis.setChecked(params.get('chkReceivedOrgDiagnosis', True))
        self.chkLeavedInfo.setChecked(params.get('chkLeavedInfo', True))
        self.chkMessageToRelatives.setChecked(params.get('chkMessageToRelatives', True))
        self.chkNotes.setChecked(params.get('chkNotes', True))
        self.cmbOrderBy.setCurrentIndex(params.get('chkOrderBy', 0))
        self.chkSex.setChecked(params.get('chkSex', True))
        self.chkAge.setChecked(params.get('chkAge', True))
        self.chkHour.setChecked(params.get('chkHour', True))
        self.chkCardNumber.setChecked(params.get('chkCardNumber', True))
        self.chkNotHospitalized.setChecked(params.get('chkNotHospitalized', True))
        self.chkEventOrder.setChecked(params.get('chkEventOrder', True))
        self.chkBedProfile.setChecked(params.get('chkBedProfile', True))
        self.chkHospitalBedProfile.setChecked(params.get('chkHospitalBedProfile', False))
        self.chkOtherRelegateOrg.setChecked(params.get('chkOtherRelegateOrg', True))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'begTime': self.edtBegTime.time(),
            'endDate': self.edtEndDate.date(),
            'endTime': self.edtEndTime.time(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'chkRegAddress': self.chkRegAddress.isChecked(),
            'chkLocAddress': self.chkLocAddress.isChecked(),
            'chkContacts': self.chkContacts.isChecked(),
            'chkRelations': self.chkRelations.isChecked(),
            'chkDocument': self.chkDocument.isChecked(),
            'chkCompulsoryPolicy': self.chkCompulsoryPolicy.isChecked(),
            'chkVoluntaryPolicy': self.chkVoluntaryPolicy.isChecked(),
            'chkRelegateOrg': self.chkRelegateOrg.isChecked(),
            'chkDeliveredOrg': self.chkDeliveredOrg.isChecked(),
            'chkRelegateOrgDiagnosis': self.chkRelegateOrgDiagnosis.isChecked(),
            'chkReceivedOrgDiagnosis': self.chkReceivedOrgDiagnosis.isChecked(),
            'chkLeavedInfo': self.chkLeavedInfo.isChecked(),
            'chkMessageToRelatives': self.chkMessageToRelatives.isChecked(),
            'chkNotes': self.chkNotes.isChecked(),
            'cmbOrderBy': self.cmbOrderBy.currentIndex(),
            'chkSex': self.chkSex.isChecked(),
            'chkAge': self.chkAge.isChecked(),
            'chkHour': self.chkHour.isChecked(),
            'chkCardNumber': self.chkCardNumber.isChecked(),
            'chkNotHospitalized': self.chkNotHospitalized.isChecked(),
            'chkEventOrder': self.chkEventOrder.isChecked(),
            'chkBedProfile': self.chkBedProfile.isChecked(),
            'chkHospitalBedProfile': self.chkHospitalBedProfile.isChecked(),
            'chkOtherRelegateOrg': self.chkOtherRelegateOrg.isChecked(),
        }


class CReportReceivedAndRefusalClients(CReport):

    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Журнал учета приема больных ф.001/у')

    def getSetupDialog(self, parent):
        result = CReportReceivedAndRefusalClientsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(QtGui.QTextCharFormat())

        orgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        headerLeft = u'Министерство здравоохранения\n' \
                     u'и социального развития\n' \
                     u'Российской Федерации\n' \
                     u'%s\n' \
                     u'%s' % (orgInfo['fullName'], forceString(QtGui.qApp.db.translate('Organisation', 'id', orgInfo['id'], 'Address')))

        headerRight = u'Медицинская документация\n' \
                      u'Форма № 001/у\n' \
                      u'утв. приказом\n' \
                      u'Минздрава СССР\n' \
                      u'№ 1030 от 04.10.1980 г'
        headerColumns = [
            ('50%', [''], CReportBase.AlignLeft),
            ('50%', [''], CReportBase.AlignRight)
        ]
        table = createTable(cursor, headerColumns, border=0, cellPadding=2, cellSpacing=0)
        table.setText(0, 0, headerLeft)
        table.setText(0, 1, headerRight)
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'ЖУРНАЛ\nучета приема больных и отказов в госпитализации\n')
        cursor.insertText(u'за период с %s %s по %s %s \n' % (params['begDate'].toString('dd.MM.yyyy'),
                                                              params['begTime'].toString('hh:mm'),
                                                              params['endDate'].toString('dd.MM.yyyy'),
                                                              params['endTime'].toString('hh:mm')))
        cursor.insertText(u'отчет составлен: %s' % QtCore.QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm'))
        cursor.movePosition(QtGui.QTextCursor.End)

        showRegAddress = params.get('chkRegAddress', True)
        showLocAddress = params.get('chkLocAddress', True)
        showContacts = params.get('chkContacts', True)
        showRelations = params.get('chkRelations', True)
        showDocument = params.get('chkDocument', True)
        showCompulsoryPolicy = params.get('chkCompulsoryPolicy', True)
        showVoluntaryPolicy = params.get('chkVoluntaryPolicy', True)
        showRelegateOrg = params.get('chkRelegateOrg', True)
        showDeliveredOrg = params.get('chkDeliveredOrg', True)
        showRelegateOrgDiagnosis = params.get('chkRelegateOrgDiagnosis', True)
        showReceivedOrgDiagnosis = params.get('chkReceivedOrgDiagnosis', True)
        showLeavedInfo = params.get('chkLeavedInfo', True)
        showMessageToRelatives = params.get('chkMessageToRelatives', True)
        showNotes = params.get('chkNotes', True)
        showSex = params.get('chkSex', True)
        showAge = params.get('chkAge', True)
        showHour = params.get('chkHour', True)
        showCardNumber = params.get('chkCardNumber')
        showNotHospitalized = params.get('chkNotHospitalized')
        showEventOrder = params.get('chkEventOrder')
        showBedProfile = params.get('chkBedProfile')
        showHospitalBedProfile = params.get('chkHospitalBedProfile')
        showOtherRelegateOrg = params.get('chkOtherRelegateOrg')

        columnNames = [
            'num',
            'receivedDate',
            'receivedTime',
            'clientName',
            'clientSex',
            'clientBirthDate',
            'clientAge',
            'clientContacts',
            'clientDocument',
            'clientPolicy',
            'relegateOrDeliveredOrg',
            'receivedOrgStructure',
            'bedProfile',
            'hospitalBedProfile',
            'cardNumber',
            'relegateOrgDiagnosis',
            'receivedOrgDiagnosis',
            'eventOrder',
            'leavedInfo',
            'messageToRelatives',
            'reason',
            'takenMeasures',
            'notes'
        ]

        columnDescription = [
            ('10?', [u'№ п/п', u''], CReportBase.AlignRight),
            ('10?', [u'Поступление', u'дата'], CReportBase.AlignRight),
            ('10?', [u'', u'час'], CReportBase.AlignRight),
            ('20?', [u'ФИО пациента', u''], CReportBase.AlignRight),
            ('10?', [u'Пол', u''], CReportBase.AlignRight),
            ('10?', [u'Дата рождения', u''], CReportBase.AlignRight),
            ('10?', [u'Возраст', u''], CReportBase.AlignRight),
            ('20?', [u'Постоянное место жительства (регистрация/проживание), контактные данные, родственные связи', u''], CReportBase.AlignRight),
            ('20?', [u'Документ, удостоверяющий личность', u''], CReportBase.AlignRight),
            ('20?', [u'Полисные данные (ОМС/ДМС)', u''], CReportBase.AlignRight),
            ('10?', [u'Каким учреждением был направлен или доставлен', u''], CReportBase.AlignRight),
            ('20?', [u'Отделение, в которое помещен пациент', u''], CReportBase.AlignRight),
            ('15?', [u'Профиль', u''], CReportBase.AlignRight),
            ('15?', [u'Профиль койки', u''], CReportBase.AlignRight),
            ('10?', [u'№ карты стационарного больного (истории родов)', u''], CReportBase.AlignRight),
            ('10?', [u'Диагноз направившего учреждения', u''], CReportBase.AlignRight),
            ('10?', [u'Диагноз при поступлении', u''], CReportBase.AlignRight),
            ('15?', [u'Порядок наступления', u''], CReportBase.AlignRight),
            ('10?', [u'Выписан, переведен в другой  стационар, умер', u''], CReportBase.AlignRight),
            ('10?', [u'Отметка о сообщении родственникам или учреждению', u''], CReportBase.AlignRight),
            ('15?', [u'Если не был госпитализирован', u'указать причину'], CReportBase.AlignRight),
            ('15?', [u'', u'принятые меры при отказе в госпитализации'], CReportBase.AlignRight),
            ('10?', [u'Примечание', u''], CReportBase.AlignRight)
        ]

        showColumn = dict([(name, True) for name in columnNames])
        showColumn['clientContacts'] = showRegAddress or showLocAddress or showContacts or showRelations
        showColumn['clientDocument'] = showDocument
        showColumn['clientPolicy'] = showCompulsoryPolicy or showVoluntaryPolicy
        showColumn['relegateOrDeliveredOrg'] = showRelegateOrg or showDeliveredOrg
        showColumn['relegateOrgDiagnosis'] = showRelegateOrgDiagnosis
        showColumn['receivedOrgDiagnosis'] = showReceivedOrgDiagnosis
        showColumn['leavedInfo'] = showLeavedInfo
        showColumn['messageToRelatives'] = showMessageToRelatives
        showColumn['notes'] = showNotes
        showColumn['clientSex'] = showSex
        showColumn['clientAge'] = showAge
        showColumn['receivedTime'] = showHour
        showColumn['cardNumber'] = showCardNumber
        showColumn['reason'] = showColumn['takenMeasures'] = showNotHospitalized
        showColumn['eventOrder'] = showEventOrder
        showColumn['hospitalBedProfile'] = showHospitalBedProfile
        showColumn['bedProfile'] = showBedProfile

        columnNumber = {}
        tableColumns = []
        for i, name in enumerate(columnNames):
            if showColumn[name]:
                columnNumber[name] = len(columnNumber)
                tableColumns.append(columnDescription[i])

        cursor.insertBlock()
        table = createTable(cursor, tableColumns)
        if showHour:
            table.mergeCells(0, columnNumber['receivedDate'], 1, 2)
        if showNotHospitalized:
            table.mergeCells(0, columnNumber['reason'], 1, 2)
        for col in xrange(len(tableColumns)):
            twoRowsHeaders = [columnNumber['receivedDate']]
            if showHour:
                twoRowsHeaders += [columnNumber['receivedTime']]
            if showNotHospitalized:
                twoRowsHeaders += [columnNumber['reason'], columnNumber['takenMeasures']]
            if col not in twoRowsHeaders:
                table.mergeCells(0, col, 2, 1)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        eventOrderValues = [
            u'',                # db enum starts with 1
            u'планово',
            u'экстренно',
            u'самотеком',
            u'принудительно',
            u'неотложно',
        ]

        rowNumber = 0
        while query.next():
            rowNumber += 1
            record = query.record()
            actionDateTime = forceDateTime(record.value('actionDateTime'))
            clientId = forceRef(record.value('clientId'))
            clientName = forceString(record.value('clientName'))
            clientSex = forceString(record.value('clientSex'))
            clientBirthDate = forceDate(record.value('clientBirthDate'))
            clientAge = forceString(record.value('clientAge'))
            clientLocAddress = forceString(record.value('clientLocAddress'))
            clientRegAddress = forceString(record.value('clientRegAddress'))
            clientContacts = forceString(record.value('clientContacts'))
            clientDocument = forceString(record.value('clientDocument'))
            clientDocumentDate = forceDate(record.value('clientDocumentDate'))
            clientCompulsoryPolicy = forceString(record.value('clientCompulsoryPolicy'))
            clientCompulsoryPolicyDate = forceDate(record.value('clientCompulsoryPolicyDate'))
            clientVoluntaryPolicy = forceString(record.value('clientVoluntaryPolicy'))
            clientVoluntaryPolicyDate = forceDate(record.value('clientVoluntaryPolicyDate'))
            relegateOrg = forceString(record.value('relegateOrg'))
            deliveredOrg = forceString(record.value('deliveredOrg'))
            receivedOrgStructure = forceString(record.value('receivedOrgStructure'))
            hospitalBedProfile = forceString(record.value('hospitalBedProfile'))
            bedProfile = forceString(record.value('bedProfile'))
            cardNumber = forceString(record.value('cardNumber'))
            relegateOrgDiag = forceString(record.value('relegateOrgDiagnosis'))
            receivedOrgDiag = forceString(record.value('receivedOrgDiagnosis'))
            leavedDate = forceDate(record.value('leavedDate'))
            leavedResult = forceString(record.value('leavedResult'))
            leavedTo = forceString(record.value('leavedTo'))
            msgToRelatives = forceString(record.value('msgToRelaties'))
            eventOrder = eventOrderValues[forceInt(record.value('eventOrder'))]
            reason = forceString(record.value('reason'))
            takenMeasures = forceString(record.value('takenMeasures'))
            notes = forceString(record.value('notes'))
            otherRelegateOrg = forceString(record.value('otherRelegateOrg'))

            i = table.addRow()
            table.setText(i, 0, rowNumber)

            if showColumn['receivedDate']:
                table.setText(i, columnNumber['receivedDate'], actionDateTime.date().toString('dd.MM.yyyy'))

            if showColumn['receivedTime']:
                table.setText(i, columnNumber['receivedTime'], actionDateTime.time().toString('hh:mm'))

            if showColumn['clientName']:
                table.setText(i, columnNumber['clientName'], clientName)

            if showColumn['clientSex']:
                table.setText(i, columnNumber['clientSex'], u'м' if clientSex == '1' else u'ж')

            if showColumn['clientBirthDate']:
                table.setText(i, columnNumber['clientBirthDate'], clientBirthDate.toString('dd.MM.yyyy'))

            if showColumn['clientAge']:
                table.setText(i, columnNumber['clientAge'], clientAge)

            if showColumn['clientContacts']:
                address = []
                if showRegAddress and clientRegAddress != '':
                    address.append(clientRegAddress)
                if showLocAddress and clientLocAddress != '':
                    address.append(clientLocAddress)
                contacts = '/'.join(address)

                if showContacts:
                    contacts = contacts + '\n' + clientContacts

                if showRelations:
                    contacts = contacts + '\n' + '\n'.join(getClientRelations(clientId))

                table.setText(i, columnNumber['clientContacts'], contacts)

            if showColumn['clientDocument']:
                text =  u'%s выдан: %s' % (clientDocument, clientDocumentDate.toString('dd.MM.yyyy'))
                table.setText(i, columnNumber['clientDocument'], text)

            if showColumn['clientPolicy']:
                policy = []
                if showCompulsoryPolicy:
                    policy.append(u'%s выдан %s' % (clientCompulsoryPolicy, clientCompulsoryPolicyDate.toString('dd.MM.yyyy')))
                if showVoluntaryPolicy:
                    policy.append(u'%s выдан %s' % (clientVoluntaryPolicy, clientVoluntaryPolicyDate.toString('dd.MM.yyyy')))
                table.setText(i, columnNumber['clientPolicy'], '/'.join(policy))

            if showColumn['relegateOrDeliveredOrg']:
                org = []
                if showRelegateOrg and relegateOrg != '':
                    org.append(relegateOrg)
                if showDeliveredOrg and deliveredOrg != '':
                    org.append(deliveredOrg)
                if showOtherRelegateOrg and otherRelegateOrg != '':
                    org.append(otherRelegateOrg)
                table.setText(i, columnNumber['relegateOrDeliveredOrg'], '/'.join(org))

            table.setText(i, columnNumber['receivedOrgStructure'], receivedOrgStructure)

            if showColumn['hospitalBedProfile']:
                table.setText(i, columnNumber['hospitalBedProfile'], hospitalBedProfile)

            if showColumn['bedProfile']:
                table.setText(i, columnNumber['bedProfile'], bedProfile)

            if showColumn['cardNumber']:
                table.setText(i, columnNumber['cardNumber'], cardNumber)

            if showColumn['relegateOrgDiagnosis']:
                table.setText(i, columnNumber['relegateOrgDiagnosis'], relegateOrgDiag)

            if showColumn['receivedOrgDiagnosis']:
                table.setText(i, columnNumber['receivedOrgDiagnosis'], receivedOrgDiag)

            if showColumn['leavedInfo']:
                text = leavedResult + u'\n' + leavedDate.toString('dd.MM.yyyy') + u'\t' + leavedTo
                table.setText(i, columnNumber['leavedInfo'], text)

            if showColumn['messageToRelatives']:
                table.setText(i, columnNumber['messageToRelatives'], msgToRelatives)

            if showColumn['eventOrder']:
                table.setText(i, columnNumber['eventOrder'], eventOrder)

            if showColumn['reason']:
                table.setText(i, columnNumber['reason'], reason)

            if showColumn['takenMeasures']:
                table.setText(i, columnNumber['takenMeasures'], takenMeasures)

            if showColumn['notes']:
                table.setText(i, columnNumber['notes'], notes)

        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'b15',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportReceivedAndRefusalClients(None)
    w.exec_()


if __name__ == '__main__':
    main()
