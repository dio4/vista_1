# -*- coding: utf-8 -*-
import copy
from PyQt4 import QtCore, QtGui, QtSql

from library.AgeSelector import parseAgeSelector, checkAgeSelector
from library.Counter import getDocumentNumber
from library.DbEntityCache import CDbEntityCache
from library.PrintInfo import CInfo, CDateInfo, CTimeInfo, CRBInfo
from library.Utils import forceBool, forceDate, forceDateTime, forceDouble, forceInt, forceRef, forceString, \
    forceStringEx, toVariant, pyDate, smartDict, forceTr


#TODO:skkachaev: Скопировал из Events/Action.py. Вырезал все иморты не из library и порезал код. Не уверен, что файл полностью рабочий
#TODO:skkachaev: Создавал исключительно для возможности писать проперти в базу удобным способом. Пример использования в EMSTService.py
#TODO:skkachaev: Но лучше, конечно, выделить из Events/Action.py независимую от прочего проекта логику (в основном, зависимости тянутся
#TODO:skkachaev: из-за CPropEditor'a и прав), для того, чтобы ей можно было пользоваться в standalone вещах


def getRBCheckSum(tableName):
    query = QtGui.qApp.db.query('SELECT SUM(CRC32(CONCAT_WS(CHAR(127), id, code, name))) FROM %s' % tableName)
    if query.next():
        record = query.record()
        return record.value(0).toInt()[0]
    else:
        return 0


class CAbstractRBModelData(object):
    idxId = 0
    idxCode = 1
    idxName = 2
    idxFlatCode = 3
    idxRegionalCode = 4
    idxFederalCode = 5

    def __init__(self):
        self._buff = []
        self.__maxCodeLen = 0
        self.__mapIdToIndex = {}

    def clear(self):
        self._buff = []
        self.__maxCodeLen = 0
        self.__mapIdToIndex = {}

    def addItem(self, item_id, code, name, flatCode=u'', regionalCode=u'', federalCode=u''):
        self.__mapIdToIndex[item_id] = len(self._buff)
        self._buff.append((item_id, code, name, flatCode, regionalCode, federalCode))
        self.__maxCodeLen = max(self.__maxCodeLen, len(code))

    def getCount(self):
        return len(self._buff)

    def getFieldByIndex(self, index, fieldIdx):
        if index < 0:
            return None
        return self._buff[index][fieldIdx]

    def getId(self, index):
        return self.getFieldByIndex(index, self.idxId)

    def getCode(self, index):
        return self.getFieldByIndex(index, self.idxCode)

    def getFlatCode(self, index):
        return self.getFieldByIndex(index, self.idxFlatCode)

    def getRegionalCode(self, index):
        return self.getFieldByIndex(index, self.idxRegionalCode)

    def getFederalCode(self, index):
        return self.getFieldByIndex(index, self.idxFederalCode)

    def getName(self, index):
        return self._buff[index][2]

    def getIndexById(self, item_id):
        result = self.__mapIdToIndex.get(item_id, -1)
        if result < 0 and not item_id:
            result = self.__mapIdToIndex.get(None, -1)
        return result

    def getIndexByCode(self, code):
        for i, item in enumerate(self._buff):
            if item[1] == code:
                return i
        return -1

    def getIndexByFlatCode(self, flatCode):
        for i, item in enumerate(self._buff):
            if item[self.idxFlatCode] == flatCode:
                return i
        return -1

    def getIndexByName(self, name, isStrict=True):
        for i, item in enumerate(self._buff):
            if (isStrict and item[2] == name) or (not isStrict and name in item[2]):
                return i
        return -1

    def getNameById(self, item_id):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getName(index)
        return '{'+str(item_id) + '}'

    def getCodeById(self, item_id):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getCode(index)
        return '{'+str(item_id) + '}'

    def getIdByCode(self, code):
        index = self.getIndexByCode(code)
        return self.getId(index)

    def getIdByFlatCode(self, flatCode):
        index = self.getIndexByFlatCode(flatCode)
        return self.getId(index)

    def getAllCodes(self):
        codes = set()
        for item in self._buff:
            codes.add(item[1])
        return codes

    def getString(self, index, showFields):
        if showFields == 0:
            return self.getCode(index)
        elif showFields == 1:
            return self.getName(index)
        elif showFields == 2:
            return '%-*s|%s' % (self.__maxCodeLen, self.getCode(index), self.getName(index))
        else:
            return 'bad field %s' % showFields

    def getStringById(self, item_id, showFields):
        index = self.getIndexById(item_id)
        if index >= 0:
            return self.getString(index, showFields)
        return '{'+str(item_id) + '}'

    def getBuff(self):
        return self._buff


