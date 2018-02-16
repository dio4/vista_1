# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils           import getWorkEventTypeFilter
from library.Utils          import forceBool, forceRef, forceString
from library.vm_collections import OrderedDict
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportAnalyticalTable import Ui_ReportAnalyticalTable


columns = OrderedDict()
columns['ExternalId']    = u'№ истории \n болезни'
columns['LastName']      = u'Фамилия'
columns['FirstName']     = u'Имя'
columns['PatrName']      = u'Отчество'
columns['Sex']           = u'Пол'
columns['BirthDate']     = u'Дата рождения'
columns['Age']           = u'Возраст'
columns['Finance']       = u'Тип финансирования'
columns['Policy']        = u'Серия и номер полиса'
columns['MKB']           = u'Диагноз'
columns['FinishedMKB']   = u'Заключительный диагноз'
columns['MES']           = u'Стандарт'
columns['Code']          = u'Код услуги'
columns['Name']          = u'Наименование услуги'
columns['Status']        = u'Статус оплаты'
columns['ActionPerson']  = u'Исполнитель в услуге'
columns['Time']          = u'Время оказания услуги \n c момента поступления'
columns['OrderEvent']    = u'Порядок поступления'
columns['PrimaryEvent']  = u'Первично/повторно'
columns['SetDate']       = u'Дата поступления'
columns['SetTime']       = u'Время поступления'
columns['ExecDate']      = u'Дата выбытия'
columns['ExecTime']      = u'Время выбытия'
columns['Received']      = u'Время доставки \n с момента получения \n травмы/заболевания'
columns['Result']        = u'Исход'
columns['OrgStructure']  = u'Отделение, из которого выбыл'
columns['Profile']       = u'Профиль'
columns['Reanimation']   = u'Нахождение в реанимации'
columns['Person']        = u'Лечащий врач'
columns['Organization']  = u'Кем направлен'
columns['Diagnosis']     = u'Диагноз направителя'
columns['Area']          = u'Район'
columns['Inhab']         = u'Житель'
columns['Work']          = u'Занятость'

