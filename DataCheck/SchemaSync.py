# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import re

from PyQt4 import QtCore, QtGui

from library.database import connectDataBase
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceString, toVariant, getVal

from Ui_SchemaSync import Ui_SchemaSyncDialog


reConstrain = re.compile(u'[ ]*CONSTRAINT.*')

routineFieldNames = ('specific_name', 'routine_catalog', #'routine_schema', 'routine_name',
       'routine_type',  'dtd_identifier', 'routine_body', 'routine_definition',
       'external_name', 'external_language', 'parameter_style', 'is_deterministic',
       'sql_data_access', 'sql_path', 'security_type', 'created', 'last_altered',
       'sql_mode', 'routine_comment', 'definer')


keyFieldNames = ('Table', 'Non_unique', 'Key_name', 'Seq_in_index', 'Column_name',
                        #'Collation',  'Cardinality',
                        'Sub_part', 'Packed', 'Null', 'Index_type',
                        'Comment')


columnFieldNames = ('Field','Type', 'Collation', 'Null', 'Key', 'Default',
    'Extra', 'Privileges', 'Comment', 'ORDINAL_POSITION')


constraintsFieldNames = ('CONSTRAINT_NAME', 'TABLE_CATALOG',
                                #'TABLE_SCHEMA',
                                'TABLE_NAME',
                                'COLUMN_NAME', 'ORDINAL_POSITION', 'POSITION_IN_UNIQUE_CONSTRAINT',
                               #'REFERENCED_TABLE_SCHEMA',
                               'REFERENCED_TABLE_NAME', 'REFERENCED_COLUMN_NAME')

def DoSchemaSync():
    serverName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'SchemaSyncServerName', ''))
    serverPort = forceInt(getVal(
        QtGui.qApp.preferences.appPrefs, 'SchemaSyncServerPort', 0))
    dbName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'SchemaSyncDbName', ''))
    userName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'SchemaSyncUserName', ''))

    dlg = CSchemaSyncDialog()
    dlg.edtServerName.setText(serverName)
    dlg.edtServerPort.setValue(serverPort)
    dlg.edtDatabaseName.setText(dbName)
    dlg.edtUserName.setText(userName)
    dlg.exec_()

    QtGui.qApp.preferences.appPrefs['SchemaSyncServerName'] = toVariant(
                                                                            dlg.edtServerName.text())
    QtGui.qApp.preferences.appPrefs['SchemaSyncServerPort'] = toVariant(
                                                                            dlg.edtServerPort.value())
    QtGui.qApp.preferences.appPrefs['SchemaSyncDbName'] = toVariant(
                                                                            dlg.edtDatabaseName.text())
    QtGui.qApp.preferences.appPrefs['SchemaSyncUserName'] = toVariant(
                                                                            dlg.edtUserName.text())


