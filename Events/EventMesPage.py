# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Utils import getDefaultMesSpecificationId, getEventMesCodeMask, \
    getEventMesNameMask, getEventProfileId
from HospitalBeds.RelatedEventListDialog import CRelatedEventListModel
from Reports.CheckMesDescription import showCheckMesDescription
from Reports.MesDescription import showMesDescription
from Ui_EventMesPage import Ui_EventMesPageWidget
from Users.Rights import urSaveWithoutMes

from library.CSG.CSGComboBox import CCSGComboBox
from library.DialogBase import CConstructHelperMixin
from library.Utils import forceBool, forceInt, forceRef, forceString, forceTr
from library.interchange import getRBComboBoxValue, setRBComboBoxValue


class CFastEventMesPage(QtGui.QWidget, CConstructHelperMixin, Ui_EventMesPageWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.eventEditor = None
        self.eventId = None
        self.relatedEventsTableActive = QtGui.qApp.isNextEventCreationFromAction()

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        if self.relatedEventsTableActive:
            self.addModels('RelatedEvents', CRelatedEventListModel(self))

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        self.cmbHTG.setTable('mes.mrbHighTechMedicalGroups')
        self.cmbMesSpecification.setTable('rbMesSpecification')
        self.chkHTG.setEnabled(True)
        if self.relatedEventsTableActive:
            self.setModels(self.tblRelatedEvents, self.modelRelatedEvents, self.selectionModelRelatedEvents)
            self.grpRelatedEvents.setVisible(True)
        else:
            self.grpRelatedEvents.setVisible(False)

    def postSetupUi(self):
        self.setFocusProxy(self.cmbMes)
        self.cmbMes.setDefaultValue()

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor

    def setCSGComboBox(self):
        """
        DEPRECATED
        :return:
        """
        self.MESLayout.removeWidget(self.cmbMes)
        self.cmbMes.setVisible(False)
        self.cmbMes = CCSGComboBox(self)
        self.MESLayout.addWidget(self.cmbMes)

    def setRecord(self, record):
        setRBComboBoxValue(self.cmbMes, record, 'MES_id')
        setRBComboBoxValue(self.cmbHTG, record, 'HTG_id')
        if forceBool(self.cmbHTG.value()):
            self.chkHTG.setChecked(True)
        setRBComboBoxValue(self.cmbMesSpecification, record, 'mesSpecification_id')
        self.eventId = forceRef(record.value('id'))
        if self.relatedEventsTableActive and hasattr(self.eventEditor, 'prevEventId'):
            self.tblRelatedEvents.model().loadData(self.eventEditor.itemId(), self.eventEditor.prevEventId)

    def setEventTypeId(self, eventTypeId):
        if forceInt(QtGui.qApp.db.translate('EventType', 'id', eventTypeId, 'setFilterStandard')) == 1:
            self.setCSGComboBox()
        self.cmbMes.setEventTypeId(eventTypeId)
        self.cmbMes.setEventProfile(getEventProfileId(eventTypeId))
        self.cmbMes.setMESCodeTemplate(getEventMesCodeMask(eventTypeId))
        self.cmbMes.setMESNameTemplate(getEventMesNameMask(eventTypeId))
        if not self.cmbMesSpecification.value():
            self.cmbMesSpecification.setValue(getDefaultMesSpecificationId(eventTypeId))
        self.cmbMes._popup.setCheckBoxes('eventMesPage' + forceString(eventTypeId))

    def setBegDate(self, date):
        self.cmbMes.setBegDate(date)

    def setEndDate(self, date):
        self.cmbMes.setEndDate(date)

    def setClientInfo(self, clientSex, clientAge, clientId=None):
        self.cmbMes.setClientSex(clientSex)
        self.cmbMes.setClientAge(clientAge)
        self.cmbMes.setClientId(clientId)

    def setSpeciality(self, specialityId):
        self.cmbMes.setSpeciality(specialityId)

    def setContract(self, contractId):
        self.cmbMes.setContract(contractId)

    def setEndDateForTariff(self, endDate):
        self.cmbMes.setEndDateForTariff(endDate)

    def getRecord(self, record):
        getRBComboBoxValue(self.cmbMes, record, 'MES_id')
        getRBComboBoxValue(self.cmbMesSpecification, record, 'mesSpecification_id')
        if not self.chkHTG.isChecked():
            self.cmbHTG.setValue(0)
        getRBComboBoxValue(self.cmbHTG, record, 'HTG_id')

    def setMKB(self, MKB):
        self.cmbMes.setMKB(MKB)

    def setMKB2(self, MKB2List):
        self.cmbMes.setMKB2(MKB2List)

    def checkMesAndSpecification(self):
        if self.eventEditor.mesRequired:
            skippable = QtGui.qApp.userHasRight(urSaveWithoutMes)
            result = True
            # result = self.cmbMes.value() or self.eventEditor.checkInputMessage(u'МЭС', skippable, self.cmbMes)
            # Нет МЭСа - нет и спецификации, и проверять нечего.
            if not skippable and not self.cmbMes.value():
                result = result and self.cmbMes.value() or self.eventEditor.checkInputMessage(
                    forceTr(u'МЭС', u'EventEditDialog'), skippable, self.cmbMes)
            if not skippable and not self.cmbMesSpecification.value():
                result = result and (self.cmbMesSpecification.value() or self.eventEditor.checkInputMessage(
                    u'Особенности выполнения %s' % forceTr(u'МЭС', u'EventEditDialog'), skippable,
                    self.cmbMesSpecification))
            return result
        return True

    @QtCore.pyqtSlot(QtCore.QString)
    def on_cmbMes_editTextChanged(self, text):
        mesId = forceRef(self.cmbMes.value())
        if forceBool(mesId):
            pass
            # self.chkHTG.setEnabled(True)
        self.btnCheckMes.setEnabled(forceBool(mesId))
        self.btnShowMes.setEnabled(forceBool(mesId))

    @QtCore.pyqtSlot()
    def on_btnShowMes_pressed(self):
        mesId = self.cmbMes.value()
        if mesId:
            showMesDescription(self, mesId)

    @QtCore.pyqtSlot()
    def on_btnCheckMes_pressed(self):
        mesId = self.cmbMes.value()
        if mesId:
            showCheckMesDescription(self, mesId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblRelatedEvents_doubleClicked(self, index):
        if index.isValid():
            row = index.row()
            column = index.column()
            model = self.tblRelatedEvents.model()
            eventId = model.items[row][14]
            if eventId and not eventId in QtGui.qApp.openedEvents:
                self.editEvent(eventId)

    @QtCore.pyqtSlot(bool)
    def on_chkHTG_toggled(self, checked):
        self.cmbHTG.setEnabled(checked)

    def editEvent(self, eventId):
        from EditDispatcher import getEventFormClass
        formClass = getEventFormClass(eventId)
        dialog = formClass(self)
        dialog.load(eventId)
        return dialog.exec_()


class CEventMesPage(CFastEventMesPage):
    def __init__(self, parent=None):
        CFastEventMesPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()
