# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Упрощенный экспорт справочника организаций. Не выгружаются ссылки на другие таблицы. #####

#TODO: рассмотреть файлы Export*Page1.ui. По возможность свести схожие формы в одну.

import os.path
import shutil

from library.database  import *
from library.Utils     import *
from library.DialogBase import CConstructHelperMixin
from library.PreferencesMixin import CContainerPreferencesMixin
from Exchange.Utils import CExportHelperMixin

from Ui_ExportPersons_VMPage1 import Ui_ExportPage1
from Ui_ExportOrganisationsPage2 import Ui_ExportPage2

def exportPersons_VM(widget):
    wizard = CExportWizard(widget)
    wizard.exec_()

def createPersonsQuery(mode = 0, onlyCurrentOrg = False, miacCode = None):
    """
    mode: 0 - GUI, 1 - console
    """
    db = QtGui.qApp.db

    tablePerson = db.table('Person')
    tableSpeciality = db.table('rbSpeciality')
    tableOrg = db.table('Organisation')

    table = tablePerson.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))
    table = table.leftJoin(tableOrg, tableOrg['id'].eq(tablePerson['org_id']))

    cols = [tablePerson['code'],
            tablePerson['federalCode'],
            tablePerson['regionalCode'],
            tablePerson['lastName'],
            tablePerson['firstName'],
            tablePerson['patrName'],
            tableOrg['miacCode'],
            tablePerson['retireDate'],
            tablePerson['retired'],
            tablePerson['birthDate'],
            tablePerson['sex'],
            tablePerson['academicDegree'],
            tableSpeciality['code'].alias('specialityCode'),
            ]

    cond = [tablePerson['deleted'].eq(0)]
    if mode == 1 and miacCode:
        cond.append(tableOrg['miacCode'].eq(miacCode))
    elif mode == 0 and onlyCurrentOrg:
        cond.append(tableOrg['miacCode'].eq(forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))))

    stmt = db.selectStmt(table, cols, cond, isDistinct = True)
    return db.query(stmt)

def createSpecialitiesQuery(mode=0, onlyCurrentOrg=False, miacCode=None):
    """
    Получаем список всех специльностей, имеющихся у выгружаемых врачей.
    """
    db = QtGui.qApp.db

    tablePerson = db.table('Person')
    tableSpeciality = db.table('rbSpeciality')

    table = tablePerson.innerJoin(tableSpeciality, tableSpeciality['id'].eq(tablePerson['speciality_id']))

    if mode == 1 and miacCode:
            tableOrg = db.table('Organisation')
            table = table.innerJoin(tableOrg, [tableOrg['id'].eq(tablePerson['org_id']), tableOrg['miacCode'].eq(miacCode)])
    elif mode == 0 and onlyCurrentOrg:
        tableOrg = db.table('Organisation')
        table = table.innerJoin(tableOrg, [tableOrg['id'].eq(tablePerson['org_id']), tableOrg['miacCode'].eq(forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode')))])

    cols = [
            tableSpeciality['code'],
            tableSpeciality['name'],
            tableSpeciality['OKSOName'],
            tableSpeciality['OKSOCode'],
            tableSpeciality['federalCode'],
            tableSpeciality['sex'],
            tableSpeciality['age'],
            tableSpeciality['mkbFilter'],
            tableSpeciality['regionalCode']
            ]

    cond = [tablePerson['deleted'].eq(0)]

    stmt = db.selectStmt(table, cols, cond, isDistinct = True)
    return db.query(stmt)

class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта справочника врачей')
        self.tmpDir = ''
        self.xmlLocalFileName = ''
        self.fileName = ''

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('PersonsXML')
        return self.tmpDir


    def getFullXmlFileName(self):
        self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
        return self.xmlLocalFileName

    def getTxtFileName(self):
        if not self.fileName:
            self.fileName = u'PERS_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
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

    def createPersonsQuery(self):
        return createPersonsQuery(mode=0, onlyCurrentOrg=self.chkOnlyCurrentOrg.isChecked())

    def createSpecialitiesQuery(self):
        return createSpecialitiesQuery(mode=0, onlyCurrentOrg=self.chkOnlyCurrentOrg.isChecked())

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
        query = self.createPersonsQuery()
        specQuery = self.createSpecialitiesQuery()
        self.progressBar.reset()
        self.progressBar.setMaximum(query.size() + specQuery.size())
        self.progressBar.setValue(0)
        return output, query, specQuery

    def exportInt(self):
        out, query, specQuery = self.prepareToExport()
        mainOut = CPersonStreamWriter(self)
        mainOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        mainOut.writeFileHeader(out, self.parent.getFullXmlFileName(), QtCore.QDate.currentDate())
        while specQuery.next():
            QtGui.qApp.processEvents()
            if self.aborted:
                break
            self.progressBar.step()
            mainOut.writeRecord(specQuery.record(), 'Speciality')

        mainOut.writeIntermediateSection()

        while query.next():
            QtGui.qApp.processEvents()
            if self.aborted:
                break
            self.progressBar.step()
            mainOut.writeRecord(query.record(), 'Person')

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
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'PersonsXMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):

        srcFullName = self.parent.getFullXmlFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                            self.parent.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

        QtGui.qApp.preferences.appPrefs['PersonsXMLExportDir'] = toVariant(self.edtDir.text())

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


class CPersonStreamWriter(QXmlStreamWriter):
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

    def writeRecord(self, record, elementName = 'Person'):
        self.writeEmptyElement(elementName)
        for i in xrange(record.count()):
            self.writeAttribute(forceString(record.fieldName(i)), forceString(record.value(i)))

    def writeFileHeader(self, device, fileName, accDate):
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('PERSON_SPEC_LIST')
        self.writeStartElement('SPECS')

    def writeIntermediateSection(self):
        # Закрываем секцию специальностей, открываем секцию врачей
        self.writeEndElement() # SPECS
        self.writeStartElement('PERSONS')


    def writeFileFooter(self):
        self.writeEndElement() # PERSONS
        self.writeEndElement() # PERSON_SPEC_LIST
        self.writeEndDocument()


# *****************************************************************************************


def main():
    """
        Реализация возможности запуска экспорта справочников отдельным скриптом,
        независимо от Виста-Меда, для включения в состав сервиса по обмену ИЭМК и НСИ между ЛПУ и РЦОД.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export list of persons, available in current organisation.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-c', dest='miacCode', default='')
    parser.add_argument('-t', dest='datetime', help='Default: currentDatetime - 60 seconds.', type=QDateTime, default=QDateTime.currentDateTime().addSecs(-60))
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', help='Directory, where output xml file will be placed.', default=os.getcwd())
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        sys.exit(-1)
    if not args['password']:
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
    fileName = u'PERS_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
    outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
    outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
    query = createPersonsQuery(mode=1, miacCode=args['miacCode'])
    specQuery = createSpecialitiesQuery(mode=1, miacCode=args['miacCode'])

    personsOut = CPersonStreamWriter(None)
    personsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
    personsOut.writeFileHeader(outFile, None, QtCore.QDate.currentDate())
    while specQuery.next():
        personsOut.writeRecord(specQuery.record(), 'Speciality')

    personsOut.writeIntermediateSection()

    while query.next():
        personsOut.writeRecord(query.record(), 'Person')

    personsOut.writeFileFooter()
    outFile.close()

if __name__ == '__main__':
    main()