class CSchemaSyncDialog(CDialogBase,  Ui_SchemaSyncDialog):
    def __init__(self,  parent=None):
        CDialogBase.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.showLog = True
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.createStmtCache = {}


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.logBrowser.append(str)
            self.logBrowser.update()
            QtGui.qApp.processEvents()


    def getTableFieldParams(self,  table,  field,  db):
        stmt = 'SHOW FULL COLUMNS FROM `%s`.`%s`'\
            ' WHERE `Field` = BINARY \'%s\';' % (db.db.databaseName(), table, field)
        query = db.query(stmt)
        params = {}
        query.next()
        record = query.record()

        for p in columnFieldNames:
            params[p] = forceString(record.value(p))

        return params


    def makeColumnSqlString(self, db, table, col):
        stmt = self.getCreateTableStmt(db, table)
        colName = '`%s`' % col
        result = ''

        for s in stmt:
            if s.strip()[:len(colName)] == colName:
                result = s[:-1] if s[-1:] == ',' else s
                break

        assert result != ''
        return result


    def makeSyncColumnSqlStr(self, table,  col, masterDb,  slaveDb):
        masterParams = self.getTableFieldParams(table,  col,  masterDb)
        slaveParams = self.getTableFieldParams(table,  col,  slaveDb)
        syncParams = []
        syncNeeded = False
        isPrimaryKey = (masterParams['Key'] == 'PRI')

        for p in columnFieldNames:
            if masterParams[p] != slaveParams[p]:
                self.log(u'  Поле "%s" "%s": "%s" <> "%s"'% (col,
                                        p,  masterParams[p] , slaveParams[p]))
                syncNeeded = True
                break


        if syncNeeded:
            columnString = self.makeColumnSqlString(masterDb, table, col)
            stmt = u'MODIFY %s' % columnString
            return stmt

        return ''


    def getCreateTableStmt(self, db, tableName):
        dbName = db.db.databaseName()
        key = (dbName,  tableName)
        result = self.createStmtCache.get(key)

        if not result:
            stmt = 'SHOW CREATE TABLE `%s`.`%s`' % (dbName,  tableName)
            query = db.query(stmt)
            query.first()
            record = query.record()
            result = forceString(record.value(1)).split('\n') if record else []
            self.createStmtCache[key] = result

        return result


    def addTable(self, tableName,  masterDb, slaveDb):
        constrains = []
        create = []
        createStmt = self.getCreateTableStmt(masterDb, tableName)

        for str in createStmt:
            m = reConstrain.match(str)

            if m:
                constrains.append(str)
            else:
                create.append(str)

        # убираем запятую из предпоследней строчки
        if len(create) > 2:
            if create[-2] and create[-2][-1:] == ',':
                create[-2] = create[-2][:-1]

        if len(constrains):
            if constrains[-1] and constrains[-1][-1:] == ',':
                constrains[-1] = constrains[-1][:-1]

        stmt = u'\n '.join([k for k in create])+';'
        constrStmt = u'ALTER TABLE `%s`\n' % tableName + \
            '\n '.join(['ADD %s' % s for s in constrains]) + ';'
        return (stmt,  constrStmt)


    def makeAddColumnSqlStr(self,  db,  table,  col, prevCol):
        u""" Добавляем колонку в таблицу """
        self.log(u'  Новая колонка "%s"' % col)
        #params = self.getTableFieldParams(table,  col,  db)
        stmt = u'ADD %s' % self.makeColumnSqlString(db, table, col)
        if prevCol:
            stmt += ' AFTER `%s`' % prevCol
        return stmt


    def getKeyList(self,  db,  table):
        stmt = "SHOW INDEX FROM `%s`.`%s`;" % (db.db.databaseName(),  table)
        query = db.query(stmt)
        result = {}

        while query.next():
            record = query.record()
            params = {}

            for p in keyFieldNames:
                params[p] = forceString(record.value(p))

            result[params['Column_name']+params['Key_name']] = params

        return result


    def getConstraintsList(self,  db,  table):
        stmt = """
            SELECT *
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE CONSTRAINT_SCHEMA = BINARY '%s'
                AND TABLE_NAME = BINARY '%s'
        """ % (db.db.databaseName(),  table)

        query = db.query(stmt)
        constraintsList = {}

        while query.next():
            record = query.record()
            params = {}

            for p in constraintsFieldNames:
                params[p] = forceString(record.value(p))

            constraintsList[params['CONSTRAINT_NAME']+params['COLUMN_NAME']] = params

        return constraintsList


    def makeKeyStmt(self,  keys,  keyParams):
        u""" формирует sql выражения для первичных ключей"""
        stmtList = []

        for key in keys:
            columns = []
            fullText = ''
            indexType = ''
            for p in keyParams.values():
                if p['Key_name'] == key:
                    columns.append((u'`%s`' % p['Column_name'],  forceInt(p['Seq_in_index'])))
                    if p['Index_type'] == 'FULLTEXT':
                        fullText = u'FULLTEXT'
                    elif p['Index_type'] in ('RTREE',  'HASH'):
                        # BTREE = default?
                        indexType = 'USING %s' % p['Index_type']

            # сортируем поля по позиции в индексе
            columns.sort(key=lambda (col,  idx): idx)

            if key == 'PRIMARY':
                stmtList.append(u'PRIMARY KEY ('+ u', '.join([k for (k,  i) in columns])+')')
            else:
                stmtList.append(u'%s INDEX `%s` %s (' % (fullText,  key,  indexType) + \
                    u', '.join([k for (k,  i) in columns])+')')

        return stmtList


    def makeConstrStmt(self,  db,  table, constrs):
        """ формирует sql выражения для внешних ключей """

        stmtList = []
        createStmt = self.getCreateTableStmt(db, table)

        for c in constrs:
            if c != 'PRIMARY':
                name = '`%s`' % c

                for s in createStmt:
                    if s.strip()[11:11+len(name)] == name:
                        stmtList.append(s[:-1] if s[-1:] == ',' else s)
                        break

        return stmtList


    def syncTableKeys(self,  table,  masterDb,  slaveDb):
        mKeyParams = self.getKeyList(masterDb,  table)
        sKeyParams = self.getKeyList(slaveDb,  table)
        mConstrParams =self.getConstraintsList(masterDb,  table)
        sConstrParams = self.getConstraintsList(slaveDb,  table)
        keysToRemove = []
        keysToAdd = []
        constrToRemove = []
        constrToAdd = []

        for key in sKeyParams.keys():
            if key not in mKeyParams.keys():
                keyName = sKeyParams[key]['Key_name']
                if keyName not in keysToRemove:
                    keysToRemove.append(keyName)
                    # если удаляемый ключ является внешним, нужно удалить
                    # соотв. constraint'ы
                    colName = sKeyParams[key]['Column_name']
                    for c in sConstrParams.keys():
                        constrName = sConstrParams[c]['CONSTRAINT_NAME']
                        if sConstrParams[c]['COLUMN_NAME'] == colName and \
                                                    constrName not in constrToRemove:
                            self.log(u' constraint `%s` удален вместе с индексом `%s`'\
                                      %  (constrName, colName))
                            constrToRemove.append(constrName)

        # удаляем внешние ключи
        for constr in sConstrParams.keys():
            constrName = sConstrParams[constr]['CONSTRAINT_NAME']
            if constr not in mConstrParams.keys() and \
                        constrName not in constrToRemove:
                self.log(u' constraint `%s` удален - отсутствует в эталонной бд'\
                                    %  constrName)
                constrToRemove.append(constrName)

        # проверка индексов
        for key in mKeyParams.keys():
            if key in sKeyParams.keys():
                # сравним параметры ключа
                for p in keyFieldNames:
                    if mKeyParams[key][p] != sKeyParams[key][p]:
                        slaveKeyName = sKeyParams[key]['Key_name']
                        self.log(u'key `%s`: `%s`: Эталон %s <> %s' % (slaveKeyName,
                                                    p, mKeyParams[key][p], sKeyParams[key][p]))
                        if slaveKeyName not in keysToRemove:
                            keysToRemove.append(slaveKeyName)
                            # если удаляемый ключ является внешним, нужно удалить
                            # соотв. constraint'ы
                            colName = sKeyParams[key]['Column_name']
                            for c in sConstrParams.keys():
                                constrName = sConstrParams[c]['CONSTRAINT_NAME']
                                if sConstrParams[c]['COLUMN_NAME'] == colName and \
                                                            constrName not in constrToRemove:
                                    constrToRemove.append(constrName)
                        masterKeyName = mKeyParams[key]['Key_name']
                        if masterKeyName not in keysToAdd:
                            keysToAdd.append(masterKeyName)
            else:
                masterKeyName = mKeyParams[key]['Key_name']
                for x in sKeyParams.values():
                    if x['Key_name'] == masterKeyName:
                        if masterKeyName not in keysToRemove:
                            keysToRemove.append(masterKeyName)
                if masterKeyName not in keysToAdd:
                    keysToAdd.append(masterKeyName)

        #проверка внешних ключей
        for c in mConstrParams.keys():
            if c in sConstrParams.keys():
                # сравниваем параметры внешнего ключа
                for p in constraintsFieldNames:
                    if mConstrParams[c][p] != sConstrParams[c][p]:
                        self.log(u'  f_key `%s`: `%s` Эталон %s <> %s' % \
                            (c,  p, mConstrParams[c][p],  sConstrParams[c][p]))
            else:
                # новый внешний ключ
                constrName = mConstrParams[c]['CONSTRAINT_NAME']
                constrToAdd.append(constrName)
                self.log(u'  Новый f_key `%s`' % (constrName))

        # если при синхронизации ключей удаляются constraint'ы
        # но они присутствуют в эталонной бд, и полностью совпадают
        # с эталоном, то нужно добавить их снова.

        for c in mConstrParams.values():
            constrName = c['CONSTRAINT_NAME']
            if constrName in constrToRemove and constrName not in constrToAdd:
                constrToAdd.append(constrName)

        stmtList = []

        for c in constrToRemove:
            if c !=  'PRIMARY':
                stmtList.append(u'DROP FOREIGN KEY `%s`' % c)

        for k in keysToRemove:
            if k == 'PRIMARY':
                stmtList.append(u'DROP PRIMARY KEY')
            else:
                stmtList.append(u'DROP INDEX `%s`' % k)

        # добавляем выражения для индексов и внешних ключей
        stmtList.extend(["ADD %s" % s for s in \
            self.makeKeyStmt(keysToAdd,  mKeyParams)])
        constrList = ["ADD %s" % s for s in \
            self.makeConstrStmt(masterDb, table, constrToAdd)]

        return (stmtList,  constrList)


    def syncTableFields(self,  table,  masterDb,  slaveDb):
        masterColumnList = self.getColumnList(masterDb, table)
        slaveColumnList = self.getColumnList(slaveDb,  table)
        alterSpecsList = []

        for col in masterColumnList:
            QtGui.qApp.processEvents()
            if col in slaveColumnList:
                alterStr = self.makeSyncColumnSqlStr(table,  col, masterDb,  slaveDb)
            else:
                idx = masterColumnList.index(col) - 1
                prevColName = masterColumnList[idx] if idx > 1 else ''
                alterStr = self.makeAddColumnSqlStr(masterDb, table,  col,  prevColName)

            if alterStr != '':
                alterSpecsList.append(alterStr)

        for col in slaveColumnList:
            if not (col in masterColumnList):
                self.log(u' - Удаляем поле `%s`' % col)
                alterSpecsList.append('DROP COLUMN `%s`' % col)

        # синхронизируем ключи
        (keyStmts,  constrStmts) = self.syncTableKeys(table,  masterDb,  slaveDb)
        alterSpecsList.extend(keyStmts)

        stmt = ''
        constrStr = ''

        if len(alterSpecsList)>0:
            stmt = u'ALTER TABLE `%s`.`%s` '%(slaveDb.db.databaseName(), \
                table) + u', '.join([k for k in alterSpecsList])+u';'

        if len(constrStmts)>0:
            constrStr = u'ALTER TABLE `%s`.`%s` '%(slaveDb.db.databaseName(), \
                table) + u', '.join([k for k in constrStmts])+u';'

        return (stmt,  constrStr)


    def syncTables(self,  masterDb,  slaveDb):
        slaveTableList = self.getTableList(slaveDb)
        masterTableList = self.getTableList(masterDb)
        self.progressBar.setText(u'Синхронизируем таблицы')
        self.progressBar.setMaximum(len(masterTableList))
        self.progressBar.setValue(0)
        alterSpecsList = []
        constrSpecsList = []

