# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from library.dbfpy.dbf import *
from library.Utils     import *
from Registry.Utils    import getClientWork, formatWorkPlace, CCheckNetMixin
from Exchange.Utils    import getInfisCodes, getClientRepresentativeInfo
from Accounting.ServiceDetailCache import CServiceDetailCache
from Accounting.Utils  import CTariff
from KLADR.KLADRModel  import getExactCityName, getRegionName, getStreetNameParts

from Ui_ExportINFISOMSPage1 import Ui_ExportINFISOMSPage1
from Ui_ExportINFISOMSPage2 import Ui_ExportINFISOMSPage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number', accountId)
#            settleDate = forceDate(accountRecord.value('settleDate'))
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        number = forceString(accountRecord.value('number'))
    else:
        date = None
        number = ''
    return date, number, 'data'


def exportINFISOMS(widget, accountId, accountItemIdList):
    wizard = CExportINFISOMSWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportINFISOMSWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportINFISOMSPage1(self)
        self.page2 = CExportINFISOMSPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в ИнФИС')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date,  number, fileName = getAccountInfo(accountId)
        self.dbfFileName = fileName
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла "%s.dbf"' %(self.dbfFileName))


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('infisoms')
        return self.tmpDir


    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '.dbf')


    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportINFISOMSPage1(QtGui.QWizardPage, Ui_ExportINFISOMSPage1, CCheckNetMixin):
    mapDocTypeToINFIS = { '1' : '1', '14': '2', '3':'3', '2':'6', '5':'7', '6':'8', '16':'8' }
    mapDocTypeToINFISName = {'1':u'ПАСПОРТ РОССИИ', '3':u'СВИД О РОЖД','14':u'ПАСПОРТ СССР', None:u'др.док-т удост.личн.'}
    mapPolicyTypeToINFIS = {'1':u'т',  '2':u'п' }
    mapRelationTypeCodeToTNFIS = { '1':u'Родитель',  '2':u'Родитель',
#                                   '3':u'Опекун',    '4':u'Опекун',
#                                   '5':u'Попечитель',
#                                   None: u'Попечитель'
                                    None: u'Опекун'
                                 }

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')
        self.cmbRepresentativeOutRule.setCurrentIndex(forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'INFISOMSRepresentativeOutRule', 1)))

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.serviceDetailCache = CServiceDetailCache()
        self.profileCache = {}
        self.kindCache = {}
        self.typeCache = {}
        self.representativeInfoCache = {}


    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query


    def export(self):
        QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def exportInt(self):
        orgInfisCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
        representativeOutRule = self.cmbRepresentativeOutRule.currentIndex()
        dbf, query = self.prepareToExport()
        if self.idList:
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), orgInfisCode, representativeOutRule)
        else:
            self.progressBar.step()
        dbf.close()


    def createDbf(self):
        dbf = Dbf(self.wizard().getFullDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
                        ('RECIEVER','C',5),     # ИНФИС код подразделения
                        ('PAYER','C',5),        # Код СМО, выдавшей полис
                        ('TMO','C',5),          # Код ЛПУ
                        ('SURNAME','C',18),     # Фамилия пациента
                        ('NAME1','C',15),       # Имя пациента
                        ('NAME2','C',15),       # Отчество пациента
                        ('SEX','C',1),          # Пол (М/Ж)
                        ('AGE','N',3,0),        # Возраст (на какую дату?)
                        ('HSNET','C',1),        # "в"-взрослая/"д"-детская/"ж"-женская
                        ('STREET','C',5),       # Адрес пациента: код улицы
                        ('STREETYPE','C',2),    # Адрес пациента: тип улицы
                        ('AREA','C',3),         # Адрес пациента: код районa
                        ('HOUSE','C',7),        # Адрес пациента: номер дома
                        ('KORP','C',2),         # Адрес пациента: корпус
                        ('FLAT','N',4,0),       # Адрес пациента: номер квартиры
                        ('WHO','C',5),          # ИНФИС-код базового ЛПУ
                        ('ORDER','C',1),        # Код порядка направления
                        ('HSOBJECT','C',5),     # ИНФИС-код подразделения
                        ('DEPART','N',2,0),     # "внутренний код отделения"
                        ('PROFILENET','C',1),   # "в"-взрослая/"д"-детская
                        ('PROFILE','C',6),      # Код профиля лечения, код услуги, "ДСтац"
                        ('COMPLEXITY','C',1),   # -
                        ('DATEIN','D'),         # Дата начала услуги
                        ('DATEOUT','D'),        # Дата окончания услуги
                        ('AMOUNT','N',5,1),     # Объем лечения
                        ('OUTCOME','C',1),      # "код исхода лечения" ("в")
                        ('DIAGNOSIS','C',5),    # Код диагноза
                        ('DIAGNPREV','C',5),    # Код диагноза
                        ('HISTORY','C',9),      # eventId
                        ('REMARK','M'),         # !!!
#                        ('REMARK','C', 200),    #
                        ('BIRTHDAY','D'),       # Дата рождения
                        ('SUM','N',11,2),       # Сумма
                        ('CARDFLAGS','N',4,0),  # -
                        ('PROFTYPE','C',1),     # "код типа отделения" ("д")
                        ('POLIS_S','C',10),     # Серия полиса
                        ('POLIS_N','C',20),     # Номер полиса
                        ('POLIS_W','C',5),      # Код СМО, выдавшей полис
                        ('PIN','C',15),         # -
                        ('CARD_ID','C',8),      # -
                        ('INSURE_ID','C',8),    # -
                        ('INSURE_LOG','C',8),   # -
                        ('TYPER','C',1),        # -
                        ('IDQ','C',15),         # -
                        ('DATEQ','D'),          # -
                        ('TYPEQ','C',1),        # -
                        ('DATEREAL','D'),       # -
                        ('TYPEINS','C',1),      # - тип страхования (т - терр., п - произв.)
                        ('DATER','D'),          # -
                        ('TGROUP','C',2),       # Признак превышения предела количества по тарифу
                        ('SEND','L'),           # Флаг обработки записи
                        ('ERROR','C',15),       # Описание ошибки
                        ('TYPEDOC','C',1),      # Тип документа
                        ('SER1','C',10),        # Серия документа, левая часть
                        ('SER2','C',10),        # Серия документа, правая часть
                        ('NPASP','C',10),       # Номер документа
                        ('CHK','C',10),         #
                        ('ORDER_A','C', 1),     #
                        ('PROF79', 'C', 3),     # профиль лечения по классификатору профилей по 79 приказу
                        ('PRVS79', 'C', 6),     # код специальности врача по 79 приказу
                        ('VPOLIS', 'C', 1),     # вид полиса, региональный код
                        ('W_P',    'C', 1),     # пол представителя ребенка
                        ('DR_P',   'D', 8),     # день рождения представителя ребенка
                        ('SNILS',  'C', 14),    # СНИЛС
                        ('DS2',    'C', 5),     # диагноз сопутствующий
                        ('VIDPOM', 'C', 1),     # виды медицинской помощи (По умолчанию - 1, 2 - для событий с типом мед помощи 4 и 5, 3 - для Событий с типом мед.помощи 2 и 3)
                        ('RSLT',   'C', 3),     # результат обращения (Результат Обращения /События/: Региональный код)
                        ('IDSP',   'C', 3),     # способы оплаты медицинской помощи
                        ('MR',     'C', 100),   # место рождения
# ######### наши доп.поля:
                        ('ACC_ID',    'N',15,0),# id счета
                        ('ACCITEM_ID','N',15,0),# id элемента счета
                        ('CLIENT_ID', 'N',15,0),# id пациента
                        ('EVENT_ID',  'N',15,0),# id события
                        ('EXTERNALID','C',64),  # externalId события
                    )
        return dbf

    def createQuery(self):
        db = QtGui.qApp.db
        tableAccountItem = db.table('Account_Item')

        stmt = """
            SELECT
              Account_Item.id        AS accountItem_id,
              Account_Item.master_id AS account_id,
              Account_Item.event_id  AS event_id,
              Event.client_id        AS client_id,
              Event.externalId       AS externalId,
              Event.`order`          AS `order`,
              rbMedicalAidKind.code  AS medicalAidKindCode,
              rbMedicalAidType.code  AS medicalAidTypeCode,
              Client.lastName        AS lastName,
              Client.firstName       AS firstName,
              Client.patrName        AS patrName,
              Client.birthDate       AS birthDate,
              Client.sex             AS sex,
              Client.SNILS           AS SNILS,
              Client.birthPlace      AS birthPlace,
              ClientPolicy.serial    AS policySerial,
              ClientPolicy.number    AS policyNumber,
              ClientPolicy.begDate   AS policyBegDate,
              ClientPolicy.endDate   AS policyEndDate,
              Insurer.infisCode      AS policyInsurer,
              Insurer.fullName       AS policyInsurerName,
              Insurer.area           AS policyInsurerArea,
              rbPolicyType.code      AS policyType,
              rbPolicyKind.regionalCode AS policyKind,
              ClientDocument.serial  AS documentSerial,
              ClientDocument.number  AS documentNumber,
              rbDocumentType.code    AS documentType,
              rbDocumentType.regionalCode AS documentRegionalCode,
              AddressHouse.KLADRCode AS KLADRCode,
              AddressHouse.KLADRStreetCode AS KLADRStreetCode,
              AddressHouse.number    AS number,
              AddressHouse.corpus    AS corpus,
              Address.flat           AS flat,
              formatClientAddress(ClientAddress.id) as freeInput,
              IF(Account_Item.service_id IS NOT NULL,
                rbItemService.id,
                IF(Account_Item.visit_id IS NOT NULL, rbVisitService.id, rbEventService.id)
                ) AS service_id,
              Diagnosis.MKB          AS MKB,
              MKB_Tree.Prim               AS prim,
              Event.setDate          AS begDate,
              Event.execDate         AS endDate,
              Event.relegateOrg_id   AS relegateOrgId,
              IF(Event.relegateOrg_id IS NOT NULL, (SELECT Org.infisCode FROM Organisation AS Org WHERE Org.deleted = 0 AND Org.id = Event.relegateOrg_id LIMIT 1), NULL) AS relegateOrgInfisCode,
              IF(Event.client_id IS NOT NULL, %s, NULL) AS attachInfisCode,
              Account_Item.amount    AS amount,
              Account_Item.`sum`     AS `sum`,
              Account_Item.tariff_id AS tariff_id,
              rbMedicalAidUnit.regionalCode AS unitCode,
              rbDiagnosticResult.regionalCode AS rbDiagnosticResultCode,
              EventResult.federalCode AS eventResultCode,
              OrgStructure.infisCode,
              OrgStructure.infisInternalCode,
              OrgStructure.infisDepTypeCode,
              OrgStructure.infisTariffCode,
              Person.id              AS person_id,
              rbSpeciality.id        AS speciality_id,
              rbSpeciality.OKSOCode  AS OKSOCode,
              rbSpeciality.federalCode  AS specialityFederalCode
            FROM Account_Item
            LEFT JOIN Account ON Account.id = Account_Item.master_id
            LEFT JOIN Contract ON Contract.id = Account.contract_id
            LEFT JOIN rbFinance ON rbFinance.id = Contract.finance_id
            LEFT JOIN Action ON Action.id = Account_Item.action_id
            LEFT JOIN Visit  ON Visit.id  = Account_Item.visit_id
            LEFT JOIN Event  ON Event.id  = Account_Item.event_id
            LEFT JOIN Client ON Client.id = Event.client_id
            LEFT JOIN ClientPolicy ON ClientPolicy.id = getClientPolicyId(Client.id, rbFinance.code != '3')
            LEFT JOIN Organisation AS Insurer ON Insurer.id = ClientPolicy.insurer_id
            LEFT JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
            LEFT JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id
            LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
                      ClientDocument.id = (SELECT MAX(CD.id)
                                         FROM   ClientDocument AS CD
                                         LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                                         LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                                         WHERE  rbDTG.code = '1' AND CD.client_id = Client.id)
            LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
            LEFT JOIN ClientAddress ON ClientAddress.client_id = Client.id AND
                      ClientAddress.id = (SELECT MAX(CA.id)
                                         FROM   ClientAddress AS CA
                                         WHERE  CA.type = 0 AND CA.client_id = Client.id)
            LEFT JOIN Address      ON Address.id = ClientAddress.address_id
            LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id
            LEFT JOIN Person       ON Person.id = IF(Visit.person_id IS NOT NULL, Visit.person_id,
                                                     IF(Action.person_id IS NOT NULL, Action.person_id, Event.execPerson_id))

            LEFT JOIN Diagnostic ON Diagnostic.id = getEventDiagnostic(Event.id)
            LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
            LEFT JOIN MKB_Tree       ON MKB_Tree.DiagID = Diagnosis.MKB
            LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
            LEFT JOIN rbResult AS EventResult ON EventResult.id=Event.result_id
            LEFT JOIN EventType ON EventType.id = Event.eventType_id
            LEFT JOIN rbMedicalAidKind ON rbMedicalAidKind.id = EventType.medicalAidKind_id
            LEFT JOIN rbMedicalAidType ON rbMedicalAidType.id = EventType.medicalAidType_id
            LEFT JOIN rbService AS rbEventService ON rbEventService.id = EventType.service_id
            LEFT JOIN rbService AS rbVisitService ON rbVisitService.id = Visit.service_id
            LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
            LEFT JOIN rbPayRefuseType ON rbPayRefuseType.id = Account_Item.refuseType_id
            LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id
            LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
            LEFT JOIN rbService AS rbItemService ON rbItemService.id = Account_Item.service_id
            LEFT JOIN Contract_Tariff ON Contract_Tariff.id = Account_Item.tariff_id
            LEFT JOIN rbMedicalAidUnit ON rbMedicalAidUnit.id = Contract_Tariff.unit_id
            WHERE
                Account_Item.reexposeItem_id IS NULL
            AND (Account_Item.date IS NULL
                 OR (Account_Item.date IS NOT NULL AND rbPayRefuseType.rerun != 0)
                )
            AND %s
            ORDER BY Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.id
        """ % (self.getClientAttach(), tableAccountItem['id'].inlist(self.idList))
        query = db.query(stmt)
        return query


    def getClientAttach(self):
        return u'''(SELECT OrgAttach.infisCode
                    FROM Organisation AS OrgAttach
                    INNER JOIN ClientAttach ON ClientAttach.LPU_id = OrgAttach.id
                    INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
                    WHERE OrgAttach.deleted = 0
                    AND ClientAttach.deleted = 0
                    AND ClientAttach.client_id = Event.client_id
                    AND (rbAttachType.code = 1 OR rbAttachType.code = 2)
                    AND
                    ((Event.setDate IS NULL AND Event.execDate IS NULL)
                    OR
                    (ClientAttach.begDate IS NULL AND ClientAttach.endDate IS NULL)
                    OR
                    (Event.setDate IS NOT NULL
                    AND (
                    (ClientAttach.begDate IS NOT NULL AND ClientAttach.endDate IS NOT NULL
                    AND ((ClientAttach.begDate <= DATE(Event.setDate) AND ClientAttach.endDate > DATE(Event.setDate))
                    OR (ClientAttach.begDate >= DATE(Event.setDate) AND (Event.execDate IS NULL OR ClientAttach.begDate < DATE(Event.execDate)))))
                    OR (ClientAttach.begDate IS NOT NULL AND ClientAttach.endDate IS NULL
                    AND (Event.execDate IS NULL OR ClientAttach.begDate < DATE(Event.execDate)))
                    OR (ClientAttach.begDate IS NULL AND ClientAttach.endDate IS NOT NULL
                    AND (ClientAttach.endDate > DATE(Event.setDate)))
                    ))
                    OR
                    (Event.execDate IS NOT NULL
                    AND (
                    (ClientAttach.begDate IS NOT NULL AND ClientAttach.endDate IS NOT NULL
                    AND (((Event.setDate IS NULL OR ClientAttach.begDate <= DATE(Event.setDate)) AND ClientAttach.begDate < DATE(Event.execDate))
                    OR ((Event.setDate IS NULL OR ClientAttach.begDate >= DATE(Event.setDate)) AND (ClientAttach.begDate < DATE(Event.execDate)))))
                    OR (ClientAttach.begDate IS NOT NULL AND ClientAttach.endDate IS NULL AND ClientAttach.begDate < DATE(Event.execDate))
                    OR (ClientAttach.begDate IS NULL AND ClientAttach.endDate IS NOT NULL
                    AND (Event.setDate IS NULL OR ClientAttach.endDate > DATE(Event.setDate)))
                    )))
                    ORDER BY rbAttachType.code
                    LIMIT 1)'''


    def process(self, dbf, record, orgInfisCode, representativeOutRule):
        eventId  = forceInt(record.value('event_id'))
        externalId = forceString(record.value('externalId'))
        clientId = forceInt(record.value('client_id'))
        birthDate = forceDate(record.value('birthDate'))
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        relegateOrgId = forceRef(record.value('relegateOrgId'))
        relegateOrgInfisCode = forceString(record.value('relegateOrgInfisCode'))
        attachInfisCode = forceString(record.value('attachInfisCode'))
        orgStructureInfisCode = forceString(record.value('infisCode'))
        sex = forceInt(record.value('sex'))
        age = max(0, calcAgeInYears(birthDate, endDate))
        if age<18:
            net = u'д'
        else:
            personId = forceRef(record.value('person_id'))
            net = self.getPersonNet(personId)
            net = u'ж' if net and net.sex == 2 else u'в'
        mkb = MKBwithoutSubclassification(forceString(record.value('MKB')))
        if len(mkb) == 3:
            mkb += '.'
        specialityId = forceRef(record.value('speciality_id'))
        serviceId = forceRef(record.value('service_id'))
        serviceDetail = self.serviceDetailCache.get(serviceId)
        eventAidKindCode = forceString(record.value('medicalAidKindCode'))
        eventAidTypeCode = forceString(record.value('medicalAidTypeCode'))
        aidProfileFederalCode, serviceAidKindCode, serviceAidTypeCode = self.getAidCodes(serviceDetail, endDate, specialityId, birthDate, sex, mkb, True)
        aidKindCode = serviceAidKindCode or eventAidKindCode
        aidTypeCode = serviceAidTypeCode or eventAidTypeCode
        policyBegDate = forceDate(record.value('policyBegDate'))
        policyEndDate = forceDate(record.value('policyEndDate'))
        policyInsurer = forceString(record.value('policyInsurer'))
        policyInsurerArea = forceString(record.value('policyInsurerArea'))
        policyInsurerAreaIsSpb = policyInsurerArea.startswith('78') or not policyInsurerArea
        docType   = forceString(record.value('documentType'))
        documentRegionalCode = forceString(record.value('documentRegionalCode'))
        docSerial = forceStringEx(record.value('documentSerial'))
        docNumber = forceString(record.value('documentNumber'))
        KLADRCode = forceString(record.value('KLADRCode'))
        KLADRStreetCode = forceString(record.value('KLADRStreetCode'))
        number = forceString(record.value('number'))
        corpus = forceString(record.value('corpus'))
        flat   = forceString(record.value('flat'))
        area, region, npunkt, street, streettype = getInfisCodes(KLADRCode, KLADRStreetCode, number, corpus)
        if area == u'ЛО':
            area = u'Ф89' # ?
        proftype = forceStringEx(record.value('infisDepTypeCode'))
        if not proftype:
            if aidTypeCode in ('1', '2', '3'):
                proftype = u'г' if begDate < endDate else u'о'
            else:
                proftype = u'у'
        clientWork = getClientWork(clientId)
        representativeInfo = ( self.getClientRepresentativeInfo(clientId)
                               if age<=14 and (   representativeOutRule == 0
                                               or representativeOutRule == 1 and street == '*'
                                              )
                               else None
                             )
        if representativeInfo:
            popDocType = representativeInfo['documentTypeCode']
            popDocSerial = representativeInfo['serial']
            popDocNumber = representativeInfo['number']
        else:
            popDocType = docType
            popDocSerial = docSerial
            popDocNumber = docNumber

        memoList = ['\x11[DOPCARD]',
                            'SER_TYPE='+self.mapDocTypeToINFISName.get(popDocType, self.mapDocTypeToINFISName[None]),
                            'PASPORT_S='+popDocSerial,
                            'PASPORT_N='+popDocNumber,
                            'WorkType='+(u'Работ' if clientWork and age>=18 else u'НеРаб'),
                            'CodeCompany='+policyInsurer,
                            'Snils='+formatSNILS(forceString(record.value('SNILS'))),
                            'Vpolis='+(forceString(record.value('policyKind')) or '1')
                    ]

        if representativeInfo:
            memoList.append('_mtrpar_=Y')
            memoList.append('Parstatus='+representativeInfo['status'])
            memoList.append('W_p='+formatSex(representativeInfo['sex']).lower())
            memoList.append('Dr_p='+unicode(representativeInfo['birthDate'].toString('dd.MM.yy')))
            memoList.append('Parsurname='+representativeInfo['lastName'])
            memoList.append('Parname1='+representativeInfo['firstName'])
            memoList.append('Parname2='+representativeInfo['patrName'])
            memoList.append('Parname='+representativeInfo['lastName'] + ' '+ representativeInfo['firstName']+' '+representativeInfo['patrName'])
        else:
            memoList.append(u'Parstatus=Отсутствует')

        if street == '*':
            aidProfileCode = self.getAidCodes(serviceDetail, endDate, specialityId, birthDate, sex, mkb, False)[0]
            memoList.append('_mtr_=Y')
            if policyBegDate:
               memoList.append('Pol_begin='+unicode(policyBegDate.toString('dd.MM.yy')))
            if policyEndDate:
               memoList.append('Pol_end='+unicode(policyEndDate.toString('dd.MM.yy')))
            memoList.append('AreaInsure='+area)
            memoList.append('Company='+forceString(record.value('policyInsurerName')))
            memoList.append('Region='+region)
            memoList.append('MTRegion='+getRegionName(KLADRCode))
            memoList.append('F_Placename='+getExactCityName(KLADRCode))
            if KLADRStreetCode:
                streetName, streetType = getStreetNameParts(KLADRStreetCode)
            else:
                streetName = streetType = ''
            memoList.append('F_Street='+streetName)
            memoList.append('F_Streetype='+streetType)
            memoList.append('F_House='+number)
            memoList.append('F_Korp='+corpus)
            memoList.append('F_Flat='+flat)
            address = ' '.join(ai
                               for ai in (streetType, streetName,
                                          (u'д.'+number) if number else '',
                                          (u'к.'+corpus) if corpus else '',
                                          (u'кв.'+flat) if flat else ''
                                         ) if ai
                              )
            memoList.append('F_Address='+address)
            if age<=6:
                patStatus = u'Дошкольник'
            elif age<=13:
                patStatus = u'Ребенок до 14 лет'
            elif age<=17:
                patStatus = u'Студент/учащийся'
            else:
                patStatus = ''
            if clientWork:
                post = forceString(clientWork.value('post')).lower()
                if u'студ' in post or u'учащ' in post:
                    patStatus = u'Студент/учащийся'
            if patStatus:
                memoList.append('patStatus='+patStatus)
            if clientWork:
                memoList.append('Job='+formatWorkPlace(clientWork))

            OKSOCode = forceString(record.value('OKSOCode'))
            memoList.append('MedSpec='+OKSOCode.lstrip('0'))
            memoList.append('MTRProf='+ aidProfileCode)
        memoList.append('Vidpom='+aidKindCode)
        memoList.append('Rslt='+forceString(record.value('eventResultCode')))
        memoList.append('Idsp='+forceString(record.value('unitCode')))
        memoList.append('Prof79='+aidProfileFederalCode)
        memoList.append('Prvs79='+forceString(record.value('specialityFederalCode')))
        memoList.append('Ishod='+forceString(record.value('eventResultCode')))
        memoList.append('MTRPOLIS_N='+ forceString(record.value('policyNumber')))
        memoList.append('Pr_nov=0')
        serviceInfisCode = serviceDetail.infisCode
        memoList.append('Typecrd=%d' % (0 if len(serviceInfisCode)>=2 # см. #0003973 в мантисе.
                                             and serviceInfisCode[:2].isalpha()
                                             and serviceInfisCode[0].islower() # а про то - русские это буквы или нет речи не шло.
                                             and serviceInfisCode[1].isupper()
                                          else
                                        1
                                       )
                       )
        memoList.append('\x1A\x1A')
        memo = '\r\n'.join(memoList)

        dbfRecord = dbf.newRecord()

        dbfRecord['RECIEVER']= orgStructureInfisCode or orgInfisCode # ИНФИС код подразделения