class CRBModelData(CAbstractRBModelData):
    """class for store data of ref book"""
    def __init__(self, tableName, addNone, filter, order, specialValues, group=''):
        CAbstractRBModelData.__init__(self)
        self._tableName = tableName
        self._addNone = addNone
        self._filter = filter
        self._order = order
        self._checkSum = None
        self._timestamp = None
        self._specialValues = specialValues
        self._notLoaded = True
        self._codeFieldName = 'code'
        self._group = group

    @property
    def codeFieldName(self):
        """
            Stores name of database table's field with code value.

        :rtype : string
        :return: field name for code column in database table.
        """
        return self._codeFieldName

    @codeFieldName.setter
    def codeFieldName(self, newFieldName):
        if newFieldName:
            self._codeFieldName = str(newFieldName)

    @property
    def group(self):
        """
            Stores name if grouping field
        :rtype  :   string
        :return :   grouping block value
        """
        return self._group

    @group.setter
    def group(self, newGroupValue):
        if newGroupValue:
            self._group = str(newGroupValue)

    def getCount(self):
        if self._notLoaded:
            self.load()
        return len(self._buff)

    def getId(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getId(self, index)

    def getIdByFlatCode(self, flatCode):
        idx = self.getIndexByFlatCode(flatCode)
        return self.getId(idx)

    def getCode(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getCode(self, index)

    def getFlatCode(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getFlatCode(self, index)

    def getName(self, index):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getName(self, index)

    def getIndexById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexById(self, itemId)

    def getIndexByCode(self, code):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByCode(self, code)

    def getIndexByFlatCode(self, flatCode):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByFlatCode(self, flatCode)

    def getIndexByName(self, name, isStrict=True):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getIndexByName(self, name, isStrict=isStrict)

    def getNameById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getNameById(self, itemId)

    def getCodeById(self, itemId):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getCodeById(self, itemId)

    def getString(self, index, showFields):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getString(self, index, showFields)

    def getStringById(self, itemId, showFields):
        if self._notLoaded:
            self.load()
        return CAbstractRBModelData.getStringById(self, itemId, showFields)

    def load(self):
        self.clear()
        if self._specialValues:
            for fakeId, fakeCode, name in self._specialValues:
                self.addItem(fakeId, fakeCode, name, u'')
        if self._addNone:
            self.addItem(None, '0', u'не задано')
        db = QtGui.qApp.db
        table = db.table(self._tableName)
        cols = ['id', self.codeFieldName, 'name']
        isExistsFlatCode = 'flatCode' in table.fieldsDict
        if isExistsFlatCode:
            cols.append('flatCode')
        if 'regionalCode' in table.fieldsDict:
            cols.append('regionalCode')
        if 'federalCode' in table.fieldsDict:
            cols.append('federalCode')

        recordList = db.getRecordList(table=table,
                                      cols=cols,
                                      where=self._filter,
                                      order=self._order if self._order else '%s, name' % self.codeFieldName,
                                      group=self._group)
        for record in recordList:
            itemId = forceRef(record.value('id'))
            code = forceString(record.value(self.codeFieldName))
            name = forceString(record.value('name'))
            flatCode = forceString(record.value('flatCode'))
            regionalCode = forceString(record.value('regionalCode'))
            federalCode = forceString(record.value('federalCode'))
            self.addItem(itemId, code, name, flatCode, regionalCode, federalCode)
        self._timestamp = QtCore.QDateTime().currentDateTime()
        self._checkSum = getRBCheckSum(self._tableName)
        self._notLoaded = False

    def isObsolete(self):
        if self._timestamp and self._timestamp.secsTo(QtCore.QDateTime().currentDateTime()) > randint(300, 600):  # magic
            checkSum = getRBCheckSum(self._tableName)
            return self._checkSum != checkSum
        else:
            return False

    def isLoaded(self):
        """
            Return loaded data status.

        :rtype : bool
        :return : True if data has been loaded, else False
        """
        return not self._notLoaded


class CRBModelDataCache(CDbEntityCache):
    mapTableToData = {}

    @classmethod
    def getData(cls, tableName, addNone=True, filter='', order=None, specialValues=None, needCache=True, codeFieldName=None, group=''):
        strTableName = unicode(tableName)
        if isinstance(specialValues, list):
            specialValues = tuple(specialValues)
        key = (strTableName, addNone, filter, order, specialValues, codeFieldName, group)
        result = cls.mapTableToData.get(key, None)
        if not result or result.isObsolete():
            result = CRBModelData(strTableName, addNone, filter, order, specialValues, group=group)
            result.codeFieldName = codeFieldName
            cls.connect()
            if needCache:
                cls.mapTableToData[key] = result
        return result

    @classmethod
    def reset(cls, tableName=None):
        if tableName:
            for key in cls.mapTableToData.keys():
                if key[0] == tableName:
                    del cls.mapTableToData[key]
        else:
            cls.mapTableToData.clear()

    @classmethod
    def purge(cls):
        cls.reset()


class CActionPropertyValueTypeRegistry(object):
    # вспомогательное средство для создания CActionPropertyValueType по имени/обл.определения
    nameList = []
    mapNameToValueType = {}
    cache = {}

    @classmethod
    def register(cls, type_):
        cls.nameList.append(type_.name)
        cls.mapNameToValueType[type_.name.lower()] = type_

    @classmethod
    def normTypeName(cls, name):
        type_ = cls.mapNameToValueType.get(name.lower(), None)
        if type_:
            return type_.name
        else:
            return name

    @classmethod
    def get(cls, typeName, domain, my_name):
        name = typeName.lower()
        key = (name, domain, my_name)
        if key in cls.cache:
            result = cls.cache[key]
        else:
            if (typeName == 'String'):
                result = cls.mapNameToValueType[name](domain, my_name)
            else:
                result = cls.mapNameToValueType[name](domain)
            cls.cache[key] = result
        return result


class CActionPropertyValueType(object):
    tableNamePrefix = 'ActionProperty_'
    prefferedHeight = 1
    prefferedHeightUnit = 1
    isCopyable = True
    isHtml = False

    def __init__(self, domain=None):
        self.domain = domain
        self.tableName = self.getTableName()

    def getTableName(self):
        return self.tableNamePrefix + self.name

    @staticmethod
    def convertPyValueToQVariant(value):
        return toVariant(value)

    @staticmethod
    def convertSpecialText(value):
        return value

    def getEditorClass(self):
        return self.CPropEditor

    def toText(self, v):
        return forceString(v)

    def toImage(self, v):
        return None

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getPresetValue(self):
        return None


class CDoubleActionPropertyValueType(CActionPropertyValueType):
    name = 'Double'
    variantType = QtCore.QVariant.Double

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDouble()[0]

    def toInfo(self, context, v):
        return v if v else 0.0

    def getEditorClass(self):
        return self.CPropEditor


class CIntegerActionPropertyValueType(CActionPropertyValueType):
    name = 'Integer'
    variantType = QtCore.QVariant.Int

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def getEditorClass(self):
        return self.CPropEditor

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceInt(value)

    def toInfo(self, context, v):
        return v if v else 0


class CStringActionPropertyValueType(CActionPropertyValueType):
    name = 'String'
    variantType = QtCore.QVariant.String

    class CComboBoxPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def __init__(self, domain, my_name):
        CActionPropertyValueType.__init__(self, domain)
        self.my_name = my_name

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getEditorClass(self):
        return self.CComboBoxPropEditor


class CBlankSerialActionPropertyValueType(CActionPropertyValueType):
    name = 'BlankSerial'
    variantType = QtCore.QVariant.String
    isCopyable = False

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v):
        return forceString(v)


class CBlankNumberActionPropertyValueType(CActionPropertyValueType):
    name = 'BlankNumber'
    variantType = QtCore.QVariant.String

    class CPlainPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getEditorClass(self):
        return self.CPlainPropEditor


class CArterialPressureActionPropertyValueType(CActionPropertyValueType):
    name = 'ArterialPressure'
    variantType = QtCore.QVariant.Int

    class CPlainPropEditor():
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getEditorClass(self):
        return self.CPlainPropEditor


class CTemperatureActionPropertyValueType(CActionPropertyValueType):
    name = 'Temperature'
    variantType = QtCore.QVariant.Double

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDouble()[0]

    def toInfo(self, context, v):
        return v if v else 0.0


class CPulseActionPropertyValueType(CActionPropertyValueType):
    name = 'Pulse'
    variantType = QtCore.QVariant.Int

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toInt()[0]

    def toInfo(self, context, v):
        return v if v else 0


class CDateActionPropertyValueType(CActionPropertyValueType):
    name = 'Date'
    variantType = QtCore.QVariant.Date

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDate()

    def toText(self, v):
        return forceString(v)

    def toInfo(self, context, v):
        return CDateInfo(v)


class CTimeActionPropertyValueType(CActionPropertyValueType):
    name = 'Time'
    variantType = QtCore.QVariant.Time

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toTime()

    def toText(self, v):
        return forceString(v)

    def toInfo(self, context, v):
        return CTimeInfo(v)


class CReferenceActionPropertyValueType(CActionPropertyValueType):
    name = 'Reference'
    variantType = QtCore.QVariant.Int

    class CRBInfoEx(CRBInfo):
        def __init__(self, context, tableName, itemId):
            CInfo.__init__(self, context)
            self.id = itemId
            self.tableName = tableName

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        result = v
        if v:
            result = forceString(QtGui.qApp.db.translate(self.domain, 'id', v, 'name'))
        return forceString(result)

    def toInfo(self, context, v):
        return CReferenceActionPropertyValueType.CRBInfoEx(context, self.domain, v)

    def getTableName(self):
        tableName = self.tableNamePrefix + self.domain
        if tableName.lower() not in (forceString(tableName).lower() for tableName in
                                     QtSql.QSqlDatabase.database(QtGui.qApp.connectionName).tables()):
            tableName = self.tableNamePrefix + self.name
        return tableName


class CPrescriptionDrugActionPropertyValueType(CReferenceActionPropertyValueType):
    name = 'PrescriptionDrug'

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass


class CTextActionPropertyValueType(CActionPropertyValueType):
    name = 'Text'
    variantType = QtCore.QVariant.String
    prefferedHeight = 10
    prefferedHeightUnit = 1

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    @staticmethod
    def convertSpecialText(value):
        return value.replace('<br>', '\n')

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CHtmlActionPropertyValueType(CActionPropertyValueType):
    name = 'Html'
    variantType = QtCore.QVariant.String
    prefferedHeight = 20
    prefferedHeightUnit = 1
    isHtml = True

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CConstructorActionPropertyValueType(CActionPropertyValueType):
    name = 'Constructor'
    prefferedHeight = 10
    prefferedHeightUnit = 1
    variantType = QtCore.QVariant.String

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId, typeEditable=True):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CComplaintsActionPropertyValueType(CActionPropertyValueType):
    name = u'Жалобы'
    prefferedHeight = 10
    prefferedHeightUnit = 1
    variantType = QtCore.QVariant.String

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CRLSActionPropertyValueType(CActionPropertyValueType):
    name = 'RLS'
    variantType = QtCore.QVariant.Int

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toInt()[0]

    def getTableName(self):
        return self.tableNamePrefix + CIntegerActionPropertyValueType.name

    def toText(self, v): pass

    def toInfo(self, context, v): pass


class COrganisationActionPropertyValueType(CActionPropertyValueType):
    name = 'Organisation'
    variantType = QtCore.QVariant.Int
    badDomain = u'Неверное описание области определения значения свойства действия типа Organisation:\n%(domain)s'
    badKey = u'Недопустимый ключ "%(key)s" в описание области определения значения свойства действия типа Organisation:\n%(domain)s'
    badValue = u'Недопустимое значение "%(val)s" ключа "%(key)s" в описание области определения значения свойства действия типа Organisation:\n%(domain)s'

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        self.rawDomain = domain
        self.domain = self.parseDomain(domain)

    def parseDomain(self, domain):
        isInsurer = None
        isHospital = None
        isMed = None
        netCodes = []
        for word in domain.split(','):
            if word:
                parts = word.split(':')
                if len(parts) == 1:
                    key, val = u'тип', parts[0].strip()
                elif len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()
                else:
                    raise ValueError, self.badDomain % locals()
                keylower = key.lower()
                vallower = val.lower()
                if keylower in [u'тип']:
                    if vallower in [u'смо']:
                        isInsurer = True
                    elif vallower in [u'стац', u'стационар']:
                        isHospital = True
                    elif vallower in [u'лпу']:
                        isMed = True
                    else:
                        raise ValueError, self.badValue % locals()
                elif keylower in [u'сеть']:
                    netCodes.append(val)
                else:
                    raise ValueError, self.badKey % locals()
        db = QtGui.qApp.db
        table = db.table('Organisation')
        cond = []
        if isInsurer:
            cond.append('isInsurer')
        if isHospital:
            cond.append('isMedical = 2')
        if isMed:
            cond.append(table['net_id'].isNotNull())
        if netCodes:
            tableNet = db.table('rbNet')
            contNet = [tableNet['code'].inlist(netCodes), tableNet['name'].inlist(netCodes)]
            netIdList = db.getIdList(tableNet, 'id', db.joinOr(contNet))
            cond.append(table['net_id'].inlist(netIdList))
        return db.joinAnd(cond)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v): pass

    def toInfo(self, context, v): pass


class COrgStructureActionPropertyValueType(CActionPropertyValueType):
    name = 'OrgStructure'
    variantType = QtCore.QVariant.Int
    emptyRootName = None
    badDomain = u'Неверное описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'
    badKey = u'Недопустимый ключ "%(key)s" в описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'
    badValue = u'Недопустимое значение "%(val)s" ключа "%(key)s" в описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        COrgStructureActionPropertyValueType.emptyRootName = None
        self.domain = self.parseDomain(domain)

    def parseDomain(self, domain):
        db = QtGui.qApp.db
        orgStructureType = None
        orgStructureTypeList = [u'амбулатория', u'стационар', u'скорая помощь', u'мобильная станция',
                                u'приемное отделение стационара', u'реанимация']
        netCodes = []
        orgStructureCode = ''
        orgStructureIdList = []
        orgStructureId = None
        isBeds = 0
        isStock = 0
        isFilter = False
        for word in domain.split(','):
            if word:
                parts = word.split(':')
                if len(parts) == 1:
                    key = parts[0].strip()
                    val = None
                elif len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()
                else:
                    raise ValueError, self.badDomain % locals()
                keylower = key.lower()
                vallower = val.lower() if val else ''
                if keylower in [u'код']:
                    orgStructureCode = vallower
                elif keylower in [u'тип']:
                    if vallower in orgStructureTypeList:
                        orgStructureType = orgStructureTypeList.index(vallower)
                    else:
                        raise ValueError, self.badValue % locals()
                elif keylower in [u'сеть']:
                    netCodes.append(val)
                elif keylower in [u'имеет койки']:
                    isBeds = 1
                elif keylower in [u'имеет склад']:
                    isStock = 1
                else:
                    raise ValueError, self.badKey % locals()
        db = QtGui.qApp.db
        table = db.table('OrgStructure')
        cond = []
        if isBeds:
            cond.append(table['hasHospitalBeds'].eq(isBeds))
            isFilter = True
        if isStock:
            cond.append(table['hasStocks'].eq(isStock))
            isFilter = True
        if orgStructureType != None:
            cond.append(table['type'].eq(orgStructureType))
            isFilter = True
        if orgStructureCode:
            isFilter = True
            record = db.getRecordEx(table, [table['id'], table['code']],
                                    [table['deleted'].eq(0), table['code'].like(orgStructureCode)])
            if record:
                orgStructureId = forceRef(record.value('id'))
                COrgStructureActionPropertyValueType.emptyRootName = orgStructureId
                if orgStructureId:
                    orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
                    if orgStructureIdList:
                        cond.append(table['id'].inlist(orgStructureIdList))
        if netCodes:
            isFilter = True
            tableNet = db.table('rbNet')
            contNet = [tableNet['code'].inlist(netCodes), tableNet['name'].inlist(netCodes)]
            netIdList = db.getIdList(tableNet, 'id', db.joinOr(contNet))
            cond.append(table['net_id'].inlist(netIdList))
        cond.append(table['deleted'].eq(0))
        return cond

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v): pass

    def toInfo(self, context, v): pass


