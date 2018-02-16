# -*- coding: utf-8 -*-
import itertools
import math
from PyQt4 import QtCore, QtGui, QtSql

from Accounting.Utils import isEventPresenceInAccounts
from Events.Action import ActionClass, ActionStatus, CAction, CActionTypeCache, CJobTicketActionPropertyValueType
from Events.ActionsModel import CActionsModel
from Events.ActionsPage import CActionsPage
from Events.ActionsSelector import getActionTypeIdListByMesId, selectActionTypes
from Events.ActionsTreeModel import CActionsTreeModel
from Events.ContractTariffCache import CContractTariffCache
from Events.EventInfo import CContractInfo, CCureMethodInfo, CCureTypeInfo, CEventCashPageInfo, CEventInfo, \
    CEventTypeInfo, CHTGInfo, CMesInfo, CMesSpecificationInfo, CPatientModelInfo, \
    CPoliclinicReferralInfo, CRecommendationInfoList, CResultInfo, CReferralInfo, CEventGoalInfo
from Events.EventJobTicketsEditor import CEventJobTicketsEditor
from Events.EventNotesPage import CFastEventNotesPage
from Events.HospitalizationTransferPage import CHospitalizationTransferPage
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils import CFinanceType, EventIsPrimary, EventOrder, checkIsHandleDiagnosisIsChecked, \
    checkTissueJournalStatusByActions, countNextDate, getAvailableCharacterIdByMKB, \
    getClosingMKBValueForAction, getClosingMorphologyValueForAction, getDeathDate, getDiagnosisPrimacy, \
    getEventActionFinance, getEventAidTypeCode, getEventContext, getEventContextData, \
    getEventControlMesNecessityEqOne, getEventFinanceId, getEventGoalFilter, getEventLengthDays, \
    getEventLittleStranger, \
    getEventMesRequired, getEventName, getEventPeriodEx, getEventPurposeId, \
    getEventServiceId, getEventShowAmountFromMes, getEventShowMedicaments, getEventShowTime, getEventShowZNO, \
    getEventTypeForm, getEventVisitFinance, getExpiredDate, getExposeConfirmation, \
    getInheritCheckupResult, getInheritResult, getMKBValueBySetPerson, getMorphologyValueBySetPerson, \
    getNeedMesPerformPercent, getTimeTableEventByPersonAndDate, isDispByMobileTeam, \
    isEventAnyActionDatePermited, recordAcceptable, specifyDiagnosis, validCalculatorSettings, getInheritGoal, \
    getEventResultId, getEventCode
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from KLADR.KLADRModel import getCityName, getDistrictName, getStreetName
from KLADR.Utils import KLADRMatch
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import COrgInfo, getOrganisationShortName, getRealOrgStructureId
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils import CBarCodeReaderThread, CCheckNetMixin, CClientInfo, CClientPolicyInfo, getClientBanner, \
    getClientCompulsoryPolicy, getClientInfo, getClientVoluntaryPolicyList, getClientWork, clientHasOncologyEvent
from Reports.Report import getEventTypeName
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin
from Users.Rights import *
from library.Counter import getDocumentNumber
from library.InDocTable import CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog
from library.LoggingModule.Logger import getLoggerDbName
from library.MES.Utils import getCmbMesType
from library.PrintInfo import CDateInfo, CDateTimeInfo, CInfoContext
from library.PrintTemplates import applyTemplate, customizePrintButton
from library.Utils import calcAgeTuple, copyFields, forceBool, forceDate, forceDateTime, forceDouble, forceInt, \
    forceRef, forceString, forceStringEx, forceTr, formatNameInt, formatSex, \
    getActionTypeIdListByMKB, getVal, toVariant
from library.constants import atcAmbulance
from library.crbcombobox import CRBModelDataCache
from library.database import addDateInRange
from library.interchange import getCheckBoxValue, getComboBoxValue, getDateEditValue, getDoubleBoxValue, \
    getRBComboBoxValue, getSpinBoxValue, setCheckBoxValue, setComboBoxValue, setDateEditValue, \
    setDoubleBoxValue, setRBComboBoxValue, setSpinBoxValue


