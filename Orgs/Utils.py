# -*- coding: utf-8 -*-

import re
from PyQt4 import QtGui

from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.Enum import CEnum
from library.PrintInfo import CInfo, CRBInfo
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, formatNameInt, \
    formatSex, formatShortNameInt, nameCase


def getOrganisationShortName(id):
    result = QtGui.qApp.db.translate('Organisation', 'id', id, 'shortName')
    if result:
        return forceString(result)
    else:
        return ''


def getOrganisationInfo(id):
    result = {}
    if id:
        db = QtGui.qApp.db
        table = db.table('Organisation')
        record = db.getRecord(table, '*', id)
        if record:
            result['id'] = id
            result['fullName'] = forceString(record.value('fullName'))
            result['shortName'] = forceString(record.value('shortName'))
            result['title'] = forceString(record.value('title'))
            result['INN'] = forceString(record.value('INN'))
            result['KPP'] = forceString(record.value('KPP'))
            result['OGRN'] = forceString(record.value('OGRN'))
            result['OKVED'] = forceString(record.value('OKVED'))
            result['infisCode'] = forceString(record.value('infisCode'))
    return result


def getOrganisationMainStaff(id):
    result = [None, None]
    if id:
        db = QtGui.qApp.db
        table = db.table('Organisation')
        record = db.getRecord(table, ['chief', 'accountant'], id)
        if record:
            result[0] = forceString(record.value('chief'))
            result[1] = forceString(record.value('accountant'))
    return result


def parseOKVEDList(str):
    return [forceStringEx(s) for s in str.replace(',', ';').replace('|', ';').split(';') if s != '']


def fixOKVED(code):
    db = QtGui.qApp.db
    table = db.table('rbOKVED')
    fixedCode = forceString(db.translate(table, 'code', code, 'code'))
    if fixedCode:
        return True, fixedCode
    partialCode = code
    while partialCode:
        fixedCode = forceString(db.translate(table, 'OKVED', partialCode, 'code'))
        if fixedCode:
            return True, fixedCode
        partialCode = partialCode[:-1]
    return False, code


def getOKVEDName(code):
    if code:
        db = QtGui.qApp.db
        table = db.table('rbOKVED')
        records = db.getRecordList(table, 'name', table['code'].eq(code))
        if records:
            return forceString(records[0].value(0))
        else:
            return u'{%s}' % code
    else:
        return u''


def advisePolicyType(insurerId, serial):
    # подобрать тип полиса по с.к. и серии
    db = QtGui.qApp.db
    table = db.table('Organisation_PolicySerial')
    record = db.getRecordEx(table, 'policyType_id',
                            [table['organisation_id'].eq(insurerId), table['serial'].eq(serial)]
                            )
    if record:
        return forceRef(record.value(0))
    else:
        return None


def getShortBankName(bankId):
    if bankId:
        db = QtGui.qApp.db
        bankRecord = db.getRecord('Bank', 'BIK, name', bankId)
        if bankRecord:
            return forceString(bankRecord.value('BIK')) + ' ' + forceString(bankRecord.value('name'))
        else:
            return '{%d}' % bankId
    return ''


def getBankFilials(BIK):
    # Список филиалов банка, имеющего данный БИК
    db = QtGui.qApp.db
    table = db.table('Bank')
    records = db.getRecordList(table, 'branchName', table['BIK'].eq(BIK))
    if records:
        return [record.value(0) for record in records]
    else:
        return []


def getAccountInfo(id):
    result = {}
    if id:
        db = QtGui.qApp.db
        table = db.table('Organisation_Account')
        record = db.getRecord(table, '*', id)
        result['id'] = id
        result['name'] = forceString(record.value('name'))
        result['notes'] = forceString(record.value('notes'))
        result['bank_id'] = forceRef(record.value('bank_id'))
        result['shortBankName'] = getShortBankName(result['bank_id'])
    return result


def getOrganisationParent(orgId):
    # найти самый верхний элемент в иерархии организаций
    db = QtGui.qApp.db
    table = db.table('Organisation')

    while orgId:
        headId = forceRef(db.translate(table, 'id', orgId, 'head_id'))
        if headId:
            orgId = headId
    return orgId


