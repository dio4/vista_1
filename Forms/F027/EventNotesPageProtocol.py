# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils              import getRealPayed, getEventFinanceCode, isLittleStranger

from library.interchange       import getTextEditValue, setTextEditValue, getRBComboBoxValue, setRBComboBoxValue
from library.Utils             import forceRef, forceString, forceDate, forceInt

from Users.Rights              import urEditClientPolicyInClosedEvent

from Ui_EventNotesPageProtocol import Ui_EventNotesPageWidget


class CEventNotesPageProtocol(QtGui.QWidget, Ui_EventNotesPageWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setFocusProxy(self.edtEventNote)
        self._externalIdIsChanged = False

        self._clientId = QtGui.qApp.currentClientId()
        self.cmbClientPolicy.setClientId(self._clientId)


    @staticmethod
    def setId(widget, record, fieldName):
        value = forceString(record.value(fieldName))
        if value:
            text = unicode(value)
        else:
            text = ''
        widget.setText(text)


    @staticmethod
    def setDateTime(widget, record, fieldName):
        value = record.value(fieldName).toDateTime()
        if value:
            text = value.toString('dd.MM.yyyy hh:mm:ss')
        else:
            text = ''
        widget.setText(text)


    @staticmethod
    def setPerson(widget, record, fieldName):
        personId = forceRef(record.value(fieldName))
        if personId:
            record = QtGui.qApp.db.getRecord('vrbPersonWithSpeciality', 'code, name', personId)
            if record:
                text = forceString(record.value('code'))+ ' | ' + forceString(record.value('name'))
            else:
                text = '{'+str(personId)+'}'
        else:
            text = ''
        widget.setText(text)


    def setNotes(self, record):
        self.setId(self.lblEventIdValue, record, 'id')
        self.setDateTime(self.lblEventCreateDateTimeValue, record, 'createDatetime')
        self.setPerson(self.lblEventCreatePersonValue, record, 'createPerson_id')
        self.setDateTime(self.lblEventModifyDateTimeValue, record, 'modifyDatetime')
        self.setPerson(self.lblEventModifyPersonValue, record, 'modifyPerson_id')
        setTextEditValue(self.edtEventNote, record, 'note')

        setRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')
        self.cmbClientPolicy.setPolicyFromRepresentative(isLittleStranger(self._clientId, forceDate(record.value('setDate')), forceDate(record.value('execDate'))))
        self.updateClientPolicy(record)


    # copied from EventNotesPage
    def updateClientPolicy(self, record):
        if record is None:
            self.cmbClientPolicy.updatePolicy()
            return

        execDate = forceDate(record.value('execDate'))
        eventIsClosed = not execDate.isNull()
        eventIsPayed = getRealPayed(forceInt(record.value('payStatus')))

        if eventIsPayed or (eventIsClosed and not QtGui.qApp.userHasRight(urEditClientPolicyInClosedEvent)):
            self.cmbClientPolicy.setEnabled(False)
        else:
            self.cmbClientPolicy.setEventIsClosed(eventIsClosed)
            self.cmbClientPolicy.setDate(execDate if eventIsClosed else QtCore.QDate.currentDate())

            if getEventFinanceCode(forceRef(record.value('eventType_id'))) == 3:  # ДМС
                franchisPolicyTypeId = forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', 'franchis', 'id'))
                if franchisPolicyTypeId:
                    self.cmbClientPolicy.setPolicyTypeId(franchisPolicyTypeId)
                    self.cmbClientPolicy.updatePolicy()
                    if not self.cmbClientPolicy.value():
                        self.cmbClientPolicy.setPolicyTypeId(forceRef(QtGui.qApp.db.translate('rbPolicyType', 'code', '3', 'id')))
                        self.cmbClientPolicy.updatePolicy()
            else:
                self.cmbClientPolicy.updatePolicy()


    def getNotes(self, record, eventTypeId):
        getTextEditValue(self.edtEventNote, record, 'note')
        getRBComboBoxValue(self.cmbClientPolicy, record, 'clientPolicy_id')

    def checkEventExternalId(self, eventId):
        return []

    def enableEditors(self, eventTypeId):
        pass

    def getClientId(self):
        return self._clientId

    def setClientId(self, clientId):
        self._clientId = clientId

    def setEventResultId(self, resultId):
        pass

    def checkOrGenerateUniqueEventExternalId(self, itemId, eventTypeId):
        pass