class CHospitalBedActionPropertyValueType(CActionPropertyValueType):
    name = 'HospitalBed'
    variantType = QtCore.QVariant.Int
    isCopyable = False

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v):
        return forceString(QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', v, 'CONCAT(code,\' | \',name)'))

    def toInfo(self, context, v):
        from HospitalBeds.HospitalBedInfo import CHospitalBedInfo
        return context.getInstance(CHospitalBedInfo, forceRef(v))


class CHospitalBedProfileActionPropertyValueType(CActionPropertyValueType):
    name = 'rbHospitalBedProfile'
    variantType = QtCore.QVariant.String

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def toText(self, v):
        result = v
        if v:
            result = forceString(QtGui.qApp.db.translate(self.domain, 'id', v, 'concat(code, \' | \', name)'))
        return forceString(result)

    def toInfo(self, context, v):
        from HospitalBeds.HospitalBedInfo import CHospitalBedProfileInfo
        return context.getInstance(CHospitalBedProfileInfo, forceRef(v))


class CPersonActionPropertyValueType(CActionPropertyValueType):
    name = 'Person'
    variantType = QtCore.QVariant.Int

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v): pass

    def toInfo(self, context, v): pass


class CImageActionPropertyValueType(CActionPropertyValueType):
    name = 'Image'
    variantType = QtCore.QVariant.Map
    prefferedHeight = 64
    prefferedHeightUnit = 0

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        if value.type() == QtCore.QVariant.ByteArray:
            byteArray = value.toByteArray()
            if byteArray:
                image = QtGui.QImage()
                if image.loadFromData(byteArray):
                    return image
                else:
                    return None
        elif value.type() == QtCore.QVariant.Image:
            image = QtGui.QImage(value)
            return image
        return None

    @staticmethod
    def convertPyValueToQVariant(value):
        if value:
            byteArray = QtCore.QByteArray()
            buf = QtCore.QBuffer(byteArray)
            buf.open(QtCore.QIODevice.WriteOnly)
            value.save(buf, 'JPG')
            buf.close()
            return QtCore.QVariant(byteArray)
        return None

    def toText(self, v):
        pass
        return ''

    def toImage(self, v):
        if v:
            if v.height() > self.prefferedHeight:
                return v.scaledToHeight(self.prefferedHeight, QtCore.Qt.FastTransformation)
        return v

    def toInfo(self, context, v):
        pass
        return None


# FIXME: raipc. Я не знаю, что такое PacsImages. Нужно уточнить.
class CPacsImagesActionPropertyValueType(CImageActionPropertyValueType):
    name = "PacsImages"


class CImageMapActionPropertyValueType(CActionPropertyValueType):
    name = "ImageMap"
    variantType = QtCore.QVariant.ByteArray
    prefferedHeight = 64
    prefferedHeightUnit = 0
    domain = None
    imgValue = None

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def __init__(self, domain=None):
        super(CImageMapActionPropertyValueType, self).__init__(domain)
        self.tableName = self.getTableName()
        self.domain = domain

        value = self.getValueFromDomain()
        if value:
            self.imgValue = self.convertDBImageToPyValue(value)

    def getValueFromDomain(self):
        db = QtGui.qApp.db
        where = 'code=\'%s\'' % self.domain
        record = db.getRecordEx('rbImageMap', 'image', where)
        return record.value('image')

    def getTableName(self):
        return self.tableNamePrefix + 'ImageMap'

    def convertDBImageToPyValue(self, value):
        if value.type() == QtCore.QVariant.ByteArray:
            byteArray = value.toByteArray()
            if byteArray:
                image = QtGui.QImage()
                if image.loadFromData(byteArray):
                    return image
                else:
                    return None
        return None

    @staticmethod
    def convertQVariantToPyValue(value):
        if type(value) == QtCore.QVariant:
            if value.type() == QtCore.QVariant.String:
                stringValue = value.toString()
                return stringValue
        elif isinstance(value, basestring):
            return value
        return None

    @staticmethod
    def convertPyValueToQVariant(value):
        if value:
            return QtCore.QVariant(value)
        return None

    def toText(self, v):
        pass
        return ''

    def toImage(self, v):
        v = self.imgValue
        if v:
            if v.height() > self.prefferedHeight:
                return v.scaledToHeight(self.prefferedHeight, QtCore.Qt.FastTransformation)
        return v

    def toInfo(self, context, v):
        pass
        return None


class CJobTicketActionPropertyValueType(CActionPropertyValueType):
    name = 'JobTicket'
    variantType = QtCore.QVariant.Int
    isCopyable = True

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        self._presetValueAllowed = False
        if domain:
            domain = domain.split(';')
            if len(domain) > 1:
                self._presetValueAllowed = forceStringEx(domain[1]).lower() in ['a', u'а']  # en & ru
            self.domain = forceStringEx(domain[0])

    class CPropEditor(object):
        def __init__(self, actionList, domain, parent, clientId):
            pass

    def getPresetValue(self):
        if self._presetValueAllowed:
            jobTypeCode = forceStringEx(self.domain)
            if jobTypeCode:
                data = CRBModelDataCache.getData('rbJobType')
                jobTypeId = data.getIdByCode(jobTypeCode)
                if jobTypeId:
                    jobTypeIdList = QtGui.qApp.db.getDescendants('rbJobType', 'group_id', jobTypeId)
                    if len(jobTypeIdList) == 1 and jobTypeIdList[0] == jobTypeId:
                        return self.getClientPresetJobTicketId(jobTypeId)
        return CActionPropertyValueType.getPresetValue(self)

    def getClientPresetJobTicketId(self, jobTypeId):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyJobTicket = db.table('ActionProperty_Job_Ticket')
        tableJobTicket = db.table('Job_Ticket')
        tableJob = db.table('Job')

        queryTable = tableEvent.innerJoin(tableAction,
                                          tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableActionProperty,
                                          tableActionProperty['action_id'].eq(tableAction['id']))
        queryTable = queryTable.innerJoin(tableActionPropertyJobTicket,
                                          tableActionPropertyJobTicket['id'].eq(tableActionProperty['id']))
        queryTable = queryTable.innerJoin(tableJobTicket,
                                          tableJobTicket['id'].eq(tableActionPropertyJobTicket['value']))
        queryTable = queryTable.innerJoin(tableJob,
                                          tableJob['id'].eq(tableJobTicket['master_id']))

        cond = [tableJob['jobType_id'].eq(jobTypeId),
                tableJobTicket['endDateTime'].isNull()]

        duration = forceInt(db.translate('rbJobType', 'id', jobTypeId, 'ticketDuration'))

        notValidDatetimeCond = 'DATE(DATE_ADD(Job_Ticket.`datetime`, INTERVAL %d DAY)) = CURRENT_DATE()' % duration

        jobTicketIdList = db.getDistinctIdList(queryTable,
                                               tableJobTicket['id'].name(),
                                               cond + [tableEvent['client_id'].eq(QtGui.qApp.currentClientId()),
                                                       tableJobTicket['status'].inlist([0, 1]),
                                                       notValidDatetimeCond],
                                               tableJobTicket['id'].name())

        for jobTicketId in jobTicketIdList:
            QtGui.qApp.addJobTicketReservation(jobTicketId, QtGui.qApp.userId)
            return jobTicketId

        jobTicketIdListDenied = db.getDistinctIdList(queryTable,
                                                     tableJobTicket['id'].name(),
                                                     cond + [tableEvent['client_id'].ne(QtGui.qApp.currentClientId()),
                                                             tableJobTicket['status'].eq(0)])

        queryTable = tableJob.innerJoin(tableJobTicket,
                                        tableJobTicket['master_id'].eq(tableJob['id']))

        cond = [tableJob['jobType_id'].eq(jobTypeId),
                tableJobTicket['datetime'].dateEq(QtCore.QDate.currentDate()),
                'NOT isReservedJobTicket(Job_Ticket.`id`)',
                tableJobTicket['status'].eq(0)]

        if jobTicketIdListDenied:
            cond.append(tableJobTicket['id'].notInlist(jobTicketIdListDenied))

        record = db.getRecordEx(queryTable, tableJobTicket['id'].name(), cond, tableJobTicket['id'].name())
        if record:
            jobTicketId = forceRef(record.value('id'))
            QtGui.qApp.addJobTicketReservation(jobTicketId, QtGui.qApp.userId)
            return jobTicketId

        return None

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    @staticmethod
    def convertQVariantListToListPyValues(values):
        return [forceRef(x) for x in values]

    def getTableName(self):
        return self.tableNamePrefix + 'Job_Ticket'

    def toText(self, v): pass

    def toInfo(self, context, v): pass


class CSamplingActionPropertyValueType(CActionPropertyValueType):
    name = u'Проба'
    variantType = QtCore.QVariant.String

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getEditorClass(self):
        return self.CPropEditor


class CToothActionPropertyValueType(CActionPropertyValueType):
    name = u'Зуб'
    variantType = QtCore.QVariant.String

    class CTextEditPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getEditorClass(self):
        return self.CTextEditPropEditor


class CCounterActionPropertyValueType(CActionPropertyValueType):
    name = u'Счетчик'
    variantType = QtCore.QVariant.String

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getCounterValue(self):
        counterId = self.getCounterId()
        value = None
        if counterId:
            clientId = QtGui.qApp.currentClientId()
            value = getDocumentNumber(clientId, counterId)
        return value

    def getCounterId(self):
        domain = self.domain
        if not domain:
            return None
        return forceRef(QtGui.qApp.db.translate('rbCounter', 'code', domain, 'id'))

    def getEditorClass(self):
        return self.CPropEditor

    def getPresetValue(self):
        value = self.getCounterValue()
        return value


