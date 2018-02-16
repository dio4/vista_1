#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path

from library.dbfpy.dbf import *
from library.DialogBase import CDialogBase
from library.TableModel import *

from Ui_DbfViewDialog import Ui_DbfViewDialog

gFileName = ''

def viewDbf(widget=None):
    global gFileName
    if gFileName == '':
        gFileName = QtGui.qApp.getSaveDir()
    fileName = forceString(QtGui.QFileDialog.getOpenFileName(
        widget, u'Укажите DBF файл', gFileName, u'Файлы DBF (*.dbf)'))
    if fileName != '' :
        gFileName = fileName
        CDbfViewDialog(widget, fileName=fileName, encoding='cp866').exec_()



class CDbfViewDialog(CDialogBase, Ui_DbfViewDialog):
    def __init__(self, parent, dbf=None, fileName='', encoding='cp866'):
        CDialogBase.__init__(self, parent)
        self.model = CDbfModel(self)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.tblDbf.setModel(self.model)
        self.tblDbf.verticalHeader().setVisible(True)
        self.tblDbf.setFocus(Qt.OtherFocusReason)
        self.setup(dbf, fileName, encoding)


    def setup(self, dbf=None, fileName='', encoding='cp866'):
        if dbf is None:
            if fileName:
                dbf = Dbf(fileName, readOnly=True, encoding=encoding, enableFieldNameDups=True)
        if dbf:
            self.setWindowTitle(u'Просмотр DBF файла '+os.path.basename(dbf.name))
            self.model.setDbf(dbf)
            charWidth = self.tblDbf.fontMetrics().averageCharWidth()+1
            for i in xrange(self.model.columnCount()):
                self.tblDbf.setColumnWidth(i, charWidth*min(32, max(3, self.model.getColumnWidth(i)+2)))
            rows = self.model.rowCount()
            self.statusBar.showMessage(u'%d %s' % (rows, agreeNumberAndWord(rows, (u'запись', u'записи', u'записей'))))



class CCache(object):
    def __init__(self):
        self.keys = []
        self.data = {}

    def get(self, key):
         return self.data.get(key, None)


    def put(self, key, val):
        if self.data.has_key(key):
            self.data[key] = val
        else:
            if len(self.keys)>100:
                del self.data[self.keys[0]]
                del self.keys[0]
            self.data[key] = val
            self.keys.append(key)


class CDbfModel(QAbstractTableModel):
    alignLeft  = QVariant(Qt.AlignLeft|Qt.AlignVCenter)
    alignRight = QVariant(Qt.AlignRight|Qt.AlignVCenter)

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.dbf = None
        self.fieldDefs = None
        self.alignment = None
        self.cache = CCache()


    def setDbf(self, dbf):
        self.dbf = dbf
        if dbf:
            self.fieldDefs = dbf.fieldDefs
            self.alignment = []
            for fieldDef in self.fieldDefs:
                self.alignment.append(self.alignRight if fieldDef.typeCode == 'N' else self.alignLeft)
        else:
            self.fieldDefs = None
            self.alignment = None

        self.cache = CCache()
        self.reset()

    def getColumnWidth(self, column):
        if self.dbf:
            columnDef = self.fieldDefs[column]
            return max(len(columnDef.name), columnDef.length)
        return 0

    def getRecord(self, row):
        record = self.cache.get(row)
        if record == None:
            record = self.dbf[row]
            self.cache.put(row, record)
        return record


    def rowCount(self, parentIndex = QtCore.QModelIndex()):
        if self.dbf:
            return self.dbf.recordCount
        else:
            return 0


    def columnCount(self, parentIndex = QtCore.QModelIndex()):
        if self.dbf:
            return len(self.fieldDefs)
        else:
            return 0


    def flags(self, index):
        result = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return result


    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if self.dbf:
                    return toVariant(self.fieldDefs[section].name)
            if role == Qt.ToolTipRole:
                fieldDef = self.fieldDefs[section]
                text = fieldDef.name+': '+fieldDef.typeCode
                if fieldDef.length:
                    text = text + str(fieldDef.length)
                    if fieldDef.decimalCount:
                        text = text + '.' + str(fieldDef.decimalCount)
                return toVariant(text)
        if orientation == Qt.Vertical:
            if role == Qt.DisplayRole:
                return toVariant(section+1)
            if role == Qt.TextAlignmentRole:
                return self.alignRight
        return QVariant()


    def data(self, index, role):
        if not index.isValid() or not self.dbf:
            return QVariant()
        column = index.column()
        row    = index.row()
        if role == Qt.DisplayRole:
            record = self.getRecord(row)
            try:
                return toVariant(record[column])
            except:
                return QVariant()
        if role == Qt.ToolTipRole:
            record = self.getRecord(row)
            try:
                return toVariant(record[column])
            except:
                return toVariant(u'Ошибка в данных')
        elif role == Qt.TextAlignmentRole:
            return self.alignment[column]
        elif role == Qt.CheckStateRole:
            return QVariant()
        return QVariant()