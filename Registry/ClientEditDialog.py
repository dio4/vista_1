# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import itertools
import sys
from PyQt4 import QtCore, QtGui, QtSql

import Users.Rights
from Events.Utils import getAvailableCharacterIdByMKBForDiagnosis, specifyDiagnosis
from Exchange.R23.attach.AttachExchange import CR23AttachExchange
from Exchange.R23.attach.Service import CR23ClientAttachService
from Exchange.R23.attach.Types import AttachedClientInfo, DocumentInfo, PolicyInfo, DeAttachQuery
from Exchange.R23.attach.Utils import CBookkeeperCode, CAttachPolicyType, CAttachSentToTFOMS, \
    syncAttachesOnSave, getDeAttachQueryLogTable
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from Orgs.OrgComboBox import CInsurerInDocTableCol, CPolyclinicComboBox, CPolyclinicExtendedInDocTableCol
from Orgs.Orgs import selectOrganisation
from Orgs.PersonComboBoxEx import CPersonFindInDocTableCol
from Orgs.Utils import advisePolicyType, findOrgStructuresByHouseAndFlat, getOKVEDName, \
    getOrganisationInfo, CAttachType
from Quoting.QuotaTypeComboBox import CQuotaTypeComboBox
from Registry.ClientAnthropometric import CClientAntrophometricModel
from Registry.ClientQuotaDiscussionEditor import CQuotingEditorDialog
from Registry.EMSRNExchange.benefitCategories import getBenefitCategories, checkBenefitCategoriesResult
from Registry.ExternalDataShow import CUekDataShow
from Registry.HurtModels import CWorkHurtFactorsModel, CWorkHurtsModel
from Registry.NameMedicamentEdit import CMedicamentInDocTableCol
from Registry.Utils import clientIdToText, findHouseId, getAddress, getAddressId, getClientAddress, \
    getClientDocument, getClientRemarkTypeIdByFlatCode, getClientWork, \
    getDocumentTypeIdListByGroupList, findKLADRRegionRecordsInQuoting, \
    uniqueIdentifierCheckingIsPassed, getClientPhonesMaskDict, getClientBodyStats, \
    setFocusToWidget
from ScardsModule.scard import Scard
from Ui_ClientEditDialog import Ui_Dialog
from Ui_SelectPaymentSchemeDialog import Ui_SelectPaymentSchemeDialog
from Users.Rights import urEditClientWorkPlace, urSkipCheckClientContacts
from library.AgeSelector import parseAgeSelector
from library.CheckableModel import CCheckableModel
from library.ClientRelationComboBox import CClientRelationComboBox
from library.Counter import getAccountingSystemIdentifier
from library.DbComboBox import CDbModel, CDbComboBox
from library.DialogBase import CDialogBase
from library.ICDInDocTableCol import CICDExInDocTableCol, CICDInDocTableCol
from library.InDocTable import CLocItemDelegate, CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, \
    CDateInDocTableCol, CDesignationInDocTableCol, CDetachmentReasonTableCol, \
    CEnumInDocTableCol, CIntInDocTableCol, CKLADRInDocTableCol, CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog
from library.RBTreeComboBox import CRBTreeInDocTableCol
from library.TableModel import CTableModel, CDateCol, CNameCol, CRefBookCol, CTextCol, CTimeCol
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, forceTime, toVariant, variantEq, getVal, calcAgeTuple, \
    checkSNILS, delWasteSymbols, fixSNILS, formatName, formatSex, formatSNILS, \
    isNameValid, nameCase, splitDocSerial, unformatSNILS, CClickSignalAdder, \
    trimNameSeparators, checkENP, fixENP, agreeNumberAndWord
from library.crbcombobox import CRBComboBox, CRBPopupView, CRBModelDataCache
from library.database import CTableRecordCache
from library.exception import CSoapException
from library.interchange import setComboBoxValue, setLineEditValue, setSpinBoxValue, setTextEditValue, \
    updateUsedIndex

try:
    from ibt.CardReader import CCardReader
    from Registry.CardPinRequest import CCardPinRequest
except ImportError:
    pass


