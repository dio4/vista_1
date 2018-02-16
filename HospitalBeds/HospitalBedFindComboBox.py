#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from HospitalBeds.HospitalBedComboBox import CHospitalBedModel
from HospitalBeds.HospitalBedFindComboBoxPopup import CHospitalBedFindComboBoxPopup

from library.Utils import forceString


class CHospitalBedFindComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                       )

    def __init__(self, parent, domain, plannedEndDate, orgStructureId, sex, bedId):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self.filter = {}
        self.filter['orgStructureId'] = orgStructureId
        self.filter['sex'] = sex
        self.filter['domain'] = domain
        self.filter['plannedEndDate'] = plannedEndDate
        self._model = CHospitalBedModel(self, self.filter)
        self.setModel(self._model)
        self.prefferedWidth = 0
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup = None
        self.code = bedId
        self.date = QtCore.QDate.currentDate()
        self.domain = domain
        self.plannedEndDate = plannedEndDate
        self.orgStructureId = orgStructureId
        self.sex = sex

    def showPopup(self):
        if not self._popup:
            self._popup = CHospitalBedFindComboBoxPopup(self)
            self.connect(self._popup, QtCore.SIGNAL('HospitalBedFindCodeSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.tblHospitalBedFind.setFocus()
        self._popup.setHospitalBedFindCode(self.code)

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def setValue(self, id):
        self.code = id
        self.updateText()

    def value(self):
        return self.code

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            QtGui.QComboBox.setCurrentIndex(self, index.row())

    def updateText(self):
        if self.code:
            self.setEditText(forceString(
                QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', self.code, 'CONCAT(code,\' | \',name)')))
        else:
            self.setEditText('')

    def keyPressEvent(self, evt):
        if evt.key() == QtCore.Qt.Key_Space:
            self.showPopup()
            evt.accept()
        else:
            super(CHospitalBedFindComboBox, self).keyPressEvent(evt)


class CHospitalBedFindComboBoxEditor(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                       )

    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self.filter = {}
        self._model = CHospitalBedModel(self, self.filter)
        self.setModel(self._model)
        self.prefferedWidth = 0
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup = None
        self.code = None
        self.date = QtCore.QDate.currentDate()
        self.domain = None
        self.plannedEndDate = None
        self.orgStructureId = None
        self.sex = None

    def showPopup(self):
        if not self._popup:
            self._popup = CHospitalBedFindComboBoxPopup(self)
            self.connect(self._popup, QtCore.SIGNAL('HospitalBedFindCodeSelected(int)'), self.setValue)
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setHospitalBedFindCode(self.code)

    def setBedId(self, bedId):
        self.code = bedId

    def setDomain(self, domain):
        self.filter['domain'] = domain
        self.domain = domain

    def setPlannedEndDate(self, plannedEndDate):
        self.filter['plannedEndDate'] = plannedEndDate
        self.plannedEndDate = plannedEndDate

    def setOrgStructureId(self, orgStructureId):
        self.filter['orgStructureId'] = orgStructureId
        self.orgStructureId = orgStructureId

    def setSex(self, sex):
        self.filter['sex'] = sex
        self.sex = sex

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def setValue(self, id):
        self.code = id
        self.updateText()

    def value(self):
        return self.code

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            QtGui.QComboBox.setCurrentIndex(self, index.row())

    def updateText(self):
        if self.code:
            self.setEditText(forceString(
                QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', self.code, 'CONCAT(code,\' | \',name)')))
        else:
            self.setEditText('')
