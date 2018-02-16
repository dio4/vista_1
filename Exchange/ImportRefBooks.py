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

def importRefBooks(widget):
    dlg = CImportRefBooks_GUI()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRefBooksFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportRefBooksFileName'] = toVariant(dlg.edtFileName.text())


class CImportRefBooks(CXMLimport):
    def __init__(self, args = None):
        self.args = args
        # Консольный режим
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
        self.nProcessedRefBooks = 0


#----------- Prepare form, process signals --------------

    @pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (RB*.xml)')
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
        self.nProcessedRefBooks = 0
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
        self.err2log(u'Обработано справочников: %d.' % self.nProcessedRefBooks)
        self.err2log(u'Обработано записей: %d.' % self.nProcessed)
        self.err2log(u'Обновлено записей: %d.' % self.nUpdated)
        self.err2log(u'Добавлено записей: %d.' % self.nAdded)


    def readFile(self, device):
        """
            Обработка импортируемого файла
        """
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement() and self.name() == 'RB_LIST':
                self.processRBList()

            if self.hasError():
                self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                return False

        return True


    def processRBList(self):
        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'RefBook':
                    self.processRefBook()
                else:
                    self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                    return False
            elif self.isEndElement():
                return

    def processRefBook(self):
        db = QtGui.qApp.db
        attrs = self.attributes()
        rbName = forceString(attrs.value('name'))
        keyCol = forceString(attrs.value('key'))
        rbTable = db.table(rbName)
        state = 0
        db.transaction()
        try:
            while (not self.atEnd()):
                self.readNext()
                if state == 0 and self.isStartElement() and self.name() == 'Item':
                    state = 1
                    keyValue = self.attributes().value(keyCol)
                    isNew = False
                    record = db.getRecordEx(forceString(rbName), '*', where='%s = \'%s\'' % (forceString(keyCol), forceString(keyValue)))
                    if not record:
                        isNew = True
                        record = rbTable.newRecord()
                    for attr in self.attributes():
                        record.setValue(forceString(attr.name()), toVariant(forceString(attr.value())))
                    self.nProcessed += 1
                    if isNew:
                        self.nAdded += 1
                    else:
                        self.nUpdated += 1
                    db.insertOrUpdate(rbName, record)
                elif self.isEndElement():
                    if state == 1:
                        state = 0
                    else:
                        self.nProcessedRefBooks += 1
                        db.commit()
                        return
                elif self.isStartElement():
                    self.err2log(u'Ошибка в XML-файле. Импорт прерван.')
                    db.rollback()
                    return
        except:
            db.rollback()
            raise

class CImportRefBooks_GUI(QtGui.QDialog, Ui_Dialog, CImportRefBooks):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.checkName()
        CImportRefBooks.__init__(self)


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Import various ref books.')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-f', dest='fileName', help='Full path to xml file')
    parser.add_argument('-t', dest='datetime', help='Default: currentDatetime - 60 seconds.', type=QDateTime, default=QDateTime.currentDateTime().addSecs(-60))
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, nargs='?', default='3306')
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

    dlg = CImportRefBooks(args)
    dlg.readFile(inFile)

if __name__ == '__main__':
    main()