#        for x in slaveTableList: # linux bugfix
#            x = x.lower()

        for table in masterTableList:
            QtGui.qApp.processEvents()
            if table in slaveTableList:
                self.log(u' ├  Синхронизируется таблица "%s"' % table)
                (alterStr, constrStr) = self.syncTableFields(table,  masterDb,  slaveDb)
                for (str,  list) in ((alterStr,  alterSpecsList), \
                                        (constrStr,  constrSpecsList)):
                    if len(str) > 0:
                        list.append(u' LOCK TABLE `%s`.`%s` WRITE;' % \
                                          (slaveDb.db.databaseName(),  table))
                        list.append(str)
                        list.append(u'UNLOCK TABLES;')
            else:
                self.log(u' ├[+] новая таблица "%s"' % table)
                (alterStr,  constrStr) = self.addTable(table,   masterDb,  slaveDb)
                if len(alterStr) >0:
                    alterSpecsList.append(alterStr)
                if len(constrStr)>0:
                    constrSpecsList.append(u' LOCK TABLE `%s`.`%s` WRITE;' % \
                                          (slaveDb.db.databaseName(),  table))
                    constrSpecsList.append(constrStr)
                    constrSpecsList.append(u'UNLOCK TABLES;')

            self.progressBar.step()

        for table in slaveTableList:
            if not (table in masterTableList):
                self.log(u' ├[-] удаляем таблицу `%s`' % table)
                alterSpecsList.append('DROP TABLE IF EXISTS `%s`.`%s`;' % (
                    slaveDb.db.databaseName(), table))

        # выражения для внешних ключей - в конец скрипта
        # чтобы не было ссылок на несозданные таблицы
        alterSpecsList.extend(constrSpecsList)

        if len(alterSpecsList)>0:
            self.progressBar.setText(u'Запись изменений в БД')
            self.progressBar.setMaximum(len(alterSpecsList))
            self.progressBar.setValue(0)

            for stmt in alterSpecsList:
                slaveDb.query(stmt)
                self.progressBar.step()
        else:
            self.log(u'<b>База не отличается от эталона<\b>')


    def getColumnList(self,  db,  tableName):