class CClientEditDialog(CItemEditorBaseDialog, Ui_Dialog, CVisibleControlMixin):
    prevAddress = None
    prevWork = None

    isTabSocStatusAlreadyLoad = False
    isTabAttachAlreadyLoad = False
    isTabWorkAlreadyLoad = False
    isTabDocsAlreadyLoad = False
    isTabFeatureAlreadyLoad = False
    isTabIdentificationAlreadyLoad = False
    isTabRelationsAlreadyLoad = False
    isTabContactsAlreadyLoad = False
    isTabQuotingAlreadyLoad = False
    isTabDiagnosisesAlreadyLoad = False
    isTabDisabilityAlreadyLoad = False
    isTabMisdemeanorAlreadyLoad = False
    isTabSuicideAlreadyLoad = False
    isTabMonitoringAlreadyLoad = False
    isTabForeignHospitalizationAlreadyLoad = False
    isTabDispanserizationAlreadyLoad = False

    bloodType_id = None
    bloodDate = None
    bloodNotes = ''

    useInputMask = False
    maskTemplates = [
        {'code':  1, 'delimiter': '-', 'onlyRomans': True,  'onlyRuL': False, 'onlyRuR': True,  'rule': ('>Aaa',          '>AA', ur'\d{6}')   },
        {'code':  2, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') },
        {'code':  3, 'delimiter': '-', 'onlyRomans': True,  'onlyRuL': False, 'onlyRuR': True,  'rule': ('>Aaaa',          '>AA', ur'\d{6}')   },
        {'code':  4, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('>AA',           '',    ur'\d{7}')   },
        {'code':  5, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') },
        {'code':  6, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': True,  'onlyRuR': False, 'rule': ('>AA',           '',    ur'\d{6}')   },
        {'code':  7, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': True,  'onlyRuR': False, 'rule': ('>AA',           '',    ur'\d{7}')   },
        {'code':  8, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('99',            '',    ur'\d{7}')   },
        {'code':  9, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'[a-zA-Z0-9]{0,12}') }, # i2650.
        {'code': 10, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxxxxxx',  '',    ur'\d{0,8}') },
        {'code': 11, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') },
        {'code': 12, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') },
        {'code': 13, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') },
        {'code': 14, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('99',            '99',  ur'\d{6}')   },
        {'code': 15, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('99',            '',    ur'\d{7}')   },
        {'code': 16, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': True,  'onlyRuR': False, 'rule': ('>AA',           '',    ur'\d{6}')   },
        {'code': 17, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': True,  'onlyRuR': False, 'rule': ('>AA',           '',    ur'\d{6}')   },
        {'code': 18, 'delimiter': ' ', 'onlyRomans': False, 'onlyRuL': False, 'onlyRuR': False, 'rule': ('xxxxxxxx',      '',    ur'\d{0,8}') }
    ]

    cLengthSerialNumberPolis = {u'ЕП': 16, u'ВС': 9}
    cLengthKindNumberPolis = {2: 9, 3: 16, 4: 16, 5: 16}

    def __init__(self, parent):
        # ctor
        CItemEditorBaseDialog.__init__(self, parent, 'Client')
        self.__id = None
        self.__regAddressRecord = None
        self.__quotaRecord = None
        self.__regAddress = None
        self.__locAddressRecord = None
        self.__locAddress = None
        self.__documentRecord = None
        self.__workRecord = None
        self._birthMaxDate = None
        self._birthMinDate = None
        self._compulsoryPolicyVisible = None
        self._voluntaryPolicyVisible = None
        self.isSearchPolicy = None
        self.isConfirmSendingData = None
        self.clickFilter = CClickSignalAdder()

        self.documentTypeId = None

        self.showDischarge = False  # QtGui.qApp.showPolicyDischargeDate()
        self.useInputMask = QtGui.qApp.useInputMask()

        # Вкладка "Паспортные данные"
        self.addModels('Contacts', CContactsModel(self))

        # Вкладка "Соц.статус"
        self.addModels('SocStatuses', CSocStatusesModel(self))

        # Вкладка "Прикрепление"
        self.addModels('Attaches', CAttachesModel(self))

        # Вкладка "Связи"
        self.addModels('DirectRelations', CDirectRelationsModel(self))
        self.addModels('BackwardRelations', CBackwardRelationsModel(self))

        # Вкладка "Занятость"
        self.addModels('WorkHurts', CWorkHurtsModel(self))
        self.addModels('WorkHurtFactors', CWorkHurtFactorsModel(self))
        self.addModels('OldWorks', COldWorksModel(self))

        # Вкладка "Документы"
        self.addModels('IdentificationDocs', CIdentificationDocsModel(self))
        self.addModels('Policies', CPoliciesModel(self))
        self.addModels('SocStatusDocs', CSocStatusDocsModel(self))

        # Вкладка "Особенности"
        self.addModels('Allergy', CAllergyModel(self))
        self.addModels('IntoleranceMedicament', CIntoleranceMedicamentModel(self))
        self.addModels('ClientAnthropometric', CClientAntrophometricModel(self))
        self.addModels('ClientCheckup', CSocStatusesModel(self))

        # Вкладка "Идентификаторы"
        self.addModels('ClientIdentification', CClientIdentificationModel(self))

        # Вкладка "Квоты"
        self.addModels('ClientQuoting', CClientQuotingModel(self))
        self.addModels('ClientQuotingDiscussion', CClientQuotingDiscussionModel(self))
        self.addModels('PaymentScheme', CPaymentSchemeModel(self))

        # Вкладка "Диагнозы"
        self.addModels('ClientMainDiagnosises', CClientDiagnosisesModel(self, '2'))
        self.addModels('ClientSecondaryDiagnosises', CClientDiagnosisesModel(self, '9'))

        # Вкладка "Льготы/Инвалидность"
        self.addModels('ClientDisability', CClientDisabilityModel(self))
        # Таблица с соц. статусами, где оставлен только класс "Льготы"
        self.addModels('ClientBenefits', CSocStatusesModel(self))

        # Вкладка "Правонарушения"
        # TODO: atronah: i1208: инициализация вкладки
        self.addModels('ClientMisdemeanor', CMisdemeanorModel(self))
        if QtGui.qApp.isPNDDiagnosisMode():
            self.addModels('ClientCompulsoryTreatment', CCompulsoryTreatmentModel(self))

        # Вкладка "Суицид"
        # TODO: atronah: i1208: инициализация вкладки
        self.addModels('ClientSuicide', CSuicideModel(self))

        # Вкладка "Наблюдения"
        # TODO: atronah: i1208: инициализация вкладки
        self.addModels('ClientMonitoring', CMonitoringModel(self))

        # Вкладка "Госпитализации в др. ЛПУ"
        self.addModels('ForeignHospitalization', CForeignHospitalizationModel(self))

        # Вкладка "Дополнительная диспантеризация"
        self.addModels('Dispanserization', CDispanserizationModel(self))

        # ui
        self.setupUi(self)

        # Перенос панели кнопок "Ок", "Отмена" и т.п. в верх окна, если указана соответствующая глобальная настройка
        buttonBoxAtTop = QtGui.qApp.isButtonBoxAtTopWindow()
        if not buttonBoxAtTop:
            mainLayout = self.layout()
            buttonBoxIndex = mainLayout.indexOf(self.buttonBox)
            mainLayout.addWidget(mainLayout.takeAt(buttonBoxIndex).widget(),  # widget
                                 mainLayout.count(),  # row
                                 0,  # column
                                 1,  # rowSpan
                                 mainLayout.columnCount())  # columnSpan

        self.setObjectName('ClientEditDialog')
        self.edtBirthDate.setHighlightRedDate(False)
        self.edtWorkOrganisationINN.setBackgroundRole(QtGui.QPalette.Window)
        self.edtWorkOrganisationOGRN.setBackgroundRole(QtGui.QPalette.Window)
        self.edtOKVEDName.setBackgroundRole(QtGui.QPalette.Window)

        self.tabSocStatus.setFocusProxy(self.tblSocStatuses)
        self.tabAttach.setFocusProxy(self.tblAttaches)
        self.tabRelations.setFocusProxy(self.tblDirectRelations)
        self.tabWork.setFocusProxy(self.btnSelectWorkOrganisation)
        self.tabFeature.setFocusProxy(self.tblAllergy)
        self.tabFeature.setFocusProxy(self.tblIntoleranceMedicament)
        self.tabIdentification.setFocusProxy(self.tblClientIdentification)
        self.tabDispanserization.setFocusProxy(self.tblDispaserization)
        self.tabPassport.setFocusProxy(self.edtLastName)
        self.tabPaymentScheme.setFocusProxy(self.tblPaymentScheme)
        if not QtGui.qApp.isPNDDiagnosisMode():
            self.tabWidget.removeTab(self.tabWidget.indexOf(self.tabDiagnosises))
            self.chkRegisterFirstInPND.setVisible(False)
            self.gbCompulsoryTreatment.setVisible(False)
        self.btnSearchPolicy.setEnabled(QtGui.qApp.identServiceEnabled())
        self.edtChartBeginDate.setDate(QtCore.QDate.currentDate())

        self.cmbDocType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')', order = 'usedIndex DESC')

        db = QtGui.qApp.db
        policyTypeList = map(lambda x: forceString(x.value('objectName')), db.getRecordList(
            table=db.table('rbUserProfile_Hidden'),
            cols='objectName',
            where='objectName LIKE \'ClientEditDialog.policyType.%\'' + 'AND master_id = %s' % QtGui.qApp.userInfo.userProfilesId[0]
        ))

        self.cmbCompulsoryPolisType.setTable(
            'rbPolicyType',
            True,
            u'name LIKE \'ОМС%\'' if u'ClientEditDialog.policyType.OMC' not in policyTypeList else u'id IS NULL'
        )
        self.cmbCompulsoryPolisKind.setTable('rbPolicyKind', True)

        voluntaryCond = u''
        if u'ClientEditDialog.policyType.DMC' not in policyTypeList:
            voluntaryCond += u'name NOT LIKE \'ОМС%\''
        if u'ClientEditDialog.policyType.franchis' not in policyTypeList:
            voluntaryCond += u'code = \'franchis\'' if len(voluntaryCond) == 0 else u' or code = \'franchis\''
        else:
            voluntaryCond += u'(code <> \'franchis\' and name NOT LIKE \'ОМС%\')' if len(voluntaryCond) == 0 else u' and (code <> \'franchis\' and name NOT LIKE \'ОМС%\')'
        if u'ClientEditDialog.policyType.DMC' in policyTypeList and u'ClientEditDialog.policyType.franchis' in policyTypeList:
            voluntaryCond = u'id IS NULL'

        self.cmbVoluntaryPolisType.setTable(
            'rbPolicyType',
            True,
            voluntaryCond
        )
        self.cmbRegDistrict.setTable(tableName='rbDistrict', addNone=True)
        self.cmbRegDistrict.setValue(None)
        self.cmbLocDistrict.setTable(tableName='rbDistrict', addNone=True)
        self.cmbLocDistrict.setValue(None)

        # assign models
        self.setModels(self.tblContacts, self.modelContacts, self.selectionModelContacts)
        self.setModels(self.tblIdentificationDocs, self.modelIdentificationDocs, self.selectionModelIdentificationDocs)
        self.setModels(self.tblPolicies, self.modelPolicies, self.selectionModelPolicies)
        self.tblPolicies.isTblPolices = True
        # Issue 924. Moved setModels here from initTab** funcs for proper geometry initialization of these tables.
        self.setModels(self.tblSocStatuses, self.modelSocStatuses, self.selectionModelSocStatuses)
        self.setModels(self.tblAttaches, self.modelAttaches, self.selectionModelAttaches)
        self.setModels(self.tblWorkHurts, self.modelWorkHurts, self.selectionModelWorkHurts)
        self.setModels(self.tblWorkHurtFactors, self.modelWorkHurtFactors, self.selectionModelWorkHurtFactors)
        self.setModels(self.tblOldWorks, self.modelOldWorks, self.selectionModelOldWorks)
        self.setModels(self.tblSocStatusDocs, self.modelSocStatusDocs, self.selectionModelSocStatusDocs)
        self.setModels(self.tblPaymentScheme, self.modelPaymentScheme, self.selectionModelPaymentScheme)

        self.setModels(self.tblAllergy, self.modelAllergy, self.selectionModelAllergy)
        self.setModels(self.tblIntoleranceMedicament, self.modelIntoleranceMedicament, self.selectionModelIntoleranceMedicament)
        self.setModels(self.tblAnthropometric, self.modelClientAnthropometric, self.selectionModelClientAnthropometric)
        self.setModels(self.tblCheckup, self.modelClientCheckup, self.selectionModelClientCheckup)

        self.setModels(self.tblClientIdentification, self.modelClientIdentification, self.selectionModelClientIdentification)
        self.setModels(self.tblDirectRelations, self.modelDirectRelations, self.selectionModelDirectRelations)
        self.setModels(self.tblBackwardRelations, self.modelBackwardRelations, self.selectionModelBackwardRelations)
        self.setModels(self.tblClientQuoting, self.modelClientQuoting, self.selectionModelClientQuoting)
        self.setModels(self.tblClientQuotingDiscussion, self.modelClientQuotingDiscussion, self.selectionModelClientQuotingDiscussion)
        self.setModels(self.tblMainDiagnosises, self.modelClientMainDiagnosises, self.selectionModelClientMainDiagnosises)
        self.setModels(self.tblSecondaryDiagnosises, self.modelClientSecondaryDiagnosises, self.selectionModelClientSecondaryDiagnosises)
        self.setModels(self.tblClientDisability, self.modelClientDisability, self.selectionModelClientDisability)
        self.setModels(self.tblClientBenefits, self.modelClientBenefits, self.selectionModelClientBenefits)

        self.setModels(self.tblMisdemeanor, self.modelClientMisdemeanor, self.selectionModelClientMisdemeanor)
        if QtGui.qApp.isPNDDiagnosisMode():
            self.setModels(self.tblCompulsoryTreatment, self.modelClientCompulsoryTreatment, self.selectionModelClientCompulsoryTreatment)
        self.setModels(self.tblSuicide, self.modelClientSuicide, self.selectionModelClientSuicide)
        self.setModels(self.tblMonitoring, self.modelClientMonitoring, self.selectionModelClientMonitoring)
        self.setModels(self.tblForeignHospitalization, self.modelForeignHospitalization, self.selectionModelForeignHospitalization)
        self.setModels(self.tblDispaserization, self.modelDispanserization, self.selectionModelDispanserization)

        # popup menus
        self.tblContacts.addPopupDelRow()
        self.tblContacts.addPopupRecordProperies()
        self.tblIdentificationDocs.addPopupDelRow()
        self.tblIdentificationDocs.addPopupRecordProperies()
        self.tblPolicies.addPopupDelRow()
        self.tblPolicies.addPopupRecordProperies()
        self.connect(self.modelPolicies, QtCore.SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.syncPoliciesBackward)
        # self.connect(self.modelIdentificationDocs, QtCore.SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.syncClientDocsBackward)


        self.cmbCompulsoryPolisCompany.setPolicyTypeFilter(True)  # ОМС компании
        self.cmbVoluntaryPolisCompany.setPolicyTypeFilter(False)  # ДМС компании
        isShowPolicyInsuranceArea = QtGui.qApp.isShowPolicyInsuranceArea()
        self.lblVoluntaryInsuranceArea.setVisible(isShowPolicyInsuranceArea)
        self.cmbVoluntaryInsuranceArea.setVisible(isShowPolicyInsuranceArea)
        self.lblCompulsoryInsuranceArea.setVisible(isShowPolicyInsuranceArea)
        self.cmbCompulsoryInsuranceArea.setVisible(isShowPolicyInsuranceArea)
        if isShowPolicyInsuranceArea:
            self.setPolicyRecord(None, True)
            self.setPolicyRecord(None, False)
        self.chkRegKLADR.setEnabled(not QtGui.qApp.isAddressOnlyByKLADR())
        self.chkLocKLADR.setEnabled(not QtGui.qApp.isAddressOnlyByKLADR())

        self.lblCompulsoryPolicy.installEventFilter(self.clickFilter)
        self.lblVoluntaryPolicy.installEventFilter(self.clickFilter)

        self.connect(self.edtBirthDate.lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onBirthDateChanged)
        self.connect(self.lblCompulsoryPolicy, QtCore.SIGNAL('clicked()'), self.on_lblCompulsoryPolicy_clicked)
        self.connect(self.lblVoluntaryPolicy, QtCore.SIGNAL('clicked()'), self.on_lblVoluntaryPolicy_clicked)
        self.connect(self.modelClientQuoting, QtCore.SIGNAL('quotaTypeSelected(int)'), self.on_modelClientQuoting_quotaTypeSelected)

        # default values
        self.cmbRegCity.setCode(QtGui.qApp.defaultKLADR())
        self.cmbRegCity.setAreaSelectable(False)
        self.cmbLocCity.setCode(QtGui.qApp.defaultKLADR())
        self.cmbLocCity.setAreaSelectable(False)
        self.edtBirthDate.setDate(QtCore.QDate())
        self.cmbDocType.setValue(self.getDefaultDocumentType())
        # etc
        orgStructureId = QtGui.qApp.currentOrgStructureId()
        rbNetId = forceRef(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'net_id'))
        if rbNetId:
            netRecord = QtGui.qApp.db.getRecordEx('rbNet', '*', 'id = %s' % rbNetId)
            if forceBool(netRecord.value('flags')):
                sex = forceInt(netRecord.value('sex'))
                age = forceString(netRecord.value('age'))
                if sex == 1:
                    self.cmbSex.removeItem(2)
                elif sex == 2:
                    self.cmbSex.removeItem(1)
                begUnit, begCount, endUnit, endCount = parseAgeSelector(age)
                if begCount:
                    if begUnit == 1:
                        self._birthMaxDate = QtCore.QDate.currentDate().addDays(-begCount)
                    elif begUnit == 2:
                        self._birthMaxDate = QtCore.QDate.currentDate().addDays(-begCount * 7)
                    elif begUnit == 3:
                        self._birthMaxDate = QtCore.QDate.currentDate().addMonths(-begCount)
                    elif begUnit == 4:
                        self._birthMaxDate = QtCore.QDate.currentDate().addYears(-begCount)
                    self.edtBirthDate.setMaximumDate(self._birthMaxDate)
                if endCount:
                    if endUnit == 1:
                        self._birthMinDate = QtCore.QDate.currentDate().addDays(-endCount - 1)
                    elif endUnit == 2:
                        self._birthMinDate = QtCore.QDate.currentDate().addDays(-endCount * 7 - 7)
                    elif endUnit == 3:
                        self._birthMinDate = QtCore.QDate.currentDate().addMonths(-endCount - 1)
                    elif endUnit == 4:
                        self._birthMinDate = QtCore.QDate.currentDate().addYears(-endCount - 1)
                    self.edtBirthDate.setMinimumDate(self._birthMinDate)

        self.btnCopyPrevAddress.setEnabled(bool(CClientEditDialog.prevAddress))
        self.btnCopyPrevWork.setEnabled(bool(CClientEditDialog.prevWork))
        self.setupDirtyCather()
        self.setIsDirty(False)
        self.lblInfo.setWordWrap(True)
        self.lblMKBText.setWordWrap(True)
        self.edtDocDate.setDate(QtCore.QDate())
        self.edtCompulsoryPolisBegDate.setDate(QtCore.QDate())
        self.edtCompulsoryPolisEndDate.setDate(QtCore.QDate())
        self.edtCompulsoryPolisDischargeDate.setDate(QtCore.QDate())
        self.edtVoluntaryPolisBegDate.setDate(QtCore.QDate())
        self.edtVoluntaryPolisEndDate.setDate(QtCore.QDate())
        self.edtVoluntaryPolisDischargeDate.setDate(QtCore.QDate())
        self.regAddressInfo = {}
        self.locAddressInfo = {}

        # hide discharge date
        if not self.showDischarge:
            self.edtCompulsoryPolisDischargeDate.setVisible(False)
            self.lblCompulsoryPolisDischargeDate.setVisible(False)
            self.edtVoluntaryPolisDischargeDate.setVisible(False)
            self.lblVoluntaryPolisDischargeDate.setVisible(False)

        # Set custom handler for keyPressEvent to TabWidget
        self.tabWidget.installEventFilter(self)

        # disabled edit mode
        if not QtGui.qApp.userHasRight(Users.Rights.urEditClientInfo):
            self.edtLastName.setEnabled(False)
            self.edtFirstName.setEnabled(False)
            self.edtPatrName.setEnabled(False)
            self.edtBirthDate.setEnabled(False)
            self.edtBirthTime.setEnabled(False)
            self.edtSNILS.setEnabled(False)
            self.cmbSex.setEnabled(False)

            notDisabledTabsName = ['tabMonitoring', 'tabDiagnosises', 'tabDisability', 'tabSuicide',
                                   'tabMisdemeanor', 'tabQuoting', 'tabForeignHospitalization']
            tabCount = self.tabWidget.count()
            for tabIndex in xrange(tabCount):
                childTab = self.tabWidget.widget(tabIndex)
                if childTab.objectName() not in notDisabledTabsName:
                    childTab.setEnabled(False)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMaximizeButtonHint)

        self._invisibleObjectsNameList = self.reduceNames(QtGui.qApp.userInfo.hiddenObjectsNameList([self.moduleName()])) \
                                         if QtGui.qApp.userInfo else []
        self.updateVisibleState(self, self._invisibleObjectsNameList)

        # atronah: new realisation (by qt standard model ?without? caching)
        self._docOriginCompleterModel = QtSql.QSqlTableModel(None, QtGui.qApp.db.db)
        self._docOriginCompleterModel.setTable(u'rbTextDataCompleter')
        self._docOriginCompleterModel.setFilter(u"code like 'documentOrigin'")
        self._docOriginCompleterModel.select()
        self._docOriginCompleter = QtGui.QCompleter(self._docOriginCompleterModel, self)
        self._docOriginCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._docOriginCompleter.setCompletionColumn(self._docOriginCompleterModel.fieldIndex(u'name'))
        self._docOriginCompleter.setCompletionMode(QtGui.QCompleter.PopupCompletion)

        if QtGui.qApp.isExtractedDocAutocomplete(): self.edtWhoExtraditedDoc.setCompleter(self._docOriginCompleter)

        self._birthPlaceCompleterModel = QtSql.QSqlTableModel(None, QtGui.qApp.db.db)
        self._birthPlaceCompleterModel.setTable(u'rbTextDataCompleter')
        self._birthPlaceCompleterModel.setFilter(u"code like 'birthPlace'")
        self._birthPlaceCompleterModel.select()
        self._birthPlaceCompleter = QtGui.QCompleter(self._birthPlaceCompleterModel, self)
        self._birthPlaceCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._birthPlaceCompleter.setCompletionColumn(self._docOriginCompleterModel.fieldIndex(u'name'))
        self._birthPlaceCompleter.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.edtBirthPlace.setCompleter(self._birthPlaceCompleter)

        btnUEKisVisible = 'ibt.CardReader' in sys.modules
        btnUEKisVisible = btnUEKisVisible and QtGui.qApp.defaultKLADR().startswith('23')
        btnUEKisVisible = btnUEKisVisible and self.btnUEK.isVisible()
        self.btnUEK.setVisible(btnUEKisVisible)

        # Временное хранение полученых данных о диспансеризации
        self.dispCode = None
        self.dispBegDate = None
        self.dispEndDate = None
        self.dispCodeMO = None

        # Временное хранение данных о прикреплении
        self.attachList = []
        self.attachId = None
        self.attachMo = None

        # Скрытие полей для Казахстана
        visibleWidgets = QtGui.qApp.defaultKLADR().startswith('90')
        self.btnIIN.setVisible(visibleWidgets)
        self.edtIIN.setVisible(visibleWidgets)
        self.lblCompulsoryPolicy.setVisible(not visibleWidgets)
        self.lblVoluntaryPolicy.setVisible(not visibleWidgets)
        self.lblSNILS.setVisible(not visibleWidgets)
        self.edtSNILS.setVisible(not visibleWidgets)
        self.chkRegKLADR.setVisible(not visibleWidgets)
        self.cmbRegCity.setVisible(not visibleWidgets)
        self.cmbRegDistrict.setVisible(not visibleWidgets)
        self.cmbRegStreet.setVisible(not visibleWidgets)
        self.lblHouse.setVisible(not visibleWidgets)
        self.edtRegHouse.setVisible(not visibleWidgets)
        self.lblBuilding.setVisible(not visibleWidgets)
        self.edtRegCorpus.setVisible(not visibleWidgets)
        self.lblFlat.setVisible(not visibleWidgets)
        self.edtRegFlat.setVisible(not visibleWidgets)
        self.chkLocKLADR.setVisible(not visibleWidgets)
        self.cmbLocCity.setVisible(not visibleWidgets)
        self.cmbLocDistrict.setVisible(not visibleWidgets)
        self.cmbLocStreet.setVisible(not visibleWidgets)
        self.lblHouse_2.setVisible(not visibleWidgets)
        self.edtLocHouse.setVisible(not visibleWidgets)
        self.lblBuilding_2.setVisible(not visibleWidgets)
        self.edtLocCorpus.setVisible(not visibleWidgets)
        self.lblFlat_2.setVisible(not visibleWidgets)
        self.edtLocFlat.setVisible(not visibleWidgets)

        self.edtDocSerialLeft.installEventFilter(self)
        self.edtDocSerialRight.installEventFilter(self)

        self.tblContacts.isClientEditDialog = True

        self.btnAddOMCPolicy.clicked.connect(self.addOMCPolicy)
        self.btnAddDMCPolicy.clicked.connect(self.addDMCPolicy)

        self.btnCloseOMCPolicy.clicked.connect(self.closeOMCPolicy)
        self.btnCloseDMCPolicy.clicked.connect(self.closeDMCPolicy)

        self.edtDMCPercent.setInputMask('999')
        self.edtDMCPercent.setText('0')
        self.edtDMCPercent.textChanged.connect(self.on_edtDMCPercentChanged)

        if not QtGui.qApp.isViewDMCPercent():
            self.edtDMCPercent.setVisible(False)
            self.lblPercent.setVisible(False)

        self.oldFranchisePercent = None
        self.newFranchisePercent = None
        self.franchisePercentChanged = False
        self.policyIdDMCF = None

        self.chkUnconscious.setVisible(QtGui.qApp.userHasRight(Users.Rights.urAccessSetUnconscious))

        self.edtPesWeight.setValidator(QtGui.QDoubleValidator(self))
        self.edtPesHeight.setValidator(QtGui.QDoubleValidator(self))

        # ЭПОМС
        # i2340
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EPOMS', False)):
            self.readEpoms.setVisible(True)
            self.readEpoms.clicked.connect(self.on_actReadScard)
            self.cardReaderName = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'cardReader', 'none'))
        else:
            self.readEpoms.setVisible(False)

        self.cmbCompulsoryPolisCompany.setCurrentIndex(0)
        self.cmbVoluntaryPolisCompany.setCurrentIndex(0)

        visibleForKrasnodarRegionWidgets = (
            self.btnGetAttachInformation,
            self.btnSyncClientAttach
        )
        for widget in visibleForKrasnodarRegionWidgets:
            widget.setVisible(QtGui.qApp.defaultKLADR().startswith('23'))

        self.btnGetAttachInformation.clicked.connect(self.requestClientAttaches)
        self.btnSyncClientAttach.clicked.connect(self.onBtnSyncClientAttach)
        self.infoSourceRecord = None
        self.chkHasImplants.setVisible(QtGui.qApp.userHasRight(Users.Rights.urEditImplantsAndProsthesis))
        self.chkHasProsthesis.setVisible(QtGui.qApp.userHasRight(Users.Rights.urEditImplantsAndProsthesis))

    @QtCore.pyqtSlot(bool)
    def on_chkHasImplants_toggled(self, checked):
        if checked and self.chkHasProsthesis.isChecked():
            self.chkHasProsthesis.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_chkHasProsthesis_toggled(self, checked):
        if checked and self.chkHasImplants.isChecked():
            self.chkHasImplants.setChecked(False)

    # i2340
    def on_actReadScard(self):
        try:
            clientInfo = Scard().getClientInfo(self.cardReaderName)
            self.edtLastName.setText(clientInfo['lastname'])
            self.edtFirstName.setText(clientInfo['name'])
            self.edtPatrName.setText(clientInfo['patrname'])

            self.on_edtLastName_editingFinished()
            self.on_edtFirstName_editingFinished()
            self.on_edtPatrName_editingFinished()

            self.edtBirthDate.clear()
            self.edtBirthDate.addItem(clientInfo['birthday'])
            self.edtBirthPlace.setText(clientInfo['born_in'])
            self.edtSNILS.setText(clientInfo['SNILS'])

            self.edtCompulsoryPolisBegDate.addItem(clientInfo['smo']['beg_date'])
            self.edtCompulsoryPolisEndDate.addItem(clientInfo['policy']['end_date'])
            self.edtCompulsoryPolisNumber.setText(clientInfo['policy']['number'])

            self.cmbCompulsoryPolisKind.setCurrentIndex(4)

            self.cmbCompulsoryPolisCompany._popup.setOGRN(clientInfo['smo']['OGRN'])
            self.cmbCompulsoryPolisCompany._popup.setOKATO(clientInfo['smo']['OKATO'])
            self.cmbCompulsoryPolisCompany._popup.disableArea()

            self.cmbCompulsoryPolisCompany._popup.on_buttonBox_apply()
        except:
            QtGui.QMessageBox.warning(
                self,
                u'ОШИБКА',
                u"Картридер сообщил об ошибке. Проверьте вставлена ли карта правильно.",
                QtGui.QMessageBox.Ok
            )

    def on_edtDMCPercentChanged(self):
        if len(self.edtDMCPercent.text()):
            if forceInt(self.edtDMCPercent.text()) != 0:
                if forceInt(self.edtDMCPercent.text()) > 100:
                    self.edtDMCPercent.setText('100')
                i = self.cmbVoluntaryPolisType.findText(forceString(u'ДМС Ф'))  # 'franchis'))
                if i >= 0:
                    self.cmbVoluntaryPolisType.setCurrentIndex(i)
                self.newFranchisePercent = forceInt(self.edtDMCPercent.text())
            else:
                self.cmbVoluntaryPolisType.setCurrentIndex(1)

    def selectPolicyEndDate(self, isDMC=False):
        if self._id > 0:
            db = QtGui.qApp.db
            record = db.getRecordEx(stmt=u'''
            SELECT
              cp.begDate,
              cp.endDate
            FROM
              ClientPolicy cp
              INNER JOIN rbPolicyType pt ON cp.policyType_id = pt.id
            WHERE
              cp.client_id = %s
              AND DATEDIFF(cp.endDate, CURDATE())<=0
              AND pt.name %s
            ORDER BY cp.endDate DESC
            ''' % (self._id, u'NOT LIKE \'ОМС%\'' if isDMC else u'LIKE \'ОМС%\'')
            )
            if record:
                return forceDate(record.value('endDate'))
            else:
                return forceDate(db.translate('Client', 'id', self._id, 'createDatetime'))

    def closeOMCPolicy(self):
        if len(self.edtCompulsoryPolisNumber.text()) and self.cmbCompulsoryPolisCompany.currentIndex():
            if self.edtCompulsoryPolisBegDate.date():
                self.edtCompulsoryPolisEndDate.setDate(QtCore.QDate.currentDate())
            else:
                self.edtCompulsoryPolisBegDate.setDate(self.selectPolicyEndDate())
                self.edtCompulsoryPolisEndDate.setDate(QtCore.QDate.currentDate())

            self.syncPolicy(True, False)  # self.syncPolicies()
            self.addOMCPolicy()
            QtGui.QMessageBox.information(
                self,
                u"Закрытие полиса ОМС",
                u"Полис ОМС закрыт.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    def closeDMCPolicy(self):
        if len(self.edtVoluntaryPolisNumber.text()) and self.cmbVoluntaryPolisCompany.currentIndex():
            if self.edtVoluntaryPolisBegDate.date():
                self.edtVoluntaryPolisEndDate.setDate(QtCore.QDate.currentDate())
            else:
                self.edtVoluntaryPolisBegDate.setDate(self.selectPolicyEndDate(isDMC=True))
                self.edtVoluntaryPolisEndDate.setDate(QtCore.QDate.currentDate())

            self.syncPolicy(False, False)  # self.syncPolicies()
            self.addDMCPolicy()
            QtGui.QMessageBox.information(
                self,
                u"Закрытие полиса ДМС",
                u"Полис ДМС закрыт.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    def addOMCPolicy(self):
        if len(self.edtCompulsoryPolisNumber.text()) != 0 \
                and self.cmbCompulsoryPolisType.currentIndex() != 0 \
                and self.cmbCompulsoryPolisCompany.currentIndex() != 0:
            self.tblPolicies.model().addRecord(self.tblPolicies.model().getEmptyRecord())
            # set default
            self.edtCompulsoryPolisSerial.setText('')
            self.edtCompulsoryPolisNumber.setText('')
            self.updateCompulsoryPolicyCompanyArea([0])
            self.cmbCompulsoryPolisCompany.setValue(0)
            self.cmbCompulsoryPolisType.setValue(0)
            self.cmbCompulsoryPolisKind.setValue(0)
            self.edtCompulsoryPolisName.setText('')
            self.edtCompulsoryPolisNote.setText('')
            self.edtCompulsoryPolisBegDate.setDate(None)
            self.edtCompulsoryPolisEndDate.setDate(None)
            self.edtCompulsoryPolisDischargeDate.setDate(None)
            # self.cmbCompulsoryInsuranceArea.setCode()
            QtGui.QMessageBox.information(
                self,
                u"Добавление полиса ОМС",
                u"Полис ОМС добавлен.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
        else:
            QtGui.QMessageBox.warning(
                self,
                u"Добавление полиса ОМС",
                u"Данные не заполнены. Полис ОМС не добавить.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    def addDMCPolicy(self):
        if len(self.edtVoluntaryPolisNumber.text()) != 0 \
                and self.cmbVoluntaryPolisType.currentIndex() != 0 \
                and self.cmbVoluntaryPolisCompany.currentIndex() != 0:
            self.tblPolicies.model().addRecord(self.tblPolicies.model().getEmptyRecord())
            # set default
            self.edtVoluntaryPolisSerial.setText('')
            self.edtVoluntaryPolisNumber.setText('')
            self.updateVoluntaryPolicyCompanyArea([0])
            self.cmbVoluntaryPolisCompany.setValue(0)
            self.cmbVoluntaryPolisType.setValue(0)
            self.edtVoluntaryPolisName.setText('')
            self.edtVoluntaryPolisNote.setText('')
            self.edtVoluntaryPolisBegDate.setDate(None)
            self.edtVoluntaryPolisEndDate.setDate(None)
            self.edtVoluntaryPolisDischargeDate.setDate(None)
            self.edtDMCPercent.setText('0')
            QtGui.QMessageBox.information(
                self,
                u"Добавление полиса ДМС",
                u"Полис ДМС добавлен.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
        else:
            QtGui.QMessageBox.warning(
                self,
                u"Добавление полиса ДМС",
                u"Данные не заполнены. Полис ДМС не добавить.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )

    @staticmethod
    def moduleName():
        return u'ClientEditDialog'

    @staticmethod
    def moduleTitle():
        return u'Регистрационная карта'

    @classmethod
    def hiddableChildren(cls):
        # TODO: atronah: решить проблему с игнором смены имен в файле интерфейса
        # один из вариантов решения: парсить ui-файл
        nameList = [(u'edtBirthTime', u'Время рождения'),
                    (u'lblChartBeginDate', u'Дата начала карты'),
                    (u'chkRegisterFirstInPND', u'Взят впервые в ПНД'),
                    (u'chkExistsOnlyTempRegistration', u'Есть только временная регистрация'),
                    (u'lblAttendingPerson', u'Лечащий врач'),
                    (u'tabPassport', u'Паспортные данные'),
                    (u'tabPassport.edtDocSerialRight', u'Второе поле серии'),
                    (u'tabPassport.cmbRegDistrict', u'Район места регистрации'),
                    (u'tabPassport.cmbLocDistrict', u'Район места жительства'),
                    (u'tabPassport.gbLocAddress', u'Адрес проживания'),
                    (u'tabPassport.lblDocDate', u'Дата выдачи документа'),
                    (u'tabPassport.lblWhoExtraditedDoc', u'Место выдачи документа'),
                    (u'tabPassport.lblCompulsoryPolisName', u'Название полиса ОМС'),
                    (u'tabPassport.lblCompulsoryPolisNote', u'Примечения полиса ОМС'),
                    (u'tabPassport.lblBirthPlace', u'Место рождения'),
                    (u'tabSocStatus', u'Соц.cтатус'),
                    (u'tabAttach', u'Прикрепление'),
                    (u'tabWork', u'Занятость'),
                    (u'tabWork.lblWorOrganisationINN', u'ИНН'),
                    (u'tabWork.lblWorOrganisationOGRN', u'ОГРН'),
                    (u'tabWork.lblWorkOKVED', u'ОКВЭД'),
                    (u'tabWork.edtOKVEDName', u'ОКВЭД свободный ввод'),
                    (u'tabDocs', u'Документы'),
                    (u'tabDocs.tabDocsSocSatus', u'Соц.статус'),
                    (u'tabDocs.tabPaymentScheme', u'Именной договор'),
                    (u'tabFeature', u'Особенности'),
                    (u'tabIdentification', u'Идентификаторы'),
                    (u'tabRelations', u'Связи'),
                    (u'tabDispanserization', u'Дополнительная диспансеризация'),
                    (u'tabContacts', u'Прочее'),
                    (u'tabContacts.lblInfoSource', u'Получили информацию о нашем учреждении'),
                    (u'tabQuoting', u'Квоты'),
                    (u'tabDiagnosises', u'Диагнозы'),
                    (u'tabDisability', u'Льготы/Инвалидность'),
                    (u'tabDisability.chkIncapacity', u'Недееспособен'),
                    (u'tabMisdemeanor', u'Правонарушения'),
                    (u'tabMisdemeanor.chkConviction', u'Судимость до обращения'),
                    (u'tabSuicide', u'Суицид'),
                    (u'tabMonitoring', u'Вид наблюдения'),
                    (u'tabFeature.lblBloodType', u'Группа крови'),
                    (u'tabFeature.lblBloodTypeDate', u'Дата уст. группы крови'),
                    (u'tabFeature.lblBloodTypeNotes', u'Прим. по группе крови'),
                    (u'tabFeature.lblGrowth', u'Рост при рождении'),
                    (u'tabFeature.lblWeight', u'Вес при рождении'),
                    (u'tabFeature.lblEmbryonalPeriodWeek', u'Неделя эмбр-го периода'),
                    (u'tabFeature.lblDiagNames', u'Диагноз'),
                    (u'tabForeignHospitalization', u'Госпитализации в др. ЛПУ'),
                    (u'lblPesHeight', u'НИИ Петрова: рост'),
                    (u'lblPesWeight', u'НИИ Петрова: вес'),
                    (u'policyType', u'Тип полиса'),
                    (u'policyType.OMC', u'ОМС'),
                    (u'policyType.DMC', u'ДМС'),
                    (u'policyType.franchis', u'ДМС Ф')
                    ]
        if QtGui.qApp.defaultKLADR().startswith('23'):
            nameList.append((u'btnUEK', u'кнопка УЭК'))
        return cls.normalizeHiddableChildren(nameList)

    def makeSerial(self, docTypeId, serialLeft, serialRight):
        if self.useInputMask:
            db = QtGui.qApp.db
            docTypeCode = forceInt(db.translate(db.table('rbDocumentType'), 'id', docTypeId, 'code'))
            if docTypeCode > 19:
                return (serialLeft + ' ' + serialRight).strip()
            for item in self.maskTemplates:
                if item['code'] == docTypeCode:
                    return (serialLeft + item['delimiter'] + serialRight).strip()
        else:
            if forceStringEx(serialRight) == '-':
                return (serialLeft + serialRight).strip()
            return (serialLeft + ' ' + serialRight).strip()

    def savePreferences(self):
        preferences = CItemEditorBaseDialog.savePreferences(self)
        preferences['compulsorypolicyvisible'] = toVariant(self._compulsoryPolicyVisible) if not self._compulsoryPolicyVisible is None else toVariant(True)
        preferences['voluntarypolicyvisible'] = toVariant(self._voluntaryPolicyVisible) if not self._voluntaryPolicyVisible is None else toVariant(True)
        return preferences

    def loadPreferences(self, preferences):
        CItemEditorBaseDialog.loadPreferences(self, preferences)
        self._compulsoryPolicyVisible = forceBool(preferences.get('compulsorypolicyvisible', True))
        self._voluntaryPolicyVisible = forceBool(preferences.get('voluntarypolicyvisible', True))
        self.setPolicyWidgetsVisible(self.lblCompulsoryPolicy, self.frmCompulsoryPolicy, self._compulsoryPolicyVisible)
        self.setPolicyWidgetsVisible(self.lblVoluntaryPolicy, self.frmVoluntaryPolicy, self._voluntaryPolicyVisible)

    def checkPolicyCorrect(self):
        if not QtGui.qApp.userHasRight(Users.Rights.urAccessCrossingDates):
            if len(self.tblPolicies.model().items()) == 1:
                return True
            for x in self.tblPolicies.model().items():
                if forceDate(x.value('begDate')) != QtCore.QDate():
                    for y in self.tblPolicies.model().items():
                        if x == y:
                            break

                        begX = forceDate(x.value('begDate'))
                        endX = forceDate(x.value('endDate'))

                        begY = forceDate(y.value('begDate'))
                        endY = forceDate(y.value('endDate'))

                        if endY != QtCore.QDate() and endX != QtCore.QDate():
                            if (begX <= begY < endX and endX > endY) or (begX < endY < endX and begX < begY):
                                return False
                            elif (begY <= begX < endY and endY > endX) or (begY < endX < endY and begY < begX):
                                return False
                        else:
                            if endX == QtCore.QDate() and (begY <= begX < endY or (begX >= begY and begX > endY)):
                                return False
                            elif endY == QtCore.QDate() and (begX <= begY < endX or (begY >= begX and begY > endX)):
                                return False
        return True

    def checkContacts(self):
        if not QtGui.qApp.userHasRight(Users.Rights.urRegWithEmptyContacts) and not self.tblContacts.model().items():
            return False
        else:
            return True

    def getClientInfoForAttach(self):
        db = QtGui.qApp.db
        lastName = trimNameSeparators(nameCase(forceStringEx(self.edtLastName.text())), 'lastName') or None
        firstName = trimNameSeparators(nameCase(forceStringEx(self.edtFirstName.text())), 'firstName') or None
        patrName = trimNameSeparators(nameCase(forceStringEx(self.edtPatrName.text())), 'patrName') or None
        birthDate = self.edtBirthDate.date() or None
        sex = formatSex(self.cmbSex.currentIndex() or 0)
        SNILS = formatSNILS(forceStringEx(self.edtSNILS.text()).replace('-', '').replace(' ', '')) or None
        docType = forceInt(db.translate('rbDocumentType', 'id', self.cmbDocType.value(), 'code')) or 0
        docSerial = ' '.join([forceStringEx(self.edtDocSerialLeft.text()), forceStringEx(self.edtDocSerialRight.text())]).strip() or None
        docNumber = forceStringEx(self.edtDocNumber.text()) or None
        policyKind = forceInt(db.translate('rbPolicyKind', 'id', self.cmbCompulsoryPolisKind.value(), 'regionalCode')) or 0
        policySerial = forceStringEx(self.edtCompulsoryPolisSerial.text()) or None
        policyNumber = forceStringEx(self.edtCompulsoryPolisNumber.text()) or None

        checkList = [
            (lastName, u'фамилию', self.edtLastName),
            (firstName, u'имя', self.edtFirstName),
            (birthDate, u'дату рождения', self.edtBirthDate),
            (sex, u'пол', self.cmbSex),
            (any((docType, docNumber, policyKind, policyNumber)), u'документ или полис ОМС', self.cmbDocType),
            (not docType or docNumber, u'номер документа', self.edtDocNumber),
            (not policyKind or policyNumber, u'номер полиса ОМС', self.edtCompulsoryPolisNumber),
        ]

        if not all(value or self.checkInputMessage(message, False, widget) for value, message, widget in checkList):
            return None

        return AttachedClientInfo(lastName, firstName, patrName, birthDate, sex, SNILS,
                                  doc=DocumentInfo(docSerial, docNumber, docType),
                                  policy=PolicyInfo(policySerial, policyNumber, policyKind))

    def requestClientAttaches(self):
        clientInfo = self.getClientInfoForAttach()
        if clientInfo is not None:
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                attachResult = CR23AttachExchange.getClientAttaches(CR23ClientAttachService.createConnection(), clientInfo)
            finally:
                QtGui.QApplication.restoreOverrideCursor()

            if attachResult.hasErrors():
                QtGui.QMessageBox.warning(self, u'Сервис "Прикрепленное население": ОШИБКА', attachResult.errorMessage())
            else:
                clientInfoTFOMS = attachResult.result
                if not clientInfoTFOMS.attaches:
                    QtGui.QMessageBox.information(self, u'Сервис "Прикрепленное население"', u'Данные о прикреплении не найдены.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                else:
                    buttonRole = self.showClientAttachInfo(clientInfoTFOMS)
                    if buttonRole == QtGui.QMessageBox.AcceptRole:
                        attachesTF = clientInfoTFOMS.attaches
                        for attachTF in attachesTF:
                            if not CBookkeeperCode.isExternalOrgCode(attachTF.orgCode):
                                self.modelAttaches.addAttach(attachTF)
                            else:
                                for item in self.modelAttaches.items():
                                    if item.value('endDate').isNull():
                                        begDate = forceDate(item.value('begDate'))
                                        item.setValue('endDate', toVariant(max(begDate, attachTF.begDate)))
                                        item.setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.Deattach_ByTFOMS))
                                        item.setValue('errorCode', toVariant(''))

    def showClientAttachInfo(self, clientInfo):
        db = QtGui.qApp.db

        clientName = formatName(clientInfo.lastName, clientInfo.firstName, clientInfo.patrName)
        birthDate = forceDate(clientInfo.birthDate).toString('dd.MM.yyyy')

        doc = clientInfo.document
        docStr = u'{type}, {serial}{number}'.format(
            type=forceString(db.translate('rbDocumentType', 'code', doc.type, 'name')) or doc.type,
            serial=(u'серия: %s, ' % doc.serial if doc.serial else u''),
            number=(u'номер: %s' % doc.number))

        policy = clientInfo.policy
        policyStr = u'{type}, {serial}{number}'.format(
            type=CAttachPolicyType.nameMap.get(policy.type) or u'вид: {type}'.format(type=policy.type),
            serial=(u'серия: %s, ' % policy.serial if policy.serial else u''),
            number=(u'номер: %s' % policy.number))

        attach = clientInfo.attaches[0]
        isExternal = CBookkeeperCode.isExternalOrgCode(attach.orgCode)
        orgId, orgStructureId = CBookkeeperCode.getOrgStructure(attach.orgCode, attach.sectionCode)
        attachDate = forceDate(attach.begDate)
        attachType = CAttachType.getName(attach.attachType or 0)
        attachOrgName = forceString(db.translate('Organisation', 'id', orgId, 'shortName'))
        attachSectionName = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'name'))

        attachOrgStr = u'<b>{name}</b>(код {code})'.format(name=(attachOrgName + ' ') if attachOrgName else '',
                                                           code=attach.orgCode)
        attachSectionStr = u'<b>{name}</b>(код {code})'.format(name=(attachSectionName + ' ') if attachSectionName else '',
                                                               code=attach.sectionCode)

        def formatAttachDate(date):
            dateStr = forceString(forceDate(date).toString('dd.MM.yyyy'))
            return u'<font color=red>%s</font>' % dateStr if date < QtCore.QDate.currentDate().addYears(-1) else dateStr

        attachStr = u"Прикрепление к {isExternal}МО: {org}<br/>" \
                    u"Участок: {section}<br/>" \
                    u"Тип: <b>{type}</b><br/>" \
                    u"Дата начала прикрепления: <b>{date}</b>".format(isExternal=u'внешней ' if isExternal else u'',
                                                                      org=attachOrgStr,
                                                                      type=attachType,
                                                                      section=attachSectionStr,
                                                                      date=formatAttachDate(attachDate))

        msg = u"<b>{clientName}</b>, {birthDate}<br/>" \
              u"Документ: {docStr}<br/>" \
              u"Полис: {policyStr}<br/><br/>" \
              u"{attachStr}".format(clientName=clientName,
                                    birthDate=birthDate,
                                    docStr=docStr,
                                    policyStr=policyStr,
                                    attachStr=attachStr)

        QtGui.QApplication.restoreOverrideCursor()
        mbox = QtGui.QMessageBox(self)
        mbox.setWindowTitle(u'Информация о прикреплении пациента')
        mbox.setText(msg)
        mbox.addButton(QtGui.QPushButton(u'Закрыть'), QtGui.QMessageBox.RejectRole)
        mbox.addButton(QtGui.QPushButton(u'Добавить прикрепление'), QtGui.QMessageBox.AcceptRole)

        mbox.exec_()

        return mbox.buttonRole(mbox.clickedButton())

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAttaches_currentChanged(self, current, previous):
        self.btnSyncClientAttach.setEnabled(current.isValid() and 0 <= current.row() < len(self.modelAttaches.items()))

    @QtCore.pyqtSlot()
    def onBtnSyncClientAttach(self):
        return self.syncClientAttach(manualSync=True)

    def syncClientAttach(self, manualSync=False):
        if not self.isTabAttachAlreadyLoad:
            self.initTabAttach()

        if self.itemId():
            self.modelAttaches.saveItems(self.itemId())  # сохраняем, т.к. нужен ClientAttach.id для маппинга ошибок

        isTabAttach = self.tabWidget.currentWidget() == self.tabAttach

        notSyncedAttaches = self.modelAttaches.getNotSyncedAttaches()
        if notSyncedAttaches:
            clientRecord = self.getRecord()
            documents = self.modelIdentificationDocs.items()
            policies = self.modelPolicies.items()

            if not documents and not policies:
                res = self.checkInputMessage(u'документ, удостоверяющий личность', False, self.tblIdentificationDocs)
                if not res:
                    return False

            if not policies:
                res = self.checkInputMessage(u'полис', True, self.tblPolicies)
                if not res:
                    return False

            attachesToSync = []
            for attachRecord, deattachQuery in notSyncedAttaches:
                attachInfo = CR23AttachExchange.makeClientAttachInfo(attachRecord, deattachQuery)
                if attachInfo.sectionCode:
                    attachesToSync.append(attachInfo)
                else:
                    orgStructureCode = forceString(QtGui.qApp.db.translate('OrgStructure', 'id', forceRef(attachRecord.value('orgStructure_id')), 'code'))
                    QtGui.QMessageBox.warning(self, u'Внимание',
                                              u'В подразделении <b>"{0}"</b> не указан код участка'.format(orgStructureCode))

            if attachesToSync:
                try:
                    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                    clientInfo = CR23AttachExchange.makeClientInfo(clientRecord, documents[-1] if documents else None, policies[-1] if policies else None)
                    connection = CR23ClientAttachService.getConnection()
                    syncedList, errorList, attachErrorMap, deattachQueryResult = CR23AttachExchange.syncClientAttach(connection, clientInfo, attachesToSync)
                finally:
                    QtGui.QApplication.restoreOverrideCursor()

                for item, _ in notSyncedAttaches:
                    itemId = forceRef(item.value('id'))
                    if itemId in syncedList:
                        item.setValue('errorCode', toVariant(''))
                        item.setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.Synced))
                    elif itemId in attachErrorMap:
                        item.setValue('errorCode', toVariant(attachErrorMap[itemId]))
                        item.setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.NotSynced))

                if self.itemId():
                    self.modelAttaches.saveItems(self.itemId())

                if isTabAttach:
                    title = u'Синхронизация прикрепления с ТФОМС'

                    msgList = []
                    if deattachQueryResult:
                        msgList.append(u'<br/>'.join(u'Уведомление № {0} от {1} успешно отправлено'.format(deattachQuery.number, deattachQuery.date.toString('dd.MM.yyyy'))
                                                     for deattachQuery, sent in deattachQueryResult.iteritems() if sent))

                    if errorList:
                        QtGui.QMessageBox.warning(self, title,
                                                  u'<br/>'.join(msgList + [u'<b>Ошибка в передаче данных:</b>'] + [u'<i>%s</i>' % error for error in errorList]))
                    elif attachErrorMap:
                        errorCount = len(attachErrorMap)
                        errorMsg = u'Ошибка в передаче данных (<b>{count}</b> {records}): см. <i>"Описание ошибки"</i>'.format(
                            count=errorCount,
                            records=agreeNumberAndWord(errorCount, [u'запись', u'записи', u'записей'])
                        )
                        answer = QtGui.QMessageBox.warning(self, title, u'<br/>'.join(msgList + [errorMsg]), QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        if answer == QtGui.QMessageBox.Cancel:
                            return False
                    elif syncedList and manualSync:
                        QtGui.QMessageBox.information(self, title, u'<br/>'.join(msgList + [u'Данные переданы успешно']))

        elif manualSync and isTabAttach:
            QtGui.QMessageBox.information(self, u'Синхронизация прикрепления с ТФОМС', u'Нет данных для синхронизации')

        return True

    def save(self):
        try:
            db = QtGui.qApp.db
            db.transaction(checkIsInit=True)
            try:
                record = self.getRecord()
                clientId = db.insertOrUpdate('Client', record)

                regAddressRecord, regAddress, regAddressRecordChanged = self.getAddressRecord(clientId, 0)
                if regAddressRecordChanged and regAddressRecord is not None:
                    if self.__regAddressRecord is not None:
                        self.__regAddressRecord.setValue('deleted', 1)
                        db.insertOrUpdate('ClientAddress', self.__regAddressRecord)
                    db.insertOrUpdate('ClientAddress', regAddressRecord)

                locAddressRecord, locAddress, locAddressRecordChanged = self.getAddressRecord(clientId, 1)
                if locAddressRecordChanged and locAddressRecord is not None:
                    if self.__locAddressRecord:
                        self.__locAddressRecord.setValue('deleted', 1)
                        db.insertOrUpdate('ClientAddress', self.__locAddressRecord)
                    db.insertOrUpdate('ClientAddress', locAddressRecord)

                if self.isTabSocStatusAlreadyLoad:
                    self.modelSocStatuses.saveItems(clientId)
                if self.isTabAttachAlreadyLoad:
                    self.modelAttaches.saveItems(clientId)
                if self.isTabRelationsAlreadyLoad:
                    self.modelDirectRelations.saveItems(clientId)
                    self.modelBackwardRelations.saveItems(clientId)
                if self.isTabFeatureAlreadyLoad:
                    self.modelAllergy.saveItems(clientId)
                    self.modelIntoleranceMedicament.saveItems(clientId)
                    self.modelClientAnthropometric.saveItems(clientId)
                    self.modelClientCheckup.saveItems(clientId)
                if self.isTabWorkAlreadyLoad:
                    workRecord, work, workRecordChanged = self.getWorkRecord(clientId)
                    if workRecordChanged and workRecord is not None:
                        workRecordId = db.insertOrUpdate('ClientWork', workRecord)
                        self.modelOldWorks.setFilter(db.joinAnd([self.modelOldWorks.filter or '1',
                                                                 'id != %d' % workRecordId]))
                    elif workRecord is not None:
                        workRecordId = forceRef(workRecord.value('id'))
                    else:
                        workRecordId = None
                    if workRecordId is not None:
                        self.modelWorkHurts.saveItems(workRecordId)
                        self.modelWorkHurtFactors.saveItems(workRecordId)
                    self.modelOldWorks.saveItems(clientId)
                    CClientEditDialog.prevWork = work
                self.syncIdentificationDocs()

                origin = self.edtWhoExtraditedDoc.text()
                if not origin.isEmpty():
                    variantOrigin = QtCore.QVariant(origin)
                    completionColumn = self._docOriginCompleter.completionColumn()
                    startIndex = self._docOriginCompleterModel.index(0,
                                                                     completionColumn)
                    if not self._docOriginCompleterModel.match(startIndex,
                                                               QtCore.Qt.DisplayRole,
                                                               variantOrigin):
                        completerTable = db.table('rbTextDataCompleter')
                        newRecord = completerTable.newRecord()
                        newRecord.setValue(u'code', QtCore.QVariant(u'documentOrigin'))
                        newRecord.setValue(u'name', variantOrigin)
                        db.insertRecord(completerTable, newRecord)

                if self.edtBirthPlace.text():
                    placeOrigin = QtCore.QVariant(self.edtBirthPlace.text())
                    completionColumn = self._birthPlaceCompleter.completionColumn()
                    startIndex = self._birthPlaceCompleterModel.index(0,
                                                                      completionColumn)
                    if not self._birthPlaceCompleterModel.match(startIndex,
                                                                QtCore.Qt.DisplayRole,
                                                                placeOrigin):
                        completerTable = db.table('rbTextDataCompleter')
                        newRecord = completerTable.newRecord()
                        newRecord.setValue(u'code', QtCore.QVariant(u'birthPlace'))
                        newRecord.setValue(u'name', placeOrigin)
                        db.insertRecord(completerTable, newRecord)

                updateUsedIndex(u'rbDocumentType', self.documentTypeId)
                self.modelIdentificationDocs.saveItems(clientId)
                self.syncPolicies()
                self.modelPolicies.cleanUpEmptyItems()
                self.modelPolicies.saveItems(clientId)
                if self.isTabDocsAlreadyLoad:
                    self.modelPaymentScheme.saveItems(clientId)
                    self.modelSocStatusDocs.saveItems(clientId)
                self.modelContacts.saveItems(clientId)

                tableAccSystem = db.table('rbAccountingSystem')
                tableClientIdent = db.table('ClientIdentification')
                tableCounter = db.table('rbCounter')

                if self.isTabIdentificationAlreadyLoad:
                    self.modelClientIdentification.saveItems(clientId)
                accSystemCounterCond = [
                    tableAccSystem['counter_id'].isNotNull(),
                    tableAccSystem['id'].notInInnerStmt(db.selectStmt(tableClientIdent,
                                                                      tableClientIdent['accountingSystem_id'],
                                                                      tableClientIdent['client_id'].eq(clientId)))
                ]
                accountingSystems = db.getRecordList(tableAccSystem, [tableAccSystem['id'], tableAccSystem['counter_id'], tableAccSystem['autoIdentificator']], accSystemCounterCond)
                for record in accountingSystems:
                    newRecord = self.modelClientIdentification.getEmptyRecord()
                    accountingSystemId = forceRef(record.value('id'))
                    counterId = forceRef(record.value('counter_id'))
                    identifier = getAccountingSystemIdentifier(counterId)
                    if forceInt(record.value('autoIdentificator')) == 1:
                        newRecord.setValue('identifier', toVariant(identifier))
                        newRecord.setValue('client_id', toVariant(clientId))
                        newRecord.setValue('accountingSystem_id', toVariant(accountingSystemId))
                        newRecord.setValue('deleted', toVariant(0))
                        db.insertRecord('ClientIdentification', newRecord)
                        recCounter = db.getRecordEx(tableCounter, '*', tableCounter['id'].eq(counterId))
                        if recCounter:
                            recCounter.setValue('value', toVariant(forceInt(recCounter.value('value')) + 1))
                            db.updateRecord(tableCounter, recCounter)

                if self.edtPesHeight.text():
                    table = db.table('ClientBodyStats')
                    record = db.getRecordEx('ClientBodyStats', table['client_id'].eq(clientId))
                    isNew = False
                    if not record:
                        record = table.newRecord()
                        isNew = True
                    elif not forceRef(record.value('client_id')):
                        record = table.newRecord()
                        isNew = True
                    record.setValue('client_id', toVariant(clientId))
                    if isNew:
                        record.setValue('createDateTime', toVariant(QtCore.QDateTime.currentDateTime()))
                    else:
                        record.setValue('modifyDateTime', toVariant(QtCore.QDateTime.currentDateTime()))
                    record.setValue('weight', toVariant(self.edtPesWeight.text()))
                    record.setValue('height', toVariant(self.edtPesHeight.text()))
                    db.insertOrUpdate('ClientBodyStats', record)

                if self.isTabDispanserizationAlreadyLoad:
                    self.modelDispanserization.saveItems(clientId)
                if self.isTabQuotingAlreadyLoad:
                    if not self.isTabAttachAlreadyLoad:  # for modelClientQuoting
                        self.on_tabWidget_currentChanged(2)  # for modelClientQuoting
                    if regAddress['useKLADR']:
                        self.modelClientQuoting.setNewRegCityCode(regAddress['KLADRCode'])
                    self.modelClientQuoting.saveItems(clientId)
                if self.isTabDiagnosisesAlreadyLoad:
                    self.modelClientMainDiagnosises.saveItems(clientId)
                    self.modelClientSecondaryDiagnosises.saveItems(clientId)
                if self.isTabDisabilityAlreadyLoad:
                    self.modelClientDisability.saveItems(clientId)
                    self.modelClientBenefits.saveItems(clientId)

                if self.isTabMisdemeanorAlreadyLoad:
                    self.modelClientMisdemeanor.saveItems(clientId)
                    if QtGui.qApp.isPNDDiagnosisMode():
                        self.modelClientCompulsoryTreatment.saveItems(clientId)
                if self.isTabSuicideAlreadyLoad:
                    self.modelClientSuicide.saveItems(clientId)
                if self.isTabMonitoringAlreadyLoad:
                    self.modelClientMonitoring.saveItems(clientId)
                if self.isTabForeignHospitalizationAlreadyLoad:
                    self.modelForeignHospitalization.saveItems(clientId)

                self.saveClientRemarks(clientId)

                if self.dispCode:
                    tmpRec = db.getRecordEx('ClientDispanserization', 'id', 'client_id = %s and date_end = \'%s\'' % (clientId, self.dispEndDate))
                    if not tmpRec:
                        dispRecord = db.table('ClientDispanserization').newRecord()
                        dispRecord.setValue('create_datetime', toVariant(QtCore.QDateTime.currentDateTime()))
                        dispRecord.setValue('code', toVariant(self.dispCode))
                        dispRecord.setValue('client_id', toVariant(clientId))
                        dispRecord.setValue('date_begin', toVariant(self.dispBegDate))
                        dispRecord.setValue('date_end', toVariant(self.dispEndDate))
                        dispRecord.setValue('codeMO', toVariant(self.dispCodeMO))
                        db.insertRecord('ClientDispanserization', dispRecord)
                if self.isTabContactsAlreadyLoad:
                    self.saveInfoSourceRecord(clientId)
                db.commit()
            except:
                QtGui.qApp.logCurrentException()
                db.rollback()
                raise
            self.setItemId(clientId)
            self.__regAddressRecord = regAddressRecord
            self.__regAddress = regAddress
            self.__locAddressRecord = locAddressRecord
            self.__locAddress = locAddress

            syncAttachResult = (not syncAttachesOnSave() or
                                self.syncClientAttach(False) or
                                self.checkValueMessage(u'Ошибка отправки прикрепления', True, self.tblAttaches))
            if not syncAttachResult:
                return False

            self.setIsDirty(False)
            CClientEditDialog.prevAddress = (regAddress,
                                             forceStringEx(regAddressRecord.value('freeInput')),
                                             forceBool(regAddressRecord.value('isVillager')),
                                             locAddress,
                                             forceStringEx(locAddressRecord.value('freeInput')),
                                             forceBool(regAddressRecord.value('isVillager')))
            QtGui.qApp.emitCurrentClientInfoChanged()
            return clientId
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self,
                                       u'',
                                       unicode(e),
                                       QtGui.QMessageBox.Close)
            return None

    def supportedClientRemarks(self):
        return [(self.chkRegisterFirstInPND, 'registerFirstInPND'),
                (self.chkExistsOnlyTempRegistration, 'existsOnlyTempRegistration'),
                (self.chkIncapacity, 'incapacity'),
                (self.chkConviction, 'conviction')]

    def loadClientRemarks(self, clientId):
        db = QtGui.qApp.db

        tableRemark = db.table('ClientRemark')
        tableRemarkType = db.table('rbClientRemarkType')
        queryTable = tableRemark.innerJoin(tableRemarkType, tableRemarkType['id'].eq(tableRemark['remarkType_id']))

        cond = [tableRemark['client_id'].eq(clientId),
                tableRemarkType['flatCode'].inlist([item[1] for item in self.supportedClientRemarks()])]
        existsRemarks = db.getColumnValues(table=queryTable,
                                           column=tableRemarkType['flatCode'],
                                           where=cond,
                                           order=[tableRemarkType['flatCode'],
                                                  tableRemarkType['code'],
                                                  tableRemark['date']])
        for checkBox, flatCode in self.supportedClientRemarks():
            checkBox.setChecked(flatCode in existsRemarks)

    def saveClientRemarks(self, clientId):
        db = QtGui.qApp.db

        tableRemark = db.table('ClientRemark')
        tableRemarkType = db.table('rbClientRemarkType')
        queryTable = tableRemark.innerJoin(tableRemarkType, tableRemarkType['id'].eq(tableRemark['remarkType_id']))

        cond = [tableRemark['client_id'].eq(clientId),
                tableRemarkType['flatCode'].inlist([item[1] for item in self.supportedClientRemarks()])]
        existsRemarks = db.getColumnValues(table=queryTable,
                                           column=tableRemarkType['flatCode'],
                                           where=cond,
                                           order=[tableRemarkType['flatCode'],
                                                  tableRemarkType['code'],
                                                  tableRemark['date']])

        for checkBox, flatCode in self.supportedClientRemarks():
            if checkBox.isChecked() and flatCode not in existsRemarks:
                typeId = getClientRemarkTypeIdByFlatCode(flatCode, checkBox.text())
                newRecord = tableRemark.newRecord()
                newRecord.setValue('remarkType_id', toVariant(typeId))
                newRecord.setValue('date', toVariant(QtCore.QDate.currentDate()))
                newRecord.setValue('client_id', toVariant(clientId))
                db.insertRecord(tableRemark, newRecord)
            elif not checkBox.isChecked() and flatCode in existsRemarks:
                typeId = getClientRemarkTypeIdByFlatCode(flatCode, checkBox.text())
                db.deleteRecord(tableRemark, [tableRemark['client_id'].eq(clientId),
                                              tableRemark['remarkType_id'].eq(typeId)])

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        clientId = self.itemId()
        self.edtLastName.setText(forceString(record.value('lastName')))
        self.edtFirstName.setText(forceString(record.value('firstName')))
        self.edtPatrName.setText(forceString(record.value('patrName')))
        self.edtGrowth.setValue(forceInt(record.value('growth')))
        self.edtWeight.setValue(forceInt(record.value('weight')))
        self.edtBirthPlace.setText(forceString(record.value('birthPlace')))
        self.edtBirthDate.setDate(forceDate(record.value('birthDate')))
        self.edtBirthTime.setTime(forceTime(record.value('birthTime')))
        self.edtEmbryonalPeriodWeek.setValue(forceInt(record.value('embryonalPeriodWeek')))
        self.edtDiagNames.setText(forceString(record.value('diagNames')))
        self.cmbSex.setCurrentIndex(forceInt(record.value('sex')))
        self.edtSNILS.setText(forceString(record.value('SNILS')))
        self.edtIIN.setText(forceString(record.value('IIN')))
        self.edtNotes.setPlainText(forceString(record.value('notes')).replace('<br>', '\n'))
        self.cmbAttendingPerson.setValue(forceRef(record.value('attendingPerson_id')))
        self.setRegAddressRecord(getClientAddress(clientId, 0))
        self.setLocAddressRecord(getClientAddress(clientId, 1))
        self.setDocumentRecord(getClientDocument(clientId))
        if not self.lblPesWeight.isHidden():
            self.setBodyStats(getClientBodyStats(clientId))
        self.loadClientRemarks(clientId)
        self.modelContacts.loadItems(clientId)
        self.modelIdentificationDocs.loadItems(clientId)
        self.modelPolicies.loadItems(clientId)
        # self.on_modelPolicies_policyChanged()
        self.bloodType_id = forceRef(record.value('bloodType_id'))
        self.bloodDate = forceDate(record.value('bloodDate'))
        self.bloodNotes = forceString(record.value('bloodNotes'))
        self.edtChartBeginDate.setDate(forceDate(record.value('chartBeginDate')))
        self.setIsDirty(False)
        self.regAddressInfo = {}
        self.locAddressInfo = {}
        self.chkUnconscious.setChecked(forceBool(record.value('isUnconscious')))
        self.reinitLoadedTab()

        if QtGui.qApp.userHasRight(Users.Rights.urEditImplantsAndProsthesis):
            self.chkHasImplants.setChecked(forceBool(record.value('hasImplants')))
            self.chkHasProsthesis.setChecked(forceBool(record.value('hasProsthesis')))

        # disabled edit mode
        self.isConfirmSendingData = False  # Используется в self.getRecord() строкой ниже
        if not QtGui.qApp.userHasRight(Users.Rights.urAllowEditAllRegistryCard) \
                and forceInt(self.getRecord().value('modifyPerson_id')) != QtGui.qApp.userId:  # \
                # and self._id:
            self.edtLastName.setEnabled(False)
            self.edtFirstName.setEnabled(False)
            self.edtPatrName.setEnabled(False)
            self.edtBirthDate.setEnabled(False)
            self.edtBirthTime.setEnabled(False)
            self.edtSNILS.setEnabled(False)
            self.cmbSex.setEnabled(False)

    def reinitLoadedTab(self):
        self.isTabSocStatusAlreadyLoad = False
        self.isTabAttachAlreadyLoad = False
        self.isTabWorkAlreadyLoad = False
        self.isTabDocsAlreadyLoad = False
        self.isTabFeatureAlreadyLoad = False
        self.isTabIdentificationAlreadyLoad = False
        self.isTabRelationsAlreadyLoad = False
        self.isTabContactsAlreadyLoad = False
        self.isTabQuotingAlreadyLoad = False
        self.isTabDiagnosisesAlreadyLoad = False
        self.isTabDisabilityAlreadyLoad = False
        self.isTabMisdemeanorAlreadyLoad = False
        self.isTabSuicideAlreadyLoad = False
        self.isTabMonitoringAlreadyLoad = False
        self.isTabRelationsAlreadyLoad = False
        self.isTabDispanserizationAlreadyLoad = False
        self.on_tabWidget_currentChanged(self.tabWidget.currentIndex())

    @QtCore.pyqtSlot(int)
    def on_cmbSex_currentIndexChanged(self, sex):
        if self.isTabRelationsAlreadyLoad:
            self.modelDirectRelations.setDirectRelationFilter(sex)
            self.modelBackwardRelations.setBackwardRelationFilter(sex)
            # focusWidget = QtGui.qApp.focusWidget()
            # self.on_tabWidget_currentChanged(self.tabWidget.indexOf(self.tabRelations))
            # if focusWidget:
            #     focusWidget.setFocus(QtCore.Qt.MouseFocusReason)


    def setRegAddressRecord(self, record):
        self.__regAddressRecord = record
        if record:
            addressId = forceRef(record.value('address_id'))
            if addressId:
                self.__regAddress = getAddress(addressId)
            else:
                self.__regAddress = None
            self.setRegAddress(self.__regAddress, forceString(record.value('freeInput')), forceBool(record.value('isVillager')))
            self.cmbRegDistrict.setValue(forceRef(record.value('district_id')))
        else:
            self.chkRegKLADR.setChecked(False or QtGui.qApp.isAddressOnlyByKLADR())
            self.__regAddress = None
            self.setRegAddress(self.__regAddress, '')
            self.cmbRegDistrict.setValue(None)

    def setRegAddress(self, regAddress, freeInput, isVillager=False):
        self.chkRegKLADR.setChecked(regAddress is not None or QtGui.qApp.isAddressOnlyByKLADR())
        self.edtRegFreeInput.setText(freeInput)
        self.chkRegIsVillager.setChecked(bool(isVillager))
        self.cmbCompulsoryPolisCompany._popup.setRegAdress(regAddress)
        if regAddress:
            self.cmbRegCity.setCode(regAddress.KLADRCode)
            self.cmbRegStreet.setCity(regAddress.KLADRCode)
            self.cmbRegStreet.setCode(regAddress.KLADRStreetCode)
            self.edtRegHouse.setText(regAddress.number)
            self.edtRegCorpus.setText(regAddress.corpus)
            self.edtRegFlat.setText(regAddress.flat)
        else:
            self.cmbRegCity.setCode(QtGui.qApp.defaultKLADR())
            self.cmbRegStreet.setCity(QtGui.qApp.defaultKLADR())
            self.cmbRegStreet.setCode('')
            self.edtRegHouse.setText('')
            self.edtRegCorpus.setText('')
            self.edtRegFlat.setText('')

    def setRegAddressRelation(self, regAddress):
        if regAddress:
            self.edtRegFreeInput.setText(regAddress.get('regFreeInput', u''))
            self.chkRegIsVillager.setChecked(regAddress.get('regIsVillager', False))
            self.cmbRegCity.setCode(regAddress.get('regCity', u''))
            self.cmbRegStreet.setCode(regAddress.get('regStreet', u''))
            self.edtRegHouse.setText(regAddress.get('regHouse', u''))
            self.edtRegCorpus.setText(regAddress.get('regCorpus', u''))
            self.edtRegFlat.setText(regAddress.get('regFlat', u''))
            self.cmbRegDistrict.setValue(regAddress.get('districtId', None))

    def setLocAddressRecord(self, record):
        self.__locAddressRecord = record
        if record:
            addressId = forceRef(record.value('address_id'))
            if addressId:
                self.__locAddress = getAddress(addressId)
            else:
                self.__locAddress = None
            self.setLocAddress(self.__locAddress, forceString(record.value('freeInput')), forceBool(record.value('isVillager')))
            self.cmbLocDistrict.setValue(forceRef(record.value('district_id')))
        else:
            self.chkLocKLADR.setChecked(False or QtGui.qApp.isAddressOnlyByKLADR())
            self.__locAddress = None
            self.setLocAddress(self.__locAddress, '')
            self.cmbLocDistrict.setValue(None)

    def setLocAddress(self, locAddress, freeInput, isVillager=False):
        self.chkLocKLADR.setChecked(locAddress is not None or QtGui.qApp.isAddressOnlyByKLADR())
        self.edtLocFreeInput.setText(freeInput)
        self.chkLocIsVillager.setChecked(isVillager)
        if locAddress:
            self.cmbLocCity.setCode(locAddress.KLADRCode)
            self.cmbLocStreet.setCity(locAddress.KLADRCode)
            self.cmbLocStreet.setCode(locAddress.KLADRStreetCode)
            self.edtLocHouse.setText(locAddress.number)
            self.edtLocCorpus.setText(locAddress.corpus)
            self.edtLocFlat.setText(locAddress.flat)
        else:
            self.cmbLocCity.setCode(QtGui.qApp.defaultKLADR())
            self.cmbLocStreet.setCity(QtGui.qApp.defaultKLADR())
            self.cmbLocStreet.setCode('')
            self.edtLocHouse.setText('')
            self.edtLocCorpus.setText('')
            self.edtLocFlat.setText('')

    def setLocAddressRelation(self, locAddress):
        if locAddress:
            self.edtLocFreeInput.setText(locAddress.get('regFreeInput', u''))
            self.chkRegIsVillager.setChecked(locAddress.get('regIsVillager', False))
            self.cmbLocCity.setCode(locAddress.get('regCity', u''))
            self.cmbLocStreet.setCode(locAddress.get('regStreet', u''))
            self.edtLocHouse.setText(locAddress.get('regHouse', u''))
            self.edtLocCorpus.setText(locAddress.get('regCorpus', u''))
            self.edtLocFlat.setText(locAddress.get('regFlat', u''))
            self.cmbLocDistrict.setValue(locAddress.get('districtId', None))

    def setBodyStats(self, record):
        if record:
            self.edtPesWeight.setText(forceString(record.value('weight')))
            self.edtPesHeight.setText(forceString(record.value('height')))

    @staticmethod
    def analyzeSerialPart(docTypeId, serialLeft, serialRight):
        db = QtGui.qApp.db
        docTypeCode = forceInt(db.translate(db.table('rbDocumentType'), 'id', docTypeId, 'code'))
        if docTypeCode == 14 and len(serialLeft) == 4:  # for russian passport
            return serialLeft[:2], serialLeft[-2:]
        return serialLeft, serialRight

    def setInputMask(self, docTypeId):
        db = QtGui.qApp.db
        docTypeCode = forceInt(db.translate(db.table('rbDocumentType'), 'id', docTypeId, 'code'))
        for item in self.maskTemplates:
            if item['code'] == docTypeCode:
                self.edtDocSerialLeft.setInputMask(unicode(item['rule'][0]))
                self.edtDocSerialRight.setInputMask(unicode(item['rule'][1]))
                self.edtDocNumber.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(item['rule'][2]), self.edtDocNumber))
                self.edtDocSerialLeft.setFormat(0)
                self.edtDocSerialRight.setFormat(0)
                if item['onlyRomans']: self.edtDocSerialLeft.setFormat('onlyRomans');
                if item['onlyRuL']: self.edtDocSerialLeft.setFormat('onlyRu');
                if item['onlyRuR']: self.edtDocSerialRight.setFormat('onlyRu');
                return
        self.edtDocSerialLeft.setInputMask('')
        self.edtDocSerialRight.setInputMask('')
        self.edtDocNumber.setValidator(None)
        self.edtDocNumber.setInputMask('')
        self.edtDocSerialLeft.setFormat(0)
        self.edtDocSerialRight.setFormat(0)

    def setDocumentRecord(self, record):
        self.__documentRecord = record
        if record:
            docTypeId = forceInt(record.value('documentType_id'))
            self.cmbDocType.setValue(docTypeId)
            if self.isVisibleObject(self.edtDocSerialRight):
                serialLeft, serialRight = splitDocSerial(forceString(record.value('serial')), isCheckLastDash=True)
                serialLeft, serialRight = self.analyzeSerialPart(self.documentTypeId, serialLeft, serialRight)
                self.edtDocSerialRight.setText(serialRight)
            else:
                serialLeft = forceString(record.value('serial'))

            self.edtDocSerialLeft.setText(serialLeft)
            self.edtDocNumber.setText(forceString(record.value('number')))
            self.edtDocDate.setDate(forceDate(record.value('date')))
            self.edtWhoExtraditedDoc.setText(forceString(record.value('origin')))

            if self.useInputMask:
                self.setInputMask(self.documentTypeId)
        else:
            self.cmbDocType.setValue(self.documentTypeId)
            self.edtDocSerialLeft.setText('')
            self.edtDocSerialRight.setText('')
            self.edtDocNumber.setText('')
            self.edtDocDate.setDate(QtCore.QDate())
            self.edtWhoExtraditedDoc.setText('')

    def setPolicyRecord(self, record, isCompulsory):
        if record:
            policyId = forceRef(record.value('id'))
            serial = forceString(record.value('serial'))
            number = forceString(record.value('number'))
            insurer = forceRef(record.value('insurer_id'))
            insurerArea = forceString(QtGui.qApp.db.translate('Organisation', 'id', insurer, 'area'))
            polisType = forceRef(record.value('policyType_id'))
            polisKind = forceRef(record.value('policyKind_id'))
            name = forceString(record.value('name'))
            note = forceString(record.value('note'))
            begDate = forceDate(record.value('begDate'))
            endDate = forceDate(record.value('endDate'))
            dischargeDate = forceDate(record.value('dischargeDate'))
            insuranceAreaCode = forceString(record.value('insuranceArea'))
            franchisePercent = forceString(forceInt(record.value('franchisePercent')))
        else:
            policyId = None
            serial = ''
            number = ''
            insurer = None
            insurerArea = ''
            polisType = None
            polisKind = None
            name = ''
            note = ''
            begDate = QtCore.QDate()
            endDate = QtCore.QDate()
            dischargeDate = QtCore.QDate()
            insuranceAreaCode = None
            franchisePercent = '0'
        if not insuranceAreaCode:
            areaList = list(filter(lambda x: x, self.getAreaList(insuranceAreaCode, insurer, insurerArea)))
            insuranceAreaCode = areaList[0] if areaList else None
        if isCompulsory:
            if insuranceAreaCode:
                self.cmbCompulsoryInsuranceArea.setCode(insuranceAreaCode)
            self.edtCompulsoryPolisSerial.setText(serial)
            self.edtCompulsoryPolisNumber.setText(number)
            self.cmbCompulsoryPolisCompany.setValue(insurer)
            self.cmbCompulsoryPolisType.setValue(polisType)
            self.cmbCompulsoryPolisKind.setValue(polisKind)
            self.updateCompulsoryPolicyCompanyArea([insurerArea])
            self.edtCompulsoryPolisName.setText(name)
            self.edtCompulsoryPolisNote.setText(note)
            self.edtCompulsoryPolisBegDate.setDate(begDate)
            self.edtCompulsoryPolisEndDate.setDate(endDate)
            self.edtCompulsoryPolisDischargeDate.setDate(dischargeDate)
        else:
            if insuranceAreaCode:
                self.cmbVoluntaryInsuranceArea.setCode(insuranceAreaCode)
            self.policyIdDMCF = policyId
            self.edtVoluntaryPolisSerial.setText(serial)
            self.edtVoluntaryPolisNumber.setText(number)
            self.cmbVoluntaryPolisCompany.setValue(insurer)
            self.cmbVoluntaryPolisType.setValue(polisType)
            self.updateVoluntaryPolicyCompanyArea([insurerArea])
            self.edtVoluntaryPolisName.setText(name)
            self.edtVoluntaryPolisNote.setText(note)
            self.edtVoluntaryPolisBegDate.setDate(begDate)
            self.edtVoluntaryPolisEndDate.setDate(endDate)
            self.edtVoluntaryPolisDischargeDate.setDate(dischargeDate)
            self.edtDMCPercent.setText(franchisePercent)
            self.oldFranchisePercent = int(franchisePercent)
            self.newFranchisePercent = int(franchisePercent)

    def setWorkRecord(self, record):
        self.__workRecord = record
        if record:
            self.cmbWorkOrganisation.setValue(forceRef(record.value('org_id')))
            self.updateWorkOrganisationInfo()
            self.edtWorkOrganisationFreeInput.setText(forceString(record.value('freeInput')))
            self.edtWorkPost.setText(forceString(record.value('post')))
            self.cmbWorkOKVED.setText(forceString(record.value('OKVED')))
            self.edtWorkStage.setValue(forceInt(record.value('stage')))
            self.edtWorkNote.setText(forceString(record.value('note')))
        else:
            self.cmbWorkOrganisation.setValue(None)
            self.updateWorkOrganisationInfo()
            self.edtWorkOrganisationFreeInput.setText('')
            self.edtWorkPost.setText('')
            self.cmbWorkOKVED.setText('')
            self.edtWorkStage.setValue(0)
            self.edtWorkNote.setText('')

        if not QtGui.qApp.userHasRight(urEditClientWorkPlace) and self.cmbWorkOrganisation.value() == QtGui.qApp.currentOrgId():
            self.tabWork.setEnabled(False)

    def setWork(self, work):
        if work:
            self.cmbWorkOrganisation.setValue(work['organisationId'])
            self.updateWorkOrganisationInfo()
            self.edtWorkOrganisationFreeInput.setText(work['freeInput'])
            self.edtWorkPost.setText(work['post'])
            self.cmbWorkOKVED.setText(work['OKVED'])
            self.edtWorkStage.setValue(work['stage'])
            self.edtWorkNote.setText(work['note'])
        else:
            self.cmbWorkOrganisation.setValue(None)
            self.updateWorkOrganisationInfo()
            self.edtWorkOrganisationFreeInput.setText('')
            self.edtWorkPost.setText('')
            self.cmbWorkOKVED.setText('')
            self.edtWorkStage.setValue(0)
            self.edtWorkNote.setText('')

        if not QtGui.qApp.userHasRight(urEditClientWorkPlace) and self.cmbWorkOrganisation.value() == QtGui.qApp.currentOrgId():
            self.tabWork.setEnabled(False)

    @staticmethod
    def getDefaultDocumentType():
        record = QtGui.qApp.db.getRecordEx('rbDocumentType', 'id', 'rbDocumentType.isDefault = 1')
        if record is not None:
            return forceRef(record.value('id'))
        else:
            return None

    def getParamsRegAddress(self):
        self.regAddressInfo = {'regFreeInput': self.edtRegFreeInput.text(), 'regIsVillager': self.chkRegIsVillager.isChecked(), 'addressType': 0,
                               'regCity'     : self.cmbRegCity.code(), 'regStreet': self.cmbRegStreet.code(),
                               'regHouse'    : self.edtRegHouse.text(), 'regCorpus': self.edtRegCorpus.text(),
                               'regFlat'     : self.edtRegFlat.text()}
        return self.regAddressInfo

    def setParamsRegAddress(self, regAddressInfo):
        self.regAddressInfo = regAddressInfo

    def getParamsLocAddress(self):
        self.locAddressInfo = {'regFreeInput': self.edtLocFreeInput.text(), 'regIsVillager': self.chkLocIsVillager.isChecked(), 'addressType': 1,
                               'regCity'     : self.cmbLocCity.code(), 'regStreet': self.cmbLocStreet.code(),
                               'regHouse'    : self.edtLocHouse.text(), 'regCorpus': self.edtLocCorpus.text(),
                               'regFlat'     : self.edtLocFlat.text()}
        return self.locAddressInfo

    def setParamsLocAddress(self, locAddressInfo):
        self.locAddressInfo = locAddressInfo

    def setClientDialogInfo(self, info=None):
        if not info:
            info = {}
        if info:
            self.edtLastName.setText(info.get('lastName', ''))
            self.edtFirstName.setText(info.get('firstName', ''))
            self.edtPatrName.setText(info.get('patrName', ''))
            birthDate = info.get('birthDate', None)
            if birthDate:
                self.edtBirthDate.setDate(birthDate)
            self.cmbSex.setCurrentIndex(info.get('sex', 0))
            self.edtSNILS.setText(info.get('SNILS', ''))
            docTypeId = info.get('docType', None)
            if docTypeId:
                self.cmbDocType.setValue(docTypeId)
                if self.isVisibleObject(self.edtDocSerialRight):
                    self.edtDocSerialLeft.setText(forceString(info.get('serialLeft', '')))
                    self.edtDocSerialRight.setText(forceString(info.get('serialRight', '')))
                else:
                    self.edtDocSerialLeft.setText(forceString(info.get('serialLeft', '')) + forceString(info.get('serialRight', '')))
                self.edtDocNumber.setText(forceString(info.get('docNumber', '')))
            addressType = info.get('addressType', None)
            if addressType == 0:
                self.cmbRegCity.setCode(info.get('regCity', ''))
                self.cmbRegStreet.setCode(info.get('regStreet', ''))
                self.edtRegHouse.setText(info.get('regHouse', ''))
                self.edtRegCorpus.setText(info.get('regCorpus', ''))
                self.edtRegFlat.setText(info.get('regFlat', ''))
            elif addressType == 1:
                self.cmbLocCity.setCode(info.get('regCity', ''))
                self.cmbLocStreet.setCode(info.get('regStreet', ''))
                self.edtLocHouse.setText(info.get('regHouse', ''))
                self.edtLocCorpus.setText(info.get('regCorpus', ''))
                self.edtLocFlat.setText(info.get('regFlat', ''))
            polisSerial = info.get('polisSerial', '')
            polisNumber = info.get('polisNumber', '')
            polisCompany = info.get('polisCompany', None)
            polisType = info.get('polisType', None)
            polisTypeName = forceString(info.get('polisTypeName', ''))
            if polisType:
                if u'ДМС' in polisTypeName:
                    self.edtVoluntaryPolisSerial.setText(polisSerial)
                    self.edtVoluntaryPolisNumber.setText(polisNumber)
                    self.cmbVoluntaryPolisCompany.setValue(polisCompany)
                    self.cmbVoluntaryPolisType.setValue(polisType)
                    polisBegDate = info.get('polisBegDate', None)
                    if polisBegDate:
                        self.edtVoluntaryPolisBegDate.setDate(polisBegDate)
                    polisEndDate = info.get('polisEndDate', None)
                    if polisEndDate:
                        self.edtVoluntaryPolisEndDate.setDate(polisEndDate)
                else:
                    self.edtCompulsoryPolisSerial.setText(polisSerial)
                    self.edtCompulsoryPolisNumber.setText(polisNumber)
                    self.cmbCompulsoryPolisCompany.setValue(polisCompany)
                    self.cmbCompulsoryPolisType.setValue(polisType)
                    polisBegDate = info.get('polisBegDate', None)
                    if polisBegDate:
                        self.edtCompulsoryPolisBegDate.setDate(polisBegDate)
                    polisEndDate = info.get('polisEndDate', None)
                    if polisEndDate:
                        self.edtCompulsoryPolisEndDate.setDate(polisEndDate)
            freeInput = forceStringEx(info.get('regFreeInput', None))
            if freeInput and not QtGui.qApp.isAddressOnlyByKLADR():
                self.chkRegKLADR.setCheckState(QtCore.Qt.Unchecked)
                self.edtRegFreeInput.setText(freeInput)
                self.chkRegIsVillager.setChecked(info.get('regIsVillager', False))
            contact = info.get('contact', '')
            typeContactId = forceRef(QtGui.qApp.db.translate('rbContactType', 'code', 1, 'id'))
            self.modelContacts.setDialogContact(typeContactId, contact)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('lastName', toVariant(trimNameSeparators(nameCase(forceStringEx(self.edtLastName.text())), 'lastName')))
        record.setValue('firstName', toVariant(trimNameSeparators(nameCase(forceStringEx(self.edtFirstName.text())), 'firstName')))
        record.setValue('patrName', toVariant(trimNameSeparators(nameCase(forceStringEx(self.edtPatrName.text())), 'patrName')))
        record.setValue('growth', toVariant(forceStringEx(self.edtGrowth.value())))
        record.setValue('weight', toVariant(forceStringEx(self.edtWeight.value())))
        record.setValue('birthPlace', toVariant(nameCase(forceStringEx(self.edtBirthPlace.text()))))
        record.setValue('birthDate', toVariant(self.edtBirthDate.date()))
        record.setValue('birthTime', toVariant(self.edtBirthTime.time()))
        record.setValue('embryonalPeriodWeek', toVariant(self.edtEmbryonalPeriodWeek.value()))
        record.setValue('diagNames', toVariant(self.edtDiagNames.text()))
        record.setValue('sex', toVariant(self.cmbSex.currentIndex()))
        record.setValue('SNILS', toVariant(forceStringEx(self.edtSNILS.text()).replace('-', '').replace(' ', '')))
        record.setValue('IIN', toVariant(self.edtIIN.text()))
        record.setValue('notes', toVariant(forceStringEx(self.edtNotes.toPlainText().replace('\n', '<br>'))))
        record.setValue('chartBeginDate', toVariant(self.edtChartBeginDate.date()))
        record.setValue('attendingPerson_id', toVariant(self.cmbAttendingPerson.value()))
        record.setValue('isConfirmSendingData', toVariant(self.isConfirmSendingData if hasattr(self, 'isConfirmSendingData') else 0))
        record.setValue('isUnconscious', toVariant(self.chkUnconscious.isChecked()))

        if QtGui.qApp.userHasRight(Users.Rights.urEditImplantsAndProsthesis):
            record.setValue('hasImplants', toVariant(self.chkHasImplants.isChecked()))
            record.setValue('hasProsthesis', toVariant(self.chkHasProsthesis.isChecked()))

        if self.isTabContactsAlreadyLoad:
            record.setValue('rbInfoSource_id', toVariant(self.cmbInfoSource.value()))

        if self.isTabFeatureAlreadyLoad:
            record.setValue('bloodType_id', toVariant(self.cmbBloodType.value()))
            record.setValue('bloodDate', toVariant(self.edtBloodTypeDate.date()))
            record.setValue('bloodNotes', toVariant(forceStringEx(self.edtBloodTypeNotes.text())))
        else:
            record.setValue('bloodType_id', toVariant(self.bloodType_id))
            record.setValue('bloodDate', toVariant(self.bloodDate))
            record.setValue('bloodNotes', toVariant(forceStringEx(self.bloodNotes)))
        return record

    def getAddress(self, addressType):
        if addressType == 0:
            return {
                'useKLADR'       : self.chkRegKLADR.isChecked(),
                'KLADRCode'      : self.cmbRegCity.code(),
                'KLADRStreetCode': self.cmbRegStreet.code() if self.cmbRegStreet.code() else '',  # без этого наростают адреса
                'number'         : forceStringEx(self.edtRegHouse.text()),
                'corpus'         : forceStringEx(self.edtRegCorpus.text()),
                'flat'           : forceStringEx(self.edtRegFlat.text()),
                'freeInput'      : forceStringEx(self.edtRegFreeInput.text()),
                'isVillager'     : forceBool(self.chkRegIsVillager.isChecked()),
                'districtId'     : forceRef(self.cmbRegDistrict.value())
            }
        else:
            return {
                'useKLADR'       : self.chkLocKLADR.isChecked(),
                'KLADRCode'      : self.cmbLocCity.code(),
                'KLADRStreetCode': self.cmbLocStreet.code() if self.cmbLocStreet.code() else '',  # без этого наростают адреса
                'number'         : forceStringEx(self.edtLocHouse.text()),
                'corpus'         : forceStringEx(self.edtLocCorpus.text()),
                'flat'           : forceStringEx(self.edtLocFlat.text()),
                'freeInput'      : forceStringEx(self.edtLocFreeInput.text()),
                'isVillager'     : forceBool(self.chkLocIsVillager.isChecked()),
                'districtId'     : forceRef(self.cmbLocDistrict.value())
            }

    def getAddressRecord(self, clientId, addressType):
        address = self.getAddress(addressType)
        if address['useKLADR']:
            addressId = getAddressId(address)
        else:
            addressId = None
        oldAddressRecord = self.__regAddressRecord if addressType == 0 else self.__locAddressRecord

        if oldAddressRecord != None:
            recordChanged = addressId != forceRef(oldAddressRecord.value('address_id')) \
                            or address['freeInput'] != forceString(oldAddressRecord.value('freeInput')) \
                            or address['isVillager'] != forceBool(oldAddressRecord.value('isVillager')) \
                            or address['districtId'] != forceRef(oldAddressRecord.value('district_id'))
        else:
            recordChanged = True

        if recordChanged:
            record = QtGui.qApp.db.record('ClientAddress')
            record.setValue('client_id', toVariant(clientId))
            record.setValue('type', toVariant(addressType))
            record.setValue('address_id', toVariant(addressId))
            record.setValue('freeInput', toVariant(address['freeInput']))
            record.setValue('isVillager', toVariant(address['isVillager']))
            record.setValue('district_id', toVariant(address['districtId']))
        else:
            record = oldAddressRecord

        return record, address, recordChanged

    def getWorkRecord(self, clientId):
        organisationId = self.cmbWorkOrganisation.value()
        freeInput = u'' if organisationId else forceStringEx(self.edtWorkOrganisationFreeInput.text())
        post = forceStringEx(self.edtWorkPost.text())
        OKVED = forceStringEx(self.cmbWorkOKVED.text())
        stage = self.edtWorkStage.value()
        note = self.edtWorkNote.text()

        work = {'organisationId': organisationId,
                'freeInput'     : freeInput,
                'post'          : post,
                'OKVED'         : OKVED,
                'stage'         : stage,
                'note'          : note}

        if self.__workRecord is not None:
            recordChanged = (
                organisationId != forceRef(self.__workRecord.value('org_id')) or
                freeInput != forceString(self.__workRecord.value('freeInput')) or
                post != forceString(self.__workRecord.value('post')) or
                OKVED != forceString(self.__workRecord.value('OKVED')) or
                stage != forceInt(self.__workRecord.value('stage')) or
                note != forceString(self.__workRecord.value('note'))
            )
        else:
            recordChanged = True

        if recordChanged:
            record = QtGui.qApp.db.record('ClientWork')
            record.setValue('client_id', toVariant(clientId))
            record.setValue('org_id', toVariant(organisationId))
            record.setValue('freeInput', toVariant(freeInput))
            record.setValue('post', toVariant(post))
            record.setValue('OKVED', toVariant(OKVED))
            record.setValue('stage', toVariant(stage))
            record.setValue('note', toVariant(note))
        else:
            record = self.__workRecord

        return record, work, recordChanged

    def checkClosedEventWithDMCF(self):
        if self.policyIdDMCF:
            db = QtGui.qApp.db
            table = db.table('Event')
            closedEventId = db.getRecordList(
                table,
                'id',
                [table['clientPolicy_id'].eq(self.policyIdDMCF), table['execDate'].isNotNull()]
            )
            if closedEventId:
                if self.oldFranchisePercent != self.newFranchisePercent:
                    if QtGui.QMessageBox.question(
                        self,
                        u'Внимание!',
                        u'Существуют обращения с прошлым значением процента. Хотите изменить процент?',
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                        QtGui.QMessageBox.Yes
                    ) == QtGui.QMessageBox.Yes:
                        return True
                    else: # if res == QtGui.QMessageBox.No:
                        if QtGui.QMessageBox.question(
                            self,
                            u'Внимание!',
                            u'Прошлое значение процента франшизы: %s. Хотите вернуть значение?' % self.oldFranchisePercent,
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                            QtGui.QMessageBox.Yes
                        ) == QtGui.QMessageBox.Yes:
                            self.edtDMCPercent.setText(str(self.oldFranchisePercent))
                            return True
                        return False

        return True

    def checkMobile(self):
        if not QtGui.qApp.userHasRight(urSkipCheckClientContacts):
            contactsItems = self.tblContacts.model().items()
            if not [x for x in contactsItems if forceRef(x.value('contactType_id') == 3)]:
                return False
            for x in contactsItems:
                if forceRef(x.value('contactType_id')) == 3 and (not forceString(x.value('contact')) and not forceString(
                        x.value('notes'))):
                    return False
            return True
        else:
            return True

    def checkEmail(self):
        result = True
        items = self.tblContacts.model().items()
        if QtGui.qApp.isAskAccess() and items:
            for x in items:
                if forceRef(x.value('contactType_id')) == 4:
                    import re
                    if re.search('^.+\@.+\.\D+$', forceString(x.value('contact'))):
                        result = True
                        setFocusToWidget(self)
                    else:
                        result = False

                    if not self.isConfirmSendingData:
                        if QtGui.QMessageBox.information(
                                self,
                                u'Внимание',
                                u'Передавать персональные данные пациента?',
                                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                QtGui.QMessageBox.No
                        ) == QtGui.QMessageBox.Yes:
                            self.isConfirmSendingData = True
                        else:
                            self.isConfirmSendingData = False
        return result

    def checkAddressEntered(self, address):
        return address['freeInput'] != '' or all(address[f] for f in ('KLADRCode', 'KLADRStreetCode', 'number'))

    def checkSocStatusesBySoftControl(self):
        u"""
        i3683
            При редактировании или создании нового пациента необходимо проверять заполненность вкладки "Соц.статус"
            только для тех классов соц статусов, для которых установлен мягкий контроль (rbSocStatusClass.softControl)
        """
        if u'онко' in QtGui.qApp.currentOrgInfis() and u'tabSocStatus' not in self._invisibleObjectsNameList:
            if not self.modelSocStatuses.items():
                self.modelSocStatuses.loadItems(self.itemId())

            clientSocStatusesId = [forceString(x.value('socStatusClass_id')) for x in self.modelSocStatuses.items() if forceString(x.value('socStatusClass_id'))]
            availableSocStatusesId = self.modelSocStatuses.availableClassIdList()
            for x in clientSocStatusesId:
                if x in availableSocStatusesId:
                    availableSocStatusesId.remove(x)

            cond = [u'softControl = 1']
            if availableSocStatusesId:
                cond.append(u'id IN (%s)' % ', '.join(availableSocStatusesId))
            if clientSocStatusesId:
                cond.append(u'id NOT IN (%s)' % ', '.join(clientSocStatusesId))

            records = QtGui.qApp.db.getRecordList(table='rbSocStatusClass', cols='id, name', where=cond)
            if records:
                message = u'следующие обязательные классы соц. статуса пациента:\n'
                message += u';\n'.join(u'\'' + forceString(x.value('name')) + u'\'' for x in records)
                return self.checkInputMessage(message, True, self.tblSocStatuses)

        return True

    def checkOpenCompulsoryPoliciesCount(self):
        u"""
        i4017
            Проверка на наличие нескольких действующих полисов ОМС при сохранении карточки клиента
        """
        if self.tabDocsPolicy.isVisible():
            if not self.modelPolicies.items():
                self.modelPolicies.loadItems(self.itemId())

            policyTypes = [
                forceInt(x.value('id')) for x in QtGui.qApp.db.getRecordList(
                    stmt=u'SELECT id FROM rbPolicyType WHERE name LIKE \'%омс%\';'
                )
            ]
            compulsoryPolicies = [
                x for x in self.modelPolicies.items() if forceInt(x.value('policyType_id')) in policyTypes and forceDate(x.value('endDate')).isNull()
            ]

            if len(compulsoryPolicies) > 1:
                name = unicode(
                    self.edtLastName.text() + u' ' + self.edtFirstName.text() + u' ' + self.edtPatrName.text()
                )
                message = u'Пациент %s имеет действующие полисы ОМС в количестве %s' % (name, len(compulsoryPolicies))
                return self.checkValueMessage(message, True, self.tblPolicies)
        return True

    def checkDataEntered(self):
        # i1188 Прибыл без сознания -> сейвим карту такую какая она есть.
        if self.chkUnconscious.isChecked():
            return True

        birthDate = self.edtBirthDate.date()

        if QtGui.qApp.userHasRight(Users.Rights.urSaveClientWithBasicInfo) \
                and formatName(self.edtLastName.text(), self.edtFirstName.text(), self.edtPatrName.text()) \
                and self.checkSexEntered() \
                and (not birthDate.isNull() and birthDate.isValid()) \
                and (self.checkAddressEntered(self.getAddress(0)) or self.checkAddressEntered(self.getAddress(1))):
            return True

        lastName = forceStringEx(self.edtLastName.text())
        tinyChild = birthDate.isValid() and birthDate.addMonths(2)>=QtCore.QDate.currentDate()
        result = True
        result = result and self.checkOpenCompulsoryPoliciesCount()
        result = result and self.checkSocStatusesBySoftControl()
        result = result and self.checkClosedEventWithDMCF()
        result = result and (lastName or self.checkInputMessage(u'фамилию', False, self.edtLastName))
        result = result and (isNameValid(lastName) or self.checkInputMessage(u'допустимую фамилию', False, self.edtLastName))
        if tinyChild:
            result = result and (isNameValid(self.edtFirstName.text()) or self.checkInputMessage(u'допустимое имя', True, self.edtFirstName))
            result = result and (isNameValid(self.edtPatrName.text()) or self.checkInputMessage(u'допустимое отчество', True, self.edtPatrName))
        else:
            result = result and (forceStringEx(self.edtFirstName.text()) or self.checkInputMessage(u'имя', False, self.edtFirstName))
            result = result and (isNameValid(self.edtFirstName.text()) or self.checkInputMessage(u'допустимое имя', False, self.edtFirstName))
            result = result and (forceStringEx(self.edtPatrName.text())  or self.checkInputMessage(u'отчество', True, self.edtPatrName))
            result = result and (isNameValid(self.edtPatrName.text()) or self.checkInputMessage(u'допустимое отчество', False, self.edtPatrName))
        result = result and self.checkSexEntered()
        result = result and (birthDate.isValid()      or self.checkInputMessage(u'дату рождения', False, self.edtBirthDate))
        result = result and self.checkBirthDateEntered()
        result = result and self.checkDup()
        if self.isVisibleObject(self.lblInfoSource):
            result = result and self.checkInfoSourceEntered()

        if QtGui.qApp.strictOccupationControl():
            if not self.isTabWorkAlreadyLoad:
                self.initTabWork()
            result = result and self.checkWorkEntered()

        result = result and self.checkSocStatus()
        if not QtGui.qApp.isCheckOnlyClientNameAndBirthdateAndSex():
            result = result and self.checkSNILSEntered()
            result = result and self.checkDocEntered()
            if self.isTabSocStatusAlreadyLoad:
                result = result and self.checkDocNumber()
            result = result and self.checkPolicyEntered()
            if self.isTabAttachAlreadyLoad:
                result = result and self.checkAttachesDataEntered()
            if self.isTabRelationsAlreadyLoad:
                result = result and self.checkClientRelations(self.cmbSex.currentIndex())
            if self.isTabDocsAlreadyLoad:
                result = result and (self.checkPaymentSchemeIntersections())
            if not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutBirthPlace):
                result = result and (forceStringEx(self.edtBirthPlace.text()) or self.checkInputMessage(u'место рождения', False, self.edtBirthPlace))
        if self.edtPesHeight.isVisible():
            if not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutBodyStats):
                result = result and (self.edtPesHeight.text() or self.checkInputMessage(u'рост', False, self.edtPesHeight))
        if self.edtPesWeight.isVisible():
            if not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutBodyStats):
                result = result and (self.edtPesWeight.text() or self.checkInputMessage(u'вес', False, self.edtPesWeight))

        result = result and (self.checkContacts() or self.checkValueMessage(u'Таблица "Контакты" не заполнена.', False, self.tblContacts))
        result = result and (self.checkEmail() or self.checkValueMessage(u'Введен неверный E-Mail.', False, self.tblContacts))
        result = result and (self.checkMobile() or self.checkValueMessage(u'Не введен мобильный телефон', False, self.tblContacts))
        result = result and (self.checkPolicyCorrect() or self.checkValueMessage(u'Обнаружено пересечение дат полисов одного типа.', False, self.tblPolicies))

        return result

    def checkSocStatus(self):
        if not self.isTabSocStatusAlreadyLoad:
            self.initTabSocStatus()
        db = QtGui.qApp.db
        tbl = db.table('rbSocStatusClass')
        cond = [tbl['tightControl'].eq(1)]
        if forceBool(db.translate('rbDocumentType', 'id', self.cmbDocType.value(), 'isForeigner')):
            cond.append(tbl['flatCode'].eq('citizenship'))
            cond = db.joinOr(cond)
        ssList = db.getRecordList(tbl, [tbl['id'], tbl['name']], where = cond)
        ssDict = {}
        for record in ssList:
            ssDict[forceInt(record.value('id'))] = forceString(record.value('name'))
        for tableView, model in [(self.tblSocStatuses, self.modelSocStatuses),
                                 (self.tblClientBenefits, self.modelClientBenefits),
                                 (self.tblCheckup, self.modelClientCheckup)]:
            for (index, item) in enumerate(model.items()):
                if forceRef(item.value('socStatusClass_id')) in ssDict.keys():
                    del ssDict[forceRef(item.value('socStatusClass_id'))]
                if not forceRef(item.value('socStatusType_id')):
                    self.checkInputMessage(u'тип соц. статуса.', False, tableView, index, 1)
                    return False
        if ssDict:
            self.checkInputMessage(u'соц. статус: %s.' % ', '.join(ssDict.values()), False, self.tblSocStatuses, len(self.modelSocStatuses.items()), 0)
            return False
        return True

    def checkDocNumber(self):
        for item in self.modelSocStatuses.items():
            if forceRef(item.value('documentType_id')):
                if not forceString(item.value('number')):
                    if QtGui.QMessageBox.question( self,
                                           u'Внимание!',
                                           u'Для типа соц.статуса не введен номер документа.',
                                           QtGui.QMessageBox.Ok|QtGui.QMessageBox.Ignore,
                                           QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
                        self.edtSocStatusDocNumber.setFocus(QtCore.Qt.ShortcutFocusReason)
                        return False
        return True

    def checkSexEntered(self):
        currentSex = self.cmbSex.currentIndex()
        firstName = forceStringEx(self.edtFirstName.text())
        firstNameSex = forceInt(QtGui.qApp.db.translate('rdFirstName', 'name', firstName, 'sex')) if firstName else 0
        patrName = forceStringEx(self.edtPatrName.text())
        patrNameSex = forceInt(QtGui.qApp.db.translate('rdPatrName', 'name', patrName, 'sex')) if patrName else 0
        if firstNameSex and patrNameSex:
            if firstNameSex == patrNameSex:
                detectedSex = firstNameSex
            else:
                res = QtGui.QMessageBox.question( self,
                                                  u'Внимание!',
                                                  u'Конфликт имени и отчества.\nХотите исправить?',
                                                  QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                                  QtGui.QMessageBox.Yes)
                if res == QtGui.QMessageBox.Yes:
                    if currentSex == firstNameSex:
                        self.edtPatrName.setFocus(QtCore.Qt.ShortcutFocusReason)
                    else:
                        return False
                detectedSex = 0
        else:
            detectedSex = max(firstNameSex, patrNameSex)

        if currentSex:
            if detectedSex and currentSex != detectedSex:
                res = QtGui.QMessageBox.question(self,
                                                 u'Внимание!',
                                                 u'Конфликт при выборе пола.\nИсправить пол на %s?' % formatSex(detectedSex),
                                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                 QtGui.QMessageBox.Yes)
                if res == QtGui.QMessageBox.Yes:
                    self.cmbSex.setCurrentIndex(detectedSex)
        else:
            if detectedSex:
                self.cmbSex.setCurrentIndex(detectedSex)
            else:
                return self.checkInputMessage(u'пол', False, self.cmbSex)

        return True

    def checkInfoSourceEntered(self):
        currentInfoSource = self.cmbInfoSource.value()
        if self.itemId():
            record = self.record()
            if self.isTabContactsAlreadyLoad:
                if not currentInfoSource:
                    return self.checkInputMessage(u'причину обращения', False, self.cmbInfoSource)
            elif not forceRef(record.value('rbInfoSource_id')):
                return self.checkInputMessage(u'причину обращения', False, self.cmbInfoSource)
        elif not currentInfoSource:
            return self.checkInputMessage(u'причину обращения', False, self.cmbInfoSource)
        return True

    def checkBirthDateEntered(self):
        checkBirthDate = self.edtBirthDate.date()
        currentDate = QtCore.QDate.currentDate()
        if checkBirthDate > currentDate:
            res = QtGui.QMessageBox.warning(self,
                                            u'Внимание!',
                                            u'Дата рождения не может быть больше текущей даты',
                                            QtGui.QMessageBox.Ok,
                                            QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                self.edtBirthDate.setFocus(QtCore.Qt.ShortcutFocusReason)
                return False
        if currentDate.year() - checkBirthDate.year() > 135:
            res = QtGui.QMessageBox.question(self,
                                             u'Внимание!',
                                             u'Возраст превышает 135 лет.\nХотите исправить?',
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                             QtGui.QMessageBox.Yes)
            if res == QtGui.QMessageBox.Yes:
                self.edtBirthDate.setFocus(QtCore.Qt.ShortcutFocusReason)
                return False
        return True

    def checkSNILSEntered(self):
        SNILS = unformatSNILS(forceStringEx(self.edtSNILS.text()))
        if SNILS:
            if len(SNILS) != 11:
                self.checkInputMessage(u'CНИЛС', True, self.edtSNILS)
                return False
            elif not checkSNILS(SNILS):
                fixedSNILS = formatSNILS(fixSNILS(SNILS))
                res = QtGui.QMessageBox.question(self,
                                                 u'Внимание!',
                                                 u'СНИЛС указан с ошибкой.\nПравильный СНИЛС %s\nИсправить?' % fixedSNILS,
                                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                 QtGui.QMessageBox.Yes)
                if res == QtGui.QMessageBox.Yes:
                    self.edtSNILS.setText(fixedSNILS)
                else:
                    self.edtSNILS.setFocus(QtCore.Qt.ShortcutFocusReason)
                    return False
        return True

    def checkDocEntered(self):
        docTypeIsEmpty = self.cmbDocType.value() in [0, None]
        docSerialLeftIsEmpty = not forceStringEx(self.edtDocSerialLeft.text())

        # TODO: избавиться от второго поля для ввода серии. Это пережиток прошлого..
        docSerialRightIsEmpty = (not forceStringEx(self.edtDocSerialRight.text())) if self.isVisibleObject(self.edtDocSerialRight) else False

        docNumberIsEmpty = not forceStringEx(self.edtDocNumber.text())
        docDateIsEmpty = not forceDate(self.edtDocDate.date())
        docWhoExtraditedIsEmpty = not forceStringEx(self.edtWhoExtraditedDoc.text())
        canRegWithoutDocSource = QtGui.qApp.userHasRight(Users.Rights.urRegWithoutDocSource)

        if docSerialLeftIsEmpty and docSerialRightIsEmpty and docNumberIsEmpty \
                and ((docTypeIsEmpty and docDateIsEmpty and docWhoExtraditedIsEmpty) or canRegWithoutDocSource):
            return True

        if docNumberIsEmpty:
            self.edtDocNumber.setCursorPosition(0)
            return self.checkInputMessage(u'номер документа', False, self.edtDocNumber)

        if self.useInputMask:
            if not self.edtDocSerialLeft.hasAcceptableInput():
                self.edtDocSerialLeft.setCursorPosition(0)
                return self.checkValueMessage(u'серия документа имеет неверный формат', False, self.edtDocSerialLeft)

            if not self.edtDocSerialRight.hasAcceptableInput():
                self.edtDocSerialRight.setCursorPosition(0)
                return self.checkValueMessage(u'серия документа имеет неверный формат', False, self.edtDocSerialRight)

            if not self.edtDocNumber.hasAcceptableInput():
                self.edtDocNumber.setCursorPosition(0)
                return self.checkValueMessage(u'номер документа имеет неверный формат', False, self.edtDocNumber)
        else:
            if docSerialLeftIsEmpty:
                canBeEmpty = self.edtDocSerialLeft.format == 0
                self.edtDocSerialLeft.setCursorPosition(0)
                return self.checkInputMessage(u'серию документа', canBeEmpty, self.edtDocSerialLeft)

            if docSerialRightIsEmpty:
                canBeEmpty = self.edtDocSerialRight.format == 0
                self.edtDocSerialRight.setCursorPosition(0)
                return self.checkInputMessage(u'серию документа', canBeEmpty, self.edtDocSerialRight)

        if not canRegWithoutDocSource:
            if self.isVisibleObject(self.lblWhoExtraditedDoc) and docWhoExtraditedIsEmpty:
                return self.checkInputMessage(u'кем выдан документ', False, self.edtWhoExtraditedDoc)
            if self.isVisibleObject(self.lblDocDate) and docDateIsEmpty:
                return self.checkInputMessage(u'дату выдачи', False, self.edtDocDate)
        return True

    def checkWorkEntered(self):





        name = forceString(self.edtWorkOrganisationFreeInput.text())
        orgId = forceString(self.cmbWorkOrganisation.value())
        if not (name or orgId):
            return self.checkInputMessage(u'занятость', False, self.cmbWorkOrganisation)
        return True

    def checkPolicyEntered(self):
        # TODO:skkachaev: Там дальше по тексту это право используется как-то ооочень странно. Хз, зачем так. Постановщик задачи (Alex) сказал, что так не надо
        if QtGui.qApp.userHasRight(Users.Rights.urRegWithoutCompulsoryPolicy): return True

        strictControl = not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutCompulsoryPolicy)
        defaultKLADR = QtGui.qApp.defaultKLADR()
        cPolisKindCode = forceInt(self.cmbCompulsoryPolisKind.code())

        cPolisCompanyIsEmpty = not self.cmbCompulsoryPolisCompany.value()
        cPolisSerialIsEmpty  = not forceStringEx(self.edtCompulsoryPolisSerial.text())
        cPolisNumberIsEmpty  = not forceStringEx(self.edtCompulsoryPolisNumber.text())
        cPolisTypeIsEmpty    = not self.cmbCompulsoryPolisType.value()
        cPolisKindIsEmpty    = not self.cmbCompulsoryPolisKind.value()
        cPolisBegDateIsEmpty = not self.edtCompulsoryPolisBegDate.date()
        cPolisEndDateIsEmpty = not self.edtCompulsoryPolisEndDate.date()
        # FIXME: atronah: заменить проверку isVisible на что-то более адекватное, так как isVisible() == False, если окно на заднем плане
        cPolisNameIsEmpty    = not (self.edtCompulsoryPolisName.isVisible() and forceStringEx(self.edtCompulsoryPolisName.text()))
        cPolisDataIsEmpty    = cPolisCompanyIsEmpty and cPolisSerialIsEmpty and cPolisNumberIsEmpty and \
                               cPolisTypeIsEmpty and cPolisKindIsEmpty and cPolisBegDateIsEmpty and \
                               cPolisEndDateIsEmpty and cPolisNameIsEmpty

        vPolisCompanyIsEmpty = not self.cmbVoluntaryPolisCompany.value()
        vPolisSerialIsEmpty  = not forceStringEx(self.edtVoluntaryPolisSerial.text())
        vPolisNumberIsEmpty  = not forceStringEx(self.edtVoluntaryPolisNumber.text())
        vPolisTypeIsEmpty    = not self.cmbVoluntaryPolisType.value()
        vPolisBegDateIsEmpty = not self.edtVoluntaryPolisBegDate.date()
        vPolisEndDateIsEmpty = not self.edtVoluntaryPolisEndDate.date()
        vPolisNameIsEmpty    = not forceStringEx(self.edtVoluntaryPolisName.text())
        vPolisDataIsEmpty    = vPolisCompanyIsEmpty and vPolisSerialIsEmpty and vPolisNumberIsEmpty and \
                               vPolisTypeIsEmpty and vPolisBegDateIsEmpty and \
                               vPolisEndDateIsEmpty and vPolisNameIsEmpty

        if strictControl and cPolisDataIsEmpty and vPolisDataIsEmpty:
            return self.checkInputMessage(u'полис ОМС', False, self.cmbCompulsoryPolisCompany)

        if not cPolisDataIsEmpty:
            if cPolisCompanyIsEmpty and (strictControl or cPolisNameIsEmpty):
                return self.checkInputMessage(u'страховую компанию (ОМС)', False, self.cmbCompulsoryPolisCompany)
            cPolisCompany = self.cmbCompulsoryPolisCompany.value()
            canOmitPolicyNumber = forceBool(QtGui.qApp.db.translate('Organisation', 'id', cPolisCompany, 'canOmitPolicyNumber'))
            if not canOmitPolicyNumber:
                cPolicySerialIsNeed = cPolisKindCode == 1
                cPolicySerialIsNeed = cPolicySerialIsNeed or (defaultKLADR.startswith('78') or defaultKLADR.startswith('47'))
                cPolicySerialIsNeed = cPolicySerialIsNeed and cPolisSerialIsEmpty and QtGui.qApp.isCheckPolisEndDateAndNumberEnabled()
                if cPolicySerialIsNeed:
                    return self.checkInputMessage(u'серию полиса ОМС', not strictControl, self.edtCompulsoryPolisSerial)
                if cPolisNumberIsEmpty:
                    return self.checkInputMessage(u'номер полиса ОМС', False, self.edtCompulsoryPolisNumber)
                elif not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutCheckNumberCompulsoryPolicy):
                    cPolisSerial = forceStringEx(self.edtCompulsoryPolisSerial.text()).upper()
                    currentLen = len(forceStringEx(self.edtCompulsoryPolisNumber.text()).replace(' ', ''))
                    # TODO: craz: возможно, следует ввести дополнительные проверки - разделять логику для регионов либо дополнительно проверять наличие серии...
                    if self.cLengthSerialNumberPolis.has_key(cPolisSerial) and self.cLengthSerialNumberPolis[cPolisSerial] != currentLen:
                        return self.checkInputMessage(u'номер полиса из %s символов' % self.cLengthSerialNumberPolis[cPolisSerial], True, self.edtCompulsoryPolisNumber)
                    elif self.cLengthKindNumberPolis.has_key(cPolisKindCode) and self.cLengthKindNumberPolis[cPolisKindCode] != currentLen:
                        return self.checkInputMessage(u'номер полиса из %s символов' % self.cLengthKindNumberPolis[cPolisKindCode], True, self.edtCompulsoryPolisNumber)
                    if cPolisKindCode in [3, 4, 5]:
                        policyNumber = str(self.edtCompulsoryPolisNumber.text())
                        if not policyNumber.isdigit() or not checkENP(policyNumber):
                            fixedENP = fixENP(policyNumber)
                            res = QtGui.QMessageBox.question(
                                self,
                                u'Внимание!',
                                u'Номер полиса указан с ошибкой.\nПравильный номер: %s\nИсправить?' % fixedENP,
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                QtGui.QMessageBox.Yes
                            )
                            if res == QtGui.QMessageBox.Yes:
                                self.edtCompulsoryPolisNumber.setText(fixedENP)
                            else:
                                self.edtCompulsoryPolisNumber.setFocus(QtCore.Qt.ShortcutFocusReason)
                            return False
                if cPolisTypeIsEmpty:
                    return self.checkInputMessage(u'тип полиса ОМС', False, self.cmbCompulsoryPolisType)
                if cPolisKindIsEmpty:
                    return self.checkInputMessage(u'вид полиса ОМС', not strictControl, self.cmbCompulsoryPolisKind)
                if cPolisBegDateIsEmpty:
                    return self.checkInputMessage(u'дату начала действия полиса ОМС', not strictControl, self.edtCompulsoryPolisBegDate)

                if cPolisEndDateIsEmpty and QtGui.qApp.isCheckPolisEndDateAndNumberEnabled():
                    return self.checkInputMessage(u'дату окончания действия полиса ОМС', not strictControl, self.edtCompulsoryPolisEndDate)
                if QtGui.qApp.isShowPolicyInsuranceArea():
                    insuranceAreaCode = self.cmbCompulsoryInsuranceArea.code()
                    if not insuranceAreaCode:
                        return self.checkInputMessage(u'территорию страхования (ОМС)',
                                                          False,
                                                          self.cmbCompulsoryInsuranceArea)
                    elif insuranceAreaCode[:13] == '6100000000000' and QtGui.qApp.defaultKLADR()[:2]== '61':
                        return self.checkValueMessage(u'Уточните территорию страхования (ОМС)',
                                                          False,
                                                          self.cmbCompulsoryInsuranceArea)

        if not vPolisDataIsEmpty:
            if vPolisCompanyIsEmpty and (strictControl or vPolisNameIsEmpty):
                return self.checkInputMessage(u'страховую компанию (ДМС)', False, self.cmbVoluntaryPolisCompany)
            vPolisCompany = self.cmbVoluntaryPolisCompany.value()
            canOmitPolicyNumber = forceBool(QtGui.qApp.db.translate('Organisation', 'id', vPolisCompany, 'canOmitPolicyNumber'))
            if not canOmitPolicyNumber:
                if vPolisSerialIsEmpty and strictControl:
                    return self.checkInputMessage(u'серию полиса ДМС', False, self.edtVoluntaryPolisSerial)
                if vPolisNumberIsEmpty:
                    return self.checkInputMessage(u'номер полиса ДМС', False, self.edtVoluntaryPolisNumber)
                if vPolisTypeIsEmpty:
                    return self.checkInputMessage(u'тип полиса ДМС', False, self.cmbVoluntaryPolisType)
                if vPolisBegDateIsEmpty:
                    return self.checkInputMessage(u'дату начала действия полиса ДМС', False, self.edtVoluntaryPolisBegDate)
                if vPolisEndDateIsEmpty and QtGui.qApp.isCheckPolisEndDateAndNumberEnabled():
                    return self.checkInputMessage(u'дату окончания действия полиса ДМС', False, self.edtVoluntaryPolisEndDate)
                if QtGui.qApp.isShowPolicyInsuranceArea():
                    insuranceAreaCode = self.cmbVoluntaryInsuranceArea.code()
                    if not insuranceAreaCode:
                        return self.checkInputMessage(u'территорию страхования (ДМС)',
                                                          False,
                                                          self.cmbVoluntaryInsuranceArea)
                    elif insuranceAreaCode[:13] == '6100000000000':
                        return self.checkValueMessage(u'Уточните территорию страхования (ДМС)',
                                                          False,
                                                          self.cmbVoluntaryInsuranceArea)
        if not QtGui.qApp.userHasRight(Users.Rights.urRegWithEmptyContacts):
            if not len(self.modelContacts._items):
                return self.checkInputMessage(u'способ свзяи с пациентом (таблица "Контакты")', False, self.tblContacts)
        if not QtGui.qApp.userHasRight(Users.Rights.urRegWithoutDistrict):
            if QtGui.qApp.defaultKLADR() == self.cmbRegCity.code() == u'7800000000000' and not self.cmbRegDistrict.value():
                return self.checkInputMessage(u'район проживания по адресу регистрации', False, self.cmbRegDistrict)
            if QtGui.qApp.defaultKLADR() == self.cmbLocCity.code() == u'7800000000000' and not self.cmbLocDistrict.value():
                return self.checkInputMessage(u'район проживания по адресу проживания', False, self.cmbLocDistrict)
        return True

    def checkClientRelations(self, clientSex):
        def checkClientRelationsInt(table, isDirect, otherFieldName, relationTypeCache, sexFieldName, otherSexFieldName):
            db = QtGui.qApp.db
            model = table.model()
            for row, record in enumerate(model.items()):
                relationTypeId = forceRef(record.value('relativeType_id'))
                otherId = forceRef(record.value(otherFieldName))
                if relationTypeId:
                    if otherId:
                        if otherId == -1:
                            continue
                        otherSex = forceInt(db.translate('Client', 'id', otherId, 'sex'))
                        relationTypeRecord = relationTypeCache.get(relationTypeId)
                        if relationTypeRecord:

                            requiredSex = forceInt(relationTypeRecord.value(sexFieldName))
                            requiredOtherSex = forceInt(relationTypeRecord.value(otherSexFieldName))
                            if ((requiredSex and requiredSex != clientSex)
                                or (requiredOtherSex and requiredOtherSex != otherSex)
                                ):
                                return self.checkValueMessage(u'Несоответствие полов в связи', False, table, row, 0)
                    elif not forceString(record.value('freeInput')):
                        return self.checkValueMessage(u'Не выбрана связь', False, table, row, 1)
                else:
                    return self.checkValueMessage(u'Не выбрана связь', False, table, row, 0)
            return True

        db = QtGui.qApp.db
        cache = CTableRecordCache(db, db.table('rbRelationType'), ['leftSex', 'rightSex'])

        return (checkClientRelationsInt(self.tblDirectRelations, True, 'relative_id', cache, 'leftSex', 'rightSex')
                and checkClientRelationsInt(self.tblBackwardRelations, False, 'client_id', cache, 'rightSex', 'leftSex')
                )

    def checkDup(self):
        dupCheckList = ((self.findDupByName, u'по имени и дате рождения'),
                        (self.findDupBySNILS, u'по СНИЛС'),
                        (self.findDupByDoc, u'по документу'),
                        (self.findDupByPolicy, u'по полису'),
                        )
        for method, title in dupCheckList:
            idlist = method()
            if idlist:
                buttons = QtGui.QMessageBox.No | QtGui.QMessageBox.Open
                if QtGui.qApp.userHasAnyRight((Users.Rights.urSaveClientDuplicate, Users.Rights.urAdmin)):
                    buttons |= QtGui.QMessageBox.Yes
                res = QtGui.QMessageBox.question(self,
                                                 u'Внимание!',
                                                 u'Обнаружен "двойник" %s\nИгнорировать?' % title,
                                                 buttons,
                                                 QtGui.QMessageBox.No)
                if res == QtGui.QMessageBox.No:
                    return False
                if res == QtGui.QMessageBox.Open:
                    self.load(idlist[0])
                    return False
        return True

    def findDup(self, cond):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        clientId = self.itemId()
        if clientId:
            cond.append(tableClient['id'].ne(clientId))
        return db.getIdList(tableClient, where=cond, order='id')

    def findDupByName(self):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        lastName = forceStringEx(self.edtLastName.text())
        firstName = forceStringEx(self.edtFirstName.text())
        patrName = forceStringEx(self.edtPatrName.text())
        birthDate = self.edtBirthDate.date()
        cond = [
            tableClient['lastName'].eq(lastName),
            tableClient['firstName'].eq(firstName),
            tableClient['patrName'].eq(patrName),
            tableClient['birthDate'].eq(birthDate),
        ]
        return self.findDup(cond)

    def findDupBySNILS(self):
        db = QtGui.qApp.db
        table = db.table('Client')
        SNILS = unformatSNILS(forceStringEx(self.edtSNILS.text()))
        if SNILS:
            cond = [table['SNILS'].eq(SNILS)]
            return self.findDup(cond)
        else:
            return []

    def findDupByDoc(self):
        docTypeId = self.cmbDocType.value()
        if docTypeId:
            if self.isVisibleObject(self.edtDocSerialRight):
                serialLeft = forceStringEx(self.edtDocSerialLeft.text())
                serialRight = forceStringEx(self.edtDocSerialRight.text())
                serial = self.makeSerial(docTypeId, serialLeft, serialRight)
            else:
                serial = forceStringEx(self.edtDocSerialLeft.text())

            number = forceStringEx(self.edtDocNumber.text())
            if serial or number:
                db = QtGui.qApp.db
                tableClientDocument = db.table('ClientDocument')
                tableLastDoc = tableClientDocument.alias('LastDoc')
                cond = [
                    tableClientDocument['documentType_id'].eq(docTypeId),
                    tableClientDocument['serial'].eq(serial),
                    tableClientDocument['number'].eq(number),
                    tableClientDocument['id'].eqStmt(
                        db.selectMax(tableLastDoc,
                                     tableLastDoc['id'],
                                     [tableLastDoc['client_id'].eq(tableClientDocument['client_id']),
                                      tableLastDoc['deleted'].eq(0)])
                    )
                ]
                clientId = self.itemId()
                if clientId:
                    cond.append(tableClientDocument['client_id'].ne(clientId))
                return db.getIdList(tableClientDocument, 'client_id', cond, 'client_id')

        return []

    def findDupByPolicy(self):
        serial = forceStringEx(self.edtCompulsoryPolisSerial.text())
        number = forceStringEx(self.edtCompulsoryPolisNumber.text())
        if serial or number:
            db = QtGui.qApp.db
            table = db.table('ClientPolicy')
            cond = [table['serial'].eq(serial),
                    table['number'].eq(number),
                    table['id'].eqEx('(SELECT MAX(CP1.id) FROM ClientPolicy AS CP1 WHERE '
                                     'CP1.client_id = ClientPolicy.client_id AND CP1.deleted = 0)')
                    ]
            clientId = self.itemId()
            if clientId:
                cond.append(table['client_id'].ne(clientId))
            return db.getIdList(table, 'client_id', cond, 'client_id')
        else:
            return []

    def checkAttachesDataEntered(self):
        result = True
        for i, item in enumerate(self.modelAttaches.items()):
            result = result and self.checkAttachDataEntered(i, item)
            if not result:
                break
        return result

    def checkDeAttachQueryDataEntered(self, row):
        result = True
        deattachQuery = self.modelAttaches.getDeAttachQuery(row)
        if deattachQuery.number is None and deattachQuery.date is not None:
            result = result and self.checkInputMessage(u'№ уведомления', False, self.tblAttaches, row, self.modelAttaches.queryNumberColumn)
        elif deattachQuery.number is not None and deattachQuery.date is None:
            result = result and self.checkInputMessage(u'дату уведомления', False, self.tblAttaches, row, self.modelAttaches.queryDateColumn)
        return result

    def checkAttachDataEntered(self, row, item):
        result = (forceRef(item.value('attachType_id')) or self.checkInputMessage(u'тип прикрепления', False, self.tblAttaches, row, item.indexOf('attachType_id'))) and \
                 (forceRef(item.value('LPU_id')) or self.checkInputMessage(u'ЛПУ', False, self.tblAttaches, row, item.indexOf('LPU_id'))) and \
                 (forceDate(item.value('begDate')) or self.checkInputMessage(u'дату прикрепления', False, self.tblAttaches, row, item.indexOf('begDate')))
        result = result and self.checkDeAttachQueryDataEntered(row)
        return result

    def checkPaymentSchemeIntersections(self):
        def isBetweenDates(date, intervalDate, strictCompare=True):
            if date is None:
                return False
            if isinstance(date, QtCore.QDate) and date.isNull():
                return False
            if not isinstance(intervalDate, list):
                return False
            if len(intervalDate) != 2:
                return False
            if not (isinstance(intervalDate[0], QtCore.QDate) and isinstance(intervalDate[1], QtCore.QDate)):
                return False
            if strictCompare:
                return date >= intervalDate[0] and date <= intervalDate[1]
            return date > intervalDate[0] and date < intervalDate[1]

        # end isBetweenDates

        dateIntervals = []
        for item in self.modelPaymentScheme.items():
            begDate = forceDate(item.value('begDate'))
            endDate = forceDate(item.value('endDate'))
            dateIntervals.append([begDate, endDate])
        for row, interval in enumerate(dateIntervals):
            begDate = interval[0]
            endDate = interval[1]
            for subRow in xrange(len(dateIntervals)):
                if subRow == row:
                    continue
                if isBetweenDates(begDate, dateIntervals[subRow], True) or isBetweenDates(endDate, dateIntervals[subRow], True):
                    return self.checkValueMessage(u'Обнаружено пересечение дат отображения именных договоров', True, self.tabPaymentScheme, row, 0)
        return True

    def syncIdentificationDocs(self, isBackward=False):
        #  синхронизация полей описания документа
        # (cmbDocType, edtDocSerialLeft, edtDocSerialRight, edtDocNumber)
        # в modelIdentificationDocs
        if not isBackward:
            docTypeId = self.cmbDocType.value()
            if self.isVisibleObject(self.edtDocSerialRight):
                serialLeft = forceStringEx(self.edtDocSerialLeft.text())
                serialRight = forceStringEx(self.edtDocSerialRight.text())
                serial = self.makeSerial(docTypeId, serialLeft, serialRight)
            else:
                serialLeft = ''
                serialRight = ''
                serial = forceStringEx(self.edtDocSerialLeft.text())
            number = forceStringEx(self.edtDocNumber.text())
            date = forceDate(self.edtDocDate.date())
            whoExtraditedDoc = forceStringEx(self.edtWhoExtraditedDoc.text())
            if docTypeId:
                row = self.modelIdentificationDocs.getCurrentDocRow(docTypeId, serial, number)
                self.modelIdentificationDocs.setValue(row, 'documentType_id', docTypeId)
                self.modelIdentificationDocs.setValue(row, 'serial', serial)
                self.modelIdentificationDocs.setValue(row, 'number', number)
                self.modelIdentificationDocs.setValue(row, 'date', date)
                self.modelIdentificationDocs.setValue(row, 'origin', whoExtraditedDoc)
            elif self.modelIdentificationDocs.rowCount() > 0:
                self.modelIdentificationDocs.removeRows(row=0, count=1)
        else:
            row = self.modelIdentificationDocs.getCurrentDocRow(None, '', '')
            self.setDocumentRecord(self.modelIdentificationDocs.items()[row])

    def updateCompulsoryPolicyType(self):
        serial = forceStringEx(self.edtCompulsoryPolisSerial.text())
        insurerId = self.cmbCompulsoryPolisCompany.value()
        if serial and insurerId and not self.cmbCompulsoryPolisType.value():
            policyTypeId = advisePolicyType(insurerId, serial)
            self.cmbCompulsoryPolisType.setValue(policyTypeId)

    def updatePolicyKind(self, serialWidget, kindWidget):
        oldKindCode = '1'
        tempKindCode = '2'
        newKindCode = '3'
        serial = forceStringEx(serialWidget.text())
        if not serial:
            return

        kindCode = None
        if serial.lower() == u'еп':
            kindCode = newKindCode
        elif serial.lower() == u'вс':
            kindCode = tempKindCode
        else:
            kindCode = oldKindCode

        if kindCode:
            kindWidget.setCode(kindCode)

    def updateVoluntaryPolicyType(self):
        serial = forceStringEx(self.edtVoluntaryPolisSerial.text())
        insurerId = self.cmbVoluntaryPolisCompany.value()
        if serial and insurerId:
            policyTypeId = advisePolicyType(insurerId, serial)
            self.cmbVoluntaryPolisType.setValue(policyTypeId)

    def syncPolicies(self):
        self.syncPolicy(True, False)
        self.syncPolicy(False, False)

    @QtCore.pyqtSlot()
    def syncPoliciesBackward(self):
        self.syncPolicy(True, True)
        self.syncPolicy(False, True)

    @QtCore.pyqtSlot()
    def syncClientDocsBackward(self):
        self.syncIdentificationDocs(True)

    def syncPolicy(self, isCompulsory, isBackward=False):
        # возможные изменения в свойствах полиса
        # (edtCompulsoryPolisSerial, edtCompulsoryPolisNumber, cmbCompulsoryPolisCompany, cmbCompulsoryPolisType, edtCompulsoryPolisName, edtCompulsoryPolisNote)
        # необходимо отобразить в modelPolicies
        if isCompulsory:
            getRow = self.modelPolicies.getCurrentCompulsoryPolicyRow
            edtSerial = self.edtCompulsoryPolisSerial
            edtNumber = self.edtCompulsoryPolisNumber
            cmbPolisCompany = self.cmbCompulsoryPolisCompany
            cmbPolisType = self.cmbCompulsoryPolisType
            cmbPolisKind = self.cmbCompulsoryPolisKind
            edtPolisName = self.edtCompulsoryPolisName
            edtPolisNote = self.edtCompulsoryPolisNote
            polisBegDate = self.edtCompulsoryPolisBegDate
            polisEndDate = self.edtCompulsoryPolisEndDate
            polisDischargeDate = self.edtCompulsoryPolisDischargeDate
            insuranceAreaCode = self.cmbCompulsoryInsuranceArea.code()
            franchisePercent = '0'
            isSearchPolicy = 2 if self.isSearchPolicy else 1 if self.isSearchPolicy is not None else 0
        else:
            getRow = self.modelPolicies.getCurrentVoluntaryPolicyRow
            edtSerial = self.edtVoluntaryPolisSerial
            edtNumber = self.edtVoluntaryPolisNumber
            cmbPolisCompany = self.cmbVoluntaryPolisCompany
            cmbPolisType = self.cmbVoluntaryPolisType
            edtPolisName = self.edtVoluntaryPolisName
            edtPolisNote = self.edtVoluntaryPolisNote
            polisBegDate = self.edtVoluntaryPolisBegDate
            polisEndDate = self.edtVoluntaryPolisEndDate
            polisDischargeDate = self.edtVoluntaryPolisDischargeDate
            insuranceAreaCode = self.cmbVoluntaryInsuranceArea.code()
            franchisePercent = self.edtDMCPercent.text()
            isSearchPolicy = 0
            cmbPolisKind = None

        if not isBackward:
            serial = forceStringEx(edtSerial.text())
            number = forceStringEx(edtNumber.text())
            insurerId = cmbPolisCompany.value()

            policyTypeId = cmbPolisType.value()
            # Автоподстановка типа полиса должна срабатывать только для полисов ОМС
            if policyTypeId is None and isCompulsory:
                cmbPolisType.setCurrentIndex(1)
                policyTypeId = cmbPolisType.value()
            policyKindId = cmbPolisKind.value() if cmbPolisKind is not None else None
            name = forceStringEx(edtPolisName.text())
            note = forceStringEx(edtPolisNote.text())
            begDate = polisBegDate.date()
            endDate = polisEndDate.date()
            dischargeDate = polisDischargeDate.date()
            canOmitPolicyNumber = False
            if insurerId:
                canOmitPolicyNumber = forceBool(QtGui.qApp.db.translate('Organisation', 'id', insurerId, 'canOmitPolicyNumber'))

            if (number and (insurerId or name) and policyTypeId) or (insurerId and canOmitPolicyNumber):
                row = getRow(serial, number, insurerId, begDate)
                self.modelPolicies.setValue(row, 'serial', serial)
                self.modelPolicies.setValue(row, 'number', number)
                self.modelPolicies.setValue(row, 'insurer_id', insurerId)
                self.modelPolicies.setValue(row, 'policyType_id', policyTypeId)
                if isCompulsory:
                    self.modelPolicies.setValue(row, 'policyKind_id', policyKindId)
                self.modelPolicies.setValue(row, 'name', name)
                self.modelPolicies.setValue(row, 'note', note)
                self.modelPolicies.setValue(row, 'begDate', begDate)
                self.modelPolicies.setValue(row, 'endDate', endDate)
                self.modelPolicies.setValue(row, 'dischargeDate', dischargeDate)
                self.modelPolicies.setValue(row, 'insuranceArea', insuranceAreaCode)
                self.modelPolicies.setValue(row, 'isSearchPolicy', isSearchPolicy)
                self.modelPolicies.setValue(row, 'franchisePercent', franchisePercent)
        else:
            row = self.modelPolicies.getCurrentPolicyRowInt(isCompulsory, '', '')
            if row >= 0:
                self.setPolicyRecord(self.modelPolicies.items()[row], isCompulsory)
            else:
                self.setPolicyRecord(None, isCompulsory)

    def evalSexByName(self, tableName, name):
        if not self.cmbSex.currentIndex():
            detectedSex = forceInt(QtGui.qApp.db.translate(tableName, 'name', name, 'sex'))
            self.cmbSex.setCurrentIndex(detectedSex)

    def updateSocStatus(self, fieldName, value):
        # изменено какое-то поле соц. статуса из числа доп.полей (сделанных отдельными widget-ами)
        row = self.tblSocStatuses.currentIndex().row()
        self.modelSocStatuses.setValue(row, fieldName, value)

    def updateSocStatuses(self, currStatuses):
        socStatusTypeIdSet = set()
        for socStatusTypeId, _ in currStatuses:
            self.modelSocStatuses.establishStatus(socStatusTypeId)
            socStatusTypeIdSet.add(socStatusTypeId)
        self.modelSocStatuses.declineUnlisted(socStatusTypeIdSet)
        self.modelSocStatuses.reset()

    def updateWorkOrganisationInfo(self):
        orgId = self.cmbWorkOrganisation.value()
        orgInfo = getOrganisationInfo(orgId)
        self.edtWorkOrganisationINN.setText(orgInfo.get('INN', ''))
        self.edtWorkOrganisationOGRN.setText(orgInfo.get('OGRN', ''))
        okved = orgInfo.get('OKVED', '')
        if self.cmbWorkOKVED.orgCode != okved:
            self.edtOKVEDName.clear()
        self.cmbWorkOKVED.setOrgCode(okved)
        self.edtWorkOrganisationFreeInput.setEnabled(not orgId)

    def getAreaList(self, code, insurer, insuranceArea):
        if code:
            return [code]
        if QtGui.qApp.defaultKLADR()[:2] in ('23', '78', '77'):
            return [QtGui.qApp.defaultKLADR()]
        return [
            forceString(QtGui.qApp.db.translate('Organisation', 'id', insurer, 'area')),
            insuranceArea,
            self.cmbRegCity.code() if self.cmbRegCity.isEnabled() else '',
            self.cmbLocCity.code(),
            QtGui.qApp.defaultKLADR(),
        ]

    def updateCompulsoryPolicyCompanyArea(self, forceAreaList=None):
        if not forceAreaList:
            forceAreaList = []
        self.disconnect(self.cmbCompulsoryPolisCompany, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbCompulsoryPolisCompany_currentIndexChanged)
        code = forceString(self.cmbCompulsoryInsuranceArea.code())
        area = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbCompulsoryPolisCompany.value(), 'area'))
        if QtGui.qApp.isShowPolicyInsuranceArea() and (not code or (code != area and area)):
            self.cmbCompulsoryPolisCompany.setValue(0)
        areaList = self.getAreaList(code, self.cmbCompulsoryPolisCompany.value(), self.cmbCompulsoryInsuranceArea.code())
        self.cmbCompulsoryPolisCompany.setAreaFilter(areaList + forceAreaList)
        self.connect(self.cmbCompulsoryPolisCompany, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbCompulsoryPolisCompany_currentIndexChanged)

    def updateVoluntaryPolicyCompanyArea(self, forceAreaList=None):
        if not forceAreaList:
            forceAreaList = []
        self.disconnect(self.cmbVoluntaryPolisCompany, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbVoluntaryPolisCompany_currentIndexChanged)
        code = forceString(self.cmbVoluntaryInsuranceArea.code())
        area = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbVoluntaryPolisCompany.value(), 'area'))
        if QtGui.qApp.isShowPolicyInsuranceArea() and (not code or (code != area and area)):
            self.cmbVoluntaryPolisCompany.setValue(0)
        areaList = self.getAreaList(code, self.cmbVoluntaryPolisCompany.value(), self.cmbVoluntaryInsuranceArea.code())
        self.cmbVoluntaryPolisCompany.setAreaFilter(areaList + forceAreaList)
        self.connect(self.cmbVoluntaryPolisCompany, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbVoluntaryPolisCompany_currentIndexChanged)

    def updateCompulsoryInsuranceArea(self):
        if not forceString(self.cmbCompulsoryInsuranceArea.code()):
            code = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbCompulsoryPolisCompany.value(), 'area'))
            self.cmbCompulsoryInsuranceArea.setCode(code)
        elif not self.cmbCompulsoryPolisCompany.value():
            self.cmbCompulsoryInsuranceArea.setCode('0' * 13)

    def updateVoluntaryInsuranceArea(self):
        if not forceString(self.cmbVoluntaryInsuranceArea.code()):
            code = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbVoluntaryPolisCompany.value(), 'area'))
            self.cmbVoluntaryInsuranceArea.setCode(code)
        elif not self.cmbVoluntaryPolisCompany.value():
            self.cmbVoluntaryInsuranceArea.setCode('0' * 13)

    def updatePolicyCompaniesArea(self, forceAreaList=None):
        if not forceAreaList:
            forceAreaList = []
        self.updateCompulsoryPolicyCompanyArea(forceAreaList)
        self.updateVoluntaryPolicyCompanyArea(forceAreaList)

    def blockQuotaWidgets(self, val):
        blockSignalList = self.grpQuotingDetails.children()
        for blockObj in blockSignalList:
            blockObj.blockSignals(val)

    def setQuotaWidgets(self, val):
        previousVal = self.edtQuotaIdentifier.isEnabled()
        if val != previousVal:
            self.setEnabledQuotaWidgets(val)
        if val:
            self.blockQuotaWidgets(True)
            record = self.__quotaRecord
            kladrCodeIndex = self.cmbQuotaKladr.getIndexByCode(forceString(record.value('regionCode')))
            if kladrCodeIndex:
                self.cmbQuotaKladr.setCurrentIndex(kladrCodeIndex)
            else:
                self.cmbQuotaKladr.setCurrentIndex(0)
            setLineEditValue(self.edtQuotaIdentifier, record, 'identifier')
            setSpinBoxValue(self.edtQuotaStage, record, 'stage')
            setLineEditValue(self.edtQuotaTicket, record, 'quotaTicket')
            setSpinBoxValue(self.edtQuotaAmount, record, 'amount')
            self.cmbQuotaMKB.setText(forceString(record.value('MKB')))
            setComboBoxValue(self.cmbQuotaRequest, record, 'request')

            directionDate = forceDate(record.value('directionDate'))
            if directionDate.isValid():
                self.edtQuotaDirectionDate.setDate(directionDate)
            else:
                self.edtQuotaDirectionDate.setDate(QtCore.QDate())

            self.cmbQuotaLPU.setValue(forceInt(record.value('org_id')))
            setLineEditValue(self.edtQuotaLPUFreeInput, record, 'freeInput')

            dateRegistration = forceDate(record.value('dateRegistration'))
            if dateRegistration.isValid():
                self.edtQuotaDateRegistration.setDate(dateRegistration)
            else:
                self.edtQuotaDateRegistration.setDate(QtCore.QDate())

            dateEnd = forceDate(record.value('dateEnd'))
            if dateRegistration.isValid():
                self.edtQuotaDateEnd.setDate(dateEnd)
            else:
                self.edtQuotaDateEnd.setDate(QtCore.QDate())

            orgStructure_id = forceInt(record.value('orgStructure_id'))
            if orgStructure_id:
                self.cmbQuotaOrgStructure.setValue(forceInt(record.value('orgStructure_id')))
            else:
                self.cmbQuotaOrgStructure.setCurrentIndex(
                    self.cmbQuotaOrgStructure.model().createIndex(0, 0))

            setComboBoxValue(self.cmbQuotaStatus, record, 'status')
            setTextEditValue(self.edtQuotaStatment, record, 'statment')
            self.blockQuotaWidgets(False)

    def setEnabledQuotaWidgets(self, val):
        self.edtQuotaIdentifier.setEnabled(val)
        self.edtQuotaStage.setEnabled(val)
        self.edtQuotaTicket.setEnabled(val)
        self.edtQuotaAmount.setEnabled(val)
        self.cmbQuotaMKB.setEnabled(val)
        self.cmbQuotaRequest.setEnabled(val)
        self.edtQuotaDirectionDate.setEnabled(val)
        self.cmbQuotaLPU.setEnabled(val)
        self.edtQuotaLPUFreeInput.setEnabled(val)
        self.edtQuotaDateRegistration.setEnabled(val)
        self.edtQuotaDateEnd.setEnabled(val)
        self.cmbQuotaOrgStructure.setEnabled(val)
        self.cmbQuotaStatus.setEnabled(val)
        self.edtQuotaStatment.setEnabled(val)
        self.tblClientQuotingDiscussion.setEnabled(val)
        self.cmbQuotaKladr.setEnabled(val)

    def setQuotingInfo(self):
        info = self.modelClientQuoting.info()
        limit = info.get('limit', 0)
        used = info.get('used', 0)
        confirmed = info.get('confirmed', 0)
        inQueue = info.get('inQueue', 0)
        quotaTypeName = info.get('quotaTypeName', '')
        txt = u''
        txt += quotaTypeName + '\n'
        if limit:
            txt += u'Предел: %d\n' % limit
        if used:
            txt += u'Использовано: %d\n' % used
        if confirmed:
            txt += u'Подтверждено: %d\n' % confirmed
        if inQueue:
            txt += u'В очереди: %d\n' % inQueue
        self.lblInfo.setText(txt)

    def selectClientQuotingDiscussion(self, quotaId):
        db = QtGui.qApp.db
        table = self.modelClientQuotingDiscussion.table()
        cond = [table['master_id'].eq(quotaId)]
        return db.getIdList(table, 'id', cond, 'dateMessage')

    def showQuotaDiscussionEditor(self, editor):
        if editor.exec_():
            master_id = forceInt(self.__quotaRecord.value('id'))
            itemId = editor.itemId()
            if self.checkIsLastMessage(master_id, itemId):
                agreementTypeId = editor.cmbAgreementType.value()
                if agreementTypeId:
                    statusModifier = forceInt(QtGui.qApp.db.translate('rbAgreementType', 'id',
                                                                      agreementTypeId, 'quotaStatusModifier'))
                    status = forceInt(self.__quotaRecord.value('status'))
                    if statusModifier and status != statusModifier - 1:
                        quotaRow = self.selectionModelClientQuoting.selectedIndexes()[0].row()
                        self.__quotaRecord.setValue('status', QtCore.QVariant(statusModifier - 1))
                        self.cmbQuotaStatus.setCurrentIndex(statusModifier - 1)
                        self.tblClientQuoting.model().emitRowChanged(quotaRow)
                        self.setSelectedQuota(quotaRow)
            idList = self.selectClientQuotingDiscussion(master_id)
            self.modelClientQuotingDiscussion.setIdList(idList, itemId)

    def newQuotaDiscussionEditor(self):
        editor = CQuotingEditorDialog(self)
        master_id = forceInt(self.__quotaRecord.value('id'))
        if not master_id:
            self.__quotaRecord.setValue('master_id', QtCore.QVariant(self._id))
            row = self.tblClientQuoting.currentIndex().row()
            master_id = QtGui.qApp.db.insertRecord('Client_Quoting', self.__quotaRecord)
            quotingRecords = self.modelClientQuoting.getActualQuotingRecords(self.__quotaRecord)
            code = self.cmbRegCity.code()
            if quotingRecords:
                for quotingRecord in quotingRecords:
                    status = forceInt(self.__quotaRecord.value('status'))
                    amount = forceInt(self.__quotaRecord.value('amount'))
                    self.modelClientQuoting.basicData[row] = [amount, status]
                    self.modelClientQuoting.changeData(quotingRecord, status, amount, amount.__add__)
                    if code:
                        self.modelClientQuoting.changeRegionData(status, amount, amount.__add__,
                                                                 code, quotingRecord)
        editor.setMaster_id(master_id)
        editor.cmbResponsiblePerson.setValue(QtGui.qApp.userId)
        self.showQuotaDiscussionEditor(editor)

    def editQuotaDiscussionEditor(self):
        isSelected = self.tblClientQuotingDiscussion.selectedIndexes()
        if isSelected:
            itemId = self.tblClientQuotingDiscussion.currentItemId()
            editor = CQuotingEditorDialog(self)
            editor.load(itemId)
            if editor.canBeEdit():
                self.showQuotaDiscussionEditor(editor)
            else:
                QtGui.QMessageBox.critical(self, u'Внимание!',
                                           u'Нет прав на редактирование записи',
                                           QtGui.QMessageBox.Ok,
                                           QtGui.QMessageBox.Ok
                                           )
        else:
            self.newQuotaDiscussionEditor()

    def deleteQuotaDiscussionMessage(self):
        isSelected = self.tblClientQuotingDiscussion.selectedIndexes()
        if isSelected:
            itemId = self.tblClientQuotingDiscussion.currentItemId()
            table = self.modelClientQuotingDiscussion.table()
            responsiblePersonId = forceInt(QtGui.qApp.db.translate(table,
                                                                   'id', itemId, 'responsiblePerson_id'))
            if responsiblePersonId == QtGui.qApp.userId:
                if QtGui.QMessageBox.question(self, u'Подтверждение удаления',
                                              u'Вы уверены что хотите удалить сообщение?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No
                                              ) == QtGui.QMessageBox.Yes:
                    QtGui.qApp.db.deleteRecord(table, table['id'].eq(itemId))
                    idList = self.selectClientQuotingDiscussion(forceInt(self.__quotaRecord.value('id')))
                    self.modelClientQuotingDiscussion.setIdList(idList)

            else:
                QtGui.QMessageBox.critical(self, u'Внимание!',
                                           u'Нет прав на удаление записи',
                                           QtGui.QMessageBox.Ok,
                                           QtGui.QMessageBox.Ok
                                           )

    def deleteClientQuotingRows(self):
        rows = self.tblClientQuoting.getSelectedRows()
        rows.sort(reverse=True)
        if not self.isTabAttachAlreadyLoad:
            self.on_tabWidget_currentChanged(self.tabWidget.indexOf(self.tabAttach))
        self.checkClientAttachesForDeleting(rows)
        for row in rows:
            self.tblClientQuoting.model().removeRow(row)

    def checkClientAttachesForDeleting(self, rows):
        db = QtGui.qApp.db
        attachTypeId = db.translate('rbAttachType', 'code', '9', 'id')
        clientAttachRecords = self.modelAttaches.items()
        quotaItems = self.tblClientQuoting.model().items()
        attachQuotes = {}
        clientAttachRowsForDeleting = []
        for attachRow, clientAttchRecord in enumerate(clientAttachRecords):
            if clientAttchRecord.value('attachType_id') == attachTypeId:
                quotaList = attachQuotes.get(attachRow, [])
                attachBegDate = forceDate(clientAttchRecord.value('begDate'))
                attachEndDate = forceDate(clientAttchRecord.value('endDate'))
                for quotaRow, quotaItem in enumerate(quotaItems):
                    quotaBegDate = forceDate(quotaItem.value('dateRegistration'))
                    quotaEndDate = forceDate(clientAttchRecord.value('dateEnd'))
                    if attachEndDate.isValid():
                        if quotaBegDate <= attachEndDate:
                            if quotaEndDate.isValid():
                                if quotaEndDate >= attachBegDate:
                                    quotaList.append(quotaRow)
                                    attachQuotes[attachRow] = quotaList
                            else:
                                quotaList.append(quotaRow)
                                attachQuotes[attachRow] = quotaList
                    else:
                        if quotaEndDate.isValid():
                            if quotaEndDate >= attachBegDate:
                                quotaList.append(quotaRow)
                                attachQuotes[attachRow] = quotaList
                        else:
                            quotaList.append(quotaRow)
                            attachQuotes[attachRow] = quotaList
        for attachRow, clientAttchRecord in enumerate(clientAttachRecords):
            if clientAttchRecord.value('attachType_id') == attachTypeId:
                quotaList = attachQuotes.get(attachRow, [])
                for row in rows:
                    if row in quotaList:
                        quotaList.pop(quotaList.index(row))
                if len(quotaList) == 0:
                    clientAttachRowsForDeleting.append(attachRow)
        if clientAttachRowsForDeleting:
            if QtGui.QMessageBox.question(self,
                                          u'Внимание!',
                                          u'Удалить соответствующие прикрепления пациента?',
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                clientAttachRowsForDeleting.sort(reverse=True)
                for attachRow in clientAttachRowsForDeleting:
                    self.tblAttaches.model().removeRow(attachRow)

    def checkIsLastMessage(self, quotingId, messageId):
        db = QtGui.qApp.db
        table = db.table('Client_QuotingDiscussion')
        cond = [table['master_id'].eq(quotingId)]
        stmt = db.selectStmt(table, 'MAX(id)', cond)
        query = db.query(stmt)
        if query.first():
            lastId = query.value(0).toInt()[0]
            if lastId == messageId:
                return True
        return False

    def setSelectedQuota(self, row=None):
        if row == None:
            items = self.modelClientQuoting.items()
            if items:
                row = 0
            else:
                return
        index = self.modelClientQuoting.index(row, 0)
        self.selectionModelClientQuoting.setCurrentIndex(index, QtGui.QItemSelectionModel.Rows)
        self.tblClientQuoting.setCurrentIndex(index)

    def setMKBTextInfo(self, text):
        if len(text) > 1:
            if text[-1:] == '.':
                text = text[:-1]
            info = forceString(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', text, 'DiagName'))
            self.lblMKBText.setText('<i>%s</i>' % info)
            if info:
                return True
            else:
                return False
        else:
            self.lblMKBText.clear()
            return False

    def initTabDiagnosises(self):
        oldIsDirty = self.isDirty()
        editable = QtGui.qApp.userHasRight(Users.Rights.urChangeDiagnosisPND)
        if editable:
            self.tblMainDiagnosises.addPopupDelRow()
            self.tblSecondaryDiagnosises.addPopupDelRow()
        self.modelClientMainDiagnosises.setEditable(editable)
        self.modelClientMainDiagnosises.loadItems(self.itemId())
        self.modelClientSecondaryDiagnosises.setEditable(editable)
        self.modelClientSecondaryDiagnosises.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabDiagnosisesAlreadyLoad = True

    def initTabDisability(self):
        oldIsDirty = self.isDirty()
        self.tblClientDisability.addPopupDelRow()
        self.modelClientDisability.loadItems(self.itemId())
        self.tblClientBenefits.addPopupDelRow()
        self.modelClientBenefits.setClassFilter("flatCode like 'benefits'")
        self.modelClientBenefits.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabDisabilityAlreadyLoad = True

    def initTabSocStatus(self):
        oldIsDirty = self.isDirty()
        self.cmbSocStatusDocType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code IN (\'2\', \'5\', \'7\'))')
        self.tblSocStatuses.addPopupDelRow()
        self.tblSocStatuses.addPopupRecordProperies()
        self.changeSocStatusClassFilterAction = QtGui.QAction(u'Изменить список отображаемых классов...',
                                                              self,
                                                              triggered=self.changeSocStatusClassFilter)
        self.tblSocStatuses.addPopupActions([self.changeSocStatusClassFilterAction])

        socStatusClassIdList = [forceString(item) for item in QtGui.qApp.preferences.appPrefs.get('showedSocStatusClassIdList', QtCore.QVariant([])).toList()]
        socStatusClassFilter = ('id IN (%s)' % ', '.join(socStatusClassIdList)) if socStatusClassIdList else None
        if QtGui.qApp.isPNDDiagnosisMode() and not socStatusClassFilter:
            db = QtGui.qApp.db
            socStatusClassFilter = db.joinOr(["flatCode like '%s'" % c for c in [u'socStatus',  # Соц. статус
                                                                                 u'accommodation',  # Условия проживания
                                                                                 u'maritalStatus',  # Семейное положение
                                                                                 u'education',  # Образование
                                                                                 u'finishedClasses'  # Законченно классов
                                                                                 u'citizenship'  # Гражданство
                                                                                 ]])
        self.modelSocStatuses.setClassFilter(socStatusClassFilter)
        self.modelSocStatuses.loadItems(self.itemId())
        self.tblSocStatuses.sortByColumn(0)

        self.setIsDirty(oldIsDirty)
        self.isTabSocStatusAlreadyLoad = True

    def initTabAttach(self):
        oldIsDirty = self.isDirty()
        self.tblAttaches.addPopupDelRow()
        self.tblAttaches.addPopupRecordProperies()
        self.modelAttaches.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabAttachAlreadyLoad = True

    def initTabWork(self):
        oldIsDirty = self.isDirty()
        self.cmbWorkOKVED.setAddNone(True)

        self.tblWorkHurts.addPopupDelRow()
        self.tblWorkHurtFactors.addPopupDelRow()
        if QtGui.qApp.userHasRight(Users.Rights.urDeleteClientOldWorks):
            self.tblOldWorks.addPopupDelRow()

        workRecord = None
        if self.itemId():
            workRecord = getClientWork(self.itemId())

        self.setWorkRecord(workRecord)

        if workRecord:
            workId = forceRef(workRecord.value('id'))
            self.modelWorkHurts.loadItems(workId)
            self.modelWorkHurtFactors.loadItems(workId)
            self.modelOldWorks.setFilter('id != %d' % workId)
        else:
            self.modelWorkHurts.clearItems()
            self.modelWorkHurtFactors.clearItems()

        self.modelOldWorks.loadItems(self.itemId())

        self.setIsDirty(oldIsDirty)
        self.isTabWorkAlreadyLoad = True

        self.updateVisibleState(self.tabWork, self._invisibleObjectsNameList)

    def initTabDocs(self):
        oldIsDirty = self.isDirty()
        self.tblSocStatusDocs.addPopupDelRow()
        self.tblSocStatusDocs.addPopupRecordProperies()
        self.modelSocStatusDocs.loadItems(self.itemId())
        self.tblPaymentScheme.addPopupDelRow()
        self.tblPaymentScheme.addPopupRecordProperies()
        self.connect(self.btnAddPaymentScheme, QtCore.SIGNAL('clicked()'), self.modelPaymentScheme.addNewContract)
        self.connect(self.btnDelPaymentScheme, QtCore.SIGNAL('clicked()'), self.tblPaymentScheme.on_deleteRows)
        self.modelPaymentScheme.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabDocsAlreadyLoad = True

    def initTabFeature(self):
        oldIsDirty = self.isDirty()
        self.cmbBloodType.setTable('rbBloodType', True)
        self.edtBloodTypeDate.canBeEmpty(True)
        self.tblAllergy.addPopupDelRow()
        self.tblAllergy.addPopupRecordProperies()
        self.tblIntoleranceMedicament.addPopupDelRow()
        self.tblIntoleranceMedicament.addPopupRecordProperies()
        self.tblAnthropometric.addPopupDelRow()
        self.tblAnthropometric.addPopupRecordProperies()
        self.tblCheckup.addPopupDelRow()
        self.tblCheckup.addPopupRecordProperies()
        self.cmbBloodType.setValue(self.bloodType_id)
        self.edtBloodTypeDate.setDate(self.bloodDate)
        self.edtBloodTypeNotes.setText(self.bloodNotes)
        self.modelAllergy.loadItems(self.itemId())
        self.modelIntoleranceMedicament.loadItems(self.itemId())
        self.modelClientAnthropometric.loadItems(self.itemId())
        self.modelClientCheckup.setClassFilter("flatCode like 'checkups'")
        self.modelClientCheckup.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabFeatureAlreadyLoad = True

    def initTabIdentification(self):
        oldIsDirty = self.isDirty()
        self.tblClientIdentification.addPopupDelRow()
        self.tblClientIdentification.addPopupRecordProperies()
        self.modelClientIdentification.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabIdentificationAlreadyLoad = True

    def initTabRelations(self):
        oldIsDirty = self.isDirty()
        self.tblDirectRelations.addPopupDelRow()
        self.tblDirectRelations.addPopupRecordProperies()
        self.tblDirectRelations.addRelativeClientEdit()
        self.tblDirectRelations.setItemDelegate(MyLocItemDelegate(self.tblDirectRelations))
        self.tblBackwardRelations.addPopupDelRow()
        self.tblBackwardRelations.addPopupRecordProperies()
        self.tblBackwardRelations.addRelativeClientEdit()
        self.tblBackwardRelations.setItemDelegate(MyLocItemDelegate(self.tblBackwardRelations))
        clientId = self.itemId()
        if clientId:
            self.modelDirectRelations.loadItems(clientId)
            self.modelDirectRelations.setClientId(clientId)
            self.modelDirectRelations.setDirectRelationFilter(self.cmbSex.currentIndex())
            self.modelBackwardRelations.loadItems(clientId)
            self.modelBackwardRelations.setClientId(clientId)
            self.modelBackwardRelations.setBackwardRelationFilter(self.cmbSex.currentIndex())
        self.setIsDirty(oldIsDirty)
        self.isTabRelationsAlreadyLoad = True

    def initTabQuoting(self):
        oldIsDirty = self.isDirty()
        self.tblClientQuoting.addPopupSelectAllRow()
        self.tblClientQuoting.addPopupClearSelectionRow()
        self.actDelClientQuotingRows = QtGui.QAction(u'Удалить выделенное', self.tblClientQuoting)
        self.tblClientQuoting.popupMenu().addAction(self.actDelClientQuotingRows)
        if not QtGui.qApp.userHasRight(Users.Rights.urDeleteClientQuotingRows):
            self.actDelClientQuotingRows.setEnabled(False)
        self.connect(self.actDelClientQuotingRows, QtCore.SIGNAL('triggered()'), self.deleteClientQuotingRows)
        self.tblClientQuoting.addPopupRecordProperies()
        self.actNewMessage = QtGui.QAction(u'Добавить сообщение', self.tblClientQuotingDiscussion)
        self.connect(self.actNewMessage, QtCore.SIGNAL('triggered()'), self.newQuotaDiscussionEditor)
        self.actEditMessage = QtGui.QAction(u'Редактировать сообщение', self.tblClientQuotingDiscussion)
        self.connect(self.actEditMessage, QtCore.SIGNAL('triggered()'), self.editQuotaDiscussionEditor)
        self.actDelMessage = QtGui.QAction(u'Удалить сообщение', self.tblClientQuotingDiscussion)
        self.connect(self.actDelMessage, QtCore.SIGNAL('triggered()'), self.deleteQuotaDiscussionMessage)
        self.tblClientQuotingDiscussion.addPopupAction(self.actNewMessage)
        self.tblClientQuotingDiscussion.addPopupAction(self.actEditMessage)
        self.tblClientQuotingDiscussion.addPopupAction(self.actDelMessage)
        self.modelClientQuoting.loadItems(self.itemId())
        if self.__regAddress:
            self.modelClientQuoting.setRegCityCode(self.__regAddress['KLADRCode'])
        self.setSelectedQuota()
        self.setIsDirty(oldIsDirty)
        self.isTabQuotingAlreadyLoad = True

    def initTabMisdemeanor(self):
        oldIsDirty = self.isDirty()
        self.tblMisdemeanor.addPopupDelRow()
        self.tblMisdemeanor.addPopupRecordProperies()
        itemId = self.itemId()
        self.modelClientMisdemeanor.loadItems(itemId)
        if QtGui.qApp.isPNDDiagnosisMode():
            self.tblCompulsoryTreatment.addPopupDelRow()
            self.tblCompulsoryTreatment.addPopupRecordProperies()
            self.modelClientCompulsoryTreatment.loadItems(itemId)
        self.setIsDirty(oldIsDirty)
        self.isTabMisdemeanorAlreadyLoad = True

    def initTabSuicide(self):
        oldIsDirty = self.isDirty()
        self.tblSuicide.addPopupDelRow()
        self.tblSuicide.addPopupRecordProperies()
        self.modelClientSuicide.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabSuicideAlreadyLoad = True

    def initTabMonitoring(self):
        oldIsDirty = self.isDirty()
        self.tblMonitoring.addPopupDelRow()
        self.tblMonitoring.addPopupRecordProperies()
        self.modelClientMonitoring.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabMonitoringAlreadyLoad = True

    def initTabForeignHospitalization(self):
        oldIsDirty = self.isDirty()
        self.tblForeignHospitalization.addPopupDelRow()
        self.tblForeignHospitalization.addPopupRecordProperies()
        self.modelForeignHospitalization.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabForeignHospitalizationAlreadyLoad = True

    def initTabDispanserization(self):
        oldIsDirty = self.isDirty()
        self.tblDispaserization.addPopupDelRow()
        self.tblDispaserization.addPopupRecordProperies()
        self.modelDispanserization.loadItems(self.itemId())
        self.setIsDirty(oldIsDirty)
        self.isTabDispanserizationAlreadyLoad = True

    def initTabContacts(self):
        oldIsDirty = self.isDirty()
        self.cmbInfoSource.setTable('rbInfoSource', True)
        record = self.record()
        if record:
            self.cmbInfoSource.setValue(forceRef(record.value('rbInfoSource_id')))
            # if u'онко' in QtGui.qApp.currentOrgInfis():
            self.infoSourceRecord = QtGui.qApp.db.getRecordEx(
                table='ClientInfoSource',
                cols=['id', 'docDoc', 'onMend', 'rbInfoSource_id', 'infoSourceDate', 'client_id'],
                where='deleted = 0 AND client_id = %s' % (self.itemId())
            )
            if self.infoSourceRecord:
                self.cmbInfoSource.setValue(forceRef(self.infoSourceRecord.value('rbInfoSource_id')))
                # self.chkDocDoc.setChecked(forceBool(self.infoSourceRecord.value('docDoc')))
                # self.chkMend.setChecked(forceBool(self.infoSourceRecord.value('onMend')))
                self.edtInfoSourceDate.setDate(forceDate(self.infoSourceRecord.value('infoSourceDate')))

        # self.chkMend.setVisible(self.cmbInfoSource.isVisible())
        # self.chkDocDoc.setVisible(self.cmbInfoSource.isVisible())
        self.edtInfoSourceDate.setVisible(self.cmbInfoSource.isVisible())
        self.setIsDirty(oldIsDirty)
        self.isTabContactsAlreadyLoad = True

    def saveInfoSourceRecord(self, clientId):
        if self.isVisibleObject(self.lblInfoSource) and (self.edtInfoSourceDate.isVisible()):
            db = QtGui.qApp.db
            tableClientInfoSource = db.table('ClientInfoSource')
            if self.infoSourceRecord:
                self.infoSourceRecord.setValue('modifyPerson_id', toVariant(QtGui.qApp.userId))
                self.infoSourceRecord.setValue('modifyDateTime', toVariant(QtCore.QDateTime.currentDateTime()))
            else:
                self.infoSourceRecord = tableClientInfoSource.newRecord()
                self.infoSourceRecord.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
                self.infoSourceRecord.setValue('createDateTime', toVariant(QtCore.QDateTime.currentDateTime()))

            self.infoSourceRecord.setValue('client_id', toVariant(clientId))
            self.infoSourceRecord.setValue('rbInfoSource_id', toVariant(self.cmbInfoSource.value()))
            # self.infoSourceRecord.setValue('docDoc', toVariant(self.chkDocDoc.isChecked()))
            # self.infoSourceRecord.setValue('onMend', toVariant(self.chkMend.isChecked()))
            self.infoSourceRecord.setValue('infoSourceDate', toVariant(self.edtInfoSourceDate.date()))
            db.insertOrUpdate(tableClientInfoSource, self.infoSourceRecord)

    def switchTabByEvent(self, event):
        def shiftTab(forward):
            index = self.tabWidget.currentIndex()
            lastIndex = self.tabWidget.count() - 1
            nextIndexFound = False
            nextIndex = index
            while not nextIndexFound:
                if forward:
                    nextIndex = 0 if nextIndex == lastIndex else nextIndex + 1
                else:
                    nextIndex = lastIndex if nextIndex == 0 else nextIndex - 1
                if self.tabWidget.isTabEnabled(nextIndex) or nextIndex == index:
                    nextIndexFound = True
                self.tabWidget.setCurrentIndex(nextIndex)
                self.setFocus(QtCore.Qt.TabFocusReason)
                return True

        key = event.key()
        modifiers = event.modifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            numericKeys = [QtCore.Qt.Key_1, QtCore.Qt.Key_2, QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5, QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8, QtCore.Qt.Key_9]
            if key == QtCore.Qt.Key_Tab:
                if shiftTab(forward=True):
                    return True
            elif key in numericKeys:
                nextIndex = int(event.text()) - 1
                if nextIndex <= self.tabWidget.count() and self.tabWidget.isTabEnabled(nextIndex):
                    self.tabWidget.setCurrentIndex(nextIndex)
                    self.setFocus(QtCore.Qt.OtherFocusReason)
                    return True
        elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if key == QtCore.Qt.Key_Backtab:
                if shiftTab(forward=False):
                    return True
        return False

    def keyPressEvent(self, event):
        if self.switchTabByEvent(event):
            event.accept()
        else:
            if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
                self.accept()
            else:
                CItemEditorBaseDialog.keyPressEvent(self, event)

    def eventFilter(self, obj, event):
        if obj in [self.edtDocSerialLeft, self.edtDocSerialRight] \
                and event.type() == QtCore.QEvent.MouseButtonPress:
            obj.setCursorPosition(0)
            return True

        if type(event) == QtGui.QKeyEvent:
            return self.switchTabByEvent(event)
        return False

    @QtCore.pyqtSlot()
    def changeSocStatusClassFilter(self):
        records = QtGui.qApp.db.getRecordList(table='rbSocStatusClass',
                                              cols='id, name',
                                              where='group_id IS NULL',
                                              order='code')
        nameList = []
        checkStateList = []
        classIdList = self.modelSocStatuses.availableClassIdList()
        for record in records:
            nameList.append(forceString(record.value('name')))
            checkStateList.append(forceString(record.value('id')) in classIdList)

        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(u'Выберите классы социальных статусов для отображения ...')
        layout = QtGui.QVBoxLayout()

        view = QtGui.QTableView()
        view.verticalHeader().setVisible(False)
        view.horizontalHeader().setVisible(False)
        model = CCheckableModel(strings=nameList)
        model.setCheckStateList(checkStateList)
        view.setModel(model)
        view.resizeColumnsToContents()
        view.verticalHeader().stretchLastSection()
        layout.addWidget(view)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dlg.accept)
        buttonBox.rejected.connect(dlg.reject)
        layout.addWidget(buttonBox)

        dlg.setLayout(layout)

        if dlg.exec_():
            checkStateList = model.checkStateList()
            classIdList = []
            for idx, record in enumerate(records):
                if checkStateList[idx]:
                    classIdList.append(forceString(record.value('id')))
            classFilterCond = u'id IN (%s)' % ', '.join(classIdList) if classIdList else '1'
            self.modelSocStatuses.setClassFilter(classFilterCond)
            QtGui.qApp.preferences.appPrefs['showedSocStatusClassIdList'] = QtCore.QVariant(classIdList)
            if (not self.modelSocStatuses.isDirty() or
                        QtGui.QMessageBox.Yes == QtGui.QMessageBox.question(self,
                                                                            u'Подтвердите обновление содержимого',
                                                                            u'В таблице имеются несохраненные изменения.\n'
                                                                            u'Хотите обновить содержимое в соответствие с новыми настройками,\n'
                                                                            u'но с потерей несохранненых изменений?\n'
                                                                            u'(иначе настройки вступят в силу после закрытия окна)',
                                                                            buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                            defaultButton=QtGui.QMessageBox.NoButton)
                ):
                self.modelSocStatuses.loadItems(self.itemId())

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        widget = self.tabWidget.widget(index)
        if widget == self.tabPassport:
            self.syncPoliciesBackward()
            self.syncClientDocsBackward()
        elif widget == self.tabSocStatus:
            if not self.isTabSocStatusAlreadyLoad:
                self.initTabSocStatus()
        elif widget == self.tabAttach:
            if not self.isTabAttachAlreadyLoad:
                self.initTabAttach()
        elif widget == self.tabWork:
            if not self.isTabWorkAlreadyLoad:
                self.initTabWork()
        elif widget == self.tabDocs:
            if not self.isTabDocsAlreadyLoad:
                self.initTabDocs()
        elif widget == self.tabFeature:
            if not self.isTabFeatureAlreadyLoad:
                self.initTabFeature()
        elif widget == self.tabIdentification:
            if not self.isTabIdentificationAlreadyLoad:
                self.initTabIdentification()
        elif widget == self.tabRelations:
            if not self.isTabRelationsAlreadyLoad:
                self.initTabRelations()
        elif widget == self.tabContacts:
            if not self.isTabContactsAlreadyLoad:  # empty
                self.initTabContacts()
        elif widget == self.tabQuoting:
            if not self.isTabQuotingAlreadyLoad:
                self.initTabQuoting()
        elif widget == self.tabDiagnosises:
            if not self.isTabDiagnosisesAlreadyLoad:
                self.initTabDiagnosises()
        elif widget == self.tabDisability:
            if not self.isTabDisabilityAlreadyLoad:
                self.initTabDisability()
        elif widget == self.tabMisdemeanor:
            if not self.isTabMisdemeanorAlreadyLoad:
                self.initTabMisdemeanor()
        elif widget == self.tabSuicide:
            if not self.isTabSuicideAlreadyLoad:
                self.initTabSuicide()
        elif widget == self.tabMonitoring:
            if not self.isTabMonitoringAlreadyLoad:
                self.initTabMonitoring()
        elif widget == self.tabForeignHospitalization:
            if not self.isTabForeignHospitalizationAlreadyLoad:
                self.initTabForeignHospitalization()
        elif widget == self.tabDispanserization:
            if not self.isTabDispanserizationAlreadyLoad:
                self.initTabDispanserization()
        if widget != self.tabPassport:
            self.syncIdentificationDocs()
            self.syncPolicies()

        if widget == self.tabRelations:
            self.modelDirectRelations.setRegAddressInfo(self.getParamsRegAddress())
            self.modelDirectRelations.setLogAddressInfo(self.getParamsLocAddress())
            self.modelBackwardRelations.setRegAddressInfo(self.getParamsRegAddress())
            self.modelBackwardRelations.setLogAddressInfo(self.getParamsLocAddress())
        else:
            self.regAddressInfo = {}
            self.logAddressInfo = {}
        if widget:
            widget.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSlot()
    def on_lblCompulsoryPolicy_clicked(self):
        self._compulsoryPolicyVisible = not self._compulsoryPolicyVisible
        self.setPolicyWidgetsVisible(self.lblCompulsoryPolicy, self.frmCompulsoryPolicy, self._compulsoryPolicyVisible)

    @QtCore.pyqtSlot()
    def on_lblVoluntaryPolicy_clicked(self):
        self._voluntaryPolicyVisible = not self._voluntaryPolicyVisible
        self.setPolicyWidgetsVisible(self.lblVoluntaryPolicy, self.frmVoluntaryPolicy, self._voluntaryPolicyVisible)

    def setPolicyWidgetsVisible(self, stateWidget, groupWidget, isVisible):
        groupWidget.setVisible(isVisible)
        text = forceString(stateWidget.text())
        if u'+ Полис' in text:
            if not isVisible:
                text = text.replace(u'+ Полис', u'- Полис')
        elif u'- Полис' in text:
            if isVisible:
                text = text.replace(u'- Полис', u'+ Полис')
        else:
            prefix = u'+ ' if isVisible else u'- '
            text = text.replace(u'Полис', prefix + u'Полис')

        stateWidget.setText(text)

    @QtCore.pyqtSlot(QtCore.QString)
    def onBirthDateChanged(self, text):
        birthDate = self.edtBirthDate.date()
        if not birthDate.isNull() and \
                ((self._birthMaxDate and birthDate > self._birthMaxDate)
                 or (self._birthMinDate and birthDate < self._birthMinDate)):
            self.checkValueMessage(u'Возраст пациента не соответствует типу сети подразделения.', False, self.edtBirthDate)
            self.edtBirthDate.setDate(QtCore.QDate())

    @QtCore.pyqtSlot()
    def on_edtLastName_editingFinished(self):
        lastName = forceStringEx(self.edtLastName.text())
        self.edtLastName.setText(trimNameSeparators(nameCase(forceStringEx(lastName)), 'lastName'))

    @QtCore.pyqtSlot()
    def on_edtFirstName_editingFinished(self):
        firstName = trimNameSeparators(forceStringEx(self.edtFirstName.text()), 'firstName')
        self.edtFirstName.setText(nameCase(firstName))
        self.evalSexByName('rdFirstName', firstName)

    @QtCore.pyqtSlot()
    def on_tblContacts_editingFinished(self):
        pass

    @QtCore.pyqtSlot()
    def on_edtPatrName_editingFinished(self):
        patrName = trimNameSeparators(forceStringEx(self.edtPatrName.text()), 'patrName')
        self.edtPatrName.setText(nameCase(patrName))
        self.evalSexByName('rdPatrName', patrName)

    @QtCore.pyqtSlot()
    def on_btnCopyPrevAddress_clicked(self):
        if CClientEditDialog.prevAddress:
            reg, freeInputReg, isVillagerReg, loc, freeInputLoc, isVillagerLoc = CClientEditDialog.prevAddress
            self.setRegAddress(reg, freeInputReg, isVillagerReg)
            self.setLocAddress(loc, freeInputLoc, isVillagerLoc)
        elif self.regAddressInfo or self.locAddressInfo:
            self.setRegAddressRelation(self.regAddressInfo)
            self.setLocAddressRelation(self.locAddressInfo)

    @QtCore.pyqtSlot()
    def on_btnIIN_clicked(self):
        from Exchange.R90.IINService.IINService import CR90IINService
        url = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'IINUrl', ''))
        login = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'IINLogin', ''))
        password = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'IINPassword', ''))
        if not url or not password or not url:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Необходимо заполнить настройки РПН!', QtGui.QMessageBox.Ok)
        service = CR90IINService(url=url, login=login, password=password)
        iin = unicode(self.edtIIN.text())
        name = unicode(self.edtLastName.text() + u' ' + self.edtFirstName.text() + u' ' + self.edtPatrName.text())
        if iin.strip() == u'' and name.strip() == u'':
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Должно быть заполнено либо имя, либо ИИН!', QtGui.QMessageBox.Ok)
        if iin: res = service.getPatient(IIN=iin)
        else: res = service.getPatient(name=name)
        if not res:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Произошла ошибка:\n' + service.error, QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.information(self, u'Успешно!', u'Данные получены успешно:\n' +
                                          '\n'.join([unicode(k) + u' : ' + unicode(s) for k,s in service.patientResult.items()]),
                                          QtGui.QMessageBox.Ok
                                          )
            self.edtFirstName.setText(service.patientResult['name'])
            self.edtPatrName.setText(service.patientResult['middlename'])
            self.edtLastName.setText(service.patientResult['surname'])
            self.edtBirthDate.setDate(QtCore.QDate.fromString(service.patientResult['birthdate'], 'dd.MM.yyyy'))
            self.edtLocFreeInput.setText(service.patientResult['address'])
            self.edtIIN.setText(service.patientResult['iin'])
            if service.patientResult['phone']: self.tblContacts.model().setDialogContact(1, service.patientResult['phone'])

    @QtCore.pyqtSlot(bool)
    def on_chkRegKLADR_toggled(self, checked):
        self.edtRegFreeInput.setEnabled(not checked)
        self.chkRegIsVillager.setEnabled(not checked)
        self.cmbRegCity.setEnabled(checked)
        self.cmbRegStreet.setEnabled(checked)
        self.edtRegHouse.setEnabled(checked)
        self.edtRegCorpus.setEnabled(checked)
        self.edtRegFlat.setEnabled(checked)

    # @QtCore.pyqtSlot(bool)
    # def on_chkDocDoc_toggled(self, checked):
    #     if self.chkDocDoc.isChecked():
    #         self.edtInfoSourceDate.setDate(QtCore.QDate.currentDate())
    #
    # @QtCore.pyqtSlot(bool)
    # def on_chkMend_toggled(self, checked):
    #     if self.chkMend.isChecked():
    #         self.edtInfoSourceDate.setDate(QtCore.QDate.currentDate())

    @QtCore.pyqtSlot(bool)
    def on_chkLocKLADR_toggled(self, checked):
        self.edtLocFreeInput.setEnabled(not checked)
        self.chkLocIsVillager.setEnabled(not checked)
        self.cmbLocCity.setEnabled(checked)
        self.cmbLocStreet.setEnabled(checked)
        self.edtLocHouse.setEnabled(checked)
        self.edtLocCorpus.setEnabled(checked)
        self.edtLocFlat.setEnabled(checked)

    @QtCore.pyqtSlot(int)
    def on_cmbRegCity_currentIndexChanged(self, val):
        code = self.cmbRegCity.code()
        self.cmbRegStreet.setCity(code)
        if QtGui.qApp.defaultKLADR()[:5] != code[:5]:
            self.cmbRegDistrict.setCode(0)
            self.cmbRegDistrict.setDisabled(True)
        else:
            self.cmbRegDistrict.setDisabled(False)
        # self.updatePolicyCompaniesArea()

    @QtCore.pyqtSlot()
    def on_btnCopy_clicked(self):
        code = self.cmbRegCity.code()
        self.cmbLocCity.setCode(code)
        self.cmbLocDistrict.setValue(self.cmbRegDistrict.getValue())
        self.cmbLocStreet.setCity(code)
        self.cmbLocStreet.setCode(self.cmbRegStreet.code())
        self.edtLocHouse.setText(self.edtRegHouse.text())
        self.edtLocCorpus.setText(self.edtRegCorpus.text())
        self.edtLocFlat.setText(self.edtRegFlat.text())
        self.edtLocFreeInput.setText(self.edtRegFreeInput.text())
        self.chkLocIsVillager.setChecked(self.chkRegIsVillager.isChecked())
        self.chkLocKLADR.setChecked(self.chkRegKLADR.isChecked())

    @QtCore.pyqtSlot(int)
    def on_cmbLocCity_currentIndexChanged(self, index):
        code = self.cmbLocCity.code()
        self.cmbLocStreet.setCity(code)
        if QtGui.qApp.defaultKLADR()[:5] != code[:5]:
            self.cmbLocDistrict.setCode(0)
            self.cmbLocDistrict.setDisabled(True)
        else:
            self.cmbLocDistrict.setDisabled(False)
        self.updatePolicyCompaniesArea()

    @QtCore.pyqtSlot(int)
    def on_cmbDocType_currentIndexChanged(self, index):
        docTypeId = self.cmbDocType.value()
        docTypeIsEmpty = docTypeId in [0, None]
        curDocTypeIsEmpty = self.documentTypeId in [0, None]

        if docTypeIsEmpty:
            self.edtDocSerialLeft.setEnabled(False)
            self.edtDocSerialRight.setEnabled(False)
            self.edtDocNumber.setEnabled(False)
            self.edtDocDate.setEnabled(False)
            self.edtWhoExtraditedDoc.setEnabled(False)

            if curDocTypeIsEmpty:
                return

        if curDocTypeIsEmpty:
            self.edtDocSerialLeft.setEnabled(True)
            self.edtDocSerialRight.setEnabled(True)
            self.edtDocNumber.setEnabled(True)
            self.edtDocDate.setEnabled(True)
            self.edtWhoExtraditedDoc.setEnabled(True)

        if self.useInputMask:
            textSerial = unicode(self.edtDocSerialLeft.text()) + unicode(self.edtDocSerialRight.text())
            textNumber = unicode(self.edtDocNumber.text())
            if textSerial or textNumber:
                message = u'При смене типа документа его данные будут стерты.\n\nПродолжить?'
                if QtGui.QMessageBox.question(self, u'Внимание!', message, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.edtDocSerialLeft.setText('')
                    self.edtDocSerialRight.setText('')
                    self.edtDocNumber.setText('')
                    self.edtDocDate.setEditText('')
                    self.edtWhoExtraditedDoc.setText('')
                else:
                    self.cmbDocType.setValue(self.documentTypeId)
                    return
            self.setInputMask(docTypeId)
        else:
            serialFormat = forceInt(QtGui.qApp.db.translate('rbDocumentType', 'id', docTypeId, 'serial_format'))
            self.edtDocSerialLeft.setFormat(serialFormat)
            self.edtDocSerialRight.setFormat(serialFormat)
        self.documentTypeId = docTypeId

    @QtCore.pyqtSlot(int)
    def on_modelIdentificationDocs_documentChanged(self, row):
        items = self.modelIdentificationDocs.items()
        self.setDocumentRecord(items[row] if 0 <= row < len(items) else None)

    @QtCore.pyqtSlot()
    def on_btnSearchPolicy_clicked(self):
        if not self.isTabDocsAlreadyLoad:
            self.on_tabWidget_currentChanged(4)

        try:
            descr = QtGui.qApp.identService(self.itemId(),
                                           forceStringEx(self.edtFirstName.text()),
                                           forceStringEx(self.edtLastName.text()),
                                           forceStringEx(self.edtPatrName.text()),
                                           self.cmbSex.currentIndex(),
                                           self.edtBirthDate.date(),
                                           forceStringEx(self.edtSNILS.text()),
                                           forceString(self.cmbCompulsoryPolisKind.value()),
                                           forceStringEx(self.edtCompulsoryPolisSerial.text()),
                                           forceStringEx(self.edtCompulsoryPolisNumber.text()),
                                           forceStringEx(self.cmbDocType.value()),
                                           forceStringEx(self.edtDocSerialLeft.text()+' '+self.edtDocSerialRight.text()),
                                           forceStringEx(self.edtDocNumber.text()))
            showDischarge = False  # QtGui.qApp.showPolicyDischargeDate()
            if descr and not hasattr(descr, 'message'):
                self.isSearchPolicy = True
                isKras = QtGui.qApp.defaultKLADR().startswith('23')
                if isKras:
                    begDateStr = forceString(descr.begDate)
                    endDateStr = forceString(descr.endDate)
                    policyPeriodStr = u''
                    if begDateStr or endDateStr:
                        policyPeriodStr = u'действителен\t'
                        if begDateStr: policyPeriodStr += u'с %s ' % begDateStr
                        if endDateStr: policyPeriodStr += u'по %s' % endDateStr
                        policyPeriodStr += u'\n'

                    msg = \
                        u'Найден полис:\n' \
                        u'ФИО:\t\t%s\n'\
                        u'Пол:\t\t%s\n' \
                        u'Дата рождения:\t%s\n' \
                        u'СМО:\t\t%s\n'\
                        u'СНИЛС:\t\t%s\n'\
                        u'серия:\t\t%s\n'\
                        u'номер:\t\t%s\n'\
                        u'тип:\t\t%s\n' \
                        u'вид:\t\t%s\n'\
                        u'%s\n'\
                        u'\n'\
                        u'Проведена диспансеризация/профосмотр в текущем году:\n'\
                        u'Код вида помощи: %s\n'\
                        u'Дата начала: %s\n'\
                        u'Дата окончания: %s\n'\
                        u'Код МО, проводивший\n'\
                        u'диспансеризацию/профосмотр:%s\n'\
                        u'Обновить данные полиса?' % (
                        formatName(descr.lastName, descr.firstName, descr.patrName),
                        descr.sex,
                        forceString(descr.birthDate),
                        forceString(QtGui.qApp.db.translate('Organisation', 'id', descr.smoId, 'shortName')) if descr.smoId else '-',
                        descr.Snils,
                        descr.policySerial,
                        descr.policyNumber,
                        forceString(QtGui.qApp.db.translate('rbPolicyType', 'id', descr.policyTypeId, 'name')) if descr.policyTypeId else '-',
                        forceString(QtGui.qApp.db.translate('rbPolicyKind', 'id', descr.policyKindId, 'name')) if descr.policyKindId else '-',
                        policyPeriodStr,
                        forceString(QtGui.qApp.db.translate('rbMedicalAidType', 'regionalCode', descr.dCode,
                                                            'name')) if descr.dCode else '-',
                        forceString(descr.dDATN) if descr.dDATN else '-',
                        forceString(descr.dDATO) if descr.dDATO else '-',
                        forceString(QtGui.qApp.db.translate('Organisation', 'infisCode', descr.dCODE_MO,
                                                            'shortName')) if descr.dCODE_MO else '-'
                        )
                else:

                    strAttachList = u''
                    if descr.attachList:
                        for v in descr.attachList:
                            strAttachList += v + u'\n'

                    msg = u'Найден полис:\n'\
                    u'СМО:   %s\n'\
                    u'серия: %s\n'\
                    u'номер: %s\n'\
                    u'тип:   %s\n'\
                    u'действителен с %s по %s\n \n'\
                    u'Найдено прикрепление: \n'\
                    u'%s \n \n'\
                    u'Список прикреплений:\n'\
                    u'%s \n'\
                    u'Обновить данные полиса?' % (
                        forceString(QtGui.qApp.db.translate('Organisation', 'id', descr.smoId, 'shortName')) if descr.smoId else '-',
                        descr.policySerial,
                        descr.policyNumber,
                        forceString(QtGui.qApp.db.translate('rbPolicyType', 'id', descr.policyTypeId, 'name')) if descr.policyTypeId else '-',
                        forceString(descr.begDate),
                        forceString(descr.endDate),
                        forceString(QtGui.qApp.db.translate('OrgStructure', 'id', descr.attach, 'name')) if descr.attach else u'Пациент не прикреплен к данному МО\n',
                        strAttachList)
                replace = QtGui.QMessageBox(self)
                replace.setWindowTitle(u'Поиск полиса')
                replace.setText(msg)
                replace.addButton(QtGui.QPushButton(u'Обновить полис'), QtGui.QMessageBox.YesRole)
                if descr.get('attach') and forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'TFCPAttach', False)):
                    replace.addButton(QtGui.QPushButton(u'Обновить полис и прикрепление'), QtGui.QMessageBox.AcceptRole)
                replace.addButton(QtGui.QPushButton(u'Отмена'), QtGui.QMessageBox.RejectRole)
                res = replace.exec_()

                def replacePolicy():
                    if isKras:
                        self.edtLastName.setText(descr.lastName)
                        self.edtFirstName.setText(descr.firstName)
                        self.edtPatrName.setText(descr.patrName)
                        if descr.Snils:
                            self.edtSNILS.setText(descr.Snils)
                        self.cmbSex.setCurrentIndex(
                            1 if descr.sex.lower() == u'м' else 2 if descr.sex.lower() == u'ж' else 0)
                        self.edtBirthDate.setDate(descr.birthDate)
                        if descr.policyKindId:
                            self.cmbCompulsoryPolisKind.setValue(descr.policyKindId)
                        self.dispCode = forceString(descr.dCode)
                        self.dispBegDate = forceDateTime(descr.dDATN)
                        self.dispEndDate = forceDateTime(descr.dDATO)
                        self.dispCodeMO = forceInt(descr.dCODE_MO)
                    else:
                        self.attachList = descr.attach

                    self.edtCompulsoryPolisSerial.setText(descr.policySerial)
                    self.edtCompulsoryPolisNumber.setText(descr.policyNumber)
                    self.edtCompulsoryPolisNote.setText('')
                    if descr.smoId:
                        area = forceString(QtGui.qApp.db.translate('Organisation', 'id', descr.smoId, 'area'))
                        self.cmbCompulsoryInsuranceArea.setCode(area)
                        self.cmbCompulsoryPolisCompany.setValue(descr.smoId)
                    if descr.policyTypeId:
                        self.cmbCompulsoryPolisType.setValue(descr.policyTypeId)
                    self.syncPolicy(True)
                    row = self.modelPolicies.getCurrentCompulsoryPolicyRow(descr.policySerial, descr.policyNumber,
                                                                           descr.smoId, descr.begDate)
                    self.modelPolicies.setValue(row, 'begDate', toVariant(descr.begDate))
                    self.modelPolicies.setValue(row, 'endDate', toVariant(descr.endDate))
                    # self.modelPolicies.setValue(row, 'insurer_id', toVariant(descr.smoId))
                    if showDischarge:
                        self.modelPolicies.setValue(row, 'dischargeDate', QtCore.QVariant())
                    begDate = descr.begDate
                    if not descr.begDate:
                        begDate = QtCore.QDate()
                    endDate = descr.endDate
                    if not descr.endDate:
                        endDate = QtCore.QDate()
                    if showDischarge:
                        self.edtCompulsoryPolisDischargeDate.setDate(QtCore.QDate())
                    self.edtCompulsoryPolisBegDate.setDate(begDate)
                    self.edtCompulsoryPolisEndDate.setDate(endDate)
                    self.updatePolicyKind(self.edtCompulsoryPolisSerial, self.cmbCompulsoryPolisKind)

                def insertAttach():
                    tableAttach = QtGui.qApp.db.table('ClientAttach')
                    recOrgStruct = QtGui.qApp.db.getRecordEx('OrgStructure', '*', 'id = %s' % forceString(descr.attach))
                    if recOrgStruct:
                        recAttach = QtGui.qApp.db.getRecordEx('ClientAttach', 'id', 'client_id = %s AND deleted = 0 AND orgStructure_id = %s AND endDate IS NULL' % (
                        forceString(QtGui.qApp.currentClientId()), forceString(recOrgStruct.value('id'))))
                        if not recAttach:
                            newAttach = tableAttach.newRecord()
                            newAttach.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                            newAttach.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
                            newAttach.setValue('modifyDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                            newAttach.setValue('modifyPerson_id', toVariant(QtGui.qApp.userId))
                            newAttach.setValue('client_id', toVariant(QtGui.qApp.currentClientId()))
                            newAttach.setValue('attachType_id', toVariant(1))
                            newAttach.setValue('LPU_id', toVariant(forceInt(recOrgStruct.value('organisation_id'))))
                            newAttach.setValue('orgStructure_id', toVariant(forceInt(recOrgStruct.value('id'))))
                            newAttach.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
                            QtGui.qApp.db.insertRecord(tableAttach, newAttach)

                if len(replace.buttons()) == 3:
                    if res == 0:
                        replacePolicy()
                    elif res == 1:
                        replacePolicy()
                        insertAttach()
                else:
                    if res == 0:
                        replacePolicy()


            else:
                self.isSearchPolicy = False
                if descr and hasattr(descr, 'message'):
                    message = descr.message
                else:
                    message = u'Полис не найден'
                QtGui.QMessageBox.information(self,
                    u'Поиск полиса',
                    message,
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        except CSoapException as e:
            message = forceString(e)
            QtGui.QMessageBox.information(self,
                u'Поиск полиса',
                message,
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCompulsoryPolisSerial_textEdited(self, text):
        defaultKLADR = QtGui.qApp.defaultKLADR()
        if len(defaultKLADR) >= 2 and defaultKLADR[:2] != '61':
            self.cmbCompulsoryPolisCompany.setSerialFilter(text)
            self.updateCompulsoryPolicyType()
        self.updatePolicyKind(self.edtCompulsoryPolisSerial, self.cmbCompulsoryPolisKind)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCompulsoryPolisSerial_textChanged(self, text):
        self.updatePolicyKind(self.edtCompulsoryPolisSerial, self.cmbCompulsoryPolisKind)
        if text.replace(' ', '').toUpper() == u'ЕП':
            self.edtCompulsoryPolisEndDate.setDate(QtCore.QDate(2200, 01, 01))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCompulsoryPolisNumber_textEdited(self, text):
        if not self.cmbCompulsoryPolisType.value():
            self.cmbCompulsoryPolisType.setCurrentIndex(1)

    @QtCore.pyqtSlot(int)
    def on_cmbCompulsoryPolisCompany_currentIndexChanged(self, index):
        self.disconnect(self.cmbCompulsoryInsuranceArea, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbCompulsoryInsuranceArea_currentIndexChanged)
        self.updateCompulsoryPolicyType()
        self.updateCompulsoryInsuranceArea()
        self.updateCompulsoryPolicyType()
        self.connect(self.cmbCompulsoryInsuranceArea, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbCompulsoryInsuranceArea_currentIndexChanged)

    @QtCore.pyqtSlot(int)
    def on_cmbCompulsoryInsuranceArea_currentIndexChanged(self, index):
        self.updateCompulsoryPolicyCompanyArea()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbCompulsoryPolisKind_currentIndexChanged(self, text):
        enabled = True
        code = forceInt(self.cmbCompulsoryPolisKind.code())
        defaultKLADR = QtGui.qApp.defaultKLADR()
        if code >= 3:  # если полис единый
            self.edtCompulsoryPolisNumber.setInputMask('9' * 16)  # 16 обязательных цифр
        elif code == 2:  # если временный
            self.edtCompulsoryPolisNumber.setInputMask('9' * 9)  # 9 обязательных цифр
        elif code == 1:  # старого образца
            self.edtCompulsoryPolisNumber.setInputMask('')

        if defaultKLADR.startswith('78') or defaultKLADR.startswith('47'):  # если СПб
            if code == 2:
                self.edtCompulsoryPolisSerial.setText(u'ВС')
            if code == 3:
                self.edtCompulsoryPolisSerial.setText(u'ЕП')
        else:
            if code != 1:  # если не питер и не старый
                self.edtCompulsoryPolisSerial.setText('')
                enabled = False
        self.edtCompulsoryPolisSerial.setEnabled(enabled)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtVoluntaryPolisSerial_textEdited(self, text):
        self.cmbVoluntaryPolisCompany.setSerialFilter(text)
        self.updateVoluntaryPolicyType()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtVoluntaryPolisNumber_textEdited(self, text):
        if not self.cmbVoluntaryPolisType.value():
            self.cmbVoluntaryPolisType.setCurrentIndex(1)

    @QtCore.pyqtSlot(int)
    def on_cmbVoluntaryPolisCompany_currentIndexChanged(self, index):
        self.disconnect(self.cmbVoluntaryInsuranceArea, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbVoluntaryInsuranceArea_currentIndexChanged)
        self.updateVoluntaryPolicyType()
        self.updateVoluntaryInsuranceArea()
        self.updateVoluntaryPolicyType()
        self.connect(self.cmbVoluntaryInsuranceArea, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbVoluntaryInsuranceArea_currentIndexChanged)

    @QtCore.pyqtSlot(int)
    def on_cmbVoluntaryInsuranceArea_currentIndexChanged(self, index):
        self.updateVoluntaryPolicyCompanyArea()

    @QtCore.pyqtSlot()
    def on_modelPolicies_policyChanged(self):
        items = self.modelPolicies.items()
        for isCompulsory in (True, False):
            row = self.modelPolicies.getCurrentPolicyRowInt(isCompulsory)
            self.setPolicyRecord(items[row] if 0 <= row < len(items) else None, isCompulsory)

    @QtCore.pyqtSlot()
    def on_btnSocStatusUpdate_clicked(self):
        lastName = forceStringEx(self.edtLastName.text())
        firstName = forceStringEx(self.edtFirstName.text())
        patrName = forceStringEx(self.edtPatrName.text())
        SNILS = forceStringEx(self.edtSNILS.text()).replace('-', '').replace(' ', '')
        result, categories = getBenefitCategories(lastName, firstName, patrName, SNILS)
        requestOk, isFound = checkBenefitCategoriesResult(result)
        if result:
            msg = u'Ответ сервера: ' + result
        else:
            msg = u'Ответ сервера не получен'
        if requestOk:
            QtGui.QMessageBox.information(self, u'Обновление соц.статуса', msg, QtGui.QMessageBox.Close)
            if isFound:
                l = []
                db = QtGui.qApp.db
                for code, default in categories:
                    socStatusTypeId = forceRef(db.translate('rbSocStatusType', 'code', code, 'id'))
                    if not socStatusTypeId:
                        QtGui.QMessageBox.critical(self, u'Обновление соц.статуса', u'Получен неизвестный код льготы "%s"' % code, QtGui.QMessageBox.Close)
                        return
                    l.append((socStatusTypeId, default))
                self.updateSocStatuses(l)
        else:
            QtGui.QMessageBox.critical(self, u'Обновление соц.статуса', msg, QtGui.QMessageBox.Close)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelSocStatuses_currentChanged(self, current, previous):
        dirty = self.isDirty()
        row = current.row()
        if 0 <= row < len(self.modelSocStatuses.items()):
            docTypeId, serial, number, begDate, endDate, origin = self.modelSocStatuses.getDocInfo(row)
            self.frmSocStatusDocument.setEnabled(True)
            self.cmbSocStatusDocType.setEnabled(True)
            if not docTypeId:
                docTypeId, serial, number, begDate, endDate, origin = None, '', '', QtCore.QDate(), QtCore.QDate(), ''
                item = self.modelSocStatuses.items()[row]
                socStatusTypeId = forceRef(item.value('socStatusType_id'))
                if socStatusTypeId:
                    db = QtGui.qApp.db
                    tableRBSocStatusType = db.table('rbSocStatusType')
                    record = db.getRecordEx(tableRBSocStatusType, [tableRBSocStatusType['documentType_id']], [tableRBSocStatusType['id'].eq(socStatusTypeId)])
                    if record:
                        docTypeId = forceRef(record.value('documentType_id'))
                        self.edtSocStatusDocSerial.setFocus(QtCore.Qt.ShortcutFocusReason)
        else:
            docTypeId, serial, number, begDate, endDate, origin = None, '', '', QtCore.QDate(), QtCore.QDate(), ''
            self.cmbSocStatusDocType.setEnabled(False)
            self.frmSocStatusDocument.setEnabled(False)
        #FIXME: atronah: странная ерунда происходит. Если после открытия окна рег. карты сразу перейти на вкладку Соц.Статусы,
        # то все норм и сначала вызывается инициализация вкладки (из on_tabWidget_currentChanged)
        # с соответствующим setTable для всех тамошних ComboBox'ов
        # а вот если перед переходом на вкладку Соц.Статусы перевести фокус на какой-либо элемент вкладки "Паспортные данные"
        # то при переходе на вкд Соц.Статусы сначала реагирует этот слот (и пытается работать с неинициализированными ComboBox'ами
        # а уже потом вызывается инициализация вкладки. ><
        if self.isTabSocStatusAlreadyLoad:
            self.cmbSocStatusDocType.setValue(docTypeId)
            self.edtSocStatusDocSerial.setText(serial)
            self.edtSocStatusDocNumber.setText(number)
            self.edtSocStatusDocDate.setDate(begDate)
            self.edtSocStatusDocOrigin.setText(origin)

        groupedDataByClassId = dict()
        autoCloseDateDict = dict()
        for x in self.modelSocStatuses.items():
            classId = forceRef(x.value('socStatusClass_id'))
            if classId not in autoCloseDateDict:
                autoCloseDateDict[classId] = forceBool(QtGui.qApp.db.translate('rbSocStatusClass', 'id', classId, 'autoCloseDate'))

            if autoCloseDateDict[classId]:
                if classId in groupedDataByClassId:
                    groupedDataByClassId[classId].append(x)
                    groupedDataByClassId[classId].sort(key=lambda k: forceDate(k.value('begDate')))
                else:
                    groupedDataByClassId[classId] = [x]

        for x in groupedDataByClassId:
            if autoCloseDateDict[x]:
                for y in groupedDataByClassId[x][:-1]:
                    if forceDate(y.value('endDate')).isNull():
                        y.setValue('endDate', toVariant(QtCore.QDate.currentDate().addDays(-1)))

        self.setIsDirty(dirty)

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusDocType_currentIndexChanged(self, index):
        docTypeId = self.cmbSocStatusDocType.value()
        docTypeOk = bool(docTypeId)
        self.edtSocStatusDocSerial.setEnabled(docTypeOk)
        self.edtSocStatusDocSerial.setFocus(QtCore.Qt.ShortcutFocusReason)
        self.edtSocStatusDocNumber.setEnabled(docTypeOk)
        self.edtSocStatusDocDate.setEnabled(docTypeOk)
        self.edtSocStatusDocOrigin.setEnabled(docTypeOk)
        self.updateSocStatus('documentType_id', docTypeId)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtSocStatusDocSerial_textEdited(self, text):
        self.updateSocStatus('serial', text)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtSocStatusDocNumber_textEdited(self, text):
        self.updateSocStatus('number', text)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtSocStatusDocDate_dateChanged(self, date):
        self.updateSocStatus('date', date)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtSocStatusDocOrigin_textEdited(self, text):
        self.updateSocStatus('origin', text)

    @QtCore.pyqtSlot()
    def on_btnCopyPrevWork_clicked(self):
        if CClientEditDialog.prevWork:
            self.setWork(CClientEditDialog.prevWork)

    @QtCore.pyqtSlot(int)
    def on_cmbWorkOrganisation_currentIndexChanged(self, index):
        self.updateWorkOrganisationInfo()

    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.setIsDirty()
            self.cmbWorkOrganisation.setValue(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbWorkOKVED_currentIndexChanged(self, index):
        self.edtOKVEDName.setText(getOKVEDName(self.cmbWorkOKVED.text()))
        self.edtOKVEDName.setCursorPosition(0)

    @QtCore.pyqtSlot(int)
    def on_modelClientQuoting_quotaTypeSelected(self, quotaType_id):
        index = self.selectionModelClientQuoting.currentIndex()
        self.modelClientQuoting.setData(index, toVariant(quotaType_id), QtCore.Qt.EditRole)
        self.on_selectionModelClientQuoting_currentChanged(index, None)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelClientQuoting_currentChanged(self, current, previous):
        row = current.row()
        modelItems = self.modelClientQuoting.items()
        if (row < len(modelItems)) and (row != -1):
            self.__quotaRecord = modelItems[row]
            self.modelClientQuotingDiscussion.setIdList(
                    self.selectClientQuotingDiscussion(
                    forceInt(self.__quotaRecord.value('id'))))
            self.modelClientQuoting.loadItemsInfo(row)
            self.setQuotaWidgets(True)
        else:
            self.modelClientQuotingDiscussion.setIdList([])
            self.setEnabledQuotaWidgets(False)
            self.__quotaRecord = None
            self.modelClientQuoting.loadItemsInfo(None)
        self.setQuotingInfo()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtQuotaIdentifier_textEdited(self, text):
        self.__quotaRecord.setValue('identifier', QtCore.QVariant(text))

    @QtCore.pyqtSlot(int)
    def on_edtQuotaStage_valueChanged(self, val):
        self.__quotaRecord.setValue('stage', QtCore.QVariant(val))
        index = self.tblClientQuoting.currentIndex()
        if index.isValid():
            self.modelClientQuoting.emitRowChanged(index.row())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtQuotaTicket_textEdited(self, text):
        self.__quotaRecord.setValue('quotaTicket', QtCore.QVariant(text))

    @QtCore.pyqtSlot(int)
    def on_edtQuotaAmount_valueChanged(self, val):
        self.__quotaRecord.setValue('amount', QtCore.QVariant(val))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbQuotaMKB_textChanged(self, text):
        self.__quotaRecord.setValue('MKB', QtCore.QVariant(text))
        if self.setMKBTextInfo(text):
            index = self.tblClientQuoting.currentIndex()
            if index.isValid():
                self.modelClientQuoting.emitRowChanged(index.row())

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaRequest_currentIndexChanged(self, index):
        self.__quotaRecord.setValue('request', QtCore.QVariant(index))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtQuotaDirectionDate_dateChanged(self, date):
        self.__quotaRecord.setValue('directionDate', QtCore.QVariant(date))

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaLPU_currentIndexChanged(self, index):
        val = self.cmbQuotaLPU.value()
        self.__quotaRecord.setValue('org_id', QtCore.QVariant(val))

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtQuotaLPUFreeInput_textEdited(self, text):
        self.__quotaRecord.setValue('freeInput', QtCore.QVariant(text))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtQuotaDateRegistration_dateChanged(self, date):
        self.__quotaRecord.setValue('dateRegistration', toVariant(date))

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtQuotaDateEnd_dateChanged(self, date):
        self.__quotaRecord.setValue('dateEnd', toVariant(date))

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaOrgStructure_currentIndexChanged(self, index):
        val = self.cmbQuotaOrgStructure.value()
        self.__quotaRecord.setValue('orgStructure_id', QtCore.QVariant(val))

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaStatus_currentIndexChanged(self, index):
        self.__quotaRecord.setValue('status', QtCore.QVariant(index))
        tblIndex = self.tblClientQuoting.currentIndex()
        if tblIndex.isValid():
            self.modelClientQuoting.emitRowChanged(tblIndex.row())

    @QtCore.pyqtSlot()
    def on_edtQuotaStatment_textChanged(self):
        text = self.edtQuotaStatment.toPlainText()
        self.__quotaRecord.setValue('statment', QtCore.QVariant(text))

    @QtCore.pyqtSlot(int)
    def on_cmbQuotaKladr_currentIndexChanged(self, index):
        data = self.cmbQuotaKladr.itemData(index)
        self.__quotaRecord.setValue('regionCode', data)

    @QtCore.pyqtSlot()
    def on_btnRegInLC_clicked(self):
        from Exchange.PersonalCabinet.Exchange import PersonalCabinet
        if not forceBool(QtGui.qApp.preferences.appPrefs['PersCabService']) or not forceString(QtGui.qApp.preferences.appPrefs['HostPersCabService']):
            QtGui.QMessageBox.warning(self, u'Ошибка', u'''Не настроен сервис "Личный кабинет"''')
            return
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        tblContacts = db.table('ClientContact')
        tblContactType = db.table('rbContactType')
        tblClientInfo = tblClient.innerJoin(tblContacts, [tblContacts['client_id'].eq(tblClient['id']), tblContacts['deleted'].eq(0)])
        tblClientInfo = tblClientInfo.innerJoin(tblContactType, [tblContactType['id'].eq(tblContacts['contactType_id']), tblContactType['code'].eq('5')])
        recClient = db.getRecordEx(tblClientInfo, tblContacts['contact'], tblClient['id'].eq(QtGui.qApp.currentClientId()))
        if recClient and forceString(recClient.value('contact')):
            if PersonalCabinet(QtGui.qApp.currentClientId()).register():
                QtGui.QMessageBox.information(self, u'Успешно', u'Регистрация прошла успешно')
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Необходимо заполнить email и сохранить карту')

    @QtCore.pyqtSignature('')
    def on_btnUEK_clicked(self):
        if 'ibt.CardReader' not in sys.modules:
            return
        db = QtGui.qApp.db
        polisKind = forceRef(db.translate('rbPolicyKind', 'code', '5', 'id'))
        uekId = forceRef(db.translate('rbAccountingSystem', 'code', u'УЭК', 'id'))
        needDbPrepare = not polisKind or not uekId
        if needDbPrepare:
            message = u'База не настроена для работы с УЭК. Обратитесь в тех.поддержку.'
            QtGui.QMessageBox.warning(self, u'Внимание!', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return
        try:
            cardReader = CCardReader(CCardPinRequest(self).exec_)
            if CUekDataShow(self).exec_(cardReader) == QtGui.QDialog.Accepted:
                insurerId = db.getRecordEx('Organisation', 'id',
                                           'deleted = 0 AND isInsurer = 1 AND'
                                           ' OGRN = "%s" AND OKATO = "%s"' % (cardReader.insurerOGRN, cardReader.insurerOKATO))
                insurerId = 0 if not insurerId else forceInt(insurerId.value('id'))
                documentTypeId = 0 if not cardReader.documentType else forceInt(db.translate('rbDocumentType', 'code', cardReader.documentType, 'id'))
                self.edtLastName.setText(cardReader.lastName)
                self.edtFirstName.setText(cardReader.firstName)
                self.edtPatrName.setText(cardReader.patrName)
                self.edtBirthDate.setDate(QtCore.QDate.fromString(cardReader.birthDate, 'dd.MM.yyyy'))
                self.cmbSex.setCurrentIndex({u'М': 1, u'м': 1, u'Ж': 2, u'ж': 2}.get(cardReader.sex, 0))
                self.edtSNILS.setText(cardReader.SNILS)

                self.disconnect(self.cmbDocType, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbDocType_currentIndexChanged)
                self.cmbDocType.setValue(documentTypeId)
                self.connect(self.cmbDocType, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbDocType_currentIndexChanged)

                if self.isVisibleObject(self.edtDocSerialRight):
                    serialLeft, serialRight = splitDocSerial(cardReader.documentSerial, isCheckLastDash=True)
                    serialLeft, serialRight = self.analyzeSerialPart(documentTypeId, serialLeft, serialRight)
                    self.edtDocSerialRight.setText(serialRight)
                else:
                    serialLeft = forceString(cardReader.documentSerial)
                self.edtDocSerialLeft.setText(serialLeft)
                if self.useInputMask:
                    self.setInputMask(documentTypeId)

                self.edtDocNumber.setText(cardReader.documentNumber)
                self.edtWhoExtraditedDoc.setText(cardReader.documentOrigin)
                self.edtBirthPlace.setText(cardReader.birthPlace)
                self.edtDocDate.setDate(QtCore.QDate.fromString(cardReader.documentDate, 'dd.MM.yyyy'))
                self.edtCompulsoryPolisSerial.setText('')
                self.edtCompulsoryPolisNumber.setText(cardReader.policyNumber)
                self.edtCompulsoryPolisBegDate.setDate(QtCore.QDate.fromString(cardReader.policyBegDate, 'dd.MM.yyyy'))
                self.edtCompulsoryPolisEndDate.setDate(QtCore.QDate())
                if insurerId:
                    # Устанавливаем в фильтр КЛАДР-код территории СМО
                    self.updateCompulsoryPolicyCompanyArea([forceString(db.translate('Organisation', 'id', insurerId,
                                                                                     'area'))])
                self.cmbCompulsoryPolisCompany.setValue(insurerId)
                # Тип полиса - ОМС Территориальный
                self.cmbCompulsoryPolisType.setValue(forceInt(db.translate('rbPolicyType', 'code', '1', 'id')))
                # Вид полиса - Электронный полис(УЭК)
                self.cmbCompulsoryPolisKind.setValue(polisKind)
                # Вставляем внешний идентификатор УЭК
                for record in self.modelClientIdentification.items():
                    if uekId == forceInt(record.value('accountingSystem_id')):
                        break
                else:
                    record = self.modelClientIdentification.getEmptyRecord()
                    self.modelClientIdentification.items().append(record)
                record.setValue('client_id', QtCore.QVariant(QtGui.qApp.currentClientId()))
                record.setValue('identifier', QtCore.QVariant(cardReader.cardNumber))
                record.setValue('accountingSystem_id', QtCore.QVariant(uekId))
                record.setValue('checkDate', QtCore.QVariant(QtCore.QDate.currentDate()))
        except CCardReader.CheckLibVersionError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не совпадает версия библиотеки ИБТ УЭК', QtGui.QMessageBox.Close)
        except CCardReader.LoadLibrariesError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не удалось загрузить библиотеку ИБТ УЭК', QtGui.QMessageBox.Close)
        except CCardReader.InitPKCS11Error:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не удалось инициализировать PKCS11', QtGui.QMessageBox.Close)
        except CCardReader.ReaderNotFoundError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Считыватель карт УЭК не найден', QtGui.QMessageBox.Close)
        except CCardReader.CardNotFoundError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Карта УЭК не найдена', QtGui.QMessageBox.Close)
        except CCardReader.InitOperationError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не удалось инициализировать операцию', QtGui.QMessageBox.Close)
        except CCardReader.VerifyPinError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не удалось проверить PIN-код', QtGui.QMessageBox.Close)
        except CCardReader.ReadDataError:
            QtGui.QMessageBox.critical(self, u'УЭК', u'Не удалось прочитать данные', QtGui.QMessageBox.Close)


class CDiseaseCharacter(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, 'rbDiseaseCharacter', **params)

    def setEditorData(self, editor, value, record):
        db = QtGui.qApp.db
        MKB = forceString(record.value('MKB'))
        codeIdList = getAvailableCharacterIdByMKBForDiagnosis(MKB)
        table = db.table('rbDiseaseCharacter')
        editor.setTable(table.name(), not bool(codeIdList), filter=db.joinAnd([table['id'].inlist(codeIdList), table['code'].eq(table['replaceInDiagnosis'])]), order=self.order)
        editor.setValue(forceRef(value))


class CClientDiagnosisesModel(CInDocTableModel):
    def __init__(self, parent, diagnosisCode='2'):
        CInDocTableModel.__init__(self, 'Diagnosis', 'id', 'client_id', parent)
        self.addCol(CICDExInDocTableCol(u'МКБ', 'MKB', 15))
        self.defaultDate = [QtCore.QDate(2200, 1, 1), QtCore.QDate(2099, 12, 31)]
        if not QtGui.qApp.isPNDDiagnosisMode():  # atronah: вроде излишне, ибо эта модель показывается только при включенной опции isPNDDiagnosisMode
            self.addCol(CDiseaseCharacter(u'Характер', 'character_id', 7, showFields=CRBComboBox.showName, prefferedWidth=150)).setToolTip(u'Характер')
        self.addCol(CDateInDocTableCol(u'Дата установки', 'setDate', 15, canBeEmpty=False))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=False, defaultDate=self.defaultDate[0]))
        self.addCol(CPersonFindInDocTableCol(u'Врач', 'person_id', 40, 'vrbPersonWithSpeciality', order='name'))
        self.addHiddenCol('diagnosisType_id')
        self.diagnosisTypeIdList = QtGui.qApp.db.getIdList('rbDiagnosisType',
                                                           where="replaceInDiagnosis like '%s'" % diagnosisCode,
                                                           order='code ASC')
        self.setFilter(self.table['diagnosisType_id'].inlist(self.diagnosisTypeIdList))
        self._parent = parent

    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        record.setValue('diagnosisType_id', self.diagnosisTypeIdList[0])
        return record

    def updateCharacterByMKB(self, row, MKB, specifiedCharacterId):
        characterIdList = getAvailableCharacterIdByMKBForDiagnosis(MKB)
        item = self.items()[row]
        if specifiedCharacterId in characterIdList:
            characterId = specifiedCharacterId
        else:
            characterId = forceRef(item.value('character_id'))
            if (characterId in characterIdList) or (characterId is None and not characterIdList):
                return
            if characterIdList:
                characterId = characterIdList[0]
            else:
                characterId = None
        item.setValue('character_id', toVariant(characterId))
        self.emitCellChanged(row, item.indexOf('character_id'))

    def setDefaultDates(self, row, column):
        item = self.items()[row]
        if column != self.getColIndex('setDate'):
            item.setValue('setDate', QtCore.QDate.currentDate())
            self.emitCellChanged(row, self.getColIndex('setDate'))
        if column != self.getColIndex('endDate'):
            item.setValue('endDate', self.defaultDate[0])
            self.emitCellChanged(row, self.getColIndex('endDate'))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        isNewItem = row == len(self.items())

        if not variantEq(self.data(index, role), value):
            if column == self.getColIndex('MKB'):  # код МКБ
                newMKB = forceString(value)
                if not newMKB:
                    specifiedMKB = ''
                    specifiedCharacterId = None
                else:
                    date = forceDate(self.value(row, 'setDate'))
                    if not date:
                        date = QtCore.QDate.currentDate()
                    age = calcAgeTuple(self._parent.edtBirthDate.date(), date)
                    acceptable, specifiedMKB, _, specifiedCharacterId, _, _ = specifyDiagnosis(self._parent, newMKB, None, self._parent.itemId(), self._parent.cmbSex.currentIndex(), age, date)
                    if not acceptable:
                        return False
                value = toVariant(specifiedMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    self.updateCharacterByMKB(row, specifiedMKB, specifiedCharacterId)
                    if isNewItem:
                        self.setDefaultDates(row, column)
                return result
            elif column == self.getColIndex('setDate') and row > 0:
                prevItem = self.items()[row - 1]
                if forceDate(prevItem.value('endDate')) in self.defaultDate:
                    prevItem.setValue('endDate', value)
                    self.emitCellChanged(row - 1, self.getColIndex('endDate'))

            result = CInDocTableModel.setData(self, index, value, role)
            return result
        else:
            return True

    def flags(self, index):
        flags = CInDocTableModel.flags(self, index)
        row = index.row()
        column = index.column()
        if not self.isEditable() or (row == len(self.items()) and column != self.getColIndex('MKB')):
            flags &= (~ QtCore.Qt.ItemIsEditable)
        return flags


class CRBDependedInDocTableCol(CRBInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, dependField, **params):
        super(CRBDependedInDocTableCol, self).__init__(title, fieldName, width, tableName, **params)
        if not isinstance(dependField, (list, tuple)):
            dependField = [dependField, dependField]

        self.baseTableFieldName, self.assocTableFieldName = dependField

    def setEditorData(self, editor, value, record):
        baseTableId = forceRef(record.value(self.baseTableFieldName))
        cond = ('%s = %d' % (self.assocTableFieldName, baseTableId)) if baseTableId else '%s is NULL' % self.assocTableFieldName
        editor.setFilter(cond)
        #       editor.setShowFields(self.showFields)
        editor.setValue(forceInt(value))

    def createEditor(self, parent):
        editor = CRBDependedComboBox(parent)
        editor.setRTF(self._isRTF)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order=self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor


class CRBDependedPopupView(CRBPopupView):
    def __init__(self, parent):
        CRBPopupView.__init__(self, parent)
        self.stringSearch = ''

    def keyboardSearch(self, search):
        rowIndex, search = self.model().searchCodeEx(search)
        if rowIndex >= 0:
            index = self.model().index(rowIndex, 1)
            self.setCurrentIndex(index)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            event.ignore()
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            event.ignore()
        if key == QtCore.Qt.Key_Delete:
            self.stringSearch = ''
        elif key == QtCore.Qt.Key_Backspace:
            self.stringSearch = self.stringSearch[:-1]
            self.keyboardSearch(self.stringSearch)
        elif key == QtCore.Qt.Key_Space:
            self.stringSearch += ' '
            self.keyboardSearch(self.stringSearch)
        elif not event.text().isEmpty():
            char = event.text().at(0)
            if char.isPrint():
                self.stringSearch = self.stringSearch + unicode(QtCore.QString(char))
                self.keyboardSearch(self.stringSearch)
            else:
                QtGui.QComboBox.keyPressEvent(self, event)
        else:
            QtGui.QComboBox.keyPressEvent(self, event)


class CRBDependedComboBox(CRBComboBox):
    def __init__(self, parent):
        CRBComboBox.__init__(self, parent)
        self.popupView = CRBDependedPopupView(self)
        self.setView(self.popupView)
        self.popupView.hideColumn(2)


class CSocStatusesModel(CInDocTableModel):
    documentFields = 'documentType_id,serial,number,date,origin'

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientSocStatus', 'id', 'client_id', parent)
        self.addCol(CRBDependedInDocTableCol(u'Тип',
                                             'socStatusType_id',
                                             50, 'vrbSocStatusType',
                                             dependField=('socStatusClass_id', 'class_id'),
                                             showFields=CRBComboBox.showNameAndCode))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'begDate', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Примечание', 'notes', 30))
        self.addHiddenCol('document_id')
        self.addHiddenCol('socStatusClass_id')

        self.setClassFilter(None)

    def setClassFilter(self, filterCond):
        if not filterCond:
            filterCond = '1'
        filterCond = QtGui.qApp.db.joinAnd(['group_id is NULL',
                                            filterCond])

        self._availableClassIdList = ['%s' % itemId for itemId in QtGui.qApp.db.getIdList('rbSocStatusClass', where=filterCond)]
        # Если для выбора доступен только один класс, то убрать этот столбец
        if len(self._availableClassIdList) == 1:
            self.removeCol(self.getColIndex('socStatusClass_id'))
        # Если для выбора доступно несколько классов (или не одного)
        else:
            # и при этом нет поля "класс", добавить его
            classCol = self.getCol('socStatusClass_id')
            if classCol is None:
                classCol = CRBInDocTableCol(u'Класс', 'socStatusClass_id', 50, 'rbSocStatusClass', showFields=CRBComboBox.showNameAndCode)
                classCol.setSortable()
                self.insertCol(self.getColIndex('socStatusType_id'), classCol)
            classCol.filter = filterCond

        self.setFilter(('socStatusClass_id IN (%s)' % ', '.join(self._availableClassIdList)) if self._availableClassIdList else '0')

    def availableClassIdList(self):
        return self._availableClassIdList

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        if len(self._availableClassIdList) == 1:
            classFieldName = 'socStatusClass_id'
            if not result.contains(classFieldName):
                result.append(QtSql.QSqlField(classFieldName, QtCore.QVariant.Int))
            result.setValue(classFieldName, QtCore.QVariant(self._availableClassIdList[0]))
        self._addExCols(result)
        return result

    def loadItems(self, itemId):
        CInDocTableModel.loadItems(self, itemId)
        db = QtGui.qApp.db
        tblClass = db.table('rbSocStatusClass')
        tblAssoc = db.table('rbSocStatusClassTypeAssoc')
        tbl = tblClass.leftJoin(tblAssoc, [tblAssoc['class_id'].eq(tblClass['id']), tblAssoc['isDefault'].eq(1)])
        cond = [tblClass['tightControl'].eq(1),
                tblClass['id'].inlist(self._availableClassIdList)]
        ssList = db.getRecordList(tbl, [tblClass['id'], tblAssoc['type_id']], where=cond)
        ssDict = {}
        for record in ssList:
            ssDict[forceInt(record.value('id'))] = forceRef(record.value('type_id'))
        for item in self.items():
            if forceRef(item.value('socStatusClass_id')) in ssDict.keys():
                del ssDict[forceRef(item.value('socStatusClass_id'))]
            self._addExCols(item)
            self._loadDocInfo(item)
        for key in ssDict.keys():
            record = self.getEmptyRecord()
            record.setValue('socStatusClass_id', toVariant(key))
            record.setValue('socStatusType_id', toVariant(ssDict[key]))
            self.addRecord(record)
        self.setDirty(False)

    def saveItems(self, clientId):
        documentIdList = []
        for item in self.items():
            documentId = self._saveDocInfo(item, clientId)
            if documentId:
                documentIdList.append(documentId)
        items = self.items()
        savedItems = []
        for record in items:
            savedItems.append(QtSql.QSqlRecord(record))
            for n in self.documentFields.split(','):
                record.remove(record.indexOf(n))
        CInDocTableModel.saveItems(self, clientId)
        for record, savedRecord in zip(items, savedItems):
            for n in self.documentFields.split(','):
                record.append(savedRecord.field(n))

    def indexOfStatus(self, socStatusTypeId):
        for i, item in enumerate(self.items()):
            if forceRef(item.value('socStatusType_id')) == socStatusTypeId:
                return i
        return -1

    def establishStatus(self, socStatusTypeId):
        i = self.indexOfStatus(socStatusTypeId)
        if i >= 0:
            item = self.items()[i]
            item.setValue('endDate', toVariant(None))
        else:
            item = self.getEmptyRecord()
            item.setValue('socStatusType_id', toVariant(socStatusTypeId))
            item.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
            item.setValue('endDate', toVariant(None))
            self.items().append(item)

    def declineUnlisted(self, socStatusTypeIdList):
        yesterday = QtCore.QDate.currentDate().addDays(-1)
        for item in self.items():
            if forceRef(item.value('socStatusType_id')) not in socStatusTypeIdList:
                endDate = forceDate(item.value('endDate'))
                if endDate.isNull() or yesterday < endDate:
                    item.setValue('endDate', toVariant(yesterday))

# todo: clean unused docs
    def getDocInfo(self, row):
        record = self.items()[row]
        return [forceRef(record.value('documentType_id')),
                forceString(record.value('serial')),
                forceString(record.value('number')),
                forceDate(record.value('date')),
                forceDate(record.value('endDate')),
                forceString(record.value('origin'))
                ]

    # odo: endDate
    def _addExCols(self, record):
        record.append(QtSql.QSqlField('documentType_id', QtCore.QVariant.Int))
        record.append(QtSql.QSqlField('serial', QtCore.QVariant.String))
        record.append(QtSql.QSqlField('number', QtCore.QVariant.String))
        record.append(QtSql.QSqlField('date', QtCore.QVariant.Date))
        record.append(QtSql.QSqlField('origin', QtCore.QVariant.String))

    def _loadDocInfo(self, record):
        db = QtGui.qApp.db
        documentId = forceRef(record.value('document_id'))
        if documentId:
            documentRecord = db.getRecord('ClientDocument', self.documentFields, documentId)
            if documentRecord:
                for n in self.documentFields.split(','):
                    record.setValue(n, documentRecord.value(n))

    def _saveDocInfo(self, record, clientId):
        documentId = None
        if record and forceRef(record.value('documentType_id')):
            db = QtGui.qApp.db
            table = db.table('ClientDocument')
            documentId = forceRef(record.value('document_id'))
            if documentId:
                documentRecord = db.getRecord(table, '*', documentId)
            else:
                documentRecord = table.newRecord()
            for n in self.documentFields.split(','):
                documentRecord.setValue(n, record.value(n))
            documentRecord.setValue('client_id', toVariant(clientId))
            documentId = db.insertOrUpdate(table, documentRecord)
            record.setValue('document_id', toVariant(documentId))
        return documentId


class CPolyclinicInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)
        self.__model = None

    def initModel(self):
        self.__model = CDbModel(None)
        self.__model.setNameField(CPolyclinicComboBox.nameField)
        self.__model.setAddNone(True)
        self.__model.setFilter(CPolyclinicComboBox._filter)
        self.__model.setTable('Organisation')

    def toString(self, val, record):
        if not self.__model:
            self.initModel()
        text = self.__model.getNameById(forceRef(val))
        return toVariant(text)

    def createEditor(self, parent):
        if not self.__model:
            self.initModel()
        editor = CDbComboBox(parent)
        editor.setModel(self.__model)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


# FIXME: modeldatacache - отсутствует.
class COrgStructureInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName='OrgStructure', **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName  = tableName
        self.filter     = params.get('filter', '')
        self.prefferedWidth = params.get('prefferedWidth', None)

    def toString(self, val, record):
        from Orgs.Utils import getOrgStructureName
        return toVariant(getOrgStructureName(val))

    def toStatusTip(self, val, record):
        from Orgs.Utils import getOrgStructureFullName
        return toVariant(getOrgStructureFullName(val))

    def createEditor(self, parent):
        from Orgs.OrgStructComboBoxes import COrgStructureComboBox
        editor = COrgStructureComboBox(parent)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceInt(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


class CClientRelationInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName = tableName
        self.filter = params.get('filter', '')
        self.prefferedWidth = params.get('prefferedWidth', None)
        self.clientIdComboBox = QtGui.qApp.currentClientId()
        self.clientId = None
        self.regAddressInfo = None
        self.logAddressInfo = None

    def toString(self, val, record):
        if forceInt(val) > 0:
            return toVariant(clientIdToText(val))
        else:
            return toVariant(record.value('freeInput'))

    def createEditor(self, parent):
        editor = CClientRelationComboBox(parent, self.clientId, self.regAddressInfo, self.logAddressInfo)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setRecord(record)
        editor.setValue(value)

    def getEditorData(self, editor):
        return toVariant(editor.value())

    def setClientId(self, clientId):
        self.clientId = clientId

    def setRegAddressInfo(self, regAddressInfo):
        self.regAddressInfo = regAddressInfo

    def setLogAddressInfo(self, logAddressInfo):
        self.logAddressInfo = logAddressInfo


class CPaymentSchemeModel(CInDocTableModel):
    class CSelectPaymentSchemeDialog(CDialogBase, Ui_SelectPaymentSchemeDialog):
        def __init__(self, parent):
            CDialogBase.__init__(self, parent)
            self.setupUi(self)
            self.cmbPaymentScheme.setEnrollment(True)

        def getPaymentSchemeId(self):
            return self.cmbPaymentScheme.value()

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Client_PaymentScheme', 'id', 'client_id', parent)
        self.addCol(CDateInDocTableCol(u'Отображается с', 'begDate', 30))
        self.addCol(CDateInDocTableCol(u'Отображается до', 'endDate', 30))
        self.addCol(CDesignationInDocTableCol(u'Тип схемы оплаты', 'paymentScheme_id', ('PaymentScheme', u'if(type = 0, \'Клинические исследования\', \'Безлимитный расчет\')'), 40).setReadOnly(True))
        self.addCol(CDesignationInDocTableCol(u'Номер схемы оплаты', 'paymentScheme_id', ('PaymentScheme', 'number'), 40).setReadOnly(True))
        self.addCol(CDateInDocTableCol(u'Нач.дата', 'begDate', 20).setReadOnly(True))
        self.addCol(CDateInDocTableCol(u'Кон.дата', 'endDate', 20).setReadOnly(True))
        self._enableAppendLine = False
        self.parentWidget = parent

    def loadItems(self, masterId):
        if masterId:
            CInDocTableModel.loadItems(self, masterId)

    @QtCore.pyqtSlot()
    def addNewContract(self):
        dlg = self.CSelectPaymentSchemeDialog(self.parentWidget)
        if dlg.exec_():
            paymentSchemeId = dlg.getPaymentSchemeId()
            if paymentSchemeId:
                record = QtGui.qApp.db.record(self.table.name())
                record.setValue('paymentScheme_id', paymentSchemeId)
                self.addRecord(record)

    def doAfterSaving(self, condition):
        db = QtGui.qApp.db
        table = self._table
        if self._filter:
            condition.append(self._filter)

        # Очистка связи с пациентом у всех договоров, которые были удалены из модели
        # (которые ссылаются текущего пациента и чьи id отсутствуют в текущей моделе)
        db.updateRecords(table,
                         [table['client_id'].sign('=', None),
                          table['begDate'].sign('=', None),
                          table['endDate'].sign('=', None)],
                         where=condition)


class CDeAttachQueryNumberCol(CInDocTableCol):
    def createEditor(self, parent):
        editor = QtGui.QLineEdit(parent)
        validator = QtGui.QIntValidator(0, 999999999, editor)
        editor.setValidator(validator)
        return editor


class CAttachSentToTFOMSCol(CBoolInDocTableCol):
    def toString(self, val, record):
        return toVariant(u'Синхронизировано' if forceBool(val) else u'Не синхронизировано')


class CAttachesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientAttach', 'id', 'client_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип', 'attachType_id', 30, 'rbAttachType'))
        self.addCol(CPolyclinicExtendedInDocTableCol(u'ЛПУ', 'LPU_id', 15))
        self.addCol(COrgStructureInDocTableCol(u'Подразделение', 'orgStructure_id', 15))
        self.addCol(CDateInDocTableCol(u'Дата прикрепления', 'begDate', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Дата открепления', 'endDate', 15, canBeEmpty=True))

        self.hasDeattachQuery = QtGui.qApp.isKrasnodarRegion()
        if self.hasDeattachQuery:
            self.deattachQueryNumberCol = CDeAttachQueryNumberCol(u'№ уведомления в другую МО', 'id', 15)
            self.queryNumberColumn = len(self.cols())
            self.addCol(self.deattachQueryNumberCol)

            self.deattachQueryDateCol = CDateInDocTableCol(u'Дата уведомления в другую МО', 'id', 15, canBeEmpty=True)
            self.queryDateColumn = len(self.cols())
            self.addCol(self.deattachQueryDateCol)

        self.addCol(CDetachmentReasonTableCol(u'Причина открепления', 'detachment_id', 15, 'rbDetachmentReason'))
        self.addCol(CAttachSentToTFOMSCol(u'Статус синхронизации', 'sentToTFOMS', 10, readOnly=True, isVisible=QtGui.qApp.isKrasnodarRegion()))
        self.addCol(CInDocTableCol(u'Описание ошибки', 'errorCode', 15, readOnly=True))

        self._attachTypeCache = {}
        self.clientEditDialog = parent
        self._deattachQueryItems = []

    def addAttach(self, attach, sentToTFOMS=CAttachSentToTFOMS.Synced):
        record = self.getEmptyRecord()
        orgId, orgStructureId = CBookkeeperCode.getOrgStructure(attach.orgCode, attach.sectionCode)
        record.setValue('LPU_id', toVariant(orgId))
        record.setValue('orgStructure_id', toVariant(orgStructureId))
        record.setValue('begDate', toVariant(attach.begDate))
        record.setValue('attachType_id', QtGui.qApp.db.translate('rbAttachType', 'code', attach.attachType, 'id'))
        record.setValue('sentToTFOMS', toVariant(sentToTFOMS))

        for item in self.items():
            if all(item.value(field) == record.value(field) for field in ('LPU_id', 'orgStructure_id', 'begDate', 'attachType_id')):
                item.setValue('sentToTFOMS', toVariant(sentToTFOMS))
                item.setValue('errorCode', toVariant(''))
                return

        self.addRecord(record)

    def addRecord(self, record):
        self._deattachQueryItems.append(DeAttachQuery())
        CInDocTableModel.addRecord(self, record)

    def getDeAttachQuery(self, row):
        return self._deattachQueryItems[row] if 0 <= row < len(self._deattachQueryItems) else DeAttachQuery()

    def getAttachTypeIsOutcome(self, attachTypeId):
        result = self._attachTypeCache.get(attachTypeId, None)
        if result is None:
            result = forceBool(QtGui.qApp.db.translate('rbAttachType', 'id', attachTypeId, 'outcome'))
            self._attachTypeCache[attachTypeId] = result
        return result

    def flags(self, index):
        flags = CInDocTableModel.flags(self, index)
        if not (index and index.isValid()):
            return flags

        row, column = index.row(), index.column()
        if column == self.getColIndex('detachment_id'):
            if row not in xrange(len(self._items)):
                return flags
            item = self._items[row]
            if not item.value('endDate').toDate().isValid() and not self.getAttachTypeIsOutcome(item.value('attachType_id')):
                flags &= ~QtCore.Qt.ItemIsEnabled

        elif self.hasDeattachQuery and column in (self.queryDateColumn, self.queryNumberColumn):
            if 0 <= row < len(self._deattachQueryItems):
                deattachQuery = self._deattachQueryItems[row]
                if deattachQuery.id is not None:
                    flags &= (~QtCore.Qt.ItemIsEditable)
            elif row == len(self._deattachQueryItems):
                flags &= (~QtCore.Qt.ItemIsEditable)

        return flags

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row, column = index.row(), index.column()
        if index.isValid() and self.hasDeattachQuery \
                and column in (self.queryNumberColumn, self.queryDateColumn) and role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            if 0 <= row < len(self._deattachQueryItems):
                deattachQuery = self._deattachQueryItems[row]
                return toVariant(deattachQuery.number if column == self.queryNumberColumn else deattachQuery.date)
            return QtCore.QVariant()

        return CInDocTableModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row, column = index.row(), index.column()
        if index and index.isValid() and column == self.getColIndex('endDate'):
            if forceString(index.data()) != forceString(value):
                index.model().items()[row].setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.NotSynced))
            if not value.toDate().isValid() and row in xrange(len(self._items)):
                self.setData(self.index(row, self.getColIndex('detachment_id')), QtCore.QVariant(), role)

        if row == len(self._deattachQueryItems):
            self._deattachQueryItems.append(DeAttachQuery())

        if self.hasDeattachQuery and column in (self.queryNumberColumn, self.queryDateColumn):
            deattachQuery = self._deattachQueryItems[row]
            if column == self.queryDateColumn:
                date = forceDate(value)
                deattachQuery.date = date if not date.isNull() else None
            elif column == self.queryNumberColumn:
                deattachQuery.number = forceRef(value)
        else:
            ret = CInDocTableModel.setData(self, index, value, role)
            if forceString(index.data()) != forceString(value):
                index.model().items()[row].setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.NotSynced))

            return ret

        return True

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        result = CInDocTableModel.removeRows(self, row, count, parentIndex)
        if result and self.hasDeattachQuery:
            del self._deattachQueryItems[row:row + count]
        return result

    def getEmptyRecord(self):
        orgId = QtGui.qApp.currentOrgId()
        address = self.clientEditDialog.getAddress(1)
        houseId = findHouseId(address)
        orgStructureIdList = findOrgStructuresByHouseAndFlat(houseId, address['flat'], orgId, QtGui.qApp.currentOrgStructureId()) if houseId else None
        orgStructureId = orgStructureIdList[0] if orgStructureIdList else None
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('LPU_id', toVariant(orgId))
        result.setValue('orgStructure_id', toVariant(orgStructureId))
        result.setValue('begDate', toVariant(QtCore.QDate.currentDate()))
        return result

    def getNotSyncedAttaches(self):
        toSend = lambda rec: (forceInt(rec.value('sentToTFOMS')) == CAttachSentToTFOMS.NotSynced) \
                             and all(not rec.value(field).isNull() for field in ('orgStructure_id', 'attachType_id', 'begDate'))
        return filter(lambda (record, deattachQuery): toSend(record), itertools.izip(self.items(), self._deattachQueryItems))

    @staticmethod
    def getDeAttachQueryLog(attachId):
        db = QtGui.qApp.db
        table = db.table(getDeAttachQueryLogTable())
        rec = db.getRecordEx(table, [table['id'], table['date'], table['number']], table['attach_id'].eq(attachId), table['id'].desc())
        if rec is not None:
            return DeAttachQuery(number=forceInt(rec.value('number')),
                                 date=forceDate(rec.value('date')),
                                 id=forceRef(rec.value('id')))
        return DeAttachQuery()

    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        if self._items is not None and self.hasDeattachQuery:
            for idx, record in enumerate(self._items):
                id = forceRef(record.value('id'))
                self._deattachQueryItems.append(self.getDeAttachQueryLog(id))

    def saveItems(self, masterId):
        if self._items is not None:
            db = QtGui.qApp.db
            table = self._table
            masterId = toVariant(masterId)
            masterIdFieldName = self._masterIdFieldName
            idFieldName = self._idFieldName
            idList = []
            for idx, record in enumerate(self._items):
                record.setValue(masterIdFieldName, masterId)
                if self._idxFieldName:
                    record.setValue(self._idxFieldName, toVariant(idx))
                if self._extColsPresent:
                    outRecord = self.removeExtCols(record)
                else:
                    outRecord = record
                db.transaction()
                try:
                    isNewRecord = not forceBool(record.value('id'))
                    isDead = forceBool(forceInt(record.value('attachType_id')) == CAttachType.Dead)
                    if isNewRecord or isDead:
                        begDate = forceDate(record.value('begDate'))
                        group = forceInt(db.translate('rbAttachType', 'id', forceRef(record.value('attachType_id')), 'grp'))
                        isOutcome = forceBool(db.translate('rbAttachType', 'id', forceRef(record.value('attachType_id')), 'outcome'))
                        if isOutcome or group or isDead:
                            queryTable = self._table
                            cond = [self._table['client_id'].eq(masterId),
                                    self._table['endDate'].isNull(),
                                    self._table['begDate'].dateLe(begDate),
                                    self._table['deleted'].eq(0)]
                            if not isOutcome:
                                tableRBAttachType = db.table('rbAttachType')
                                queryTable = queryTable.join(tableRBAttachType, tableRBAttachType['id'].eq(self._table['attachType_id']))
                                cond.append(tableRBAttachType['grp'].eq(group), )
                            prevRecordList = db.getRecordList(queryTable, 'ClientAttach.id, ClientAttach.endDate', cond)
                            for prevRecord in prevRecordList:
                                # Открепляем предыдущие прикрепления с датой открепления, равной дате нового прикрепления
                                prevRecord.setValue('endDate', toVariant(begDate))
                                prevRecordId = forceRef(prevRecord.value('id'))
                                db.updateRecords(self._table, prevRecord, self._table['id'].eq(prevRecordId))

                    itemId = db.insertOrUpdate(table, outRecord)
                    record.setValue(idFieldName, toVariant(itemId))
                    idList.append(itemId)
                    db.commit()
                except:
                    QtGui.qApp.logCurrentException()
                    db.rollback()

            cond = [
                table[masterIdFieldName].eq(masterId),
                table[idFieldName].notInlist(idList)
            ]
            if self._filter:
                cond.append(self._filter)
            if table.hasField('deleted'):
                db.markRecordsDeleted(table, cond)
            else:
                db.deleteRecord(table, cond)


class CDirectRelationsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientRelation', 'id', 'client_id', parent)
        self.addCol(CRBInDocTableCol(u'Прямая связь', 'relativeType_id', 30, 'vrbDirectClientRelation'))
        self.addCol(CClientRelationInDocTableCol(u'Связан с пациентом', 'relative_id', 30, 'ClientRelation'))
        self.addHiddenCol('freeInput')
        self.clientEditDialog = parent
        self.clientId = None
        self._extraData = None
        self._extraField = None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self._items):
                if value.isNull():
                    return False
                self.addRecord(self.getEmptyRecord())
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), value)
            if not forceRef(value) and forceString(self._extraData) and forceString(col.fieldName()) == u'relative_id':
                record.setValue(col.fieldName(), toVariant(None))
                record.setValue(self._extraField, self._extraData)
            self.emitCellChanged(row, column)
            return True
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            state = value.toInt()[0]
            if row == len(self._items):
                if state == QtCore.Qt.Unchecked:
                    return False
                self.addRecord(self.getEmptyRecord())
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), QtCore.QVariant(0 if state == QtCore.Qt.Unchecked else 1))
            self.emitCellChanged(row, column)
            return True
        return False

    def setClientId(self, clientId):
        self.clientId = clientId
        self.cols()[1].setClientId(clientId)

    def setRegAddressInfo(self, regAddressInfo):
        self.cols()[1].setRegAddressInfo(regAddressInfo)

    def setLogAddressInfo(self, logAddressInfo):
        self.cols()[1].setLogAddressInfo(logAddressInfo)

    def setDirectRelationFilter(self, sex):
        if sex:
            self.cols()[0].filter = 'id IN (SELECT rbRelationType.id FROM rbRelationType WHERE rbRelationType.leftSex = %d OR rbRelationType.leftSex = 0)' % (sex)
        else:
            self.cols()[0].filter = ''

    def setExtraData(self, field, data):
        self._extraField = field
        self._extraData = data

    def eventFilter(self, watched, event):
        return True


class CBackwardRelationsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientRelation', 'id', 'relative_id', parent)
        self.addCol(CRBInDocTableCol(u'Обратная связь', 'relativeType_id', 30, 'vrbBackwardClientRelation'))
        self.addCol(CClientRelationInDocTableCol(u'Связан с пациентом', 'client_id', 30, 'ClientRelation'))
        self.addHiddenCol('freeInput')
        self.clientEditDialog = parent
        self.clientId = None
        self._extraData = None
        self._extraField = None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self._items):
                if value.isNull():
                    return False
                self.addRecord(self.getEmptyRecord())
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), value)
            if not forceRef(value) and forceString(self._extraData) and forceString(col.fieldName()) == u'client_id':
                record.setValue(col.fieldName(), toVariant(None))
                record.setValue(self._extraField, self._extraData)
            self.emitCellChanged(row, column)
            return True
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            state = value.toInt()[0]
            if row == len(self._items):
                if state == QtCore.Qt.Unchecked:
                    return False
                self.addRecord(self.getEmptyRecord())
            record = self._items[row]
            col = self._cols[column]
            record.setValue(col.fieldName(), QtCore.QVariant(0 if state == QtCore.Qt.Unchecked else 1))
            self.emitCellChanged(row, column)
            return True
        return False

    def setClientId(self, clientId):
        self.clientId = clientId
        self.cols()[1].setClientId(clientId)

    def setRegAddressInfo(self, regAddressInfo):
        self.cols()[1].setRegAddressInfo(regAddressInfo)

    def setLogAddressInfo(self, logAddressInfo):
        self.cols()[1].setLogAddressInfo(logAddressInfo)

    def setBackwardRelationFilter(self, sex):
        if sex:
            self.cols()[0].filter = 'id IN (SELECT rbRelationType.id FROM rbRelationType WHERE rbRelationType.rightSex = %d OR rbRelationType.rightSex = 0)' % (sex)
        else:
            self.cols()[0].filter = ''

    def setExtraData(self, field, data):
        self._extraField = field
        self._extraData = data


