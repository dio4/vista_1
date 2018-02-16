# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
from PyQt4 import QtGui

__author__ = 'mdldml'


from Events.EventInfo import CEventInfo, CFinanceInfo
from library.PrintInfo import CInfo, CDateInfo, CRBInfo
from library.Utils import forceRef, forceDate, forceString, forceInt, forceBool


class CDrugRecipeInfo(CInfo):
    def __init__(self, context, drugRecipeId, record=None):
        CInfo.__init__(self, context, record=record)
        self.id = drugRecipeId

    def setRecord(self, record):
        self._event = self.getInstance(CEventInfo, forceRef(record.value('event_id')))
        self._dateTime = CDateInfo(forceDate(record.value('dateTime')))
        self._number = forceString(record.value('number'))
        self._socCode = forceString(record.value('socCode'))
        self._pregCard = forceInt(record.value('pregCard'))
        self._finance = self.getInstance(CFinanceInfo, forceRef(record.value('finance_id')))
        self._percentage = forceInt(record.value('percentage'))
        self._mkb = forceString(record.value('mkb'))
        self._formularyItem = self.getInstance(CDloDrugFormularyItemInfo, forceRef(record.value('formularyItem_id')))
        self._dosage = forceString(record.value('dosage'))
        self._qnt = forceInt(record.value('qnt'))
        self._duration = forceInt(record.value('duration'))
        self._numPerDay = forceInt(record.value('numPerDay'))
        self._signa = forceString(record.value('signa'))
        self._isVk = forceInt(record.value('isVk'))
        self._term = forceInt(record.value('term'))
        self._status = forceInt(record.value('status'))
        self._sentToMiac = forceInt(record.value('sentToMiac'))
        self._errorCode = forceString(record.value('errorCode'))
        self._printMnn = forceInt(record.value('printMnn'))

    def _load(self):
        record = self._record
        if record is None:
            db = QtGui.qApp.db
            record = db.getRecord('DrugRecipe', '*', self.id)
        self.setRecord(record if record else db.table('DrugRecipe').newRecord())
        return bool(record)

    event = property(lambda self: self.load()._event)
    dateTime = property(lambda self: self.load()._dateTime)
    number = property(lambda self: self.load()._number)
    socCode = property(lambda self: self.load()._socCode)
    pregCard = property(lambda self: self.load()._pregCard)
    finance = property(lambda self: self.load()._finance)
    percentage = property(lambda self: self.load()._percentage)
    mkb = property(lambda self: self.load()._mkb)
    formularyItem = property(lambda self: self.load()._formularyItem)
    dosage = property(lambda self: self.load()._dosage)
    qnt = property(lambda self: self.load()._qnt)
    duration = property(lambda self: self.load()._duration)
    numPerDay = property(lambda self: self.load()._numPerDay)
    signa = property(lambda self: self.load()._signa)
    isVk = property(lambda self: self.load()._isVk)
    term = property(lambda self: self.load()._term)
    status = property(lambda self: self.load()._status)
    sentToMiac = property(lambda self: self.load()._sentToMiac)
    errorCode = property(lambda self: self.load()._errorCode)
    printMnn = property(lambda self: self.load()._printMnn)

class CDloDrugFormularyItemInfo(CInfo):
    def __init__(self, context, formularyItemId):
        CInfo.__init__(self, context)
        self.id = formularyItemId

    def setRecord(self, record):
        self._code = forceString(record.value('code'))
        self._mnn = self.getInstance(CMNNInfo, forceRef(record.value('mnn_id')))
        self._issueForm = self.getInstance(CIssueFormInfo, forceRef(record.value('issueForm_id')))
        self._name = forceString(record.value('name'))
        self._dosageQnt = forceInt(record.value('dosageQnt'))
        self._dosage = self.getInstance(CDosageInfo, forceRef(record.value('dosage_id')))
        self._tradeName = self.getInstance(CTradeNameInfo, forceRef(record.value('tradeName_id')))
        self._qnt = forceInt(record.value('qnt'))
        self._producer = forceString(record.value('producer'))
        self._isDrugs = forceBool(record.value('isDrugs'))
        self._federalCode = forceInt(record.value('federalCode'))
        self._dosageLs = forceString(record.value('dosageLs'))
        self._isDevice = forceInt(record.value('isDevice'))

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord('DloDrugFormulary_Item', '*', self.id)
        self.setRecord(record if record else db.table('DrugRecipe').newRecord())
        return bool(record)

    code = property(lambda self: self.load()._code)
    mnn = property(lambda self: self.load()._mnn)
    issueForm = property(lambda self: self.load()._issueForm)
    name = property(lambda self: self.load()._name)
    dosageQnt = property(lambda self: self.load()._dosageQnt)
    dosage = property(lambda self: self.load()._dosage)
    tradeName = property(lambda self: self.load()._tradeName)
    qnt = property(lambda self: self.load()._qnt)
    producer = property(lambda self: self.load()._producer)
    isDrugs = property(lambda self: self.load()._isDrugs)
    federalCode = property(lambda self: self.load()._federalCode)
    dosageLs = property(lambda self: self.load()._dosageLs)
    isDevice = property(lambda self: self.load()._isDevice)


class CMNNInfo(CRBInfo):
    tableName = 'dlo_rbMNN'

    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def setRecord(self, record):
        self._code = forceString(record.value('code'))
        self._name = forceString(record.value('name'))
        self._latinName = forceString(record.value('latinName'))

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id)
        self.setRecord(record if record else db.table(self.tableName).newRecord())
        return bool(record)

    latinName = property(lambda self: self.load()._latinName)


class CTradeNameInfo(CRBInfo):
    tableName = 'dlo_rbTradeName'

    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def setRecord(self, record):
        self._code = forceString(record.value('code'))
        self._name = forceString(record.value('name'))
        self._latinName = forceString(record.value('latinName'))

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id)
        self.setRecord(record if record else db.table(self.tableName).newRecord())
        return bool(record)

    name = property(lambda self: self.load()._name)
    latinName = property(lambda self: self.load()._latinName)


class CDosageInfo(CRBInfo):
    tableName = 'dlo_rbDosage'


class CIssueFormInfo(CRBInfo):
    tableName = 'dlo_rbIssueForm'

    def __init__(self, context, id):
        CInfo.__init__(self, context)
        self.id = id

    def setRecord(self, record):
        self._code = forceString(record.value('code'))
        self._name = forceString(record.value('name'))
        self._latinName = forceString(record.value('latinName'))

    def _load(self):
        db = QtGui.qApp.db
        record = db.getRecord(self.tableName, '*', self.id)
        self.setRecord(record if record else db.table(self.tableName).newRecord())
        return bool(record)

    latinName = property(lambda self: self.load()._latinName)
