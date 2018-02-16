# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Упрощенный экспорт справочника организаций. Не выгружаются ссылки на другие таблицы. #####

#TODO: настроить savePreferences
#TODO: добавить выбор организации
import os.path
import shutil

from library.Utils     import *
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CContainerPreferencesMixin
from Exchange.Utils import CExportHelperMixin

from Ui_ExportOrganisationsPage1 import Ui_ExportPage1
from Ui_ExportOrganisationsPage2 import Ui_ExportPage2

def exportR67Duplicates(widget):
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
        self.setWindowTitle(u'Мастер экспорта дубликатов.')
        self.tmpDir = ''
        self.xmlLocalFileName = ''
        self.fileName = ''

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('DuplicatesXML')
        return self.tmpDir


    def getFullXmlFileName(self):
        self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
        return self.xmlLocalFileName

    def getTxtFileName(self):
        if not self.fileName:
            self.fileName = u'DUP_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
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

        self.chkExportInsurer.setVisible(False)
        self.chkExportMedical.setVisible(False)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт дубликатов.')
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
        self.chkExportMedical.setEnabled(not flag)
        self.chkExportInsurer.setEnabled(not flag)

    def log(self, str, forceLog = True):
        """
            Вывод сообщения в окно отчета.
        """
        self.logBrowser.append(str)
        self.logBrowser.update()

    def createQuery(self):
        db = QtGui.qApp.db

        accountingSystemId = forceRef(db.translate('rbAccountingSystem', 'code', '67VM', 'id'))
        if accountingSystemId:
            stmt = '''
            SELECT ci1.identifier as baseId, ci2.identifier as dupId FROM ClientIdentification ci1
            INNER JOIN ClientIdentification ci2
                ON ci2.client_id = ci1.client_id
                    AND ci1.deleted = 0
                    AND ci2.deleted = 0
                    AND ci2.id != ci1.id
                    AND ci1.accountingSystem_id = %(accountingSystemId)d
                    AND ci2.accountingSystem_id = %(accountingSystemId)d
                    AND SUBSTRING_INDEX(ci2.identifier, '.', 1) = SUBSTRING_INDEX(ci2.identifier, '.', 1)
            WHERE ci1.modifyDatetime = (SELECT MIN(modifyDatetime)
                                        FROM ClientIdentification ci3
                                        WHERE ci3.client_id = ci1.client_id
                                                AND ci3.deleted = 0
                                                AND ci3.accountingSystem_id = %(accountingSystemId)d
                                                AND SUBSTRING_INDEX(ci3.identifier, '.', 1) = SUBSTRING(ci1.identifier, '.', 1))
            ''' % {'accountingSystemId':accountingSystemId}
        else:
            stmt = 'SELECT 0'
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
        output = self.createXML()
        query = self.createQuery()
        self.progressBar.reset()
        self.progressBar.setMaximum(query.size())
        self.progressBar.setValue(0)
        return output, query

    def exportInt(self):
        out, query = self.prepareToExport()
        orgsOut = COrgsStreamWriter(self)
        orgsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        orgsOut.writeFileHeader(out, self.parent.getFullXmlFileName(), QtCore.QDate.currentDate())
        while query.next():
            QtGui.qApp.processEvents()
            if self.aborted:
                break
            self.progressBar.step()
            orgsOut.writeRecord(query.record())

        orgsOut.writeFileFooter()
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
        self.setTitle(u'Экспорт списка дубликатов')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'DupsXMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):

        srcFullName = self.parent.getFullXmlFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                            self.parent.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

        QtGui.qApp.preferences.appPrefs['DupsXMLExportDir'] = toVariant(self.edtDir.text())

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
                u'Выберите директорию для сохранения файла выгрузки списка дубликатов',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
             self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))


class COrgsStreamWriter(QXmlStreamWriter):
    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._clientsSet = None
        self.xmlErrorsList = []

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeRecord(self, record):
        baseString = forceString(record.value('baseId'))
        dupString = forceString(record.value('dupId'))

        baseArray = baseString.split('.')
        dupArray = dupString.split('.')

        if len(baseArray) != 2 or len(dupArray) != 2:
            return -1

        orgCode = baseArray[0]
        baseId = baseArray[1]
        dupId = dupArray[1]

        self.writeEmptyElement('Duplicate')
        self.writeAttribute('lpu', orgCode)
        self.writeAttribute('baseId', baseId)
        self.writeAttribute('dupId', dupId)

        for i in xrange(record.count()):
            fieldName = forceString(record.fieldName(i))
            if not fieldName.lower() in ['id', 'net_id', 'createPerson_id', 'modifyPerson_id', 'OKPF_id', 'OKFS_id', 'head_id']:
                self.writeAttribute(forceString(record.fieldName(i)), forceString(record.value(i)))

    def writeFileHeader(self, device, fileName, accDate):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('DUPS')


    def writeFileFooter(self):
        self.writeEndElement() # DUPS
        self.writeEndDocument()


# *****************************************************************************************



