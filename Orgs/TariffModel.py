# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 28.06.2013

@author: atronah
"""

from PyQt4 import QtCore, QtGui

from Registry.ClientEditDialog import CPolyclinicInDocTableCol
from library.CashRegister.CheckItemModel import CCheckItem
from library.InDocTable import CInDocTableModel, CRBInDocTableCol, CEnumInDocTableCol, CDateInDocTableCol, \
    CInDocTableCol, CFloatInDocTableCol
from library.Utils import forceInt, forceTr, toVariant
from library.crbcombobox import CRBComboBox


class CTariffModel(CInDocTableModel):
    tariffTypeNames = [u'посещение',                                #0
                       u'событие',                                  #1
                       u'мероприятие по количеству',                #2
                       u'визит-день',                               #3
                       u'событие по койко-дням',                    #4
                       u'мероприятие по УЕТ',                       #5
                       u'мероприятие по количеству и тарифу койки', #6
                       u'визиты по мероприятию',                    #7
                       u'визиты по МЭС',                            #8
                       u'событие по МЭС',                           #9
                       u'событие по МЭС и длительности',            #10
                       u'мероприятие по МЭС',                       #11
                       u'посещение с одним диагнозом в обращении',  #12
                       u'стандарт по КСГ',                          #13
                       u'посещение по УЕТ услуги',                  #14
                       u'событие по ВМП',                           #15
                       u'услуга по диспансеризации',                #16
                       ]

    vat = [u'без НДС', '18%', '10%']
    vat_values = [CCheckItem.VAT_NONE, CCheckItem.VAT_18, CCheckItem.VAT_10]
    pricePrecision = 2

    def __init__(self, parent):
        self.retranslate()
        CInDocTableModel.__init__(self, 'Contract_Tariff', 'id', 'master_id', parent)
        self.parent=parent
        self.addCol(CRBInDocTableCol(u'Событие',            'eventType_id',  30, 'EventType')).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Тарифицируется',   'tariffType',     5, CTariffModel.tariffTypeNames)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Услуга',             'service_id',    30, 'rbService', showFields=CRBComboBox.showCodeAndName)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id',   30,  'rbSpeciality')).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Тарифная категория', 'tariffCategory_id',    30, 'rbTariffCategory')).setSortable(True)
        self.addCol(CInDocTableCol(u'Код по МКБ',           'MKB',           8)).setSortable(True)
        self.addCol(CDateInDocTableCol(u'Дата начала',      'begDate',      10, canBeEmpty=True)).setSortable(True)
        self.addCol(CDateInDocTableCol(u'Дата окончания',   'endDate',      10, canBeEmpty=True)).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Пол',              'sex',           3, [u'', u'М', u'Ж']))
        self.addCol(CInDocTableCol(u'Возраст',              'age',           8))
        self.addCol(CRBInDocTableCol(u'Тип',                'attachType_id', 30, 'rbAttachType'))
        self.addCol(CPolyclinicInDocTableCol(u'ЛПУ',        'attachLPU_id',       15))
        self.addCol(CRBInDocTableCol(u'Ед.Уч.',             'unit_id',       8, 'rbMedicalAidUnit'))
        self.addCol(CFloatInDocTableCol(u'Кол-во',          'amount',        8))
        self.addCol(CFloatInDocTableCol(u'УЕТ',             'uet',           4, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Цена',            'price',         8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Второй тариф с',  'frag1Start', 8, precision=0))
        self.addCol(CFloatInDocTableCol(u'Сумма второго тарифа', 'frag1Sum',   8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Цена второго тарифа',  'frag1Price',  8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Третий тариф с',  'frag2Start', 8, precision=0))
        self.addCol(CFloatInDocTableCol(u'Сумма третьего тарифа', 'frag2Sum',   8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Цена третьего тарифа',  'frag2Price',  8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Фед.цена',        'federalPrice',        8, precision=self.pricePrecision))
        self.addCol(CFloatInDocTableCol(u'Фед.предел',      'federalLimitation',   8))
        self.addCol(CEnumInDocTableCol(u'НДС',              'vat',  8, CTariffModel.vat, precision=self.pricePrecision))

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

                # i4707 set rounded prices
                record.setValue('price', round(record.value('price').toDouble()[0], self.pricePrecision))
                record.setValue('frag1Sum', round(record.value('frag1Sum').toDouble()[0], self.pricePrecision))
                record.setValue('frag2Price', round(record.value('frag2Price').toDouble()[0], self.pricePrecision))
                record.setValue('federalPrice', round(record.value('federalPrice').toDouble()[0], self.pricePrecision))

                itemId = db.insertOrUpdate(table, outRecord)
                record.setValue(idFieldName, toVariant(itemId))
                for col in self.cols():
                    # сохранение внешних данных столбцов, если такие имеются
                    col.saveExternalData(record)
                idList.append(itemId)

            cond = [table[masterIdFieldName].eq(masterId),
                      'NOT ('+table[idFieldName].inlist(idList)+')']

            self.doAfterSaving(cond)
            self.setDirty(False)

    def retranslate(self):
        for idx in xrange(len(self.tariffTypeNames)):
            name = self.tariffTypeNames[idx]
            if u'МЭС' in name:
                self.tariffTypeNames[idx] = name.replace(u'МЭС', forceTr(u'МЭС', u'TariffModel'))



    def serviceDisabled(self, row):
        return row < len(self.items()) and forceInt(self.items()[row].value('tariffType')) == 1


    def cellReadOnly(self, index):
        if index.isValid():
            row = index.row()
            column = index.column()
            if column == 2 and self.serviceDisabled(row):
                return True
        return False


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role==QtCore.Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 2 and self.serviceDisabled(row):
                    return QtCore.QVariant()
            if column == 24:
                if row<len(self.items()):
                    record = self.items()[row]
                    vat = forceInt(record.value('vat'))
                    if vat and 0 <= vat < 3:
                        return QtCore.QVariant(self.vat[vat])
        return CInDocTableModel.data(self, index, role)


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        if column == 1:
            if forceInt(value) == 1:
                if row<len(self.items()):
                    record = self.items()[row]
                    record.setValue('service_id', QtCore.QVariant())
            self.emitCellChanged(row, 2)
        return CInDocTableModel.setData(self, index, value, role)
#
# ###################################################################
#