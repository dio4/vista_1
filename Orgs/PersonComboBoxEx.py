#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

import library.InDocTable
from PersonComboBox import CPersonComboBox
from Registry.Utils import personIdToText
from library.Utils import forceInt, forceString, toVariant, forceBool, getVal


class CPersonComboBoxEx(CPersonComboBox):
    __pyqtSignals__ = (
        'textChanged(QString)',
        'textEdited(QString)'
    )

    def __init__(self, parent=None):
        self.acceptableSpecialities = []
        CPersonComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self._popup = None
        self.personId = None
        self.date = QtCore.QDate.currentDate()
        self.orgStructureId = None
        self.organisationId = None
        self.activityCode = None
        self.postCode = None
        self.postId = None
        self.specialityCode = None
        self._specialityId = None
        self._specialValueCount = 0
        self.onlyDoctorsIfUnknowPost = False
        self.defaultOrgStructureId = None
        self.isShown = False

    def getActualEmptyRecord(self):
        self._createPopup()
        return self._popup.getActualEmptyRecord()

    def addNotSetValue(self):
        record = self.getActualEmptyRecord()
        record.setValue('code', QtCore.QVariant(u'----'))
        record.setValue('name', QtCore.QVariant(u'Значение не задано'))
        self.setSpecialValues(((-1, record),))

    def setSpecialValues(self, specialValues):
        self._createPopup()
        self._popup.setSpecialValues(specialValues)
        sv = []
        for itemId, record in specialValues:
            sv.append((itemId, forceString(record.value('code')), forceString(record.value('name'))))
        CPersonComboBox.setSpecialValues(self, sv)
        self._specialValueCount = len(sv)

    def _createPopup(self):
        if not self._popup:
            self._popup = CPersonComboBoxExPopup(self)
            self.connect(self._popup, QtCore.SIGNAL('personIdSelected(int)'), self.setValue)
            if self.defaultOrgStructureId:
                self._popup.cmbOrgStructure.setValue(self.defaultOrgStructureId)
            self._popup.setOnlyDoctorsIfUnknowPost(self.onlyDoctorsIfUnknowPost)
            self._popup.initModel(self.personId)

    def showPopup(self):
        self.isShown = True
        self._createPopup()
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self._popup.sizeHint()
        width = max(size.width(), self.width())

        if QtGui.qApp.preferences.decor_crb_width_unlimited:
            below = self.mapToGlobal(self.rect().bottomLeft())
            screen = QtGui.qApp.desktop().availableGeometry(below)
            width = screen.width()

        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.cmbOrganisation.setValue(self._orgId)
        if self.orgStructureId:
            self._popup.cmbOrgStructure.setValue(self.orgStructureId)
        self._popup.cmbPost.setCode(self.postCode)
        self._popup.cmbPost.setValue(self.postId)
        self._popup.cmbActivity.setCode(self.activityCode)
        self._popup.chkIsInvestigator.setChecked(bool(self._isInvestigator))
        self._popup.setAcceptableSpecialities(self.acceptableSpecialities)
        if self.acceptableSpecialities:
            self._popup.cmbSpeciality.setFilter(
                'id IN (%s)' % u', '.join(str(spec) for spec in self.acceptableSpecialities)
            )
        if self._specialityId or self.specialityCode is None:
            self._popup.cmbSpeciality.setValue(self._specialityId)
        else:
            self._popup.cmbSpeciality.setCode(self.specialityCode)
        self._popup.setDate(self.date)
        self._popup.setPersonId(self.personId)
        self._popup.on_buttonBox_apply(self.personId)
        self._popup.show()

    def hidePopup(self):
        super(CPersonComboBoxEx, self).hidePopup()
        self.isShown = False

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.isShown:
                self.hidePopup()
            else:
                self.showPopup()
        else:
            CPersonComboBox.keyPressEvent(self, event)

    def compileFilter(self):
        cond = CPersonComboBox.compileFilter(self)
        if self.acceptableSpecialities:
            specCond = 'speciality_id IN (%s)' % u', '.join(str(spec) for spec in self.acceptableSpecialities)
            return QtGui.qApp.db.joinAnd([cond, specCond])
        else:
            return cond

    def setOrgStructureId(self, orgStructureId):
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'linkingPerson', None)):
            super(CPersonComboBoxEx, self).setOrgStructureId(orgStructureId)
            self.orgStructureId = orgStructureId

    def setDefaultOrgStructureId(self, orgStructureId):
        self.defaultOrgStructureId = orgStructureId

    def setActivityCode(self, code):
        self.activityCode = code

    def setPostCode(self, code):
        self.postCode = code

    def setPostId(self, postId):
        self.postId = postId

    def setOnlyDoctorsIfUnknowPost(self, value):
        self.onlyDoctorsIfUnknowPost = value

    def setSpecialityCode(self, code):
        self.specialityCode = code

    def setSpecialityId(self, itemId):
        if itemId != self._specialityId:
            self._specialityId = itemId
            self.updateFilter()

    def setAcceptableSpecialities(self, specList):
        if specList != self.acceptableSpecialities:
            self.acceptableSpecialities = specList
            self.updateFilter()

    def setDate(self, date):
        self.date = date

    def setValue(self, personId):
        self.personId = personId
        rowIndex = self._model.searchId(self.personId)
        self.setCurrentIndex(rowIndex)
        self.updateText()
        self.lineEdit().setCursorPosition(0)

    def value(self):
        rowIndex = self.currentIndex()
        self.personId = self._model.getId(rowIndex)
        return self.personId

    def createPopupIfNotExist(self):
        if not self._popup:
            self._popup = CPersonComboBoxExPopup(self)
            self.connect(self._popup, QtCore.SIGNAL('personIdSelected(int)'), self.setValue)

    def setSpecialityIndependents(self):
        self.createPopupIfNotExist()
        self._popup.setSpecialityIndependents()

    def updateText(self):
        self._createPopup()
        text = self._popup.getStringValue(self.personId)
        self.setEditText(text if text else u'не задано')

    def lookup(self):
        self._createPopup()
        i, self._searchString = self._specialValuesLookupWraper(
            self._model.searchCodeEx(self._searchString, docIdList=self._popup.idList))
        if i >= 0 and i != self.currentIndex():
            if len(self._searchString) > 0 and (not self.model().getId(i) in self._popup.idList):
                return
            self.setCurrentIndex(i)
            rowIndex = self.currentIndex()
            self.personId = self._model.getId(rowIndex)

    def _specialValuesLookupWraper(self, (index, searchString)):
        if self._addNone:
            return (index + self._specialValueCount, searchString) if index == 0 else (index, searchString)
        return index, searchString


class CPersonFindInDocTableCol(library.InDocTable.CInDocTableCol):
    def __init__(self, title, fieldName, width, tableName='vrbPersonWithSpeciality', **params):
        library.InDocTable.CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.tableName = tableName
        self.filter = params.get('filter', '')
        self.prefferedWidth = params.get('prefferedWidth', None)
        self.orgStructureId = QtGui.qApp.currentOrgStructureId()

    def toString(self, val, record):
        text = personIdToText(val)
        return toVariant(text if text else u'не задано')

    def createEditor(self, parent):
        editor = CPersonComboBoxEx(parent)
        editor.setOrgStructureId(self.orgStructureId)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceInt(value))

    def getEditorData(self, editor):
        return toVariant(editor.value())


from PersonComboBoxExPopup import CPersonComboBoxExPopup
