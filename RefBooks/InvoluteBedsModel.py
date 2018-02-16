# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.InDocTable import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CDateInDocTableCol, \
                               CEnumInDocTableCol, CIntInDocTableCol, CRBInDocTableCol
from library.Utils      import forceInt


class CHospitalBedsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'OrgStructure_HospitalBed', 'id', 'master_id', parent)
        self.addCol(CInDocTableCol(u'Код койки', 'code', 10))
        self.addCol(CInDocTableCol(u'Код палаты', 'ward', 10))
        self.addCol(CInDocTableCol(u'Наименование', 'name', 20))
        self.addCol(CBoolInDocTableCol(u'Штат', 'isPermanent', 10))
        self.addCol(CRBInDocTableCol(u'Тип', 'type_id', 10, 'rbHospitalBedType', prefferedWidth=150))
        self.addCol(CRBInDocTableCol(u'Профиль', 'profile_id', 10, 'rbHospitalBedProfile', prefferedWidth=150))
        self.addCol(CIntInDocTableCol(u'Смены', 'relief', 20, low=0,  high=9))
        self.addCol(CRBInDocTableCol(u'Режим', 'schedule_id', 10, 'rbHospitalBedShedule', prefferedWidth=150))
        self.addCol(CEnumInDocTableCol( u'Пол',            'sex',  5, ['', u'М', u'Ж']))
        self.addCol(CInDocTableCol(     u'Возраст',        'age',  12))
        self.addCol(CDateInDocTableCol(u'Начало',   'begDate', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Окончание', 'endDate', 15, canBeEmpty=True))
        self.__involuteBeds = []
        self.__involuteBedsModel = None


    def setInvoluteBedsModel(self,  model):
        self.__involuteBedsModel = model


    def involuteBeds(self, row):
        if row >= len(self.__involuteBeds):
            self.__involuteBeds.extend([None]*(row-len(self.__involuteBeds)+1))
        if self.__involuteBeds[row] == None:
            self.__involuteBeds[row] = []
        return self.__involuteBeds[row]


    def upRow(self, row):
        self.__involuteBeds[row-1], self.__involuteBeds[row] = self.__involuteBeds[row], self.__involuteBeds[row-1]
        return CInDocTableModel.upRow(self, row)


    def downRow(self, row):
        self.__involuteBeds[row+1], self.__involuteBeds[row] = self.__involuteBeds[row], self.__involuteBeds[row+1]
        return CInDocTableModel.downRow(self, row)


    def insertRecord(self, row, record):
        CInDocTableModel.insertRecord(self, row, record)
        self.__involuteBeds.insert(row, [])


    def removeRows(self, row, count, parentIndex = QtCore.QModelIndex()):
        result = CInDocTableModel.removeRows(self, row, count, parentIndex)
        if result:
            del self.__involuteBeds[row:row+count]
        return result


    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        db = QtGui.qApp.db
        factorTable = db.table('HospitalBed_Involute')
        self.__involuteBeds = []
        if self.__involuteBedsModel:
            self.__involuteBedsModel.blockSignals(True)
            try:
                for row, item in enumerate(self.items()):
                    itemId = forceInt(item.value('id'))
                    self.__involuteBedsModel.setItems(self.involuteBeds(row))
                    self.__involuteBedsModel.loadItems(itemId)
                    self.__involuteBeds[row] = self.__involuteBedsModel.items()
            finally:
                self.__involuteBedsModel.blockSignals(False)
            self.__involuteBedsModel.reset()
            self.__involuteBedsModel.setItems(self.involuteBeds(0))


    def saveItems(self, masterId):
        CInDocTableModel.saveItems(self, masterId)
        saveItems = self.__involuteBedsModel.items()
        if self.__involuteBedsModel:
            try:
                for row, item in enumerate(self.items()):
                    itemId = forceInt(item.value('id'))
                    self.__involuteBedsModel.setItems(self.involuteBeds(row))
                    self.__involuteBedsModel.saveItems(itemId)
                self.__involuteBedsModel.setItems(saveItems)
            finally:
                self.__involuteBedsModel.blockSignals(False)


class CInvoluteBedsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'HospitalBed_Involute', 'id', 'master_id', parent)
        self.addCol(CEnumInDocTableCol(u'Причина сворачивания', 'involuteType', 16, [u'нет сворачивания', u'ремонт', u'карантин']))
        self.addCol(CDateInDocTableCol(u'Начало сворачивания', 'begDateInvolute', 20, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Окончание сворачивания', 'endDateInvolute', 20, canBeEmpty=True))

