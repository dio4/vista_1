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

import zipfile

from library.dbfpy.dbf import Dbf
from library.Utils import *

class CAccount(object):

    class RequiredFilesNotFoundError(Exception):
        """Обязательные файлы-реестра не найдены."""
        def __init__(self, requiredFiles):
            self.requiredFiles = requiredFiles

    class InsertError(Exception):
        """Не удалось загрузить файл-реестра."""
        def __init__(self, fileName, message):
            self.fileName = fileName
            self.message = message

    _labels = {'P': 1, 'U': 1, 'D': 1, 'L': 0, 'N': 0}

    def __init__(self, fileName, callbackUpdate):
        self._db = QtGui.qApp.db
        self._dirName = QtGui.qApp.getTmpDir('CheckAccounts')
        self._fileNames = []
        zipFile = zipfile.ZipFile(fileName, mode='r', allowZip64=True)
        for fileName in zipFile.namelist():
            if os.path.splitext(fileName)[1].upper() == u'.DBF':
                zipFile.extract(fileName, self._dirName)
                self._fileNames.append(fileName)
        self._callbackUpdate = callbackUpdate

    def update(self):
        self.clear()
        labels = self._labels.copy()
        isRollback = False
        dbfFile = None
        self._db.transaction()
        try:
            for fileName in self._fileNames:
                if fileName[:1] in labels.keys():
                    try:
                        dbfFile = Dbf(os.path.join(self._dirName, fileName), readOnly=True, encoding='cp866')
                        if dbfFile.recordCount:
                            if not self._callbackUpdate(fileName, 0, dbfFile.recordCount):
                                isRollback = True
                                return
                            insertRowCount = 0
                            rbTable = self._db.table('rbCheckAccounts' + fileName[:1])
                            for dbfRow in dbfFile:
                                newRecord = rbTable.newRecord()
                                for fieldName, fieldValue in dbfRow.asDict().items():
                                    fieldValue = forceStringEx(fieldValue)
                                    if fieldValue:
                                        newRecord.setValue(forceString(fieldName), toVariant(fieldValue))
                                self._db.insertRecord(rbTable, newRecord)
                                insertRowCount += 1
                                if not self._callbackUpdate(fileName, insertRowCount, dbfFile.recordCount):
                                    isRollback = True
                                    return
                            del labels[fileName[:1]]
                        dbfFile.close()
                        dbfFile = None
                    except Exception as e:
                        isRollback = True
                        raise self.InsertError(fileName, e)
            requiredFiles = [label for label, required in labels.items() if required]
            if requiredFiles:
                isRollback = True
                raise self.RequiredFilesNotFoundError(requiredFiles)
            self._db.commit()
        finally:
            if isRollback:
                self._db.rollback()
            if dbfFile:
                dbfFile.close()
            QtGui.qApp.removeTmpDir(self._dirName)

    @classmethod
    def clear(cls):
        for label in cls._labels:
            QtGui.qApp.db.query(u'DELETE FROM rbCheckAccounts%s' % label)