# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library                      import database
from library.crbcombobox          import CRBComboBox
from library.DateEdit             import CDateEdit
from library.DialogBase           import CConstructHelperMixin
from library.PreferencesMixin     import CDialogPreferencesMixin
from library.Utils                import forceDate, forceInt, forceRef, forceString, forceStringEx, getVal, addDots,\
                                         formatSex, formatSNILS

from Orgs.Orgs                    import selectOrganisation
from Orgs.Utils                   import getOrganisationShortName, getOrgStructureAddressIdList, \
                                         getOrgStructureDescendants, getOrgStructures

from Registry.RegistryTable       import CClientsTableModel
from Registry.Utils               import formatDocument, formatPolicy, CCheckNetMixin

from Users.Rights                 import urSeeStaff

from Ui_FindClientDialog          import Ui_FindClientDialog


class CFindClientWindow(QtGui.QDialog, Ui_FindClientDialog, CDialogPreferencesMixin, CCheckNetMixin, CConstructHelperMixin):
    u"""
        Окно для поиска пациентов с последующим их добавлением в фильтр ЖОС
    """

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        CCheckNetMixin.__init__(self)

        self.selectedClient = None

        self.addModels('Clients', CClientsTableModel(self))

        self.mnuGetClientId = QtGui.QMenu(self)

        self.mnuGetClientId.setObjectName('mnuGetClientId')
        self.actGetClientId = QtGui.QAction(u'''Добавить в фильтр ЖОС''', self)
        self.actGetClientId.setObjectName('actGetClientId')
        self.mnuGetClientId.addAction(self.actGetClientId)

        self.setObjectName('FindClientDialog')
        self.setupUi(self)
        self.setWindowTitle(u'Поиск пациента')

        self.setModels(self.tblClients, self.modelClients, self.selectionModelClients)

        self.cmbFilterDocumentType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.cmbFilterPolicyType.setTable('rbPolicyType', True)
        self.cmbFilterAttachType.setTable('rbAttachType', True)

        self.cmbFilterSocStatType.setTable('vrbSocStatusType', True)
        self.cmbFilterSocStatType.setShowFields(CRBComboBox.showNameAndCode)

        self.cmbFilterHurtType.setTable('rbHurtType', True)
        self.cmbFilterLocationCardType.setTable('rbLocationCardType', True)
        self.cmbFilterStatusObservationType.setTable('rbStatusObservationClientType', True)

        self.idValidator = CIdValidator(self)
        self.edtFilterId.setValidator(self.idValidator)
        self.edtFilterBirthDay.setHighlightRedDate(False)
        self.cmbFilterAddressStreet.setAddNone(True)
        self.chkListOnClientsPage = [
            (self.chkFilterId,        [self.edtFilterId,  self.cmbFilterAccountingSystem]),
            (self.chkFilterLastName,  [self.edtFilterLastName]),
            (self.chkFilterFirstName, [self.edtFilterFirstName]),
            (self.chkFilterPatrName,  [self.edtFilterPatrName]),
            (self.chkFilterBirthDay,  [self.edtFilterBirthDay]),
            (self.chkFilterSex,       [self.cmbFilterSex]),
            (self.chkFilterContact,   [self.edtFilterContact]),
            (self.chkFilterSNILS,     [self.edtFilterSNILS]),
            (self.chkFilterDocument,  [self.cmbFilterDocumentType,  self.edtFilterDocumentSerial, self.edtFilterDocumentNumber]),
            (self.chkFilterPolicy,    [self.cmbFilterPolicyType, self.cmbFilterPolicyInsurer, self.edtFilterPolicySerial, self.edtFilterPolicyNumber]),
            (self.chkFilterWorkOrganisation, [self.cmbWorkOrganisation, self.btnSelectWorkOrganisation]),
            (self.chkFilterHurtType, [self.cmbFilterHurtType]),
            (self.chkFilterSocStatuses, [self.cmbFilterSocStatClass, self.cmbFilterSocStatType]),
            (self.chkFilterLocationCardType, [self.cmbFilterLocationCardType]),
            (self.chkFilterStatusObservationType, [self.cmbFilterStatusObservationType]),
            (self.chkFilterCreatePerson, [self.cmbFilterCreatePerson]),
            (self.chkFilterCreateDate, [self.edtFilterBegCreateDate, self.edtFilterEndCreateDate]),
            (self.chkFilterModifyPerson, [self.cmbFilterModifyPerson]),
            (self.chkFilterModifyDate,[self.edtFilterBegModifyDate, self.edtFilterEndModifyDate]),
            (self.chkFilterEvent,     [self.chkFilterFirstEvent, self.edtFilterEventBegDate, self.edtFilterEventEndDate]),
            (self.chkFilterAge,       [self.edtFilterBegAge, self.cmbFilterBegAge, self.edtFilterEndAge, self.cmbFilterEndAge]),
            (self.chkFilterAddress,   [self.cmbFilterAddressType,
                                       self.cmbFilterAddressCity,
                                       self.cmbFilterAddressStreet,
                                       self.lblFilterAddressHouse, self.edtFilterAddressHouse,
                                       self.lblFilterAddressCorpus, self.edtFilterAddressCorpus,
                                       self.lblFilterAddressFlat, self.edtFilterAddressFlat,
                                       ]),
            (self.chkFilterAddressOrgStructure, [self.cmbFilterAddressOrgStructureType, self.cmbFilterAddressOrgStructure]),
            (self.chkFilterBeds, [self.cmbFilterStatusBeds, self.cmbFilterOrgStructureBeds]),
            (self.chkFilterAddressIsEmpty, []),
            (self.chkFilterAttachType, [self.cmbFilterAttachCategory, self.cmbFilterAttachType]),
            (self.chkFilterAttach,    [self.cmbFilterAttachOrganisation]),
            (self.chkFilterAttachNonBase, []),
            (self.chkFilterTempInvalid, [self.edtFilterBegTempInvalid, self.edtFilterEndTempInvalid]),
            (self.chkFilterRPFUnconfirmed, []),
            (self.chkFilterRPFConfirmed, [self.edtFilterBegRPFConfirmed, self.edtFilterEndRPFConfirmed]),
            ]

        self.cmbFilterAccountingSystem.setTable('rbAccountingSystem',  True)
        self.cmbFilterAccountingSystem.setValue(forceRef(getVal(
            QtGui.qApp.preferences.appPrefs, 'FilterAccountingSystem', 0)))

        self.RPFAccountingSystemId = forceRef(QtGui.qApp.db.translate('rbAccountingSystem', 'code', '1', 'id')) #FIXME: record code in code
        if not self.RPFAccountingSystemId:
            self.chkFilterRPFUnconfirmed.setEnabled(False)
            self.chkFilterRPFConfirmed.setEnabled(False)

        self.__filter = {}

        self.tblClients.setPopupMenu(self.mnuGetClientId)

        #self.connect(self.tblClients.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.onListBeforeRecordClientPopupMenuAboutToShow)

        self.loadDialogPreferences()
        self.cmbFilterAddressCity.setCode(QtGui.qApp.defaultKLADR())


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
        self.saveDialogPreferences()




    def focusClients(self):
        self.tblClients.setFocus(QtCore.Qt.TabFocusReason)


    def updateClientsList(self, filter, posToId=None):
        """
            в соответствии с фильтром обновляет список пациентов.
        """
        db = QtGui.qApp.db

        def calcBirthDate(cnt, unit):
            result = QtCore.QDate.currentDate()
            if unit == 3: # дни
                result = result.addDays(-cnt)
            elif unit == 2: # недели
                result = result.addDays(-cnt*7)
            elif unit == 1: # месяцы
                result = result.addMonths(-cnt)
            else: # года
                result = result.addYears(-cnt)
            return result

        def addAddressCond(cond, addrType, addrIdList):
            tableClientAddress = db.table('ClientAddress')
            subcond = [tableClientAddress['client_id'].eqEx('`Client`.`id`'),
                       tableClientAddress['id'].eqEx('(SELECT MAX(`id`) FROM `ClientAddress` AS `CA` WHERE `CA`.`client_id` = `Client`.`id` AND `CA`.`type`=%d)' % addrType)
                      ]
            if addrIdList == None:
                subcond.append(tableClientAddress['address_id'].isNull())
            else:
                subcond.append(tableClientAddress['address_id'].inlist(addrIdList))
            cond.append(db.existsStmt(tableClientAddress, subcond))


        def addAttachCond(cond, orgCond, attachCategory, attachTypeId):
            outerCond = ['ClientAttach.client_id = Client.id']
            innerCond = ['CA2.client_id = Client.id']
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
            if QtGui.qApp.hideAllLeavers() or QtGui.qApp.hideLeaversBeforeCurrentYearPatients():
                stmt = '''NOT EXISTS (SELECT ClientAttach.id
                   FROM ClientAttach
                   INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
                   WHERE rbAttachType.outcome != 0 AND ClientAttach.client_id=Client.id AND %s
                   )''' % ('NOT YEAR(ClientAttach.begDate)=YEAR(CURRENT_DATE)' if QtGui.qApp.hideLeaversBeforeCurrentYearPatients()
                                                                               else '1')
                cond.append(stmt) 
            

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.__filter = filter
            tableClient = db.table('Client')
            table = tableClient
            cond = [tableClient['deleted'].eq(0)]
            if 'id' in filter:
                accountingSystemId = filter.get('accountingSystemId',  None)
                if accountingSystemId:
                    tableIdentification = db.table('ClientIdentification')
                    table = table.leftJoin(tableIdentification, tableIdentification['client_id'].eq(tableClient['id']))
                    cond.append(tableIdentification['accountingSystem_id'].eq(accountingSystemId))
                    cond.append(tableIdentification['identifier'].eq(filter['id']))
                    cond.append(tableIdentification['deleted'].eq(0))
                else:
                    cond.append(tableClient['id'].eq(filter['id']))
            database.addCondLike(cond, tableClient['lastName'],  addDots(filter.get('lastName', '')))
            database.addCondLike(cond, tableClient['firstName'], addDots(filter.get('firstName', '')))
            database.addCondLike(cond, tableClient['patrName'],  addDots(filter.get('patrName', '')))
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
                table = table.innerJoin(tableEventTypePurpose, tableEventTypePurpose['id'].eq(tableEventType['purpose_id']))
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
                    cond.append('''NOT EXISTS(SELECT E.id FROM Event AS E WHERE E.client_id = Client.id AND Event.deleted = 0 AND DATE(E.setDate) < DATE(%s))'''%(db.formatDate(begDate)))
            if 'age' in filter:
                lowAge, highAge = filter['age']
                cond.append(tableClient['birthDate'].le(calcBirthDate(*lowAge)))
                cond.append(tableClient['birthDate'].ge(calcBirthDate(*highAge)))
            if 'sex' in filter:
                cond.append(tableClient['sex'].eq(filter['sex']))
            if 'SNILS' in filter:
                cond.append(tableClient['SNILS'].eq(filter['SNILS']))
            if 'contact' in filter:
                tableContact = db.table('ClientContact')
                table = table.leftJoin(tableContact, tableContact['client_id'].eq(tableClient['id']))
                cond.append(tableContact['deleted'].eq(0)),
                cond.append(tableContact['contact'].like(contactToLikeMask(filter['contact'])))
            doc = filter.get('doc', None)
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

            orgId = filter.get('orgId', None)
            hurtType = filter.get('hurtType', None)
            isSeparateStaff = QtGui.qApp.isSeparateStaffFromPatient()
            isOnlyStaff = filter.get('onlyStaff', False)
            if orgId or isSeparateStaff or hurtType:
                tableWork = db.table('ClientWork')
                joinCond = [ tableClient['id'].eq(tableWork['client_id']),
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
                #При указанном типе соц.статуса поиск по классу соц.статуса излишен
                cond.append(tableSocStat['socStatusType_id'].eq(socStatTypeId) if socStatTypeId
                            else tableSocStat['socStatusClass_id'].eq(socStatClassId))


            locationCardType = filter.get('locationCardType', None)
            if locationCardType:
                cond.append('''EXISTS(SELECT Client_LocationCard.id FROM Client_LocationCard WHERE Client_LocationCard.deleted = 0 AND Client_LocationCard.master_id = Client.id AND Client_LocationCard.locationCardType_id = %s)'''%(str(locationCardType)))
            statusObservationType = filter.get('statusObservationType', None)
            if statusObservationType:
                cond.append('''EXISTS(SELECT Client_StatusObservation.id FROM Client_StatusObservation WHERE Client_StatusObservation.deleted = 0 AND Client_StatusObservation.master_id = Client.id AND Client_StatusObservation.statusObservationType_id = %s)'''%(str(statusObservationType)))
            address = filter.get('address', None)
            if address:
                addrType, KLADRCode, KLADRStreetCode, house, corpus, flat = address
                tableClientAddress = db.table('ClientAddress')
                tableAddressHouse = db.table('AddressHouse')
                tableAddress = db.table('Address')
                table = table.leftJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
                table = table.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
                table = table.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))

                cond.append('ClientAddress.id = (SELECT MAX(CA.id) FROM ClientAddress AS CA WHERE CA.deleted=0 AND CA.type=%d AND CA.client_id=Client.id)' % addrType)
                if KLADRStreetCode:
                    cond.append(tableAddressHouse['KLADRStreetCode'].eq(KLADRStreetCode))
                if house:
                    cond.append( tableAddressHouse['number'].eq(house) )
                    cond.append( tableAddressHouse['corpus'].eq(corpus) )
                if flat:
                    cond.append( tableAddress['flat'].eq(flat) )
            elif 'addressOrgStructure' in filter:
                addrType, orgStructureId = filter['addressOrgStructure']
                addrIdList = None
                cond2 = []
                if (addrType+1) & 1:
                    addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 0, addrIdList)
                if (addrType+1) & 2:
                    if addrIdList is None:
                        addrIdList = getOrgStructureAddressIdList(orgStructureId)
                    addAddressCond(cond2, 1, addrIdList)
                if ((addrType+1) & 4):
                    if orgStructureId:
                        addAttachCond(cond2, 'orgStructure_id=%d'%orgStructureId, 1, None)
                    else:
                        addAttachCond(cond2, 'LPU_id=%d'%QtGui.qApp.currentOrgId(), 1, None)
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
                    addAttachCond(cond, 'LPU_id=%d'%attachOrgId, *filter.get('attachType', (0, None)))
                else:
                    pass # добавить - не имеет пост. прикрепления
            elif 'attachToNonBase' in filter:
                if 'attachType' in filter:
                    attachCategory, attachTypeId = filter['attachType']
                else:
                    attachCategory, attachTypeId = 0, None
                addAttachCond(cond, 'LPU_id!=%d'%QtGui.qApp.currentOrgId(), *filter.get('attachType', (0, None)))
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
                    condClientIdentification  = [ tableClientIdentification['client_id'].eq(tableClient['id']),
                                                  tableClientIdentification['accountingSystem_id'].eq(self.RPFAccountingSystemId),
                                                ]
                    cond.append('NOT '+db.existsStmt(tableClientIdentification, condClientIdentification))
                    cond.append(tableClientIdentification['deleted'].eq(0))
                elif 'RPFConfirmed' in filter: #atronah: РПФ - регистр периодов финансирования (согласно документаци ПО «ЕИС ОМС. ВМУ. АПУ. Учёт пациентов»)
                    begDate, endDate = filter['RPFConfirmed']
                    tableClientIdentification = db.table('ClientIdentification')
                    condClientIdentification  = [ tableClientIdentification['client_id'].eq(tableClient['id']),
                                                  tableClientIdentification['accountingSystem_id'].eq(self.RPFAccountingSystemId),
                                                ]
                    cond.append(tableClientIdentification['deleted'].eq(0))
                    if begDate and begDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].ge(begDate))
                    if endDate and endDate.isValid():
                        condClientIdentification.append(tableClientIdentification['checkDate'].le(endDate))
                    cond.append(db.existsStmt(tableClientIdentification, condClientIdentification))

            hideLeaversPatients(cond)
            clientsLimit = 250
            getIdList = db.getDistinctIdList if table != tableClient else db.getIdList
            #Если включена глобальная опция сокрытия сотрудников из общего списка
            if isSeparateStaff:
                onlyStaffCond = db.joinAnd([tableWork['org_id'].isNotNull(),
                                           tableWork['org_id'].eq(QtGui.qApp.currentOrgId())])
                #Сформировать условие для списка, включающего только пациентов (без сотрудников)
                onlyPatientCond = 'NOT (%s)' % onlyStaffCond

                idListStaff = getIdList(table,
                                        tableClient['id'].name(),
                                        cond + [onlyStaffCond],
                                        [tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name(), tableClient['birthDate'].name(), tableClient['id'].name()],
                                        limit=clientsLimit)
                idListPatient = getIdList(table,
                                          tableClient['id'].name(),
                                          cond + [onlyPatientCond],
                                          [tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name(), tableClient['birthDate'].name(), tableClient['id'].name()],
                                          limit=clientsLimit)
                if len(idListPatient) < clientsLimit:
                    patientCount = len(idListPatient)
                else:
                    patientCount = db.getDistinctCount(table, tableClient['id'].name(), cond + [onlyPatientCond])
                if len(idListPatient) < clientsLimit:
                    staffCount = len(idListPatient)
                else:
                    staffCount = db.getDistinctCount(table, tableClient['id'].name(), cond + [onlyStaffCond])

                if isOnlyStaff: #показывать только сотрудников
                    idList = idListStaff
                    clientCount = staffCount
                else: # показывать только пациентов, не относящихся к текущему ЛПУ
                    idList = idListPatient
                    clientCount = patientCount
            else: #Если отключено разделение на сотрудников и пациентов
                idList = getIdList(table,
                                   tableClient['id'].name(),
                                   cond,
                                   [tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name(), tableClient['birthDate'].name(), tableClient['id'].name()],
                                   limit=clientsLimit)
                if len(idList) < clientsLimit:
                    clientCount = len(idList)
                else:
                    getCount = db.getDistinctCount if table != tableClient else db.getCount
                    clientCount = getCount(table, tableClient['id'].name(), cond)

            tmplist = []
            self.tblClients.setIdList(idList, posToId, clientCount)
