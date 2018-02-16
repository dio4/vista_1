#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.CreateEvent         import requestNewEvent
from Registry.RegistryWindow import CIdValidator

from library.database           import CTableRecordCache
from library.DialogBase         import CDialogBase
from library.TableModel         import CTableModel, CDateCol, CEnumCol, CTextCol
from library.Utils              import forceDate, forceRef, forceString, forceStringEx, getPref, getVal, setPref, forceBool

from Registry.ClientEditDialog  import CClientEditDialog
from Registry.Utils             import CCheckNetMixin, readOMSBarCode

from Orgs.Utils                 import advisePolicyType

from Users.Rights               import urAdmin, urRegTabWriteRegistry, urAddClient

from Ui_HospitalizationEventDialog import Ui_HospitalizationEventDialog
from library.simple_thread import SimpleThread
from ScardsModule.scard import Scard

class CHospitalizationEventDialog(CDialogBase, Ui_HospitalizationEventDialog, CCheckNetMixin):
    __pyqtSignals__ = ('HospitalizationEventCodeSelected(int)',)

    def __init__(self, parent, isQueue, clientId=None, eventId=None, otherType=False):
        CDialogBase.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        self.otherType = otherType
        self.tableModel = CHospitalizationEventDialogTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')

        self.setupGetClientIdMenu()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.tblHospitalizationEvent.setModel(self.tableModel)
        self.tblHospitalizationEvent.setSelectionModel(self.tableSelectionModel)
        self.parent = parent
        self.date = None
        self.code = None
        self.clientId = None
        self.eventId = eventId
        self.newEventId = None
        self.flagPlanningHospital = False
        self.dialogInfo = {}
        self.tblHospitalizationEvent.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CHospitalizationEventDialog', {})
        # self.tblHospitalizationEvent.loadPreferences(preferences)
        self.edtBirthDate.setDate(QtCore.QDate())
        self.edtLastName.setFocus(QtCore.Qt.OtherFocusReason)
        self.cmbDocType.setTable('rbDocumentType', True, 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.cmbPolicyType.setTable('rbPolicyType', True)
        self.connect(self.tblHospitalizationEvent, QtCore.SIGNAL('requestNewEvent'), self.requestNewEvent)
        self.btnCommit.clicked.connect(self.requestNewEvent)
        self.getPanning(isQueue, clientId)
        
        self.edtLastName.textChanged.connect(self.checkSearchAvailable)
        self.edtFirstName.textChanged.connect(self.checkSearchAvailable)
        self.edtPatrName.textChanged.connect(self.checkSearchAvailable)
        self.connect(self.edtBirthDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.checkSearchAvailable)
        self.cmbDocType.currentIndexChanged.connect(self.checkSearchAvailable)
        self.edtLeftSerial.textChanged.connect(self.checkSearchAvailable)
        self.edtRightSerial.textChanged.connect(self.checkSearchAvailable)
        self.edtNumber.textChanged.connect(self.checkSearchAvailable)
        self.cmbPolicyType.currentIndexChanged.connect(self.checkSearchAvailable)
        self.edtPolicySerial.textChanged.connect(self.checkSearchAvailable)
        self.edtPolicyNumber.textChanged.connect(self.checkSearchAvailable)
        self.cmbPolicyInsurer.currentIndexChanged.connect(self.checkSearchAvailable)
        self.edtPolicyBegDate.setDate(QtCore.QDate())
        self.edtPolicyEndDate.setDate(QtCore.QDate())
        self.edtContact.textChanged.connect(self.checkSearchAvailable)
        self.cmbSex.currentIndexChanged.connect(self.checkSearchAvailable)
        self.connect(self.edtPolicyBegDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.checkSearchAvailable)
        self.connect(self.edtPolicyEndDate, QtCore.SIGNAL('dateChanged(const QDate &)'), self.checkSearchAvailable)
        self.checkSearchAvailable()

        self.idValidator = CIdValidator(self)
        self.edtClientId.setValidator(self.idValidator)
        self.edtClientId.textChanged.connect(self.checkSearchAvailable)

        # сканирование полиса ОМС
        self.btnReadOMSBarcode.clicked.connect(self.on_actReadBarCode)
        self.btnReadOMSBarcode.setVisible(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderEnable', False)))
        self.omsPolicyData = {'errorMessage':  u'<Unknown error>' }

        # ЭПОМС
        # i2340
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EPOMS', False)):
            self.readEpoms.setVisible(True)
            self.readEpoms.clicked.connect(self.on_actReadScard)
            self.cardReaderName = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'cardReader', 'none'))
        else:
            self.readEpoms.setVisible(False)

        self.cmbSex.setEnabled(True)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            self.btnApply.click()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def on_actReadScard(self):
        try:
            clientInfo = Scard().getClientInfo(self.cardReaderName)
            # self.edtFilterLastName.setText(getVal(clientInfo, 'lastname', ''))
            self.edtLastName.setText(clientInfo['lastname'])
            self.edtFirstName.setText(clientInfo['name'])
            self.edtPatrName.setText(clientInfo['patrname'])

            # self.on_edtLastName_editingFinished()
            # self.on_edtFirstName_editingFinished()
            # self.on_edtPatrName_editingFinished()

            # self.edtFilterPatrName.setEnabled(True)
            self.edtBirthDate.clear()
            self.edtBirthDate.addItem(clientInfo['birthday'])
            # self.edtBirthPlace.setText(clientInfo['born_in'])
            # self.edtSNILS.setText(clientInfo['SNILS'])

            self.edtPolicyBegDate.addItem(clientInfo['smo']['beg_date'])
            self.edtPolicyEndDate.addItem(clientInfo['policy']['end_date'])
            self.edtPolicyNumber.setText(clientInfo['policy']['number'])

            self.cmbPolicyType.setCurrentIndex(4)

            self.cmbPolicyInsurer._popup.setOGRN(clientInfo['smo']['OGRN'])
            self.cmbPolicyInsurer._popup.setOKATO(clientInfo['smo']['OKATO'])
            self.cmbPolicyInsurer._popup.disableArea()

            self.cmbPolicyInsurer._popup.on_buttonBox_apply()
            # self.cmbCompulsoryPolisCompany._popup.on_buttonBox_apply()
        except:
            QtGui.QMessageBox.warning(
                self,
                u'ОШИБКА',
                u"Картридер сообщил об ошибке. Проверьте вставлена ли карта правильно.",
                QtGui.QMessageBox.Ok
            )

    def evalSexByName(self, tableName, name):
        if not self.cmbSex.currentIndex():
            from library.Utils import forceInt
            detectedSex = forceInt(QtGui.qApp.db.translate(tableName, 'name', name, 'sex'))
            self.cmbSex.setCurrentIndex(detectedSex)

    @QtCore.pyqtSlot()
    def on_edtFirstName_editingFinished(self):
        self.evalSexByName('rdFirstName', self.edtFirstName.text())

    @QtCore.pyqtSlot()
    def on_edtPatrName_editingFinished(self):
        self.evalSexByName('rdPatrName', self.edtPatrName.text())


    @SimpleThread
    def barCodeReaderThread(self):
        PORT = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'BarCodeReaderName', u"COM2"))
        self.omsPolicyData = readOMSBarCode(PORT)

    def on_barCodeReaderThread_finished(self):
        self.btnReadOMSBarcode.setEnabled(True)
        if self.omsPolicyData['errorMessage']:
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка чтения',
                self.omsPolicyData['errorMessage'],
                QtGui.QMessageBox.Close)
        else:
            self.on_btnReset_clicked()
            self.edtLastName.setText(self.omsPolicyData['lastName'])
            self.edtFirstName.setText(self.omsPolicyData['firstName'])
            self.edtPatrName.setText(self.omsPolicyData['patrName'])
            self.edtBirthDate.setDate(self.omsPolicyData['bDate'])
            self.cmbSex.setCurrentIndex(self.omsPolicyData['sex'])

            self.edtPolicySerial.setText(u'ЕП')
            self.edtPolicyNumber.setText(self.omsPolicyData['number'])

            self.cmbPolicyType.setCode(u'1')
            self.edtPolicyBegDate.setDate(self.omsPolicyData['endDate'])
            self.edtPolicyEndDate.setDate(QtCore.QDate(2200, 01, 01))

            self.on_btnApply_clicked()

    def on_actReadBarCode(self):
        thread = self.barCodeReaderThread(thr_method = 'b', thr_start = False)
        thread.finished.connect(self.on_barCodeReaderThread_finished)
        self.btnReadOMSBarcode.setEnabled(False)
        thread.start()

    def setupGetClientIdMenu(self):
        pass

    @QtCore.pyqtSlot()
    def checkSearchAvailable(self):
        isAvailable = bool(forceStringEx(self.edtLastName.text())
                           or forceStringEx(self.edtLastName.text())
                           or forceStringEx(self.edtFirstName.text())
                           or forceStringEx(self.edtPatrName.text())
                           or forceDate(self.edtBirthDate.date()).isValid()
                           or forceRef(self.cmbDocType.value())
                           or forceStringEx(self.edtLeftSerial.text())
                           or forceStringEx(self.edtRightSerial.text())
                           or forceStringEx(self.edtNumber.text())
                           or forceRef(self.cmbPolicyType.value())
                           or forceStringEx(self.edtPolicySerial.text())
                           or forceStringEx(self.edtPolicyNumber.text())
                           or forceRef(self.cmbPolicyInsurer.value())
                           or forceStringEx(self.edtContact.text())
                           or forceStringEx(self.edtClientId.text()))
        self.btnApply.setEnabled(isAvailable)

    @QtCore.pyqtSlot()
    def on_actGetClientId_triggered(self):
        pass

    @QtCore.pyqtSlot(int)
    def on_cmbPolicyInsurer_currentIndexChanged(self, index):
        self.updatePolicyType()
        self.getParamsDialogHospital()

    def updatePolicyType(self):
        serial = forceStringEx(self.edtPolicySerial.text())
        insurerId = self.cmbPolicyInsurer.value()
        if serial and insurerId:
            policyTypeId = advisePolicyType(insurerId, serial)
            self.cmbPolicyType.setValue(policyTypeId)

    def getPanning(self, isQueue, clientId):
        if isQueue and clientId:
            self.tblHospitalizationEvent.model().setTable('Client')
            self.selectHospitalizationEventCode(clientId)
            self.setHospitalizationEventIdList([clientId], clientId)
            self.flagPlanningHospital = True
            self.tabSearch.setEnabled(False)
            self.btnApply.setEnabled(False)
            self.btnRegistry.setEnabled(False)
            self.btnReset.setEnabled(False)

    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent is not None:
            opt=QtGui.QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox, opt, QtGui.QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos()):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QDialog.mousePressEvent(self, event)

    def eventFilter(self, watched, event):
        if watched == self.tblHospitalizationEvent:
            if event.type() == QtCore.QEvent.KeyPress and event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                event.accept()
                index = self.tblHospitalizationEvent.currentIndex()
                self.tblHospitalizationEvent.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QDialog.eventFilter(self, watched, event)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, idx):
        self.btnCommit.setDefault(idx == 0)
        self.btnApply.setDefault(idx == 1)

    @QtCore.pyqtSlot()
    def on_btnFillingFilter_clicked(self):
        clientId = QtGui.qApp.currentClientId()
        if clientId != self.clientId:
            db = QtGui.qApp.db
            tableClient = db.table('Client')
            record = db.getRecordEx(tableClient, [tableClient['lastName'], tableClient['firstName'], tableClient['patrName'], tableClient['birthDate']], [tableClient['deleted'].eq(0), tableClient['id'].eq(clientId)])
            if record:
                self.edtLastName.setText(forceString(record.value('lastName')))
                self.edtFirstName.setText(forceString(record.value('firstName')))
                self.edtPatrName.setText(forceString(record.value('patrName')))
                self.edtBirthDate.setDate(forceDate(record.value('birthDate')))

    @QtCore.pyqtSlot()
    def on_btnReset_clicked(self):
        self.on_buttonBox_reset()

    @QtCore.pyqtSlot()
    def on_btnApply_clicked(self):
        self.on_buttonBox_apply()

    @QtCore.pyqtSlot()
    def on_btnRegistry_clicked(self):
        self.editNewClient()

    def editNewClient(self):
        if QtGui.qApp.userHasAnyRight([urAdmin, urAddClient]):
            dialog = CClientEditDialog(self)
            self.getParamsDialogHospital()
            if self.dialogInfo:
                dialog.setClientDialogInfo(self.dialogInfo)
            if dialog.exec_():
                clientId = dialog.itemId()
                self.tblHospitalizationEvent.model().setTable('Client')
                self.setHospitalizationEventIdList([clientId], clientId)
                self.focusClients()
                self.requestNewEvent()