def getOrganisationDescendants(orgId):
    # найти все организации явл. "потомками" данной
    return QtGui.qApp.db.getDescendants('Organisation', 'head_id', orgId)


def getOrganisationCluster(orgId):
    # найти все родственные организации
    return getOrganisationDescendants(getOrganisationParent(orgId))


def getPersonInfo(id):
    result = {}
    if id:
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        record = db.getRecord(tablePerson, '*', id)
        if record:
            result['id'] = id

            result['code'] = forceString(record.value('code'))

            lastName = nameCase(forceString(record.value('lastName')))
            firstName = nameCase(forceString(record.value('firstName')))
            patrName = nameCase(forceString(record.value('patrName')))

            result['lastName'] = lastName
            result['firstName'] = firstName
            result['patrName'] = patrName
            result['fullName'] = formatNameInt(lastName, firstName, patrName)
            result['shortName'] = formatShortNameInt(lastName, firstName, patrName)

            result['orgStructure_id'] = forceRef(record.value('orgStructure_id'))
            result['post_id'] = forceRef(record.value('post_id'))
            result['postName'] = forceString(db.translate('rbPost', 'id', result['post_id'], 'name'))
            result['speciality_id'] = forceRef(record.value('speciality_id'))
            result['specialityName'] = forceString(db.translate('rbSpeciality', 'id', result['speciality_id'], 'name'))

            result['maritalStatus'] = forceInt(record.value('maritalStatus'))
            result['contactNumber'] = forceString(record.value('contactNumber'))
            result['regType'] = forceInt(record.value('regType'))
            result['regBegDate'] = forceDate(record.value('regBegDate'))
            result['regEndDate'] = forceDate(record.value('regEndDate'))
            result['isReservist'] = forceInt(record.value('isReservist'))
            result['employmentType'] = forceInt(record.value('employmentType'))
            result['occupationType'] = forceInt(record.value('occupationType'))
            result['citizenship_id'] = forceInt(record.value('citizenship_id'))
    return result


def getPersonChiefs(personId):
    # Список начальников сотрудника
    result = []
    if personId:
        db = QtGui.qApp.db
        stmt = '''
        SELECT Chief.id
        FROM Person
        INNER JOIN rbPost ON rbPost.id = Person.post_id
        INNER JOIN Person AS Chief ON Chief.orgStructure_id = Chief.orgStructure_id
        INNER JOIN rbPost AS rbChiefPost ON rbChiefPost.id = Chief.post_id
        WHERE Person.id = %d AND SUBSTR(rbChiefPost.code, 1, 1)  in ('1', '2') AND SUBSTR(rbChiefPost.code, 1, 1) <  SUBSTR(rbPost.code, 1, 1)''' % personId
        query = db.query(stmt)
        while query.next():
            result.append(forceRef(query.record().value(0)))
    return result


def findOrgStructuresByHouseAndFlat(houseId, flat, orgId, orgStructureId=None):
    if houseId:
        db = QtGui.qApp.db
        flatNum = 0
        flatNumFilter = re.compile(r'^(\d+)')
        flatNumPart = flatNumFilter.search(flat)
        if flatNumPart:
            flatNumText = flatNumPart.group(1)
            if flatNumText:
                flatNum = int(flatNumText)

        tableOrgStructure = db.table('OrgStructure')
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        table = tableOrgStructureAddress.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableOrgStructureAddress['master_id']))

        fir = db.joinAnd([tableOrgStructureAddress['firstFlat'].le(flatNum),
                          tableOrgStructureAddress['lastFlat'].ge(flatNum)])
        fre = tableOrgStructureAddress['lastFlat'].eq(0)
        cond = [tableOrgStructure['organisation_id'].eq(orgId),
                tableOrgStructureAddress['house_id'].eq(houseId),
                db.joinOr([fre, fir])
                ]
        if orgStructureId:
            cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        return db.getIdList(table, tableOrgStructureAddress['master_id'].name(), cond)
    return []