def selectData(begDate, endDate, eventTypeIds, financeIds, diagnosisType, orgStructureIds,  MKBFilter, MKBFrom, MKBTo, area, result, MESFrom, MESTo, MESFilter, birthDate):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableOrgStructure = db.table('OrgStructure')
    tableLastMovingAction = db.table('Action').alias('lastMovingAction')
    tableResult = db.table('rbResult')
    tableMES = db.table('mes.MES').alias('mes')

    additionalSelect = additionalFrom = ''
    cond = [tableEvent['execDate'].dateLe(endDate),
            tableEvent['execDate'].dateGe(begDate),
            '''Event.id IN (SELECT act.event_id
                                       FROM Action act
                                       INNER JOIN ActionType actType ON act.actionType_id = actType.id
                                       WHERE Event.id = act.event_id AND actType.flatCode = 'leaved' AND act.deleted = 0 AND actType.deleted = 0)''']
    if not eventTypeIds[0] and eventTypeIds[1]:
        cond.append(tableEvent['eventType_id'].eq(eventTypeIds[1]))
    elif eventTypeIds[0] and eventTypeIds[2]:
        cond.append(tableEvent['eventType_id'].inlist(eventTypeIds[2]))
    if not financeIds[0] and financeIds[1]:
        cond.append(tableContract['finance_id'].eq(financeIds[1]))
    elif eventTypeIds[0] and eventTypeIds[2]:
        cond.append(tableContract['finance_id'].inlist(financeIds[2]))
    if not orgStructureIds[0] and orgStructureIds[1]:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureIds[1])))
    elif orgStructureIds[0] and orgStructureIds[2]:
        cond.append(tableOrgStructure['id'].inlist(orgStructureIds[2]))
    if MKBFilter == 1:
        additionalSelect += u', Diagnosis.MKB AS FinishedMKB'
        cond.append(tableLastMovingAction['MKB'].ge(MKBFrom))
        cond.append(tableLastMovingAction['MKB'].le(MKBTo))
    if diagnosisType:
        additionalFrom += ' LEFT JOIN rbDiagnosisType ON Diagnostic.diagnosisType_id = rbDiagnosisType.id AND rbDiagnosisType.code = %s' % diagnosisType
    if result == 1:
        cond.append(tableResult['code'].inlist(['105', '106', '205', '206']))
    elif result == 2:
        cond.append(tableResult['code'].notInlist(['105', '106', '205', '206']))
    if MESFilter:
        cond.append(tableMES['code'].between(MESFrom, MESTo))
    if area:
        additionalSelect += u', if(left(AddressHouse.KLADRCode, 2) = 78, OKATO.NAME, kl.NAME) Area'
        additionalFrom += u' LEFT JOIN kladr.OKATO AS OKATO ON OKATO.CODE = left(kladr.getOKATO(AddressHouse.KLADRCode, AddressHouse.KLADRStreetCode, AddressHouse.number), 5)'
    if birthDate:
        additionalSelect +=  u', Client.birthDate AS birthDate'

    socStatusClassId = forceRef(db.translate('rbSocStatusClass', 'flatCode', u'citizenship', 'id'))
    stmt =u'''SELECT Event.id
                     , Event.externalId AS ExternalId
                     , Event.client_id AS ClientId
                     , Client.lastName AS LastName
                     , Client.firstName AS FirstName
                     , Client.patrName AS PatrName
                     , if(Client.sex = 1, 'м', 'ж') AS Sex
                     , age(Client.birthDate, Event.setDate) AS Age
                     , getClientPolicy(Client.id, 1) AS Policy
                     , Contract.number AS Finance
                     , mes.code AS MES
                     , lastMovingAction.MKB
                     , ActionType.code AS Code
                     , ActionType.name AS Name
                     , vrbActionPerson.name AS ActionPerson
                     , datediff(Action.begDate, Event.setDate) AS Time
                     , if(Event.order = 2, 'экстренно', 'планово') AS OrderEvent
                     , if(Event.isPrimary = 2, 'повторный', 'первичный') AS PrimaryEvent
                     , date(Event.setDate) AS SetDate
                     , time(Event.setDate) AS SetTime
                     , date(Event.execDate) AS ExecDate
                     , time(Event.execDate) AS ExecTime
                     , rbResult.name AS Result
                     , vrbPerson.name AS Person
                     , if(ClientWork.org_id IS NULL, ClientWork.freeInput, Organisation.shortName) AS Work
                     , max(if(ReceivedActionPropertyType.name = 'Доставлен', ActionProperty_String.value, NULL)) AS Received
                     , max(if(ReceivedActionPropertyType.name = 'Диагноз направителя', ActionProperty_String.value, NULL)) AS Diagnosis
                     , max(if(ReceivedActionPropertyType.name = 'Кем направлен', receivedOrganisation.shortName, NULL)) AS Organization
                     , if(LEFT(AddressHouse.KLADRCode,2) = 78, 'СПБ', if(LEFT(AddressHouse.KLADRCode,2) = 47, 'Лен.области', if(ClientDocument.documentType_id IN (SELECT rbDocumentType.id FROM rbDocumentType WHERE rbDocumentType.isForeigner = 1) AND getClientPolicyId(Client.id, 1) IS NULL, rbSocStatusType.name, 'иногородний'))) Inhab
                     , OrgStructure.code AS OrgStructure
                     , if(ReanimationOrgStructure.id IS NOT NULL, 'да', 'нет') AS Reanimation
                     , rbHospitalBedProfile.name AS Profile
                     , IF(Account_Item.date AND Account_Item.refuseType_id IS NULL, 'оплачено',
                       IF(Account_Item.date AND Account_Item.refuseType_id, 'отказано',
                       IF(Account_Item.id, 'выставлено', ''))) AS Status
                     %s
                FROM
                    Event
                    INNER JOIN Client ON Client.id = Event.client_id
                    LEFT JOIN Contract ON Contract.id = Event.contract_id
                    LEFT JOIN ActionType MovingActionType ON MovingActionType.flatCode = 'moving' AND MovingActionType.deleted = 0
                    LEFT JOIN Action lastMovingAction ON lastMovingAction.event_id = Event.id AND lastMovingAction.id = (SELECT max(act.id)
                                                                                                                        FROM    Action act
                                                                                                                        WHERE   act.event_id = Event.id AND act.actionType_id = MovingActionType.id AND act.deleted = 0)
                    LEFT JOIN ActionPropertyType MovingActionPropertyType ON MovingActionPropertyType.actionType_id = MovingActionType.id AND MovingActionPropertyType.name = 'Отделение пребывания'
                    LEFT JOIN ActionPropertyType MovingActionPropertyTypeProfile ON MovingActionPropertyTypeProfile.actionType_id = MovingActionType.id AND MovingActionPropertyTypeProfile.name = 'Профиль'
                    LEFT JOIN ActionProperty MovingActionProperty ON MovingActionProperty.action_id = lastMovingAction.id AND MovingActionProperty.type_id = MovingActionPropertyType.id AND MovingActionProperty.deleted = 0
                    LEFT JOIN ActionProperty MovingActionPropertyProfile ON MovingActionPropertyProfile.action_id = lastMovingAction.id AND MovingActionPropertyProfile.type_id = MovingActionPropertyTypeProfile.id AND MovingActionPropertyProfile.deleted = 0
                    LEFT JOIN ActionProperty_rbHospitalBedProfile ON ActionProperty_rbHospitalBedProfile.id = MovingActionPropertyProfile.id
                    LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = ActionProperty_rbHospitalBedProfile.value
                    LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = MovingActionProperty.id
                    LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                    LEFT JOIN OrgStructure ReanimationOrgStructure ON ReanimationOrgStructure.id IN (SELECT ap_OrgStructure.value
                                                                                                     FROM ActionPropertyType apt
                                                                                                     INNER JOIN ActionProperty ap ON ap.type_id = apt.id AND ap.deleted = 0
                                                                                                     INNER JOIN Action act ON act.id = ap.action_id AND act.deleted = 0
                                                                                                     INNER JOIN ActionProperty_OrgStructure ap_OrgStructure ON ap_OrgStructure.id = ap.id
                                                                                                     WHERE apt.actionType_id = MovingActionType.id AND apt.name = 'Переведен в отделение' AND act.event_id = Event.id) AND (ReanimationOrgStructure.code = 'Реанимация' OR ReanimationOrgStructure.parent_id IN (SELECT org.id FROM OrgStructure org WHERE org.code = 'Реанимация'))
                    LEFT JOIN rbResult ON rbResult.id = Event.result_id
                    LEFT JOIN mes.MES mes ON mes.id = lastMovingAction.MES_id
                    LEFT JOIN vrbPerson ON vrbPerson.id = lastMovingAction.setPerson_id
                    LEFT JOIN ClientWork ON ClientWork.client_id = Client.id AND ClientWork.id = (SELECT max(clWork.id)
                                                                                                  FROM ClientWork clWork
                                                                                                     WHERE clWork.deleted = 0 AND clWork.client_id = Client.id)
                    LEFT JOIN Organisation ON Organisation.id = ClientWork.org_id
                    LEFT JOIN ActionType ReceivedActionType ON ReceivedActionType.flatCode = 'received'
                    LEFT JOIN Action ReceivedAction ON ReceivedAction.event_id = Event.id AND ReceivedAction.deleted = 0 AND ReceivedAction.actionType_id = ReceivedActionType.id AND ReceivedAction.deleted = 0
                    LEFT JOIN ActionPropertyType ReceivedActionPropertyType ON ReceivedActionPropertyType.actionType_id = ReceivedActionType.id AND ReceivedActionPropertyType.name IN ('Доставлен', 'Кем направлен', 'Диагноз направителя')
                    LEFT JOIN ActionProperty ReceivedActionProperty ON ReceivedActionProperty.action_id = ReceivedAction.id AND ReceivedActionProperty.type_id = ReceivedActionPropertyType.id
                    LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ReceivedActionProperty.id
                    LEFT JOIN ActionProperty_Organisation ON ActionProperty_Organisation.id = ReceivedActionProperty.id
                    LEFT JOIN Organisation receivedOrganisation ON receivedOrganisation.id = ActionProperty_Organisation.value
                    LEFT JOIN Action ON Action.event_id = Event.id AND Action.deleted = 0 AND (SELECT SubActionType.id FROM ActionType SubActionType WHERE SubActionType.id = Action.actionType_id AND SubActionType.flatCode NOT IN ('received', 'moving', 'planning', 'leaved') AND SubActionType.deleted = 0) IS NOT NULL
                    LEFT JOIN vrbPerson vrbActionPerson ON vrbActionPerson.id = Action.person_id
                    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id AND ActionType.deleted = 0
                    LEFT JOIN ClientAddress ON ClientAddress.deleted = 0 AND ClientAddress.id = getClientRegAddressId(Event.client_id)
                    LEFT JOIN Address ON Address.deleted = 0 AND Address.id = ClientAddress.address_id
                    LEFT JOIN AddressHouse ON AddressHouse.deleted = 0 AND AddressHouse.id = Address.house_id
                    LEFT JOIN kladr.KLADR kl ON kl.CODE = AddressHouse.KLADRCode
                    LEFT JOIN ClientDocument ON ClientDocument.id = getClientDocumentID(Client.id)
                    LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
                    LEFT JOIN ClientSocStatus ON ClientSocStatus.client_id = Client.id AND ClientSocStatus.socStatusClass_id = %s AND ClientSocStatus.deleted = 0
                    LEFT JOIN rbSocStatusType ON rbSocStatusType.id = ClientSocStatus.socStatusType_id
                    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                    LEFT JOIN ActionType_Service ON ActionType_Service.master_id = Action.actionType_id
                    LEFT JOIN Account_Item ON Account_Item.action_id = Action.id AND Account_Item.deleted = 0
                    %s
                WHERE
                    %s AND (ActionType.id IS NULL OR ActionType.nomenclativeService_id IS NOT NULL OR EXISTS(SELECT ActionType_Service.id
                                                                              FROM ActionType_Service
                                                                              WHERE ActionType_Service.master_id = ActionType.id)) AND Event.deleted = 0
                GROUP BY
                    Event.id
                    , ActionType.code
                ORDER BY
                    Event.externalId''' % (additionalSelect, socStatusClassId,
                                           additionalFrom, db.joinAnd(cond))
    return db.query(stmt)

