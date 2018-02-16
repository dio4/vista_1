# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceInt, forceRef, forceString, getVal, forceBool
from Orgs.Utils         import getOrgStructureDescendants
from library.vm_collections import OrderedDict

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportListLeavedClient import Ui_ReportListLeavedClient

columns = OrderedDict()
columns['Num']         = ( '2%', [u'№'],                           CReportBase.AlignLeft)
columns['FIO']         = ('15%', [u'ФИО'],                          CReportBase.AlignLeft)
columns['ExternalId']  = ('10%', [u'№ истории болезни'],           CReportBase.AlignLeft)
columns['Address']     = ('15%', [u'Адрес'],                        CReportBase.AlignLeft)
columns['OrgReceived'] = ('10%', [u'Кем направлен'],                CReportBase.AlignLeft)
columns['OrderEvent']  = ('10%', [u'Порядок оказания помощи'],      CReportBase.AlignLeft)
columns['Diagnosis']   = ('10%', [u'Диагноз'],                      CReportBase.AlignLeft)
columns['SetDate']     = ( '5%', [u'Дата поступления'],             CReportBase.AlignLeft)
columns['MovingDate']  = ( '5%', [u'Дата поступления в отделение'], CReportBase.AlignLeft)
columns['LeavedDate']  = ( '5%', [u'Дата выписки'],                 CReportBase.AlignLeft)
columns['Profile']     = ( '5%', [u'Профиль'],                      CReportBase.AlignLeft)
columns['Operation']   = ('10%', [u'Код операции'],                 CReportBase.AlignLeft)
columns['Days']        = ( '5%', [u'Общее количество койкодней'],   CReportBase.AlignLeft)
columns['Result']      = ('10%', [u'Исход'],                        CReportBase.AlignLeft)