#    @QtCore.pyqtSlot()
#    def on_btnClose_clicked(self):
#        self.close()

    def on_buttonBox_reset(self):
        self.dialogInfo = {}
        self.edtLastName.setText('')
        self.edtFirstName.setText('')
        self.edtPatrName.setText('')
        self.edtClientId.setText('')
        self.edtBirthDate.setDate(QtCore.QDate())
        self.cmbSex.setCurrentIndex(0)
        self.cmbDocType.setValue(None)
        self.edtLeftSerial.setText('')
        self.edtRightSerial.setText('')
        self.edtNumber.setText('')
        self.newEventId = None
        self.edtContact.setText('')
        self.edtPolicySerial.setText('')
        self.edtPolicyNumber.setText('')
        self.cmbPolicyInsurer.setValue(None)
        self.cmbPolicyType.setValue(None)
        self.edtPolicyBegDate.setDate(QtCore.QDate())
        self.edtPolicyEndDate.setDate(QtCore.QDate())

    def on_buttonBox_apply(self):
        self.newEventId = None
        crIdList = self.getHospitalizationEventIdList()
        self.setHospitalizationEventIdList(crIdList, None)

    def setHospitalizationEventIdList(self, idList, posToId):
        if idList:
            self.tblHospitalizationEvent.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblHospitalizationEvent.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.edtLastName.setFocus(QtCore.Qt.OtherFocusReason)
            res = QtGui.QMessageBox.warning(self,
                                            u'Внимание',
                                            u'Пациент не обнаружен.\nХотите зарегистрировать пациента?',
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                            QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                self.editNewClient()
                self.focusClients()

    def getParamsDialogHospital(self):
        self.dialogInfo = {}
        self.dialogInfo['lastName'] = forceString(self.edtLastName.text())
        self.dialogInfo['firstName'] = forceString(self.edtFirstName.text())
        self.dialogInfo['patrName'] = forceString(self.edtPatrName.text())
        self.dialogInfo['clientId'] = forceRef(self.edtClientId.text())
        self.dialogInfo['birthDate'] = forceDate(self.edtBirthDate.date())
        self.dialogInfo['sex'] = self.cmbSex.currentIndex()
        self.dialogInfo['docType'] = self.cmbDocType.value()
        self.dialogInfo['serialLeft'] = forceString(self.edtLeftSerial.text())
        self.dialogInfo['serialRight'] = forceString(self.edtRightSerial.text())
        self.dialogInfo['docNumber'] = forceString(self.edtNumber.text())
        self.dialogInfo['contact'] = forceString(self.edtContact.text())
        self.dialogInfo['polisSerial'] = forceString(self.edtPolicySerial.text())
        self.dialogInfo['polisNumber'] = forceString(self.edtPolicyNumber.text())
        self.dialogInfo['polisCompany'] = self.cmbPolicyInsurer.value()
        self.dialogInfo['polisType'] = self.cmbPolicyType.value()
        self.dialogInfo['polisTypeName'] = self.cmbPolicyType.model().getName(self.cmbPolicyType.currentIndex())
        self.dialogInfo['polisBegDate'] = forceDate(self.edtPolicyBegDate.date())
        self.dialogInfo['polisEndDate'] = forceDate(self.edtPolicyEndDate.date())

    def getHospitalizationEventIdList(self):
        self.dialogInfo = {}
        lastName = forceStringEx(self.edtLastName.text())
        firstName = forceStringEx(self.edtFirstName.text())
        patrName = forceStringEx(self.edtPatrName.text())
        birthDate = forceDate(self.edtBirthDate.date())
        clientId = forceRef(self.edtClientId.text())
        sex = self.cmbSex.currentIndex()
        docTypeId = self.cmbDocType.value()
        leftSerial = forceStringEx(self.edtLeftSerial.text())
        rightSerial = forceStringEx(self.edtRightSerial.text())
        number = forceStringEx(self.edtNumber.text())
        contactText = self.edtContact.text()
        contact = forceString((contactText.remove(QtCore.QChar('-'), QtCore.Qt.CaseInsensitive)).remove(QtCore.QChar(' '), QtCore.Qt.CaseInsensitive))
        policyType = self.cmbPolicyType.value()
        policySerial = forceStringEx(self.edtPolicySerial.text())
        policyNumber = forceStringEx(self.edtPolicyNumber.text())
        policyInsurer = self.cmbPolicyInsurer.value()
        policyBegDate = self.edtPolicyBegDate.date()
        policyEndDate = self.edtPolicyEndDate.date()
        self.dialogInfo['lastName'] = lastName
        self.dialogInfo['firstName'] = firstName
        self.dialogInfo['patrName'] = patrName
        self.dialogInfo['birthDate'] = birthDate
        self.dialogInfo['clientId'] = clientId
        self.dialogInfo['sex'] = sex
        self.dialogInfo['docType'] = docTypeId
        self.dialogInfo['serialLeft'] = leftSerial
        self.dialogInfo['serialRight'] = rightSerial
        self.dialogInfo['docNumber'] = number
        self.dialogInfo['contact'] = forceString(self.edtContact.text())
        self.dialogInfo['polisSerial'] = policySerial
        self.dialogInfo['polisNumber'] = policyNumber
        self.dialogInfo['polisCompany'] = policyInsurer
        self.dialogInfo['polisType'] = policyType
        self.dialogInfo['polisTypeName'] = self.cmbPolicyType.model().getName(self.cmbPolicyType.currentIndex())
        self.dialogInfo['polisBegDate'] = policyBegDate
        self.dialogInfo['polisEndDate'] = policyEndDate
        serial = u''
        if leftSerial:
            serial = leftSerial
        if rightSerial:
            if serial != u'':
                serial += u' ' + rightSerial
            else:
                serial += rightSerial
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableAddress = db.table('ClientAddress')
        tableRBDocumentType = db.table('rbDocumentType')
        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyType = db.table('rbPolicyType')
        tableOrganisation = db.table('Organisation')
        tableClientContact = db.table('ClientContact')
        queryTable = tableClient.leftJoin(tableAddress, db.joinAnd([tableClient['id'].eq(tableAddress['client_id']), tableAddress['deleted'].eq(0)]))
        cond = [tableClient['deleted'].eq(0)]
        if self.clientId:
            cond.append(tableClient['id'].ne(self.clientId))
        orderList = ['Client.lastName', 'Client.firstName', 'Client.patrName']
        if clientId:
            cond.append(tableClient['id'].eq(clientId))
        if lastName:
            cond.append(tableClient['lastName'].like('%%%s%%' % lastName))
        if firstName:
            cond.append(tableClient['firstName'].like('%%%s%%' % firstName))
        if patrName:
            cond.append(tableClient['patrName'].like('%%%s%%' % patrName))
        if birthDate:
            cond.append(tableClient['birthDate'].eq(birthDate))
        if sex:
            cond.append(tableClient['sex'].eq(sex))
        if docTypeId:
            cond.append(tableDocument['documentType_id'].eq(docTypeId))
        if serial:
            cond.append(tableDocument['serial'].eq(serial))
        if number:
            cond.append(tableDocument['number'].eq(number))
        if docTypeId or serial or number:
            queryTable = queryTable.innerJoin(tableDocument, tableClient['id'].eq(tableDocument['client_id']))
            queryTable = queryTable.innerJoin(tableRBDocumentType, tableDocument['documentType_id'].eq(tableRBDocumentType['id']))
            cond.append(tableDocument['deleted'].eq(0))
        if contact:
            queryTable = queryTable.innerJoin(tableClientContact, tableClient['id'].eq(tableClientContact['client_id']))
            strContact = u'%'
            for element in contact:
                strContact += element + u'%'
            if len(strContact) > 1:
                cond.append(tableClientContact['contact'].like(strContact))
        if policySerial or policyNumber or policyInsurer or policyType:
            queryTable = queryTable.innerJoin(tableClientPolicy, tableClient['id'].eq(tableClientPolicy['client_id']))
            if policyType:
                queryTable = queryTable.innerJoin(tablePolicyType, tableClientPolicy['policyType_id'].eq(tablePolicyType['id']))
            if policyInsurer:
                queryTable = queryTable.innerJoin(tableOrganisation, tableClientPolicy['insurer_id'].eq(tableOrganisation['id']))
            if policySerial:
                cond.append(tableClientPolicy['serial'].eq(policySerial))
            if policyNumber:
                cond.append(tableClientPolicy['number'].eq(policyNumber))
            if policyInsurer:
                cond.append(tableClientPolicy['insurer_id'].eq(policyInsurer))
            if policyType:
                cond.append(tableClientPolicy['policyType_id'].eq(policyType))
            if policyBegDate.isValid():
                cond.append(tableClientPolicy['begDate'].eq(policyBegDate))
            if policyEndDate.isValid():
                cond.append(tableClientPolicy['endDate'].eq(policyEndDate))
        orderStr = ', '.join([fieldName for fieldName in orderList])
        idList = db.getDistinctIdList(queryTable, tableClient['id'].name(),
                              where=cond,
                              order=orderStr,
                              limit=1000)
        return idList

    def setDate(self, date):
        self.tableModel.date = date

    def selectHospitalizationEventCode(self, code):
        if self.otherType:
            return
        self.code = code
        self.emit(QtCore.SIGNAL('HospitalizationEventCodeSelected(int)'), code)

    def getCurrentClientId(self):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        id = self.tblHospitalizationEvent.currentItemId()
        code = None
        if id:
            record = db.getRecordEx(tableClient, [tableClient['id']], [tableClient['deleted'].eq(0), tableClient['id'].eq(id)])
            if record:
                code = forceRef(record.value(0))
            return code
        return None

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblHospitalizationEvent_doubleClicked(self, index):
        if index.isValid():
            if (QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index)):
                clientId = self.getCurrentClientId()
                if clientId and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
                    self.selectHospitalizationEventCode(clientId)
                    self.editClient(clientId)
                    self.focusClients()

    def editClient(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry if clientId else urAddClient]):
            dialog = CClientEditDialog(self)
            if clientId:
                dialog.load(clientId)
            dialog.exec_()

    def focusClients(self):
        self.tblHospitalizationEvent.setFocus(QtCore.Qt.TabFocusReason)

    def requestNewEvent(self):
        self.close()
        self.newEventId = None
        clientId = self.getCurrentClientId()
        actionId = None
        bedId = None
        orgStructureId = None
        begDate = None
        endDate = None
        execDate = None
        personId = None
        actionTypeIdValue = None
        flagHospitalization = True
        financeId = None
        protocolQuoteId = None
        planningHospitalEventId = None
        if self.eventId and self.flagPlanningHospital:
            actionId, orgStructureId, bedId, begDate, endDate, execDate, personId, form = self.getDataQueueEvent(self.eventId)
            planningHospitalEventId = self.eventId
            financeId = self.getPlanningFinanceId(self.eventId)
            if form == '027':
                protocolQuoteId = self.getProtocolQuote(self.eventId)
        if clientId:
            if self.otherType:
                self.newEventId = requestNewEvent(self.parent, clientId)
            else:
                self.selectHospitalizationEventCode(clientId)
                eventTypeFilterHospitalization = forceRef(
                    getVal(QtGui.qApp.preferences.appPrefs, 'hospitalizationDefaultEventTypeId', None)) \
                                                or '(EventType.medicalAidType_id IN' \
                                                   ' (SELECT rbMedicalAidType.id from rbMedicalAidType where' \
                                                   ' rbMedicalAidType.code IN (\'1\', \'2\', \'3\', \'7\', \'10\')))'
                diagnos = self.getDiagnosString(self.eventId)
                self.newEventId = requestNewEvent(
                    self.parent,
                    clientId,
                    flagHospitalization,
                    actionTypeIdValue,
                    [orgStructureId, bedId],
                    eventTypeFilterHospitalization,
                    None,
                    personId,
                    planningHospitalEventId,
                    diagnos,
                    financeId,
                    protocolQuoteId
                )
            if self.newEventId:
                if self.flagPlanningHospital and actionId:
                    self.editReceivedQueueEvent(actionId, begDate, endDate, execDate)
                return self.newEventId
        return None

    def getPlanningFinanceId(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableActionPRBF = db.table('ActionProperty_rbFinance')
            tableActionProperty = db.table('ActionProperty')
            tableAPT = db.table('ActionPropertyType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            table = table.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableActionProperty, tableActionProperty['type_id'].eq(tableAPT['id']))
            table = table.innerJoin(tableActionPRBF, tableActionPRBF['id'].eq(tableActionProperty['id']))
            cols = [tableActionPRBF['value']]
            cond = [tableEvent['id'].eq(eventId),
                    tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'planning%')),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAction['id'].isNotNull(),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableAPT['deleted'].like(u'источник финансирования'),
                    tableActionProperty['deleted'].eq(0),
                    tableActionProperty['action_id'].eq(tableAction['id'])
                    ]
            record = db.getRecordEx(table, cols, cond, 'Action.id DESC')
            return forceRef(record.value('value')) if record else None
        return None

    def getProtocolQuote(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableActionCQ = db.table('ActionProperty_Client_Quoting')
            tableActionProperty = db.table('ActionProperty')
            tableAPT = db.table('ActionPropertyType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            table = table.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableActionProperty, tableActionProperty['type_id'].eq(tableAPT['id']))
            table = table.innerJoin(tableActionCQ, tableActionCQ['id'].eq(tableActionProperty['id']))
            cols = [tableActionCQ['value']]
            cond = [tableEvent['id'].eq(eventId),
                    tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode(u'protocol%')),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableAction['id'].isNotNull(),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableAPT['name'].like(u'Квота'),
                    tableActionProperty['deleted'].eq(0),
                    tableActionProperty['action_id'].eq(tableAction['id'])
                    ]
            record = db.getRecordEx(table, cols, cond, 'Action.id DESC')
            return forceRef(record.value('value')) if record else None
        return None

    def getDiagnosString(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            table = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            cols = [tableActionType['flatCode']]
            cols.append('''(SELECT APS.value
                            FROM ActionPropertyType AS APT
                            INNER JOIN ActionProperty AS AP ON AP.type_id=APT.id
                            INNER JOIN ActionProperty_String AS APS ON APS.id=AP.id
                            WHERE  Action.id IS NOT NULL AND APT.actionType_id=Action.actionType_id AND AP.action_id=Action.id AND APT.deleted=0 AND APT.name LIKE '%s') AS diagnos'''%(u'Диагноз'))
            cond = [tableEvent['id'].eq(eventId),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0),
                    tableActionType['deleted'].eq(0)
                    ]
            records = db.getRecordList(table, cols, cond, 'Action.endDate DESC')
            for record in records:
                diagnos = forceString(record.value('diagnos'))
                flatCode = forceString(record.value('flatCode'))
                if u'protocol' in flatCode.lower():
                    return diagnos
            for record in records:
                diagnos = forceString(record.value('diagnos'))
                if diagnos:
                    return diagnos
        return None

    def getDataQueueEvent(self, eventId = None):
        if eventId:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            db = QtGui.qApp.db
            tableAPHB = db.table('ActionProperty_HospitalBed')
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableActionType = db.table('ActionType')
            tableAction = db.table('Action')
            tableOSHB = db.table('OrgStructure_HospitalBed')
            tableOS = db.table('OrgStructure')
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            tableAPOS = db.table('ActionProperty_OrgStructure')
            cols = [tableAction['id'],
                    tableAction['begDate'],
                    tableAction['endDate'],
                    tableAction['person_id'],
                    tableEvent['execDate'],
                    tableEventType['form'],
                    tableOSHB['id'].alias('bedId')
                    ]
            queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryTable = queryTable.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
            queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
            queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            cond = [tableActionType['flatCode'].like('planning'),
                    tableAction['deleted'].eq(0),
                    tableAP['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableOS['deleted'].eq(0),
                    tableEvent['deleted'].eq(0),
                    tableEventType['deleted'].eq(0),
                    tableAction['event_id'].eq(eventId),
                    tableAPT['typeName'].like('HospitalBed'),
                    tableAP['action_id'].eq(tableAction['id'])
                    ]
            records = db.getRecordList(queryTable, cols, cond)
            orgStructureId = None
            begDate = None
            endDate = None
            actionId = None
            bedId = None
            execDate = None
            personId = None
            form = ''
            for record in records:
                actionId = forceRef(record.value('id'))
                bedId = forceRef(record.value('bedId'))
                begDate = forceDate(record.value('begDate'))
                endDate = forceDate(record.value('endDate'))
                execDate = forceDate(record.value('execDate'))
                personId = forceRef(record.value('person_id'))
                form     = forceString(record.value('form'))

            cols = [tableAction['id'],
                    tableAction['begDate'],
                    tableAction['endDate'],
                    tableAction['person_id'],
                    tableEvent['execDate'],
                    tableEventType['form'],
                    tableOS['id'].alias('orgStructureId')
                    ]
            cond = [tableActionType['flatCode'].like(u'planning%'),
                tableAction['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableAction['event_id'].eq(eventId),
                tableActionType['deleted'].eq(0),
                tableAPT['deleted'].eq(0),
                tableOS['deleted'].eq(0),
                tableAP['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tableAP['action_id'].eq(tableAction['id']),
                tableAPT['typeName'].like('OrgStructure')
                ]
            queryNoBed = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            queryNoBed = queryNoBed.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            queryNoBed = queryNoBed.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            queryNoBed = queryNoBed.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
            queryNoBed = queryNoBed.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
            queryNoBed = queryNoBed.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
            queryNoBed = queryNoBed.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
            recordsNoBed = db.getRecordList(queryNoBed, cols, cond)
            for recordNoBed in recordsNoBed:
                actionId = forceRef(recordNoBed.value('id'))
                orgStructureId = forceRef(recordNoBed.value('orgStructureId'))
                begDate = forceDate(recordNoBed.value('begDate'))
                endDate = forceDate(recordNoBed.value('endDate'))
                execDate = forceDate(recordNoBed.value('execDate'))
                personId = forceRef(recordNoBed.value('person_id'))
                form     = forceString(recordNoBed.value('form'))
        return actionId, orgStructureId, bedId, begDate, endDate, execDate, personId, form

    def editReceivedQueueEvent(self, actionId, begDate, endDate, execDate):
        if actionId:
            currentDateTime = QtCore.QDateTime.currentDateTime()
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            if not endDate:
                recQuery = db.updateRecords(tableAction.name(), tableAction['endDate'].eq(currentDateTime), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])
                recQuery = db.updateRecords(tableAction.name(), tableAction['status'].eq(2), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])
                if not begDate:
                    recQuery = db.updateRecords(tableAction.name(), tableAction['begDate'].eq(currentDateTime), [tableAction['id'].eq(actionId), tableAction['deleted'].eq(0)])


class CHospitalizationEventDialogTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Фамилия', ['lastName'], 30))
        self.addColumn(CTextCol(u'Имя', ['firstName'], 30))
        self.addColumn(CTextCol(u'Отчество', ['patrName'], 30))
        self.addColumn(CTextCol(u'Номер клиента', ['id'], 20))
        self.addColumn(CEnumCol(u'Пол', ['sex'], ['', u'М', u'Ж'], 10))
        self.addColumn(CDateCol(u'Дата рождения', ['birthDate'], 20))
        self.addColumn(CTextCol(u'Адрес регистрации', ['regAddress'], 20))
        self.addColumn(CTextCol(u'Адрес проживания', ['logAddress'], 20))
        self.addColumn(CTextCol(u'Контакт', ['contact'], 20))
        self.addColumn(CTextCol(u'Тип документа', ['name'], 20))
        self.addColumn(CTextCol(u'Серия документа', ['serial'], 20))
        self.addColumn(CTextCol(u'Номер документа', ['number'], 20))
        self.addColumn(CTextCol(u'Документ выдан', ['origin'], 20))
        self.addColumn(CDateCol(u'Дата выдачи документа', ['date'], 20))
        self.addColumn(CTextCol(u'страховая организация', ['nameOrgPolicy'], 20))
        self.addColumn(CTextCol(u'страховая Id', ['id'], 20))
        self.addColumn(CTextCol(u'Тип полиса', ['typePolicy'], 20))
        self.addColumn(CTextCol(u'Серия полиса', ['serialPolicy'], 20))
        self.addColumn(CTextCol(u'Номер полиса', ['numberPolicy'], 20))

        self.setTable('Client')
        self.date = QtCore.QDate.currentDate()

    def flags(self, index):
        # row = index.row()
        # record = self.getRecordByRow(row)
        enabled = True
        if enabled:
            return QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsSelectable

    def setTable(self, tableName):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableAddress = db.table('ClientAddress')
        tableRBDocumentType = db.table('rbDocumentType')
        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyType = db.table('rbPolicyType')
        tableOrganisation = db.table('Organisation')
        tableClientContact = db.table('ClientContact')
        loadFields = []
        loadFields.append(u'''DISTINCT Client.id, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.sex, ClientDocument.serial, ClientDocument.number, ClientDocument.date, ClientDocument.origin, rbDocumentType.name, IF(ClientAddress.type = 0,  ClientAddress.freeInput, _utf8'') AS regAddress, IF(ClientAddress.type = 1, ClientAddress.freeInput, _utf8'') AS logAddress, ClientPolicy.serial AS serialPolicy, ClientPolicy.number AS numberPolicy, rbPolicyType.name AS typePolicy, Organisation.shortName AS nameOrgPolicy, Organisation.id, ClientContact.contact''')
        queryTable = tableClient.leftJoin(tableAddress, tableClient['id'].eq(tableAddress['client_id']))
        queryTable = queryTable.leftJoin(tableDocument, tableClient['id'].eq(tableDocument['client_id']))
        queryTable = queryTable.leftJoin(tableRBDocumentType, tableDocument['documentType_id'].eq(tableRBDocumentType['id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, tableClient['id'].eq(tableClientPolicy['client_id']))
        queryTable = queryTable.leftJoin(tablePolicyType, tableClientPolicy['policyType_id'].eq(tablePolicyType['id']))
        queryTable = queryTable.leftJoin(tableOrganisation, tableClientPolicy['insurer_id'].eq(tableOrganisation['id']))
        queryTable = queryTable.leftJoin(tableClientContact, tableClient['id'].eq(tableClientContact['client_id']))
        self._table = queryTable
        self._recordsCache = CTableRecordCache(db, self._table, loadFields)


class CFindClientInfoDialog(CHospitalizationEventDialog):
    def __init__(self, parent):
        CHospitalizationEventDialog.__init__(self, parent, None)
        self.filterClientId = None
        self.tblHospitalizationEvent.setPopupMenu(self.mnuGetClientId)

    def setupGetClientIdMenu(self):
        self.mnuGetClientId = QtGui.QMenu(self)
        self.mnuGetClientId.setObjectName('mnuGetClientId')
        self.actGetClientId = QtGui.QAction(u'''Добавить в фильтр "Стационарного монитора"''', self)
        self.actGetClientId.setObjectName('actGetClientId')
        self.mnuGetClientId.addAction(self.actGetClientId)

    @QtCore.pyqtSlot()
    def on_actGetClientId_triggered(self):
        self.filterClientId = self.getCurrentClientId()
        self.close()


def getActionTypeIdListByFlatCode(flatCode):
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    cond =[
        tableActionType['flatCode'].like(flatCode),
        tableActionType['deleted'].eq(0)
    ]
    return db.getIdList(tableActionType, 'id', cond)