def findOrgStructuresByAddress(addressId, orgId, orgStructureId=None):
    if addressId:
        db = QtGui.qApp.db
        tableAddress = db.table('Address')
        record = db.getRecord(tableAddress, 'house_id, flat', addressId)
        houseId = record.value('house_id')
        flat = forceStringEx(record.value('flat'))
        return findOrgStructuresByHouseAndFlat(houseId, flat, orgId, orgStructureId)
    return []


def getOrgStructureName(orgStructureId):
    db = QtGui.qApp.db
    table = db.table('OrgStructure')
    return forceString(db.translate(table, 'id', orgStructureId, 'code'))


def getOrgStructureFullName(orgStructureId):
    db = QtGui.qApp.db
    table = db.table('OrgStructure')
    names = []
    ids = set()

    while orgStructureId:
        record = db.getRecord(table, 'code, parent_id', orgStructureId)
        if record:
            names.append(forceString(record.value('code')))
            orgStructureId = forceRef(record.value('parent_id'))
        else:
            orgStructureId = None
        if orgStructureId in ids:
            orgStructureId = None
        else:
            ids.add(orgStructureId)
    return '/'.join(reversed(names))


def getOrgStructureFullNameList(orgStructureIdList):
    db = QtGui.qApp.db
    table = db.table('OrgStructure')

    result = []
    for orgStructureId in orgStructureIdList:
        names = []
        ids = set()
        while orgStructureId:
            record = db.getRecord(table, 'code, parent_id', orgStructureId)
            if record:
                names.append(forceString(record.value('code')))
                orgStructureId = forceRef(record.value('parent_id'))
            else:
                orgStructureId = None
            if orgStructureId in ids:
                orgStructureId = None
            else:
                ids.add(orgStructureId)
        result.append('/'.join(reversed(names)))

    return ';\n'.join(result)


def getOrgStructureNetId(orgStructureId):
    if orgStructureId:
        db = QtGui.qApp.db
        stmt = 'SELECT getOrgStructureNetId(%d)' % orgStructureId
        query = db.query(stmt)
        if query.next():
            return forceRef(query.record().value(0))
    else:
        return None


def getOrgStructures(orgId):
    db = QtGui.qApp.db
    table = db.table('OrgStructure')
    return db.getIdList(table, where=table['organisation_id'].eq(orgId))


def getOrgStructureDescendants(orgStructureId):
    return QtGui.qApp.db.getDescendants('OrgStructure', 'parent_id', orgStructureId)


def getOrgStructurePersonIdList(orgStructureId):
    db = QtGui.qApp.db
    table = db.table('Person')
    orgStructureIdList = getOrgStructureDescendants(orgStructureId)
    return db.getIdList(table, where=table['orgStructure_id'].inlist(orgStructureIdList))


