# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CColorCol, CTextCol
from library.TableView          import CTableView
from library.Utils              import forceString, forceStringEx, toVariant
from library.DialogBase         import CConstructHelperMixin
from RefBooks.Tables            import rbCode, rbName
from Registry.RegistryTable     import CClientsTableModel

from Ui_RBLocationCardEditor    import Ui_ItemEditorDialog


class CRBLocationCardTypeList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CColorCol(u'Цветовая маркировка', ['color'], 10, 'r')
            ], 'rbLocationCardType', [rbCode, rbName])
        self.btnDelete = QtGui.QPushButton(u'Удаление', self)
        self.btnDelete.setObjectName('btnDelete')
        self.btnDelete.setEnabled(not self.forSelect)
        self.buttonBox.addButton(self.btnDelete, QtGui.QDialogButtonBox.DestructiveRole)
        self.setWindowTitleEx(u'Место нахождения амбулаторной карты')

        self.btnDelete.clicked.connect(self.on_btnDelete_clicked)

    def getItemEditor(self):
        return CRBLocationCardTypeEditor(self)

    @QtCore.pyqtSlot()
    def on_btnDelete_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = CRBLocationCardTypeDeleteDialog(self)
            if dialog.exec_():
                self.renewListAndSetTo()


class CRBLocationCardTypeEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbLocationCardType')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Место нахождения амбулаторной карты')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbColor.setColor(forceString(record.value('color')))


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,       toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,       toVariant(forceStringEx(self.edtName.text())))
        record.setValue('color',      QtCore.QVariant(self.cmbColor.colorName()))
        return record

class CRBLocationCardTypeDeleteDialog(QtGui.QDialog, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.itemId = parent.currentItemId()
        self.db = QtGui.qApp.db
        self.tableClientsCard = self.db.table('Client_LocationCard')
        self.table = self.db.table('rbLocationCardType')
        self.clientIdList = self.db.getIdList(self.tableClientsCard, 'master_id',
                                         [self.tableClientsCard['locationCardType_id'].eq(self.itemId),
                                          self.tableClientsCard['deleted'].eq(0)])
        self.setWindowTitle(u'Место нахождения амбулаторной карты')
        self.lblDeleteLocationCardType = QtGui.QLabel(self)
        self.lblDeleteLocationCardType.setObjectName('lblDeleteLocationCardType')
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setObjectName('buttonBox')
        self.vLayout = QtGui.QVBoxLayout()
        self.vLayout.setObjectName('vLayout')
        self.vLayout.addWidget(self.lblDeleteLocationCardType)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        if len(self.clientIdList) == 0:
            self.lblDeleteLocationCardType.setText(u"Вы действительно желаете удалить "
                                                   u"это место нахождения амбулаторной карты?")
        else:
            self.lblDeleteLocationCardType.setText(u"Вы действительно желаете удалить это место нахождения амбулаторной карты? "
                                                   u"К нему прикреплены карты следующих пациентов:")
            self.addModels('Clients', CClientsTableModel(self))
            self.tblClients = CTableView(self)
            self.tblClients.setObjectName('tblClients')
            self.vLayout.addWidget(self.tblClients)
            self.vLayout.addWidget(self.buttonBox)
            self.setModels(self.tblClients, self.modelClients)
            self.modelClients.setIdList(self.clientIdList)

        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.deleteMarked)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)

    def deleteMarked(self):
        self.db.deleteRecord(self.tableClientsCard, [self.tableClientsCard['locationCardType_id'].eq(self.itemId)])
        self.db.deleteRecord(self.table, [self.table['id'].eq(self.itemId)])
        QtGui.QDialog.accept(self)

