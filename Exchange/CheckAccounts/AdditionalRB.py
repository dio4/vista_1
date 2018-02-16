#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

import hashlib

from library.dbfpy.dbf import Dbf
from library.Utils import *

class CAdditionalRB(object):

    class FileNotFoundError(Exception):
        """Файл справочника не найден."""
        pass

    class ReferenceBookNotFoundError(Exception):
        """Справочник не найден в таблице дополнительных справочников модуля."""
        pass

    class MetadataMappingError(Exception):
        """Структура справочника не соответствует файлу справочника."""
        pass

    class CreateError(Exception):
        """Не удалось создать справочник."""
        pass

    # def __init__(self, fileName, callbackUpdate):
    #     """Конструктор для отладки загрузки справочника."""
    #     self._db = QtGui.qApp.db
    #     self._dirName = os.path.dirname(fileName)
    #     try:
    #         nameFilters = QStringList(os.path.basename(fileName))
    #         self._fileName = forceString(QDir(self._dirName).entryList(nameFilters, QDir.Files)[0])
    #     except:
    #         raise self.FileNotFoundError()
    #     self._additionalRBs = self._db.table('rbCheckAccountsAdditionalRBs')
    #     self._metaData = self._db.getRecordEx(self._additionalRBs, '*', self._additionalRBs['fileName'].eq(
    #         self._fileName.upper()))
    #     if not self._metaData:
    #         raise self.ReferenceBookNotFoundError()
    #     try:
    #         self._rbTable = self._db.table(forceString(self._metaData.value('tableName')))
    #     except:
    #         self._rbTable = None
    #     self._callbackUpdate = callbackUpdate

    def __init__(self, dirName, referenceBookInfo, callbackUpdate):
        self._db = QtGui.qApp.db
        self._dirName = forceString(dirName) if dirName else forceString(QtGui.qApp.getHomeDir()) # forceString(getVal(QtGui.qApp.preferences.appPrefs, 'CheckAccounts_additionalRBs', QVariant(QtGui.qApp.getHomeDir())))
        self._metaData = referenceBookInfo
        try:
            nameFilters = QStringList(forceString(self._metaData.value('fileName')))
            self._fileName = forceString(QDir(self._dirName).entryList(nameFilters, QDir.Files)[0])
        except:
            raise self.FileNotFoundError()
        self._additionalRBs = self._db.table('rbCheckAccountsAdditionalRBs')
        try:
            self._rbTable = self._db.table(forceString(self._metaData.value('tableName')))
        except:
            self._rbTable = None
        self._callbackUpdate = callbackUpdate

    def update(self):
        isRollback = False
        dbfFile = Dbf(os.path.join(self._dirName, self._fileName), readOnly=True, encoding='cp866')
        try:
            if not self._callbackUpdate(0, dbfFile.recordCount):
                return
            fileHash = forceString(hashlib.md5(dbfFile.stream.read()).hexdigest())
            if not self._rbTable or fileHash != forceString(self._metaData.value('hash')) or \
                    self._db.getCount(self._rbTable, countCol='id') != dbfFile.recordCount:
                self._drop()
                rbTableFields = [trim(field) for field in forceString(self._metaData.value('fields')).split(',')]
                fieldsStatement = ''
                fieldsStatementCount = 0
                for dbfField in dbfFile.fieldDefs:
                    if forceString(dbfField.name) in rbTableFields:
                        fieldsStatement += u'`%s` %s DEFAULT NULL COMMENT \'Поле %s\', ' % (forceString(dbfField.name),
                                                                                            self._getType(dbfField),
                                                                                            forceString(dbfField.name))
                        fieldsStatementCount += 1
                if len(rbTableFields) != fieldsStatementCount:
                    raise self.MetadataMappingError()
                rbTableIndexes = [index for index in map(trim, forceString(self._metaData.value('indexes')).split(','))
                                  if index]
                indexesStatement = ''
                for index in rbTableIndexes:
                    indexesStatement += u', INDEX `%s` (`%s`)' % (index, index)
                createStatement = u"""
                CREATE TABLE `%s` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Отметка удаления записи',
                    %s
                    PRIMARY KEY (`id`)
                    %s
                ) ENGINE = InnoDB DEFAULT charset = utf8 COMMENT = '%s';""" % (forceString(self._metaData.value('tableName')),
                                                                               fieldsStatement,
                                                                               indexesStatement,
                                                                               forceString(self._metaData.value('name')))
                try:
                    self._db.query(createStatement)
                    self._db.transaction()
                    try:
                        insertRowCount = 0
                        self._rbTable = self._db.table(forceString(self._metaData.value('tableName')))
                        for dbfRow in dbfFile:
                            newRecord = self._rbTable.newRecord()
                            for field in rbTableFields:
                                fieldValue = forceStringEx(dbfRow[field])
                                if fieldValue:
                                    newRecord.setValue(field, toVariant(fieldValue))
                            self._db.insertRecord(self._rbTable, newRecord)
                            insertRowCount += 1
                            if not self._callbackUpdate(insertRowCount, dbfFile.recordCount):
                                isRollback = True
                                return
                        self._metaData.setValue('hash', toVariant(fileHash))
                        self._db.updateRecord(self._additionalRBs, self._metaData)
                        self._db.commit()
                    except:
                        isRollback = True
                        raise
                except Exception as e:
                    raise self.CreateError(e)
            else:
                self._callbackUpdate(dbfFile.recordCount, dbfFile.recordCount)
        finally:
            if isRollback:
                self._db.rollback()
                self._drop()
            dbfFile.close()

    def _drop(self):
        if self._rbTable:
            self._db.query(u'DROP TABLE %s' % forceString(self._metaData.value('tableName')))
            del self._db.tables[self._rbTable.tableName]
            self._rbTable = None

    def _getType(self, dbfField):
        if dbfField.typeCode == 'N':
            if dbfField.decimalCount:
                return u'DOUBLE'
            else:
                return u'INT(11)'
        elif dbfField.typeCode == 'D':
            return u'DATE'
        else:
            return u'VARCHAR(%s)' % dbfField.length