#            self.tabMain.setTabEnabled(1, bool(idList))
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        self.focusClients()
        self.updateClientsListRequest = False

        if not idList:
            # если поиск по id, включено разделение на сотрудников и пациентов и список сотрудников не пуст
            if isSeparateStaff and 'id' in filter and idListStaff:
                #если у текущего пользователя есть права на просмотр списка сотрудников
                if QtGui.qApp.userHasRight(urSeeStaff):
                    self.chkShowStaffOnly.setCheckState(QtCore.Qt.Checked) #переключиться в режим отображения сотрудников
                    self.on_buttonBoxClient_apply() #применить изменения режима
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
                                % (u' (возможно он является сотрудником)' if isSeparateStaff and not isOnlyStaff else u''),
                                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                QtGui.QMessageBox.Ok)
                if res == QtGui.QMessageBox.Ok:
                    self.editNewClient()
                    self.focusClients()


    def getClientFilterAsText(self):
        filter  = self.__filter
        resList = []
        convertFilterToTextItem(resList, filter, 'id',        u'Код пациента',  unicode)
        convertFilterToTextItem(resList, filter, 'lastName',  u'Фамилия')
        convertFilterToTextItem(resList, filter, 'firstName', u'Имя')
        convertFilterToTextItem(resList, filter, 'patrName',  u'Отчество')
        convertFilterToTextItem(resList, filter, 'birthDate', u'Дата рождения', forceString)
        convertFilterToTextItem(resList, filter, 'sex',       u'Пол',           formatSex)
        convertFilterToTextItem(resList, filter, 'SNILS',     u'СНИЛС',         formatSNILS)
        convertFilterToTextItem(resList, filter, 'doc',       u'документ',      lambda doc: formatDocument(doc[0], doc[1], doc[2]))
        convertFilterToTextItem(resList, filter, 'policy',    u'полис',         lambda policy: formatPolicy(policy[0], policy[1], policy[2]))
        convertFilterToTextItem(resList, filter, 'orgId',     u'занятость',     getOrganisationShortName)
        convertFilterToTextItem(resList, filter, 'addressIsEmpty', u'адрес',    lambda dummy: u'пуст')
        return '\n'.join([item[0]+u': '+item[1] for item in resList])


