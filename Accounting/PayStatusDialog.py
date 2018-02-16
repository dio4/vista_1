# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.interchange import *
from library.DialogBase import CDialogBase
from library.crbcombobox import CRBComboBox

from Ui_PayStatusDialog import Ui_PayStatusDialog


class CPayStatusDialog(CDialogBase, Ui_PayStatusDialog):
    def __init__(self,  parent, financeId):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
#        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
#        self.setWindowTitleEx(u'Счет')
        self.cmbRefuseType.setTable('rbPayRefuseType', addNone=False, filter='finance_id=\'%s\'' % financeId)
        self.cmbRefuseType.setShowFields(CRBComboBox.showCodeAndName)
        self.setupDirtyCather()


    def setAccountItemsCount(self, count):
        self.setWindowTitle(u'Подтверждение оплаты по %s реестра'% formatNum1(count, (u'записи', u'записям', u'записям')))


    def setParams(self,  params):
        self.edtDate.setDate(params.get('date', QDate()))
        self.edtNumber.setText(params.get('number', ''))
        if params.get('accepted', True):
            self.rbnAccepted.setChecked(True)
        else:
            self.rbnRefused.setChecked(True)

        refuseTypeId = params.get('refuseTypeId', None) or self.cmbRefuseType.model().getIdByFlatCode('default')
        self.cmbRefuseType.setValue(refuseTypeId)
        self.edtNote.setText(params.get('note', ''))
        self.setIsDirty(False)


    def params(self):
        accepted = self.rbnAccepted.isChecked()
        result = {'date': self.edtDate.date(),
                  'number': forceString(self.edtNumber.text()),
                  'accepted': accepted,
                  'refuseTypeId': None if accepted else self.cmbRefuseType.value(),
                  'note': forceStringEx(self.edtNote.text())}
        return result

    #FIXME: atronah: не используется и не нужно, так как (цитирую Ириску) "для платных услуг не всегда указывается номер (подтверждение)"
    def checkDataEntered(self):
        result = True
        date = self.edtDate.date()
        number = forceStringEx(self.edtNumber.text())
        accepted = self.rbnAccepted.isChecked()
        refuseTypeId = self.cmbRefuseType.value()
        if not date.isNull() or number or (not accepted and refuseTypeId):
            result = result and (not date.isNull() or self.checkInputMessage(u'дату', False, self.edtDate))
            result = result and (number or self.checkInputMessage(u'номер', False, self.edtNumber))
            if not accepted:
                result = result and (refuseTypeId or self.checkInputMessage(u'причину отказа', False, self.cmbRefuseType))
        return result


    @QtCore.pyqtSlot(bool)
    def on_rbnAccepted_toggled(self, checked):
        self.cmbRefuseType.setEnabled( not self.rbnAccepted.isChecked() )