def getOrgStructureAddressIdList(orgStructureId):
    if orgStructureId:
        orgStructureIdList = getOrgStructureDescendants(orgStructureId)
    else:
        orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
    db = QtGui.qApp.db
    tableAddress = db.table('Address')
    tableOrgStructureAddress = db.table('OrgStructure_Address')
    table = tableAddress
    table = table.leftJoin(tableOrgStructureAddress, tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']))
    cond = db.joinOr([
        tableOrgStructureAddress['lastFlat'].eq(0),
        db.joinAnd([
            tableOrgStructureAddress['firstFlat'].le(tableAddress['flat']),
            tableOrgStructureAddress['lastFlat'].ge(tableAddress['flat']),
        ])
    ])
    cond = [tableOrgStructureAddress['master_id'].inlist(orgStructureIdList), cond]
    return db.getIdList(table, tableAddress['id'].name(), where=cond)


def getOrgStructureActionTypeIdList(orgStructureId, isIncludeChilds=False):
    result = []
    db = QtGui.qApp.db
    table = db.table('OrgStructure_ActionType')
    cond = [table['actionType_id'].isNotNull()]
    if isIncludeChilds:
        orgStructureIdListWithChilds = getOrgStructureDescendants(orgStructureId)
        cond.append(table['master_id'].inlist(orgStructureIdListWithChilds))
    else:
        cond.append(table['master_id'].eq(orgStructureId))
    result.extend(db.getIdList(table, 'actionType_id', cond))
    return result


def getOrgStructureActionTypeIdSet(orgStructureId):
    idSet = set()
    db = QtGui.qApp.db
    table = db.table('OrgStructure_ActionType')
    tableOrgStructure = db.table('OrgStructure')

    idList = getOrgStructureActionTypeIdList(orgStructureId, isIncludeChilds=QtGui.qApp.isShowActionsForChildOrgStructures())
    idSet |= set(idList)
    record = db.getRecord(tableOrgStructure, ['parent_id', 'inheritActionTypes'], orgStructureId)
    orgStructureId = forceRef(record.value(0)) if (record and forceBool(record.value(1))) else None
    while orgStructureId:
        idList = getOrgStructureActionTypeIdList(orgStructureId, False)
        idSet |= set(idList)
        record = db.getRecord(tableOrgStructure, ['parent_id', 'inheritActionTypes'], orgStructureId)
        orgStructureId = forceRef(record.value(0)) if (record and forceBool(record.value(1))) else None
    return idSet


def getActionTypesIdSetByClasses(classes):
    if not isinstance(classes, list):
        classes = [classes]
    db = QtGui.qApp.db
    table = db.table('ActionType')
    cond = [table['class'].inlist(classes)]
    return set(db.getDistinctIdList(table, where=cond))


def getTopParentIdForOrgStructure(orgStructureId):
    return QtGui.qApp.db.getTopParent(table='OrgStructure',
                                      idList=orgStructureId,
                                      groupCol='parent_id',
                                      maxLevels=32)


def getActionTypeOrgStructureIdList(actionTypeId, includeInheritance=False):
    db = QtGui.qApp.db
    table = db.table('OrgStructure_ActionType')
    tableOrgStructure = db.table('OrgStructure')

    resultIdList = db.getDistinctIdList(table.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(table['master_id'])),
                                        table['master_id'],
                                        [table['actionType_id'].eq(actionTypeId),
                                         tableOrgStructure['deleted'].eq(0)
                                         ]
                                        )
    if includeInheritance:
        resultIdSet = set(resultIdList)
        idSet = set(resultIdSet)
        while idSet:
            idList = db.getIdList(tableOrgStructure,
                                  'id',
                                  [tableOrgStructure['deleted'].eq(0),
                                   tableOrgStructure['master_id'].inlist(idSet),
                                   tableOrgStructure['inheritActionTypes'].eq(1),
                                   ]
                                  )
            idSet = set(idList) - resultIdSet
            resultIdList += list(idSet)
            resultIdSet |= idSet
    return resultIdList


class CSexAgeConstraint(object):
    def __init__(self):
        self.age = None
        self.sex = None

    def constrain(self):
        return bool(self.age or self.sex)

    def initBySimpleType(self, sex, age):
        self.sex = sex
        self.age = parseAgeSelector(age) if age else None

    def initByRecord(self, record):
        self.initBySimpleType(forceInt(record.value('sex')), forceStringEx(record.value('age')))

    def applicable(self, clientSex, clientAge):
        if self.sex and clientSex != self.sex:
            return False
        if self.age and not checkAgeSelector(self.age, clientAge):
            return False
        return True


class CNet(CSexAgeConstraint):
    def __init__(self, id):
        CSexAgeConstraint.__init__(self)
        db = QtGui.qApp.db
        table = db.table('rbNet')
        record = db.getRecord(table, '*', id)
        if record:
            self.initByRecord(record)
            self.code = forceString(record.value('code'))
            self.name = forceString(record.value('name'))
        else:
            self.code = None
            self.name = None


class COKFSInfo(CRBInfo):
    tableName = 'rbOKFS'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._ownership = forceInt(record.value('ownership'))

    def _initByNull(self):
        self._ownership = None

    ownership = property(lambda self: self.load()._ownership)


