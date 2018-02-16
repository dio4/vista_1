#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant

from Events.Utils import getActionTypeMesIdList
from library.ComboBox.ComboBox import CComboBox
from library.InDocTable import CInDocTableCol
from library.MES.MESComboBoxPopup import CMESComboBoxPopup
from library.Utils import forceInt, toVariant, forceString, forceRef


class CMESComboBox(CComboBox):
    def __init__(self, parent=None):
        CComboBox.__init__(self, CMESComboBoxPopup, parent)
        self._eventProfileId = None
        self._mesCodeTemplate = ''

    def setEventProfile(self, eventProfileId):
        self._eventProfileId = eventProfileId

    @QtCore.pyqtSlot()
    def showPopup(self):
        if not self.isVisible():
            return

        if not self._popup or self._popup.isVisible():
            return
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right()-size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom()-size.height()), screen.top()))

        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setup(self._clientSex,
                          self._clientAge,
                          self._clientId,
                          self._eventProfileId,
                          self._eventTypeId,
                          self._mesCodeTemplate,
                          self._mesNameTemplate,
                          self._specialityId,
                          self._contractId,
                          self._MKB,
                          self._id,
                          self._availableIdList,
                          self._endDateForTariff,
                          self._actionTypeIdList,
                          self._checkDate)


    def setDefaultValue(self):
        self._popup.setup(self._clientSex,
                          self._clientAge,
                          self._clientId,
                          self._eventProfileId,
                          self._eventTypeId,
                          self._mesCodeTemplate,
                          self._mesNameTemplate,
                          self._specialityId,
                          self._contractId,
                          self._MKB,
                          self._id,
                          endDateForTariff=self._endDateForTariff,
                          actionTypeIdList=self._actionTypeIdList,
                          date=self._checkDate)
        self._popup.setValueIfOnly()


class CMesInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, eventEditor, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.eventEditor = eventEditor
        self.mesTextCache = {}
        self.mesIdListByActionTypeCach = {}

    def toString(self, val, record):
        mesId = forceInt(record.value('MES_id'))
        if mesId:
            #TODO:skkachaev:CMESComboBox.getText(mesId) — Что это?
            rec = QtGui.qApp.db.getRecordEx('mes.MES', 'code', 'id = %i' % mesId)
            #mesText = self.mesTextCache.setdefault(mesId, CMESComboBox.getText(mesId))
            if rec:
                return toVariant(rec.value('code'))
        return QVariant()

    def createEditor(self, parent):
        comboBox = CMESComboBox(parent)
        comboBox._popup.setCheckBoxes('actionPage' + forceString(self.eventEditor.getEventTypeId()))
        return comboBox

    def setEditorData(self, editor, value, record):
        editor.setSpeciality(self.eventEditor.personSpecialityId)
        editor.setClientSex(self.eventEditor.clientSex)
        editor.setClientAge(self.eventEditor.clientAge)
        editor.setMKB(forceString(record.value('MKB')))

        financeId = forceRef(record.value('finance_id'))
        actionTypeId = forceRef(record.value('actionType_id'))
        eventSetDate = self.eventEditor.setDateTime.date() if self.eventEditor.setDateTime else None
        editor.setAvailableIdList(self.mesIdListByActionTypeCach.setdefault(actionTypeId,
                                                                               getActionTypeMesIdList(actionTypeId, financeId, date=eventSetDate)))
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())