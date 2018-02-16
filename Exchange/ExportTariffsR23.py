# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2014-2015 Vista Software. All rights reserved.
##
#############################################################################

u"""
Экспорт тарифа в территориальный фонд Краснодарского Края
"""
import os
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

from PyQt4 import QtCore, QtGui
from library.dbfpy.dbf import Dbf
from library.DialogBase import CConstructHelperMixin
from library.crbcombobox import CRBModelDataCache
from library.Utils import forceBool, forceDate, forceDouble, forceRef, forceString, forceStringEx, getVal, toVariant


from Ui_ExportTariffR23_Page1 import Ui_ExportTariffR23_Page1
from Ui_ExportTariffR23_Page2 import Ui_ExportTariffR23_Page2

exportVersion = '1.00'

def ExportTariffsR23(widget, tariffRecordList, orgId):
    appPrefs = QtGui.qApp.preferences.appPrefs
    fileName = forceString(appPrefs.get('ExportTariffsDBFFileName', ''))
    #exportAll = forceBool(appPrefs.get('ExportTariffsDBFExportAll', True))
    #compressRAR = forceBool(appPrefs.get('ExportTariffsDBFCompressRAR', False))
    dlg = CExportTariffDBF(fileName, tariffRecordList, orgId, widget)
    dlg.exec_()


