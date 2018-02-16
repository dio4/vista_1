# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from Ui_ActionPropertyMergeDialog import Ui_ActionPropertyMergeDialog
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CTextCol
from library.Utils import forceString
from library.database import CTableRecordCache


class CActionPropertyValueModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, cols=[
            CTextCol(u'Предыдущие значения', ['value'], 20)
        ])
        self.setTable('ActionProperty')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAP = db.table('ActionProperty')
        tableAPD = db.table('ActionProperty_Double')
        tableAPI = db.table('ActionProperty_Integer')
        tableAPS = db.table('ActionProperty_String')

        table = tableAP
        table = table.leftJoin(tableAPD, tableAPD['id'].eq(tableAP['id']))
        table = table.leftJoin(tableAPI, tableAPI['id'].eq(tableAP['id']))
        table = table.leftJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
        cols = [
            db.coalesce(tableAPD['value'],
                        tableAPI['value'],
                        tableAPS['value']).alias('value')
        ]
        self._table = table
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)


class CActionPropertyMergeDialog(CDialogBase, Ui_ActionPropertyMergeDialog):
    def __init__(self, parent):
        super(CActionPropertyMergeDialog, self).__init__(parent)
        self.addModels('SrcProperties', CActionPropertyValueModel(self))

        self.setupUi(self)
        self.setWindowTitle(u'Слияние свойств')

        self.setModels(self.tblSrcProperties, self.modelSrcProperties, self.selectionModelSrcProperties)
        self.tblSrcProperties.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.tblSrcProperties.clicked.connect(self.on_tblSrcPropertiesClicked)

    def on_tblSrcPropertiesClicked(self):
        index = self.tblSrcProperties.currentIndex()
        data = self.tblSrcProperties.model().data(index)
        self.edtDestProperty.setText(forceString(data))

    def setData(self, name, srcPropertyIdList, value):
        self.lblName.setText(name)
        self.tblSrcProperties.setIdList(srcPropertyIdList)
        self.edtDestProperty.setText(forceString(value))

    def getValue(self):
        return forceString(self.edtDestProperty.toPlainText())
