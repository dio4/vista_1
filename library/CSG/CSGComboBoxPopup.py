# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2017 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.CSG.Utils import getCsgIdListByCond, getCSGDepartmentMaskByRegionalCode
from library.ComboBox.ComboBoxPopup import CComboBoxPopup
from library.TableModel import getPref, setPref
from library.Utils import forceString, getPrefBool


class CCSGComboBoxPopup(CComboBoxPopup):
    __pyqtSignals__ = ('resetText()')

    def __init__(self, parent=None):
        CComboBoxPopup.__init__(self, parent, type='CSG')
        self._duration = None
        self.chkMesCodeTemplate.setVisible(False)
        self.chkMesNameTemplate.setVisible(False)
        self.chkSpeciality.setVisible(False)
        self.chkEventProfile.setVisible(False)
        self.chkOperativeMes.setVisible(False)
        self.chkSex.setVisible(False)
        self.chkAge.setVisible(False)
        self.chkContract.setVisible(False)
        self.lblMKB.setText('')
        self.cmbMKB.setVisible(False)
        self.chkDuration.setVisible(False)

        self._begDate = None
        self._endDate = None

    def setValueIfOnly(self):
        idList = self.tableModel.idList()
        if idList:
            if len(idList) == 1:
                self._id = idList[0]
                self.table.setCurrentItemId(self._id)
                self.emit(QtCore.SIGNAL('ItemSelected(int)'), self._id)
                self.close()
                return self._id

    def setIdList(self, idList):
        if not self._isDoubleClick:
            self.emit(QtCore.SIGNAL('resetText()'))

        self._isDoubleClick = False
        if idList:
            self.tableSelectionModel.clear()
            self.tableModel.setIdList(idList)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.table.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.table.setIdList([], self._id)
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.chkSex.setFocus(QtCore.Qt.OtherFocusReason)

    def closeEvent(self, event):
        self.on_buttonBox_apply()
        self.setValueIfOnly()
        self.emit(QtCore.SIGNAL('closed()'))
        QtGui.QFrame.closeEvent(self, event)

    def on_buttonBox_reset(self):
        self.chkSex.setChecked(False)
        self.chkAge.setChecked(True)
        self.chkContract.setChecked(True)
        self.chkDuration.setChecked(False)

    def on_buttonBox_apply(self):
        idList = self.getKsgIdList(self.chkShowAll.isChecked())
        if len(idList) == 1: self._id = idList[0]
        self.setIdList(idList)

    def getId(self):
        return self._id

    def getKsgIdList(self, showAll):
        db = QtGui.qApp.db
        tblActionType = db.table('ActionType')
        tblEventType = db.table('EventType')
        tblRbEventProfile = db.table('rbEventProfile')
        tblQ = tblEventType.innerJoin(
            tblRbEventProfile, tblEventType['eventProfile_id'].eq(tblRbEventProfile['id']))
        code = forceString(db.translate(tblQ, tblEventType['id'], self._eventTypeId, tblRbEventProfile['regionalCode']))
        return getCsgIdListByCond(
            sex=self._clientSex,
            age=self._clientAge,
            mkb=self._MKB,
            mkb2List=self._MKB2List,
            actionTypeCodesList=db.getColumnValues(
                tblActionType,
                column=tblActionType['code'],
                where=[tblActionType['id'].inlist(self._actionTypeIdList)]
            ),
            code=getCSGDepartmentMaskByRegionalCode(code),
            date=self._endDate if self._endDate else self._begDate,
            duration=self._begDate.daysTo(self._endDate) if self._begDate and self._endDate else None,
            weakSelection=showAll
        )

    def setup(
            self, clientSex, clientAge,
            clientId, eventTypeId, contractId, MKB, MKB2List, ksgId, mesCodeTemplate, mesNameTemplate, specialityId,
            endDateForTariff, availableIdList=None, actionTypeIdList=None, checkDate=None,
            begDate=None, endDate=None
    ):
        self._clientSex = clientSex
        self._clientAge = clientAge
        self._clientId = clientId
        self._eventTypeId = eventTypeId
        self._mesCodeTemplate = mesCodeTemplate
        self._mesNameTemplate = mesNameTemplate
        self._contractId = contractId
        self._MKB = MKB
        self._MKB2List = MKB2List
        self._id = ksgId
        self._availableIdList = availableIdList
        self._actionTypeIdList = actionTypeIdList
        self._checkDate = checkDate
        self._endDateForTariff = endDateForTariff
        self._specialityId = specialityId
        self._begDate = begDate
        self._endDate = endDate
        self.on_buttonBox_apply()
        # TODO: Выяснить почему пропадает кнопка Apply c формы, а пока ее возвращаем так
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset)

    def setCheckBoxes(self, dicTag):
        self._dicTag = dicTag
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CSGCBCheckBoxes', {})
        checkList = getPref(preferences, forceString(self._dicTag), {})
        if checkList:
            self.chkShowAll.setChecked(getPrefBool(checkList, 'showAll', False))

    def getCheckBoxes(self):
        if self._dicTag:
            checkList = {}
            setPref(checkList, 'showAll', self.chkShowAll.isChecked())
            preferences = {}
            setPref(preferences, forceString(self._dicTag), checkList)
            setPref(QtGui.qApp.preferences.windowPrefs, 'CSGCBCheckBoxes', preferences)

    @QtCore.pyqtSlot(bool)
    def on_chkShowAll_clicked(self, checked):
        self.chkSex.setEnabled(not checked)
        self.chkAge.setEnabled(not checked)
        self.chkContract.setEnabled(not checked)
        if checked:
            self.chkSex.setChecked(False)
            self.chkAge.setChecked(False)
            self.chkContract.setChecked(False)
        if not checked:
            self.on_buttonBox_reset()
