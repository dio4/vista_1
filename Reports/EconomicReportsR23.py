# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

from PyQt4 import QtCore, QtGui
from collections import defaultdict

from Accounting.Utils import getContractInfo, isTariffApplicable, CTariff
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CFinanceType, getExposed, getPayed, getRefused, getPayStatusMask, getEventServiceId, \
    getEventLengthDays
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo
from Registry.Utils import getClientInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_EconomicAnalisysSetup import Ui_EconomicAnalisysSetupDialog
from library.Utils import forceBool, forceDate, forceRef, forceInt, forceString, forceStringEx, \
    formatDate, getPref, getPrefDate, getPrefInt, getPrefRef, getPrefString, firstMonthDay, \
    forceDecimal
from library.database import decorateString


#TODO: craz: обрабатывать галочку "нулевые тарифы"

class CEconomicReportsSetup(QtGui.QDialog, Ui_EconomicAnalisysSetupDialog):

    def __init__(self, parent, report):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._report = report
        self.periodTypeList = [QtCore.QString(u'Дата окончания лечения'),
                               QtCore.QString(u'Дата формирования счет-фактуры')]
        self.cmbPeriodType.addItems(self.periodTypeList)
        self.payStatusList = [QtCore.QString(u'Нет выставления, оплаты и отказа'),
                              QtCore.QString(u'Выставлено, нет оплаты и отказа'),
                              QtCore.QString(u'Отказано'),
                              QtCore.QString(u'Оплачено'),
                              QtCore.QString(u'Выставлено, оплачено, отказано')]
        self.cmbPayStatus.addItems(self.payStatusList)
        self.cmbPerson.setAddNone(False)
        self.ageList = [QtCore.QString(u'Дети'), QtCore.QString(u'Взрослые'), QtCore.QString(u'Старше трудоспособного возраста')]
        self.cmbAge.addItems(self.ageList)
        self.cmbEventType.setTable('EventType', addNone=False)
        self.cmbFinance.setTable('rbFinance', addNone=False)
        self.cmbSocStatusType.setTable('vrbSocStatusType', addNone=False)
        self.cmbTariff.setVisible(False)
        self.lblTariff.setVisible(False)
        self.tariffList = [(QtCore.QString(u'Основной тариф'), 'sum'),
                           (QtCore.QString(u'Базовый тариф'), 'tariffB'),
                           (QtCore.QString(u'Тариф на дополнительные расходы'), 'tariffD'),
                           (QtCore.QString(u'Текущие расходы'), 'tariffDValue1'),
                           (QtCore.QString(u'Расходы на коммунальные услуги'), 'tariffDValue2'),
                           (QtCore.QString(u'Расходы на налоги, аренду'), 'tariffDValue3'),
                           (QtCore.QString(u'Расходы на оборудование до 100 тысяч'), 'tariffDValue4'),
                           (QtCore.QString(u'Стимулирующие выплаты мед. персоналу участковой службы'), 'tariffUC'),
                           (QtCore.QString(u'Тариф по выполнению СОМП и повышению доступности АПМП'), 'tariffDM')]
        for tariffName, tariffKey in self.tariffList:
            self.cmbTariff.addItem(tariffName)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.cmbForm.setCurrentIndex(params.get('formIndex', 0))
        self.cmbTariff.setCurrentIndex(params.get('tariffIndex', 0))
        self.cmbTariff.setEnabled(self.cmbForm.currentIndex())
        self.cmbPeriodType.setCurrentIndex(self.periodTypeList.index(params.get('periodType', self.periodTypeList[0])))
        if self.cmbPeriodType.currentText() == self.periodTypeList[0]:
            self.edtBegin.setDate(firstMonthDay(QtCore.QDate.currentDate()))
            self.edtEnd.setDate(QtCore.QDate.currentDate())
        else:
            self.edtBegin.setDate(params.get('begDate', firstMonthDay(QtCore.QDate.currentDate())))
            self.edtEnd.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.chkOrgStructure.setCheckState(params.get('orgStructureCheckState', QtCore.Qt.Unchecked))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkPayStatus.setCheckState(params.get('payStatusCheckState', QtCore.Qt.Unchecked))
        self.cmbPayStatus.setCurrentIndex(self.payStatusList.index(params.get('payStatus', self.payStatusList[0])))
        self.chkPerson.setCheckState(params.get('personCheckState', QtCore.Qt.Unchecked))
        self.cmbPerson.setValue(params.get('personId', None))
        if not self.cmbPerson.value():
            self.cmbPerson.setCurrentIndex(0)
        self.chkInsurer.setCheckState(params.get('insurerCheckState', QtCore.Qt.Unchecked))
        self.cmbInsurer.setValue(params.get('insurerId', None))
        if not self.cmbInsurer.value():
            self.cmbInsurer.setCurrentIndex(0)
        self.chkAge.setCheckState(params.get('ageCheckState', QtCore.Qt.Unchecked))
        self.cmbAge.setCurrentIndex(self.ageList.index(params.get('age', self.ageList[0])))
        self.chkEventType.setCheckState(params.get('eventTypeCheckState', QtCore.Qt.Unchecked))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        if not self.cmbEventType.value():
            self.cmbEventType.setCurrentIndex(0)
        self.chkSocStatusType.setCheckState(params.get('socStatusCheckState', QtCore.Qt.Unchecked))
        self.cmbSocStatusType.setValue(params.get('socStatusId', None))
        if not self.cmbSocStatusType.value():
            self.cmbSocStatusType.setCurrentIndex(0)
        self.chkFinance.setCheckState(params.get('financeCheckState', QtCore.Qt.Unchecked))
        self.cmbFinance.setValue(params.get('financeId', None))
        if not self.cmbFinance.value():
            self.cmbFinance.setCurrentIndex(0)
        self.chkHideEmpty.setCheckState(params.get('hideEmptyCheckState', QtCore.Qt.Unchecked))

    def params(self):
        params = {'formIndex': self.cmbForm.currentIndex(),
                  'tariffIndex': self.cmbTariff.currentIndex(),
                  'periodType': self.cmbPeriodType.currentText(),
                  'begDate': self.edtBegin.date(),
                  'endDate': self.edtEnd.date(),
                  'orgStructureCheckState': self.chkOrgStructure.checkState(),
                  'orgStructureId': self.cmbOrgStructure.value(),
                  'payStatusCheckState': self.chkPayStatus.checkState(),
                  'payStatus': self.cmbPayStatus.currentText(),
                  'personCheckState': self.chkPerson.checkState(),
                  'personId': self.cmbPerson.value(),
                  'insurerCheckState': self.chkInsurer.checkState(),
                  'insurerId': self.cmbInsurer.value(),
                  'ageCheckState': self.chkAge.checkState(),
                  'age': self.cmbAge.currentText(),
                  'eventTypeCheckState': self.chkEventType.checkState(),
                  'eventTypeId': self.cmbEventType.value(),
                  'socStatusCheckState': self.chkSocStatusType.checkState(),
                  'socStatusId': self.cmbSocStatusType.value(),
                  'financeCheckState': self.chkFinance.checkState(),
                  'financeId': self.cmbFinance.value(),
                  'hideEmptyCheckState': self.chkHideEmpty.checkState()}
        return params

    @QtCore.pyqtSignature("int")
    def on_cmbForm_currentIndexChanged(self, index):
        self.cmbTariff.setEnabled(index)

    @QtCore.pyqtSignature("int")
    def on_chkOrgStructure_stateChanged(self, state):
        self.cmbOrgStructure.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkPayStatus_stateChanged(self, state):
        self.cmbPayStatus.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkPerson_stateChanged(self, state):
        self.cmbPerson.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkInsurer_stateChanged(self, state):
        self.cmbInsurer.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkAge_stateChanged(self, state):
        self.cmbAge.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkEventType_stateChanged(self, state):
        self.cmbEventType.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkSocStatusType_stateChanged(self, state):
        self.cmbSocStatusType.setEnabled(state == QtCore.Qt.Checked)

    @QtCore.pyqtSignature("int")
    def on_chkFinance_stateChanged(self, state):
        self.cmbFinance.setEnabled(state == QtCore.Qt.Checked)