class CClientQuotingActionPropertyValueType(CActionPropertyValueType):
    mapIdToName = {}
    name = u'Квота пациента'
    variantType = QtCore.QVariant.Int
    isObsolete = False

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def getEditorClass(self):
        return self.CPropEditor

    def getTableName(self):
        return self.tableNamePrefix + 'Client_Quoting'

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        v = forceRef(v)
        name = ''
        if v:
            db = QtGui.qApp.db
            quotaTypeId = forceRef(db.translate('Client_Quoting', 'id', v, 'quotaType_id'))
            name = CClientQuotingActionPropertyValueType.mapIdToName.get(v, None)
            if not name:
                name = forceString(db.translate('QuotaType', 'id', quotaTypeId, 'CONCAT_WS(\' | \', code, name)'))
                CClientQuotingActionPropertyValueType.mapIdToName[quotaTypeId] = name
            self.isObsolete = forceBool(QtGui.qApp.db.translate('QuotaType', 'id', quotaTypeId, 'isObsolete'))
        else:
            self.isObsolete = False
        return name

    def toInfo(self, context, v): pass


class CQuotaTypeActionPropertyValueType(CActionPropertyValueType):
    mapIdToName = {}
    name = 'QuotaType'
    variantType = QtCore.QVariant.Int
    isObsolete = False

    class CPropEditor(object):
        def __init__(self, action, domain, parent, clientId):
            pass

    def getEditorClass(self):
        return self.CPropEditor

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        quotaTypeId = forceRef(v)
        name = ''
        if quotaTypeId:
            db = QtGui.qApp.db
            name = CQuotaTypeActionPropertyValueType.mapIdToName.get(quotaTypeId, None)
            if name is None:
                name = forceString(db.translate('QuotaType', 'id', quotaTypeId, 'concat_ws(\' | \', code, name)'))
                CQuotaTypeActionPropertyValueType.mapIdToName[quotaTypeId] = name
            self.isObsolete = forceBool(db.translate('QuotaType', 'id', quotaTypeId, 'isObsolete'))
        else:
            self.isObsolete = False
        return name

    def toInfo(self, context, v): pass


class CRadiationDoseActionPropertyValueType(CDoubleActionPropertyValueType):
    name = u'Доза облучения'
    variantType = QtCore.QVariant.Double

    def getTableName(self):
        return self.tableNamePrefix + CDoubleActionPropertyValueType.name


