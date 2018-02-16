# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################
from library.CashRegister.CashRegisterDriverInfo import CCashRegisterDriverInfo

from library.Utils import forceString, toNativeType, forceDate, forceInt
from PyQt4 import QtCore, QtGui
from library.CashRegister.Ui_OperationInfoDialog import Ui_OperationInfoDialog

'''
Created on 26.09.2013

@author: atronah
'''




class CCashRegisterOperationInfo(object):    
    
    
    def __init__(self):
        self._checkType = None
        self._checkNumber = 0
        self._checkSumm = 0.0
        self._closeType = None
        self._closeDatetime = None
        self._operator = None
        self._deviceLogicalNumber = None
        self._deviceSerialNumber = None
        self._isDeviceFiscal = None
        self._substructure = u''
        self._cashFlowArticle = None
        self._operationTypeId = None
        self._operationTypeName = u''
        self._personName = u''
        self._personINN = u''
        self._personDocumentNumber = None
        self._personDocumentSerial = None
        self._personDocumentType = u''
        self._personDocumentIssuedDate = QtCore.QDate()
        self._personDocumentIssued = u''
        self._isPersonNatural = None
        self._session = None
        self._isExpense = False
        self._description = u''
    
    
    def setCheckType(self, checkType):
        self._checkType = toNativeType(checkType)
        
    
    def setCheckNumber(self, number):
        self._checkNumber = toNativeType(number)
    
    
    def setCheckSumm(self, summ):
        self._checkSumm = toNativeType(summ)
        
    
    def setCloseType(self, closeType):
        self._closeType = toNativeType(closeType)
        
    
    def setCloseDatetime(self, closeDatetime):
        self._closeDatetime = toNativeType(closeDatetime)
        
    
    def setOperator(self, operator):
        self._operator = toNativeType(operator)
    
    
    def setDescription(self, description):
        self._description = toNativeType(description)
    
    
    def setCheckInfo(self, checkType, number, summ, closeType, closeDatetime, operator):
        self.setCheckType(checkType)
        self.setCheckNumber(number)
        self.setCheckSumm(summ)
        self.setCloseType(closeType)
        self.setCloseDatetime(closeDatetime)
        self.setOperator(operator)
    
    
    def setDeviceLogicalNumber(self, number):
        self._deviceLogicalNumber = number
    
    
    def setDeviceSerialNumber(self, number):
        self._deviceSerialNumber = number
    
    
    def setDeviceFiscal(self, isFiscal):
        self._isDeviceFiscal = bool(isFiscal)
    
    
    def setSubstructure(self, substructure):
        self._substructure = toNativeType(substructure)
    
    
    def setCashFlowArticle(self, article):
        self._cashFlowArticle = toNativeType(article)
        
    
    def setOperationTypeName(self, typeName):
        self._operationTypeName = toNativeType(typeName)
    
    
    def setOperationTypeId(self, typeId):
        self._operationTypeId = toNativeType(typeId)
    
    
    def setPersonName(self, name):
        self._personName = toNativeType(name)
        
    
    def setPersonINN(self, personINN):
        self._personINN = personINN
    
    
    def setPersonDocumentType(self, docType):
        self._personDocumentType = toNativeType(docType)
    
    
    def setPersonDocumentSerial(self, serial):
        self._personDocumentSerial = toNativeType(serial)
        
        
    def setPersonDocumentNumber(self, number):
        self._personDocumentNumber = toNativeType(number) 
        
        
    def setPersonDocumentIssuedDate(self, issuedDate):
        if isinstance(issuedDate, (basestring, QtCore.QString)):
            issuedDate = QtCore.QDate.fromString(issuedDate.strip(), COperationExportToTxtInfo.dateFormat)
        self._personDocumentIssuedDate = forceDate(issuedDate)
        
        
    def setPersonDocumentIssued(self, issued):
        self._personDocumentIssued = issued 
        
    
    def setSession(self, session):
        self._session = toNativeType(session)
        
    
    def setExpense(self, isExpense):
        isExpense = toNativeType(isExpense)
        if isinstance(isExpense, basestring):
            isExpense = forceInt(isExpense)
        self._isExpense = bool(isExpense)
        
    
    def setPersonNatural(self, isPersonNatural):
        isPersonNatural = toNativeType(isPersonNatural)
        if isinstance(isPersonNatural, basestring):
            isPersonNatural = forceInt(isPersonNatural)
        self._isPersonNatural = bool(isPersonNatural)
        
    # Общие данные по операции
    operationTypeId = property(lambda self: self._operationTypeId, setOperationTypeId,
                           doc=u"""
                                    id типа операции {rbECROperationType}.
                                    :rtype : int or None
                              """)
    operationTypeName = property(lambda self: self._operationTypeName, setOperationTypeName,
                              doc=u"""
                                        Наименование типа операции {rbECROperationType}.
                                        :rtype : basestring
                                """)
    description = property(lambda self: self._description, setDescription,
                           doc=u"""
                                        Описание операции.
                                        :rtype : basestring
                                """)
    substructure = property(lambda self: self._substructure, setSubstructure,
                              doc=u"""
                                        Подразделение.
                                        :rtype : basestring
                                """)
    cashFlowArticle = property(lambda self: self._cashFlowArticle, setCashFlowArticle,
                              doc=u"""
                                        Статья движения денежных средств.
                                        :rtype : basestring or None
                                """)


    isExpense = property(lambda self: self._isExpense, setExpense,
                              doc=u"""
                                        Метка операции по расходу.
                                        :rtype : bool
                                """)
    direction = property(lambda self: 1 if self._isExpense else 0, setExpense,
                              doc=u"""
                                        Направоение движения денежных средств.
                                            * 0 - приход
                                            * 1 - расход
                                        :rtype : int
                                """)

    # Информация о ККМ
    deviceLogicalNumber = property(lambda self: self._deviceLogicalNumber, setDeviceLogicalNumber,
                           doc=u"""
                                        Логический номер ККМ.
                                        :rtype : int or None
                                """)
    deviceSerialNumber = property(lambda self: self._deviceSerialNumber, setDeviceSerialNumber,
                                  doc=u"""
                                        Серийный номер ККМ.
                                        :rtype : basestring
                                        """)
    isDeviceFiscal = property(lambda self: self._isDeviceFiscal, setDeviceFiscal,
                              doc=u"""
                                        Признак фискализированности ККМ.
                                        :rtype : bool or None
                                """)
    deviceFiscal = property(lambda self: self._isDeviceFiscal, setDeviceFiscal,
                              doc=u"""
                                        Аналогично isDeviceFiscal.
                                        :rtype : bool or None
                                """)


    # Информация о кассире и смене
    operator = property(lambda self: self._operator, setOperator,
                         doc=u"""
                                    Оператор/кассир.
                                    :rtype : int or None
                              """)
    session = property(lambda self: self._session, setSession,
                         doc=u"""
                                    Номер смены.
                                    :rtype : int
                              """)

    # Информация о чеке
    checkType = property(lambda self: self._checkType, setCheckType,
                         doc=u"""
                                    Тип чека.
                                    %s
                                    :rtype : int or None
                              """ % u'\n'.join([u'\t* %s - %s' % (value, CCashRegisterDriverInfo.CheckType.titles[value])\
                                                    for value in sorted(CCashRegisterDriverInfo.CheckType.titles.keys())]))
    checkNumber = property(lambda self: self._checkNumber, setCheckNumber,
                           doc=u"""
                                    Номер чека.
                                    :rtype : int
                              """)
    checkSumm = property(lambda self: self._checkSumm, setCheckSumm,
                         doc=u"""
                                    Сумма чека.
                                    :rtype : float
                              """)
    closeType = property(lambda self: self._closeType, setCloseType,
                         doc=u"""
                                    Тип оплаты чека.
                                    0 - наличными
                                    1..5 - тип оплаты 1..5 (настраивается в ККМ)
                                    :rtype : int or None
                              """)
    closeDatetime = property(lambda self: self._closeDatetime, setCloseDatetime,
                         doc=u"""
                                    Дата и время закрытия чека.
                                    :rtype : datetime or None
                              """)


    # Информация о контрагенте (лицо, производящее оплату или получающее денежные средства из кассы)

    personType = property(lambda self: 1 if self._isPersonNatural else 0, setPersonNatural,
                              doc=u"""
                                        Тип контрагента.
                                            * 0 - юр. лицо
                                            * 1 - физ. лицо
                                        :rtype : int
                                """)
    isPersonNatural = property(lambda self: self._isPersonNatural, setPersonNatural,
                              doc=u"""
                                        Метка физического лица в роли контрагента.
                                        :rtype : bool
                                """)
    personName = property(lambda self: self._personName, setPersonName,
                              doc=u"""
                                        Имя/наименование контрагента (плательщика/получателя).
                                        :rtype : basestring
                                """)
    personDocumentType = property(lambda self: self._personDocumentType, setPersonDocumentType,
                              doc=u"""
                                        Тип документа, предъявленного контрагентом (для физ. лица).
                                        :rtype : basestring
                                """)
    personINN = property(lambda self: self._personINN, setPersonINN,
                         doc=u"""
                                        ИНН контрагента.
                                        :rtype : basestring
                                """)
    personDocumentSerial = property(lambda self: self._personDocumentSerial, setPersonDocumentSerial,
                              doc=u"""
                                        Серия документа, предъявленного контрагентом (для физ. лица).
                                        :rtype : basestring or None
                                """)
    personDocumentNumber = property(lambda self: self._personDocumentNumber, setPersonDocumentNumber,
                              doc=u"""
                                        Номер документа, предъявленного контрагентом (для физ. лица).
                                        :rtype : basestring or None
                                """)
    personDocumentIssuedDate = property(lambda self: self._personDocumentIssuedDate, setPersonDocumentIssuedDate,
                              doc=u"""
                                        Дата выдачи документа документа, предъявленного контрагентом (для физ. лица).
                                        :rtype : QDate
                                """)
    personDocumentIssued = property(lambda self: self._personDocumentIssued, setPersonDocumentIssued,
                              doc=u"""
                                        Кем выдан документ, предъявленный контрагентом (для физ. лица).
                                        :rtype : basestring
                                """)



