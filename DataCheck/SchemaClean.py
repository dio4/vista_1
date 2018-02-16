# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils      import forceString

from Ui_SchemaClean     import Ui_SchemaCleanDialog


def DoSchemaClean():
    dlg = CSchemaCleanDialog()
    dlg.exec_()


class CSchemaCleanDialog(CDialogBase,  Ui_SchemaCleanDialog):
    def __init__(self,  parent=None):
        CDialogBase.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.showLog = True
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()


    def cleanTables(self,  db):
        self.progressBar.setText(u'Получение списка таблиц')
        QtGui.qApp.processEvents()
        tableList = self.getTableList(db)
        self.progressBar.setMaximum(len(tableList))
        self.progressBar.setValue(0)
        list = []

        for table in tableList:
            self.log(u' *  Проверка таблицы "%s"' % table)
            QtGui.qApp.processEvents()
            columnList = self.getColumnList(db,  table)

            if 'deleted' in columnList:
                self.log(u' +  Найдено поле  "deleted", будем чистить')
                list.append(u' LOCK TABLE `%s`.`%s` WRITE;' % \
                                        (db.db.databaseName(),  table))
                list.append(u' DELETE FROM `%s`.`%s` WHERE deleted != 0;' % \
                                        (db.db.databaseName(),  table))
                list.append(u'UNLOCK TABLES;')
            else:
                self.log(u' +  Поле  "deleted" не обнаружено')

            self.progressBar.step()

        if len(list)>0:
            self.progressBar.setText(u'Запись изменений в БД')
            self.progressBar.setMaximum(len(list))
            self.progressBar.setValue(0)

            for stmt in list:
                db.query(stmt)
                QtGui.qApp.processEvents()
                self.progressBar.step()

        self.btnClean.setEnabled(False)


    def getColumnList(self,  db,  tableName):
        stmt = """
            SHOW FULL COLUMNS
            FROM `%s`.`%s`;
        """ % (db.db.databaseName(),  tableName)

        query = db.query(stmt)
        columnList = []

        while (query.next()):
            record = query.record()
            columnList.append(forceString(record.value("Field")))
        return columnList


    def getTableList(self,  db):
        stmt = """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = '%s' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """ % db.db.databaseName()

        query = db.query(stmt)
        tableList = []

        while (query.next()):
            record = query.record()
            tableList.append(forceString(record.value('table_name')))

        return tableList


    def schemaClean(self):
        try:
            self.logBrowser.clear()
            db = QtGui.qApp.db
            self.cleanTables(db)
            self.progressBar.setText(u'Готово')
        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', unicode(msg), QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnClean_clicked(self):
        self.schemaClean()