class COKPFInfo(CRBInfo):
    tableName = 'rbOKPF'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CNetInfo(CRBInfo):
    tableName = 'rbNet'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._sexCode = forceInt(record.value('sex'))
        self._age = forceString(record.value('age'))

    def _initByNull(self):
        self._sexCode = 0
        self._age = ''

    sexCode = property(lambda self: self.load()._sexCode)
    sex = property(lambda self: formatSex(self.load()._sexCode))
    age = property(lambda self: self.load()._age)


class COrgInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._fullName = ''
        self._shortName = ''
        self._title = ''
        self._net = None
        self._infisCode = ''
        self._miacCode = ''
        self._OKVED = ''
        self._INN = ''
        self._KPP = ''
        self._OGRN = ''
        self._OKATO = ''
        self._OKPF = None
        self._OKFS = None
        self._OKPO = ''
        self._FSS = ''
        self._region = ''
        self._address = ''
        self._chief = ''
        self._phone = ''
        self._accountant = ''
        self._notes = ''
        self._area = ''
        self._voluntaryServiceStop = ''
        self._compulsoryServiceStop = ''

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('Organisation', '*', self.id) if self.id else None
        if record:
            self._fullName = forceString(record.value('fullName'))
            self._shortName = forceString(record.value('shortName'))
            self._title = forceString(record.value('title'))
            self._net = self.getInstance(CNetInfo, record.value('net_id'))
            self._infisCode = forceString(record.value('infisCode'))
            self._miacCode = forceString(record.value('miacCode'))
            self._OKVED = forceString(record.value('OKVED'))
            self._INN = forceString(record.value('INN'))
            self._KPP = forceString(record.value('KPP'))
            self._OGRN = forceString(record.value('OGRN'))
            self._OKATO = forceString(record.value('OKATO'))
            self._OKPF = self.getInstance(COKPFInfo, forceRef(record.value('OKPF_id')))
            self._OKFS = self.getInstance(COKFSInfo, forceRef(record.value('OKFS_id')))
            self._OKPO = forceString(record.value('OKPO'))
            self._FSS = forceString(record.value('FSS'))
            self._region = forceString(record.value('region'))
            self._address = forceString(record.value('address'))
            self._chief = forceString(record.value('chief'))
            self._phone = forceString(record.value('phone'))
            self._accountant = forceString(record.value('accountant'))
            self._notes = forceString(record.value('notes'))
            self._voluntaryServiceStop = forceBool(record.value('voluntaryServiceStop'))
            self._compulsoryServiceStop = forceBool(record.value('compulsoryServiceStop'))
            areaKladr = forceString(record.value('area'))
            if areaKladr:
                areaRecord = db.getRecordEx('kladr.KLADR', 'NAME, SOCR', 'CODE = \'%s\'' % areaKladr)
                if areaRecord:
                    self._area = u' '.join((forceString(areaRecord.value('NAME')), forceString(areaRecord.value('SOCR'))))
            return True
        else:
            self._net = self.getInstance(CNetInfo, None)
            self._OKPF = self.getInstance(COKPFInfo, None)
            self._OKFS = self.getInstance(COKFSInfo, None)
            return False

    def __str__(self):
        return self.load()._shortName

    fullName = property(lambda self: self.load()._fullName)
    shortName = property(lambda self: self.load()._shortName)
    title = property(lambda self: self.load()._title)
    net = property(lambda self: self.load()._net)
    infisCode = property(lambda self: self.load()._infisCode)
    miacCode = property(lambda self: self.load()._miacCode)
    OKVED = property(lambda self: self.load()._OKVED)
    INN = property(lambda self: self.load()._INN)
    KPP = property(lambda self: self.load()._KPP)
    OGRN = property(lambda self: self.load()._OGRN)
    OKATO = property(lambda self: self.load()._OKATO)
    OKPF = property(lambda self: self.load()._OKPF)
    OKFS = property(lambda self: self.load()._OKFS)
    OKPO = property(lambda self: self.load()._OKPO)
    FSS = property(lambda self: self.load()._FSS)
    region = property(lambda self: self.load()._region)
    address = property(lambda self: self.load()._address)
    chief = property(lambda self: self.load()._chief)
    phone = property(lambda self: self.load()._phone)
    accountant = property(lambda self: self.load()._accountant)
    notes = property(lambda self: self.load()._notes)
    note = property(lambda self: self.load()._notes)
    area = property(lambda self: self.load()._area)
    voluntaryServiceStop = property(lambda self: self.load()._voluntaryServiceStop)
    compulsoryServiceStop = property(lambda self: self.load()._compulsoryServiceStop)


