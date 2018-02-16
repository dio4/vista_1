# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

from Events.Utils import CPayStatus
from PyQt4 import QtCore, QtGui
from library.CashRegister.CashRegisterDriverInfo import CCashRegisterDriverInfo
from library.Utils import forceString, forceDecimal, forceDouble, forceInt

'''
Created on 26.09.2013

@author: atronah
'''


class CCheckItem(object):
    precision = 0.0001

    VAT_BY_SECTION = 0
    VAT_0 = 1
    VAT_10 = 2
    VAT_18 = 3
    VAT_NONE = 4
    VAT_110_10 = 5
    VAT_118_18 = 6

    VAT_CHOICES = [
        u'По секции',
        u'НДС 0%',
        u'НДС 10%',
        u'НДС 18%',
        u'Без НДС',
        u'НДС 110/10',
        u'НДС 118/18',
    ]

    def __init__(self, name=u'', quantity=forceDecimal(1.0), price=forceDecimal(0.0), payStatus=None,
                 department=0, discountInfo=(1, 0), userInfo=None, vat=VAT_0, clientId=None):
        self._name = name
        self._quantity = quantity
        self._price = price
        self._department = department
        self._discountType = discountInfo[0]
        self._discountValue = forceDecimal(discountInfo[1])
        self._payStatus = payStatus
        self._isSelected = bool(payStatus == CPayStatus.exposed)
        self._payStatusChanged = False
        self._vat = vat
        self._clientId = clientId

        self.errorList = []
        self.lastCheckInfo = {}
        self.userInfo = userInfo

    @property
    def vat(self):
        return self._vat

    @vat.setter
    def vat(self, value):
        self._vat = value

    @property
    def department(self):
        return self._department

    @department.setter
    def department(self, value):
        self._department = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price

    @property
    def sum(self):
        return self.summ()

    @property
    def isSelected(self):
        return self._isSelected

    @isSelected.setter
    def isSelected(self, selected):
        self._isSelected = selected

    @property
    def discountValue(self):
        return self._discountValue

    @discountValue.setter
    def discountValue(self, value):
        if value < CCheckItem.precision:
            value = forceDecimal(0)
        if self.discountType == CCashRegisterDriverInfo.DiscountType.percent:
            if value > forceDecimal(100):
                value = forceDecimal(100)
        elif self.discountType == CCashRegisterDriverInfo.DiscountType.currency:
            value = min(self.summ(False), value)
        self._discountValue = value

    @property
    def discountType(self):
        return self._discountType

    @discountType.setter
    def discountType(self, newType):
        if newType not in [CCashRegisterDriverInfo.DiscountType.percent,
                           CCashRegisterDriverInfo.DiscountType.currency]:
            newType = CCashRegisterDriverInfo.DiscountType.percent
        self._discountType = newType
        self.discountValue = self.discountValue  # atronah: пересчет скидки после смены типа

    @property
    def payStatus(self):
        return self._payStatus

    @payStatus.setter
    def payStatus(self, newPayStatus):
        if newPayStatus == self._payStatus:
            return
        assert newPayStatus in [CPayStatus.exposed, CPayStatus.payed, CPayStatus.refused]
        self._payStatus = newPayStatus
        self._payStatusChanged = True

    @property
    def payStatusChanged(self):
        return self._payStatusChanged

    def summ(self, withDiscount=False):
        discountSumm = self.quantity * self.price
        if withDiscount:
            if self._discountType == CCashRegisterDriverInfo.DiscountType.percent:
                discountSumm -= forceDecimal(discountSumm) * forceDecimal(self.discountValue) / forceDecimal(100)
            else:
                discountSumm -= forceDecimal(self.discountValue)
        return discountSumm

    def isCorrect(self):
        self.errorList = []
        if self.quantity < 0:
            self.errorList.append(u'отрицательное количество')
        elif self.quantity < CCheckItem.precision:
            self.errorList.append(u'нулевое количество')
        if self.price < 0:
            self.errorList.append(u'отрицательная цена')
        elif self.price < CCheckItem.precision:
            self.errorList.append(u'нулевая цена')
        if self.department not in xrange(17):
            self.errorList.append(u'неверная секция: %d' % self.department)
        # Проверка корректности процентной скидки (тип = 1)
        if self.discountType == 1 and not (forceDecimal(0) <= self.discountValue <= forceDecimal(100)):
            self.errorList.append(u'ошибочная скидка: %d%%' % self.discountValue)
        if self.payStatus not in [None, CPayStatus.exposed, CPayStatus.payed, CPayStatus.refused]:
            self.errorList.append(u'ошибочный статус оплаты: %d' % self.payStatus)
        return len(self.errorList) == 0

    @classmethod
    def fromTuple(cls, t):
        if len(t) < 3:
            return None
        if len(t) >= 5 and (not isinstance(t[4], tuple) or len(t[4]) < 2):
            return None
        if not isinstance(t[0], basestring):
            return None

        return cls(t[:5])

    def __str__(self):
        strItems = [u'%s' % self.name,
                    u'кол-во = %0.3f' % forceDouble(self.quantity),
                    u'цена = %0.3f' % forceDouble(self.price),
                    u'Статус оплаты = %s' % (CPayStatus.names[self.payStatus] if self.payStatus in xrange(len(CPayStatus.names)) else u'<ошибка>'),
                    u'Отдел = %s' % self.department,
                    u'скидка = %0.3f%s' % (forceDouble(self.discountValue), u'%' if self.discountType == 1 else u'')]

        return ', '.join(strItems)