class COperationInfoDialog(QtGui.QDialog, Ui_OperationInfoDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Свойства операции по кассе')
        
        self.edtDocumentIssuedDate.setCalendarPopup(True)
        self.edtDocumentIssuedDate.setDate(QtCore.QDate.currentDate())
        
        self._typesInfo = {'names' : [],
                           'idList' : [],
                           'showedIdx': []
                           }
        self.completer = None
        self.setTypesInfo(self._typesInfo)
    
    def setTypesInfo(self, typesInfo):
        self._typesInfo = typesInfo
        self.cmbOperationType.clear()
        showedIdx = typesInfo.get('showedIdx', [])
        self.cmbOperationType.addItems([itemName for itemIdx, itemName in enumerate(typesInfo.get('names', [])) if itemIdx in showedIdx])
        self.completer = QtGui.QCompleter(typesInfo.get('names', [])) #TODO: atronah: Возможно стоит удалять прежний или перенастраивать.
        self.completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.cmbOperationType.setCompleter(self.completer)
    
    def setTypeId(self, typeId):
        try:
            itemIdx = self._typesInfo.get('idList', []).index(typeId)
        except:
            itemIdx = -1
        
        itemNames = self._typesInfo.get('names', [])
        itemName = itemNames[itemIdx] if itemIdx in xrange(len(itemNames)) else u''
        cmbIdx = self.cmbOperationType.findText(itemName)
        if cmbIdx >= 0:
            self.cmbOperationType.setCurrentIndex(cmbIdx)
        else:
            self.cmbOperationType.setEditText(itemName)
    
    
    def typeId(self):
        itemName = forceString(self.cmbOperationType.currentText())
        try:
            itemIdx = self._typesInfo.get('names', []).index(itemName)
        except:
            itemIdx = -1
        
        itemId = None
        itemIdList = self._typesInfo.get('idList', [])
        
        if itemIdx in xrange(len(itemIdList)):
            itemId = itemIdList[itemIdx]
        
        return itemId
    
    
    def setPersonName(self, name):
        self.edtPersonName.setText(name)
    
    
    def personName(self):
        return self.edtPersonName.text()
    
    
    def setPersonNatural(self, isNatural):
        self.gbNaturalPersonDocument.setChecked(isNatural)
    
    
    def personNatural(self):
        return self.gbNaturalPersonDocument.isChecked()
    
    
    def setDocumentTypeList(self, nameList):
        self.cmbDocumentType.clear()
        self.cmbDocumentType.addItems(nameList)
    
    
    def setDocumentTypeName(self, typeName):
        self.cmbDocumentType.setCurrentIndex(self.cmbDocumentType.findText(typeName))
    
    
    def setDocumentType(self, typeIdx):
        self.cmbDocumentType.setCurrentIndex(typeIdx)
    
    
    def documentType(self):
        return self.cmbDocumentType.currentText() if self.personNatural() else QtCore.QString(u'')
    
    
    def setDocumentSerial(self, serial):
        self.edtDocumentSerial.setText(serial)
    
    
    def documentSerial(self):
        return self.edtDocumentSerial.text() if self.personNatural() else QtCore.QString(u'')
    
    
    def setDocumentNumber(self, number):
        self.edtDocumentNumber.setText(number)
    
    
    def documentNumber(self):
        return self.edtDocumentNumber.text() if self.personNatural() else QtCore.QString(u'')
    
    
    def setDocumentIssuedDate(self, issuedDate):
        self.edtDocumentIssuedDate.setDate(issuedDate)
    
    
    def documentIssuedDate(self):
        return self.edtDocumentIssuedDate.date() if self.personNatural() else QtCore.QDate()
    
    
    def setDocumentIssued(self, issued):
        self.edtDocumentIssued.setText(issued)
        
        
    def documentIssued(self):
        return self.edtDocumentIssued.text() if self.personNatural() else QtCore.QString(u'')
    
    
    def setPersonINN(self, personINN):
        self.edtPersonINN.setText(personINN)
    
    
    def personINN(self):
        return self.edtPersonINN.text()
    
    
    
    def setSubstructure(self, substructure):
        self.edtSubstructure.setText(substructure)
        
    
    def substructure(self):
        return self.edtSubstructure.text()
    
    
    def setCashFlowArticle(self, article):
        self.edtCashFlowArticle.setText(article)
    
    
    def cashFlowArticle(self):
        return self.edtCashFlowArticle.text()
        
    
    def opearationInfo(self):
        operationInfo = CCashRegisterOperationInfo()
        
        operationInfo.setPersonNatural(self.personNatural())
        operationInfo.setPersonName(self.personName())
        operationInfo.setPersonINN(self.personINN())
        operationInfo.setPersonDocumentType(self.documentType())
        operationInfo.setPersonDocumentSerial(self.documentSerial())
        operationInfo.setPersonDocumentNumber(self.documentNumber())
        operationInfo.setPersonDocumentIssuedDate(self.documentIssuedDate())
        operationInfo.setPersonDocumentIssued(self.documentIssued())
        operationInfo.setSubstructure(self.substructure())
        operationInfo.setOperationTypeId(self.typeId())
        operationInfo.setCashFlowArticle(self.cashFlowArticle())
        return operationInfo
        
        
    @QtCore.pyqtSlot()
    def accept(self):
        canAccept = True
        message = u'Заполните пустые поля'
        if self.typeId() is None and self._typesInfo.get('idList', []):
            canAccept = False
            message = u'Укажите вид операции'
        
        elif self.cashFlowArticle().isEmpty():
            canAccept = False
            message = u'Укажите статью движения денежных средств'
            
        if canAccept:
            QtGui.QDialog.accept(self)
        else:
            QtGui.QMessageBox.warning(self, u'Не заполнены данные', message)
        
    
    
    
    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbOperationType_editTextChanged(self, text):
        text = toNativeType(text)
        if text not in self._typesInfo.get('names', []):
            self.cmbOperationType.lineEdit().setStyleSheet(u'background-color: red')
        else:
            self.cmbOperationType.lineEdit().setStyleSheet(u'')


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCashFlowArticle_textChanged(self, text):
        self.edtCashFlowArticle.setStyleSheet(u'background-color: red' if text.isEmpty() else u'')
            


class COperationExportToTxtInfo:
    dateFormat = u'dd.MM.yyyy'
    
#    header = u'Начало документа'
    
#    closeDatetime = u'Дата операции'
#    checkNumber = u'Внутренний номер операции'
#    isExpense = u'Направление движения'
#    isPersonNatural = u'Получатель/Плательщик вид'
#    personName = u'Получатель/Плательщик'
#    personDocumentType = u'Тип документа'
#    personDocumentSerial = u'Серия паспорта'
#    personDocumentNumber = u'Номер паспорта'
#    personDocumentIssuedDate = u'Дата выдачи документа'
#    personDocumentIssued = u'Кем выдано (документ)'
#    personINN = u'ИНН контрагента'
#    substructure = u'Подразделение'
#    cashFlowArticle = u'Статья движения денежных средств'
#    checkSumm = u'Сумма операции'
#    
#    description = u'Описание платежа'
#    
#    operationType = u'Вид операции'
    
    @staticmethod
    def dateToString(date):
        date = forceDate(date)
        return forceString(date.toString(COperationExportToTxtInfo.dateFormat))
                           
    
    @staticmethod
    def dateFromString(stringDate):
        return QtCore.QDate.fromString(stringDate.strip(), COperationExportToTxtInfo.dateFormat)
    
    
    formatedDocumentIssuedDate = property(lambda self: COperationExportToTxtInfo.dateToString(CCashRegisterOperationInfo.personDocumentIssuedDate.__get__(self)),
                                          lambda self, value: CCashRegisterOperationInfo.personDocumentIssuedDate.__set__(self, COperationExportToTxtInfo.dateFromString(value)))
    
    formatedClosedDatetime = property(lambda self: COperationExportToTxtInfo.dateToString(CCashRegisterOperationInfo.closeDatetime.__get__(self)),
                                      lambda self, value: CCashRegisterOperationInfo.closeDatetime.__set__(self, COperationExportToTxtInfo.dateFromString(value)))
    
    beginField = u'Начало документа' 
    
    fields = [
              (u'Дата операции', formatedClosedDatetime),
              (u'Внутренний номер операции', CCashRegisterOperationInfo.checkNumber),
              (u'Направление движения', CCashRegisterOperationInfo.direction),
              (u'Получатель/Плательщик вид', CCashRegisterOperationInfo.personType),
              (u'Получатель/Плательщик', CCashRegisterOperationInfo.personName),
              (u'ИНН/КПП контрагента', CCashRegisterOperationInfo.personINN),
              (u'Номер паспорта', CCashRegisterOperationInfo.personDocumentNumber),
              (u'Серия паспорта', CCashRegisterOperationInfo.personDocumentSerial),
              (u'Тип документа', CCashRegisterOperationInfo.personDocumentType),
              (u'Дата выдачи документа', formatedDocumentIssuedDate),
              (u'Кем выдано (документ)', CCashRegisterOperationInfo.personDocumentIssued),
              (u'Подразделение', CCashRegisterOperationInfo.substructure),
              (u'Статья движения денежных средств', CCashRegisterOperationInfo.cashFlowArticle),
              (u'Сумма операции', CCashRegisterOperationInfo.checkSumm),
              (u'Описание платежа', CCashRegisterOperationInfo.description),
              (u'Вид операции', CCashRegisterOperationInfo.operationTypeName)
              ]
    
    endField = u'Конец документа'
    
    
#    deviceNameToTitle = {'LogicalNumber' : u'Логический номер',
#                         'SerialNumber' : u'Серийный номер',
#                         'Fiscal' : u'Касса фискализирована'
#                         }
#    
#    
#    documentNameToTitle = {
#                           'INN' : u'ИНН/КПП контрагента',
#                           'DocumentType' : u'Тип документа',
#                           'DocumentSerial' : u'Серия паспорта',
#                           'DocumentNumber' : u'Номер паспорта',
#                           'DocumentIssuedDate' : u'Дата выдачи документа',
#                           'DocumentIssued' : u'Кем выдано (документ)', 
#                           }

