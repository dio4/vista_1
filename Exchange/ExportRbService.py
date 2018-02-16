#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.TableModel import *
from library.DialogBase import CConstructHelperMixin
from RefBooks.Tables import rbCode,  rbName

from Utils import *

from Ui_ExportRbService_Wizard_1 import Ui_ExportRbService_Wizard_1
from Ui_ExportRbService_Wizard_2 import Ui_ExportRbService_Wizard_2

rbServiceFields = ('code', 'name', 'eisLegacy', 'nomenclatureLegacy', 'license',
                    'infis', 'begDate', 'endDate')


def ExportRbService(parent):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbServiceFileName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbServiceExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbServiceCompressRAR', 'False'))
    dlg = CExportRbService(fileName, exportAll,  compressRAR,  parent)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportRbServiceFileName'] = toVariant(
                                                                            dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportRbServiceExportAll'] = toVariant(
                                                                            dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportRbServiceCompressRAR'] = toVariant(
                                                                            dlg.compressRAR)


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, idList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._idList = idList


    def createQuery(self,  idList):
        db = QtGui.qApp.db
        stmt = """
        SELECT  code, name, eisLegacy, nomenclatureLegacy, license,
                    infis, begDate, endDate
        FROM rbService
        """
        if idList:
            stmt+=' WHERE id in ('+', '.join([str(et) for et in idList])+')'

        query = db.query(stmt)
        return query


    def writeRecord(self, record):
        self.writeStartElement("ServiceElement")

        # все свойства действия экспортируем как атрибуты
        for x in rbServiceFields:
            if x in ['begDate',  'endDate']:
                date = forceDate(record.value(x)).toString(QtCore.Qt.ISODate)
                self.writeAttribute(x, forceString(date))
            else:
                self.writeAttribute(x, forceString(record.value(x)))

        self.writeEndElement() # ThesaurusElement


    def writeFile(self,  device,  progressBar):
        global lastChangedRev
        global lastChangedDate
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        try:
            progressBar.setText(u'Запрос данных')
            query = self.createQuery(self._idList)
            self.setDevice(device)
            progressBar.setMaximum(max(query.size(), 1))
            progressBar.reset()
            progressBar.setValue(0)

            self.writeStartDocument()
            self.writeDTD("<!DOCTYPE xRbService>")
            self.writeStartElement("RbServiceExport")
            self.writeAttribute("SAMSON",
                                "2.0 revision(%s, %s)" %(lastChangedRev, lastChangedDate))
            self.writeAttribute("version", "1.00")
            while (query.next()):
                self.writeRecord(query.record())
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

