# -*- coding: utf-8 -*-
from PyQt4 import QtCore
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CTextCol
from library.Utils              import forceString, forceStringEx, toVariant, forceInt
from RefBooks.ServiceModifier   import createModifier, parseModifier, CServiceModifierCol
from RefBooks.Tables            import rbCode, rbName, rbVisitType
from Ui_RBVisitTypeEditor       import Ui_ItemEditorDialog


class CRBVisitTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',                     [rbCode], 10),
            CTextCol(u'Наименование',            [rbName], 30),
            CServiceModifierCol(u'Модификатор кода услуги', ['serviceModifier'],  30),
            ], rbVisitType, [rbCode, rbName])
        self.setWindowTitleEx(u'Типы визитов')

    def getItemEditor(self):
        return CRBVisitTypeEditor(self)


class CRBVisitTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbVisitType)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Тип визита')
        self.setupDirtyCather()

        self.chkNoModifyService.stateChanged.connect(self.on_chkNoModifyService_changed)
        self.chkReplaceService.stateChanged.connect(self.on_chkReplaceService_changed)
        self.chkModifyHeadService.stateChanged.connect(self.on_chkModifyHeadService_changed)
        self.chkModifyTailService.stateChanged.connect(self.on_chkModifyTailService_changed)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        modifiers = parseModifier(forceStringEx(record.value('serviceModifier')))
        for action, text, n in modifiers:
            if action == 0:
                self.chkNoModifyService.setChecked(True)
            elif action == 1:
                self.chkReplaceService.setChecked(True)
                self.edtReplaceService.setText(text)
            elif action == 2:
                self.chkModifyHeadService.setChecked(True)
                self.edtModifyHeadService.setText(text)
                self.edtModifyHeadService_N.setText(unicode(n))
            elif action == 3:
                self.chkModifyTailService.setChecked(True)
                self.edtModifyTailService.setText(text)
                self.edtModifyTailService_N.setText(unicode(n))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        modifier = u''

        if self.chkReplaceService.isChecked():
            action = 1
            text = forceStringEx(self.edtReplaceService.text())
            modifier = createModifier(action, text)

        # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyTailService
        if self.chkModifyHeadService.isChecked():
            action = 2
            text = forceStringEx(self.edtModifyHeadService.text())
            n = forceInt(self.edtModifyHeadService_N.text())
            modifier = createModifier(action, text, n)

        # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyHeadService
        if self.chkModifyTailService.isChecked():
            action = 3
            text = forceStringEx(self.edtModifyTailService.text())
            n = forceInt(self.edtModifyTailService_N.text())
            if modifier:
                modifier = modifier + u'/' + createModifier(action, text, n)
            else:
                modifier = createModifier(action, text, n)

        # Если было кликнуто ничего или chkNoModifyService, то modifier должен быть равен u''

        record.setValue('serviceModifier', toVariant(modifier))
        return record

    def on_chkNoModifyService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.chkReplaceService.setChecked(False)
            self.chkModifyHeadService.setChecked(False)
            self.chkModifyTailService.setChecked(False)

    def on_chkReplaceService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtReplaceService.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkModifyHeadService.setChecked(False)
            self.chkModifyTailService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtReplaceService.setEnabled(False)

    # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyTailService
    def on_chkModifyHeadService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtModifyHeadService.setEnabled(True)
            self.edtModifyHeadService_N.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkReplaceService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtModifyHeadService.setEnabled(False)
            self.edtModifyHeadService_N.setEnabled(False)

    # Этот модификатор может выставляться/сохраняться/применяться вместе с ModifyHeadService
    def on_chkModifyTailService_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.edtModifyTailService.setEnabled(True)
            self.edtModifyTailService_N.setEnabled(True)

            self.chkNoModifyService.setChecked(False)
            self.chkReplaceService.setChecked(False)

        if state == QtCore.Qt.Unchecked:
            self.edtModifyTailService.setEnabled(False)
            self.edtModifyTailService_N.setEnabled(False)