CActionPropertyValueTypeRegistry.register(CDoubleActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CIntegerActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CStringActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CDateActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTimeActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CReferenceActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTextActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHtmlActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CConstructorActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CComplaintsActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CRLSActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(COrganisationActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(COrgStructureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHospitalBedActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHospitalBedProfileActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPersonActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CImageActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CJobTicketActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CImageMapActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CSamplingActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CBlankSerialActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CBlankNumberActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTemperatureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CArterialPressureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPulseActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CToothActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CCounterActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CClientQuotingActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CQuotaTypeActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CRadiationDoseActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPacsImagesActionPropertyValueType)


class CActionPropertyType(object):
    class UserProfileBehaviour:
        DisableEdit = 0
        Hide = 1

    # Атрибуты для проверки схожих типов свойств. Для начала примем, что соответствие должно быть полным (кроме id)
    similarAPTattributes = [
        'idx', 'name', 'shortName', 'descr', 'typeName', 'valueDomain', 'valueType', 'isVector', 'unitId', 'norm',
        'sex', 'age', 'visibleInJobTicket', 'visibleInTableRedactor', 'isAssignable', 'testId',
        'defaultEvaluation', 'canChangeOnlyOwner', 'isActionNameSpecifier', 'laboratoryCalculator',
        'inActionsSelectionTable', 'redactorSizeFactor', 'isFrozen', 'typeEditable'
    ]

    def __init__(self, record):
        self.initByRecord(record)

    def initByRecord(self, record):
        self.id = forceInt(record.value('id'))
        self.idx = forceInt(record.value('idx'))
        self.name = forceString(record.value('name'))
        self.shortName = forceString(record.value('shortName'))
        self.descr = forceString(record.value('descr'))
        self.typeName = forceString(record.value('typeName'))
        self.valueDomain = forceString(record.value('valueDomain'))
        self.valueType = self.getValueType()
        self.defaultValue = self.valueType.convertSpecialText(forceString(record.value('defaultValue')))
        #        self.defaultValue = forceString(record.value('defaultValue'))
        self.isVector = forceBool(record.value('isVector'))
        self.unitIdAsQVariant = record.value('unit_id')
        self.normAsQVariant = record.value('norm')
        self.unitId = forceRef(self.unitIdAsQVariant)
        self.norm = forceString(self.normAsQVariant)
        self.sex = forceInt(record.value('sex'))
        self.penalty = forceInt(record.value('penalty'))
        age = forceStringEx(record.value('age'))
        self.age = parseAgeSelector(age) if age else None
        self.qVariantType = self.valueType.variantType
        self.valueSqlFieldTemplate = QtSql.QSqlField('value', self.qVariantType)
        self.convertQVariantToPyValue = self.valueType.convertQVariantToPyValue
        self.convertPyValueToQVariant = self.valueType.convertPyValueToQVariant
        self.tableName = self.valueType.tableName
        self.visibleInJobTicket = forceBool(record.value('visibleInJobTicket'))
        self.visibleInTableRedactor = forceInt(record.value('visibleInTableRedactor'))
        self.isAssignable = forceBool(record.value('isAssignable'))
        self.testId = forceInt(record.value('test_id'))
        self.defaultEvaluation = forceInt(record.value('defaultEvaluation'))
        self.canChangeOnlyOwner = forceInt(record.value('canChangeOnlyOwner'))
        self.isActionNameSpecifier = forceBool(record.value('isActionNameSpecifier'))
        self.laboratoryCalculator = forceString(record.value('laboratoryCalculator'))
        self.inActionsSelectionTable = forceInt(record.value('inActionsSelectionTable'))
        self.redactorSizeFactor = forceDouble(record.value('redactorSizeFactor'))
        self.isFrozen = forceBool(record.value('isFrozen'))
        self.typeEditable = forceBool(record.value('typeEditable'))
        self.userProfileId = forceRef(record.value('userProfile_id'))
        self.userProfileBehaviour = forceInt(record.value('userProfileBehaviour'))

    def getValueType(self):
        return CActionPropertyValueTypeRegistry.get(self.typeName, self.valueDomain, self.name)

    def getNewRecord(self):
        db = QtGui.qApp.db
        record = db.table('ActionProperty').newRecord()
        #        record.append(QtSql.QSqlField(self.valueSqlFieldTemplate)) ???
        record.setValue('type_id', QtCore.QVariant(self.id))
        record.setValue('unit_id', self.unitIdAsQVariant)
        record.setValue('norm', self.normAsQVariant)
        return record

    def getValueTableName(self):
        return self.tableName

    def getValue(self, valueId):
        db = QtGui.qApp.db
        valueTable = db.table(self.tableName)
        if self.isVector:
            stmt = db.selectStmt(valueTable, 'value', valueTable['id'].eq(valueId), order='`index`')
            query = db.query(stmt)
            result = []
            while query.next():
                result.append(self.convertQVariantToPyValue(query.record().value(0)))
            return result
        else:
            stmt = db.selectStmt(valueTable, 'value', [valueTable['id'].eq(valueId), valueTable['index'].eq(0)])
            query = db.query(stmt)
            if query.next():
                return self.convertQVariantToPyValue(query.record().value(0))
            else:
                return None

    def storeRecord(self, record, value):
        db = QtGui.qApp.db
        valueTable = db.table(self.tableName)
        valueId = db.insertOrUpdate('ActionProperty', record)

        if self.isVector:
            vector = value
            indexes = range(len(vector))
        else:
            if value:
                vector = [value]
                indexes = [0]
            else:
                vector = []
                indexes = []

        if indexes:
            stmt = QtCore.QString()
            stream = QtCore.QTextStream(stmt, QtCore.QIODevice.WriteOnly)
            stream << (u'INSERT INTO %s (`id`, `index`, `value`) VALUES ' % self.tableName)
            for index in indexes:
                val = self.convertPyValueToQVariant(vector[index])
                if index:
                    stream << u', '
                stream << (u'(%d, %d, ' % (valueId, index))
                stream << db.formatQVariant(val.type(), val)
                stream << u')'
            stream << u' ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)'
            db.query(stmt)
            db.deleteRecord(valueTable,
                            [valueTable['id'].eq(valueId), 'NOT(' + valueTable['index'].inlist(indexes) + ')'])
        else:
            db.deleteRecord(valueTable, [valueTable['id'].eq(valueId)])
        return valueId

    def createEditor(self, action, editorParent, clientId):
        result = None
        editorClass = self.valueType.getEditorClass()
        if editorClass:
            if editorClass == CConstructorActionPropertyValueType.CPropEditor:
                result = editorClass(action, self.valueType.domain, editorParent, clientId, self.typeEditable)
            else:
                result = editorClass(action, self.valueType.domain, editorParent, clientId)
        return result

    def applicable(self, clientSex, clientAge):
        if self.sex and clientSex and clientSex != self.sex:
            return False
        if self.age and clientAge and not checkAgeSelector(self.age, clientAge):
            return False
        return True

    def getPrefferedHeight(self):
        return self.valueType.prefferedHeightUnit, self.valueType.prefferedHeight

    def isHtml(self):
        return self.valueType.isHtml

    def isSimilar(self, other):
        if not isinstance(other, CActionPropertyType):
            return False
        result = True
        for attr in self.similarAPTattributes:
            result = result and self.__getattribute__(attr) == other.__getattribute__(attr)
            if not result:
                break
        return result


class CActionType(object):
    # atronah: флаг того, что статические строковые константы класса уже были переведены
    isTranslated = False
    # режимы подсчёта количества в действии
    userInput = 0
    eventVisitCount = 1
    eventLength = 2
    eventLengthWithoutRedDays = 3
    actionLength = 4
    actionLengthWithoutRedDays = 5
    actionFilledProps = 6
    bedDaysEventLength = 7
    bedDaysEventLengthWithoutRedDays = 8

    # статусы
    statusStarted = 0
    statusWait = 1
    statusFinished = 2
    statusCanceled = 3
    statusWithoutResult = 4
    statusAppointed = 5
    statusNotProvided = 6

    statusNames = (
    u'Начато', u'Ожидание', u'Закончено', u'Отменено', u'Без результата', u'Назначено', u'Не предусмотрено')

    # дата выполнения(default end date)
    dedUndefined = 0
    dedCurrentDate = 1
    dedEventSetDate = 2
    dedEventExecDate = 3

    # планируемая дата выполнения(default planned end date)
    dpedUndefined = 0
    dpedNextDay = 1
    dpedNextWorkDay = 2
    dpedJobTicketDate = 3
    dpedBegDatePlusAmount = 4
    dpedBegDatePlusDuration = 5

    # дата назначения(default direction date)
    dddUndefined = 0
    dddEventSetDate = 1
    dddCurrentDate = 2
    dddActionExecDate = 3

    # ответственный (default person)
    dpUndefined = 0
    dpEmpty = 1
    dpSetPerson = 2
    dpEventExecPerson = 3
    dpCurrentUser = 4

    # MKB (default MKB)
    dmkbNotUsed = 0
    dmkbByFinalDiag = 1
    dmkbBySetPersonDiag = 2
    dmkbSyncFinalDiag = 3
    dmkbSyncSetPersonDiag = 4
    dmkbEmpty = 5

    # Morphology (default Morphology)
    dmorphologyNotUsed = 0
    dmorphologyByFinalDiag = 1
    dmorphologyBySetPersonDiag = 2
    dmorphologySyncFinalDiag = 3
    dmorphologySyncSetPersonDiag = 4
    dmorphologyEmpty = 5

    dMESNotUsed = 0
    dMESFromEvent = 1
    dMESEmpty = 2

    # их названия
    amountEvaluation = [
        u'Количество вводится непосредственно',
        u'По числу визитов',
        u'По длительности события',
        u'По длительности события без выходных дней',
        u'По длительности действия',
        u'По длительности действия без выходных дней',
        u'По заполненным свойствам действия',
        u'Койко-дни заполняются по длительности',
        u'Койко-дни заполняются по длительности без выходных дней'
    ]

    # вид услуги
    serviceTypeOther = 0
    serviceTypeInitialInspection = 1
    serviceTypeReinspection = 2
    serviceTypeProcedure = 3
    serviceTypeOperation = 4
    serviceTypeResearch = 5
    serviceTypeHealing = 6
    serviceTypeSupplies = 7
    serviceTypeWardPayment = 8

    # Атрибуты, проверяемые при проверке схожих типов дествий. Помимо атрибутов ОБЯЗАТЕЛЬНО проверяются свойства типов действий.
    similarATattributes = [
        'isRequiredCoordination', 'amount', 'amountEvaluation', 'defaultStatus', 'defaultDirectionDate', 'defaultBeginDate',
        'defaultPlannedEndDate', 'defaultEndDate', 'defaultSetPersonId', 'defaultExecPersonId', 'defaultPersonInEvent',
        'defaultPersonInEditor',
        'defaultOrgId', 'defaultMKB', 'defaultMES', 'defaultMorphology', 'isMorphologyRequired', 'office', 'showTime',
        'maxOccursInEvent', 'isMes',  # 'nomenclativeServiceId',
        'isPrinted', 'context', 'prescribedTypeId', 'sheduleId',
        'isNomenclatureExpense', 'hasAssistant', 'propertyAssignedVisible', 'propertyUnitVisible',
        'propertyNormVisible',
        'propertyEvaluationVisible', 'serviceType', 'actualAppointmentDuration'
    ]

    def __init__(self, record):
        self._propertiesByName = {}
        self._propertiesById = {}
        self.initByRecord(record)
        self.retranslateClass(force=False)

    @classmethod
    def retranslateClass(cls, force=True):
        if force or not cls.isTranslated:
            cls.statusNames = map(lambda s: forceTr(s, u'ActionStatus'),
                                  cls.statusNames)
            cls.isTranslated = True
        return cls

    def initByRecord(self, record):
        self.id = forceRef(record.value('id'))
        self.groupId = forceRef(record.value('group_id'))
        self.class_ = forceInt(record.value('class'))
        self.code = forceString(record.value('code'))
        self.name = forceString(record.value('name'))
        self.title = forceString(record.value('title'))
        self.flatCode = forceString(record.value('flatCode'))
        self.isRequiredCoordination = forceBool(record.value('isRequiredCoordination'))
        #        self.serviceId = forceRef(record.value('service_id'))
        self.amount = forceDouble(record.value('amount'))
        self.amountEvaluation = forceInt(record.value('amountEvaluation'))
        self.defaultStatus = forceInt(record.value('defaultStatus'))
        self.defaultDirectionDate = forceInt(record.value('defaultDirectionDate'))
        self.defaultBeginDate = forceInt(record.value('defaultBeginDate'))
        self.defaultPlannedEndDate = forceInt(record.value('defaultPlannedEndDate'))
        self.defaultEndDate = forceInt(record.value('defaultEndDate'))
        self.defaultExecPersonId = forceRef(record.value('defaultExecPerson_id'))
        self.defaultSetPersonId = forceRef(record.value('defaultSetPerson_id'))
        self.defaultPersonInEvent = forceInt(record.value('defaultPersonInEvent'))
        self.defaultPersonInEditor = forceInt(record.value('defaultPersonInEditor'))
        self.defaultOrgId = forceRef(record.value('defaultOrg_id'))
        self.defaultMKB = forceInt(record.value('defaultMKB'))
        self.defaultMES = forceInt(record.value('defaultMES'))
        self.defaultMorphology = forceInt(record.value('defaultMorphology'))
        self.isMorphologyRequired = forceInt(record.value('isMorphologyRequired'))
        self.office = forceString(record.value('office'))
        self.showTime = forceBool(record.value('showTime'))
        self.maxOccursInEvent = forceInt(record.value('maxOccursInEvent'))
        self.isMes = forceBool(record.value('isMES'))
        self.nomenclativeServiceId = forceRef(record.value('nomenclativeService_id'))
        self.isPrinted = forceBool(record.value('isPrinted'))
        self.context = forceString(record.value('context'))
        self.prescribedTypeId = forceRef(record.value('prescribedType_id'))
        self.sheduleId = forceRef(record.value('shedule_id'))
        self.isNomenclatureExpense = forceBool(record.value('isNomenclatureExpense'))
        self.hasAssistant = forceInt(record.value('hasAssistant'))
        self.propertyAssignedVisible = forceBool(record.value('propertyAssignedVisible'))
        self.propertyUnitVisible = forceBool(record.value('propertyUnitVisible'))
        self.propertyNormVisible = forceBool(record.value('propertyNormVisible'))
        self.propertyEvaluationVisible = forceBool(record.value('propertyEvaluationVisible'))
        self.serviceType = forceInt(record.value('serviceType'))
        self.actualAppointmentDuration = forceInt(record.value('actualAppointmentDuration'))
        self.isCustomSum = forceBool(record.value('isCustomSum'))

        self.frequencyCount = forceInt(record.value('frequencyCount'))
        self.frequencyPeriod = forceInt(record.value('frequencyPeriod'))
        self.frequencyPeriodType = forceInt(record.value('frequencyPeriodType'))
        self.isStrictFrequency = forceBool(record.value('isStrictFrequency'))
        self.isFrequencyPeriodByCalendar = forceBool(record.value('isFrequencyPeriodByCalendar'))
        self.counterId = forceRef(record.value('counter_id'))
        self.isExecRequiredForEventExec = forceBool(record.value('isExecRequiredForEventExec'))
        self.isSubstituteEndDateToEvent = forceBool(record.value('isSubstituteEndDateToEvent'))
        self.isIgnoreEventExecDate = forceBool(record.value('isIgnoreEventExecDate'))

        self._initProperties()

    def _initProperties(self):
        db = QtGui.qApp.db
        tablePropertyType = db.table('ActionPropertyType')
        stmt = db.selectStmt(tablePropertyType, '*',
                             [tablePropertyType['actionType_id'].eq(self.id), tablePropertyType['deleted'].eq(0)],
                             order='name')
        query = db.query(stmt)
        while query.next():
            propertyType = CActionPropertyType(query.record())
            self._propertiesByName[propertyType.name.lower()] = propertyType
            self._propertiesById[propertyType.id] = propertyType

    def initPropertiesByRecords(self, recordList, clear=False):
        """
            Инициализируем свойства по списку записей. Используется в редакторе типов действий,
            когда актуальные для нас данные еще не записаны в БД.
            @param clear - удалить все старые свойства
        """
        if clear:
            self._propertiesByName = {}
            self._propertiesById = {}
        for record in recordList:
            propertyType = CActionPropertyType(record)
            self._propertiesByName[propertyType.name.lower()] = propertyType
            self._propertiesById[propertyType.id] = propertyType

    def containsPropertyWithName(self, name):
        return name.lower() in self._propertiesByName

    def getPropertiesById(self):
        return self._propertiesById

    def getPropertiesByName(self):
        return self._propertiesByName

    def getPropertyType(self, name):
        return self._propertiesByName.get(name.lower(), None)

    def getPropertyTypeById(self, propertyId):
        return self._propertiesById[propertyId]

    def propertyTypeIdPresent(self, propertyId):
        return propertyId in self._propertiesById

    def checkMaxOccursLimit(self, count, displayMessage=True):
        return self.maxOccursInEvent == 0 or count < self.maxOccursInEvent

    def checkReceivedMovingLeaved(self, message):
        return False

    def isSimilar(self, otherActionType):
        other = otherActionType
        if not isinstance(otherActionType, CActionType):
            return False
        result = True
        for attr in self.similarATattributes:
            result = result and self.__getattribute__(attr) == other.__getattribute__(attr)
            if not result:
                break
        if result:
            if not len(self.getPropertiesByName()) == len(other.getPropertiesByName()):
                return False
            for propertyName in self._propertiesByName:
                thisProperty = self.getPropertyType(propertyName)
                otherProperty = other.getPropertyType(propertyName)
                result = result and thisProperty.isSimilar(otherProperty)
                if not result:
                    break
        return result


class CActionTypeCache(CDbEntityCache):
    mapIdToActionType = {}
    mapCodeToActionType = {}
    mapFlatCodeToActionType = {}

    @classmethod
    def purge(cls):
        cls.mapIdToActionType.clear()
        cls.mapCodeToActionType.clear()
        cls.mapFlatCodeToActionType.clear()

    @classmethod
    def getById(cls, actionTypeId):
        result = cls.mapIdToActionType.get(actionTypeId, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            actionTypeRecord = db.getRecord('ActionType', '*', actionTypeId)
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def getByCode(cls, actionTypeCode):
        result = cls.mapCodeToActionType.get(actionTypeCode, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType['code'].eq(actionTypeCode))
            assert actionTypeRecord
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def getByFlatCode(cls, actionTypeFlatCode):
        result = cls.mapFlatCodeToActionType.get(actionTypeFlatCode, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType['flatCode'].eq(actionTypeFlatCode))
            assert actionTypeRecord is not None, 'No ActionType with flatCode = %s' % actionTypeFlatCode
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def register(cls, actionType):
        cls.mapIdToActionType[actionType.id] = actionType
        cls.mapCodeToActionType[actionType.code] = actionType
        cls.mapFlatCodeToActionType[actionType.flatCode] = actionType


class CActionProperty(object):
    def __init__(self, actionType, record=None, propertyType=None):
        self._unitId = None
        self._norm = ''
        self._record = None
        self._changed = False
        self._isAssigned = False
        self._evaluation = None
        self.setType(propertyType)
        if record:
            self.setRecord(record, actionType)
        elif self._type and self._type.isVector:
            self._value = []
        elif self._type and self._type.defaultValue:
            if self._type.typeName == 'OrgStructure':
                self._type.defaultValue = QtGui.qApp.db.translate('OrgStructure', 'code', self._type.defaultValue, 'id')
            self._value = self._type.convertQVariantToPyValue(toVariant(self._type.defaultValue))
            self._changed = True
        else:
            self._value = propertyType.valueType.getPresetValue() if propertyType else None
            self._changed = bool(self._value)

    def setType(self, propertyType):
        self._type = propertyType
        if propertyType:
            if propertyType.isVector:
                self.getValue = self.getValueVector
                self.getText = self.getTextVector
                self.getImage = self.getImageVector
                self.getInfo = self.getInfoVector
            else:
                self.getValue = self.getValueScalar
                self.getText = self.getTextScalar
                self.getImage = self.getImageScalar
                self.getInfo = self.getInfoScalar
            self._unitId = propertyType.unitId
            self._norm = propertyType.norm

    def type(self):
        return self._type

    def setRecord(self, record, actionType):
        propertyTypeId = forceRef(record.value('type_id'))
        if self._type:
            assert self._type.id == propertyTypeId
        else:
            self.setType(actionType.getPropertyTypeById(propertyTypeId))
        self._record = record
        self._value = self._type.getValue(record.value('id'))
        self._unitId = forceRef(record.value('unit_id'))
        self._norm = forceString(record.value('norm'))
        self._isAssigned = forceBool(record.value('isAssigned'))
        evaluation = record.value('evaluation')
        self._evaluation = None if evaluation.isNull() else forceInt(evaluation)

    def getRecord(self):
        return self._record

    def save(self, actionId):
        if self._changed:
            if not self._record:
                self._record = self._type.getNewRecord()
            self._record.setValue('action_id', toVariant(actionId))
            self._record.setValue('isAssigned', toVariant(self._isAssigned))
            self._record.setValue('evaluation', toVariant(self._evaluation))
            result = self._type.storeRecord(self._record, self._value)
            self._changed = False
        else:
            if self._record:
                result = forceRef(self._record.value('id'))
            else:
                result = None
        return result

    def getValueScalar(self):
        return self._value

    def getTextScalar(self):
        return self._type.valueType.toText(self._value)

    def getImageScalar(self):
        return self._type.valueType.toImage(self._value)

    def getInfoScalar(self, context):
        return self._type.valueType.toInfo(context, self._value)

    def getValueVector(self):
        return self._value[:]  # shalow copy

    def getTextVector(self):
        toText = self._type.valueType.toText
        return [toText(x) for x in self._value]

    def getImageVector(self):
        toImage = self._type.valueType.toImage
        return [toImage(x) for x in self._value]

    def getInfoVector(self, context):
        toInfo = self._type.valueType.toInfo
        return [toInfo(context, x) for x in self._value]

    def setValue(self, value):
        if self._value != value:
            self._changed = True
        self._value = value

    def getUnitId(self):
        return self._unitId

    def getNorm(self):
        return self._norm

    ## Описание свойства действия @see setAssigned
    def isAssigned(self):
        return self._isAssigned

    ## Оотражение поля БД ActionProperty.isAssigned
    # 0 = ничего
    # 1 = назначен
    def setAssigned(self, isAssigned):
        if self._isAssigned != isAssigned:
            self._changed = True
        self._isAssigned = isAssigned

    def getEvaluation(self):
        return self._evaluation

    def setEvaluation(self, evaluation):
        if self._evaluation != evaluation:
            self._changed = True
        self._evaluation = evaluation

    def copy(self, src):
        self.setAssigned(src.isAssigned())
        self.setValue(src.getValue())
        self.setEvaluation(src.getEvaluation())

    def copyIfNotEmpty(self, src):
        val = src.getValue()
        if val and not (isinstance(val, basestring) and val.isspace()):
            self.setAssigned(src.isAssigned())
            self.setValue(src.getValue())
            self.setEvaluation(src.getEvaluation())

    def getPrefferedHeight(self):
        return self._type.getPrefferedHeight()

    def isHtml(self):
        return self._type.isHtml()

    def isActionNameSpecifier(self):
        return self._type.isActionNameSpecifier


class CAction(object):
    def __init__(self, actionType=None, record=None):
        self._actionType = actionType
        self._record = None
        self._propertiesByName = {}
        self._propertiesById = {}
        self._executionPlan = {}
        self._assistantsByCode = {}
        self._properties = []
        self._locked = False
        self._nomenclatureExpense = None
        self._specifiedName = ''
        if record:
            self.setRecord(record)
        else:
            self._nomenclatureExpense = CNomenclatureExpense(
                None) if self._actionType and self._actionType.isNomenclatureExpense else None

    @classmethod
    def createByTypeId(cls, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        return cls(actionType=actionType)

    @classmethod
    def createByTypeCode(cls, actionTypeCode):
        actionType = CActionTypeCache.getByCode(actionTypeCode)
        return cls(actionType=actionType)

    @classmethod
    def createByFlatCode(cls, actionTypeFlatCode):
        actionType = CActionTypeCache.getByFlatCode(actionTypeFlatCode)
        return cls(actionType=actionType)

    @classmethod
    def getAction(cls, eventId, actionTypeCode):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        actionType = CActionTypeCache.getByCode(actionTypeCode)
        cond = [tableAction['event_id'].eq(eventId), tableAction['actionType_id'].eq(actionType.id)]
        record = db.getRecordEx(tableAction, '*', cond)
        return cls(record=record, actionType=actionType)

    @classmethod
    def getActionById(cls, actionId):
        record = QtGui.qApp.db.getRecord('Action', '*', actionId)
        return cls(record=record)

    def setRecord(self, record):
        # установить тип
        actionTypeId = forceRef(record.value('actionType_id'))
        if self._actionType:
            assert actionTypeId == self._actionType.id
        else:
            self._actionType = CActionTypeCache.getById(actionTypeId)
        self._record = record
        # инициализировать properties
        actionId = record.value('id')
        if forceRef(actionId):
            db = QtGui.qApp.db
            propertiesTable = db.table('ActionProperty')
            stmt = db.selectStmt(propertiesTable, '*',
                                 [propertiesTable['action_id'].eq(actionId), propertiesTable['deleted'].eq(0)])
            query = db.query(stmt)
            while query.next():
                propertyRecord = query.record()
                propertyTypeId = forceRef(propertyRecord.value('type_id'))
                if self._actionType.propertyTypeIdPresent(propertyTypeId):
                    prop = CActionProperty(self._actionType, propertyRecord)
                    # ???                    if prop.isValid():
                    self._propertiesByName[prop._type.name.lower()] = prop
                    self._propertiesById[prop._type.id] = prop
            self._properties = self._propertiesById.values()
            self._properties.sort(key=lambda prop: prop._type.idx)
            # план выполнения
            tableActionExecutionPlan = db.table('Action_ExecutionPlan')
            stmt = db.selectStmt(tableActionExecutionPlan, '*', [tableActionExecutionPlan['master_id'].eq(actionId),
                                                                 tableActionExecutionPlan['deleted'].eq(0)])
            query = db.query(stmt)
            while query.next():
                executionPlanRecord = query.record()
                execDateTime = forceDateTime(executionPlanRecord.value('execDate'))
                execDate = pyDate(execDateTime.date())
                execTime = execDateTime.time()
                execTimeDict = self._executionPlan.get(execDate, {})
                execTimeDict[execTime] = executionPlanRecord
                self._executionPlan[execDate] = execTimeDict
            # Загрузка ассистентов действия.
            self._assistantsByCode = self.loadAssistants(actionId)
        else:
            if self._actionType.counterId:
                self._record.setValue('counterValue',
                                      QtCore.QVariant(getDocumentNumber(None, self._actionType.counterId)))
        # спец. отметки
        status = forceInt(record.value('status'))
        personId = forceRef(record.value('person_id'))
        if forceRef(record.value('id')) and status == CActionType.statusFinished and personId:
            self._locked = False
        # списание ЛСиИМН
        if self._actionType.isNomenclatureExpense:
            self._nomenclatureExpense = CNomenclatureExpense(actionId)
        self._specifiedName = forceString(record.value('specifiedName'))

    def save(self, eventId=None, idx=0, isActionTemplate=False):
        db = QtGui.qApp.db
        if self._locked:
            # для заблокированной записи сохраняем только idx (позиция в списке на экране)
            actionId = forceRef(self._record.value('id'))
            if forceInt(self._record.value('idx')) != idx:
                self._record.setValue('idx', QtCore.QVariant(idx))
                db.query('UPDATE Action SET idx=%d WHERE id=%d' % (idx, actionId))
            return actionId
        else:
            # сохранить основную запись
            tableAction = db.table('Action')
            if not self._record:
                self._record = tableAction.newRecord()
                self._record.setValue('actionType_id', QtCore.QVariant(self._actionType.id))
                self._record.setValue('specifiedName', QtCore.QVariant(self._specifiedName))
                if self._actionType.counterId:
                    self._record.setValue('counterValue',
                                          QtCore.QVariant(getDocumentNumber(None, self._actionType.counterId)))
            if eventId:
                self._record.setValue('event_id', QtCore.QVariant(eventId))

            signature = 1 if forceDate(self._record.value('endDate')).isValid() else 0
            self._record.setValue('signature', QtCore.QVariant(
                signature))  # atronah: Для синхронизации с изменениями в ДокторРум по просьбе olooo

            self._record.setValue('idx', QtCore.QVariant(idx))
            itemId = db.insertOrUpdate(tableAction, self._record)
            self._record.setValue('id', toVariant(itemId))
            propertiesIdList = []
            # сохранить записи свойств
            for propertyObject in self._propertiesById.itervalues():
                if type(propertyObject.type().valueType) is CCounterActionPropertyValueType and isActionTemplate:
                    continue
                propertyId = propertyObject.save(itemId)
                if propertyId:
                    propertiesIdList.append(propertyId)
            # сохранить план выполнения
            executionPlanIdList = []
            if self._executionPlan:
                tableActionExecutionPlan = db.table('Action_ExecutionPlan')
                for _, execTimeDict in self._executionPlan.items():
                    for _, planRecord in execTimeDict.items():
                        planRecord.setValue('master_id', QtCore.QVariant(itemId))
                        executionPlanId = db.insertOrUpdate(tableActionExecutionPlan, planRecord)
                        planRecord.setValue('id', toVariant(executionPlanId))
                        if executionPlanId not in executionPlanIdList:
                            executionPlanIdList.append(executionPlanId)
            # удалить записи свойств кроме сохранённых
            propertiesTable = db.table('ActionProperty')
            if propertiesIdList:
                db.deleteRecord(propertiesTable,
                                [propertiesTable['action_id'].eq(itemId),
                                 propertiesTable['id'].notInlist(propertiesIdList)])
            else:
                db.deleteRecord(propertiesTable,
                                [propertiesTable['action_id'].eq(itemId)])

            # удалить записи плана выполнения кроме сохранённых
            if self._executionPlan:
                tableActionExecutionPlan = db.table('Action_ExecutionPlan')
                if executionPlanIdList:
                    db.deleteRecord(tableActionExecutionPlan,
                                    [tableActionExecutionPlan['master_id'].eq(itemId),
                                     tableActionExecutionPlan['id'].notInlist(executionPlanIdList)])
                else:
                    db.deleteRecord(tableActionExecutionPlan,
                                    [tableActionExecutionPlan['master_id'].eq(itemId)])
            # списание ЛСиИМН
            if self._nomenclatureExpense:
                self._nomenclatureExpense.save(itemId)

            self.saveAssistants(itemId, self._assistantsByCode)
            return itemId

    def getType(self):
        return self._actionType

    def getRecord(self):
        return self._record

    def getId(self):
        return forceRef(self._record.value('id')) if self._record else None

    def isLocked(self):
        return self._locked

    def getSpecifiedName(self):
        return self._specifiedName

    def getProperties(self):
        return self._properties

    def getPropertiesById(self):
        return self._propertiesById

    def getPropertiesByName(self):
        return self._propertiesByName

    def containsPropertyWithName(self, name):
        return name.lower() in self._propertiesByName

    def getFilledPropertiesCount(self):
        count = 0
        for prop in self._propertiesById.itervalues():
            if prop.getValue():
                count += 1
        return count

    def getProperty(self, name):
        result = self._propertiesByName.get(name.lower(), None)
        if not result:
            propertyType = self._actionType.getPropertyType(name)
            if propertyType:
                result = CActionProperty(self._actionType, propertyType=propertyType)
                self._propertiesByName[propertyType.name.lower()] = result
                self._propertiesById[propertyType.id] = result
                self._properties.append(result)
                self._properties.sort(key=lambda prop: prop._type.idx)
            else:
                raise KeyError(u'ActionType (%s: %s) does not have property named %s' % (self._actionType.id,
                                                                                         self._actionType.name,
                                                                                         name))
        return result

    ## Получение Свойства Действия по id Типа Свойства действия
    # @param propertyId: - id ТИПА свойства действия
    def getPropertyById(self, propertyId):
        result = self._propertiesById.get(propertyId, None)
        if not result:
            propertyType = self._actionType.getPropertyTypeById(propertyId)
            result = CActionProperty(self._actionType, propertyType=propertyType)
            self._propertiesByName[propertyType.name.lower()] = result
            self._propertiesById[propertyType.id] = result
            self._properties.append(result)
            self._properties.sort(key=lambda prop: prop._type.idx)
        return result

    def getPropertyByIndex(self, index):
        return self._properties[index]

    def getExecutionPlan(self):
        return self._executionPlan

    def setExecutionPlan(self, executionPlan):
        self._executionPlan = executionPlan

    def __getitem__(self, name):
        propertyObject = self.getProperty(name)
        return propertyObject.getValue() if propertyObject else None

    def __setitem__(self, name, value):
        propertyObject = self.getProperty(name)
        if propertyObject:
            propertyObject.setValue(value)

    def __delitem__(self, name):
        if self._propertiesByName.has_key(name.lower()):
            propertyObject = self._propertiesByName[name.lower()]
            del self._propertiesByName[name.lower()]
            del self._propertiesById[propertyObject._type.id]

    def updateByTemplate(self, templateId):
        db = QtGui.qApp.db
        templateActionId = forceRef(db.translate('ActionTemplate', 'id', templateId, 'action_id'))
        self.updateByActionId(templateActionId)

    def updateByActionId(self, actionId):
        db = QtGui.qApp.db
        templateRecord = db.getRecord('Action', '*', actionId)
        if templateRecord:
            templateAction = CAction(record=templateRecord)
            self.updateByAction(templateAction)

    def updateByAction(self, templateAction):
        for propertyName in self._propertiesByName:
            propertyObject = self._propertiesByName[propertyName]
            if propertyObject.type().valueType.isCopyable and propertyName in templateAction._propertiesByName:
                templatePropertyObject = templateAction._propertiesByName[propertyName]
                if propertyObject.type().isSimilar(templatePropertyObject.type()):
                    propertyObject.copyIfNotEmpty(templateAction._propertiesByName[propertyName])

    ## Очищает список свойств действия
    def clearProperties(self):
        self._propertiesByName.clear()
        self._propertiesById.clear()
        self._properties = []

    ## Очищает список плана выполнения действия
    def clearExecution(self):
        self._executionPlan.clear()

    ## Создает копию текущего действия
    #
    # Дополнительные (необязательная) параметры копирования данных текущего Действия в новое.
    # @param isCopyRecordData: пометка о необходимости копировать запись БД. (По умолчанию False).
    # @param isCopyActionId: пометка о необходимости копирования ID Действия при копировании записи БД. (По умолчанию False).
    # @param isCopyExecutionPlan: пометка о необходимости копирования плана выполнения. (По умолчанию False).
    # @param isCopyProperties: пометка о необходимости копирования свойств действия. (По умолчанию True).
    # @param isCheckPropertiesCopyable: пометка о необходимости проверки при копировании свойств,
    #                                    является ли значение свойства копируемым (CActionPropertyValueType.isCopyable).
    #                                    (По умолчанию True).
    def clone(self, **kwargs):
        newAction = CAction(actionType=self.getType())
        self.copyAction(self, newAction, **kwargs)
        return newAction

    ## Копирует план выполнения из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    @staticmethod
    def copyActionExecutionPlan(sourceAction, targetAction):
        targetAction.clearExecution()
        targetAction.setExecutionPlan(copy.deepcopy(sourceAction.getExecutionPlan()))

    ## Копирует ассистентов из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    @staticmethod
    def copyActionAssistants(sourceAction, targetAction):
        for assistantTypeCode in sourceAction.existedAssistantCodeList():
            assistantId = sourceAction.getAssistantId('assistant')
            assistantFreeInput = sourceAction.getAssistantFreeInput('assistant')
            targetAction.setAssistant(assistantTypeCode, assistantId, assistantFreeInput)

    ## Копирует свойства из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    # @param isCheckCopyable: проверять свойства на возможность копирования. По умолчанию включено (True).
    @staticmethod
    def copyActionProperties(sourceAction, targetAction, isCheckCopyable=True):
        targetAction.clearProperties()
        for sourceProperty in sourceAction.getProperties():
            if not isCheckCopyable or sourceProperty.type().valueType.isCopyable:
                sourcePropertyTypeId = sourceProperty.type().id
                targetProperty = targetAction.getPropertyById(sourcePropertyTypeId)
                targetProperty.copy(sourceProperty)

    ## Копирует основные данные о Действии из одного в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    # @param isCopyIdFieldData: копировать данные поля ID записи из БД. По умолчанию выключено (False).
    @staticmethod
    def copyActionRecordData(sourceAction, targetAction, isCopyIdFieldData=False):
        # получаем копиюю записи БД из исходного действия
        sourceActionRecord = QtSql.QSqlRecord(sourceAction.getRecord())
        # обнуляем id записи БД исходного действия, чтобы оно не копировалось
        # и чтобы при setRecord не подгружались свойства действия
        sourceActionRecord.setValue(u'id', QtCore.QVariant())
        # сохраняем id целевого действия
        sourceActionId, targetActionId = sourceAction.getId(), targetAction.getId()
        # Присваиваем целевому действию новую запись БД
        targetAction.setRecord(sourceActionRecord)
        # Восстанавливаем id целевого действия
        targetAction.getRecord().setValue('id', toVariant(sourceActionId if isCopyIdFieldData else targetActionId))

    ## Копирует содержимое одного Действия в другое. По умолчанию копирует только свойства и план выполнения
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    #
    # Дополнительные (необязательная) параметры копирования
    # @param isCopyRecordData: пометка о необходимости копировать запись БД. (По умолчанию False).
    # @param isCopyActionId: пометка о необходимости копирования ID Действия при копировании записи БД. (По умолчанию False).
    # @param isCopyAssistants: пометка о необходимости копирования ассистентов Действия при копировании записи БД. (По умолчанию True).
    # @param isCopyExecutionPlan: пометка о необходимости копирования плана выполнения. (По умолчанию False).
    # @param isCopyProperties: пометка о необходимости копирования свойств действия. (По умолчанию True).
    # @param isCheckPropertiesCopyable: пометка о необходимости проверки при копировании свойств,
    #                                    является ли значение свойства копируемым (CActionPropertyValueType.isCopyable)
    #                                    (По умолчанию True).
    @classmethod
    def copyAction(cls, sourceAction, targetAction, **kwargs):
        isCopyRecordData = kwargs.get('isCopyRecordData', False)
        if isCopyRecordData:
            isCopyActionId = kwargs.get('isCopyActionId', False)
            cls.copyActionRecordData(sourceAction, targetAction, isCopyActionId)

        isCopyAssistants = kwargs.get('isCopyAssistants', True)
        if isCopyAssistants:
            cls.copyActionAssistants(sourceAction, targetAction)

        isCopyExecutionPlan = kwargs.get('isCopyExecutionPlan', False)
        if isCopyExecutionPlan:
            cls.copyActionExecutionPlan(sourceAction, targetAction)

        isCopyProperties = kwargs.get('isCopyProperties', True)
        if isCopyProperties:
            isCheckPropertiesCopyable = kwargs.get('isCheckPropertiesCopyable', True)
            cls.copyActionProperties(sourceAction, targetAction, isCheckPropertiesCopyable)

    def findFireableJobTicketId(self):
        for propertyObject in self._properties:
            if type(propertyObject.type().valueType) == CJobTicketActionPropertyValueType:
                jobTicketId = propertyObject.getValue()
                if jobTicketId:
                    return jobTicketId
        return None

    def getTestProperties(self):
        return [propertyObject
                for propertyObject in self._properties
                if propertyObject.type().testId and propertyObject.isAssigned()
                ]

    def updateSpecifiedName(self):
        name = ' '.join([forceString(propertyObject.getText())
                         for propertyObject in self._properties
                         if propertyObject.isActionNameSpecifier() and propertyObject.getValue()
                         ]
                        )
        self.setSpecifiedName(name)

    def setSpecifiedName(self, name):
        if self._record:
            self._record.setValue('specifiedName', QtCore.QVariant(name))
        self._specifiedName = name

    def initPropertyPresetValues(self):
        actionType = self.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        for propertyType in propertyTypeList:
            self.getPropertyById(propertyType.id)

    def existedAssistantCodeList(self):
        """
        Возвращает список кодов типов ассистентов, имеющихся в событии.
        :return: список имеющихся ассистентов (кодов их типов)
        """
        return self._assistantsByCode.keys()

    def getAssistantId(self, code):
        """
        Возвращает ID ассистента, с типом, код которого передан при вызове.
        :return: ID ассистента для указанного типа или None
        """
        if self._assistantsByCode.has_key(code):
            return self._assistantsByCode[code].id

        return None

    def getAssistantFreeInput(self, code):
        """
        Возвращает имя ассистента, с типом, код которого передан при вызове, в виде строки, введеной с клавиатуры.
        :return: строка с именем ассистента.
        """
        if self._assistantsByCode.has_key(code):
            return self._assistantsByCode[code].freeInput

    def setAssistant(self, code, assistantId=None, assistantFreeInput=u''):
        self.addAssistant(self._assistantsByCode, code, assistantId, assistantFreeInput)

    @staticmethod
    def addAssistant(assistantsByCode, code, assistantId=None, assistantFreeInput=u''):
        """
        Добавляет/изменяет информацию об ассистенте указанного типа (задает его ID или имя в свободной форме) в справочнике.
        :param assistantsByCode: словарь с информацией (smartDict()) об ассистентах по их коду, в котором будут сделаны изменения
        :param code: код типа изменяемого ассистента.
        :param assistantId: id врача, который необходимо установить для заданного типа ассистента.
        :param assistantFreeInput: имя врача, которое необходимо установить для заданного типа ассистента.
        """
        if assistantsByCode.has_key(code):
            assistantInfo = assistantsByCode[code]
        else:
            assistantInfo = smartDict()
            assistantInfo.recordId = None
            assistantsByCode[code] = assistantInfo

        assistantInfo.id = forceRef(assistantId)
        assistantInfo.freeInput = assistantFreeInput
        assistantInfo.hasBeenChanged = True

    @staticmethod
    def loadAssistants(actionId):
        """
        Загружает данные об ассистентах Действия, распределяя их по кодам типов.
        """
        assistantByCode = {}
        db = QtGui.qApp.db
        tableAssistant = db.table('Action_Assistant')
        tableAssistantType = db.table('rbActionAssistantType')

        recordList = db.getRecordList(table=tableAssistant.innerJoin(tableAssistantType,
                                                                     tableAssistantType['id']
                                                                     .eq(tableAssistant['assistantType_id'])),
                                      cols=[tableAssistantType['code'],
                                            tableAssistantType['isEnabledFreeInput'],
                                            tableAssistant['id'].alias('recordId'),
                                            tableAssistant['person_id'],
                                            tableAssistant['freeInput']],
                                      where=[tableAssistant['action_id'].eq(actionId)])
        for record in recordList:
            code = forceString(record.value('code'))
            isEnabledFreeInput = forceBool(record.value('isEnabledFreeInput'))
            assistantInfo = smartDict()
            assistantInfo.recordId = forceRef(record.value('recordId'))
            assistantInfo.id = forceRef(record.value('person_id'))
            assistantInfo.freeInput = forceString(record.value('freeInput')) if isEnabledFreeInput else u''
            assistantInfo.hasBeenChanged = False
            assistantByCode[code] = assistantInfo

        return assistantByCode

    @staticmethod
    def saveAssistants(actionId, assistantsByCode):
        """
        Сохраняет данные об ассистентах Действия, если они были изменены
        """
        db = QtGui.qApp.db
        tableAssistant = db.table('Action_Assistant')
        tableAssistantType = db.table('rbActionAssistantType')

        savedAssistantTypeIdList = []
        db.transaction()
        try:
            for code, assistantInfo in assistantsByCode.items():
                if assistantInfo.id is None:
                    continue
                assistantTypeId = db.translate(tableAssistantType, tableAssistantType['code'], code,
                                               tableAssistantType['id'])
                if assistantInfo.hasBeenChanged:
                    newRecord = tableAssistant.newRecord()
                    newRecord.setValue('id', QtCore.QVariant(assistantInfo.recordId))
                    newRecord.setValue('action_id', QtCore.QVariant(actionId))
                    newRecord.setValue('assistantType_id', QtCore.QVariant(assistantTypeId))
                    newRecord.setValue('person_id', QtCore.QVariant(assistantInfo.id))
                    newRecord.setValue('freeInput', QtCore.QVariant(assistantInfo.freeInput))
                    db.insertOrUpdate(tableAssistant, newRecord)
                savedAssistantTypeIdList.append(assistantTypeId)
            db.deleteRecord(table=tableAssistant,
                            where=[tableAssistant['action_id'].eq(actionId),
                                   tableAssistant['assistantType_id'].notInlist(savedAssistantTypeIdList)])
            db.commit()
        except:
            db.rollback()


class CNomenclatureExpense:
    def __init__(self, actionId=None):
        self._dirty = False
        self._motionId = None
        self._items = []
        if actionId:
            self._load(actionId)

    def _load(self, actionId):
        pass

    def save(self, actionId):
        pass


def ensureActionTypePresence(actionTypeCode, propTypeList=None, isUseFlatCode=False):
    if not propTypeList:
        propTypeList = []
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    tablePropertyType = db.table('ActionPropertyType')
    codeFieldName = 'code' if not isUseFlatCode else 'flatCode'
    actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType[codeFieldName].eq(actionTypeCode))
    if actionTypeRecord:
        actionTypeId = forceRef(actionTypeRecord.value('id'))
    else:
        actionTypeRecord = tableActionType.newRecord()
        actionTypeRecord.setValue(codeFieldName, toVariant(actionTypeCode))
        actionTypeId = db.insertOrUpdate(tableActionType, actionTypeRecord)
    if propTypeList:
        for propTypeDef in propTypeList:
            name = propTypeDef.get('name', None)
            descr = propTypeDef.get('descr', None)
            unit = propTypeDef.get('unit', None)
            typeName = propTypeDef.get('typeName', 'String')
            valueDomain = propTypeDef.get('valueDomain', None)
            isVector = propTypeDef.get('isVector', False)
            norm = propTypeDef.get('norm', None)
            sex = propTypeDef.get('sex', None)
            age = propTypeDef.get('age', None)

            propertyTypeRecord = db.getRecordEx(tablePropertyType, '*',
                                                [tablePropertyType['actionType_id'].eq(actionTypeId),
                                                 tablePropertyType['name'].eq(name)])
            if propertyTypeRecord:
                pass
            else:
                propertyTypeRecord = tablePropertyType.newRecord()
                propertyTypeRecord.setValue('actionType_id', toVariant(actionTypeId))
                propertyTypeRecord.setValue('name', toVariant(name))
                propertyTypeRecord.setValue('descr', toVariant(descr))
                if unit:
                    unitId = db.translate('rbUnit', 'code', unit, 'id')
                    if unitId:
                        propertyTypeRecord.setValue('descr', unitId)
                propertyTypeRecord.setValue('typeName',
                                            toVariant(CActionPropertyValueTypeRegistry.normTypeName(typeName)))
                propertyTypeRecord.setValue('valueDomain', toVariant(valueDomain))
                propertyTypeRecord.setValue('isVector', toVariant(isVector))
                propertyTypeRecord.setValue('norm', toVariant(norm))
                propertyTypeRecord.setValue('sex', toVariant(sex))
                propertyTypeRecord.setValue('age', toVariant(age))
                db.insertRecord(tablePropertyType, propertyTypeRecord)


####################################################################
# сценарий работы c Actions:
#
# 1) создание Action
#    a1 = CAction.createByTypeCode(10)
# 2) загрузка Action
#    a2 = CAction(record=query.record())
# 3) сохранение Action
#    a1.save(eventId)
#    a2.save()
# 4) доступ к свойствам Action
#    x = a2['value']
# 5) изменение свойства Action
#    a2['value'] = x
# 6) очистка/удаление свойства Action
#    del a2['value']
# 7) векторные свойства?
