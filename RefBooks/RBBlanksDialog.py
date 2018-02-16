# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Blank.BlankItemsListDialog import CBlanksItemsListDialog
from RefBooks.Tables import rbCode, rbName
from Ui_RBBlanksEditor import Ui_ItemEditorDialog
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CEnumCol, CTextCol
from library.Utils import forceInt, forceString, forceStringEx, toVariant


class CBlanksList(CBlanksItemsListDialog):
    def __init__(self, parent):
        CBlanksItemsListDialog.__init__(self, parent, [
            CTextCol(u'код', ['code'], 20),
            CTextCol(u'название', ['name'], 20),
            CEnumCol(u'контроль серии', ['checkingSerial'], [u'нет', u'мягко', u'жестко'], 20),
            CEnumCol(u'контроль номера', ['checkingNumber'], [u'нет', u'мягко', u'жестко'], 20),
            CEnumCol(u'контроль количества', ['checkingAmount'], [u'нет', u'мягко', u'жестко'], 20)
        ], 'rbTempInvalidDocument', 'rbBlankTempInvalids', 'ActionType', 'rbBlankActions', [])
        self.setWindowTitleEx(u'Типы бланков')
        self.treeItemsTempInvalid.expand(self.modelTree.index(0, 0))
        self.tblItemsTempInvalid.addPopupDelRow()
        self.tblItemsOthers.addPopupDelRow()

    def setupUi(self, widget):
        CBlanksItemsListDialog.setupUi(self, widget)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, widgetIndex):
        if widgetIndex == 0:
            self.treeItemsTempInvalid.expand(self.modelTree.index(0, 0))
        else:
            self.treeItemsOthers.expand(self.modelTree2.index(0, 0))

    def getItemEditor(self):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 0:
            tableName = u'rbBlankTempInvalids'
            doctypeId = self.currentGroupId()
        else:
            tableName = u'rbBlankActions'
            doctypeId = self.currentGroupId()
        return CBlanksEditor(self, tableName, doctypeId)


class CBlanksEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent, tableName, doctypeId):
        CItemEditorBaseDialog.__init__(self, parent, tableName)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Бланк')
        self.setupDirtyCather()
        self.doctypeId = doctypeId

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbCheckingSerial.setCurrentIndex(forceInt(record.value('checkingSerial')))
        self.cmbCheckingNumber.setCurrentIndex(forceInt(record.value('checkingNumber')))
        self.cmbCheckingAmount.setCurrentIndex(forceInt(record.value('checkingAmount')))

    def getRecord(self):
        if not self.doctypeId:
            return None
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('doctype_id', toVariant(self.doctypeId))
        record.setValue(rbCode, toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName, toVariant(forceStringEx(self.edtName.text())))
        record.setValue('checkingSerial', toVariant(forceInt(self.cmbCheckingSerial.currentIndex())))
        record.setValue('checkingNumber', toVariant(forceInt(self.cmbCheckingNumber.currentIndex())))
        record.setValue('checkingAmount', toVariant(forceInt(self.cmbCheckingAmount.currentIndex())))
        return record

    def save(self):
        try:
            prevId = self.itemId()
            db = QtGui.qApp.db
            db.transaction()
            try:
                record = self.getRecord()
                if not record:
                    return True
                id = db.insertOrUpdate(db.table(self._tableName), record)
                self.saveInternals(id)
                db.commit()
            except:
                db.rollback()
                self.setItemId(prevId)
                raise
            self.setItemId(id)
            self.afterSave()
            return id
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self, u'Внимание', unicode(e), QtGui.QMessageBox.Close)
            return None
