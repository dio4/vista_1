# -*- coding: utf-8 -*-
import re
from PyQt4 import QtCore, QtGui, QtSql

from Banks import CBanksList
from RefBooks.Tables import rbNet, rbOKFS, rbOKPF
from Ui_OrgEditor import Ui_OrgEditorDialog
from Ui_OrgFilterDialog import Ui_OrgFilterDialog
from Utils import getShortBankName, fixOKVED, parseOKVEDList
from library.DialogBase import CDialogBase
from library.InDocTable import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel import CTextCol
from library.Utils import forceRef, forceString, forceStringEx, toVariant, addDotsEx, getPrefBool, setPref
from library.interchange import getCheckBoxValue, getComboBoxValue, getLineEditValue, getRBComboBoxValue, \
    getTextEditValue, setCheckBoxValue, setComboBoxValue, setLineEditValue, \
    setRBComboBoxValue, setTextEditValue


def selectOrganisation(parent, orgId, showListFirst, filter=None):
    if showListFirst:
        dialog = COrgsList(parent)
        dialog.filter = filter
        dialog.setItemId(orgId)
        if dialog.exec_():
            return dialog.currentItemId()
    else:
        filterDialog = COrgFilterDialog(parent)
        if filterDialog.exec_():
            dialog = COrgsList(parent, True)
            dialog.filter = filter
            dialog.props = filterDialog.props()
            dialog.renewListAndSetTo(orgId)
            if dialog.model.rowCount() == 1:
                return dialog.currentItemId()
            else:
                if dialog.exec_():
                    return dialog.currentItemId()
    return None


class COrgsList(CItemsListDialog):
    def __init__(self, parent, forSelect=False):
        CItemsListDialog.__init__(
            self,
            parent,
            [
                CTextCol(u'Краткое наименование', ['shortName'], 30),
                CTextCol(u'ИНН', ['INN'], 12),
                CTextCol(u'ОГРН', ['OGRN'], 10),
                CTextCol(u'Код ИНФИС', ['infisCode'], 10),
                CTextCol(u'Код МИАЦ', ['miacCode'], 10),
                CTextCol(u'Полное наименование', ['fullName'], 30),
            ],
            'Organisation',
            ['shortName', 'INN', 'OGRN', 'miacCode'],
            forSelect=forSelect,
            filterClass=COrgFilterDialog
        )
        self.setWindowTitleEx(u'Организации')
        self.filter = None

    def getItemEditor(self):
        return COrgEditor(self)

    def select(self, props):
        table = self.model.table()
        cond = []
        name = props.get('name', '')
        if name:
            nameFilter = []
            dotedName = addDotsEx(name)
            nameFilter.append(table['shortName'].like(dotedName))
            nameFilter.append(table['fullName'].like(dotedName))
            nameFilter.append(table['title'].like(dotedName))
            cond.append(QtGui.qApp.db.joinOr(nameFilter))

        inn = props.get('INN', '')
        if inn:
            cond.append(table['INN'].eq(inn))
        ogrn = props.get('OGRN', '')
        if ogrn:
            cond.append(table['OGRN'].eq(ogrn))
        infis = props.get('infis', '')
        if infis:
            cond.append(table['infisCode'].eq(infis))

        miac = props.get('miacCode', '')
        if miac:
            cond.append(table['miacCode'].eq(miac))

        okved = props.get('OKVED', '')
        if okved:
            cond.append(table['OKVED'].like(okved))
        isInsurer = props.get('isInsurer', 0)
        if isInsurer:
            cond.append(table['isInsurer'].eq(isInsurer - 1))
        localsOnly = props.get('localsOnly', False)
        if localsOnly:
            region = QtGui.qApp.provinceKLADR()[:2]
            if region not in ('78', '77', '92'):
                region = QtGui.qApp.defaultKLADR()[:2]
            if region:
                cond.append(QtGui.qApp.db.left(table['area'], 2).eq(region))
        activeOnly = props.get('activeOnly', True)
        if activeOnly:
            cond.append(table['DATO'].ge(QtCore.QDate.currentDate()))
            cond.append(table['DATN'].le(QtCore.QDate.currentDate()))
        cond.append(table['deleted'].eq(0))
        if self.filter:
            cond.append(self.filter)

        return QtGui.qApp.db.getIdList(table.name(), 'id', cond, self.order)

    def updateOrgsList(self, itemId):
        self.filter = None
        self.props = {}
        idList = self.select(self.props)
        self.model.setIdList(idList, itemId)
        if idList:
            self.tblItems.selectRow(0)
        self.setCurrentItemId(itemId)
        self.label.setText(u'всего: %d' % len(idList))
        self.btnSelect.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        name = self.props.get('name', '')
        if name:
            words = forceStringEx(name).split(u'...')
            if len(words) == 1 and (u'...' not in words[0].lower()):
                name = words[0]
                dialog.edtFullName.setText(name)
                dialog.edtShortName.setText(name)
                dialog.edtTitle.setText(name)
        if dialog.exec_():
            itemId = dialog.itemId()
            self.updateOrgsList(itemId)

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                self.updateOrgsList(itemId)
        else:
            self.on_btnNew_clicked()


