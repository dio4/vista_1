# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.interchange        import getDateEditValue, getLineEditValue, getRBComboBoxValue, setDateEditValue, \
                                       setLineEditValue, setRBComboBoxValue, setComboBoxValue, getComboBoxValue
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CDateCol, CDesignationCol, CRefBookCol, CTextCol
from library.Utils              import forceString, toVariant

from RefBooks.Tables            import rbCode, rbAssignedContracts, rbOKPF

from Ui_RBAssignedContractsEditor import Ui_ItemEditorDialog


# TODO: Возможно стоит переименовать из Assigned Contracts во что-нибудь иное, если итоговое предназначение окажется иным
types = {'paidServices': 1,
                'clinicalTrials': 2}
class CRBAssignedContractsList(CItemsListDialog):
    """ Базовый класс для справочников различных типов именных договоров.
        На данный момент предполагается, что справочники будут храниться в одной
        таблице и различаться только полем Type. (При существенном увеличении
        количества типов стоит создать отдельную табличку с именами типов и
        возможно переделать все в CItemsSplitListDialog)
        При добавлении новых справочников и сохранении разделения на отдельные
        диалоги наследование производится путем переопределения метода select
        родительского класса с указанием в запросе getIdList фильтра по соответствующему типу.

        Типы индивидуальных договоров:
        1 - Платные услуги
        2 - Клинические испытания
    """
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 20),
            CRefBookCol(u'Организационная форма', ['OKPF_id'], rbOKPF, 20),
            CDesignationCol(u'Организация',    ['org_id'],        ('Organisation', 'shortName'), 12),
            CTextCol(u'Номер договора', ['contractNumber'], 20),
            CDateCol(u'Дата заключения договора', ['contractDate'], 10),
            CDateCol(u'Дата окончания договора', ['contractEndDate'], 10),
            CTextCol(u'Сумма договора', ['contractSum'], 10)
            ], rbAssignedContracts, [rbCode])

    def preSetupUi(self):
        self.btnPrint =  QtGui.QPushButton(u'Печать F6', self)
        self.btnPrint.setObjectName('btnPrint')
        self.btnDelete = QtGui.QPushButton(u'Удалить', self)
        self.btnDelete.setObjectName('btnDelete')
        self.btnNew =  QtGui.QPushButton(u'Вставка F9', self)
        self.btnNew.setObjectName('btnNew')
        self.btnEdit =  QtGui.QPushButton(u'Правка F4', self)
        self.btnEdit.setObjectName('btnEdit')
        self.btnFilter =  QtGui.QPushButton(u'Фильтр', self)
        self.btnFilter.setObjectName('btnFilter')
        self.btnSelect =  QtGui.QPushButton(u'Выбор', self)
        self.btnSelect.setObjectName('btnSelect')

    def postSetupUi(self):
        self.buttonBox.addButton(self.btnSelect, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnFilter, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEdit, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnNew, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnDelete, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.ActionRole)

    def getItemEditor(self):
        return CRBAssignedContractsEditor(self)

    def select(self, props):
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, table['type'].eq(self.cond), self.order)

    @QtCore.pyqtSlot()
    def on_btnDelete_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            table = QtGui.qApp.db.table(self.model.table().name())
            QtGui.qApp.db.deleteRecord(table, table['id'].eq(itemId))
            self.renewListAndSetTo()


class CRBPaidServicesList(CRBAssignedContractsList):
    def __init__(self, parent):
        CRBAssignedContractsList.__init__(self, parent)
        self.setWindowTitleEx(u'Безналичные договоры')
        self.cond = types['paidServices']

    def getItemEditor(self):
        return CRBPaidServicesEditor(self)


class CRBClinicalTrialsList(CRBAssignedContractsList):
    def __init__(self, parent):
        CRBAssignedContractsList.__init__(self, parent)
        self.setWindowTitleEx(u'Клинические исследования')
        self.cond = types['clinicalTrials']

    def getItemEditor(self):
        return CRBClinicalTrialsEditor(self)

#
# ##########################################################################
#

class CRBAssignedContractsEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent, type):
        CItemEditorBaseDialog.__init__(self, parent, rbAssignedContracts)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.cmbOKPF.setTable(rbOKPF, True)
        db = QtGui.qApp.db
        codesAll = db.getRecordList(db.table(rbAssignedContracts), rbCode,  db.table(rbAssignedContracts)[u'type'].eq(type))
        self.codes = {}
        for code in codesAll:
            pType, codePart, cnt = forceString(code.value(0)).split('.')
            if (pType, codePart) in self.codes.keys() :
                if int(cnt)>int(self.codes[(pType, codePart)]):
                    self.codes[(pType, codePart)] = int(cnt)
            else:
                self.codes[(pType, codePart)] = int(cnt)
        self.type = type
        self.setupDirtyCather()
        if QtGui.qApp.checkGlobalPreference('68', u'нет') and self.type == 1:
            self.lblProtocolNumber.setVisible(False)
            self.edtProtocolNum.setVisible(False)
            self.lblProtocolPhase.setVisible(False)
            self.edtProtocolPhase.setVisible(False)
            self.lblProtocolName.setVisible(False)
            self.edtProtocolName.setVisible(False)
            self.lblRecPatients.setVisible(False)
            self.cmbRecPatients.setVisible(False)
        elif QtGui.qApp.checkGlobalPreference('68', u'нет') and self.type == 2:
            self.lblAddress.setVisible(False)
            self.edtAddress.setVisible(False)
            self.lblContractItem.setVisible(False)
            self.edtContractItem.setVisible(False)
        elif QtGui.qApp.checkGlobalPreference('68', u'да'):
            self.lblContragent.setVisible(False)
            self.edtContragent.setVisible(False)
            self.lblProtocolNumber.setVisible(False)
            self.edtProtocolNum.setVisible(False)
            self.lblProtocolPhase.setVisible(False)
            self.edtProtocolPhase.setVisible(False)
            self.lblProtocolName.setVisible(False)
            self.edtProtocolName.setVisible(False)
            self.lblRecPatients.setVisible(False)
            self.cmbRecPatients.setVisible(False)
            self.lblAddress.setVisible(False)
            self.edtAddress.setVisible(False)
            self.lblContractItem.setVisible(False)
            self.edtContractItem.setVisible(False)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        pType, codePart, cnt = forceString(record.value('code')).split('.')
        self.cmbPaymentType.setCurrentIndex(int(pType) - 1)
        self.cmbCodePart.setCurrentIndex(int(codePart) - 1)
        setRBComboBoxValue(self.cmbOKPF, record, 'OKPF_id')
        setRBComboBoxValue(self.cmbOrgId, record, 'org_id')
        setLineEditValue(self.edtContractNumber, record, 'contractNumber')
        setDateEditValue(self.edtDate, record, 'contractDate')
        setDateEditValue(self.edtEndDate, record, 'contractEndDate')
        self.edtEndDate.setMinimumDate(self.edtDate.date())
        setLineEditValue(self.edtContractSum, record, 'contractSum')
        if QtGui.qApp.checkGlobalPreference('68', u'нет') and self.type == 2:
            setLineEditValue(self.edtContragent, record, 'contragent')
            setLineEditValue(self.edtProtocolNum, record, 'protocolNumber')
            setLineEditValue(self.edtProtocolPhase, record, 'protocolPhase')
            setLineEditValue(self.edtProtocolName, record, 'protocolName')
            setComboBoxValue(self.cmbRecPatients, record, 'protocolRecruit')
        elif QtGui.qApp.checkGlobalPreference('68', u'нет') and self.type == 1:
            setLineEditValue(self.edtContragent, record, 'contragent')
            setLineEditValue(self.edtContractItem, record, 'contractItem')
            setLineEditValue(self.edtAddress, record, 'address')


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        pType = '%.2d' % (self.cmbPaymentType.currentIndex() + 1)
        codePart = '%.2d' % (self.cmbCodePart.currentIndex() + 1)

        if (pType, codePart) in self.codes.keys():
            code = '%s.%s.%.3d' % (pType, codePart, self.codes[(pType, codePart)])
        else:
            code = '%s.%s.%.3d' % (pType, codePart, 1)

        record.setValue(rbCode, toVariant(code))
        record.setValue('type', toVariant(self.type))
        getRBComboBoxValue(self.cmbOKPF, record, 'OKPF_id')
        getRBComboBoxValue(self.cmbOrgId, record, 'org_id')
        getLineEditValue(self.edtContractNumber, record, 'contractNumber')
        getDateEditValue(self.edtDate, record, 'contractDate')
        getDateEditValue(self.edtEndDate, record, 'contractEndDate')
        getLineEditValue(self.edtContractSum, record, 'contractSum')
        if QtGui.qApp.checkGlobalPreference('68', u'нет') and type == 2:
            getLineEditValue(self.edtContragent, record, 'contragent')
            getLineEditValue(self.edtProtocolNum, record, 'protocolNumber')
            getLineEditValue(self.edtProtocolPhase, record, 'protocolPhase')
            getLineEditValue(self.edtProtocolName, record, 'protocolName')
            getComboBoxValue(self.cmbRecPatients, record, 'protocolRecruit')
        elif QtGui.qApp.checkGlobalPreference('68', u'нет') and type == 1:
            getLineEditValue(self.edtContragent, record, 'contragent')
            getLineEditValue(self.edtContractItem, record, 'contractItem')
            getLineEditValue(self.edtAddress, record, 'address')
        return record

    def checkDataEntered(self):
        if self.edtDate.text() == '':
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести дату заключения договора.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return False
        if QtGui.qApp.checkGlobalPreference('68', u'нет'):
            if self.type == 2:
                if self.edtContragent.text() == '':
                    QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести контрагента.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
                if self.edtProtocolNum.text() == '':
                    QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести номер протокола.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
                if self.edtProtocolPhase.text() == '':
                    QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести фазу протокола.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
                if self.edtProtocolName.text() == '':
                    QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести наименование протокола.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
            elif self.type == 1:
                if self.edtContragent.text() == '':
                    QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо ввести контрагента.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                    return False
        return True

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtDate_dateChanged(self, date):
        self.edtEndDate.setMinimumDate(date)

class CRBPaidServicesEditor(CRBAssignedContractsEditor):
    def __init__(self,  parent):
        CRBAssignedContractsEditor.__init__(self, parent, types['paidServices'])
        self.setWindowTitleEx(u'Безналичные договоры')
        self.lblCodePart.setText(u'Статус учреждения')
        self.lblCodePart.setToolTip(u'Статус учреждения, заключившего договор')
        self.cmbCodePart.setToolTip(u'Статус учреждения, заключившего договор')
        cmbItems = [u'Страховая компания', u'Медицинский центр', u'Другая организация']
        self.cmbCodePart.addItems(cmbItems)

class CRBClinicalTrialsEditor(CRBAssignedContractsEditor):
    def __init__(self,  parent):
        CRBAssignedContractsEditor.__init__(self, parent, types['clinicalTrials'])
        self.setWindowTitleEx(u'Безналичные договоры')
        self.lblCodePart.setText(u'Код подразделения')
        cmbItems = []
        for i in range (1, 31):
            cmbItems.append(u'%.2d'%i)
        self.cmbCodePart.addItems(cmbItems)
