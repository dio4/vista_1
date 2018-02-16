# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Ui_KLADRMilitaryUnitsEditor import Ui_ItemEditorDialog
from Ui_KLADRMilitaryUnitsFilterDialog import Ui_ItemFilterDialog
from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CTextCol
from library.Utils import forceString, forceStringEx, toVariant


class CKLADRMilitaryUnitsList(CItemsListDialog):
    def __init__(self, parent):
        self.idFieldName = 'CODE'
        CItemsListDialog.__init__(
            self,
            parent,
            [
                CTextCol(u'Наименование', ['NAME'], 40),
                CTextCol(u'Код', ['CODE'], 13),
                CTextCol(u'ИНФИС код', ['infis'], 5),
            ],
            'kladr.KLADR',
            ['NAME'],
            filterClass=CKLADRMilitaryUnitsFilterDialog,
            idFieldName='CODE'
        )
        self.setWindowTitleEx(u'Воинские части')

    def select(self, props):
        table = self.model.table()
        cond = []
        cond.append(table['NAME'].like('%s'%(u'%в/ч%')))
        nameTemp = props.get('nameTemp', '')
        if nameTemp:
#            cond.append(table['NAME'].like(addDotsEx(nameTemp)))
            cond.append(table['NAME'].like(nameTemp))
        return QtGui.qApp.db.getColumnValues(table.name(), self.idFieldName, cond, self.order, handler=forceString)

    def getItemEditor(self):
        return CKLADRMilitaryUnitsEditor(self)


class CKLADRMilitaryUnitsEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'kladr.KLADR')
        self.setupUi(self)
        self.setWindowTitle(u'Воинская часть')
        self.new    = None
        self.code   = None

    def setRecord(self, record):
        self.new = False
        CItemEditorBaseDialog.setRecord(self, record)
        MUName = forceString(record.value('NAME'))
        if u'в/ч' in MUName:
            if u'в/ч' == MUName[:3]:
                count = len(MUName)-4 if len(MUName)-4 > 8 else 8
                self.edtName.setInputMask(u'в/ч '+'X'*count)
                MUName = MUName.split(u'в/ч')[1].strip(' ')
            else:
                self.edtName.setInputMask('')
        else:
            self.edtName.setInputMask('')
        self.edtName.setText(MUName)
        self.edtInfis.setText(forceString(record.value('infis')))
        self.edtCode.setText(forceString(record.value('CODE')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('NAME', toVariant(self.edtName.text().simplified()))
        record.setValue('infis', toVariant(self.edtInfis.text().simplified()))
        code = self.edtCode.text().simplified()
        record.setValue('CODE', toVariant(code))
        record.setValue('parent', toVariant(code[:3]))
        record.setValue('prefix', toVariant(code[:2]))
        return record

    def load(self, id):
        db = QtGui.qApp.db
        record = db.getRecordEx(db.table(self._tableName), '*', where='CODE = %s' % id)
        assert record
        self.setRecord(record)
        self.setIsDirty(False)

    def exec_(self):
        name = self.edtName.text().simplified()
        if not name:
            self.new = True
            self.edtName.setInputMask(u'в/ч '+'X'*8)
        else:
            self.code = self.edtCode.text().simplified()
        return CItemEditorBaseDialog.exec_(self)

    def checkDataEntered(self):
        chkCode = self.checkUniqueCode()
        result = CItemEditorBaseDialog.checkDataEntered(self)
        return result and chkCode

    def checkUniqueCode(self):
        code = self.edtCode.text().simplified()
        if not self.new:
            if code == self.code:
                return True
        chkCode = checkCode(code)
        if chkCode:
            QtGui.QMessageBox.critical(self,
                                         u'Внимание!',
                                         u'Данный код уже существует',
                                         QtGui.QMessageBox.Ok)
            return False
        return True

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtName_textEdited(self, txt):
        if self.new:
            txt = txt.split(' ')[1]
            self.edtInfis.setText(txt)
            count = 8-len(txt)
            self.edtCode.setText('001'+'0'*count+txt+'00')

def checkCode(code):
    table = 'kladr.KLADR'
    col   = 'CODE'
    where = '`CODE`=\'%s\''% code
    order = ''
    limit = None
    db = QtGui.qApp.db
    stmt = db.selectStmt(table, col, where,  order = order, limit = limit)
    query = db.query(stmt)
    result = False
    while query.next():
        result = query.value(0).toString
    return result

# ########################

class CKLADRMilitaryUnitsFilterDialog(QtGui.QDialog, Ui_ItemFilterDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Фильтр войсковых частей')

    def setProps(self, props):
        self.edtNameTemplate.setText(props.get('nameTemp', ''))

    def props(self):
        resume = {}
        resume['nameTemp'] = forceStringEx(self.edtNameTemplate.text())
        return resume
