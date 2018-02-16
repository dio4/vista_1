# -*- coding: utf-8 -*-
from library.Utils import forceRef, toVariant, toNativeType, forceDate,\
    forceString, forceBool
from PyQt4 import QtCore, QtSql, QtGui
from library.CashRegister.CashRegisterOperationInfo import CCashRegisterOperationInfo,\
    COperationExportToTxtInfo
from library.CashRegister.CheckItemModel import CCheckItem
import codecs
import os

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

'''
Created on 01.10.2013

@author: atronah
'''


class CECRLogger(QtCore.QObject):
    dateFormat = u'dd.MM.yyyy'
    propertyInfoTemplate = '%s = %s'
    
    deviceInfo = property(lambda self: CECRLogger._getInfo(CECRLogger._deviceNameToProperty, self),
                          lambda self, value: CECRLogger._setInfo(CECRLogger._deviceNameToProperty, self, value))
    
    
    execPersonId = property(lambda self: QtGui.qApp.userId if hasattr(QtGui.qApp, 'userId') else None,
                            lambda self, value: None)
    
    
    documentInfo = property(lambda self: CECRLogger._getInfo(CECRLogger._documentNameToProperty, self),
                          lambda self, value: CECRLogger._setInfo(CECRLogger._documentNameToProperty, self, value))
    
    
    #TODO: atronah: Этот ад (повторяющийся в классе COperationExportToTxtInfo) стоит привести к чему-то более
    # адекватному путем создания общего класса, вроде CStoreManager, 
    # отвечающий за загрузку/сохранение данных в различные источники (база, файл)
    formatedDocumentIssuedDate = property(lambda self: CECRLogger.dateToString(CCashRegisterOperationInfo.personDocumentIssuedDate.__get__(self)),
                                          lambda self, value: CCashRegisterOperationInfo.personDocumentIssuedDate.__set__(self, CECRLogger.dateFromString(value)))
    
    _sqlOperationRecordInfo = {'execPerson_id' : (QtCore.QVariant.Int, execPersonId),
                               'checkType' : (QtCore.QVariant.Int, CCashRegisterOperationInfo.checkType),
                               'checkNumber' : (QtCore.QVariant.Int, CCashRegisterOperationInfo.checkNumber),
                               'checkSumm' : (QtCore.QVariant.Double, CCashRegisterOperationInfo.checkSumm),
                               'closeType' : (QtCore.QVariant.Int, CCashRegisterOperationInfo.closeType),
                               'isExpense' : (QtCore.QVariant.Bool, CCashRegisterOperationInfo.direction),
                               'closeDatetime' : (QtCore.QVariant.DateTime, CCashRegisterOperationInfo.closeDatetime),
                               'operator' : (QtCore.QVariant.Int, CCashRegisterOperationInfo.operator),
                               'session'  : (QtCore.QVariant.Int, CCashRegisterOperationInfo.session),
                               'deviceInfo' : (QtCore.QVariant.String, deviceInfo),
                               'substructure' : (QtCore.QVariant.String, CCashRegisterOperationInfo.substructure),
                               'cashFlowArticle' : (QtCore.QVariant.String, CCashRegisterOperationInfo.cashFlowArticle),
                               'operationType_id' : (QtCore.QVariant.Int, CCashRegisterOperationInfo.operationTypeId),
                               'operationTypeName' : (None, CCashRegisterOperationInfo.operationTypeName),
                               'personName' : (QtCore.QVariant.String, CCashRegisterOperationInfo.personName),
                               'isPersonNatural' : (QtCore.QVariant.Bool, CCashRegisterOperationInfo.personType),
                               'documentInfo' : (QtCore.QVariant.String, documentInfo),
                               'description' : (QtCore.QVariant.String, CCashRegisterOperationInfo.description)
                               }
    
    
    _deviceNameToProperty = {u'Логический номер' : CCashRegisterOperationInfo.deviceLogicalNumber,
                             u'Серийный номер' : CCashRegisterOperationInfo.deviceSerialNumber,
                             u'Касса фискализирована' : CCashRegisterOperationInfo.deviceFiscal
                             }
    
    
    _documentNameToProperty = {u'ИНН/КПП контрагента' : CCashRegisterOperationInfo.personINN,
                               u'Тип документа' : CCashRegisterOperationInfo.personDocumentType,
                               u'Серия паспорта' : CCashRegisterOperationInfo.personDocumentSerial,
                               u'Номер паспорта' : CCashRegisterOperationInfo.personDocumentNumber,
                               u'Дата выдачи документа' : formatedDocumentIssuedDate,
                               u'Кем выдано (документ)' : CCashRegisterOperationInfo.personDocumentIssued
                               }
    
    
    _sqlCheckItemRecordInfo = {'name' : (QtCore.QVariant.String, CCheckItem.name),
                               'quantity' : (QtCore.QVariant.Double, CCheckItem.quantity),
                               'price' : (QtCore.QVariant.Double, CCheckItem.price)
                               }
    
    mapTypeIdToName = {}
    
    # Сигнал о необходимости вывести сообщение для пользователя (сообщение, выделить_красным)
    showedMessage = QtCore.pyqtSignal(QtCore.QString, bool)
    
    def __init__(self, db = None):
        QtCore.QObject.__init__(self)
        self._db = db
        self._tableOperation = self._db.table('ECROperation')
        self._tableCheckItem = self._db.table('ECRCheckItem')
        self._tableOperationType = self._db.table('rbECROperationType')
        self.loadOperationTypesInfo()
    
    
    
    def loadOperationTypesInfo(self):
        self._operationsTypeInfo = {'names' : [],
                                    'idList' : [],
                                    'showedIdx': []
                                    }
        for idx, record in enumerate(self._db.getRecordList(self._tableOperationType, '*')):
            typeName = forceString(record.value('name'))
            typeId = forceRef(record.value('id'))
            isShowed = forceBool(record.value('isShowed'))
            self._operationsTypeInfo['names'].append(typeName)
            self._operationsTypeInfo['idList'].append(typeId)
            if isShowed:
                self._operationsTypeInfo['showedIdx'].append(idx)
            
    
    
    def operationTypesInfo(self):
        return self._operationsTypeInfo


    @staticmethod
    def dateToString(date):
        return forceString(date.toString(CECRLogger.dateFormat))
                           
    
    @staticmethod
    def dateFromString(stringDate):
        return QtCore.QDate.fromString(stringDate.strip(), CECRLogger.dateFormat)
    
    
    @staticmethod
    def _saveToSqlRecord(sqlRecordInfo, record, sourceData):
        for fieldName in sqlRecordInfo.keys():
            if not record.contains(fieldName) and sqlRecordInfo[fieldName][0] is not None:
                record.append(QtSql.QSqlField(fieldName, sqlRecordInfo[fieldName][0]))
            # получение значение поля через соответствующее свойство (указанное в _sqlRecordInfo)
            value = sqlRecordInfo[fieldName][1].__get__(sourceData)
            record.setValue(fieldName, toVariant(value))

        return record
    
    
    @staticmethod
    def _loadFromSqlRecord(sqlRecordInfo, record, destClass):
        result = destClass()
                    
        for fieldName in sqlRecordInfo.keys():
            if not record.contains(fieldName):
                continue
            # получение значение поля через соответствующее свойство (указанное в _sqlRecordInfo)
            value = toNativeType(record.value(fieldName))
            sqlRecordInfo[fieldName][1].__set__(result, value)

        return result
    
    
    def saveOperationInfoToSqlRecord(self, operationInfo):
        return CECRLogger._saveToSqlRecord(self._sqlOperationRecordInfo, self._tableOperation.newRecord(), operationInfo)
    
    
    def loadOperationFromSqlRecord(self, record):
        return CECRLogger._loadFromSqlRecord(self._sqlOperationRecordInfo, record, CCashRegisterOperationInfo)
        
    
    @staticmethod
    def loadOperationsFromFile(fileName, encoding = 'utf8'):
        operationInfoList = []
        with codecs.open(fileName, 'r', encoding = encoding) as sourceFile:
            fileLines = sourceFile.readlines()
            operationLines = []
            needAppend = False
            while fileLines:                    
                currentLine = fileLines.pop(0)
                if currentLine.strip() == COperationExportToTxtInfo.beginField:
                    operationLines = []
                    needAppend = True
                elif currentLine.strip() == COperationExportToTxtInfo.endField:
                    needAppend = False
                    operationInfo = CCashRegisterOperationInfo()
                    loadInfoDict = dict([(fieldName, prop) for fieldName, prop in COperationExportToTxtInfo.fields])
                    CECRLogger._setInfo(loadInfoDict, operationInfo, '\n'.join(operationLines))
                    operationInfoList.append(operationInfo)
                elif needAppend:
                    operationLines.append(currentLine)
        return operationInfoList
                    
    
    
    def saveCheckItemToSqlRecord(self, checkItem):
        return CECRLogger._saveToSqlRecord(self._sqlCheckItemRecordInfo, self._tableCheckItem.newRecord(), checkItem)
    
    
    def loadCheckItemFromSqlRecord(self, record):
        return CECRLogger._loadFromSqlRecord(self._sqlCheckItemRecordInfo, record, CCheckItem)

    
    def saveOperationInfo(self, operationInfo, itemList=None):
        if not itemList:
            itemList = []
        result = True
        operationRecord = self.saveOperationInfoToSqlRecord(operationInfo)
        
        operationId = self._db.insertOrUpdate(self._tableOperation, operationRecord)
        
        try:
            self._db.transaction()
            for item in itemList:
                itemRecord = self.saveCheckItemToSqlRecord(item)
                itemId = forceRef(item.userInfo)
                itemRecord.setValue('master_id', toVariant(operationId))
                itemRecord.setValue('accountItem_id', toVariant(itemId))
                self._db.insertOrUpdate(self._tableCheckItem, itemRecord)
            self._db.commit()
        except:
            self._db.rollback()
            result = False
            
        return result
    
    
    def operationTypeName(self, typeId):
        name = self.mapTypeIdToName.get(typeId, None)
        if name is None:
            name = forceString(self._db.translate(self._tableOperationType, 'id', typeId, 'name'))
            self.mapTypeIdToName[typeId] = name
        
        return name
    
    
    def exportToFile(self, operationInfoList, fileName, encoding, outFormat = 'txt'):
        errorMessage = u''
        
        if isinstance(operationInfoList, CCashRegisterOperationInfo):
            operationInfoList = [operationInfoList]
        
        fileName += '.' + outFormat
        if outFormat == 'txt':
            with codecs.open(fileName, 'w', encoding) as outFile:
                for operationInfo in operationInfoList:
                    fileLines = [COperationExportToTxtInfo.beginField]
                    for fieldName, prop in COperationExportToTxtInfo.fields:
                        fileLines.append(self.propertyInfoTemplate % (fieldName, 
                                                                      forceString(prop.__get__(operationInfo))))
                    
        
                    fileLines.append(COperationExportToTxtInfo.endField)
                    fileLines.append(os.linesep) 
                    outFile.writelines(os.linesep.join(fileLines))
            return os.path.abspath(fileName), len(operationInfoList), None
        else:
            errorMessage = u'Неподдерживаемый формат экспорта: %s' % outFormat
        
        return None, 0, errorMessage
    
    
    @staticmethod
    def _setInfo(nameToPropertyDict, destInstance, value):
        value = forceString(value)
        infoPairList = [infoLine.split('=') for infoLine in value.split('\n') if len(infoLine.split('=')) == 2]
        for title, value in dict(infoPairList).items():
                title = title.strip()
                value = value.strip()
                if title in nameToPropertyDict.keys():
                    nameToPropertyDict[title].__set__(destInstance, value)
                    
    @staticmethod
    def _getInfo(nameToPropertyDict, sourceInstance):
        infoList = []
        for fieldName, prop in nameToPropertyDict.items():
            infoList.append(CECRLogger.propertyInfoTemplate % (fieldName, 
                                                               forceString(prop.__get__(sourceInstance))))
        return '\n'.join(infoList)
    


    def loadOperationInfo(self, begDate = None, endDate = None, session = None, checkNumber = None):
        operationInfoList = []

        table = self._tableOperation.leftJoin(self._tableOperationType,
                                              self._tableOperationType['id'].eq(self._tableOperation['operationType_id']))

        cols = ['%s.*' % self._tableOperation.name(),
                self._tableOperationType['name'].alias('operationTypeName')
                ]

        cond = [self._tableOperation['cashFlowArticle'].notlike(''),
                self._tableOperation['operationType_id'].isNotNull()]

        for title, prop in self._deviceNameToProperty.items():
            if prop == CCashRegisterOperationInfo.deviceFiscal:
                fiscalString = self.propertyInfoTemplate % (title, True)
                cond.append(self._db.joinOr([self._tableOperation['deviceInfo'].like('%%%s%%' % fiscalString),
                                             self._tableOperation['deviceInfo'].isNull()]))

        if begDate:
            cond.append(self._tableOperation['closeDatetime'].ge(begDate))

        if endDate:
            cond.append(self._tableOperation['closeDatetime'].lt(endDate.addDays(1)))

        if checkNumber is not None:
            cond.append(self._tableOperation['checkNumber'].eq(checkNumber))

        if session is not None:
            cond.append(self._tableOperation['session'].eq(session))


        self.showMessage(u'Загрузка списка операций из базы данных...')
        for record in self._db.getRecordList(table, cols, where = cond, order = 'checkNumber'):
            operationInfoList.append(self.loadOperationFromSqlRecord(record))

        return operationInfoList

    #FIXME: обрабатывать случаи наличия нескольких ККМ в рамках одной базы данных, чтобы выгружались данные только по одной (выбранной или подключенной к текущему ПК)
    def export(self, params):
        #TODO: atronah: заменить на что-то более универсальное (словари и класс-методы по их изменению, добавлению новых языков)
        enFileNameModificators = [u'ecr', u'full', u'from', u'to', u'check', u'session']
        ruFileNameModificators = [u'ККМ', u'полная', u'с', u'по', u'чек', u'смена']
        iECR = 0
        iFull = 1
        iFrom = 2
        iTo = 3
        iCheck = 4
        iSession = 5
        fileNameDateFormat = 'ddMMyy'
        
        encoding = forceString(params.get('encoding', 'utf8'))
        outFormat = forceString(params.get('format', 'txt'))
        
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        checkNumber = params.get('checkNumber', None)
        session = params.get('session', None)
        langCode = params.get('langCode', 'en')
        if langCode == 'ru':
            fileNameModificators = ruFileNameModificators
        else:
            fileNameModificators = enFileNameModificators
        outDir = forceString(params.get('outDir', QtCore.QDir.homePath()))
        
        fileNameParts = [fileNameModificators[iECR]]
        if not (begDate or endDate or checkNumber or session):
            fileNameParts.append(fileNameModificators[iFull])
            fileNameParts.append(fileNameModificators[iTo] + forceString(QtCore.QDate.currentDate().toString(fileNameDateFormat)))
        else:
            if begDate:
                fileNameParts.append(fileNameModificators[iFrom] + forceString(forceDate(begDate).toString(fileNameDateFormat)))
            
            if endDate:
                fileNameParts.append(fileNameModificators[iTo] + forceString(forceDate(endDate).toString(fileNameDateFormat)))
                
            if checkNumber is not None:
                fileNameParts.append(fileNameModificators[iCheck] + forceString(checkNumber))
            
            if session is not None:
                fileNameParts.append(fileNameModificators[iSession] + forceString(session))
        
        operationInfoList = self.loadOperationInfo(begDate, endDate, session, checkNumber)

        fullFileName = os.path.join(outDir,
                                    '_'.join(fileNameParts))
        self.showMessage(u'Запись данных в файл...')
        
        return self.exportToFile(operationInfoList, fullFileName, encoding, outFormat)
    
    
    @QtCore.pyqtSlot(QtCore.QString, bool)
    def showMessage(self, message, isError = False):
        self.showedMessage.emit(message, isError)



def main():
    srcDir = 'C:/tmp/ecr'
    
    for fileName in os.listdir(srcDir):
        CECRLogger.loadOperationsFromFile(os.path.join(srcDir, fileName))




if __name__ == '__main__':
    main()