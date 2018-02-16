# -*- coding: utf-8 -*-
import locale
import os
import sys
import types
from PyQt4 import QtCore, QtGui
from collections import defaultdict

from Accounting.AccountingDialog import CAccountingDialog
from DataCheck.LogicalControlDoubles import CControlDoubles
from Events.Action import CAction, CActionType
from Events.ActionEditDialog import CActionEditDialog
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from Events.CreateEvent import editEvent, requestNewEvent
from Events.EditDispatcher import getEventFormClass
from Events.EventCashPage import CPaymentsModel
from Events.EventInfo import CEventInfo
from Events.TempInvalidDuplicateEditDialog import CTempInvalidDuplicateEditDialog
from Events.TempInvalidEditDialog import CTempInvalidEditDialog, CTempInvalidCreateDialog
from Events.TempInvalidInfo import CTempInvalidInfo, CTempInvalidDuplicateInfo
from Events.Utils import getActionTypeDescendants, getEventContext, getEventContextData, \
    getEventName, getEventPurposeId, getPayStatusMaskByCode, \
    getPayStatusValueByCode, getWorkEventTypeFilter, payStatusText, \
    CPayStatus, getEventTypeForm
from Exchange.MIP.MIPWinSrv import CMIPWinSrv
from Exchange.MIP.WSMCC import CWSMCC
from Exchange.R23.ExamPlan.Utils import Quarter, ExamKind
from Exchange.R23.netrica.services import NetricaServices
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from Orgs.Orgs import selectOrganisation
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import getOrganisationShortName, getOrgStructureAddressIdList, \
    getOrgStructureDescendants, getOrgStructures, getPersonInfo
from RefBooks.RBCancellationReasonList import CRBCancellationReasonList
from Registry.BeforeRecordClient import printOrder
from Registry.CPropertysComboBox import CFilterPropertyOptionsItem
from Registry.ClientEditDialog import CClientEditDialog
from Registry.ComplaintsEditDialog import CComplaintsEditDialog
from Registry.CustomizableRegistry import CStandardRegistryWidget, CCustomizableRegistryWidget
from Registry.DeferredQueueWindow import CCreateDeferredQueue
from Registry.FastFind import CFastFindClientWindow
from Registry.HospitalizationTransferDialog import CHospitalizationTransferDialog
from Registry.LocationCardTypeEditor import CLocationCardTypeEditor
from Registry.ReferralEditDialog import CReferralEditDialog
from Registry.RegistryQueueModels import CQueueModel, CVisitByQueueModel
from Registry.RegistryTable import CActionsTableModel, CActionsAnalysesTableModel, CEventAccActionsTableModel, \
    CEventActionsTableModel, \
    CEventDiagnosticsTableModel, CEventsTableModel, CEventVisitsTableModel, \
    CExpertTempInvalidDuplicatesTableModel, \
    CExpertTempInvalidPeriodsTableModel, CExpertTempInvalidTableModel, \
    CRecommendationsModel, CInputReferralsModel, COutgoingReferralsModel
from Registry.StatusObservationClientEditor import CStatusObservationClientEditor
from Registry.Utils import formatDocument, formatPolicy, getClientBanner, getClientContextData, \
    getClientInfo2, getClientInfoEx, getClientMiniInfo, \
    getFullClientInfoAsHtml, CCheckNetMixin, readOMSBarCode, \
    checkTempInvalidNumber, CBarCodeReaderThread
from Registry.VIPStatusCommentEditDialog import CVIPStatusCommentEditDialog
from Reports.ReportBase import CReportBase
from Reports.ReportF30PRR import CReportF30PRR
from Reports.ReportInformationCost import CReportInformationCost
from Reports.ReportView import CReportViewDialog
from Resources.JobTicketReserveMixin import CJobTicketReserveMixin
from ScardsModule.scard import Scard
from Timeline.TimeTable import formatTimeRange
from Ui_Registry import Ui_Form
from Users.Rights import urAdmin, urEditLocationCard, urEditStatusObservationClient, \
    urQueueDeletedTime, urQueueToSelfDeletedTime, urRegControlDoubles, \
    urRegTabReadActions, urRegTabReadAmbCard, urRegTabReadAmbulance, \
    urRegTabReadEvents, urRegTabReadExpert, urRegTabReadRegistry, \
    urRegTabWriteActions, urRegTabWriteEvents, urRegTabWriteExpert, \
    urRegTabWriteRegistry, urRegWithoutSearch, urSeeStaff, \
    urCreateEventFromRecommendations, urAddClient, urChangeEventType, \
    urEditSetVIPStatus, urSetVIPComment
from Users.UserInfo import CUserInfo
from library import database
from library.DateEdit import CDateEdit
from library.LoggingModule import Logger
from library.Preferences import isPython27
from library.PreferencesMixin import CDialogPreferencesMixin
from library.PrintInfo import CInfoContext
from library.PrintTemplates import additionalCustomizePrintButton, applyTemplate, directPrintTemplate, \
    getFirstPrintTemplate, getPrintAction, CPrintAction, compileAndExecTemplate
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, toVariant, getVal, addDots, formatRecordsCount, \
    formatRecordsCount2, formatSex, formatSNILS, quote
from library.constants import atcAmbulance
from library.crbcombobox import CRBComboBox, CRBModel
from library.database import decorateString
from library.simple_thread import SimpleThread
from library.web import openURLinBrowser


