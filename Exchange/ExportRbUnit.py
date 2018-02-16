#!/usr/bin/env python
# -*- coding: utf-8 -*-
from library.TableModel import *
from library.DialogBase import CConstructHelperMixin

from Utils import *

from Ui_ExportRbUnit_Wizard_1 import Ui_ExportRbUnit_Wizard_1
from Ui_ExportRbUnit_Wizard_2 import Ui_ExportRbUnit_Wizard_2


def ExportRbUnit(parent):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbUnitFileName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbUnitExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbUnitCompressRAR', 'False'))
    dlg = CExportRbUnit(fileName, exportAll, compressRAR,  parent)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportRbUnitFileName'] = toVariant(
                                                                            dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportRbUnitExportAll'] = toVariant(
                                                                            dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportRbUnitCompressRAR'] = toVariant(
                                                                            dlg.compressRAR)

rbUnitFields = ('code', 'name')

class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, idList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._idList = idList


    def createQuery(self,  idList):
        """ Запрос информации по справочнику. Если idList пуст,
            запрашиваются все элементы"""

        db = QtGui.qApp.db
        stmt = """
        SELECT  code,
                    name
        FROM rbUnit
        """

        if idList:
            stmt+= 'WHERE id in ('+', '.join([str(et) for et in idList])+ ')'

        query = db.query(stmt)
        return query


    def writeRecord(self, record):
        self.writeStartElement("Unit")

        # все свойства действия экспортируем как атрибуты
        for x in rbUnitFields:
            self.writeAttribute(x, forceString(record.value(x)))

        self.writeEndElement()

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
            self.writeDTD("<!DOCTYPE xRbUnit>")
            self.writeStartElement("RbUnitExport")
            self.writeAttribute("SAMSON",
                                "2.0 revision(%s, %s)" %(lastChangedRev, lastChangedDate))
            self.writeAttribute("version", "1.0")
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


class CExportRbUnitWizardPage1(QtGui.QWizardPage, Ui_ExportRbUnit_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   30)
            ]
        self.tableName = "rbUnit"
        self.order = ['code', 'name', 'id']
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')


    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        return self.parent.exportAll or self.parent.selectedItems != []


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
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.checkExportAll.setChecked(self.parent.exportAll)


    def select(self):
        table = self.modelTable.table()
        return QtGui.qApp.db.getIdList(table.name(), order=self.order)


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        self.parent.selectedItems =self.tblItems.selectedItemIdList()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.parent.selectedItems = []
        self.selectionModelTable.clearSelection()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkExportAll_clicked(self):
        self.parent.exportAll = self.checkExportAll.isChecked()
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.emit(QtCore.SIGNAL('completeChanged()'))



class CExportRbUnitWizardPage2(QtGui.QWizardPage, Ui_ExportRbUnit_Wizard_2):
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
        self.checkRAR.setChecked(self.parent.compressRAR)


    def isComplete(self):
        return self.done


    def initializePage(self):
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.done = False

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
        assert self.parent.exportAll or self.parent.selectedItems != []
        fileName = self.edtFileName.text()

        if fileName.isEmpty():
            return

        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr(u'Экспорт справочника "Единицы измерения"'),
                                      self.tr(u'Не могу открыть файл для записи %1:\n%2.')
                                      .arg(fileName)
                                      .arg(outFile.errorString()))

        myXmlStreamWriter = CMyXmlStreamWriter(self, self.parent.selectedItems)
        if (myXmlStreamWriter.writeFile(outFile,  self.progressBar)):
            self.progressBar.setText(u'Готово')
        else:
            self.progressBar.setText(u'Прервано')
            outFile.close()
            return

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


class CExportRbUnit(QtGui.QWizard):
    def __init__(self, fileName,  exportAll, compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт справочника "Единицы измерения"')
        self.selectedItems = []
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.addPage(CExportRbUnitWizardPage1(self))
        self.addPage(CExportRbUnitWizardPage2(self))