class COrgStructureInfo(CInfo):
    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id
        self._name = ''
        self._code = ''
        self._organisation = self.getInstance(COrgInfo, None)
        self._parent = None
        self._net = None
        self._chief = None
        self._headNurse = None
        self._address = None
        self._infisDepTypeCode = None
        self._infisInternalCode = None
        self._bookkeeperCode = None
        self._actionTypes = None

    def _load(self):
        from PersonInfo import CPersonInfo

        db = QtGui.qApp.db
        record = db.getRecord('OrgStructure', '*', self.id) if self.id else None
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            parentId = forceRef(record.value('parent_id'))
            self._parent = self.getInstance(COrgStructureInfo, parentId) if parentId else None
            organisationId = forceRef(record.value('organisation_id'))
            self._organisation = self.getInstance(COrgInfo, organisationId) if organisationId else None
            netId = forceRef(record.value('net_id'))
            self._net = self.getInstance(CNetInfo, netId) if netId else None
            self._chief = self.getInstance(CPersonInfo, forceRef(record.value('chief_id')))
            self._headNurse = self.getInstance(CPersonInfo, forceRef(record.value('headNurse_id')))
            self._infisInternalCode = forceString(record.value('infisInternalCode'))
            self._infisDepTypeCode = forceString(record.value('infisDepTypeCode'))
            self._bookkeeperCode = forceString(record.value('bookkeeperCode'))
            address = forceString(record.value('address'))
            if address:
                self._address = address
            return True
        else:
            return False

    def getNet(self):
        self.load()
        if self._net is None:
            if self._parent:
                self._net = self._parent.getNet()
            elif self._organisation:
                self._net = self._organisation.net
            else:
                self._net = self.getInstance(CNetInfo, None)
        return self._address

    def getFullName(self):
        return getOrgStructureFullName(self.id)

    def getAddress(self):
        self.load()
        if self._address is None:
            if self._parent:
                self._address = self._parent.getAddress()
            elif self._organisation:
                self._address = self._organisation.address
            else:
                self._address = ''
        return self._address

    def getActionTypes(self):
        if self._actionTypes is None:
            from Events.ActionInfo import CActionTypeInfoList
            self._actionTypes = CActionTypeInfoList()
            self._actionTypes.idList = list(getOrgStructureActionTypeIdSet(self.id))
        return self._actionTypes

    def __str__(self):
        return self.getFullName()

    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)
    organisation = property(lambda self: self.load()._organisation)
    parent = property(lambda self: self.load()._parent)
    net = property(getNet)
    chief = property(lambda self: self.load()._chief)
    headNurse = property(lambda self: self.load()._headNurse)
    infisInternalCode = property(lambda self: self.load()._infisInternalCode)
    infisDepTypeCode = property(lambda self: self.load()._infisDepTypeCode)
    bookkeeperCode = property(lambda self: self.load()._bookkeeperCode)
    fullName = property(getFullName)
    address = property(getAddress)
    actionTypes = property(getActionTypes)


class COrgStructureAreaInfo(CEnum):
    u""" Тип участка подразделения (OrgStructure.isArea) """
    No = 0
    Therapeutic = 1
    Pediatric = 2
    AntenatalClinic = 3
    GeneralPractice = 4
    Other = 5

    nameMap = {
        No             : u'Не является',
        Therapeutic    : u'Терапевтический',
        Pediatric      : u'Педиатрический',
        AntenatalClinic: u'Женская консультация',
        GeneralPractice: u'Общей практики',
        Other          : u'Прочий'
    }