class CExportRbServiceWizardPage1(QtGui.QWizardPage, Ui_ExportRbService_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(u'Код',                 [rbCode], 20),
            CTextCol(u'Наименование',        [rbName], 40),
            CBoolCol(u'Унаследовано из ЕИС', ['eisLegacy'], 10),
            CTextCol(u'ИНФИС код',           ['infis'], 20),
            CEnumCol(u'Лицензирование',      ['license'], [u'не требуется', u'требуется лицензия', u'требуется персональный сертификат'], 30),
            ]
        self.tableName = "rbService"
        self.filter = ''
        self.table = QtGui.qApp.db.table(self.tableName)
        self.order = ['code', 'name', 'id']
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')


    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        if self.parent.exportAll:
            return True
        else:
            return self.parent.selectedItems != []


    def preSetupUi(self):
        self.addModels('Table',CTableModel(self, self.cols, self.tableName))


    def postSetupUi(self):
        self.setModels(self.tblItems,   self.modelTable, self.selectionModelTable)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        idList = self.select()
        self.modelTable.setIdList(idList)
        self.selectionModelTable.clearSelection()
        self.tblItems.setFocus(Qt.OtherFocusReason)
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.gbFilter.setEnabled(not self.parent.exportAll)
        self.checkExportAll.setChecked(self.parent.exportAll)
        self.chkFilterEIS.setCheckState(Qt.PartiallyChecked)
        self.chkFilterNomenclature.setCheckState(Qt.PartiallyChecked)


    def select(self):
        return QtGui.qApp.db.getIdList(self.table,
                            'id', self.filter,  self.order)


    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblItems.currentItemId()


    def renewListAndSetTo(self, itemId=None):
        if not itemId:
            itemId = self.tblItems.currentItemId()
        self.updateFilter()
        idList = self.select()
        self.tblItems.setIdList(idList, itemId)
        self.selectionModelTable.clearSelection()
        rows = []
        # восстанавливаем выбранные элементы в таблице

        for id in self.parent.selectedItems:
            if idList.count(id)>0:
                row = idList.index(id)
                rows.append(row)
        for row in rows:
            index = self.modelTable.index(row, 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                QtGui.QItemSelectionModel.Rows)


    def resetFilter(self):
        self.chkFilterCode.setChecked(False)
        self.chkFilterName.setChecked(False)
        self.chkFilterEIS.setCheckState(Qt.PartiallyChecked)
        self.chkFilterNomenclature.setCheckState(Qt.PartiallyChecked)
        self.chkFilterPeriod.setChecked(False)
        self.filter = []


    def updateFilter(self):
        cond = []

        if self.chkFilterCode.isChecked():
            cond.append(self.table[rbCode].likeBinary( \
                addDots(forceString(self.edtFilterCode.text()))))

        if self.chkFilterName.isChecked():
            cond.append(self.table[rbName].like(
                forceString(self.edtFilterName.text()) + u'%'))

        if self.chkFilterEIS.checkState() != Qt.PartiallyChecked:
            cond.append(self.table['eisLegacy'].eq( \
                forceBool(self.chkFilterEIS.isChecked())))

        if self.chkFilterNomenclature.checkState() != Qt.PartiallyChecked:
            cond.append(self.table['nomenclatureLegacy'].eq( \
                forceBool(self.chkFilterNomenclature.isChecked())))

        if self.chkFilterPeriod.isChecked():
            cond.append(self.table['begDate'].ge( \
                forceString(self.edtFilterBegDate.date().toString(QtCore.Qt.ISODate))))
            cond.append(self.table['endDate'].le( \
                forceString(self.edtFilterEndDate.date().toString(QtCore.Qt.ISODate))))

        self.filter = QtGui.qApp.db.joinAnd(cond)


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        self.parent.selectedItems = self.tblItems.selectedItemIdList()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        selectionList = self.modelTable.idList()
        self.parent.selectedItems = selectionList

        for id in selectionList:
            index = self.modelTable.index(selectionList.index(id), 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                    QtGui.QItemSelectionModel.Rows)

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        selectionList = self.modelTable.idList()

        for id in selectionList:
            index = self.modelTable.index(selectionList.index(id), 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Deselect|
                                                                    QtGui.QItemSelectionModel.Rows)
            self.parent.selectedItems.remove(id)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkExportAll_clicked(self):
        self.parent.exportAll = self.checkExportAll.isChecked()
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.gbFilter.setEnabled(not self.parent.exportAll)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_chkFilterCode_clicked(self):
        self.edtFilterCode.setEnabled(self.chkFilterCode.isChecked())

    @QtCore.pyqtSlot()
    def on_chkFilterName_clicked(self):
        self.edtFilterName.setEnabled(self.chkFilterName.isChecked())


    @QtCore.pyqtSlot()
    def on_chkFilterPeriod_clicked(self):
        self.edtFilterBegDate.setEnabled(self.chkFilterPeriod.isChecked())
        self.edtFilterEndDate.setEnabled(self.chkFilterPeriod.isChecked())


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxFilter_clicked(self, button):
        buttonCode = self.bbxFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.renewListAndSetTo()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetFilter()
            self.renewListAndSetTo()


class CExportRbServiceWizardPage2(QtGui.QWizardPage, Ui_ExportRbService_Wizard_2):
    def __init__(self,  parent):
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
        fileName = QtGui.QFileDialog.getSaveFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.parent.fileName = fileName
            self.btnExport.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        fileName = self.edtFileName.text()

        if fileName.isEmpty():
            return

        idList = []
        if not self.parent.exportAll:
            for key in self.parent.selectedItems:
                if key and (not (key in idList)):
                    idList.append(key)

            if idList == []:
                QtGui.QMessageBox.warning(self, u'Экспорт справочника "Услуги"',
                                      u'Не выбрано ни одного элемента для выгрузки')
                self.parent.back() # вернемся на пред. страницу. пусть выбирают
                return


        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Экспорт справочника "Услуги"',
                                      u'Не могу открыть файл для записи %s:\n%s.' %\
                                      (fileName, outFile.errorString()))
            return

        myXmlStreamWriter = CMyXmlStreamWriter(self, idList)
        result=myXmlStreamWriter.writeFile(outFile,  self.progressBar)
        self.progressBar.setText(u'Готово' if result else u'Прервано')
        outFile.close()

        if self.checkRAR.isChecked() and result:
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


class CExportRbService(QtGui.QWizard):
    def __init__(self, fileName,  exportAll, compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт справочника "Услуги"')
        self.selectedItems = []
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.addPage(CExportRbServiceWizardPage1(self))
        self.addPage(CExportRbServiceWizardPage2(self))