class CEventEditDialog(CItemEditorBaseDialog, CJobTicketReserveMixin, CCheckNetMixin, CVisibleControlMixin):
    u"""базовый диалог для всех форм событий"""
    __pyqtSignals__ = ('updateActionsAmount()',
                       'updateActionsPriceAndUet()',
                       'eventEditorSetDirty(bool)',
                       )

    ctLocal = 1
    ctProvince = 2
    ctOther = 0

    saveAndCreateAccount = 2
    saveAndCreateAccountForPeriod = 3

    preDialogCheckedRightList = []
    PreDialogClass = None
    PreDagnosticAndActionPresetsClass = None

    defaultGoalByType = {}
    defaultDiagnosticResultId = {}
    defaultEventResultId = {}

    isTabMesAlreadyLoad = True
    isTabStatusAlreadyLoad = True
    isTabDiagnosticAlreadyLoad = True
    isTabCureAlreadyLoad = True
    isTabMiscAlreadyLoad = True
    isTabAmbCardAlreadyLoad = True
    isTabTempInvalidEtcAlreadyLoad = True
    isTabCashAlreadyLoad = True
    isTabNotesAlreadyLoad = True
    isTabFeedAlreadyLoaded = True

    filterDiagnosticResultByPurpose = True

    addActPrintEventCost = True

    class PrintTriggerType:
        AtOpenEvent = 0
        AtSaveEvent = 1

    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Event')
        CJobTicketReserveMixin.__init__(self)
        CCheckNetMixin.__init__(self)

        self.isVipClient = None
        self.vipColor = QtGui.QColor(255, 215, 0)
        self.orgId = None
        self.clientId = None
        self.clientSex = None
        self.clientBirthDate = None
        self.clientDeathDate = None
        self.clientAge = None
        self.clientWorkOrgId = None
        self.clientPolicyInfoList = []
        self.clientInfo = None
        self.clientType = CEventEditDialog.ctOther

        self.personId = None
        self.personSpecialityId = None
        self.personServiceId = None
        self.personFinanceId = None
        self.personTariffCategoryId = None
        self.orgStructureId = None

        self.personSSFCache = {}

        self.eventTypeId = None
        self.eventTypeName = ''
        self.eventPurposeId = None
        self.eventServiceId = None
        self.eventFinanceId = None
        self.policyId = None
        self.contractId = None
        self.eventPeriod = 0
        self.eventContext = ''
        self.eventPayStatus = None
        self.paymentSchemeItem = None
        self.mapPaymentScheme = {'universalContracts': None, 'paymentScheme': None, 'item': None}
        self.isReportEventCostPrinted = False
        self.isDispByMobileTeam = None

        self.recommendationsInfo = {}
        self.prevActionIdCache = {}
        self.modifiableDiagnosisesMap = {}  # отображение: код по МКБ -> id модифицируемого диагноза.
        self.contractTariffCache = CContractTariffCache()
        self._isCheckPresenceInAccounts = False

        self.littleStrangerId = None
        self.exposeConfirmation = False

        self._isClosedEventCheck = True

        self.saveMovingWithoutMes = False
        self.oldTemplates = {}  # Распечатанные ранее шаблоны печати и их номера. Не должны изменяться.
        self.newTemplates = {}  # Распечатанные во время текущей сессии шаблоны печати и присвоенные им номера. Подлежат сохранению.

        self.urSaveMovingWithoutMes = False

        self.accepted.connect(self.printAtSaveEventTriggered)

        # mapped trigerType (EventType_AutoPrint.triggerType)
        # to list of tuples with print template settings
        # (list of tuple (<templateId>,         -- rbPrintTemplate.id
        #                 <templateContext>,    -- rbPrintTemplate.context
        #                 <templateName>,       -- rbPrintTemplate.name
        #                 <checkData>,          -- Проверяемые данные (содержимое зависит от типы повтора у автопечати)
        #                 <masterId>,           -- EventType_AutoPrint.id
        #                 <repeatResetType>,    -- Настройка сброса счетчика повторов (0 - Не сбрасывать, 1 - Сбрасывать в указанную дату, 2 - В конце месяца
        #                 <repeatResetDate>))   -- Пользовательская дата сброса повторов.
        self.mapPrintTriggerToTemplate = {}
        self.connect(QtGui.qApp.db, QtCore.SIGNAL('disconnected()'), self.clearCaches)

        self._invisibleObjectsNameList = self.reduceNames(
            QtGui.qApp.userInfo.hiddenObjectsNameList(
                [self.moduleName()],
                True
            )
        ) if QtGui.qApp.userInfo else []
        # ==================================================
        # i3592
        if forceStringEx(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'б15' and \
                forceBool(QtGui.qApp.preferences.appPrefs.get('BarCodeReaderEnable', False)):
            if not hasattr(QtGui.qApp, 'barCodethread'):
                QtGui.qApp.barCodethread = CBarCodeReaderThread(
                    forceString(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderName', u"COM3")))
                QtGui.qApp.barCodethread.start()

            QtGui.qApp.barCodethread.barCodeReader.read.connect(self.setVerifiedAction)
            QtGui.qApp.barCodethread.barCodeReader.error.connect(self.onBarcodeReaderError)
            QtGui.qApp.barCodethread.busyByEvent = True
            # ==================================================

    @property
    def eventSetDateTime(self):
        u""" Дата-время начала обращения """
        return QtCore.QDateTime()

    @eventSetDateTime.setter
    def eventSetDateTime(self, value):
        raise NotImplementedError

    @property
    def eventDate(self):
        u""" Дата выполнения обращения """
        return QtCore.QDate()

    @eventDate.setter
    def eventDate(self, value):
        raise NotImplementedError

    @property
    def eventDateTime(self):
        u""" Дата-время выполнения обращения """
        return QtCore.QDateTime()

    @eventDateTime.setter
    def eventDateTime(self, value):
        raise NotImplementedError

    def savePreferences(self):
        preferences = super(CEventEditDialog, self).savePreferences()
        if hasattr(self, 'sptTopLevel'):
            preferences['sptTop'] = self.sptTopLevel.saveState()
        return preferences

    def loadPreferences(self, preferences):
        super(CEventEditDialog, self).loadPreferences(preferences)
        if hasattr(self, 'sptTopLevel') and 'sptTop' in preferences:
            self.sptTopLevel.restoreState(preferences['sptTop'])

    def onBarcodeReaderError(self, message):
        QtGui.QMessageBox.information(self, u'Внимание!', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def setVerifiedAction(self, result):
        if hasattr(self, 'tblActions'):
            for x in self.modelActionsSummary.items():  # self.tblActions.model().items():
                if forceString(x.value('id')) == result['action_id']:
                    if forceInt(x.value('isVerified')) == 1:
                        QtGui.QMessageBox.warning(
                            self,
                            u'Внимание!',
                            u'Услуга уже проверена.',
                            QtGui.QMessageBox.Ok,
                            QtGui.QMessageBox.Ok
                        )
                        return
                    else:
                        x.setValue('isVerified', toVariant(1))
                        QtGui.QMessageBox.information(
                            self,
                            u'Внимание!',
                            u'Услуга проверена.',
                            QtGui.QMessageBox.Ok,
                            QtGui.QMessageBox.Ok
                        )
                        return

            query = u"""
              SELECT
                EventType.name,
                Event.externalId
              FROM
                Event
                LEFT JOIN EventType ON Event.eventType_id = EventType.id
                LEFT JOIN Action ON Event.id = Action.event_id
              WHERE
                Action.id = %s
                AND Event.deleted = 0
                AND Action.deleted = 0
            """ % result['action_id']

            record = QtGui.qApp.db.getRecordEx(stmt=query)
            if record:
                QtGui.QMessageBox.information(
                    self,
                    u'Внимание!',
                    u'Данная услуга добавлена в \"%s\" %s' % (
                        forceString(record.value('name')), forceString(record.value('externalId'))
                    ),
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
                action = QtGui.qApp.db.getRecordEx(
                    'Action', '*', 'Action.id = %s AND Action.deleted = 0' % result['action_id']
                )
                action.setValue('isVerified', QtCore.QVariant(2))  # Проверено с ошибкой
                QtGui.qApp.db.insertOrUpdate('Action', action)
        pass

    @staticmethod
    def moduleName():
        return u'EventEditDialog'

    @staticmethod
    def moduleTitle():
        return u'Обращение'

    @classmethod
    def hiddableChildren(cls):
        # TODO: atronah: решить проблему с игнором смены имен в файле интерфейса
        # один из вариантов решения: парсить ui-файл
        nameList = [(u'lblNextDate', u'Cлед. явка'),
                    (u'lblGoal', u'Цель'),
                    (u'lblIBLocation', u'Местоположение И/Б (Ф.003)'),
                    (u'chkHospParent', u'Флажок "Госпитализация с родителем/представителем"'),
                    (u'tabMes', u'вкладка "%s"' % forceTr(u'Стандарт', u'Dialog'), [u'EventMesPageWidget']),
                    (u'tabMes.chkKSG', forceTr(u'КСГ', u'Dialog'), [u'cmbKSG']),
                    (u'tabMes.chkHTG', forceTr(u'ВМП', u'Dialog'), [u'cmbHTG']),
                    (u'chkHTG', forceTr(u'ВМП', u'Dialog'), [u'cmbHTG']),
                    (u'tabMes.lblMesSpecification', u'Особенности выполнения %s' % forceTr(u'МЭС', u'Dialog')),
                    (u'tabMes.btnCheckMes', u'Проверить выполнение стандарта'),
                    (u'tabMes.btnShowMes', u'Показать требования стандарта'),
                    (u'tabStatus', u'вкладка "Статус"'),
                    (u'tabDiagnostic', u'вкладка "Диагностика"'),
                    (u'tabCure', u'вкладка "Лечение"'),
                    (u'tabMisc', u'вкладка "Мероприятия"'),
                    (u'tabAnalyses', u'вкладка "Анализы"'),
                    (u'tabRecipes', u'вкладка "Льготные рецепты"'),
                    (u'tabRecommendations', u'вкладка "Рекомендации"'),
                    (u'tabReferrals', u'вкладка "Направления"'),
                    # (u'tabDestinations', u'вкладка "Лекарственные назначения"'),
                    (u'tabAmbCard', u'вкладка "Мед. карта"'),
                    (u'tabTreatmentPlan', u'вкладка "План лечения"'),
                    (u'tabTempInvalidEtc', u'вкладка "Трудоспособность"'),
                    (u'tabCash', u'вкладка "Оплата"'),
                    (u'tabFeed', u'вкладка "Питание"', [u'EventFeedPage']),
                    (u'btnSaveAndCreateAccount', u'Кнопка "Сохранить и создать счет"'),
                    (u'chkExposeConfirmed', u'Флажок "Добавить к выставлению"'),
                    (u'frDurAberr', u'Норма по МЭС/отклонение'),
                    (u'tabNotes', u'Примечания', [u'EventNotesPageWidget']),
                    # FIXME: atronah: не работает с F001, F027, F043, F106, F110
                    (u'buttonBox:Apply', u'Кнопка "Применить"')
                    ]
        return cls.normalizeHiddableChildren(nameList)

    @QtCore.pyqtSlot()
    def clearCaches(self):
        if self.__class__.defaultGoalByType:
            self.__class__.defaultGoalByType.clear()
        if self.__class__.defaultDiagnosticResultId:
            self.__class__.defaultDiagnosticResultId.clear()
        if self.__class__.defaultEventResultId:
            self.__class__.defaultEventResultId.clear()

    def moveInformationFromAnotherEvent(self, otherEventId):
        if hasattr(self, 'tblVisits'):
            # atronah: очистка посещения, добавленного при создании текущего обращения.
            self.tblVisits.model().loadItems(None)
        self.copyActionsFromOtherEvent(otherEventId)
        self.copyVisitsFromOtherEvent(otherEventId)
        self.copyDiagnosticsFromOtherEvent(otherEventId)
        self.updateCsg()

    def addNosologyInfo(self, nosologyMKB):
        db = QtGui.qApp.db
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableEvent = db.table('Event')

        queryTable = tableEvent.innerJoin(tableDiagnostic,
                                          ['%s = getEventDiagnostic(%s)' % (tableDiagnostic['id'].name(),
                                                                            tableEvent['id'].name()),
                                           tableDiagnostic['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableDiagnosis, [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                                                           tableDiagnosis['MKB'].eq(nosologyMKB)])

        begDate = self.eventSetDateTime.date() if self.eventSetDateTime else QtCore.QDate(
            QtCore.QDate.currentDate().year(), 1, 1)
        endDate = self.eventDate if self.eventDate else QtCore.QDate.currentDate()
        cond = [tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(self.clientId)]
        addDateInRange(cond, tableEvent['setDate'], begDate, endDate)

        eventIdList = db.getDistinctIdList(queryTable, idCol=tableEvent['id'], where=cond)

        if hasattr(self, 'tblVisits'):
            # atronah: очистка посещения, добавленного при создании текущего обращения.  
            self.tblVisits.model().loadItems(None)

        for eventId in eventIdList:
            self.copyActionsFromOtherEvent(eventId)
            self.copyVisitsFromOtherEvent(eventId)
            self.copyDiagnosticsFromOtherEvent(eventId)

    def copyActionsFromOtherEvent(self, otherEventId):
        if not hasattr(self, 'tblActions'):
            # return False
            if hasattr(self, 'tabMisc'):
                model = self.tabMisc.tblAPActions.model()
            elif hasattr(self, 'wdgActions'):
                model = self.wdgActions.tblAPActions.model()
            else:
                model = None

            if not model:
                return False

            db = QtGui.qApp.db

            tableAction = db.table('Action')
            actionRecordList = db.getRecordList(tableAction,
                                                where=[tableAction['event_id'].eq(otherEventId),
                                                       tableAction['deleted'].eq(0)])
            for actionRecord in actionRecordList:
                otherEventAction = CAction(record=actionRecord)
                newAction = otherEventAction.clone()
                newActionRecord = QtSql.QSqlRecord(otherEventAction.getRecord())
                newActionRecord.setValue(tableAction.idFieldName(), toVariant(None))
                newActionRecord.setValue('event_id', toVariant(self.itemId()))
                newAction.setRecord(newActionRecord)
                if isinstance(model, CActionsTreeModel):
                    model.addItems([(newAction.getType().id, newAction)])
                else:
                    model.addItem((newActionRecord, newAction))
        else:
            model = self.tblActions.model()
            if not model:
                return False

            db = QtGui.qApp.db

            tableAction = db.table('Action')
            actionRecordList = db.getRecordList(tableAction,
                                                where=[tableAction['event_id'].eq(otherEventId),
                                                       tableAction['deleted'].eq(0)])
            for actionRecord in actionRecordList:
                otherEventAction = CAction(record=actionRecord)
                newAction = otherEventAction.clone()
                newActionRecord = QtSql.QSqlRecord(otherEventAction.getRecord())
                newActionRecord.setValue(tableAction.idFieldName(), toVariant(None))
                newActionRecord.setValue('event_id', toVariant(self.itemId()))
                newAction.setRecord(newActionRecord)
                model.addAction(newAction)
            return True

    def copyVisitsFromOtherEvent(self, otherEventId):
        if not hasattr(self, 'tblVisits'):
            return False

        model = self.tblVisits.model()
        if not model:
            return False

        db = QtGui.qApp.db

        tableVisit = db.table('Visit')
        visitRecordList = db.getRecordList(tableVisit,
                                           where=[tableVisit['event_id'].eq(otherEventId),
                                                  tableVisit['deleted'].eq(0)])
        for visitRecord in visitRecordList:
            visitRecord.setValue(tableVisit.idFieldName(), QtCore.QVariant())
            visitRecord.setValue('event_id', toVariant(self.itemId()))
            model.addRecord(visitRecord)

        return True

    def copyDiagnosticsFromOtherEvent(self, otherEventId):
        modelFinalDiagnostics = self.modelDiagnostics if hasattr(self, 'modelDiagnostics') \
            else (self.modelFinalDiagnostics if hasattr(self, 'modelFinalDiagnostics') else None)
        modelPreliminaryDiagnostics = self.modelPreliminaryDiagnostics if hasattr(self,
                                                                                  'modelPreliminaryDiagnostics') else None

        if not (modelFinalDiagnostics or modelPreliminaryDiagnostics):
            return False

        db = QtGui.qApp.db
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')

        for diagnosticRecord in db.iterRecordList(tableDiagnostic, where=[tableDiagnostic['event_id'].eq(otherEventId),
                                                                          tableDiagnostic['deleted'].eq(0)]):
            diagnosisTypeId = forceRef(diagnosticRecord.value('diagnosisType_id'))
            for model in [modelFinalDiagnostics, modelPreliminaryDiagnostics]:
                if not model:
                    continue
                if hasattr(model, 'diagnosisTypeCol') and diagnosisTypeId not in model.diagnosisTypeCol.ids:
                    continue
                isDiagnosisManualSwitch = model.manualSwitchDiagnosis()
                newDiagnosticsRecord = model.getEmptyRecord()
                copyFields(newDiagnosticsRecord, diagnosticRecord)
                diagnosisId = forceRef(newDiagnosticsRecord.value('diagnosis_id'))
                if diagnosisId:
                    recDiagnosis = db.getRecord(tableDiagnosis, ['MKB', 'MKBEx', 'morphologyMKB'], diagnosisId)
                    newDiagnosticsRecord.setValue('MKB', recDiagnosis.value('MKB'))
                    newDiagnosticsRecord.setValue('MKBEx', recDiagnosis.value('MKBEx'))
                    newDiagnosticsRecord.setValue('morphologyMKB', recDiagnosis.value('morphologyMKB'))
                setDate = forceDate(newDiagnosticsRecord.value('setDate'))
                TNMS = forceString(newDiagnosticsRecord.value('TNMS'))
                newDiagnosticsRecord.setValue('TNMS', toVariant(TNMS))
                newDiagnosticsRecord.setValue('id', toVariant(self.itemId()))
                if isDiagnosisManualSwitch:
                    isCheckedHandleDiagnosis = checkIsHandleDiagnosisIsChecked(setDate,
                                                                               self.clientId,
                                                                               diagnosisId)
                    newDiagnosticsRecord.setValue('handleDiagnosis', QtCore.QVariant(isCheckedHandleDiagnosis))
                model.items().append(newDiagnosticsRecord)

        if modelFinalDiagnostics:
            modelFinalDiagnostics.reset()

        if modelPreliminaryDiagnostics:
            modelPreliminaryDiagnostics.reset()

        return True

    def setPrimacy(self):
        db = QtGui.qApp.db
        record = db.getRecordEx(table=None, stmt=u'''
                SELECT
                  e.id
                FROM
                  Event e
                WHERE
                  e.client_id = %s
                  AND e.eventType_id = %s
                  AND e.deleted = 0
            ''' % (self.clientId, self.eventTypeId)
                                )
        return not record

    def setEditable(self, editable):
        u"""
        Заглушка, переопределяется потомками
        :param editable:
        :return:
        """
        pass

    def isPrimary(self, clientId, eventTypeId, personId):
        u"""
        Проверяет на первичность.
        :param clientId: ID пациента, для которого производится проверка обращений.
        :param eventTypeId: ID типа обращений, которые стоит просматривать.
        :param personId: ID врача, специальность которого должна быть у выполневшего врача проверяемых обращений.
        :return True, если у пациента нет других обращений с тем же типом
                      и с выполневшим врачом той же специальности, что у пераданного врача.
                      ИЛИ у этих обращений не установленна дата следующей явки (Event.nextEventDate).
                Иначе False.
        """
        if QtGui.qApp.isAutoPrimacy():
            return self.setPrimacy()
        else:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tablePerson = db.table('Person')
            tableP1 = tablePerson.alias('p1')
            tableP2 = tablePerson.alias('p2')
            table = tableEvent.leftJoin(tableP1, tableP1['id'].eq(tableEvent['execPerson_id']))
            table = table.leftJoin(tableP2, tableP1['speciality_id'].eq(tableP2['speciality_id']))
            cond = [tableEvent['deleted'].eq(0),
                    tableEvent['client_id'].eq(clientId),
                    tableEvent['eventType_id'].eq(eventTypeId),
                    tableP2['id'].eq(personId),
                    ]
            record = db.getRecordEx(table, tableEvent['nextEventDate'].name(), cond,
                                    order=tableEvent['execDate'].name() + ' DESC')
            return not (record and not record.value('nextEventDate').isNull())

    def setPrimaryState(self, primaryState):
        """Устанавливает индекс первичности (Event.isPrimary).
        :param primaryState: целое число: 1-первичный, 2-повторный, 3-активное посещение, 4-перевозка (:see EventIsPrimary)
        :return: None
        """
        if hasattr(self, 'cmbPrimary'):
            if QtGui.qApp.isAutoPrimacy():
                return self.setPrimacy()
            else:
                self.cmbPrimary.setCurrentIndex(max(0, primaryState - 1))

    def primaryState(self):
        u"""Индекс первичности"""
        addOne = lambda x: x + 1
        return self.getFromViewOrRecord(
            viewPath=['cmbPrimary'],
            viewGetter=compose(addOne, method('currentIndex')),
            recordGetter=recValue('isPrimary', forceInt),
            default=EventIsPrimary.Primary)

    def setOrder(self, order):
        u"""
        Устанавливает индекс порядка наступления
        :param order: целое число: 1-плановый, 2-экстренный, 3-самотёком, 4-принудительный, 5-неотложный (@see EventOrder)
        :return:
        """
        if hasattr(self, 'cmbOrder'):
            self.cmbOrder.setCode(order)  # self.cmbOrder.setCurrentIndex(order)

    def order(self):
        u"""Индекс порядка наступления"""
        if hasattr(self, 'cmbOrder'):
            return self.cmbOrder.code()
        return EventOrder.Planned

    def setNotesEx(self, externalId, assistantId, curatorId, relegateOrgId, referrals):
        u"""Устанавливает примечания"""
        if hasattr(self, 'tabNotes') and isinstance(self.tabNotes, CFastEventNotesPage):
            self.tabNotes.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals=referrals)
            self.tabNotes.setEventEditor(self)

    def syncDates(self):
        pass

    def initFocus(self):
        u"""Передает фокус виджет, который пользователь должен редактировать первым."""
        pass

    def initMes(self):
        if hasattr(self, 'tabMes'):
            self.tabMes.setEventTypeId(self.eventTypeId)
            self.tabMes.setBegDate(self.begDate())
            self.tabMes.setEndDate(self.endDate())

    def createCsgComboBox(self):
        pass

    def createHtgComboBox(self):
        pass

    def setCsgRecord(self, record, withoutDate=False):
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setRecord(record)
            if not withoutDate:
                self.cmbCsg.setBegDate(forceDate(record.value('setDate')))
                self.cmbCsg.setEndDate(forceDate(record.value('execDate')))
                self.cmbCsg.setDefaultValue()

    def getCsgRecord(self, record):
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.getRecord(record)

    def setHtgRecord(self, record):
        if hasattr(self, 'cmbHTG') and hasattr(self, 'chkHTG'):
            setRBComboBoxValue(self.cmbHTG, record, 'HTG_id')
            if forceBool(self.cmbHTG.value()):
                self.chkHTG.setChecked(True)

    def getHtgRecord(self, record):
        if hasattr(self, 'cmbHTG') and hasattr(self, 'chkHTG'):
            if not self.chkHTG.isChecked():
                self.cmbHTG.setValue(0)
            getRBComboBoxValue(self.cmbHTG, record, 'HTG_id')

    @QtCore.pyqtSlot(bool)
    def on_chkHTG_toggled(self, checked):
        self.cmbHTG.setEnabled(checked)
        if hasattr(self, 'cmbCsg'):
            # self.cmbCsg.setEnabled(not checked)

            if checked:
                self.cmbCsg.reset()
            else:
                self.updateCsg()

    def setOrgId(self, orgId):
        u"""Устанавливает организацию"""
        self.orgId = orgId
        self.cmbContract.setOrgId(orgId)

    def orgId(self):
        u"""Возвращает id организации для текущего события"""
        return self.orgId

    def setExternalId(self, externalId):
        u"""Устанавливает значение внешнего идентификатора"""
        pass

    def begDate(self):
        return self.edtBegDate.date() if hasattr(self, 'edtBegDate') \
            else (self.eventSetDateTime.date() if self.eventSetDateTime else None)

    def endDate(self):
        return self.edtEndDate.date() if hasattr(self, 'edtEndDate') \
            else (self.eventDate if self.eventDate else QtCore.QDate())

    def endTime(self):
        return self.edtEndTime.time() if hasattr(self, 'edtEndTime') else QtCore.QTime()

    def setRecommendations(self, recommendationList):
        for record in recommendationList:
            self.recommendationsInfo[forceInt(record.value('actionType_id'))] = record

    def _prepare(self, contractId, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime,
                 includeRedDays, numDays, presetDiagnostics, presetActions, disabledActions, externalId, assistantId,
                 curatorId, movingActionTypeId=None, valueProperties=None, relegateOrgId=None, diagnos=None,
                 financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                 recommendationList=None):
        if not referrals:
            referrals = {}
        if not recommendationList:
            recommendationList = []
        self.eventSetDateTime = eventSetDatetime
        self.eventDate = eventDatetime
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(eventTypeId)
        self.setClientId(clientId)
        self.prolongateEvent = True if actionByNewEvent else False
        self.setExternalId(externalId)
        self.setPrimaryState(
            EventIsPrimary.Primary
            if self.isPrimary(clientId, eventTypeId, personId)
            else EventIsPrimary.Secondary
        )
        self.setOrder(forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder')))
        self.setContract()
        # TODO: atronah: актуально почти для всех форм (в 110 referrals передается {}, а в 027 не используется)
        self.setNotesEx(externalId, assistantId, curatorId, relegateOrgId, referrals=referrals)
        self.initFocus()
        self.setIsDirty(False)
        self.setRecommendations(recommendationList)
        self.initMes()
        if getEventTypeForm(eventTypeId) == u'003':
            if hasattr(self, 'tabNotes') and self.tabNotes.chkLPUReferral.isChecked():
                self.setOrder(1)

        return self.checkEventCreationRestriction()

    def initGoal(self):
        if hasattr(self, 'cmbGoal'):
            if self.inheritGoal:
                self.cmbGoal.setValue(self.defaultGoalByType.get(self.eventTypeId, None))
            if self.cmbGoal.currentIndex() < 0:
                self.cmbGoal.setCurrentIndex(0)

    def prepare(self, clientId, eventTypeId, orgId, personId, eventSetDatetime, eventDatetime, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, movingActionTypeId=None,
                valueProperties=None, tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, isAmb=True,
                recommendationList=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
        if not valueProperties:
            valueProperties = []
        if not actionByNewEvent:
            actionByNewEvent = []
        if not referrals:
            referrals = {}
        self.setPersonId(personId)
        self.setOrgStructureId(orgStructureId)
        plannerDate = self.getPlannerDate(eventSetDatetime, eventDatetime)

        # Если список прав пользователя, необходимых для проверки перед открытием диалога предварительных настроек, пуст  
        # или необходимые права есть у пользователя (если есть необходимые для проверке права)
        if (self.PreDialogClass is not None
            and (not self.preDialogCheckedRightList or QtGui.qApp.userHasAnyRight(self.preDialogCheckedRightList))):
            dlg = self.PreDialogClass(self,
                                      self.contractTariffCache)  # TODO: atronah: self.PreDialogClass у каждой формы свой
            dlg.prepare(clientId,
                        eventTypeId,
                        plannerDate,
                        self.personId,
                        self.personSpecialityId,
                        self.personTariffCategoryId,
                        flagHospitalization,
                        movingActionTypeId,
                        tissueTypeId,
                        recommendationList)
            if dlg.diagnosticsTableIsNotEmpty() or dlg.actionsTableIsNotEmpty():
                if not dlg.exec_():
                    return False
            result = self._prepare(
                dlg.contractId,
                clientId,
                eventTypeId,
                orgId,
                personId,
                eventSetDatetime,
                eventDatetime,
                includeRedDays,
                numDays,
                dlg.diagnostics(),
                dlg.actions(),
                dlg.disabledActionTypeIdList,
                externalId,
                assistantId,
                curatorId,
                movingActionTypeId,
                valueProperties,
                relegateOrgId,
                diagnos,
                financeId,
                protocolQuoteId,
                actionByNewEvent,
                referrals=referrals,
                isAmb=True,
                recommendationList=recommendationList
            )
            if result and dlg.contractId:
                contractFinanceId = forceRef(
                    QtGui.qApp.db.translate('Contract', 'id', dlg.contractId, 'finance_id'))
                if contractFinanceId == getEventFinanceId(eventTypeId):
                    self.cmbContract.setValue(dlg.contractId)
            return result
        else:
            presets = self.PreDagnosticAndActionPresetsClass(clientId,
                                                             eventTypeId,
                                                             plannerDate,
                                                             self.personSpecialityId,
                                                             flagHospitalization,
                                                             movingActionTypeId,
                                                             recommendationList)
            return self._prepare(None,
                                 clientId,
                                 eventTypeId,
                                 orgId,
                                 personId,
                                 eventSetDatetime,
                                 eventDatetime,
                                 includeRedDays,
                                 numDays,
                                 presets.unconditionalDiagnosticList,
                                 presets.unconditionalActionList,
                                 presets.disabledActionTypeIdList,
                                 externalId,
                                 assistantId,
                                 curatorId,
                                 movingActionTypeId,
                                 valueProperties,
                                 relegateOrgId,
                                 diagnos,
                                 financeId,
                                 protocolQuoteId,
                                 actionByNewEvent,
                                 referrals=referrals,
                                 recommendationList=recommendationList)

    def postSetupUi(self):
        self.setIsDirty(False)  # Не уверен, что это не нарушает логики или не является избыточным.
        self.createJobTicketsButton()
        self.createEpicrisButton()
        self.createAISSocLabButton()
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDefault(True)
        self.buttonBox.addButton(QtGui.QDialogButtonBox.Apply)
        self.buttonBox.clicked.connect(self.buttonBoxClicked)
        self.setLittleStrangerFlag(self.littleStrangerId)
        self.tabWidget.installEventFilter(self)
        if hasattr(self, 'cmbResult'):
            self.cmbResult.currentIndexChanged.connect(self.onCmbResultCurrentIndexChanged)
        if hasattr(self, 'cmbGoal'):
            self.cmbGoal.currentIndexChanged.connect(self.onCmbGoalCurrentIndexChanged)
        if hasattr(self, 'cmbOrder'):
            EventOrder.fillCmb(self.cmbOrder)
        self.createCsgComboBox()
        self.createHtgComboBox()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def buttonBoxClicked(self, button):
        if button == self.buttonBox.button(QtGui.QDialogButtonBox.Apply):
            if self.saveData():
                self.setRecord(QtGui.qApp.db.getRecord('Event', '*', self.itemId()))

    def markEditableTableWidget(self, widget):
        self.connect(widget, QtCore.SIGNAL('editInProgress(bool)'), self.on_editInProgress)
        self.connect(widget.model(), QtCore.SIGNAL('editInProgress(bool)'), self.on_editInProgress)

    def updateMesMKB(self):
        if hasattr(self, 'tabMes'):
            MKB = self.getFinalDiagnosisMKB()[0]
            self.tabMes.setMKB(MKB)
            MKB2List = self.getRelatedDiagnosisMKB()
            self.tabMes.setMKB2([r[0] for r in MKB2List])

            if hasattr(self, 'cmbCsg'):
                self.cmbCsg.setMKB(MKB)
                self.cmbCsg.setMKB2([r[0] for r in MKB2List])

    def updateCsg(self):
        if hasattr(self, 'tblActions'):
            items = self.tblActions.model().items()
            actionTypeIdList = [
                forceInt(item.value('actionType_id'))
                for item in items if forceInt(item.value('status')) == ActionStatus.Done
            ]
            self.setContract()
            self.updateMesMKB()

            if hasattr(self, 'tabMes'):
                self.tabMes.cmbMes.setActionTypeIdList(actionTypeIdList)
                self.tabMes.cmbMes.setBegDate(self.begDate())
                self.tabMes.cmbMes.setEndDate(self.endDate())
                self.tabMes.cmbMes.setDefaultValue()

            if hasattr(self, 'cmbCsg'):
                self.cmbCsg.fill(self.eventTypeId)
                self.cmbCsg.setActionTypeIdList(actionTypeIdList)
                self.cmbCsg.setBegDate(self.begDate())
                self.cmbCsg.setEndDate(self.endDate())
                self.cmbCsg.setDefaultValue()

    def load(self, id):
        CItemEditorBaseDialog.load(self, id)
        QtGui.qApp.openedEvents.append(id)

        # self.updateCsg()

    def on_editInProgress(self, state):
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDefault(not state)

    def createCsgComboBox(self):
        pass

    def createHtgComboBox(self):
        pass

    def createEpicrisButton(self):
        if forceBool(QtGui.qApp.preferences.appPrefs.get('enableEpircisModule', False)):
            self.btnEpicris = QtGui.QPushButton(u'Эпикризы', self)
            self.btnEpicris.setObjectName('btnEpicris')
            self.buttonBox.addButton(self.btnEpicris, QtGui.QDialogButtonBox.ActionRole)
            self.connect(self.btnEpicris, QtCore.SIGNAL('clicked()'), self.on_btnEpicris_clicked)
            self.btnEpicrisPressed = False

    def createAISSocLabButton(self):
        if forceBool(QtGui.qApp.preferences.appPrefs.get('enableSocLab', False)):
            self.btnSocLab = QtGui.QPushButton(u'АИС "Соц-Лаб"', self)
            self.btnSocLab.setObjectName('btnSocLab')
            self.buttonBox.addButton(self.btnSocLab, QtGui.QDialogButtonBox.ActionRole)
            self.connect(self.btnSocLab, QtCore.SIGNAL('clicked()'), self.on_btnSocLab_clicked)

    def createJobTicketsButton(self):
        self.btnJobTickets = QtGui.QPushButton(u'Работы', self)
        self.btnJobTickets.setObjectName('btnJobTickets')
        self.buttonBox.addButton(self.btnJobTickets, QtGui.QDialogButtonBox.ActionRole)
        self.connect(self.btnJobTickets, QtCore.SIGNAL('clicked()'), self.on_btnJobTickets_clicked)

    def createSaveAndCreateAccountButton(self):
        self.btnSaveAndCreateAccount = QtGui.QPushButton(u'Сохранить и создать счёт', self)
        self.btnSaveAndCreateAccount.setObjectName('btnSaveAndCreateAccount')

    # i3838 don't delete
    # def createSignGrkmCardButton(self):
    #     if forceBool(QtGui.qApp.preferences.appPrefs.get('GRKMService', False)):
    #         self.addObject('btnSignGrkmCard', QtGui.QPushButton(u'Подписать', self))
    #         self.buttonBox.addButton(self.btnSignGrkmCard, QtGui.QDialogButtonBox.ActionRole)
    #         self.connect(self.btnSignGrkmCard, QtCore.SIGNAL('clicked()'), self.on_btnSignGrkmCard_clicked)

    def setupSaveAndCreateAccountButton(self):
        if hasattr(self, 'btnSaveAndCreateAccount'):
            self.buttonBox.addButton(self.btnSaveAndCreateAccount, QtGui.QDialogButtonBox.ActionRole)

    def setupSaveAndCreateAccountForPeriodButton(self):
        if hasattr(self, 'btnSaveAndCreateAccountForPeriod'):
            self.buttonBox.addButton(self.btnSaveAndCreateAccountForPeriod, QtGui.QDialogButtonBox.ActionRole)

    def setupSignGrkmCardButton(self):
        pass

    def setupActionSummarySlots(self):
        self.connect(self.modelActionsSummary, QtCore.SIGNAL('currentRowMovedTo(int)'),
                     self.onActionsSummaryCurrentRowMovedTo)
        self.connect(self.modelActionsSummary, QtCore.SIGNAL('currentRowMovedToWithActionTypeClass(int,int)'),
                     self.onActionsSummaryCurrentRowMovedToWithActionTypeClass)

    def exec_(self):
        QtGui.qApp.setJTR(self)

        self.printAtOpenEventTriggered()
        self.updateVisibleState(self, self._invisibleObjectsNameList)
        result = CItemEditorBaseDialog.exec_(self)

        if not result:
            self.delAllJobTicketReservations()
        QtGui.qApp.setJTR(None)

        if self.itemId():
            QtGui.qApp.addMruEvent(self.itemId(), self.getMruDescr())
        if result == self.saveAndCreateAccount:
            try:
                # findme
                from Accounting.InstantAccountDialog import createInstantAccount
                createInstantAccount(self.itemId())
            except:
                QtGui.qApp.logCurrentException()
        elif result == self.saveAndCreateAccountForPeriod:
            try:
                from Accounting.InstantAccountDialog import createInstantAccountForPeriod
                createInstantAccountForPeriod(self.itemId(), self.getEventTypeId(), self.clientId)
            except:
                QtGui.qApp.logCurrentException()
        QtGui.qApp.disconnectClipboard()
        if self.itemId() in QtGui.qApp.openedEvents:
            QtGui.qApp.openedEvents.remove(self.itemId())
        return result

    def restrictToPayment(self):
        if hasattr(self, 'tabCash'):
            tabCashIndex = self.tabWidget.indexOf(self.tabCash)
            tabNotesIndex = self.tabWidget.indexOf(self.tabNotes) if hasattr(self, 'tabNotes') else -1
            for i in xrange(self.tabWidget.count()):
                if i != tabCashIndex and i != tabNotesIndex:
                    self.tabWidget.setTabEnabled(i, False)
            self.tabWidget.setCurrentIndex(tabCashIndex)
            self.tabCash.tabCach.setCurrentIndex(1)
            return True
        else:
            return False

    def onActionsSummaryCurrentRowMovedTo(self, row):
        self.setFocusToWidget(self.tblActions, row, 0)

    def onActionsSummaryCurrentRowMovedToWithActionTypeClass(self, row, actionTypeClass):
        return

    def setLittleStrangerFlag(self, littleStrangerId):
        if hasattr(self, 'gbLittleStrangerFlag'):
            db = QtGui.qApp.db
            tableEventLittleStranger = db.table('Event_LittleStranger')

            self.gbLittleStrangerFlag.setChecked(bool(littleStrangerId))
            self.gbLittleStrangerFlag.toggled.emit(bool(littleStrangerId))

            if self.littleStrangerId:
                db.deleteRecord(tableEventLittleStranger, tableEventLittleStranger['id'].eq(littleStrangerId))

            if littleStrangerId:
                self.littleStrangerId = littleStrangerId
                record = db.getRecord(tableEventLittleStranger, '*', self.littleStrangerId)
                setDateEditValue(self.edtChildBirthDate, record, 'birthDate')
                setSpinBoxValue(self.sbChildNumber, record, 'currentNumber')
                setComboBoxValue(self.cmbChildSex, record, 'sex')
                setCheckBoxValue(self.chkMultipleBirths, record, 'multipleBirths')
                setDoubleBoxValue(self.sbBirthWeight, record, 'birthWeight')
            else:
                self.littleStrangerId = None

    def getLittleStrangerFlagId(self):
        if hasattr(self, 'gbLittleStrangerFlag'):
            db = QtGui.qApp.db
            tableEventLittleStranger = db.table('Event_LittleStranger')
            if self.gbLittleStrangerFlag.isChecked():
                record = db.getRecord(tableEventLittleStranger, '*', self.littleStrangerId)
                if not record:
                    record = tableEventLittleStranger.newRecord()

                getDateEditValue(self.edtChildBirthDate, record, 'birthDate')
                getSpinBoxValue(self.sbChildNumber, record, 'currentNumber')
                getComboBoxValue(self.cmbChildSex, record, 'sex')
                getCheckBoxValue(self.chkMultipleBirths, record, 'multipleBirths')
                getDoubleBoxValue(self.sbBirthWeight, record, 'birthWeight')

                self.littleStrangerId = db.insertOrUpdate(tableEventLittleStranger, record)

                return forceRef(record.value(tableEventLittleStranger.idFieldName()))
            else:
                if self.littleStrangerId:
                    db.deleteRecord(tableEventLittleStranger, tableEventLittleStranger['id'].eq(self.littleStrangerId))
        return None

    def realClientSex(self):
        if hasattr(self, 'gbLittleStrangerFlag') and self.gbLittleStrangerFlag.isChecked():
            return self.cmbChildSex.currentIndex()
        return self.clientSex

    def realClientBirthDate(self):
        if hasattr(self, 'gbLittleStrangerFlag') and self.gbLittleStrangerFlag.isChecked():
            return self.edtChildBirthDate.date()
        return self.clientBirthDate

    def realClientAge(self):
        birthDate = self.realClientBirthDate()
        return calcAgeTuple(birthDate, self.eventSetDateTime) if birthDate else self.clientAge

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtChildBirthDate_dateChanged(self, date):
        if hasattr(self, 'tabMes'):
            self.tabMes.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)

    @QtCore.pyqtSlot(int)
    def on_cmbChildSex_currentIndexChanged(self, index):
        if hasattr(self, 'tabMes'):
            self.tabMes.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)

    @QtCore.pyqtSlot(int)
    def on_gbLittleStrangerFlag_toggled(self, state):
        if hasattr(self, 'tabMes'):
            self.tabMes.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)

    @QtCore.pyqtSlot(int)
    def on_cmbGoal_currentIndexChanged(self, index):
        if getEventGoalFilter(self.eventTypeId) and hasattr(self, 'tblVisits'):
            visits = self.tblVisits.model().items()
            services = [forceRef(record.value('service_id')) for record in visits]
            if None in services:
                services.remove(None)
            if services:
                QtGui.QMessageBox.warning(self, u'Внимание',
                                          u'В посещениях существуют услуги, связанные с другой целью события.',
                                          QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def _addActionPrintEventCost(self):
        if hasattr(self, 'btnPrint') and QtGui.qApp.defaultKLADR().startswith('78') and self.addActPrintEventCost:
            self.actPrintEventCost = QtGui.QAction(u'Справка о стоимости', self)
            self.actPrintEventCost.setObjectName('actPrintEventCost')
            self.btnPrint.addAction(self.actPrintEventCost)
            self.actPrintEventCost.triggered.connect(self.on_actPrintEventCost_triggered)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        orgId = forceRef(record.value('org_id'))
        self.setOrgId(orgId if orgId else QtGui.qApp.currentOrgId())
        self.setEventTypeId(forceRef(record.value('eventType_id')))
        self.isReportEventCostPrinted = forceBool(record.value('eventCostPrinted'))
        self._addActionPrintEventCost()
        self.eventSetDateTime = forceDateTime(record.value('setDate'))
        self.eventDate = forceDate(record.value('execDate'))
        self.setLittleStrangerFlag(forceRef(record.value('littleStranger_id')))
        self.setClientId(forceRef(record.value('client_id')))
        self.setClientPolicyId(forceRef(record.value('clientPolicy_id')))
        self.setContractId(forceRef(record.value('contract_id')))
        self.setOrgStructureId(forceRef(record.value('orgStructure_id')))
        if hasattr(self, 'chkExposeConfirmed'):
            self.chkExposeConfirmed.setChecked(forceBool(record.value('exposeConfirmed')))
        if hasattr(self, 'chkHospParent'):
            self.chkHospParent.setChecked(forceBool(record.value('hospParent')))
        if hasattr(self, 'chkDispByMobileTeam') and QtGui.qApp.region() == '23':
            self.chkDispByMobileTeam.setChecked(forceBool(record.value('dispByMobileTeam')))
            self.chkDispByMobileTeam.setVisible(self.isDispByMobileTeam)

        self.loadOldTemplates(record)

        if hasattr(self, 'edtPregnancyWeek'):
            self.edtPregnancyWeek.setValue(forceInt(record.value('pregnancyWeek')))
        if hasattr(self, 'cmbGoal'):
            setRBComboBoxValue(self.cmbGoal, record, 'goal_id')
            if self.cmbGoal.currentIndex() < 0:
                self.initGoal()
        if hasattr(self, 'chkZNOFirst'):
            self.chkZNOFirst.setChecked(forceBool(record.value('ZNOFirst')))
        if hasattr(self, 'chkZNOMorph'):
            self.chkZNOMorph.setChecked(forceBool(record.value('ZNOMorph')))
            self.setZNOMorphEnabled(forceString(record.value('externalId')))
        if hasattr(self, 'chkIsClosed'):
            self.chkIsClosed.setChecked(forceBool(record.value('isClosed')))
            if not QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)) \
                    and self.chkIsClosed.isChecked() \
                    and hasattr(self.tabNotes, 'chkLock'):
                self.tabNotes.chkLock.setEnabled(False)
                self.tabNotes.lblLock.setEnabled(False)
        self.updatePrintTriggerMap()
        if hasattr(self, 'cmbOrder'):
            EventOrder.fillCmb(self.cmbOrder)
        # if hasattr(self, 'cmbCsg'):
        #     self.cmbCsg.setRecord(record)
        self.setCsgRecord(record, True)
        self.setHtgRecord(record)

    # Вызов setEditable перенесен в дочерние классы, так как для корректной работы требуется либо
    # инициализированный cmbPerson, либо передача нужных данных в getEditable иным способом.
    # self.setEditable(self.getEditable()) #atronah: getEditable может использовать self.eventPayStatus,
    # поэтому он должен быть к этому моменту обновлен.
    # Загрузка ранее распечатанных шаблонов печати, требующих учета (однажны распечатанномму шаблону присваивается
    # некое значение счетчика, неизменное в пределах текущего обращения)
    def loadOldTemplates(self, record):
        self.oldTemplates = {}
        recordList = QtGui.qApp.db.getRecordList('Event_PrintTemplateCounter', 'template_id, counterValue',
                                                 'deleted = 0 AND event_id = %s' % forceInt(record.value('id')))
        for record in recordList:
            templateId = forceRef(record.value('template_id'))
            counterValue = forceString(record.value('counterValue'))
            self.oldTemplates[templateId] = counterValue

    def saveNewTemplates(self, eventId):
        db = QtGui.qApp.db
        table = db.table('Event_PrintTemplateCounter')
        for templateId, counterValue in self.newTemplates.items():
            record = table.newRecord()
            record.setValue('event_id', QtCore.QVariant(eventId))
            record.setValue('template_id', QtCore.QVariant(templateId))
            record.setValue('counterValue', QtCore.QVariant(counterValue))
            db.insertOrUpdate(table, record)
        self.oldTemplates.update(self.newTemplates)
        self.newTemplates = {}

    def getEventPayStatus(self):
        payStatus = 0
        if self.eventPayStatus:
            return self.eventPayStatus
        return payStatus

    def getEditable(self):
        editable = True
        if self.itemId() and hasattr(self, 'cmbPerson') \
                and self.cmbPerson.value() == QtGui.qApp.userId and self.endDate() != QtCore.QDate() \
                and not QtGui.qApp.userHasRight(urEditOwnEvents):
            editable = False
        if self.itemId() and hasattr(self, 'cmbPerson') and self.cmbPerson.value() != QtGui.qApp.userId:
            editable = editable and QtGui.qApp.userHasRight(urEditNotOwnEvents)

        if self._isCheckPresenceInAccounts:
            allowEditing = not isEventPresenceInAccounts(forceRef(self._record.value('id')))
            editable = editable and (allowEditing or QtGui.qApp.userHasRight(urEditPayedEvents))

        if QtGui.qApp.isEventLockEnabled() and not QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)):
            editable = editable and not forceBool(self._record.value('locked'))  # eventlock
        return editable

    def checkEventCreationRestriction(self):
        if QtGui.qApp.isRestrictedEventCreationByContractPresence() and self.cmbContract.value() is None:
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Обслуживание пациента запрещено, так как нельзя подобрать договор',
                                       QtGui.QMessageBox.Close)
            return False
        return True

    def getRecord(self):
        if not self.record():
            record = CItemEditorBaseDialog.getRecord(self)
            record.setValue('eventType_id', toVariant(self.eventTypeId))
            record.setValue('org_id', toVariant(self.orgId))
            record.setValue('client_id', toVariant(self.clientId))
            record.setValue('isPrimary', QtCore.QVariant(self.primaryState()))
            record.setValue('order', QtCore.QVariant(self.order()))
            record.setValue('setDate', QtCore.QVariant(self.eventSetDateTime))
            record.setValue('contract_id', QtCore.QVariant(self.contractId))
            record.setValue('orgStructure_id', QtCore.QVariant(self.orgStructureId))
        else:
            record = self.record()
        record.setValue('eventCostPrinted', QtCore.QVariant(self.isReportEventCostPrinted))
        if hasattr(self, 'edtPregnancyWeek'):
            record.setValue('pregnancyWeek', QtCore.QVariant(self.edtPregnancyWeek.value()))
        if hasattr(self, 'gbLittleStrangerFlag'):
            record.setValue('littleStranger_id', toVariant(self.getLittleStrangerFlagId()))
        if hasattr(self, 'chkExposeConfirmed'):
            record.setValue('exposeConfirmed', toVariant(self.chkExposeConfirmed.isChecked()))
        if hasattr(self, 'chkHospParent'):
            record.setValue('hospParent', toVariant(self.chkHospParent.isChecked()))
        if hasattr(self, 'chkDispByMobileTeam') and QtGui.qApp.region() == '23':
            record.setValue('dispByMobileTeam', toVariant(self.chkDispByMobileTeam.isChecked()))
        if hasattr(self, 'cmbGoal'):
            getRBComboBoxValue(self.cmbGoal, record, 'goal_id')
            self.defaultGoalByType[self.eventTypeId] = self.cmbGoal.value()
        if hasattr(self, 'cmbResult') and self.cmbResult.value():
            self.defaultEventResultId[self.eventPurposeId] = self.cmbResult.value()
            self.updateAttachAndSocStatus()
        diagnostics = None
        if hasattr(self, 'modelFinalDiagnostics'):
            diagnostics = self.modelFinalDiagnostics
        elif hasattr(self, 'modelDiagnostics'):
            diagnostics = self.modelDiagnostics
        if diagnostics and hasattr(diagnostics, 'resultId'):
            self.defaultDiagnosticResultId[self.eventPurposeId] = diagnostics.resultId()
        if hasattr(self, 'chkZNOFirst'):
            record.setValue('ZNOFirst', QtCore.QVariant(self.chkZNOFirst.isChecked()))
        if hasattr(self, 'chkZNOMorph'):
            record.setValue('ZNOMorph', QtCore.QVariant(self.chkZNOMorph.isChecked() and self.chkZNOMorph.isEnabled()))
        if hasattr(self, 'tabMes'):
            self.tabMes.getRecord(record)

        self.getCsgRecord(record)
        self.getHtgRecord(record)
        if hasattr(self, 'chkIsClosed'):
            record.setValue('isClosed', QtCore.QVariant(self.chkIsClosed.isChecked()))
            record.setValue('locked', QtCore.QVariant(self.chkIsClosed.isChecked()))
        try:
            if not self.endDate().isNull() and not self.begDate().isNull():
                record.setValue('duration', QtCore.QVariant(self.begDate().daysTo(self.endDate())))
        except:
            pass
        return record

    def updateAttachAndSocStatus(self):
        if hasattr(self, 'cmbResult') and self.cmbResult.value() and not self.edtEndDate.date().isNull():
            db = QtGui.qApp.db
            tblResult = db.table('rbResult')
            recResult = db.getRecordEx(tblResult, '*', tblResult['id'].eq(self.cmbResult.value()))
            if recResult:
                if forceInt(recResult.value('attachType')):
                    tblClientAttach = db.table('ClientAttach')
                    recAttach = db.getRecordEx(
                        tblClientAttach,
                        tblClientAttach['id'],
                        [
                            tblClientAttach['attachType_id'].eq(forceInt(recResult.value('attachType'))),
                            tblClientAttach['client_id'].eq(self.clientId)
                        ]
                    )
                    if not recAttach:
                        newAttach = tblClientAttach.newRecord()
                        newAttach.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                        newAttach.setValue('client_id', toVariant(self.clientId))
                        newAttach.setValue('attachType_id', toVariant(forceInt(recResult.value('attachType'))))
                        newAttach.setValue('LPU_id', toVariant(QtGui.qApp.currentOrgId()))
                        newAttach.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                        newAttach.setValue('endDate', toVariant(self.edtEndDate.date()))
                        db.insertRecord(tblClientAttach, newAttach)
                if forceInt(recResult.value('socStatusClass')) and forceInt(recResult.value('socStatusType')):
                    tblClientSocStatus = db.table('ClientSocStatus')
                    recSocStatus = db.getRecordEx(
                        tblClientSocStatus,
                        tblClientSocStatus['id'],
                        [
                            tblClientSocStatus['client_id'].eq(self.clientId),
                            tblClientSocStatus['socStatusClass_id'].eq(forceInt(recResult.value('socStatusClass'))),
                            tblClientSocStatus['socStatusType_id'].eq(forceInt(recResult.value('socStatusType')))
                        ]
                    )
                    if not recSocStatus:
                        newClientSocStatus = tblClientSocStatus.newRecord()
                        newClientSocStatus.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                        newClientSocStatus.setValue('client_id', toVariant(self.clientId))
                        newClientSocStatus.setValue(
                            'socStatusClass_id', toVariant(forceInt(recResult.value('socStatusClass')))
                        )
                        newClientSocStatus.setValue(
                            'socStatusType_id', toVariant(forceInt(recResult.value('socStatusType')))
                        )
                        newClientSocStatus.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                        newClientSocStatus.setValue('endDate', toVariant(self.edtEndDate.date()))
                        db.insertRecord(tblClientSocStatus, newClientSocStatus)

    def updateModelsRetiredList(self):
        if hasattr(self, 'modelVisits'): self.modelVisits.updateRetiredList()
        if hasattr(self, 'modelActionsSummary'): self.modelActionsSummary.updateRetiredList()
        if hasattr(self, 'modelDiagnostics'): self.modelDiagnostics.updateRetiredList()
        if hasattr(self, 'modelFinalDiagnostics'): self.modelFinalDiagnostics.updateRetiredList()
        if hasattr(self, 'modelPreliminaryDiagnostics'): self.modelPreliminaryDiagnostics.updateRetiredList()
        if hasattr(self, 'modelPersonnel'): self.modelPersonnel.updateRetiredList()

    def updateRecommendations(self):
        def getAllRecommendationsMap():
            cond = db.joinAnd([
                tableRecommendation['setEvent_id'].inInnerStmt(db.selectStmt(
                    tableEvent,
                    tableEvent['id'],
                    tableEvent['client_id'].eq(self.clientId))),
                tableRecommendation['amount_left'].gt(0.0),
                tableRecommendation['expireDate'].dateLe(QtCore.QDate.currentDate())
            ])
            return dict((forceInt(rec.value('actionType_id')), rec)
                        for rec in db.iterRecordList(tableRecommendation, where=cond))

        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableRecommendation = db.table('Recommendation')
        tableRecommendationAction = db.table('Recommendation_Action')
        allRecommendationsMap = getAllRecommendationsMap()
        actions = self.getActionsModelsItemsList()
        for actionRecord, action in actions:
            actualActionTypeId = forceInt(actionRecord.value('actionType_id'))
            actionId = forceInt(actionRecord.value('id'))
            actionTypeIdList = [actualActionTypeId]
            actionTypeIdList.extend(db.getDistinctIdList('rbActionTypeSimilarity', 'firstActionType_id',
                                                         ['secondActionType_id=%s' % actualActionTypeId,
                                                          'similarityType=1']))
            actionTypeIdList.extend(db.getDistinctIdList('rbActionTypeSimilarity', 'secondActionType_id',
                                                         ['firstActionType_id=%s' % actualActionTypeId,
                                                          'similarityType=1']))
            for actionTypeId in actionTypeIdList:
                if actionTypeId in self.recommendationsInfo or actionTypeId in allRecommendationsMap:
                    if actionTypeId in self.recommendationsInfo:
                        recRecord = self.recommendationsInfo[actionTypeId]
                    else:
                        recRecord = allRecommendationsMap[actionTypeId]

                    amountLeft = forceDouble(recRecord.value('amount_left'))
                    amountAction = forceDouble(actionRecord.value('amount'))
                    amountRec = min(amountLeft, amountAction)
                    recRecord.setValue('amount_left', toVariant(amountLeft - amountRec))
                    recActionRecord = tableRecommendationAction.newRecord()
                    recActionRecord.setValue('recommendation_id', recRecord.value('id'))
                    recActionRecord.setValue('action_id', toVariant(actionId))
                    recActionRecord.setValue('amount', toVariant(amountRec))
                    recActionRecord.setValue('execDate', toVariant(QtCore.QDate.currentDate()))
                    db.updateRecord(tableRecommendation, recRecord)
                    db.insertRecord(tableRecommendationAction, recActionRecord)
                    break

    def saveInternals(self, eventId):
        self.saveNewTemplates(eventId)

    def afterSave(self):
        CItemEditorBaseDialog.afterSave(self)
        self.checkTissueJournalStatusByActions()
        self.modifiableDiagnosisesMap = {}
        if hasattr(self, 'tabRecipes'):
            self.tabRecipes.sendRecipes()
        if hasattr(self, 'tabNotes') and self.tabNotes.chkLPUReferral.isChecked():
            record = self.getRecord()
            if forceInt(record.value('id')):
                self.tabNotes.getNotes(record, forceInt(record.value('eventType_id')))


    def checkTissueJournalStatusByActions(self):
        actionsModelsItemsList = self.getActionsModelsItemsList()
        checkTissueJournalStatusByActions(actionsModelsItemsList)

    def getActionsTabsList(self):
        actionsTabsList = []
        if hasattr(self, 'tabActions'):
            actionsTabsList.append(self.tabActions)
        else:
            if hasattr(self, 'tabStatus'):
                actionsTabsList.append(self.tabStatus)
            if hasattr(self, 'tabDiagnostic'):
                actionsTabsList.append(self.tabDiagnostic)
            if hasattr(self, 'tabCure'):
                actionsTabsList.append(self.tabCure)
            if hasattr(self, 'tabMisc'):
                actionsTabsList.append(self.tabMisc)
            if hasattr(self, 'tabAnalyses'):
                actionsTabsList.append(self.tabAnalyses)
        return actionsTabsList

    def getActionsTabMap(self):
        tabNameMap = {
            ActionClass.Status: 'tabStatus',
            ActionClass.Diagnostic: 'tabDiagnostic',
            ActionClass.Cure: 'tabCure',
            ActionClass.Misc: 'tabMisc',
            ActionClass.Analyses: 'tabAnalyses'
        }
        return dict((cl, getattr(self, tabName))
                    for cl, tabName in tabNameMap.iteritems() if hasattr(self, tabName))

    def getActionsModelsItemsList(self, filter=None):
        actionsModelsItemsList = []
        for actionsTab in self.getActionsTabsList():
            items = filter(actionsTab.modelAPActions.items()) if filter else actionsTab.modelAPActions.items()
            actionsModelsItemsList.extend(items)
        return actionsModelsItemsList

    def checkNeedLaboratoryCalculator(self, propertyTypeList, clipboardSlot):
        actualPropertyTypeList = [propType for propType in propertyTypeList if
                                  validCalculatorSettings(propType.laboratoryCalculator)]
        if actualPropertyTypeList:
            QtGui.qApp.connectClipboard(clipboardSlot)
        else:
            QtGui.qApp.disconnectClipboard()
        return actualPropertyTypeList

    def setEventTypeId(self, eventTypeId, title='', titleF003=''):
        self.eventTypeId = eventTypeId

        if hasattr(self, 'cmbOrder'):
            self.cmbOrder.setCode(
                forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'defaultOrder'))
            )

        self.eventTypeName = getEventName(eventTypeId)
        self.eventPurposeId = getEventPurposeId(eventTypeId)
        self.eventServiceId = getEventServiceId(eventTypeId)
        self.eventPeriod = getEventPeriodEx(eventTypeId)
        self.eventContext = getEventContext(eventTypeId)
        self.mesRequired = getEventMesRequired(eventTypeId)
        self.inheritResult = getInheritResult(eventTypeId)
        self.inheritCheckupResult = getInheritCheckupResult(eventTypeId)
        self.inheritGoal = getInheritGoal(eventTypeId)
        self.showAmountFromMes = None
        self.showAmountFromMes = getEventShowAmountFromMes(eventTypeId)
        self.showMedicaments = getEventShowMedicaments(eventTypeId)
        self.controlMesNecessityEqOne = getEventControlMesNecessityEqOne(eventTypeId)
        self.showLittleStranger = getEventLittleStranger(eventTypeId)
        self.exposeConfirmation = getExposeConfirmation(eventTypeId)
        self.showZNO = getEventShowZNO(self.eventTypeId)
        self.isDispByMobileTeam = isDispByMobileTeam(eventTypeId)

        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.fill(eventTypeId)
            if not self.mesRequired:
                self.lblCsg.setVisible(False)
                self.cmbCsg.setVisible(False)

        if hasattr(self, 'cmbContract'):
            self.cmbContract.setEventTypeId(eventTypeId)
        orgName = getOrganisationShortName(self.orgId)
        eventPurposeName = forceString(QtGui.qApp.db.translate('rbEventTypePurpose', 'id', self.eventPurposeId, 'name'))
        self.setWindowTitle(u'%s %s %s - %s: %s' % (title, orgName, titleF003, eventPurposeName, self.eventTypeName))
        if hasattr(self, 'tabMes'):
            if self.mesRequired:
                self.tabMes.setEventTypeId(eventTypeId)
                self.tabMes.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
                self.setContract()
            else:
                self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tabMes), False)
        if hasattr(self, 'tabNotes'):
            self.tabNotes.enableEditors(self.eventTypeId)
        if hasattr(self, 'tblActions') and not hasattr(self, 'actDialogAPActionsAdd'):
            if title != u'Ф.001':
                self.actDialogAPActionsAdd = QtGui.QAction(u'Добавить ...', self)
                self.actDialogAPActionsAdd.setObjectName('actDialogAPActionsAdd')
                self.actDialogAPActionsAdd.setShortcut(QtCore.Qt.Key_F9)
                self.mnuAction.addAction(self.actDialogAPActionsAdd)
                self.connect(self.actDialogAPActionsAdd, QtCore.SIGNAL('triggered()'),
                             self.on_actDialogAPActionsAdd_triggered)
        if hasattr(self, 'gbLittleStrangerFlag'):
            self.gbLittleStrangerFlag.setVisible(self.showLittleStranger)
        if hasattr(self, 'cmbGoal'):
            self.cmbGoal.setTable('rbEventGoal', True, 'eventTypePurpose_id=\'%d\'' % self.eventPurposeId)
            if not self.cmbGoal.value():
                self.cmbGoal.setCurrentIndex(0)
        if hasattr(self, 'chkExposeConfirmed'):
            self.chkExposeConfirmed.setVisible(self.exposeConfirmation)
        if hasattr(self, 'chkZNOFirst'):
            self.chkZNOFirst.setVisible(self.showZNO)
        if hasattr(self, 'chkZNOMorph'):
            self.chkZNOMorph.setVisible(self.showZNO)

        if hasattr(self, 'tabWidget') and getEventCode(eventTypeId) == '04':
            self.tabHospitalizationTransfer = CHospitalizationTransferPage(self, self.itemId())
            self.tabHospitalizationTransfer.setObjectName('tabHospitalizationTransfer')
            self.tabWidget.addTab(self.tabHospitalizationTransfer, u'Причины переноса госпитализации')

    @staticmethod
    def setVisitAssistantVisible(table, visible):
        model = table.model()
        model.hasAssistant = visible
        table.setColumnHidden(model.getColIndex('assistant_id'), not visible)

    @staticmethod
    def getPlannerDate(eventSetDatetime, eventDatetime):
        if QtGui.qApp.getClientAgeOnEventSetDate():
            plannerDatetime = eventSetDatetime or eventDatetime or QtCore.QDate.currentDate()
        else:
            plannerDatetime = eventDatetime or eventSetDatetime or QtCore.QDate.currentDate()
        return plannerDatetime.date() if isinstance(plannerDatetime, QtCore.QDateTime) else plannerDatetime

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if key == QtCore.Qt.Key_F9 and hasattr(self, 'tabWidget'):
            widget = self.tabWidget.currentWidget()
            cond = []
            if hasattr(self, 'tabToken'):
                cond.append(self.tabToken)
            if hasattr(self, 'tabMes'):
                cond.append(self.tabMes)
            if hasattr(self, 'tabRecommendations'):
                cond.append(self.tabRecommendations)
            if widget in cond and event.type() == QtCore.QEvent.KeyPress:
                if hasattr(self, 'tabRecommendations') and widget == self.tabRecommendations:
                    self.addRecommendations()
                else:
                    self.on_actDialogAPActionsAdd_triggered()
        elif modifiers == QtCore.Qt.ControlModifier:
            numericKeys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                           QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, QtCore.Qt.Key_9]
            if key == QtCore.Qt.Key_Tab:
                index = self.tabWidget.currentIndex()
                lastIndex = self.tabWidget.count() - 1
                nextIndexFound = False
                nextIndex = index
                while not nextIndexFound:
                    if nextIndex == lastIndex:
                        nextIndex = 0
                    else:
                        nextIndex += 1
                    if self.tabWidget.isTabEnabled(nextIndex) or nextIndex == index:
                        nextIndexFound = True
                self.tabWidget.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.TabFocusReason)

            elif key in numericKeys:
                nextIndex = int(event.text()) - 1
                if nextIndex <= self.tabWidget.count() and self.tabWidget.isTabEnabled(nextIndex):
                    self.tabWidget.setCurrentIndex(nextIndex)
                    self.setFocus(QtCore.Qt.OtherFocusReason)
            elif key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                self.accept()
            elif key == QtCore.Qt.Key_0:
                self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)
                self.setFocus(QtCore.Qt.TabFocusReason)
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if key == QtCore.Qt.Key_Backtab:
                index = self.tabWidget.currentIndex()
                lastIndex = self.tabWidget.count() - 1
                nextIndexFound = False
                nextIndex = index
                while not nextIndexFound:
                    if nextIndex == 0:
                        nextIndex = lastIndex
                    else:
                        nextIndex -= 1
                    if self.tabWidget.isTabEnabled(nextIndex) or nextIndex == index:
                        nextIndexFound = True
                self.tabWidget.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.BacktabFocusReason)

        CItemEditorBaseDialog.keyPressEvent(self, event)

    def eventFilter(self, object, event):
        if type(event) == QtGui.QKeyEvent:
            key = event.key()
            modifiers = event.modifiers()
            numericKeys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                           QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, QtCore.Qt.Key_9, QtCore.Qt.Key_0]
            if (modifiers == QtCore.Qt.ControlModifier and (key == QtCore.Qt.Key_Tab or key in numericKeys)) \
                    or (modifiers == (
                                QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier) and key == QtCore.Qt.Key_Backtab):
                self.keyPressEvent(event)
                return True
        return False

    def getEventTypeId(self):
        return self.eventTypeId

    def getEventPurposeId(self):
        return self.eventPurposeId

    def getFromViewOrRecord(self, viewPath, viewGetter, recordGetter, default=None):
        u"""
        Gets a value from (possibly nested) widget or, if the specified widget is not present,
        tries to get it from 'self.record()'.

        :param viewPath: path from 'self' to needed widget.
                        e.g. for 'self.tabNotes.btnPrint' viewPath would be
                        '["tabNotes","btnPrint"]' (@see getAttrFromPathIfExists).
        :param viewGetter: a function of type 'widget -> value', it accepts a widget and returns a final value
        :param recordGetter: function to get a value from a record

        # Here is the diff of 'EventEditDialog.getNote' for further clarity::
         def getNote(self):
        -    if hasattr(self, 'tabNotes'):
        -        return self.tabNotes.edtEventNote.toPlainText()
        -    if self.record():
        -        return forceString(self.record().value('note'))
        -    return ''
        +    return self.getFromViewOrRecord(
        +            viewPath     = ['tabNotes', 'edtEventNote'],
        +            viewGetter   = method('toPlainText'),
        +            recordGetter = recValue('note', forceString),
        +            default      = '')
        """
        exists, view = getAttrFromPathIfExists(self, viewPath)
        if exists:
            return viewGetter(view)
        if self.record():
            return recordGetter(self.record())
        return default

    # NOTE: could be implemented in terms of 'getFromViewOrRecord':
    #     getFromViewOrRecord(viewPath, viewGetter, const(default), default)
    #         where const(x) = lambda _: x
    def getFromView(self, viewPath, viewGetter, default=None):
        u"""
        NOTE: could be implemented in terms of 'getFromViewOrRecord':
            getFromViewOrRecord(viewPath, viewGetter, const(default), default)
            where const(x) = lambda _: x
        """
        exists, view = getAttrFromPathIfExists(self, viewPath)
        if exists:
            return viewGetter(view)
        return default

    def getDateTimeFromView(self, formDate, formTime):
        date = QtCore.QDate()
        time = QtCore.QTime()
        if hasattr(self, formDate):
            date = getattr(self, formDate).date()
        if hasattr(self, formTime):
            time = getattr(self, formTime).time()
        if not date.isNull():
            return QtCore.QDateTime(date, time)
        return None

    def getDateTime(self, dateWidget, timeWidget, fieldName):
        u"""
        Get date and time from specified widgets on 'self' and,
        if no valid datetime specified, go for the value in the record.
        """
        dateTime = self.getDateTimeFromView(dateWidget, timeWidget)
        if dateTime is not None:
            return dateTime
        if self.record():
            return self.record().value(fieldName).toDateTime()
        return QtCore.QDateTime()

    def getExternalId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'edtEventExternalIdValue'],
            viewGetter=stringOfText,
            recordGetter=recValue('externalId', forceString),
            default=''
        )

    def getCuratorId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbEventCurator'],
            viewGetter=method('value'),
            recordGetter=recValue('curator_id', forceRef)
        )

    def getAssistantId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbEventAssistant'],
            viewGetter=method('value'),
            recordGetter=recValue('assistant_id', forceRef)
        )

    def getPatientModelId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbPatientModel'],
            viewGetter=method('value'),
            recordGetter=recValue('patientModel_id', forceRef)
        )

    def getCureTypeId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbCureType'],
            viewGetter=method('value'),
            recordGetter=recValue('cureType_id', forceRef)
        )

    def getCureMethodId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbCureMethod'],
            viewGetter=method('value'),
            recordGetter=recValue('cureMethod_id', forceRef)
        )

    def getNote(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'edtEventNote'],
            viewGetter=method('toPlainText'),
            recordGetter=recValue('note', forceString),
            default=''
        )

    def getRelegateOrgId(self):
        return self.getFromViewOrRecord(
            viewPath=['tabNotes', 'cmbRelegateOrg'],
            viewGetter=method('value'),
            recordGetter=recValue('relegateOrg_id', forceRef)
        )

    def getContractId(self):
        return self.contractId

    def getPrevEventDateTime(self):
        return self.getDateTime('edtPrevDate', 'edtPrevTime', 'prevEventDate')

    def getSetDateTime(self):
        return self.getDateTime('edtBegDate', 'edtBegTime', 'setDate')

    def getDirectionDate(self):
        try:
            return self.edtPlanningDate.date()
        except AttributeError:
            return None

    def getExecDateTime(self):
        return self.getDateTime('edtEndDate', 'edtEndTime', 'execDate')

    def getNextEventDateTime(self):
        return self.getDateTime('edtNextDate', 'edtNextTime', 'nextEventDate')

    def getOrder(self):
        return self.getFromViewOrRecord(
            viewPath=['cmbOrder'],
            viewGetter=method('currentIndex'),
            recordGetter=recValue('order', forceInt),
            default=0
        )

    def getResult(self):
        return self.getFromViewOrRecord(
            viewPath=['cmbResult'],
            viewGetter=method('value'),
            recordGetter=recValue('result_id', forceRef)
        )

    # FIXME:skkachaev:ActionsModel — только МЭСы (В одном эвенте у экшенов могут быть свои МЭСы. Логика используется только в Питере)
    # FIXME:skkachaev:ActionsPage.on_btnNextAction_clicked — МЭС или КСГ (Создавать связанный эвент по действию движения. Везде)
    # FIXME:skkachaev:ActionsPage.on_actAPActionsAdd_triggered — только МЭС (Фильтр только по МЭСу)
    # FIXME:skkachaev:ActionsSelector — только МЭС (это вообще КПГ и используется в Крыму)
    # FIXME:skkachaev:EventEditDialog.getEventInfo — МЭС и КСГ
    # FIXME:skkachaev:EventEditDialog.checkDataEntered — МЭС (там проверки только МЭСовские)
    # FIXME:skkachaev:EventEditDialog.addRecommendations,actionsAdd — МЭС (добавление экшенов фильтруется только по МЭС)
    # FIXME:skkachaev:F003 — МЭС (duration — логика МЭСов)
    # FIXME:skkachaev:F043 — МЭС (добавление экшенов фильтруется только по МЭС)
    # FIXME:skkachaev:F110 — МЭС (duration — логика МЭСов)
    def getMesId(self):
        if getCmbMesType(self) != 1: return None
        return self.getFromView(['tabMes', 'cmbMes'], method('value'))

    def getCSGId(self):
        if getCmbMesType(self) != 2:
            return None
        return self.getFromView(['tabMes', 'cmbMes'], method('value'))

    def getHTGId(self):
        if hasattr(self, 'cmbHTG') and hasattr(self, 'chkHTG'):
            self.cmbHTG.value()

        if self.getFromView(['tabMes', 'chkHTG'], method('isChecked')):
            return self.getFromView(['tabMes', 'cmbHTG'], method('value'))

    def getMesSpecificationId(self):
        return self.getFromView(['tabMes', 'cmbMesSpecification'], method('value'))

    def getPaymentScheme(self):
        if self.mapPaymentScheme['paymentScheme']:
            return self.mapPaymentScheme

    def getMruDescr(self):
        return u'%s:\t%s, %s, %s' % (self.eventTypeName,
                                     formatNameInt(self.clientInfo['lastName'], self.clientInfo['firstName'],
                                                   self.clientInfo['patrName']),
                                     forceString(self.clientInfo['birthDate']),
                                     formatSex(self.clientInfo['sexCode']),
                                     )

    def getDefaultMKBValue(self, defaultMKB, setPersonId):
        defaultValue = ''
        diagnostics = None
        diagnosticsRecordList = []
        diagnosisTypeIdList = []
        if hasattr(self, 'modelFinalDiagnostics'):
            diagnostics = self.modelFinalDiagnostics
        elif hasattr(self, 'modelDiagnostics'):
            diagnostics = self.modelDiagnostics
        else:
            return defaultValue
        if diagnostics:
            diagnosticsRecordList = diagnostics.items()
            diagnosisTypeIdList = diagnostics.getCloseOrMainDiagnosisTypeIdList()
        if defaultMKB in [1, 3]:  # 1-по заключительному, 3-синхронизация по заключительному
            return getClosingMKBValueForAction(diagnosticsRecordList, diagnosisTypeIdList)
        elif defaultMKB in [2,
                            4]:  # 2-по диагнозу назначившего действие, 4-синхронизация по диагнозу назначившего действие
            eventPersonId = self.getSuggestedPersonId()
            return getMKBValueBySetPerson(diagnosticsRecordList, setPersonId, diagnosisTypeIdList, eventPersonId)
        return defaultValue

    def getDefaultMorphologyValue(self, defaultMorphology, setPersonId):
        defaultValue = ''
        diagnostics = None
        diagnosticsRecordList = []
        diagnosisTypeIdList = []
        if hasattr(self, 'modelFinalDiagnostics'):
            diagnostics = self.modelFinalDiagnostics
        elif hasattr(self, 'modelDiagnostics'):
            diagnostics = self.modelDiagnostics
        else:
            return defaultValue
        if diagnostics:
            diagnosticsRecordList = diagnostics.items()
            diagnosisTypeIdList = diagnostics.getCloseOrMainDiagnosisTypeIdList()
        if defaultMorphology in [1, 3]:  # 1-по заключительному, 3-синхронизация по заключительному
            return getClosingMorphologyValueForAction(diagnosticsRecordList, diagnosisTypeIdList)
        elif defaultMorphology in [2,
                                   4]:  # 2-по диагнозу назначившего действие, 4-синхронизация по диагнозу назначившего действие
            eventPersonId = self.getSuggestedPersonId()
            return getMorphologyValueBySetPerson(diagnosticsRecordList, setPersonId, diagnosisTypeIdList, eventPersonId)
        return defaultValue

    def getMKBValueForActionDuringSaving(self, record, action):
        actionType = action.getType()
        defaultMKB = actionType.defaultMKB
        defaultMorphology = actionType.defaultMorphology
        defaultMKBValue = ''
        defaultMorphologyMKBValue = ''
        if defaultMKB in [3, 4]:
            setPersonId = forceRef(record.value('setPerson_id'))
            defaultMKBValue = self.getDefaultMKBValue(defaultMKB, setPersonId)
        if defaultMorphology in [3, 4]:
            setPersonId = forceRef(record.value('setPerson_id'))
            defaultMorphologyMKBValue = self.getDefaultMorphologyValue(defaultMorphology, setPersonId)
        if bool(defaultMKBValue):
            record.setValue('MKB', QtCore.QVariant(defaultMKBValue))
        if bool(defaultMorphologyMKBValue):
            record.setValue('morphologyMKB', QtCore.QVariant(defaultMorphologyMKBValue))

    def getGoalId(self):
        return self.cmbGoal.value() if hasattr(self, 'cmbGoal') else None

    def setClientId(self, clientId):
        self.clientId = clientId
        if hasattr(self, 'tabAmbCard'):
            self.tabAmbCard.setClientId(clientId)
        if hasattr(self, 'tabNotes'):
            self.tabNotes.setClientId(clientId)
        self.updateClientInfo()
        self.updatePrintTriggerMap()
        if hasattr(self, 'chkZNOMorph'):
            self.setZNOMorphEnabled(u'')

    def setClientPolicyId(self, policyId):
        self.policyId = policyId

    @QtCore.pyqtSlot(int)
    def updateContractByClientPolicy(self, policyId):
        def getPolicyInfo(policyRecord):
            if policyRecord:
                insurerId = forceRef(policyRecord.value('insurer_id'))
                policyTypeId = forceRef(policyRecord.value('policyType_id'))
            else:
                insurerId = None
                policyTypeId = None
            return insurerId, policyTypeId

        clientPolicyRecord = QtGui.qApp.db.getRecord('ClientPolicy', '*', policyId)

        self.clientPolicyInfoList = [getPolicyInfo(clientPolicyRecord)]

        if hasattr(self, 'cmbContract'):
            oldContractId = self.cmbContract.value()
            self.cmbContract.setClientInfo(self.clientId,
                                           self.clientSex,
                                           self.clientAge,
                                           self.clientWorkOrgId,
                                           self.clientPolicyInfoList)
            if oldContractId in self.cmbContract.values():
                self.cmbContract.setValue(oldContractId)

    @QtCore.pyqtSlot()
    def updateContractSelected(self):
        if hasattr(self, 'cmbContract'):
            preferredContractId = None
            existedContractIdList = self.cmbContract.values()
            for policyInfo in self.clientPolicyInfoList:
                db = QtGui.qApp.db
                tableContractContingent = db.table('Contract_Contingent')
                cond = [tableContractContingent['master_id'].inlist(existedContractIdList),
                        tableContractContingent['insurer_id'].eq(policyInfo[0]),
                        tableContractContingent['deleted'].eq(0)]
                preferedContractIdList = db.getDistinctIdList(tableContractContingent, 'master_id', cond,
                                                              'master_id DESC')
                if preferedContractIdList:
                    preferredContractId = preferedContractIdList[0]
                    break

            if preferredContractId:
                self.cmbContract.setValue(preferredContractId)
            else:
                self.cmbContract.setCurrentIndex(0)

    def checkVipPerson(self, textBrowser):
        if self.isVipClient:
            textBrowser.setStyleSheet("background-color: %s;" % self.vipColor)
        else:
            textBrowser.setStyleSheet("")

    def updateClientInfo(self):
        def getPolicyInfo(policyRecord):
            if policyRecord:
                insurerId = forceRef(policyRecord.value('insurer_id'))
                policyTypeId = forceRef(policyRecord.value('policyType_id'))
            else:
                insurerId = None
                policyTypeId = None
            return insurerId, policyTypeId

        if self.clientId:
            self.clientDeathDate = getDeathDate(self.clientId)
        db = QtGui.qApp.db
        self.clientInfo = getClientInfo(self.clientId)

        if u'онко' in forceString(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')
        ):
            vipRecord = QtGui.qApp.db.getRecordEx(
                QtGui.qApp.db.table('ClientVIP'),
                [
                    QtGui.qApp.db.table('ClientVIP')['client_id'],
                    QtGui.qApp.db.table('ClientVIP')['color']
                ],
                [
                    QtGui.qApp.db.table('ClientVIP')['deleted'].eq(0),
                    QtGui.qApp.db.table('ClientVIP')['client_id'].eq(self.clientId)
                ]
            )

            self.isVipClient = forceBool(vipRecord)
            if self.isVipClient:
                self.vipColor = forceString(vipRecord.value('color'))

        if hasattr(self, 'txtClientInfoBrowser'):
            self.txtClientInfoBrowser.setHtml(getClientBanner(self.clientId))
            self.checkVipPerson(self.txtClientInfoBrowser)

        # if hasattr(self, 'cmbOrder'):
        #     EventOrder.fillCmb(self.cmbOrder)

        table = db.table('Client')
        record = db.getRecord(table, 'sex, birthDate', self.clientId)
        if record:
            self.clientSex = forceInt(record.value('sex'))
            self.clientBirthDate = forceDate(record.value('birthDate'))
            self.clientAge = calcAgeTuple(self.clientBirthDate, self.eventDate)
        self.resetActionTemplateCache()
        if hasattr(self, 'cmbContract'):
            workRecord = getClientWork(self.clientId)
            self.setWorkRecord(workRecord)
            self.clientWorkOrgId = forceRef(workRecord.value('org_id')) if workRecord else None
            self.clientPolicyInfoList = []
            policyDate = self.eventDate or self.eventSetDateTime

            clientPolicyId = self.tabNotes.cmbClientPolicy.value() if hasattr(self, 'tabNotes') else None

            if hasattr(self, 'tabNotes') and not clientPolicyId is None:
                clientPolicyRecord = db.getRecord('ClientPolicy', '*', clientPolicyId)
                self.clientPolicyInfoList = [getPolicyInfo(clientPolicyRecord)]
            else:
                policyRecord = getClientCompulsoryPolicy(self.clientId, policyDate)
                if policyRecord:
                    self.clientPolicyInfoList.append(getPolicyInfo(policyRecord))
                else:
                    policyRecord = getClientCompulsoryPolicy(self.clientId)
                    if policyRecord:
                        self.clientPolicyInfoList.append(getPolicyInfo(policyRecord))

                policyRecordList = getClientVoluntaryPolicyList(self.clientId, policyDate)
                for policyRecord in policyRecordList:
                    self.clientPolicyInfoList.append(getPolicyInfo(policyRecord))

            self.connect(self.cmbContract.model(), QtCore.SIGNAL('modelReset()'), self.updateContractSelected)
            self.cmbContract.setClientInfo(self.clientId, self.clientSex, self.clientAge, self.clientWorkOrgId,
                                           self.clientPolicyInfoList)

            if hasattr(self, 'tabNotes'):
                self.connect(self.tabNotes.cmbClientPolicy, QtCore.SIGNAL('clientPolicyChanged(int)'),
                             self.updateContractByClientPolicy)

        if hasattr(self, 'edtPregnancyWeek'):
            pregnancyVisible = (self.clientSex == 2) and bool(self.clientAge) and self.clientAge[3] >= 12
            self.lblPregnancyWeek.setVisible(pregnancyVisible)
            self.edtPregnancyWeek.setVisible(pregnancyVisible)
            self.edtPregnancyWeek.setMaximum(42)
        if hasattr(self, 'tabMes'):
            self.tabMes.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setClientInfo(self.realClientSex(), self.realClientAge(), self.clientId)
        try:
            clientKLADRCode = self.clientInfo.regAddressInfo.KLADRCode
        except:
            clientKLADRCode = ''
        if KLADRMatch(clientKLADRCode, QtGui.qApp.defaultKLADR()):
            self.clientType = CEventEditDialog.ctLocal
        elif KLADRMatch(clientKLADRCode, QtGui.qApp.provinceKLADR()):
            self.clientType = CEventEditDialog.ctProvince
        else:
            self.clientType = CEventEditDialog.ctOther

    def getSetPersonId(self):
        return self.personId

    def getExecPersonId(self):
        return self.personId

    def getEventInfo(self, context, infoClass=CEventInfo):
        # TODO: Привести поля в соответствие с CEventInfo
        selfId = self.itemId()
        if selfId == None:
            selfId = False
        result = context.getInstance(infoClass, selfId)

        date = self.eventDate if self.eventDate else QtCore.QDate.currentDate()
        record = self.record()
        showTime = getEventShowTime(self.eventTypeId)
        dateInfoClass = CDateTimeInfo if showTime else CDateInfo
        # инициализация свойств
        result._eventType = context.getInstance(CEventTypeInfo, self.eventTypeId)
        result._externalId = self.getExternalId()
        result._org = context.getInstance(COrgInfo, self.orgId)
        result._relegateOrg = context.getInstance(COrgInfo, self.getRelegateOrgId())
        result._curator = context.getInstance(CPersonInfo, self.getCuratorId())
        result._assistant = context.getInstance(CPersonInfo, self.getAssistantId())
        result._client = context.getInstance(CClientInfo, self.clientId, date)
        result._order = self.getOrder()
        result._prevEventDate = dateInfoClass(self.getPrevEventDateTime())
        result._setDate = dateInfoClass(self.getSetDateTime())
        result._setPerson = context.getInstance(CPersonInfo, self.getSetPersonId())
        result._execDate = dateInfoClass(self.getExecDateTime())
        result._execPerson = context.getInstance(CPersonInfo, self.getExecPersonId())
        result._directionDate = dateInfoClass(self.getDirectionDate())
        result._result = context.getInstance(CResultInfo, self.getResult())
        result._nextEventDate = dateInfoClass(self.getNextEventDateTime())
        result._contract = context.getInstance(CContractInfo, self.contractId)
        result._tariffDescr = self.contractTariffCache.getTariffDescr(self.contractId, self)
        result._localContract = self.tabCash.getLocalContractInfo(context, selfId) if hasattr(self, 'tabCash') else None
        result._mes = context.getInstance(CMesInfo, self.getMesId() or self.getCSGId(), selfId)
        result._mesSpecification = context.getInstance(CMesSpecificationInfo, self.getMesSpecificationId())
        result._note = self.getNote()
        result._payStatus = record.value('payStatus') if record else 0
        result._patientModel = context.getInstance(CPatientModelInfo, self.getPatientModelId())
        result._cureType = context.getInstance(CCureTypeInfo, self.getCureTypeId())
        result._cureMethod = context.getInstance(CCureMethodInfo, self.getCureMethodId())
        result._htg = context.getInstance(CHTGInfo, self.getHTGId(), selfId)
        result._recommendations = context.getInstance(CRecommendationInfoList, selfId)
        result._policy = context.getInstance(CClientPolicyInfo, self.clientId, self.policyId)
        result._referral = context.getInstance(CReferralInfo, forceRef(record.value('referral_id'))) if record else None
        result._policlinicReferral = context.getInstance(CPoliclinicReferralInfo, self.clientId)
        # формальная инициализация таблиц
        result._actions = []
        result._diagnosises = []
        result._visits = []
        result._ok = True
        result._loaded = True
        result._isPrimary = self.primaryState()
        result._goal = context.getInstance(CEventGoalInfo, self.getGoalId())

        if hasattr(self, 'tabCash') and self.isTabCashAlreadyLoad:
            result._cashPage = context.getInstance(CEventCashPageInfo, selfId)
            result._cashPage._accValue = self.tabCash.lblPaymentAccValue.text()
            result._cashPage._payedValue = self.tabCash.lblPaymentPayedSumValue.text()
            result._cashPage._totalValue = self.tabCash.lblPaymentTotalValue.text()

        return result

    def recordAcceptable(self, record):
        return recordAcceptable(self.clientSex, self.clientAge, record)

    def setWorkRecord(self, record):
        pass

    def checkClientAttendaceEE(self, personId):
        return self.checkClientAttendaceEx(personId, self.clientSex, self.clientAge) or \
               self.confirmClientAttendace(self, personId, self.clientId)

    def getPersonSSF(self, personId):
        key = personId, self.clientType
        result = self.personSSFCache.get(key, None)
        if not result:
            record = QtGui.qApp.db.getRecord(
                'Person LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id',
                'speciality_id, service_id, provinceService_id, otherService_id, '
                'finance_id, tariffCategory_id, fundingService_id, orgStructure_id',
                personId
            )
            if record:
                specialityId = forceRef(record.value('speciality_id'))
                serviceId = forceRef(record.value('service_id'))
                provinceServiceId = forceRef(record.value('provinceService_id'))
                otherServiceId = forceRef(record.value('otherService_id'))
                fundingServiceId = forceRef(record.value('fundingService_id'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                financeId = forceRef(record.value('finance_id'))
                tariffCategoryId = forceRef(record.value('tariffCategory_id'))

                if forceRef(
                        QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'isArea')) and fundingServiceId:
                    serviceId = fundingServiceId
                elif self.clientType == CEventEditDialog.ctOther and otherServiceId:
                    serviceId = otherServiceId
                elif self.clientType == CEventEditDialog.ctProvince and provinceServiceId:
                    serviceId = provinceServiceId
                result = (specialityId, serviceId, financeId, tariffCategoryId)
            else:
                result = (None, None, None, None)
            self.personSSFCache[key] = result
        return result

    def getPersonServiceId(self, personId):
        return self.getPersonSSF(personId)[1]

    def getPersonFinanceId(self, personId):
        return self.getPersonSSF(personId)[2]

    def getPersonTariffCategoryId(self, personId):
        return self.getPersonSSF(personId)[3]

    def setPersonId(self, personId):
        self.personId = personId
        self.personSpecialityId, self.personServiceId, self.personFinanceId, self.personTariffCategoryId = self.getPersonSSF(
            personId)
        self.resetActionTemplateCache()
        if hasattr(self, 'tabMes'):
            self.tabMes.setSpeciality(self.personSpecialityId)
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setSpeciality(self.personSpecialityId)
        if hasattr(self, 'cmbPerson'):
            self.cmbPerson.setValue(personId)

    def setOrgStructureId(self, orgStructureId):
        self.orgStructureId = orgStructureId

    def setContract(self):
        if hasattr(self, 'tabMes'):
            self.tabMes.setContract(self.contractId)
            if self.eventDate and not self.eventDate.isNull():
                self.tabMes.setEndDateForTariff(self.eventDate)
            elif self.eventSetDateTime and not self.eventSetDateTime.date().isNull():
                self.tabMes.setEndDateForTariff(self.eventSetDateTime.date())
        if hasattr(self, 'cmbCsg'):
            self.cmbCsg.setContract(self.contractId)
            if self.eventDate and not self.eventDate.isNull():
                self.cmbCsg.setEndDateForTariff(self.eventDate)
            elif self.eventSetDateTime and not self.eventSetDateTime.date().isNull():
                self.cmbCsg.setEndDateForTariff(self.eventSetDateTime.date())

    def getSuggestedPersonId(self):
        return QtGui.qApp.userId if QtGui.qApp.userSpecialityId else self.personId

    def getVisitFinanceId(self, personId=None):
        if getEventVisitFinance(self.eventTypeId):
            return self.getPersonFinanceId(personId) if personId else self.personFinanceId
        else:
            return self.eventFinanceId

    def getActionFinanceId(self, actionRecord):
        finance = getEventActionFinance(self.eventTypeId)
        if finance == 1:
            return self.eventFinanceId
        elif finance == 2:
            personId = forceRef(actionRecord.value('setPerson_id'))
            return self.getPersonFinanceId(personId) if personId else self.personFinanceId
        elif finance == 3:
            personId = forceRef(actionRecord.value('person_id'))
            return self.getPersonFinanceId(personId) if personId else self.personFinanceId
        else:
            return None

    def specifyDiagnosis(self, MKB):
        diagFilter = self.getDiagFilter()
        date = min([d for d in [self.eventSetDateTime.date(), self.eventDate, QtCore.QDate.currentDate()] if d])
        acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId, modifiableDiagnosisId = specifyDiagnosis(
            self, MKB, diagFilter, self.clientId, self.clientSex, self.clientAge, date, self.endDate(),
            self.eventTypeId)
        self.modifiableDiagnosisesMap[specifiedMKB] = modifiableDiagnosisId
        return acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId

    def modifyDiagnosises(self, MKBDiagnosisIdPairList):
        db = QtGui.qApp.db
        #        table = db.table('Diagnosis')
        for MKB, newDiagnosisId in MKBDiagnosisIdPairList:
            oldDiagnosisId = self.modifiableDiagnosisesMap.get(MKB, None)
            if oldDiagnosisId:
                db.query('UPDATE Diagnosis SET mod_id=%d WHERE id=%d AND mod_id IS NULL AND deleted=0' % (
                    newDiagnosisId, oldDiagnosisId))
                db.query('UPDATE Diagnosis AS DOld, Diagnosis AS DNew '
                         'SET DNew.setDate=DOld.setDate '
                         'WHERE DNew.id=%d AND DOld.id=%d AND DOld.mod_id=DNew.id AND '
                         'DNew.setDate IS NOT NULL AND DOld.setDate IS NOT NULL AND DOld.setDate<DNew.setDate' % (
                             newDiagnosisId, oldDiagnosisId))

    def resetActionTemplateCache(self):
        pass

    def getVisitCount(self):
        return 1

    def getEventLength(self, countRedDays):
        startDate = self.eventSetDateTime.date() if self.eventSetDateTime else QtCore.QDate.currentDate()
        stopDate = self.eventDate if self.eventDate else QtCore.QDate.currentDate()
        return getEventLengthDays(startDate, stopDate, countRedDays, self.eventTypeId)

    def fillNextDate(self):
        if self.eventPeriod:
            nextDate = countNextDate(self.eventSetDateTime.date(), self.eventPeriod)
            self.edtNextDate.setDate(nextDate)
        else:
            self.edtNextDate.setDate(QtCore.QDate())

    def emitUpdateActionsAmount(self):
        self.emit(QtCore.SIGNAL('updateActionsAmount()'))

    def getPrevActionId(self, action, searchMode):
        u"""
        @param action: действие, для которого ищем образец
        @param searchFlag: 0 - только свои, 1 - врачей той же специальности, 2 - любых врачей
        @return:
        """
        actionTypeId = action.getType().id
        actionId = forceRef(action.getRecord().value('id')) if action.getRecord() else None
        personId = forceRef(action.getRecord().value('person_id')) or self.personId
        eventDate = self.eventDate if self.eventDate else QtCore.QDate.currentDate()
        actionTypes = QtGui.qApp.db.getDistinctIdList('rbActionTypeSimilarity', 'firstActionType_id',
                                                      ['secondActionType_id=%s' % actionTypeId, 'similarityType=0'])
        actionTypes.extend(QtGui.qApp.db.getDistinctIdList('rbActionTypeSimilarity', 'secondActionType_id',
                                                           ['firstActionType_id=%s' % actionTypeId,
                                                            'similarityType=0']))
        actionTypes.append(actionTypeId)
        actionTypes = tuple(set(actionTypes))
        key = (actionTypeId, actionTypes, personId, searchMode, eventDate.toPyDate())
        if key in self.prevActionIdCache:
            return self.prevActionIdCache[key]
        else:
            result = self.findPrevActionId(actionTypes, actionId, personId, searchMode, eventDate)
            self.prevActionIdCache[key] = result
            return result

    def deleteTabMes(self):
        if hasattr(self, 'tabMes') and hasattr(self, 'tabWidget'):
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabMes))
            del self.tabMes
        elif hasattr(self, 'tabMes'):
            self.tabMes.setEnabled(False)

    def findPrevActionId(self, actionTypeId, actionId, personId, searchMode, eventDate):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        if searchMode == 1:
            tablePerson = db.table('Person')
            tablePerson2 = db.table('Person').alias('Person2')
            table = table.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
            table = table.leftJoin(tablePerson2, tablePerson2['speciality_id'].eq(tablePerson['speciality_id']))

        cond = [tableAction['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(self.clientId),
                tableEvent['execDate'].lt(eventDate.addDays(1)),
                ]
        if isinstance(actionTypeId, tuple):
            cond.append(tableAction['actionType_id'].inlist(actionTypeId))
        else:
            cond.append(tableAction['actionType_id'].eq(actionTypeId))
        if searchMode == 1:
            cond.append(tablePerson2['id'].eq(personId))
        elif searchMode == 0:
            cond.append(tableEvent['execPerson_id'].eq(personId))
        if actionId:
            cond.append(tableAction['id'].ne(actionId))
        idList = db.getIdList(table, tableAction['id'].name(), cond, tableEvent['execDate'].name() + ' DESC', 1)
        if idList:
            return idList[0]
        else:
            return None

    def primaryCheck(self, modelDiagnostics):
        u"""Проверка на соответствие признака первичности обращения первичности диагноза"""
        record = modelDiagnostics.items()[0] if modelDiagnostics.items() else None
        if record:
            MKB = forceString(record.value('MKB'))
            characterId = forceRef(record.value('character_id'))
            # atronah: проверка на наличие такого же диагноза в этом году у пациента (True, если такой же диагноз не найден)
            diagnosisPrimacy = getDiagnosisPrimacy(self.clientId, self.eventDate, MKB, characterId)
            newValue = EventIsPrimary.Primary if diagnosisPrimacy else EventIsPrimary.Secondary
            primaryState = self.primaryState()
            if (primaryState in [EventIsPrimary.Primary,
                                 EventIsPrimary.Secondary]
                and newValue != primaryState):
                if QtGui.QMessageBox.question(
                        self,
                        u'Внимание!',
                        u'Указание первичности обращения противоречит данным ЛУД.\nИзменить признак первичности?',
                                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                        QtGui.QMessageBox.Yes
                ) == QtGui.QMessageBox.Yes:
                    self.setPrimaryState(newValue)
        return True

    def saveData(self):
        if hasattr(self, 'updateVisitInfo'):
            self.updateVisitInfo()
        if hasattr(self, 'updateDuration'):
            self.updateDuration()

        return self.checkDataEntered() and self.checkTabNotesEventExternalId() and self.save()

    def setEventDuration(self, amount):
        if self._record:
            self._record.setValue('duration', toVariant(amount))

    def checkMESLimitation(self):
        u"""
        Только для СПб.
        Жесткое ограничение: при сохранении события проверяем есть ли у "стандарта" ограничение и было ли введено
        ранее событие с этим "стандартом": если да - показываем окно предупреждение и не даем сохранить обращение
        :return: возвращает результат проверки
        :rtype bool
        """
        if QtGui.qApp.defaultKLADR()[:2] == '78' and self.tabMes.cmbMes.value() > 0:
            stmt = u"""
                SELECT
                  *
                FROM
                  Event INNER JOIN mes.MES ON Event.MES_id = mes.MES.id
                WHERE
                  Event.deleted = 0
                  AND mes.MES.deleted = 0
                  AND YEAR(Event.setDate) = YEAR(NOW())
                  AND mes.MES.hasLimit = 1
                  AND mes.MES.id = %s
            """ % self.tabMes.cmbMes.value()
            rec = QtGui.qApp.db.getRecordEx(stmt=stmt)
            if rec:
                return self.checkValueMessage(
                    u'Пациент уже проходил лечение по стандарту \n"%s" \nв календарном году' % self.tabMes.cmbMes.currentText(),
                    False,
                    self.tabMes.cmbMes
                )
        return True

    # TODO: atronah: перенести сюда общие для всех форм проверки
    def checkDataEntered(self):
        if forceBool(QtGui.qApp.preferences.appPrefs.get('enableEpircisModule', False)) \
                and self._id \
                and self.btnEpicrisPressed:
            # self.saveActions(eventId)
            # self.resetActionTemplateCache()
            if hasattr(self, 'loadActions'):
                self.loadActions()

        result = True
        if self._record and not self.getEditable():
            self.checkValueMessage(u'Невозможно сохранить заблокированное обращение', False, None)
            return False
        if hasattr(self, 'cmbGoal'):
            if not QtGui.qApp.userHasRight('saveEventWithoutGoal'):
                result = result and self.check_is_cmbGoal_filled()
        if hasattr(self, 'modelVisits') and hasattr(self, 'tblVisits'):
            if not QtGui.qApp.userHasRight('createSeveralVisits'):
                result = result and self.checkMoreThanOneVisit()
        endDate = self.edtEndDate.date() if self._isClosedEventCheck and hasattr(self, 'edtEndDate') else QtCore.QDate()

        if hasattr(self, 'tabMes') and getEventMesRequired(self.eventTypeId):
            if not endDate.isNull():
                mesId = self.tabMes.cmbMes.value()
                if not getEventTypeForm(self.eventTypeId) == u'030S':
                    mesSpecificationId = self.tabMes.cmbMesSpecification.value()
                    result = result and self.checkMesNecessityEqOne(mesId)
                    # i821. Отключать проверки, если указан МЭС с особенностью выполнения без признака выполненности МЭСа (rbMesSpecification.done)
                    # Даже если мэс не применен, требуется ввод всех услуг с ЧП=1.
                    if mesSpecificationId and not CMesSpecificationInfo(CInfoContext(), mesSpecificationId).done:
                        self._isClosedEventCheck = False
                        return result
                    result = result and self.tabMes.checkMesAndSpecification()
                if hasattr(self, 'tblFinalDiagnostics') and getCmbMesType(self) == 2:
                    result = result and self.checkDiagnosticsMKBForMes(self.tblFinalDiagnostics,
                                                                       self.tabMes.cmbMes.SPR69value())

                if hasattr(self, 'chkHTG') and not self.chkHTG.isChecked():
                    result = result and (self.checkContractForMes(self.contractId, mesId) or self.checkValueMessage(
                    u'Выбранного стандарта нет в договоре', True, None))

                if not QtGui.qApp.userHasRight(urAllowSaveEventsWithoutCSG):
                    if getEventTypeForm(self.eventTypeId) == u'003' and QtGui.qApp.defaultKLADR()[:2] == '23':
                        if self.tabMes.cmbMes.value() < 0:
                            if not self.tabMes.chkHTG.isChecked():
                                result = result and self.checkInputMessage(u'КСГ.', True, self.tabMes)

                    result = result and self.checkMESLimitation()
        if not QtGui.qApp.userHasRight(urAllowSaveEventsWithoutCSG) and getEventMesRequired(self.eventTypeId):
            if QtGui.qApp.defaultKLADR()[:2] == '23' and hasattr(self, 'cmbCsg') and not endDate.isNull():
                if self.cmbCsg.value() < 0:
                    if not (hasattr(self, 'chkHTG') and self.chkHTG.isChecked()):
                        result = result and self.checkInputMessage(u'КСГ.', False, self.cmbCsg)

        if (hasattr(self,
                    'gbLittleStrangerFlag') and self.gbLittleStrangerFlag.isChecked() and not QtGui.qApp.userHasRight(
            urIgnoreLittleStrangerCheck)):
            result = result and (
                self.cmbChildSex.currentIndex() or self.checkInputMessage(u'пол новорожденного',
                                                                          False,
                                                                          self.cmbChildSex))
            result = result and (
                not self.edtChildBirthDate.date().isNull() or self.checkInputMessage(u'дату рождения новорожденного',
                                                                                     False,
                                                                                     self.edtChildBirthDate))
        if hasattr(self, 'tblActions') and getEventMesRequired(self.eventTypeId):
            actionTypeIdList = [forceRef(record.value('actionType_id')) for record in self.tblActions.model().items()]
            mesId = self.getMesId()
            result = result and self.checkCompulsoryService(actionTypeIdList, self.eventTypeId, mesId=mesId)
            result = result and self.checkComplexService(actionTypeIdList, self.eventTypeId, mesId=mesId)

        MKB = ''
        if getEventTypeForm(self.eventTypeId) not in [u'001', u'']:
            MKB = self.getFinalDiagnosisMKB()[0]

        if getEventTypeForm(self.eventTypeId) in [u'003', u'030'] \
                and not QtGui.qApp.checkGlobalPreference('21', u'0') \
                and hasattr(self, 'tabNotes') \
                and not QtGui.qApp.userHasRight(urDisableCheckRefferal):
            if self.tabNotes.chkLPUReferral.isChecked():
                if self.order() in [3, 4]:
                    self.checkValueMessage(u'Для данного порядка поступления не должно быть направления', True,
                                           self.tabNotes)
                    return False
                elif self.tabNotes.edtDate.date().isNull():
                    self.checkValueMessage(u'Необходимо указать дату направления', False, self.tabNotes.edtDate)
                    return False
                elif self.tabNotes.edtPlannedDate.date().isNull():
                    self.checkValueMessage(u'Необходимо указать дату плановой госпитализации', False,
                                           self.tabNotes.edtPlannedDate)
                    return False
                elif not self.tabNotes.cmbReferralType.value():
                    self.checkValueMessage(u'Необходимо указать тип направления', False,
                                           self.tabNotes.cmbReferralType)
                    return False
                elif not self.tabNotes.edtNumber.text():
                    self.checkValueMessage(u'Необходимо указать номер направления', False,
                                           self.tabNotes.edtNumber)
                    return False
                elif self.tabNotes.edtDate.date().isNull():
                    self.checkValueMessage(u'Необходимо указать дату направления', False, self.tabNotes.edtDate)
                    return False
                elif not self.tabNotes.cmbRelegateOrg.value() and not self.tabNotes.edtFreeInput.text():
                    self.checkValueMessage(u'Необходимо указать направителя', False,
                                           self.tabNotes.cmbRelegateOrg)
                    return False
                elif self.tabNotes.edtPlannedDate.date() < self.tabNotes.edtDate.date():
                    self.checkValueMessage(
                        u'Планируемая дата госпитализации не может быть меньше даты направления', False,
                        self.tabNotes.edtPlannedDate)
                    return False
                elif self.tabNotes.edtDate.date() > QtCore.QDate.currentDate():
                    self.checkInputMessage(
                        u'Дата направления не может быть больше текущей', False, self.tabNotes.edtDate
                    )
                elif self.tabNotes.edtPlannedDate.date() > self.tabNotes.edtDate.date().addMonths(6):
                    self.checkValueMessage(
                        u'Планируемая дата госпитализации превышает дату направления более чем на 6 месяцев',
                        False,
                        self.tabNotes.edtPlannedDate
                    )
                    return False
                elif not self.tabNotes.cmbMKB.text():
                    self.checkValueMessage(u'Необходимо указать код МКБ', False, self.tabNotes.cmbMKB)
                    return False
                elif self.tabNotes.cmbMKB.text():
                    db = QtGui.qApp.db
                    tableMKB = db.table('MKB')
                    if not db.getRecordEx(tableMKB, tableMKB['id'],
                                          tableMKB['DiagID'].eq(forceString(self.tabNotes.cmbMKB.text()))):
                        self.checkValueMessage(u'Введен не корректный код МКБ', False, self.tabNotes.cmbMKB)
                        return False

            elif not self.tabNotes.chkLPUReferral.isChecked() and self.order() == 1:
                result = result and self.checkValueMessage(
                    u'Для плановой госпитализации необходимо добавить направление', True, self.tabNotes
                )

        if hasattr(self, 'tblActions') and MKB and MKB != '':
            actionTypeIdList = frozenset(
                [forceRef(record.value('actionType_id')) for record in self.tblActions.model().items()])
            MESActionTypes = frozenset(getActionTypeIdListByMKB(MKB))
            result = result and (
                (actionTypeIdList.issubset(MESActionTypes) or len(MESActionTypes) == 0) or self.checkValueMessage(
                    u'Выбранные услуги не соотвествуют заключительному диагнозу', True, None))

        if hasattr(self, 'tabRecommendations') and self.tabWidget.indexOf(self.tabRecommendations) != -1 and hasattr(
                self, 'isTabRecommendationsAlreadyLoad'):
            result = result and (self.isTabRecommendationsAlreadyLoad or self.checkValueMessage(
                u'У пациента нет рекомендаций. Добавить рекомендации?', False, self.tabRecommendations))
            # if not result:
            #     self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabRecommendations))
        if hasattr(self, 'chkZNOFirst') and hasattr(self, 'chkZNOMorph'):
            if self.chkZNOFirst.isChecked() or (self.chkZNOMorph.isChecked() and self.chkZNOMorph.isEnabled()):
                resultBuf, errorMessage = self.checkZNO(self.chkZNOFirst.isChecked(), self.chkZNOMorph.isChecked())
                if not resultBuf:
                    result = result and self.checkValueMessage(errorMessage, False, self.chkZNOFirst)
        return result

    def setZNOMorphEnabled(self, externalId):
        db = QtGui.qApp.db
        stmt = u'''
        Select `Event`.`externalId`, `Event`.`ZNOFirst`, `Event`.`ZNOMorph`, `Event`.`execDate`
        From `Event`
        Where `Event`.`client_id` = '%s'
            and `Event`.`deleted` = '0' ''' % self.clientId
        morphError = False
        query = db.query(stmt)
        while query.next():
            record = query.record()
            if forceBool(record.value('ZNOMorph')):
                morphExtId = forceString(record.value('externalId'))
                if externalId != morphExtId:
                    morphError = True
        self.chkZNOMorph.setChecked(morphError)
        self.chkZNOMorph.setEnabled(not morphError)

    def checkZNO(self, first, morph):
        db = QtGui.qApp.db
        stmt = u'''
        Select `Event`.`externalId`, `Event`.`ZNOFirst`, `Event`.`ZNOMorph`, `Event`.`execDate`
        From `Event`
        Where `Event`.`client_id` = '%s'
            and `Event`.`deleted` = '0' ''' % self.clientId
        firstExtId = u''
        firstError = False
        morphExtId = u''
        morphError = False
        morphDate = QtCore.QDate()
        conflictError = False
        result = True
        query = db.query(stmt)
        while query.next():
            record = query.record()
            if forceBool(record.value('ZNOFirst')):
                firstExtId = forceString(record.value('externalId'))
                firstDate = forceDate(record.value('execDate'))
                if self.getExternalId() != firstExtId and first:
                    result = False
                    firstError = True
            if forceBool(record.value('ZNOMorph')):
                morphExtId = forceString(record.value('externalId'))
                morphDate = forceDate(record.value('execDate'))
                if self.getExternalId() != morphExtId and morph:
                    result = False
                    morphError = True
        if (first
            and morphExtId
            and morphExtId != self.getExternalId()
            and not firstExtId
            and self.eventDate > morphDate) or (morph
                                                and firstExtId
                                                and firstExtId != self.getExternalId()
                                                and not morphExtId
                                                and self.eventDate < firstDate):
            result = False
            conflictError = True
        errorMessage = u''
        errorList = []
        if firstError:
            errorList.append(u'ЗНО установлен впервые в обращении с внешним идентификатором: %s' % firstExtId)
        if morphError:
            errorList.append(u'ЗНО подтверждён морфологически в обращении с внешним идентификатором: %s' % morphExtId)
        if conflictError:
            errorList.append(u'ЗНО не может быть подтверждён раньше, чем установлен')
        errorMessage = u'\n'.join(errorList)
        return result, errorMessage

    def check_is_cmbGoal_filled(self):
        result = True
        if not forceInt(self.cmbGoal.currentIndex()):
            message = u'цель обращения'
            result = self.checkInputMessage(message, False, self.cmbGoal)
        return result

    def checkMoreThanOneVisit(self):
        result = True
        record_list = self.modelVisits.items()
        personId_list = []
        datePerson_list = []
        visitListFromModel = []
        for record in record_list:
            date = forceString(forceDate(record.value('date')))
            person_id = forceRef(record.value('person_id'))
            visitId = forceRef(record.value('id'))
            if visitId:
                visitListFromModel.append(visitId)
            datePerson_list.append((date, person_id))
            personId_list.append(person_id)
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableVisit = db.table('Visit')
        where = db.joinAnd([tableEvent['client_id'].eq(self.clientId), tableEvent['deleted'].eq(0)])
        rl = db.getRecordList(tableEvent, ['id'], where=where)
        events_list = map(lambda r: forceRef(r.value('id')), rl)
        where = db.joinAnd([tableVisit['event_id'].inlist(events_list),
                            tableVisit['id'].notInlist(visitListFromModel),
                            tableVisit['deleted'].eq(0)])
        rl = db.getRecordList(tableVisit, ['id', 'date', 'person_id'], where=where)
        for record in rl:
            date = forceString(forceDate(record.value('date')))
            person_id = forceRef(record.value('person_id'))
            datePerson_list.append((date, person_id))
            personId_list.append(person_id)
        tablePerson = db.table('Person')
        rl = db.getRecordList('Person', ['id', 'speciality_id'], where=tablePerson['id'].inlist(personId_list))
        personSpecMap = {}
        speciality_list = []
        for r in rl:
            person_id = forceRef(r.value('id'))
            speciality_id = forceRef(r.value('speciality_id'))
            personSpecMap[person_id] = speciality_id
            speciality_list.append(speciality_id)
        dateSpeciality = {}
        for dp in datePerson_list:
            date = dp[0]
            person_id = dp[1]
            t = (date, personSpecMap.get(person_id))
            c = dateSpeciality.setdefault(t, 0)
            c += 1
            dateSpeciality[t] = c
        tablerbSpeciality = db.table('rbSpeciality')
        rl = db.getRecordList('rbSpeciality', ['id', 'name'], where=tablerbSpeciality['id'].inlist(speciality_list))
        specIdNameMap = dict(map(lambda r: (forceRef(r.value('id')), forceString(r.value('name'))), rl))
        msg = u''
        for t, num in dateSpeciality.items():
            if num > 1:
                msg += u'%s, %s : %s посещений\n' % (t[0], specIdNameMap.get(t[1]), num)
        if msg:
            message = u'На следующие даты существует больше одного посещения врача с той же специальностью:\n' + msg
            result = self.checkValueMessage(message, True, self.tblVisits)
        return result

    def checkDiagnosticsMKBForMes(self, tableFinalDiagnostics, SPR69_id):
        model = tableFinalDiagnostics.model()
        result, finalDiagnosis = self.checkMKBForMes(tableFinalDiagnostics, SPR69_id, model.diagnosisTypeCol.ids[0])
        if result and not finalDiagnosis:
            result, finalDiagnosis = self.checkMKBForMes(tableFinalDiagnostics, SPR69_id, model.diagnosisTypeCol.ids[1])
        return result

    @staticmethod
    def checkContractForMes(contractId, MesId):
        db = QtGui.qApp.db
        tblContractTariff = db.table('Contract_Tariff')
        tblRbService = db.table('rbService')
        tblMes = db.table('mes.MES')
        qTable = tblContractTariff.innerJoin(tblRbService, [tblContractTariff['service_id'].eq(tblRbService['id']),
                                                            tblContractTariff['deleted'].eq(0)])
        qTable = qTable.innerJoin(tblMes, tblRbService['code'].eq(tblMes['code']))
        cond = [tblMes['id'].eq(MesId), tblContractTariff['master_id'].eq(contractId)]
        query = db.query(db.selectStmt(table=qTable, where=cond))
        if query.next():
            return True
        else:
            return False

    def checkDiagnosticsDataEntered(self, checkList, endDate):
        u"""
        Проверка диагностик/осмотров
        :param checkList: список из кортежей, описывающих таблицы, которые необходимо проверить
                кортеж:    (виджет_таблицы,
                            проверка_результата,
                            проверка_на_нулевое_количество_элементов,
                            дата_закрытия_обращения_если_надо_проверять_тип_иначе_None)
                пример checkList:    [ (qTableViewWidget1, True, True, None),
                                       (qTableViewWidget1, False, True, endDate) ]
        :param endDate: дата конца обращения
        :return: True если проверка прошла успешно, иначе False
        """
        if QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            return True

        for table, checkResult, checkCount, typeCheckEndDate in checkList:
            # Если обращение закончено, но список диагностик пуст, а должен быть заполнен (checkCount = True)
            if endDate and checkCount and len(table.model().items()) <= 0:
                # то сообещить об ошибке
                rowCount = table.model().rowCount() or None
                column = table.model().getColIndex('MKB') if rowCount else None
                self.checkInputMessage(forceTr(u'диагноз', 'EventEditDialog'), False, table, rowCount - 1, column)
                return False
            # Если необходимо проверять типы диагнозов для закрытого обращения
            if typeCheckEndDate is not None:
                # то выполнить проверку типов
                self.checkDiagnosticsType(table, typeCheckEndDate)
            # Проверить дналичие МКБ у всех записей текущей таблицы с диагностиками/осмотрами.
            for row, record in enumerate(table.model().items()):
                if not self.checkDiagnosticDataEntered(table, row, record, checkResult, endDate):
                    return False
            # Если обращение не закончено и нет замечательного права, проверяем, чтобы был хотя бы один диагноз
            if not QtGui.qApp.userHasRight(urNeedAtLeastOneDiagnosisInOpenEvent):
                if not table.model().items():
                    self.checkInputMessage(forceTr(u'диагноз', 'EventEditDialog'), False, table, 0, 0)
                    return False
        if not self.checkEventResult():
            return False
        return True

    def checkDiagnosticDataEntered(self, table, row, record, checkResult=True, endDate=None):
        MKB = forceString(record.value('MKB'))
        MKBEx = forceString(record.value('MKBEx'))
        result = MKB or self.checkInputMessage(forceTr(u'диагноз', 'EventEditDialog'), False, table, row,
                                               table.model().getColIndex('MKB'))
        if result:
            char = MKB[:1]
            traumaTypeId = forceRef(record.value('traumaType_id'))
            if char in 'ST' and not traumaTypeId:
                result = result and self.checkValueMessage(u'Необходимо указать тип травмы', True, table, row,
                                                           table.model().indexOf('traumaType_id'))
            elif char not in 'ST' and traumaTypeId:
                result = result and self.checkValueMessage(u'Необходимо удалить тип травмы', False, table, row,
                                                           table.model().indexOf('traumaType_id'))
            if char in 'ST' and (not MKBEx or MKBEx[0] not in 'VWXY'):
                result = result and self.checkValueMessage(u'Необходимо указать доп. МКБ из группы XX '
                                                           u'(выбрана группа XIX - травмы)', True, table, row,
                                                           table.model().indexOf('MKBEx'))
            if checkResult:
                result = result and self.checkDiagnosticResultEntered(table, row, record, endDate)

        result = result and self.checkDiagnosticDoctorEntered(table, row, record)
        return result

    def checkDiagnosticDoctorEntered(self, table, row, record):
        if forceRef(record.value('person_id')) is None:
            self.checkInputMessage(u'врача', False, table, row, record.indexOf('person_id'))
            return False
        else:
            return True

    def checkEventResult(self):
        result = True
        if hasattr(self, 'cmbResult') and not QtGui.qApp.userHasRight(urDoNotCheckResultAndMKB):
            result = self.eventDate.isNull() or self.cmbResult.value() or self.checkInputMessage(u'результат обращения',
                                                                                                 False, self.cmbResult)
            if not result:
                self.setFocusToWidget(self.cmbResult)
        return result

    def checkDiagnosticResultEntered(self, table, row, record, endDate):
        result = True
        if not endDate.isNull():
            if row == 0:
                resultId = forceRef(record.value('result_id'))
                result = (resultId or self.checkInputMessage(u'результат лечения', False, table, row,
                                                             table.model().getColIndex(
                                                                 'result_id')))  # record.indexOf('result_id')))
        return result

    def checkDiagnosticsType(self, table, endDate):
        model = table.model()
        if endDate:
            for record in model.items():
                if forceInt(record.value('diagnosisType_id')) == model.diagnosisTypeCol.ids[0]:
                    return True
        else:
            return True
        return self.checkValueMessage(u'Необходимо указать основной диагноз', True, table)

    def setIsDirty(self, dirty=True):
        CItemEditorBaseDialog.setIsDirty(self, dirty)
        if hasattr(self, 'btnPrint'):
            customizePrintButton(self.btnPrint, self.eventContext, dirty or not self.itemId())
            self._addActionPrintEventCost()
        self.emit(QtCore.SIGNAL('eventEditorSetDirty(bool)'), dirty)

    # Проверка на наличие услуг с частотой применения 1
    def checkMesNecessityEqOne(self, mesId):
        def getCheckType(eventTypeId):
            if getNeedMesPerformPercent(eventTypeId):
                if getEventControlMesNecessityEqOne(eventTypeId):
                    return 1
                else:
                    return 2
            else:
                if getEventControlMesNecessityEqOne(eventTypeId):
                    return 3
            return 0

        if hasattr(self, 'modelActionsSummary'):
            # param checkType:
            # 1 — все нижеприведенные типы
            # 2 — проверяем по needMesPerformPercent; Ошибка "Слишком мало услуг"
            # 3 — проверяем по mesRequired & 8; Всё, кроме ошибки "Слишком мало услуг"
            checkType = getCheckType(self.eventTypeId)
            if not checkType: return True

            # Список всех требуемых по МЭСу действий
            requiredAllActionTypeIdList = getActionTypeIdListByMesId(
                mesId)  # , date = self.eventSetDateTime.date() if self.eventSetDateTime else None)
            # Получение всех типов действий, частота применения которых по МЭС равна 1.0 сгруппированные по коду
            # (Тип действия привязан к услуге по полю ActionType.nomenclativeService_id)
            requiredActionTypeIdListByGroupCode = getActionTypeIdListByMesId(
                mesId,
                1.0,
                isGrouping=True,
                date=self.eventSetDateTime.date() if self.eventSetDateTime else None
            )

            # формирование списка всех требуемых услуг без учета группы
            requiredActionTypeIdList = []
            for idList in requiredActionTypeIdListByGroupCode.values():
                requiredActionTypeIdList.extend(idList)

            numReqActions = len(requiredActionTypeIdList)

            incorrectActionTypeIdList = []  # Список всех услуг ЧП = 1.0 г, у которых проблемы с датой и врачом
            existedActionTypeIdList = []  # Список всех имеющихся в событии услуг
            for item in self.modelActionsSummary.items():
                existedActionTypeId = forceRef(item.value('actionType_id'))
                EATStatus = forceInt(item.value('status'))
                EATorg_id = forceRef(item.value('org_id'))
                # i2172c9571 На условия фильтра не влияют экшены, которые были проведены не нами
                if (False  # EATStatus == 3
                    # #TODO:skkachaev:i2852. Правда ли, что нам в принципе во всех проверках надо учитывать отменённые?
                    or EATStatus == 6) and EATorg_id != self.orgId: continue
                existedActionTypeIdList.append(existedActionTypeId)
                # Проверка всех требуемых по МЭС действий на корректность (дату окончания и врача)
                if existedActionTypeId in requiredActionTypeIdList:
                    if not forceDate(item.value('endDate')).isValid() or item.value('person_id').isNull():
                        incorrectActionTypeIdList.append(existedActionTypeId)

                    # Поиск других типов действия той же группы
                    for groupCode in requiredActionTypeIdListByGroupCode.keys():
                        if not groupCode:
                            continue
                        # Если текущая услуга содержится в просматриваемой группе
                        if existedActionTypeId in requiredActionTypeIdListByGroupCode[groupCode]:
                            # То все услуги этой группы считать имеющимися
                            existedActionTypeIdList.extend(requiredActionTypeIdListByGroupCode[groupCode])

            existedActionTypeIdList = list(set(existedActionTypeIdList))
            excessActionTypeIdList = []  # Список "лишних" услуг, которых нет в списке услуг МЭС с ЧП = 1.0
            # Удаление из требуемых услуг всех имеющихся и отбор всех "лишних" услуг
            # "Лишняя" услуга - это услуга, которая есть в событии, есть в МЭСе, но его ЧП не равно 1.0
            for actionTypeId in existedActionTypeIdList:
                if (actionTypeId not in requiredActionTypeIdList
                    and actionTypeId not in excessActionTypeIdList
                    and actionTypeId in requiredAllActionTypeIdList):
                    excessActionTypeIdList.append(actionTypeId)
                while actionTypeId in requiredActionTypeIdList:
                    requiredActionTypeIdList.remove(actionTypeId)

            if (checkType == 3 or not requiredActionTypeIdList) and (
                            checkType == 2 or (not incorrectActionTypeIdList and not excessActionTypeIdList)):
                return True

            errorMessageList = []
            numDoneActions = numReqActions - len(requiredActionTypeIdList)
            if checkType == 2:
                if numDoneActions < math.floor(numReqActions * getNeedMesPerformPercent(self.eventTypeId) / 100):
                    errorMessageList.append(
                        u'Данное обращение не подходит под тип "%s" (малое количество мероприятий)' % getEventTypeName(
                            self.eventTypeId))
                else:
                    return True
            elif checkType == 1:
                if numDoneActions < math.floor(numReqActions * getNeedMesPerformPercent(self.eventTypeId) / 100):
                    errorMessageList.append(
                        u'Данное обращение не подходит под тип "%s" (малое количество мероприятий)' % getEventTypeName(
                            self.eventTypeId))
            errorMessageList.append(u'Обнаружены несоответствия выбранному %s.' % forceTr(u'МЭС', u'EventEditDialog'))

            if checkType == 1 or checkType == 3:
                tableActionType = QtGui.qApp.db.table('ActionType')

                if excessActionTypeIdList:
                    excessActionTypeNames = QtGui.qApp.db.getColumnValues(tableActionType,
                                                                          tableActionType['name'],
                                                                          where=tableActionType['id'].inlist(
                                                                              excessActionTypeIdList))
                    excessActionTypeNames.insert(0, u'Необходимо УДАЛИТЬ следующие услуги:')
                    errorMessageList.append(u'\n\t-'.join(excessActionTypeNames))

                if incorrectActionTypeIdList:
                    incorrectActionTypeNames = QtGui.qApp.db.getColumnValues(tableActionType,
                                                                             tableActionType['name'],
                                                                             where=tableActionType['id'].inlist(
                                                                                 incorrectActionTypeIdList))
                    incorrectActionTypeNames.insert(0,
                                                    u'Необходимо указать дату окончания/выполнения и врача-исполнителя для следующих услуг:')
                    errorMessageList.append(u'\n\t-'.join(incorrectActionTypeNames))

            return self.checkValueMessage(u'\n\nА также\n'.join(errorMessageList), False, None)
        else:
            return self.checkValueMessage(
                u'Невозможно проверить наличие услуг с част. прим. = 1\nпри отсутствии списка всех услуг', False, None)

    # TODO: atronah: diagnosisTypeCol - на самом деле diagnosisTypeId
    def checkMKBForMes(self, tableFinalDiagnostics, SPR69_id, diagnosisTypeCol):
        finalDiagnosis = False
        model = tableFinalDiagnostics.model()
        db = QtGui.qApp.db
        table = db.table('mes.SPR69')
        if SPR69_id:
            for row, record in enumerate(model.items()):
                if forceInt(record.value('diagnosisType_id')) == diagnosisTypeCol:
                    MKB = forceString(record.value('MKB'))
                    if MKB:
                        finalDiagnosis = True
                        recordSPR69 = db.getRecordEx(
                            table,
                            '*',
                            db.joinAnd([
                                table['id'].eq(SPR69_id),
                                db.joinOr([table['MKBX'].eq(''), u''' '%s' LIKE SPR69.MKBX''' % (MKB)])
                            ])
                        )

                        if not (bool(recordSPR69) or self.checkValueMessage(
                                    u'Несоответствие шифра МКБ заключительного диагноза %s требованиям %s' % (
                                        MKB,
                                        forceTr(u'МЭС', u'EventEditDialog')
                                ),
                                True,
                                tableFinalDiagnostics,
                                row,
                                record.indexOf('MKB')
                        )):
                            return False, finalDiagnosis
        return True, finalDiagnosis

    def checkCompulsoryService(self, actionTypesIdList, eventTypeId, mesId=None):
        compulsoryService = []
        recordMesList = []
        compulsoryIdList = []

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        if mesId:
            table = db.table('mes.MES_service')
            tableMrbService = db.table('mes.mrbService')
            tableService = db.table('rbService')

            queryTable = table.innerJoin(tableMrbService, table['service_id'].eq(tableMrbService['id']))
            queryTable = queryTable.innerJoin(tableService, tableMrbService['code'].eq(tableService['code']))
            queryTable = queryTable.innerJoin(tableActionType,
                                              tableService['id'].eq(tableActionType['nomenclativeService_id']))

            cond = [table['selectionGroup'].eq(1),
                    table['master_id'].eq(mesId),
                    tableActionType['deleted'].eq(0),
                    tableMrbService['deleted'].eq(0),
                    table['deleted'].eq(0)]

            if actionTypesIdList:
                cond.append(tableActionType['id'].notInlist(actionTypesIdList))

            recordMesList = db.getRecordList(queryTable,
                                             cols=[tableActionType['id'], tableActionType['code'],
                                                   tableActionType['name']],
                                             where=cond,
                                             group=[tableActionType['id']])

        tableEventTypeAction = db.table('EventType_Action')

        cond = [tableEventTypeAction['eventType_id'].eq(eventTypeId),
                tableEventTypeAction['isCompulsory'].eq(1),
                tableActionType['deleted'].eq(0)]

        if actionTypesIdList:
            cond.append(tableActionType['id'].notInlist(actionTypesIdList))
        recordEventTypeList = db.getRecordList(tableEventTypeAction.innerJoin(tableActionType, tableActionType['id'].eq(
            tableEventTypeAction['actionType_id'])),
                                               cols=[tableActionType['id'], tableActionType['code'],
                                                     tableActionType['name']],
                                               where=cond,
                                               group=tableActionType['id'])
        recordList = recordMesList + recordEventTypeList
        for record in list(recordList):
            id = forceRef(record.value('id'))
            if id not in compulsoryIdList:
                compulsoryIdList.append(id)
                serviceCodeName = forceStringEx(record.value('code')) + '|' + forceString(record.value('name'))
                compulsoryService.append(serviceCodeName)
        if compulsoryService:
            endDate = self.edtEndDate.date() if self._isClosedEventCheck and hasattr(self,
                                                                                     'edtEndDate') else QtCore.QDate()
            if not endDate.isNull():
                QtGui.QMessageBox.critical(
                    None,
                    u'Внимание',
                    u'В обращении отсутствуют обязательные услуги: %s' % ', '.join(sorted(compulsoryService)),
                    QtGui.QMessageBox.Ok
                )
            return False
        return True

    def checkComplexService(self, actionTypesIdList, eventTypeId, mesId=None):
        if not actionTypesIdList:
            return True
        compulsoryService = []
        recordMesList = []
        actionTypesId = ', '.join([forceStringEx(actionTypeId) for actionTypeId in actionTypesIdList])

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        if mesId:
            table = db.table('mes.MES_service')
            tableMrbService = db.table('mes.mrbService')
            tableService = db.table('rbService')

            queryTable = table.innerJoin(tableMrbService, table['service_id'].eq(tableMrbService['id']))
            queryTable = queryTable.innerJoin(tableService, tableMrbService['code'].eq(tableService['code']))
            queryTable = queryTable.innerJoin(tableActionType,
                                              tableService['id'].eq(tableActionType['nomenclativeService_id']))

            cond = [table['master_id'].eq(mesId),
                    tableActionType['deleted'].eq(0),
                    '''mes.MES_service.selectionGroup IN (SELECT DISTINCT ms.selectionGroup
                                                          FROM mes.MES_service ms
                                                            INNER JOIN mes.mrbService rs ON ms.service_id = rs.id
                                                            INNER JOIN rbService s ON s.code = rs.code
                                                            INNER JOIN ActionType at ON at.nomenclativeService_id = s.id
                                                          WHERE at.id IN (%s) AND ms.master_id = MES_service.master_id AND ms.selectionGroup < 0)''' % actionTypesId]
            if actionTypesIdList:
                cond.append(tableActionType['id'].notInlist(actionTypesIdList))

            recordMesList = db.getRecordList(queryTable,
                                             cols=[tableService['code'], tableService['name']],
                                             where=cond)

        tableEventTypeAction = db.table('EventType_Action')

        cond = [tableEventTypeAction['eventType_id'].eq(eventTypeId),
                '''EventType_Action.selectionGroup IN (SELECT DISTINCT selectionGroup
                                                       FROM EventType_Action eta
                                                       WHERE eta.actionType_id IN (%s)
                                                            AND eta.eventType_id = EventType_Action.eventType_id
                                                            AND eta.selectionGroup < 0)''' % actionTypesId]

        if actionTypesIdList:
            cond.append(tableActionType['id'].notInlist(actionTypesIdList))
        recordEventTypeList = db.getRecordList(tableEventTypeAction.innerJoin(tableActionType, tableActionType['id'].eq(
            tableEventTypeAction['actionType_id'])),
                                               cols=[tableActionType['code'], tableActionType['name']],
                                               where=cond)
        recordList = set(recordMesList) | set(recordEventTypeList)
        for record in list(recordList):
            serviceCodeName = forceStringEx(record.value('code')) + '|' + forceString(record.value('name'))
            compulsoryService.append(serviceCodeName)
        if compulsoryService:
            QtGui.QMessageBox.critical(None,
                                       u'Внимание',
                                       u'В комплекс услуг необходимо добавить: %s' % ', '.join(
                                           sorted(compulsoryService)),
                                       QtGui.QMessageBox.Ok)
            return False
        return True

    def checkActionsDateEnteredActuality(self, begDate, endDate, tabList):
        skippable = isEventAnyActionDatePermited(self.eventTypeId)
        result = True
        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        cols = [table['actuality']]
        for actionTab in tabList:
            model = actionTab.tblAPActions.model()
            for row, (record, action) in enumerate(model.items()):
                if action and action._actionType.id:
                    rowEndDate = forceDate(record.value('endDate'))
                    if rowEndDate:
                        actuality = 0
                        actionTypeId = action._actionType.id
                        if self.eventTypeId and actionTypeId:
                            cond = [table['eventType_id'].eq(self.eventTypeId),
                                    table['actionType_id'].eq(actionTypeId)
                                    ]
                            recordActuality = db.getRecordEx(table, cols, cond, 'EventType_Action.eventType_id')
                            if recordActuality:
                                actuality = forceInt(recordActuality.value(0))
                        if endDate and rowEndDate > endDate and not action._actionType.isIgnoreEventExecDate:
                            boxRes = self.checkValueMessageIgnoreAll(
                                u'Дата выполнения должна быть не позже %s ( с учетом срока "годности" данных)' % forceString(
                                    endDate), skippable, actionTab.tblAPActions, row, 0, actionTab.edtAPEndDate)
                            result = result and boxRes
                            if boxRes == 2:
                                break
                        lowDate = begDate.addMonths(-actuality)
                        # Мероприятия могут быть с датами начала-закрытия сильно предшествующими датам начала-закрытия события,
                        # например, флюшка в обращении 01.01.2014-02.02.2014 может быть сделана 06.06.2013-07.07.2013
                        # и быть действительной, если не прошло 6 мес.
                        if rowEndDate < lowDate:
                            boxRes = self.checkValueMessageIgnoreAll(
                                u'Дата выполнения должна быть не раньше %s( с учетом срока "годности" данных)' % forceString(
                                    lowDate), skippable, actionTab.tblAPActions, row, 0, actionTab.edtAPEndDate)
                            result = result and boxRes
                            if boxRes == 2:
                                break
        return result

    def checkActionProperties(self, tab, action, tblAPProps, actionRow=None):
        def isNull(val, typeName):
            if val is None:
                return True
            if type(val) in [QtCore.QString, str, unicode]:
                if typeName == 'ImageMap':
                    return not 'object' in val
                if typeName == 'Html':
                    edt = QtGui.QTextEdit()
                    edt.setHtml(val)
                    val = edt.toPlainText()
                if not forceStringEx(val):
                    return True
            if type(val) == list:
                if len(val) == 0:
                    return True
            if type(val) == QtCore.QDate:
                return not val.isValid()
            return False

        def clrJobTickets(action):
            db = QtGui.qApp.db
            tblProp = db.table('ActionProperty')
            tblJobTicket = db.table('Job_Ticket')
            for prop in action._properties:
                if prop._type.typeName == u'JobTicket':
                    recTicket = db.getRecordEx(tblJobTicket, '*', tblJobTicket['id'].eq(prop._value))
                    if recTicket:
                        recTicket.setNull('person_id')
                        recTicket.setNull('begDateTime')
                        recTicket.setNull('endDateTime')
                        recTicket.setNull('resConnectionId')
                        recTicket.setNull('resTimestamp')
                        recTicket.setValue('status', toVariant(0))
                        db.updateRecord(tblJobTicket, recTicket)
                        if action._properties[0]._record:
                            recProp = db.getRecordEx(tblProp, '*', forceInt(action._properties[0]._record.value('id')))
                            if recProp:
                                db.deleteRecord(tblProp, tblProp['id'].eq(forceInt(action._properties[0]._record.value('id'))))

        actionType = action.getType()
        propertyTypeList = actionType.getPropertiesById().items()
        propertyTypeList.sort(key=lambda x: (x[1].idx, x[0]))
        propertyTypeList = [x[1] for x in propertyTypeList if x[1].applicable(self.clientSex, self.clientAge)]

        for row, propertyType in enumerate(propertyTypeList):
            penalty = propertyType.penalty
            if not forceInt(action._record.value('status')) == 3 and penalty == 666:
                continue
            needChecking = penalty > 0
            if needChecking:
                skippable = penalty < 100
                if forceInt(action._record.value('status')) == 3 and penalty == 666:
                    if QtGui.qApp.userHasRight(urSkipCheckCancelationReason):
                        skippable = True
                    else:
                        skippable = False
                    clrJobTickets(action)
                elif forceInt(action._record.value('status')) == 3:
                    clrJobTickets(action)


                property = action.getPropertyById(propertyType.id)
                if isNull(property._value, propertyType.typeName) and (not forceInt(action._record.value('status')) == 3 or penalty == 666):
                    actionTypeName = action._actionType.name
                    propertyTypeName = propertyType.name
                    if actionRow is not None:
                        tab.tblAPActions.setCurrentIndex(tab.tblAPActions.model().createIndex(actionRow, 0))
                    for idx, prop in enumerate(tblAPProps.model()._rowDataList):
                        if prop.name == propertyTypeName:
                            row = idx
                            break

                    if actionTypeName in [u'форма 090/у']:
                        actName = u'поле'
                    else:
                        actName = u'действии'

                    result = self.checkValueMessage(
                        u'Необходимо заполнить значение поля "{propType}" в {actName} "{actType}"'.format(
                            propType=propertyTypeName, actName=actName, actType=actionTypeName
                        ),
                        skippable,
                        tblAPProps,
                        row,
                        1
                    )
                    if not result:
                        return result
        return True

    def checkVisitsDataEntered(self, begDate, endDate):
        if hasattr(self, 'modelVisits'):
            if hasattr(self, 'cmbGoal') and endDate:
                visitCount = forceStringEx(QtGui.qApp.db.translate('rbEventGoal',
                                                                   'id',
                                                                   self.cmbGoal.value(),
                                                                   'visitCount'))
                if '-' in visitCount:
                    leftCount, rightCount = visitCount.split('-')
                    leftCount = forceInt(leftCount.strip())
                    rightCount = forceInt(rightCount.strip())
                    itemsCount = len(self.modelVisits.items())
                    # atronah: надеюсь, разберетесь, что я хотел) вроде весело и понятно)
                    if not ((leftCount or itemsCount) <= itemsCount <= (rightCount or itemsCount)):
                        return self.checkValueMessage(
                            u'Для закрытия обращения необходимо %s-%s посещений' % (leftCount, rightCount),
                            QtGui.qApp.userHasRight(urIgnoreVisitCountCheck),
                            self.tblVisits if hasattr(self, 'cmbGoal') else None)
            visitsServiceIdList = []
            for row, record in enumerate(self.modelVisits.items()):
                if not self.checkVisitDataEntered(begDate, endDate, row, record):
                    return False
                if not self.checkDoubleVisitsEntered(row, record):
                    return False
                serviceId = forceRef(record.value('service_id'))
                if not serviceId in visitsServiceIdList:
                    visitsServiceIdList.append(serviceId)
            if getEventAidTypeCode(self.eventTypeId) == '7' and len(visitsServiceIdList) > 1:
                if not self.checkValueMessage(u'У визитов разные профили оплаты. Отредактировать по первому визиту?',
                                              True, None):
                    serviceId = visitsServiceIdList[0]
                    for record in self.modelVisits.items():
                        record.setValue('service_id', toVariant(serviceId))
        return True

    def checkVisitDataEntered(self, begDate, endDate, row, record):
        result = True
        date = forceDate(record.value('date'))
        currentDate = QtCore.QDate.currentDate()
        possibleDeathDate = QtCore.QDate()
        if self.clientBirthDate:
            possibleDeathDate = self.clientBirthDate.addYears(QtGui.qApp.maxLifeDuration)
        result = result and (
            not date.isNull() or self.checkInputMessage(u'дату', False, self.tblVisits, row, record.indexOf('date')))
        result = result and (date <= currentDate or self.checkValueMessage(
            u'Датa посещения %s не может быть позже текущей даты %s' % (forceString(date), forceString(currentDate)),
            False, self.tblVisits, row, record.indexOf('date')))
        result = result and (begDate <= date or self.checkUpdateMessage(
            u'Датa посещения %s предшествует дате назначения %s.\nИзменить дату назначения на %s?' % (
                forceString(date), forceString(begDate), forceString(date)), self.edtBegDate, self.tblVisits, date, row,
            record.indexOf('date')))
        if endDate:
            result = result and (date <= endDate or self.checkValueMessage(
                u'Датa посещения %s после даты завершения %s' % (forceString(date), forceString(endDate)), False,
                self.tblVisits, row, record.indexOf('date')))
        if self.clientBirthDate:
            result = result and (date >= self.clientBirthDate or self.checkValueMessage(
                u'Дата посещения %s не может быть раньше даты рождения пациента %s' % (
                    forceString(date), forceString(self.clientBirthDate)), False, self.tblVisits, row,
                record.indexOf('date')))
        if self.clientDeathDate:
            result = result and (date <= self.clientDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                u'Дата посещения %s не может быть позже имеющейся даты смерти пациента %s' % (
                    forceString(date), forceString(self.clientDeathDate)), False, self.tblVisits, row,
                record.indexOf('date')))
        if possibleDeathDate:
            result = result and (date <= possibleDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                u'Дата посещения %s не может быть позже возможной даты смерти пациента %s' % (
                    forceString(date), forceString(possibleDeathDate)), False, self.tblVisits, row,
                record.indexOf('date')))
        result = result and (
            forceRef(record.value('finance_id')) or self.checkInputMessage(u'тип финансирования', False, self.tblVisits,
                                                                           row, record.indexOf('finance_id')))
        return result

    def checkDoubleVisitsEntered(self, row, record):
        result = True
        eventId = self.itemId()
        serviceId = forceRef(record.value('service_id'))
        date = forceDate(record.value('date'))
        currentVisitId = forceRef(record.value('id'))
        nameService = u''
        currentVisitIdList = []
        if serviceId and date and (self.eventSetDateTime.date() <= date):
            db = QtGui.qApp.db
            nameService = forceString(db.translate('rbService', 'id', serviceId, 'code'))
            if currentVisitId:
                for rowVisits, recordVisits in enumerate(self.modelVisits.items()):
                    visitId = forceRef(recordVisits.value('id'))
                    if forceRef(recordVisits.value('service_id')) == serviceId and forceDate(
                            recordVisits.value('date')) == date and visitId != currentVisitId:
                        if visitId not in currentVisitIdList:
                            currentVisitIdList.append(visitId)
                        result = result and self.checkValueMessage(
                            u'Посещение %s с услугой %s не уникально в данном событии' % (
                                forceString(date), nameService), True, self.tblVisits, row,
                            record.indexOf('service_id'))
                        if not result:
                            return result
            else:
                checkQuantity = 0
                for rowVisits, recordVisits in enumerate(self.modelVisits.items()):
                    if forceRef(recordVisits.value('service_id')) == serviceId and forceDate(
                            recordVisits.value('date')) == date:
                        if checkQuantity > 0:
                            result = result and self.checkValueMessage(
                                u'Посещение %s с услугой %s не уникально в данном событии' % (
                                    forceString(date), nameService), True, self.tblVisits, row,
                                record.indexOf('service_id'))
                            if not result:
                                return result
                        checkQuantity += 1
            if self.clientId:
                tableEvent = db.table('Event')
                tableVisit = db.table('Visit')
                tableEventType = db.table('EventType')
                tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
                cols = [tableVisit['id'],
                        tableVisit['date'],
                        tableVisit['service_id'],
                        tableEventType['name'].alias('nameEventType'),
                        tableEvent['setDate'],
                        tableEvent['execDate'],
                        tableVrbPersonWithSpeciality['name'].alias('namePerson')
                        ]
                table = tableEvent.innerJoin(tableVisit, tableVisit['event_id'].eq(tableEvent['id']))
                table = table.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
                table = table.innerJoin(tableVrbPersonWithSpeciality,
                                        tableVrbPersonWithSpeciality['id'].eq(tableEvent['execPerson_id']))
                condEvents = [tableVisit['date'].eq(date),
                              tableVisit['service_id'].eq(serviceId),
                              tableEvent['client_id'].eq(self.clientId),
                              tableEvent['deleted'].eq(0),
                              tableVisit['deleted'].eq(0),
                              tableEventType['deleted'].eq(0)
                              ]
                if eventId:
                    condEvents.append(tableEvent['id'].ne(eventId))
                if currentVisitIdList != []:
                    condEvents.append(tableVisit['id'].notInlist(currentVisitIdList))
                recordListEvents = db.getRecordList(table, cols, condEvents, 'Event.eventType_id')
                visitId = None
                for recordEvents in recordListEvents:
                    if currentVisitId:
                        visitId = forceRef(recordEvents.value('id'))
                        if visitId != currentVisitId:
                            result = result and self.checkValueMessage(
                                u'Посещение %s с услугой %s не уникально.\n'
                                u'И находится в событии: %s за период с %s по %s ответственный %s' % (
                                    forceString(date), nameService, forceString(recordEvents.value('nameEventType')),
                                    forceString(recordEvents.value('setDate')),
                                    forceString(recordEvents.value('execDate')),
                                    forceString(recordEvents.value('namePerson'))), True, self.tblVisits, row,
                                record.indexOf('service_id'))
                            if not result:
                                return result
                    else:
                        if forceRef(recordEvents.value('service_id')) == serviceId and forceDate(
                                recordEvents.value('date')) == date:
                            result = result and self.checkValueMessage(
                                u'Посещение %s с услугой %s не уникально.\n'
                                u'И находится в событии: %s за период с %s по %s ответственный %s' % (
                                    forceString(date), nameService, forceString(recordEvents.value('nameEventType')),
                                    forceString(recordEvents.value('setDate')),
                                    forceString(recordEvents.value('execDate')),
                                    forceString(recordEvents.value('namePerson'))), True, self.tblVisits, row,
                                record.indexOf('service_id'))
                            if not result:
                                return result
        return result

    def checkEventDate(self, directionDate, endDate, nextDate, widget, widgetNextDate, widgetEndDate=None,
                       boolEvent=False, row=None, column=None):
        result = True
        if nextDate and directionDate:
            result = result and (nextDate >= directionDate or self.checkValueMessage(
                u'Дата следующей явки %s не должна быть раньше даты назначения %s' % (
                    forceString(nextDate), forceString(directionDate)), False, widget, row, column, widgetNextDate))
            result = result and (nextDate != directionDate or self.checkValueMessage(
                u'Дата следующей явки %s не должна быть равна дате назначения %s' % (
                    forceString(nextDate), forceString(directionDate)), False, widget, row, column, widgetNextDate))
        if nextDate and endDate:
            result = result and (nextDate >= endDate or self.checkValueMessage(
                u'Дата следующей явки %s не должна быть раньше даты выполнения %s' % (
                    forceString(nextDate), forceString(endDate)), False, widget, row, column, widgetNextDate))
            result = result and (nextDate != endDate or self.checkValueMessage(
                u'Дата следующей явки %s не должна быть равна дате выполнения %s' % (
                    forceString(nextDate), forceString(endDate)), False, widget, row, column, widgetNextDate))
        directionDate = QtCore.QDate.currentDate()
        if boolEvent:
            if self.orgId == QtGui.qApp.currentOrgId():
                if endDate and directionDate:
                    result = result and (endDate <= directionDate or self.checkValueMessage(
                        u'Дата выполнения %s не должна быть позже текущей даты %s' % (
                            forceString(endDate), forceString(directionDate)), True, widget, row, column,
                        widgetEndDate))
        else:
            if endDate and directionDate:
                result = result and (endDate <= directionDate or self.checkValueMessage(
                    u'Дата выполнения %s не должна быть позже текущей даты %s' % (
                        forceString(endDate), forceString(directionDate)), True, widget, row, column, widgetEndDate))
        return result

    # Проверка на соответствие договора и типа финансирования классу ВМП (высокотехнологичная мед.помощь)
    def checkOncologyHTMH(self, action, actionId, financeId):
        result = True
        actionTypeItem = action.getType()
        if actionTypeItem and (
                    u'leaved' in actionTypeItem.flatCode.lower()) and actionTypeItem.containsPropertyWithName(u'Квота'):
            leavedQuotaTypeId = forceRef(
                QtGui.qApp.db.translate('Client_Quoting', 'id', action[u'Квота'], 'quotaType_id'))
            leavedQuotaCode = forceString(QtGui.qApp.db.translate('QuotaType', 'id', leavedQuotaTypeId, 'code'))
            if leavedQuotaCode[0:2] == '09':
                contractNumber = forceString(QtGui.qApp.db.translate('Contract', 'id', self.contractId, 'number'))
                result = result and (contractNumber.find(u'ВМП') >= 0 or self.checkValueMessage(
                    u'Для данного события неверно определен договор', True, self.cmbContract, 0, 0))
                financeName = forceString(QtGui.qApp.db.translate('rbFinance', 'id', financeId, 'name'))
                result = result and (financeName.find(u'целевой') >= 0 or self.checkValueMessage(
                    u'Для данного события неверно определен тип финансирования услуги "выписка"', True,
                    self.tabCash.tblAccActions, 0, 0))
        return result

    def checkActionsDataEntered(self, tabList, eventDirectionDate, eventEndDate):
        eventId = self.itemId()
        skipDateCheck = False
        for actionTab in tabList:
            model = actionTab.tblAPActions.model()
            for row, (record, action) in enumerate(model.items()):
                if action and action._actionType.id:
                    actionTypeItem = action.getType()
                    nameActionType = action._actionType.name  # название типа действия
                    status = forceInt(record.value('status'))
                    directionDate = forceDate(record.value('directionDate'))
                    begDate = forceDate(record.value('begDate'))
                    endDate = forceDate(record.value('endDate'))
                    actionId = forceRef(record.value('id'))
                    if len(nameActionType) > 0:
                        strNameActionType = u': ' + nameActionType
                    else:
                        strNameActionType = u''
                    if actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()):
                        begDateTime = forceDateTime(record.value('begDate'))
                        endDateTime = forceDateTime(record.value('endDate'))
                        if not self.checkDateActionsMoving(model, begDateTime, endDateTime, actionTab.tblAPActions, row,
                                                           0, actionTab.edtAPBegDate):
                            return False
                        if not forceRef(record.value('MES_id')) and not (
                                    QtGui.qApp.userHasRight(urSaveMovingWithoutMes) or (self.saveMovingWithoutMes)):
                            self.checkValueMessage(u'Необходимо указать стандарт для действия "Движение"', False,
                                                   actionTab.tblAPActions, row, 0, actionTab.cmbActionMes)
                            return False
                        for i in xrange(len(action._properties)):
                            if action._properties[i]._type.typeName.lower() == (u'HospitalBed').lower():
                                if not self.checkMovingBeds(self.clientId, eventId, actionId,
                                                            forceDateTime(action._record.value('begDate')),
                                                            forceDateTime(action._record.value('endDate')),
                                                            actionTab.tblAPActions, row, 0, actionTab.edtAPBegDate):
                                    return False
                    if eventEndDate and not begDate:
                        self.checkValueMessage(u'Должна быть указана дата начала действия%s' % (strNameActionType),
                                               False, actionTab.tblAPActions, row, 0, actionTab.edtAPBegDate)
                        return False
                    if not self.checkOncologyHTMH(action, actionId, forceRef(record.value('finance_id'))):
                        return False
                    if not self.checkActionDataEntered(directionDate, begDate, endDate, actionTab.tblAPActions,
                                                       actionTab.edtAPDirectionDate, actionTab.edtAPBegDate,
                                                       actionTab.edtAPEndDate, row, 0):
                        return False
                    if not self.checkEventDate(directionDate, endDate, None, actionTab.tblAPActions, None,
                                               actionTab.edtAPEndDate, False, row, 0):
                        return False
                    if not skipDateCheck:
                        boxRes = self.checkEventActionDateEntered(eventDirectionDate, eventEndDate, status,
                                                                  directionDate, begDate, endDate,
                                                                  actionTab.tblAPActions, actionTab.edtAPEndDate,
                                                                  actionTab.edtAPBegDate, row, 0, nameActionType,
                                                                  actionTypeItem)
                        if not boxRes:
                            return False
                        elif boxRes == 2:
                            skipDateCheck = True
                    if eventEndDate and not endDate and status == 0 and actionTypeItem.isExecRequiredForEventExec:  # статус: начато
                        if not self.checkActionEndDate(strNameActionType, actionTab.tblAPActions, row, 0,
                                                       actionTab.edtAPEndDate):
                            return False
                    if not self.checkActionProperties(actionTab, action, actionTab.tblAPProps, row):
                        return False
                    if not self.checkExistsActionsForCurrentDay(row, record, action, actionTab):
                        return False
                    if not self.checkActionMorphology(row, record, action,
                                                      actionTab.tblAPActions, actionTab.cmbAPMorphologyMKB):
                        return False

        if not self.checkOncologyForm90():
            return False
        return True

    def checkRecommendationsDataEntered(self):
        db = QtGui.qApp.db
        stmt = u'''
            SELECT
                Recommendation.setDate AS date,
                vrbPerson.name AS person
            FROM
                Recommendation
                INNER JOIN vrbPerson ON Recommendation.person_id = vrbPerson.id
                INNER JOIN Event ON Recommendation.setEvent_id = Event.id
                INNER JOIN ActionType ON Recommendation.actionType_id = ActionType.id
            WHERE
                Event.client_id = %s
                AND Recommendation.actionType_id = %s
                AND DATE(NOW()) <= DATE_ADD(Recommendation.setDate, INTERVAL ActionType.recommendationExpirePeriod DAY)
            LIMIT 1
        '''
        items = self.tabRecommendations.modelRecommendations.items()
        for row, record in enumerate(items):
            if record.value('id').isNull():
                actionTypeId = forceRef(record.value('actionType_id'))
                actionType = CActionTypeCache.getById(actionTypeId)
                query = db.query(stmt % (self.clientId, forceString(actionTypeId)))
                if query.next():
                    existingRecord = query.record()
                    person = forceString(existingRecord.value('person'))
                    date = forceString(existingRecord.value('date'))
                    self.checkValueMessage(
                        u'Направления: услуга ' + actionType.code + u'|' + actionType.name + u' была рекомендована врачом ' + person + u' и ' + date,
                        False, self.tabRecommendations.tblRecommendations, row=row,
                        column=self.tabRecommendations.modelRecommendations.getColIndex('actionType_id'))
                    return False
        return True

    def checkActionMorphology(self, row, record, action, tblAPActions, cmbAPMorphologyMKB):
        status = forceInt(record.value('status'))
        if QtGui.qApp.defaultMorphologyMKBIsVisible() and (status in [2, 4]):
            actionTypeItem = action.getType()
            defaultMorphology = actionTypeItem.defaultMKB
            isMorphologyRequired = actionTypeItem.isMorphologyRequired
            morphologyMKB = forceString(record.value('morphologyMKB'))
            if not cmbAPMorphologyMKB.isValid(morphologyMKB) and defaultMorphology > 0 and isMorphologyRequired > 0:
                if status == 4 and isMorphologyRequired == 2:
                    return True
                skippable = True if isMorphologyRequired == 1 else False
                message = u'Необходимо ввести корректную морфологию диагноза действия `%s`' % actionTypeItem.name
                return self.checkValueMessage(message, skippable, tblAPActions, row, 0, cmbAPMorphologyMKB)
        return True

    def checkExistsActionsForCurrentDay(self, row, record, action, actionTab):
        return True

    def checkDateActionsMoving(self, model, begDateAction, endDateAction, widget, rowAction, column, widgetBegDate):
        for row, (record, action) in enumerate(model.items()):
            if action and action._actionType.id:
                actionTypeItem = action.getType()
                if actionTypeItem and (u'moving' in actionTypeItem.flatCode.lower()) and row != rowAction:
                    begDate = forceDateTime(record.value('begDate'))
                    endDate = forceDateTime(record.value('endDate'))
                    if (not begDateAction and not endDateAction) or (not begDate and not endDate) or (
                                    begDateAction and ((not begDate) or begDateAction >= begDate) and (
                                        (not endDate) or begDateAction < endDate)) or (
                                        endDateAction and begDate and (endDateAction > begDate) and (
                                        (not endDate) or endDateAction <= endDate)) or (
                                    begDateAction and ((not begDate) or begDateAction <= begDate) and (
                                        ((not endDateAction) and (not endDate)) or (
                                                        endDateAction and endDate and endDateAction >= endDate and endDate > begDateAction))):
                        return self.checkValueMessage(
                            u'Попытка ввести период (%s - %s) пересекающийся с уже имеющимся (%s - %s)' % (
                                forceString(begDateAction), forceString(endDateAction), forceString(begDate),
                                forceString(endDate)), False, widget, rowAction, column, widgetBegDate)
        return True

    def checkMovingBeds(self, clientId, eventId, actionId, begDate, endDate, widget, rowAction, column, widgetBegDate):
        if hasattr(self, 'gbLittleStrangerFlag') and self.gbLittleStrangerFlag.isChecked():
            return True
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')

        cond = [tableActionType['flatCode'].like(u'moving%'),
                tableAction['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableAP['deleted'].eq(0),
                tableActionType['deleted'].eq(0),
                tableOS['deleted'].eq(0),
                tableClient['deleted'].eq(0),
                tableAPT['deleted'].eq(0),
                tableAPT['typeName'].like('HospitalBed'),
                tableAP['action_id'].eq(tableAction['id'])
                ]
        if begDate and endDate:
            whereDate = db.joinOr([db.joinAnd([tableAction['begDate'].ge(begDate), tableAction['begDate'].lt(endDate)]),
                                   db.joinAnd([tableAction['endDate'].gt(begDate), tableAction['endDate'].le(endDate)]),
                                   db.joinAnd(
                                       [tableAction['begDate'].le(begDate), tableAction['endDate'].ge(endDate)])])
        elif (not endDate) and begDate:
            whereDate = db.joinOr([db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()]),
                                   db.joinAnd([tableAction['begDate'].isNotNull(),
                                               db.joinOr([tableAction['begDate'].ge(begDate),
                                                          db.joinAnd([tableAction['begDate'].lt(begDate),
                                                                      db.joinOr([tableAction['endDate'].isNull(),
                                                                                 tableAction['endDate'].gt(
                                                                                     begDate)])])])]),
                                   db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(),
                                               tableAction['endDate'].gt(begDate)])
                                   ])
        elif endDate and (not begDate):
            whereDate = db.joinOr([db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()]),
                                   db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].lt(endDate)]),
                                   tableAction['begDate'].isNull()])
        else:
            whereDate = u''
        if len(whereDate) > 0:
            cond.append(whereDate)
        eventClientId = None
        if actionId:
            cond.append(tableAction['id'].ne(actionId))
            if not eventId:
                queryTableParams = tableAction.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                recordEvent = db.getRecordEx(queryTableParams, [tableEvent['client_id'], tableEvent['id']],
                                             [tableAction['id'].eq(actionId), tableEvent['deleted'].eq(0),
                                              tableAction['deleted'].eq(0)])
                eventId = forceRef(recordEvent.value('id'))
                eventClientId = forceRef(recordEvent.value('client_id'))
        if eventId and not eventClientId:
            recordEvent = db.getRecordEx(tableEvent, [tableEvent['client_id']],
                                         [tableEvent['id'].eq(eventId), tableEvent['deleted'].eq(0)])
            clientId = forceRef(recordEvent.value(0))
        elif eventId and eventClientId:
            clientId = eventClientId
        if eventId:
            cond.append(tableEvent['id'].ne(eventId))
        if not clientId:
            clientId = QtGui.qApp.currentClientId()
        if clientId:
            cond.append(tableEvent['client_id'].eq(clientId))
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            record = db.getRecordEx(queryTable,
                                    [u'COUNT(DISTINCT %s) AS countAll' % tableEvent['id'].name(),
                                     u'COUNT(%s) AS countLittleStranger' % tableEvent['littleStranger_id'].name()],
                                    cond)
        if forceInt(record.value('countAll')) > 0 and forceInt(record.value('countLittleStranger')) == 0:
            return self.checkValueMessage(u'Пациент уже занимает койку в этом периоде', False, widget, rowAction,
                                          column, widgetBegDate)
        return True

    def checkEventActionDateEntered(self, eventDirectionDate, eventEndDate, status, actionDirectionDate, actionBegDate,
                                    actionEndDate, widget, widgetEndDate=None, widgetBegDate=None, row=None,
                                    column=None, nameActionType=u'', actionTypeItem=None):
        skippable = isEventAnyActionDatePermited(self.eventTypeId)
        result = True
        if eventDirectionDate and actionDirectionDate:
            if actionBegDate:
                result = result and (actionBegDate >= eventDirectionDate or self.checkValueMessageIgnoreAll(
                    u'Дата начала действия %s не должна быть раньше даты назначения события %s' % (
                        forceString(actionBegDate), forceString(eventDirectionDate)), skippable, widget, row, column,
                    widgetBegDate))
                if result == 2:
                    return result
            if actionEndDate:
                result = result and (actionEndDate >= eventDirectionDate or self.checkValueMessageIgnoreAll(
                    u'Дата выполнения действия %s не должна быть раньше даты назначения события %s' % (
                        forceString(actionEndDate), forceString(eventDirectionDate)), skippable, widget, row, column,
                    widgetEndDate))
                if result == 2:
                    return result
        if eventEndDate and actionDirectionDate:
            if actionBegDate:
                result = result and (actionBegDate <= eventEndDate or self.checkValueMessageIgnoreAll(
                    u'Дата начала действия %s не должна быть позже даты выполнения события %s' % (
                        forceString(actionBegDate), forceString(eventEndDate)), skippable, widget, row, column,
                    widgetBegDate))
                if result == 2:
                    return result
            if actionEndDate:
                if not actionTypeItem.isIgnoreEventExecDate:
                    result = result and (actionEndDate <= eventEndDate or self.checkValueMessageIgnoreAll(
                        u'Дата выполнения действия %s не должна быть позже даты выполнения события %s' % (
                            forceString(actionEndDate), forceString(eventEndDate)), skippable, widget, row, column,
                        widgetEndDate))
                    if result == 2:
                        return result
        if eventDirectionDate and (actionEndDate and actionEndDate >= eventDirectionDate and (
                    not eventEndDate or eventEndDate >= actionEndDate)) and actionBegDate:
            result = result and (actionBegDate >= eventDirectionDate or self.checkValueMessageIgnoreAll(
                u'Дата начала действия %s не должна быть раньше даты начала события %s' % (
                    forceString(actionBegDate), forceString(eventDirectionDate)), skippable, widget, row, column,
                widgetBegDate))
            if result == 2:
                return result
        return result

    def checkActionEndDate(self, strNameActionType, widget, row, column, widgetEndDate):
        return self.checkValueMessage(u'Должна быть указана дата выполнения действия%s' % (strNameActionType), True,
                                      widget, row, column, widgetEndDate)

    def checkActionDataEntered(self, directionDate, begDate, endDate, widget, widgetDirectionDate=None,
                               widgetBegDate=None, widgetEndDate=None, row=None, column=None):
        result = True
        possibleDeathDate = QtCore.QDate()
        if self.clientBirthDate:
            possibleDeathDate = self.clientBirthDate.addYears(QtGui.qApp.maxLifeDuration)
        if endDate:
            if directionDate:
                result = result and (endDate >= directionDate or self.checkValueMessage(
                    u'Дата выполнения (окончания) %s не может быть раньше даты назначения %s' % (
                        forceString(endDate), forceString(directionDate)), False, widget, row, column, widgetEndDate))
            if begDate:
                result = result and (endDate >= begDate or self.checkValueMessage(
                    u'Дата выполнения (окончания) %s не может быть раньше даты начала %s' % (
                        forceString(endDate), forceString(begDate)), False, widget, row, column, widgetEndDate))
            if self.clientBirthDate:
                result = result and (endDate >= self.clientBirthDate or self.checkValueMessage(
                    u'Дата выполнения (окончания) %s не может быть раньше даты рождения пациента %s' % (
                        forceString(endDate), forceString(self.clientBirthDate)), False, widget, row, column,
                    widgetEndDate))
            if self.clientDeathDate:
                result = result and (
                    endDate <= self.clientDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                        u'Дата выполнения (окончания) %s не может быть позже имеющейся даты смерти пациента %s' % (
                            forceString(endDate), forceString(self.clientDeathDate)), False, widget, row, column,
                        widgetEndDate))
            else:
                if possibleDeathDate:
                    result = result and (
                        endDate <= possibleDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                            u'Дата выполнения (окончания) %s не может быть позже возможной даты смерти пациента %s' % (
                                forceString(endDate), forceString(possibleDeathDate)), False, widget, row, column,
                            widgetEndDate))

        if directionDate and begDate:
            result = result and (directionDate <= begDate or self.checkValueMessage(
                u'Дата назначения %s не может быть позже даты начала %s' % (
                    forceString(directionDate), forceString(begDate)), False, widget, row, column, widgetDirectionDate))

        if self.clientBirthDate:
            if directionDate:
                result = result and (directionDate >= self.clientBirthDate or self.checkValueMessage(
                    u'Дата назначения %s не может быть раньше даты рождения пациента %s' % (
                        forceString(directionDate), forceString(self.clientBirthDate)), False, widget, row, column,
                    widgetDirectionDate))
            if begDate:
                result = result and (begDate >= self.clientBirthDate or self.checkValueMessage(
                    u'Дата начала %s не может быть раньше даты рождения пациента %s' % (
                        forceString(begDate), forceString(self.clientBirthDate)), False, widget, row, column,
                    widgetBegDate))

        if self.clientDeathDate:
            if directionDate:
                result = result and (
                    directionDate <= self.clientDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                        u'Дата назначения %s не может быть позже имеющейся даты смерти пациента %s' % (
                            forceString(directionDate), forceString(self.clientDeathDate)), False, widget, row, column,
                        widgetDirectionDate))
            if begDate:
                result = result and (
                    begDate <= self.clientDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                        u'Дата начала %s не может быть позже имеющейся даты смерти пациента %s' % (
                            forceString(begDate), forceString(self.clientDeathDate)), False, widget, row, column,
                        widgetBegDate))
        else:
            if possibleDeathDate:
                if directionDate:
                    result = result and (
                        directionDate <= possibleDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                            u'Дата назначения %s не может быть позже возможной даты смерти пациента %s' % (
                                forceString(directionDate), forceString(possibleDeathDate)), False, widget, row, column,
                            widgetDirectionDate))
                if begDate:
                    result = result and (
                        begDate <= possibleDeathDate or self.eventPurposeId == 6 or self.checkValueMessage(
                            u'Дата начала %s не может быть позже возможной даты смерти пациента %s' % (
                                forceString(begDate), forceString(possibleDeathDate)), False, widget, row, column,
                            widgetBegDate))
        return result

    def checkTabNotesEventExternalId(self):
        if hasattr(self, 'tabNotes'):
            result = self.tabNotes.checkOrGenerateUniqueEventExternalId(self.itemId(), self.eventTypeId)
            if result and isinstance(result, list):
                sameExternalIdListText = '\n'.join(result)
                message = u'Подобный внешний идентификатор уже существует в других событиях:\n%s\n\n%s' % (
                    sameExternalIdListText, u'Исправить?')
                return self.checkValueMessage(message, True, self.tabNotes.edtEventExternalIdValue)
            elif result == -2:
                return self.checkInputMessage(u'внешний идентификатор', False, self.tabNotes.edtEventExternalIdValue)
            elif result == -1:
                return False
        return True

    def checkTabNotesReferral(self):
        if QtGui.qApp.isReferralRequired() and not QtGui.qApp.userHasRight(urDisableCheckRefferal):
            if self.tabNotes.chkLPUReferral.isChecked():
                numText = forceString(self.tabNotes.edtNumber.text()).strip()
                numRight = QtGui.qApp.userHasRight(urCreateReferral)
                if not numRight and numText:
                    QtGui.QMessageBox.critical(
                        self, u'Внимание!',
                        u'Вы не имеете права создавать направления.\nПожалуйста, выберите одно из уже существующих.',
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    self.setFocusToWidget(self.tabNotes.cmbNumber)
                    return False
                elif not numText:
                    boxResult = QtGui.QMessageBox.critical(
                        self, u'Внимание!', u'Не указан номер направления.',
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                        QtGui.QMessageBox.Ok)
                    if boxResult == QtGui.QMessageBox.Ok:
                        self.tabNotes.dontSaveReferral = True
                        return True
                    self.tabNotes.dontSaveReferral = False
                    self.setFocusToWidget(self.tabNotes.cmbNumber)
                    return False
                elif self.tabNotes.cmbRelegateOrg.currentIndex() == 0 and not forceString(
                        self.tabNotes.edtFreeInput.text()).strip():
                    boxResult = QtGui.QMessageBox.critical(
                        self, u'Внимание!', u'Не указана организация направителя.',
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                        QtGui.QMessageBox.Ok)
                    if boxResult == QtGui.QMessageBox.Ok:
                        self.tabNotes.dontSaveReferral = True
                        return True
                    self.tabNotes.dontSaveReferral = False
                    self.setFocusToWidget(self.tabNotes.cmbRelegateOrg)
                    return False
            if self.tabNotes.chkArmyReferral.isChecked():
                numRow = self.tabNotes.cmbArmyNumber.currentIndex()
                numText = forceString(self.tabNotes.cmbArmyNumber.lineEdit().text()).strip()
                numRight = QtGui.qApp.userHasRight(urCreateReferral)
                if numRow == 0:
                    if not numRight and numText:
                        QtGui.QMessageBox.critical(
                            self, u'Внимание!',
                            u'Вы не имеете права создавать направления.\n'
                            u'Пожалуйста, выберите одно из уже существующих.',
                            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                        return False
                    elif not numText:
                        boxResult = QtGui.QMessageBox.critical(
                            self, u'Внимание!',
                            u'Не указан номер направления. Не создавать направление для обращения?',
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                            QtGui.QMessageBox.Ok)
                        if boxResult == QtGui.QMessageBox.Ok:
                            self.tabNotes.dontSaveReferral = True
                            return True
                        self.tabNotes.dontSaveReferral = False
                        self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                        return False

                elif numRow != 0 and not numText:
                    boxResult = QtGui.QMessageBox.critical(
                        self, u'Внимание!',
                        u'Не указан номер направления. Не прикреплять обращение к направлению?',
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                        QtGui.QMessageBox.Ok)
                    if boxResult == QtGui.QMessageBox.Ok:
                        self.tabNotes.dontSaveReferral = True
                        return True
                    self.tabNotes.dontSaveReferral = False
                    self.setFocusToWidget(self.tabNotes.cmbArmyNumber)
                    return False
                elif not forceString(self.tabNotes.edtArmyDate.text()).strip():
                    boxResult = QtGui.QMessageBox.critical(
                        self, u'Внимание!',
                        u'Не указана организация направителя. Не прикреплять обращение к направлению?',
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                        QtGui.QMessageBox.Ok)
                    if boxResult == QtGui.QMessageBox.Ok:
                        self.tabNotes.dontSaveReferral = True
                        return True
                    self.tabNotes.dontSaveReferral = False
                    self.setFocusToWidget(self.tabNotes.edtArmyDate)
                    return False
        return True

    def checkBlankParams(self, blankParams, result, serial, number, table, row):
        for blankMovingId, blankInfo in blankParams.items():
            checkingSerialCache = forceInt(toVariant(blankInfo.get('checkingSerial', 0)))
            serialCache = forceString(blankInfo.get('serial', u''))
            if checkingSerialCache and serial:
                result = result and (serialCache == serial or self.checkValueMessage(u'Серия не соответсвует документу',
                                                                                     True if checkingSerialCache == 1 else False,
                                                                                     table, row))
            if result:
                checkingNumberCache = forceInt(toVariant(toVariant(blankInfo.get('checkingNumber', 0))))
                if checkingNumberCache and number:
                    numberFromCache = forceInt(toVariant(blankInfo.get('numberFrom', 0)))
                    numberToCache = forceInt(toVariant(blankInfo.get('numberTo', 0)))
                    result = result and (
                        (number >= numberFromCache and number <= numberToCache) or self.checkValueMessage(
                            u'Номер не соответсвует диапазону номеров документа',
                            True if checkingNumberCache == 1 else False, table, row))
            if result:
                checkingAmountCache = forceInt(toVariant(blankInfo.get('checkingAmount', 0)))
                if checkingAmountCache:
                    returnAmount = forceInt(blankInfo.get('returnAmount', 0))
                    used = forceInt(blankInfo.get('used', 0))
                    received = forceInt(blankInfo.get('received', 0))
                    balance = received - used - returnAmount
                    result = result and (
                        balance > 0 or self.checkValueMessage(u'В партии закончились соответствующие документы',
                                                              True if checkingAmountCache == 1 else False, table, row))
            return result, forceRef(blankMovingId)
        return result, None

    def checkDischargePaymentAndQuoting(self, tabCash, tabMisc):
        dischargeFinType, cashRow = tabCash.modelAccActions.getDischargePayType()
        dischargeQuotaTypeNumber, quotaRow = tabMisc.getDischargeQuotaTypeNumber()
        if not (cashRow and quotaRow):
            return True
        eventFinType = forceInt(QtGui.qApp.db.translate('Contract', 'id', self.getContractId(), 'finance_id'))
        if dischargeQuotaTypeNumber:
            if dischargeFinType:
                if eventFinType == dischargeFinType:
                    return True
                else:
                    return self.checkValueMessage(u'Тип финансирования выписки не соответствует договору', True,
                                                  tabCash.tblAccActions, cashRow)
            else:
                return self.checkValueMessage(u'Неверно определён тип финансирования выписки', True,
                                              tabCash.tblAccActions, cashRow)
        return True

    def checkOncologyForm90(self):
        if (hasattr(self, 'tblActions') and
                QtGui.qApp.userInfo.specialityId and
                forceBool(QtGui.qApp.db.translate('rbSpeciality', 'id', QtGui.qApp.userInfo.specialityId, 'shouldFillOncologyForm90')) and
                # self.primaryState() == EventIsPrimary.Primary and
                QtGui.qApp.isOncologyForm90Enabled() and
                getEventTypeForm(self.eventTypeId) in ('000', '025', '030') and
                (self.getFinalDiagnosisMKB()[0].startswith('C') or
                    any(x[0].startswith('C') for x in self.getRelatedDiagnosisMKB())) and
                self.personId and self.personSpecialityId and
                forceBool(QtGui.qApp.db.translate('rbSpeciality', 'id', self.personSpecialityId, 'shouldFillOncologyForm90')) and
                not clientHasOncologyEvent(self.clientId, self.itemId())):

            canSkip = QtGui.qApp.userHasRight(urSkipOncologyForm90)

            actionType = QtGui.qApp.db.getRecordEx('ActionType', 'id, class', "flatCode = 'f90'")
            actionTypeId, actionTypeClass = forceRef(actionType.value('id')), forceInt(actionType.value('class'))
            actionsTab = self.getActionsTabMap()[actionTypeClass]  # type: CActionsPage
            model = actionsTab.tblAPActions.model()  # type: CActionsModel
            if any(action[1].getType().id == actionTypeId for action in model.items()):
                return True
            index = model.index(model.rowCount() - 1, 0)

            return self.checkValueMessage(
                u'Не заполнена онкологическая форма 90',
                canSkip,
                actionsTab.tblAPActions,
                index.row(), 0,
                callback=lambda skip: not skip and model.setData(index, actionTypeId),
                btnOkName=u'Заполнить'
            )
        return True

    def getBlankIdList(self, action):
        blankParams = {}
        docTypeId = action._actionType.id
        if docTypeId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableRBBlankActions = db.table('rbBlankActions')
            tableBlankActionsParty = db.table('BlankActions_Party')
            tableBlankActionsMoving = db.table('BlankActions_Moving')
            tablePerson = db.table('Person')
            eventId = forceRef(action._record.value('event_id'))
            personId = None
            orgStructureId = None
            if eventId:
                record = db.getRecordEx(tableEvent, [tableEvent['execPerson_id'], tableEvent['setDate']],
                                        [tableEvent['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                if record:
                    personId = forceRef(record.value('execPerson_id')) if record else None
                    setDate = forceDate(record.value('setDate')) if record else None
            else:
                personId = forceRef(action._record.value('person_id'))
            if not personId:
                personId = forceRef(action._record.value('setPerson_id'))
            if not personId:
                personId = QtGui.qApp.userId
            if personId:
                orgStructRecord = db.getRecordEx(tablePerson, [tablePerson['orgStructure_id']],
                                                 [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)])
                orgStructureId = forceRef(orgStructRecord.value('orgStructure_id')) if orgStructRecord else None
            if not orgStructureId:
                orgStructureId = QtGui.qApp.currentOrgStructureId()

            date = forceDate(action._record.value('begDate'))
            if not date and setDate:
                date = setDate
            cond = [tableRBBlankActions['doctype_id'].eq(docTypeId),
                    tableBlankActionsParty['deleted'].eq(0),
                    tableBlankActionsMoving['deleted'].eq(0)
                    ]
            if date:
                cond.append(tableBlankActionsMoving['date'].le(date))
            if personId and orgStructureId:
                cond.append(db.joinOr([tableBlankActionsMoving['person_id'].eq(personId),
                                       tableBlankActionsMoving['orgStructure_id'].eq(orgStructureId)]))
            elif personId:
                cond.append(tableBlankActionsMoving['person_id'].eq(personId))
            elif orgStructureId:
                cond.append(tableBlankActionsMoving['orgStructure_id'].eq(orgStructureId))
            queryTable = tableRBBlankActions.innerJoin(tableBlankActionsParty, tableBlankActionsParty['doctype_id'].eq(
                tableRBBlankActions['id']))
            queryTable = queryTable.innerJoin(tableBlankActionsMoving,
                                              tableBlankActionsMoving['blankParty_id'].eq(tableBlankActionsParty['id']))
            records = db.getRecordList(
                queryTable,
                u'BlankActions_Moving.numberFrom, BlankActions_Moving.numberTo, BlankActions_Moving.returnAmount, '
                u'BlankActions_Moving.used, BlankActions_Moving.received, BlankActions_Moving.id AS blankMovingId, '
                u'BlankActions_Party.serial, rbBlankActions.checkingSerial, rbBlankActions.checkingNumber, '
                u'rbBlankActions.checkingAmount',
                cond,
                u'rbBlankActions.checkingSerial, rbBlankActions.checkingNumber, rbBlankActions.checkingAmount DESC'
            )
            for record in records:
                blankInfo = {}
                blankMovingId = forceRef(record.value('blankMovingId'))
                checkingSerial = forceInt(record.value('checkingSerial'))
                checkingNumber = forceInt(record.value('checkingNumber'))
                checkingAmount = forceInt(record.value('checkingAmount'))
                serial = forceString(record.value('serial'))
                numberFrom = forceInt(record.value('numberFrom'))
                numberTo = forceInt(record.value('numberTo'))
                returnAmount = forceInt(record.value('returnAmount'))
                used = forceInt(record.value('used'))
                received = forceInt(record.value('received'))
                blankInfo['blankMovingId'] = blankMovingId
                blankInfo['checkingSerial'] = checkingSerial
                blankInfo['checkingNumber'] = checkingNumber
                blankInfo['checkingAmount'] = checkingAmount
                blankInfo['serial'] = serial
                blankInfo['numberFrom'] = numberFrom
                blankInfo['numberTo'] = numberTo
                blankInfo['returnAmount'] = returnAmount
                blankInfo['used'] = used
                blankInfo['received'] = received
                blankParams[blankMovingId] = blankInfo
        return blankParams

    def saveBlankUsers(self, blankMovingIdList=None):
        if not blankMovingIdList:
            blankMovingIdList = []
        db = QtGui.qApp.db
        tableBlankActionsMoving = db.table('BlankActions_Moving')
        for blankMovingId in blankMovingIdList:
            recordMoving = db.getRecordEx(tableBlankActionsMoving, u'*', [tableBlankActionsMoving['deleted'].eq(0),
                                                                          tableBlankActionsMoving['id'].eq(
                                                                              blankMovingId)])
            used = forceInt(recordMoving.value('used'))
            recordMoving.setValue('used', toVariant(used + 1))
            db.updateRecord(tableBlankActionsMoving, recordMoving)

    def setContractId(self, contractId):
        if contractId and self.contractId != contractId:
            # if self.contractId != contractId:
            if contractId:
                self.eventFinanceId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
            else:
                self.eventFinanceId = getEventFinanceId(self.eventTypeId)
            self.contractId = contractId
            cols = self.tblActions.model().cols() if hasattr(self, 'tblActions') else []
            if cols:
                cols[0].setContractId(contractId)
            if hasattr(self, 'tabCash'):
                self.tabCash.modelAccActions.setContractId(contractId)
                self.tabCash.updatePaymentsSum()
            if hasattr(self, 'tabRecommendations') and self.tabRecommendations != None:
                self.tabRecommendations.updateContractId(contractId)
            self.emit(QtCore.SIGNAL('updateActionsPriceAndUet()'))
            self.updateTotalUet()

    def getUet(self, actionTypeId, personId, financeId, contractId):
        if not contractId:
            contractId = self.contractId
            financeId = self.eventFinanceId
        if contractId and actionTypeId:
            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(actionTypeId, financeId)
            tariffDescr = self.contractTariffCache.getTariffDescr(contractId, self)
            tariffCategoryId = self.getPersonTariffCategoryId(personId)
            uet = CContractTariffCache.getUet(tariffDescr.actionTariffMap, serviceIdList, tariffCategoryId)
            return uet
        return 0

    def updateTotalUet(self):
        if hasattr(self, 'lblShowTotalUet') and hasattr(self, 'modelActionsSummary'):
            if not QtGui.qApp.isPNDDiagnosisMode():
                uet = self.modelActionsSummary.calcTotalUet()
                self.frmTotalUet.setVisible(bool(uet))
                self.lblShowTotalUet.setNum(uet)

    def hideMedicamentCols(self, status):
        if not hasattr(self, 'tblActions') or not hasattr(self, 'modelActionsSummary'):
            return
        self.tblActions.setColumnHidden(self.modelActionsSummary.getColIndex('packPurchasePrice'), status)
        self.tblActions.setColumnHidden(self.modelActionsSummary.getColIndex('doseRatePrice'), status)

    def updatePrintTriggerMap(self):
        self.mapPrintTriggerToTemplate.clear()

        db = QtGui.qApp.db
        tableEventTypeAutoPrint = db.table('EventType_AutoPrint')
        tableRepeat = db.table('EventType_AutoPrint_Repeat')
        tablePrintTemplate = db.table('rbPrintTemplate')
        queryTable = tableEventTypeAutoPrint.innerJoin(tablePrintTemplate, tablePrintTemplate['id'].eq(
            tableEventTypeAutoPrint['printTemplate_id']))
        for record in db.getRecordList(
                table=queryTable,
                cols=[
                    tableEventTypeAutoPrint['id'].alias('masterId'),
                    tableEventTypeAutoPrint['triggerType'],
                    tableEventTypeAutoPrint['repeatType'],
                    tablePrintTemplate['id'].alias('templateId'),
                    tablePrintTemplate['context'].alias('templateContext'),
                    tablePrintTemplate['name'].alias('templateName'),
                    tableEventTypeAutoPrint['repeatResetType'],
                    tableEventTypeAutoPrint['repeatResetDate']
                ],
                where=[
                    tableEventTypeAutoPrint['eventType_id'].eq(self.eventTypeId),
                    tablePrintTemplate['deleted'].eq(0)
                ]
        ):
            masterId = forceRef(record.value('masterId'))
            templateId = forceRef(record.value('templateId'))
            templateContext = forceString(record.value('templateContext'))
            templateName = forceString(record.value('templateName'))
            triggerType = forceInt(record.value('triggerType'))
            repeatType = forceInt(record.value('repeatType'))
            repeatResetType = forceInt(record.value('repeatResetType'))
            repeatResetDate = forceDate(record.value('repeatResetDate'))

            if repeatType == 2:  # один раз на пациента
                checkData = self.clientId
            elif repeatType == 1:  # один раз
                checkData = 1
            else:
                checkData = None  # 0 - каждый раз

            if not (checkData and db.getRecordList(table=tableRepeat,
                                                   cols='*',
                                                   where=[tableRepeat['master_id'].eq(masterId),
                                                          db.joinOr([tableRepeat['expiredDate'].gt(
                                                              QtCore.QDate.currentDate()),
                                                              tableRepeat['expiredDate'].isNull()]),
                                                          tableRepeat['checkData'].eq(checkData)]
                                                   )):
                self.mapPrintTriggerToTemplate.setdefault(triggerType, []).append((templateId,
                                                                                   templateContext,
                                                                                   templateName,
                                                                                   checkData,
                                                                                   masterId,
                                                                                   repeatResetType,
                                                                                   repeatResetDate))

    def autoPrintTriggered(self, triggerType):
        if self.mapPrintTriggerToTemplate.has_key(triggerType) and not QtGui.qApp.userHasRight(
                urIgnoreAutoPrintTemplates):
            eventContextData = getEventContextData(self)
            mapContextToActionInfoList = {}
            for actionInfo in eventContextData['event'].actions:
                mapContextToActionInfoList.setdefault(actionInfo.contextName, []).append(actionInfo)

            for templateId, templateContext, templateName, checkData, masterId, repeatResetType, repeatResetDate in self.mapPrintTriggerToTemplate.get(
                    triggerType, []):
                # проверка на соответствие контекста шаблона автопечати либо контексту события
                # либо контексту одного из типов действий в нем
                if templateContext and self.eventContext != templateContext:
                    if templateContext not in mapContextToActionInfoList.keys():
                        # Пропустить шаблон печати, если его контекст не соответствует ни событию ни одному из действий.
                        continue

                actionInfoList = []
                if templateContext:
                    actionInfoList = mapContextToActionInfoList.get(templateContext, [])
                else:
                    for actionInfo in mapContextToActionInfoList.values():
                        actionInfoList.extend(actionInfo)

                contextDataList = []
                if templateContext == self.eventContext:
                    contextDataList.append(eventContextData)

                for actionInfo in actionInfoList:
                    actionContextData = dict(eventContextData)
                    actionContextData['action'] = actionInfo
                    actionContextData['actions'] = eventContextData['event'].actions
                    actionContextData['currentActionIndex'] = None
                    contextDataList.append(actionContextData)

                isPrinted = False

                for contextData in contextDataList:
                    message = u'''
                                    <p align="center" style="font: 12px;">%s</p>
                                    <p align="center" style="font: bold 16px;">"%s"</p>
                    ''' % (u'Нажатием кнопки "ДА" Вы перейдете к печати', templateName)
                    userChoise = QtGui.QMessageBox.information(self,
                                                               u'Печатать документ?',
                                                               message,
                                                               buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                               defaultButton=QtGui.QMessageBox.No)
                    if userChoise == QtGui.QMessageBox.Yes:
                        applyTemplate(self, templateId, contextData)
                        isPrinted = True

                if isPrinted and checkData and masterId:
                    tableRepeat = QtGui.qApp.db.table('EventType_AutoPrint_Repeat')
                    record = tableRepeat.newRecord()
                    record.setValue('master_id', toVariant(masterId))
                    record.setValue('checkData', toVariant(checkData))
                    expiredDate = getExpiredDate(repeatResetType, repeatResetDate)
                    record.setValue('expiredDate', toVariant(expiredDate))
                    QtGui.qApp.db.insertOrUpdate(tableRepeat, record)

        # Автопечать зашитых в код отчетов при сохранении обращения
        if triggerType == CEventEditDialog.PrintTriggerType.AtSaveEvent \
                and not self.isReportEventCostPrinted \
                and not self.getExecDateTime().isNull() \
                and QtGui.qApp.defaultKLADR().startswith('78') \
                and QtGui.qApp.userHasRight(urAutoPrintCostTemplate) \
                and CFinanceType.getCode(self.eventFinanceId) in (CFinanceType.CMI, CFinanceType.highTechCMI):
            message = u'''
                            <p align="center" style="font: 12px;">%s</p>
                            <p align="center" style="font: bold 16px;">"%s"</p>
            ''' % (u'Нажатием кнопки "ДА" Вы перейдете к печати', u'Справка о стоимости лечения')
            userChoise = QtGui.QMessageBox.information(self,
                                                       u'Печатать документ?',
                                                       message,
                                                       buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                       defaultButton=QtGui.QMessageBox.No)
            if userChoise == QtGui.QMessageBox.Yes:
                self.on_actPrintEventCost_triggered()
                r = self.record()
                r.setValue('eventCostPrinted', QtCore.QVariant(1))
                QtGui.qApp.db.updateRecord('Event', r)

    def setPaymentScheme(self):
        self.mapPaymentScheme = {'universalContracts': self.cmbPaymentScheme.getUniversalContract(),
                                 'paymentScheme': self.paymentScheme, 'item': self.paymentSchemeItem}
        if self.contractId and self.paymentScheme:
            self.cmbPaymentScheme.setValue(forceRef(
                QtGui.qApp.db.translate('PaymentSchemeItem', 'contract_id', self.contractId, 'paymentScheme_id')))
            self.setPaymentSchemeItem(self.cmbPaymentScheme.getItemsByContract()[self.contractId])
            if self.paymentSchemeItem:
                self.lblPaymentScheme.setEnabled(False)
                self.cmbPaymentScheme.setEnabled(False)

    def setPaymentSchemeItem(self, item):
        self.paymentSchemeItem = item
        self.mapPaymentScheme['item'] = item
        self.btnPaymentScheme.setText(u'Начать' if not self.paymentSchemeItem else u'Следующий этап')
        if item:
            lblCurrentItemText = u'Текущий этап: %s | %s' % (item['idx'], item['name'])
            lblContractText = u'Договор: %s' % item['contract']
            self.setContractId(item['contract_id'])
            if item['idx'] == len(self.cmbPaymentScheme.getItemsByContract().keys()):
                self.btnPaymentScheme.setEnabled(False)
        else:
            lblCurrentItemText = u'Текущий этап: не выбрана схема оплаты'
            lblContractText = u'Договор: не выбрана схема оплаты'
        self.lblCurrentItem.setText(lblCurrentItemText)
        self.lblContract.setText(lblContractText)

    @QtCore.pyqtSlot()
    def on_btnPaymentScheme_clicked(self):
        if not self.cmbPaymentScheme.value():
            self.checkInputMessage(u'cхему оплаты', False, self.cmbPaymentScheme)
            return
        if QtGui.QMessageBox.question(
                self,
                u'Схема оплаты',
                        u'Нажатием кнопки "ДА" Вы перейдете к %s этапу. '
                        u'Обратный переход будет невозможен. Осуществить переход?' % (
                        u'следующему' if self.paymentSchemeItem else u'первому'
                ),
                buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                defaultButton=QtGui.QMessageBox.No
        ) == QtGui.QMessageBox.Yes:
            self.setPaymentSchemeItem(self.cmbPaymentScheme.getItemsByIdx()[1] if not self.paymentSchemeItem else
                                      self.cmbPaymentScheme.getItemsByIdx()[self.paymentSchemeItem['idx'] + 1])
            if self.paymentSchemeItem:
                self.lblPaymentScheme.setEnabled(False)
                self.cmbPaymentScheme.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_actPrintEventCost_triggered(self):
        from Reports.ReportEventCost import CReportEventCost
        CReportEventCost(self.itemId(), self.clientId, self).exec_()
        self.isReportEventCostPrinted = True

    @QtCore.pyqtSlot()
    def printAtOpenEventTriggered(self):
        self.autoPrintTriggered(CEventEditDialog.PrintTriggerType.AtOpenEvent)

    @QtCore.pyqtSlot()
    def printAtSaveEventTriggered(self):
        self.autoPrintTriggered(CEventEditDialog.PrintTriggerType.AtSaveEvent)

    @QtCore.pyqtSlot(bool)
    def on_chkIsClosed_clicked(self, checked):
        if not QtGui.qApp.userHasAnyRight((urAdmin, urEventLock)) and checked == False:
            if hasattr(self, 'tabNotes'):
                if hasattr(self.tabNotes, 'chkIsClosed'):
                    self.tabNotes.chkIsClosed.setChecked(True)
                if hasattr(self.tabNotes, 'chkLock'):
                    self.tabNotes.chkLock.setChecked(True)
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Недостаточно прав')
                self.chkIsClosed.setChecked(not checked)
            return
        if hasattr(self, 'tabNotes') and hasattr(self.tabNotes, 'chkLock'):
            self.tabNotes.chkLock.setChecked(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkLock_clicked(self, checked):
        if hasattr(self, 'chkIsClosed'):
            self.chkIsClosed.setChecked(checked)

    @QtCore.pyqtSlot()
    def on_actEditClient_triggered(self):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(self.clientId)
            if dialog.exec_():
                self.updateClientInfo()

    @QtCore.pyqtSlot(int)
    def on_cmbPaymentScheme_currentIndexChanged(self, index):
        if not self.cmbPaymentScheme.getItemsByIdx():
            self.btnPaymentScheme.setEnabled(False)
        elif not self.btnPaymentScheme.isEnabled():
            self.btnPaymentScheme.setEnabled(True)
        self.paymentScheme = self.cmbPaymentScheme.value()

    @QtCore.pyqtSlot()
    def on_cmbContract_valueChanged(self):
        contractId = self.cmbContract.value()
        self.setContractId(contractId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelActionsSummary_dataChanged(self, leftTop, rightBottom):
        self.updateTotalUet()

    @QtCore.pyqtSlot()
    def on_modelActionsSummary_modelReset(self):
        self.updateTotalUet()

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def on_modelActionsSummary_rowsInserted(self, parent, start, end):
        self.updateTotalUet()

    @QtCore.pyqtSlot(QtCore.QModelIndex, int, int)
    def on_modelActionsSummary_rowsRemoved(self, parent, start, end):
        self.updateTotalUet()

    @QtCore.pyqtSlot()
    def on_actDialogAPActionsAdd_triggered(self):
        self.actionsAdd(False)

    def getRelatedDiagnosisMKB(self):
        try:
            return self.modelFinalDiagnostics.getRelatedDiagnosisMKB()
        except AttributeError:
            return [['', '']]

    def addRecommendations(self, quiet=False):
        model = self.tabRecommendations.tblRecommendations.model()
        if QtGui.qApp.userId != model.personId:
            QtGui.QMessageBox.warning(self, u'Внимание', u'У вас нет права добавлять направления', QtGui.QMessageBox.Ok,
                                      QtGui.QMessageBox.Ok)
            return
        if not hasattr(model, 'isEditable') or model.isEditable():
            chkContractByFinanceId = CFinanceType.getCode(self.eventFinanceId) in [CFinanceType.VMI,
                                                                                   CFinanceType.cash]
            actionTypes = selectActionTypes(self,
                                            actionTypeClasses=ActionClass.All,
                                            clientSex=self.clientSex,
                                            clientAge=self.clientAge,
                                            orgStructureId=getRealOrgStructureId(),
                                            eventTypeId=self.eventTypeId,
                                            contractId=self.contractId,
                                            mesId=self.getMesId(),
                                            chkContractByFinanceId=chkContractByFinanceId,
                                            eventId=self._id,
                                            existsActionTypesList=[],
                                            contractTariffCache=self.contractTariffCache,
                                            showAmountFromMes=self.showAmountFromMes,
                                            eventBegDate=self.edtBegDate.date(),
                                            eventEndDate=self.edtEndDate.date(),
                                            showMedicaments=self.showMedicaments,
                                            isQuietAddingByMes=quiet,
                                            paymentScheme=self.mapPaymentScheme,
                                            MKB=self.getFinalDiagnosisMKB()[0],
                                            returnDirtyRows=True)

            for actionTypeId, action in actionTypes:
                index = model.index(model.rowCount() - 1, model.getColIndex('actionType_id'))
                if model.setData(index, toVariant(actionTypeId)):
                    amount = forceDouble(action.getRecord().value('amount'))
                    if amount != 0:
                        amountIndex = model.index(index.row(), model.getColIndex('amount'))
                        model.setData(amountIndex, toVariant(amount))
                    price = forceDouble(action.getRecord().value('price')) / amount if amount != 0 else 0
                    priceIndex = model.index(index.row(), model.getColIndex('price'))
                    model.setData(priceIndex, toVariant(price))
            model.emitDataChanged()

    def getExistsActionTypes(self):
        if hasattr(self, 'modelActionsSummary'):
            return [forceRef(item.value('actionType_id')) for item in self.modelActionsSummary.items()]
        return []

    def getSelectedAnalyses(self):
        tabAnalyses = self.getActionsTabMap().get(ActionClass.Analyses)
        if tabAnalyses:
            availableAnalysesGroups = filter(
                lambda action: not any((actionProperty.getRecord() is not None and
                                        actionProperty.getValue() is not None)
                                       for actionProperty in action
                                       if
                                       isinstance(actionProperty.type().valueType, CJobTicketActionPropertyValueType)),
                tabAnalyses.modelAPActions.getMainActions()
            )
            return list(itertools.chain.from_iterable([action] + tabAnalyses.modelAPActions.getAnalysesGroups()[action]
                                                      for action in availableAnalysesGroups))
        return []

    def actionsAdd(self, quiet=False):
        if hasattr(self, 'tblActions'):
            model = self.tblActions.model()
            if not hasattr(model, 'isEditable') or model.isEditable():
                selectedAnalyses = self.getSelectedAnalyses()
                chkContractByFinanceId = CFinanceType.getCode(self.eventFinanceId) in [CFinanceType.VMI,
                                                                                       CFinanceType.cash,
                                                                                       CFinanceType.CMI,]
                actionTypes = selectActionTypes(self,
                                                actionTypeClasses=ActionClass.All,
                                                clientSex=self.clientSex,
                                                clientAge=self.clientAge,
                                                orgStructureId=getRealOrgStructureId(),
                                                eventTypeId=self.eventTypeId,
                                                contractId=self.contractId,
                                                mesId=self.getMesId(),
                                                chkContractByFinanceId=chkContractByFinanceId,
                                                eventId=self._id,
                                                existsActionTypesList=self.getExistsActionTypes(),
                                                contractTariffCache=self.contractTariffCache,
                                                showAmountFromMes=self.showAmountFromMes,
                                                eventBegDate=self.edtBegDate.date(),
                                                eventEndDate=self.edtEndDate.date(),
                                                showMedicaments=self.showMedicaments,
                                                isQuietAddingByMes=quiet,
                                                paymentScheme=self.mapPaymentScheme,
                                                MKB=self.getFinalDiagnosisMKB()[0],
                                                chosenActionTypes=[action.getType().id for action in selectedAnalyses])

                for actionTypeId, action in actionTypes:
                    index = model.index(model.rowCount() - 1, 0)
                    model.setData(index, toVariant(actionTypeId), presetAction=action)
                model.emitDataChanged()
                self.tblActions.selectRow(len(model.items()) - 1)

    def appendActionTypesByMes(self):
        if not hasattr(self, 'controlMesNecessityEqOne') or not self.controlMesNecessityEqOne:
            return
        if not hasattr(self, 'tblActions') or not hasattr(self, 'tabMes'):
            return

        mesId = self.tabMes.cmbMes.value()
        if not mesId:
            return
        self.actionsAdd(True)

    def beforePrintTemplate(self, templateId):
        u"""Проверка возможности печати шаблона.
        Если печать доступна только после сохранения, предлагается сохранить обращение.
        Если требуется учет всех распечатанных обращений - перед сохранением включать счетчик.
        """
        needSave = False
        banUnkeptData = forceInt(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate'))
        if self.isDirty() and banUnkeptData == 2:
            if QtGui.QMessageBox.question(
                    self,
                    u'Внимание!',
                    u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return -1
            needSave = True
        if banUnkeptData > 0 and not templateId in self.oldTemplates.keys():
            counterId = forceRef(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'counter_id'))
            if counterId:
                counterValue = getDocumentNumber(self.clientId, counterId)
                self.newTemplates[templateId] = counterValue
                needSave = True
        if needSave:
            needRefresh = not self.itemId()
            if not self.saveData():
                return -1
            if needRefresh:
                self.setRecord(QtGui.qApp.db.getRecord('Event', '*', self.itemId()))
        return 0

    @QtCore.pyqtSlot(int)
    def on_btnPrint_printByTemplate(self, templateId):
        if self.beforePrintTemplate(templateId) == -1:
            return
        banUnkeptData = forceInt(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'banUnkeptDate'))
        if self.isDirty() and banUnkeptData == 2:
            if QtGui.QMessageBox.question(
                    self,
                    u'Внимание!',
                    u'Для печати данного шаблона необходимо сохранить обращение.\nСохранить сейчас?',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return
            counterId = None
            if banUnkeptData > 0 and not templateId in self.oldTemplates.keys():
                counterId = forceRef(QtGui.qApp.db.translate('rbPrintTemplate', 'id', templateId, 'counter_id'))
            if counterId:
                counterValue = getDocumentNumber(self.clientId, counterId)
                self.newTemplates[templateId] = counterValue
            if not self.saveData():
                return
        data = getEventContextData(self)
        data['templateCounterValue'] = self.oldTemplates.get(templateId, '')
        applyTemplate(self, templateId, data)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if hasattr(self, 'tabMes') and index == self.tabWidget.indexOf(self.tabMes):
            if not self.isTabMesAlreadyLoad:
                self.initTabMes()
            items = self.tblActions.model().items()
            actionTypeIdList = [forceInt(item.value('actionType_id'))
                                for item in items if forceInt(item.value('status')) == ActionStatus.Done]
            self.tabMes.cmbMes.setActionTypeIdList(actionTypeIdList)
            self.tabMes.cmbMes.setBegDate(self.begDate())
            self.tabMes.cmbMes.setEndDate(self.endDate())
            self.tabMes.cmbMes.setDefaultValue()
            if hasattr(self.tabMes, 'MKB') and not self.tabMes.MKB:
                self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabToken))
                QtGui.QMessageBox.information(None, u'Ошибка', u'Не заполнен диагноз')
        elif hasattr(self, 'tabStatus') and index == self.tabWidget.indexOf(self.tabStatus):
            if not self.isTabStatusAlreadyLoad:
                self.initTabStatus()
        elif hasattr(self, 'tabDiagnostic') and index == self.tabWidget.indexOf(self.tabDiagnostic):
            if not self.isTabDiagnosticAlreadyLoad:
                self.initTabDiagnostic()
        elif hasattr(self, 'tabCure') and index == self.tabWidget.indexOf(self.tabCure):
            if not self.isTabCureAlreadyLoad:
                self.initTabCure()
        elif hasattr(self, 'tabMisc') and index == self.tabWidget.indexOf(self.tabMisc):
            if not self.isTabMiscAlreadyLoad:
                self.initTabMisc()
        elif hasattr(self, 'tabAnalyses') and index == self.tabWidget.indexOf(self.tabAnalyses):
            if not self.isTabAnalysesAlreadyLoad:
                self.initTabAnalyses()
        elif hasattr(self, 'tabAmbCard') and index == self.tabWidget.indexOf(self.tabAmbCard):
            if not self.isTabAmbCardAlreadyLoad:
                self.initTabAmbCard()
            self.tabAmbCard.resetWidgets()
        elif hasattr(self, 'tabTempInvalidEtc') and index == self.tabWidget.indexOf(self.tabTempInvalidEtc):
            if not self.isTabTempInvalidEtcAlreadyLoad:
                self.initTabTempInvalidEtc()
        elif hasattr(self, 'tabCash') and index == self.tabWidget.indexOf(self.tabCash):
            if not self.isTabCashAlreadyLoad:
                self.initTabCash()
        elif hasattr(self, 'tabNotes') and index == self.tabWidget.indexOf(self.tabNotes):
            if not self.isTabNotesAlreadyLoad:
                self.initTabNotes()
        elif hasattr(self, 'tabFeed') and index == self.tabWidget.indexOf(self.tabFeed):
            if not self.isTabFeedAlreadyLoaded:
                self.initTabFeed()
        elif hasattr(self, 'tabRecommendations') and index == self.tabWidget.indexOf(self.tabRecommendations):
            if not self.isTabRecommendationsAlreadyLoad:
                self.initTabRecommendations()

        widget = self.tabWidget.widget(index)
        if widget is not None:
            focusProxy = widget.focusProxy()
            if focusProxy:
                focusProxy.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSlot()
    def on_btnSaveAndCreateAccount_clicked(self):
        self.done(self.saveAndCreateAccount)

    @QtCore.pyqtSlot()
    def on_btnSaveAndCreateAccountForPeriod_clicked(self):
        self.done(self.saveAndCreateAccountForPeriod)

    def on_btnEpicris_clicked(self):
        needSave = False
        if self.isDirty():
            if QtGui.QMessageBox.question(self,
                                          u'Внимание!',
                                          u'Для продолжения необходимо сохранить изменения.\nСохранить сейчас?',
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) != QtGui.QMessageBox.Yes:
                return -1
            needSave = True

        if needSave:
            needRefresh = not self.itemId()
            if not self.saveData():
                return -1
            if needRefresh:
                self.setRecord(QtGui.qApp.db.getRecord('Event', '*', self.itemId()))
        else:
            moduleUrl = forceString(QtGui.qApp.preferences.appPrefs.get('epircisModuleAddress', ''))

            if QtGui.qApp.currentOrgStructureId() is None:
                QtGui.QMessageBox.information(
                    self,
                    u'Внимание!',
                    u'Для начала работы с эпикризами укажите Подраделение в Умолчаниях.',
                    QtGui.QMessageBox.Ok
                )
            elif moduleUrl:
                import webbrowser

                if moduleUrl[-1] not in ['/', '\\']:
                    moduleUrl += '/'

                params = '?event_id=%s&user_id=%s&orgStructure_id=%s' % (
                    self.itemId(),
                    QtGui.qApp.userId,
                    QtGui.qApp.currentOrgStructureId()
                )

                webbrowser.open(moduleUrl + params)
                self.btnEpicrisPressed = True
            else:
                QtGui.QMessageBox.information(
                    self,
                    u'Внимание!',
                    u'Для корректной работы с эпикризами укажите проверьте адрес модуля в Умолчаниях.',
                    QtGui.QMessageBox.Ok
                )

    def on_btnSocLab_clicked(self):
        checkList = {
            'socLabLog': u'логин',
            'socLabPass': u'пароль',
            'socLabAddress': u'адрес сервиса',
            'socLabPort': u'порт'
        }
        socLabPref = dict((k, forceString(QtGui.qApp.preferences.appPrefs.get(k, ''))) for k in checkList)
        emptyPrefs = [checkList[k] for k, v in socLabPref.iteritems() if not v]

        if emptyPrefs:
            QtGui.QMessageBox.information(
                self,
                u'Внимание!',
                u'Для работы с АИС "Соц-Лаборатормя" необходимо указать в настройках: {0}'.format(
                    u', '.join(u'<i>%s</i>' % p for p in emptyPrefs)),
                QtGui.QMessageBox.Ok
            )
            return

        if QtGui.QMessageBox.question(
                self,
                u'Внимание!',
                u'Для работы с АИС "Соц-Лаборатормя" необходимо сохранить обращение.\nСохранить сейчас?',
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No
        ) != QtGui.QMessageBox.Yes:
            return

        if not self.saveData():
            return

        if not socLabPref['socLabAddress'].startswith('http://'):
            socLabPref['socLabAddress'] = 'http://' + socLabPref['socLabAddress']

        if forceString(self.clientInfo.compulsoryPolicyRecord.value('insurer_id')):
            insurerInfis = forceString(QtGui.qApp.db.translate('Organisation', 'id', forceString(
                self.clientInfo.compulsoryPolicyRecord.value('insurer_id')), 'infisCode'))
        else:
            insurerInfis = ''

        if forceString(self.clientInfo.compulsoryPolicyRecord.value('policyKind_id')):
            policyKindName = forceString(QtGui.qApp.db.translate('rbPolicyKind', 'id', forceString(
                self.clientInfo.compulsoryPolicyRecord.value('policyKind_id')), 'regionalCode'))
        else:
            policyKindName = ''

        if forceString(self.clientInfo.documentRecord.value('documentType_id')):
            docTypeRegionalCode = forceString(QtGui.qApp.db.translate('rbDocumentType', 'id', forceString(
                self.clientInfo.documentRecord.value('documentType_id')), 'regionalCode'))
        else:
            docTypeRegionalCode = ''

        locAddress = self.clientInfo.locAddressInfo
        params = [
            ('user', socLabPref['socLabLog']),
            ('password', socLabPref['socLabPass']),
            ('city', getCityName(locAddress.KLADRCode) if locAddress and locAddress.KLADRCode else None),
            ('rayon', getDistrictName(locAddress.KLADRCode, locAddress.KLADRStreetCode,
                                      locAddress.number) if locAddress.KLADRCode and locAddress.KLADRStreetCode else None),
            ('im', self.clientInfo.firstName or None),
            ('fam', self.clientInfo.lastName or None),
            ('otch', self.clientInfo.patrName or None),
            ('sex', self.clientInfo.sexCode or None),
            ('datr', self.clientInfo.birthDate.toString('dd.MM.yyyy') if self.clientInfo.birthDate else None),
            ('street', getStreetName(locAddress.KLADRStreetCode) or None),
            ('dom', locAddress.number if locAddress and locAddress.number else None),
            ('korp', locAddress.corpus if locAddress and locAddress.corpus else None),
            ('kv', locAddress.flat if locAddress and locAddress.flat else None),
            ('pserial', forceString(self.clientInfo.compulsoryPolicyRecord.value('serial')) or None),
            ('pnumber', forceString(self.clientInfo.compulsoryPolicyRecord.value('number')) or None),
            ('poms', insurerInfis or None),
            ('ptype', policyKindName or None),
            ('dserial', forceString(self.clientInfo.documentRecord.value('serial')).replace(' ',
                                                                                            '') if self.clientInfo.documentRecord and forceString(
                self.clientInfo.documentRecord.value('serial')) else None),
            ('dnumber', forceString(
                self.clientInfo.documentRecord.value('number')) if self.clientInfo.documentRecord and forceString(
                self.clientInfo.documentRecord.value('number')) else None),
            ('dtype', docTypeRegionalCode or None),
            ('MKB', self.getFinalDiagnosisMKB()[0] or None),
            ('Patient.identifier.value', self.clientId),
            ('Encounter.identifier.value', self.itemId()),
            ('Order.identifier.value', self.itemId()),
            ('Condition.category.system', '1.2.643.2.69.1.1.1.36'),
            ('Condition.category.code', 'diagnosis'),
            # ('Condition.category.version', '3'),
        ]

        url = '?'.join([u'{socLabAddress}:{socLabPort}/LIS/faces/dlilanding'.format(**socLabPref),
                        u'&'.join(u'{0}={1}'.format(k, v) for k, v in params if v is not None)])

        import webbrowser
        if not webbrowser.open_new(url):
            QtGui.QMessageBox.information(self, u'Внимание!', u'<br/>'.join([u'Не удалось открыть браузер по умолчанию',
                                                                             u"<b>URL</b>: <a href='{0}'>{0}</a>".format(
                                                                                 url)]), QtGui.QMessageBox.Ok)
        self.setAwaitSocLabResult()

    def on_btnJobTickets_clicked(self):
        def filterAction(action):
            actionType = action.getType()
            propertyTypeList = actionType.getPropertiesById().values()
            for propertyType in propertyTypeList:
                property = action.getPropertyById(propertyType.id)
                if isinstance(property.type().valueType, CJobTicketActionPropertyValueType):
                    return bool(property.getValue())
            return False

        def filterEmpty(items):
            return [(record, action) for (record, action) in items if not filterAction(action)]

        def filterFull(items):
            return [(record, action) for (record, action) in items if filterAction(action)]

        emptyActionsModelsItemList = self.getActionsModelsItemsList(filterEmpty)
        fullActionsModelsItemList = self.getActionsModelsItemsList(filterFull)
        dlg = CEventJobTicketsEditor(self, emptyActionsModelsItemList,
                                     fullActionsModelsItemList, self.clientId)
        if dlg.exec_():
            for actionsTab in self.getActionsTabsList():
                actionsTab.onActionCurrentChanged()

    # i3838 don't delete
    # def on_btnSignGrkmCard_clicked(self):
    #     if not self.isDirty():
    #         showErrorHint(u'Ошибка', u'Необходимо сохранить обращение')
    #         return
    #     eventId = self.itemId()
    #     db = QtGui.qApp.db
    #     tblReferrals = db.table('Referral')
    #     recReferral = db.getRecordEx(tblReferrals, '*', [tblReferrals['event_id'].eq(eventId), tblReferrals['isSend'].eq(1)])
    #     if recReferral:
    #         service = CGRKMSerice()
    #         result = service.saveCard(recReferral)
    #     else:
    #         showErrorHint(u'Ошибка', u'Необходимо создать направление')
    #         return

    def createNextEvent(self, personId, nextDate, outputMessage=False):
        if QtGui.qApp.autoCreationOfNextEvent() and nextDate and personId:
            nextEvent = getTimeTableEventByPersonAndDate(nextDate, personId)
            if nextEvent:
                nextEventTimetableId = forceRef(nextEvent.value('id'))
                timetableAction = CAction.getAction(nextEventTimetableId, atcAmbulance)
                times = timetableAction['times']
                if times and (
                            QtGui.qApp.userHasRight(urQueueOverTime) or
                                    personId == QtGui.qApp.userId and QtGui.qApp.userHasRight(urQueueToSelfOverTime)
                ):
                    from Registry.ResourcesDock import createQueueEvent
                    queueEventId, queueActionId = createQueueEvent(personId, nextDate, None, self.clientId)  # office??
                    queue = timetableAction['queue']
                    amountDiff = len(times) - len(queue)
                    if amountDiff > 0:
                        queue.extend([None] * amountDiff)
                    queue.append(queueActionId)
                    timetableAction['queue'] = queue
                    timetableAction.save()
                    if outputMessage:
                        stmt = u'''
                            SELECT Person.lastName,
                            Person.firstName,
                            Person.patrName
                            FROM Person
                            WHERE Person.id = %s
                        ''' % personId
                        query = QtGui.qApp.db.query(stmt)
                        if query.first():
                            record = query.record()
                            personName = forceString(record.value('lastName')) + ' ' + forceString(
                                record.value('firstName')) + ' ' + forceString(record.value('patrName'))
                            message = u'Пациент записан к %s на %s' % (personName, nextDate.toString('dd.MM.yyyy'))
                    QtGui.qApp.emit(QtCore.SIGNAL('createdOrder()'))
                elif outputMessage:
                    message = u'У ответственного врача на указанную дату нет приема'
            elif outputMessage:
                message = u'У ответственного врача на указанную дату нет приема'
            if outputMessage:
                QtGui.QMessageBox.warning(self, u'Внимание', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot(int)
    def onCmbResultCurrentIndexChanged(self, index):
        if index >= 0 and self.cmbResult.value() is not None:
            if self.eventPurposeId not in self.defaultEventResultId \
                    or self.defaultEventResultId[self.eventPurposeId] is None:
                self.defaultEventResultId[self.eventPurposeId] = self.cmbResult.value()
        if hasattr(self, 'tabNotes'):
            self.tabNotes.setEventResultId(self.cmbResult.value())

    @QtCore.pyqtSlot(int)
    def onCmbGoalCurrentIndexChanged(self, index):
        if index >= 0 and self.cmbGoal.value() is not None:
            if self.eventTypeId not in self.defaultGoalByType \
                    or self.defaultGoalByType[self.eventTypeId] is None:
                self.defaultGoalByType[self.eventTypeId] = self.cmbGoal.value()

    def getModelFinalDiagnostics(self):
        raise NotImplementedError

    def getFinalDiagnostic(self):
        return self.getModelFinalDiagnostics().getFinalDiagnosis()

    def getFinalDiagnosisMKB(self):
        finalDiagnostic = self.getFinalDiagnostic()
        if finalDiagnostic:
            MKB = forceString(finalDiagnostic.value('MKB'))
            MKBEx = forceString(finalDiagnostic.value('MKBEx'))
            return MKB, MKBEx
        else:
            return '', ''

    def getFinalDiagnosisId(self):
        finalDiagnostic = self.getFinalDiagnostic()
        return forceRef(finalDiagnostic.value('diagnosis_id')) if finalDiagnostic else None

    def getFinalDiagnosticResult(self):
        finalDiagnostic = self.getFinalDiagnostic()
        return forceRef(finalDiagnostic.value('result_id')) if finalDiagnostic else None

    def updateResultFilter(self):
        db = QtGui.qApp.db
        tblResult = db.table('rbResult')
        cond = [tblResult['eventPurpose_id'].eq(self.eventPurposeId)]

        cmbResultFilter = self.getCmbResultFilter()
        if cmbResultFilter:
            cond.append(cmbResultFilter)

        begDate = self.edtBegDate.date()
        if begDate.isValid():
            cond.append(tblResult['begDate'].dateLe(begDate))
            cond.append(tblResult['endDate'].dateGe(begDate))

        val = self.cmbResult.value()
        self.cmbResult.setFilter(db.joinAnd(cond), order='code')
        self.cmbResult.setValue(val)
        if self.cmbResult.value() is None:
            self.cmbResult.setCurrentIndex(0)

        if self.cmbResult.count() >= 2 and self.cmbResult.currentIndex() == 0 and self.getFinalDiagnosticResult() is not None:  # если только более одного пункта помимо "не задано"
            self.cmbResult.setCurrentIndex(1)

        if self.filterDiagnosticResultByPurpose:
            self.updateDiagnosticResultFilter()

        if self.cmbResult.value() is None:
            self.cmbResult.setValue(getEventResultId(CEventEditDialog.defaultDiagnosticResultId.get(self.eventPurposeId)))

    def updateDiagnosticResultFilter(self):
        db = QtGui.qApp.db
        tblDiagnosticResult = db.table('rbDiagnosticResult')
        diagCond = [tblDiagnosticResult['eventPurpose_id'].eq(self.eventPurposeId)]

        begDate = self.edtBegDate.date()
        if begDate.isValid():
            diagCond.append(tblDiagnosticResult['begDate'].dateLe(begDate))
            diagCond.append(tblDiagnosticResult['endDate'].dateGe(begDate))

        cols = self.getModelFinalDiagnostics().cols()
        resultCol = cols[-1]
        resultCol.filter = db.joinAnd(diagCond)

    def getCmbResultFilter(self):
        db = QtGui.qApp.db
        if self.getModelFinalDiagnostics().rowCount():
            pass
        diagnostic_result_id = self.getFinalDiagnosticResult()
        if diagnostic_result_id:
            if not forceBool(db.translate('rbDiagnosticResult', 'id', diagnostic_result_id, 'filterResults')):
                return ''
            results_list = db.getIdList(
                'rbDiagnosticResult_rbResult',
                idCol='result_id',
                where='diagnosticResult_id=%d' % diagnostic_result_id,
            )
            if results_list:
                return 'rbResult.id IN (%s)' % ', '.join(str(result_id) for result_id in results_list)
        return ''

    def setAwaitSocLabResult(self):
        """
        Создаем в logger.N3LabOrder запись с заявкой к СОЦ-Лаборатории
        В сервисе обмена с ОДЛИ забираем результат по OrderMisID = Event.id
        """
        db = QtGui.qApp.db
        tableLabOrder = db.table('{logger}.N3LabOrderLog'.format(logger=getLoggerDbName()))

        OrderType_SocLab = 1  # Заявка через СОЦ-Лабораторию
        OrderStatus_AwaitingResult = 1  # Ожидание результата

        eventId = self.itemId()
        if eventId is not None:
            labOrder = db.getRecordEx(tableLabOrder, '*', [tableLabOrder['event_id'].eq(eventId),
                                                           tableLabOrder['orderType'].eq(OrderType_SocLab)])
            if labOrder is None:
                labOrder = tableLabOrder.newRecord()
                labOrder.setValue('event_id', toVariant(eventId))
                labOrder.setValue('orderMisId', toVariant(eventId))
                labOrder.setValue('datetime', toVariant(QtCore.QDateTime.currentDateTime()))
                labOrder.setValue('orderType', toVariant(OrderType_SocLab))
            labOrder.setValue('status', toVariant(OrderStatus_AwaitingResult))
            db.insertOrUpdate(tableLabOrder, labOrder)


class CDiseaseCharacter(CRBInDocTableCol):
    u""" Диагностика: характер заболевания """

    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbDiseaseCharacter', **params)

    def setEditorData(self, editor, value, record):
        db = QtGui.qApp.db
        MKB = forceString(record.value('MKB'))
        codeIdList = getAvailableCharacterIdByMKB(MKB)
        table = db.table('rbDiseaseCharacter')
        editor.setTable(table.name(), not bool(codeIdList), filter=table['id'].inlist(codeIdList), order=self.order)
        editor.setValue(forceRef(value))


class CDiseaseStage(CRBInDocTableCol):
    u""" Диагностика: стадия заболевания """

    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbDiseaseStage', **params)

    def setEditorData(self, editor, value, record):
        db = QtGui.qApp.db
        MKB = forceString(record.value('MKB'))
        characterId = forceRef(record.value('character_id'))
        characterDataCache = CRBModelDataCache.getData('rbDiseaseCharacter', True)
        characterCode = characterDataCache.getCodeById(characterId)
        enabledCharacterReations = [0]
        if MKB.startswith('Z'):
            enabledCharacterReations.append(4)
        else:
            if characterCode == '1':
                enabledCharacterReations.append(1)
            else:
                enabledCharacterReations.append(2)
            enabledCharacterReations.append(3)
        table = db.table('rbDiseaseStage')
        editor.setTable(table.name(), True, filter=table['characterRelation'].inlist(enabledCharacterReations),
                        order=self.order)
        editor.setValue(forceRef(value))


class CDiseasePhases(CRBInDocTableCol):
    u""" Диагностика: фаза заболевания """

    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbDiseasePhases', **params)

    def setEditorData(self, editor, value, record):
        db = QtGui.qApp.db
        MKB = forceString(record.value('MKB'))
        characterId = forceRef(record.value('character_id'))
        characterDataCache = CRBModelDataCache.getData('rbDiseaseCharacter', True)
        characterCode = characterDataCache.getCodeById(characterId)
        enabledCharacterReations = [0]
        if MKB.startswith('Z'):
            enabledCharacterReations.append(4)
        else:
            if characterCode == '1':
                enabledCharacterReations.append(1)
            else:
                enabledCharacterReations.append(2)
            enabledCharacterReations.append(3)
        table = db.table('rbDiseasePhases')
        editor.setTable(table.name(), True, filter=table['characterRelation'].inlist(enabledCharacterReations),
                        order=self.order)
        editor.setValue(forceRef(value))


def getAttrFromPathIfExists(root, path):
    u"""
    Given a deeply nested object structure and a path to
    the needed attribute, returns the value of given attribute.

    Example::
    > a       = lambda: 1408
    > a.b     = lambda: None
    > a.b.c   = lambda: None
    > a.b.c.d = 42
    > getAttrFromPathIfExists(a, ['b','c','d'])
    (True, 42)
    > getAttrFromPathIfExists(a, ['b', 'blah'])
    (False, None)
    > getAttrFromPathIfExists(a, [])[1]()
    1408

    :param root: top-level object
    :param path: list of attribute names
    :return: (existsFlag, value), where existsFlag is True if
             a value does exist, and False otherwise.
    :param root:
    :param path:
    :return:
    """
    curr = root
    for attr in path:
        if hasattr(curr, attr):
            curr = getattr(curr, attr)
        else:
            return False, None
    return True, curr


def method(name, *args):
    u"""
    XXX: This probably should be in 'library/'
    helpers that allow building getters on-the-fly
    Example:
        def plainValue(x): return x.value()
    can be built on-the-fly as
        method('value')
    """
    return lambda x: getattr(x, name)(*args)


def compose(outer, inner):
    return lambda *arg: outer(inner(*arg))


def identity(x):
    return x


# Helpers for getFromViewOrRecord.
def stringOfText(x):
    return compose(forceString, method('text'))(x)  # == forceString(x.text())


def recValue(fieldName, convFunc=identity):
    return compose(convFunc, method('value', fieldName))
