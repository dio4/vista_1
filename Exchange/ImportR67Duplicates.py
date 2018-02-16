# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################
from library.Utils     import *
from DataCheck.LogicalControlDoubles import CControlDoubles

from Exchange.Cimport import CXMLimport
from Ui_ImportRefBooks import Ui_Dialog

# TODO: реализовать разные режимы обновления (пропуск, обновление, спросить)

def importR67Duplicates(widget):
    dlg = CImportDuplicates_GUI()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportDupsFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportDupsFileName'] = toVariant(dlg.edtFileName.text())


class CImportDuplicates2(CXMLimport):
    """
    Старая версия. По новым правилам, в Смоленске все происходит наоборот, но мб пригодится.
    """
    def __init__(self, args = None):
        CXMLimport.__init__(self, self.log if args is None else None)

        self.nProcessed = 0
        self.nUpdated = 0
        self.miacCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))

#----------- Prepare form, process signals --------------

    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (DUP*.xml)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

#---------------------- Utils ----------------------------
    def attributes(self):
        return self._xmlReader.attributes()

    def err2log(self, e):
        self.log.append(e)

#----------------- Parsing xml file ------------------------
    def startImport(self):
        """
            Отображение процесса импорта, вызов соответствующих функций.
        """
        self.nProcessed = 0
        self.nUpdated = 0
        fileName = forceStringEx(self.edtFileName.text())

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


    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and self.name() == 'DUPS':
                self.processDupsList()

            if self.hasError():
                self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                return False

        return True


    def processDupsList(self):
        state = 0
        db = QtGui.qApp.db
        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and state == 0:
                if self.name() == 'Duplicate':
                    self.nProcessed += 1
                    state = 1

                    recordDict = {}
                    for attr in self.attributes():
                        recordDict[forceString(attr.name())] = forceString(attr.value())
                    if not 'lpu' in recordDict or not recordDict['lpu']:
                        self.err2log(u'В записи не найден код МИАЦ. Пропускаем.')
                        continue
                    if recordDict['lpu'] != self.miacCode:
                        continue
                    errorMessageList, workLogMessageList = CControlDoubles.mergeClients(forceInt(recordDict['baseId']), forceInt(recordDict['dupId']))
                    if errorMessageList:
                        for error in errorMessageList:
                            self.err2log(error)
                    else:
                        self.nUpdated += 1
                else:
                    self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                    return False
            elif self.isEndElement():
                if state == 1:
                    state = 0
                else:
                    return


class CImportDuplicates(CXMLimport):
    def __init__(self, args = None):
        CXMLimport.__init__(self, self.log if args is None else None)

        self.nProcessed = 0
        self.nUpdated = 0
        self.miacCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'miacCode'))

#----------- Prepare form, process signals --------------

    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (DUP*.xml)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

#---------------------- Utils ----------------------------
    def attributes(self):
        return self._xmlReader.attributes()

    def err2log(self, e):
        if self.log:
            self.log.append(e)

#----------------- Parsing xml file ------------------------
    def startImport(self):
        """
            Отображение процесса импорта, вызов соответствующих функций.
        """
        self.nProcessed = 0
        self.nUpdated = 0
        fileName = forceStringEx(self.edtFileName.text())

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


    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and self.name() == 'DUPS':
                self.processDupsList()

            if self.hasError():
                self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                return False

        return True


    def processDupsList(self):
        state = 0
        db = QtGui.qApp.db
        tableClientIdentification = db.table('ClientIdentification')
        accountingSystemId = forceRef(db.translate('rbAccountingSystem', 'code', '67VM', 'id'))
        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and state == 0:
                if self.name() == 'Duplicate':
                    self.nProcessed += 1
                    state = 1

                    recordDict = {}
                    for attr in self.attributes():
                        recordDict[forceString(attr.name())] = forceString(attr.value())
                    if not 'lpu' in recordDict or not recordDict['lpu']:
                        self.err2log(u'В записи не найден код МИАЦ. Пропускаем.')
                        continue
                    lpu = recordDict['lpu']
                    baseId = recordDict['baseId']
                    dupId = recordDict['dupId']
                    baseClientRecord = db.getRecordEx(tableClientIdentification, 'client_id',
                                                      [tableClientIdentification['accountingSystem_id'].eq(accountingSystemId),
                                                       tableClientIdentification['identifier'].eq(lpu + u'.' + baseId)])
                    if not baseClientRecord:
                        continue

                    dupClientRecord = db.getRecordEx(tableClientIdentification, 'client_id',
                                                      [tableClientIdentification['accountingSystem_id'].eq(accountingSystemId),
                                                       tableClientIdentification['identifier'].eq(lpu + u'.' + dupId)])

                    if not dupClientRecord:
                        continue

                    errorMessageList, workLogMessageList = CControlDoubles.mergeClients(forceRef(baseClientRecord.value('client_id')),
                                                                                        forceRef(dupClientRecord.value('client_id')))
                    if errorMessageList:
                        for error in errorMessageList:
                            self.err2log(error)
                    else:
                        self.nUpdated += 1
                else:
                    self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                    return False
            elif self.isEndElement():
                if state == 1:
                    state = 0
                else:
                    return

class CImportDuplicates_GUI(QtGui.QDialog, Ui_Dialog, CImportDuplicates):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.checkName()
        CImportDuplicates.__init__(self)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Import duplicates from Regional Data Center and merge records if necessary.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-f', dest='fileName')
    parser.add_argument('-t', dest='datetime', type=QDateTime, default=QDateTime.currentDateTime().addSecs(-60))
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database',  default='s11')
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
    dlg = CImportDuplicates(args)

    inFile = QtCore.QFile(args['fileName'])
    if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
        print u'Couldnt open file for reading %s:\n%s.' % (args['fileName'], inFile.errorString())
        return

    dlg.readFile(inFile)

if __name__ == '__main__':
    main()