def valIsMatched(old, new):
    return old == new or not old or not new


class CIdentificationDocsModel(CInDocTableModel):
    __pyqtSignals__ = ('documentChanged(int)',
                       )

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientDocument', 'id', 'client_id', parent)
        documentTypeIdList = getDocumentTypeIdListByGroupList(['1'])
        self.setFilter(self.table['documentType_id'].inlist(documentTypeIdList))
        tableDocumentType = QtGui.qApp.db.table('rbDocumentType')
        self.addCol(CRBInDocTableCol(u'Тип', 'documentType_id', 30, 'rbDocumentType', filter=tableDocumentType['id'].inlist(documentTypeIdList)))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 8))
        self.addCol(CInDocTableCol(u'Номер', 'number', 16))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'date', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Выдан', 'origin', 30))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole:
            items = self.items()
            row = index.row()
            if row == len(items) - 1:
                self.emit(QtCore.SIGNAL('documentChanged(int)'), row)

    def getCurrentDocRow(self, docTypeId, serial, number):
        items = self.items()
        if items:
            row = len(items) - 1
            item = items[row]
            item_docTypeId = forceRef(item.value('documentType_id'))
            item_serial = delWasteSymbols(forceStringEx(item.value('serial')))
            item_number = delWasteSymbols(forceStringEx(item.value('number')))
            serial = delWasteSymbols(serial)
            number = delWasteSymbols(number)
            if (forceRef(item.value('id')) is None or
                    (valIsMatched(item_docTypeId, docTypeId)
                     and valIsMatched(item_serial, serial)
                     and valIsMatched(item_number, number)
                     )
                ):
                return row
        row = len(items)
        self.insertRecord(row, self.getEmptyRecord())
        return row


