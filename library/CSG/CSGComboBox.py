# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2017 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Events.Utils import getEventProfileId, getEventMesCodeMask, getEventMesNameMask
from library.CSG.CSGComboBoxPopup import CCSGComboBoxPopup
from library.ComboBox.ComboBox import CComboBox
from library.Utils import forceRef, forceString
from library.interchange import getRBComboBoxValue, setRBComboBoxValue


class CCSGComboBox(CComboBox):
    def __init__(self, parent=None):
        CComboBox.__init__(self, CCSGComboBoxPopup, parent)
        self._eventTypeId = None
        self._CSGId = None
        self.connect(self._popup, QtCore.SIGNAL('resetText()'), self.resetText)
        self.connect(self._popup, QtCore.SIGNAL('ItemSelected(int)'), self.on_ItemSelected)

    def fill(self, eventTypeId):
        self.setEventTypeId(eventTypeId)
        self.setEventProfile(getEventProfileId(eventTypeId))
        self.setMESCodeTemplate(getEventMesCodeMask(eventTypeId))
        self.setMESNameTemplate(getEventMesNameMask(eventTypeId))
        self._popup.setCheckBoxes('eventMesPage' + forceString(eventTypeId))

    def setClientInfo(self, clientSex, clientAge, clientId=None):
        self.setClientSex(clientSex)
        self.setClientAge(clientAge)
        self.setClientId(clientId)

    def setRecord(self, record):
        setRBComboBoxValue(self, record, 'MES_id')  # 'KSG_id')
        setRBComboBoxValue(self, record, 'KSG_id')

    def getRecord(self, record):
        getRBComboBoxValue(self, record, 'MES_id')  # 'KSG_id')
        getRBComboBoxValue(self, record, 'KSG_id')

    def resetText(self):
        self.setEditText(self.getText(0))

    def reset(self):
        self._actionTypeIdList = None
        self._MKB = ''
        self._mesCodeTemplate = ''
        self._mesNameTemplate = ''
        self._MKB2List = []
        self._begDate = None
        self._endDate = None
        self.setValue(None)

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
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))

        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setup(
            self._clientSex,
            self._clientAge,
            self._clientId,
            self._eventTypeId,
            self._contractId,
            self._MKB,
            self._MKB2List,
            self._id,
            self._mesCodeTemplate,
            self._mesNameTemplate,
            self._specialityId,
            self._endDateForTariff,
            self._availableIdList,
            self._actionTypeIdList,
            self._checkDate,
            self._begDate,
            self._endDate
        )

    def setDefaultValue(self):
        self._popup.setup(
            self._clientSex,
            self._clientAge,
            self._clientId,
            self._eventTypeId,
            self._contractId,
            self._MKB,
            self._MKB2List,
            self._id,
            self._mesCodeTemplate,
            self._mesNameTemplate,
            self._specialityId,
            self._endDateForTariff,
            actionTypeIdList=self._actionTypeIdList,
            checkDate=self._checkDate,
            begDate=self._begDate,
            endDate=self._endDate
        )
        self._id = self._popup.setValueIfOnly()
        self.updateText()

    def fillById(self, id=None, byList=True):
        if id is None:
            id = self._CSGId
        if id:
            db = QtGui.qApp.db
            tblSPR69 = db.table('mes.SPR69')
            tblMES = db.table('mes.MES')
            table = tblSPR69.innerJoin(tblMES, db.joinAnd([
                tblMES['code'].eq(tblSPR69['KSG']),
                tblMES['begDate'].le(tblSPR69['endDate']),
                tblMES['endDate'].ge(tblSPR69['begDate'])
            ]))
            cond = [
                tblMES['id'].eq(id),
                tblMES['deleted'].eq(0)
            ]
            if byList and self._popup.tableModel.idList():
                cond.append(tblSPR69['id'].inlist(self._popup.tableModel.idList()))

            record = db.getRecordEx(table, ['MES.id as MES_id', 'SPR69.id as SPR69_id'],  cond)
            if record:
                self._CSGId = forceRef(record.value('MES_id'))
                self._id = forceRef(record.value('SPR69_id'))
                self.updateText()

    def getText(self, id):
        if id:
            db = QtGui.qApp.db
            tblSPR69 = db.table('mes.SPR69')
            tblMES = db.table('mes.MES')
            table = tblSPR69.innerJoin(tblMES, db.joinAnd([
                tblMES['code'].eq(tblSPR69['KSG']),
                tblMES['begDate'].le(tblSPR69['endDate']),
                tblMES['endDate'].ge(tblSPR69['begDate'])
            ]))
            record = db.getRecordEx(
                table,
                [
                    'SPR69.KSG',
                    'MES.name',
                    'MES.id as MES_id',
                    'SPR69.id as SPR69_id'
                ],
                [
                    tblSPR69['id'].eq(id),
                    tblMES['deleted'].eq(0)
                ]
            )
            if record:
                self._CSGId = forceRef(record.value('MES_id'))
                self._id = forceRef(record.value('SPR69_id'))
                code = forceString(record.value('KSG'))
                name = forceString(record.value('name'))
                text = code + ' | ' + name
            else:
                text = '{%s}' % id
        else:
            text = ''
        return text

    def on_ItemSelected(self):
        self._id = self._popup.getId()
        self.updateText()

    def value(self):
        if self.currentText():
            return self._CSGId
        else:
            return None

    def setValue(self, CSGId):
        self._CSGId = CSGId
        if self._CSGId and self._id:
            self.updateText()

    @QtCore.pyqtSlot()
    def updateText(self):
        try:
            self.editTextChanged.disconnect(self.showPopup)
        except Exception as e:
            print u'[CSGComboBox Error] %s' % e
        finally:
            self.setEditText(self.getText(self._id))
            self.setToolTip(self.currentText())
            self.editTextChanged.connect(self.showPopup)
            self.lineEdit().setCursorPosition(0)