class CAttachType(CEnum):
    u""" Тип прикрепления (rbAttachType.code) """
    Territorial = 1  # территориал/первичное
    Attached = 2  # прикреплённый/по заявлению
    # FirstVisit = 3  # для пер.осм.
    # AdditionalVisit = 4  # для доп.осм.
    # AdditionalDisp = 5  # для доп.дисп.
    # View = 6  # для наблюдения
    # Leaved = 7  # выбыл
    Dead = 8  # умер
    # Quota = 9  # Квота
    # AdmissionBirth = 10  # Для планового или экстренного приема родов
    # Refuse = 11  # Отказ пациента
    # Dismissal = 12  # Увольнение

    allAttached = (Territorial,
                   Attached)

    nameMap = {
        Territorial: u'Первичное',
        Attached   : u'По заявлению',

        Dead       : u'Умер'
    }

    _idMap = {}

    @classmethod
    def getAttachTypeId(cls, attachType):
        if attachType not in cls._idMap:
            cls._idMap[attachType] = forceRef(QtGui.qApp.db.translate('rbAttachType', 'code', str(attachType), 'id'))
        return cls._idMap.get(attachType)


class CAttachTypeInfo(CRBInfo): # Тип прикрепления
    tableName = 'rbAttachType'

    def _initByRecord(self, record):
        self._temporary = forceBool(record.value('temporary'))
        self._outcome = forceBool(record.value('outcome'))
        self._grp = forceInt(record.value('grp'))
        from Events.EventInfo import CFinanceInfo
        self._finance = self.getInstance(CFinanceInfo, forceRef(record.value('finance_id')))

    def _initByNull(self):
        self._temporary = None
        self._outcome = None
        self._grp = None
        from Events.EventInfo import CFinanceInfo
        self._financeType = self.getInstance(CFinanceInfo, None)

    temporary = property(lambda self: self.load()._temporary)
    outcome = property(lambda self: self.load()._outcome)
    grp = property(lambda self: self.load()._grp)
    finance = property(lambda self: self.load()._finance)


class CDetachmentReasonInfo(CRBInfo):  # Причина открепления
    tableName = 'rbDetachmentReason'


def getRealOrgStructureId():
    if QtGui.qApp.isHideActionsFromOtherTopOrgStructures():
        return getTopParentIdForOrgStructure(QtGui.qApp.userOrgStructureId)

    elif QtGui.qApp.currentOrgStructureId():
        return QtGui.qApp.currentOrgStructureId()

    elif QtGui.qApp.userSpecialityId:
        return QtGui.qApp.userOrgStructureId

    return None


def getAttachedCount(orgStructureId, withDescendants=True):
    return getDetailedAttachedCount(orgStructureId,
                                    [(None, None)],
                                    withDescendants)[0]


def getDetailedAttachedCount(orgStructureId, colDescr, withDescendants=True):
    u""" Кол-во прикрепленного населения у заданного подразделения
    :param orgStructureId: OrgStructure.id
    :param colDescr: list of (rbAttachType.code, ClientAttach.sentToTFOMS):
    :param withDescendants: с учетом дочерних подраздлений
    :return: кол-во прикрепленных с разбивкой пл colDescr
    :rtype: tuple
    """
    db = QtGui.qApp.db
    tableAttachType = db.table('rbAttachType')
    tableClient = db.table('Client')
    tableClientAttach = db.table('ClientAttach')

    table = tableClientAttach
    table = table.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
    table = table.innerJoin(tableClient, [tableClient['id'].eq(tableClientAttach['client_id']),
                                          tableClient['deleted'].eq(0)])
    cols = []
    for attachTypeCode, sentToTFOMS in colDescr:
        if attachTypeCode is not None:
            col = db.countIf(tableAttachType['code'].eq(attachTypeCode), tableClient['id'], distinct=True)
        elif sentToTFOMS is not None:
            col = db.countIf(tableClientAttach['sentToTFOMS'].eq(sentToTFOMS), tableClient['id'], distinct=True)
        else:
            col = db.count(tableClient['id'], distinct=True)
        cols.append(col)

    cond = [
        tableClientAttach['deleted'].eq(0),
        tableClientAttach['endDate'].isNull(),
        tableAttachType['code'].inlist([CAttachType.Territorial,
                                        CAttachType.Attached])
    ]
    if withDescendants:
        cond.append(tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tableClientAttach['orgStructure_id'].eq(orgStructureId))

    rec = db.getRecordEx(table, cols, cond)
    return tuple(forceInt(rec.value(idx)) for idx in xrange(len(cols))) if rec is not None else tuple([0] * len(cols))