class CEventsCountCol(CInDocTableCol):
    u"""
        Количество обращений, к которым привязан полис
    """

    def __init__(self, title, fieldName, width, **params):
        super(CEventsCountCol, self).__init__(title, fieldName, width, **params)
        super(CEventsCountCol, self).setReadOnly(True)

    def setReadOnly(self, readOnly):
        pass

    def toString(self, val, record):
        policyId = val.toInt()[0]

        db = QtGui.qApp.db
        Event = db.table('Event')

        cnt = db.getCount(Event, countCol=Event['id'], where=[Event['deleted'].eq(0),
                                                              Event['clientPolicy_id'].eq(policyId)])
        return toVariant(cnt)


class CPoliciesModel(CInDocTableModel):
    __pyqtSignals__ = ('policyChanged()',
                       )

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientPolicy', 'id', 'client_id', parent)
        self.policyTypeColumn = CRBInDocTableCol(u'Тип', 'policyType_id', 30, 'rbPolicyType')
        self.policyKindColumn = CRBInDocTableCol(u'Тип', 'policyKind_id', 30, 'rbPolicyKind')

        franchisePercent = CInDocTableCol(u'Процент франшизы', 'franchisePercent', 10)
        self.addHiddenCol(franchisePercent.fieldName())

        self.addCol(self.policyTypeColumn)
        self.addCol(self.policyKindColumn)
        self.addCol(CInDocTableCol(u'Серия', 'serial', 30))
        self.addCol(CInDocTableCol(u'Номер', 'number', 30))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'begDate', 15, canBeEmpty=True, sortable=True))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=True, sortable=True))
        # if QtGui.qApp.showPolicyDischargeDate():
        #     self.addCol(CDateInDocTableCol(u'Дата погашения', 'dischargeDate', 15, canBeEmpty=True))
        self.addCol(CInsurerInDocTableCol(u'СМО', 'insurer_id', 50))
        self.addCol(CInDocTableCol(u'Наименование', 'name', 50))
        insuranceAreaCol = CKLADRInDocTableCol(u'Территория страхования', 'insuranceArea', 50)
        if QtGui.qApp.isShowPolicyInsuranceArea():
            self.addCol(insuranceAreaCol)
        else:
            self.addHiddenCol(insuranceAreaCol.fieldName())
        self.addCol(CInDocTableCol(u'Примечание', 'note', 50))
        self.addCol(CIntInDocTableCol(u'Искать', 'isSearchPolicy', 0))
        self.addCol(CEventsCountCol(u'Привязано обращений', 'id', 4))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole:
            self.emit(QtCore.SIGNAL('policyChanged()'))

    def getCurrentPolicyRowInt(self, isCompulsory, serial='', number='', smo_id='', start_date=''):
        items = self.items()
        for row in reversed(xrange(len(items))):
            item = items[row]
            policyTypeId = forceRef(item.value('policyType_id'))
            if (policyTypeId is None and isCompulsory) or self.policyTypeIsCompulsory(policyTypeId, isCompulsory):
                if forceRef(item.value('id')) is None or (
                                    valIsMatched(forceStringEx(item.value('serial')), serial)
                                and valIsMatched(forceStringEx(item.value('number')), number)
                            and (not smo_id or valIsMatched(forceRef(item.value('insurer_id')), smo_id))
                        and (not start_date or valIsMatched(forceDate(item.value('begDate')), start_date))
                ):
                    return row
                elif isCompulsory:
                    return -1
        return -1

    def getCurrentPolicyRow(self, isCompulsory, serial, number, smo_id='', start_date=''):
        row = self.getCurrentPolicyRowInt(isCompulsory, serial, number, smo_id, start_date)
        if row < 0:
            row = len(self.items())
            item = self.getEmptyRecord()
            self.insertRecord(row, item)
            item.setValue('policyType_id', toVariant(self.getFirstPolicyTypeId(isCompulsory)))
        return row

    def getCurrentCompulsoryPolicyRow(self, serial, number, smo_id='', start_date=''):
        return self.getCurrentPolicyRow(True, serial, number, smo_id, start_date)

    def getCurrentVoluntaryPolicyRow(self, serial, number, smo_id='', start_date=''):
        return self.getCurrentPolicyRow(False, serial, number, smo_id, start_date)

    def policyTypeIsCompulsory(self, policyTypeId, isCompulsory):
        if policyTypeId:
            cache = CRBModelDataCache.getData(self.policyTypeColumn.tableName, True)
            return self.policyTypeNameIsCompulsory(cache.getNameById(policyTypeId)) == isCompulsory
        return False

    def getFirstPolicyTypeId(self, isCompulsory):
        cache = CRBModelDataCache.getData(self.policyTypeColumn.tableName, True)
        for i in xrange(cache.getCount()):
            itemId = cache.getId(i)
            if itemId and self.policyTypeNameIsCompulsory(cache.getName(i)) == isCompulsory:
                return itemId
        return None

    def policyTypeNameIsCompulsory(self, name):
        return unicode(name)[:3].upper() == u'ОМС'

    def cleanUpEmptyItems(self):
        items = self.items()
        for i in reversed(xrange(len(items))):
            item = items[i]
            itemId = forceRef(item.value('id'))
            # serial = forceStringEx(item.value('serial'))
            number = forceStringEx(item.value('number'))
            insurerId = forceRef(item.value('insurer_id'))
            name = forceStringEx(item.value('name'))
            if not (itemId or number or insurerId or name):
                self.removeRows(i, 1)


class CSocStatusDocsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientDocument', 'id', 'client_id', parent)
        documentTypeIdList = getDocumentTypeIdListByGroupList(['2', '5', '7'])
        self.setFilter(self.table['documentType_id'].inlist(documentTypeIdList))
        tableDocumentType = QtGui.qApp.db.table('rbDocumentType')
        self.addCol(CRBInDocTableCol(u'Тип', 'documentType_id', 30, 'rbDocumentType', filter=tableDocumentType['id'].inlist(documentTypeIdList)))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 8))
        self.addCol(CInDocTableCol(u'Номер', 'number', 16))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'date', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Выдан', 'origin', 30))


class CContactsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientContact', 'id', 'client_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип', 'contactType_id', 30, 'rbContactType', addNone=False))
        self.addCol(CInDocTableCol(u'Номер', 'contact', 30))
        self.addCol(CInDocTableCol(u'Примечание', 'notes', 30))
        typeRecord = QtGui.qApp.db.getRecordEx('rbContactType', 'id')
        self.defaultContactType = typeRecord.value(0)
        self.maskDict = getClientPhonesMaskDict()

    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        record.setValue('contactType_id', self.defaultContactType)
        return record

    def setEditorData(self, column, editor, value, record):
        id = forceInt(record.value('contactType_id'))
        if self.maskDict.has_key(id) and column == self.getColIndex('contact') and self.maskDict[id]['enabled']:
            editor.setInputMask(self.maskDict[id]['mask'])
            editor.setText(forceStringEx(value))
        else:
            return CInDocTableModel.setEditorData(self, column, editor, value, record)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            column = index.column()
            row = index.row()
            id = forceInt(value)
            if column == self.getColIndex('contactType_id'):
                if row != len(self._items) and self.maskDict.has_key(id) and self.maskDict[id]['enabled']:
                    contact = forceString(self._items[row].value('contact'))
                    check = QtGui.QLineEdit()
                    check.setInputMask(self.maskDict[id]['mask'])
                    check.setText(contact)
                    contact = check.text()
                    self.setData(self.index(row, self.getColIndex('contact')), toVariant(contact))

        return CInDocTableModel.setData(self, index, value, role)

    def setDialogContact(self, typeContactId, contact):
        if typeContactId:
            row = len(self.items())
            item = CInDocTableModel.getEmptyRecord(self)
            self.insertRecord(row, item)
            item.setValue('contactType_id', toVariant(typeContactId))
            item.setValue('contact', toVariant(contact))

    def saveItems(self, masterId):
        if self._items is not None:
            for i in xrange(len(self._items)):
                typeId = forceInt(self._items[i].value('contactType_id'))
                if self.maskDict.has_key(typeId) and self.maskDict[typeId]['enabled']:
                    contact = forceString(self._items[i].value('contact'))
                    self._items[i].setValue('contact', toVariant(contact))
        return CInDocTableModel.saveItems(self, masterId)

    def loadItems(self, masterId):
        result = CInDocTableModel.loadItems(self, masterId)
        if self._items is not None:
            for i in xrange(len(self._items)):
                typeId = forceInt(self._items[i].value('contactType_id'))
                if self.maskDict.has_key(typeId) and self.maskDict[typeId]['enabled']:
                    contact = forceString(self._items[i].value('contact'))
                    check = QtGui.QLineEdit()
                    check.setInputMask(self.maskDict[typeId]['mask'])
                    check.setText(contact)
                    self._items[i].setValue('contact', toVariant(unicode(check.text())))
        self.reset()
        self.setDirty(False)
        return result


class CAllergyModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientAllergy', 'id', 'client_id', parent)
        self.addCol(CInDocTableCol(u'Наименование вещества', 'nameSubstance', 50))
        self.addCol(CEnumInDocTableCol(u'Степень', 'power', 15, [u'0 - не известно', u'1 - малая', u'2 - средняя', u'3 - высокая', u'4 - строгая']))
        self.addCol(CDateInDocTableCol(u'Дата установления', 'createDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Примечание', 'notes', 30))


class CDispanserizationModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientDispanserization', 'id', 'client_id', parent)
        self.addCol(CInDocTableCol(u'Код', 'code', 30))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'date_begin', 15))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'date_end', 15))
        self.addCol(CInDocTableCol(u'Код МО', 'codeMO', 50))


class CIntoleranceMedicamentModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientIntoleranceMedicament', 'id', 'client_id', parent)
        self.addCol(CMedicamentInDocTableCol(u'Название медикамента', 'nameMedicament', 50))
        self.addCol(CEnumInDocTableCol(u'Степень', 'power', 15, [u'0 - не известно', u'1 - малая', u'2 - средняя', u'3 - высокая', u'4 - строгая']))
        self.addCol(CDateInDocTableCol(u'Дата установления', 'createDate', 15, canBeEmpty=True))
        self.addCol(CInDocTableCol(u'Примечание', 'notes', 30))


