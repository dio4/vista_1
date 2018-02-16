#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on Jul 17, 2012

@author: atronah
"""
import PyQt4
from library.DialogBase import CDialogBase
from Exchange.Ui_DbfToMySqlDumpDialog import Ui_DbfToMySqlDumpDialog
from PyQt4.QtGui import QFileDialog, QMessageBox
from PyQt4.QtCore import QFile, QTextStream
from library.dbfpy.dbf import *
import os



mapDbfCodeToMySqlTypes = {'C' : 'VARCHAR(%(length)d)',
                          'N' : 'NUMERIC(%(length)d, %(decimal)d)',
                          'F' : 'FLOAT(%(length)d)',
                          'I' : 'INT',
                          'Y' : 'VARCHAR(%(length)d)',
                          'L' : 'BOOL',
                          'M' : 'TEXT',
                          'D' : 'DATE',
                          'T' : 'TIMESTAMP(%(length)d)'
                          }

def typeCodeToMySQLType(typeCode, length = None, decimalCount = 0):
    params = {'length' : length if length else 8,
              'decimal' : decimalCount
              } 
    return mapDbfCodeToMySqlTypes[typeCode] % params

def createHeaderStmt(fieldDefs, tableName, charset, engine):
    valuesList = []
    for fieldDef in fieldDefs:
        name = fieldDef.name
        typeCode = fieldDef.typeCode
        length = fieldDef.length
        decimal = fieldDef.decimalCount
        valuesList.append("`%s` %s NOT NULL" % (name, typeCodeToMySQLType(typeCode, length, decimal)))
    values = ', \n'.join(valuesList)
         
         
    outStmt = """
    DROP TABLE IF EXISTS `%(tableName)s`;
    SET @saved_cs_client = @@character_set_client;
    SET character_set_client = %(encoding)s;
    CREATE TABLE `%(tableName)s` (
    %(fields)s
    ) ENGINE = %(engine)s DEFAULT CHARSET = %(encoding)s;
    SET character_set_client = @saved_cs_client;
    """ % {'tableName' : tableName, 'encoding' : charset, 'engine' : engine, 'fields' : values}
    
    return outStmt

    
def exportToSql(fileName, tableName = None, dbfEncoding = 'cp866', mySqlCharset = 'utf8', tableEngine = 'MyISAM'):
    dbf = Dbf(fileName, readOnly=True, encoding=dbfEncoding, enableFieldNameDups=False)
    tableName = tableName if tableName else os.path.splitext(os.path.basename(fileName))[0]
    outStmt = ''
    if dbf:
        recordCount = len(dbf)
        if recordCount <= 0:
            return
        outStmt += createHeaderStmt(fieldDefs = dbf.fieldDefs, tableName = tableName, charset = mySqlCharset, engine = tableEngine)
        insertsList = []
        for row in xrange(recordCount):
            record = dbf[row]
            valuesList = []
            for value in record.asList():
                valuesList.append("'%s'" % unicode(value))
            insertsList.append("INSERT INTO `%(tableName)s` VALUES(%(values)s);" % {'tableName' : tableName, 'values' : ','.join(valuesList)})
        
        inserts = '\n'.join(insertsList)
        outStmt += """
        LOCK TABLES `%(tableName)s` WRITE;
        /*!40000 ALTER TABLE `%(tableName)s` DISABLE KEYS */;
        %(inserts)s
        /*!40000 ALTER TABLE `%(tableName)s` ENABLE KEYS */;
        UNLOCK TABLES;
        """ % {'tableName' : tableName, 'inserts' : inserts}
        
    return outStmt





class CDbfToMySqlDumpDialog(CDialogBase, Ui_DbfToMySqlDumpDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Формирование файла дампов MySql из файлов DBF')
        self.lblMySqlCodec.setVisible(False)
        self.cmbMySqlCodec.setVisible(False)
        
    @PyQt4.QtCore.pyqtSlot()
    def on_btnAddFiles_clicked(self):
        fileNames = QFileDialog.getOpenFileNames(parent = self, caption = u'Выберите исходные файлы', filter = u'DBF (*.dbf)')
        self.lstSourceFiles.addItems(fileNames)
        
    @PyQt4.QtCore.pyqtSlot()    
    def on_btnDelFiles_clicked(self):
        itemsForDel = self.lstSourceFiles.selectedItems()
        for item in itemsForDel:
            self.lstSourceFiles.takeItem(self.lstSourceFiles.row(item))
            
    @PyQt4.QtCore.pyqtSlot()        
    def on_btnGenerate_clicked(self):
        self.outStmtText.clear()
        filesCount = self.lstSourceFiles.count()
        if filesCount <= 0:
            QMessageBox.warning(self, u'Ошибка', 
                                u'Не указанно ни одного входного файла', 
                                buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
            return
        
        isSaveToFile = self.chkSaveToFile.isChecked()
        for fileIndex in xrange(filesCount):
            fileName = unicode(self.lstSourceFiles.item(fileIndex).text())
            if os.path.exists(fileName):
                self.outStmtText.appendPlainText(exportToSql(fileName = fileName, 
                                                             dbfEncoding = unicode(self.cmbDbfCodec.currentText())))
        
        if isSaveToFile:
            outFileName = QFileDialog.getSaveFileName(parent=self, caption=u'Сохранить в файл...')
            outFile = QFile(outFileName)
            if outFile.open(QFile.Text | QFile.WriteOnly):
                outStream = QTextStream(outFile)
                outStream << self.outStmtText.toPlainText()
                outFile.close()
            else:
                QMessageBox.warning(self, u'Ошибка', 
                                    u'Невозможно создать указанный для сохранения файл \n %s' % outFileName, 
                                    buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
        