#    def showClientInfo(self, id):
#        """
#            показ информации о пациенте в панели наверху
#        """
#        if id:
#            self.txtClientInfoBrowser.setHtml(getClientBanner(id))
#        else :
#            self.txtClientInfoBrowser.setText('')
#        self.actEditClient.setEnabled(bool(id))
#        self.actEditLocationCard.setEnabled(bool(id))
#        self.actEditStatusObservationClient.setEnabled(bool(id))
#        QtGui.qApp.setCurrentClientId(id)


    def clientId(self, index):
        return self.tblClients.itemId(index)


    def selectedClientId(self):
        return self.tblClients.currentItemId()


    def selectedClientRecord(self):
        return self.tblClients.currentItem()


    def currentClientId(self):
        return QtGui.qApp.currentClientId()





    def findClient(self, clientId, clientRecord=None):
        self.tabMain.setCurrentIndex(0)
        if not clientRecord:
            db = QtGui.qApp.db
            clientRecord = db.getRecord('Client', 'lastName, firstName, patrName, sex, birthDate, SNILS', clientId)
        if clientRecord:
            filter = {}
            filter['id'] = clientId
            filter['accountingSystemId'] = None
            filter['lastName'] = forceString(clientRecord.value('lastName'))
            filter['firstName'] = forceString(clientRecord.value('firstName'))
            filter['patrName'] = forceString(clientRecord.value('patrName'))
            filter['sex'] = forceInt(clientRecord.value('sex'))
            filter['birthDate'] = forceDate(clientRecord.value('birthDate'))
            filter['SNILS'] = forceString(clientRecord.value('SNILS'))
            self.__filter = self.updateFilterWidgets(filter)
            if not self.__filter:
                self.__filter = self.updateFilterWidgets({'id': clientId, 'accountingSystemId':None}, True)
            self.updateClientsList(self.__filter, clientId)
            self.tabMain.setTabEnabled(1, True)




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
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'id', outFilter)
                intUpdateClientFilterRBComboBox(chk, s[1][1], filter, 'accountingSystemId', outFilter)
            elif chk == self.chkFilterLastName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'lastName', outFilter)
            elif chk == self.chkFilterFirstName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'firstName', outFilter)
            elif chk == self.chkFilterPatrName:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'patrName', outFilter)
            elif chk == self.chkFilterSex:
                value = intUpdateClientFilterComboBox(chk, s[1][0], filter, 'sex', outFilter)
            elif chk == self.chkFilterBirthDay:
                value = intUpdateClientFilterDateEdit(chk, s[1][0], filter, 'birthDate', outFilter)
            elif chk == self.chkFilterContact:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'contact', outFilter)
            elif chk == self.chkFilterSNILS:
                value = intUpdateClientFilterLineEdit(chk, s[1][0], filter, 'SNILS', outFilter)
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