class CReportAnalyticTable(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Аналитическая таблица')


    def getSetupDialog(self, parent):
        result = CAnalyticalTable(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        eventTypeIds = (params.get('chkEventType'), params.get('eventTypeId'), params.get('eventTypeIdMulti'))
        orgStructureIds = (params.get('chkOrgStructure'), params.get('orgStructureId'), params.get('orgStructureIdMulti'))
        financeIds = (params.get('chkFinance'), params.get('financeId'), params.get('financeIdMulti'))
        diagnosisType = params.get('diagnosisType')
        MKBFilter = params.get('MKBFilter')
        MKBFrom = params.get('MKBFrom')
        MKBTo = params.get('MKBTo')
        area = params.get('area')
        result = params.get('result')
        outputColumns = params.get('outputColumns')
        MESFrom = params.get('MESFrom')
        MESTo = params.get('MESTo')
        MESFilter = params.get('MESFilter', 0)
        birthDate = params.get('chkBirthDate', False)

        query = selectData(begDate, endDate, eventTypeIds, financeIds, diagnosisType,
                           orgStructureIds,  MKBFilter, MKBFrom, MKBTo, area, result, MESFrom, MESTo, MESFilter, birthDate)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [('2%', [u'№'], CReportBase.AlignLeft)]
        queryFeild = []
        for key in outputColumns.keys():
            if outputColumns[key]:
                tableColumns.append(('3%', [columns[key]], CReportBase.AlignLeft))
                queryFeild.append(key)
        table = createTable(cursor, tableColumns)
        self.setQueryText(forceString(query.lastQuery()))
        currentEvent = None
        count = 1
        i = 0
        rowNumber = 0
        client_ids = []
        external_ids = []
        if len(queryFeild):
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('id'))
                i = table.addRow()
                if currentEvent != eventId:
                    rowNumber += 1
                    table.setText(i, 0, rowNumber)
                    for index, feild in enumerate(queryFeild):
                        if feild not in ('Code', 'Name', 'Status', 'ActionPerson', 'Time'):
                            table.mergeCells(i - count, 0, count, 1)
                            table.mergeCells(i - count, index + 1, count, 1)
                        table.setText(i, index + 1, forceString(record.value(feild)))
                    count = 1
                    currentEvent = eventId
                else:
                    count += 1
                    for index, feild in enumerate(queryFeild):
                        if feild in ('Code', 'Name', 'Status', 'ActionPerson', 'Time'):
                            table.setText(i, index + 1, forceString(record.value(feild)))
                if record.value('ExternalId') not in external_ids:
                    external_ids.append(record.value('ExternalId'))
                if record.value('ClientId') not in client_ids:
                    client_ids.append(record.value('ClientId'))
            if count and i:
                table.mergeCells(i - count + 1, 0, count, 1)
                for index, feild in enumerate(queryFeild):
                    if feild not in ('Code', 'Name', 'Status', 'ActionPerson', 'Time'):
                        table.mergeCells(i - count + 1, index + 1, count, 1)
            i = 1
            table.table.insertRows(i, 1)
            table.setText(i, 0, u'ИТОГО', CReportBase.TableTotal)
            count_merging = 0
            for index, feild in enumerate(queryFeild):
                if feild == 'LastName':
                    table.setText(i, index+1, len(client_ids), CReportBase.TableTotal)
                    count_merging += 1
                elif feild == 'ExternalId':
                    table.setText(i, index+1, len(external_ids), CReportBase.TableTotal)
                    count_merging += 1
            table.mergeCells(i, count_merging + 1, 1, len(tableColumns) - count_merging)
        return doc


class CAnalyticalTable(QtGui.QDialog, Ui_ReportAnalyticalTable):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter = getWorkEventTypeFilter())
        self.cmbFinance.setTable('rbFinance', True)
        self.cmbDiagnosisType.setTable('rbDiagnosisType', True)
        self.cmbFinance.setCurrentIndex(0)
        self.cmbDiagnosisType.setCurrentIndex(0)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.lstEventType.setTable('EventType', filter = getWorkEventTypeFilter())
        self.lstEventType.setVisible(False)
        self.lstOrgStructure.setTable('OrgStructure')
        self.lstOrgStructure.setVisible(False)
        self.lstFinance.setTable('rbFinance')
        self.lstFinance.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbDiagnosisType.setValue(params.get('diagnosisType', None))
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        MESFilter = params.get('MESFilter', 0)
        self.cmbMES.setCurrentIndex(MESFilter)
        self.edtMESFrom.setText(params.get('MESFrom', ''))
        self.edtMESTo.setText(params.get('MESTo', ''))
        self.cmbResult.setCurrentIndex(params.get('result', 0))
        arg = params.get('outputColumns', False)
        if type(arg) == QtCore.QVariant:
            arg = arg.toPyObject()
        if set(columns.keys()) == set(arg.keys()):
            for key in columns.keys():
                try:
                    self.callObjectAtributeMethod('chk%s' % key, 'setChecked', forceBool(arg[key.lower()]) if arg else True)
                except KeyError:
                    self.callObjectAtributeMethod('chk%s' % key, 'setChecked', forceBool(arg[key]) if arg else True)

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['eventTypeId'] = self.cmbEventType.value()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['financeId'] = self.cmbFinance.value()
        params['diagnosisType'] = self.cmbDiagnosisType.value()
        params['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        params['MKBFrom']   = forceString(self.edtMKBFrom.text())
        params['MKBTo']     = forceString(self.edtMKBTo.text())
        params['area']      =   self.chkArea.isChecked()
        params['result'] = self.cmbResult.currentIndex()
        params['outputColumns'] = OrderedDict()
        for key in columns.keys():
            params['outputColumns'][key] = self.callObjectAtributeMethod('chk%s' % key, 'isChecked')
        params['eventTypeIdMulti'] = self.lstEventType.nameValues()
        params['chkEventType'] = self.chkEventTypeMulti.isChecked()
        params['orgStructureIdMulti'] = self.lstOrgStructure.nameValues()
        params['chkOrgStructure'] = self.chkOrgStructureMulti.isChecked()
        params['financeIdMulti'] = self.lstOrgStructure.nameValues()
        params['chkFinance'] = self.chkOrgStructureMulti.isChecked()
        params['chkBirthDate'] = self.chkBirthDate.isChecked()
        params['MESFilter'] = self.cmbMES.currentIndex()
        params['MESFrom'] = forceString(self.edtMESFrom.text())
        params['MESTo'] = forceString(self.edtMESTo.text())
        return params

    def callObjectAtributeMethod(self, objectName, nameMethod, *args):
        return self.__getattribute__(objectName).__getattribute__(nameMethod)(*args)

    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)

    @QtCore.pyqtSlot(int)
    def on_cmbMES_currentIndexChanged(self, index):
        self.edtMESFrom.setEnabled(index == 1)
        self.edtMESTo.setEnabled(index == 1)

    @QtCore.pyqtSlot(bool)
    def on_chkEventTypeMulti_clicked(self, checked):
        self.lstEventType.setVisible(checked)
        self.cmbEventType.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureMulti_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFinanceMulti_clicked(self, checked):
        self.lstFinance.setVisible(checked)
        self.cmbFinance.setVisible(not checked)