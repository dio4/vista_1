#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, QtSql

from Registry.Utils import personIdToText
from Ui_PersonComboBoxExPopup import Ui_PersonComboBoxExPopup
from library.TableModel import CDateCol, CRefBookCol, CTableModel, CTextCol, CEnumCol
from library.Utils import forceInt, forceRef, forceStringEx
from library.database import CTableRecordCache


class CPersonComboBoxExPopup(QtGui.QFrame, Ui_PersonComboBoxExPopup):
    __pyqtSignals__ = (
        'personIdSelected(int)',
    )

    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.cPersonComboBoxEx = parent
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.tableModel = CPersonFindTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblPersonFind.setModel(self.tableModel)
        self.tblPersonFind.setSelectionModel(self.tableSelectionModel)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
        # к сожалению в данном случае setDefault обеспечивает рамочку вокруг кнопочки
        # но enter не работает...
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(QtCore.Qt.Key_Return)
        self.date = None
        self.personId = None
        self.onlyDoctorsIfUnknowPost = False
        self.tblPersonFind.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CPersonComboBoxExPopup', {})
        # self.tblPersonFind.loadPreferences(preferences)
        self.cmbOrganisation.setValue(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbPost.setTable('rbPost')
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbActivity.setTable('rbActivity')
        self.cmbPost.setValue(0)
        self.cmbSpeciality.setValue(0)
        self.cmbActivity.setValue(0)
        self.cmbAcademicDegree.setCurrentIndex(0)
        self.chkDeallocatedPerson.setChecked(False)
        self.chkSpeciality.setChecked(True)
        self.cmbSpeciality.setSpecialValues([(-1, '-', u'без специальности')])
        self.chkIsInvestigator.setChecked(False)
        self._parent = parent
        self._acceptableSpecialities = []
        self.idList = []

    def getActualEmptyRecord(self):
        return self.tableModel.getActualEmptyRecord()

    def getStringValue(self, id):
        return self.tableModel.getStringValue(id)

    def addNotSetValue(self):
        self.tableModel.addNotSetValue()

    def setSpecialValues(self, specialValues):
        self.tableModel.setSpecialValues(specialValues)

    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent is not None:
            opt = QtGui.QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox, opt, QtGui.QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos()):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)

    # def closeEvent(self, event):
    #     preferences = self.tblPersonFind.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CPersonComboBoxExPopup', preferences)
    #     QtGui.QFrame.closeEvent(self, event)

    def eventFilter(self, watched, event):
        if watched == self.tblPersonFind:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter, QtCore.Qt.Key_Select]:
                    event.accept()
                    index = self.tblPersonFind.currentIndex()
                    self.tblPersonFind.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                    return True
                elif event.key() == QtCore.Qt.Key_Space:
                    CPersonComboBoxEx.keyPressEvent(self.cPersonComboBoxEx, event)
                    self.close()
                    return True
        return QtGui.QFrame.eventFilter(self, watched, event)

    @staticmethod
    def getOrgStructureIdList(treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        return treeItem.getItemIdList() if treeItem else []

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cPersonComboBoxEx.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbOrganisation_currentIndexChanged(self, index):
        orgId = self.cmbOrganisation.value()
        self.cmbOrgStructure.setEnabled(bool(orgId))
        self.cmbOrgStructure.setOrgId(orgId)

    @QtCore.pyqtSlot(bool)
    def on_chkSpeciality_clicked(self, checked):
        specialityId = self.cmbSpeciality.value()
        if checked:
            self.cmbSpeciality.setSpecialValues([(-1, '-', u'без специальности')])
        else:
            self.cmbSpeciality.setSpecialValues(None)
        self.cmbSpeciality.setValue(specialityId)

    def on_buttonBox_reset(self):
        self.cmbOrganisation.setValue(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbPost.setValue(0)
        self.cmbSpeciality.setValue(0)
        self.cmbActivity.setValue(0)
        self.cmbAcademicDegree.setCurrentIndex(0)
        self.chkDeallocatedPerson.setChecked(False)
        self.chkSpeciality.setChecked(True)
        self.cmbSpeciality.setEnabled(False)
        self.chkIsInvestigator.setChecked(False)
        self.edtFedCode.setText('')

    def setOnlyDoctorsIfUnknowPost(self, value):
        self.onlyDoctorsIfUnknowPost = value

    def on_buttonBox_apply(self, id=None):
        organisationId = forceRef(self.cmbOrganisation.value())
        orgStructureId = forceRef(self.cmbOrgStructure.value())
        postId = forceRef(self.cmbPost.value())
        specialityId = forceRef(self.cmbSpeciality.value()) if self.chkSpeciality.isChecked() else None
        activityId = forceRef(self.cmbActivity.value())
        academicDegree = forceInt(self.cmbAcademicDegree.currentIndex())
        deallocatedPerson = forceRef(self.chkDeallocatedPerson.isChecked())
        isInvestigator = forceRef(self.chkIsInvestigator.isChecked())
        fedCode = forceStringEx(self.edtFedCode.text())

        self.idList = self.getPersonFindIdList(
            organisationId,
            orgStructureId,
            postId,
            specialityId,
            activityId,
            academicDegree,
            deallocatedPerson,
            isInvestigator,
            fedCode
        )
        self.setPersonFindIdList(self.idList, id)

    def initModel(self, id=None):
        self.on_buttonBox_apply(id)

    def setPersonFindIdList(self, idList, posToId):
        if idList:
            self.tblPersonFind.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblPersonFind.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)

    def setSpecialityIndependents(self):
        self.chkSpeciality.setChecked(False)
        self.on_buttonBox_apply()

    def getPersonFindIdList(self, organisationId, orgStructureId, postId, specialityId, activityId, academicDegree,
                            deallocatedPerson, isInvestigator, fedCode):
        db = QtGui.qApp.db
        tableVRBPerson = db.table('vrbPerson')
        tablePerson = db.table('Person')
        tablePerson_Activity = db.table('Person_Activity')
        queryTable = tableVRBPerson

        cond = []
        if organisationId:
            cond.append(tableVRBPerson['org_id'].eq(organisationId))
        if orgStructureId:
            orgStructureIndex = self.cmbOrgStructure._model.index(self.cmbOrgStructure.currentIndex(), 0,
                                                                  self.cmbOrgStructure.rootModelIndex())
            orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
            cond.append(tableVRBPerson['orgStructure_id'].inlist(orgStructureIdList))
        if postId:
            cond.append(tablePerson['post_id'].eq(postId))
        else:
            if self.onlyDoctorsIfUnknowPost:
                cond.append(
                    'EXISTS (SELECT rbPost.`id` FROM rbPost '
                    'WHERE Person.`post_id`=rbPost.`id` AND rbPost.`code` REGEXP \'^[1-3]+\')'
                )
        if self.chkSpeciality.isChecked():
            if specialityId == -1:
                cond.append(tableVRBPerson['speciality_id'].isNull())
            elif specialityId is None:
                cond.append(tableVRBPerson['speciality_id'].isNotNull())
            else:
                cond.append(tableVRBPerson['speciality_id'].eq(specialityId))
        if self._acceptableSpecialities:
            cond.append(tableVRBPerson['speciality_id'].inlist(self._acceptableSpecialities))
        if activityId:
            queryTable = queryTable.innerJoin(tablePerson_Activity,
                                              tableVRBPerson['id'].eq(tablePerson_Activity['master_id']))
            cond.append(tablePerson_Activity['activity_id'].eq(activityId))
            cond.append(tablePerson_Activity['deleted'].eq(0))
        if academicDegree:
            cond.append(tablePerson['academicDegree'].eq(academicDegree))
        if not deallocatedPerson:
            cond.append(db.joinOr([tableVRBPerson['retireDate'].isNull(),
                                   tablePerson['retireDate'].lt(u'ADDDATE(Person.retireDate, 15)')]))
        if academicDegree or postId or not deallocatedPerson or self.onlyDoctorsIfUnknowPost:
            cond.append(tablePerson['deleted'].eq(0))
            queryTable = queryTable.innerJoin(tablePerson, tableVRBPerson['id'].eq(tablePerson['id']))
        if isInvestigator:
            cond.append(tablePerson['isInvestigator'].eq(isInvestigator))
        if fedCode:
            cond.append(tablePerson['federalCode'].like(fedCode + '%'))
        idList = db.getDistinctIdList(queryTable, tableVRBPerson['id'].name(),
                                      where=cond,
                                      order=u'vrbPerson.name ASC',
                                      limit=1000)
        fakeIdList = self.tableModel.getSpecialValuesKeys()
        if fakeIdList:
            return fakeIdList + idList
        return idList

    def setDate(self, date):
        self.tableModel.date = date

    def setPersonId(self, personId):
        self.personId = personId
        self.on_buttonBox_apply(self.personId)

    def selectPersonId(self, personId):
        self.personId = personId
        self.emit(QtCore.SIGNAL('personIdSelected(int)'), personId)
        self.close()

    def getCurrentPersonId(self):
        return self.tblPersonFind.currentItemId()

    def setAcceptableSpecialities(self, specs):
        self._acceptableSpecialities = specs
        self.on_buttonBox_apply(self.personId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblPersonFind_doubleClicked(self, index):
        if index.isValid():
            if (QtCore.Qt.ItemIsEnabled & self.tableModel.flags(index)):
                personId = self.getCurrentPersonId()
                self.selectPersonId(personId)


class CPersonFindTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(
            self, parent,
            cols=[  # При добавлении, перемещении столбцов необходимо обновить getStringValue
                CTextCol(u'Код', ['code'], 5),
                CTextCol(u'ФИО', ['name'], 15),
                CRefBookCol(u'Подразделение', ['orgStructure_id'], 'OrgStructure', 10),
                CTextCol(u'Федеральный код', ['federalCode'], 15),
                CRefBookCol(u'Должность', ['post_id'], 'rbPost', 15),
                CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 10),
                CDateCol(u'Дата запрещения', ['retireDate'], 10),
                CEnumCol(u'Ученая степень', ['academicDegree'], [u'', u'к.м.н', u'д.м.н'], 10)
            ]
        )
        self._showAcademicDegree = forceStringEx(
            QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')) == u'онко'
        self._parent = parent
        self._specialValues = []
        self.date = QtCore.QDate.currentDate()
        self.setTable('vrbPerson')

    def flags(self, index):
        # row = index.row()
        # record = self.getRecordByRow(row)
        enabled = True
        if enabled:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsSelectable

    def getActualEmptyRecord(self):
        record = QtSql.QSqlRecord()
        record.append(QtSql.QSqlField('code', QtCore.QVariant.String))
        record.append(QtSql.QSqlField('name', QtCore.QVariant.String))
        record.append(QtSql.QSqlField('orgStructure_id', QtCore.QVariant.Int))
        record.append(QtSql.QSqlField('federalCode', QtCore.QVariant.String))
        record.append(QtSql.QSqlField('post_id', QtCore.QVariant.Int))
        record.append(QtSql.QSqlField('speciality_id', QtCore.QVariant.Int))
        record.append(QtSql.QSqlField('retireDate', QtCore.QVariant.Date))
        return record

    def getStringValue(self, id):
        row = self._idList.index(id) if id in self._idList else None
        if not row is None:
            name = forceStringEx(self.data(self.index(row, 1)))
            speciality = forceStringEx(self.data(self.index(row, 5)))
            degree = forceStringEx(self.data(self.index(row, 7)))
            values = [name, speciality]
            if degree and self._showAcademicDegree:
                values.append(degree)
            return ', '.join(values)
        return personIdToText(id, self._showAcademicDegree)

    def setSpecialValues(self, specialValues):
        if self._specialValues != specialValues:
            self._specialValues = specialValues
            self.setTable(specialValues)

    def getSpecialValuesKeys(self):
        return [key for key, item in self._specialValues]

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableVRBPerson = db.table('vrbPerson')
        tablePerson = db.table('Person')
        cols = [
            tableVRBPerson['code'],
            tableVRBPerson['name'],
            tableVRBPerson['orgStructure_id'],
            tablePerson['federalCode'],
            tablePerson['post_id'],
            tableVRBPerson['speciality_id'],
            tableVRBPerson['retireDate'],
            tablePerson['academicDegree']
        ]
        loadFields = [u'DISTINCT ' + u', '.join(col.name() for col in cols)]
        table = tableVRBPerson.innerJoin(tablePerson, tablePerson['id'].eq(tableVRBPerson['id']))
        self._table = table
        self._recordsCache = CTableRecordCache(
            db,
            self._table,
            loadFields,
            recordCacheCapacity,
            fakeValues=self._specialValues
        )


from PersonComboBoxEx import CPersonComboBoxEx
