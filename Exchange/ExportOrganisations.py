# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Упрощенный экспорт справочника организаций. Не выгружаются ссылки на другие таблицы. #####

#TODO: настроить savePreferences

import os.path
import shutil

from library.database  import *
from library.Utils     import *
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CContainerPreferencesMixin
from Exchange.Utils import CExportHelperMixin

from Ui_ExportOrganisationsPage1 import Ui_ExportPage1
from Ui_ExportOrganisationsPage2 import Ui_ExportPage2

def exportOrganisations(widget):
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
        self.setWindowTitle(u'Мастер экспорта справочника организаций')
        self.tmpDir = ''
        self.xmlLocalFileName = ''
        self.fileName = ''

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('OrgsXML')
        return self.tmpDir


    def getFullXmlFileName(self):
        self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
        return self.xmlLocalFileName

    def getTxtFileName(self):
        if not self.fileName:
            self.fileName = u'ORG_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
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

        self.setTitle(u'Экспорт справочника организаций')
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

        table = db.table('Organisation')
        cond = []

        cond.append(table['isMedical'].ne(0) if self.chkExportMedical.isChecked() else '0')
        cond.append(table['isInsurer'].eq(1) if self.chkExportInsurer.isChecked() else '0')
        if cond[0] == '0' and cond[1] == '0':
            cond = []
        stmt = db.selectStmt(table, '*', db.joinOr(cond))
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
        print outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        print outFile.isOpen()
        print self.parent.getFullXmlFileName()
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
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'OrgsXMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):

        srcFullName = self.parent.getFullXmlFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                            self.parent.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

        QtGui.qApp.preferences.appPrefs['OrgsXMLExportDir'] = toVariant(self.edtDir.text())

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
        self.writeEmptyElement('Organisation')
        for i in xrange(record.count()):
            fieldName = forceString(record.fieldName(i))
            if not fieldName.lower() in ['id', 'net_id', 'createPerson_id', 'modifyPerson_id', 'OKPF_id', 'OKFS_id', 'head_id']:
                self.writeAttribute(forceString(record.fieldName(i)), forceString(record.value(i)))

    def writeFileHeader(self, device, fileName, accDate):
        self._clientsSet = set()
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('ORGS')
        #self.writeHeader(fileName, accDate)


    def writeFileFooter(self):
        self.writeEndElement() # RB_LIST
        self.writeEndDocument()


# *****************************************************************************************

def main():
    """
        Реализация возможности запуска экспорта справочников отдельным скриптом,
        независимо от Виста-Меда, для включения в состав сервиса по обмену ИЭМК и НСИ между ЛПУ и РЦОД.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export list of organisations')
    parser.add_argument('-m', dest='mode', type=int, default=0,
                        help = '0 - Export all orgs, 1 - export medical orgs, '
                               '2 - export insurers, 3 - export medical orgs & insurers')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', help='Full path for xml file', type=QDateTime, default=QDateTime.currentDateTime().addSecs(-60))
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', help='Directory, where output xml file will be placed.', default=os.getcwd())
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'IEMK',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    fileName = u'ORG_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
    outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
    if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
        print 'Couldnt open file for writing'
        sys.exit(-1)
    table = db.table('Organisation')
    cond = []
    mode = args['mode']
    if mode in (1, 3): cond.append(table['isMedical'].ne(0))
    if mode in (2, 3): cond.append(table['isInsurer'].eq(1))

    stmt = db.selectStmt(table, '*', db.joinOr(cond))
    query = db.query(stmt)

    orgsOut = COrgsStreamWriter(None)
    orgsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
    orgsOut.writeFileHeader(outFile, None, QtCore.QDate.currentDate())
    while query.next():
        orgsOut.writeRecord(query.record())

    orgsOut.writeFileFooter()
    outFile.close()

if __name__ == '__main__':
    main()

