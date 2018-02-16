# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Упрощенный экспорт справочника организаций. Не выгружаются ссылки на другие таблицы. #####

import os.path
import shutil

from library.Utils     import *
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CContainerPreferencesMixin
from Exchange.Utils import CExportHelperMixin

from Ui_ExportDiagnosticResultPage1 import Ui_ExportPage1
from Ui_ExportOrganisationsPage2 import Ui_ExportPage2

def exportDiagnosticResult(widget):
    wizard = CExportWizard(widget)
    wizard.exec_()

class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта справочника результатов диагнозов')
        self.tmpDir = ''
        self.xmlLocalFileName = ''
        self.fileName = ''

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('DiagnosticResultsXML')
        return self.tmpDir


    def getFullXmlFileName(self):
        self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
        return self.xmlLocalFileName

    def getTxtFileName(self):
        if not self.fileName:
            self.fileName = u'DR_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
        return self.fileName

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()

class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin, CConstructHelperMixin, CContainerPreferencesMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        CExportHelperMixin.__init__(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт справочника врачей')
        self.setSubTitle(u'для выполнения шага нажмите на кнопку "Экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.parent = parent
        self.loadPreferences(getPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), {}))
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)

    def setExportMode(self, flag):
        """
            Настройка активных кнопок в зависимости от текущего состояния.
        """
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)

    def log(self, str, forceLog = True):
        """
            Вывод сообщения в окно отчета.
        """
        self.logBrowser.append(str)
        self.logBrowser.update()

    def createQuery(self):
        db = QtGui.qApp.db

        tableDiagnosticResult = db.table('rbDiagnosticResult')
        tableResult = db.table('rbResult')
        tableEventPurpose = db.table('rbEventTypePurpose')

        table = tableDiagnosticResult.leftJoin(tableResult, tableResult['id'].eq(tableDiagnosticResult['result_id']))
        table = table.leftJoin(tableEventPurpose, tableEventPurpose['id'].eq(tableDiagnosticResult['eventPurpose_id']))

        cols = [tableDiagnosticResult['code'],
                tableDiagnosticResult['name'],
                tableDiagnosticResult['continued'],
                tableDiagnosticResult['regionalCode'],
                tableDiagnosticResult['federalCode'],
                tableResult['code'].alias('resultCode'),
                tableEventPurpose['code'].alias('purposeCode')
        ]

        stmt = db.selectStmt(table, cols, isDistinct = True)
        print stmt
        return db.query(stmt)

    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        self.progressBar.setText(u'Запрос в БД...')
        output = self.createXML()
        query = self.createQuery()
        self.progressBar.reset()
        self.progressBar.setMaximum(query.size())
        self.progressBar.setValue(0)
        return output, query

    def exportInt(self):
        out, query = self.prepareToExport()
        mainOut = CDiagnosticResultStreamWriter(self)
        mainOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        mainOut.writeFileHeader(out, self.parent.getFullXmlFileName(), QtCore.QDate.currentDate())

        while query.next():
            QtGui.qApp.processEvents()
            if self.aborted:
                break
            self.progressBar.step()
            mainOut.writeRecord(query.record())

        mainOut.writeFileFooter()
        out.close()

# *****************************************************************************************

    def getTxtFileName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        return forceString(lpuCode + u'.TXT')

    def createTxt(self):
        txt = QFile(os.path.join(self.parent.getTmpDir(), self.getTxtFileName()))
        txt.open(QIODevice.WriteOnly | QIODevice.Text)
        txtStream =  QTextStream(txt)
        txtStream.setCodec('CP866')
        return txt,  txtStream

    def validatePage(self):
        return True

# *****************************************************************************************

    def createXML(self):
        outFile = QtCore.QFile(self.parent.getFullXmlFileName())
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        return outFile

# *****************************************************************************************

    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True
        self.savePreferences()


    @QtCore.pyqtSignature('')
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSignature('')
    def on_btnCancel_clicked(self):
        self.abort()


class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт справочника организаций')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'DiagnosticResultXMLExportDir', homePath))
        self.edtDir.setText(exportDir)

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        srcFullName = self.parent.getFullXmlFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                            self.parent.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

        QtGui.qApp.preferences.appPrefs['DiagnosticResultXMLExportDir'] = toVariant(self.edtDir.text())
        return success


    @QtCore.pyqtSignature('QString')
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSignature('')
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки справочника организаций',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
             self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))


class CDiagnosticResultStreamWriter(QXmlStreamWriter):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.xmlErrorsList = []

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeRecord(self, record):
        self.writeEmptyElement('DiagnosticResult')
        for i in xrange(record.count()):
            self.writeAttribute(forceString(record.fieldName(i)), forceString(record.value(i)))

    def writeFileHeader(self, device, fileName, accDate):
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('DIAGNOSTIC_RESULT_LIST')

    def writeFileFooter(self):
        self.writeEndElement() # DIAGNOSTIC_RESULT_LIST
        self.writeEndDocument()


# *****************************************************************************************