class CRegistryWindow(
    QtGui.QScrollArea,
    Ui_Form,
    CDialogPreferencesMixin,
    CCheckNetMixin,
    CVisibleControlMixin,
    CJobTicketReserveMixin
):
    u"""
        Окно для просмотра списка пациентов,
        обеспечивает возможность фильтрации, сортировки, редактирования
        описания пациента, перехода к связанным с данным пациентом event-ов
        и создания новых event-ов
    """

    isTabEventAlreadyLoad = False
    isTabActionsAlreadyLoad = False
    isTabExpertAlreadyLoad = False

    def __init__(self, parent):
        super(CRegistryWindow, self).__init__(parent)
        # raise Exception()
        CCheckNetMixin.__init__(self)
        CJobTicketReserveMixin.__init__(self)
        Logger.logWindowAccess(
            windowName=type(self).__name__,
            login_id=Logger.loginId,
            notes=u'Регистрационная карточка. Инициализация'
        )
        self.internal = QtGui.QWidget(self)
        self.setObjectName('RegistryWindow')
        self.setWidget(self.internal)
        self.setupUi(self.internal)
        curYear = QtCore.QDate.currentDate().year()
        self.edtFilterEndBirthYear.setMaximum(curYear)
        self.edtFilterEndBirthYear.setValue(curYear)
        self.edtFilterBegBirthYear.setMaximum(curYear)
        # Заполнение элементов комбобокса переведенными значениями из первоисточника
        self.cmbFilterActionStatus.clear()
        self.cmbFilterActionStatus.addItems(CActionType.retranslateClass(False).statusNames)
        self.setWidgetResizable(True)

        self.setupRegistryWidget()
        self.updateClientsListRequest = False

        self.cmbFilterVisitPerson.setOrgId(None)
        self.cmbFilterVisitPerson.setAddNone(False)
        self.cmbFilterVisitPerson.addNotSetValue()

        #        self.addModels('Clients', CClientsTableModel(self))
        self.addModels('Queue', CQueueModel(self))
        self.addModels('VisitByQueue', CVisitByQueueModel(self))

        self.addModels('Events', CEventsTableModel(self, self.registryWidget().model().recordCache()))
        self.addModels('EventDiagnostics', CEventDiagnosticsTableModel(self))
        self.addModels('EventActions', CEventActionsTableModel(self))
        self.addModels('EventVisits', CEventVisitsTableModel(self))
        self.addModels('EventAccActions', CEventAccActionsTableModel(self))
        self.addModels('EventPayments', CPaymentsModel(self))
        self.addModels('ActionsStatus', CActionsTableModel(self, self.registryWidget().model().recordCache(),
                                                           self.modelEvents.recordCache()))
        self.addModels('ActionsStatusProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsDiagnostic', CActionsTableModel(self, self.registryWidget().model().recordCache(),
                                                               self.modelEvents.recordCache()))
        self.addModels('ActionsDiagnosticProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsCure', CActionsTableModel(self, self.registryWidget().model().recordCache(),
                                                         self.modelEvents.recordCache()))
        self.addModels('ActionsCureProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsMisc', CActionsTableModel(self, self.registryWidget().model().recordCache(),
                                                         self.modelEvents.recordCache()))
        self.addModels('ActionsMiscProperties', CActionPropertiesTableModel(self))
        self.addModels('ActionsAnalyses', CActionsAnalysesTableModel(self, self.registryWidget().model().recordCache(),
                                                                     self.modelEvents.recordCache()))
        self.addModels('ActionsAnalysesProperties', CActionPropertiesTableModel(self))
        self.addModels('ExpertTempInvalid',
                       CExpertTempInvalidTableModel(self, self.registryWidget().model().recordCache()))
        self.addModels('ExpertTempInvalidPeriods', CExpertTempInvalidPeriodsTableModel(self))
        self.addModels('ExpertTempInvalidDuplicates', CExpertTempInvalidDuplicatesTableModel(self))
        self.addModels('ExpertDisability',
                       CExpertTempInvalidTableModel(self, self.registryWidget().model().recordCache()))
        self.addModels('ExpertDisabilityPeriods', CExpertTempInvalidPeriodsTableModel(self))
        self.addModels('ExpertVitalRestriction',
                       CExpertTempInvalidTableModel(self, self.registryWidget().model().recordCache()))
        self.addModels('ExpertVitalRestrictionPeriods', CExpertTempInvalidPeriodsTableModel(self))
        self.addModels('Recommendations', CRecommendationsModel(self))
        self.addModels('InputReferrals', CInputReferralsModel(self))
        self.addModels('OutgoingReferrals', COutgoingReferralsModel(self))

        self.actEditClient = QtGui.QAction(u'Изменить описание клиента', self)

        self.actEditClient.setObjectName('actEditClient')
        self.actEditLocationCard = QtGui.QAction(u'Изменить место нахождения амбулаторной карты', self)
        self.actEditLocationCard.setObjectName('actEditLocationCard')
        self.actEditStatusObservationClient = QtGui.QAction(u'Изменить статус наблюдения пациента', self)
        self.actEditStatusObservationClient.setObjectName('actEditStatusObservationClient')
        self.actPrintClient = getPrintAction(self, 'token', u'Напечатать шаблон')
        self.actPrintClient.setObjectName('actPrintClient')
        self.actPrintClientLabel = QtGui.QAction(u'Напечатать визитку пациента', self)
        self.actPrintClientLabel.setObjectName('actPrintClientLabel')
        self.actSearchInDiabetRegistry = QtGui.QAction(u'Найти пациента в Регистре Диабета', self)
        self.actSearchInDiabetRegistry.setObjectName('actSearchInDiabetRegistry')
        self.actPrintClientLabel.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT + QtCore.Qt.Key_F6))
        self.clientLabelTemplate = getFirstPrintTemplate('clientLabel')
        self.actPrintClientList = QtGui.QAction(u'Напечатать список пациентов', self)
        self.actPrintClientList.setObjectName('actPrintClientList')
        self.actEventPrint = CPrintAction(u'Напечатать список обращений', None, self, self)
        self.actEventPrint.setObjectName('actEventPrint')
        self.actEventListPrintTemplate = getPrintAction(self, 'eventList', u'Напечатать шаблон по списку обращений')
        self.actEventListPrintTemplate.setObjectName('actEventListPrintTemplate')
        self.actEventEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actEventEditClient.setObjectName('actEventEditClient')
        self.actAmbCardEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actAmbCardEditClient.setObjectName('actAmbCardEditClient')
        self.actActionEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actActionEditClient.setObjectName('actActionEditClient')
        self.actEditActionEvent = QtGui.QAction(u'Редактировать обращение', self)
        self.actEditActionEvent.setObjectName('actEditActionEvent')
        self.actExpertPrint = CPrintAction(u'Напечатать список документов ВУТ', None, self, self)
        self.actExpertPrint.setObjectName('actExpertPrint')
        self.actExpertEditClient = QtGui.QAction(u'Изменить описание клиента', self)
        self.actExpertEditClient.setObjectName('actExpertEditClient')
        self.actExpertTempInvalidDuplicate = QtGui.QAction(u'Учесть дубликат документа', self)
        self.actExpertTempInvalidDuplicate.setObjectName('actExpertTempInvalidDuplicate')
        self.actExpertTempInvalidNext = QtGui.QAction(u'Следующий документ', self)
        self.actExpertTempInvalidNext.setObjectName('actExpertTempInvalidNext')
        self.actExpertTempInvalidPrev = QtGui.QAction(u'Предыдущий документ', self)
        self.actExpertTempInvalidPrev.setObjectName('actExpertTempInvalidPrev')
        self.actSetToDeferredQueue = QtGui.QAction(u'Отложенная запись на прием', self)
        self.actSetToDeferredQueue.setObjectName('actSetToDeferredQueue')
        self.actListVisitByQueue = QtGui.QAction(u'Протокол обращений пациента по предварительной записи', self)
        self.actListVisitByQueue.setObjectName('actListVisitByQueue')
        self.actLocationCard = QtGui.QAction(u'Изменить место нахождения амбулаторной карты', self)
        self.actLocationCard.setObjectName('actLocationCard')
        self.actStatusObservationClient = QtGui.QAction(u'Изменить статус наблюдения пациента', self)
        self.actStatusObservationClient.setObjectName('actStatusObservationClient')
        self.actControlDoublesRecordClient = QtGui.QAction(u'Логический контроль двойников', self)
        self.actControlDoublesRecordClient.setObjectName('actControlDoublesRecordClient')
        self.actReservedOrderQueueClient = QtGui.QAction(u'Использовать бронь в очереди', self)
        self.actReservedOrderQueueClient.setObjectName('actReservedOrderQueueClient')
        self.actAmbCreateEvent = QtGui.QAction(u'Новое обращение', self)
        self.actAmbCreateEvent.setObjectName('actAmbCreateEvent')
        self.actAmbDeleteOrder = QtGui.QAction(u'Удалить из очереди', self)
        self.actAmbDeleteOrder.setObjectName('actAmbDeleteOrder')
        self.actAmbChangeNotes = QtGui.QAction(u'Изменить жалобы/примечания', self)
        self.actAmbChangeNotes.setObjectName('actAmbChangeNotes')
        self.actAmbPrintOrder = QtGui.QAction(u'Напечатать направление', self)
        self.actAmbPrintOrder.setObjectName('actAmbPrintOrder')
        self.actAmbPrintOrder.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT + QtCore.Qt.Key_F4))
        self.actAmbPrintOrderTemplate = getPrintAction(self, 'regQueue', u'Напечатать направление (шаблон)')
        self.actAmbPrintOrderTemplate.setObjectName('actAmbPrintOrderTemplate')
        self.actJumpQueuePosition = QtGui.QAction(u'Перейти в график', self)
        self.actJumpQueuePosition.setObjectName('actJumpQueuePosition')
        self.actPrintBeforeRecords = QtGui.QAction(u'Печать предварительной записи', self)
        self.actPrintBeforeRecords.setObjectName('actPrintBeforeRecords')
        self.actShowPreRecordInfo = QtGui.QAction(u'Свойства записи', self)
        self.actShowPreRecordInfo.setObjectName('actShowPreRecordInfo')

        # if QtGui.qApp.userHasRight(urEditSetVIPStatus):
        self.actSetVIPStatus = QtGui.QAction(u'Выставить/изменить VIP-статус', self)
        self.actSetVIPStatus.setObjectName('actSetVIPStatus')
        self.actDelVIPStatus = QtGui.QAction(u'Снять VIP-статус', self)
        self.actDelVIPStatus.setObjectName('actDelVIPStatus')

        # if QtGui.qApp.userHasRight(urSetVIPComment) or QtGui.qApp.userHasRight(urEditSetVIPStatus):
        self.actEditVIPComment = QtGui.QAction(u'Изменить комментарий к VIP-статусу', self)
        self.actEditVIPComment.setObjectName('actEditVIPComment')

        self.actOpenAccountingByEvent = QtGui.QAction(u'Перейти к счетам', self)

        self.actOpenAccountingByEvent.setObjectName('actOpenAccountingByEvent')
        self.actOpenAccountingByAction = QtGui.QAction(u'Перейти к счетам', self)
        self.actOpenAccountingByAction.setObjectName('actOpenAccountingByAction')
        self.actOpenAccountingByVisit = QtGui.QAction(u'Перейти к счетам', self)
        self.actOpenAccountingByVisit.setObjectName('actOpenAccountingByVisit')
        self.actPrintF30PRR = QtGui.QAction(u'Напечатать Ф. 30 для ПРР', self)
        self.actPrintF30PRR.setObjectName('actPrintF30PRR')
        self.actInformationCost = QtGui.QAction(u'Справка о стоимости лечения', self)
        self.actInformationCost.setObjectName('actInformationCost')
        self.actRecreateEventWithAnotherType = QtGui.QAction(u'Сменить тип события', self)
        self.actRecreateEventWithAnotherType.setObjectName('actRecreateEventWithAnotherType')

        self.actTransferHospitalization = QtGui.QAction(u'Перенос госпитализации', self)
        self.actTransferHospitalization.setObjectName('actTransferHospitalization')

        self.mnuPrint = QtGui.QMenu(self)
        self.mnuPrint.setObjectName('mnuPrint')
        self.mnuPrint.addAction(self.actPrintClient)
        self.mnuPrint.addAction(self.actPrintClientLabel)
        self.mnuPrint.addAction(self.actPrintClientList)
        self.mnuPrint.addAction(self.actPrintF30PRR)
        self.mnuPrint.addAction(self.actInformationCost)
        self.addBarcodeScanAction('actScanBarcode')

        additionalMenuItems = defaultdict(list)
        db = QtGui.qApp.db
        tableUrls = db.table('AdditionalFeaturesUrl')
        self.additionalMenuItems = []
        records = db.getRecordList(tableUrls, '*')
        for i, record in enumerate(records):
            name = forceString(record.value('name'))
            template = forceString(record.value('template'))
            menuItemName = 'additionalFeaturesUrl%d' % i
            action = QtGui.QAction(name, self)
            triggerName = 'on_actAdditionalFeatures%d_triggered' % i
            trigger = self.createAdditionalFeaturesTrigger(triggerName, name, template)
            setattr(self, triggerName, types.MethodType(trigger, self))
            self.connect(action, QtCore.SIGNAL('triggered()'), getattr(self, triggerName))
            setattr(self, menuItemName, action)
            getattr(self, menuItemName).setObjectName(menuItemName)
            tabKeys = ['tabRegistry', 'tabEvents', 'tabAmbCard', 'tabActions', 'tabExpert', 'tabAmbulance']
            activeTabs = dict([(key, forceBool(record.value(key))) for key in tabKeys])
            for key, value in activeTabs.items():
                if value:
                    additionalMenuItems[key].append(action)

        self.teFullClientInfo.setReadOnly(True)

        self.btnPrint.setMenu(self.mnuPrint)
        self.btnPrint.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_F6))
        if forceBool(getVal(
                QtGui.qApp.preferences.appPrefs, 'SocCard_SupportEnabled', False)):
            self.enableCardReaderSupport()

        self.setModels(self.tblQueue, self.modelQueue, self.selectionModelQueue)
        self.setModels(self.tblVisitByQueue, self.modelVisitByQueue, self.selectionModelVisitByQueue)
        self.setModels(self.tblEvents, self.modelEvents, self.selectionModelEvents)
        self.setModels(self.tblRecommendations, self.modelRecommendations, self.selectionModelRecommendations)
        self.setModels(self.tblInputReferrals, self.modelInputReferrals, self.selectionModelInputReferrals)
        self.setModels(self.tblOutgoingReferrals, self.modelOutgoingReferrals, self.selectionModelOutgoingReferrals)
        self.setModels(self.tblEventAccActions, self.modelEventAccActions, self.selectionModelEventAccActions)
        self.setModels(self.tblEventPayments, self.modelEventPayments, self.selectionModelEventPayments)
        self.tblEventDiagnostics.setModel(self.modelEventDiagnostics)
        self.tblEventActions.setModel(self.modelEventActions)
        self.tblEventVisits.setModel(self.modelEventVisits)
        self.cmbFilterDocumentType.setTable('rbDocumentType', True,
                                            'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.cmbFilterPolicyType.setTable('rbPolicyType', True)
        self.cmbFilterAttachType.setTable('rbAttachType', True)
        self.cmbFilterSocStatType.setTable('vrbSocStatusType', True)
        self.cmbFilterSocStatType.setShowFields(CRBComboBox.showNameAndCode)
        self.cmbFilterLocationCardType.setTable('rbLocationCardType', True)
        self.cmbFilterStatusObservationType.setTable('rbStatusObservationClientType', True)
        self.cmbFilterHurtType.setTable('rbHurtType', True)
        self.tblInputReferrals.setSortingEnabled(True)
        self.tblOutgoingReferrals.setSortingEnabled(True)

        self.idValidator = CIdValidator(self)
        self.edtFilterId.setValidator(self.idValidator)
        self.edtFilterBirthDay.setHighlightRedDate(False)
        self.cmbFilterAddressStreet.setAddNone(True)

        self.chkFilterShowDeads.setVisible(False)

        # Скрытие полей для Казахстана
        filterVisible = QtGui.qApp.defaultKLADR().startswith('90')
        self.edtFilterSNILS.setVisible(not filterVisible)
        self.chkFilterSNILS.setVisible(not filterVisible)
        self.chkFilterPolicy.setVisible(not filterVisible)
        self.cmbFilterPolicyType.setVisible(not filterVisible)
        self.cmbFilterPolicyInsurer.setVisible(not filterVisible)
        self.edtFilterPolicySerial.setVisible(not filterVisible)
        self.edtFilterPolicyNumber.setVisible(not filterVisible)
        self.cmbFilterAddressCity.setVisible(not filterVisible)
        self.chkFilterAddress.setVisible(not filterVisible)
        self.cmbFilterAddressType.setVisible(not filterVisible)
        self.cmbFilterAddressStreet.setVisible(not filterVisible)
        self.lblFilterAddressHouse.setVisible(not filterVisible)
        self.edtFilterAddressHouse.setVisible(not filterVisible)
        self.lblFilterAddressCorpus.setVisible(not filterVisible)
        self.edtFilterAddressCorpus.setVisible(not filterVisible)
        self.lblFilterAddressFlat.setVisible(not filterVisible)
        self.edtFilterAddressFlat.setVisible(not filterVisible)
        self.chkFilterIIN.setVisible(filterVisible)
        self.edtFilterIIN.setVisible(filterVisible)

        # Скрытие чекбокса умерших пациентов
        if QtGui.qApp.checkGlobalPreference('20', u'всех') or QtGui.qApp.checkGlobalPreference('20',
                                                                                               u'до начала текущего года'):
            self.chkFilterShowDeads.setVisible(True)

        # atronah: Служит для задания связи между "галочками" фильтров и виджетами,
        # которые должны (де-)актив-ся при смене состояния этих галочек
        self.chkListOnClientsPage = [
            (self.chkFilterId, [self.edtFilterId, self.cmbFilterAccountingSystem]),
            (self.chkFilterLastName, [self.edtFilterLastName]),
            (self.chkFilterFirstName, [self.edtFilterFirstName]),
            (self.chkFilterPatrName, [self.edtFilterPatrName]),
            (self.chkFilterBirthDay, [self.edtFilterBirthDay]),
            (self.chkFilterSex, [self.cmbFilterSex]),
            (self.chkFilterContact, [self.edtFilterContact]),
            (self.chkFilterSNILS, [self.edtFilterSNILS]),
            (self.chkFilterIIN, [self.edtFilterIIN]),
            (self.chkFilterDocument,
             [self.cmbFilterDocumentType, self.edtFilterDocumentSerial, self.edtFilterDocumentNumber]),
            (self.chkFilterPolicy, [self.cmbFilterPolicyType, self.cmbFilterPolicyInsurer, self.edtFilterPolicySerial,
                                    self.edtFilterPolicyNumber]),
            (self.chkFilterWorkOrganisation, [self.cmbWorkOrganisation, self.btnSelectWorkOrganisation]),
            (self.chkFilterHurtType, [self.cmbFilterHurtType]),
            (self.chkFilterSocStatuses, [self.cmbFilterSocStatClass, self.cmbFilterSocStatType]),
            (self.chkFilterLocationCardType, [self.cmbFilterLocationCardType]),
            (self.chkFilterStatusObservationType, [self.cmbFilterStatusObservationType]),
            (self.chkFilterCreatePerson, [self.cmbFilterCreatePerson]),
            (self.chkFilterCreateDate, [self.edtFilterBegCreateDate, self.edtFilterEndCreateDate]),
            (self.chkFilterModifyPerson, [self.cmbFilterModifyPerson]),
            (self.chkFilterModifyDate, [self.edtFilterBegModifyDate, self.edtFilterEndModifyDate]),
            (self.chkFilterEvent, [self.chkFilterFirstEvent, self.edtFilterEventBegDate, self.edtFilterEventEndDate]),
            (self.chkFilterAge,
             [self.edtFilterBegAge, self.cmbFilterBegAge, self.edtFilterEndAge, self.cmbFilterEndAge]),
            (self.chkFilterBirthYear, [self.edtFilterBegBirthYear, self.edtFilterEndBirthYear]),
            (self.chkFilterAddress, [self.cmbFilterAddressType,
                                     self.cmbFilterAddressCity,
                                     self.cmbFilterAddressStreet,
                                     self.lblFilterAddressHouse, self.edtFilterAddressHouse,
                                     self.lblFilterAddressCorpus, self.edtFilterAddressCorpus,
                                     self.lblFilterAddressFlat, self.edtFilterAddressFlat,
                                     ]),
            (self.chkFilterBirthMonth, [self.cmbFilterBirthMonth]),
            (self.chkFilterAddressOrgStructure,
             [self.cmbFilterAddressOrgStructureType, self.cmbFilterAddressOrgStructure]),
            (self.chkFilterBeds, [self.cmbFilterStatusBeds, self.cmbFilterOrgStructureBeds]),
            (self.chkFilterAddressIsEmpty, []),
            (self.chkFilterAttachType, [self.cmbFilterAttachCategory, self.cmbFilterAttachType]),
            (self.chkFilterAttach, [self.cmbFilterAttachOrganisation, self.btnFilterAttachOrganisation]),
            (self.chkFilterAttachNonBase, []),
            (self.chkFilterTempInvalid, [self.edtFilterBegTempInvalid, self.edtFilterEndTempInvalid]),
            (self.chkFilterRPFUnconfirmed, []),
            (self.chkFilterShowDeads, []),
            (self.chkFilterRPFConfirmed, [self.edtFilterBegRPFConfirmed, self.edtFilterEndRPFConfirmed]),
            (self.chkFilterContingentDD, [self.cmbFilterContingentDD]),
            (self.chkFilterMKBRange_Client,
             [self.edtFilterMKBTop_Client, self.edtFilterMKBBottom_Client, self.cmbFilterEventDiagnosisType_Client]),
            (self.chkUnconscious, []),
            (self.chkClientExamPlan, [self.cmbClientExamPlanKind,
                                      self.cmbClientExamPlanYear,
                                      self.cmbClientExamPlanQuarter])
        ]

        self.cmbFilterAccountingSystem.setTable('rbAccountingSystem', True)
        self.cmbFilterAccountingSystem.setValue(forceRef(getVal(
            QtGui.qApp.preferences.appPrefs, 'FilterAccountingSystem', 0)))

        self.chkListOnEventsPage = []

        self.__actionTypeIdListByClassPage = [None] * 5
        self.__tempInvalidDocTypeIdListByTypePage = [None] * 3

        QtCore.QMetaObject.connectSlotsByName(self)  # т.к. в setupUi параметр не self
        # FIXME: atronah: это актуально только для стандартной картотеки и не должно выполняться для Настраиваемой.
        self.registryWidget().viewWidget().setColumnHidden(6, True)  # Документ
        self.registryWidget().viewWidget().setColumnHidden(7, True)  # Полис ОМС
        self.registryWidget().viewWidget().setColumnHidden(8, True)  # Полис ДМС
        self.registryWidget().viewWidget().setColumnHidden(13, True)  # Адрес регистрации
        self.registryWidget().viewWidget().setColumnHidden(14, True)  # БС
        self.registryWidget().viewWidget().setColumnHidden(15, True)  # VIP
        self.registryWidget().viewWidget().setColumnHidden(9, True)  # Занятость
        self.registryWidget().viewWidget().setColumnHidden(10, True)  # Контакты

        self.RPFAccountingSystemId = forceRef(
            QtGui.qApp.db.translate('rbAccountingSystem', 'code', '1', 'id'))  # FIXME: record code in code
        if not self.RPFAccountingSystemId:
            self.chkFilterRPFUnconfirmed.setEnabled(False)
            self.chkFilterRPFConfirmed.setEnabled(False)

        self.__filter = {}
        self.bufferRecordsOptionProperty = []

        # if QtGui.qApp.userHasRight(urEditSetVIPStatus):
        #    self.txtClientInfoBrowserEvents.actions.append(self.actSetVIPStatus)
        #    self.txtClientInfoBrowserEvents.actions.append(self.actDelVIPStatus)

        # if QtGui.qApp.userHasRight(urSetVIPComment) or QtGui.qApp.userHasRight(urEditSetVIPStatus):
        #    self.txtClientInfoBrowserEvents.actions.append(self.actEditVIPComment)

        self.txtClientInfoBrowser.actions.append(self.actEditClient)
        self.txtClientInfoBrowser.actions.append(self.actEditLocationCard)
        self.txtClientInfoBrowser.actions.append(self.actEditStatusObservationClient)
        self.txtClientInfoBrowserEvents.actions.append(self.actEventEditClient)
        self.txtClientInfoBrowserAmbCard.actions.append(self.actAmbCardEditClient)
        if QtGui.qApp.userHasRight(urAdmin) or QtGui.qApp.userHasRight(urChangeEventType):
            self.tblEvents.addPopupAction(self.actRecreateEventWithAnotherType)

        if QtGui.qApp.currentOrgInfis() == u'онко':
                self.tblEvents.addPopupAction(self.actTransferHospitalization)

        self.tblEvents.addPopupAction(self.actOpenAccountingByEvent)
        for act in additionalMenuItems['tabEvents']:
            self.tblEvents.addPopupAction(act)
        self.tblEvents.addPopupDelRow()
        self.tblEventActions.addPopupAction(self.actOpenAccountingByAction)
        for act in additionalMenuItems['tabAction']:
            self.tblEventActions.addPopupAction(act)
        self.tblEventVisits.addPopupAction(self.actOpenAccountingByVisit)

        popupList = [
            self.actSetToDeferredQueue,
            self.actListVisitByQueue,
            self.actLocationCard,
            self.actStatusObservationClient,
            self.actControlDoublesRecordClient,
            self.actReservedOrderQueueClient,
            self.actSearchInDiabetRegistry
        ]

        if u'онко' in forceString(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
            if QtGui.qApp.userHasRight(urSetVIPComment) or QtGui.qApp.userHasRight(urEditSetVIPStatus):
                popupList.append(self.actSetVIPStatus)

        self.registryWidget().viewWidget().createPopupMenu(popupList)
        for act in additionalMenuItems['tabRegistry']:
            self.registryWidget().viewWidget().addPopupAction(act)
        if isPython27():
            self.actSearchInDiabetRegistry.setEnabled(
                forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'UseDiaReg', '')))
        else:
            self.actSearchInDiabetRegistry.setEnabled(False)
        self.registryWidget().viewWidget().addPopupRecordProperies()

        popupList = [
            self.actAmbCreateEvent, self.actAmbDeleteOrder, self.actAmbChangeNotes, self.actAmbPrintOrder,
            self.actAmbPrintOrderTemplate, self.actJumpQueuePosition, self.actPrintBeforeRecords,
            self.actShowPreRecordInfo
        ]

        self.tblQueue.createPopupMenu(popupList)

        self.connect(self.registryWidget().viewWidget().popupMenu(), QtCore.SIGNAL('aboutToShow()'),
                     self.onListBeforeRecordClientPopupMenuAboutToShow)
        self.connect(self.tblQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onQueuePopupMenuAboutToShow)
        self.connect(self.tblEvents.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.checkTblEventsPopupMenu)
        self.connect(self.tblEventActions.popupMenu(), QtCore.SIGNAL('aboutToShow()'),
                     self.checkTblEventActionsPopupMenu)
        self.connect(self.tblEventVisits.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.checkTblEventVisitsPopupMenu)

        self.setFocusProxy(self.tabMain)
        self.internal.setFocusProxy(self.tabMain)
        self.tabMain.setFocusProxy(
            self.registryWidget().viewWidget())  # на первый взгляд не нужно, но строка ниже не справляется...
        self.tabRegistry.setFocusProxy(self.registryWidget().viewWidget())
        self.tabEvents.setFocusProxy(self.tblEvents)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        if not QtGui.qApp.isPNDDiagnosisMode():
            self.tabMain.removeTab(self.tabMain.indexOf(self.tabFullClientInfo))
            self.tabMain.removeTab(self.tabMain.indexOf(self.tabJournal))
            self.cmbFilterEventDiagnosisType_Client.hide()
            self.chkFilterMKBRange_Client.hide()
            self.edtFilterMKBBottom_Client.hide()
            self.edtFilterMKBTop_Client.hide()
            self.lblH1.hide()
            self.lblH2.hide()
            self.lblH3.hide()
        self.tabMainCurrentPage = self.tabMain.indexOf(self.tabRegistry)
        self.currentClientFromEvent = False
        self.currentClientFromAction = False
        self.currentClientFromExpert = False
        self.controlSplitter = self.splitterRegistry
        self.tabMain.setCurrentIndex(self.tabMainCurrentPage)
        self.loadDialogPreferences()
        self.cmbFilterAddressCity.setCode(QtGui.qApp.defaultKLADR())
        self.personInfo = CRBModel(self)
        self.personInfo.setTable('vrbPersonWithSpeciality')
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientInfoChanged()'), self.updateQueue)
        self.tabRegistry.addAction(self.actScanBarcode)

        self.setUserRights()

        # сканирование бар кода; КЭР
        self.addBarcodeScanAction('actScanBarcodeTabExpert')
        self.tabExpert.addAction(self.actScanBarcodeTabExpert)
        self.connect(self.actScanBarcodeTabExpert, QtCore.SIGNAL('triggered()'), self.on_actScanBarcodeTabExpert)

        # работа с УЭК
        if isPython27():
            self.connect(self.readUek, QtCore.SIGNAL('clicked()'), self.on_actReadUek)
            self.extUekService = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'MIP', False))
            self.intUekService = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'UEKDirect', False))
        else:
            self.connect(self.readUek, QtCore.SIGNAL('clicked()'), self.on_actReadUek)
            self.extUekService = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'MIP', False))
            self.intUekService = False

        self.readUek.setVisible(self.extUekService | self.intUekService)

        # сканирование полиса ОМС
        self.readBarCode.clicked.connect(self.on_actReadBarCode)
        self.readBarCode.setVisible(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderEnable', False)))
        self.omsPolisData = {'errorMessage': u'<Unknown error>'}

        # Направления
        if not QtGui.qApp.userHasRight(urCreateEventFromRecommendations):
            self.btnRecCancel.setVisible(False)
            self.btnRecNewEvent.setVisible(False)

        self._invisibleObjectsNameList = self.reduceNames(
            QtGui.qApp.userInfo.hiddenObjectsNameList(
                [self.moduleName()],
                True
            )
        ) if QtGui.qApp.userInfo else []
        self.updateVisibleState(self, self._invisibleObjectsNameList)

        self.chkFilterContingentDD.setEnabled(QtGui.qApp.checkContingentDDGlobalPreference())

        self.cmbFilterEventDiagnosisType_Client.setTable('rbDiagnosisType', True)

        self.cmbClientExamPlanKind.setEnum(ExamKind)
        self.cmbClientExamPlanYear.setValues(range(curYear - 3, curYear + 4))
        self.cmbClientExamPlanYear.setValue(curYear)
        self.cmbClientExamPlanQuarter.setEnum(Quarter, addNone=True)

        # ЭПОМС
        # i2340
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EPOMS', False)):
            self.readEpoms.setVisible(True)
            self.readEpoms.clicked.connect(self.on_actReadScard)
            self.cardReaderName = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'cardReader', 'none'))
        else:
            self.readEpoms.setVisible(False)

        pass
        self.enableBarCodeReader()

        # Надстройка для ПНД5
        # i3706
        if QtGui.qApp.isPNDDiagnosisMode():
            self.tabEventInternals.setTabText(0, u'ЛУД')
            self.tabEventInternals.setTabText(4, u'История')

    def enableBarCodeReader(self):
        # ==================================================
        # i3592
        if forceStringEx(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'б15' and \
                forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderEnable', False)
                          ):
            if not hasattr(QtGui.qApp, 'barCodethread'):
                QtGui.qApp.barCodethread = CBarCodeReaderThread(
                    forceString(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderName', u"COM3")))
                QtGui.qApp.barCodethread.start()
            QtGui.qApp.barCodethread.barCodeReader.read.connect(self.setVerifiedAction)
        # ==================================================

    def setVerifiedAction(self, result):
        if not QtGui.qApp.barCodethread.busyByEvent:
            if result:
                query = u"""
                  SELECT
                    Action.event_id
                  FROM
                    Action
                  WHERE
                    Action.id = %s
                    AND Action.deleted = 0
                """ % result['action_id']

                record = QtGui.qApp.db.getRecordEx(stmt=query)
                if record:
                    eventId = forceRef(record.value('event_id'))
                    if eventId:
                        # QtGui.qApp..barCodethread.barCodeReader.close = True
                        formClass = getEventFormClass(eventId)
                        dialog = formClass(self)
                        try:
                            dialog.load(eventId)
                            dialog.setVerifiedAction(result)
                            # dialog.setClientId(self.getCurrentClientId())
                            dialog.exec_()
                        finally:
                            self.enableBarCodeReader()
                else:
                    QtGui.QMessageBox.information(
                        self,
                        u'Сканер штрих-кодов: Внимание!',
                        u'Обращение по данному штрих-коду не найдено.',
                        QtGui.QMessageBox.Ok,
                        QtGui.QMessageBox.Ok
                    )
            pass

    # i2340
    def on_actReadScard(self):
        try:
            clientInfo = Scard().getClientInfo(self.cardReaderName, True)
            # self.edtFilterLastName.setText(getVal(clientInfo, 'lastname', ''))
            self.edtFilterLastName.setText(clientInfo['lastname'])
            self.edtFilterLastName.setEnabled(True)
            self.chkFilterLastName.setChecked(True)

            self.edtFilterFirstName.setText(clientInfo['name'])
            self.edtFilterFirstName.setEnabled(True)
            self.chkFilterFirstName.setChecked(True)

            self.edtFilterPatrName.setText(clientInfo['patrname'])
            self.edtFilterPatrName.setEnabled(True)
            self.chkFilterPatrName.setChecked(True)

            self.edtFilterBirthDay.clear()
            self.edtFilterBirthDay.addItem(clientInfo['birthday'])
            self.edtFilterBirthDay.setEnabled(True)
            self.chkFilterBirthDay.setChecked(True)

            # self.edtFilterSNILS.setText(clientInfo['SNILS'])
            # self.edtFilterSNILS.setEnabled(True)
            # self.chkFilterSNILS.setChecked(True)

            self.on_buttonBoxClient_apply()
        except Exception as e:
            QtGui.QMessageBox.warning(
                self,
                u'ОШИБКА',
                u"Картридер сообщил об ошибке. Проверьте вставлена ли карта правильно.",
                QtGui.QMessageBox.Ok
            )
            # self.readEpoms.setVisible(False)

    @staticmethod
    def moduleName():
        return u'RegistryWindow'

    @staticmethod
    def moduleTitle():
        return u'Картотека'

    @classmethod
    def hiddableChildren(cls):
        # TODO: atronah: решить проблему с игнором смены имен в файле интерфейса
        # один из вариантов решения: парсить ui-файл
        nameList = [
            (u'tabRegistry', u'Вкладка "Картотека"'),
            (u'tabEvents', u'Вкладка "Обращение"'),
            (u'tabAmbCard', u'Вкладка "Мед.карта"'),
            (u'tabActions', u'Вкладка "Обслуживание"'),
            (u'tabExpert', u'Вкладка "КЭР"'),
            (u'tabAmbulance', u'Вкладка "СМП"'),
            (u'tabFullClientInfo', u'Вкладка "Амб.карта"'),
            (u'tabJournal', u'Вкладка "Журнал посещений на день"'),
            (u'tabRecommendations', u'Вкладка "Рекомендации"'),
            (u'tabReferrals', u'Вкладка "Направления"'),
            (u'btnRecSetPerson2', u'Кнопка "Снять актуальность"')
        ]
        return cls.normalizeHiddableChildren(nameList)

    def setupRegistryWidget(self):
        baseName = u'registry.xml'

        fileName = os.path.join(unicode(QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())), baseName)
        if not os.path.exists(fileName):
            fileName = os.path.join(os.path.dirname(sys.argv[0]).decode(locale.getpreferredencoding()),
                                    baseName)

        customizableRegistryFile = QtCore.QFile(fileName)

        if customizableRegistryFile.open(QtCore.QFile.ReadOnly):
            try:
                # Активация настраиваемой картотеки
                self.registryWidgetSwitcher.setCurrentIndex(1)
                self.registryWidget().setStyleSheet(u'QToolBox {font: bold 12px}')
                self.registryWidget().setSource(customizableRegistryFile)
                # self.registryWidget().model().updateContent()
                self.gbFilter.setVisible(False)
                self.tabBeforeRecord.setVisible(False)
                self.lblClientsCount.setVisible(True)
            finally:
                customizableRegistryFile.close()
        else:
            self.registryWidgetSwitcher.setCurrentIndex(0)
            self.lblClientsCount.setVisible(True)
            self.connect(self.registryWidget().model(), QtCore.SIGNAL('itemsCountChanged(int)'),
                         self.onRegistryItemCountChanged)

        self.registryWidget().selectionModel().currentChanged.connect(self.onCurrentClientChanged)
        self.registryWidget().viewWidget().doubleClicked.connect(self.registryContentDoubleClicked)
        self.registryWidget().requestNewEvent.connect(self.requestNewEvent)

    def registryWidget(self):
        return self.registryWidgetSwitcher.currentWidget()

    def updateRegistryContent(self, posToId=None):
        if isinstance(self.registryWidget(), CStandardRegistryWidget):
            self.updateStandardRegistryWidget(posToId)
        else:
            view = self.registryWidget().viewWidget()
            model = self.registryWidget().model()
            model.updateContent(posToId if posToId not in self.registryWidget().model().idList() else None)
            for r in xrange(model.rowCount()):
                if model.itemId(model.index(r, 0)) == posToId:
                    view.selectRow(r)
                    break

    def updateStandardRegistryWidget(self, posToId=None):
        """
            в соответствии с фильтром обновляет список пациентов.
        """
        db = QtGui.qApp.db

        def calcBirthDate(cnt, unit):
            result = QtCore.QDate.currentDate()
            if unit == 3:  # дни
                result = result.addDays(-cnt)
            elif unit == 2:  # недели
                result = result.addDays(-cnt * 7)
            elif unit == 1:  # месяцы
                result = result.addMonths(-cnt)
            else:  # года
                result = result.addYears(-cnt)
            return result

        def addAddressCond(cond, addrType, addrIdList):
            tableClientAddress = db.table('ClientAddress')
            subcond = [tableClientAddress['client_id'].eqEx('`Client`.`id`'),
                       # atronah: если в подзапросе использовать CA.client_id = Client.id, то запрос падает с ошибкой
                       # "Error Code: 1235.
                       # This version of MariaDB doesn't yet support 'SUBQUERY in ROW in left expression of IN/ALL/ANY'"
                       tableClientAddress['id'].eqEx(
                           '(SELECT MAX(`id`) FROM `ClientAddress` AS `CA` WHERE `CA`.`client_id` =%s AND `CA`.`type`=%d)' % (
                               tableClientAddress['client_id'].name(), addrType))
                       ]
            if addrIdList == None:
                subcond.append(tableClientAddress['address_id'].isNull())
            else:
                subcond.append(tableClientAddress['address_id'].inlist(addrIdList))
            cond.append(db.existsStmt(tableClientAddress, subcond))

        def addAttachCond(cond, orgCond, attachCategory, attachTypeId):
            outerCond = ['ClientAttach.client_id = Client.id']
            outerCond.append('ClientAttach.deleted = 0')
            innerCond = ['CA2.client_id = ClientAttach.client_id']
            if orgCond:
                outerCond.append(orgCond)
            if attachTypeId:
                outerCond.append('attachType_id=%d' % attachTypeId)
                innerCond.append('CA2.attachType_id=%d' % attachTypeId)
            else:
                if attachCategory == 1:
                    innerCond.append('rbAttachType2.temporary=0')
                elif attachCategory == 2:
                    innerCond.append('rbAttachType2.temporary')
                elif attachCategory == 3:
                    innerCond.append('rbAttachType2.outcome')
                elif attachCategory == 0:
                    outerCond.append('rbAttachType.outcome=0')
                    innerCond.append('rbAttachType2.temporary=0')
                else:
                    attachCategory = None
            tblCA2 = db.table('ClientAttach').alias('CA2')
            innerCond.append(
                db.joinOr([tblCA2['endDate'].isNull(), tblCA2['endDate'].dateGt(QtCore.QDate.currentDate())]))

            if attachCategory is None and attachTypeId is None:
                innerStmt = '1'
            else:
                innerStmt = """
                    ClientAttach.id = (SELECT MAX(CA2.id)
                                       FROM ClientAttach AS CA2
                                           LEFT JOIN rbAttachType AS rbAttachType2 ON rbAttachType2.id = CA2.attachType_id
                                       WHERE %s)
                """ % db.joinAnd(innerCond)

            stmt = '''EXISTS (SELECT ClientAttach.id
               FROM ClientAttach
               LEFT JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
               WHERE %s
               AND %s)'''
            cond.append(stmt % (db.joinAnd(outerCond), innerStmt))

        def hideLeaversPatients(cond):
            if filter.get('showDeads', False):
                if QtGui.qApp.hideAllLeavers() or QtGui.qApp.hideLeaversBeforeCurrentYearPatients():
                    stmt = '''NOT EXISTS (SELECT ClientAttach.id
                       FROM ClientAttach
                       INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
                       WHERE ClientAttach.deleted = 0 AND rbAttachType.outcome != 0 AND ClientAttach.client_id=Client.id AND %s
                       )''' % (
                        'NOT YEAR(ClientAttach.begDate)=YEAR(CURRENT_DATE)' if QtGui.qApp.hideLeaversBeforeCurrentYearPatients()
                        else '1')
                    cond.append(stmt)

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            tableClient = db.table('Client')
            filter = self.__filter
            table = tableClient
            cond = [tableClient['deleted'].eq(0)]
            if 'id' in filter:
                accountingSystemId = filter.get('accountingSystemId', None)
                if accountingSystemId:
                    tableIdentification = db.table('ClientIdentification')
                    table = table.leftJoin(tableIdentification, tableIdentification['client_id'].eq(tableClient['id']))
                    cond.append(tableIdentification['accountingSystem_id'].eq(accountingSystemId))
                    cond.append(tableIdentification['identifier'].eq(filter['id']))
                    cond.append(tableIdentification['deleted'].eq(0))
                else:
                    cond.append(tableClient['id'].eq(filter['id']))
            database.addCondLike(cond, tableClient['lastName'], addDots(filter.get('lastName', '')))
            database.addCondLike(cond, tableClient['firstName'], addDots(filter.get('firstName', '')))
            # if filter.get('isUnconscious', None):
            #    database.addCondLike(cond, tableClient['isUnconscious'], addDots(filter.get('isUnconscious', '')))
            database.addCondLike(cond, tableClient['patrName'], addDots(filter.get('patrName', '')))
            if 'birthDate' in filter:
                birthDate = filter['birthDate']
                if birthDate is not None and birthDate.isNull():
                    birthDate = None
                cond.append(tableClient['birthDate'].eq(birthDate))
            self.addEqCond(cond, tableClient, 'createPerson_id', filter, 'createPersonIdEx')
            self.addDateCond(cond, tableClient, 'createDatetime', filter, 'begCreateDateEx', 'endCreateDateEx')
            self.addEqCond(cond, tableClient, 'modifyPerson_id', filter, 'modifyPersonIdEx')
            self.addDateCond(cond, tableClient, 'modifyDatetime', filter, 'begModifyDateEx', 'endModifyDateEx')
            event = filter.get('event', None)
            if event:
                tableEvent = db.table('Event')
                tableEventType = db.table('EventType')
                tableEventTypePurpose = db.table('rbEventTypePurpose')
                table = table.innerJoin(tableEvent, tableEvent['client_id'].eq(tableClient['id']))
                table = table.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
                table = table.innerJoin(tableEventTypePurpose,
                                        tableEventTypePurpose['id'].eq(tableEventType['purpose_id']))
                cond.append(tableEventTypePurpose['code'].notlike('0'))
                firstEvent, begDate, endDate = event
                if begDate or endDate:
                    cond.append(tableEvent['setDate'].isNotNull())
                    cond.append(tableEvent['deleted'].eq(0))
                if begDate:
                    cond.append(tableEvent['setDate'].dateGe(begDate))
                if endDate:
                    cond.append(tableEvent['setDate'].dateLe(endDate))
                if firstEvent and begDate:
                    cond.append(
                        '''NOT EXISTS(SELECT E.id FROM Event AS E WHERE E.client_id = Client.id AND Event.deleted = 0 AND DATE(E.setDate) < DATE(%s))''' % (
                            db.formatDate(begDate)))
            if 'age' in filter:
                lowAge, highAge = filter['age']
                cond.append(tableClient['birthDate'].le(calcBirthDate(*lowAge)))
                cond.append(tableClient['birthDate'].ge(calcBirthDate(*highAge)))
            if 'birthYear' in filter:
                lowYear, highYear = filter['birthYear']
                cond.append('YEAR(Client.birthDate) BETWEEN %d AND %d' % (lowYear, highYear))
            if 'birthMonth' in filter:
                cond.append('MONTH(Client.birthDate) = %d' % filter['birthMonth'])
            if 'sex' in filter:
                cond.append(tableClient['sex'].eq(filter['sex']))
            if 'SNILS' in filter:
                cond.append(tableClient['SNILS'].eq(filter['SNILS']))
            if 'IIN' in filter:
                cond.append(tableClient['IIN'].eq(filter['IIN']))
            if 'contact' in filter:
                tableContact = db.table('ClientContact')
                table = table.leftJoin(tableContact, tableContact['client_id'].eq(tableClient['id']))
                cond.append(tableContact['deleted'].eq(0)),
                cond.append(tableContact['contact'].like(contactToLikeMask(filter['contact'])))
            doc = filter.get('doc', None)
            if 'isUnconscious' in filter:
                if filter['isUnconscious']:
                    cond.append(tableClient['isUnconscious'].eq(filter['isUnconscious']))
            if 'oncologyForm90' in filter:
                if filter['oncologyForm90']:
                    cond.append('EXISTS(SELECT a.id'
                                '       FROM Event e'
                                '         INNER JOIN Action a ON e.id = a.event_id'
                                '         INNER JOIN ActionType at ON a.actionType_id = at.id AND at.flatCode = "f90"'
                                '       WHERE e.client_id = Client.id AND e.deleted = 0 AND a.deleted = 0)')
            if doc:
                tableDoc = db.table('ClientDocument')
                table = table.leftJoin(tableDoc,
                                       [tableDoc['client_id'].eq(tableClient['id']), tableDoc['deleted'].eq(0)]
                                       )
                typeId, serial, number = doc
                if typeId or serial or number:
                    if typeId:
                        cond.append(tableDoc['documentType_id'].eq(typeId))
                    if serial:
                        cond.append(tableDoc['serial'].eq(serial))
                    if number:
                        cond.append(tableDoc['number'].eq(number))
                else:
                    cond.append(cond.append(tableDoc['id'].isNull()))
            policy = filter.get('policy', None)
            if policy:
                tablePolicy = db.table('ClientPolicy')
                table = table.leftJoin(tablePolicy,
                                       [tablePolicy['client_id'].eq(tableClient['id']), tablePolicy['deleted'].eq(0)]
                                       )
                policyType, insurerId, serial, number = policy
                if policyType or insurerId or serial or number:
                    if policyType:
                        cond.append(tablePolicy['policyType_id'].eq(policyType))
                    if insurerId:
                        cond.append(tablePolicy['insurer_id'].eq(insurerId))
                    if serial:
                        cond.append(tablePolicy['serial'].eq(serial))
                    if number:
                        cond.append(tablePolicy['number'].eq(number))
                else:
                    cond.append(tablePolicy['id'].isNull())

            mkbTop = filter.get('MKBTop', '')
            mkbBottom = filter.get('MKBBottom', '')
            MKBCond = []
            if mkbTop: MKBCond.append('compareMKB(\'%s\', Diagnosis.MKB, 1)' % mkbTop)
            if mkbBottom: MKBCond.append('compareMKB(Diagnosis.MKB, \'%s\', 0)' % mkbBottom)
            if MKBCond:
                tableDiagnosis = db.table('Diagnosis')
                diagTypeId = filter.get('diagnosisTypeId', None)
                cond.append(db.joinAnd(MKBCond))
                if diagTypeId: cond.append(tableDiagnosis['diagnosisType_id'].eq(diagTypeId))

                table = table.innerJoin(tableDiagnosis, [tableDiagnosis['client_id'].eq(tableClient['id']),
                                                         tableDiagnosis['deleted'].eq(0)])

            orgId = filter.get('orgId', None)
            hurtType = filter.get('hurtType', None)
            isSeparateStaff = QtGui.qApp.isSeparateStaffFromPatient()
            isOnlyStaff = filter.get('onlyStaff', False)
            if orgId or isSeparateStaff or hurtType:
                tableWork = db.table('ClientWork')
                joinCond = [tableClient['id'].eq(tableWork['client_id']),
                            'ClientWork.id = (select max(CW.id) from ClientWork as CW where CW.client_id=Client.id)'
                            ]
                table = table.leftJoin(tableWork, joinCond)
            if orgId:
                cond.append(tableWork['org_id'].eq(orgId))

            if hurtType:
                tableWorkHurt = db.table('ClientWork_Hurt')
                tableHurtType = db.table('rbHurtType')
                table = table.join(tableWorkHurt, tableWorkHurt['master_id'].eq(tableWork['id']))
                table = table.join(tableHurtType, tableHurtType['id'].eq(tableWorkHurt['hurtType_id']))
                cond.append(tableHurtType['id'].eq(hurtType))

            socStatTypeId = filter.get('socStatType_id', None)
            socStatClassId = filter.get('socStatClass_id', None)
            if socStatTypeId or socStatClassId:
                tableSocStat = db.table('ClientSocStatus')
                table = table.join(tableSocStat, tableSocStat['client_id'].eq(tableClient['id']))
                cond.append(tableSocStat['deleted'].eq(0))
                cond.append(db.joinOr([tableSocStat['endDate'].isNull(),
                                       tableSocStat['endDate'].dateGe(QtCore.QDate.currentDate())]))
                cond.append(tableSocStat['begDate'].dateLe(QtCore.QDate.currentDate()))
                # При указанном типе соц.статуса поиск по классу соц.статуса излишен
                cond.append(tableSocStat['socStatusType_id'].eq(socStatTypeId) if socStatTypeId
                            else tableSocStat['socStatusClass_id'].eq(socStatClassId))

            locationCardType = filter.get('locationCardType', None)
            if locationCardType:
                cond.append(
                    '''EXISTS(SELECT Client_LocationCard.id FROM Client_LocationCard WHERE Client_LocationCard.deleted = 0 AND Client_LocationCard.master_id = Client.id AND Client_LocationCard.locationCardType_id = %s)''' % (
                        str(locationCardType)))
            statusObservationType = filter.get('statusObservationType', None)
            if statusObservationType:
                cond.append(
                    '''EXISTS(SELECT Client_StatusObservation.id FROM Client_StatusObservation WHERE Client_StatusObservation.deleted = 0 AND Client_StatusObservation.master_id = Client.id AND Client_StatusObservation.statusObservationType_id = %s)''' % (
                        str(statusObservationType)))
            address = filter.get('address', None)
            if address:
                addrType, KLADRCode, KLADRStreetCode, house, corpus, flat = address
                tableClientAddress = db.table('ClientAddress')
                tableAddressHouse = db.table('AddressHouse')
                tableAddress = db.table('Address')
                table = table.leftJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
                table = table.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
                table = table.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))

                cond.append(
                    'ClientAddress.id = (SELECT MAX(CA.id) FROM ClientAddress AS CA WHERE CA.deleted=0 AND CA.type=%d AND CA.client_id=Client.id)' % addrType)
                if KLADRCode:
                    regionCode = KLADRCode[2:]
                    if regionCode.ljust(len(KLADRCode), '0') == KLADRCode:  # Код является кодом региона
                        cond.append(tableAddressHouse['KLADRCode'].like('%s%%' % regionCode))
                    else:
                        cond.append(tableAddressHouse['KLADRCode'].eq(KLADRCode))
                if KLADRStreetCode:
                    cond.append(tableAddressHouse['KLADRStreetCode'].eq(KLADRStreetCode))
                if house:
                    cond.append(tableAddressHouse['number'].eq(house))
                    if corpus:
                        cond.append(tableAddressHouse['corpus'].eq(corpus))
                if flat:
                    cond.append(tableAddress['flat'].eq(flat))
            elif 'addressOrgStructure' in filter:
                addrType, orgStructureId = filter['addressOrgStructure']
                addrIdList = None
                cond2 = []
                if (addrType + 1) & 1:
                    addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 0, addrIdList)
                if (addrType + 1) & 2:
                    if addrIdList is None:
                        addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 1, addrIdList)
                if ((addrType + 1) & 4):
                    if orgStructureId:
                        addAttachCond(cond2, 'orgStructure_id=%d' % orgStructureId, 1, None)
                    else:
                        addAttachCond(cond2, 'LPU_id=%d' % QtGui.qApp.currentOrgId(), 1, None)
                if cond2:
                    cond.append(db.joinOr(cond2))
            elif 'addressIsEmpty' in filter:
                addAddressCond(cond, 0, None)
            if 'beds' in filter:
                indexFlatCode, orgStructureId = filter['beds']
                if orgStructureId:
                    bedsIdList = getOrgStructureDescendants(orgStructureId)
                else:
                    bedsIdList = getOrgStructures(QtGui.qApp.currentOrgId())
                if indexFlatCode == 2:
                    clientBedsIdList = self.getLeavedHospitalBeds(bedsIdList)
                else:
                    clientBedsIdList = self.getHospitalBeds(bedsIdList, indexFlatCode)
                cond.append(tableClient['id'].inlist(clientBedsIdList))
            if 'attachTo' in filter:
                attachOrgId = filter['attachTo']
                if attachOrgId:
                    addAttachCond(cond, 'LPU_id=%d' % attachOrgId, *filter.get('attachType', (0, None)))
                else:
                    addAttachCond(cond, 'not isNull(LPU_id)', *filter.get('attachType', (0, None)))
            elif 'attachToNonBase' in filter:
                addAttachCond(cond, 'LPU_id!=%d' % QtGui.qApp.currentOrgId(), *filter.get('attachType', (0, None)))
            elif 'attachType' in filter:
                addAttachCond(cond, '', *filter['attachType'])
            if 'tempInvalid' in filter:
                begDate, endDate = filter['tempInvalid']
                if begDate or endDate:
                    tableTempInvalid = db.table('TempInvalid')
                    table = table.leftJoin(tableTempInvalid, tableTempInvalid['client_id'].eq(tableClient['id']))
                    if begDate and begDate.isValid():
                        cond.append(tableTempInvalid['endDate'].ge(begDate))
                    if endDate and endDate.isValid():
                        cond.append(tableTempInvalid['begDate'].le(endDate))
            if self.RPFAccountingSystemId:
                if filter.get('RPFUnconfirmed', False):
                    tableClientIdentification = db.table('ClientIdentification')
                    condClientIdentification = [tableClientIdentification['client_id'].eq(tableClient['id']),
                                                tableClientIdentification['accountingSystem_id'].eq(
                                                    self.RPFAccountingSystemId),
                                                ]
                    cond.append('NOT ' + db.existsStmt(tableClientIdentification, condClientIdentification))
                    cond.append(tableClientIdentification['deleted'].eq(0))
                elif 'RPFConfirmed' in filter:  # atronah: РПФ - регистр периодов финансирования (согласно документаци ПО «ЕИС ОМС. ВМУ. АПУ. Учёт пациентов»)
                    begDate, endDate = filter['RPFConfirmed']
                    tableClientIdentification = db.table('ClientIdentification')
                    condClientIdentification = [tableClientIdentification['client_id'].eq(tableClient['id']),
                                                tableClientIdentification['accountingSystem_id'].eq(
                                                    self.RPFAccountingSystemId),
                                                ]
                    cond.append(tableClientIdentification['deleted'].eq(0))
                    if begDate and begDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].ge(begDate))
                    if endDate and endDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].le(endDate))
                    cond.append(db.existsStmt(tableClientIdentification, condClientIdentification))

            if 'contingentDD' in filter:  # Фильтр картотеки для контингента ДД
                contingentDD_Id = filter['contingentDD']

                ageSelectors = QtGui.qApp.getContingentDDAgeSelectors()
                eventTypeCodes = QtGui.qApp.getContingentDDEventTypeCodes()

                curDate = QtCore.QDate.currentDate()

                tableEvent = db.table('Event')
                tableEventType = db.table('EventType')
                tableClientAlias = tableClient.alias('C')

                subQueryTable = tableEvent.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
                subQueryTable = subQueryTable.leftJoin(tableClientAlias,
                                                       tableClientAlias['id'].eq(tableEvent['client_id']))
                subQueryCond = [
                    tableClientAlias['id'].eq(tableClient['id']),
                    tableEventType['code'].inlist(eventTypeCodes),
                    tableEvent['setDate'].yearEq(curDate),
                    tableEvent['deleted'].eq(0)
                ]

                if contingentDD_Id == 0:  # Подлежащие ДД
                    subjectToDDCond = []
                    for begAge, endAge, step, useCalendarYear, useExclusion in ageSelectors:
                        ages = range(begAge, endAge + 1, step if step else 1)
                        years = [curDate.year() - age for age in ages]
                        field = 'YEAR(Client.birthDate)' if useCalendarYear else 'age(Client.birthDate, curdate())'
                        subjectToDDCond.append(field + (' NOT' if useExclusion else '') + ' IN (' + ','.join(
                            '%d' % d for d in (years if useCalendarYear else ages)) + ')')

                    cond.append(db.joinOr(subjectToDDCond))  # подходящий возраст
                    cond.append('NOT ' + db.existsStmt(subQueryTable, subQueryCond))  # в этом году не проходил

                else:
                    dateLessCurDate = [tableEvent['execDate'].dateLt(curDate)]

                    passingDDCond = db.existsStmt(subQueryTable, subQueryCond)
                    passedDDCond = db.existsStmt(subQueryTable, subQueryCond + dateLessCurDate)

                    if contingentDD_Id == 1:  # Проходящие ДД
                        cond.append(passingDDCond)
                        cond.append('NOT ' + passedDDCond)

                    elif contingentDD_Id == 2:  # Прошедшие ДД
                        cond.append(passedDDCond)

            if 'clientExamPlanYear' in filter:
                examYear = filter['clientExamPlanYear']
                examQuarter = filter.get('clientExamPlanQuarter')
                examKind = filter.get('clientExamPlanKind')

                tableClientExamPlan = db.table('ClientExaminationPlan')
                clientExamPlanCond = [
                    tableClientExamPlan['client_id'].eq(tableClient['id']),
                    tableClientExamPlan['year'].eq(examYear),
                ]
                if examQuarter is not None:
                    clientExamPlanCond.append(tableClientExamPlan['month'].inlist(Quarter.months(examQuarter)))
                if examKind is not None:
                    clientExamPlanCond.append(tableClientExamPlan['kind'].eq(examKind))

                cond.append(db.existsStmt(tableClientExamPlan, clientExamPlanCond))

            hideLeaversPatients(cond)
            if filter and not filter.keys() == ['onlyStaff']:
                clientsLimit = 10000
            else:
                clientsLimit = 30
            getIdList = db.getDistinctIdList if table != tableClient else db.getIdList
            # Если включена глобальная опция сокрытия сотрудников из общего списка
            if isSeparateStaff:
                onlyStaffCond = db.joinAnd([tableWork['org_id'].isNotNull(),
                                            tableWork['org_id'].eq(QtGui.qApp.currentOrgId())])
                # Сформировать условие для списка, включающего только пациентов (без сотрудников)
                onlyPatientCond = 'NOT (%s)' % onlyStaffCond

                idListStaff = getIdList(table,
                                        tableClient['id'].name(),
                                        cond + [onlyStaffCond],
                                        [tableClient['lastName'].name(), tableClient['firstName'].name(),
                                         tableClient['patrName'].name(), tableClient['birthDate'].name(),
                                         tableClient['id'].name()],
                                        limit=clientsLimit)
                idListPatient = getIdList(table,
                                          tableClient['id'].name(),
                                          cond + [onlyPatientCond],
                                          [tableClient['lastName'].name(), tableClient['firstName'].name(),
                                           tableClient['patrName'].name(), tableClient['birthDate'].name(),
                                           tableClient['id'].name()],
                                          limit=clientsLimit)
                if len(idListPatient) < clientsLimit:
                    patientCount = len(idListPatient)
                else:
                    patientCount = db.getDistinctCount(table, tableClient['id'].name(), cond + [onlyPatientCond])
                if len(idListPatient) < clientsLimit:
                    staffCount = len(idListPatient)
                else:
                    staffCount = db.getDistinctCount(table, tableClient['id'].name(), cond + [onlyStaffCond])

                if isOnlyStaff:  # показывать только сотрудников
                    idList = idListStaff
                    clientCount = staffCount
                else:  # показывать только пациентов, не относящихся к текущему ЛПУ
                    idList = idListPatient
                    clientCount = patientCount
            else:  # Если отключено разделение на сотрудников и пациентов
                idList = getIdList(table,
                                   tableClient['id'].name(),
                                   cond,
                                   [tableClient['lastName'].name(), tableClient['firstName'].name(),
                                    tableClient['patrName'].name(), tableClient['birthDate'].name(),
                                    tableClient['id'].name()],
                                   limit=clientsLimit)
                if len(idList) < clientsLimit:
                    clientCount = len(idList)
                else:
                    getCount = db.getDistinctCount if table != tableClient else db.getCount
                    clientCount = getCount(table, tableClient['id'].name(), cond)

            self.registryWidget().viewWidget().setIdList(idList, posToId, clientCount)
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        self.focusClients()
        self.updateClientsListRequest = False

        if not idList:
            # если поиск по id, включено разделение на сотрудников и пациентов и список сотрудников не пуст
            if isSeparateStaff and 'id' in filter and idListStaff:
                # если у текущего пользователя есть права на просмотр списка сотрудников
                if QtGui.qApp.userHasRight(urSeeStaff):
                    self.chkShowStaffOnly.setCheckState(
                        QtCore.Qt.Checked)  # переключиться в режим отображения сотрудников
                    self.on_buttonBoxClient_apply()  # применить изменения режима
                else:
                    QtGui.QMessageBox.warning(self,
                                              u'Внимание',
                                              u'Искомый пациент является сотрудником и не доступен для просмотра.',
                                              QtGui.QMessageBox.Ok,
                                              QtGui.QMessageBox.Ok)

            else:
                res = QtGui.QMessageBox.warning(self,
                                                u'Внимание',
                                                u'Пациент не обнаружен%s.\nХотите зарегистрировать пациента?'
                                                % (
                                                    u' (возможно он является сотрудником)' if isSeparateStaff and not isOnlyStaff else u''),
                                                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                QtGui.QMessageBox.Ok)
                if res == QtGui.QMessageBox.Ok:
                    self.editNewClient()
                    self.focusClients()

    @SimpleThread
    def barCodeReaderThread(self):
        PORT = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderName', u"COM2"))
        self.omsPolisData = readOMSBarCode(PORT)

    def on_barCodeReaderThread_finished(self):
        self.readBarCode.setEnabled(True)
        if self.omsPolisData['errorMessage']:
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка чтения',
                self.omsPolisData['errorMessage'],
                QtGui.QMessageBox.Close)
        else:
            self.on_buttonBoxEvent_reset()
            self.chkFilterLastName.setChecked(True)
            self.edtFilterLastName.setText(self.omsPolisData['lastName'])
            self.edtFilterLastName.setEnabled(True)
            self.chkFilterFirstName.setChecked(True)
            self.edtFilterFirstName.setText(self.omsPolisData['firstName'])
            self.edtFilterFirstName.setEnabled(True)
            self.chkFilterPatrName.setChecked(True)
            self.edtFilterPatrName.setText(self.omsPolisData['patrName'])
            self.edtFilterPatrName.setEnabled(True)
            self.chkFilterSex.setChecked(True)
            self.cmbFilterSex.setCurrentIndex(self.omsPolisData['sex'])
            self.cmbFilterSex.setEnabled(True)
            self.chkFilterBirthDay.setChecked(True)
            self.edtFilterBirthDay.setDate(self.omsPolisData['bDate'])
            self.edtFilterBirthDay.setEnabled(True)

            self.chkFilterPolicy.setChecked(True)
            defaultKLADR = QtGui.qApp.defaultKLADR()
            if defaultKLADR.startswith('78') or defaultKLADR.startswith('47'):
                self.edtFilterPolicySerial.setText(u'ЕП')
                self.edtFilterPolicySerial.setEnabled(True)
            self.edtFilterPolicyNumber.setText(self.omsPolisData['number'])
            self.edtFilterPolicyNumber.setEnabled(True)

            self.cmbFilterPolicyType.setCode(u'1')
            self.cmbFilterPolicyType.setEnabled(True)

            if self.omsPolisData['endDate'] is not None:
                self.newUserOmsEnd = self.omsPolisData['endDate']
            else:
                self.newUserOmsEnd = None

            self.on_buttonBoxClient_apply()

    def on_actReadBarCode(self):
        thread = self.barCodeReaderThread(thr_method='b', thr_start=False)
        thread.finished.connect(self.on_barCodeReaderThread_finished)
        self.readBarCode.setEnabled(False)
        thread.start()

    def on_actReadUek(self):

        ############################################################
        # чтение УЭК через МИП сервис

        if self.extUekService:
            try:
                mipSrv = CMIPWinSrv(
                    forceString(getVal(QtGui.qApp.preferences.appPrefs, 'MIPUrl', 'http://127.0.0.1:2116/MIPWinSrv/')))
                mipSrv.ReadContext()
                contextSrv = CWSMCC(
                    forceString(getVal(QtGui.qApp.preferences.appPrefs, 'MIPContext', 'http://127.0.0.1:2116/WSMCC/')))
                contextSrv.ReadContext(mipSrv.Guid)

                if contextSrv.Code == u'Ok':
                    self.on_buttonBoxEvent_reset()
                    self.chkFilterLastName.setChecked(True)
                    self.edtFilterLastName.setText(contextSrv.lastName)
                    self.edtFilterLastName.setEnabled(True)
                    self.chkFilterFirstName.setChecked(True)
                    self.edtFilterFirstName.setText(contextSrv.firstName)
                    self.edtFilterFirstName.setEnabled(True)
                    self.chkFilterPatrName.setChecked(True)
                    self.edtFilterPatrName.setText(contextSrv.patrName)
                    self.edtFilterPatrName.setEnabled(True)
                    self.chkFilterSex.setChecked(True)
                    self.cmbFilterSex.setCurrentIndex(contextSrv.sex)
                    self.cmbFilterSex.setEnabled(True)
                    self.chkFilterBirthDay.setChecked(True)
                    self.edtFilterBirthDay.setDate(QtCore.QDate(contextSrv.bDate))
                    self.edtFilterBirthDay.setEnabled(True)
                    self.chkFilterSNILS.setChecked(True)
                    self.edtFilterSNILS.setText(contextSrv.snils)
                    self.edtFilterSNILS.setEnabled(True)

                    self.newUserLocation = None

                    self.chkFilterPolicy.setChecked(True)
                    self.edtFilterPolicySerial.setText(u'')
                    self.edtFilterPolicySerial.setEnabled(True)
                    self.edtFilterPolicyNumber.setText(contextSrv.oms)
                    self.edtFilterPolicyNumber.setEnabled(True)

                    self.cmbFilterPolicyType.setCode(u'1')
                    self.cmbFilterPolicyType.setEnabled(True)
                    self.cmbFilterPolicyInsurer._popup.on_buttonBox_reset()
                    self.cmbFilterPolicyInsurer._popup.edtOGRN.setText(contextSrv.omsOgrn)
                    self.cmbFilterPolicyInsurer._popup.edtOKATO.setText(contextSrv.omsOkato)
                    self.cmbFilterPolicyInsurer._popup.on_buttonBox_apply()
                    self.cmbFilterPolicyInsurer.setEnabled(True)
                    self.newUserOmsBeg = contextSrv.omsBegDate
                    self.newUserOmsEnd = contextSrv.omsEndDate
                    self.on_buttonBoxClient_apply()
                else:
                    QtGui.QMessageBox.critical(
                        self,
                        u'Ошибка чтения УЭК',
                        u'Невозможно прочтать данные с сервиса клинического контекста.\nУбедитесь что карта УЭК вставлена в карт-ридер.')
            except:
                QtGui.QMessageBox.critical(
                    self,
                    u'Ошибка чтения УЭК',
                    u'Невозможно прочтать данные с сервиса клинического контекста.\nУбедитесь что ПО серсвиса клинического контекста настроено корректно.')

        ############################################################
        # чтение УЭК напрямую
        if self.intUekService:
            uek = CUekRead()
            uek.open()
            if (True):  # (uek.lastErrorCode == eUECRetCode_NoErrors):
                askPin = CUekPin(QtGui.qApp.mainWindow)
                askPin.exec_()
                if askPin.result() == QtGui.QDialog.Accepted:
                    uek.read(str(askPin.pin.text()))
                    if (uek.lastErrorCode == eUECRetCode_NoErrors):
                        self.on_buttonBoxEvent_reset()
                        self.chkFilterLastName.setChecked(True)
                        self.edtFilterLastName.setText(uek.lastName)
                        self.edtFilterLastName.setEnabled(True)
                        self.chkFilterFirstName.setChecked(True)
                        self.edtFilterFirstName.setText(uek.firstName)
                        self.edtFilterFirstName.setEnabled(True)
                        self.chkFilterPatrName.setChecked(True)
                        self.edtFilterPatrName.setText(uek.patrName)
                        self.edtFilterPatrName.setEnabled(True)
                        self.chkFilterSex.setChecked(True)
                        self.cmbFilterSex.setCurrentIndex(uek.sex)
                        self.cmbFilterSex.setEnabled(True)
                        self.chkFilterBirthDay.setChecked(True)
                        self.edtFilterBirthDay.setDate(QtCore.QDate(uek.bDate))
                        self.edtFilterBirthDay.setEnabled(True)
                        self.chkFilterSNILS.setChecked(True)
                        self.edtFilterSNILS.setText(uek.snils)
                        self.edtFilterSNILS.setEnabled(True)

                        self.newUserLocation = uek.bLoc

                        self.chkFilterPolicy.setChecked(True)
                        self.edtFilterPolicySerial.setText(u'')
                        self.edtFilterPolicySerial.setEnabled(True)
                        self.edtFilterPolicyNumber.setText(uek.oms)
                        self.edtFilterPolicyNumber.setEnabled(True)

                        self.cmbFilterPolicyType.setCode(u'1')
                        self.cmbFilterPolicyType.setEnabled(True)
                        self.cmbFilterPolicyInsurer._popup.on_buttonBox_reset()
                        self.cmbFilterPolicyInsurer._popup.edtOGRN.setText(uek.omsOgrn)
                        self.cmbFilterPolicyInsurer._popup.edtOKATO.setText(uek.omsOkato)
                        self.cmbFilterPolicyInsurer._popup.on_buttonBox_apply()
                        self.cmbFilterPolicyInsurer.setEnabled(True)
                        self.newUserOmsBeg = uek.omsBegDate
                        self.newUserOmsEnd = uek.omsEndDate

                        uek.close()
                        self.on_buttonBoxClient_apply()
                    else:
                        QtGui.QMessageBox.critical(
                            self,
                            u'Ошибка чтения УЭК',
                            u'Невозможно прочтать данные с УЭК.\nВы ввели не правильный PIN код.')
            else:
                QtGui.QMessageBox.critical(
                    self,
                    u'Ошибка чтения УЭК',
                    u'Невозможно прочтать данные с УЭК.\nУбедитесь что карта УЭК вставлена в карт-ридер!')

            uek.close()

    def on_actScanBarcodeTabExpert(self):
        self.cmbFilterExpert.setCurrentIndex(2)
        chkWidgetList = [
            #                        self.chkFilterExpertDocType,
            self.chkFilterExpertSerial,
            #                        self.chkFilterExpertNumber,
            self.chkFilterExpertReason,
            self.chkFilterExpertBegDate,
            self.chkFilterExpertEndDate,
            self.chkFilterExpertOrgStruct,
            self.chkFilterExpertSpeciality,
            self.chkFilterExpertPerson,
            self.chkFilterExpertMKB,
            self.chkFilterExpertClosed,
            self.chkFilterExpertDuration,
            self.chkFilterExpertInsuranceOfficeMark,
            self.chkFilterExpertLinked,
            self.chkFilterExpertCreatePerson,
            self.chkFilterExpertCreateDate,
            self.chkFilterExpertModifyPerson,
            self.chkFilterExpertModifyDate,
        ]
        for chkWidget in chkWidgetList:
            self.manualWidgetCheck(chkWidget, False)
        self.manualWidgetCheck(self.chkFilterExpertNumber, True)

    def manualWidgetCheck(self, wgt, value):
        wgt.setChecked(value)
        wgt.emit(QtCore.SIGNAL('clicked(bool)'), value)

    def setUserRights(self):
        u"""Права доступа по вкладкам"""
        app = QtGui.qApp
        isAdmin = app.userHasRight(urAdmin)
        # чтение
        self.tabRegistry.setEnabled(isAdmin or app.userHasRight(urRegTabReadRegistry))
        self.tabEvents.setEnabled(isAdmin or app.userHasRight(urRegTabReadEvents))
        self.tabAmbCard.setEnabled(isAdmin or app.userHasRight(urRegTabReadAmbCard))
        self.tabActions.setEnabled(isAdmin or app.userHasRight(urRegTabReadActions))
        self.tabExpert.setEnabled(isAdmin or app.userHasRight(urRegTabReadExpert))
        self.tabAmbulance.setEnabled(isAdmin or app.userHasRight(urRegTabReadAmbulance))
        # Запись\изменение
        # Вкладка Картотека: кнопки Редактировать и Регистрация
        self.btnEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteRegistry))
        self.btnNew.setEnabled(isAdmin or app.userHasRight(urAddClient))
        self.btnNew.setVisible(app.userHasRight(urRegWithoutSearch))
        self.chkShowStaffOnly.setVisible(app.isSeparateStaffFromPatient() and app.userHasRight(urSeeStaff))
        self.chkShowStaffOnly.setCheckState(QtCore.Qt.Unchecked)
        # Вкладка Обращение: кнопки Редактировать и Новый
        #        self.btnEventEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))
        #        self.btnEventNew.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))
        # Вкладка Мед. Карта
        #   зарезервировано право urRegTabWriteAmbCard
        # Вкладка Обслуживание: кнопка Редактировать событие
        #        self.btnActionEventEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))
        # Вкладка Обслуживание: элемент контекстного меню
        #        self.actEditActionEvent.setEnabled(isAdmin or app.userHasRight(urRegTabWriteActions))
        # Вкладка Обслуживание: кнопка Редактировать
        #        self.btnActionEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteActions))
        # Вкладка КЭР
        #   зарезервировано право urRegTabWriteExpert
        #        self.btnExpertEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteExpert))
        # Вкладка  СМП
        #   зарезервировано право urRegTabWriteAmbulance
        # заполнение combobox-ов тип прикрепления
        self.setupCmbFilterAttachTypeCategory(0)
        # перенести в exec_
        self.updateRegistryContent()

    def setUserRights_ForEventTab(self):
        app = QtGui.qApp
        isAdmin = app.userHasRight(urAdmin)
        self.btnEventEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))
        self.btnEventNew.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))

    def setUserRights_ForActionsTab(self):
        app = QtGui.qApp
        isAdmin = app.userHasRight(urAdmin)
        self.btnActionEventEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteEvents))
        self.actEditActionEvent.setEnabled(isAdmin or app.userHasRight(urRegTabWriteActions))
        self.btnActionEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteActions))

    def setUserRights_ForExpertTab(self):
        app = QtGui.qApp
        isAdmin = app.userHasRight(urAdmin)
        self.btnExpertEdit.setEnabled(isAdmin or app.userHasRight(urRegTabWriteExpert))

    def setupCmbFilterAttachTypeCategory(self, category, filterDict=None):
        if not filterDict:
            filterDict = {1: 'temporary=0',
                          2: 'temporary',
                          3: 'outcome'}
        v = self.cmbFilterAttachType.value()
        self.cmbFilterAttachType.setFilter(filterDict.get(category, ''))
        if v:
            self.cmbFilterAttachType.setValue(v)

    def closeEvent(self, event):
        # self.barCodethread.barCodeReader.close = True
        self.saveDialogPreferences()
        QtGui.qApp.preferences.appPrefs['FilterAccountingSystem'] = toVariant(
            self.cmbFilterAccountingSystem.value())
        super(CRegistryWindow, self).closeEvent(event)
        QtGui.qApp.mainWindow.registry = None
        if forceBool(getVal(
                QtGui.qApp.preferences.appPrefs, 'SocCard_SupportEnabled', False)):
            self.cardReader.finalize()

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            numericKeys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                           QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, QtCore.Qt.Key_9]
            if key == QtCore.Qt.Key_Tab:
                index = self.tabMain.currentIndex()
                lastIndex = self.tabMain.count() - 1
                nextIndexFound = False
                nextIndex = index
                while not nextIndexFound:
                    if nextIndex == lastIndex:
                        nextIndex = 0
                    else:
                        nextIndex += 1
                    if self.tabMain.isTabEnabled(nextIndex) or nextIndex == index:
                        nextIndexFound = True
                self.tabMain.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.TabFocusReason)
            elif key in numericKeys:
                nextIndex = int(event.text()) - 1
                if nextIndex <= self.tabMain.count() and self.tabMain.isTabEnabled(nextIndex):
                    self.tabMain.setCurrentIndex(nextIndex)
                    self.setFocus(QtCore.Qt.OtherFocusReason)
            elif key == QtCore.Qt.Key_0:
                self.tabMain.setCurrentIndex(self.tabMain.count() - 1)
                self.setFocus(QtCore.Qt.OtherFocusReason)
            elif key == QtCore.Qt.Key_F:
                # self.setEnableForMainFields(False)
                self.on_buttonBoxClient_reset()
                self.fastFind = CFastFindClientWindow(self)
                self.fastFind.exec_()
                if self.fastFind.findFields:
                    self.chkFilterLastName.setChecked(True)
                    self.edtFilterLastName.setEnabled(True)
                    self.edtFilterLastName.setText(self.fastFind.findFields['lastName'])

                    if self.fastFind.findFields['firstName']:
                        self.chkFilterFirstName.setChecked(True)
                        self.edtFilterFirstName.setEnabled(True)
                        self.edtFilterFirstName.setText(self.fastFind.findFields['firstName'])

                    if self.fastFind.findFields['patrName']:
                        self.chkFilterPatrName.setChecked(True)
                        self.edtFilterPatrName.setEnabled(True)
                        self.edtFilterPatrName.setText(self.fastFind.findFields['patrName'])

                    if self.fastFind.findFields['birthDate']:
                        self.chkFilterBirthDay.setChecked(True)
                        self.edtFilterBirthDay.setEnabled(True)
                        self.edtFilterBirthDay.setDate(self.fastFind.findFields['birthDate'])
                    self.on_buttonBoxClient_apply()  # применить изменения режима

        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if key == QtCore.Qt.Key_Backtab:
                index = self.tabMain.currentIndex()
                lastIndex = self.tabMain.count() - 1
                nextIndexFound = False
                nextIndex = index
                while not nextIndexFound:
                    if nextIndex == 0:
                        nextIndex = lastIndex
                    else:
                        nextIndex -= 1
                    if self.tabMain.isTabEnabled(nextIndex) or nextIndex == index:
                        nextIndexFound = True
                self.tabMain.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.BacktabFocusReason)
        elif modifiers == QtCore.Qt.ShiftModifier:
            if key == QtCore.Qt.Key_F4:
                self.on_actAmbPrintOrder_triggered()
        elif key == QtCore.Qt.Key_F11:
            directIEMCImport(self.currentClientId())
            self.on_buttonBoxEvent_apply()
        elif key == QtCore.Qt.Key_Escape:
            if self.tabMain.currentIndex() == self.tabMain.indexOf(self.tabRegistry):
                self.on_buttonBoxClient_reset()
            elif self.tabMain.currentIndex() == self.tabMain.indexOf(self.tabEvents):
                self.on_buttonBoxEvent_reset()
            elif self.tabMain.currentIndex() == self.tabMain.indexOf(self.tabActions):
                self.on_buttonBoxAction_reset()
            elif self.tabMain.currentIndex() == self.tabMain.indexOf(self.tabExpert):
                self.on_buttonBoxExpert_reset()

    def syncSplitters(self, nextSplitter):
        if nextSplitter != self.controlSplitter:
            nextSplitter.setSizes(self.controlSplitter.sizes())
            self.controlSplitter = nextSplitter

    def focusClients(self):
        self.registryWidget().viewWidget().setFocus(QtCore.Qt.TabFocusReason)
        self.registryWidget().viewWidget().model().fillVIPClients()

    def focusEvents(self):
        self.tblEvents.setFocus(QtCore.Qt.TabFocusReason)

    def showAccountingDialog(self, eventId=None, actionId=None, visitId=None):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        dlg = CAccountingDialog(self)
        dlg.accessCountTotalSumWithFranchise = True
        dlg.setWatchingFields(eventId, actionId, visitId)
        QtGui.qApp.restoreOverrideCursor()
        dlg.exec_()

    def getLeavedHospitalBeds(self, orgStructureIdList):
        currentDate = QtCore.QDate.currentDate()
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        tableClient = db.table('Client')
        # Получение списка всех коек для указанных подразделений
        orgStructureBedsIdList = db.getDistinctIdList(tableOSHB, [tableOSHB['master_id']],
                                                      [tableOSHB['master_id'].inlist(orgStructureIdList)])
        clientIdList = []
        # Если список коек не пуст
        if orgStructureBedsIdList:
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableActionType['flatCode'].like('leaved%'),
                    tableAction['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableClient['deleted'].eq(0),
                    tableEvent['setDate'].le(currentDate),
                    tableAction['begDate'].le(currentDate),
                    tableAction['endDate'].isNull()
                    ]
            # Поиск всех событий типа "Выписка" начатых по сегодня включительно, но еще не законченных
            stmt = db.selectStmt(queryTable, [tableEvent['id'].alias('eventId'), tableAction['id'].alias('actionId')],
                                 cond)
            query = db.query(stmt)
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            # TODO: atronah: Есть подозрение, что вместо запроса по каждому результату другого запроса можно использовать один общий запрос.
            # TODO: atronah: И вообще все свести к getIdList
            while query.next():
                record = query.record()
                eventId = forceRef(record.value('eventId'))
                cond = [db.joinOr([tableActionType['flatCode'].like('moving%'),
                                   tableActionType['flatCode'].like('reanimation%')]),
                        tableAction['deleted'].eq(0),
                        tableEvent['deleted'].eq(0),
                        tableEvent['id'].eq(eventId),
                        tableAP['deleted'].eq(0),
                        tableActionType['deleted'].eq(0),
                        tableAPT['deleted'].eq(0),
                        tableOS['deleted'].eq(0),
                        tableClient['deleted'].eq(0),
                        tableEvent['setDate'].le(currentDate),
                        tableAction['begDate'].le(currentDate),
                        tableAPT['typeName'].like('HospitalBed'),
                        tableAP['action_id'].eq(tableAction['id'])
                        ]
                order = u'Action.begDate DESC'
                cols = [tableClient['id'],
                        u'%s AS boolOrgStructure' % tableOS['id'].inlist(orgStructureBedsIdList)]
                firstRecord = db.getRecordEx(queryTable, cols, cond, order)
                if firstRecord:
                    if forceBool(firstRecord.value('boolOrgStructure')):
                        clientIdList.append(forceInt(firstRecord.value('id')))
        return clientIdList

    def getHospitalBeds(self, orgStructureIdList, indexFlatCode=0):
        currentDate = QtCore.QDate.currentDate()
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        tableClient = db.table('Client')
        orgStructureBedsIdList = db.getDistinctIdList(tableOSHB, [tableOSHB['master_id']],
                                                      [tableOSHB['master_id'].inlist(orgStructureIdList)])
        if orgStructureBedsIdList:
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond = [tableClient['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAP['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableOS['deleted'].eq(0),
                    tableOS['id'].inlist(orgStructureBedsIdList),
                    tableEvent['setDate'].le(currentDate),
                    tableAction['begDate'].le(currentDate),
                    tableAPT['typeName'].like('HospitalBed'),
                    tableAP['action_id'].eq(tableAction['id'])
                    ]
            cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(currentDate)]))
            cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(currentDate)]))
            actionTypeCond = []
            if indexFlatCode != 3:  # если не "в очереди", то искать по движению и реанимации
                actionTypeCond.append(tableActionType['flatCode'].like('moving'))
                actionTypeCond.append(tableActionType['flatCode'].like('reanimation'))

            if indexFlatCode != 1:  # если не "на лечении", то искать по планированию
                actionTypeCond.append(tableActionType['flatCode'].like('planning'))

            cond.append(db.joinOr(actionTypeCond))
            return db.getDistinctIdList(queryTable, [tableClient['id']], cond)
        else:
            return None

    def getClientFilterAsText(self):
        filter = self.__filter
        resList = []
        convertFilterToTextItem(resList, filter, 'id', u'Код пациента', unicode)
        convertFilterToTextItem(resList, filter, 'lastName', u'Фамилия')
        convertFilterToTextItem(resList, filter, 'firstName', u'Имя')
        convertFilterToTextItem(resList, filter, 'patrName', u'Отчество')
        convertFilterToTextItem(resList, filter, 'birthDate', u'Дата рождения', forceString)
        convertFilterToTextItem(resList, filter, 'sex', u'Пол', formatSex)
        if QtGui.qApp.defaultKLADR().startswith('90'):
            convertFilterToTextItem(resList, filter, 'IIN', u'ИИН', forceString)
        else:
            convertFilterToTextItem(resList, filter, 'SNILS', u'СНИЛС', formatSNILS)
        convertFilterToTextItem(resList, filter, 'doc', u'документ', lambda doc: formatDocument(doc[0], doc[1], doc[2]))
        convertFilterToTextItem(resList, filter, 'policy', u'полис',
                                lambda policy: formatPolicy(policy[0], policy[1], policy[2]))
        convertFilterToTextItem(resList, filter, 'orgId', u'занятость', getOrganisationShortName)
        convertFilterToTextItem(resList, filter, 'addressIsEmpty', u'адрес', lambda dummy: u'пуст')
        return '\n'.join([item[0] + u': ' + item[1] for item in resList])

    def checkVipPerson(self, textBrowser, clientId):
        # if hasattr(self.registryWidget().viewWidget().model(), 'vipList'):
        if clientId in self.registryWidget().viewWidget().model().vipList:
            color = self.registryWidget().viewWidget().model().vipList[clientId]
            textBrowser.setStyleSheet("background-color: %s;" % color)
        else:
            textBrowser.setStyleSheet("")

    def showClientInfo(self, id):
        """
            показ информации о пациенте в панели наверху
        """
        if id:
            self.txtClientInfoBrowser.setHtml(getClientBanner(id))
        else:
            self.txtClientInfoBrowser.setText('')
        self.checkVipPerson(self.txtClientInfoBrowser, id)

        self.actEditClient.setEnabled(bool(id))
        self.actEditLocationCard.setEnabled(bool(id))
        self.actEditStatusObservationClient.setEnabled(bool(id))
        QtGui.qApp.setCurrentClientId(id)

    def setCurrentClientId(self, clientId):
        self.chkFilterId.setChecked(True)
        self.on_chkFilterId_clicked(True)
        self.edtFilterId.setText(forceString(clientId))
        self.cmbFilterAccountingSystem.setCode(None)
        self.on_buttonBoxClient_apply()

    def clientId(self, index):
        return self.registryWidget().viewWidget().itemId(index)

    def selectedClientId(self):
        return self.registryWidget().viewWidget().currentItemId()

    def currentClientId(self):
        return QtGui.qApp.currentClientId()

    def editClient(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry if clientId else urAddClient]):
            dialog = CClientEditDialog(self)
            Logger.logWindowAccess(windowName=type(self).__name__, login_id=Logger.loginId,
                                   notes=u'Открытие редактирования карточки клиента.')
            Logger.updateClient(self.currentClientId())
            if clientId:
                dialog.load(clientId)
            if dialog.exec_():
                clientId = dialog.itemId()
                self.updateRegistryContent(clientId)
        else:
            self.showNotAllowedErrorMessage()

    def editCurrentClient(self):
        clientId = self.currentClientId()
        self.editClient(clientId)

    def findClient(self, clientId, clientRecord=None):
        self.tabMain.setCurrentIndex(self.tabMain.indexOf(self.tabRegistry))
        if not clientRecord:
            db = QtGui.qApp.db
            cols = 'lastName, firstName, patrName, sex, birthDate, SNILS'
            if QtGui.qApp.defaultKLADR().startswith('90'):
                cols += ', INN'
            clientRecord = db.getRecord('Client', cols, clientId)
        if clientRecord:
            filter = {}
            filter['id'] = clientId
            filter['accountingSystemId'] = None
            filter['lastName'] = forceString(clientRecord.value('lastName'))
            filter['firstName'] = forceString(clientRecord.value('firstName'))
            filter['patrName'] = forceString(clientRecord.value('patrName'))
            filter['sex'] = forceInt(clientRecord.value('sex'))
            filter['birthDate'] = forceDate(clientRecord.value('birthDate'))
            if QtGui.qApp.defaultKLADR().startswith('90'):
                filter['IIN'] = forceString(clientRecord.value('INN'))
            else:
                filter['SNILS'] = forceString(clientRecord.value('SNILS'))
            self.__filter = self.updateFilterWidgets(filter)
            if not self.__filter:
                self.__filter = self.updateFilterWidgets({'id': clientId, 'accountingSystemId': None}, True)
            self.updateRegistryContent(clientId)
            self.tabMain.setTabEnabled(self.tabMain.indexOf(self.tabEvents), True)

    def getParamsDialogFilter(self):
        dialogInfo = {}
        if self.chkFilterLastName.isChecked():
            dialogInfo['lastName'] = forceString(self.edtFilterLastName.text())
        if self.chkFilterFirstName.isChecked():
            dialogInfo['firstName'] = forceString(self.edtFilterFirstName.text())
        if self.chkFilterPatrName.isChecked():
            dialogInfo['patrName'] = forceString(self.edtFilterPatrName.text())
        if self.chkFilterBirthDay.isChecked():
            dialogInfo['birthDate'] = forceDate(self.edtFilterBirthDay.date())
        if self.chkFilterSex.isChecked():
            dialogInfo['sex'] = self.cmbFilterSex.currentIndex()
        if self.chkFilterSNILS.isChecked():
            dialogInfo['SNILS'] = self.edtFilterSNILS.text()
        if self.chkFilterIIN.isChecked():
            dialogInfo['IIN'] = self.edtFilterIIN.text()
        if self.chkFilterDocument.isChecked():
            dialogInfo['docType'] = self.cmbFilterDocumentType.value()
            serial = self.edtFilterDocumentSerial.text()
            for c in '-=/_|':
                serial = serial.replace(c, ' ')
            serial = forceStringEx(serial).split()
            dialogInfo['serialLeft'] = serial[0] if len(serial) >= 1 else ''
            dialogInfo['serialRight'] = serial[1] if len(serial) >= 2 else ''
            dialogInfo['docNumber'] = self.edtFilterDocumentNumber.text()
        if self.chkFilterContact.isChecked():
            dialogInfo['contact'] = forceString(self.edtFilterContact.text())
        if self.chkFilterPolicy.isChecked():
            dialogInfo['polisSerial'] = forceString(self.edtFilterPolicySerial.text())
            dialogInfo['polisNumber'] = forceString(self.edtFilterPolicyNumber.text())
            dialogInfo['polisCompany'] = self.cmbFilterPolicyInsurer.value()
            dialogInfo['polisType'] = self.cmbFilterPolicyType.value()
            dialogInfo['polisTypeName'] = self.cmbFilterPolicyType.model().getName(
                self.cmbFilterPolicyType.currentIndex())
        if self.chkFilterAddress.isChecked():
            dialogInfo['addressType'] = self.cmbFilterAddressType.currentIndex()
            dialogInfo['regCity'] = self.cmbFilterAddressCity.code()
            dialogInfo['regStreet'] = self.cmbFilterAddressStreet.code()
            dialogInfo['regHouse'] = self.edtFilterAddressHouse.text()
            dialogInfo['regCorpus'] = self.edtFilterAddressCorpus.text()
            dialogInfo['regFlat'] = self.edtFilterAddressFlat.text()
        try:
            dialogInfo['polisBegDate'] = self.newUserOmsBeg
            dialogInfo['polisEndDate'] = self.newUserOmsEnd
            dialogInfo['regFreeInput'] = self.newUserLocation
        except:
            pass

        return dialogInfo

    def editNewClient(self):
        if QtGui.qApp.userHasAnyRight([urAdmin, urAddClient]):
            dialog = CClientEditDialog(self)
            dialogInfo = self.getParamsDialogFilter()
            if dialogInfo:
                dialog.setClientDialogInfo(dialogInfo)
            if dialog.exec_():
                clientId = dialog.itemId()
                clientRecord = dialog.getRecord()
                self.findClient(clientId, clientRecord)
        else:
            self.showNotAllowedErrorMessage()

    # Возвращает список виджетов, относящихся к указанному QCheckBox
    # @param chk: QCheckBox, ответственный за включение\выключение отдельного фильтра
    # @return: список (list) с сылками на виджеты, которые привязаны к указанному QCheckBox
    def findControlledByChk(self, chk):
        for s in self.chkListOnClientsPage:
            if s[0] == chk:
                return s[1]
        if self.isTabEventAlreadyLoad:
            for s in self.chkListOnEventsPage:
                if s[0] == chk:
                    return s[1]
        if self.isTabActionsAlreadyLoad:
            for s in self.chkListOnActionsPage:
                if s[0] == chk:
                    return s[1]
        if self.isTabExpertAlreadyLoad:
            for s in self.chkListOnExpertPage:
                if s[0] == chk:
                    return s[1]
        return None

    def activateFilterWdgets(self, alist):
        if alist:
            for s in alist:
                s.setEnabled(True)
                if isinstance(s, (QtGui.QLineEdit, CDateEdit)):
                    s.selectAll()
            alist[0].setFocus(QtCore.Qt.ShortcutFocusReason)
            alist[0].update()

    def deactivateFilterWdgets(self, alist):
        for s in alist:
            s.setEnabled(False)

    def updateFilterWidgets(self, filter, force=False):
        def intUpdateClientFilterLineEdit(chk, widget, inFilter, name, outFilter):
            val = inFilter.get(name, None)
            if val and (chk.isChecked() or force):
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setText(unicode(val))
                outFilter[name] = val

        def intUpdateClientFilterComboBox(chk, widget, inFilter, name, outFilter):
            if name in inFilter and (chk.isChecked() or force):
                val = inFilter[name]
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setCurrentIndex(val)
                outFilter[name] = val

        def intUpdateClientFilterRBComboBox(chk, widget, inFilter, name, outFilter):
            if name in inFilter and (chk.isChecked() or force):
                val = inFilter[name]
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setValue(val)
                outFilter[name] = val

        def intUpdateClientFilterDateEdit(chk, widget, inFilter, name, outFilter):
            val = inFilter.get(name, None)
            if val and (chk.isChecked() or force):
                chk.setChecked(True)
                self.activateFilterWdgets([widget])
                widget.setDate(val)
                outFilter[name] = val

        outFilter = {}
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk == self.chkFilterId:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'id', outFilter)
                intUpdateClientFilterRBComboBox(chk, s[1][1], filter, 'accountingSystemId', outFilter)
            elif chk == self.chkFilterLastName:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'lastName', outFilter)
            elif chk == self.chkFilterFirstName:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'firstName', outFilter)
            elif chk == self.chkFilterPatrName:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'patrName', outFilter)
            elif chk == self.chkFilterSex:
                intUpdateClientFilterComboBox(chk, s[1][0], filter, 'sex', outFilter)
            elif chk == self.chkFilterBirthDay:
                intUpdateClientFilterDateEdit(chk, s[1][0], filter, 'birthDate', outFilter)
            elif chk == self.chkFilterContact:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'contact', outFilter)
            elif chk == self.chkFilterSNILS:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'SNILS', outFilter)
            elif chk == self.chkFilterIIN:
                intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'IIN', outFilter)
            else:
                chk.setChecked(False)
                self.deactivateFilterWdgets(s[1])
        return outFilter

    def setChkFilterChecked(self, chk, checked):
        chk.setChecked(checked)
        self.onChkFilterClicked(chk, checked)

    def onChkFilterClicked(self, chk, checked):
        controlled = self.findControlledByChk(chk)
        if checked:
            self.activateFilterWdgets(controlled)
        else:
            self.deactivateFilterWdgets(controlled)

    def findEvent(self, eventId):
        self.tabMain.setCurrentIndex(self.tabMain.indexOf(self.tabEvents))
        if eventId in self.modelEvents.idList():
            self.tblEvents.setCurrentItemId(eventId)
        else:
            self.updateEventsList({}, eventId)

    def setEventList(self, eventIdList):
        self.tabMain.setCurrentIndex(self.tabMain.indexOf(self.tabEvents))
        self.tblEvents.setIdList(eventIdList)

    def requestNewEvent(self, isAmb=True, moveEventId=None, personId=None, begDate=None, endDate=None, externalId=None,
                        referralId=None, clientId=None):
        QtGui.qApp.setJTR(self)
        # TODO: skkachaev: Не освобождается память!
        if not clientId:
            clientId = self.currentClientId()
        dockFreeQueue = QtGui.qApp.mainWindow.dockFreeQueue
        if dockFreeQueue and dockFreeQueue.content and dockFreeQueue.content._appLockId:
            dockFreeQueue.content.on_actAmbCreateOrder_triggered()
        elif clientId:
            result = requestNewEvent(self, clientId, isAmb=isAmb, moveEventId=moveEventId,
                                     personId=personId, begDate=begDate, endDate=endDate, externalId=externalId,
                                     referralId=referralId)
            try:
                if not result:
                    self.delAllJobTicketReservations()
            except:
                QtGui.qApp.logCurrentException()
            self.onCurrentClientChanged()
            return result
        try:
            self.delAllJobTicketReservations()
        except:
            QtGui.qApp.logCurrentException()
        QtGui.qApp.setJTR(None)
        return None

    def setCmbFilterEventTypeFilter(self, eventPurposeId):
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbFilterEventType.setFilter(filter)
        self.lstFilterEventType.setFilter(filter)

    def addEqCond(self, cond, table, fieldName, filter, name):
        if name in filter:
            cond.append(table[fieldName].eq(filter[name]))

    def addLikeCond(self, cond, table, fieldName, filter, name):
        if name in filter:
            cond.append(table[fieldName].like(filter[name]))

    def addDateCond(self, cond, table, fieldName, filter, begDateName, endDateName):
        begDate = filter.get(begDateName, None)
        if begDate and not begDate.isNull():
            cond.append(table[fieldName].ge(begDate))
        endDate = filter.get(endDateName, None)
        if endDate and not endDate.isNull():
            cond.append(table[fieldName].lt(endDate.addDays(1)))

    def addDateTimeCond(self, cond, table, fieldName, filter, begDateName, endDateName, begExecTime, endExecTime):
        begDate = filter.get(begDateName, None)
        if begDate and not begDate.isNull():
            if begExecTime:
                cond.append(table[fieldName].ge(QtCore.QDateTime(begDate, begExecTime)))
            else:
                cond.append(table[fieldName].dateGe(begDate))
        endDate = filter.get(endDateName, None)
        if endDate and not endDate.isNull():
            if endExecTime:
                cond.append(table[fieldName].lt(QtCore.QDateTime(endDate.addDays(1), endExecTime)))
            else:
                cond.append(table[fieldName].dateLt(endDate.addDays(1)))

    def addRangeCond(self, cond, table, fieldName, filter, begName, endName):
        if begName in filter:
            cond.append(table[fieldName].ge(filter[begName]))
        if endName in filter:
            cond.append(table[fieldName].le(filter[endName]))

    def updateEventListAfterEdit(self, eventId):
        def clearAllColsCache(model):
            for x in model.cols():
                x.clearCache()

        if self.tabMain.currentIndex() == self.tabMain.indexOf(self.tabEvents):
            self.updateEventsList(self.__eventFilter, eventId)
        QtGui.qApp.emitCurrentClientInfoChanged()
        clearAllColsCache(self.tblEvents.model())

    def updateEventsList(self, filter, posToId=None):
        # в соответствии с фильтром обновляет список событий.
        self.__eventFilter = filter
        db = QtGui.qApp.db
        table = db.table('Event')
        tableEventType = db.table('EventType')
        tableVisit = db.table('Visit')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableRbEventGoal = db.table('rbEventGoal')
        queryTable = table
        cond = [table['deleted'].eq(0)]
        queryTable = queryTable.innerJoin(tableEventType, tableEventType['id'].eq(table['eventType_id']))
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')
        if 'clientIds' in filter:
            clientIds = filter['clientIds']
            cond.append(table['client_id'].inlist(clientIds))
        if 'externalId' in filter:
            if not filter['maskExternalId']:
                cond.append(table['externalId'].eq(filter['externalId']))
            else:
                cond.append(table['externalId'].regexp("^[^0-9]*" + filter['externalId'] + "[^0-9]*$"))
        if 'accountSumLimit' in filter:
            accountSumLimit = filter.get('accountSumLimit', 0)
            sumLimitFrom = filter.get('sumLimitFrom', 0)
            sumLimitTo = filter.get('sumLimitTo', 0)
            sumLimitDelta = filter.get('sumLimitDelta', 0)
            tableEventLocalContract = db.table('Event_LocalContract')
            queryTable = queryTable.innerJoin(tableEventLocalContract,
                                              tableEventLocalContract['master_id'].eq(table['id']))
            cond.append(tableEventLocalContract['deleted'].eq(0))
            cond.append(tableEventLocalContract['sumLimit'].gt(0))
            if sumLimitFrom or sumLimitTo and sumLimitFrom <= sumLimitTo:
                cond.append(tableEventLocalContract['sumLimit'].ge(sumLimitFrom))
                cond.append(tableEventLocalContract['sumLimit'].le(sumLimitTo))
            if accountSumLimit == 1:
                cond.append(table['totalCost'].gt(tableEventLocalContract['sumLimit']))
                if sumLimitDelta > 0:
                    cond.append(u'Event.totalCost >= (Event_LocalContract.sumLimit + %d)' % (sumLimitDelta))
            elif accountSumLimit == 2:
                cond.append(table['totalCost'].lt(tableEventLocalContract['sumLimit']))
                if sumLimitDelta > 0:
                    cond.append(u'Event.totalCost <= (Event_LocalContract.sumLimit + %d)' % (sumLimitDelta))
        self.addDateCond(cond, table, 'setDate', filter, 'begSetDate', 'endSetDate')
        if filter.get('emptyExecDate', False):
            cond.append(table['execDate'].isNull())
        self.addDateCond(cond, table, 'execDate', filter, 'begExecDate', 'endExecDate')
        self.addDateCond(cond, table, 'nextEventDate', filter, 'begNextDate', 'endNextDate')
        eventPurposeId = filter.get('eventPurposeId', None)
        if eventPurposeId:
            cond.append(table[
                            'eventType_id'].name() + ' IN (SELECT id FROM EventType WHERE EventType.purpose_id=%d)' % eventPurposeId)
        if 'eventTypeId' in filter:
            cond.append(table['eventType_id'].inlist(filter['eventTypeId']))
        elif not eventPurposeId:
            queryTable = getWorkEventTypeFilter(queryTable, cond)
        if 'personId' in filter:
            personId = filter['personId']
            if personId == -1:
                cond.append(table['execPerson_id'].isNull())
            else:
                cond.append(table['execPerson_id'].eq(personId))
        else:
            if 'specialityId' in filter or 'orgStructureId' in filter:
                tablePerson = db.table('Person')
                queryTable = queryTable.join(tablePerson, tablePerson['id'].eq(table['execPerson_id']))
            if 'specialityId' in filter:
                cond.append(tablePerson['speciality_id'].eq(filter['specialityId']))
            if 'orgStructureId' in filter:
                orgStructureId = filter.get('orgStructureId', None)
                if orgStructureId:
                    orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
                    if orgStructureIdList:
                        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        if 'relegateOrgId' in filter:
            cond.append(table['relegateOrg_id'].eq(filter['relegateOrgId']))
        if filter.get('dispanserObserved', False):
            condDispanserObserved = 'EXISTS (SELECT * FROM Diagnostic LEFT JOIN rbDispanser ON rbDispanser.id = Diagnostic.dispanser_id WHERE Diagnostic.event_id = Event.id AND rbDispanser.observed)'
            cond.append(condDispanserObserved)
        self.addEqCond(cond, table, 'org_id', filter, 'LPUId')
        if filter.get('nonBase', False):
            cond.append(table['org_id'].ne(QtGui.qApp.currentOrgId()))
        mesCode = filter.get('mesCode', None)
        if mesCode is not None:
            if mesCode:
                condMes = 'MES_id IN (SELECT id FROM mes.MES WHERE code LIKE %s)' % quote(
                    database.undotLikeMask(mesCode))
                cond.append(condMes)
            else:
                cond.append(table['eventType_id'].name() + ' IN (SELECT id FROM EventType WHERE EventType.mesRequired)')
                cond.append(table['MES_id'].isNull())

        self.addEqCond(cond, table, 'result_id', filter, 'eventResultId')
        if filter.get('errorInDiagnostic', False):
            condErrInFinish = '(SELECT COUNT(*) FROM Diagnostic WHERE Diagnostic.event_id = Event.id AND diagnosisType_id=(SELECT id FROM rbDiagnosisType WHERE code=\'1\')) != 1'
            condErrInGroup = 'EXISTS (SELECT * FROM Diagnostic WHERE Diagnostic.event_id = Event.id AND healthGroup_id IS NULL)'
            cond.append(db.joinOr([condErrInFinish, condErrInGroup]))

        mkbTop = filter.get('MKBTop', '')
        mkbBottom = filter.get('MKBBottom', '')
        MKBCond = []
        if mkbTop:
            MKBCond.append('compareMKB(\'%s\', Diagnosis.MKB, 1)' % mkbTop)
        if mkbBottom:
            MKBCond.append('compareMKB(Diagnosis.MKB, \'%s\', 0)' % mkbBottom)
        if MKBCond:
            diagTypeId = filter.get('diagnosisTypeId', None)
            queryTable = queryTable.innerJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(table['id']),
                                                                tableDiagnostic['deleted'].eq(0)])
            queryTable = queryTable.innerJoin(tableDiagnosis, [tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']),
                                                               tableDiagnosis['deleted'].eq(0)])
            cond.append(db.joinAnd(MKBCond))
            if diagTypeId:
                cond.append(tableDiagnostic['diagnosisType_id'].eq(diagTypeId))
        payStatusFinanceCode = filter.get('payStatusFinanceCode', None)
        if payStatusFinanceCode:
            payStatusCode = filter.get('payStatusCode', 0)
            cond.append(self.getPayStatusCond(payStatusCode, refFieldName='event_id', refFieldValue=table['id'].name()))
        if self.chkPrimary.isChecked():
            visitFilter = filter.get('visits', 0) + 1
            if visitFilter != 0:
                cond.append('(%s = %d)' % (table['isPrimary'], visitFilter))
        if self.chkFilterVisits.isChecked():
            queryTable = queryTable.innerJoin(tableVisit, tableVisit['event_id'].eq(table['id']))
            cond.append(tableVisit['deleted'].eq(0))
            if 'visitScene' in filter:
                visitScene = filter.get('visitScene', None)
                if visitScene:
                    cond.append(tableVisit['scene_id'].eq(visitScene))
            if 'visitType' in filter:
                visitType = filter.get('visitType', None)
                if visitType:
                    cond.append(tableVisit['visitType_id'].eq(visitType))
            if 'visitProfile' in filter:
                visitProfile = filter.get('visitProfile', None)
                if visitProfile:
                    cond.append(tableVisit['service_id'].eq(visitProfile))
            if 'visitPersonId' in filter:
                visitPersonId = filter.get('visitPersonId', None)
                if visitPersonId:
                    cond.append(tableVisit['person_id'].eq(visitPersonId))

        if self.chkFilterVisitPayStatus.isChecked():
            if not self.chkFilterVisits.isChecked():
                queryTable = queryTable.innerJoin(tableVisit, tableVisit['event_id'].eq(table['id']))
                cond.append(tableVisit['deleted'].eq(0))
            payStatusFinanceCodeVisit = filter.get('payStatusFinanceCodeVisit', None)
            if payStatusFinanceCodeVisit:
                payStatusCodeVisit = filter.get('payStatusCodeVisit', 0)
                mask = getPayStatusMaskByCode(payStatusFinanceCodeVisit)
                value = getPayStatusValueByCode(payStatusCodeVisit, payStatusFinanceCodeVisit)
                cond.append('((%s & %d) = %d)' % (tableVisit['payStatus'].name(), mask, value))
        if 'exposeConfirmed' in filter:
            exposeConfirmed = filter.get('exposeConfirmed')
            if exposeConfirmed == 0:
                cond.append(table['exposeConfirmed'].eq(0))
            if exposeConfirmed == 1:
                cond.append(table['exposeConfirmed'].eq(1))
        if 'goalRegionalCode' in filter:
            goalCode = filter.get('goalRegionalCode')
            queryTable = queryTable.innerJoin(tableRbEventGoal, table['goal_id'].eq(tableRbEventGoal['id']))
            cond.append(tableRbEventGoal['regionalCode'].eq(goalCode))
        if self.chkFilterMesEvents.isChecked():
            from Events.StandartsPage import CFindMesEventsInfo
            events = CFindMesEventsInfo()
            events.getEvents()
            if self.cmbFilterMesEvents.currentIndex() == 0:
                doneEvents = events.getDoneEvents()
                if doneEvents:
                    cond.append(table['id'].inlist(doneEvents))
            elif self.cmbFilterMesEvents.currentIndex() == 1:
                inProgressEvents = events.getInProgessEvents()
                if inProgressEvents:
                    cond.append(table['id'].inlist(inProgressEvents))
        if 'LID' in filter:
            LID = decorateString(filter['LID'])
            cond.append(u'''EXISTS(SELECT *
                                   FROM Action a
                                     INNER JOIN TakenTissueJournal ttj ON ttj.id = a.takenTissueJournal_id
                                   WHERE a.event_id = Event.id AND ttj.externalId LIKE {})'''.format(LID))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            idList = db.getDistinctIdList(queryTable,
                                          table['id'].name(),
                                          cond,
                                          ['Event.setDate DESC', 'Event.id'])
            self.tblEvents.setIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        hideClientInfo = 'clientIds' in filter and len(filter['clientIds']) == 1
        for i in xrange(4):
            self.tblEvents.setColumnHidden(i, hideClientInfo)

    def getEventFilterAsText(self):
        db = QtGui.qApp.db
        filter = self.__eventFilter
        resList = []

        clientIds = filter.get('clientIds', None)
        if clientIds and len(clientIds) == 1:
            resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
        elif clientIds is None:
            resList.append((u'список пациентов', u'полный'))
        else:
            resList.append((u'список пациентов', u'из вкладки'))

        tmpList = [
            ('begSetDate', u'Дата назначения с', forceString),
            ('endSetDate', u'Дата назначения по', forceString),
            ('emptyExecDate', u'Пустая дата выполнения', lambda dummy: ''),
            ('begExecDate', u'Дата выполнения с', forceString),
            ('endExecDate', u'Дата выполнения по', forceString),
            ('begNextDate', u'Дата следующей явки с', forceString),
            ('endNextDate', u'Дата следующей явки по', forceString),
            ('eventTypeId', u'Тип обращения',
             lambda idList: u', '.join([getEventName(id) for id in idList])),
            ('specialityId', u'Специальность',
             lambda id: forceString(db.translate('rbSpeciality', 'id', id, 'name'))),
            ('personId', u'Выполнил',
             lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('dispanserObserved', u'Дисп.наблюдение', lambda dummy: ''),
            ('LPUId', u'ЛПУ', getOrganisationShortName),
            ('nonBase', u'Не базовое ЛПУ', lambda dummy: ''),
            ('eventResultId', u'Результат обращения',
             lambda id: forceString(db.translate('rbResult', 'id', id, 'name'))),
            ('errorInDiagnostic', u'Ошибки', lambda dummy: ''),
            ('mkbBottom', u'Диагноз с', forceString),
            ('mkbTop', u'Диагноз по', forceString),
            ('diagnosisTypeId', u'Тип диагноза',
             lambda id: forceString(db.translate('rbDiagnosisType', 'id', id, 'name'))),
        ]
        for (key, title, ftm) in tmpList:
            convertFilterToTextItem(resList, filter, key, title, ftm)
        return '\n'.join([': '.join(item) for item in resList])

    def eventId(self, index):
        return self.tblEvents.itemId(index)

    def currentEventId(self):
        return self.tblEvents.currentItemId()

    def updateEventInfo(self, eventId):
        db = QtGui.qApp.db
        record = db.getRecord('Event',
                              ['createDatetime', 'createPerson_id', 'modifyDatetime', 'modifyPerson_id', 'eventType_id',
                               'externalId', 'client_id', 'payStatus', 'note', 'outgoingRefNumber'], eventId)
        if record:
            createDatetime = dateTimeToString(record.value('createDatetime').toDateTime())
            createPersonId = forceRef(record.value('createPerson_id'))
            modifyDatetime = dateTimeToString(record.value('modifyDatetime').toDateTime())
            modifyPersonId = forceRef(record.value('modifyPerson_id'))
            eventTypeId = forceRef(record.value('eventType_id'))
            externalId = forceString(record.value('externalId'))
            clientId = forceRef(record.value('client_id'))
            note = forceString(record.value('note'))
            payStatus = forceInt(record.value('payStatus'))
            outgoingRefNumber = forceString(db.translate('Event_OutgoingReferral', 'master_id', eventId, 'number'))
        else:
            createDatetime = ''
            createPersonId = None
            modifyDatetime = ''
            modifyPersonId = None
            externalId = ''
            clientId = None
            note = ''
            payStatus = 0
            outgoingRefNumber = ''

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserEvents.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserEvents.setText('')
        self.checkVipPerson(self.txtClientInfoBrowserEvents, clientId)

        self.actEventEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

        if eventId:
            table = db.table('Diagnostic')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId), table['deleted'].eq(0)], ['id'])
            self.tblEventDiagnostics.setIdList(idList)

            table = db.table('Action')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId), table['deleted'].eq(0)], ['id'])
            self.tblEventActions.setIdList(idList)
            self.tblEventAccActions.setIdList(idList, eventId=eventId)
            if self.tblEventAccActions.model().isChangeItems:
                self.tblEventAccActions.setIdList(idList, eventId=eventId)

            table = db.table('Visit')
            idList = db.getIdList(table, 'id', [table['event_id'].eq(eventId), table['deleted'].eq(0)], ['id'])
            self.tblEventVisits.setIdList(idList)

            context = getEventContext(eventTypeId)
            additionalCustomizePrintButton(self, self.btnEventPrint, context,
                                           [{'action': self.actEventPrint, 'slot': self.on_actEventPrint_triggered}, ])
            self.modelEventPayments.loadItems(eventId)
            paymentsSum = self.modelEventAccActions.getPaymentSum()
            accSum = self.modelEventAccActions.sum()
        else:
            self.tblEventDiagnostics.setIdList([])
            self.tblEventActions.setIdList([])
            self.tblEventAccActions.setIdList([])
            self.tblEventVisits.setIdList([])
            self.modelEventPayments.loadItems(None)
            paymentsSum = 0.0
            accSum = 0.0

        self.lblPaymentAccValue.setText('%.2f' % accSum)
        self.lblPaymentPayedSumValue.setText('%.2f' % paymentsSum)
        self.lblPaymentTotalValue.setText('%.2f' % (accSum - paymentsSum))
        palette = QtGui.QPalette()
        if accSum > paymentsSum:
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 0, 0))
        self.lblPaymentTotalValue.setPalette(palette)
        self.lblEventIdValue.setText(str(eventId) if eventId else '')
        self.lblEventExternalIdValue.setText(externalId)
        self.lblEventCreateDateTimeValue.setText(createDatetime)
        self.lblEventCreatePersonValue.setText(self.getPersonText(createPersonId))
        self.lblEventModifyDateTimeValue.setText(modifyDatetime)
        self.lblEventModifyPersonValue.setText(self.getPersonText(modifyPersonId))
        self.lblEventOutgoingRefNumberValue.setText(outgoingRefNumber)
        self.lblEventNoteValue.setText(note)
        self.lblEventPayStatusValue.setText(payStatusText(payStatus))

    def getPersonText(self, personId):
        if personId:
            index = self.personInfo.searchId(personId)
            if index > 0:
                return self.personInfo.getCode(index) + ' | ' + self.personInfo.getName(index)
            else:
                return '{' + str(personId) + '}'
        else:
            return ''

    def updateFilterEventResultTable(self):
        if self.chkFilterEventPurpose.isChecked():
            purposeIdList = [self.cmbFilterEventPurpose.value()]
        else:
            purposeIdList = []
        if not purposeIdList:
            if self.chkFilterEventType.isChecked():
                eventTypeIdList = self.lstFilterEventType.values() if self.chkFilterEventTypeMulti.isChecked() else [
                    self.cmbFilterEventType.value()] if self.cmbFilterEventType.value() else []
            else:
                eventTypeIdList = []
            if eventTypeIdList:
                purposeIdList = []
                for eventTypeId in eventTypeIdList:
                    purposeIdList.append(getEventPurposeId(eventTypeId))
                purposeIdList = list(set(purposeIdList))
        fltr = ''
        if filter(lambda x: x != 0, purposeIdList):
            purposeIdString = []
            for purposeId in purposeIdList:
                if purposeId:
                    purposeIdString.append("'%d'" % purposeId)
            purposeIdString = ', '.join(purposeIdString)
            if purposeIdString:
                fltr = ('eventPurpose_id in (%s)' % purposeIdString)
        self.cmbFilterEventResult.setTable('rbResult', False, fltr)

    def updateAmbCardInfo(self):
        clientId = self.currentClientId()
        if clientId:
            self.txtClientInfoBrowserAmbCard.setHtml(getClientBanner(clientId))
            self.tabAmbCardContent.setClientId(clientId)
        else:
            self.txtClientInfoBrowserAmbCard.setText('')
        self.checkVipPerson(self.txtClientInfoBrowserAmbCard, clientId)
        self.actAmbCardEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

    def editAction(self, actionId):
        dialog = CActionEditDialog(self)
        dialog.load(actionId)
        if dialog.exec_():
            self.updateActionsList(self.__actionFilter, dialog.itemId())
            QtGui.qApp.emitCurrentClientInfoChanged()
            return dialog.itemId()
        else:
            self.updateActionInfo(actionId)
            self.updateClientsListRequest = True
        return None

    @staticmethod
    def getPayStatusCond(payStatusCode, refFieldName='event_id', refFieldValue='Event.id'):
        existsTemplate = u'''EXISTS( SELECT AI.id
                                        FROM Account_Item AS AI
                                        WHERE AI.deleted = 0 AND AI.%(refFieldName)s = %(refFieldValue)s AND %(payStatusCond)s)'''
        payStatusCond = None
        if payStatusCode == CPayStatus.exposed:
            payStatusCond = u"(AI.refuseType_id IS NULL AND (AI.date IS NULL AND AI.number like ''))"
        elif payStatusCode == CPayStatus.payed:
            payStatusCond = u"(AI.refuseType_id IS NULL AND NOT (AI.date IS NULL AND AI.number LIKE ''))"
        elif payStatusCode == CPayStatus.refused:
            payStatusCond = u"(AI.refuseType_id IS NOT NULL)"
        elif payStatusCode == CPayStatus.initial:
            existsTemplate = 'NOT ' + existsTemplate
            payStatusCond = u'1'

        return existsTemplate % {'payStatusCond': payStatusCond,
                                 'refFieldName': refFieldName,
                                 'refFieldValue': refFieldValue} if payStatusCond else u'1'

    def updateActionsList(self, filter, posToId=None):
        u"""в соответствии с фильтром обновляет список действий (мероприятий)"""
        self.__actionFilter = filter
        optionPropertyIdList = []
        db = QtGui.qApp.db
        table = db.table('Action')
        tableEvent = db.table('Event')
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyType = db.table('ActionPropertyType')
        queryTable = table.leftJoin(tableEvent, tableEvent['id'].eq(table['event_id']))
        cond = [table['deleted'].eq(0), tableEvent['deleted'].eq(0)]
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')
        if 'clientIds' in filter:
            clientIds = filter.get('clientIds')
            cond.append(tableEvent['client_id'].inlist(clientIds))
        if 'eventIds' in filter:
            eventIds = filter.get('eventIds')
            cond.append(table['event_id'].inlist(eventIds))
        if 'isUrgent' in filter:
            cond.append(table['isUrgent'].ne(0))
        self.addDateCond(cond, table, 'directionDate', filter, 'begSetDate', 'endSetDate')
        self.addDateCond(cond, table, 'plannedEndDate', filter, 'begPlannedEndDate', 'endPlannedEndDate')
        begExecTime = filter.get('begExecTime', None)
        endExecTime = filter.get('endExecTime', None)
        if not begExecTime and not endExecTime:
            self.addDateCond(cond, table, 'endDate', filter, 'begExecDate', 'endExecDate')
        else:
            self.addDateTimeCond(cond, table, 'endDate', filter, 'begExecDate', 'endExecDate', begExecTime, endExecTime)
        actionClass = self.tabWidgetActionsClasses.currentIndex()
        if 'actionTypeId' in filter:
            actionTypeIdList = getActionTypeDescendants(filter['actionTypeId'], actionClass)
            cond.append(table['actionType_id'].inlist(actionTypeIdList))
        else:
            cond.append(table[
                            'actionType_id'].name() + ' IN (SELECT ActionType.id FROM ActionType WHERE ActionType.class=%d)' % actionClass)
        # сделано без учета значений value в таблицах ActionProperty_Double, ActionProperty_Action и т.п.,
        # учитывается наличие записи в ActionProperty, т.к. считается, что при не заполнении не создается запись в ActionProperty.
        if self.chkTakeIntoAccountProperty.isChecked():
            if self.chkListProperty.isChecked() and not self.chkThresholdPenaltyGrade.isChecked():
                if not ('booleanFilledProperty' in filter):
                    queryTable = queryTable.leftJoin(tableActionPropertyType,
                                                     tableActionPropertyType['actionType_id'].eq(
                                                         table['actionType_id']))
                optionPropertyIdList = self.getDataOptionPropertyChecked()
                if optionPropertyIdList != []:
                    cond.append(tableActionPropertyType['id'].inlist(optionPropertyIdList))
            if 'booleanFilledProperty' in filter:
                if filter.get('booleanFilledProperty') == True:
                    queryTable = queryTable.leftJoin(tableActionProperty,
                                                     tableActionProperty['action_id'].eq(table['id']))
                    queryTable = queryTable.leftJoin(tableActionPropertyType,
                                                     tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
                    cond.append(tableActionProperty['deleted'].eq(0))
                elif not self.chkThresholdPenaltyGrade.isChecked():
                    queryTable = queryTable.leftJoin(tableActionPropertyType,
                                                     tableActionPropertyType['actionType_id'].eq(
                                                         table['actionType_id']))
                    cond.append(
                        u'Action.id NOT IN (SELECT DISTINCT AP.action_id FROM ActionProperty AS AP WHERE AP.deleted = 0)')
            if self.chkThresholdPenaltyGrade.isChecked() and ('thresholdPenaltyGrade' in filter):
                filterPenaltyGrade = filter.get('thresholdPenaltyGrade')
                if filterPenaltyGrade:
                    whereOptionPropertyId = u''
                    if self.chkListProperty.isChecked():
                        optionPropertyIdList = self.getDataOptionPropertyChecked()
                        if optionPropertyIdList != []:
                            strPropertyIdList = u''
                            col = len(optionPropertyIdList) - 1
                            for propertyId in optionPropertyIdList:
                                strPropertyIdList += forceString(propertyId)
                                col -= 1
                                if col > 0:
                                    strPropertyIdList += u', '
                            whereOptionPropertyId = u'(APT.id IN (%s)) AND ' % (strPropertyIdList)
                    cond.append(
                        u'SELECT SUM(APT.penalty) >= %s FROM ActionPropertyType AS APT WHERE %s(APT.id NOT IN (SELECT AP.type_id FROM ActionProperty AS AP WHERE AP.action_id = Action.id AND AP.deleted = 0 GROUP BY AP.type_id) AND (APT.actionType_id = Action.actionType_id))' % (
                            filterPenaltyGrade, whereOptionPropertyId))
        if 'setPersonId' in filter:
            cond.append(table['setPerson_id'].eq(filter['setPersonId']))
        elif 'setSpecialityId' in filter:
            tablePerson = db.table('Person')
            queryTable = queryTable.join(tablePerson, tablePerson['id'].eq(table['setPerson_id']))
            cond.append(tablePerson['speciality_id'].eq(filter['setSpecialityId']))
        if 'execPersonId' in filter:
            execPersonId = filter['execPersonId']
            if execPersonId == -1:
                cond.append(table['person_id'].isNull())
            else:
                cond.append(table['person_id'].eq(execPersonId))
        if 'assistantId' in filter:
            assistantId = filter['assistantId']
            if assistantId == -1:
                cond.append(u"NOT EXISTS(SELECT A_A.id "
                            u"       FROM Action_Assistant AS A_A"
                            u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                            u"       WHERE A_A.action_id = %s "
                            u"              AND rbAAT.code like 'assistant')" % table['id'].name())
            else:
                cond.append(u"EXISTS(SELECT A_A.id "
                            u"       FROM Action_Assistant AS A_A"
                            u"       INNER JOIN rbActionAssistantType AS rbAAT ON rbAAT.id = A_A.assistantType_id"
                            u"       WHERE A_A.action_id = %s "
                            u"              AND rbAAT.code like 'assistant'"
                            u"              AND A_A.person_id = %s)" % (table['id'].name(),
                                                                        assistantId))
        elif 'execSpecialityId' in filter:
            tablePersonExec = db.table('Person').alias('PersonExec')
            queryTable = queryTable.join(tablePersonExec, tablePersonExec['id'].eq(table['person_id']))
            cond.append(tablePersonExec['speciality_id'].eq(filter['execSpecialityId']))
        self.addEqCond(cond, table, 'status', filter, 'status')

        payStatusFinanceCode = filter.get('payStatusFinanceCode', None)
        if payStatusFinanceCode:
            payStatusCode = filter.get('payStatusCode', 0)
            cond.append(
                self.getPayStatusCond(payStatusCode, refFieldName='action_id', refFieldValue=table['id'].name()))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            idList = db.getDistinctIdList(queryTable,
                                          table['id'].name(),
                                          cond,
                                          ['execDate DESC', 'id'])
            self.setActionsIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        actionsFilterType = filter['actionsFilterType']
        if actionsFilterType in [0, 2]:
            hideClientInfo = True
        elif actionsFilterType == 1:
            hideClientInfo = len(filter['clientIds']) == 1
        elif actionsFilterType == 3:
            hideClientInfo = len(filter['eventIds']) == 1 or \
                             len(self.__eventFilter.get('clientIds', [])) == 1
        else:
            hideClientInfo = False
        table = self.getCurrentActionsTable()
        table.setClientInfoHidden(hideClientInfo)

    def getActionFilterAsText(self):
        db = QtGui.qApp.db
        filter = self.__actionFilter
        resList = []

        actionsFilterType = filter['actionsFilterType']
        if actionsFilterType in [0, 1]:
            clientIds = filter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'список пациентов', u'из вкладки'))
        elif actionsFilterType in [2, 3]:
            clientIds = self.__eventFilter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'список пациентов', u'по списку осмотров'))
        else:
            resList.append((u'список пациентов', u'полный'))

        tmpList = [
            ('begSetDate', u'Дата назначения с', forceString),
            ('endSetDate', u'Дата назначения по', forceString),
            ('actionTypeId', u'Тип мероприятия',
             lambda id: forceString(db.translate('ActionType', 'id', id, 'name'))),
            ('setSpecialityId', u'Специальность назначившего',
             lambda id: forceString(db.translate('rbSpeciality', 'id', id, 'name'))),
            ('personId', u'Назначил',
             lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('isUrgent', u'Срочно', lambda dummy: u'+'),
            ('begPlannedEndDate', u'Плановая дата выполнения с', forceString),
            ('endPlannedEndDate', u'Плановая дата окончания по', forceString),
            ('begExecDate', u'Дата выполнения с', forceString),
            ('endExecDate', u'Дата выполнения по', forceString),
        ]
        for (x, y, z) in tmpList:
            convertFilterToTextItem(resList, filter, x, y, z)
        return '\n'.join([': '.join(item) for item in resList])

    def getCurrentActionsTable(self):
        index = self.tabWidgetActionsClasses.currentIndex()
        return [self.tblActionsStatus,
                self.tblActionsDiagnostic,
                self.tblActionsCure,
                self.tblActionsMisc,
                self.tblActionsAnalyses][index]

    def currentActionId(self):
        return self.getCurrentActionsTable().currentItemId()

    def setActionsIdList(self, idList, posToId):
        self.getCurrentActionsTable().setIdList(idList, posToId)

    def focusActions(self):
        self.getCurrentActionsTable().setFocus(QtCore.Qt.TabFocusReason)

    def updateActionInfo(self, actionId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        record = db.getRecord(table,
                              ['Action.createDatetime', 'Action.createPerson_id', 'Action.modifyDatetime',
                               'Action.modifyPerson_id', 'Event.client_id', 'Action.payStatus', 'Action.note'],
                              actionId)

        clientId = forceRef(record.value('client_id')) if record else None

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserActions.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserActions.setText('')
        self.checkVipPerson(self.txtClientInfoBrowserActions, clientId)

        self.actActionEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

    def updateTempInvalidList(self, filter, posToId=None):
        u"""в соответствии с фильтром обновляет список документов вр. нетрудоспособности."""
        self.__expertFilter = filter
        db = QtGui.qApp.db
        if filter.get('linked', False):
            table = db.table('TempInvalid').alias('ti')
            mainTable = db.table('TempInvalid')
            queryTable = mainTable.join(table,
                                        db.joinAnd([mainTable['client_id'].eq(table['client_id']),
                                                    mainTable['caseBegDate'].eq(table['caseBegDate'])
                                                    ]))
        else:
            table = db.table('TempInvalid')
            mainTable = table
            queryTable = table

        tableDiagnosis = db.table('Diagnosis')
        queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(table['diagnosis_id']))
        tempInvalidType = self.tabWidgetTempInvalidTypes.currentIndex()
        cond = [mainTable['deleted'].eq(0),
                mainTable['type'].eq(tempInvalidType)
                ]
        self.addEqCond(cond, table, 'id', filter, 'id')
        self.addEqCond(cond, table, 'doctype_id', filter, 'docTypeId')
        self.addLikeCond(cond, table, 'serial', filter, 'serial')
        self.addLikeCond(cond, table, 'number', filter, 'number')
        self.addEqCond(cond, table, 'tempInvalidReason_id', filter, 'reasonId')
        self.addDateCond(cond, table, 'begDate', filter, 'begBegDate', 'endBegDate')
        self.addDateCond(cond, table, 'endDate', filter, 'begEndDate', 'endEndDate')
        self.addEqCond(cond, table, 'person_id', filter, 'personId')
        self.addRangeCond(cond, tableDiagnosis, 'MKB', filter, 'begMKB', 'endMKB')
        self.addEqCond(cond, table, 'closed', filter, 'closed')
        if 'expertOrgStructureId' in filter or 'expertOrgStructureId' in filter:
            tablePerson = db.table('Person')
            queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(table['person_id']))
            cond.append(tablePerson['deleted'].eq(0))
            if 'expertOrgStructureId' in filter:
                expertOrgStructureId = filter.get('expertOrgStructureId', None)
                if expertOrgStructureId:
                    orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', expertOrgStructureId)
                    if orgStructureIdList:
                        cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
            if 'expertSpecialityId' in filter:
                expertSpecialityId = filter.get('expertSpecialityId', None)
                if expertSpecialityId:
                    cond.append(tablePerson['speciality_id'].eq(expertSpecialityId))
        if 'begDuration' in filter:
            cond.append(table['duration'].ge(filter['begDuration']))
        if 'endDuration' in filter:
            endDuration = filter['endDuration']
            if endDuration:
                cond.append(table['duration'].le(endDuration))
        self.addEqCond(cond, table, 'insuranceOfficeMark', filter, 'insuranceOfficeMark')
        self.addEqCond(cond, table, 'createPerson_id', filter, 'createPersonId')
        self.addDateCond(cond, table, 'createDatetime', filter, 'begCreateDate', 'endCreateDate')
        self.addEqCond(cond, table, 'modifyPerson_id', filter, 'modifyPersonId')
        self.addDateCond(cond, table, 'modifyDatetime', filter, 'begModifyDate', 'endModifyDate')

        if 'clientIds' in filter:
            clientIds = filter['clientIds']
            cond.append(mainTable['client_id'].inlist(clientIds))

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            if table == mainTable:
                getIdList = db.getIdList
            else:
                getIdList = db.getDistinctIdList
            idList = getIdList(queryTable,
                               mainTable['id'].name(),
                               cond,
                               [mainTable['endDate'].name() + ' DESC', mainTable['id'].name()])
            self.setExpertIdList(idList, posToId)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

        expertFilterType = filter['expertFilterType']
        hideClientInfo = expertFilterType == 0 or expertFilterType == 1 and len(filter['clientIds']) == 1
        table = self.getCurrentExpertTable()
        for i in range(3):
            table.setColumnHidden(i, hideClientInfo)

    def updateTempInvalidInfo(self, tempInvalidId):
        db = QtGui.qApp.db
        tableTempInvalid = db.table('TempInvalid')
        record = db.getRecord(tableTempInvalid,
                              ['client_id'], tempInvalidId)
        if record:
            clientId = forceRef(record.value('client_id'))
        else:
            clientId = None

        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.txtClientInfoBrowserExpert.setHtml(getClientBanner(clientId))
        else:
            self.txtClientInfoBrowserExpert.setText('')
        self.checkVipPerson(self.txtClientInfoBrowserExpert, clientId)

        self.actExpertEditClient.setEnabled(bool(clientId))
        QtGui.qApp.setCurrentClientId(clientId)

        if tempInvalidId:
            table = db.table('TempInvalid_Period')
            idList = db.getIdList(table, 'id', table['master_id'].eq(tempInvalidId), ['id'])
        else:
            idList = []
        tblPeriods = self.getCurrentTempPeriodsTable()
        tblPeriods.setIdList(idList)

        if self.tabWidgetTempInvalidTypes.currentIndex() == 0:
            if tempInvalidId:
                table = db.table('TempInvalidDuplicate')
                idList = db.getIdList(
                    table,
                    'id',
                    [table['tempInvalid_id'].eq(tempInvalidId), table['deleted'].eq(0)],
                    ['id']
                )
            else:
                idList = []
            self.tblExpertTempInvalidDuplicates.setIdList(idList)

    def getExpertFilterAsText(self):
        db = QtGui.qApp.db
        filter = self.__expertFilter
        resList = []

        expertFilterType = filter['expertFilterType']
        if expertFilterType in [0, 1]:
            clientIds = filter.get('clientIds', None)
            if clientIds and len(clientIds) == 1:
                resList.append((u'Пациент', getClientMiniInfo(clientIds[0])))
            elif clientIds and len(clientIds) > 1:
                resList.append((u'Список пациентов', u'из вкладки'))
        else:
            resList.append((u'Список пациентов', u'полный'))

        tmpList = [
            ('id', u'Идентифиатор записи', lambda id: '%d' % id),
            ('docTypeId', u'Тип документа',
             lambda id: forceString(db.translate('rbTempInvalidDocument', 'id', id, 'name'))),
            ('serial', u'Серия', forceString),
            ('number', u'Номер', forceString),
            ('reasonId', u'Причина нетрудоспособности',
             lambda id: forceString(db.translate('rbTempInvalidReason', 'id', id, 'name'))),
            ('begBegDate', u'Дата начала с', forceString),
            ('endBegDate', u'Дата начала по', forceString),
            ('begEndDate', u'Дата окончания с', forceString),
            ('endEndDate', u'Дата окончания по', forceString),
            ('personId', u'Врач', lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begMKB', u'Код МКБ с', forceString),
            ('endMKB', u'Код МКБ по', forceString),
            ('closed', u'состояние', lambda closed: [u'открыт', u'закрыт', u'продлён', u'передан'][closed]),
            ('begDuration', u'длительность с', lambda v: '%d' % v),
            ('endDuration', u'длительность по', lambda v: '%d' % v),
            ('insuranceOfficeMark', u'отметка страхового стола', lambda i: [u'без отметки', u'с отметкой']),
            ('createPerson_id', u'Автор записи',
             lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begCreateDate', u'Дата создания с', forceString),
            ('endCreateDate', u'Дата создания по', forceString),
            ('modifyPerson_id', u'Запись изменил',
             lambda id: forceString(db.translate('vrbPersonWithSpeciality', 'id', id, 'name'))),
            ('begModifyDate', u'Дата изменения с', forceString),
            ('endModifyDate', u'Дата изменения по', forceString),
        ]
        for (x, y, z) in tmpList:
            convertFilterToTextItem(resList, filter, x, y, z)
        return '\n'.join([': '.join(item) for item in resList])

    def getCurrentExpertTable(self):
        index = self.tabWidgetTempInvalidTypes.currentIndex()
        return [self.tblExpertTempInvalid, self.tblExpertDisability, self.tblExpertVitalRestriction][index]

    def getCurrentTempPeriodsTable(self):
        index = self.tabWidgetTempInvalidTypes.currentIndex()
        return \
            [self.tblExpertTempInvalidPeriods, self.tblExpertDisabilityPeriods, self.tblExpertVitalRestrictionPeriods][
                index]

    def currentTempInvalidId(self):
        return self.getCurrentExpertTable().currentItemId()

    def currentTempInvalidDuplicateId(self):
        return self.tblExpertTempInvalidDuplicates.currentItemId()

    def setExpertIdList(self, idList, posToId):
        self.getCurrentExpertTable().setIdList(idList, posToId)

    def focusExpert(self):
        self.getCurrentExpertTable().setFocus(QtCore.Qt.TabFocusReason)

    def editTempInvalid(self, tempInvalidId):
        widgetIndex = self.tabWidgetTempInvalidTypes.currentIndex()
        dialog = CTempInvalidEditDialog(self)
        dialog.setWindowTitle(self.tabWidgetTempInvalidTypes.tabText(widgetIndex))
        dialog.load(tempInvalidId)
        if dialog.exec_():
            tempInvalidNewId = dialog.itemId()
            self.updateTempInvalidList(self.__expertFilter, tempInvalidNewId if tempInvalidNewId else tempInvalidId)

    def editTempInvalidExpert(self):
        widgetIndex = self.tabWidgetTempInvalidTypes.currentIndex()
        clientId = self.currentClientId()
        if clientId:
            dialog = CTempInvalidCreateDialog(self, clientId)
            dialog.setType(widgetIndex)
            dialog.setWindowTitle(self.tabWidgetTempInvalidTypes.tabText(widgetIndex))
            if dialog.exec_():
                self.updateTempInvalidList(self.__expertFilter, dialog.itemId())

    def getExpertPrevDocId(self, table):
        tempInvalidId = table.currentItemId()
        if tempInvalidId:
            model = table.model()
            currentItem = model.recordCache().get(tempInvalidId)
            return forceRef(currentItem.value('prev_id'))
        return None

    def getExpertNextDocId(self, table):
        tempInvalidId = table.currentItemId()
        if tempInvalidId:
            return forceRef(QtGui.qApp.db.translate('TempInvalid', 'prev_id', tempInvalidId, 'id'))
        return None

    def enableCardReaderSupport(self):
        QtGui.qApp.startProgressBar(1, u'Поддержка соц. карт...')

        prefs = QtGui.qApp.preferences.appPrefs
        if forceBool(getVal(prefs, 'SocCard_Emulation', False)):
            from Registry.CardReader import CCardReaderEmulator
            self.cardReader = CCardReaderEmulator()
        else:
            from Registry.CardReader import CCardReader
            self.cardReader = CCardReader()

        self.mapDocumentCodeToSocialCardCode = {}
        self.mapBenefitCodeToSocialCardCode = {}
        self.rbSocialCardDocumentType = None
        self.rbSocialCardBenefitType = None

        nPortNo = forceInt(getVal(prefs, 'SocCard_PortNumber', 0))
        diDevId = forceInt(getVal(prefs, 'SocCard_DevId', 0))
        listIssBSC = []

        for i in range(0, 6):
            listIssBSC.append(forceInt(getVal(prefs, 'SocCard_IssBSC%d' % i, 0)))

        szOperatorId = forceString(getVal(prefs, 'SocCard_OperatorId', ''))

        if self.cardReader.init(nPortNo, diDevId, listIssBSC, szOperatorId):
            QtGui.qApp.stepProgressBar()
            self.actFilterSocCard = QtGui.QAction(u'Социальная карта', self)
            self.actFilterSocCard.setObjectName('actFilterSocCard')
            self.actFilter = QtGui.QAction(u'Фильтр', self)
            self.actFilter.setObjectName('actFilter')
            self.mnuFilter = QtGui.QMenu(self)
            self.mnuFilter.setObjectName('mnuFilter')
            self.mnuFilter.addAction(self.actFilterSocCard)
            self.mnuFilter.addAction(self.actFilter)
            self.btnFilter.setMenu(self.mnuFilter)
            self.btnFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_F7))

            if forceBool(getVal(prefs, 'SocCard_SetAsDefaultSearch', False)):
                self.actFilterSocCard.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F7))
                self.actFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT + QtCore.Qt.Key_F7))
                self.mnuFilter.setDefaultAction(self.actFilterSocCard)
            else:
                self.actFilterSocCard.setShortcut(QtGui.QKeySequence(QtCore.Qt.SHIFT + QtCore.Qt.Key_F7))
                self.actFilter.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F7))
                self.mnuFilter.setDefaultAction(self.actFilter)

        else:
            rc = self.cardReader.rc()
            message = u'<h4>Ошибка инициализации считывателя карт.</h4>\n' \
                      u'Проверьте правильность подключения устройства и его ' \
                      u'настроек в меню Настойки.Умолчания.<br><br>' \
                      u'Параметры соединения:<table>' \
                      u'<tr><td>Номер порта:</td><td><b>%d</b></td></tr>' \
                      u'<tr><td>Идентификатор устройства:</td><td><b>%d</b></td></tr>' \
                      u'<tr><td>Код банка:</td><td><b>%.2d%.2d%.2d%.2d%.2d%.2d</b></td></tr>' \
                      u'<tr><td>Идентификатор оператора:</td><td><b>%s</b></td></tr>' \
                      u'<tr><td>Ошибка:</td><td><b>%s (код %d)</b></td></tr></table>' % \
                      (nPortNo, diDevId, listIssBSC[0], listIssBSC[1], listIssBSC[2], listIssBSC[3],
                       listIssBSC[4], listIssBSC[5], szOperatorId, self.cardReader.errorText(rc), rc)

            QtGui.QMessageBox.critical(self, u'Внимание!',
                                       message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        QtGui.qApp.stopProgressBar()

    def findClientBySocCardInfo(self, clientInfo):
        table = QtGui.qApp.db.table('Client')
        cond = []
        cond.append(table['deleted'].eq(0))

        for x in ('lastName', 'firstName', 'patrName', 'sex', 'birthDate'):
            if clientInfo.has_key(x):
                cond.append(table[x].eq(clientInfo[x]))

        QtGui.qApp.startProgressBar(2, u'Поиск пациента в БД...')
        record = QtGui.qApp.db.getRecordEx(table, 'id', cond, 'id')
        QtGui.qApp.stepProgressBar()
        SNILS = clientInfo.get('SNILS')

        if not record and SNILS:
            record = QtGui.qApp.db.getRecordEx(table, 'id', [table['deleted'].eq(0),
                                                             table['SNILS'].eq(SNILS),
                                                             ], 'id')
            QtGui.qApp.stepProgressBar()

        return record

    def processSocCard(self):
        if self.cardReader.checkCardType():
            QtGui.qApp.stepProgressBar()
            clientInfo = self.cardReader.socialInfo()
            QtGui.qApp.stepProgressBar()
            benefitInfo = self.cardReader.benefitInfo()
            QtGui.qApp.stepProgressBar()
            vitalInfo = self.cardReader.vitalInfo()
            QtGui.qApp.stepProgressBar()
            record = self.findClientBySocCardInfo(clientInfo) if clientInfo else None

            if record:
                return self.findClient(forceRef(record.value(0)), record)
            elif clientInfo:
                message = u'Пациент: %s %s %s, пол: %s, дата рождения:' \
                          u' %s, СНИЛС: %s, не найден в БД. Добавить новую ' \
                          u'регистрационную карту?' % (clientInfo.get('lastName', ''),
                                                       clientInfo.get('firstName', ''), clientInfo.get('patrName', ''),
                                                       formatSex(clientInfo.get('sex', 0)),
                                                       clientInfo.get('birthDate', QtCore.QDate()).toString(
                                                           'dd.MM.yyyy'),
                                                       formatSNILS(clientInfo.get('SNILS')))

                if QtGui.QMessageBox.question(self,
                                              u'Добавление нового пациента', message,
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.createNewClientDialogWithInfoFromSocCard(clientInfo, benefitInfo, vitalInfo)
            else:
                message = u'Социальная карта не содержит информации о пациенте'
                QtGui.QMessageBox.critical(self, u'Поиск пациента', message,
                                           QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self, u'Внимание!',
                                      u'Социальная карта не вставлена в считыватель,' \
                                      u' или имеет неверный формат.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def createNewClientDialogWithInfoFromSocCard(self, socialInfo, benefitInfo, vitalInfo):
        if QtGui.qApp.userHasAnyRight([urAdmin, urAddClient]):
            dialog = CClientEditDialog(self)
            self.loadSocialInfo(dialog, socialInfo)
            self.loadBenefitInfo(dialog, benefitInfo)
            self.loadVitalInfo(dialog, vitalInfo)
            if dialog.exec_():
                clientId = dialog.itemId()
                clientRecord = dialog.getRecord()
                self.findClient(clientId, clientRecord)
        else:
            self.showNotAllowedErrorMessage()

    def loadSocialInfo(self, dialog, socialInfo):
        dialog.edtFirstName.setText(socialInfo.get('firstName', ''))
        dialog.edtLastName.setText(socialInfo.get('lastName', ''))
        dialog.edtPatrName.setText(socialInfo.get('patrName', ''))
        dialog.edtBirthDate.setDate(socialInfo.get('birthDate', QtCore.QDate()))
        dialog.cmbSex.setCurrentIndex(socialInfo.get('sex', 0))
        dialog.edtSNILS.setText(socialInfo.get('SNILS', ''))
        serial = socialInfo.get('docSerial')
        for c in '-=/_|':
            serial = serial.replace('c', ' ')
        serial = forceStringEx(serial).split()
        serialLeft = serial[0] if len(serial) >= 1 else ''
        serialRight = serial[1] if len(serial) >= 2 else ''
        dialog.edtDocSerialLeft.setText(serialLeft)
        dialog.edtDocSerialRight.setText(serialRight)
        dialog.edtDocNumber.setText(socialInfo.get('docNumber'))
        docTypeId = self.getSocialCardDocumentTypeId(socialInfo.get('docType'))
        if docTypeId:
            dialog.cmbDocType.setValue(docTypeId)
        notes = u'Социальная карта: серия %s, номер %s. Идентификационный ' \
                u'номер социального регистра %s.' % (socialInfo.get('cardNumber', '-'),
                                                     socialInfo.get('cardSerial', '-'),
                                                     socialInfo.get('numberSocial', '-'))
        dialog.edtNotes.setText(notes)
        dialog.edtCompulsoryPolisSerial.setText(socialInfo.get('policySerial', ''))
        dialog.edtCompulsoryPolisNumber.setText(socialInfo.get('policyNumber', ''))
        notes = socialInfo.get('orgCode', '')
        policyDate = socialInfo.get('policyDate', None)
        if policyDate:
            notes += u' Дата действия полиса %s.' % policyDate
        dialog.edtCompulsoryPolisNote.setText(notes)

    def getSocialCardDocumentTypeId(self, code):
        id = self.lookupDocumentTypeId(code)

        if not id:
            if self.rbSocialCardDocumentType == None:
                fileName = forceString(getVal(QtGui.qApp.preferences.appPrefs,
                                              'SocCard_rbDocumentTypeRbFileName', ''))
                from Registry.CardReader import loadDocumentTypeRb
                self.rbSocialCardDocumentType = loadDocumentTypeRb(self, fileName)

            name = self.rbSocialCardDocumentType.get(code)

            if name:
                from Registry.CardReader import askUserForDocumentTypeId
                id = askUserForDocumentTypeId(self, code, name)
            else:
                message = u'Неизвестный код типа документа "%s".' % code
                QtGui.QMessageBox.critical(self, u'Импорт документа с социальной карты',
                                           message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

        return id

    def loadBenefitInfo(self, dialog, benefitInfo):
        if benefitInfo != []:

            for (code, begDate, endDate) in benefitInfo:
                id = self.lookupBenefitId(code)
                if not id:
                    if self.rbSocialCardBenefitType == None:
                        fileName = forceString(getVal(QtGui.qApp.preferences.appPrefs,
                                                      'SocCard_rbClientBenefitRbFileName', ''))
                        from Registry.CardReader import loadBenefitTypeRb
                        self.rbSocialCardBenefitType = loadBenefitTypeRb(self, fileName)

                    name = self.rbSocialCardBenefitType.get(code)

                    if name:
                        from Registry.CardReader import askUserForBenefitId
                        id = askUserForBenefitId(self, code, name)

                if id:
                    self.addBenefit(dialog, id, begDate, endDate)
                else:
                    message = u'Неизвестный код льготы "%s".' % code
                    QtGui.QMessageBox.critical(self, u'Импорт льгот с социальной карты',
                                               message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def addBenefit(self, dialog, id, begDate, endDate):
        record = dialog.modelSocStatuses.getEmptyRecord()
        record.setValue('socStatusType_id', toVariant(id))
        record.setValue('begDate', toVariant(begDate))
        record.setValue('endDate', toVariant(endDate))
        dialog.modelSocStatuses.insertRecord(0, record)

    def loadVitalInfo(self, dialog, vitalInfo):
        if vitalInfo != 0:
            (allergy, intolerance, notes) = self.cardReader.decodeVitalInfo(vitalInfo)

            for x in allergy:
                record = dialog.modelAllergy.getEmptyRecord()
                record.setValue('nameSubstance', toVariant(x))
                record.setValue('createDate', toVariant(QtCore.QDate.currentDate()))
                dialog.modelAllergy.insertRecord(0, record)

            for x in intolerance:
                record = dialog.modelIntoleranceMedicament.getEmptyRecord()
                record.setValue('nameMedicament', toVariant(x))
                record.setValue('createDate', toVariant(QtCore.QDate.currentDate()))
                dialog.modelIntoleranceMedicament.insertRecord(0, record)

            if notes != []:
                strNotes = forceString(dialog.edtNotes.toPlainText()) + \
                           u' ' + u', '.join([str(et) for et in notes])
                dialog.edtNotes.setText(strNotes)

    def lookupBenefitId(self, code):
        id = self.mapBenefitCodeToSocialCardCode.get(code)

        if not id:
            db = QtGui.qApp.db
            table = db.table('rbSocStatusType')
            record = db.getRecordEx(table, 'id',
                                    [table['socCode'].eq(code)], 'id')

            if record:
                id = forceInt(record.value(0))
                self.mapBenefitCodeToSocialCardCode[code] = id

        return id

    def lookupDocumentTypeId(self, code):
        id = self.mapDocumentCodeToSocialCardCode.get(code)

        if not id:
            db = QtGui.qApp.db
            table = db.table('rbDocumentType')
            record = db.getRecordEx(table, 'id',
                                    [table['socCode'].eq(code)], 'id')

            if record:
                id = forceInt(record.value(0))
                self.mapDocumentCodeToSocialCardCode[code] = id

        return id

    def printConfigurableList(self, header, view, model, filterString):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle(u'Выбор полей для печати')
        dialog.layout = QtGui.QVBoxLayout(dialog)
        dialog.lblDescription = QtGui.QLabel(u'Выберите поля для печати:', dialog)
        dialog.lstItems = QtGui.QListWidget(dialog)
        dialog.lstItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        values = [forceString(col.title()) for col in model.cols()]
        dialog.lstItems.addItems(values)
        dialog.lstItems.selectAll()
        dialog.buttonBox = QtGui.QDialogButtonBox(dialog)
        dialog.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        dialog.buttonBox.accepted.connect(dialog.accept)
        dialog.buttonBox.rejected.connect(dialog.reject)
        dialog.layout.addWidget(dialog.lblDescription)
        dialog.layout.addWidget(dialog.lstItems)
        dialog.layout.addWidget(dialog.buttonBox)
        if dialog.exec_():
            if isinstance(self.registryWidget(), CStandardRegistryWidget):
                dialog.lstItems.selectedIndexes()
                dataRoles = [None] * model.columnCount()  # Скрываем все элементы
                for index in dialog.lstItems.selectedIndexes():
                    dataRoles[index.row()] = QtCore.Qt.DisplayRole  # Разрешаем печатать выбранные
            else:
                dataRoles = None
            view.setReportHeader(header)
            view.setReportDescription(filterString)
            view.printContent(columnRoleList=dataRoles)

    def getKerContextData(self):
        clientId = self.currentClientId()
        tempInvalidId = self.currentTempInvalidId()
        data = getClientContextData(clientId)
        context = data['client'].context
        if self.tabWidgetExpertTempInvalidDetails.currentIndex() == 0:  # вкладка "Периоды"
            tempInvalidInfo = context.getInstance(CTempInvalidInfo, tempInvalidId)
            data['isDuplicate'] = False
            data['tempInvalid'] = tempInvalidInfo
            # tempInvalidPeriodId = self.currentTempInvalidPeriodId() ??????????
        else:  # self.tabWidgetExpertTempInvalidDetails.currentIndex() == 1: #вкладка "Дубликаты"
            tempInvalidDuplicateId = self.currentTempInvalidDuplicateId()
            tempInvalidInfo = context.getInstance(CTempInvalidDuplicateInfo, tempInvalidId, tempInvalidDuplicateId)
            data['isDuplicate'] = (tempInvalidDuplicateId > 0)
            data['tempInvalid'] = tempInvalidInfo
        diagnosisId = forceRef(QtGui.qApp.db.translateEx('TempInvalid', 'id', tempInvalidId, 'diagnosis_id'))
        data['event'] = getEventInfoByDiagnosis(context, diagnosisId)
        return data

    @QtCore.pyqtSlot(int)
    def on_tabMain_currentChanged(self, index):
        Logger.logWindowAccess(windowName=type(self).__name__, element=self.tabMain.tabText(index),
                               login_id=Logger.loginId, notes=u'Переход по вкладке в рег карте')
        keyboardModifiers = QtGui.qApp.keyboardModifiers()
        self.registryWidget().viewWidget().model().fillVIPClients()

        if index == self.tabMain.indexOf(self.tabRegistry):  # реестр
            self.syncSplitters(self.splitterRegistry)
            if self.tabMainCurrentPage == self.tabMain.indexOf(self.tabEvents):
                if keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                    db = QtGui.qApp.db
                    eventId = self.currentEventId()
                    clientId = forceRef(db.translate('Event', 'id', eventId, 'client_id'))
                    self.registryWidget().viewWidget().setCurrentItemId(clientId)
                if self.updateClientsListRequest:
                    self.updateRegistryContent()
            self.currentClientFromEvent = False
            self.currentClientFromAction = False
            self.currentClientFromExpert = False
            self.chkFilterContingentDD.setEnabled(QtGui.qApp.checkContingentDDGlobalPreference())
        elif index == self.tabMain.indexOf(self.tabEvents):  # осмотры
            if not self.isTabEventAlreadyLoad:
                self.btnEventPrint.addAction(self.actEventPrint)
                self.btnEventPrint.addAction(self.actEventListPrintTemplate)
                self.btnEventPrint.addAction(self.actPrintF30PRR)
                self.cmbFilterVisitScene.setTable('rbScene', True)
                self.cmbFilterVisitType.setTable('rbVisitType', True)
                self.cmbFilterVisitProfile.setTable('rbService', True)
                self.edtFilterEventId.setValidator(self.idValidator)
                self.cmbFilterEventPurpose.setTable('rbEventTypePurpose', False, filter='code != \'0\'')
                self.cmbFilterEventType.setTable('EventType', False, filter=getWorkEventTypeFilter())
                self.lstFilterEventType.setTable('EventType', filter=getWorkEventTypeFilter())
                self.lstFilterEventType.setVisible(False)
                self.selectionModelFilterEventType = self.lstFilterEventType.selectionModel()
                self.connect(self.selectionModelFilterEventType,
                             QtCore.SIGNAL('currentRowChanged(QModelIndex,QModelIndex)'),
                             self.on_selectionModelFilterEventType_currentRowChanged)

                self.cmbFilterEventSpeciality.setTable('rbSpeciality', False)
                self.cmbFilterEventGoal.setTable('rbEventGoal', False, codeFieldName='regionalCode',
                                                 group='regionalCode')
                self.cmbFilterEventDiagnosisType.setTable('rbDiagnosisType', True)
                self.cmbFilterEventPerson.setOrgId(None)
                self.cmbFilterEventPerson.setAddNone(False)
                self.cmbFilterEventPerson.addNotSetValue()

                self.cmbFilterVisitPerson.setOrgId(None)
                self.cmbFilterVisitPerson.setAddNone(False)
                self.cmbFilterVisitPerson.addNotSetValue()

                self.cmbFilterEventCreatePerson.setSpecialityPresent(False)
                self.cmbFilterEventModifyPerson.setSpecialityPresent(False)
                self.setUserRights_ForEventTab()
                self.chkListOnEventsPage = [
                    (self.chkFilterEventPurpose, [self.cmbFilterEventPurpose]),
                    (self.chkFilterEventType,
                     [self.cmbFilterEventType, self.lstFilterEventType, self.chkFilterEventTypeMulti]),
                    (self.chkFilterEventSetDate, [self.edtFilterEventBegSetDate, self.edtFilterEventEndSetDate]),
                    (self.chkFilterEventEmptyExecDate, []),
                    (self.chkFilterEventExecDate, [self.edtFilterEventBegExecDate, self.edtFilterEventEndExecDate]),
                    (self.chkFilterEventNextDate, [self.edtFilterEventBegNextDate, self.edtFilterEventEndNextDate]),
                    (self.chkFilterEventOrgStructure, [self.cmbFilterEventOrgStructure]),
                    (self.chkFilterEventSpeciality, [self.cmbFilterEventSpeciality]),
                    (self.chkFilterEventPerson, [self.cmbFilterEventPerson]),
                    (self.chkFilterEventDispanserObserved, []),
                    (self.chkFilterEventLPU, [self.cmbFilterEventLPU]),
                    (self.chkFilterEventNonBase, []),
                    (self.chkRelegateOrg, [self.cmbRelegateOrg]),
                    (self.chkFilterEventMes, [self.edtFilterEventMes]),
                    (self.chkFilterEventResult, [self.cmbFilterEventResult]),
                    (self.chkFilterEventGoal, [self.cmbFilterEventGoal]),
                    (self.chkFilterEventCreatePerson, [self.cmbFilterEventCreatePerson]),
                    (self.chkFilterEventCreateDate,
                     [self.edtFilterEventBegCreateDate, self.edtFilterEventEndCreateDate]),
                    (self.chkFilterEventModifyPerson, [self.cmbFilterEventModifyPerson]),
                    (self.chkFilterEventModifyDate,
                     [self.edtFilterEventBegModifyDate, self.edtFilterEventEndModifyDate]),
                    (self.chkErrorInDiagnostic, []),
                    (self.chkFilterMKBRange,
                     [self.edtFilterMKBBottom, self.edtFilterMKBTop, self.cmbFilterEventDiagnosisType]),
                    (self.chkFilterEventPayStatus,
                     [self.cmpFilterEventPayStatusCode, self.cmbFilterEventPayStatusFinance]),
                    (self.chkFilterVisitPayStatus,
                     [self.cmpFilterVisitPayStatusCode, self.cmbFilterVisitPayStatusFinance]),
                    (self.chkFilterMesEvents, [self.cmbFilterMesEvents]),
                    (self.chkFilterEventId, [self.edtFilterEventId]),
                    (self.chkFilterExternalId, [self.edtFilterExternalId, self.chkFilterMaskExternalId]),
                    (self.chkFilterAccountSumLimit,
                     [self.cmbFilterAccountSumLimit, self.edtFilterSumLimitFrom, self.edtFilterSumLimitTo,
                      self.edtFilterSumLimitDelta]),
                    (self.chkPrimary, [self.cmpPrimary]),
                    (self.chkFilterVisits,
                     [self.cmbFilterVisitScene, self.cmbFilterVisitType, self.cmbFilterVisitProfile,
                      self.cmbFilterVisitPerson]),
                    (self.chkFilterExposeConfirmed, [self.cmbFilterExposeConfirmed]),
                    (self.chkEventLID, [self.edtEventLID])
                ]
                self.isTabEventAlreadyLoad = True
            self.syncSplitters(self.splitterEvents)
            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 2
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = 1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = 0
            if clientsFilterType == 0 and self.currentClientFromEvent and not self.currentClientFromAction and not self.currentClientFromExpert:
                # возврат из мед. карты или подобного, на одного пациента
                self.updateEventInfo(self.currentEventId())
            else:
                self.updateEventInfo(None)
                if clientsFilterType != -1:
                    self.on_buttonBoxEvent_reset()
                    self.cmbFilterEventByClient.setCurrentIndex(clientsFilterType)
                self.on_buttonBoxEvent_apply()
            self.currentClientFromEvent = True
            self.currentClientFromAction = False
            self.currentClientFromExpert = False
        elif index == self.tabMain.indexOf(self.tabAmbCard):  # мед.карта
            self.syncSplitters(self.splitterAmbCard)
            self.updateAmbCardInfo()
            self.tabAmbCardContent.resetWidgets()
        elif index == self.tabMain.indexOf(self.tabActions):  # Обслуживание
            if not self.isTabActionsAlreadyLoad:
                self.setModels(self.tblActionsStatus, self.modelActionsStatus, self.selectionModelActionsStatus)
                self.setModels(self.tblActionsStatusProperties, self.modelActionsStatusProperties,
                               self.selectionModelActionsStatusProperties)
                self.setModels(self.tblActionsDiagnostic, self.modelActionsDiagnostic,
                               self.selectionModelActionsDiagnostic)
                self.setModels(self.tblActionsDiagnosticProperties, self.modelActionsDiagnosticProperties,
                               self.selectionModelActionsDiagnosticProperties)
                self.setModels(self.tblActionsCure, self.modelActionsCure, self.selectionModelActionsCure)
                self.setModels(self.tblActionsCureProperties, self.modelActionsCureProperties,
                               self.selectionModelActionsCureProperties)
                self.setModels(self.tblActionsMisc, self.modelActionsMisc, self.selectionModelActionsMisc)
                self.setModels(self.tblActionsMiscProperties, self.modelActionsMiscProperties,
                               self.selectionModelActionsMiscProperties)
                self.setModels(self.tblActionsAnalyses, self.modelActionsAnalyses, self.selectionModelActionsAnalyses)
                self.setModels(self.tblActionsAnalysesProperties, self.modelActionsAnalysesProperties,
                               self.selectionModelActionsAnalysesProperties)
                self.cmbFilterActionType.setAllSelectable(True)
                self.cmbFilterActionType.setClass(0)
                self.cmbFilterActionSetSpeciality.setTable('rbSpeciality', False)
                self.cmbFilterExecSetSpeciality.setTable('rbSpeciality', False)
                self.cmbFilterActionSetPerson.setOrgId(None)
                self.cmbFilterActionSetPerson.setAddNone(False)
                self.cmbFilterExecSetPerson.setOrgId(None)
                self.cmbFilterExecSetPerson.setAddNone(True)
                self.cmbFilterExecSetPerson.addNotSetValue()
                self.cmbFilterAssistant.addNotSetValue()
                self.cmbFilterActionCreatePerson.setSpecialityPresent(False)
                self.cmbFilterActionModifyPerson.setSpecialityPresent(False)
                self.chkListOnActionsPage = [
                    (self.chkFilterActionType, [self.cmbFilterActionType, self.chkListProperty]),
                    (self.chkFilterActionStatus, [self.cmbFilterActionStatus]),
                    (self.chkFilterActionSetDate, [self.edtFilterActionBegSetDate, self.edtFilterActionEndSetDate]),
                    (self.chkFilterActionSetSpeciality, [self.cmbFilterActionSetSpeciality]),
                    (self.chkFilterActionSetPerson, [self.cmbFilterActionSetPerson]),
                    (self.chkFilterActionIsUrgent, []),
                    (self.chkFilterActionPlannedEndDate,
                     [self.edtFilterActionBegPlannedEndDate, self.edtFilterActionEndPlannedEndDate]),
                    (self.chkFilterActionExecDate,
                     [self.edtFilterActionBegExecDate, self.edtFilterActionBegExecTime, self.edtFilterActionEndExecDate,
                      self.edtFilterActionEndExecTime]),
                    (self.chkFilterExecSetSpeciality, [self.cmbFilterExecSetSpeciality]),
                    (self.chkFilterExecSetPerson, [self.cmbFilterExecSetPerson]),
                    (self.chkFilterAssistant, [self.cmbFilterAssistant]),
                    (self.chkFilterActionCreatePerson, [self.cmbFilterActionCreatePerson]),
                    (self.chkFilterActionCreateDate,
                     [self.edtFilterActionBegCreateDate, self.edtFilterActionEndCreateDate]),
                    (self.chkFilterActionModifyPerson, [self.cmbFilterActionModifyPerson]),
                    (self.chkFilterActionModifyDate,
                     [self.edtFilterActionBegModifyDate, self.edtFilterActionEndModifyDate]),
                    (self.chkFilterActionPayStatus,
                     [self.cmpFilterActionPayStatusCode, self.cmbFilterActionPayStatusFinance]),
                    (self.chkTakeIntoAccountProperty, [self.chkFilledProperty, self.chkThresholdPenaltyGrade]),
                    (self.chkThresholdPenaltyGrade, [self.edtThresholdPenaltyGrade]),
                    (self.chkListProperty, [self.tblListOptionProperty]),
                    (self.chkFilledProperty, [])
                ]
                self.tblActionsStatusProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.tblActionsDiagnosticProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.tblActionsCureProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.tblActionsMiscProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.tblActionsAnalysesProperties.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
                self.txtClientInfoBrowserActions.actions.append(self.actActionEditClient)

                if u'онко' in forceString(
                        QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')):
                    if QtGui.qApp.userHasRight(urSetVIPComment) or QtGui.qApp.userHasRight(urEditSetVIPStatus):
                        self.txtClientInfoBrowserEvents.actions.append(self.actSetVIPStatus)

                self.tblActionsStatus.createPopupMenu([self.actEditActionEvent])
                self.tblActionsDiagnostic.createPopupMenu([self.actEditActionEvent])
                self.tblActionsCure.createPopupMenu([self.actEditActionEvent])
                self.tblActionsMisc.createPopupMenu([self.actEditActionEvent])
                self.tblActionsAnalyses.createPopupMenu([self.actEditActionEvent])
                self.setUserRights_ForActionsTab()
                self.isTabActionsAlreadyLoad = True
            self.syncSplitters(self.splitterActions)
            self.updateActionInfo(None)
            if self.currentClientFromEvent:  # переход сквозь осмотры
                cmbFilterActionFlags = QtCore.QVariant(int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable))
                cmbFilterActionDefault = 2
            else:
                cmbFilterActionFlags = QtCore.QVariant(0)
                cmbFilterActionDefault = 0
            self.cmbFilterAction.setItemData(2, cmbFilterActionFlags, QtCore.Qt.UserRole - 1)
            self.cmbFilterAction.setItemData(3, cmbFilterActionFlags, QtCore.Qt.UserRole - 1)

            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 5
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = cmbFilterActionDefault + 1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = cmbFilterActionDefault
            if clientsFilterType != -1:
                self.on_buttonBoxAction_reset()
                self.cmbFilterAction.setCurrentIndex(clientsFilterType)
            self.on_buttonBoxAction_apply()
            self.currentClientFromEvent = False
            self.currentClientFromAction = True
            self.currentClientFromExpert = False
        elif index == self.tabMain.indexOf(self.tabExpert):  # КЭР
            if not self.isTabExpertAlreadyLoad:
                self.btnExpertPrint.addAction(self.actExpertPrint)
                additionalCustomizePrintButton(self, self.btnExpertPrint, getKerContext(), [
                    {'action': self.actExpertPrint, 'slot': self.on_actExpertPrint_triggered}, ])
                self.setModels(self.tblExpertTempInvalid, self.modelExpertTempInvalid,
                               self.selectionModelExpertTempInvalid)
                self.setModels(self.tblExpertTempInvalidPeriods, self.modelExpertTempInvalidPeriods,
                               self.selectionModelExpertTempInvalidPeriods)
                self.setModels(self.tblExpertTempInvalidDuplicates, self.modelExpertTempInvalidDuplicates,
                               self.selectionModelExpertTempInvalidDuplicates)
                self.setModels(self.tblExpertDisability, self.modelExpertDisability,
                               self.selectionModelExpertDisability)
                self.setModels(self.tblExpertDisabilityPeriods, self.modelExpertDisabilityPeriods,
                               self.selectionModelExpertDisabilityPeriods)
                self.setModels(self.tblExpertVitalRestriction, self.modelExpertVitalRestriction,
                               self.selectionModelExpertVitalRestriction)
                self.setModels(self.tblExpertVitalRestrictionPeriods, self.modelExpertVitalRestrictionPeriods,
                               self.selectionModelExpertVitalRestrictionPeriods)
                self.chkListOnExpertPage = [
                    (self.chkFilterExpertDocType, [self.cmbFilterExpertDocType]),
                    (self.chkFilterExpertSerial, [self.edtFilterExpertSerial]),
                    (self.chkFilterExpertNumber, [self.edtFilterExpertNumber]),
                    (self.chkFilterExpertReason, [self.cmbFilterExpertReason]),
                    (self.chkFilterExpertBegDate, [self.edtFilterExpertBegBegDate, self.edtFilterExpertEndBegDate]),
                    (self.chkFilterExpertEndDate, [self.edtFilterExpertBegEndDate, self.edtFilterExpertEndEndDate]),
                    (self.chkFilterExpertOrgStruct, [self.cmbFilterExpertOrgStruct]),
                    (self.chkFilterExpertSpeciality, [self.cmbFilterExpertSpeciality]),
                    (self.chkFilterExpertPerson, [self.cmbFilterExpertPerson]),
                    (self.chkFilterExpertMKB, [self.edtFilterExpertBegMKB, self.edtFilterExpertEndMKB]),
                    (self.chkFilterExpertClosed, [self.cmbFilterExpertClosed]),
                    (self.chkFilterExpertDuration, [self.edtFilterExpertBegDuration, self.edtFilterExpertEndDuration]),
                    (self.chkFilterExpertInsuranceOfficeMark, [self.cmbFilterExpertInsuranceOfficeMark]),
                    (self.chkFilterExpertLinked, []),
                    (self.chkFilterExpertCreatePerson, [self.cmbFilterExpertCreatePerson]),
                    (self.chkFilterExpertCreateDate,
                     [self.edtFilterExpertBegCreateDate, self.edtFilterExpertEndCreateDate]),
                    (self.chkFilterExpertModifyPerson, [self.cmbFilterExpertModifyPerson]),
                    (self.chkFilterExpertModifyDate,
                     [self.edtFilterExpertBegModifyDate, self.edtFilterExpertEndModifyDate]),
                ]
                self.txtClientInfoBrowserExpert.actions.append(self.actExpertEditClient)
                self.tblExpertTempInvalid.createPopupMenu(
                    [self.actExpertTempInvalidNext, self.actExpertTempInvalidPrev, '-',
                     self.actExpertTempInvalidDuplicate])
                self.tblExpertDisability.addPopupDelRow()
                self.tblExpertTempInvalid.addPopupDelRow()
                self.tblExpertTempInvalidDuplicates.addPopupDelRow()
                self.connect(self.tblExpertTempInvalid.popupMenu(), QtCore.SIGNAL('aboutToShow()'),
                             self.onExpertTempInvalidPopupMenuAboutToShow)
                self.setUserRights_ForExpertTab()
                self.isTabExpertAlreadyLoad = True
            self.syncSplitters(self.splitterExpert)
            self.updateTempInvalidInfo(None)
            if keyboardModifiers & QtCore.Qt.AltModifier == QtCore.Qt.AltModifier:
                clientsFilterType = 2
            elif keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
                clientsFilterType = 1
            elif keyboardModifiers & QtCore.Qt.ShiftModifier == QtCore.Qt.ShiftModifier:
                clientsFilterType = -1
            else:
                clientsFilterType = 0
            if clientsFilterType != -1:
                self.on_buttonBoxExpert_reset()
                self.cmbFilterExpert.setCurrentIndex(clientsFilterType)
            self.on_tabWidgetTempInvalidTypes_currentChanged(self.tabWidgetTempInvalidTypes.currentIndex())
            self.currentClientFromEvent = False
            self.currentClientFromAction = False
            self.currentClientFromExpert = True
        elif index == self.tabMain.indexOf(self.tabFullClientInfo):  # Амбулаторная карта для ПНД
            self.teFullClientInfo.setHtml(getFullClientInfoAsHtml(self.selectedClientId()))
        elif index == self.tabMain.indexOf(self.tabRecommendations):
            self.modelRecommendations.updateContents()
            pass  # self.modelRecommendations.update
        elif index == self.tabMain.indexOf(self.tabReferrals):
            self.modelOutgoingReferrals.updateContents()
            self.modelInputReferrals.updateContents()
            self.updateRefCount()
            self.cmbFRefRelegateMO.setFilter('NOT isMedical = 0')
            self.cmbFRefType.setTable('rbReferralType')
            self.edtFRefBegDate.setDate(QtCore.QDate.currentDate())
            self.edtFRefEndDate.setDate(QtCore.QDate.currentDate())
        self.tabMainCurrentPage = index

    def getFilterInfoBed(self):
        def getNameOrgStructure(orgStructureId):
            db = QtGui.qApp.db
            if orgStructureId:
                tableOS = db.table('OrgStructure')
                record = db.getRecordEx(tableOS, [tableOS['name']],
                                        [tableOS['deleted'].eq(0), tableOS['id'].eq(orgStructureId)])
                if record:
                    nameOrgStructure = forceString(record.value(0))
                else:
                    nameOrgStructure = forceString(None)
            else:
                tableO = db.table('Organisation')
                recordOrg = db.getRecordEx(tableO, [tableO['shortName']],
                                           [tableO['deleted'].eq(0), tableO['id'].eq(QtGui.qApp.currentOrgId())])
                if recordOrg:
                    nameOrgStructure = forceString(recordOrg.value(0))
                else:
                    nameOrgStructure = forceString(None)
            return nameOrgStructure

        infoBeds = u''
        if self.chkFilterBeds.isChecked():
            statusBeds = self.cmbFilterStatusBeds.currentText()
            orgStructureId = self.cmbFilterOrgStructureBeds.value()
            infoBeds = u'; по койкам: статус %s подразделение %s' % (statusBeds, getNameOrgStructure(orgStructureId))
        infoAddressOrgStructure = u''
        if self.chkFilterAddressOrgStructure.isChecked():
            orgStructureType = self.cmbFilterAddressOrgStructureType.currentText()
            orgStructureId = self.cmbFilterAddressOrgStructure.value()
            infoAddressOrgStructure = u'; по участкам: тип %s подразделение %s' % (
                orgStructureType, getNameOrgStructure(orgStructureId))
        return [infoBeds, infoAddressOrgStructure]

    def showNotAllowedErrorMessage(self):
        QtGui.QMessageBox.information(self, u'Ошибка!',
                                      u'Недостаточно прав для выполнения операции. Обратитесь к системному администратору.')

    def updateRefCount(self):
        self.lblRefOutCountTxt.setText(u'Количество записей: ' + forceString(len(self.modelOutgoingReferrals._idList)))
        self.lblRefInCountTxt.setText(u'Количество записей: ' + forceString(len(self.modelInputReferrals._idList)))

    @QtCore.pyqtSlot(int)  # TODO: atronah: need connect
    def onRegistryItemCountChanged(self, count):
        realItemCount = self.registryWidget().model().getRealItemCount()
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblClientsCount.setText(formatRecordsCount2(count, realItemCount) + infoBeds + infoAddressOrgStructure)

    @QtCore.pyqtSlot()
    def onCurrentClientChanged(self):
        clientId = self.selectedClientId()
        self.showClientInfo(clientId)
        self.tabMain.setTabEnabled(self.tabMain.indexOf(self.tabEvents), bool(clientId))
        if clientId:
            recommendationsAvailable = len(QtGui.qApp.db.getIdList('Recommendation',
                                                                   where='setEvent_id in (SELECT id FROM Event WHERE client_id = %d)' % clientId)) > 0
        else:
            recommendationsAvailable = False
        self.tabMain.setTabEnabled(self.tabMain.indexOf(self.tabRecommendations), recommendationsAvailable)
        self.updateQueue()
        Logger.logClientChoice(login_id=Logger.loginId, client_id=clientId)

    @QtCore.pyqtSlot()
    def updateQueue(self):
        clientId = self.currentClientId()
        self.modelQueue.loadData(clientId)
        self.modelVisitByQueue.loadData(clientId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def registryContentDoubleClicked(self, index):
        if isinstance(self.registryWidget(), CStandardRegistryWidget):
            column = index.column()
            if column == 11:
                self.updateStatusObservationClient()
            elif column == 12:
                self.updateLocationCardType()
            else:
                self.editCurrentClient()
        elif isinstance(self.registryWidget(), CCustomizableRegistryWidget):
            if index.row() not in xrange((self.registryWidget().viewWidget().model().filterRowCount())):
                self.editCurrentClient()
        self.focusClients()

    def showQueuePosition(self, actionId, VisitBefore=False):
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tablePerson = db.table('Person')
            cols = [tableAction['directionDate'],
                    tableAction['person_id'],
                    tablePerson['orgStructure_id'],
                    tablePerson['speciality_id']]
            cond = [tableAction['id'].eq(actionId),
                    tableAction['deleted'].eq(0),
                    tablePerson['deleted'].eq(0)]
            table = tableAction.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
            record = db.getRecordEx(table, cols, cond)
            if record:
                date = forceDate(record.value('directionDate'))
                personId = forceRef(record.value('person_id'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                specialityId = forceRef(record.value('speciality_id'))
                try:
                    if QtGui.qApp.mainWindow.dockResources and personId and date and orgStructureId and specialityId and actionId:
                        QtGui.qApp.mainWindow.dockResources.content.showQueueItem(orgStructureId, specialityId,
                                                                                  personId, date, actionId)
                except:
                    pass

    ##########tabReferral#############
    @QtCore.pyqtSlot()
    def on_btnCreateEventByInputReferral_clicked(self):
        recReferral = self.tblInputReferrals.model().getRecordByRow(self.tblInputReferrals.currentIndex().row())
        if not forceInt(recReferral.value('event_id')):
            self.requestNewEvent(referralId=forceInt(recReferral.value('id')),
                                 clientId=forceInt(recReferral.value('client_id')))
            self.focusEvents()
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Для данного направления уже создано обращение')

    @QtCore.pyqtSlot()
    def on_btnAnnulateInputReferral_clicked(self):
        db = QtGui.qApp.db
        tableReferral = db.table('Referral')
        currentRow = self.tblInputReferrals.model().getRecordByRow(self.tblInputReferrals.currentIndex().row())
        recReferral = db.getRecordEx(tableReferral, '*', tableReferral['id'].eq(forceRef(currentRow.value('id'))))
        if recReferral:
            if forceInt(recReferral.value('isCancelled')):
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Направление уже аннулировано.')
            reasonDialog = CRBCancellationReasonList(self)
            if not reasonDialog.exec_():
                return
            reason = reasonDialog.params()
            if QtGui.qApp.defaultKLADR().startswith('23') and forceInt(recReferral.value('type')) == 1:
                recReferral.setValue('cancelReason', toVariant(reason))
                recReferral.setValue('isCancelled', toVariant(1))
                recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                if db.updateRecord(tableReferral, recReferral):
                    QtGui.QMessageBox.information(self, u'Успешно',
                                                  u'Направление успешно аннулировано.\nДанные обновятся в ЦОД при следующей передаче.')
                    self.tblOutgoingReferrals.model().updateContents()
                    self.updateRefCount()
                else:
                    QtGui.QMessageBox.information(self, u'Ошибка', u'При аннулировании возникли ошибки')
            else:
                service = NetricaServices()
                cancellation = service.sendCancellation(forceString(recReferral.value('netrica_id')))
                if cancellation:
                    recReferral.setValue('isCancelled', toVariant(1))
                    recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                    recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                    if db.updateRecord(tableReferral, recReferral):
                        QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно аннулировано')
                        self.tblInputReferrals.model().updateContents()
                        self.updateRefCount()
                    else:
                        QtGui.QMessageBox.information(self, u'Ошибка', u'При аннулировании возникли ошибки')

    @QtCore.pyqtSlot()
    def on_btnAnnulateOutgoingReferral_clicked(self):
        db = QtGui.qApp.db
        tableReferral = db.table('Referral')
        currentRow = self.tblOutgoingReferrals.model().getRecordByRow(self.tblOutgoingReferrals.currentIndex().row())
        recReferral = db.getRecordEx(tableReferral, '*', tableReferral['id'].eq(forceRef(currentRow.value('id'))))
        if recReferral:
            if forceInt(recReferral.value('isCancelled')):
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Направление уже аннулировано.')
                return
            reasonDialog = CRBCancellationReasonList(self)
            if not reasonDialog.exec_():
                return
            reason = reasonDialog.params()
            if QtGui.qApp.defaultKLADR().startswith('23') and forceInt(recReferral.value('type')) == 1:
                recReferral.setValue('cancelReason', toVariant(reason))
                recReferral.setValue('isCancelled', toVariant(1))
                recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                recReferral.setValue('status', toVariant(0))
                if db.updateRecord(tableReferral, recReferral):
                    QtGui.QMessageBox.information(self, u'Успешно',
                                                  u'Направление успешно аннулировано.\nДанные обновятся в ЦОД при следующей передаче.')
                    self.tblOutgoingReferrals.model().updateContents()
                    self.updateRefCount()
                else:
                    QtGui.QMessageBox.information(self, u'Ошибка', u'При аннулировании возникли ошибки')
            else:
                service = NetricaServices()
                cancellation = service.sendCancellation(forceString(recReferral.value('netrica_id')))
                if cancellation:
                    recReferral.setValue('cancelReason', toVariant(reason))
                    recReferral.setValue('isCancelled', toVariant(1))
                    recReferral.setValue('cancelPerson_id', toVariant(QtGui.qApp.userId))
                    recReferral.setValue('cancelDate', toVariant(QtCore.QDateTime.currentDateTime()))
                    recReferral.setValue('status', toVariant(0))
                    if db.updateRecord(tableReferral, recReferral):
                        QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно аннулировано')
                        self.tblOutgoingReferrals.model().updateContents()
                        self.updateRefCount()
                    else:
                        QtGui.QMessageBox.information(self, u'Ошибка', u'При аннулировании возникли ошибки')

    @QtCore.pyqtSlot()
    def on_btnEditOutgoingReferral_clicked(self):
        record = self.tblOutgoingReferrals.model().getRecordByRow(self.tblOutgoingReferrals.currentIndex().row())
        edtDlg = CReferralEditDialog(parent=self, referralId=forceString(record.value('id')))
        if edtDlg.checkData():
            if not edtDlg.exec_():
                return False
            if QtGui.qApp.defaultKLADR().startswith('23') and forceInt(record.value('type')) == 1:
                if edtDlg.checkData() and edtDlg.beforeSave() and edtDlg.getRecord():
                    QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно изменено')
                    self.tblOutgoingReferrals.model().updateContents()
                else:
                    QtGui.QMessageBox.warning(self, u'Ошибка', u'При изменении направления возникли ошибки')
            else:
                if edtDlg.checkData() and edtDlg.beforeSave() and edtDlg.updReferral() and edtDlg.getRecord():
                    QtGui.QMessageBox.information(self, u'Успешно', u'Направление успешно изменено')
                    self.tblOutgoingReferrals.model().updateContents()
                else:
                    QtGui.QMessageBox.warning(self, u'Ошибка', u'При изменении направления возникли ошибки')

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblOutgoingReferrals_doubleClicked(self, index):
        self.on_btnEditOutgoingReferral_clicked()

    @QtCore.pyqtSlot()
    def on_btnFRefApply_clicked(self):
        db = QtGui.qApp.db
        tblRef = db.table('Referral')
        tblClient = db.table('Client')
        refFilters = [tblRef['deleted'].eq(0)]
        if self.chkFRefPeriod.isChecked():
            refFilters.append(tblRef['date'].ge(self.edtFRefBegDate.date()))
            refFilters.append(tblRef['date'].le(self.edtFRefEndDate.date()))
        if self.chkFRefNumber.isChecked():
            refFilters.append(tblRef['number'].eq(self.edtFRefNumber.text()))
        if self.chkFRefType.isChecked():
            refFilters.append(tblRef['type'].eq(self.cmbFRefType.value()))
        if self.chkFRefRelegateMO.isChecked():
            refFilters.append(tblRef['relegateOrg_id'].eq(self.cmbFRefRelegateMO.value()))
        if self.chkFRefOnlyWithoutEvents.isChecked():
            refFilters.append(tblRef['event_id'].isNull())
        if self.chkFRefOnlyAnnulated.isChecked():
            refFilters.append(tblRef['isCancelled'].eq(1))
        if self.chkFRefOrgStructure.isChecked():
            refFilters.append(tblRef['orgStructure'].eq(self.cmbFRefOrgStructure.value()))
        if self.chkFRefClientId.isChecked():
            refFilters.append(tblRef['client_id'].eq(self.edtFRefClientId.text()))
        if self.chkFRefClientFirstName.isChecked():
            refFilters.append(tblClient['firstName'].eq(self.edtFRefClientFirstName.text()))
        if self.chkFRefClientLastName.isChecked():
            refFilters.append(tblClient['lastName'].eq(self.edtFRefClintLastName.text()))
        if self.chkFRefClientPatrName.isChecked():
            refFilters.append(tblClient['patrName'].eq(self.edtFRefClientPatrName.text()))
        if self.chkFRefClientBirthdate.isChecked():
            refFilters.append(tblClient['birthDate'].eq(forceDate(self.edtFRefClientBirthdate.date())))
        if self.tabWgtReferrals.currentIndex() == self.tabWgtReferrals.indexOf(self.tabInputReferrals):
            self.modelInputReferrals.setFilter(refFilters + [tblRef['isSend'].eq(0)])
        else:
            self.modelOutgoingReferrals.setFilter(refFilters + [tblRef['isSend'].eq(1)])
        self.updateRefCount()

    @QtCore.pyqtSlot()
    def on_btnFRefCancel_clicked(self):
        self.chkFRefPeriod.setChecked(False)
        self.chkFRefNumber.setChecked(False)
        self.chkFRefType.setChecked(False)
        self.chkFRefRelegateMO.setChecked(False)
        self.chkFRefOrgStructure.setChecked(False)
        self.chkFRefClientId.setChecked(False)
        self.chkFRefClientLastName.setChecked(False)
        self.chkFRefClientFirstName.setChecked(False)
        self.chkFRefClientPatrName.setChecked(False)
        self.chkFRefClientBirthdate.setChecked(False)
        self.chkFRefOnlyWithoutEvents.setChecked(False)
        self.chkFRefOnlyAnnulated.setChecked(False)
        self.edtFRefBegDate.setEnabled(False)
        self.edtFRefEndDate.setEnabled(False)
        self.edtFRefNumber.setEnabled(False)
        self.cmbFRefType.setEnabled(False)
        self.cmbFRefRelegateMO.setEnabled(False)
        self.cmbFRefOrgStructure.setEnabled(False)
        self.edtFRefClientId.setEnabled(False)
        self.edtFRefClintLastName.setEnabled(False)
        self.edtFRefClientFirstName.setEnabled(False)
        self.edtFRefClientPatrName.setEnabled(False)
        self.edtFRefClientBirthdate.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefPeriod_clicked(self, clicked):
        self.edtFRefBegDate.setEnabled(clicked)
        self.edtFRefEndDate.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefNumber_clicked(self, clicked):
        self.edtFRefNumber.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefType_clicked(self, clicked):
        self.cmbFRefType.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefRelegateMO_clicked(self, clicked):
        self.cmbFRefRelegateMO.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefOrgStructure_clicked(self, clicked):
        self.cmbFRefOrgStructure.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefClientId_clicked(self, clicked):
        self.edtFRefClientId.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefClientFirstName_clicked(self, clicked):
        self.edtFRefClientFirstName.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefClientLastName_clicked(self, clicked):
        self.edtFRefClintLastName.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefClientPatrName_clicked(self, clicked):
        self.edtFRefClientPatrName.setEnabled(clicked)

    @QtCore.pyqtSlot(bool)
    def on_chkFRefClientBirthdate_clicked(self, clicked):
        self.edtFRefClientBirthdate.setEnabled(clicked)

    ##############################

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblQueue_doubleClicked(self, index):
        if QtGui.qApp.doubleClickQueueClient() == 1:
            self.on_actAmbCreateEvent_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 2:
            self.on_actAmbChangeNotes_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 3:
            self.on_actAmbPrintOrder_triggered()
        elif QtGui.qApp.doubleClickQueueClient() == 4:
            self.on_actJumpQueuePosition_triggered()

    @QtCore.pyqtSlot()
    def on_actJumpQueuePosition_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            item = self.modelQueue.items()[row]
            actionId = forceRef(item.value('id'))
            if actionId:
                QtGui.qApp.callWithWaitCursor(self, self.showQueuePosition, actionId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblVisitByQueue_doubleClicked(self, index):
        index = self.tblVisitByQueue.currentIndex()
        if index.isValid():
            row = index.row()
            eventId = forceRef(self.modelVisitByQueue.items()[row].value('event_id'))
            if eventId:
                editEvent(self, eventId)
                self.focusEvents()

    @QtCore.pyqtSlot()
    def on_actEditClient_triggered(self):
        self.editCurrentClient()
        self.focusClients()

    @QtCore.pyqtSlot()
    def on_actEditLocationCard_triggered(self):
        self.updateLocationCardType()

    @QtCore.pyqtSlot()
    def on_actEditStatusObservationClient_triggered(self):
        self.updateStatusObservationClient()

    def updateLocationCardType(self):
        try:
            clientId = self.currentClientId()
            if clientId:
                if QtGui.qApp.userHasAnyRight([urAdmin, urEditLocationCard]):
                    dialog = CLocationCardTypeEditor(self, clientId)
                    if dialog.exec_():
                        self.updateRegistryContent(clientId)
        except:
            pass

    def updateStatusObservationClient(self):
        try:
            clientId = self.currentClientId()
            if clientId:
                if QtGui.qApp.userHasAnyRight([urAdmin, urEditStatusObservationClient]):
                    dialog = CStatusObservationClientEditor(self, clientId)
                    if dialog.exec_():
                        self.updateRegistryContent(clientId)
        except:
            pass

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        self.editCurrentClient()
        self.focusClients()

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        self.editNewClient()
        self.focusClients()

    @QtCore.pyqtSlot()
    def on_mnuPrint_aboutToShow(self):
        clientId = self.selectedClientId()
        if clientId:
            self.mnuPrint.setDefaultAction(self.actPrintClient)
            self.actPrintClient.setEnabled(True)
            printer = QtGui.qApp.labelPrinter()
            self.actPrintClientLabel.setEnabled(self.clientLabelTemplate is not None and bool(printer))
        else:
            self.actPrintClient.setEnabled(False)
            self.actPrintClientLabel.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_actPrintClient_printByTemplate(self, templateId):
        clientId = self.selectedClientId()
        if clientId:
            data = getClientContextData(clientId)
            QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_actPrintF30PRR_triggered(self):
        CReportF30PRR(self).exec_()

    @QtCore.pyqtSlot()
    def on_actInformationCost_triggered(self):
        CReportInformationCost(self, self.currentClientId()).exec_()

    @QtCore.pyqtSlot()
    def on_actPrintClientLabel_triggered(self):
        clientId = self.selectedClientId()
        printer = QtGui.qApp.labelPrinter()
        if clientId and self.clientLabelTemplate and printer:
            clientInfo = getClientInfo2(clientId)
            QtGui.qApp.call(self, directPrintTemplate, (self.clientLabelTemplate[1], {'client': clientInfo}, printer))

    @QtCore.pyqtSlot()
    def on_actPrintClientList_triggered(self):
        self.printConfigurableList(u'Список пациентов',
                                   self.registryWidget().viewWidget(),
                                   self.registryWidget().model(),
                                   self.getClientFilterAsText())
        self.focusClients()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_actFilterSocCard_triggered(self):
        QtGui.qApp.startProgressBar(4, u'Чтение карты...')
        self.processSocCard()
        QtGui.qApp.stopProgressBar()

    @QtCore.pyqtSlot()
    def on_actFilter_triggered(self):
        self.on_btnFilter_clicked()

    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        if isinstance(self.registryWidget(), CStandardRegistryWidget):
            for s in self.chkListOnClientsPage:
                chk = s[0]
                if chk.isChecked():
                    self.activateFilterWdgets(s[1])
                    return
            dfltChk = self.chkFilterBirthDay
            self.setChkFilterChecked(dfltChk, True)
        else:
            self.registryWidget().activateFiltersTab()

    @QtCore.pyqtSlot()
    def on_actScanBarcode_triggered(self):
        self.cmbFilterAccountingSystem.setValue(None)
        self.chkFilterId.setChecked(True)
        self.on_chkFilterId_clicked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterId_clicked(self, checked):
        self.onChkFilterClicked(self.chkFilterId, checked)
        if self.chkFilterLastName.isChecked():
            self.setChkFilterChecked(self.chkFilterLastName, False)
        if self.chkFilterFirstName.isChecked():
            self.setChkFilterChecked(self.chkFilterFirstName, False)
        if self.chkFilterPatrName.isChecked():
            self.setChkFilterChecked(self.chkFilterPatrName, False)
        if self.chkFilterBirthDay.isChecked():
            self.setChkFilterChecked(self.chkFilterBirthDay, False)
        if self.chkFilterSex.isChecked():
            self.setChkFilterChecked(self.chkFilterSex, False)
        if self.chkFilterContact.isChecked():
            self.setChkFilterChecked(self.chkFilterContact, False)
        if self.chkFilterSNILS.isChecked():
            self.setChkFilterChecked(self.chkFilterSNILS, False)
        if self.chkFilterIIN.isChecked():
            self.setChkFilterCheked(self.chkFilterIIN, False)
        if self.chkFilterDocument.isChecked():
            self.setChkFilterChecked(self.chkFilterDocument, False)
        if self.chkFilterPolicy.isChecked():
            self.setChkFilterChecked(self.chkFilterPolicy, False)
        if self.chkFilterAddress.isChecked():
            self.setChkFilterChecked(self.chkFilterAddress, False)
        if self.chkFilterWorkOrganisation.isChecked():
            self.setChkFilterChecked(self.chkFilterWorkOrganisation, False)
        if self.chkFilterHurtType.isChecked():
            self.setChkFilterChecked(self.chkFilterHurtType, False)
        if self.chkFilterLocationCardType.isChecked():
            self.setChkFilterChecked(self.chkFilterLocationCardType, False)
        if self.chkFilterStatusObservationType.isChecked():
            self.setChkFilterChecked(self.chkFilterStatusObservationType, False)
        if self.chkFilterCreatePerson.isChecked():
            self.setChkFilterChecked(self.chkFilterCreatePerson, False)
        if self.chkFilterCreateDate.isChecked():
            self.setChkFilterChecked(self.chkFilterCreateDate, False)
        if self.chkFilterModifyPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterModifyPerson, False)
        if self.chkFilterModifyDate.isChecked():
            self.setChkFilterChecked(self.chkFilterModifyDate, False)
        if self.chkFilterEvent.isChecked():
            self.setChkFilterChecked(self.chkFilterEvent, False)
        if self.chkFilterAge.isChecked():
            self.setChkFilterChecked(self.chkFilterAge, False)
        if self.chkFilterBirthYear.isChecked():
            self.setChkFilterChecked(self.chkFilterBirthYear, False)
        if self.chkFilterBirthMonth.isChecked():
            self.setChkFilterChecked(self.chkFilterBirthMonth, False)
        if self.chkFilterAddressOrgStructure.isChecked():
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)
        if self.chkFilterBeds.isChecked():
            self.setChkFilterChecked(self.chkFilterBeds, False)
        if self.chkFilterAddressIsEmpty.isChecked():
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)
        if self.chkFilterAttach.isChecked():
            self.setChkFilterChecked(self.chkFilterAttach, False)
        if self.chkFilterAttachType.isChecked():
            self.setChkFilterChecked(self.chkFilterAttach, False)
        if self.chkFilterAttachNonBase.isChecked():
            self.setChkFilterChecked(self.chkFilterAttachNonBase, False)
        if self.chkFilterTempInvalid.isChecked():
            self.setChkFilterChecked(self.chkFilterTempInvalid, False)
        if self.chkFilterRPFUnconfirmed.isChecked():
            self.setChkFilterChecked(self.chkFilterRPFUnconfirmed, False)
        if self.chkFilterRPFConfirmed.isChecked():
            self.setChkFilterChecked(self.chkFilterRPFConfirmed, False)
        if self.chkFilterSocStatuses.isChecked():
            self.setChkFilterChecked(self.chkFilterSocStatuses, False)
        if self.chkFilterContingentDD.isChecked():
            self.setChkFilterChecked(self.chkFilterContingentDD, False)
        if self.chkFilterShowDeads.isChecked():
            self.setChkFilterChecked(self.chkFilterShowDeads, False)
        if self.chkFilterMesEvents.isChecked():
            self.setChkFilterChecked(self.chkFilterMesEvents, False)
        if self.chkEventLID.isChecked():
            self.setChkFilterChecked(self.chkEventLID, False)
        if self.chkClientExamPlan.isChecked():
            self.setChkFilterChecked(self.chkClientExamPlan, False)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterSocStatClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbFilterSocStatClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbFilterSocStatType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAccountingSystem_currentIndexChanged(self, index):
        self.edtFilterId.setValidator(None)
        if self.cmbFilterAccountingSystem.value():
            self.edtFilterId.setValidator(None)
        else:
            self.edtFilterId.setValidator(self.idValidator)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterLastName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterFirstName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterSocStatuses_clicked(self, checked):
        if self.chkFilterSocStatuses.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterContingentDD_clicked(self, checked):
        if self.chkFilterContingentDD.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterPatrName_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterBirthDay_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAge, False)
            self.setChkFilterChecked(self.chkFilterBirthYear, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterSex_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterContact_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterSNILS_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterIIN_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterShowDeads_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterMesEvents_clicked(self, checked):
        if self.chkFilterMesEvents.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterDocument_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterPolicy_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFilterPolicySerial_textEdited(self, text):
        self.cmbFilterPolicyInsurer.setSerialFilter(text)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterWorkOrganisation_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterHurtType_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterLocationCardType_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterStatusObservationType_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreatePerson_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreateDate_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyPerson_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyDate_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEvent_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAge_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterBirthDay, False)
            self.setChkFilterChecked(self.chkFilterBirthYear, False)
            self.stkFilterAges.setCurrentIndex(1)
        elif not self.chkFilterBirthYear.isChecked():
            self.stkFilterAges.setCurrentIndex(0)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterBirthYear_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAge, False)
            self.setChkFilterChecked(self.chkFilterBirthDay, False)
            self.stkFilterAges.setCurrentIndex(2)
        elif not self.chkFilterAge.isChecked():
            self.stkFilterAges.setCurrentIndex(0)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAgeYearDisabled_clicked(self, checked):
        if checked:
            self.stkFilterAges.setCurrentIndex(0)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterBirthMonth_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)

    @QtCore.pyqtSlot()
    def on_btnFilterAttachOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbFilterAttachOrganisation.value(), False)
        self.cmbFilterAttachOrganisation.update()
        if orgId:
            self.cmbFilterAttachOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddress_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAddressCity_currentIndexChanged(self, index):
        code = self.cmbFilterAddressCity.code()
        self.cmbFilterAddressStreet.setCity(code)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddressOrgStructure_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddressIsEmpty, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterBeds_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddressIsEmpty_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddress, False)
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttach_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAttachNonBase, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttachType_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAttachNonBase_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAttach, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterTempInvalid_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterRPFUnconfirmed_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterRPFConfirmed, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterRPFConfirmed_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterRPFUnconfirmed, False)

    @QtCore.pyqtSlot(bool)
    def on_chkClientExamPlan_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxClient_clicked(self, button):
        buttonCode = self.buttonBoxClient.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxClient_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxClient_reset()

    def on_buttonBoxClient_apply(self):
        filter = {}
        if self.chkFilterId.isChecked():
            accountingSystemId = self.cmbFilterAccountingSystem.value()
            clientId = forceStringEx(self.edtFilterId.text())
            if not accountingSystemId:
                clientId = parseClientId(clientId)
            if clientId:
                filter['id'] = clientId
                filter['accountingSystemId'] = accountingSystemId

        if self.chkFilterLastName.isChecked():
            tmp = forceStringEx(self.edtFilterLastName.text())
            if tmp:
                filter['lastName'] = tmp
        if self.chkFilterFirstName.isChecked():
            tmp = forceStringEx(self.edtFilterFirstName.text())
            if tmp:
                filter['firstName'] = tmp
        if self.chkFilterPatrName.isChecked():
            tmp = forceStringEx(self.edtFilterPatrName.text())
            if tmp:
                filter['patrName'] = tmp
        if self.chkFilterBirthDay.isChecked():
            filter['birthDate'] = self.edtFilterBirthDay.date()
        if self.chkFilterSex.isChecked():
            filter['sex'] = self.cmbFilterSex.currentIndex()
        if self.chkFilterContact.isChecked():
            contact = forceStringEx(self.edtFilterContact.text())
            if contact:
                filter['contact'] = contact
        if self.chkFilterSNILS.isChecked():
            tmp = forceStringEx(forceString(self.edtFilterSNILS.text()).replace('-', '').replace(' ', ''))
            filter['SNILS'] = tmp
        if self.chkFilterIIN.isChecked():
            tmp = forceStringEx(self.edtFilterIIN.text())
            filter['IIN'] = tmp
        if self.chkFilterDocument.isChecked():
            typeId = self.cmbFilterDocumentType.value()
            serial = forceStringEx(self.edtFilterDocumentSerial.text())
            number = forceStringEx(self.edtFilterDocumentNumber.text())
            filter['doc'] = (typeId, serial, number)
        if self.chkFilterPolicy.isChecked():
            policyType = self.cmbFilterPolicyType.value()
            insurerId = self.cmbFilterPolicyInsurer.value()
            serial = forceStringEx(self.edtFilterPolicySerial.text())
            number = forceStringEx(self.edtFilterPolicyNumber.text())
            filter['policy'] = (policyType, insurerId, serial, number)
        if self.chkFilterWorkOrganisation.isChecked():
            filter['orgId'] = self.cmbWorkOrganisation.value()
        if self.chkFilterHurtType.isChecked():
            filter['hurtType'] = self.cmbFilterHurtType.value()
        if self.chkFilterSocStatuses.isChecked():
            filter['socStatType_id'] = self.cmbFilterSocStatType.value()
            filter['socStatClass_id'] = self.cmbFilterSocStatClass.value()
        if self.chkFilterLocationCardType.isChecked():
            filter['locationCardType'] = self.cmbFilterLocationCardType.value()
        if self.chkFilterStatusObservationType.isChecked():
            filter['statusObservationType'] = self.cmbFilterStatusObservationType.value()
        if self.chkFilterCreatePerson.isChecked():
            filter['createPersonIdEx'] = self.cmbFilterCreatePerson.value()
        if self.chkFilterCreateDate.isChecked():
            filter['begCreateDateEx'] = self.edtFilterBegCreateDate.date()
            filter['endCreateDateEx'] = self.edtFilterEndCreateDate.date()
        if self.chkFilterModifyPerson.isChecked():
            filter['modifyPersonIdEx'] = self.cmbFilterModifyPerson.value()
        if self.chkFilterModifyDate.isChecked():
            filter['begModifyDateEx'] = self.edtFilterBegModifyDate.date()
            filter['endModifyDateEx'] = self.edtFilterEndModifyDate.date()
        if self.chkFilterEvent.isChecked():
            filter['event'] = (self.chkFilterFirstEvent.isChecked(),
                               self.edtFilterEventBegDate.date(),
                               self.edtFilterEventEndDate.date())
        if self.chkFilterAge.isChecked():
            filter['age'] = ((self.edtFilterBegAge.value(), self.cmbFilterBegAge.currentIndex()),
                             (self.edtFilterEndAge.value() + 1, self.cmbFilterEndAge.currentIndex())
                             )
        if self.chkFilterBirthYear.isChecked():
            filter['birthYear'] = (self.edtFilterBegBirthYear.value(), self.edtFilterEndBirthYear.value())
        if self.chkFilterBirthMonth.isChecked():
            filter['birthMonth'] = self.cmbFilterBirthMonth.currentIndex() + 1
        if self.chkFilterAddress.isChecked() and self.chkFilterAddressOrgStructure.isChecked():
            filter['address'] = (self.cmbFilterAddressType.currentIndex(),
                                 self.cmbFilterAddressCity.code(),
                                 self.cmbFilterAddressStreet.code(),
                                 self.edtFilterAddressHouse.text(),
                                 self.edtFilterAddressCorpus.text(),
                                 self.edtFilterAddressFlat.text()
                                 )
            filter['addressOrgStructure'] = (self.cmbFilterAddressOrgStructureType.currentIndex(),
                                             self.cmbFilterAddressOrgStructure.value()
                                             )
        elif self.chkFilterAddress.isChecked():
            filter['address'] = (self.cmbFilterAddressType.currentIndex(),
                                 self.cmbFilterAddressCity.code(),
                                 self.cmbFilterAddressStreet.code(),
                                 self.edtFilterAddressHouse.text(),
                                 self.edtFilterAddressCorpus.text(),
                                 self.edtFilterAddressFlat.text()
                                 )
        elif self.chkFilterAddressOrgStructure.isChecked():
            filter['addressOrgStructure'] = (self.cmbFilterAddressOrgStructureType.currentIndex(),
                                             self.cmbFilterAddressOrgStructure.value()
                                             )
        elif self.chkFilterAddressIsEmpty.isChecked():
            filter['addressIsEmpty'] = True
        if self.chkFilterBeds.isChecked():
            filter['beds'] = (self.cmbFilterStatusBeds.currentIndex(),
                              self.cmbFilterOrgStructureBeds.value()
                              )
        if self.chkFilterAttach.isChecked():
            filter['attachTo'] = self.cmbFilterAttachOrganisation.value()
        elif self.chkFilterAttachNonBase.isChecked():
            filter['attachToNonBase'] = True
        if self.chkFilterAttachType.isChecked():
            filter['attachType'] = (self.cmbFilterAttachCategory.currentIndex(),
                                    self.cmbFilterAttachType.value())
        if self.chkFilterTempInvalid.isChecked():
            filter['tempInvalid'] = (self.edtFilterBegTempInvalid.date(),
                                     self.edtFilterEndTempInvalid.date()
                                     )
        if self.chkFilterRPFUnconfirmed.isChecked():
            filter['RPFUnconfirmed'] = True
        elif self.chkFilterRPFConfirmed.isChecked():  # atronah: РПФ - регистр периодов финансирования (согласно документаци ПО «ЕИС ОМС. ВМУ. АПУ. Учёт пациентов»)
            filter['RPFConfirmed'] = (self.edtFilterBegRPFConfirmed.date(),
                                      self.edtFilterEndRPFConfirmed.date()
                                      )
        if self.chkFilterContingentDD.isChecked():
            filter['contingentDD'] = self.cmbFilterContingentDD.currentIndex()

        if self.chkFilterMKBRange_Client.isChecked():
            filter['MKBBottom'] = self.edtFilterMKBBottom_Client.text()
            filter['MKBTop'] = self.edtFilterMKBTop_Client.text()
            filter['diagnosisTypeId'] = self.cmbFilterEventDiagnosisType_Client.value()

        if self.chkFilterShowDeads.isChecked():
            filter['showDeads'] = True

        if self.chkClientExamPlan.isChecked():
            filter['clientExamPlanKind'] = self.cmbClientExamPlanKind.value()
            filter['clientExamPlanYear'] = self.cmbClientExamPlanYear.value()
            filter['clientExamPlanQuarter'] = self.cmbClientExamPlanQuarter.value()

        filter['onlyStaff'] = self.chkShowStaffOnly.isChecked()
        filter['isUnconscious'] = self.chkUnconscious.isChecked()
        filter['oncologyForm90'] = self.chkOncologyForm90.isChecked()
        self.__filter = filter
        self.updateRegistryContent()
        self.focusClients()

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAttachCategory_currentIndexChanged(self, index):
        self.setupCmbFilterAttachTypeCategory(index)

    def on_buttonBoxClient_reset(self):
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)

    @QtCore.pyqtSlot()
    def on_actEventEditClient_triggered(self):
        clientId = self.currentClientId()
        if not clientId:
            clientId = self.selectedClientId()
        if clientId:
            self.editClient(clientId)
            self.updateEventInfo(self.currentEventId())
            self.updateClientsListRequest = True

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelEvents_currentRowChanged(self, current, previous):
        eventId = self.eventId(current)
        self.updateEventInfo(eventId)
        Logger.logEventChoice(login_id=Logger.loginId, event_Id=eventId)

    @QtCore.pyqtSlot(int)
    def on_modelEvents_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblEventsCount.setText(formatRecordsCount(count) + infoBeds + infoAddressOrgStructure)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblEvents_doubleClicked(self, index):
        self.on_btnEventEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnEventEdit_clicked(self):
        eventId = self.currentEventId()
        if eventId:
            editEvent(self, eventId)
        else:
            self.requestNewEvent()
        self.focusEvents()

    @QtCore.pyqtSlot()
    def on_btnEventNew_clicked(self):
        self.requestNewEvent()
        self.focusEvents()

    @QtCore.pyqtSlot()
    def on_actEventPrint_triggered(self):
        self.printConfigurableList(u'Список обращений',
                                   self.tblEvents,
                                   self.modelEvents,
                                   self.getEventFilterAsText())
        self.focusEvents()

    @QtCore.pyqtSlot(int)
    def on_actEventListPrintTemplate_printByTemplate(self, templateId):
        context = CInfoContext()
        data = {'events': [context.getInstance(CEventInfo, eventId) for eventId in self.modelEvents.idList()]}
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    def getEventInfo(self, context):
        eventId = self.currentEventId()
        return context.getInstance(CEventInfo, eventId)

    @QtCore.pyqtSlot(int)
    def on_btnEventPrint_printByTemplate(self, templateId):
        data = getEventContextData(self)
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_btnEventFilter_clicked(self):
        for s in self.chkListOnEventsPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterEventType
        self.setChkFilterChecked(dfltChk, True)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventSetDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventNextDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventEmptyExecDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventExecDate, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventExecDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventEmptyExecDate, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPurpose_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()
            self.setCmbFilterEventTypeFilter(self.cmbFilterEventPurpose.value())
        else:
            self.setCmbFilterEventTypeFilter(None)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventPurpose_currentIndexChanged(self, index):
        self.setCmbFilterEventTypeFilter(self.cmbFilterEventPurpose.value())
        self.updateFilterEventResultTable()

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()

    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventType_currentIndexChanged(self, index):
        self.updateFilterEventResultTable()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelFilterEventType_currentRowChanged(self, current, previous):
        self.updateFilterEventResultTable()

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventSpeciality_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterEventPerson.setSpecialityId(self.cmbFilterEventSpeciality.value())
        else:
            self.cmbFilterEventPerson.setSpecialityId(None)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventOrgStructure_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterEventPerson.setOrgStructureId(self.cmbFilterEventOrgStructure.value())
        else:
            if not self.chkFilterEventPerson.isChecked():
                self.cmbFilterEventPerson.setOrgStructureId(None)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventOrgStructure_currentIndexChanged(self, index):
        self.cmbFilterEventPerson.setOrgStructureId(self.cmbFilterEventOrgStructure.value())

    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventSpeciality_currentIndexChanged(self, index):
        self.cmbFilterEventPerson.setSpecialityId(self.cmbFilterEventSpeciality.value())

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if not self.chkFilterEventOrgStructure.isChecked():
            self.cmbFilterEventPerson.setOrgStructureId(QtGui.qApp.currentOrgStructureId())
        self.cmbFilterEventPerson.setOrgId(QtGui.qApp.currentOrgId())

    @QtCore.pyqtSlot(bool)
    def on_chkRelegateOrg_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventDispanserObserved_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventLPU_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            db = QtGui.qApp.db
            orgId = forceRef(db.translate('Event', 'id', self.currentEventId(), 'org_id'))
            self.cmbFilterEventLPU.setValue(orgId)
            self.cmbFilterEventPerson.setOrgId(orgId)
            self.setChkFilterChecked(self.chkFilterEventNonBase, False)
        else:
            self.cmbFilterEventLPU.setValue(None)
            self.cmbFilterEventPerson.setOrgId(None)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterEventLPU_currentIndexChanged(self, index):
        self.cmbFilterEventPerson.setOrgId(self.cmbFilterEventLPU.value())

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventNonBase_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        if checked:
            self.setChkFilterChecked(self.chkFilterEventLPU, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventMes_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventResult_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.updateFilterEventResultTable()

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventGoal_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventCreatePerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventCreateDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterVisits_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkPrimary_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventModifyPerson_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventModifyDate_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventPayStatus_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterVisitPayStatus_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkErrorInDiagnostic_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterMKBRange_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterMKBRange_Client_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterEventId_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if self.chkFilterEventCreatePerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventCreatePerson, False)
        if self.chkFilterEventCreateDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventCreateDate, False)
        if self.chkFilterEventModifyPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventModifyPerson, False)
        if self.chkFilterEventModifyDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventModifyDate, False)
        if self.chkErrorInDiagnostic.isChecked():
            self.setChkFilterChecked(self.chkErrorInDiagnostic, False)
        if self.chkFilterMKBRange.isChecked():
            self.setChkFilterChecked(self.chkFilterMKBRange, False)
        if self.chkFilterEventPayStatus.isChecked():
            self.setChkFilterChecked(self.chkFilterEventPayStatus, False)
        if self.chkFilterVisitPayStatus.isChecked():
            self.setChkFilterChecked(self.chkFilterVisitPayStatus, False)
        if self.chkFilterEventSetDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventSetDate, False)
        if self.chkFilterEventEmptyExecDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventEmptyExecDate, False)
        if self.chkFilterEventExecDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventExecDate, False)
        if self.chkFilterEventNextDate.isChecked():
            self.setChkFilterChecked(self.chkFilterEventNextDate, False)
        if self.chkFilterEventOrgStructure.isChecked():
            self.setChkFilterChecked(self.chkFilterEventOrgStructure, False)
        if self.chkFilterEventSpeciality.isChecked():
            self.setChkFilterChecked(self.chkFilterEventSpeciality, False)
        if self.chkFilterEventPerson.isChecked():
            self.setChkFilterChecked(self.chkFilterEventPerson, False)
        if self.chkRelegateOrg.isChecked():
            self.setChkFilterChecked(self.chkRelegateOrg, False)
        if self.chkFilterEventDispanserObserved.isChecked():
            self.setChkFilterChecked(self.chkFilterEventDispanserObserved, False)
        if self.chkFilterEventLPU.isChecked():
            self.setChkFilterChecked(self.chkFilterEventLPU, False)
        if self.chkFilterEventNonBase.isChecked():
            self.setChkFilterChecked(self.chkFilterEventNonBase, False)
        if self.chkFilterEventMes.isChecked():
            self.setChkFilterChecked(self.chkFilterEventMes, False)
        if self.chkFilterEventResult.isChecked():
            self.setChkFilterChecked(self.chkFilterEventResult, False)
        if self.chkFilterEventGoal.isChecked():
            self.setChkFilterChecked(self.chkFilterEventGoal, False)
        if self.chkFilterExternalId.isChecked():
            self.setChkFilterChecked(self.chkFilterExternalId, False)
        if self.chkFilterAccountSumLimit.isChecked():
            self.setChkFilterChecked(self.chkFilterAccountSumLimit, False)
        if self.chkFilterVisits.isChecked():
            self.setChkFilterChecked(self.chkFilterVisits, False)
        if self.chkPrimary.isChecked():
            self.setChkFilterChecked(self.chkPrimary, False)
        if self.chkFilterExposeConfirmed.isChecked():
            self.setChkFilterChecked(self.chkFilterExposeConfirmed, False)
        if self.chkFilterMesEvents.isChecked():
            self.setChkFilterChecked(self.chkFilterMesEvents, False)
        if self.chkEventLID.isChecked():
            self.setChkFilterChecked(self.chkEventLID, False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExternalId_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkEventLID_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkEventLID, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAccountSumLimit_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if self.cmbFilterAccountSumLimit.currentIndex() == 0:
            self.edtFilterSumLimitDelta.setValue(0)
            self.edtFilterSumLimitDelta.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAccountSumLimit_currentIndexChanged(self, index):
        if index == 0:
            self.edtFilterSumLimitDelta.setValue(0)
            self.edtFilterSumLimitDelta.setEnabled(False)
        else:
            self.edtFilterSumLimitDelta.setEnabled(True)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExposeConfirmed_clicked(self, checked):
        if self.chkFilterEventId.isChecked():
            self.setChkFilterChecked(self.chkFilterEventId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxEvent_clicked(self, button):
        buttonCode = self.buttonBoxEvent.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxEvent_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxEvent_reset()

    def on_buttonBoxEvent_reset(self):
        for s in self.chkListOnEventsPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)
        self.cmbFilterEventByClient.setCurrentIndex(0)

    def on_buttonBoxEvent_apply(self):
        filter = {}
        if self.chkFilterEventSetDate.isChecked():
            filter['begSetDate'] = self.edtFilterEventBegSetDate.date()
            filter['endSetDate'] = self.edtFilterEventEndSetDate.date()
        filter['emptyExecDate'] = self.chkFilterEventEmptyExecDate.isChecked()
        if self.chkFilterEventExecDate.isChecked():
            filter['begExecDate'] = self.edtFilterEventBegExecDate.date()
            filter['endExecDate'] = self.edtFilterEventEndExecDate.date()
        if self.chkFilterEventNextDate.isChecked():
            filter['begNextDate'] = self.edtFilterEventBegNextDate.date()
            filter['endNextDate'] = self.edtFilterEventEndNextDate.date()
        if self.chkFilterEventPurpose.isChecked():
            filter['eventPurposeId'] = self.cmbFilterEventPurpose.value()
        if self.chkFilterEventType.isChecked():
            filter['eventTypeId'] = self.lstFilterEventType.values() if self.chkFilterEventTypeMulti.isChecked() else [
                self.cmbFilterEventType.value()] if self.cmbFilterEventType.value() else []
        if self.chkFilterEventOrgStructure.isChecked():
            filter['orgStructureId'] = self.cmbFilterEventOrgStructure.value()
        if self.chkFilterEventSpeciality.isChecked():
            filter['specialityId'] = self.cmbFilterEventSpeciality.value()
        if self.chkFilterEventPerson.isChecked():
            filter['personId'] = self.cmbFilterEventPerson.value()
        if self.chkRelegateOrg.isChecked():
            filter['relegateOrgId'] = self.cmbRelegateOrg.value()
        if self.chkFilterEventGoal.isChecked():
            filter['goalRegionalCode'] = self.cmbFilterEventGoal.code()
        filter['dispanserObserved'] = self.chkFilterEventDispanserObserved.isChecked()
        if self.chkFilterEventLPU.isChecked():
            filter['LPUId'] = self.cmbFilterEventLPU.value()
        else:
            filter['nonBase'] = self.chkFilterEventNonBase.isChecked()
        filter['errorInDiagnostic'] = self.chkErrorInDiagnostic.isChecked()
        if self.chkFilterMKBRange.isChecked():
            filter['MKBBottom'] = self.edtFilterMKBBottom.text()
            filter['MKBTop'] = self.edtFilterMKBTop.text()
            filter['diagnosisTypeId'] = self.cmbFilterEventDiagnosisType.value()
        if self.chkFilterEventMes.isChecked():
            filter['mesCode'] = forceStringEx(self.edtFilterEventMes.text())
        if self.chkFilterEventResult.isChecked():
            filter['eventResultId'] = self.cmbFilterEventResult.value()

        if self.chkFilterEventCreatePerson.isChecked():
            filter['createPersonId'] = self.cmbFilterEventCreatePerson.value()
        if self.chkFilterEventCreateDate.isChecked():
            filter['begCreateDate'] = self.edtFilterEventBegCreateDate.date()
            filter['endCreateDate'] = self.edtFilterEventEndCreateDate.date()
        if self.chkFilterEventModifyPerson.isChecked():
            filter['modifyPersonId'] = self.cmbFilterEventModifyPerson.value()
        if self.chkFilterEventModifyDate.isChecked():
            filter['begModifyDate'] = self.edtFilterEventBegModifyDate.date()
            filter['endModifyDate'] = self.edtFilterEventEndModifyDate.date()
        if self.chkFilterEventPayStatus.isChecked():
            filter['payStatusCode'] = self.cmpFilterEventPayStatusCode.currentIndex()
            index = self.cmbFilterEventPayStatusFinance.currentIndex()
            if not 0 <= index < 5:
                index = 0
            filter['payStatusFinanceCode'] = 5 - index
        if self.chkFilterVisitPayStatus.isChecked():
            filter['payStatusCodeVisit'] = self.cmpFilterVisitPayStatusCode.currentIndex()
            index = self.cmbFilterVisitPayStatusFinance.currentIndex()
            if not 0 <= index < 5:
                index = 0
            filter['payStatusFinanceCodeVisit'] = 5 - index
        if self.chkFilterMesEvents.isChecked():
            filter['mesEvents'] = self.cmbFilterMesEvents.currentIndex()
        if self.chkFilterEventId.isChecked():
            tmp = forceStringEx(self.edtFilterEventId.text())
            if tmp:
                filter['id'] = int(tmp)
        if self.chkFilterExternalId.isChecked():
            filter['maskExternalId'] = self.chkFilterMaskExternalId.isChecked()
            tmpExternalId = forceStringEx(self.edtFilterExternalId.text())
            if tmpExternalId:
                filter['externalId'] = tmpExternalId
        if self.chkFilterAccountSumLimit.isChecked():
            filter['accountSumLimit'] = forceInt(self.cmbFilterAccountSumLimit.currentIndex())
            filter['sumLimitFrom'] = forceInt(self.edtFilterSumLimitFrom.value())
            filter['sumLimitTo'] = forceInt(self.edtFilterSumLimitTo.value())
            filter['sumLimitDelta'] = forceInt(self.edtFilterSumLimitDelta.value())
        if self.chkFilterVisits.isChecked():
            filter['visitScene'] = self.cmbFilterVisitScene.value()
            filter['visitType'] = self.cmbFilterVisitType.value()
            filter['visitProfile'] = self.cmbFilterVisitProfile.value()
            filter['visitPersonId'] = self.cmbFilterVisitPerson.value()
        if self.chkPrimary.isChecked():
            filter['visits'] = self.cmpPrimary.currentIndex()
        filterEventByClient = self.cmbFilterEventByClient.currentIndex()
        if filterEventByClient == 0:
            filter['clientIds'] = [self.selectedClientId()]
        elif filterEventByClient == 1:
            filter['clientIds'] = self.registryWidget().model().idList()
        filter['filterEventByClient'] = filterEventByClient
        if self.chkFilterExposeConfirmed.isChecked():
            filter['exposeConfirmed'] = self.cmbFilterExposeConfirmed.currentIndex()
        if self.chkEventLID.isChecked():
            filter['LID'] = self.edtEventLID.text()
        self.updateEventsList(filter)
        self.focusEvents()

    @QtCore.pyqtSlot()
    def on_actAmbCardEditClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            self.updateAmbCardInfo()
            self.updateClientsListRequest = True

    @QtCore.pyqtSlot()
    def on_actActionEditClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            actionId = self.tblActionsStatus.currentItemId()
            self.updateActionInfo(actionId)
            self.updateClientsListRequest = True

    @QtCore.pyqtSlot(int)
    def on_tabWidgetActionsClasses_currentChanged(self, index):
        self.cmbFilterActionType.setClass(index)
        self.cmbFilterActionType.setValue(self.__actionTypeIdListByClassPage[index])
        self.on_buttonBoxAction_apply()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsStatus_currentRowChanged(self, current, previous):
        actionId = self.tblActionsStatus.currentItemId()
        self.updateActionInfo(actionId)
        self.tabAmbCardContent.updateAmbCardPropertiesTable(current, self.tblActionsStatusProperties)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsDiagnostic_currentRowChanged(self, current, previous):
        actionId = self.tblActionsDiagnostic.currentItemId()
        self.updateActionInfo(actionId)
        self.tabAmbCardContent.updateAmbCardPropertiesTable(current, self.tblActionsDiagnosticProperties)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsCure_currentRowChanged(self, current, previous):
        actionId = self.tblActionsCure.currentItemId()
        self.updateActionInfo(actionId)
        self.tabAmbCardContent.updateAmbCardPropertiesTable(current, self.tblActionsCureProperties)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsMisc_currentRowChanged(self, current, previous):
        actionId = self.tblActionsMisc.currentItemId()
        self.updateActionInfo(actionId)
        self.tabAmbCardContent.updateAmbCardPropertiesTable(current, self.tblActionsMiscProperties)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActionsAnalyses_currentRowChanged(self, current, previous):
        actionId = self.tblActionsAnalyses.currentItemId()
        self.updateActionInfo(actionId)
        self.tabAmbCardContent.updateAmbCardPropertiesTable(current, self.tblActionsAnalysesProperties)

    @QtCore.pyqtSlot(int)
    def on_modelActionsStatus_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblActionsStatusCount.setText(formatRecordsCount(count) + infoBeds + infoAddressOrgStructure)
        self.lblActionsStatusAmountSum.setText(u'Количество: %.2f' % self.modelActionsStatus.getAmountSum())

    @QtCore.pyqtSlot(int)
    def on_modelActionsDiagnostic_itemsCountChanged(self, count):
        self.lblActionsDiagnosticCount.setText(formatRecordsCount(count))
        self.lblActionsDiagnosticAmountSum.setText(u'Количество: %.2f' % self.modelActionsDiagnostic.getAmountSum())

    @QtCore.pyqtSlot(int)
    def on_modelActionsCure_itemsCountChanged(self, count):
        self.lblActionsCureCount.setText(formatRecordsCount(count))
        self.lblActionsCureAmountSum.setText(u'Количество: %.2f' % self.modelActionsCure.getAmountSum())

    @QtCore.pyqtSlot(int)
    def on_modelActionsMisc_itemsCountChanged(self, count):
        self.lblActionsMiscCount.setText(formatRecordsCount(count))
        self.lblActionsMiscAmountSum.setText(u'Количество: %.2f' % self.modelActionsMisc.getAmountSum())

    @QtCore.pyqtSlot(int)
    def on_modelActionsAnalyses_itemsCountChanged(self, count):
        self.lblActionsAnalysesCount.setText(formatRecordsCount(count))
        self.lblActionsAnalysesAmountSum.setText(u'Количество: %.2f' % self.modelActionsAnalyses.getAmountSum())

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsStatus_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsDiagnostic_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsCure_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsMisc_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblActionsAnalyses_doubleClicked(self, index):
        self.on_btnActionEdit_clicked()

    @QtCore.pyqtSlot()
    def on_actTransferHospitalization_triggered(self):
        eventId = self.tblEvents.currentItemId()
        if eventId:
            dialog = CHospitalizationTransferDialog(self, eventId)
            dialog.exec_()

    @QtCore.pyqtSlot()
    def on_actRecreateEventWithAnotherType_triggered(self):
        eventId = self.tblEvents.currentItemId()
        if not eventId:
            return
        db = QtGui.qApp.db
        tblEvent = db.table('Event')

        # FIXME:skkachaev: мы можем получить это не обращаясь к базе?
        record = db.getRecordEx(tblEvent,
                                'execPerson_id, externalId, setDate, execDate',
                                'id = %i' % eventId)
        personId = forceRef(record.value('execPerson_id'))
        externalId = forceStringEx(record.value('externalId'))
        begDate = forceDateTime(record.value('setDate'))
        endDate = forceDateTime(record.value('execDate'))

        # Условия при которых менять тип события запрещено
        # i4301
        # TODO: pirozhok: отговорить юзеров пользоваться этим

        hasAccountMsg = u'Смена типа события невозможна в связи с тем, что счет на услуги выставлен.'
        hasTTJMsg = u'Смена типа события невозможна в связи с тем, что биоматериал уже зарегистрирован.'
        disclaimer = u'\nВНИМАНИЕ! Данный функционал необходимо использовать только в экстренных случаях. ' \
                     u'Смена типа события может привести к ошибкам в работе системы.'

        hasAccount = forceRef(db.translateEx('Account_Item', 'event_id', eventId, 'id')) is not None
        hasTTJ = forceRef(db.getRecordEx(
            'Action', 'id', ['event_id = %i' % eventId, 'takenTissueJournal_id IS NOT NULL']
        )) is not None

        if hasAccount and hasTTJ:
            msg = u'\n'.join([hasAccountMsg, hasTTJMsg, disclaimer])
        elif hasAccount:
            msg = u'\n'.join([hasAccountMsg, disclaimer])
        elif hasTTJ:
            msg = u'\n'.join([hasTTJMsg, disclaimer])
        else:
            msg = disclaimer

        QtGui.QMessageBox.warning(self, u'Предупреждение', msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        if (hasTTJ and not QtGui.qApp.userHasRight(urAdmin)) or hasAccount:
            return

        self.requestNewEvent(
            moveEventId=eventId, personId=personId, externalId=externalId, begDate=begDate, endDate=endDate
        )
        self.focusEvents()
        self.on_buttonBoxEvent_apply()

    @QtCore.pyqtSlot()
    def on_actOpenAccountingByEvent_triggered(self):
        eventId = self.tblEvents.currentItemId()
        self.showAccountingDialog(eventId)

    @QtCore.pyqtSlot()
    def on_actOpenAccountingByAction_triggered(self):
        actionId = self.tblEventActions.currentItemId()
        self.showAccountingDialog(None, actionId)

    @QtCore.pyqtSlot()
    def on_actOpenAccountingByVisit_triggered(self):
        visitId = self.tblEventVisits.currentItemId()
        self.showAccountingDialog(None, None, visitId)

    @QtCore.pyqtSlot()
    def on_actEditActionEvent_triggered(self):
        self.on_btnActionEventEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnActionEventEdit_clicked(self):
        actionId = self.currentActionId()
        if actionId:
            eventId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'event_id'))
            if eventId:
                if editEvent(self, eventId):
                    self.on_buttonBoxAction_apply()
        self.focusActions()

    @QtCore.pyqtSlot()
    def on_btnActionEdit_clicked(self):
        actionId = self.currentActionId()
        if actionId:
            self.editAction(actionId)
        self.focusActions()

    @QtCore.pyqtSlot()
    def on_btnActionPrint_clicked(self):
        tblActions = self.getCurrentActionsTable()
        tblActions.setReportHeader(u'Список мероприятий')
        tblActions.setReportDescription(self.getActionFilterAsText())
        tblActions.printContent()
        self.focusActions()

    @QtCore.pyqtSlot()
    def on_btnActionFilter_clicked(self):
        for s in self.chkListOnActionsPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterActionType
        self.setChkFilterChecked(dfltChk, True)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if not checked or not self.chkTakeIntoAccountProperty.isChecked():
            self.enabledOptionProperty(checked)
            self.setChkFilterChecked(self.chkListProperty, False)
            self.chkListProperty.setEnabled(False)
            self.tblListOptionProperty.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def on_chkThresholdPenaltyGrade_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkListProperty_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        actionTypeId = forceRef(self.cmbFilterActionType.value())
        self.enabledOptionProperty(checked, actionTypeId)

    def enabledOptionProperty(self, checked, actionTypeId=None):
        if actionTypeId and checked:
            self.bufferRecordsOptionProperty = []
            self.tblListOptionProperty.setEnabled(True)
            QtGui.qApp.callWithWaitCursor(self, self.printDataOptiontPropertys, actionTypeId)
        else:
            self.bufferRecordsOptionProperty = []
            self.tblListOptionProperty.selectAll()
            self.tblListOptionProperty.clear()
            self.tblListOptionProperty.setEnabled(False)

    def printDataOptiontPropertys(self, typeActionId=None):
        self.bufferRecordsOptionProperty = []
        self.rows = 0
        if typeActionId:
            db = QtGui.qApp.db
            table = db.table('ActionPropertyType')
            cols = [table['id'], table['name']]
            cond = [table['actionType_id'].eq(typeActionId)]
            records = db.getRecordList(table, cols, cond, u'name')
            for record in records:
                nameProperty = u''
                self.bufferRecordsOptionProperty.append(record)
                nameProperty = forceString(record.value('name'))
                self.tblListOptionProperty.addItem(CFilterPropertyOptionsItem(nameProperty, self.tblListOptionProperty))
                item = self.tblListOptionProperty.item(self.rows)
                self.tblListOptionProperty.scrollToItem(item)
                self.rows += 1

    def getDataOptionPropertyChecked(self):
        optionPropertyIdList = []
        rowCount = self.tblListOptionProperty.count() - 1
        while rowCount >= 0:
            optionPropertyItem = self.tblListOptionProperty.item(rowCount)
            if optionPropertyItem:
                if optionPropertyItem.checkState() == QtCore.Qt.Checked:
                    record = self.bufferRecordsOptionProperty[rowCount]
                    optionPropertyIdList.append(forceRef(record.value('id')))
            rowCount -= 1
        return optionPropertyIdList

    @QtCore.pyqtSlot(bool)
    def on_chkFilledProperty_clicked(self, checked):
        if checked:
            self.setChkFilterChecked(self.chkThresholdPenaltyGrade, False)
            self.chkThresholdPenaltyGrade.setEnabled(False)
            self.edtThresholdPenaltyGrade.setEnabled(False)
        elif self.chkTakeIntoAccountProperty.isChecked():
            self.chkThresholdPenaltyGrade.setEnabled(True)

    @QtCore.pyqtSlot(bool)
    def on_chkTakeIntoAccountProperty_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if not checked or not self.chkFilterActionType.isChecked():
            self.enabledOptionProperty(checked)
            self.setChkFilterChecked(self.chkListProperty, False)
            self.chkListProperty.setEnabled(False)
            self.tblListOptionProperty.setEnabled(False)
        elif checked and self.chkFilterActionType.isChecked():
            self.chkListProperty.setEnabled(True)
        if not self.chkThresholdPenaltyGrade.isChecked():
            self.edtThresholdPenaltyGrade.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterActionType_currentIndexChanged(self, index):
        index = self.tabWidgetActionsClasses.currentIndex()
        self.__actionTypeIdListByClassPage[index] = self.cmbFilterActionType.value()
        actionTypeId = forceRef(self.cmbFilterActionType.value())
        self.enabledOptionProperty(self.chkListProperty.isChecked(), actionTypeId)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetSpeciality_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterActionSetPerson.setSpecialityId(self.cmbFilterActionSetSpeciality.value())
        else:
            self.cmbFilterActionSetPerson.setSpecialityId(None)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExecSetSpeciality_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.cmbFilterExecSetPerson.setSpecialityId(self.cmbFilterExecSetSpeciality.value())
        else:
            self.cmbFilterExecSetPerson.setSpecialityId(None)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterActionSetSpeciality_currentIndexChanged(self, index):
        self.cmbFilterActionSetPerson.setSpecialityId(self.cmbFilterActionSetSpeciality.value())

    @QtCore.pyqtSlot(int)
    def on_cmbFilterExecSetSpeciality_currentIndexChanged(self, index):
        self.cmbFilterExecSetPerson.setSpecialityId(self.cmbFilterExecSetSpeciality.value())

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionSetPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExecSetPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAssistant_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionPlannedEndDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionStatus_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionExecDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionCreatePerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionCreateDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionModifyPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionModifyDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionPayStatus_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterActionId_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxAction_clicked(self, button):
        buttonCode = self.buttonBoxAction.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxAction_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxAction_reset()

    def on_buttonBoxAction_reset(self):
        for s in self.chkListOnActionsPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)
        self.cmbFilterAction.setCurrentIndex(0)

    def on_buttonBoxAction_apply(self):
        filter = {}
        if self.chkFilterActionType.isChecked():
            filter['actionTypeId'] = self.cmbFilterActionType.value()
        if self.chkFilterActionStatus.isChecked():
            filter['status'] = self.cmbFilterActionStatus.currentIndex()
        if self.chkFilterActionSetDate.isChecked():
            filter['begSetDate'] = self.edtFilterActionBegSetDate.date()
            filter['endSetDate'] = self.edtFilterActionEndSetDate.date()
        if self.chkFilterActionSetSpeciality.isChecked():
            filter['setSpecialityId'] = self.cmbFilterActionSetSpeciality.value()
        if self.chkFilterActionSetPerson.isChecked():
            filter['setPersonId'] = self.cmbFilterActionSetPerson.value()
        if self.chkFilterExecSetSpeciality.isChecked():
            filter['execSpecialityId'] = self.cmbFilterExecSetSpeciality.value()
        if self.chkFilterExecSetPerson.isChecked():
            filter['execPersonId'] = self.cmbFilterExecSetPerson.value()
        if self.chkFilterAssistant.isChecked():
            filter['assistantId'] = self.cmbFilterAssistant.value()
        if self.chkFilterActionIsUrgent.isChecked():
            filter['isUrgent'] = True
        if self.chkFilterActionPlannedEndDate.isChecked():
            filter['begPlannedEndDate'] = self.edtFilterActionBegPlannedEndDate.date()
            filter['endPlannedEndDate'] = self.edtFilterActionEndPlannedEndDate.date()
        if self.chkFilterActionExecDate.isChecked():
            filter['begExecDate'] = self.edtFilterActionBegExecDate.date()
            filter['endExecDate'] = self.edtFilterActionEndExecDate.date()
            filter['begExecTime'] = self.edtFilterActionBegExecTime.time()
            filter['endExecTime'] = self.edtFilterActionEndExecTime.time()
        if self.chkFilterActionCreatePerson.isChecked():
            filter['createPersonId'] = self.cmbFilterActionCreatePerson.value()
        if self.chkFilterActionCreateDate.isChecked():
            filter['begCreateDate'] = self.edtFilterActionBegCreateDate.date()
            filter['endCreateDate'] = self.edtFilterActionEndCreateDate.date()
        if self.chkFilterActionModifyPerson.isChecked():
            filter['modifyPersonId'] = self.cmbFilterActionModifyPerson.value()
        if self.chkFilterActionModifyDate.isChecked():
            filter['begModifyDate'] = self.edtFilterActionBegModifyDate.date()
            filter['endModifyDate'] = self.edtFilterActionEndModifyDate.date()
        if self.chkFilterActionPayStatus.isChecked():
            filter['payStatusCode'] = self.cmpFilterActionPayStatusCode.currentIndex()
            index = self.cmbFilterActionPayStatusFinance.currentIndex()
            if not 0 <= index < 5:
                index = 0
            filter['payStatusFinanceCode'] = 5 - index
        actionsFilterType = self.cmbFilterAction.currentIndex()
        if actionsFilterType == 0:
            filter['clientIds'] = [self.selectedClientId()]
        elif actionsFilterType == 1:
            filter['clientIds'] = self.registryWidget().model().idList()
        elif actionsFilterType == 2:
            filter['eventIds'] = [self.tblEvents.currentItemId()]
        elif actionsFilterType == 3:
            filter['eventIds'] = self.modelEvents.idList()
        filter['actionsFilterType'] = actionsFilterType
        filter['booleanFilledProperty'] = self.chkFilledProperty.isChecked()  # True = заполнено; False = не заполнено
        if self.chkThresholdPenaltyGrade.isChecked():
            filter['thresholdPenaltyGrade'] = self.edtThresholdPenaltyGrade.text()

        self.updateActionsList(filter)
        self.focusEvents()

    @QtCore.pyqtSlot()
    def on_actExpertEditClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            self.editClient(clientId)
            self.updateTempInvalidInfo()
            self.updateClientsListRequest = True

    @QtCore.pyqtSlot(int)
    def on_tabWidgetTempInvalidTypes_currentChanged(self, index):
        filter = 'type=%d' % index
        self.cmbFilterExpertDocType.setTable('rbTempInvalidDocument', False, filter)
        self.cmbFilterExpertReason.setTable('rbTempInvalidReason', False, filter)
        self.cmbFilterExpertSpeciality.setTable('rbSpeciality', True)
        self.cmbFilterExpertDocType.setValue(self.__tempInvalidDocTypeIdListByTypePage[index])
        self.on_buttonBoxExpert_apply()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertTempInvalid_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)

    def onExpertTempInvalidPopupMenuAboutToShow(self):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        prevId = self.getExpertPrevDocId(self.tblExpertTempInvalid)
        nextId = self.getExpertNextDocId(self.tblExpertTempInvalid)
        self.actExpertTempInvalidNext.setEnabled(bool(nextId))
        self.actExpertTempInvalidPrev.setEnabled(bool(prevId))
        self.actExpertTempInvalidDuplicate.setEnabled(bool(tempInvalidId))

    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidNext_triggered(self):
        nextId = self.getExpertNextDocId(self.tblExpertTempInvalid)
        if nextId:
            row = self.tblExpertTempInvalid.model().findItemIdIndex(nextId)
            if row >= 0:
                self.tblExpertTempInvalid.setCurrentRow(row)
            else:
                QtGui.QMessageBox.information(self, u'Переход к следующему документу',
                                              u'Переход невозможен - необходимо изменить фильтр')

    def onListBeforeRecordClientPopupMenuAboutToShow(self):
        clientId = self.currentClientId()
        self.actSetToDeferredQueue.setEnabled(bool(clientId))
        self.actListVisitByQueue.setEnabled(bool(clientId))
        self.actLocationCard.setEnabled(bool(clientId))
        self.actStatusObservationClient.setEnabled(bool(clientId))
        self.actControlDoublesRecordClient.setEnabled(bool(clientId) and QtGui.qApp.userHasRight(urRegControlDoubles))
        self.actReservedOrderQueueClient.setEnabled(bool(
            QtGui.qApp.mainWindow.dockFreeQueue and QtGui.qApp.mainWindow.dockFreeQueue.content and QtGui.qApp.mainWindow.dockFreeQueue.content._appLockId))

    def onQueuePopupMenuAboutToShow(self):
        notEmpty = self.modelQueue.rowCount() > 0
        self.actAmbCreateEvent.setEnabled(notEmpty and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]))
        self.actAmbDeleteOrder.setEnabled(notEmpty)
        self.actAmbChangeNotes.setEnabled(notEmpty)
        self.actAmbPrintOrder.setEnabled(notEmpty)
        self.actAmbPrintOrderTemplate.setEnabled(notEmpty)
        self.actPrintBeforeRecords.setEnabled(notEmpty)
        self.actShowPreRecordInfo.setEnabled(notEmpty)

    def checkTblEventsPopupMenu(self):
        eventTypeId = forceRef(self.modelEvents.getRecordByRow(self.tblEvents.currentRow()).value('eventType_id'))
        self.actOpenAccountingByEvent.setEnabled(self.modelEvents.rowCount() > 0)
        self.actTransferHospitalization.setVisible(getEventTypeForm(eventTypeId) == '027')

    def checkTblEventActionsPopupMenu(self):
        self.actOpenAccountingByAction.setEnabled(self.modelEventActions.rowCount() > 0)

    def checkTblEventVisitsPopupMenu(self):
        self.actOpenAccountingByVisit.setEnabled(self.modelEventVisits.rowCount() > 0)

    @QtCore.pyqtSlot()
    def on_actAmbCreateEvent_triggered(self):
        clientId = self.currentClientId()
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            record = self.modelQueue.items()[row]
            directionDate = forceDateTime(record.value('directionDate'))
            personId = forceDate(record.value('person_id'))
            requestNewEvent(self, clientId, False, None, [], None, directionDate, personId)
            self.onCurrentClientChanged()

    @QtCore.pyqtSlot()
    def on_actAmbDeleteOrder_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            record = self.modelQueue.items()[row]
            actionId = forceRef(record.value('id'))
            setPersonId = forceRef(record.value('setPerson_id'))
            createPersonId = forceRef(record.value('createPerson_id'))
            nurseOwnerId = QtGui.qApp.nurseOwnerId()
            # текущий пользователь - врач, назначивший услугу и имеющий право отменять свои назначения
            currentUserIsSetPerson = (setPersonId
                                      and setPersonId == QtGui.qApp.userId
                                      and QtGui.qApp.userHasRight(urQueueToSelfDeletedTime))
            # текущий пользователь - медсестра, и она работает с врачом, назначившим услугу и имеющим право отменять свои назначения, а так же она создала эту запись
            currentUserIsNurseOfSetPerson = (QtGui.qApp.isNurse()
                                             and setPersonId
                                             and setPersonId == nurseOwnerId  # Назначено врачом, с которым работает медстестра
                                             and createPersonId == QtGui.qApp.userId  # Создано текущей медсестрой
                                             and CUserInfo(nurseOwnerId).hasRight(urQueueToSelfDeletedTime))

            if actionId and (QtGui.qApp.userHasRight(urQueueDeletedTime)
                             or currentUserIsSetPerson
                             or currentUserIsNurseOfSetPerson
                             ):
                confirmation = QtGui.QMessageBox.warning(self,
                                                         u'Внимание!',
                                                         u'Подтвердите удаление записи к врачу',
                                                         QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                         QtGui.QMessageBox.Cancel)
                if confirmation != QtGui.QMessageBox.Ok:
                    return
                db = QtGui.qApp.db
                propertiesTable = db.table('ActionProperty_Action')
                tableAction = db.table('Action')
                db.transaction()
                try:
                    record = db.getRecordEx(tableAction, '*', tableAction['id'].eq(actionId))
                    record.setValue('deleted', QtCore.QVariant(1))
                    record.setValue('status', QtCore.QVariant(3))
                    db.updateRecord(tableAction, record)

                    db.updateRecords(propertiesTable, 'value=NULL', [propertiesTable['value'].eq(actionId)])
                    db.commit()
                except:
                    db.rollback()
                    raise
            QtGui.qApp.emitCurrentClientInfoChanged()
            self.updateQueue()
            if QtGui.qApp.mainWindow.dockResources:
                QtGui.qApp.mainWindow.dockResources.content.updateTimeTable()

    @QtCore.pyqtSlot()
    def on_actAmbChangeNotes_triggered(self):
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            item = self.modelQueue.items()[row]
            actionId = forceRef(item.value('id'))
            if actionId:
                dlg = CComplaintsEditDialog(self)
                dlg.setComplaints(forceString(item.value('note')))
                if dlg.exec_():
                    db = QtGui.qApp.db
                    table = db.table('Action')
                    record = table.newRecord(['id', 'note'])
                    record.setValue('id', toVariant(actionId))
                    record.setValue('note', toVariant(dlg.getComplaints()))
                    db.updateRecord(table, record)
                    # item.setValue('note', record.value('note'))
                    self.modelQueue.setValue(row, 'note', record.value('note'))

    @QtCore.pyqtSlot(int)
    def on_actAmbPrintOrderTemplate_printByTemplate(self, templateId):
        eventId = None
        timeRange = None, None
        timeRange1 = None, None
        timeRange2 = None, None
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            record = self.modelQueue.items()[row]
            actionId = forceRef(record.value('id'))
            if actionId:
                db = QtGui.qApp.db
                table = db.table('ActionProperty_Action')
                num = forceInt(db.translate(table, table['value'], actionId, table['index']))
                office = forceString(record.value('office'))
                personId = forceRef(record.value('person_id'))
                dateTime = forceDateTime(record.value('directionDate'))
                date = dateTime.date()
                time = dateTime.time()
                clientId = self.currentClientId()
                if clientId:
                    records = forceRef(db.query(
                        '''
                        SELECT A.event_id FROM Action AS A WHERE A.id = (SELECT ActionProperty.action_id
                        FROM Action
                        INNER JOIN ActionProperty_Action ON ActionProperty_Action.value = Action.id
                        INNER JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
                        INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                        WHERE Action.id = %d AND ActionPropertyType.name LIKE \'%s\' LIMIT 0, 1)
                        ''' % (actionId, 'queue')
                    )
                    )
                    if records.first():
                        record = records.record()
                        eventId = forceRef(record.value('event_id'))
                    if eventId:
                        action = CAction.getAction(eventId, atcAmbulance)
                        begTime = action['begTime']
                        endTime = action['endTime']
                        begTime1 = action['begTime1']
                        endTime1 = action['endTime1']
                        begTime2 = action['begTime2']
                        endTime2 = action['endTime2']
                        if begTime and endTime:
                            timeRange = (begTime, endTime)
                        if begTime1 and endTime1:
                            timeRange1 = (begTime1, endTime1)
                        if begTime2 and endTime2:
                            timeRange2 = (begTime2, endTime2)
                        if timeRange1 and timeRange2:
                            start1, finish1 = timeRange1
                            if time >= start1 and time < finish1:
                                timeRange = timeRange1
                            start2, finish2 = timeRange2
                            if time >= start2 and time < finish2:
                                timeRange = timeRange2

                        row = self.tblQueue.currentIndex().row()
                        eventId = forceInt(self.tblQueue.model().value(row, 'event_id'))
                        typeText = u'Направление на приём к врачу'
                        timeRange = '' + timeRange[0].toString('HH:mm') + ' - ' + timeRange[1].toString('HH:mm')

                        visitInfo = {'clientId': clientId,
                                     'type': typeText,
                                     'date': forceString(date),
                                     'office': office,
                                     'personId': personId,
                                     'num': num,
                                     'time': time.toString('HH:mm') if time else '--:--',
                                     'timeRange': timeRange,
                                     }

                        clientInfo = getClientInfo2(clientId)
                        personInfo = clientInfo.getInstance(CPersonInfo, personId)
                        eventInfo = clientInfo.getInstance(CEventInfo, eventId)

                        data = {'event': eventInfo,
                                'client': clientInfo,
                                'person': personInfo,
                                'visit': visitInfo}

                        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_actAmbPrintOrder_triggered(self):
        eventId = None
        timeRange = None, None
        timeRange1 = None, None
        timeRange2 = None, None
        index = self.tblQueue.currentIndex()
        if index.isValid():
            row = index.row()
            record = self.modelQueue.items()[row]
            actionId = forceRef(record.value('id'))
            if actionId:
                db = QtGui.qApp.db
                table = db.table('ActionProperty_Action')
                num = forceInt(db.translate(table, table['value'], actionId, table['index']))
                office = forceString(record.value('office'))
                personId = forceRef(record.value('person_id'))
                dateTime = forceDateTime(record.value('directionDate'))
                date = dateTime.date()
                time = dateTime.time()
                clientId = self.currentClientId()
                if clientId:
                    records = forceRef(db.query(
                        '''
                            SELECT A.event_id FROM Action AS A WHERE A.id = (SELECT ActionProperty.action_id
                            FROM Action
                            INNER JOIN ActionProperty_Action ON ActionProperty_Action.value = Action.id
                            INNER JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
                            INNER JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
                            WHERE Action.id = %d AND ActionPropertyType.name LIKE \'%s\' LIMIT 0, 1)
                        ''' % (actionId, 'queue')
                    )
                    )
                    if records.first():
                        record = records.record()
                        eventId = forceRef(record.value('event_id'))
                    if eventId:
                        action = CAction.getAction(eventId, atcAmbulance)
                        begTime = action['begTime']
                        endTime = action['endTime']
                        begTime1 = action['begTime1']
                        endTime1 = action['endTime1']
                        begTime2 = action['begTime2']
                        endTime2 = action['endTime2']
                        if begTime and endTime:
                            timeRange = (begTime, endTime)
                        if begTime1 and endTime1:
                            timeRange1 = (begTime1, endTime1)
                        if begTime2 and endTime2:
                            timeRange2 = (begTime2, endTime2)
                        if timeRange1 and timeRange2:
                            start1, finish1 = timeRange1
                            if time >= start1 and time < finish1:
                                timeRange = timeRange1
                            start2, finish2 = timeRange2
                            if time >= start2 and time < finish2:
                                timeRange = timeRange2

                        row = self.tblQueue.currentIndex().row()
                        eventId = forceInt(self.tblQueue.model().value(row, 'event_id'))

                        printOrder(self, clientId, 0, date, office, personId, eventId, num + 1, time,
                                   unicode(formatTimeRange(timeRange)))

    @QtCore.pyqtSlot()
    def on_actPrintBeforeRecords_triggered(self):
        if self.modelQueue.rowCount():
            self.tblQueue.setReportHeader(u'Протокол предварительной записи пациента')
            self.tblQueue.setReportDescription(self.txtClientInfoBrowser.toHtml())
            dataRoles = [None] + [QtCore.Qt.DisplayRole] * (self.tblQueue.model().columnCount() - 1)
            self.tblQueue.printContent(dataRoles)

    @QtCore.pyqtSlot()
    def on_actShowPreRecordInfo_triggered(self):
        row = self.tblQueue.currentRow()
        item = self.modelQueue.items()[row]
        self.showPreRecordInfo(item)

    @QtCore.pyqtSlot()
    def on_actSetVIPStatus_triggered(self):
        dlg = CVIPStatusCommentEditDialog(self.currentClientId())
        dlg.exec_()
        if dlg.saved:
            if dlg.isVIP:
                self.registryWidget().viewWidget().model().vipList[self.currentClientId()] = dlg.getColor()
                self.showClientInfo(self.currentClientId())
            elif self.currentClientId() in self.registryWidget().viewWidget().model().vipList:
                self.registryWidget().viewWidget().model().vipList.pop(self.currentClientId())
                self.showClientInfo(self.currentClientId())

    # @QtCore.pyqtSlot()
    # def on_actSetVIPStatus_triggered(self):
    #    dlg = CVIPStatusCommentEditDialog(self.currentClientId())
    #    dlg.exec_()
    #    editClientVIPStatus(self.currentClientId(), dlg.edtVIPStatusComment.toPlainText())
    #    if self.currentClientId() not in self.registryWidget().viewWidget().model().vipList:
    #        self.registryWidget().viewWidget().model().vipList.append(self.currentClientId())

    # @QtCore.pyqtSlot()
    # def on_actDelVIPStatus_triggered(self):
    #    editClientVIPStatus(self.currentClientId(), delete=True)
    #    if self.currentClientId() in self.registryWidget().viewWidget().model().vipList:
    #        self.registryWidget().viewWidget().model().vipList.remove(self.currentClientId())

    # @QtCore.pyqtSlot()
    # def on_actEditVIPComment_triggered(self):
    #    dlg = CVIPStatusCommentEditDialog(self.currentClientId())
    #    dlg.setData()
    #    if dlg.exec_():
    #        editClientVIPComment(self.currentClientId(), dlg.edtVIPStatusComment.toPlainText())


    @QtCore.pyqtSlot()
    def on_actControlDoublesRecordClient_triggered(self):
        clientId = self.currentClientId()
        if clientId:
            dlg = CControlDoubles(self)
            dlg.setTemplateDir(forceStringEx(QtGui.qApp.preferences.appPrefs.get('controlDoubles', '')))
            dlg.setClientId(clientId)
            dlg.exec_()
            QtGui.qApp.preferences.appPrefs['controlDoubles'] = dlg.templateDir()
            self.on_buttonBoxClient_apply()

    @QtCore.pyqtSlot()
    def on_actReservedOrderQueueClient_triggered(self):
        dockFreeQueue = QtGui.qApp.mainWindow.dockFreeQueue
        if dockFreeQueue and dockFreeQueue.content and dockFreeQueue.content._appLockId:
            dockFreeQueue.content.on_actAmbCreateOrder_triggered()

    @QtCore.pyqtSlot()
    def on_actListVisitByQueue_triggered(self):
        try:
            clientId = self.currentClientId()
            if QtGui.qApp.mainWindow.dockResources.content and clientId:
                QtGui.qApp.mainWindow.dockResources.content.createVisitBeforeRecordClient(clientId)
        except:
            pass

    @QtCore.pyqtSlot()
    def on_actSetToDeferredQueue_triggered(self):
        dialog = CCreateDeferredQueue(self)
        dialog.setCheckedReturnTo(1)
        dialog.setClient(self.currentClientId())
        self.connect(dialog, QtCore.SIGNAL('showRegistry(int)'), QtGui.qApp.mainWindow.on_actRegistry_triggered)
        self.connect(dialog, QtCore.SIGNAL('showDeferredQueue(int)'),
                     QtGui.qApp.mainWindow.on_actDeferredQueue_triggered)
        dialog.exec_()

    @QtCore.pyqtSlot()
    def on_actLocationCard_triggered(self):
        self.updateLocationCardType()

    @QtCore.pyqtSlot()
    def on_actStatusObservationClient_triggered(self):
        self.updateStatusObservationClient()

    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidPrev_triggered(self):
        prevId = self.getExpertPrevDocId(self.tblExpertTempInvalid)
        if prevId:
            row = self.tblExpertTempInvalid.model().findItemIdIndex(prevId)
            if row >= 0:
                self.tblExpertTempInvalid.setCurrentRow(row)
            else:
                QtGui.QMessageBox.information(self, u'Переход к предыдущему документу',
                                              u'Переход невозможен - необходимо изменить фильтр')

    @QtCore.pyqtSlot()
    def on_actSearchInDiabetRegistry_triggered(self):
        id = self.currentClientId()
        db = QtGui.qApp.db
        record = db.getRecord(db.table('Client'), '*', id)
        lastName = forceString(record.value('lastName'))
        firstName = forceString(record.value('firstName'))
        patrName = forceString(record.value('patrName'))
        birthDate = forceString(forceDate(record.value('birthDate')).toString('dd.MM.yyyy'))

        browser = CBrowserDialog(self)
        try:
            browser.gotoFullSearch(lastName, firstName, patrName, birthDate)
            browser.exec_()
        except:
            pass

    @QtCore.pyqtSlot()
    def on_actExpertTempInvalidDuplicate_triggered(self):
        tempInvalidId = self.tblExpertTempInvalid.currentItemId()
        if tempInvalidId:
            dialog = CTempInvalidDuplicateEditDialog(self)
            dialog.setTempInvalid(tempInvalidId)
            if dialog.exec_():
                self.updateTempInvalidInfo(tempInvalidId)

    def createAdditionalFeaturesTrigger(self, triggerName, name, template):
        @QtCore.pyqtSlot()
        def inner(self):
            appPrefs = QtGui.qApp.preferences.appPrefs
            browserPath = forceString(appPrefs.get('browserPath', ''))
            clientInfo = getClientInfo2(self.currentClientId())
            if template:
                url, _ = compileAndExecTemplate(template, {'client': clientInfo})
                openURLinBrowser(url, browserPath)

        return inner

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertTempInvalidDuplicates_doubleClicked(self, index):
        itemId = self.tblExpertTempInvalidDuplicates.currentItemId()
        if itemId:
            dialog = CTempInvalidDuplicateEditDialog(self)
            dialog.load(itemId)
            if dialog.exec_():
                self.tblExpertTempInvalidDuplicates.model().invalidateRecordsCache()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertDisability_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertDisability.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelExpertVitalRestriction_currentRowChanged(self, current, previous):
        tempInvalidId = self.tblExpertVitalRestriction.currentItemId()
        self.updateTempInvalidInfo(tempInvalidId)

    @QtCore.pyqtSlot(int)
    def on_modelExpertTempInvalid_itemsCountChanged(self, count):
        infoBeds, infoAddressOrgStructure = self.getFilterInfoBed()
        self.lblExpertTempInvalidCount.setText(formatRecordsCount(count) + infoBeds + infoAddressOrgStructure)

    @QtCore.pyqtSlot(int)
    def on_modelExpertDisability_itemsCountChanged(self, count):
        self.lblExpertDisabilityCount.setText(formatRecordsCount(count))

    @QtCore.pyqtSlot(int)
    def on_modelExpertVitalRestriction_itemsCountChanged(self, count):
        self.lblExpertVitalRestrictionCount.setText(formatRecordsCount(count))

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertTempInvalid_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertDisability_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblExpertVitalRestriction_doubleClicked(self, index):
        self.on_btnExpertEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnExpertEdit_clicked(self):
        tempInvalidId = self.currentTempInvalidId()
        if tempInvalidId:
            self.editTempInvalid(tempInvalidId)
        self.focusExpert()
        QtGui.qApp.emitCurrentClientInfoChanged()

    @QtCore.pyqtSlot()
    def on_actExpertPrint_triggered(self):
        tblExpert = self.getCurrentExpertTable()
        tempInvalidType = self.tabWidgetTempInvalidTypes.currentIndex()
        tblExpert.setReportHeader(unicode(self.tabWidgetTempInvalidTypes.tabText(tempInvalidType)))
        tblExpert.setReportDescription(self.getExpertFilterAsText())
        tblExpert.printContent()
        self.focusExpert()

    @QtCore.pyqtSlot(int)
    def on_btnExpertPrint_printByTemplate(self, templateId):
        data = self.getKerContextData()
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_btnExpertFilter_clicked(self):
        for s in self.chkListOnExpertPage:
            chk = s[0]
            if chk.isChecked():
                self.activateFilterWdgets(s[1])
                return
        dfltChk = self.chkFilterExpertDocType
        self.setChkFilterChecked(dfltChk, True)

    @QtCore.pyqtSlot()
    def on_btnExpertNew_clicked(self):
        self.editTempInvalidExpert()
        self.focusExpert()
        QtGui.qApp.emitCurrentClientInfoChanged()

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertDocType_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertSerial_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertNumber_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertReason_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertBegDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertEndDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertOrgStruct_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertSpeciality_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertMKB_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertClosed_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertDuration_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertInsuranceOfficeMark_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertCreatePerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertModifyPerson_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterExpertCreateDate_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot()
    def on_btnRecCancel_clicked(self):
        self.tblRecommendations.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnRecNewEvent_clicked(self):
        db = QtGui.qApp.db
        clientId = self.currentClientId()
        if clientId:
            idList = []
            for index in self.tblRecommendations.selectionModel().selectedIndexes():
                idList.append(self.modelRecommendations.getRecordByRow(index.row()).value('id'))
            tableRecommendation = db.table('Recommendation')
            recommendationList = db.getRecordList(tableRecommendation, where=tableRecommendation['id'].inlist(idList))
            requestNewEvent(self, clientId, isAmb=True, recommendationList=recommendationList)
            self.modelRecommendations.updateContents()

    @QtCore.pyqtSlot()
    def on_btnRecSetPerson2_clicked(self):
        if QtGui.QMessageBox.question(
                self,
                u'Внимание!',
                u'Вы действительно хотите отметить выделенные направления как выполненные?',
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No
        ) == QtGui.QMessageBox.Yes:
            db = QtGui.qApp.db
            clientId = self.currentClientId()
            if clientId:
                tableRecommendation = db.table('Recommendation')
                idList = []
                for index in self.tblRecommendations.selectionModel().selectedIndexes():
                    idList.append(self.modelRecommendations.getRecordByRow(index.row()).value('id'))
                db.updateRecords(tableRecommendation, tableRecommendation['person2_id'].eq(QtGui.qApp.userId),
                                 where=tableRecommendation['id'].inlist(idList))
                self.modelRecommendations.updateContents()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxExpert_clicked(self, button):
        buttonCode = self.buttonBoxExpert.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxExpert_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxExpert_reset()

    def on_buttonBoxExpert_reset(self):
        for s in self.chkListOnExpertPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)
        self.cmbFilterExpert.setCurrentIndex(0)

    def on_buttonBoxExpert_apply(self):
        if not checkTempInvalidNumber(self, self.edtFilterExpertNumber.text()):
            return

        filter = {}
        if self.chkFilterExpertDocType.isChecked():
            filter['docTypeId'] = self.cmbFilterExpertDocType.value()
        if self.chkFilterExpertSerial.isChecked():
            filter['serial'] = forceStringEx(self.edtFilterExpertSerial.text())
        if self.chkFilterExpertNumber.isChecked():
            filter['number'] = forceStringEx(self.edtFilterExpertNumber.text())
        if self.chkFilterExpertReason.isChecked():
            filter['reasonId'] = self.cmbFilterExpertReason.value()
        if self.chkFilterExpertBegDate.isChecked():
            filter['begBegDate'] = self.edtFilterExpertBegBegDate.date()
            filter['endBegDate'] = self.edtFilterExpertEndBegDate.date()
        if self.chkFilterExpertEndDate.isChecked():
            filter['begEndDate'] = self.edtFilterExpertBegEndDate.date()
            filter['endEndDate'] = self.edtFilterExpertEndEndDate.date()
        if self.chkFilterExpertPerson.isChecked():
            filter['personId'] = self.cmbFilterExpertPerson.value()
        if self.chkFilterExpertOrgStruct.isChecked():
            filter['expertOrgStructureId'] = self.cmbFilterExpertOrgStruct.value()
        if self.chkFilterExpertSpeciality.isChecked():
            filter['expertSpecialityId'] = self.cmbFilterExpertSpeciality.value()
        if self.chkFilterExpertMKB.isChecked():
            filter['begMKB'] = self.edtFilterExpertBegMKB.text()
            filter['endMKB'] = self.edtFilterExpertEndMKB.text()
        if self.chkFilterExpertClosed.isChecked():
            filter['closed'] = self.cmbFilterExpertClosed.currentIndex()
        if self.chkFilterExpertDuration.isChecked():
            filter['begDuration'] = self.edtFilterExpertBegDuration.value()
            filter['endDuration'] = self.edtFilterExpertEndDuration.value()
        if self.chkFilterExpertInsuranceOfficeMark.isChecked():
            filter['insuranceOfficeMark'] = self.cmbFilterExpertInsuranceOfficeMark.currentIndex()
        filter['linked'] = self.chkFilterExpertLinked.isChecked()
        if self.chkFilterExpertCreatePerson.isChecked():
            filter['createPersonId'] = self.cmbFilterExpertCreatePerson.value()
        if self.chkFilterExpertCreateDate.isChecked():
            filter['begCreateDate'] = self.edtFilterExpertBegCreateDate.date()
            filter['endCreateDate'] = self.edtFilterExpertEndCreateDate.date()
        if self.chkFilterExpertModifyPerson.isChecked():
            filter['modifyPersonId'] = self.cmbFilterExpertModifyPerson.value()
        if self.chkFilterExpertModifyDate.isChecked():
            filter['begModifyDate'] = self.edtFilterExpertBegModifyDate.date()
            filter['endModifyDate'] = self.edtFilterExpertEndModifyDate.date()
        expertFilterType = self.cmbFilterExpert.currentIndex()
        if expertFilterType == 0:
            filter['clientIds'] = [self.selectedClientId()]
        elif expertFilterType == 1:
            filter['clientIds'] = self.registryWidget().model().idList()
        filter['expertFilterType'] = expertFilterType
        self.updateTempInvalidList(filter)
        self.focusExpert()

    @QtCore.pyqtSlot()
    def on_btnFRefFindMo_clicked(self):
        orgId = selectOrganisation(self, self.cmbFRefRelegateMO.value(), False)
        self.cmbFRefRelegateMO.update()
        if orgId:
            self.cmbFRefRelegateMO.setValue(orgId)

    def checkAmbOrHome(self, APActionId):
        stmt = 'SELECT ActionType.code FROM ActionProperty_Action LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id LEFT JOIN Action ON Action.id = ActionProperty.action_id LEFT JOIN ActionType ON ActionType.id = Action.actionType_id WHERE ActionProperty_Action.id = %d' % APActionId
        query = QtGui.qApp.db.query(stmt)
        if query.first():
            return forceString(query.value(0))
        return None

    def showPreRecordInfo(self, preRecordItem):
        actionId = forceRef(preRecordItem.value('id'))
        dateTime = forceDateTime(preRecordItem.value('directionDate')).toString('dd.MM.yyyy hh:mm')
        office = forceString(preRecordItem.value('office'))
        APActionId = forceRef(preRecordItem.value('APAction_id'))
        ambOrHome = self.checkAmbOrHome(APActionId)
        db = QtGui.qApp.db
        actionRecord = db.getRecord('Action', '*', actionId)
        createDatetime = forceString(actionRecord.value('createDatetime'))
        createPerson = forceString(db.translate('vrbPersonWithSpeciality',
                                                'id', forceRef(actionRecord.value('createPerson_id')),
                                                'name'))
        modifyDatetime = forceString(actionRecord.value('modifyDatetime'))
        modifyPerson = forceString(db.translate('vrbPersonWithSpeciality',
                                                'id', forceRef(actionRecord.value('modifyPerson_id')),
                                                'name'))
        clientId = forceRef(db.translate('Event', 'id',
                                         forceRef(actionRecord.value('event_id')), 'client_id'))
        personInfo = getPersonInfo(forceRef(actionRecord.value('person_id')))
        clientInfo = getClientInfoEx(clientId)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Свойства записи')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)

        cursor.insertText(u'Создатель записи: %s\n' % createPerson)
        cursor.insertText(u'Дата создания записи: %s\n' % createDatetime)
        cursor.insertText(u'Редактор записи: %s\n' % modifyPerson)
        cursor.insertText(u'Дата редактирования записи: %s\n\n' % modifyDatetime)

        cursor.insertText(u'дата записи: %s\n' % forceString(forceDate(actionRecord.value('createDatetime'))))
        if personInfo:
            orgStructure_id = forceInt(db.translate('Person', 'id', personInfo['id'], 'orgStructure_id'))
            orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
            cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
            cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))
        if clientInfo:
            cursor.insertText(u'пациент: %s\n' % clientInfo['fullName'])
            cursor.insertText(u'д/р: %s\n' % clientInfo['birthDate'])
            cursor.insertText(u'возраст: %s\n' % clientInfo['age'])
            cursor.insertText(u'пол: %s\n' % clientInfo['sex'])
            cursor.insertText(u'адрес: %s\n' % clientInfo['regAddress'])
            cursor.insertText(u'полис: %s\n' % clientInfo['policy'])
            cursor.insertText(u'паспорт: %s\n' % clientInfo['document'])
            cursor.insertText(u'СНИЛС: %s\n' % clientInfo['SNILS'])
        note = forceString(actionRecord.value('note'))
        cursor.insertText(u'жалобы/примечания: %s\n' % note)

        if ambOrHome:
            if ambOrHome == 'amb':
                cursor.insertText(u'запись на амбулаторный приём ')
                if bool(office):
                    office = u' к. ' + office
                else:
                    office = ''
                cursor.insertText(unicode(dateTime) + office)
            elif ambOrHome == 'home':
                cursor.insertText(u'вызов на дом ')
                cursor.insertText(unicode(dateTime))

        cursor.insertBlock()
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Свойства записи')
        reportView.setText(doc)
        reportView.exec_()