def getOrganisationSections(orgId=None):
    u"""
    Список всех подразделений МО, являющихся участками, либо содержащих участки в своей структуре
    :param orgId: Organisation.id
    :return: [list of OrgStructure.id]
    """
    if orgId is None:
        orgId = QtGui.qApp.currentOrgId()

    db = QtGui.qApp.db
    tableOrgStructure = db.table('OrgStructure')
    cols = [
        tableOrgStructure['id'],
        db.func.getOrgStructurePath(tableOrgStructure['id']).alias('path')
    ]
    cond = [
        tableOrgStructure['organisation_id'].eq(orgId),
        tableOrgStructure['isArea'].ne(COrgStructureAreaInfo.No),
        tableOrgStructure['deleted'].eq(0),
    ]
    sections = set()
    for rec in db.iterRecordList(tableOrgStructure, cols, cond):
        sections.add(forceRef(rec.value('id')))
        path = forceString(rec.value('path'))
        if path:
            sections |= set(map(int, path.split('.')))
    return list(sections)


def getPersonAttachOrgStructureId(personId, date):
    db = QtGui.qApp.db
    tablePersonAttach = db.table('PersonAttach')
    cond = [
        tablePersonAttach['master_id'].eq(personId),
        tablePersonAttach['deleted'].eq(0),
        db.joinOr([tablePersonAttach['begDate'].isNull(),
                   tablePersonAttach['begDate'].dateLe(date)]),
        db.joinOr([tablePersonAttach['endDate'].isNull(),
                   tablePersonAttach['endDate'].dateGe(date)]),
        tablePersonAttach['orgStructure_id'].isNotNull()
    ]
    cols = [
        tablePersonAttach['orgStructure_id']
    ]
    order = [
        tablePersonAttach['id'].desc()
    ]
    rec = db.getRecordEx(tablePersonAttach, cols, cond, order)
    return forceRef(rec.value('orgStructure_id')) if rec is not None else None


def getPersonOrgStructureId(personId):
    db = QtGui.qApp.db
    return forceRef(db.translate('Person', 'id', personId, 'orgStructure_id'))


def getPersonOrgId(personId):
    db = QtGui.qApp.db
    return forceRef(db.translate('Person', 'id', personId, 'org_id'))


def getPersonOrgStructureOnDate(personId, date):
    return getPersonAttachOrgStructureId(personId, date) or \
           getPersonOrgStructureId(personId)


def getPersonSpecialityCategory(personId):
    if not personId: return None
    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tableSpeciality = db.table('rbSpeciality')

    table = tablePerson
    table = table.innerJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
    cols = [
        db.left(tableSpeciality['federalCode'], 1).alias('code')
    ]
    cond = [
        tablePerson['id'].eq(personId)
    ]
    rec = db.getRecordEx(table, cols, cond)
    return forceStringEx(rec.value('code')) if rec else None


def findPersonBySpecialityCategory(orgStructureId, code, excludePersonId=None):
    if not code: return []

    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tablePersonAttach = db.table('PersonAttach')
    tableSpeciality = db.table('rbSpeciality')

    table = tablePersonAttach
    table = table.innerJoin(tablePerson, tablePerson['id'].eq(tablePersonAttach['master_id']))
    table = table.innerJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))

    cond = [
        tablePersonAttach['orgStructure_id'].eq(orgStructureId),
        tablePersonAttach['deleted'].eq(0),
        tablePersonAttach['endDate'].isNull(),
        db.left(tableSpeciality['federalCode'], 1).eq(code)
    ]
    if excludePersonId is not None:
        cond.append(tablePersonAttach['master_id'].ne(excludePersonId))

    return db.getIdList(table, tablePerson['id'], cond)