class CEconomicReports(CReport):

    # GLOBAL_PREFERENCE_ADULT_AGE_CODE = '22'
    # GLOBAL_PREFERENCE_PENSION_MALE_AGE_CODE = '23'
    # GLOBAL_PREFERENCE_PENSION_FEMALE_AGE_CODE = '24'

    _COLS_COUNT = 9
    (_COL_EVENTS,
     _COL_STANDARDS,
     _COL_HOSPITAL_DAYS,
     _COL_VISITS,
     _COL_UETS,
     _COL_PATIENT_DAYS,
     _COL_SIMPLE_SERVICES,
     _COL_SMP,
     _COL_SUM) = range(_COLS_COUNT)
    _COL_EVENT_IDS = 'eventIds'
    _COL_STANDARDS_SUM = 'standardsSum'
    _COL_VISITS_SUM = 'visitsSum'
    _COL_SIMPLE_SERVICES_SUM = 'simpleServicesSum'
    _COL_SMP_SUM = 'smpSum'
    _COL_SERVICES_COUNT = 'serviceCount'
    _COL_FINISHED_EVENTS = 'finishedEvents'

    (_SELECT_EVENTS,
     _SELECT_ACTIONS,
     _SELECT_VISITS) = range(3)

    _DEFAULT_ADULT_AGE = 18
    _DEFAULT_PENSION_MALE_AGE = 60
    _DEFAULT_PENSION_FEMALE_AGE = 55

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setOrientation(QtGui.QPrinter.Landscape)
        self._forms = [
            [u'Форма Э-1. Нагрузка на врача', self._build_e1],
            [u'Форма Э-2. Выполненные объемы услуг в разрезе диагнозов', self._build_e2],
            [u'Форма Э-3. Анализ нагрузки на врачей', self._build_e3],
            [u'Форма Э-4. Анализ нагрузки на врачей по видам финансирования', self._build_e4],
            [u'Форма Э-5. Выполненные объемы услуг в отделении', self._build_e5],
            [u'Форма Э-6. Анализ нагрузки на отделение по видам финансирования', self._build_e6],
            [u'Форма Э-7. Анализ нагрузки на подразделения', self._build_e7],
            [u'Форма Э-8. Анализ нагрузки на подразделения по видам финансирования', self._build_e8],
            [u'Форма Э-9. Сводка о выполненных медицинских услугах по врачам', self._build_e9],
            [u'Форма Э-10. Сводка о выполненных медицинских услугах по отделениям', self._build_e10],
            [u'Форма Э-11. Сводка о выполненных медицинских услугах по видам финансирования'
             u' в разрезе плательщиков', self._build_e11],
            [u'Форма Э-12. Список введенных услуг с нулевой ценой', self._build_e12],
            [u'Форма Э-14. Отчет о пролеченных больных в разрезе страховщиков', self._build_e14],
            [u'Форма Э-15. Отчет о работе отделений в разрезе плательщиков', self._build_e15],
            [u'Форма Э-16. Отчет о работе врачей в разрезе плательщиков', self._build_e16],
            [u'Форма Э-17. Выполненные объемы услуг по врачам', self._build_e17],
            [u'Форма Э-19. Список услуг, оказанных пациентам, в разрезе отделений', self._build_e19],
            [u'Форма Э-22. Выполненные объемы услуг в разрезе видов финансирования', self._build_e22],
            [u'Форма Э-24. Анализ нагрузки на отделение по видам финансирования в разрезе профилей коек', self._build_e24],
            [u'Форма Э-26. Сведения о численности застрахованных лиц, обратившихся в организацию'
             u' для оказания медицинской помощи', self._build_e26]
        ]
        self.dialog = CEconomicReportsSetup(parent, self)
        self.setTitle(u'Экономический анализ')
        self.dialog.setTitle(self.title())
        for form in self._forms:
            self.dialog.cmbForm.addItem(form[0])
        self._adultAge = self._DEFAULT_ADULT_AGE
        self._pensionMaleAge = self._DEFAULT_PENSION_MALE_AGE #int(self._pensionMaleAge) if self._pensionMaleAge is not None \
                                                         # else self._DEFAULT_PENSION_MALE_AGE
        self._pensionFemaleAge = self._DEFAULT_PENSION_FEMALE_AGE #int(self._pensionFemaleAge) if self._pensionFemaleAge is not None \
                                                             # else self._DEFAULT_PENSION_FEMALE_AGE
        self._financeIds = QtGui.qApp.db.getIdList('rbFinance')
        self._serviceInfoByServiceId = {}
        self._processedIds = {}
        self._contractMetaData = {}
        self._contractInfoMap = {}
        self._mapEventIdToMKB = {}

    def _selectRecords(self, params, selectType, isUseEndDate=False, isWithBedProfiles=False):
        db = QtGui.qApp.db
        # ---
        periodType = params.get('periodType', '')
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureCheckState = params.get('orgStructureCheckState', QtCore.Qt.Unchecked)
        orgStructureId = params.get('orgStructureId', None)
        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')
        personCheckState = params.get('personCheckState', QtCore.Qt.Unchecked)
        personId = params.get('personId', None)
        insurerCheckState = params.get('insurerCheckState', QtCore.Qt.Unchecked)
        insurerId = params.get('insurerId', None)
        ageCheckState = params.get('ageCheckState', QtCore.Qt.Unchecked)
        age = params.get('age', '')
        eventTypeCheckState = params.get('eventTypeCheckState', QtCore.Qt.Unchecked)
        eventTypeId = params.get('eventTypeId', None)
        socStatusCheckState = params.get('socStatusCheckState', QtCore.Qt.Unchecked)
        socStatusId = params.get('socStatusId', None)
        financeCheckState = params.get('financeCheckState', QtCore.Qt.Unchecked)
        financeId = params.get('financeId', None)
        # ---
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableClient = db.table('Client')
        tableContract = db.table('Contract')
        tableMes = db.table('mes.MES')
        tableMesSpecification = db.table('rbMesSpecification')
        tableClientPolicy = db.table('ClientPolicy')
        tableClientInsurer = db.table('Organisation').alias('ClientInsurer')
        tableAccountItem = db.table('Account_Item')
        tableAccount = db.table('Account')
        tableClientSocStatus = db.table('ClientSocStatus')
        tableSocStatusType = db.table('rbSocStatusType')
        tableAction = db.table('Action')
        tableVisit = db.table('Visit')
        tablePerson = db.table('Person')
        tableService = db.table('rbService')
        # ---
        queryTable = tableEvent
        baseTable = 'Event'
        # --- --- Event/Action/Visit
        if selectType == CEconomicReports._SELECT_ACTIONS:
            queryTable = tableAction
            queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            baseTable = 'Action'
        elif selectType == CEconomicReports._SELECT_VISITS:
            queryTable = tableVisit
            queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
            baseTable = 'Visit'
        # --- ---
        queryTable = queryTable.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
        queryTable = queryTable.leftJoin(tableMes, tableMes['id'].eq(tableEvent['MES_id']))
        queryTable = queryTable.leftJoin(tableMesSpecification, tableMesSpecification['id'].eq(
            tableEvent['mesSpecification_id']))
        queryTable = queryTable.leftJoin(tableService,
                                         '''rbService.id = (SELECT MAX(id) FROM rbService s WHERE s.code = mes.MES.code)''')
        queryTable = queryTable.leftJoin(tableClientPolicy, [tableClientPolicy['client_id'].eq(tableEvent['client_id']),
            '''ClientPolicy.id = getClientPolicyOnDateId(Event.client_id, 1, Event.execDate)'''])
        queryTable = queryTable.leftJoin(tableClientInsurer, tableClientInsurer['id'].eq(
            tableClientPolicy['insurer_id']))
        # --- --- Event/Action/Visit
        if selectType == CEconomicReports._SELECT_EVENTS:
            queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['event_id'].eq(tableEvent['id']))
        elif selectType == CEconomicReports._SELECT_ACTIONS:
            queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['action_id'].eq(tableAction['id']))
        elif selectType == CEconomicReports._SELECT_VISITS:
            queryTable = queryTable.leftJoin(tableAccountItem, tableAccountItem['visit_id'].eq(tableVisit['id']))
        # --- ---
        queryTable = queryTable.leftJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
        # ---
        cols = [tableEvent['client_id'].alias('clientId'),
                'age(Client.birthDate, %s) AS clientAge' %
                    ('Event.setDate' if not isUseEndDate else decorateString(endDate.toString(QtCore.Qt.ISODate))),
                tableClient['sex'].alias('clientSex'),
                tableEvent['id'].alias('eventId'),
                '''IF(IFNULL(Event.externalId, '') <> '', Event.externalId, Event.client_id) AS cardNo''',
                tableEvent['setDate'].alias('begTreatDate'),
                tableEvent['execDate'].alias('endTreatDate'),
                tableEvent['eventType_id'].alias('eventTypeId')]
        # --- --- Event/Action/Visit
        if selectType == CEconomicReports._SELECT_EVENTS:
            cols.append(tableEvent['execPerson_id'].alias('personId'))
            cols.append(tableEvent['contract_id'].alias('contractId'))
            cols.append(tableService['id'].alias('serviceId'))
        elif selectType == CEconomicReports._SELECT_ACTIONS:
            cols.append(tableAction['id'].alias('actionId'))
            cols.append('IF(Action.person_id IS NOT NULL, Action.person_id, Event.execPerson_id) AS personId')
            cols.append('IFNULL(Action.contract_id, Event.contract_id) as contractId')
            cols.append(tableAction['actionType_id'].alias('actionTypeId'))
            cols.append(tableAction['amount'].alias('actionAmount'))
            cols.append(tableAction['MKB'].alias('actionMKB'))
        elif selectType == CEconomicReports._SELECT_VISITS:
            cols.append(tableVisit['id'].alias('visitId'))
            cols.append('IF(Visit.person_id IS NOT NULL, Visit.person_id, Event.execPerson_id) AS personId')
            cols.append(tableEvent['contract_id'].alias('contractId'))
            cols.append(tableVisit['service_id'].alias('serviceId'))
        # --- ---
        cols.append('''
            (CASE (Contract.exposeDiscipline >> 5) & 3
             WHEN 0 THEN Contract.payer_id
             WHEN 1 THEN IF(ClientInsurer.head_id IS NULL, ClientInsurer.id, ClientInsurer.head_id)
             WHEN 2 THEN ClientInsurer.id
             END) AS payerId
        ''')
        cols.append(tableContract['finance_id'].alias('financeId'))
        cols.append('''
                IFNULL(COALESCE(%s
                                (SELECT Diagnosis.MKB FROM Diagnosis
                                 WHERE Diagnosis.id = (SELECT MAX(Diagnosis.id) FROM Diagnostic
                                                       INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                                                       WHERE Event.id = Diagnostic.event_id AND
                                                             Diagnostic.diagnosisType_id = 1 AND
                                                             Diagnostic.deleted = 0)),
                                (SELECT Diagnosis.MKB FROM Diagnosis
                                 WHERE Diagnosis.id = (SELECT MAX(Diagnosis.id) FROM Diagnostic
                                                       INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                                                       WHERE Event.id = Diagnostic.event_id AND
                                                             Diagnostic.diagnosisType_id = 2 AND
                                                             Diagnostic.deleted = 0)),
                                (SELECT Diagnosis.MKB FROM Diagnosis
                                 WHERE Diagnosis.id = (SELECT MAX(Diagnosis.id) FROM Diagnostic
                                                       INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                                                       WHERE Event.id = Diagnostic.event_id AND
                                                             Diagnostic.deleted = 0))), '') AS mkb
            ''' % ('' if selectType == CEconomicReports._SELECT_EVENTS else
                        '''IF(IFNULL(Action.MKB, '') <> '', Action.MKB, NULL),'''
                      if selectType == CEconomicReports._SELECT_ACTIONS else
                        '''(SELECT Diagnosis.MKB FROM Diagnosis
                           WHERE Diagnosis.id = (SELECT MAX(Diagnosis.id) FROM Diagnostic
                                                 INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
                                                 WHERE Event.id = Diagnostic.event_id AND
                                                       Visit.person_id = Diagnostic.person_id AND
                                                       Visit.service_id = Diagnostic.service_id AND
                                                       Diagnostic.deleted = 0)),'''))
        cols.append('ClientInsurer.id AS insurerId')
        cols.append('''(IFNULL(mes.MES.code, '') <> '' AND IFNULL(rbMesSpecification.code, '') <> '2') AS isMES''')
        cols.append('%s AS isWorker' %
                    db.existsStmt(tableClientSocStatus.innerJoin(tableSocStatusType, tableSocStatusType['id'].eq(
                                                                 tableClientSocStatus['socStatusType_id'])),
                                  [tableClientSocStatus['deleted'].eq(0),
                                   tableClientSocStatus['client_id'].eq(tableClient['id']),
                                   tableClientSocStatus['begDate'].le(endDate),
                                   db.joinOr([tableClientSocStatus['endDate'].isNull(),
                                              tableClientSocStatus['endDate'].gt(endDate)]),
                                   tableSocStatusType['name'].like(u'Работающий')]))
        if isWithBedProfiles:
            cols.append('''
                (SELECT rbHospitalBedProfile.name FROM Action
                 INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND
                                          ActionType.flatCode LIKE 'moving%' AND Action.deleted = 0
                 LEFT JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id
                 LEFT JOIN ActionProperty ON ActionProperty.type_id = ActionPropertyType.id
                 LEFT JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id = ActionProperty.id
                 LEFT JOIN OrgStructure_HospitalBed ON OrgStructure_HospitalBed.id = ActionProperty_HospitalBed.value
                 LEFT JOIN rbHospitalBedProfile ON rbHospitalBedProfile.id = OrgStructure_HospitalBed.profile_id
                 WHERE  Event.id = Action.event_id AND
                        Action.begDate = (SELECT MAX(Action.begDate) FROM Action
                                          INNER JOIN ActionType ON ActionType.id = Action.actionType_id AND
                                                     ActionType.flatCode LIKE 'moving%' AND Action.deleted = 0
                                          WHERE Event.id = Action.event_id) AND
                        ActionProperty.deleted = 0 AND
                        ActionProperty.action_id = Action.id AND
                        ActionPropertyType.typeName = 'HospitalBed'
                 ORDER BY Action.id DESC
                 LIMIT 1) AS bedProfile''')
        cols.append('mes.Mes.id as mesId')
        #TODO:skkachaev: Больше так не работает, если нужно будет восстановить логику — SPR71, SPR72
        # cols.append('mes.Mes.isUltraShort as isUltraShort')
        # cols.append('mes.Mes.isExtraLong as isExtraLong')
        cols.append('mes.Mes.code as mesCode')
        # ---
        cond = [tableEvent['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tableContract['deleted'].eq(0)]
        if selectType == CEconomicReports._SELECT_ACTIONS:
            cond.append(tableAction['deleted'].eq(0))
        elif selectType == CEconomicReports._SELECT_VISITS:
            cond.append(tableVisit['deleted'].eq(0))
        # --- FILTER
        # --- --- тип периода и период
        periodTypeIndex = self.dialog.periodTypeList.index(periodType)
        if periodTypeIndex:
            cond.append(tableAccount['deleted'].eq(0))
            cond.append(tableAccount['date'].ge(begDate))
            cond.append(tableAccount['date'].le(endDate))
            cond.append(tableAccountItem['deleted'].eq(0))
            cond.append(tableAccountItem['reexposeItem_id'].isNull())
            if selectType == CEconomicReports._SELECT_EVENTS:
                cond.append(tableAccountItem['visit_id'].isNull())
                cond.append(tableAccountItem['action_id'].isNull())
        else:
            cond.append(tableEvent['execDate'].ge(begDate))
            cond.append(tableEvent['execDate'].lt(endDate.addDays(1)))
        if orgStructureCheckState == QtCore.Qt.Checked and orgStructureId is not None:
            cond.append(db.existsStmt(tablePerson,
                ['Person.id = %s' % ('IF(Action.person_id IS NOT NULL, Action.person_id, Event.execPerson_id)'
                                        if selectType == CEconomicReports._SELECT_ACTIONS else
                                     'IF(Visit.person_id IS NOT NULL, Visit.person_id, Event.execPerson_id)'
                                        if selectType == CEconomicReports._SELECT_VISITS else
                                     'Event.execPerson_id'),
                 tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId))]))
        # --- --- тип реестра
        if payStatusCheckState == QtCore.Qt.Checked:
            payStatusIndex = self.dialog.payStatusList.index(payStatus)
            payStatusList = []
            if payStatusIndex == 0:  # Нет выставления, оплаты и отказа
                cond.append('%s.payStatus = 0' % baseTable)
            elif payStatusIndex == 1:  # Выставлено, нет оплаты и отказа
                for f_id in self._financeIds:
                    payStatusList.append(str(getExposed(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            elif payStatusIndex == 2:  # Отказано, нет оплаты
                for f_id in self._financeIds:
                    payStatusList.append(str(getRefused(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            elif payStatusIndex == 3:  # Оплачено
                for f_id in self._financeIds:
                    payStatusList.append(str(getPayed(getPayStatusMask(f_id))))
                cond.append('%s.payStatus IN (%s)' % (baseTable, ','.join(payStatusList)))
            else:  # Выставлено, оплачено, отказано
                cond.append('%s.payStatus <> 0' % baseTable)
        # ---  --- возрастная группа
        if ageCheckState == QtCore.Qt.Checked:
            age_index = self.dialog.ageList.index(age)
            age_string = u'TIMESTAMPDIFF(YEAR, Client.birthDate,' \
                         u' %s)' % ('Event.setDate' if not isUseEndDate
                                                    else decorateString(endDate.toString(QtCore.Qt.ISODate)))
            if age_index == 0:  # Дети
                cond.append('(%s < %d)' % (age_string, self._adultAge))
            elif age_index == 1:
                cond.append('(%s >= %d)' % (age_string, self._adultAge))
                cond.append('(({0} < {1} AND Client.sex=1) OR'
                            ' ({0} < {2} AND Client.sex=2))'.format(age_string, self._pensionMaleAge,
                                                                    self._pensionFemaleAge))
            elif age_index == 2:
                cond.append('(({0} >= {1} AND Client.sex=1) OR '
                            '({0} >= {2} AND Client.sex=2))'.format(age_string, self._pensionMaleAge,
                                                                    self._pensionFemaleAge))
        # --- --- вид медицинской помощи
        if eventTypeCheckState == QtCore.Qt.Checked and eventTypeId is not None:
            cond.append(tableEventType['id'].eq(eventTypeId))
        # --- --- категория населения
        if socStatusCheckState == QtCore.Qt.Checked and socStatusId is not None:
            cond.append(db.existsStmt(tableClientSocStatus, [tableClientSocStatus['deleted'].eq(0),
                                                             tableClientSocStatus['client_id'].eq(tableClient['id']),
                                                             tableClientSocStatus['begDate'].le(endDate),
                                                             db.joinOr([tableClientSocStatus['endDate'].isNull(),
                                                                        tableClientSocStatus['endDate'].gt(endDate)]),
                                                             tableClientSocStatus['socStatusType_id'].eq(socStatusId)]))
        # --- --- тип финансирования
        if financeCheckState == QtCore.Qt.Checked and financeId is not None:
            cond.append(tableContract['finance_id'].eq(financeId))
        # --- --- плательщик и врач
        result = []
        stmt = db.selectStmt(queryTable, cols, cond, isDistinct=True)
        query = db.query(stmt)
        descSelectType = u'Events' if selectType == CEconomicReports._SELECT_EVENTS else u'Actions' if selectType == CEconomicReports._SELECT_ACTIONS else u'Visits'
        self.addQueryText(forceString(query.lastQuery()), descSelectType)
        while query.next():
            #TODO: почему бы не вынести все эти условия в запрос?
            record = query.record()
            if (insurerCheckState != QtCore.Qt.Checked or insurerId == forceRef(record.value('payerId'))) and \
                    (personCheckState != QtCore.Qt.Checked or personId == forceRef(record.value('personId'))):
                result.append(record)
                contractId = forceRef(record.value('contractId'))
                if selectType in (CEconomicReports._SELECT_EVENTS, CEconomicReports._SELECT_VISITS):
                    serviceId = forceRef(record.value('serviceId'))
                    if serviceId:
                        self._contractMetaData.setdefault(contractId, set()).add(forceRef(record.value('serviceId')))
                elif selectType == CEconomicReports._SELECT_ACTIONS:
                    actionTypeId = forceRef(record.value('actionTypeId'))
                    financeId = forceRef(record.value('financeId'))
                    serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
                    if serviceIdList:
                        self._contractMetaData.setdefault(contractId, set()).update(serviceIdList)
        return result

    def _prepareTariffs(self, params):
        for contractId, services in self._contractMetaData.iteritems():
            self._contractInfoMap[contractId] = getContractInfo(contractId,
                                                                params.get('begDate', None),
                                                                params.get('endDate', None),
                                                                services)

    def build(self, params):
        doc = QtGui.QTextDocument()
        self._contractMetaData.clear()
        self._contractInfoMap.clear()
        self._mapEventIdToMKB.clear()
        # self._helper.setIsReturnZeroPrice(params.get('hideEmptyCheckState', QtCore.Qt.Unchecked) == QtCore.Qt.Unchecked)
        self._processedIds = {'event': [], 'action': [], 'visit': []}
        self._forms[params.get('formIndex', 0)][1](params, QtGui.QTextCursor(doc))
        return doc

    def _build_e1(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    serviceId = costInfo['serviceId']
                    costInfo.pop('serviceId')
                    if serviceId in reportRows:
                        for tariffName in costInfo.iterkeys():
                            reportRows[serviceId][tariffName] += costInfo[tariffName]
                    else:
                        reportRows[serviceId] = costInfo

        reportRows = {}
        totalRow = {}
        colByTariffName = [
            ('amount', 2),
            ('uet', 3),
            #('tariffB', 4),
            #('tariffDValue1', 5),
            #('tariffDValue2', 6),
            #('tariffDValue3', 7),
            #('tariffDValue4', 8),
            #('tariffD', 9),
            #('tariffDM', 10),
            ('sum', 11)
        ]
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-1. НАГРУЗКА НА ВРАЧА\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
                ('22%', [u'', u'Наименование'], CReportBase.AlignLeft),
                ('7%', [u'Кол-во услуг', u''],  CReportBase.AlignLeft),
                ('7%', [u'Кол-во УЕТ', u''], CReportBase.AlignLeft),
                ('7%', [u'Сумма по БТ', u''], CReportBase.AlignLeft),
                ('7%', [u'Сумма по дополнительному тарифу', u'Текущие расходы'], CReportBase.AlignLeft),
                ('7%', [u'', u'Расходы КУ'], CReportBase.AlignLeft),
                ('7%', [u'', u'Расходы НА'], CReportBase.AlignLeft),
                ('7%', [u'', u'Расходы оборуд.'], CReportBase.AlignLeft),
                ('7%', [u'', u'Итого'], CReportBase.AlignLeft),
                ('7%', [u'Сумма по модерн.', u''], CReportBase.AlignLeft),
                ('7%', [u'Сумма', u''], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 1, 5)
        table.mergeCells(0, 10, 2, 1)
        table.mergeCells(0, 11, 2, 1)
        # --- EVENT
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        for tariffName, col in colByTariffName:
            totalRow[tariffName] = 0
        for serviceId, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
            serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
            table.setText(row, 0, serviceCode)
            table.setText(row, 1, serviceName)
            for tariffName, col in colByTariffName:
                table.setText(row, col, reportRow[tariffName])
                totalRow[tariffName] += reportRow[tariffName]
        # --- ИТОГО
        row = table.addRow()
        table.setText(row, 1, u'Итого', fontBold=True)
        for tariffName, col in colByTariffName:
            table.setText(row, col, totalRow[tariffName], fontBold=True)
        # --- подтабличный текст
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        abbr = [u'\nБТ - базовый тариф',
                u'КУ - коммунальные услуги',
                u'НА - налоги, аренда',
                u'оборуд. - оборудование',
                u'модерн. - модернизация']
        cursor.insertText(',  '.join(abbr))
        cursor.insertText(u'\nПоле \"Количество услуг\" для койко-дня равно количеству койко-дней (пациенто-дней)')

    def _build_e2(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    mkb = forceString(record.value('mkb'))
                    reportRows[mkb] = self._tableValues(reportRows.get(mkb, None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'], costInfo['uet'],
                                                        costInfo['sum'], forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-2. ВЫПОЛНЕННЫЕ ОБЪЕМЫ УСЛУГ В РАЗРЕЗЕ ДИАГНОЗОВ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'Диагноз', u'Код'], CReportBase.AlignLeft),
                ('22%', [u'', u'Наименование'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев', u''],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг', u''], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП', u''], CReportBase.AlignLeft),
                ('8%', [u'Сумма', u''], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)
        table.mergeCells(0, 10, 2, 1)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 2
        for mkb, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, mkb)
            table.setText(row, 1, forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', mkb, 'DiagName')))
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, reportRow.get(col, 0))
                totalRow[col] = totalRow.get(col, 0) + reportRow.get(col, 0)
        # --- ИТОГО
        row = table.addRow()
        table.setText(row, 1, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e3(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    personName = u'%s (%s)' % (personInfo['fullName'], personInfo['code'])
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    orgStructureName = orgStructureName[-1] if len(orgStructureName) <= 2 \
                                                            else '/'.join(orgStructureName[-2:])
                    orgStructureName = orgStructureName if orgStructureName else u'Не задано'
                    reportRows[personName][orgStructureName] = self._tableValues(
                                                        reportRows.setdefault(personName, {}).get(orgStructureName,
                                                                                                  None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'], costInfo['uet'],
                                                        costInfo['sum'], forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-3. АНАЛИЗ НАГРУЗКИ НА ВРАЧЕЙ')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Врач / Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for personName, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, u'\nВрач: %s' % personName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            personTotalRow = {}
            for orgStructureName, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, orgStructureName)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, values.get(col, 0))
                    personTotalRow[col] = personTotalRow.get(col, 0) + values.get(col, 0)
            row = table.addRow()
            table.setText(row, 0, u'Итого по врачу', fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, personTotalRow.get(col, 0), fontBold=True)
                totalRow[col] = totalRow.get(col, 0) + personTotalRow.get(col, 0)
        # ---
        row = table.addRow()
        table.setText(row, 0, u'ИТОГО', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e4(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    personName = u'%s (%s)' % (personInfo['fullName'], personInfo['code'])
                    financeId = forceRef(record.value('financeId'))
                    reportRows[financeId][personName] = self._tableValues(
                                                            reportRows.setdefault(financeId, {}).get(personName, None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-4. АНАЛИЗ НАГРУЗКИ НА ВРАЧЕЙ ПО ВИДАМ ФИНАНСИРОВАНИЯ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Вид оплаты / Врач'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for financeId, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
            table.setText(row, 0, u'Вид финансирования: %s' % financeName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            financeTotalRow = {}
            for personInfo, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, personInfo)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, values.get(col, 0))
                    financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % financeName)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
                totalRow[col] = totalRow.get(col, 0) + financeTotalRow.get(col, 0)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e5(self, params, cursor):
        
        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id'])
                    orgStructureName = orgStructureName if orgStructureName else u'Не задано'
                    serviceId = costInfo['serviceId']
                    reportRows[orgStructureName][serviceId] = self._tableValues(
                                                            reportRows.setdefault(orgStructureName, {}).get(serviceId,
                                                                                                            None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))
        def addTotalRow(title, values):
            alignRightFormat = QtGui.QTextBlockFormat()
            alignRightFormat.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            row = table.addRow()
            table.setText(row, 0, title, fontBold=True)
            table.mergeCells(row, 0, 1, 2)
            table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0), fontBold=True)
            table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0),
                          fontBold=True)
            table.setText(row, 4, values.get(self._COL_UETS, 0), fontBold=True)
            table.setText(row, 5, values.get(self._COL_SUM, 0), fontBold=True)
            for title, colCount, colSum in totalRowTitles:
                row = table.addRow()
                table.setText(row, 0, title, blockFormat=alignRightFormat, fontBold=True)
                table.mergeCells(row, 0, 1, 2)
                table.setText(row, 2, values.get(colCount, 0), fontBold=True)
                table.setText(row, 5, values.get(colSum, 0), fontBold=True)

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-5. ВЫПОЛНЕННЫЕ ОБЪЕМЫ УСЛУГ В ОТДЕЛЕНИИ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
                ('22%', [u'', u'Наименование'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во услуг'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней/дн. лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        totalRowTitles = [[u'кол-во стандартов', self._COL_STANDARDS, self._COL_STANDARDS_SUM],
                          [u'кол-во посещений', self._COL_VISITS, self._COL_VISITS_SUM],
                          [u'кол-во простых услуг', self._COL_SIMPLE_SERVICES, self._COL_SIMPLE_SERVICES_SUM],
                          [u'кол-во вызовов СМП', self._COL_SMP, self._COL_SMP_SUM]]
        # ---
        for orgStructureName, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, u'\n%s' % orgStructureName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            orgTotalRow = {}
            for serviceId, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
                serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
                table.setText(row, 0, serviceCode)
                table.setText(row, 1, serviceName)
                table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0))
                table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0))
                table.setText(row, 4, values.get(self._COL_UETS, 0))
                table.setText(row, 5, values.get(self._COL_SUM, 0))
                for col in range(self._COLS_COUNT) + [totalRowTitle[2] for totalRowTitle in totalRowTitles] + \
                        [self._COL_SERVICES_COUNT]:
                    orgTotalRow[col] = orgTotalRow.get(col, 0) + values.get(col, 0)
            addTotalRow(u'Итого по отделению:', orgTotalRow)
            for col in range(self._COLS_COUNT) + [totalRowTitle[2] for totalRowTitle in totalRowTitles] + \
                    [self._COL_SERVICES_COUNT]:
                totalRow[col] = totalRow.get(col, 0) + orgTotalRow.get(col, 0)
        addTotalRow(u'ИТОГО:', totalRow)

    def _build_e6(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    financeId = forceRef(record.value('financeId'))
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    unit = '/'.join(orgStructureName[:-1])
                    unit = unit if unit else u'Не задано'
                    office = orgStructureName[-1]
                    reportRows[financeId][unit][office] = self._tableValues(
                                                            reportRows.setdefault(financeId,
                                                                                  {}).setdefault(unit, {}).get(office,
                                                                                                               None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))
                    

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-6. АНАЛИЗ НАГРУЗКИ НА ОТДЕЛЕНИЕ ПО ВИДАМ ФИНАНСИРОВАНИЯ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for financeId, organisation in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')),
            table.setText(row, 0, u'\nВид финансирования: %s' % financeName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            financeTotalRow = {}
            for unit, orgStructure in sorted(organisation.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, u'\n%s' % unit, fontBold=True)
                organisationTotalRow = {}
                for office, values in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    table.setText(row, 0, office)
                    for col in xrange(self._COLS_COUNT):
                        table.setText(row, col + colsShift, values.get(col, 0))
                        organisationTotalRow[col] = organisationTotalRow.get(col, 0) + values.get(col, 0)
                        financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
                        totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                row = table.addRow()
                table.setText(row, 0, u'Итого по %s' % unit, fontBold=True)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, organisationTotalRow.get(col, 0), fontBold=True)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % financeName, fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e7(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    unit = '/'.join(orgStructureName[:-1])
                    unit = unit if unit else u'Не задано'
                    office = orgStructureName[-1]
                    reportRows[unit][office] = self._tableValues(
                                                        reportRows.setdefault(unit, {}).get(office, None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'],
                                                        costInfo['uet'], costInfo['sum'],
                                                        forceBool(record.value('isMes')))
        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-7. АНАЛИЗ НАГРУЗКИ НА ПОДРАЗДЕЛЕНИЯ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for unit, orgStructure in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, u'\n%s' % unit, fontBold=True)
            organisationTotalRow = {}
            for office, values in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, office)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, values.get(col, 0))
                    organisationTotalRow[col] = organisationTotalRow.get(col, 0) + values.get(col, 0)
                    totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
            row = table.addRow()
            table.setText(row, 0, u'Итого по подразделению: ', fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, organisationTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'ИТОГО', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e8(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    financeId = forceRef(record.value('financeId'))
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    if len(orgStructureName) < 3:
                        parent = orgStructureName[0] if orgStructureName[0] else u'Не задано'
                        unit = orgStructureName[1] if len(orgStructureName) > 1 else ''
                    else:
                        parent = '/'.join(orgStructureName[:-2])
                        unit = orgStructureName[-2]
                    reportRows[financeId][parent][unit] = self._tableValues(
                                                            reportRows.setdefault(financeId,
                                                                                  {}).setdefault(parent, {}).get(unit,
                                                                                                                 None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-8. АНАЛИЗ НАГРУЗКИ НА ПОДРАЗДЕЛЕНИЯ ПО ВИДАМ ФИНАНСИРОВАНИЯ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for financeId, organisation in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')),
            table.setText(row, 0, u'\nВид финансирования: %s' % financeName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            financeTotalRow = {}
            for parent, orgStructure in sorted(organisation.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, u'\n%s' % parent, fontBold=True)
                organisationTotalRow = {}
                for unit, values in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    table.setText(row, 0, unit)
                    for col in xrange(self._COLS_COUNT):
                        table.setText(row, col + colsShift, values.get(col, 0))
                        organisationTotalRow[col] = organisationTotalRow.get(col, 0) + values.get(col, 0)
                        financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
                        totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                row = table.addRow()
                table.setText(row, 0, u'Итого по %s' % parent, fontBold=True)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, organisationTotalRow.get(col, 0), fontBold=True)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % financeName, fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e9(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    personName = u'%s (%s)' % (personInfo['fullName'], personInfo['code'])
                    financeId = forceRef(record.value('financeId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    orgStructureName = orgStructureName[-1] if len(orgStructureName) <= 2 \
                                                            else '/'.join(orgStructureName[-2:])
                    orgStructureName = orgStructureName if orgStructureName else u'Не задано'
                    reportRows[personName][financeId][orgStructureName] = self._tableValues(
                                                        reportRows.setdefault(personName,
                                                                              {}).setdefault(financeId,
                                                                                             {}).get(orgStructureName,
                                                                                                     None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'], costInfo['uet'],
                                                        costInfo['sum'], forceBool(record.value('isMes')))
        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-9. СВОДКА О ВЫПОЛНЕННЫХ МЕДИЦИНСКИХ УСЛУГАХ ПО ВРАЧАМ')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Врач / Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for personName, finance in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()            
            table.setText(row, 0, u'\nВрач: %s' % personName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            personTotalRow = {}
            for financeId, orgStructure in sorted(finance.iteritems(), key=lambda item: item[0]):
                financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')),
                row = table.addRow()
                table.setText(row, 0, u'Вид финансирования: %s' % financeName, fontBold=True)
                financeTotalRow = {}
                for orgStructureName, values in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    table.setText(row, 0, orgStructureName)
                    for col in xrange(self._COLS_COUNT):
                        table.setText(row, col + colsShift, values.get(col, 0))
                        financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
                        personTotalRow[col] = personTotalRow.get(col, 0) + values.get(col, 0)
                        totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                row = table.addRow()
                table.setText(row, 0, u'Итого по %s' % financeName, fontBold=True)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
            row = table.addRow()
            table.setText(row, 0, u'Итого по врачу', fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, personTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e10(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id'])
                    orgStructureName = orgStructureName if orgStructureName else u'Не задано'
                    financeId = forceRef(record.value('financeId'))
                    serviceId = costInfo['serviceId']
                    reportRows[orgStructureName][financeId][serviceId] = self._tableValues(
                                                        reportRows.setdefault(orgStructureName,
                                                                              {}).setdefault(financeId,
                                                                                             {}).get(serviceId, None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'], costInfo['uet'],
                                                        costInfo['sum'], forceBool(record.value('isMes')))

        def addTotalRow(title, values):
            alignRightFormat = QtGui.QTextBlockFormat()
            alignRightFormat.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            row = table.addRow()
            table.setText(row, 0, title, fontBold=True)
            table.mergeCells(row, 0, 1, 2)
            table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0), fontBold=True)
            table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0),
                          fontBold=True)
            table.setText(row, 4, values.get(self._COL_UETS, 0), fontBold=True)
            table.setText(row, 5, values.get(self._COL_SUM, 0), fontBold=True)

        reportRows = {}
        totalRow = {}
        totalFinishedEvents = 0
        totalVisits = 0
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-10. СВОДКА О ВЫПОЛНЕННЫХ МЕДИЦИНСКИХ УСЛУГАХ ПО ОТДЕЛЕНИЯМ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
                ('40%', [u'', u'Наименование'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во услуг'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней/дн. лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        totalRowTitles = [[u'кол-во стандартов', self._COL_STANDARDS, self._COL_STANDARDS_SUM],
                          [u'кол-во посещений', self._COL_VISITS, self._COL_VISITS_SUM],
                          [u'кол-во простых услуг', self._COL_SIMPLE_SERVICES, self._COL_SIMPLE_SERVICES_SUM],
                          [u'кол-во вызовов СМП', self._COL_SMP, self._COL_SMP_SUM]]
        # ---
        for orgStructureName, finance in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, u'\n%s' % orgStructureName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            orgTotalRow = {}
            orgFinishedEvents = 0
            orgVisits = 0
            for financeId, service in sorted(finance.iteritems(), key=lambda item: item[0]):
                financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
                row = table.addRow()
                table.setText(row, 0, u'Вид финансирования: %s' % financeName, fontBold=True)
                table.mergeCells(row, 0, 1, 10)
                financeTotalRow = {}
                financeFinishedEvents = 0
                financeVisits = 0
                for serviceId, values in sorted(service.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
                    serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
                    table.setText(row, 0, serviceCode)
                    table.setText(row, 1, serviceName)
                    table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0))
                    table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) +
                                          values.get(self._COL_PATIENT_DAYS, 0))
                    table.setText(row, 4, values.get(self._COL_UETS, 0))
                    table.setText(row, 5, values.get(self._COL_SUM, 0))
                    for col in range(self._COLS_COUNT) + [totalRowTitle[2] for totalRowTitle in totalRowTitles] + \
                            [self._COL_SERVICES_COUNT]:
                        financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
                        orgTotalRow[col] = orgTotalRow.get(col, 0) + values.get(col, 0)                        
                        totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                    financeFinishedEvents += values.get(self._COL_FINISHED_EVENTS, 0)
                    financeVisits += values.get(self._COL_VISITS, 0)
                    orgFinishedEvents += values.get(self._COL_FINISHED_EVENTS, 0)
                    orgVisits += values.get(self._COL_VISITS, 0)
                    totalFinishedEvents += values.get(self._COL_FINISHED_EVENTS, 0)
                    totalVisits += values.get(self._COL_VISITS, 0)
                addTotalRow(u'Итого по %s: кол-во законченных случаев - %d,'
                            u' кол-во посещений - %d' % (financeName, financeFinishedEvents, financeVisits),
                            financeTotalRow)
            addTotalRow(u'Итого по отделению: кол-во законченных случаев - %d,'
                        u' кол-во посещений - %d' % (orgFinishedEvents, orgVisits), orgTotalRow)
        addTotalRow(u'ИТОГО: кол-во законченных случаев - %d,'
                    u' кол-во посещений - %d' % (totalFinishedEvents, totalVisits), totalRow)

    def _build_e11(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    financeId = forceRef(record.value('financeId'))
                    payerId = forceInt(record.value('payerId'))
                    reportRows[financeId][payerId] = self._tableValues(
                                                                reportRows.setdefault(financeId, {}).get(payerId, None),
                                                                forceRef(record.value('eventId')),
                                                                forceRef(record.value('actionId')),
                                                                forceRef(record.value('visitId')),
                                                                costInfo['serviceId'], costInfo['amount'],
                                                                costInfo['uet'], costInfo['sum'],
                                                                forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-11. СВОДКА О ВЫПОЛНЕННЫХ МЕДИЦИНСКИХ УСЛУГАХ ПО ВИДАМ ФИНАНСИРОВАНИЯ'
                          U' В РАЗРЕЗЕ ПЛАТЕЛЬЩИКОВ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Вид финансирования / Плательщик'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for financeId, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
            table.setText(row, 0, u'Вид финансирования: %s' % financeName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            financeTotalRow = {}
            for payerId, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                payerName = u'Не задан' if not payerId else forceString(QtGui.qApp.db.translate('Organisation', 'id',
                                                                                                payerId, 'fullName'))
                table.setText(row, 0, payerName)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, values.get(col, 0))
                    financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % financeName)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
                totalRow[col] = totalRow.get(col, 0) + financeTotalRow.get(col, 0)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e12(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo and not costInfo['sum']:
                    serviceId = costInfo['serviceId']
                    ticketNo = forceInt(record.value('eventId'))
                    begTreatDate = formatDate(record.value('begTreatDate'))
                    endTreatDate = formatDate(record.value('endTreatDate'))
                    clientId = forceInt(record.value('clientId'))
                    clientInfo = getClientInfo(clientId)
                    clientName = u'%s %s %s' % (clientInfo['lastName'], clientInfo['firstName'], clientInfo['patrName'])
                    reportRows.setdefault(serviceId, set()).add((clientName, ticketNo, begTreatDate, endTreatDate,
                                                                 clientId))

        reportRows = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-12. Список введнных услуг с нулевой ценой\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('10%', [u'Код услуги/№ талона'], CReportBase.AlignLeft),
                ('10%', [u'Дата начала лечения'], CReportBase.AlignLeft),
                ('10%', [u'Дата окончания лечения'],  CReportBase.AlignLeft),
                ('10%', [u'№ карты'],  CReportBase.AlignLeft),
                ('40%', [u'Фамилия Имя Отчество'],  CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        for serviceId, clients in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
            serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
            table.setText(row, 0, u'\n%s %s' % (serviceCode, serviceName), fontBold=True)
            table.mergeCells(row, 0, 1, 5)
            for clientName, ticketNo, begTreatDate, endTreatDate, clientId in sorted(clients,
                                                                                     key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, ticketNo)
                table.setText(row, 1, begTreatDate)
                table.setText(row, 2, endTreatDate)
                table.setText(row, 3, clientId)
                table.setText(row, 4, clientName)


    def _build_e14(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    financeId = forceRef(record.value('financeId'))
                    if financeId != CFinanceType.getId(CFinanceType.CMI):
                        continue
                    insurerId = forceRef(record.value('insurerId'))
                    insurerName = forceString(QtGui.qApp.db.translate('Organisation', 'id', insurerId, 'fullName'))
                    insurerCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', insurerId, 'infisCode'))
                    isWorker = forceInt(record.value('isWorker'))
                    reportRows[(insurerName, insurerCode)][isWorker] = self._tableValues(
                                                            reportRows.setdefault((insurerName, insurerCode),
                                                                                  {}).get(isWorker, None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-14. ОТЧЕТ О ПРОЛЕЧЕННЫХ БОЛЬНЫХ, ЗАСТРАХОВАННЫХ НА ТЕРРИТОРИИ '
                          u'КРАСНОДАРСКОГО КРАЯ, В РАЗРЕЗЕ СТРАХОВЩИКОВ')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('19%', [u'Страховщик'], CReportBase.AlignLeft),
                ('8%', [u'Всего', u'Кол-во случаев'], CReportBase.AlignLeft),
                ('8%', [u'', u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'', u'Сумма по ОМС, руб.'], CReportBase.AlignLeft),
                ('8%', [u'по работающим', u'Кол-во случаев'], CReportBase.AlignLeft),
                ('8%', [u'', u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'', u'Сумма по ОМС, руб.'], CReportBase.AlignLeft),
                ('8%', [u'по неработающим', u'Кол-во случаев'], CReportBase.AlignLeft),
                ('8%', [u'', u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'', u'Сумма по ОМС, руб.'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 3)
        table.mergeCells(0, 4, 1, 3)
        table.mergeCells(0, 7, 1, 3)
        # ---
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for (insurerName, insurerCode), worker in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            if not insurerCode:
                continue
            if not insurerName:
                insurerName = u'Не задана'
            row = table.addRow()
            table.setText(row, 0, insurerName)
            totalColumn = {}
            for isWorker, values in sorted(worker.iteritems(), key=lambda item: item[0]):
                if isWorker:
                    totalColumn[3] = values.get(self._COL_EVENTS, 0)
                    totalColumn[4] = values.get(self._COL_UETS, 0.0)
                    totalColumn[5] = values.get(self._COL_SUM, 0.0)
                else:
                    totalColumn[6] = values.get(self._COL_EVENTS, 0)
                    totalColumn[7] = values.get(self._COL_UETS, 0.0)
                    totalColumn[8] = values.get(self._COL_SUM, 0.0)
            for i in xrange(3):
                totalColumn[i] = totalColumn.get(3 + i, 0) + totalColumn.get(6 + i, 0)
            for i in xrange(9):
                table.setText(row, 1 + i, totalColumn.get(i, 0))
                totalRow[i] = totalRow.get(i, 0) + totalColumn.get(i, 0)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(len(totalRow)):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)
        # ---
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'\n\n\nФОРМА Э-14. ОТЧЕТ О ПРОЛЕЧЕННЫХ БОЛЬНЫХ, ЗАСТРАХОВАННЫХ ВНЕ ТЕРРИТОРИИ '
                          u'КРАСНОДАРСКОГО КРАЯ\n')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cols = [('50%', [u'Регион'], CReportBase.AlignLeft),
                ('10%', [u'Кол-во случаев'], CReportBase.AlignLeft),
                ('10%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('10%', [u'Сумма по ОМС, руб.'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        # ---
        totalRow = {}
        for (insurerName, insurerCode), worker in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            if insurerCode:
                continue
            if not insurerName:
                insurerName = u'Не задана'
            row = table.addRow()
            table.setText(row, 0, insurerName)
            totalColumn = {}
            for isWorker, values in sorted(worker.iteritems(), key=lambda item: item[0]):
                totalColumn[0] = totalColumn.get(0, 0) + values.get(self._COL_EVENTS, 0)
                totalColumn[1] = totalColumn.get(1, 0) + values.get(self._COL_UETS, 0.0)
                totalColumn[2] = totalColumn.get(2, 0) + values.get(self._COL_SUM, 0.0)
            for i in xrange(3):
                table.setText(row, 1 + i, totalColumn.get(i, 0))
                totalRow[i] = totalRow.get(i, 0) + totalColumn.get(i, 0)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(len(totalRow)):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)


    def _build_e15(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    payerId = forceInt(record.value('payerId'))
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    unit = '/'.join(orgStructureName[:-1])
                    unit = unit if unit else u'Не задано'
                    office = orgStructureName[-1]
                    reportRows[payerId][unit][office] = self._tableValues(
                                                        reportRows.setdefault(payerId,
                                                                              {}).setdefault(unit,
                                                                                             {}).get(office, None),
                                                        forceRef(record.value('eventId')),
                                                        forceRef(record.value('actionId')),
                                                        forceRef(record.value('visitId')),
                                                        costInfo['serviceId'], costInfo['amount'],
                                                        costInfo['uet'], costInfo['sum'],
                                                        forceBool(record.value('isMes')))
        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-15. ОТЧЕТ О РАБОТЕ ОТДЕЛЕНИЙ В РАЗРЕЗЕ ПЛАТЕЛЬЩИКОВ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Плательщик/Отделение'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        # --- Select data
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for payerId, organisation in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            payerName = u'Не задан' if not payerId else forceString(QtGui.qApp.db.translate('Organisation', 'id',
                                                                                            payerId, 'fullName'))
            table.setText(row, 0, u'\nПлательщик: %s' % payerName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            payerTotalRow = {}
            for unit, orgStructure in sorted(organisation.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, u'\n%s' % unit, fontBold=True)
                table.mergeCells(row, 0, 1, 10)
                organisationTotalRow = {}
                for office, values in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    table.setText(row, 0, office)
                    for col in xrange(self._COLS_COUNT):
                        table.setText(row, col + colsShift, values.get(col, 0))
                        organisationTotalRow[col] = organisationTotalRow.get(col, 0) + values.get(col, 0)
                        payerTotalRow[col] = payerTotalRow.get(col, 0) + values.get(col, 0)
                        totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                row = table.addRow()
                table.setText(row, 0, u'Итого по %s' % unit, fontBold=True)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, organisationTotalRow.get(col, 0), fontBold=True)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % payerName, fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, payerTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e16(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    personName = u'%s (%s)' % (personInfo['fullName'], personInfo['code'])
                    payerId = forceInt(record.value('payerId'))
                    reportRows[payerId][personName] = self._tableValues(
                                                            reportRows.setdefault(payerId, {}).get(personName, None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-16. ОТЧЕТ О РАБОТЕ ВРАЧЕЙ В РАЗРЕЗЕ ПЛАТЕЛЬЩИКОВ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Плательщик / Врач'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for payerId, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            payerName = u'Не задан' if not payerId else forceString(QtGui.qApp.db.translate('Organisation', 'id',
                                                                                            payerId, 'fullName'))
            table.setText(row, 0, u'Плательщик: %s' % payerName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            payerTotalRow = {}
            for personName, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, personName)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, values.get(col, 0))
                    payerTotalRow[col] = payerTotalRow.get(col, 0) + values.get(col, 0)
            row = table.addRow()
            table.setText(row, 0, u'Итого по плательщику:')
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, payerTotalRow.get(col, 0), fontBold=True)
                totalRow[col] = totalRow.get(col, 0) + payerTotalRow.get(col, 0)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e17(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    personName = u'%s (%s)' % (personInfo['fullName'], personInfo['code'])
                    serviceId = costInfo['serviceId']
                    reportRows[personName][serviceId] = self._tableValues(
                                                            reportRows.setdefault(personName, {}).get(serviceId, None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))

        def addTotalRow(title, values):
            alignRightFormat = QtGui.QTextBlockFormat()
            alignRightFormat.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            row = table.addRow()
            table.setText(row, 0, title, fontBold=True)
            table.mergeCells(row, 0, 1, 2)
            table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0))
            table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0))
            table.setText(row, 4, values.get(self._COL_UETS, 0))
            table.setText(row, 5, values.get(self._COL_SUM, 0))
            for title, colCount, colSum in totalRowTitles:
                row = table.addRow()
                table.setText(row, 0, title, blockFormat=alignRightFormat, fontBold=True)
                table.mergeCells(row, 0, 1, 2)
                table.setText(row, 2, values.get(colCount, 0), fontBold=True)
                table.setText(row, 5, values.get(colSum, 0))

        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-17. ВЫПОЛНЕННЫЕ ОБЪЕМЫ УСЛУГ ПО ВРАЧАМ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
                ('22%', [u'', u'Наименование'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во услуг'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней/дн. лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        totalRowTitles = [[u'кол-во стандартов', self._COL_STANDARDS, self._COL_STANDARDS_SUM],
                          [u'кол-во посещений', self._COL_VISITS, self._COL_VISITS_SUM],
                          [u'кол-во простых услуг', self._COL_SIMPLE_SERVICES, self._COL_SIMPLE_SERVICES_SUM],
                          [u'кол-во вызовов СМП', self._COL_SMP, self._COL_SMP_SUM]]
        for personName, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            table.setText(row, 0, u'\nВрач: %s' % personName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            personTotalRow = {}
            for serviceId, values in sorted(reportRow.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
                serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
                table.setText(row, 0, serviceCode)
                table.setText(row, 1, serviceName)
                table.setText(row, 2, values.get(self._COL_SERVICES_COUNT, 0))
                table.setText(row, 3, values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0))
                table.setText(row, 4, values.get(self._COL_UETS, 0))
                table.setText(row, 5, values.get(self._COL_SUM, 0))
                for col in range(self._COLS_COUNT) + [totalRowTitle[2] for totalRowTitle in totalRowTitles] + \
                        [self._COL_SERVICES_COUNT]:
                    personTotalRow[col] = personTotalRow.get(col, 0) + values.get(col, 0)
            addTotalRow(u'Итого по врачу:', personTotalRow)
            for col in range(self._COLS_COUNT) + [totalRowTitle[2] for totalRowTitle in totalRowTitles] + \
                    [self._COL_SERVICES_COUNT]:
                totalRow[col] = totalRow.get(col, 0) + personTotalRow.get(col, 0)
        addTotalRow(u'ИТОГО:', totalRow)

    def _build_e19(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureId = personInfo['orgStructure_id']
                    eventKey = (forceInt(record.value('clientId')), forceString(record.value('cardNo')),
                                formatDate(record.value('begTreatDate')), formatDate(record.value('endTreatDate')))
                    serviceId = costInfo['serviceId']
                    reportRows[orgStructureId][eventKey][serviceId] = \
                        self._tableValues(reportRows[orgStructureId][eventKey][serviceId],
                                          forceRef(record.value('eventId')),
                                          forceRef(record.value('actionId')),
                                          forceRef(record.value('visitId')),
                                          costInfo['serviceId'], costInfo['amount'], costInfo['uet'],
                                          costInfo['sum'], forceBool(record.value('isMes')))

        reportRows = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-19. СПИСОК УСЛУГ, ОКАЗАННЫХ ПАЦИЕНТАМ, В РАЗРЕЗЕ ОТДЕЛЕНИЙ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('6%', [u'№ карты (ист. болезни)', u''], CReportBase.AlignLeft),
                ('24%', [u'ФИО', u''], CReportBase.AlignLeft),
                ('10%', [u'Период лечения', u'с'],  CReportBase.AlignLeft),
                ('10%', [u'', u'по'],  CReportBase.AlignLeft),
                ('10%', [u'Код услуги', u''],  CReportBase.AlignLeft),
                ('10%', [u'Кол-во услуг', u''],  CReportBase.AlignLeft),
                ('10%', [u'Кол-во койко-дней', u''],  CReportBase.AlignLeft),
                ('10%', [u'Кол-во УЕТ', u''],  CReportBase.AlignLeft),
                ('10%', [u'Сумма', u''],  CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 2)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        totalRowTitles = [u'кол-во персональных счетов:',
                          u'кол-во стандартов:',
                          u'кол-во койко-дней (дней лечения):',
                          u'кол-во посещений:',
                          u'кол-во простых услуг:',
                          u'кол-во УЕТ:',
                          u'сумма, р:']
        # ---
        orgStructureNames = {}
        clientNames = {}
        serviceCodes = {}
        alignRightFormat = QtGui.QTextBlockFormat()
        alignRightFormat.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        for orgStructureId, clients in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            if orgStructureId in orgStructureNames:
                orgStructureName = orgStructureNames[orgStructureId]
            else:
                orgStructureName = getOrgStructureFullName(orgStructureId)
                orgStructureName = orgStructureName if orgStructureName else u'Не задано'
                orgStructureNames[orgStructureId] = orgStructureName
            row = table.addRow()
            table.setText(row, 0, u'\n%s' % orgStructureName, fontBold=True)
            table.mergeCells(row, 0, 1, 9)
            orgTotalRow = {}
            for (clientId, cardNo, begTreatDate, endTreatDate), service in sorted(clients.iteritems(),
                                                                                  key=lambda item: item[0]):
                if clientId in clientNames:
                    clientName = clientNames[clientId]
                else:
                    clientInfo = getClientInfo(clientId)
                    clientName = u'%s %s %s' % (clientInfo['lastName'], clientInfo['firstName'], clientInfo['patrName'])
                    clientNames[clientId] = clientName
                row = table.addRow()
                clientRow = row
                table.setText(row, 0, cardNo)
                table.setText(row, 1, clientName)
                table.setText(row, 2, begTreatDate)
                table.setText(row, 3, endTreatDate)
                serviceCounter = 0
                for serviceId, values in sorted(service.iteritems(), key=lambda item: item[0]):
                    serviceCounter += 1
                    if serviceCounter > 1:
                        row = table.addRow()
                    if serviceId in serviceCodes:
                        serviceCode = serviceCodes[serviceId]
                    else:
                        serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
                        serviceCodes[serviceId] = serviceCode
                    table.setText(row, 4, serviceCode)
                    table.setText(row, 5, values.get(self._COL_SERVICES_COUNT, 0))
                    table.setText(row, 6, values.get(self._COL_HOSPITAL_DAYS, 0))
                    table.setText(row, 7, values.get(self._COL_UETS, 0))
                    table.setText(row, 8, values.get(self._COL_SUM, 0))
                    orgTotalRow[0] = orgTotalRow.get(0, 0) + values.get(self._COL_EVENTS, 0)
                    orgTotalRow[1] = orgTotalRow.get(1, 0) + values.get(self._COL_STANDARDS, 0)
                    orgTotalRow[2] = orgTotalRow.get(2, 0) + (values.get(self._COL_HOSPITAL_DAYS, 0) +
                                                              values.get(self._COL_PATIENT_DAYS, 0))
                    orgTotalRow[3] = orgTotalRow.get(3, 0) + values.get(self._COL_VISITS, 0)
                    orgTotalRow[4] = orgTotalRow.get(4, 0) + values.get(self._COL_SIMPLE_SERVICES, 0)
                    orgTotalRow[5] = orgTotalRow.get(5, 0) + values.get(self._COL_UETS, 0)
                    orgTotalRow[6] = orgTotalRow.get(6, 0) + values.get(self._COL_SUM, 0)
                for col in range(4):
                    table.mergeCells(clientRow, col, serviceCounter, 1)
            for index in orgTotalRow.keys():
                totalRow[index] = totalRow.get(index, 0) + orgTotalRow.get(index, 0)
            row = table.addRow()
            orgRow = row
            table.setText(row, 0, u'Итого по %s' % orgStructureName, fontBold=True)
            for index, totalRowTitle in enumerate(totalRowTitles):
                if index > 0:
                    row = table.addRow()
                table.setText(row, 2, totalRowTitle, blockFormat=alignRightFormat, fontBold=True)
                table.mergeCells(row, 2, 1, 5)
                table.setText(row, 7, orgTotalRow.get(index, 0))
                table.mergeCells(row, 7, 1, 2)
            table.mergeCells(orgRow, 0, len(totalRowTitles), 2)
        row = table.addRow()
        orgRow = row
        table.setText(row, 0, u'ИТОГО', fontBold=True)
        for index, totalRowTitle in enumerate(totalRowTitles):
            if index > 0:
                row = table.addRow()
            table.setText(row, 2, totalRowTitle, blockFormat=alignRightFormat, fontBold=True)
            table.mergeCells(row, 2, 1, 5)
            table.setText(row, 7, totalRow.get(index, 0))
            table.mergeCells(row, 7, 1, 2)
        table.mergeCells(orgRow, 0, len(totalRowTitles), 2)

    def _build_e22(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    serviceId = costInfo['serviceId']
                    financeId = forceRef(record.value('financeId'))
                    if financeId not in financeIdList:
                        financeIdList.append(financeId)
                    reportRows[serviceId][financeId] = self._tableValues(
                                                            reportRows.setdefault(serviceId, {}).get(financeId, None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))
        reportRows = {}
        financeIdList = []
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-22. ВЫПОЛНЕННЫЕ ОБЪЕМЫ УСЛУГ В РАЗРЕЗЕ ВИДОВ ФИНАНСИРОВАНИЯ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        # ---
        colWidth = '6%' if len(financeIdList) < 3 else '3%'
        # ---
        cursor.insertBlock()
        cols = [('6%', [u'Услуга', u'Код'], CReportBase.AlignLeft),
                ('22%', [u'', u'Наименование'], CReportBase.AlignLeft)]
        for financeId in sorted(financeIdList):
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
            cols += [(colWidth, [u'%s' % financeName, u'Кол-во услуг'], CReportBase.AlignLeft),
                     (colWidth, [u'', u'Кол-во КД/ДЛ'], CReportBase.AlignLeft),
                     (colWidth, [u'', u'УЕТ'], CReportBase.AlignLeft),
                     (colWidth, [u'', u'Сумма'], CReportBase.AlignLeft)]
        cols += [(colWidth, [u'Итого по всем источникам финансирования', u'Кол-во услуг'], CReportBase.AlignLeft),
                 (colWidth, [u'', u'Кол-во КД/ДЛ'], CReportBase.AlignLeft),
                 (colWidth, [u'', u'УЕТ'], CReportBase.AlignLeft),
                 (colWidth, [u'', u'Сумма'], CReportBase.AlignLeft)]
        # ---
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 1, 2)
        for col in range(2, len(cols), 4):
            table.mergeCells(0, col, 1, 4)
        # ---
        totalRow = {}
        # ---
        for serviceId, reportRow in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            serviceCode = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'infis'))
            serviceName = forceString(QtGui.qApp.db.translate('rbService', 'id', serviceId, 'name'))
            table.setText(row, 0, serviceCode)
            table.setText(row, 1, serviceName)
            for i in range(2, len(cols), 4):
                table.setText(row, i, 0)
                table.setText(row, i + 1, 0)
                table.setText(row, i + 2, 0.0)
                table.setText(row, i + 3, 0.0)
            totalColumn = [0, 0, 0, 0]
            for financeId, values in reportRow.iteritems():
                col = 2 + sorted(financeIdList).index(financeId)*4
                rowVals = [0, 0, 0, 0]
                rowVals[0] = values.get(self._COL_SERVICES_COUNT, 0)
                rowVals[1] = values.get(self._COL_HOSPITAL_DAYS, 0) + values.get(self._COL_PATIENT_DAYS, 0)
                rowVals[2] = values.get(self._COL_UETS, 0)
                rowVals[3] = values.get(self._COL_SUM, 0)
                for i in range(4):
                    table.clearCell(row, col + i)
                    table.setText(row, col + i, rowVals[i])
                    totalColumn[i] += rowVals[i]
                    totalRow[col + i] = totalRow.get(col + i, 0) + rowVals[i]
            # ---
            col = 2 + len(financeIdList)*4
            for i in range(4):
                table.clearCell(row, col + i)
                table.setText(row, col + i, totalColumn[i])
                totalRow[col + i] = totalRow.get(col + i, 0) + totalColumn[i]
        # ---
        row = table.addRow()
        table.setText(row, 0, u'ИТОГО', fontBold=True)
        table.mergeCells(row, 0, 1, 2)
        for col, val in totalRow.iteritems():
            table.setText(row, col, val, fontBold=True)
        # --- подтабличный текст
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        abbr = [u'\nКД - койко-дни',
                u'ДЛ - дни лечения']
        cursor.insertText(',  '.join(abbr))

    def _build_e24(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                costInfo = self._getCostInfo(record, selectType)
                if costInfo:
                    financeId = forceRef(record.value('financeId'))
                    personInfo = getPersonInfo(record.value('personId'))
                    orgStructureName = getOrgStructureFullName(personInfo['orgStructure_id']).split('/')
                    unit = '/'.join(orgStructureName[:-1])
                    unit = unit if unit else u'Не задано'
                    office = orgStructureName[-1]
                    bedProfile = forceString(record.value('bedProfile'))
                    reportRows[financeId][unit][office][bedProfile] = self._tableValues(
                                                            reportRows.setdefault(
                                                                financeId,
                                                                {}).setdefault(unit,
                                                                               {}).setdefault(office,
                                                                                              {}).get(bedProfile,
                                                                                                      None),
                                                            forceRef(record.value('eventId')),
                                                            forceRef(record.value('actionId')),
                                                            forceRef(record.value('visitId')),
                                                            costInfo['serviceId'], costInfo['amount'],
                                                            costInfo['uet'], costInfo['sum'],
                                                            forceBool(record.value('isMes')))
                    
        reportRows = {}
        totalRow = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-24. АНАЛИЗ НАГРУЗКИ НА ОТДЕЛЕНИЕ ПО ВИДАМ ФИНАНСИРОВАНИЯ В РАЗРЕЗЕ ПРОФИЛЕЙ КОЕК\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('28%', [u'Отделение/Профиль койки'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во случаев'],  CReportBase.AlignLeft),
                ('8%', [u'Кол-во стандартов'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во койко-дней'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во посещений'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во УЕТ'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во дней лечения'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во простых услуг'], CReportBase.AlignLeft),
                ('8%', [u'Кол-во вызовов СМП'], CReportBase.AlignLeft),
                ('8%', [u'Сумма'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        tariffIndex = self.dialog.tariffList[params.get('tariffIndex', 0)][1]
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        colsShift = 1
        for financeId, organisation in sorted(reportRows.iteritems(), key=lambda item: item[0]):
            row = table.addRow()
            financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name')),
            table.setText(row, 0, u'\nВид финансирования: %s' % financeName, fontBold=True)
            table.mergeCells(row, 0, 1, 10)
            financeTotalRow = {}
            for unit, orgStructure in sorted(organisation.iteritems(), key=lambda item: item[0]):
                row = table.addRow()
                table.setText(row, 0, u'\n%s' % unit, fontBold=True)
                organisationTotalRow = {}
                for office, bedProfiles in sorted(orgStructure.iteritems(), key=lambda item: item[0]):
                    row = table.addRow()
                    officeRow = row
                    table.setText(row, 0, office, fontBold=True)
                    inCount = False
                    officeTotalRow = {}
                    for bedProfile, values in sorted(bedProfiles.iteritems(), key=lambda item: item[0]):
                        if len(bedProfile) != 0:
                            if not inCount:
                                row = table.addRow()
                                table.setText(row, 0, u'  в том числе:')
                                inCount = True
                            row = table.addRow()
                            table.setText(row, 0, u'    %s' % bedProfile)
                            for col in xrange(self._COLS_COUNT):
                                table.setText(row, col + colsShift, values.get(col, 0))
                        for col in xrange(self._COLS_COUNT):
                            officeTotalRow[col] = officeTotalRow.get(col, 0) + values.get(col, 0)
                            organisationTotalRow[col] = organisationTotalRow.get(col, 0) + values.get(col, 0)
                            financeTotalRow[col] = financeTotalRow.get(col, 0) + values.get(col, 0)
                            totalRow[col] = totalRow.get(col, 0) + values.get(col, 0)
                    for col in xrange(self._COLS_COUNT):
                        table.setText(officeRow, col + colsShift, officeTotalRow.get(col, 0))
                row = table.addRow()
                table.setText(row, 0, u'Итого по %s' % unit, fontBold=True)
                for col in xrange(self._COLS_COUNT):
                    table.setText(row, col + colsShift, organisationTotalRow.get(col, 0), fontBold=True)
            row = table.addRow()
            table.setText(row, 0, u'Итого по %s' % financeName, fontBold=True)
            for col in xrange(self._COLS_COUNT):
                table.setText(row, col + colsShift, financeTotalRow.get(col, 0), fontBold=True)
        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        for col in xrange(self._COLS_COUNT):
            table.setText(row, col + colsShift, totalRow.get(col, 0), fontBold=True)

    def _build_e26(self, params, cursor):

        def processRecords(records, selectType):
            for record in records:
                clientId = forceRef(record.value('clientId'))
                if not clientId in processedClientIds:
                    costInfo = self._getCostInfo(record, selectType)
                    if costInfo:
                        processedClientIds.append(clientId)
                        payerId = forceInt(record.value('payerId'))
                        clientAge = forceInt(record.value('clientAge'))
                        clientSex = forceInt(record.value('clientSex'))
                        reportRow = reportRows.setdefault(payerId, [0]*9)
                        reportRow[0] += 1
                        if clientAge <= 4:  # 0-4 лет
                            if clientSex == 1:
                                reportRow[1] += 1  # муж
                            else:
                                reportRow[2] += 1  # жен
                        elif 5 <= clientAge <= 17:  # 5-17 лет
                            if clientSex == 1:
                                reportRow[3] += 1  # муж
                            else:
                                reportRow[4] += 1  # жен
                        elif 18 <= clientAge < 60 and clientSex == 1:
                            reportRow[5] += 1  # 18-59 лет муж
                        elif 18 <= clientAge < 55 and clientSex == 2:
                            reportRow[6] += 1  # 18-54 лет жен
                        elif clientAge >= 60 and clientSex == 1:
                            reportRow[7] += 1  # от 60 муж
                        elif clientAge >= 55 and clientSex == 2:
                            reportRow[8] += 1  # от 55 жен

        def createFormTable(cursor):
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertBlock()
            cols = [
                ('20%', [u'Число застрахованных лиц, чел.', u'', u'', u''], CReportBase.AlignLeft),
                ('10%', [u'В том числе по группам застрахованных лиц', u'Дети', u'0-4 лет', u'муж.'],
                    CReportBase.AlignLeft),
                ('10%', [u'', u'', u'', u'жен.'],  CReportBase.AlignLeft),
                ('10%', [u'', u'', u'5-17 лет', u'муж.'], CReportBase.AlignLeft),
                ('10%', [u'', u'', u'', u'жен.'], CReportBase.AlignLeft),
                ('10%', [u'', u'Трудоспособный возраст', u'18-59 лет', u'муж.'], CReportBase.AlignLeft),
                ('10%', [u'', u'', u'18-54 лет', u'жен.'], CReportBase.AlignLeft),
                ('10%', [u'', u'пенсионеры', u'60 лет и старше', u'муж.'], CReportBase.AlignLeft),
                ('10%', [u'', u'', u'55 лет и старше', u'жен.'], CReportBase.AlignLeft),
            ]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 4, 1)
            table.mergeCells(0, 1, 1, 9)
            table.mergeCells(1, 1, 1, 4)
            table.mergeCells(2, 1, 1, 2)
            table.mergeCells(2, 3, 1, 2)
            table.mergeCells(1, 5, 1, 2)
            table.mergeCells(1, 7, 1, 2)
            return table

        processedClientIds = []
        reportRows = {}
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertBlock()
        cursor.insertText(u'ФОРМА Э-26. СВЕДЕНИЯ О ЧИСЛЕННОСТИ ЗАСТРАХОВАННЫХ ЛИЦ, ОБРАТИВШИХСЯ В ОРГАНИЗАЦИЮ'
                          u' ДЛЯ ОКАЗАНИЯ МЕДИЦИНСКОЙ ПОМОЩИ\n')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        eventRecords = self._selectRecords(params, CEconomicReports._SELECT_EVENTS)
        actionRecords = self._selectRecords(params, CEconomicReports._SELECT_ACTIONS)
        visitRecords = self._selectRecords(params, CEconomicReports._SELECT_VISITS)
        # --- Prepare tariffs
        self._prepareTariffs(params)

        # --- Process records
        processRecords(eventRecords, CEconomicReports._SELECT_EVENTS)
        processRecords(actionRecords, CEconomicReports._SELECT_ACTIONS)
        processRecords(visitRecords, CEconomicReports._SELECT_VISITS)
        # ---
        for payerId, reportRow in reportRows.iteritems():
            if payerId:
                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.insertBlock()
                cursor.insertText('\n\n')
                cursor.insertText(forceString(QtGui.qApp.db.translate('Organisation', 'id', payerId, 'fullName')))
                table = createFormTable(cursor)
                row = table.addRow()
                for col, value in enumerate(reportRow):
                    table.setText(row, col, value)
        cursor.movePosition(QtGui.QTextCursor.End)
        # Пациенты без полиса
        if 0 in reportRows:
            cursor.insertBlock()
            cursor.insertText(u'\n\nНезарегистрированные в страховых организациях пациенты')
            table = createFormTable(cursor)
            row = table.addRow()
            for col, value in enumerate(reportRows[0]):
                table.setText(row, col, value)

    def getSetupDialog(self, parent):
        return self.dialog

    def getDefaultParams(self):
        result = CReport.getDefaultParams(self)
        prefs = getPref(QtGui.qApp.preferences.reportPrefs, self.title(), {})
        result['formIndex'] = getPrefInt(prefs, 'formIndex', 0)
        result['tariffIndex'] = getPrefInt(prefs, 'tariffIndex', 0)
        result['periodType'] = getPrefString(prefs, 'periodType', self.dialog.periodTypeList[0])
        result['begDate'] = getPrefDate(prefs, 'begDate', firstMonthDay(QtCore.QDate.currentDate()))
        result['endDate'] = getPrefDate(prefs, 'endDate', QtCore.QDate.currentDate())
        result['orgStructureCheckState'] = getPrefInt(prefs, 'orgStructureCheckState', QtCore.Qt.Unchecked)
        result['orgStructureId'] = getPrefRef(prefs, 'orgStructureId', None)
        result['payStatusCheckState'] = getPrefInt(prefs, 'payStatusCheckState', QtCore.Qt.Unchecked)
        result['payStatus'] = getPrefString(prefs, 'payStatus', self.dialog.payStatusList[0])
        result['personCheckState'] = getPrefInt(prefs, 'personCheckState', QtCore.Qt.Unchecked)
        result['personId'] = getPrefRef(prefs, 'personId', None)
        result['insurerCheckState'] = getPrefInt(prefs, 'insurerCheckState', QtCore.Qt.Unchecked)
        result['insurerId'] = getPrefRef(prefs, 'insurerId', None)
        result['ageCheckState'] = getPrefInt(prefs, 'ageCheckState', QtCore.Qt.Unchecked)
        result['age'] = getPrefString(prefs, 'age', self.dialog.ageList[0])
        result['eventTypeCheckState'] = getPrefInt(prefs, 'eventTypeCheckState', QtCore.Qt.Unchecked)
        result['eventTypeId'] = getPrefRef(prefs, 'eventTypeId', None)
        result['socStatusCheckState'] = getPrefInt(prefs, 'socStatusCheckState', QtCore.Qt.Unchecked)
        result['socStatusId'] = getPrefRef(prefs, 'socStatusId', None)
        result['financeCheckState'] = getPrefInt(prefs, 'financeCheckState', QtCore.Qt.Unchecked)
        result['financeId'] = getPrefRef(prefs, 'financeId', None)
        result['hideEmptyCheckState'] = getPrefInt(prefs, 'hideEmptyCheckState', QtCore.Qt.Unchecked)
        return result

    def dumpParams(self, cursor, params):

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u'с %s ' % forceString(begDate)
            if endDate:
                result += u'по %s ' % forceString(endDate)
            return result

        db = QtGui.qApp.db
        # ---
        formIndex = params.get('formIndex', 0)
        tariffIndex = params.get('tariffIndex', 0)
        periodType = params.get('periodType', '')
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureCheckState = params.get('orgStructureCheckState', QtCore.Qt.Unchecked)
        orgStructureId = params.get('orgStructureId', None)
        payStatusCheckState = params.get('payStatusCheckState', QtCore.Qt.Unchecked)
        payStatus = params.get('payStatus', '')
        personCheckState = params.get('personCheckState', QtCore.Qt.Unchecked)
        personId = params.get('personId', None)
        insurerCheckState = params.get('insurerCheckState', QtCore.Qt.Unchecked)
        insurerId = params.get('insurerId', None)
        ageCheckState = params.get('ageCheckState', QtCore.Qt.Unchecked)
        age = params.get('age', '')
        eventTypeCheckState = params.get('eventTypeCheckState', QtCore.Qt.Unchecked)
        eventTypeId = params.get('eventTypeId', None)
        socStatusCheckState = params.get('socStatusCheckState', QtCore.Qt.Unchecked)
        socStatusId = params.get('socStatusId', None)
        financeCheckState = params.get('financeCheckState', QtCore.Qt.Unchecked)
        financeId = params.get('financeId', None)
        hideEmpty = params.get('hideEmptyCheckState', QtCore.Qt.Unchecked)
        # ---
        rows = []
        if formIndex != 0:
            rows.append(u'Тариф: %s' % self.dialog.tariffList[tariffIndex][0])
        rows.append(u'Тип периода: %s' % periodType)
        rows.append(u'За период %s' % dateRangeAsStr(begDate, endDate))
        # ---
        if orgStructureCheckState == QtCore.Qt.Checked and orgStructureId is not None:
            rows.append(u'Подразделение: %s' % forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name')))
        else:
            rows.append(u'Подразделение: не задано')
        # ---
        if payStatusCheckState == QtCore.Qt.Checked:
            rows.append(u'Тип реестра: %s' % payStatus)
        else:
            rows.append(u'Тип реестра: не задан')
        # ---
        if personCheckState == QtCore.Qt.Checked and personId is not None:
            personInfo = getPersonInfo(personId)
            rows.append(u'Врач: %s, %s' % (personInfo['shortName'], personInfo['specialityName']))
        else:
            rows.append(u'Врач: не задан')
        # ---
        if insurerCheckState == QtCore.Qt.Checked and insurerId is not None:
            rows.append(u'СМО: %s' % forceString(db.translate('Organisation', 'id', insurerId, 'shortName')))
        else:
            rows.append(u'СМО: не задана')
        # ---
        if ageCheckState == QtCore.Qt.Checked:
            rows.append(u'Возрастная группа: %s' % age)
        else:
            rows.append(u'Возрастная группа: не задана')
        # ---
        if eventTypeCheckState == QtCore.Qt.Checked and eventTypeId is not None:
            rows.append(u'Вид медицинской помощи: %s' % forceString(db.translate('EventType', 'id', eventTypeId,
                                                                                 'name')))
        else:
            rows.append(u'Вид медицинской помощи: не задан')
        # ---
        if socStatusCheckState == QtCore.Qt.Checked and socStatusId is not None:
            rows.append(u'Категория населения: %s' % forceString(db.translate('vrbSocStatusType', 'id', socStatusId,
                                                                              'name')))
        else:
            rows.append(u'Категория населения: не задана')
        # ---
        if financeCheckState == QtCore.Qt.Checked and financeId is not None:
            rows.append(u'Тип финансирования: %s' % forceString(db.translate('rbFinance', 'id', financeId, 'name')))
        else:
            rows.append(u'Тип финансирования: не задан')
        # ---
        if hideEmpty == QtCore.Qt.Checked:
            rows.append(u'Услуги с нулевой ценой НЕ учитываются')
        else:
            rows.append(u'Услуги с нулевой ценой учитываются')
        # ---
        rows.append(u'Отчёт составлен: %s' % forceString(QtCore.QDateTime.currentDateTime()))
        # ---
        columns = [('100%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def _tableValues(self, tableValues, eventId, actionId, visitId, serviceId, amount, uet, tariff, isMes):
        if not tableValues:
            tableValues = {}
        if (not self._COL_EVENT_IDS in tableValues or not eventId in tableValues[self._COL_EVENT_IDS]) and \
                not actionId and not visitId:
            tableValues[self._COL_STANDARDS] = tableValues.get(self._COL_STANDARDS, 0) + (0 if not isMes else 1)
            tableValues[self._COL_STANDARDS_SUM] = tableValues.get(self._COL_STANDARDS_SUM, 0) + (0 if not isMes
                                                                                                    else tariff)
        tableValues.setdefault(self._COL_EVENT_IDS, set()).add(eventId)
        tableValues[self._COL_EVENTS] = len(tableValues[self._COL_EVENT_IDS])
        serviceCode, isVisit = self._serviceInfo(serviceId)
        if serviceCode[:1] in ('G', 'V') or (serviceCode[:1] == 'S' and serviceCode[-5:-4] == '0') or \
                serviceCode[:2] == 'K1':
            tableValues[self._COL_HOSPITAL_DAYS] = tableValues.get(self._COL_HOSPITAL_DAYS, 0) + amount
        elif serviceCode[:1] == 'S' or serviceCode[:2] in ('K4', 'K5', 'K7'):
            tableValues[self._COL_PATIENT_DAYS] = tableValues.get(self._COL_PATIENT_DAYS, 0) + amount
        elif visitId or (actionId and isVisit):
            tableValues[self._COL_VISITS] = tableValues.get(self._COL_VISITS, 0) + amount
            tableValues[self._COL_VISITS_SUM] = tableValues.get(self._COL_VISITS_SUM, 0) + tariff
        elif actionId and not isVisit:
            tableValues[self._COL_SIMPLE_SERVICES] = tableValues.get(self._COL_SIMPLE_SERVICES, 0) + amount
            tableValues[self._COL_SIMPLE_SERVICES_SUM] = tableValues.get(self._COL_SIMPLE_SERVICES_SUM, 0) + tariff
        tableValues[self._COL_UETS] = tableValues.get(self._COL_UETS, 0) + uet
        tableValues[self._COL_SUM] = tableValues.get(self._COL_SUM, 0) + tariff
        tableValues[self._COL_SERVICES_COUNT] = tableValues.get(self._COL_SERVICES_COUNT, 0) + \
                                               (1 if serviceCode[:1] in ('G', 'V', 'S') else amount)
        tableValues[self._COL_FINISHED_EVENTS] = tableValues.get(self._COL_FINISHED_EVENTS, 0) + \
                                                 (1 if serviceCode[:1] in ('G', 'V') or
                                                       (serviceCode[:1] == 'S' and isMes) else 0)
        return tableValues

    def _serviceInfo(self, serviceId):
        if not serviceId in self._serviceInfoByServiceId:
            serviceInfo = QtGui.qApp.db.getRecord('rbService', 'infis, visitType_id', serviceId)
            self._serviceInfoByServiceId[serviceId] = (forceString(serviceInfo.value('infis')),
                                                       forceRef(serviceInfo.value('visitType_id')) is not None)
        return self._serviceInfoByServiceId[serviceId]

    def _getCostInfo(self, record, selectType):
        costInfo = None
        contractInfo = self._contractInfoMap.get(forceRef(record.value('contractId')))
        eventTypeId = forceRef(record.value('eventTypeId'))
        eventId = forceInt(record.value('eventId'))
        tariffCategoryId = forceRef(record.value('tariffCategory_id'))
        begDate = forceDate(record.value('begTreatDate'))
        endDate = forceDate(record.value('endTreatDate'))
        age = forceInt(record.value('clientAge'))
        if not contractInfo:
            return None
        if selectType == CEconomicReports._SELECT_EVENTS and \
                not eventId in self._processedIds['event']:
            serviceId = forceRef(record.value('serviceId'))
            tariffs = []
            tariffs.extend(contractInfo.tariffByEventType.get(eventTypeId, []))
            tariffs.extend(contractInfo.tariffEventByCSG.get(serviceId, []))
            tariffs.extend(contractInfo.tariffEventByMES.get((eventTypeId, serviceId), []))
            tariffs.extend(contractInfo.tariffEventByHTG.get(serviceId, []))
            tariff = None
            for testTariff in tariffs:
                if isTariffApplicable(testTariff, eventId, tariffCategoryId, endDate,
                                      mapEventIdToMKB=self._mapEventIdToMKB):
                    tariff = testTariff
                    break
            if tariff:
                tariffType = tariff.tariffType
                if tariffType == CTariff.ttEvent:
                    costInfo = {
                        'amount': 1,
                        'uet': 0.0,
                        'serviceId': getEventServiceId(eventTypeId),
                        'sum': tariff.price
                    }
                elif tariffType == CTariff.ttEventByCSG:
                    eventLength = getEventLengthDays(begDate, endDate, False, eventTypeId)
                    costInfo = {
                        'amount': int(eventLength),
                        'uet': 0.0,
                        'serviceId': serviceId,
                        'sum': self.countCoeff(begDate, endDate, record, serviceId, age, tariff, eventId, eventTypeId)
                    }
                elif tariffType in (CTariff.ttEventByMES or CTariff.ttEventByMESLen):
                    # Для данного типа isTariffApplicable изначально несколько сложнее, вохможно потребуется доработка. Хотя в Краснодаре вроде бы такой тип больше не должен использоваться.
                    amount = 1 if tariffType == CTariff.ttEventByMES else getEventLengthDays(
                        begDate, endDate, True, eventTypeId
                    )
                    amount, price, _ = tariff.evalAmountPriceSum(amount)
                    costInfo = {
                        'amount': int(amount),
                        'uet': 0.0,
                        'serviceId': serviceId,
                        'sum': round(amount * price, 2)
                    }
                elif tariffType == CTariff.ttEventByHTG:
                    amount = getEventLengthDays(begDate, endDate, False, eventTypeId)
                    costInfo = {
                        'amount': int(amount),
                        'uet': 0.0,
                        'serviceId': serviceId,
                        'sum': tariff.price
                    }
            self._processedIds['event'].append(forceInt(record.value('eventId')))
        elif selectType == CEconomicReports._SELECT_ACTIONS and \
                not forceInt(record.value('actionId')) in self._processedIds['action']:
            actionTypeId = forceRef(record.value('actionTypeId'))
            financeId = forceRef(record.value('financeId'))
            services = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
            tariff = None
            for serviceId in services:
                tariffs = contractInfo.tariffByActionService.get(serviceId, [])
                for testTariff in tariffs:
                    if isTariffApplicable(
                            testTariff,
                            eventId,
                            tariffCategoryId,
                            endDate,
                            forceStringEx(record.value('actionMKB')),
                            mapEventIdToMKB=self._mapEventIdToMKB
                    ):
                        tariff = testTariff
                        break
                # TODO: craz: В нашем оригинале на каждую услугу отдельный accountItem, после первого подходящего мы не останавливаемся.
                # Версия осс при нескольких подходящих serviceId должна вообще упасть.
                if tariff:
                    break
            if tariff:
                origAmount = forceDecimal(record.value('actionAmount'))
                amount, _, sum = tariff.evalAmountPriceSum(origAmount)
                costInfo = {
                    'amount': int(amount),
                    'uet': amount * tariff.uet if tariff.tariffType == CTariff.ttActionUET else 0.0,
                    'serviceId': serviceId,
                    'sum': sum
                }
            self._processedIds['action'].append(forceInt(record.value('actionId')))
        elif selectType == CEconomicReports._SELECT_VISITS and \
                not forceInt(record.value('visitId')) in self._processedIds['visit']:
            serviceId = forceRef(record.value('serviceId'))
            tariffs = contractInfo.tariffByVisitService.get(serviceId, [])
            tariff = None
            for testTariff in tariffs:
                if isTariffApplicable(
                        testTariff, eventId, tariffCategoryId, endDate, mapEventIdToMKB=self._mapEventIdToMKB
                ):
                    tariff = testTariff
                    break
            if tariff:
                costInfo = {
                    'amount': 1,
                    'uet': 0.0,
                    'serviceId': serviceId,
                    'sum': tariff.price
                }
            self._processedIds['visit'].append(forceInt(record.value('visitId')))

        return costInfo

    def countCoeff(self, begDate, endDate, record, serviceId, age, tariff, eventId, eventTypeId):
        curTime = QtCore.QDateTime.currentDateTime()
        db = QtGui.qApp.db

        mesId = forceInt(record.value('mesId'))
        # isUltraShort = forceBool(record.value('isUltraShort'))
        # isExtraLong = forceBool(record.value('isExtraLong'))
        eventLengthDays = getEventLengthDays(begDate, endDate, False, eventTypeId)

        stmt = """Select
                EXISTS(SELECT Action.id
                   FROM Action
                   INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                   INNER JOIN mes.mrbService ON mrbService.code = ActionType.code
                   INNER JOIN mes.MES_service ON MES_service.service_id = mrbService.id
                   WHERE Action.event_id = %s AND MES_service.master_id = %s AND MES_service.deleted = 0 AND mrbService.deleted = 0 AND Action.deleted = 0) as hasMesService,
                EXISTS(SELECT Action.id
                   FROM Action
                   INNER JOIN ActionType ON ActionType.id = Action.actionType_id
                   INNER JOIN rbService ON rbService.code = ActionType.code
                   WHERE Action.event_id = %s AND ActionType.deleted = 0 AND rbService.qualityLevel = 2) as hasComplexService""" %(eventId, mesId, eventId)
        query = db.query(stmt)
        hasMesService = False
        hasComplexService = False
        query.next()
        if forceInt(query.record().value('hasMesService')):
            hasMesService = True
        if forceInt(query.record().value('hasComplexService')):
            hasComplexService = True

        coeffCur = forceDecimal(1.03) if age < 5 and forceString(record.value('mesCode')).lower().startswith('g10') else 1

        coeffLong = 1
        coeffShort = 1

        if eventLengthDays > 30: #and isExtraLong:
            coeffLong += forceDecimal(0.2)
        if hasComplexService:
            coeffLong += forceDecimal(0.1)

        elif eventLengthDays < 3: #and not isUltraShort:
            if hasMesService:
                coeffShort = forceDecimal(0.80)
            else:
                coeffShort = forceDecimal(0.20)
        return forceDecimal(tariff.price) * forceDecimal(coeffCur * coeffLong * coeffShort)
