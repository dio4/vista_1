# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DbComboBox import CDbDataCache
from library.DialogBase import CDialogBase
from library.ItemListModel import CItemIndexCol, CItemListModel, CRowCounterCol
from library.RLS.RLSComboBox import CRLSComboBox
from library.RLS.ui.Ui_RLSExtendedEditor import Ui_RLSExtendedEditor
from library.RLS.ui.Ui_RLSExtendedVectorEditor import Ui_RLSExtendedVectorEditor
from library.Utils import forceInt, forceRef, forceStringEx, getPref, setPref
from library.crbcombobox import CRBComboBox


class CRLSExtendedEditor(CDialogBase, Ui_RLSExtendedEditor):
    def __init__(self, parent):
        super(CRLSExtendedEditor, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(u'Препарат')

        self.cmbForm.setTable('rls.rlsForm', codeFieldName='name')
        self.cmbForm.setShowFields(CRBComboBox.showName)
        self.cmbForm.popupView.setColumnHidden(0, True)

        self.edtAmount.setValidator(QtGui.QDoubleValidator(self))

    @QtCore.pyqtSlot(int)
    def on_cmbRLS_codeSelected(self, code):
        if code:
            formId = forceRef(QtGui.qApp.db.translate('rls.rlsNomen', 'code', code, 'form_id'))
            self.cmbForm.setValue(formId)

    def getAmount(self):
        text = self.edtAmount.text()  # type: QtCore.QString
        value, ok = text.toDouble()
        return value if ok else 0

    def value(self):
        return (
            self.cmbRLS.value(),
            self.cmbForm.value(),
            self.getAmount(),
            forceStringEx(self.edtNote.toPlainText())
        )

    def setValue(self, value):
        if isinstance(value, tuple):
            rlsId, formId, amount, note = value[:4]
            self.cmbRLS.setValue(rlsId)
            self.cmbForm.setValue(formId)
            self.edtAmount.setText(unicode(amount))
            self.edtNote.setText(note)

    @staticmethod
    def valueToText(code, formId, amount, note):
        rlsName = CRLSComboBox.codeToText(code)
        if formId:
            tableForm = QtGui.qApp.db.table('rls.rlsForm')
            cache = CDbDataCache.getData('rls.rlsForm', 'name', tableForm['id'].eq(formId), addNone=True, noneText=u'-')
            form = forceStringEx(cache.strList[-1])
        else:
            form = u''

        return u', '.join(filter(bool, [rlsName,
                                        u'{0} {1}'.format(amount, form) if form else unicode(amount),
                                        note]))


class CRLSExtendedVectorModel(CItemListModel):
    class CNomenCol(CItemIndexCol):
        def displayValue(self, item, **params):
            itemId = forceInt(self.value(item))
            db = QtGui.qApp.db
            tableVNomen = db.table('rls.vNomen')
            cache = CDbDataCache.getData('rls.vNomen', 'tradeName', tableVNomen['code'].eq(itemId), addNone=True, noneText=u'-')
            return forceStringEx(cache.strList[-1])

    class CFormCol(CItemIndexCol):
        def displayValue(self, item, **params):
            itemId = forceRef(self.value(item))
            tableForm = QtGui.qApp.db.table('rls.rlsForm')
            cache = CDbDataCache.getData('rls.rlsForm', 'name', tableForm['id'].eq(itemId), addNone=True, noneText=u'-')
            return forceStringEx(cache.strList[-1])

    def __init__(self, parent):
        super(CRLSExtendedVectorModel, self).__init__(
            parent,
            cols=[
                CRowCounterCol(u'№'),
                self.CNomenCol(u'Препарат', 0),
                self.CFormCol(u'Ед. изм.', 1),
                CItemIndexCol(u'Дозировка', 2),
                CItemIndexCol(u'Примечание', 3),
            ],
            extendable=True)

    def newItem(self):
        return None, None, 0, u''


class CRLSExtendedVectorEditor(CDialogBase, Ui_RLSExtendedVectorEditor):
    def __init__(self, parent):
        super(CRLSExtendedVectorEditor, self).__init__(parent)
        self.addModels('Items', CRLSExtendedVectorModel(self))

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle(u'Список препаратов')

        self.setModels(self.tblItems, self.modelItems, self.selectionModelItems)
        self.tblItems.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblItems.doubleClicked.connect(self.editItem)
        self.tblItems.addPopupDelRow()

        self.loadPreferences(getPref(QtGui.qApp.preferences.windowPrefs, 'CRLSExtendedVectorEditor', {}))

    def closeEvent(self, event):
        prefs = self.savePreferences()
        setPref(QtGui.qApp.preferences.windowPrefs, 'CRLSExtendedVectorEditor', prefs)
        super(CRLSExtendedVectorEditor, self).closeEvent(event)

    def savePreferences(self):
        prefs = super(CRLSExtendedVectorEditor, self).savePreferences()
        setPref(prefs, 'tblItems', self.tblItems.savePreferences())
        return prefs

    def loadPreferences(self, preferences):
        super(CRLSExtendedVectorEditor, self).loadPreferences(preferences)
        self.tblItems.loadPreferences(getPref(preferences, 'tblItems', {}))

    def editItem(self, index):
        item = self.tblItems.currentItem()
        editor = CRLSExtendedEditor(self)
        editor.setValue(item)
        if editor.exec_():
            item = editor.value()
            row = index.row()
            model = self.tblItems.model()
            if row < model.itemCount():
                model.setItem(row, item)
            else:
                model.addItem(item)

    def value(self):
        return self.tblItems.model().items()

    def setValue(self, value):
        self.tblItems.model().setItems(value)
