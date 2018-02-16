#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Экспорт тарифа из XML
"""
from library.DialogBase import CConstructHelperMixin
from library.crbcombobox import CRBComboBox

from Utils import *

from Ui_ExportTariff_Wizard_1 import Ui_ExportTariff_Wizard_1
from Ui_ExportTariff_Wizard_2 import Ui_ExportTariff_Wizard_2

tariffSimpleFields = ('tariffType', 'begDate', 'endDate', 'sex', 'age', 'MKB',
                      'amount', 'uet', 'price',
                      'frag1Start', 'frag1Sum', 'frag1Price',
                      'frag2Start', 'frag2Sum', 'frag2Price',
                      'federalLimitation', 'federalPrice'
                     )

tariffRefFields    =  ('eventType_id', 'service_id', 'unit_id',          'tariffCategory_id')
tariffRefTableNames=  ('EventType',    'rbService',  'rbMedicalAidUnit', 'rbTariffCategory')

tariffKeyFields    = ('eventType_id', 'tariffType', 'service_id', 'tariffCategory_id', 'MKB', 'sex', 'age', 'begDate', 'endDate')


exportVersion = '1.05'

def ExportTariffsXML(widget, tariffRecordList):
    appPrefs = QtGui.qApp.preferences.appPrefs
    fileName = forceString(appPrefs.get('ExportTariffsXMLFileName', ''))
    exportAll = forceBool(appPrefs.get('ExportTariffsXMLExportAll', True))
    compressRAR = forceBool(appPrefs.get('ExportTariffsXMLCompressRAR', False))
    dlg = CExportTariffXML(fileName, exportAll, compressRAR, tariffRecordList, widget)
    dlg.exec_()
    appPrefs['ExportTariffsXMLFileName'] = toVariant(dlg.fileName)
    appPrefs['ExportTariffsXMLExportAll'] = toVariant(dlg.exportAll)
    appPrefs['ExportTariffsXMLCompressRAR'] = toVariant(dlg.compressRAR)


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self, parent, tariffRecordList, selectedItems):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.tariffRecordList = tariffRecordList
        self.selectedItems = selectedItems
        self.refValueCache = {}
        for field, tableName in zip(tariffRefFields, tariffRefTableNames):
            self.refValueCache[field] = CRBModelDataCache.getData(tableName, True)

        self.expensesType = {}


    def getExpenses(self, tariffIdList):
        u"""Возвращает словарь списков записей затрат"""

        db = QtGui.qApp.db
        typeList = db.getRecordList('rbExpenseServiceItem')

        for record in typeList:
            self.expensesType[forceRef(record.value('id'))] = forceString(record.value('code'))

        table = db.table('Contract_CompositionExpense')
        result = {}
        recordList = db.getRecordList(table, where=table['master_id'].inlist(tariffIdList))

        for record in recordList:
            id = forceRef(record.value('master_id'))
            if result.has_key(id):
                result[id].append(record)
            else:
                result[id] = [record]

        return result


    def writeRecord(self, record, expenses):
        self.writeStartElement('TariffElement')
        # все нессылочные свойства действия экспортируем как атрибуты
        for fieldName in tariffSimpleFields:
            value = record.value(fieldName)
            fieldType = record.field(fieldName).type()
            if fieldType == QVariant.Date:
                strValue = forceDate(value).toString(QtCore.Qt.ISODate)
            elif fieldType == QVariant.Double:
                strValue = unicode(forceDouble(value))
            else:
                strValue = forceString(value)
            self.writeAttribute(fieldName, strValue)
        # ссылочные свойства экспортируем как элементы с атрибутами code и name
        for fieldName in tariffRefFields:
            elementName = fieldName[:-3]
            self.writeStartElement(elementName)
            value = forceRef(record.value(fieldName))
            if value:
                cache = self.refValueCache[fieldName]
                self.writeAttribute('code', cache.getStringById(value, CRBComboBox.showCode))
                self.writeAttribute('name', cache.getStringById(value, CRBComboBox.showName))
            self.writeEndElement()
        #затраты
        for ex in expenses.get(forceRef(record.value('id')), []):
            self.writeStartElement('expense')
            self.writeAttribute('code', self.expensesType.get(forceRef(ex.value('rbTable_id')), ''))
            self.writeAttribute('percent', forceString(ex.value('percent')))
            self.writeEndElement()

        self.writeEndElement() # TariffElement


    def writeFile(self, device, progressBar):
        global lastChangedRev
        global lastChangedDate
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        try:
            progressBar.setMaximum(max(len(self.selectedItems), 1))
            progressBar.reset()
            progressBar.setValue(0)

            self.setDevice(device)
            self.writeStartDocument()
            self.writeDTD('<!DOCTYPE xTariff>')
            self.writeStartElement('TariffExport')
            self.writeAttribute('SAMSON',
                                '2.0 revision(%s, %s)' %(lastChangedRev, lastChangedDate))
            self.writeAttribute('version', exportVersion)

            idList = [forceRef(self.tariffRecordList[i].value('id')) for i in self.selectedItems]
            expenses = self.getExpenses(idList)

            for i in self.selectedItems:
                self.writeRecord(self.tariffRecordList[i], expenses)
                QtGui.qApp.processEvents()
                progressBar.step()

            self.writeEndDocument()

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True

class CExportTariffWizardPage1(QtGui.QWizardPage, Ui_ExportTariff_Wizard_1, CConstructHelperMixin):
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
        self.addModels('Table', CTariffModel(self))
        self.modelTable.cellReadOnly = lambda index: True
        self.modelTable.setEnableAppendLine(False)


    def postSetupUi(self):
        self.setModels(self.tblItems, self.modelTable, self.selectionModelTable)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.modelTable.setItems(self.parent.tariffRecordList)
        self.selectionModelTable.clearSelection()
        self.tblItems.setFocus(Qt.OtherFocusReason)
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.chkExportAll.setChecked(self.parent.exportAll)
        if self.parent.exportAll:
            self.parent.selectedItems = range(self.modelTable.rowCount())


    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        if self.parent.exportAll:
            return True
        else:
            return self.parent.selectedItems != []


    def selectedItemList(self):
        rows = [index.row() for index in self.selectionModelTable.selectedRows()]
        rows.sort()
        return rows


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        self.parent.selectedItems = self.selectedItemList()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        selectedItems = range(self.modelTable.rowCount())
        self.parent.selectedItems = selectedItems
        for row in selectedItems:
            index = self.modelTable.index(row, 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Rows)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.selectionModelTable.clearSelection()
        self.parent.selectedItems = []
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_chkExportAll_clicked(self):
        self.parent.exportAll = self.chkExportAll.isChecked()
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        if self.chkExportAll.isChecked():
            self.parent.selectedItems = range(self.modelTable.rowCount())
        else:
            self.parent.selectedItems = self.selectedItemList()
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportTariffWizardPage2(QtGui.QWizardPage, Ui_ExportTariff_Wizard_2):
    def __init__(self, parent):
        self.done = False
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.edtFileName.setText(self.parent.fileName)
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.checkRAR.setChecked(self.parent.compressRAR)


    def initializePage(self):
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.done = False


    def isComplete(self):
        return self.done


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if fileName:
            self.edtFileName.setText(fileName)
            self.parent.fileName = fileName
            self.btnExport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        fileName = self.edtFileName.text()
        if fileName.isEmpty():
            return

        if not self.parent.selectedItems:
            QtGui.QMessageBox.warning(self,
                                      u'Экспорт тарифов договора',
                                      u'Не выбрано ни одного элемента для выгрузки')
            self.parent.back() # вернемся на пред. страницу. пусть выбирают
            return

        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self,
                                      u'Экспорт тарифов договора',
                                      QString(u'Не могу открыть файл для записи %1:\n%2.').arg(fileName).arg(outFile.errorString()))
            return

        myXmlStreamWriter = CMyXmlStreamWriter(self, self.parent.tariffRecordList, self.parent.selectedItems)
        if (myXmlStreamWriter.writeFile(outFile, self.progressBar)):
            self.progressBar.setText(u'Готово')
        else:
            self.progressBar.setText(u'Прервано')
        outFile.close()

        if self.checkRAR.isChecked():
            self.progressBar.setText(u'Сжатие')
            try:
                compressFileInRar(fileName, fileName+'.rar')
                self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
            except CRarException as e:
                self.progressBar.setText(unicode(e))
                QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)

        self.done = True
        self.btnExport.setEnabled(False)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self):
        self.parent.fileName = self.edtFileName.text()
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportTariffXML(QtGui.QWizard):
    def __init__(self, fileName, exportAll, compressRAR, tariffRecordList, parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт тарифов договора')
        self.selectedItems = []
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.tariffRecordList = tariffRecordList
        self.addPage(CExportTariffWizardPage1(self))
        self.addPage(CExportTariffWizardPage2(self))
