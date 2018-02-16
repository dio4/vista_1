# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2017 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceString

__author__ = 'nat'


class CComboBox(QtGui.QComboBox):
    __pyqtSignals__ = (
        'textChanged(QString)',
        'textEdited(QString)'
    )

    def __init__(self, popupClass, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self._popup = popupClass(self)
        self.connect(self._popup, QtCore.SIGNAL('ItemSelected(int)'), self.setValue)
        self.connect(self._popup, QtCore.SIGNAL('close()'), self.updateText)
        self.editTextChanged.connect(self.searchStringChanged)
        self.editTextChanged.connect(self.showPopup)

        self._date = QtCore.QDate.currentDate()
        self._clientSex = None
        self._clientAge = None
        self._contractId = None
        self._endDateForTariff = None
        self._specialityId = None
        self._availableIdList = None
        self._actionTypeIdList = None
        self._checkDate = None
        self._MKB = ''
        self._mesCodeTemplate = ''
        self._mesNameTemplate = ''
        self._eventTypeId = None
        self._clientId = None
        self._id = None
        self._MKB2List = []

        self._begDate = None
        self._endDate = None

        self.setValue(None)

    def setBegDate(self, date):
        self._begDate = date

    def setEndDate(self, date):
        self._endDate = date

    def setClientSex(self, clientSex):
        self._clientSex = clientSex

    def setClientAge(self, clientAge):
        self._clientAge = clientAge

    def setClientId(self, clientId):
        self._clientId = clientId

    def setContract(self, contractId):
        self._contractId = contractId

    def setCheckDate(self, checkDate):
        self._checkDate = checkDate

    def setMKB(self, MKB):
        self._MKB = MKB

    def setMKB2(self, MKB2List):
        self._MKB2List = MKB2List

    def setEventProfile(self, eventProfileId):
        pass

    def setEventTypeId(self, eventTypeId):
        self._eventTypeId = eventTypeId

    def setMESCodeTemplate(self, mesCodeTemplate):
        self._mesCodeTemplate = mesCodeTemplate

    def setMESNameTemplate(self, mesNameTemplate):
        self._mesNameTemplate = mesNameTemplate

    def setSpeciality(self, specialityId):
        self._specialityId = specialityId

    def setEndDateForTariff(self, endDate):
        try:
            if endDate.isValid():
                self._endDateForTariff = endDate
        except:
            pass

    def setDuration(self, duration):
        pass

    # atronah: None - не фильтровать по списку id. [] - фильтровать по пустому списку (т.е. запрет выбора)
    def setAvailableIdList(self, idList=None):
        self._availableIdList = idList

    def setActionTypeIdList(self, actionTypeIdList):
        self._actionTypeIdList = actionTypeIdList

    def setValue(self, id):
        self._id = id
        self.updateText()

    def value(self):
        return self._id

    def SPR69value(self):
        return self._id

    def getText(self, id):
        if id:
            db = QtGui.qApp.db
            table = db.table('mes.MES')
            record = db.getRecordEx(table, ['code', 'name'], [table['id'].eq(id), table['deleted'].eq(0)])
            if record:
                code = forceString(record.value('code'))
                name = forceString(record.value('name'))
                text = code + ' | ' + name
            else:
                text = '{%s}' % id
        else:
            text = ''
        return text

    @QtCore.pyqtSlot()
    def updateText(self):
        try:
            self.editTextChanged.disconnect(self.showPopup)
        except:
            pass
        finally:
            self.setEditText(self.getText(self._id))
            self.editTextChanged.connect(self.showPopup)

    @QtCore.pyqtSlot(QtCore.QString)
    def searchStringChanged(self, newSearchString):
        if self._popup and hasattr(self._popup, 'filterModelProxy'):
            # Вычленение кода (после updateText выводится строка вида <code> | <name>
            newSearchString = forceString(newSearchString).split('|')[0].strip()
            self._popup.filterModelProxy.setFilterFixedString(newSearchString)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            self.setValue(None)
            event.accept()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)
