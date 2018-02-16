# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase     import CDialogBase
from library.InDocTable     import CRecordListModel,  CRBInDocTableCol, CEnumInDocTableCol, CDateInDocTableCol, \
                                   CInDocTableCol, CFloatInDocTableCol

from library.Utils          import forceString
from Registry.ClientEditDialog  import CPolyclinicInDocTableCol


from TariffModel import CTariffModel

from Ui_DublicateTariff import Ui_DublicateTariff

class CBaseTariffTableModel(CRecordListModel):
    def __init__(self, parent=None):
        CRecordListModel.__init__(self, parent)
        self.addExtCol(CRBInDocTableCol(u'Услуга', 'service_id', 40, 'rbService', showFields=2).setReadOnly(), QtCore.QVariant.Int)
        self.table = QtGui.qApp.db.table('Contract_Tariff')


class CDuplicateTariffTableModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CRBInDocTableCol(u'Событие',            'eventType_id',  30, 'EventType')).setSortable(True)
        self.addCol(CEnumInDocTableCol(u'Тарифицируется',   'tariffType',     5, CTariffModel.tariffTypeNames)).setSortable(True)
        self.addCol(CRBInDocTableCol(u'Услуга',             'service_id',    30, 'rbService')).setSortable(True)
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
        self.addCol(CFloatInDocTableCol(u'УЕТ',             'uet',           4, precision=2))
        self.addCol(CFloatInDocTableCol(u'Цена',            'price',         8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Второй тариф с',  'frag1Start', 8, precision=0))
        self.addCol(CFloatInDocTableCol(u'Сумма второго тарифа', 'frag1Sum',   8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Цена второго тарифа',  'frag1Price',  8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Третий тариф с',  'frag2Start', 8, precision=0))
        self.addCol(CFloatInDocTableCol(u'Сумма третьего тарифа', 'frag2Sum',   8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Цена третьего тарифа',  'frag2Price',  8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Фед.цена',        'federalPrice',        8, precision=2))
        self.addCol(CFloatInDocTableCol(u'Фед.предел',      'federalLimitation',   8))
        self.addCol(CEnumInDocTableCol(u'НДС',              'vat',  8, CTariffModel.vat, precision=2))
        self.parent = parent
        self.table = QtGui.qApp.db.table('Contract_Tariff')

    def isEditable(self):
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            record = self.items()[row]
            col = self._cols[column]
            field = col.fieldName()
            oldValue = forceString(record.value(field))
            record.setValue(field, value)
            self.emitCellChanged(row, column)
            if oldValue != forceString(value):
                self.parent.editRecord(row, record, field)
            return True
        return False


class CDuplicateTariff(CDialogBase, Ui_DublicateTariff):
    def __init__(self, parent, checkTariffList):
        CDialogBase.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('BaseTariff', CBaseTariffTableModel(self))
        self.addModels('DuplicateTariff', CDuplicateTariffTableModel(self))
        self.btnBeginCheck = QtGui.QPushButton(u'Проверка', self)
        self.btnBeginCheck.setObjectName('btnBeginCheck')
        self.setupUi(self)
        self.setModels(self.tblBaseTariff, self.modelBaseTariff, self.selectionModelBaseTariff)
        self.setModels(self.tblDuplicateTariff, self.modelDuplicateTariff, self.selectionModelDuplicateTariff)
        self.buttonBox.addButton(self.btnBeginCheck, QtGui.QDialogButtonBox.ActionRole)
        self.checkTariffList = checkTariffList
        self.duplicaleRecordList = []
        self.tariffList = []
        self.popupMenu = QtGui.QMenu(self)
        self.popupMenu.setObjectName('popupMenu')
        self.actCombineTariff = QtGui.QAction(u'Объединить тарифы на основании выделенной строки', self)
        self.actCombineTariff.setObjectName('actCombineTariff')
        self.connect(self.actCombineTariff, QtCore.SIGNAL('triggered()'), self.on_actCombineTariff_triggered)
        self.popupMenu.addAction(self.actCombineTariff)
        self.tblDuplicateTariff.setPopupMenu(self.popupMenu)

    def getTariffList(self):
        return self.tariffList

    def getDublicaleList(self):
        return self.duplicaleRecordList

    def editRecord(self, row, record, field):
        if field in self.fields:
            baseRow = self.tblBaseTariff.currentIndex().row()
            self.tariffList.append(record)
            self.duplicaleRecordList[baseRow].pop(row)
            self.modelDuplicateTariff.reset()
            if not self.duplicaleRecordList[baseRow]:
                self.modelBaseTariff.removeRows(baseRow, 1)

    def startSearch(self):
        self.tariffList = []
        self.duplicaleRecordList = []
        mapDuplicate = {}

        self.fields = ['service_id']
        if self.chkEvent.isChecked():
            self.fields.append('eventType_id')
        if self.chkTariff.isChecked():
            self.fields.append('tariffType')
        if self.chkBegDate.isChecked():
            self.fields.append('begDate')
        if self.chkEndDate.isChecked():
            self.fields.append('endDate')
        if self.chkAmount.isChecked():
            self.fields.append('amount')
        if self.chkPrice.isChecked():
            self.fields.append('price')
        if self.chkTariffCategory.isChecked():
            self.fields.append('tariffCategory_id')
        if self.chkSpeciality.isChecked():
            self.fields.append('speciality_id')
        if self.chkSex.isChecked():
            self.fields.append('sex')
        if self.chkAge.isChecked():
            self.fields.append('age')
        if self.chkAttachType.isChecked():
            self.fields.append('attachType_id')
        if self.chkUnit.isChecked():
            self.fields.append('unit_id')

        self.modelBaseTariff.clearItems()
        for record in self.checkTariffList:
            key = []
            for field in self.fields:
                key.append(forceString(record.value(field)))
            tupleKey = tuple(key)
            if not mapDuplicate.has_key(tupleKey):
                mapDuplicate[tupleKey] = []
            mapDuplicate[tuple(key)].append(record)

        for key, recordList in mapDuplicate.iteritems():
            if len(recordList) > 1:
                self.modelBaseTariff.addRecord(recordList[0])
                self.duplicaleRecordList.append(recordList)
            else:
                self.tariffList.append(recordList[0])
        self.label.setText(u'Количество услуг с дубликатами: %s' % (len(self.duplicaleRecordList)))

    def accept(self):
        for recordList in self.duplicaleRecordList:
            if len(recordList) == 1:
                self.tariffList.append(recordList[0])
            elif len(recordList) > 1:
                QtGui.QMessageBox.warning(None, u'Проверка дубликатов тарифов',
                                          u'Не все дубликаты были исправлены! Проверте их еще раз.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                return
        QtGui.QDialog.accept(self)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelBaseTariff_currentRowChanged(self, current, previous):
        row = current.row()
        items = []
        if row >= 0:
            items = self.duplicaleRecordList[0]
        self.modelDuplicateTariff.setItems(items)
        self.label.setText(u'Количество дубликатов по выбранной услуге: %s' % (len(items)))

    @QtCore.pyqtSlot()
    def on_actCombineTariff_triggered(self):
        baseRow = self.tblBaseTariff.currentIndex().row()
        duplicateRow = self.tblDuplicateTariff.currentIndex().row()
        self.tariffList.append(self.duplicaleRecordList[baseRow][duplicateRow])
        self.duplicaleRecordList.pop(baseRow)
        self.modelBaseTariff.removeRows(baseRow, 1)
        self.modelDuplicateTariff.reset()

    @QtCore.pyqtSlot()
    def on_btnBeginCheck_clicked(self):
        self.modelDuplicateTariff.setItems([])
        self.startSearch()