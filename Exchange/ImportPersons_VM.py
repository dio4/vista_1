# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################
from library.database  import *
from library.Utils     import *

from Exchange.Cimport import CXMLimport
from Ui_ImportRefBooks import Ui_Dialog

# TODO: реализовать разные режимы обновления (пропуск, обновление, спросить)
# TODO: Добавить возможность выбора ключевого поля.

def importPersons_VM(widget):
    dlg = CImportPersons_VM_GUI()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPersonsFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPersonsFileName'] = toVariant(dlg.edtFileName.text())


class CImportPersons_VM(CXMLimport):
    def __init__(self, args=None):
        self.args = args
        if args:
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
            QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

        CXMLimport.__init__(self, self.log if args is None else None)

        self.nProcessed = 0
        self.nUpdated = 0
        self.nAdded = 0

        self.mapSpecialityCodeToId = {}
        self.mapOrgMiacCodeToId = {}



#----------- Prepare form, process signals --------------

    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (PERS*.xml)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

#---------------------- Utils ----------------------------
    def attributes(self):
        return self._xmlReader.attributes()

    def err2log(self, e):
        if self.log:
            self.log.append(e)

    def getOrgIdByMiacCode(self, code):
        orgId = self.mapOrgMiacCodeToId.get(code, None)
        if orgId is None:
            orgId = QtGui.qApp.db.translate('Organisation', 'miacCode', code, 'id')
            self.mapOrgMiacCodeToId[code] = orgId
        return orgId

#----------------- Parsing xml file ------------------------
    def startImport(self):
        """
            Отображение процесса импорта, вызов соответствующих функций.
        """
        self.nProcessed = 0
        self.nAdded = 0
        self.nUpdated = 0
        if self.args is None:
            fileName = forceStringEx(self.edtFileName.text())
        else:
            fileName = self.args['fileName']

        inFile = QtCore.QFile(fileName)
        fn = QtCore.QFileInfo(fileName)
        self.filename = fn.baseName()

        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл для чтения %s:\n%s.' \
                                  % (fileName, inFile.errorString()))
            return

        self.progressBar.reset()
        self.progressBar.setValue(0)
        size = inFile.size()
        self.progressBar.setMaximum(size)
        self.progressBar.setFormat(u'%v байт')

        self.labelNum.setText(u'размер источника: '+str(size))
        self.btnImport.setEnabled(False)

        if (not self.readFile(inFile)):
            if self.abort:
                self.err2log(u'! Прервано пользователем.')
            else:
                self.err2log(u'! Ошибка: файл %s, %s' % (fileName,
                                            self.errorString()))

        self.stat.setText(
            u'обработано: %d' % \
            (self.nProcessed))
        self.err2log(u'Обработано записей: %d.' % self.nProcessed)
        self.err2log(u'Обновлено записей: %d.' % self.nUpdated)
        self.err2log(u'Добавлено записей: %d.' % self.nAdded)


    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.setDevice(device)
        depth = 0

        while (not self.atEnd()):
            self.readNext()

            if depth == 0:
                if self.isStartElement():
                    if self.name() == 'PERSON_SPEC_LIST':
                        depth = 1
                    else:
                        self.err2log(u'Ошибка в структуре XML-файла. Импорт прерван.')
                        return
            elif depth == 1:
                if self.isStartElement():
                    if self.name() == 'SPECS':
                        self.processSpecs()
                    elif self.name() == 'PERSONS':
                        self.processPersons()
                    else:
                        self.err2log(u'Ошибка в XML-файле. Неизвестный элемент %s. Импорт прерван.' % self.name())
                elif self.isEndElement():
                    depth = 0


            if self.hasError():
                self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                return False

        return True


    def processSpecs(self):
        state = 0
        db = QtGui.qApp.db
        table = db.table('rbSpeciality')
        while not self.atEnd():
            self.readNext()
            if self.isStartElement() and state == 0:
                if self.name() == 'Speciality':
                    self.nProcessed += 1
                    state = 1
                    recordDict = {}
                    for attr in self.attributes():
                        recordDict[forceString(attr.name())] = forceString(attr.value())
                    if not recordDict.get('code', None):
                        self.err2log(u'Для специальности "%s" не задан код. Пропускаем.' % recordDict.get('name', ''))
                        continue
                    record = db.getRecordEx(table, '*', table['code'].eq(recordDict['code']))
                    isNew = False
                    if not record:
                        record = table.newRecord()
                        isNew = True
                    for field, value in recordDict.items():
                        record.setValue(field, toVariant(value))
                    specId = db.insertOrUpdate(table, record)
                    self.mapSpecialityCodeToId[recordDict['code']] = specId
                    if isNew:
                        self.nAdded += 1
                    else:
                        self.nUpdated += 1

                else:
                    self.err2log(u'Ошибка в XML-файле. Неизвестный элемент %s. Импорт прерван.' % self.name())
                    return False
            elif self.isEndElement():
                if state == 0:
                    return True
                elif state == 1:
                    state = 0

    def processPersons(self):
        state = 0
        db = QtGui.qApp.db
        table = db.table('Person')
        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and state == 0:
                if self.name() == 'Person':
                    self.nProcessed += 1
                    state = 1
                    recordDict = {}
                    for attr in self.attributes():
                        recordDict[forceString(attr.name())] = forceString(attr.value())
                    if not recordDict.get('code', None):
                        self.err2log(u'Для врача %s не задан код. Пропускаем' % formatName(recordDict['lastName'],
                                                                                           recordDict['firstName'],
                                                                                           recordDict['patrName']))
                        continue
                    isNew = False
                    record = db.getRecordEx(table, '*', table['code'].eq(recordDict['code']))
                    if not record:
                        isNew = True
                        record = table.newRecord()
                    for field, value in recordDict.items():
                        if field == 'miacCode':
                            orgId = self.getOrgIdByMiacCode(value)
                            record.setValue('org_id', toVariant(orgId))

                        elif field == 'specialityCode':
                            record.setValue('speciality_id', toVariant(self.mapSpecialityCodeToId.get(value, None)))
                        else:
                            if field in ('retireDate', 'birthDate') and not value:
                                value = None
                            record.setValue(field, toVariant(value))
                    db.insertOrUpdate(table, record)
                    if isNew:
                        self.nAdded += 1
                    else:
                        self.nUpdated += 1
                else:
                    self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                    return False

            elif self.isEndElement():
                if state == 1:
                    state = 0
                else:
                    return True

class CImportPersons_VM_GUI(QtGui.QDialog, Ui_Dialog, CImportPersons_VM):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.checkName()
        CImportPersons_VM.__init__(self)

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Import list of persons to specified database')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-f', dest='fileName', help='Full path to xml file')
    parser.add_argument('-t', dest='datetime', help='Default: currentDatetime - 60 seconds.', type=QDateTime, default=QDateTime.currentDateTime().addSecs(-60))
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)
    if not args['fileName']:
        print 'Error: you should specify file name'
        sys.exit(-3)

    app = QtCore.QCoreApplication(sys.argv)
    inFile = QtCore.QFile(args['fileName'])

    if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        print u'Couldnt open file for reading %s:\n%s.' % (args['fileName'], inFile.errorString())
        return

    dlg = CImportPersons_VM(args)
    dlg.readFile(inFile)

if __name__ == '__main__':
    main()