#    @pyqtSlot(QModelIndex, QModelIndex)
#    def on_selectionModelClients_currentRowChanged(self, current, previous):
#        clientId = self.clientId(current)
#        self.showClientInfo(clientId)
#        self.tabMain.setTabEnabled(1, current.isValid())
#        self.updateQueue()


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblClients_doubleClicked(self, index):
        self.selectedClient = self.selectedClientId()
        self.close()
#        column = index.column()
#        if column == 12:
#            self.updateStatusObservationClient()
#        elif column == 13:
#            self.updateLocationCardType()
#        else:
#            self.editCurrentClient()
#        self.focusClients()


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


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)


    @QtCore.pyqtSlot(bool)
    def on_chkFilterAddress_clicked(self, checked):
        if self.chkFilterId.isChecked():
            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)
        if checked:
            self.setChkFilterChecked(self.chkFilterAddressOrgStructure, False)
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
            self.setChkFilterChecked(self.chkFilterAddress, False)
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


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBoxClient_clicked(self, button):
        buttonCode = self.buttonBoxClient.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBoxClient_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBoxClient_reset()


#    @pyqtSlot()
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
            tmp = forceStringEx(forceString(self.edtFilterSNILS.text()).replace('-','').replace(' ',''))
            filter['SNILS'] = tmp
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
            filter['event'] = ( self.chkFilterFirstEvent.isChecked(),
                                self.edtFilterEventBegDate.date(),
                                self.edtFilterEventEndDate.date() )
        if self.chkFilterAge.isChecked():
            filter['age'] = ((self.edtFilterBegAge.value(), self.cmbFilterBegAge.currentIndex()),
                             (self.edtFilterEndAge.value()+1, self.cmbFilterEndAge.currentIndex())
                            )
        if self.chkFilterAddress.isChecked():
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
        if self.chkFilterRPFUnconfirmed.isChecked(): #atronah: РПФ - регистр периодов финансирования (согласно документаци ПО «ЕИС ОМС. ВМУ. АПУ. Учёт пациентов»)
            filter['RPFUnconfirmed'] = True
        elif self.chkFilterRPFConfirmed.isChecked():
            filter['RPFConfirmed'] = (self.edtFilterBegRPFConfirmed.date(),
                                      self.edtFilterEndRPFConfirmed.date()
                                     )
        filter['onlyStaff'] = self.chkShowStaffOnly.isChecked()
        self.updateClientsList(filter)
        self.focusClients()

    @QtCore.pyqtSlot(int)
    def on_cmbFilterAttachCategory_currentIndexChanged(self, index):
        self.setupCmbFilterAttachTypeCategory(index)

#    @pyqtSlot()
    def on_buttonBoxClient_reset(self):
        for s in self.chkListOnClientsPage:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWdgets(s[1])
                chk.setChecked(False)


    @QtCore.pyqtSlot()
    def on_actGetClientId_triggered(self):
        self.selectedClient = self.selectedClientId()
        self.close()
# ===== :)


def findClient(parent):
    dialog = CFindClientWindow(parent)
    dialog.exec_()
    return dialog.selectedClientId()


def findClientRecord(parent):
    dialog = CFindClientWindow(parent)
    dialog.exec_()
    return dialog.selectedClientRecord()


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


def parseClientId(clientIdEx):
    if '.' in clientIdEx:
        miacCode, clientId = clientIdEx.split('.')
    else:
        miacCode, clientId = '', clientIdEx
    if miacCode:
        if forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')) != miacCode.strip():
            return -1
    return int(clientId)



def contactToLikeMask(contact):
    m = '...'
    result = m+m.join(contact.replace('-','').replace(' ','').replace('.',''))+m
    return result