#        self.log(u'  ├  получаю список колонок таблицы %s, бд: %s' % (tableName, dbName))
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
            WHERE table_schema = BINARY '%s'
                AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """ % db.db.databaseName()

        query = db.query(stmt)
        tableList = []

        while (query.next()):
            record = query.record()
            tableList.append(forceString(record.value('table_name')))

        return tableList


    def getViewList(self,  db):
        self.log(u'Получаю список view для бд: %s' % db.db.databaseName())
        stmt = """
            SELECT table_name FROM information_schema.views
            WHERE table_schema = BINARY '%s'
            ORDER BY table_name;
        """ % db.db.databaseName()

        query = db.query(stmt)
        viewList = []

        while (query.next()):
            record = query.record()
            viewList.append(forceString(record.value('table_name')))

        return viewList


    def syncViewParams(self,  view,  masterDb,  slaveDb):
        pass


    def addView(self, view,  masterDb,  slaveDb):
        pass


    def syncViews(self, masterDb,  slaveDb):
        self.log(u' Синхронизация View:')

        masterViewList = self.getViewList(masterDb)
        slaveViewList = self.getViewList(slaveDb)
        self.progressBar.setText(u'Синхронизируем представления')
        self.progressBar.setMaximum(len(masterViewList))
        self.progressBar.setValue(0)

        for view in masterViewList:
            if view in slaveViewList:
                self.log(u' Синхронизируем view: %s' % view)
                self.syncViewParams(view,  masterDb,  slaveDb)
            else:
                self.log(u' Добавляем новый view: %s' % view)
                self.addView(view,  masterDb,  slaveDb)

            self.progressBar.step()


    def getRoutinesList(self,  db):
        self.log(u'Получаю список хранимых процедур для бд: %s' % db.db.databaseName())
        stmt = """
            SELECT routine_name FROM information_schema.routines
            WHERE routine_schema = BINARY '%s'
            ORDER BY routine_name;
        """ % db.db.databaseName()

        query = db.query(stmt)
        routinesList = []

        while (query.next()):
            record = query.record()
            routinesList.append(forceString(record.value('routine_name')))

        return routinesList


    def getRoutineParams(self,  routine,  db):
        stmt = """
            SELECT  specific_name, routine_catalog,
                        routine_type,  dtd_identifier, routine_body, routine_definition,
                        external_name, external_language, parameter_style, is_deterministic,
                        sql_data_access, sql_path, security_type, created, last_altered,
                        sql_mode, routine_comment, definer
            FROM information_schema.routines
            WHERE routine_schema = BINARY '%s'
                AND routine_name = BINARY '%s';
        """ % (db.db.databaseName(),  routine)

        routineParams = {}
        query = db.query(stmt)
        query.next()
        record = query.record()

        for fieldName in routineFieldNames:
            routineParams[fieldName] = record.value(fieldName)

        return routineParams


    def syncRoutineParams(self,  routine,  masterDb,  slaveDb):
        masterParams = self.getRoutineParams(routine,  masterDb)
        slaveParams = self.getRoutineParams(routine,  slaveDb)

        for p in routineFieldNames:
            mParam = forceString(masterParams[p])
            sParam = forceString(slaveParams[p])

            if mParam != sParam:
                self.log(u' Routine "%s", различается поле "%s":' % (routine,  p))
                self.log(u'  Эталон "%s" <> "%s"'% (mParam, sParam))


    def addRoutine(self,  routine,  masterDb,  slaveDb):
        pass


    def removeRoutine(self,  routine,  db):
        pass


    def syncRoutines(self,  masterDb,  slaveDb):
        self.log(u' Синхронизация хранимых процедур:')

        masterRoutinesList = self.getRoutinesList(masterDb)
        slaveRoutinesList = self.getRoutinesList(slaveDb)
        self.progressBar.setText(u'Синхронизируем хранимые процедуры')
        self.progressBar.setMaximum(len(masterRoutinesList))
        self.progressBar.setValue(0)

        for routine in masterRoutinesList:
            if routine in slaveRoutinesList:
                self.log(u' Синхронизируем процедуру: %s' % routine)
                self.syncRoutineParams(routine,  masterDb,  slaveDb)
            else:
                self.log(u' Добавяем новую процедуру: %s' % routine)
                self.addRoutine(routine,  masterDb,  slaveDb)

            self.progressBar.step()

        for routine in slaveRoutinesList:
            if routine not in masterRoutinesList:
                self.log(u' Процедура %s удалена в эталонной бд. Удаляем.')
                self.removeRoutine(routine,  slaveDb)

    def schemaSync(self):
        try:
            self.logBrowser.clear()
            self.btnSync.setEnabled(False)
            self.log(u'[■] Подключение к эталонной базе данных: ')
            self.log(u' ├  Сервер: %s:%d ' % (self.edtServerName.text(),  self.edtServerPort.value()))
            self.log(u' ├  Имя базы данных: %s, пользователь: %s' % (self.edtDatabaseName.text(),
                        self.edtUserName.text()))
            masterDb = connectDataBase('MYSQL', self.edtServerName.text(),  self.edtServerPort.value(),
                                       self.edtDatabaseName.text(),  self.edtUserName.text(), self.edtPassword.text(),  'SyncConnection')
            db = QtGui.qApp.db
            self.syncTables(masterDb,  db)
#            self.syncViews(masterDb,  db)
#            self.syncRoutines(masterDb,  db)
            self.log(u'[*] Отключение от эталонной базы данных.')
            masterDb.close()
            self.progressBar.setText(u'Готово')
        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            #masterDb.close()
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            #masterDb.close()
            return False

        self.btnSync.setEnabled(True)
        return True


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnSync_clicked(self):
        self.schemaSync()
