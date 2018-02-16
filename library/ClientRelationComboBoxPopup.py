#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtGui import *

from Users.Rights       import *
from library.TableModel import *
from library.Utils      import *

from Ui_ClientRelationComboBoxPopup import Ui_ClientRelationComboBoxPopup


class CClientRelationComboBoxPopup(QtGui.QFrame, Ui_ClientRelationComboBoxPopup):
    __pyqtSignals__ = ('relatedClientIdSelected(int, QString)'
                      )

    def __init__(self, parent = None):
        QFrame.__init__(self, parent, Qt.Popup)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_WindowPropagation)
        self.tableModel = CClientRelationTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.edtBirthDate.setHighlightRedDate(False)
        self.tblClientRelation.setModel(self.tableModel)
        self.tblClientRelation.setSelectionModel(self.tableSelectionModel)
        self.buttonBox.button(QDialogButtonBox.Apply).setDefault(True)
        addControlsVisible = QtGui.qApp.addUnregisteredRelationsEnabled()
        self.btnCreateEntry.setVisible(addControlsVisible)
        self.edtWork.setVisible(addControlsVisible)
        self.lblWork.setVisible(addControlsVisible)
            
#       к сожалению в данном случае setDefault обеспечивает рамочку вокруг кнопочки
#       но enter не работает...
        self.buttonBox.button(QDialogButtonBox.Apply).setShortcut(Qt.Key_Return)
        self.date = None
        self.code = None
        self.clientId = None
        self.regAddressInfo = {}
        self.logAddressInfo = {}
        self.dialogInfo = {}
        self.tblClientRelation.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CClientRelationComboBoxPopup', {})
        # self.tblClientRelation.loadPreferences(preferences)
        self.edtBirthDate.setDate(QDate())
        self.cmbDocType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')


    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent!=None:
            opt=QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(Qt.WA_NoMouseReplay)
        QFrame.mousePressEvent(self, event)


    # def closeEvent(self, event):
    #     preferences = self.tblClientRelation.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CClientRelationComboBoxPopup', preferences)
    #     QFrame.closeEvent(self, event)


    def eventFilter(self, watched, event):
        if watched == self.tblClientRelation:
            if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Select]:
                event.accept()
                index = self.tblClientRelation.currentIndex()
                self.tblClientRelation.emit(SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QFrame.eventFilter(self, watched, event)


    @pyqtSlot()
    def on_btnFillingFilter_clicked(self):
        clientId = QtGui.qApp.currentClientId()
        if clientId != self.clientId:
            db = QtGui.qApp.db
            tableClient = db.table('Client')
            record = db.getRecordEx(tableClient, [tableClient['lastName'], tableClient['firstName'], tableClient['patrName'], tableClient['sex'], tableClient['birthDate']], [tableClient['deleted'].eq(0), tableClient['id'].eq(clientId)])
            if record:
                self.edtLastName.setText(forceString(record.value('lastName')))
                self.edtFirstName.setText(forceString(record.value('firstName')))
                self.edtPatrName.setText(forceString(record.value('patrName')))
                self.cmbSex.setCurrentIndex(forceInt(record.value('sex')))
                self.edtBirthDate.setDate(forceDate(record.value('birthDate')))


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QDialogButtonBox.Reset:
            self.on_buttonBox_reset()


    def on_buttonBox_reset(self):
        self.edtLastName.setText('')
        self.edtFirstName.setText('')
        self.edtPatrName.setText('')
        self.cmbSex.setCurrentIndex(0)
        self.edtBirthDate.setDate(QDate())
        self.cmbDocType.setValue(None)
        self.edtLeftSerial.setText('')
        self.edtRightSerial.setText('')
        self.edtNumber.setText('')
        self.edtComment.setText('')


    def on_buttonBox_apply(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            lastName = forceString(self.edtLastName.text())
            firstName = forceString(self.edtFirstName.text())
            patrName = forceString(self.edtPatrName.text())
            sex = forceInt(self.cmbSex.currentIndex())
            birthDate = forceDate(self.edtBirthDate.date())
            docTypeId = self.cmbDocType.value()
            leftSerial = forceString(self.edtLeftSerial.text())
            rightSerial = forceString(self.edtRightSerial.text())
            number = forceString(self.edtNumber.text())
            serial = u''
            if leftSerial:
                serial = leftSerial
            if rightSerial:
                if serial != u'':
                    serial += u' ' + rightSerial
                else:
                    serial += rightSerial
            crIdList = self.getClientRelationIdList(lastName, firstName, patrName, sex, birthDate, docTypeId, serial, number, self.code, self.clientId)
            self.setClientRelationIdList(crIdList, None)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        if not crIdList:
            res = QtGui.QMessageBox.warning(self,
                                            u'Внимание',
                                            u'Пациент не обнаружен.\nХотите зарегистрировать пациента?',
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                            QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                self.editNewClient()


    @QtCore.pyqtSlot()
    def on_btnRegistry_clicked(self):
        self.editNewClient()


    @QtCore.pyqtSlot()
    def on_btnCreateEntry_clicked(self):
        self.createFreeInput()


    def getParamsDialogFilter(self):
        self.dialogInfo = {}
        self.dialogInfo['lastName'] = forceString(self.edtLastName.text())
        self.dialogInfo['firstName'] = forceString(self.edtFirstName.text())
        self.dialogInfo['patrName'] = forceString(self.edtPatrName.text())
        self.dialogInfo['sex'] = forceInt(self.cmbSex.currentIndex())
        self.dialogInfo['birthDate'] = forceDate(self.edtBirthDate.date())
        self.dialogInfo['docType'] = self.cmbDocType.value()
        self.dialogInfo['serialLeft'] = forceString(self.edtLeftSerial.text())
        self.dialogInfo['serialRight'] = forceString(self.edtRightSerial.text())
        self.dialogInfo['docNumber'] = forceString(self.edtNumber.text())


    def editNewClient(self):
        from Registry.ClientEditDialog  import CClientEditDialog
        if QtGui.qApp.userHasAnyRight([urAdmin, urAddClient]):
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
            try:
                dialog = CClientEditDialog(self)
                dialog.tabWidget.setTabEnabled(7, False)
                dialog.tabRelations.setEnabled(False)
                self.getParamsDialogFilter()
                if self.dialogInfo:
                    dialog.setClientDialogInfo(self.dialogInfo)
                if self.regAddressInfo or self.logAddressInfo:
                    dialog.btnCopyPrevAddress.setEnabled(True)
                    dialog.prevAddress = None
                    dialog.setParamsRegAddress(self.regAddressInfo)
                    dialog.setParamsLocAddress(self.logAddressInfo)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            if dialog.exec_():
                clientId = dialog.itemId()
                self.selectClientRelationCode(clientId)


    def createFreeInput(self):
        db = QtGui.qApp.db
        nameList = [' '.join(forceString(self.edtLastName.text()).split()),
                        ' '.join(forceString(self.edtFirstName.text()).split()),
                        ' '.join(forceString(self.edtPatrName.text()).split())]
        documentList = [' '.join(forceString(self.edtLeftSerial.text()).split()),
                            ' '.join(forceString(self.edtRightSerial.text()).split()),
                            ' '.join(forceString(self.edtNumber.text()).split())]
        work = forceStringEx(self.edtWork.text())
        name= (' '.join(nameList)).strip()
        sex = forceInt(self.cmbSex.currentIndex())
        birthDate = forceString(self.edtBirthDate.date())
        docType = forceString(db.translate(db.table('rbDocumentType'), 'id', self.cmbDocType.value(), 'name'))
        docNumber = (' '.join(documentList)).strip()
        comment = forceStringEx(self.edtComment.text())
        result = ''
        if name:
            result += name
            result += u', пол: %s' % (u'м' if sex == 1 else u'ж' if sex == 2 else u'')
            if birthDate or docType or docNumber:
                result += ', '
        if birthDate:
            result += birthDate
            if docType or docNumber:
                result += ', '
        if docType:
            result += docType
            if docNumber:
                result += ': '
        if docNumber:
            result += docNumber
        if work:
            result += u', Занятость: %s' % work
        if comment:
            result += u', Прочее: %s' % comment
        self.selectClientRelationCode(0,  result)




    def setClientRelationIdList(self, idList, posToId):
        if idList:
            self.tblClientRelation.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblClientRelation.setFocus(Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.edtLastName.setFocus(Qt.OtherFocusReason)


    def getClientRelationIdList(self, lastName, firstName, patrName, sex, birthDate, docTypeId, serial, number, forceCode, clientId):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableAddress = db.table('ClientAddress')
        tableRBDocumentType = db.table('rbDocumentType')
        queryTable = tableClient.leftJoin(tableAddress, tableClient['id'].eq(tableAddress['client_id']))
        queryTable = queryTable.leftJoin(tableDocument, tableClient['id'].eq(tableDocument['client_id']))
        queryTable = queryTable.leftJoin(tableRBDocumentType, tableDocument['documentType_id'].eq(tableRBDocumentType['id']))
        cond = [tableClient['deleted'].eq(0)]
        if clientId:
            cond.append(tableClient['id'].ne(clientId))
        orderList = ['Client.lastName', 'Client.firstName', 'Client.patrName']
        if lastName:
            cond.append(tableClient['lastName'].like(lastName))
        if firstName:
            cond.append(tableClient['firstName'].like(firstName))
        if patrName:
            cond.append(tableClient['patrName'].like(patrName))
        if sex:
            cond.append(tableClient['sex'].eq(sex))
        if birthDate:
            cond.append(tableClient['birthDate'].eq(birthDate))
        if docTypeId:
            cond.append(tableDocument['documentType_id'].eq(docTypeId))
        if serial:
            cond.append(tableDocument['serial'].eq(serial))
        if number:
            cond.append(tableDocument['number'].eq(number))
        if docTypeId or serial or number:
            cond.append(tableDocument['deleted'].eq(0))        
        cond.append(db.joinOr([tableAddress['id'].isNull(), tableAddress['deleted'].eq(0)]))
        orderStr = ', '.join([fieldName for fieldName in orderList])
        idList = db.getDistinctIdList(queryTable, tableClient['id'].name(),
                              where=cond,
                              order=orderStr,
                              limit=1000)
        return idList


    def setDate(self, date):
        self.tableModel.date = date


    def setClientRelationCode(self, code, clientId, regAddressInfo, logAddressInfo):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        self.code = code
        self.clientId = clientId
        self.regAddressInfo = regAddressInfo
        self.logAddressInfo = logAddressInfo
        idList = []
        id = None
        if code:
            record = db.getRecordEx(tableClient, [tableClient['id']], [tableClient['deleted'].eq(0), tableClient['id'].eq(id)])
            if record:
                id = forceInt(record.value(0))
            if id:
                idList = [id]
        self.setClientRelationIdList(idList, id)


    def selectClientRelationCode(self, code,  freeInput = u''):
        self.code = code
        self.emit(SIGNAL('relatedClientIdSelected(int, QString)'), code,  freeInput)
        self.close()


    def getCurrentClientRelationCode(self):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        id = self.tblClientRelation.currentItemId()
        code = None
        if id:
            #TODO: atronah: что за бред? Проверка на наличие в базе и на deleted=0? Зачем для одного значения два имени: id и code?
            record = db.getRecordEx(tableClient, [tableClient['id']], [tableClient['deleted'].eq(0), tableClient['id'].eq(id)])
            if record:
                code = forceInt(record.value(0))
            return code
        return None


    @pyqtSlot(QModelIndex)
    def on_tblClientRelation_doubleClicked(self, index):
        if index.isValid():
            if (Qt.ItemIsEnabled & self.tableModel.flags(index)):
                code = self.getCurrentClientRelationCode()
                self.selectClientRelationCode(code)

    @QtCore.pyqtSlot()
    def on_edtLastName_editingFinished(self):
        lastName = forceStringEx(self.edtLastName.text())
        self.edtLastName.setText(nameCase(lastName))

    @QtCore.pyqtSlot()
    def on_edtFirstName_editingFinished(self):
        firstName = forceStringEx(self.edtFirstName.text())
        self.edtFirstName.setText(nameCase(firstName))
        self.evalSexByName('rdFirstName', firstName)

    @QtCore.pyqtSlot()
    def on_edtPatrName_editingFinished(self):
        patrName = forceStringEx(self.edtPatrName.text())
        self.edtPatrName.setText(nameCase(patrName))
        self.evalSexByName('rdPatrName', patrName)

    @QtCore.pyqtSlot(int)
    def on_cmbSex_currentIndexChanged(self, sex):
        if not self.isTabRelationsAlreadyLoad:
            focusWidget = QtGui.qApp.focusWidget()
            self.on_tabWidget_currentChanged(7)
            if focusWidget:
                focusWidget.setFocus(QtCore.Qt.MouseFocusReason)

    def evalSexByName(self, tableName, name):
        if not self.cmbSex.currentIndex():
            detectedSex = forceInt(QtGui.qApp.db.translate(tableName, 'name', name, 'sex'))
            self.cmbSex.setCurrentIndex(detectedSex)


class CClientRelationTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Фамилия', ['lastName'], 30))
        self.addColumn(CTextCol(u'Имя', ['firstName'], 30))
        self.addColumn(CTextCol(u'Отчество', ['patrName'], 30))
        self.addColumn(CTextCol(u'Номер клиента', ['id'], 20))
        self.addColumn(CEnumCol(u'Пол', ['sex'], ['', u'М', u'Ж'], 10))
        self.addColumn(CDateCol(u'Дата рождения', ['birthDate'], 20, highlightRedDate=False))
        self.addColumn(CTextCol(u'Адрес регистрации', ['regAddress'], 20))
        self.addColumn(CTextCol(u'Адрес проживания', ['logAddress'], 20))
        self.addColumn(CTextCol(u'Тип документа', ['name'], 20))
        self.addColumn(CTextCol(u'Серия документа', ['serial'], 20))
        self.addColumn(CTextCol(u'Номер документа', ['number'], 20))
        self.addColumn(CTextCol(u'Документ выдан', ['origin'], 20))
        self.addColumn(CDateCol(u'Дата выдачи документа', ['date'], 20))
        self.setTable('Client')
        self.date = QDate.currentDate()


    def flags(self, index):
        row = index.row()
        record = self.getRecordByRow(row)
        enabled = True
        if enabled:
            return Qt.ItemIsEnabled|Qt.ItemIsSelectable
        else:
            return Qt.ItemIsSelectable


    def setTable(self, tableName):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableAddress = db.table('ClientAddress')
        tableRBDocumentType = db.table('rbDocumentType')
        loadFields = []
        loadFields.append(u'''DISTINCT Client.id, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.sex, ClientDocument.serial, ClientDocument.number, ClientDocument.date, ClientDocument.origin, rbDocumentType.name, IF(ClientAddress.type = 0, concat(_utf8'Адрес регистрации: ', ClientAddress.freeInput), _utf8'') AS regAddress, IF(ClientAddress.type = 1, concat(_utf8'Адрес проживания: ', ClientAddress.freeInput), _utf8'') AS logAddress''')
        queryTable = tableClient.leftJoin(tableAddress, tableClient['id'].eq(tableAddress['client_id']))
        queryTable = queryTable.leftJoin(tableDocument, tableClient['id'].eq(tableDocument['client_id']))
        queryTable = queryTable.leftJoin(tableRBDocumentType, tableDocument['documentType_id'].eq(tableRBDocumentType['id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, loadFields)