class CVATItemDelegate(QtGui.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        for label in CCheckItem.VAT_CHOICES:
            editor.addItem(label)
        return editor

    def setEditorData(self, editor, index):
        item = index.internalPointer()
        editor.setCurrentIndex(item.vat)

    def setModelData(self, editor, model, index):
        item = index.internalPointer()
        item.vat = editor.currentIndex()


class CCheckItemModel(QtCore.QAbstractTableModel):
    columnInfo = {'name':       {'index': 0, 'title': u'Наименование'},
                  'quantity':   {'index': 1, 'title': u'Кол-во'},
                  'price':      {'index': 2, 'title': u'Цена'},
                  'sum':        {'index': 3, 'title': u'Сумма'},
                  'discount':   {'index': 4, 'title': u'Сумма со скидкой\n(скидка, %)'},
                  'vat':        {'index': 5, 'title': u'НДС'}
                  }
    # Сигнал о необходимости вывести сообщение для пользователя (сообщение, выделить_красным)
    showedMessage = QtCore.pyqtSignal(QtCore.QString, bool)

    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._headerData = dict([(info['index'], info['title']) for info in self.columnInfo.values()])
        self._items = []
        self._currentCheckType = None
        self._editable = True

    def setAppendEnabled(self, enabled):
        self._editable = bool(enabled)

    def showMessage(self, message, isRed=False):
        self.showedMessage.emit(message, isRed)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        row = index.row()
        column = index.column()
        if row not in xrange(self.rowCount()) or column not in xrange(self.columnCount()):
            return QtCore.Qt.NoItemFlags

        result = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if self._editable and column != self.columnInfo['sum']['index']:
            result |= QtCore.Qt.ItemIsEditable

        if column == self.columnInfo['name']['index']:
            result |= QtCore.Qt.ItemIsUserCheckable

        return result

    def applyDiscount(self, value, discountType=CCashRegisterDriverInfo.DiscountType.percent):
        for row, item in enumerate(self.items()):
            item.discountValue = value
            item.discountType = discountType
            idx = self.index(row, self.columnInfo['discount']['index'])
            self.dataChanged.emit(idx, idx)

    def rowCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self._items) + (1 if self._editable else 0)

    def columnCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self.columnInfo.keys())

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section in self._headerData.keys():
                    return QtCore.QVariant(self._headerData[section])
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        column = index.column()
        rowCount = self.rowCount()
        if row not in xrange(rowCount):
            return QtCore.QVariant()

        if self._editable and row == (rowCount - 1):
            if role == QtCore.Qt.DisplayRole and column == self.columnInfo['name']['index']:
                return QtCore.QVariant(u'<Добавить элемент чека>')
            return QtCore.QVariant()

        checkItem = self.items()[row]
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == self.columnInfo['name']['index']:
                return QtCore.QVariant(unicode(checkItem.name))
            elif column == self.columnInfo['quantity']['index']:
                return QtCore.QVariant(unicode(checkItem.quantity))
            elif column == self.columnInfo['price']['index']:
                return QtCore.QVariant(unicode(checkItem.price))
            elif column == self.columnInfo['sum']['index']:
                return QtCore.QVariant(unicode(checkItem.summ(False)))
            elif column == self.columnInfo['discount']['index']:
                if role == QtCore.Qt.EditRole:
                    return QtCore.QVariant(checkItem.discountValue)

                return QtCore.QVariant(u'%s (%s %s)' %
                                       (checkItem.summ(True), checkItem.discountValue,
                                        u'%' if checkItem.discountType == CCashRegisterDriverInfo.DiscountType.percent else u'руб.'))
            elif column == self.columnInfo['vat']['index']:
                return QtCore.QVariant(unicode(CCheckItem.VAT_CHOICES[checkItem.vat]))
        elif role == QtCore.Qt.CheckStateRole:
            if column == self.columnInfo['name']['index']:
                return QtCore.QVariant(QtCore.Qt.Checked if checkItem.isSelected else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.BackgroundRole:
            if checkItem.payStatus == CPayStatus.refused:
                return QtCore.QVariant(QtGui.QColor(255, 128, 128))
            elif checkItem.payStatus == CPayStatus.payed:
                return QtCore.QVariant(QtGui.QColor(128, 255, 128))
        elif role == QtCore.Qt.ToolTipRole:
            payStatusText = u'-'
            if checkItem.payStatus is not None:
                payStatusText = CPayStatus.names[checkItem.payStatus] if checkItem.payStatus in xrange(
                    len(CPayStatus.names)) \
                    else u'<ошибка>'
            return QtCore.QVariant('\n'.join([u'Элемент чека',
                                              u'%s для обработки' % u'Выбран' if checkItem.isSelected else u'Не выбран',
                                              u'Статус оплаты: %s' % payStatusText
                                              ]))
        return QtCore.QVariant()

    def setCurrentCheckType(self, checkType):
        u"""
        Установка типа текущего чека. Влияет на контроль выбора (установки в состояние "выбран) элементов модели
        :param checkType: тип чека
        :return: None
        """
        self._currentCheckType = checkType if checkType in CCashRegisterDriverInfo.CheckType.titles.keys() else None
        self.checkAllItemsSelect()

    def checkItemSelect(self, item):
        result = (True, u'', True)  # (флаг_ошибки, текст_ошибки, может_быть_проигнорированно)
        if not self._currentCheckType in CCashRegisterDriverInfo.CheckType.titles.keys():
            return result

        if item.isSelected and not item.isCorrect():
            result = (False, u'Элемент чека "%s" некорректен (%s)' % (item, ', '.join(item.errorList)), False)

        elif item.payStatus is None:
            result = (True, u'', True)

        else:
            warningPayStatusList = []
            if self._currentCheckType == CCashRegisterDriverInfo.CheckType.sale:
                warningPayStatusList = [CPayStatus.payed, CPayStatus.refused]
            elif self._currentCheckType in [CCashRegisterDriverInfo.CheckType.returnSale,
                                            CCashRegisterDriverInfo.CheckType.annulateSale]:
                warningPayStatusList = [CPayStatus.exposed, CPayStatus.refused]

            # Если статус оплаты выбраного элемента соответствует ошибочному статусу
            # или статус оплаты невыбранного элемента соответствует верному статусу (отсутствует среди списка ошибочных)
            if not (item.payStatus in warningPayStatusList) ^ item.isSelected:
                result = (False,
                          u'Статус оплаты элемента (%s) не соответствует типу чека (%s)' % (
                              CPayStatus.names[item.payStatus],
                              CCashRegisterDriverInfo.CheckType.title(self._currentCheckType)),
                          True)

        return result

    def checkAllItemsSelect(self):
        warningsItems = []
        for item in self.items():
            if not self.checkItemSelect(item)[0]:
                warningsItems.append(item)

        if warningsItems:
            userChoise = QtGui.QMessageBox.warning(QtGui.qApp.activeWindow(),
                                                   u'Внимание!',
                                                   '\n'.join([u'Некорректный выбор элементов для выбранного типа чека',
                                                              u'Изменить на корректный?']),
                                                   buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.Ignore,
                                                   defaultButton=QtGui.QMessageBox.Yes)
            if userChoise == QtGui.QMessageBox.Yes:
                for item in warningsItems:
                    item.isSelected = not item.isSelected
                self.reset()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        row = index.row()
        column = index.column()
        rowCount = self.rowCount()
        if row not in xrange(rowCount):
            return False

        if self._editable and row == (rowCount - 1):
            self.beginInsertRows(index.parent(), row, row)
            self._items.append(CCheckItem(payStatus=None))
            self.endInsertRows()

        if role == QtCore.Qt.CheckStateRole and column == self.columnInfo['name']['index']:
            item = self.items()[row]
            item.isSelected = (value != QtCore.Qt.Unchecked)
            checkResult, checkMessage, canIgnore = self.checkItemSelect(item)
            if not checkResult:
                buttons = QtGui.QMessageBox.Ok
                if canIgnore:
                    buttons |= QtGui.QMessageBox.Ignore
                userChoise = QtGui.QMessageBox.warning(QtGui.qApp.activeWindow(),
                                                       u'Внимание!',
                                                       checkMessage,
                                                       buttons=buttons,
                                                       defaultButton=QtGui.QMessageBox.Ok)
                if userChoise == QtGui.QMessageBox.Ok:
                    item.isSelected = not item.isSelected
                    return False
            self.dataChanged.emit(index, index)
            return True

        if role == QtCore.Qt.EditRole and self._editable:
            item = self.items()[row]
            sumIndex = self.index(index.row(), self.columnInfo['sum']['index'])
            if column == self.columnInfo['name']['index']:
                item.name = forceString(value)
                self.dataChanged.emit(index, index)
                return True
            elif column == self.columnInfo['quantity']['index']:
                newValue = forceDecimal(value)
                if newValue < forceDecimal(0):
                    return False
                item.quantity = newValue
                self.dataChanged.emit(index, sumIndex)
                return True
            elif column == self.columnInfo['price']['index']:
                newValue = forceDecimal(value)
                if newValue < forceDecimal(0):
                    return False
                item.price = newValue
                self.dataChanged.emit(index, sumIndex)
                return True
            elif column == self.columnInfo['discount']['index']:
                newValue = forceDecimal(value)
                if newValue <= CCheckItem.precision:
                    newValue = forceDecimal(0)
                item.discountType = CCashRegisterDriverInfo.DiscountType.percent
                item.discountValue = forceDecimal(value)
                return True
            elif column == self.columnInfo['vat']['index']:
                item.vat = forceInt(value)
                return True
        return False

    def totalSumm(self, onlySelected=True, withDiscount=False):
        totalSumm = forceDecimal(0.0)
        for item in self.items():
            if item.isSelected or not onlySelected:
                totalSumm += item.summ(withDiscount)
        return totalSumm

    def items(self):
        return self._items

    def selectedItems(self):
        selectedItems = []
        for item in self.items():
            if item.isSelected:
                selectedItems.append(item)
        return selectedItems

    def setItems(self, items):
        self._items = []
        if isinstance(items, CCheckItem):
            self._items = [items]
        elif isinstance(items, tuple):
            item = CCheckItem.fromTuple(items)
            self._items = [item] if item else []
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, tuple):
                    tmpItem = CCheckItem.fromTuple(item)
                    if tmpItem:
                        item = tmpItem
                if not (item and isinstance(item, CCheckItem)):
                    self.showMessage(u'Не удалось распознать один из элементов чека: %s' % item, True)
                elif not item.isCorrect():
                    self.showMessage(u'Элемент чека "%s" некорректен (%s)' % (item, ', '.join(item.errorList)), True)
                else:
                    self._items.append(item)
        self.reset()

    def index(self, row, col, parent=None, *args, **kwargs):
        if row >= len(self._items):
            return super(CCheckItemModel, self).index(row, col, parent,*args, **kwargs)
        return self.createIndex(row, col, self._items[row])