class CExportTariffR23Page1(QtGui.QWizardPage, Ui_ExportTariffR23_Page1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')


    def preSetupUi(self):
        from Orgs.TariffModel import CTariffModel
        self.addModels('Tariff', CTariffModel(self))
        self.modelTariff.cellReadOnly = lambda index: True
        self.modelTariff.setEnableAppendLine(False)
        self.addModels('Dates', CTariffDatesModel(self))


    def postSetupUi(self):
        #self.tblItems.setModel(self.proxyModelTariff)
        self.setModels(self.tblItems, self.modelTariff, self.selectionModelTariff)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.modelTariff.setItems(self.parent.tariffRecordList)
        self.selectionModelTariff.clearSelection()
        self.tblItems.setFocus(QtCore.Qt.OtherFocusReason)

        self.setModels(self.tblDates, self.modelDates, self.selectionModelDates)
        self.tblDates.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        dates = set(forceDate(record.value('begDate')).toPyDate() for record in self.parent.tariffRecordList)
        self.modelDates.setItems([QtCore.QDate(d) for d in sorted(list(dates))])



    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        # if self.parent.exportAll:
        #     return True
        # else:
        return forceBool(self.tblItems.selectedIndexes())


    def selectedItemList(self):
        return self.tblItems.getSelectedItems()

    def validatePage(self):
        self.wizard().selectedItems = self.selectedItemList()
        return True

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItems_clicked(self, index):
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        self.tblItems.selectAll()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.tblItems.clearSelection()
        self.emit(QtCore.SIGNAL('completeChanged()'))

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblDates_clicked(self, index):
        dates = [self.tblDates.model().data(index, QtCore.Qt.DisplayRole) for index in self.tblDates.selectedIndexes()]
        self.modelTariff.setItems(filter(lambda x: x.value('begDate') in dates, self.parent.tariffRecordList) if dates else self.parent.tariffRecordList)

class CExportTariffR23Page2(QtGui.QWizardPage, Ui_ExportTariffR23_Page2):
    def __init__(self, parent):
        self.done = False
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.pathIsValid = False
        # self.cmbMedicalAidLevel.setTable('rbMedicalLevel', addNone=False)
        self.edtDirName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportTariffsR23DBFExportDir', '')))
        self.edtLpuCode.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportTariffsR23DBFLpuCode', '')))
        # self.cmbMedicalAidLevel.setValue(forceRef(getVal(QtGui.qApp.preferences.appPrefs, 'ExportTariffsR23DBFMedicalAidLevel', None)))
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.updateBtnExport()

    def createSpr22Dbf(self):
        dbf = Dbf(self.wizard().getFullDbfFileName('SPR22'), new=True, encoding='cp866')
        dbf.addField (
            ('CODE_MO',     'C', 5),  # Код МО
            ('KUSL',        'C', 15), # Код услуги
            ('DATN',        'D', 30), # Дата начала действия тарифа
            ('DATO',        'D', 30), # Дата окончания тарифа
            ('TARIF',       'N', 10, 2), # Стоимость услуги
            # ('TARIF_B',     'N', 10, 2), # Базовая часть стоимости услуги
            # ('TARIF_DM',    'N', 10, 2), # что-то
            # ('TARIF_D',     'N', 10, 2), # Сумма примененных коэффициентов
            # ('TARIF_UC',    'N', 10, 2), # Цена "коэффициента участковости"
            # ('CENA_KD',     'N', 10, 2), # Цена койко-дня
            # ('LEVEL',       'C',  5), # Уровень оказания МП
        )
        return dbf

    def initializePage(self):
        self.updateBtnExport()
        self.done = False


    def isComplete(self):
        return self.done


    def updateBtnExport(self):
        self.btnExport.setEnabled(forceBool(self.pathIsValid and forceStringEx(self.edtLpuCode.text())))

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        dbfSpr22 = self.createSpr22Dbf()

        selectedItems = self.wizard().selectedItems
        self.exportTariffs(dbfSpr22, selectedItems)

        dbfSpr22.close()
        self.collect()
        self.done = True
        self.btnExport.setEnabled(False)
        self.emit(QtCore.SIGNAL('completeChanged()'))

    def collect(self):
        zipFileName = '%s.zip' % forceString(self.edtLpuCode.text())
        zipFilePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                zipFileName)
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)

        for src in map(self.parent.getFullDbfFileName, ['SPR22']):
            zf.write(src, os.path.basename(src), ZIP_DEFLATED)

        zf.close()

        dst = os.path.join(forceStringEx(self.edtDirName.text()), zipFileName)
        success, result = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))

        if success:
            QtGui.qApp.preferences.appPrefs['ExportTariffsR23DBFExportDir'] = toVariant(self.edtDirName.text())
            QtGui.qApp.preferences.appPrefs['ExportTariffsR23DBFLpuCode'] = toVariant(self.edtLpuCode.text())
            # QtGui.qApp.preferences.appPrefs['ExportTariffsR23DBFMedicalAidLevel'] = toVariant(self.cmbMedicalAidLevel.value())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtDirName_textChanged(self):
        dir = forceStringEx(self.edtDirName.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.updateBtnExport()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtLpuCode_textChanged(self):
        self.updateBtnExport()

    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Архангельской области',
                 forceStringEx(self.edtDirName.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDirName.setText(QtCore.QDir.toNativeSeparators(dir))

    def exportTariffs(self, dbf, tariffs):
        lpuCode = forceString(self.edtLpuCode.text())
        expenses = self.getExpenses([forceRef(t.value('id')) for t in tariffs])

        serviceCache = CRBModelDataCache.getData('rbService', True, codeFieldName='code')

        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(len(tariffs))

        for tariff in tariffs:
            self.progressBar.step(1)
            QtGui.qApp.processEvents()
            tariffExpenses = expenses.get(forceRef(tariff.value('id')), {})
            record = dbf.newRecord()
            record['CODE_MO'] = lpuCode
            record['KUSL'] = serviceCache.getCodeById(forceRef(tariff.value('service_id')))
            record['DATN'] = forceDate(tariff.value('begDate')).toPyDate()
            record['DATO'] = forceDate(tariff.value('endDate')).toPyDate() if forceString(tariff.value('endDate')) else u''
            price = forceDouble(tariff.value('price'))
            # amount = forceDouble(tariff.value('amount'))
            # priceKD = price/amount if amount else price
            record['TARIF'] = price
            # record['TARIF_B'] = tariffExpenses.get('1', 0.0)
            # record['TARIF_DM'] = tariffExpenses.get('2', 0.0)
            # record['TARIF_D'] = tariffExpenses.get('3', 0.0)
            # record['TARIF_UC'] = tariffExpenses.get('4', 0.0)
            # record['CENA_KD'] = 0 if forceDate(tariff.value('begDate')) >= QtCore.QDate(2015, 01, 01) else priceKD
            # record['LEVEL'] = self.cmbMedicalAidLevel.code()
            record.store()

    def getExpenses(self, tariffIdList):
        u"""Возвращает словарь списков записей затрат"""

        db = QtGui.qApp.db
        tableCCE = db.table('Contract_CompositionExpense')
        tableRBESI = db.table('rbExpenseServiceItem')
        queryTable = tableCCE.innerJoin(tableRBESI, tableRBESI['id'].eq(tableCCE['rbTable_id']))
        result = {}
        recordList = db.getRecordList(queryTable,
                                      cols=[tableCCE['master_id'], tableCCE['percent'], tableRBESI['code']],
                                      where=[tableCCE['master_id'].inlist(tariffIdList),
                                             tableRBESI['code'].inlist(['1', '2', '3', '4'])])

        for record in recordList:
            tariffId = forceRef(record.value('master_id'))
            expenses = result.setdefault(tariffId, {})
            expenses[forceString(record.value('code'))] = forceDouble(record.value('percent'))

        return result


class CExportTariffDBF(QtGui.QWizard):
    def __init__(self, fileName, tariffRecordList, orgId, parent=None):
        QtGui.QWizard.__init__(self, parent, QtCore.Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт тарифов договора')
        self.selectedItems = []
        self.fileName= fileName
        self.orgId = orgId
        self.tmpDir = None
        #self.exportAll = exportAll
        self.tariffRecordList = tariffRecordList
        self.addPage(CExportTariffR23Page1(self))
        self.addPage(CExportTariffR23Page2(self))

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('exportTariffR23')
        return self.tmpDir

    def getFullDbfFileName(self, sprName):
        return os.path.join(self.getTmpDir(), sprName + '.dbf')


class CTariffDatesModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(CTariffDatesModel, self).__init__(parent)
        self.items = []

    def setItems(self, items):
        self.items = items
        self.reset()

    def rowCount(self, index):
        return len(self.items)

    def columnCount(self, index):
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            if row < len(self.items):
                return QtCore.QVariant(self.items[row])
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and section == 0:
            return QtCore.QVariant(u'Дата')
        return QtCore.QVariant()