#        dbfRecord['RECIEVER']= forceString(record.value('infisInternalCode'))  # Код подразделения
        dbfRecord['PAYER']   = policyInsurer if policyInsurerAreaIsSpb else u'кФонд'  # Код СМО, выдавшей полис
        dbfRecord['TMO']     = (attachInfisCode or orgInfisCode) if policyInsurerAreaIsSpb else u'кФонд' # ИНФИС-код организации прикрепления, если нет, то ИНФИС-код базового ЛПУ
        dbfRecord['SURNAME'] = nameCase(forceString(record.value('lastName')))  # Фамилия пациента
        dbfRecord['NAME1']   = nameCase(forceString(record.value('firstName'))) # Имя пациента
        dbfRecord['NAME2']   = nameCase(forceString(record.value('patrName')))  # Отчество пациента
        dbfRecord['SEX']     = formatSex(sex).lower()                           # Пол (м/ж)
        dbfRecord['AGE']     = age                                              # Возраст (на какую дату?)
        dbfRecord['BIRTHDAY']= pyDate(birthDate)                                # дата рождения
        dbfRecord['SNILS']   = formatSNILS(forceString(record.value('SNILS')))  # СНИЛС
        dbfRecord['MR']      = forceString(record.value('birthPlace'))          # место рождения
        dbfRecord['STREET']  = street                                           # Адрес пациента: код улицы
        dbfRecord['STREETYPE']= streettype if street != '*' else u''            # Адрес пациента: тип улицы
        dbfRecord['AREA']    = area                                             # Адрес пациента: код районa
        dbfRecord['HOUSE']   = number if street != '*' else u''                 # Адрес пациента: номер дома
        dbfRecord['KORP']    = corpus if street != '*' else u''                 # Адрес пациента: корпус
        dbfRecord['FLAT']    = forceInt(record.value('flat')) if street != '*' else 0 # Адрес пациента: номер квартиры
        dbfRecord['TYPEDOC'] = documentRegionalCode if documentRegionalCode else self.mapDocTypeToINFIS.get(docType, '5') # Тип документа
        docSeries = docSerial.split()
        dbfRecord['SER1']    = docSeries[0] if len(docSeries)>=1 else '' # Серия документа, левая часть
        dbfRecord['SER2']    = docSeries[1] if len(docSeries)>=2 else '' # Серия документа, правая часть
        dbfRecord['NPASP']   = docNumber # Номер документа
        dbfRecord['POLIS_S'] = forceString(record.value('policySerial'))      # Серия полиса
        dbfRecord['POLIS_N'] = forceString(record.value('policyNumber'))      # Номер полиса
        dbfRecord['POLIS_W'] = policyInsurer if policyInsurerAreaIsSpb else u'Проч' # Код СМО, выдавшей полис
        dbfRecord['TYPEINS'] = self.mapPolicyTypeToINFIS.get(forceString(record.value('policyType')), '')
        dbfRecord['VPOLIS']  = forceString(record.value('policyKind')) or '1'
        dbfRecord['HSNET']   = net                                              # Тип сети профиля (в - взрослая, д - детская)
        dbfRecord['WHO']     = relegateOrgInfisCode or orgInfisCode # ИНФИС-код организации направителя, если нет, то ИНФИС-код базового ЛПУ
        dbfRecord['ORDER']   = u'э' if forceInt(record.value('order')) == 2 else u'п'  # Признак экстренности случая лечения (если случай экстренный - принимает значение "э" или "Э")
        dbfRecord['HSOBJECT']= forceString(record.value('infisTariffCode'))     # ИНФИС-код подразделения
        dbfRecord['DEPART']  = forceInt(record.value('infisInternalCode'))      # "внутренний код отделения"
        dbfRecord['PROFILENET'] = net             # Тип сети профиля (в - взрослая, д - детская)
        dbfRecord['PROFILE'] = serviceDetail.infisCode # Код профиля лечения, код услуги, "ДСтац"
        dbfRecord['DATEIN']  = pyDate(begDate)    # Дата начала услуги
        dbfRecord['DATEOUT'] = pyDate(endDate)    # Дата окончания услуги
        dbfRecord['AMOUNT']  = forceDouble(record.value('amount')) # Объем лечения
        dbfRecord['SUM']     = forceDouble(record.value('sum')) # Сумма
        dbfRecord['OUTCOME']   = u'в'             # "код исхода лечения" ("в")
        dbfRecord['DIAGNOSIS'] = mkb              # Код диагноза
        dbfRecord['DIAGNPREV'] = mkb              # Код диагноза
        dbfRecord['VIDPOM']    = aidKindCode
        dbfRecord['PROF79']    = aidProfileFederalCode
        dbfRecord['PRVS79']    = forceString(record.value('specialityFederalCode'))
        dbfRecord['RSLT']      = forceString(record.value('eventResultCode'))
        dbfRecord['IDSP']      = forceString(record.value('unitCode'))
        dbfRecord['REMARK']    = memo
        dbfRecord['PROFTYPE']  = proftype              # "код типа отделения" ("д")
        dbfRecord['TGROUP']    = self.getTariffGroup(record) # Признак превышения предела количества по тарифу
        dbfRecord['HISTORY']   = str(eventId)          # eventId
        dbfRecord['SEND']      = False                 # Флаг обработки записи
        dbfRecord['ERROR']     = ''                    # Описание ошибки