class COrgFilterDialog(CDialogBase, Ui_OrgFilterDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtName.setFocus(QtCore.Qt.ShortcutFocusReason)

    def loadPreferences(self, preferences):
        self.chkLocalsOnly.setChecked(getPrefBool(preferences, 'localsOnly', True))
        self.chkActiveOnly.setChecked(getPrefBool(preferences, 'activeOnly', True))

    def savePreferences(self):
        preferences = CDialogBase.savePreferences(self)
        setPref(preferences, 'localsOnly', toVariant(self.chkLocalsOnly.isChecked()))
        setPref(preferences, 'activeOnly', toVariant(self.chkActiveOnly.isChecked()))

        return preferences

    def setProps(self, props):
        self.edtName.setText(props.get('name', ''))
        self.edtINN.setText(props.get('INN', ''))
        self.edtOGRN.setText(props.get('OGRN', ''))
        self.edtInfis.setText(props.get('infis', ''))
        self.edtOKVED.setText(props.get('OKVED', ''))
        self.edtmiacCode.setText(props.get('miacCode', ''))

        self.cmbIsInsurer.setCurrentIndex(props.get('isInsurer', 0))
        self.chkLocalsOnly.setChecked(props.get('localsOnly', False))
        self.chkActiveOnly.setChecked(props.get('activeOnly', True))

    def props(self):
        result = {}
        result['name'] = forceStringEx(self.edtName.text())
        result['INN'] = forceStringEx(self.edtINN.text())
        result['OGRN'] = forceStringEx(self.edtOGRN.text())
        result['infis'] = forceStringEx(self.edtInfis.text())
        result['OKVED'] = forceStringEx(self.edtOKVED.text())
        result['miacCode'] = forceStringEx(self.edtmiacCode.text())
        result['isInsurer'] = self.cmbIsInsurer.currentIndex()
        result['localsOnly'] = self.chkLocalsOnly.isChecked()
        result['activeOnly'] = self.chkActiveOnly.isChecked()
        return result


class COrgEditor(CItemEditorBaseDialog, Ui_OrgEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Organisation')
        self.addModels('OrganisationAccounts', COrganisationAccountsModel(self))
        self.addModels('OrganisationPolicySerials', COrganisationPolicySerialsModel(self))

        self.setupUi(self)
        self.tblOrganisationAccounts.addPopupDelRow()
        self.tabWidget.setTabEnabled(2, False)
        self.setWindowTitleEx(u'Организация')

        self.setModels(self.tblOrganisationAccounts, self.modelOrganisationAccounts,
                       self.selectionModelOrganisationAccounts)
        self.setModels(self.tblOrganisationPolicySerials, self.modelOrganisationPolicySerials,
                       self.selectionModelOrganisationPolicySerials)
        self.tblOrganisationPolicySerials.addPopupDelRow()

        self.cmbNet.setTable(rbNet, True)
        self.cmbOKPF.setTable(rbOKPF, True)
        self.cmbOKFS.setTable(rbOKFS, True)
        self.cmbArea.setAreaSelectable(True)
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtFullName, record, 'fullName')
        setLineEditValue(self.edtShortName, record, 'shortName')
        setLineEditValue(self.edtTitle, record, 'title')
        setLineEditValue(self.edtAddress, record, 'address')
        setRBComboBoxValue(self.cmbNet, record, 'net_id')
        setLineEditValue(self.edtInfisCode, record, 'infisCode')
        setLineEditValue(self.edtObsoleteInfisCode, record, 'obsoleteInfisCode')
        setLineEditValue(self.edtMiacCode, record, 'miacCode')
        setLineEditValue(self.edtOKVED, record, 'OKVED')
        setLineEditValue(self.edtINN, record, 'INN')
        setLineEditValue(self.edtKPP, record, 'KPP')
        setLineEditValue(self.edtOGRN, record, 'OGRN')
        setLineEditValue(self.edtFSS, record, 'FSS')
        setLineEditValue(self.edtOKATO, record, 'OKATO')
        setLineEditValue(self.edtOKPO, record, 'OKPO')
        setLineEditValue(self.edtNetricaCode, record, 'netrica_Code')
        setRBComboBoxValue(self.cmbOKPF, record, 'OKPF_id')
        setRBComboBoxValue(self.cmbOKFS, record, 'OKFS_id')
        setLineEditValue(self.edtChief, record, 'chief')
        setLineEditValue(self.edtPhone, record, 'phone')
        setLineEditValue(self.edtAccountant, record, 'accountant')
        setCheckBoxValue(self.chkIsInsurer, record, 'isInsurer')
        setCheckBoxValue(self.chkIsCompulsoryInsurer, record, 'isCompulsoryInsurer')
        setCheckBoxValue(self.chkIsVoluntaryInsurer, record, 'isVoluntaryInsurer')
        setCheckBoxValue(self.chkCompulsoryServiceStop, record, 'compulsoryServiceStop')
        setCheckBoxValue(self.chkVoluntaryServiceStop, record, 'voluntaryServiceStop')
        setCheckBoxValue(self.chkCanOmitPolicyNumber, record, 'canOmitPolicyNumber')
        self.cmbArea.setCode(forceString(record.value('area')))
        setComboBoxValue(self.cmbIsMedical, record, 'isMedical')
        setTextEditValue(self.edtNotes, record, 'notes')
        setRBComboBoxValue(self.cmbHead, record, 'head_id')
        self.modelOrganisationAccounts.loadItems(self.itemId())
        self.modelOrganisationPolicySerials.loadItems(self.itemId())

    def getRecord(self):
        obsoleteInfisCode = forceString(self.edtObsoleteInfisCode.text())
        obsoleteInfisCode = forceStringEx(obsoleteInfisCode.replace(',', ' ')).replace(' ', ',')

        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtFullName, record, 'fullName')
        getLineEditValue(self.edtShortName, record, 'shortName')
        getLineEditValue(self.edtTitle, record, 'title')
        getLineEditValue(self.edtAddress, record, 'address')
        getRBComboBoxValue(self.cmbNet, record, 'net_id')
        getLineEditValue(self.edtInfisCode, record, 'infisCode')
        record.setValue('obsoleteInfisCode', toVariant(obsoleteInfisCode))
        getLineEditValue(self.edtMiacCode, record, 'miacCode')
        getLineEditValue(self.edtOKVED, record, 'OKVED')
        getLineEditValue(self.edtINN, record, 'INN')
        getLineEditValue(self.edtKPP, record, 'KPP')
        getLineEditValue(self.edtOGRN, record, 'OGRN')
        getLineEditValue(self.edtFSS, record, 'FSS')
        getLineEditValue(self.edtOKATO, record, 'OKATO')
        getLineEditValue(self.edtOKPO, record, 'OKPO')
        getLineEditValue(self.edtNetricaCode, record, 'netrica_Code')
        getRBComboBoxValue(self.cmbOKPF, record, 'OKPF_id')
        getRBComboBoxValue(self.cmbOKFS, record, 'OKFS_id')
        getLineEditValue(self.edtChief, record, 'chief')
        getLineEditValue(self.edtPhone, record, 'phone')
        getLineEditValue(self.edtAccountant, record, 'accountant')
        getCheckBoxValue(self.chkIsInsurer, record, 'isInsurer')
        getCheckBoxValue(self.chkIsCompulsoryInsurer, record, 'isCompulsoryInsurer')
        getCheckBoxValue(self.chkIsVoluntaryInsurer, record, 'isVoluntaryInsurer')
        area = self.cmbArea.code()
        record.setValue('area', toVariant(area))
        getCheckBoxValue(self.chkCompulsoryServiceStop, record, 'compulsoryServiceStop')
        getCheckBoxValue(self.chkVoluntaryServiceStop, record, 'voluntaryServiceStop')
        getCheckBoxValue(self.chkCanOmitPolicyNumber, record, 'canOmitPolicyNumber')
        getComboBoxValue(self.cmbIsMedical, record, 'isMedical')
        getTextEditValue(self.edtNotes, record, 'notes')
        getRBComboBoxValue(self.cmbHead, record, 'head_id')
        return record

    def saveInternals(self, id):
        self.modelOrganisationAccounts.saveItems(id)
        self.modelOrganisationPolicySerials.saveItems(id)

    def checkDataEntered(self):
        result = True
        message = u'Необходимо указать '
        if not forceStringEx(self.edtFullName.text()):
            res = self.checkValueMessageIgnoreAll(message + u'полное наименование', False, self.edtFullName)
            if res == 0:
                return False
            elif res == 2:
                return True
        if not forceStringEx(self.edtShortName.text()):
            res = self.checkValueMessageIgnoreAll(message + u'краткое наименование', False, self.edtShortName)
            if res == 0:
                return False
            elif res == 2:
                return True
        if not forceStringEx(self.edtOGRN.text()):
            res = self.checkValueMessageIgnoreAll(message + u'ОГРН', True, self.edtOGRN)
            if res == 0:
                return False
            elif res == 2:
                return True
        headOrgId = self.cmbHead.value()
        if not headOrgId:
            INN = forceStringEx(self.edtINN.text())
            if not INN:
                res = self.checkValueMessageIgnoreAll(message + u'ИНН', True, self.edtINN)
                if res == 0:
                    return False
                elif res == 2:
                    return True
            if INN and not self.checkINN(INN):
                res = self.checkValueMessageIgnoreAll(message + u'правильный ИНН', True, self.edtINN)
                if res == 0:
                    return False
                elif res == 2:
                    return True
            if not forceStringEx(self.edtKPP.text()):
                res = self.checkValueMessageIgnoreAll(message + u'КПП', True, self.edtKPP)
                if res == 0:
                    return False
                elif res == 2:
                    return True
            if not self.cmbOKPF.value():
                res = self.checkValueMessageIgnoreAll(message + u'ОКПФ', True, self.cmbOKPF)
                if res == 0:
                    return False
                elif res == 2:
                    return True
            if not self.cmbOKFS.value():
                res = self.checkValueMessageIgnoreAll(message + u'ОКФС', True, self.cmbOKFS)
                if res == 0:
                    return False
                elif res == 2:
                    return True
        if not forceStringEx(self.edtOKVED.text()):
            res = self.checkValueMessageIgnoreAll(message + u'ОКВЭД', True, self.edtOKVED)
            if res == 0:
                return False
            elif res == 2:
                return True
        result = result and self.checkOKVED()
        if result:
            for row, record in enumerate(self.modelOrganisationAccounts.items()):
                if not self.checkAccountDataEntered(row, record):
                    return False
        result = result and self.checkDup()
        return result

    def checkINN(self, INN):
        def checksum(n, s):
            result = sum(d * int(c) for (d, c) in zip(n, s)) % 11
            if result == 10:
                result = 0
            return result

        n121 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
        n122 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
        n10 = (2, 4, 10, 3, 5, 9, 4, 6, 8)

        if len(INN) == 10:
            return str(checksum(n10, INN[0:9])) == INN[9]
        elif len(INN) == 12:
            return str(checksum(n121, INN[0:11])) + str(checksum(n122, INN[0:11])) == INN[10:12]
        else:
            return False

    def checkOKVED(self):
        fixedCodes = []
        str = forceString(self.edtOKVED.text())
        list = parseOKVEDList(str)
        for code in list:
            success, fixedCode = fixOKVED(code)
            fixedCodes.append(fixedCode)
        self.edtOKVED.setText(u','.join(fixedCodes))
        return True

    def checkAccountDataEntered(self, row, record):
        result = True
        column = record.indexOf('name')
        name = forceString(record.value(column))
        if result and not re.match(r'^\d{20}$', name):
            result = self.checkValueMessage(
                u'Номер расчетного счета должен состоять из 20 цифр', True, self.tblOrganisationAccounts, row, column
            )

        column = record.indexOf('bank_id')
        bankId = forceRef(record.value(column))
        if result and not bankId:
            result = self.checkValueMessage(
                u'Необходимо указать банк', False, self.tblOrganisationAccounts, row, column
            )
        return result

    def checkDup(self):
        dupCheckList = (
            (self.findDupByInfisCode, u'по коду ИНФИС'),
            (self.findDupByINN, u'по ИНН'),
            (self.findDupByOGRN, u'по ОГРН'),
        )
        for method, title in dupCheckList:
            idlist = method()
            if idlist:
                res = QtGui.QMessageBox.question(
                    self,
                    u'Внимание!',
                    u'Обнаружен "двойник" %s\nИгнорировать?' % title,
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No
                )
                if res == QtGui.QMessageBox.No:
                    return False
        return True

    def findDup(self, cond):
        db = QtGui.qApp.db
        table = db.table('Organisation')
        id = self.itemId()
        if id:
            cond.append(table['id'].ne(id))
        return db.getIdList(table, where=cond, order='id')

    def findDupByInfisCode(self):
        infisCode = forceStringEx(self.edtInfisCode.text())
        if infisCode:
            db = QtGui.qApp.db
            table = db.table('Organisation')
            cond = [table['infisCode'].eq(infisCode)]
            return self.findDup(cond)
        else:
            return None

    def findDupByINN(self):
        INN = forceStringEx(self.edtINN.text())
        if not self.cmbHead.value() and INN:
            db = QtGui.qApp.db
            table = db.table('Organisation')
            cond = [table['INN'].eq(INN)]
            return self.findDup(cond)
        else:
            return None

    def findDupByOGRN(self):
        OGRN = forceStringEx(self.edtOGRN.text())
        if not self.cmbHead.value() and OGRN:
            db = QtGui.qApp.db
            table = db.table('Organisation')
            cond = [table['OGRN'].eq(OGRN)]
            return self.findDup(cond)
        else:
            return None

    def updateInfoByHead(self, orgId):
        if orgId or self.cmbHead.value():
            db = QtGui.qApp.db
            record = db.getRecord(db.table('Organisation'), '*', orgId)
            if not record:
                record = QtSql.QSqlRecord()
            setLineEditValue(self.edtINN, record, 'INN')
            setLineEditValue(self.edtKPP, record, 'KPP')
            setLineEditValue(self.edtOGRN, record, 'OGRN')
            setLineEditValue(self.edtFSS, record, 'FSS')
            setLineEditValue(self.edtOKATO, record, 'OKATO')
            setLineEditValue(self.edtOKPO, record, 'OKPO')
            setRBComboBoxValue(self.cmbOKPF, record, 'OKPF_id')
            setRBComboBoxValue(self.cmbOKFS, record, 'OKFS_id')

        headIsEmpty = not orgId
        self.edtINN.setEnabled(headIsEmpty)
        self.edtKPP.setEnabled(headIsEmpty)
        self.edtOGRN.setEnabled(headIsEmpty)
        self.edtFSS.setEnabled(headIsEmpty)
        self.edtOKATO.setEnabled(headIsEmpty)
        self.edtOKPO.setEnabled(headIsEmpty)
        self.cmbOKPF.setEnabled(headIsEmpty)
        self.cmbOKFS.setEnabled(headIsEmpty)

    @QtCore.pyqtSlot()
    def on_btnSelectHeadOrganisation_clicked(self):
        headOrgId = selectOrganisation(self, self.cmbHead.value(), False)
        self.cmbHead.update()
        if headOrgId:
            self.cmbHead.setValue(headOrgId)

    @QtCore.pyqtSlot(int)
    def on_cmbHead_currentIndexChanged(self):
        headOrgId = self.cmbHead.value()
        self.updateInfoByHead(headOrgId)

    @QtCore.pyqtSlot(bool)
    def on_chkIsInsurer_toggled(self, checked):
        self.tabWidget.setTabEnabled(2, checked)
        self.chkIsCompulsoryInsurer.setEnabled(checked)
        self.chkIsVoluntaryInsurer.setEnabled(checked)


class COrganisationAccountsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Organisation_Account', 'id', 'organisation_id', parent)
        self.addCol(CInDocTableCol(u'Расчетный счет', 'name', 22, maxLength=20, inputMask='9' * 20))
        self.addCol(CBankInDocTableCol(u'Банк', 'bank_id', 22))
        self.addCol(CInDocTableCol(u'Наименование в банке', 'bankName', 22))
        self.addCol(CInDocTableCol(u'Примечания', 'notes', 22))
        self.addCol(CBoolInDocTableCol(u'Нал', 'cash', 4))


class CBankInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width):
        CInDocTableCol.__init__(self, title, fieldName, width)

    def toString(self, value, record):
        bankId = forceRef(value)
        return QtCore.QVariant(getShortBankName(bankId))

    def createEditor(self, parent):
        editor = CBankSelectButton(parent)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setBankId(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.bankId)


class CBankSelectButton(QtGui.QPushButton):
    def __init__(self, parent):
        QtGui.QPushButton.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.bankId = None
        self.connect(self, QtCore.SIGNAL('pressed()'), self.selectBank)

    def setBankId(self, bankId):
        if bankId != self.bankId:
            self.bankId = bankId
            self.setText(getShortBankName(self.bankId))

    def selectBank(self):
        dlg = CBanksList(self, True)
        dlg.setCurrentItemId(self.bankId)
        if dlg.selectItem():
            self.setBankId(dlg.currentItemId())


class COrganisationPolicySerialsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Organisation_PolicySerial', 'id', 'organisation_id', parent)
        self.addCol(CRBInDocTableCol(u'Тип', 'policyType_id', 30, 'rbPolicyType'))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 16, maxLength=8))