class CClientIdentificationModel(CInDocTableModel):
    __pyqtSignals__ = ('documentChanged(int)',
                       )
    mapAccountingSystemIdToNeedUniqueValue = {}

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientIdentification', 'id', 'client_id', parent)
        self.__parent = parent
        self.addCol(CRBInDocTableCol(u'Внешняя учётная система', 'accountingSystem_id', 30, 'rbAccountingSystem', addNone=False, filter=u'autoIdentificator = 0'))
        self.addCol(CInDocTableCol(u'Идентификатор', 'identifier', 30))
        self.addCol(CDateInDocTableCol(u'Дата подтверждения', 'checkDate', 15, canBeEmpty=True))
        self.isEditableInfo = {}
        flagsList = QtGui.qApp.db.getRecordList('rbAccountingSystem', 'id, isEditable')
        if flagsList:
            for x in flagsList:
                self.isEditableInfo[forceRef(x.value(0))] = forceBool(x.value(1))

    def flags(self, index=QtCore.QModelIndex()):
        column = index.column()
        if column == 0 : #  accountingSystem
            row = index.row()
            items = self.items()
            record = items[row] if 0 <= row < len(items) else None
            if record:
                accountingSystemId = forceRef(record.value('accountingSystem_id'))
                counterId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', 'id', accountingSystemId, 'counter_id'))
                if counterId:
                    return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if column == 1:  # identifier
            row = index.row()
            items = self.items()
            record = items[row] if 0 <= row < len(items) else None
            accountingSystemId = forceRef(record.value('accountingSystem_id')) if record else None
            nullId = (forceString(record.value('identifier')) == '') if record else True
            if accountingSystemId and (self.isEditableInfo.get(accountingSystemId,  False) or nullId):
                return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return CInDocTableModel.flags(self, index)

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('checkDate', toVariant(QtCore.QDate.currentDate()))
        return result

    def emitDataChanged(self, row, column):
        index = self.index(row, column)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        items = self.items()
        col = index.column()
        db = QtGui.qApp.db
        if col == 0:  # если меняем систему, проверим уникальность
            if not forceRef(value):
                return False
            if not QtGui.qApp.userHasRight(Users.Rights.urAddDublicateClientIdentifier):
                for record in items:
                    if forceRef(record.value('accountingSystem_id')) == forceRef(value):
                        return False

        if col == 1:  # меняем идентификатор. Проверяем необходимость проверки на уникальность и если нужно проверяем.
            newIdentifier = forceString(value)
            if newIdentifier == '':
                return False
            item = items[index.row()]
            currentItemId = forceRef(item.value('id'))
            accountingSystemId = forceRef(item.value('accountingSystem_id'))
            if self.needUniqueValue(accountingSystemId):
                if not uniqueIdentifierCheckingIsPassed(currentItemId, accountingSystemId, newIdentifier):
                    return False
        result = CInDocTableModel.setData(self, index, value, role)
        if result and role == QtCore.Qt.EditRole and col == 0:
            row = index.row()
            record = items[row] if 0 <= row < len(items) else None
            if record:
                record.setValue('checkDate', toVariant(QtCore.QDate().currentDate()))
                self.emitDataChanged(row, 2)  # колонка checkDate
                accountingSystem = db.getRecord('rbAccountingSystem', '*', forceRef(record.value('accountingSystem_id')))
                counterId = forceRef(accountingSystem.value('counter_id'))
                if counterId and not forceBool(accountingSystem.value('autoIdentifier')) and not forceRef(record.value('id')):
                    counter = db.getRecord('rbCounter', '*', counterId)
                    counterVal = forceInt(counter.value('value'))
                    record.setValue('identifier', counterVal)
                    self.emitDataChanged(row, 1)  # колонка identifier
                    # update counter
                    counter.setValue('value', counterVal + 1)
                    db.updateRecord('rbCounter', counter)
        return result

    @classmethod
    def needUniqueValue(cls, accountingSystemId):
        isUnique = cls.mapAccountingSystemIdToNeedUniqueValue.get(accountingSystemId, None)
        if isUnique is None:
            isUnique = forceBool(QtGui.qApp.db.translate('rbAccountingSystem',
                                                         'id',
                                                         accountingSystemId,
                                                         'isUnique'))
            cls.mapAccountingSystemIdToNeedUniqueValue[accountingSystemId] = isUnique
        return isUnique


class COldWorksModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ClientWork', 'id', 'client_id', parent)
        self.addCol(CDesignationInDocTableCol(u'Организация', 'org_id', ('Organisation', 'shortName'), 50))
        self.addCol(CInDocTableCol(u'Должность', 'post', 50).setReadOnly(True))
        self.addCol(CIntInDocTableCol(u'Стаж', 'stage', 50).setReadOnly(True))
        self.addHiddenCol('freeInput')
        self.setEnableAppendLine(False)

    def data(self, index, role):
        result = CInDocTableModel.data(self, index, role)
        if result.isValid() and index.column() == 0 and not forceString(result):
            return self._items[index.row()].value('freeInput')
        return result


class CRBQuotaTypeInDocTableCol(CRBInDocTableCol, QtCore.QObject):
    __pyqtSignals__ = ('quotaTypeSelected(int)',
                       )

    def __init__(self, title, fieldName, width, tableName, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)
        QtCore.QObject.__init__(self)

    def createEditor(self, parent):
        editor = CQuotaTypeComboBox(parent)
        editor.setTable(self.tableName, addNone=self.addNone, filter=self.filter, order=self.order)
        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        self.connect(editor, QtCore.SIGNAL('quotaTypeSelected(int)'), self.on_editor_quotaTypeSelected)
        return editor

    @QtCore.pyqtSlot()
    def on_editor_quotaTypeSelected(self, quotaType_id):
        self.emit(QtCore.SIGNAL('quotaTypeSelected(int)'), quotaType_id)


class CClientQuotingModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Client_Quoting', 'id', 'master_id', parent)
        self.parentWidget = parent
        self.addCol(CRBQuotaTypeInDocTableCol(u'Квота', 'quotaType_id', 255, 'QuotaType', showFields=0))
        self.addCol(CIntInDocTableCol(u'Этап', 'stage', 2))
        self.addCol(CInDocTableCol(u'МКБ', 'MKB', 8))
        self.addCol(CEnumInDocTableCol(u'Статус', 'status', 2, [u'Отменено',
                                                                u'Ожидание',
                                                                u'Активный талон',
                                                                u'Талон для заполнения',
                                                                u'Заблокированный талон',
                                                                u'Отказано',
                                                                u'Необходимо согласовать дату обслуживания',
                                                                u'Дата обслуживания на согласовании',
                                                                u'Дата обслуживания согласована',
                                                                u'Пролечен',
                                                                u'Обслуживание отложено',
                                                                u'Отказ пациента',
                                                                u'Импортировано из ВТМП']))
        self.addHiddenCol('identifier')
        self.addHiddenCol('quotaTicket')
        self.addHiddenCol('directionDate')
        self.addHiddenCol('freeInput')
        self.addHiddenCol('org_id')
        self.addHiddenCol('amount')
        self.addHiddenCol('request')
        self.addHiddenCol('statment')
        self.addHiddenCol('dateRegistration')
        self.addHiddenCol('dateEnd')
        self.addHiddenCol('orgStructure_id')
        self.addHiddenCol('regionCode')
        self._info = {}
        self.basicData = []
        self.basicDataCount = 0
        self.isActiveQuota = None
        self.currentRow = None
        self.isChangeingRow = None
        self.recordsForDeleting = []
        self.clientAttachForDeleting = []
        self.regCityCode = None
        self.newRegCityCode = None
        self.connect(self.getCol('quotaType_id'), QtCore.SIGNAL('quotaTypeSelected(int)'), self.on_quotaTypeCol_quotaTypeSelected)

    def addClientAttachForDeleting(self, attachRecord):
        self.clientAttachForDeleting.append(attachRecord)

    def setRegCityCode(self, regCityCode):
        self.regCityCode = regCityCode

    def setNewRegCityCode(self, regCityCode):
        self.newRegCityCode = regCityCode

    def flags(self, index):
        column = index.column()
        row = index.row()
        if column == 0 and row == len(self.items()):
            return CInDocTableModel.flags(self, index)
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def getEmptyRecord(self):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('status', toVariant(1))
        currentDate = QtCore.QDate().currentDate()
        result.setValue('dateRegistration', toVariant(currentDate))
        result.setValue('amount', QtCore.QVariant(1))
        return result

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        resume = CInDocTableModel.setData(self, index, value, role)
        if resume:
            self.basicData.append([None, None, ''])
        return resume

    def info(self):
        return self._info

    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        self.saveBasicData()

    def saveBasicData(self):
        items = self.items()
        self.basicDataCount = len(items)
        for item in items:
            data = []
            data.append(forceInt(item.value('amount')))
            data.append(forceInt(item.value('status')))
            data.append(forceString(item.value('regionCode')))
            self.basicData.append(data)

    def saveItems(self, masterId):
        items = self.items()
        basicData = self.basicData
        endedQuotes = 0
        minDate = None
        maxDate = None
        for idx, record in enumerate(items):
            currAmount = forceInt(record.value('amount'))
            currStatus = forceInt(record.value('status'))
            currRegionCode = forceString(record.value('regionCode'))
            baseAmount = basicData[idx][0]
            baseStatus = basicData[idx][1]
            baseRegionCode = basicData[idx][2]
            if currStatus in [5, 9, 11]:
                endedQuotes += 1
                date = forceDate(record.value('dateEnd'))
                if not maxDate:
                    maxDate = date
                else:
                    if date > maxDate:
                        maxDate = date
            if not minDate:
                minDate = forceDate(record.value('dateRegistration'))
            else:
                date = forceDate(record.value('dateRegistration'))
                if date < minDate:
                    minDate = date
            if baseRegionCode:
                regCityCode = baseRegionCode
            else:
                regCityCode = self.regCityCode
            if currRegionCode:
                newRegCityCode = currRegionCode
            else:
                newRegCityCode = self.newRegCityCode
            if currStatus != baseStatus:
                quotingRecords = self.getActualQuotingRecords(record)
                if quotingRecords:
                    for quotingRecord in quotingRecords:
                        if baseAmount:
                            self.changeData(quotingRecord, baseStatus, baseAmount, baseAmount.__sub__)
                        self.changeData(quotingRecord, currStatus, currAmount, currAmount.__add__)
                        if regCityCode:
                            if baseAmount:
                                self.changeRegionData(baseStatus, baseAmount, baseAmount.__sub__,
                                                      regCityCode, quotingRecord)
                        if newRegCityCode:
                            if regCityCode != newRegCityCode:
                                self.changeRegionData(currStatus, currAmount, currAmount.__add__,
                                                          newRegCityCode, quotingRecord)
                            else:
                                self.changeRegionData(currStatus, currAmount, currAmount.__add__,
                                                          regCityCode, quotingRecord)
            else:
                if currAmount != baseAmount:
                    quotingRecords = self.getActualQuotingRecords(record)
                    if quotingRecords:
                        for quotingRecord in quotingRecords:
                            dAmount = currAmount-baseAmount
                            self.changeData(quotingRecord, currStatus, dAmount, dAmount.__add__)
                            if regCityCode != newRegCityCode:
                                if regCityCode:
                                    self.changeRegionData(baseStatus, baseAmount, baseAmount.__sub__,
                                                      regCityCode, quotingRecord)
                                if newRegCityCode:
                                    self.changeRegionData(currStatus, currAmount, currAmount.__add__,
                                                          newRegCityCode, quotingRecord)
                            else:
                                if newRegCityCode:
                                    self.changeRegionData(currStatus, dAmount, dAmount.__add__,
                                                          newRegCityCode, quotingRecord)

        if len(items) > 0:
            self.setQuotingAttach(masterId, endedQuotes==len(items), minDate, maxDate, self.basicDataCount<len(items))
        CInDocTableModel.saveItems(self, masterId)
        if self.recordsForDeleting:
            self.changeQuotingDataForDeletedRecordList(self.recordsForDeleting)

    def setQuotingAttach(self, clientId, allAreEnded, minDate, maxDate, newQuotaAdded):
        db = QtGui.qApp.db
        table = db.table('ClientAttach')
        attachTypeId = db.translate('rbAttachType', 'code', '9', 'id')
        attachItems = self.parentWidget.tblAttaches.model().items()
        quotaAttachListEnded = []
        quotaAttachListNotEnded = []
        recordList = []
        if attachItems:
            quotaAttachList = [attach for attach in attachItems if attach.value('attachType_id') == attachTypeId]
            if quotaAttachList:
                for attach in quotaAttachList:
                    if forceDate(attach.value('endDate')).isValid():
                        quotaAttachListEnded.append(attach)
                    else:
                        quotaAttachListNotEnded.append(attach)
        if (not attachItems) or (not quotaAttachListNotEnded and newQuotaAdded):
            record = table.newRecord()
            record.setValue('client_id', QtCore.QVariant(clientId))
            record.setValue('attachType_id', attachTypeId)
            record.setValue('LPU_id', QtCore.QVariant(QtGui.qApp.currentOrgId()))
            record.setValue('begDate', toVariant(minDate))
            if allAreEnded:
                record.setValue('endDate', toVariant(maxDate))
            recordList.append(record)
        else:
            if quotaAttachListNotEnded:
                for attach in quotaAttachListNotEnded:
                    attach.setValue('begDate', toVariant(minDate))
                    if allAreEnded:
                        attach.setValue('endDate', toVariant(maxDate))
                    recordList.append(attach)
        clientQuotaAttachIdList = []
        for record in recordList:
            clientQuotaAttachIdList.append(db.insertOrUpdate('ClientAttach', record))
        return clientQuotaAttachIdList

    def changeRegionData(self, status, amount, action, code, quotingRecord):
        regionRecords = findKLADRRegionRecordsInQuoting(code, quotingRecord)
        for regionRecord in regionRecords:
            self.changeData(regionRecord, status, amount, action, 'Quoting_Region')

    def changeData(self, quotingRecord, status, amount, action, table='Quoting'):
        columnName = self.translateStatusToColumn(status)
        if columnName:
            columnValue = forceInt(quotingRecord.value(columnName))
            resumeValue = abs(action(columnValue))
            quotingRecord.setValue(columnName, QtCore.QVariant(resumeValue))
            QtGui.qApp.db.updateRecord(table, quotingRecord)

    def translateStatusToColumn(self, status):
        if status == 9:
            return 'used'
        if status == 8:
            return 'confirmed'
        if status in [1, 2, 3, 4, 6, 7, 10, 12]:
            return 'inQueue'
#        if status in [0, 5, 11]:
        return None

    def getActualQuotingRecords(self, record):
        db = QtGui.qApp.db
        dateRegistration = forceDate(record.value('dateRegistration'))
        dateEnd = forceDate(record.value('dateEnd'))
        quotaType_id = forceInt(record.value('quotaType_id'))
        tableQuoting = db.table('Quoting')
        if not dateEnd.isValid():
            condDate = [tableQuoting['endDate'].ge(dateRegistration)]
        else:
            condDate = [db.joinOr([db.joinAnd([tableQuoting['beginDate'].le(dateRegistration),
                                               tableQuoting['endDate'].ge(dateRegistration)]),
                                   db.joinAnd([tableQuoting['beginDate'].le(dateEnd),
                                               tableQuoting['endDate'].ge(dateEnd)])])]
        condDate.append(tableQuoting['deleted'].eq(0))
        record = db.getRecordEx(tableQuoting, '*', [tableQuoting['quotaType_id'].eq(quotaType_id)] + condDate)
        result = []
        if record:
            result.append(record)
#        else:
        code = forceString(db.translate('QuotaType', 'id', quotaType_id, 'code'))
        while code.find('.') > -1:
            record, code = self.checkParent(tableQuoting, condDate, quotaType_id)
            quotaType_id = forceRef(db.translate('QuotaType', 'code', code, 'id'))
            if record:
                result.append(record)
        return result

    def setNullInfo(self):
        self._info['limit'] = 0
        self._info['used'] = 0
        self._info['confirmed'] = 0
        self._info['inQueue'] = 0

    def loadItemsInfo(self, row):
        if row == None:
            self.setNullInfo()
            self._info['quotaTypeName'] = ''
            return
        db = QtGui.qApp.db
        tableQuoting = db.table('Quoting')
        record = self.items()[row]
        quotaType_id = forceInt(record.value('quotaType_id'))
        quotaTypeName = forceString(
            QtGui.qApp.db.translate('QuotaType', 'id', quotaType_id, 'name'))
        condDate = []
        dateRegistration = forceDateTime(record.value('dateRegistration'))
        dateEnd = forceDateTime(record.value('dateEnd'))
        if dateRegistration.isValid():
            condDate.append(db.joinAnd([tableQuoting['beginDate'].le(dateRegistration),
                                        tableQuoting['endDate'].ge(dateRegistration)]))
        if dateEnd.isValid():
            condDate.append(db.joinAnd([tableQuoting['beginDate'].le(dateEnd),
                                        tableQuoting['endDate'].ge(dateEnd)]))
        cond = [db.joinOr(condDate)] if condDate else []
        recordQuoting, brothersLimitIfNeedElseZero = self.getQuotingRecord(tableQuoting, cond, quotaType_id)
        self._info['quotaTypeName'] = quotaTypeName
        if recordQuoting:
            self._info['limit'] = forceInt(recordQuoting.value('limitation')) - brothersLimitIfNeedElseZero
            self._info['used'] = forceInt(recordQuoting.value('used'))
            self._info['confirmed'] = forceInt(recordQuoting.value('confirmed'))
            self._info['inQueue'] = forceInt(recordQuoting.value('inQueue'))
        else:
            self.setNullInfo()

    def getQuotingRecord(self, tableQuoting, cond, quotaType_id):
        db = QtGui.qApp.db
        condTmp = list(cond)
        condTmp.append(tableQuoting['quotaType_id'].eq(quotaType_id))
        record = db.getRecordEx('Quoting', '*', condTmp)
        if record:
            return record, 0
        else:
            val = 0
            record, parentCode = self.checkParent(tableQuoting, cond, quotaType_id)
            if record:
                val = self.checkBrothersLimit(tableQuoting, cond, parentCode)
            return record, val

    def checkParent(self, tableQuoting, cond, quotaType_id):
        db = QtGui.qApp.db
        parentCode = forceString(db.translate('QuotaType', 'id', quotaType_id, 'group_code'))
        if parentCode:
            parentId = forceInt(db.translate('QuotaType', 'code', parentCode, 'id'))
            record, _ = self.getQuotingRecord(tableQuoting, cond, parentId)
            return record, parentCode
        else:
            return None, ''

    def checkBrothersLimit(self, tableQuoting, cond, parentCode):
        db = QtGui.qApp.db
        idList = db.getIdList('QuotaType', 'id', 'group_code=%s' % parentCode)
        condTmp = list(cond)
        condTmp.append(tableQuoting['quotaType_id'].inlist(idList))
        stmt = db.selectStmt(tableQuoting, 'SUM(`limitation`)', condTmp)
        query = db.query(stmt)
        if query.first():
            return forceInt(query.value(0))
        return 0

    def removeRows(self, row, count, parentIndex=QtCore.QModelIndex()):
        tmpItems = list(self.items())
        resume = CInDocTableModel.removeRows(self, row, count, parentIndex)
        if resume:
            itemsForDeleting = tmpItems[row:row + count]
            for item in itemsForDeleting:
                self.recordsForDeleting.append(item)
            decreaseBD = row in range(len(self.basicData))
            del self.basicData[row:row + count]
            if decreaseBD:
                self.basicDataCount = len(self.basicData)
        return resume

    def changeQuotingDataForDeletedRecordList(self, recordList):
        for record in recordList:
            if record.value('id').isValid():
                quotingRecords = self.getActualQuotingRecords(record)
                if quotingRecords:
                    for quotingRecord in quotingRecords:
                        status = forceInt(record.value('status'))
                        amount = forceInt(record.value('amount'))
                        self.changeData(quotingRecord, status, amount, amount.__sub__)
                        regCityCode = self.regCityCode
                        if not regCityCode:
                            regCityCode = self.parentWidget.cmbRegCity.code()
                        self.changeRegionData(status, amount, amount.__sub__,
                                              regCityCode, quotingRecord)

    @QtCore.pyqtSlot(int)
    def on_quotaTypeCol_quotaTypeSelected(self, quotaType_id):
        self.emit(QtCore.SIGNAL('quotaTypeSelected(int)'), quotaType_id)


class CClientQuotingDiscussionModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CDateCol(u'Дата', ['dateMessage'], 16),
            CTimeCol(u'Время', ['dateMessage'], 16),
            CRefBookCol(u'Тип согласования', ['agreementType_id'], 'rbAgreementType', 15),
            CRefBookCol(u'Ответственный ЛПУ', ['responsiblePerson_id'], 'vrbPersonWithSpeciality', 16, 1),
            CTextCol(u'Контрагент', ['cosignatory'], 25),
            CTextCol(u'Должность', ['cosignatoryPost'], 20),
            CNameCol(u'ФИО', ['cosignatoryName'], 50),
            CTextCol(u'Примечание', ['remark'], 128)
        ], 'Client_QuotingDiscussion')


class CClientDisabilityModel(CInDocTableModel):
    def __init__(self, parent=None):
        super(CClientDisabilityModel, self).__init__(u'ClientDisability',
                                                     u'id',
                                                     u'client_id',
                                                     parent)
        self.addCol(CBoolInDocTableCol(u'Cомат.', 'isSomatic', 10))
        self.addCol(CDateInDocTableCol(u'Дата установления', 'setDate', 50))
        self.addCol(CBoolInDocTableCol(u'Бессрочно', 'isTermless', 10))
        # atronah: возможно лучше текстом, так как CIntInDocTableCol вроде не допускает пустого значения
        self.addCol(CEnumInDocTableCol(u'Группа', 'groupNumber', 15, [u'0 (отказ)', u'1', u'2', u'3', u'4 (дети-инвалиды)']))
        self.addCol(CDateInDocTableCol(u'Очередное переосв.', 'recertificationDate', 50))
        self.addCol(CDesignationInDocTableCol(title=u'Место работы',
                                              fieldName='work_id',
                                              designationChain=[(u'ClientWork', ['org_id', 'freeInput']),
                                                                (u'Organisation', 'shortName')],
                                              defaultWidth=15,
                                              addNone=True,
                                              editorValueFilter=('client_id', 'client_id')
                                              ).setReadOnly(False))
        self.addCol(CEnumInDocTableCol(u'Степень утраты трудосп.', 'degree', 15, [u'1', u'2', u'3'], addNone=True))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 30))
        self.addCol(CBoolInDocTableCol(u'Перв.', 'isPrimary', 10))
        self.addCol(CBoolInDocTableCol(u'Стационар', 'isStationary', 10))


class CSuicideModel(CInDocTableModel):
    def __init__(self, parent=None):
        super(CSuicideModel, self).__init__(u'ClientRemark',
                                            u'id',
                                            u'client_id',
                                            parent,
                                            rowNumberTitle=u'№ п/п')
        suicideCond = u"flatCode like 'suicide%'"
        self._suicideTypeIdList = QtGui.qApp.db.getIdList('rbClientRemarkType', where=suicideCond)
        if self._suicideTypeIdList:
            self.setFilter(self.table['remarkType_id'].inlist(self._suicideTypeIdList))
        else:
            self.setEditable(False)
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 50))
        self.addCol(CRBInDocTableCol(u'Состояние', 'remarkType_id', 50, 'rbClientRemarkType', addNone=False, showFields=CRBComboBox.showName, filter=suicideCond))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 15))
        self.addHiddenCol('remarkType_id')

    def getEmptyRecord(self):
        record = super(CSuicideModel, self).getEmptyRecord()
        record.setValue('remarkType_id', toVariant(self._suicideTypeIdList[0]))
        return record


class CMisdemeanorModel(CInDocTableModel):
    def __init__(self, parent=None):
        super(CMisdemeanorModel, self).__init__(u'ClientMisdemeanor',
                                                u'id',
                                                u'client_id',
                                                parent)
        if QtGui.qApp.isPNDDiagnosisMode():
            self.addCol(CDateInDocTableCol(u'Дата совершения ООД', 'crimeDate', 15))
        self.addCol(CInDocTableCol(u'Статья УК', 'criminalRule', 15))
        self.addCol(CInDocTableCol(u'Суд', 'court', 15))
        self.addCol(CInDocTableCol(u'№ дела', 'caseNumber', 15))
        self.addCol(CDateInDocTableCol(u'Дата постановления', 'writDate', 15))
        self.addCol(CInDocTableCol(u'Постановление', 'writ', 15))
        self.addCol(CRBInDocTableCol(u'Врач', 'person_id', 15, 'vrbPersonWithSpeciality', filter='(speciality_id IS NOT NULL AND retireDate IS NULL)'))
        self.addCol(CDateInDocTableCol(u'Дата очередного обращения в суд', 'nextRecourceDate', 15))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 15))


class CCompulsoryTreatmentModel(CInDocTableModel):
    def __init__(self, parent=None):
        super(CCompulsoryTreatmentModel, self).__init__(u'ClientCompulsoryTreatment',
                                                        u'id',
                                                        u'client_id',
                                                        parent,
                                                        rowNumberTitle=u'№ п/п')
        self.addCol(CDateInDocTableCol(u'Дата решения суда о начале лечения', 'begDate', 15))
        self.addCol(CRBInDocTableCol(u'Вид', 'setKind_id', 15, 'rbCompulsoryTreatmentKind'))
        self.addCol(CDateInDocTableCol(u'Дата изменения вида (продления)', 'extensionDate', 15))
        self.addCol(CRBInDocTableCol(u'Вид', 'newKind_id', 15, 'rbCompulsoryTreatmentKind'))
        self.addCol(CDateInDocTableCol(u'Дата решения суда об окончании принуд. лечения', 'endDate', 15))
        self.addCol(CInDocTableCol(u'Примечание', 'note', 15))


class CMonitoringModel(CInDocTableModel):
    def __init__(self, parent=None):
        super(CMonitoringModel, self).__init__(u'ClientMonitoring',
                                               u'id',
                                               u'client_id',
                                               parent)
        self.addCol(CRBTreeInDocTableCol(u'Вид наблюдения', 'kind_id', 15, 'rbClientMonitoringKind', showFields=CRBComboBox.showName))
        self.addCol(CRBDependedInDocTableCol(u'Частота посещений',
                                             'frequence_id',
                                             50, 'vrbClientMonitoringFrequence',
                                             dependField='kind_id',
                                             showFields=CRBComboBox.showName))
        self.addCol(CDateInDocTableCol(u'Дата начала', 'setDate', 15, canBeEmpty=False))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(u'Причина прекращения наблюдения', 'reason_id', 15, 'rbStopMonitoringReason'))

    def flags(self, index):
        flags = super(CMonitoringModel, self).flags(index)
        isLastRow = index.row() == (self.rowCount() - 1)
        isKindColumn = index.column() == self.getColIndex('kind_id')
        isFrequenceColumn = index.column() == self.getColIndex('frequence_id')
        # запрет на редактирования вида наблюдения в имеющихся наблюдениях,
        # и в добавляемых, если нет на это права.
        # плюс запрет на редактирования в добавляемом наблюдения всего кроме вида и частоты
        if isLastRow and (isKindColumn and not QtGui.qApp.userHasRight(Users.Rights.urChangeMonitoringKind) or not (isFrequenceColumn or isKindColumn)) \
                or not isLastRow and isKindColumn:
            flags = flags & (~QtCore.Qt.ItemIsEditable) & (~QtCore.Qt.ItemIsUserCheckable)
        return flags

    def loadItems(self, itemId):
        super(CMonitoringModel, self).loadItems(itemId)

    def getEmptyRecord(self):
        record = super(CMonitoringModel, self).getEmptyRecord()
        record.setValue('setDate', toVariant(QtCore.QDate.currentDate()))
        return record

    def getSameKindItems(self, kindId):
        result = []
        for row, record in enumerate(self.items()):
            if forceRef(record.value('kind_id')) == kindId:
                result.append((row, record))
        return result

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # Если редактируется частота для ново-добавляемого вида наблюдения,
        # то вид наблюдения ставится, как у предыдущего наблюдения
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.row() == self.rowCount() - 1 and index.column() == self.getColIndex('frequence_id'):
                self.setData(self.index(index.row(),
                                        self.getColIndex('kind_id')),
                             self._items[-1].value('kind_id'))

        return super(CMonitoringModel, self).data(index, role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        setDate = QtCore.QDate()
        isLastRow = index.row() == self.rowCount() - 1
        isKindColumn = index.column() == self.getColIndex('kind_id')
        if isLastRow and isKindColumn:
            kindId = forceRef(value)
        elif not isLastRow:
            kindId = self.value(index.row(), 'kind_id')
        else:
            kindId = None

        sameKindItems = self.getSameKindItems(kindId)

        # check setDate for previous monitorings with same kind
        if (index.column() == self.getColIndex('setDate')
            or (isLastRow and isKindColumn)
            ):
            setDate = forceDate(value) if not (isLastRow and isKindColumn) else QtCore.QDate.currentDate()
            if not setDate.isValid() or setDate.isNull():
                return False

            # check that setDate is not greater than endDate if endDate is not null
            endDate = forceDate(self.value(index.row(), 'endDate'))
            if endDate.isValid() and not endDate.isNull() and setDate > endDate:
                return False

            if sameKindItems:
                row, previousItem = max(sameKindItems,
                                        key=lambda (_, record): forceDate(record.value('setDate')) if setDate >= forceDate(record.value('setDate'))
                                        else None)
                prevSetDate = forceDate(previousItem.value('setDate'))
                if setDate == prevSetDate:
                    return False
                elif setDate > prevSetDate:
                    prevEndDate = forceDate(previousItem.value('endDate'))
                    if prevEndDate > setDate:
                        if not self.setData(self.index(row, self.getColIndex('endDate')), setDate):
                            return False

        if (not isLastRow and index.column() == self.getColIndex('endDate')):
            endDate = forceDate(value)
            if endDate.isValid() and not endDate.isNull():
                # check that setDate is greater than endDate if endDate is not null
                setDate = forceDate(self.value(index.row(), 'setDate'))
                if setDate > endDate:
                    return False
                if sameKindItems:
                    row, nextItem = min(sameKindItems,
                                        key=lambda (_, record): forceDate(record.value('setDate')) if forceDate(record.value('setDate')) > setDate
                                        else None)
                    nextSetDate = forceDate(nextItem.value('setDate'))
                    if setDate < nextSetDate:
                        if endDate > nextSetDate:
                            return False

        result = super(CMonitoringModel, self).setData(index, value, role)

        # close (set endDate) previous openned monitorings with same kind
        if result and isLastRow and isKindColumn:
            for _, record in sameKindItems[::-1]:
                if record.value('endDate').isNull():
                    record.setValue('endDate', toVariant(setDate))
                    setDate = forceDate(record.value('setDate'))

        return result


class CForeignHospitalizationModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'ForeignHospitalization', 'id', 'client_id', parent, rowNumberTitle=u'№ п/п')
        self.defaultDate = [QtCore.QDate(2200, 1, 1), QtCore.QDate(2099, 12, 31)]
        self.addCol(CPolyclinicExtendedInDocTableCol(u'Наименование ЛПУ', 'org_id', 20))
        self.addCol(CRBInDocTableCol(u'Цель госпитализации', 'purpose_id', 20, 'rbHospitalizationPurpose', showFields=CRBComboBox.showName))
        self.addCol(CDateInDocTableCol(u'Дата поступления', 'startDate', 10, canBeEmpty=False))
        self.addCol(CDateInDocTableCol(u'Дата выбытия', 'endDate', 10, canBeEmpty=False, defaultDate=self.defaultDate[0]))
        self.addCol(CICDInDocTableCol(u'МКБ', 'MKB', 5))
        self.addCol(CInDocTableCol(u'Клинический диагноз', 'clinicDiagnosis', 20))
        self._parent = parent

    def getEmptyRecord(self):
        record = CInDocTableModel.getEmptyRecord(self)
        return record

    def setDefaultDates(self, row, column):
        item = self.items()[row]
        if column != self.getColIndex('startDate'):
            item.setValue('startDate', QtCore.QDate.currentDate())
            self.emitCellChanged(row, self.getColIndex('setDate'))
        if column != self.getColIndex('endDate'):
            item.setValue('endDate', QtCore.QDate())
            self.emitCellChanged(row, self.getColIndex('endDate'))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        isNewItem = row == len(self.items())

        if not variantEq(self.data(index, role), value):
            if column == self.getColIndex('MKB'):
                newMKB = forceString(value)
                if not newMKB:
                    specifiedMKB = ''
                    specifiedCharacterId = None
                else:
                    date = forceDate(self.value(row, 'startDate'))
                    if not date:
                        date = QtCore.QDate.currentDate()
                    age = calcAgeTuple(self._parent.edtBirthDate.date(), date)
                    acceptable, specifiedMKB, _, specifiedCharacterId, _, _ = specifyDiagnosis(
                        self._parent, newMKB, None, self._parent.itemId(),
                        self._parent.cmbSex.currentIndex(), age, date)
                    if not acceptable:
                        return False
                value = toVariant(specifiedMKB)
                result = CInDocTableModel.setData(self, index, value, role)
                if result and isNewItem:
                    self.setDefaultDates(row, column)
                return result
            elif column == self.getColIndex('startDate') and row > 0:
                prevItem = self.items()[row - 1]
                if forceDate(prevItem.value('endDate')) in self.defaultDate:
                    prevItem.setValue('endDate', value)
                    self.emitCellChanged(row - 1, self.getColIndex('endDate'))

            result = CInDocTableModel.setData(self, index, value, role)
            return result
        else:
            return True

    def flags(self, index):
        flags = CInDocTableModel.flags(self, index)
        row = index.row()
        column = index.column()
        if not self.isEditable() or (row == len(self.items())
                                     and column != self.getColIndex('MKB') and column != self.getColIndex('org_id')):
            flags &= (~ QtCore.Qt.ItemIsEditable)
        return flags


class MyLocItemDelegate(CLocItemDelegate):
    def eventFilter(self, obj, event):
        return QtGui.QStyledItemDelegate.eventFilter(self, obj, event)