#
        dbfRecord['ACC_ID']    = forceInt(record.value('account_id'))
        dbfRecord['ACCITEM_ID']= forceInt(record.value('accountItem_id'))
        dbfRecord['CLIENT_ID'] = clientId
        dbfRecord['EVENT_ID']  = eventId
        dbfRecord['EXTERNALID']= externalId
#------------------------------------
        dbfRecord.store()


    def getTariff(self, tariffId):
        result = self.tariffCache.get(tariffId, False)
        if result == False:
            result = None
            if tariffId:
                record = QtGui.qApp.db.getRecord('Contract_Tariff', '*', tariffId)
                if record:
                    result = CTariff(record)
            self.tariffCache[tariffId] = result
        return result


    def getTariffGroup(self, record):
        amount = forceDouble(record.value('amount'))
        tariffId = forceRef(record.value('tariff_id'))
        tariff = self.getTariff(tariffId)
        if tariff and tariff.limitationIsExceeded(amount):
            return u'кд'
        return ''


    def getAidCodes(self, serviceDetail, date, specialityId, birthDate, sex, mkb, federal):
        age = calcAgeTuple(birthDate, date)
        profileId, kindId, typeId = serviceDetail.getMedicalAidIds(specialityId, sex, age, mkb)
        if profileId:
            item = self.profileCache.get(profileId, None)
            if item is None:
                item = (forceString(QtGui.qApp.db.translate('rbMedicalAidProfile', 'id', profileId, 'federalCode')),
                        forceString(QtGui.qApp.db.translate('rbMedicalAidProfile', 'id', profileId, 'regionalCode'))
                       )
                self.profileCache[profileId] = item
            profileCode = item[0 if federal else 1]
        else:
            profileCode = '0'
        if kindId:
            kindCode = self.kindCache.get(typeId, None)
            if kindCode is None:
                kindCode = forceString(QtGui.qApp.db.translate('rbMedicalAidKind', 'id', kindId, 'code'))
                self.kindCache[kindId] = kindCode
        else:
            kindCode = ''
        if typeId:
            typeCode = self.typeCache.get(typeId, None)
            if typeCode is None:
                typeCode = forceString(QtGui.qApp.db.translate('rbMedicalAidType', 'id', typeId, 'code'))
                self.typeCache[typeId] = typeCode
        else:
            typeCode = ''
        return profileCode, kindCode, typeCode


    def getClientRepresentativeInfo(self, clientId):
        result = self.representativeInfoCache.get(clientId, None)
        if result is None:
            result = getClientRepresentativeInfo(clientId)
            if result:
                result['status'] = self.mapRelationTypeCodeToTNFIS.get(result['relationTypeCode'],
                                                                       self.mapRelationTypeCodeToTNFIS[None])
            self.representativeInfoCache[clientId] = result
        return result


    def isComplete(self):
        return self.done


    def validatePage(self):
        QtGui.qApp.preferences.appPrefs['INFISOMSRepresentativeOutRule'] = toVariant(self.cmbRepresentativeOutRule.currentIndex())
        return True


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


class CExportINFISOMSPage2(QtGui.QWizardPage, Ui_ExportINFISOMSPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'INFISOMSExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        src = self.wizard().getFullDbfFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
        success1, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        src = os.path.splitext(src)[0] + '.dbt'
        if os.path.exists(src):
            dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
            success2, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        else:
            success2 = True
        if success1 and success2:
            QtGui.qApp.preferences.appPrefs['INFISOMSExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()
            return True
        else:
            return False


    @QtCore.pyqtSlot(QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ИнФИС',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))