def selectData(begDate, endDate, chkEventType, eventTypeId, lstEventType, chkOrgStructure, orgStructureId, lstOrgStructure, typeRegistry, typeHospitalisation):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableDocumentType = db.table('rbDocumentType')
    tableOpAction = db.table('Action').alias('opAction1')
    tableOrgStructure = db.table('OrgStructure')

    opActionTypeIdList = db.getIdList('ActionType', where=u'code LIKE \'6%\' OR code LIKE \'о%\'')
    opActionCond = tableOpAction['actionType_id'].inlist(opActionTypeIdList) if opActionTypeIdList else '0'

    cond = [tableEvent['execDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate)]

    if typeHospitalisation == 1:
        cond.append(tableOrgStructure['hasDayStationary'].eq(1))
    elif typeHospitalisation == 2:
        cond.append('receivedReason.id IS NOT NULL')
    elif typeHospitalisation == 3:
        cond.extend([tableOrgStructure['hasDayStationary'].eq(0),
                     'receivedReason.id IS NULL'])

    if lstEventType and chkEventType:
        cond.append(tableEvent['eventType_id'].inlist(lstEventType))
    elif eventTypeId and not chkEventType:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if lstOrgStructure and chkOrgStructure:
        cond.append(tableOrgStructure['id'].inlist(lstOrgStructure))
    elif orgStructureId and not chkOrgStructure:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if typeRegistry == 3:
        cond.append('LEFT(AddressHouse.KLADRCode,2) = 78')
    elif typeRegistry == 4:
        cond.append('LEFT(AddressHouse.KLADRCode,2) = 47')
    elif typeRegistry == 5:
        cond.append('if(AddressHouse.KLADRCode IS NOT NULL, LEFT(AddressHouse.KLADRCode,2) not in (78, 47), %s)' % tableDocumentType['isForeigner'].eq(0))
    elif typeRegistry:
        cond.append(tableDocumentType['isForeigner'].eq(1))
        if typeRegistry == 2:
            cond.append('AddressHouse.KLADRCode IS NOT NULL')
        elif typeRegistry == 1:
            cond.append('AddressHouse.KLADRCode IS NULL')
    diagnosisTypeId = forceRef(db.translate('rbDiagnosisType', 'code', u'1', 'id'))
    socStatusClassId = forceRef(db.translate('rbSocStatusClass', 'flatCode', u'citizenship', 'id'))

    stmt = u'''SELECT Client.lastName
                     , Client.firstName
                     , Client.patrName
                     , Event.externalId
                     , if(rbDocumentType.isForeigner AND getClientPolicyId(Client.id, 1) IS NULL, rbSocStatusType.name, getClientRegAddress(Client.id)) AS address
                     , orgReceived.value AS orgReceived
                     , concat(if(Event.order = 1, 'плановый', if(Event.order = 2, 'экстренный', NULL))) AS orderEvent
                     , Diagnosis.MKB
                     , Event.setDate
                     , MovingAction.begDate AS movingDate
                     , LeavedAction.begDate AS leavedDate
                     , if(datediff(Event.execDate, Event.setDate) = 0, 1, datediff(Event.execDate, Event.setDate)) AS days
                     , OrgStructure.name AS orgStructure
                     , rbResult.name AS result
                     , opActionType.code AS operation
                     , rbHospitalBedProfile.name AS profile
            FROM
              Client
                INNER JOIN Event
                ON Client.id = Event.client_id AND Event.deleted = 0
                INNER JOIN Diagnostic
                ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0 AND Diagnostic.diagnosisType_id = %s
                INNER JOIN Diagnosis
                ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0

                INNER JOIN ActionType ReceivedActionType
                ON ReceivedActionType.deleted = 0 AND ReceivedActionType.flatCode = 'received'
                LEFT JOIN ActionType MovingActionType
                ON MovingActionType.deleted = 0 AND MovingActionType.flatCode = 'moving'
                LEFT JOIN ActionType LeavedActionType
                ON LeavedActionType.deleted = 0 AND LeavedActionType.flatCode = 'leaved'
                LEFT JOIN ActionPropertyType ReceivedActionPropertyType ON ReceivedActionPropertyType.actionType_id = ReceivedActionType.id AND (ReceivedActionPropertyType.name LIKE 'Прочие направители%%')
                LEFT JOIN ActionPropertyType ReceivedActionPropertyTypeReason ON ReceivedActionPropertyTypeReason.actionType_id = ReceivedActionType.id AND ReceivedActionPropertyTypeReason.name LIKE 'Причина отказа от госпитализации%%'
                LEFT JOIN ActionPropertyType MovingActionPropertyType
                ON MovingActionPropertyType.actionType_id = MovingActionType.id AND MovingActionPropertyType.name LIKE 'Отделение пребывания%%'
                LEFT JOIN ActionPropertyType MovingActionPropertyTypeProfile ON MovingActionPropertyTypeProfile.actionType_id = MovingActionType.id AND MovingActionPropertyTypeProfile.name LIKE 'Профиль%%'

                INNER JOIN Action ReceivedAction ON ReceivedAction.event_id = Event.id AND ReceivedActionType.id = ReceivedAction.actionType_id  AND ReceivedAction.deleted = 0
                LEFT JOIN ActionProperty ReceivedActionProperty ON ReceivedActionProperty.action_id = ReceivedAction.id AND ReceivedActionProperty.type_id = ReceivedActionPropertyType.id AND ReceivedActionProperty.deleted = 0
                LEFT JOIN ActionProperty_String orgReceived ON orgReceived.id = ReceivedActionProperty.id

                LEFT JOIN ActionProperty ReceivedActionPropertyReason ON ReceivedActionPropertyReason.action_id = ReceivedAction.id AND ReceivedActionPropertyReason.type_id = ReceivedActionPropertyType.id AND ReceivedActionPropertyReason.deleted = 0
                LEFT JOIN ActionProperty_String receivedReason ON receivedReason.id = ReceivedActionPropertyReason.id

                LEFT JOIN Action LeavedAction ON LeavedAction.event_id = ReceivedAction.event_id AND LeavedAction.actionType_id = LeavedActionType.id AND LeavedAction.deleted = 0

                LEFT JOIN Action MovingAction ON MovingAction.event_id = Event.id AND MovingAction.id = (SELECT max(act.id)
                                                                                                         FROM Action act
                                                                                                         WHERE act.event_id = Event.id AND act.actionType_id = MovingActionType.id AND act.deleted = 0)
                LEFT JOIN ActionProperty MovingActionProperty ON MovingActionProperty.action_id = MovingAction.id AND MovingActionProperty.type_id = MovingActionPropertyType.id
                LEFT JOIN ActionProperty_OrgStructure orgMoving ON orgMoving.id = MovingActionProperty.id
                LEFT JOIN OrgStructure ON OrgStructure.id = orgMoving.value

                LEFT JOIN ActionProperty MovingActionPropertyProfile ON MovingActionPropertyProfile.action_id = MovingAction.id AND MovingActionPropertyProfile.type_id = MovingActionPropertyTypeProfile.id AND MovingActionPropertyProfile.deleted = 0
                LEFT JOIN ActionProperty_rbHospitalBedProfile ON ActionProperty_rbHospitalBedProfile.id = MovingActionPropertyProfile.id
                LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = ActionProperty_rbHospitalBedProfile.value

                LEFT JOIN ClientAddress ON ClientAddress.id = getClientRegAddressId(Event.client_id) AND ClientAddress.deleted = 0
                LEFT JOIN Address ON Address.id = ClientAddress.address_id AND Address.deleted = 0
                LEFT JOIN AddressHouse ON AddressHouse.deleted = 0 AND AddressHouse.id = Address.house_id

                LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentID(Client.id)
                LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
                LEFT JOIN ClientSocStatus ON ClientSocStatus.client_id = Client.id AND ClientSocStatus.socStatusClass_id = %s AND ClientSocStatus.deleted = 0
                LEFT JOIN rbSocStatusType ON rbSocStatusType.id = ClientSocStatus.socStatusType_id
                LEFT JOIN rbResult ON rbResult.id = Event.result_id
                LEFT JOIN Action opAction ON opAction.id = (SELECT MAX(id) FROM Action opAction1 WHERE opAction1.deleted = 0
                        AND opAction1.event_id = Event.id
                        AND %s)
                LEFT JOIN ActionType opActionType ON opActionType.id = opAction.actionType_id
            WHERE
              %s AND Event.deleted = 0
            ORDER BY
             OrgStructure.name, Client.lastName, Client.firstName, Client.patrName''' % (diagnosisTypeId, socStatusClassId, opActionCond, db.joinAnd(cond))
    return db.query(stmt)

class CReportListLeavedClient(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Список больных, выбывших из отделений')


    def getSetupDialog(self, parent):
        result = CListLeavedClient(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        chkEventType = params.get('chkEventType', False)
        eventTypeId = params.get('eventTypeId')
        lstEventTypeDict = params.get('lstEventType', None)
        lstEventType = lstEventTypeDict.keys()
        chkOrgStructure = params.get('cmbOrgStructure', False)
        orgStructureId = params.get('orgStructureId')
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        typeRegisty = params.get('typeRegistry')
        typeHospitalization = params.get('typeHospitalization')
        columnsFilter = params.get('columnsFilter')
        query = selectData(begDate, endDate, chkEventType, eventTypeId, lstEventType, chkOrgStructure, orgStructureId, lstOrgStructure, typeRegisty, typeHospitalization)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        filteredColumns = [col for col, mask in zip(columns.values(), columnsFilter.values()) if mask]
        colCount = len(filteredColumns)
        table = createTable(cursor, filteredColumns)
        total = [0]*2
        orgTotal = [0]*2
        prevOrgStructure = None
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            orgStructure  = forceString(record.value('orgStructure'))
            if not orgStructure:
                orgStructure = '-'
            if prevOrgStructure and orgStructure != prevOrgStructure and columnsFilter['Days']:
                i = table.addRow()
                table.mergeCells(i, 0, 1, (colCount - 2 if columnsFilter['Result'] else colCount - 1))
                table.setText(i, 0, u'всего по ' + prevOrgStructure, CReportBase.TableTotal)
                table.setText(i, (colCount - 2 if columnsFilter['Result'] else colCount - 1), forceString(orgTotal[0]) + u'/' + forceString(orgTotal[1]), CReportBase.TableTotal)
                for index in xrange(2):
                    total[index] += orgTotal[index]
                orgTotal = [0]*2
            if  orgStructure != prevOrgStructure:
                i = table.addRow()
                table.mergeCells(i, 0, 1, colCount)
                i = table.addRow()
                table.setText(i, 0, orgStructure, CReportBase.TableTotal)
                table.mergeCells(i, 0, 1, colCount)
                prevOrgStructure = orgStructure
            i = table.addRow()
            days = forceInt(record.value('days'))
            orgTotal[0] += 1
            orgTotal[1] += days
            MKB = forceString(record.value('MKB'))
            recordFieldsVal = (
                orgTotal[0],
                forceString(record.value('lastName')) + ' ' + forceString(record.value('firstName')) + ' ' + forceString(record.value('patrName')),
                forceString(record.value('externalId')),
                forceString(record.value('address')),
                forceString(record.value('orgReceived')),
                forceString(record.value('orderEvent')),
                forceString(MKB + ' ' + forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', MKB, 'DiagName'))),
                forceString(record.value('setDate')),
                forceString(record.value('movingDate')),
                forceString(record.value('leavedDate')),
                forceString(record.value('profile')),
                forceString(record.value('operation')),
                days,
                forceString(record.value('result'))
            )
            filteredRecordFieldsVal = [val for val, mask in zip(recordFieldsVal, columnsFilter.values()) if mask]
            for col, colVal in enumerate(filteredRecordFieldsVal):
                table.setText(i, col, colVal)
        if orgTotal[0] and columnsFilter['Days']:
            i = table.addRow()
            table.mergeCells(i, 0, 1, (colCount - 2 if columnsFilter['Result'] else colCount - 1))
            table.setText(i, 0, u'всего по ' + orgStructure, CReportBase.TableTotal)
            table.setText(i, (colCount - 2 if columnsFilter['Result'] else colCount - 1), forceString(orgTotal[0]) + u'/' + forceString(orgTotal[1]), CReportBase.TableTotal)
            for index in xrange(2):
                total[index] += orgTotal[index]
        if columnsFilter['Days']:
            i = table.addRow()
            table.mergeCells(i, 0, 1, (colCount - 2 if columnsFilter['Result'] else colCount - 1))
            table.setText(i, 0, u'ИТОГОВОЕ ИТОГО по отделениям:', CReportBase.TableTotal)
            table.setText(i, (colCount - 2 if columnsFilter['Result'] else colCount - 1), forceString(total[0]) + u'/' + forceString(total[1]), CReportBase.TableTotal)
        return doc


class CListLeavedClient(QtGui.QDialog, Ui_ReportListLeavedClient):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.lstEventType.setTable('EventType')
        self.lstOrgStructure.setTable('OrgStructure')
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())
        self.on_chkEventType_clicked(self.chkEventType.isChecked())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbTypeRegistry.setCurrentIndex(getVal(params, 'typeRegistry', 0))
        self.cmbHospitalization.setCurrentIndex(getVal(params, 'typeHospitalization', 0))
        arg = params.get('columnsFilter', False)
        if type(arg) == QtCore.QVariant:
            arg = arg.toPyObject()
        if not arg or set(columns.keys()) == set(arg.keys()):
            for key in columns.keys():
                try:
                    self.callObjectAtributeMethod('chk%s' % key, 'setChecked', forceBool(arg[key]) if arg else True)
                except AttributeError:
                    pass

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['chkEventType'] = self.chkEventType.isChecked()
        params['eventTypeId'] = self.cmbEventType.value()
        params['lstEventType'] = self.lstEventType.nameValues()
        params['cmbOrgStructure'] = self.chkOrgStructure.isChecked()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        params['typeRegistry']  = self.cmbTypeRegistry.currentIndex()
        params['typeHospitalization'] = self.cmbHospitalization.currentIndex()
        params['columnsFilter'] = OrderedDict()
        for key in columns.keys():
            try:
                params['columnsFilter'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
            except AttributeError:
                params['columnsFilter'][key] = True
        return params

    def callObjectAtributeMethod(self, objectName, nameMethod, *args):
        return self.__getattribute__(objectName).__getattribute__(nameMethod)(*args)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkEventType_clicked(self, checked):
        self.lstEventType.setVisible(checked)
        self.cmbEventType.setVisible(not checked)