# ===== :)


def convertFilterToTextItem(resList, filter, prop, propTitle, format=None):
    val = filter.get(prop, None)
    if val:
        if format:
            resList.append((propTitle, format(val)))
        else:
            resList.append((propTitle, val))


class CIdValidator(QtGui.QRegExpValidator):
    def __init__(self, parent):
        QtGui.QRegExpValidator.__init__(self, QtCore.QRegExp(r'(\d*)(\.\d*)?'), parent)


def dateTimeToString(value):
    return value.toString('dd.MM.yyyy hh:mm:ss')


def parseClientId(clientIdEx):
    if '.' in clientIdEx:
        miacCode, clientId = clientIdEx.split('.')
    else:
        miacCode, clientId = '', clientIdEx
    if miacCode:
        if forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(),
                                               'miacCode')) != miacCode.strip():
            return None
    try:
        clientId = int(clientId)
    except ValueError:
        clientId = None

    return clientId


def contactToLikeMask(contact):
    m = '...'
    result = m + m.join(contact.replace('-', '').replace(' ', '').replace('.', '')) + m
    return result


def getKerContext():
    return 'tempInvalid'


def getEventInfoByDiagnosis(context, diagnosisId):
    db = QtGui.qApp.db
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    table = tableDiagnosis.innerJoin(tableDiagnostic, [tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id'])])
    eventId = db.translate(table, tableDiagnosis['id'], diagnosisId, 'event_id')
    return context.getInstance(CEventInfo, eventId)
