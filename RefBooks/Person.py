# -*- coding: utf-8 -*-

import hashlib
import urllib2
import xml.etree.ElementTree
from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.Utils import CAttachSentToTFOMS
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from Orgs.OrgComboBox import COrgInDocTableCol
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import getOrgStructureDescendants
from RefBooks.EnumFields import PersonAcademicDegree, PersonEducationType, PersonEmploymentType, PersonIsReservist, \
    PersonMaritalStatus, PersonOccupationType, \
    PersonOrderType, PersonQALevel, PersonRegType
from RefBooks.Tables import rbCode
from Registry.ClientEditDialog import COrgStructureInDocTableCol
from Registry.PrerecordQuotaModel import CPrerecordQuotaModel
from Registry.Utils import getAddress, getAddressId
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Timeline.TimeTable import CPersonTimeTableModel
from Ui_PersonEditor import Ui_ItemEditorDialog
from Ui_PersonsListDialog import Ui_PersonsListDialog
from Users.Login import createLogin
from Users.Rights import urCopyPerson
from library.InDocTable import CBoolInDocTableCol, CDateInDocTableCol, CEnumInDocTableCol, CInDocTableCol, \
    CInDocTableModel, CIntInDocTableCol, CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialog
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, getPrintAction
from library.TableModel import CDesignationCol, CRefBookCol, CTextCol
from library.Utils import AnyRequest, agreeNumberAndWord, checkExistFieldWithMessage, forceBool, forceDate, forceInt, \
    forceRef, forceString, forceStringEx, \
    getVal, nameCase, toVariant, unformatSNILS
from library.crbcombobox import CRBComboBox
from library.interchange import getCheckBoxValue, getComboBoxValue, getDateEditValue, getLineEditValue, \
    getRBComboBoxValue, getSpinBoxValue, getTextEditValue, getWidgetValue, \
    setCheckBoxValue, setComboBoxValue, setDateEditValue, setLineEditValue, setRBComboBoxValue, setSpinBoxValue, \
    setTextEditValue, setWidgetValue


class CPersonList(CItemsListDialog, Ui_PersonsListDialog):
    setupUi = Ui_PersonsListDialog.setupUi
    retranslateUi = Ui_PersonsListDialog.retranslateUi

    NoSpeciality = 0
    AnySpeciality = -1

    NoActivity = 0
    AnyActivity = -1

    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 6),
            CTextCol(u'Фамилия', ['lastName'], 20),
            CTextCol(u'Имя', ['firstName'], 20),
            CTextCol(u'Отчество', ['patrName'], 20),
            CTextCol(u'Федеральный код', ['federalCode'], 10),
            CDesignationCol(u'ЛПУ', ['org_id'], ('Organisation', 'infisCode'), 5),
            CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'name'), 5),
            CRefBookCol(u'Должность', ['post_id'], 'rbPost', 20),
            CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 10),
        ], 'Person', ['lastName', 'firstName', 'patrName'])
        self.setWindowTitleEx(u'Сотрудники')

        self.cmbUserRightsProfile.setTable('rbUserProfile')
        self.cmbUserRightsProfile.setValue(None)

        self.cmbSpeciality.setTable('rbSpeciality',
                                    addNone=False,
                                    filter='rbSpeciality.id IN (SELECT DISTINCT p.speciality_id FROM Person p WHERE p.deleted = 0 GROUP BY p.speciality_id)',
                                    order='name',
                                    specialValues=[(self.NoSpeciality, u'-', u'Без специальности'),
                                                   (self.AnySpeciality, u'-', u'Любая специальность')])
        self.cmbSpeciality.setShowFields(CRBComboBox.showName)
        self.cmbSpeciality.setValue(self.NoSpeciality)

        self.cmbActivity.setTable('rbActivity',
                                  addNone=False,
                                  specialValues=[(self.NoActivity, u'-', u'Без вида деятельности'),
                                                 (self.AnyActivity, u'-', u'Любой вид деятельности')])
        self.cmbActivity.setValue(self.NoActivity)

        self.cmbOrg.setFilter('id IN (SELECT DISTINCT org_id FROM Person WHERE deleted = 0)')
        self.cmbOrg.setValue(None)

        self.cmbAcademicDegree.setEnum(PersonAcademicDegree)
        self.cmbEmploymentType.setEnum(PersonEmploymentType)
        self.cmbIsReservist.setEnum(PersonIsReservist)
        self.cmbMaritalStatus.setEnum(PersonMaritalStatus)
        self.cmbOccupationType.setEnum(PersonOccupationType)
        self.cmbRegistryType.setEnum(PersonRegType)
        self.cmbEducationType.setEnum(PersonEducationType)
        self.cmbCitizenship.setTable('rbCitizenship')
        self.cmbCategory.setTable('rbPersonCategory')

        self.actReports = getPrintAction(self, 'person', u'Формы')
        self.actReports.setObjectName('actReports')
        self.actPersonList = QtGui.QAction(u'Список сотрудников', self)
        self.actPersonList.setObjectName('actPersonList')
        self.mnuPrint = QtGui.QMenu(self)
        self.mnuPrint.setObjectName('mnuPrint')
        self.actCopy = QtGui.QAction(u'Дублировать запись', self)
        self.actCopy.setObjectName('actCopy')
        self.mnuPrint.addAction(self.actReports)
        self.mnuPrint.addSeparator()
        self.mnuPrint.addAction(self.actPersonList)
        self.btnPrint.setMenu(self.mnuPrint)
        if QtGui.qApp.userHasRight(urCopyPerson):
            self.tblItems.createPopupMenu([self.actCopy])

        QtCore.QObject.connect(self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)
        QtCore.QObject.connect(self.actPersonList, QtCore.SIGNAL('triggered()'), self.on_actPersonList_triggered)
        QtCore.QObject.connect(self.actReports, QtCore.SIGNAL('printByTemplate(int)'),
                               self.on_actReports_printByTemplate)
        QtCore.QObject.connect(self.actCopy, QtCore.SIGNAL('triggered()'), self.on_actCopy_triggered)
        QtCore.QObject.connect(self.tblItems.selectionModel(),
                               QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                               self.on_tblItems_selectionChanged)

        checkBoxes = [
            self.chkOnlyOwn,
            self.chkOnlyWorking,
            self.chkOnlyResearcher,

            self.chkCode,
            self.chkLastName,
            self.chkFirstName,
            self.chkPatrName,
            self.chkStrPodr,
            self.chkSpec,
            self.chkActivity,
            self.chkOccupationType,
            self.chkUserRightsProfile,
            self.chkLPU,
            self.chkIsReservist,
            self.chkEmploymentType,
            self.chkAcademicDegree,
            self.chkFedCode,

            self.chkRegistryType,
            self.chkMaritalStatus,
            self.chkCitizenship,
            self.chkSex,
            self.chkBirthDate,

            self.chkEducationType,
            self.chkCategory
        ]
        for checkBox in checkBoxes:
            checkBox.stateChanged.connect(self.updatePersonList)

        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.btnSync.setVisible(QtGui.qApp.isKrasnodarRegion())

    def getItemEditor(self):
        return CRBPersonEditor(self)

    def select(self, props):
        db = QtGui.qApp.db
        table = self.model.table()
        queryTable = table

        cond = [
            table['deleted'].eq(0)
        ]

        onlyOwn = self.chkOnlyOwn.isChecked()
        if onlyOwn:
            cond.append(table['org_id'].eq(QtGui.qApp.currentOrgId()))

        onlyWorking = self.chkOnlyWorking.isChecked()
        if onlyWorking:
            cond.append(table['retireDate'].isNull())

        onlyResearcher = self.chkOnlyResearcher.isChecked()
        if onlyResearcher:
            cond.append(table['isInvestigator'].eq(1))

        if self.chkStrPodr.isChecked():
            orgStructure_id = self.boxStrPodr.value()
            if orgStructure_id:
                orgStructureIdList = getOrgStructureDescendants(orgStructure_id)
                cond.append(table['orgStructure_id'].inlist(orgStructureIdList))

        if self.chkSpec.isChecked():
            specialityId = self.cmbSpeciality.value()
            if specialityId == self.NoSpeciality:
                cond.append(table['speciality_id'].isNull())
            elif specialityId == self.AnySpeciality:
                cond.append(table['speciality_id'].isNotNull())
            elif specialityId is not None:
                cond.append(table['speciality_id'].eq(specialityId))

        if self.chkActivity.isChecked():
            tablePersonActivity = db.table('Person_Activity')
            activityCond = [
                tablePersonActivity['master_id'].eq(table['id']),
                tablePersonActivity['deleted'].eq(0)
            ]
            activityId = self.cmbActivity.value()
            if activityId == self.NoActivity:
                cond.append(db.notExistsStmt(tablePersonActivity, activityCond))
            elif activityId == self.AnyActivity:
                cond.append(
                    db.existsStmt(tablePersonActivity, activityCond + [tablePersonActivity['activity_id'].isNotNull()]))
            elif activityId is not None:
                cond.append(db.existsStmt(tablePersonActivity,
                                          activityCond + [tablePersonActivity['activity_id'].eq(activityId)]))

        if self.chkLPU.isChecked():
            orgId = self.cmbOrg.value()
            if orgId is not None:
                cond.append(table['org_id'].eq(orgId))

        if self.chkUserRightsProfile.isChecked():
            userProfileId = self.cmbUserRightsProfile.value()
            if userProfileId:
                tablePersonUserProfile = QtGui.qApp.db.table('Person_UserProfile')
                queryTable = queryTable.innerJoin(tablePersonUserProfile,
                                                  [tablePersonUserProfile['person_id'].eq(table['id']),
                                                   tablePersonUserProfile['userProfile_id'].eq(userProfileId)])
        if self.chkOccupationType.isChecked():
            occupationType = self.cmbOccupationType.value()
            if occupationType:
                cond.append(table['occupationType'].eq(occupationType))

        if self.chkRegistryType.isChecked():
            regType = self.cmbRegistryType.value()
            if regType:
                cond.append(table['regType'].eq(regType))

        if self.chkMaritalStatus.isChecked():
            maritalStatus = self.cmbMaritalStatus.value()
            if maritalStatus:
                cond.append(table['maritalStatus'].eq(maritalStatus))

        if self.chkIsReservist.isChecked():
            isReservist = self.cmbIsReservist.value()
            if isReservist:
                cond.append(table['isReservist'].eq(isReservist))

        if self.chkEmploymentType.isChecked():
            employmentType = self.cmbEmploymentType.value()
            if employmentType:
                cond.append(table['employmentType'].eq(employmentType))

        if self.chkCitizenship.isChecked():
            index = self.cmbCitizenship.value()
            if index:
                cond.append(table['citizenship_id'].eq(index))

        if self.chkEducationType.isChecked() or self.chkCategory.isChecked():
            db = QtGui.qApp.db
            tablePersonEducation = db.table('Person_Education')
            queryTable = queryTable.innerJoin(tablePersonEducation, table['id'].eq(tablePersonEducation['master_id']))
            if self.chkEducationType.isChecked():
                educationType = self.cmbEducationType.value()
                if educationType:
                    cond.append(tablePersonEducation['educationType'].eq(educationType))
            if self.chkCategory.isChecked():
                index = self.cmbCategory.value()
                if index:
                    cond.append(tablePersonEducation['category_id'].eq(index))

        if self.chkAcademicDegree.isChecked():
            degree = self.cmbAcademicDegree.value()
            if degree is not None:
                cond.append(table['academicDegree'].eq(degree))

        if self.chkLastName.isChecked():
            name = self.edtLastName.text()
            if name:
                cond.append(table['lastName'].like(forceString(name) + '%'))

        if self.chkFirstName.isChecked():
            name = self.edtFirstName.text()
            if name:
                cond.append(table['firstName'].like(forceString(name) + '%'))

        if self.chkPatrName.isChecked():
            name = self.edtPatrName.text()
            if name:
                cond.append(table['patrName'].like(forceString(name) + '%'))

        if self.chkSex.isChecked():
            index = self.cmbSex.currentIndex()
            if index:
                cond.append(table['sex'].eq(index))

        if self.chkBirthDate.isChecked():
            date = self.edtBirthDate.date()
            if date:
                cond.append(table['birthDate'].eq(date))

        if self.chkCode.isChecked():
            code = self.edtCode.text()
            if code:
                cond.append(table['code'].like(forceString(code) + '%'))

        if self.chkFedCode.isChecked():
            fedCode = self.edtFedCode.text()
            if fedCode:
                cond.append(table['federalCode'].like(forceString(fedCode) + '%'))

        return QtGui.qApp.db.getIdList(queryTable, table['id'], where=cond, order=self.order)

    def updatePersonList(self):
        self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_boxStrPodr_currentIndexChanged(self, text):
        if self.chkStrPodr.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbUserRightsProfile_currentIndexChanged(self, text):
        if self.chkUserRightsProfile.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        if self.chkSpec.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbActivity_currentIndexChanged(self, text):
        if self.chkActivity.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbOrg_currentIndexChanged(self, index):
        if self.chkLPU.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbOccupationType_currentIndexChanged(self, text):
        if self.chkOccupationType.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbRegistryType_currentIndexChanged(self, text):
        if self.chkRegistryType.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbMaritalStatus_currentIndexChanged(self, text):
        if self.chkMaritalStatus.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbIsReservist_currentIndexChanged(self, text):
        if self.chkIsReservist.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbEmploymentType_currentIndexChanged(self, text):
        if self.chkEmploymentType.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbCitizenship_currentIndexChanged(self, text):
        if self.chkCitizenship.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbEducationType_currentIndexChanged(self, text):
        if self.chkEducationType.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbCategory_currentIndexChanged(self, text):
        if self.chkCategory.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbAcademicDegree_currentIndexChanged(self, text):
        if self.chkAcademicDegree.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtLastName_textEdited(self, text):
        if self.chkLastName.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFirstName_textEdited(self, text):
        if self.chkFirstName.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtPatrName_textEdited(self, text):
        if self.chkPatrName.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(int)
    def on_cmbSex_currentIndexChanged(self, text):
        if self.chkSex.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBirthDate_dateChanged(self, text):
        if self.chkBirthDate.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textEdited(self, text):
        if self.chkCode.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        pass

    @QtCore.pyqtSlot(int)
    def on_actReports_printByTemplate(self, templateId):
        allPersonId = self.tblItems.selectedItemIdList()
        personInfoList = []
        for personId in allPersonId:
            if personId:
                context = CInfoContext()
                personInfo = context.getInstance(CPersonInfo, personId)
                personInfoList.append(personInfo)
        QtGui.qApp.call(self, applyTemplate, (self, templateId, {'Person': personInfoList}))

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_tblItems_selectionChanged(self, selected, deselected):
        allPersonId = self.tblItems.selectedItemIdList()
        if len(allPersonId) > 1:
            self.btnEdit.setEnabled(False)
            self.btnNew.setEnabled(False)
        else:
            self.btnEdit.setEnabled(True)
            self.btnNew.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFedCode_textEdited(self, text):
        if self.chkFedCode.isChecked():
            self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot()
    def on_actPersonList_triggered(self):
        tbl = self.tblItems
        model = tbl.model()
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сотрудники\n')
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        if self.chkOnlyOwn.isChecked():
            cursor.insertText(u'Только свои\n')
        if self.chkOnlyWorking.isChecked():
            cursor.insertText(u'Только работающие\n')
        if self.chkOnlyResearcher.isChecked():
            cursor.insertText(u'Только главные исследователи\n')
        if self.chkStrPodr.isChecked():
            cursor.insertText(u'Структурное подразделение: %s\n' % self.boxStrPodr.currentText())
        if self.chkSpec.isChecked():
            cursor.insertText(u'Специальность: %s\n' % self.cmbSpeciality.currentText())
        if self.chkActivity.isChecked():
            cursor.insertText(u'Вид деятельности: %s\n' % self.cmbActivity.currentText())
        if self.chkLPU.isChecked():
            cursor.insertText(u'Внешнее ЛПУ: %s\n' % self.cmbOrg.currentText())
        if self.chkUserRightsProfile.isChecked():
            cursor.insertText(u'Профиль прав: %s\n' % self.cmbUserRightsProfile.currentText())
        if self.chkOccupationType.isChecked():
            cursor.insertText(u'Тип занятия должности: %s\n' % self.cmbOccupationType.currentText())
        if self.chkRegistryType.isChecked():
            cursor.insertText(u'Тип регистрации: %s\n' % self.cmbRegistryType.currentText())
        if self.chkMaritalStatus.isChecked():
            cursor.insertText(u'Семейное положение: %s\n' % self.cmbMaritalStatus.currentText())
        if self.chkIsReservist.isChecked():
            cursor.insertText(u'Отношение к военной службе: %s\n' % self.cmbIsReservist.currentText())
        if self.chkEmploymentType.isChecked():
            cursor.insertText(u'Режим работы: %s\n' % self.cmbEmploymentType.currentText())
        if self.chkCitizenship.isChecked():
            cursor.insertText(u'Гражданство: %s\n' % self.cmbCitizenship.currentText())
        if self.chkEducationType.isChecked():
            cursor.insertText(u'Тип образования: %s\n' % self.cmbEducationType.currentText())
        if self.chkCategory.isChecked():
            cursor.insertText(u'Категория: %s\n' % self.cmbCategory.currentText())
        if self.chkAcademicDegree.isChecked():
            cursor.insertText(u'Учёная степень: %s\n' % self.cmbAcademicDegree.currentText())
        if self.chkLastName.isChecked():
            cursor.insertText(u'Фамилия: %s\n' % self.edtLastName.text())
        if self.chkFirstName.isChecked():
            cursor.insertText(u'Имя: %s\n' % self.edtFirstName.text())
        if self.chkPatrName.isChecked():
            cursor.insertText(u'Отчество: %s\n' % self.edtPatrName.text())
        if self.chkSex.isChecked():
            cursor.insertText(u'Пол: %s\n' % self.cmbSex.currentText())
        if self.chkBirthDate.isChecked():
            cursor.insertText(u'Дата рождения: %s\n' % self.edtBirthDate.text())
        if self.chkCode.isChecked():
            cursor.insertText(u'Код: %s\n' % self.edtCode.text())
        cursor.insertBlock()

        cols = model.cols()
        colWidths = [tbl.columnWidth(i) for i in xrange(len(cols))]
        colWidths.insert(0, 10)
        totalWidth = sum(colWidths)
        tableColumns = []
        for iCol, colWidth in enumerate(colWidths):
            widthInPercents = str(max(1, colWidth * 90 / totalWidth)) + '%'
            if iCol == 0:
                tableColumns.append((widthInPercents, [u'№'], CReportBase.AlignRight))
            else:
                col = cols[iCol - 1]
                colAlingment = QtCore.Qt.AlignHorizontal_Mask & forceInt(col.alignment())
                blockFormat = QtGui.QTextBlockFormat()
                blockFormat.setAlignment(QtCore.Qt.AlignmentFlag(colAlingment))
                tableColumns.append((widthInPercents, [forceString(col.title())], blockFormat))

        table = createTable(cursor, tableColumns)
        for iModelRow in xrange(model.rowCount()):
            iTableRow = table.addRow()
            table.setText(iTableRow, 0, iModelRow + 1)
            for iModelCol in xrange(len(cols)):
                index = model.createIndex(iModelRow, iModelCol)
                text = forceString(model.data(index))
                table.setText(iTableRow, iModelCol + 1, text)

        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()

    @QtCore.pyqtSlot()
    def on_actCopy_triggered(self):
        personId = self.currentItemId()
        model = self.tblItems.model()
        QtGui.qApp.db.query(u'''CREATE TEMPORARY TABLE tempTable AS SELECT * FROM `Person` WHERE `id` =  %s;
            UPDATE tempTable SET `id` = NULL, lastName = CONCAT_WS(' ', tempTable.lastName, '(копия)');
            INSERT INTO `Person` SELECT * FROM tempTable;
            DROP TABLE tempTable;''' % personId)
        self.renewListAndSetTo()

    def setSort(self, col):
        name = self.model.cols()[col].fields()[0]
        self.order = name
        header = self.tblItems.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)
        self.renewListAndSetTo(self.currentItemId())

    @QtCore.pyqtSlot()
    def on_btnSync_clicked(self):
        login = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'personSyncLogin', ''))
        if not login:
            self.checkInputMessage(u'логин на вкладке "Синхронизация сотрудников" в Умолчаниях', False, self)
            return
        password = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'personSyncPassword', ''))
        if not password:
            self.checkInputMessage(u'пароль на вкладке "Синхронизация сотрудников" в Умолчаниях', False, self)
            return
        url = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'personSyncUrl', ''))
        if not url:
            self.checkInputMessage(u'адрес на вкладке "Синхронизация сотрудников" в Умолчаниях', False, self)
            return
        service = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'personSyncService', 0))
        if service == '0':
            sender = ParusExchange(login, password, url)
            data = QtGui.qApp.callWithWaitCursor(self, sender.findAll)
            if data is None:
                QtGui.QMessageBox.warning(None,
                                          u'Ошибка!',
                                          u'Данные не были скачаны.\n',
                                          QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            else:
                QtGui.qApp.callWithWaitCursor(self, sender.createNewPersons, data)
        elif service == '1':
            from Exchange.ImportDKKBPersons import ImportDKKBPersonsDialog
            dlg = ImportDKKBPersonsDialog(login, password, url, self)
            dlg.exec_()


class ParusExchange:
    def __init__(self, login, password, url='https://katastrofa:14577/ard', db=None):
        self.login = login
        self.password = password
        self.url = url
        self.headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'urn:ard-search-helper/ISearchHelperService/Find'
        }
        if db is None:
            self.db = QtGui.qApp.db

    def sendData(self, url, data):
        try:
            req = AnyRequest(url, data=data.encode('utf-8'), headers=self.headers, method='POST')
            return '\n'.join(urllib2.urlopen(req).readlines())
        except urllib2.HTTPError as e:
            QtGui.QMessageBox.warning(None,
                                      u'Ошибка!',
                                      u'Ошибка HTTP ' + str(e.code) + ' ' + str(url) + '\n',
                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return None
        except urllib2.URLError, e:
            QtGui.QMessageBox.warning(None,
                                      u'Ошибка!',
                                      u'Ошибка ' + str(e.reason) + ' ' + str(url) + '\n',
                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return None
        except Exception as e:
            QtGui.QMessageBox.warning(None,
                                      u'Ошибка!',
                                      u'Прозошла ошибка при скачивании данных.\n',
                                      QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return None

    def findAll(self):
        data = u'''<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:ard-search-helper"><x:Header/><x:Body><urn:Find><urn:query/><urn:userName>%s</urn:userName><urn:password>%s</urn:password></urn:Find></x:Body></x:Envelope>''' % (
        self.login, self.password)
        try:
            resp = self.sendData(self.url, data)
            return resp
        except:
            pass

    def notExistingPerson(self, snils):
        db = self.db
        if snils is None:
            return False
        table = db.table('Person')
        return db.getRecordEx(table, '*', table['SNILS'].eq(unformatSNILS(snils))) is None

    def createNewPersons(self, data):
        db = self.db
        root = xml.etree.ElementTree.fromstring(data)
        root = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        root = root.find('{urn:ard-search-helper}FindResponse')
        root = root.find('{urn:ard-search-helper}FindResult')
        table = db.table('Person')
        added = 0
        for entry in root:
            snils = entry.find('{urn:ard-search-helper}Snils').text
            if self.notExistingPerson(snils):
                record = table.newRecord()
                record.setValue('lastName', toVariant(entry.find('{urn:ard-search-helper}Surname').text))
                record.setValue('firstName', toVariant(entry.find('{urn:ard-search-helper}Name').text))
                record.setValue('patrName', toVariant(entry.find('{urn:ard-search-helper}MiddleName').text))
                record.setValue('SNILS', toVariant(unformatSNILS(snils)))
                record.setValue('birthDate', toVariant(entry.find('{urn:ard-search-helper}DateBirth').text))
                record.setValue('org_id', toVariant(QtGui.qApp.currentOrgId()))
                record.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                db.insertOrUpdate(table, record)
                added += 1
        QtGui.QMessageBox.warning(None,
                                  u'Завершено',
                                  u'Синхронизация завершена. Добавлено ' + str(added) + '\n',
                                  QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)


class CRBPersonEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog, CVisibleControlMixin):
    prevAddress = None

    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Person')

        self.isUserDeleted = False
        self.oldUsername = u''
        self.newUsername = u''
        self.hashedPassword = u''

        self.__regAddressRecord = None
        self.__regAddress = None
        self.__locAddressRecord = None
        self.__locAddress = None
        self.__documentRecord = None

        self.addModels('EducationDocs', CEducationDocsModel(self))
        self.addModels('Awards', CAwardsModel(self))
        self.addModels('OrderDocs', COrderDocsModel(self))
        self.addModels('PersonActivity', CPersonActivityModel(self))
        self.addModels('PersonJobType', CPersonJobTypeModel(self))
        self.addModels('TimeTable', CPersonTimeTableModel(self))
        self.addModels('PrerecordQuotas', CPrerecordQuotaModel(self))
        self.addModels('UserProfile', CPersonUserProfileModel(self))
        self.addModels('PersonAttach', CPersonAttachModel(self))

        self.setupUi(self)

        # Перенос панели кнопок "Ок", "Отмена" и т.п. в верх окна, если указана соответствующая глобальная настройка
        buttonBoxAtTop = QtGui.qApp.isButtonBoxAtTopWindow()
        mainLayout = self.layout()
        buttonBoxIndex = mainLayout.indexOf(self.buttonBox)
        mainLayout.insertWidget(0 if buttonBoxAtTop else -1, mainLayout.takeAt(buttonBoxIndex).widget())

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Сотрудник')

        self.edtBirthDate.canBeEmpty(True)
        self.edtBirthDate.setDate(QtCore.QDate())
        self.edtBirthDate.setHighlightRedDate(False)
        self.cmbPost.setTable('rbPost')
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbTariffCategory.setTable('rbTariffCategory')
        self.cmbFinance.setTable('rbFinance')
        self.cmbNationality.setTable('rbCitizenship')
        self.cmbOrg.setValue(QtGui.qApp.currentOrgId())
        self.edtRetireDate.setDate(QtCore.QDate())
        self.chkChangePassword.setChecked(False)
        self.edtPassword.setEnabled(False)
        self.btnCopyPrevAddress.setEnabled(bool(CRBPersonEditor.prevAddress))
        self.cmbDocType.setTable('rbDocumentType', True,
                                 'group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'1\')')
        self.cmbAcademicDegree.setEnum(PersonAcademicDegree)
        self.cmbEmploymentType.setEnum(PersonEmploymentType)
        self.cmbIsReservist.setEnum(PersonIsReservist)
        self.cmbMaritalStatus.setEnum(PersonMaritalStatus)
        self.cmbOccupationType.setEnum(PersonOccupationType)
        self.cmbRegType.setEnum(PersonRegType)
        self.cmbQALevel.setEnum(PersonQALevel)

        self.setModels(self.tblEducationDocs, self.modelEducationDocs, self.selectionModelEducationDocs)
        self.setModels(self.tblAwards, self.modelAwards, self.selectionModelAwards)
        self.setModels(self.tblOrderDocs, self.modelOrderDocs, self.selectionModelOrderDocs)
        self.setModels(self.tblPersonActivity, self.modelPersonActivity, self.selectionModelPersonActivity)
        self.setModels(self.tblPersonJobType, self.modelPersonJobType, self.selectionModelPersonJobType)
        self.setModels(self.tblTimeTable, self.modelTimeTable, self.selectionModelTimeTable)
        self.setModels(self.tblPrerecordQuota, self.modelPrerecordQuotas, self.selectionModelPrerecordQuotas)
        self.setModels(self.tblUserProfile, self.modelUserProfile, self.selectionModelUserProfile)
        self.setModels(self.tblPersonAttach, self.modelPersonAttach, self.selectionModelPersonAttach)

        self.tblEducationDocs.addPopupDelRow()
        self.tblOrderDocs.addPopupDelRow()
        self.tblPersonActivity.addPopupDelRow()
        self.tblPersonJobType.addPopupDelRow()
        self.tblAwards.addPopupDelRow()
        self.tblUserProfile.addPopupDelRow()

        self.setupDirtyCather()

        self.on_cmbTypeTimeLinePerson_currentIndexChanged(0)
        self._invisibleObjectsNameList = self.reduceNames(
            QtGui.qApp.userInfo.hiddenObjectsNameList([self.moduleName()])) \
            if QtGui.qApp.userInfo else []

        self.updateVisibleState(self, self._invisibleObjectsNameList)

    @staticmethod
    def moduleName():
        return u'CRBPersonEditor'

    @staticmethod
    def moduleTitle():
        return u'Сотрудники'

    @classmethod
    def hiddableChildren(cls):
        # TODO: atronah: решить проблему с игнором смены имен в файле интерфейса
        # один из вариантов решения: парсить ui-файл
        nameList = [(u'tabGeneral', u'вкладка "Общие"'),
                    (u'tabPersonal', u'вкладка "Личные"'),
                    (u'tabQualification', u'вкладка "Квалификация"'),
                    (u'tabAwards', u'вкладка "Награды"'),
                    (u'tabStaffMovements', u'вкладка "Кадровые перемещния"'),
                    (u'tabActivity', u'вкладка "Вид деятельности"'),
                    (u'tabTimeLine', u'вкладка "График"'),
                    (u'tabQuota', u'вкладка "Квота"'),
                    (u'tabJobType', u'вкладка "Вид работы"'),
                    (u'tabPersonAttach', u'вкладка "Работа на участке"'),
                    (u'tabAccess', u'вкладка "Управление доступом"')
                    ]
        return cls.normalizeHiddableChildren(nameList)

    def save(self):
        try:
            db = QtGui.qApp.db
            db.transaction()
            try:
                record = self.getRecord()
                idFieldName = db.forceTable('Person').idFieldName()
                isInsert = record.isNull(idFieldName)
                id = db.insertOrUpdate('Person', record)
                regAddressRecord, regAddress, regAddressRecordChanged = self.getAddressRecord(id, 0)
                if regAddressRecordChanged and regAddressRecord is not None:
                    db.insertOrUpdate('Person_Address', regAddressRecord)
                locAddressRecord, locAddress, locAddressRecordChanged = self.getAddressRecord(id, 1)
                if locAddressRecordChanged and locAddressRecord is not None:
                    db.insertOrUpdate('Person_Address', locAddressRecord)
                documentRecord, documentRecordChanged = self.getDocumentRecord(id)
                if documentRecordChanged and documentRecord is not None:
                    db.insertOrUpdate('Person_Document', documentRecord)
                self.modelEducationDocs.saveItems(id)
                self.modelAwards.saveItems(id)
                self.modelOrderDocs.saveItems(id)
                self.modelPersonActivity.saveItems(id)
                self.modelPersonJobType.saveItems(id)
                self.modelPrerecordQuotas.saveItems(id)
                self.modelTimeTable.saveData()
                self.modelUserProfile.saveItems(id)
                self.modelPersonAttach.saveItems(id)
                db.commit()
            except:
                db.rollback()
                QtGui.qApp.logCurrentException()
                raise
            self.setItemId(id)
            self.__regAddressRecord = regAddressRecord
            self.__regAddress = regAddress
            self.__locAddressRecord = locAddressRecord
            self.__locAddress = locAddress
            self.__documentRecord = documentRecord

            self.setIsDirty(False)
            CRBPersonEditor.prevAddress = (regAddress, forceStringEx(regAddressRecord.value('freeInput')), locAddress)

            # -- BEGIN -------------------------------------------------------------------------
            # -- INSERT\UPDATE USER INFO (MYSQL ACCOUNT) ---------------------------------------
            # ----------------------------------------------------------------------------------
            if QtGui.qApp.preferences.dbNewAuthorizationScheme:
                convertedLogin = createLogin(self.newUsername)
                whoIsEdit = createLogin(unicode(QtGui.qApp.preferences.appUserName).encode('utf8'))

                sqlCreateUser = "CREATE USER '{0}'@'{1}' IDENTIFIED BY '{2}';"
                sqlCreateUser += "GRANT ALL PRIVILEGES ON *.* TO '{0}'@'{1}' WITH GRANT OPTION MAX_USER_CONNECTIONS 1;"
                sqlUserExits = "SELECT user FROM mysql.user WHERE user = '{0}' AND host = '{1}';"
                sqlDropUser = "DROP USER '{0}'@'{1}';"
                sqlRenameUser = "RENAME USER '{0}'@'{1}' TO '{2}'@'{1}';"
                sqlSetPass = "SET PASSWORD FOR '{0}'@'{1}' = PASSWORD('{2}');"
                insertInLog = "INSERT INTO `logUsernamesChanges` (userName, guiName, dbName, idPerson, createDate, operationName) \
                                  VALUES ('%s', '%s', '%s', '%s', NOW(), '%s')"
                dbHost = "%"

                if isInsert:
                    qryRes = db.query(sqlUserExits.format(convertedLogin, dbHost))
                    if qryRes.first():
                        db.query(sqlDropUser.format(convertedLogin, dbHost))
                    db.query(sqlCreateUser.format(convertedLogin, dbHost, self.hashedPassword))
                    actionDesc = "created"
                else:
                    rez = db.query(sqlUserExits.format(convertedLogin, dbHost))
                    if rez.first():
                        if self.isUserDeleted:
                            db.query(sqlDropUser.format(convertedLogin, dbHost))
                            actionDesc = "deleted"
                        else:
                            convertedOldName = createLogin(self.oldUsername)
                            if convertedOldName != convertedLogin:
                                db.query(sqlRenameUser.format(convertedOldName, dbHost, convertedLogin))
                            if self.chkChangePassword.isChecked():
                                db.query(sqlSetPass.format(convertedLogin, dbHost, self.hashedPassword))
                            actionDesc = "changed"
                    else:
                        db.query(sqlCreateUser.format(convertedLogin, dbHost, self.hashedPassword))
                        actionDesc = "created (changed)"

                insertInLog = insertInLog % (
                whoIsEdit, self.newUsername.decode('utf-8'), convertedLogin, id, actionDesc)
                db.query(insertInLog)

            return id

        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self,
                                       u'',
                                       unicode(e),
                                       QtGui.QMessageBox.Close)
            return None

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        id = self.itemId()
        setLineEditValue(self.edtLastName, record, 'lastName')
        setLineEditValue(self.edtFirstName, record, 'firstName')
        setLineEditValue(self.edtPatrName, record, 'patrName')
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtFederalCode, record, 'federalCode')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setRBComboBoxValue(self.cmbOrg, record, 'org_id')
        setRBComboBoxValue(self.cmbOrgStructure, record, 'orgStructure_id')
        setRBComboBoxValue(self.cmbPost, record, 'post_id')
        setRBComboBoxValue(self.cmbSpeciality, record, 'speciality_id')
        setLineEditValue(self.edtOffice, record, 'office')
        setLineEditValue(self.edtOffice2, record, 'office2')
        setRBComboBoxValue(self.cmbTariffCategory, record, 'tariffCategory_id')
        setRBComboBoxValue(self.cmbFinance, record, 'finance_id')
        setLineEditValue(self.edtLogin, record, 'login')
        setLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        setDateEditValue(self.edtRetireDate, record, 'retireDate')
        setCheckBoxValue(self.chkRetired, record, 'retired')
        setCheckBoxValue(self.chkAvailableForExternal, record, 'availableForExternal')
        setDateEditValue(self.edtLastAccessibleTimelineDate, record, 'lastAccessibleTimelineDate')
        setSpinBoxValue(self.edtTimelineAccessibilityDays, record, 'timelineAccessibleDays')
        setSpinBoxValue(self.edtCanSeeDays, record, 'canSeeDays')
        setSpinBoxValue(self.edtAmbPlan, record, 'ambPlan')
        setSpinBoxValue(self.edtHomePlan, record, 'homPlan')
        setSpinBoxValue(self.edtAmbPlan2, record, 'ambPlan2')
        setSpinBoxValue(self.edtHomePlan2, record, 'homPlan2')
        setSpinBoxValue(self.edtExpPlan, record, 'expPlan')
        setLineEditValue(self.edtContactNumber, record, 'contactNumber')
        setDateEditValue(self.edtRegBegDate, record, 'regBegDate')
        setDateEditValue(self.edtRegEndDate, record, 'regEndDate')
        setRBComboBoxValue(self.cmbNationality, record, 'citizenship_id')
        setWidgetValue(self.cmbMaritalStatus, record, 'maritalStatus')
        setWidgetValue(self.cmbOccupationType, record, 'occupationType')
        setWidgetValue(self.cmbEmploymentType, record, 'employmentType')
        setWidgetValue(self.cmbAcademicDegree, record, 'academicDegree')
        setWidgetValue(self.cmbIsReservist, record, 'isReservist')
        setWidgetValue(self.cmbRegType, record, 'regType')
        setWidgetValue(self.cmbQALevel, record, 'qaLevel')

        self.chkDefaultInHB.setChecked(forceBool(record.value('isDefaultInHB')))
        self.chkInvestigator.setChecked(forceBool(record.value('isInvestigator')))
        self.edtBirthDate.setDate(forceDate(record.value('birthDate')))
        setLineEditValue(self.edtBirthPlace, record, 'birthPlace')
        self.cmbSex.setCurrentIndex(forceInt(record.value('sex')))
        self.edtSNILS.setText(forceString(record.value('SNILS')))
        self.setRegAddressRecord(getPersonAddress(id, 0))
        self.setLocAddressRecord(getPersonAddress(id, 1))
        self.setDocumentRecord(getPersonDocument(id))
        self.modelEducationDocs.loadItems(id)
        self.modelAwards.loadItems(id)
        self.modelOrderDocs.loadItems(id)
        self.modelPersonAttach.loadItems(id)
        self.modelPersonActivity.loadItems(id)
        self.modelPersonJobType.loadItems(id)
        self.modelPrerecordQuotas.loadItems(id)
        self.modelUserProfile.loadItems(id)
        self.modelPrerecordQuotas.setDisabledTypeCodes(
            ['external'] if not self.chkAvailableForExternal.isChecked() else [])
        setComboBoxValue(self.cmbTypeTimeLinePerson, record, 'typeTimeLinePerson')
        self.on_cmbTypeTimeLinePerson_currentIndexChanged()
        setLineEditValue(self.edtINN, record, 'INN')
        self.setIsDirty(False)

        # added by atronah (31.05.2012) for issue #350
        if checkExistFieldWithMessage(record, 'addComment', self, 'Person'):
            setCheckBoxValue(self.chkAddComment, record, 'addComment')  # added by atronah (30.05.2012)
            setTextEditValue(self.edtComment, record, 'commentText')
        else:
            self.chkAddComment.setVisible(False)
            self.edtComment.setVisible(False)
        # end adding by atronah for issue #350
        self.oldUsername = unicode(self.edtLogin.text()).encode('utf-8')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('lastName', toVariant(nameCase(forceStringEx(self.edtLastName.text()))))
        record.setValue('firstName', toVariant(nameCase(forceStringEx(self.edtFirstName.text()))))
        record.setValue('patrName', toVariant(nameCase(forceStringEx(self.edtPatrName.text()))))
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtFederalCode, record, 'federalCode')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getRBComboBoxValue(self.cmbOrg, record, 'org_id')
        getRBComboBoxValue(self.cmbOrgStructure, record, 'orgStructure_id')
        getRBComboBoxValue(self.cmbPost, record, 'post_id')
        getRBComboBoxValue(self.cmbSpeciality, record, 'speciality_id')
        getLineEditValue(self.edtOffice, record, 'office')
        getLineEditValue(self.edtOffice2, record, 'office2')
        getRBComboBoxValue(self.cmbTariffCategory, record, 'tariffCategory_id')
        getRBComboBoxValue(self.cmbFinance, record, 'finance_id')
        self.newUsername = unicode(self.edtLogin.text()).encode('utf8')
        getLineEditValue(self.edtLogin, record, 'login')
        getLineEditValue(self.edtSyncGUID, record, 'syncGUID')

        self.hashedPassword = hashlib.md5('').hexdigest()
        if self.chkChangePassword.isChecked():
            encodedPassword = unicode(self.edtPassword.text()).encode('utf8')
            self.hashedPassword = hashlib.md5(encodedPassword).hexdigest()
            record.setValue('password', toVariant(self.hashedPassword))
        elif not self.itemId():
            self.hashedPassword = hashlib.md5('').hexdigest()
            record.setValue('password', toVariant(self.hashedPassword))
        else:
            record.remove(record.indexOf('password'))
        getDateEditValue(self.edtRetireDate, record, 'retireDate')
        self.isUserDeleted = bool(self.chkRetired.isChecked())
        getCheckBoxValue(self.chkRetired, record, 'retired')
        getCheckBoxValue(self.chkAvailableForExternal, record, 'availableForExternal')
        getDateEditValue(self.edtLastAccessibleTimelineDate, record, 'lastAccessibleTimelineDate')
        getSpinBoxValue(self.edtTimelineAccessibilityDays, record, 'timelineAccessibleDays')
        getSpinBoxValue(self.edtCanSeeDays, record, 'canSeeDays')
        getSpinBoxValue(self.edtAmbPlan, record, 'ambPlan')
        getSpinBoxValue(self.edtHomePlan, record, 'homPlan')
        getSpinBoxValue(self.edtAmbPlan2, record, 'ambPlan2')
        getSpinBoxValue(self.edtHomePlan2, record, 'homPlan2')
        getSpinBoxValue(self.edtExpPlan, record, 'expPlan')
        getDateEditValue(self.edtBirthDate, record, 'birthDate')
        getComboBoxValue(self.cmbTypeTimeLinePerson, record, 'typeTimeLinePerson')
        getLineEditValue(self.edtBirthPlace, record, 'birthPlace')
        getLineEditValue(self.edtContactNumber, record, 'contactNumber')
        getDateEditValue(self.edtRegBegDate, record, 'regBegDate')
        getDateEditValue(self.edtRegEndDate, record, 'regEndDate')
        getRBComboBoxValue(self.cmbNationality, record, 'citizenship_id')
        getWidgetValue(self.cmbMaritalStatus, record, 'maritalStatus')
        getWidgetValue(self.cmbOccupationType, record, 'occupationType')
        getWidgetValue(self.cmbEmploymentType, record, 'employmentType')
        getWidgetValue(self.cmbAcademicDegree, record, 'academicDegree')
        getWidgetValue(self.cmbIsReservist, record, 'isReservist')
        getWidgetValue(self.cmbRegType, record, 'regType')
        getWidgetValue(self.cmbQALevel, record, 'qaLevel')
        getCheckBoxValue(self.chkDefaultInHB, record, 'isDefaultInHB')
        getCheckBoxValue(self.chkInvestigator, record, 'isInvestigator')

        if record.contains('userProfile_id'):
            record.setValue('userProfile_id', QtCore.QVariant(self.modelUserProfile.primaryProfileId()))

        record.setValue('sex', toVariant(self.cmbSex.currentIndex()))
        record.setValue('SNILS', toVariant(forceStringEx(self.edtSNILS.text()).replace('-', '').replace(' ', '')))
        getLineEditValue(self.edtINN, record, 'INN')
        getCheckBoxValue(self.chkAddComment, record, 'addComment')  # added by atronah (30.05.2012)  for issue #350
        getTextEditValue(self.edtComment, record, 'commentText')
        return record

    def getAddress(self, addressType):
        if addressType == 0:
            return {'useKLADR': self.chkRegKLADR.isChecked(),
                    'KLADRCode': self.cmbRegCity.code(),
                    'KLADRStreetCode': self.cmbRegStreet.code(),
                    'number': forceStringEx(self.edtRegHouse.text()),
                    'corpus': forceStringEx(self.edtRegCorpus.text()),
                    'flat': forceStringEx(self.edtRegFlat.text()),
                    'freeInput': forceStringEx(self.edtRegFreeInput.text())}
        else:
            return {'useKLADR': True,
                    'KLADRCode': self.cmbLocCity.code(),
                    'KLADRStreetCode': self.cmbLocStreet.code(),
                    'number': forceStringEx(self.edtLocHouse.text()),
                    'corpus': forceStringEx(self.edtLocCorpus.text()),
                    'flat': forceStringEx(self.edtLocFlat.text()),
                    'freeInput': ''}

    def getAddressRecord(self, personId, addressType):
        address = self.getAddress(addressType)
        addressId = getAddressId(address) if address['useKLADR'] else None
        oldAddressRecord = self.__regAddressRecord if addressType == 0 else self.__locAddressRecord
        recordChanged = (not oldAddressRecord or
                         addressId != forceRef(oldAddressRecord.value('address_id')) or
                         address['freeInput'] != forceString(oldAddressRecord.value('freeInput')))

        if recordChanged:
            record = QtGui.qApp.db.record('Person_Address')
            record.setValue('master_id', toVariant(personId))
            record.setValue('type', toVariant(addressType))
            record.setValue('address_id', toVariant(addressId))
            record.setValue('freeInput', toVariant(address['freeInput']))
        else:
            record = oldAddressRecord

        return record, address, recordChanged

    def setRegAddressRecord(self, record):
        self.__regAddressRecord = record
        if record:
            addressId = forceRef(record.value('address_id'))
            if addressId:
                self.__regAddress = getAddress(addressId)
            else:
                self.__regAddress = None
            self.setRegAddress(self.__regAddress, forceString(record.value('freeInput')))
        else:
            self.chkRegKLADR.setChecked(False)
            self.__regAddress = None
            self.setRegAddress(self.__regAddress, '')

    def setRegAddress(self, regAddress, freeInput):
        self.chkRegKLADR.setChecked(regAddress is not None)
        self.edtRegFreeInput.setText(freeInput)
        if regAddress:
            self.cmbRegCity.setCode(regAddress.KLADRCode)
            self.cmbRegStreet.setCity(regAddress.KLADRCode)
            self.cmbRegStreet.setCode(regAddress.KLADRStreetCode)
            self.edtRegHouse.setText(regAddress.number)
            self.edtRegCorpus.setText(regAddress.corpus)
            self.edtRegFlat.setText(regAddress.flat)
        else:
            self.cmbRegCity.setCode(QtGui.qApp.defaultKLADR())
            self.cmbRegStreet.setCity(QtGui.qApp.defaultKLADR())
            self.cmbRegStreet.setCode('')
            self.edtRegHouse.setText('')
            self.edtRegCorpus.setText('')
            self.edtRegFlat.setText('')

    def setLocAddressRecord(self, record):
        self.__locAddressRecord = record
        if record:
            addressId = forceRef(record.value('address_id'))
            self.__locAddress = getAddress(addressId)
        else:
            self.__locAddress = None
        self.setLocAddress(self.__locAddress)

    def setLocAddress(self, locAddress):
        if locAddress:
            self.cmbLocCity.setCode(locAddress.KLADRCode)
            self.cmbLocStreet.setCity(locAddress.KLADRCode)
            self.cmbLocStreet.setCode(locAddress.KLADRStreetCode)
            self.edtLocHouse.setText(locAddress.number)
            self.edtLocCorpus.setText(locAddress.corpus)
            self.edtLocFlat.setText(locAddress.flat)
        else:
            self.cmbLocCity.setCode(QtGui.qApp.defaultKLADR())
            self.cmbLocStreet.setCity(QtGui.qApp.defaultKLADR())
            self.cmbLocStreet.setCode('')
            self.edtLocHouse.setText('')
            self.edtLocCorpus.setText('')
            self.edtLocFlat.setText('')

    def getDocumentRecord(self, personId):
        docTypeId = self.cmbDocType.value()
        serialLeft = forceStringEx(self.edtDocSerialLeft.text())
        serialRight = forceStringEx(self.edtDocSerialRight.text())
        serial = serialLeft + ' ' + serialRight
        number = forceStringEx(self.edtDocNumber.text())
        origin = forceStringEx(self.edtOrigin.text())
        date = forceDate(self.edtDocDate.date())
        if docTypeId in [0, None]:
            record = None
            recordChanged = self.__documentRecord is not None
        else:
            if self.__documentRecord is not None:
                recordChanged = (
                    docTypeId != forceRef(self.__documentRecord.value('documentType_id')) or
                    serial != forceString(self.__documentRecord.value('serial')) or
                    number != forceString(self.__documentRecord.value('number')) or
                    origin != forceString(self.__documentRecord.value('origin')) or
                    date != forceDate(self.__documentRecord.value('date'))
                )
            else:
                recordChanged = True

            if recordChanged:
                record = QtGui.qApp.db.record('Person_Document')
                record.setValue('master_id', toVariant(personId))
                record.setValue('documentType_id', toVariant(docTypeId))
                record.setValue('serial', toVariant(serial))
                record.setValue('number', toVariant(number))
                record.setValue('origin', toVariant(origin))
                record.setValue('date', toVariant(date))
            else:
                record = self.__documentRecord

        return record, recordChanged

    def setDocumentRecord(self, record):
        self.__documentRecord = record
        if record:
            self.cmbDocType.setValue(forceInt(record.value('documentType_id')))
            serial = forceString(record.value('serial'))
            for c in '-=/_|':
                serial = serial.replace('c', ' ')
            serial = forceStringEx(serial).split()
            serialLeft = serial[0] if len(serial) >= 1 else ''
            serialRight = serial[1] if len(serial) >= 2 else ''
            self.edtDocSerialLeft.setText(serialLeft)
            self.edtDocSerialRight.setText(serialRight)
            self.edtDocNumber.setText(forceString(record.value('number')))
            self.edtOrigin.setText(forceString(record.value('origin')))
            self.edtDocDate.setDate(forceDate(record.value('date')))
        else:
            self.cmbDocType.setValue(None)
            self.edtDocSerialLeft.setText('')
            self.edtDocSerialRight.setText('')
            self.edtDocNumber.setText('')

    def checkAttaches(self):
        result = True

        birthDate = forceDate(self.edtBirthDate.date())
        attachList = []

        model = self.tblPersonAttach.model()
        for row, item in enumerate(model.items()):
            begDate = forceDate(item.value('begDate'))
            endDate = forceDate(item.value('endDate'))
            orgStructureId = forceRef(item.value('orgStructure_id'))
            if orgStructureId is not None:
                attachList.append((row, orgStructureId, begDate, endDate))

            result = result and (orgStructureId is not None or
                                 self.checkInputMessage(u'участок', False,
                                                        self.tblPersonAttach, row,
                                                        model.getColIndex('orgStructure_id')))
            result = result and (begDate and not begDate.isNull() or
                                 self.checkInputMessage(u'дату начала', False,
                                                        self.tblPersonAttach, row, model.getColIndex('begDate')))
            result = result and (begDate >= birthDate or
                                 self.checkValueMessage(u'Дата начала меньше даты рождения сотрудника', True,
                                                        self.edtRegBegDate))

            result = result and (not endDate or begDate <= endDate or
                                 self.checkValueMessage(u'Дата начала больше даты окончания', False,
                                                        self.tblPersonAttach, row, model.getColIndex('begDate')))
            #
            # i4312, comment (0017955)
            #
            # result = result and (not endDate or endDate <= QtCore.QDate.currentDate() or
            #                      self.checkValueMessage(u'Дата окончания не может быть больше текущей даты', False,
            #                                             self.tblPersonAttach, row, model.getColIndex('endDate')))
            result = result and self.checkAvailableForAttach(row, orgStructureId, begDate, endDate, self.itemId())

        openedRows = [row for row, orgStructureId, begDate, endDate in attachList if not endDate]
        #
        # i4312, comment (0017955)
        #
        # result = result and (len(openedRows) <= 1 or
        #                     self.checkValueMessage(u'Более одной записи без даты окончания', False,
        #                                            self.tblPersonAttach, openedRows[-1], model.getColIndex('endDate')))

        # for i, (iRow, iOrgStructureId, iBegDate, iEndDate) in enumerate(attachList):
        # for jRow, jOrgStructureId, jBegDate, jEndDate in attachList[i + 1:]:
        # result = result
        # result = result and (not self.checkIntersection(iBegDate, iEndDate, jBegDate, jEndDate) or
        #                     self.checkValueMessage(u'Пересечение дат работ:<br>'
        #                                            u'<b>{0}</b> {1}–{2}<br>'
        #                                            u'<b>{3}</b> {4}–{5}'.format(getOrgStructureName(iOrgStructureId),
        #                                                                         forceString(iBegDate),
        #                                                                         forceString(iEndDate) if iEndDate else u'&lt;не задано&gt;',
        #                                                                         getOrgStructureName(jOrgStructureId),
        #                                                                         forceString(jBegDate),
        #                                                                         forceString(jEndDate) if jEndDate else u'&lt;не задано&gt;'),
        #                                            False,
        #                                            self.tblPersonAttach, jRow, model.getColIndex('begDate')))
        return result

    @staticmethod
    def checkIntersection(begDate1, endDate1, begDate2, endDate2):
        if not endDate1 and not endDate2: return True
        if endDate1 and endDate2: return min(endDate1, endDate2) >= max(begDate1, begDate2)
        if not endDate1: return endDate2 >= begDate1
        if not endDate2: return endDate1 >= begDate2
        return False

    def checkAvailableForAttach(self, row, orgStructureId, begDate, endDate=None, personId=None):
        db = QtGui.qApp.db
        tablePersonAttach = db.table('PersonAttach')
        tableVPerson = db.table('vrbPersonWithSpeciality')

        table = tablePersonAttach.innerJoin(tableVPerson, tableVPerson['id'].eq(tablePersonAttach['master_id']))
        cols = [
            tableVPerson['name'],
            tablePersonAttach['begDate'],
            tablePersonAttach['endDate']
        ]
        cond = [
            tablePersonAttach['orgStructure_id'].eq(orgStructureId),
            tablePersonAttach['begDate'].isNotNull(),
            tablePersonAttach['deleted'].eq(0),
        ]

        if not endDate:
            dateCond = db.joinOr([
                tablePersonAttach['endDate'].isNull(),
                tablePersonAttach['endDate'].dateGe(begDate)
            ])
        else:
            dateCond = db.joinOr([
                db.joinAnd([
                    tablePersonAttach['endDate'].isNull(),
                    tablePersonAttach['begDate'].dateLe(endDate)]),
                db.joinAnd([
                    tablePersonAttach['endDate'].isNotNull(),
                    db.least(db.date(endDate), tablePersonAttach['endDate']) >= db.greatest(db.date(begDate),
                                                                                            tablePersonAttach[
                                                                                                'begDate'])
                ])
            ])
        cond.append(dateCond)

        if personId is not None:
            cond.append(tablePersonAttach['master_id'].ne(personId))

        order = [
            tablePersonAttach['id'].desc()
        ]
        rec = db.getRecordEx(table, cols, cond, order)
        if rec:
            name = forceStringEx(rec.value('name'))
            begDate = forceDate(rec.value('begDate'))
            endDate = forceDate(rec.value('endDate'))
            return self.checkValueMessage(u'За данным участком уже закреплён:<br>'
                                          u'<b>{0}</b>, {1}–{2}'.format(name,
                                                                        forceString(begDate),
                                                                        forceString(
                                                                            endDate) if endDate else u'&lt;не задано&gt;'),
                                          False,
                                          self.tblPersonAttach, row,
                                          self.tblPersonAttach.model().getColIndex('begDate'))
        return True

    def checkDataEntered(self):
        result = True

        code = forceStringEx(self.edtCode.text())
        name = forceStringEx(self.edtLastName.text())
        login = forceStringEx(self.edtLogin.text())
        birthDate = forceDate(self.edtBirthDate.date())

        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'фамилию', False, self.edtLastName))
        result = result and (login or self.checkInputMessage(u'регистрационное имя', True, self.edtLogin))
        result = result and (birthDate.addYears(18) <= QtCore.QDate.currentDate() or
                             self.checkValueMessage(u'ВНИМАНИЕ! Возраст сотрудника меньше 18 лет', False,
                                                    self.edtBirthDate))
        if result and login:
            db = QtGui.qApp.db
            table = db.table('Person')
            idList = db.getIdList(table, 'id', table['login'].eq(login))
            if idList and idList != [self.itemId()]:
                QtGui.QMessageBox.warning(self,
                                          u'Внимание!',
                                          u'Регистрационное имя "%s" уже занято' % login,
                                          QtGui.QMessageBox.Ok,
                                          QtGui.QMessageBox.Ok)
                self.edtLogin.setFocus(QtCore.Qt.OtherFocusReason)
                result = False
            result = result and (
            len(self.modelUserProfile.items()) or self.checkInputMessage(u'Профиль', False, self.tblUserProfile))

        if self.cmbSpeciality.value():
            excludedQuotaTypeCodeList = [] if self.chkAvailableForExternal.isChecked() else ['external']
            sumQuota = self.modelPrerecordQuotas.summaryQuota(excludedQuotaTypeCodeList)
            result = result and (
            sumQuota >= 100 or self.checkValueMessage(u'Сумма квот должна быть не менее 100%', True,
                                                      self.tblPrerecordQuota))

        result = result and self.checkAwards()
        result = result and self.checkAttaches()

        return result

    def checkAwards(self):
        for row, item in enumerate(self.modelAwards.items()):
            if not forceString(item.value('name')):
                return self.checkValueMessage(u'Необходимо указать название награды', False, self.tblAwards, row, 1)
        return True

    @QtCore.pyqtSlot(int)
    def on_cmbOrg_currentIndexChanged(self, index):
        orgId = self.cmbOrg.value()
        self.cmbOrgStructure.setEnabled(bool(orgId))
        self.cmbOrgStructure.setOrgId(orgId)

    @QtCore.pyqtSlot(int)
    def on_cmbTypeTimeLinePerson_currentIndexChanged(self, index=None):
        typeTemplate = self.cmbTypeTimeLinePerson.currentIndex()
        if typeTemplate < 2:
            countRow = typeTemplate + 1
        else:
            countRow = (typeTemplate - 1) * 7
        self.modelTimeTable.getRowCount(countRow, typeTemplate, self.itemId())

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        isDoctor = bool(self.cmbSpeciality.value())
        self.chkAvailableForExternal.setEnabled(isDoctor)
        self.edtLastAccessibleTimelineDate.setEnabled(isDoctor)
        self.edtTimelineAccessibilityDays.setEnabled(isDoctor)
        self.edtAmbPlan.setEnabled(isDoctor)
        self.edtHomePlan.setEnabled(isDoctor)
        self.edtAmbPlan2.setEnabled(isDoctor)
        self.edtHomePlan2.setEnabled(isDoctor)
        self.edtExpPlan.setEnabled(isDoctor)
        self.tblPrerecordQuota.setEnabled(isDoctor)

    @QtCore.pyqtSlot(int)
    def on_chkChangePassword_stateChanged(self, state):
        self.setIsDirty(True)

    @QtCore.pyqtSlot(bool)
    def on_chkAvailableForExternal_toggled(self, checked):
        isDoctor = bool(self.cmbSpeciality.value())
        isAvailableDoctorDoctor = isDoctor and checked
        self.edtLastAccessibleTimelineDate.setEnabled(isDoctor)
        self.edtTimelineAccessibilityDays.setEnabled(isDoctor)
        self.tblPrerecordQuota.model().setDisabledTypeCodes(['external'] if not isAvailableDoctorDoctor else [])

    @QtCore.pyqtSlot(int)
    def on_edtTimelineAccessibilityDays_valueChanged(self, value):
        self.lblTimelineAccessibilityDaysSuffix.setText(agreeNumberAndWord(value, (u'день', u'дня', u'дней')))

    @QtCore.pyqtSlot(int)
    def on_edtCanSeeDays_valueChanged(self, value):
        self.lblCanSeeDaysSuffix.setText(agreeNumberAndWord(value, (u'день', u'дня', u'дней')))

    @QtCore.pyqtSlot()
    def on_btnCopyPrevAddress_clicked(self):
        if CRBPersonEditor.prevAddress:
            reg, freeInput, loc = CRBPersonEditor.prevAddress
            self.setRegAddress(reg, freeInput)
            self.setLocAddress(loc)

    @QtCore.pyqtSlot(bool)
    def on_chkRegKLADR_toggled(self, checked):
        self.edtRegFreeInput.setEnabled(not checked)
        self.cmbRegCity.setEnabled(checked)
        self.cmbRegStreet.setEnabled(checked)
        self.edtRegHouse.setEnabled(checked)
        self.edtRegCorpus.setEnabled(checked)
        self.edtRegFlat.setEnabled(checked)

    @QtCore.pyqtSlot(int)
    def on_cmbRegCity_currentIndexChanged(self, val):
        code = self.cmbRegCity.code()
        self.cmbRegStreet.setCity(code)

    @QtCore.pyqtSlot()
    def on_btnCopy_clicked(self):
        code = self.cmbRegCity.code()
        self.cmbLocCity.setCode(code)
        self.cmbLocStreet.setCity(code)
        self.cmbLocStreet.setCode(self.cmbRegStreet.code())
        self.edtLocHouse.setText(self.edtRegHouse.text())
        self.edtLocCorpus.setText(self.edtRegCorpus.text())
        self.edtLocFlat.setText(self.edtRegFlat.text())

    @QtCore.pyqtSlot(int)
    def on_cmbLocCity_currentIndexChanged(self, index):
        code = self.cmbLocCity.code()
        self.cmbLocStreet.setCity(code)

    @QtCore.pyqtSlot(int)
    def on_cmbDocType_currentIndexChanged(self, index):
        docTypeId = self.cmbDocType.value()
        serialFormat = forceInt(QtGui.qApp.db.translate('rbDocumentType', 'id', docTypeId, 'serial_format'))
        self.edtDocSerialLeft.setFormat(serialFormat)
        self.edtDocSerialRight.setFormat(serialFormat)


class CEducationDocsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_Education', 'id', 'master_id', parent)
        self.setFilter(
            'documentType_id IN (SELECT rbDocumentType.id FROM rbDocumentType LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id = rbDocumentType.group_id WHERE rbDocumentTypeGroup.code=\'3\')')
        self.addCol(COrgInDocTableCol(u'Учебное заведение', 'org_id', 20))
        self.addCol(CEnumInDocTableCol(u'Тип образования', 'educationType', 30, PersonEducationType))
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 15, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 30, 'rbSpeciality'))
        self.addCol(CInDocTableCol(u'Статус', 'status', 30))
        self.addCol(CInDocTableCol(u'Цикл', 'cycle', 30))
        self.addCol(CIntInDocTableCol(u'Количество часов', 'hours', 10, low=0, high=1000))
        self.addCol(CRBInDocTableCol(u'Категория', 'category_id', 15, 'rbPersonCategory'))
        self.addCol(CRBInDocTableCol(u'Тип документа', 'documentType_id', 30, 'rbDocumentType',
                                     filter='group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'3\')'))
        self.addCol(CInDocTableCol(u'Серия', 'serial', 8))
        self.addCol(CInDocTableCol(u'Номер', 'number', 16))
        self.addCol(CInDocTableCol(u'Выдан', 'origin', 30))
        self.addCol(CDateInDocTableCol(u'Действителен с', 'validFromDate', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Действителен по', 'validToDate', 15, canBeEmpty=True))


class CAwardsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_Awards', 'id', 'master_id', parent)
        self.addCol(CInDocTableCol(u'Номер', 'number', 30))
        self.addCol(CInDocTableCol(u'Название', 'name', 50))
        self.addCol(CDateInDocTableCol(u'Дата получения', 'date', 20))


class COrderDocsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_Order', 'id', 'master_id', parent)
        self.setFilter(
            'documentType_id IN (SELECT rbDocumentType.id FROM rbDocumentType LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id = rbDocumentType.group_id WHERE rbDocumentTypeGroup.code=\'4\') OR documentType_id IS NULL')
        self.addCol(CDateInDocTableCol(u'Дата', 'date', 15))
        self.addCol(CEnumInDocTableCol(u'Тип перемещения', 'type', 15, PersonOrderType, sortable=True))
        self.addCol(CDateInDocTableCol(u'Дата', 'documentDate', 15))
        self.addCol(CInDocTableCol(u'Номер', 'documentNumber', 8))
        self.addCol(CRBInDocTableCol(u'Тип документа', 'documentType_id', 30, 'rbDocumentType',
                                     filter='group_id IN (SELECT id FROM rbDocumentTypeGroup WHERE code=\'4\')'))
        self.addCol(CDateInDocTableCol(u'Действителен с', 'validFromDate', 15, canBeEmpty=True))
        self.addCol(CDateInDocTableCol(u'Действителен по', 'validToDate', 15, canBeEmpty=True))
        self.addCol(CRBInDocTableCol(u'Должность', 'post_id', 30, 'rbPost'))
        self.addCol(COrgStructureInDocTableCol(u'Подразделение', 'orgStructure_id', 15))
        self.addCol(CInDocTableCol(u'Ставка', 'salary', 15))


class CAttachSyncStatusCol(CBoolInDocTableCol):
    def toString(self, val, record):
        return toVariant(u'Синхронизировано' if forceBool(val) else u'Не синхронизировано')


class CPersonAttachModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'PersonAttach', 'id', 'master_id', parent)
        self.addCol(CDateInDocTableCol(u'Дата начала', 'begDate', 15))
        self.addCol(CDateInDocTableCol(u'Дата окончания', 'endDate', 15))
        self.addCol(CInDocTableCol(u'Ставка', 'salary', 15))
        self.addExtCol(COrgStructureInDocTableCol(u'Подразделение', 'orgS', 15), QtCore.QVariant.Int)
        self.addCol(CRBInDocTableCol(u'Номер участка', 'orgStructure_id', 30, 'OrgStructure',
                                     codeFieldName='infisInternalCode'))
        self.addCol(CAttachSyncStatusCol(u'Статус синхронизации', 'sentToTFOMS', 10, readOnly=True,
                                         isVisible=QtGui.qApp.isKrasnodarRegion()))
        self.addCol(CInDocTableCol(u'Описание ошибки', 'errorCode', 15, readOnly=True,
                                   isVisible=QtGui.qApp.isKrasnodarRegion()))

    @staticmethod
    def getOrgStructureFilter(orgStructureId):
        if not orgStructureId: return '0'
        db = QtGui.qApp.db
        tableOrgStructure = db.table('OrgStructure')
        cond = [
            tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)),
            tableOrgStructure['isArea'].ne(0),
            tableOrgStructure['name'].ne('')
        ]
        return db.joinAnd(cond)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        if column == self.getColIndex('orgS'):
            self.getCol('orgStructure_id').setFilter(self.getOrgStructureFilter(forceRef(value)))
        ret = CInDocTableModel.setData(self, index, value, role)
        if forceString(index.data()) != forceString(value):
            index.model().items()[index.row()].setValue('sentToTFOMS', toVariant(CAttachSentToTFOMS.NotSynced))
        return ret

    def loadItems(self, masterId):
        CInDocTableModel.loadItems(self, masterId)
        db = QtGui.qApp.db
        tableOrgStructure = db.table('OrgStructure')

        if self._items:
            idList = [forceRef(item.value('orgStructure_id')) for item in self._items]
            orgStructureParent = db.getColumnValueMap(tableOrgStructure, 'id', 'parent_id',
                                                      [tableOrgStructure['id'].inlist(idList),
                                                       tableOrgStructure['deleted'].eq(0)])
            for item in self._items:
                item.setValue('orgS', toVariant(orgStructureParent.get(forceRef(item.value('orgStructure_id')))))


class CPersonActivityModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_Activity', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Вид деятельности', 'activity_id', 30, 'rbActivity'))


class CPersonJobTypeModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_JobType', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Типы работ', 'jobType_id', 30, 'rbJobType'))


class CPersonUserProfileModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Person_UserProfile', 'id', 'person_id', parent)
        self._profileCol = CRBInDocTableCol(u'Профиль прав', 'userProfile_id', 30, 'rbUserProfile')
        self.addCol(self._profileCol)

    def primaryProfileId(self):
        """
        Возвращает id первого профился прав с ненулевым кодом, если такой есть, иначе первый из всего списка профилей

        (Для сохранения работоспособности doctor_room без изменения его кода)
        :return: id профиля прав с ненулевым кодом.
        """
        result = None
        for record in self._items:
            profileId = forceRef(record.value(self._profileCol.fieldName()))
            if result is None:
                result = profileId
            code = self._profileCol.getCode(profileId)
            if code:
                result = profileId
                break

        return result


def getPersonAddress(id, addrType):
    return selectLatestRecord('Person_Address', id, 'type=\'%d\'' % addrType)


def getPersonDocument(id):
    filter = '''Tmp.documentType_id IN (SELECT rbDocumentType.id FROM rbDocumentType LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id=rbDocumentType.group_id WHERE rbDocumentTypeGroup.code = '1')'''
    return selectLatestRecord('Person_Document', id, filter)


def selectLatestRecordStmt(tableName, personId, filter=''):
    if type(tableName) == tuple:
        tableName1, tableName2 = tableName
    else:
        tableName1 = tableName
        tableName2 = tableName
    pos = tableName2.find('AS Tmp')
    if pos < 0:
        tableName2 += ' AS Tmp'

    if filter:
        filter = ' AND (' + filter + ')'
    return u'SELECT * FROM %s AS Main WHERE Main.master_id = \'%d\' AND Main.id = (SELECT MAX(Tmp.id) FROM %s WHERE Tmp.master_id =\'%d\' %s)' % (
    tableName1, personId, tableName2, personId, filter)


def selectLatestRecord(tableName, personId, filter=''):
    stmt = selectLatestRecordStmt(tableName, personId, filter)
    query = QtGui.qApp.db.query(stmt)
    if query.next():
        return query.record()
    else:
        return None


class CChangePasswordDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.blinkTimer = QtCore.QTimer()
        self.blinkTimer.setInterval(256)
        self.connect(self.blinkTimer, QtCore.SIGNAL('timeout()'), self.changeConfirmEditBackGround)
        self.blinkCounter = 0

    # atronah: для совместимости с автоматически генерируемым кодом для ui файлов.
    def setupUi(self, dialog):
        self._setupUi(dialog)

    # atronah: подчеркивание перед именем, чтобы убрать warning-messages насчет того, что переменные впервые объявленны вне __init__
    def _setupUi(self, dialog):
        self.edtOldPassword = QtGui.QLineEdit(dialog)
        self.edtOldPassword.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.lblOldPassword = QtGui.QLabel(dialog)
        self.lblOldPassword.setBuddy(self.edtOldPassword)

        self.edtNewPassword = QtGui.QLineEdit(dialog)
        self.edtNewPassword.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.lblNewPassword = QtGui.QLabel(dialog)
        self.lblNewPassword.setBuddy(self.edtNewPassword)

        self.edtConfirmNewPassword = QtGui.QLineEdit(dialog)
        self.edtConfirmNewPassword.setEchoMode(QtGui.QLineEdit.PasswordEchoOnEdit)
        self.lblConfirmNewPassword = QtGui.QLabel(dialog)
        self.lblConfirmNewPassword.setBuddy(self.edtConfirmNewPassword)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                                QtCore.Qt.Horizontal,
                                                dialog)

        self.gridLayout = QtGui.QGridLayout(dialog)
        self.gridLayout.addWidget(self.lblOldPassword, 0, 0)
        self.gridLayout.addWidget(self.edtOldPassword, 0, 1)
        self.gridLayout.addWidget(self.lblNewPassword, 1, 0)
        self.gridLayout.addWidget(self.edtNewPassword, 1, 1)
        self.gridLayout.addWidget(self.lblConfirmNewPassword, 2, 0)
        self.gridLayout.addWidget(self.edtConfirmNewPassword, 2, 1)
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        dialog.setLayout(self.gridLayout)

        self.retranslateUi(dialog)

        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), dialog.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), dialog.close)

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(
            QtGui.QApplication.translate(u'CChangePasswordDialog', u'Смена пароля', disambiguation=None,
                                         encoding=QtGui.QApplication.UnicodeUTF8))
        self.lblOldPassword.setText(
            QtGui.QApplication.translate(u'CChangePasswordDialog', u'Старый пароль', disambiguation=None,
                                         encoding=QtGui.QApplication.UnicodeUTF8))
        self.lblNewPassword.setText(
            QtGui.QApplication.translate(u'CChangePasswordDialog', u'Новый пароль', disambiguation=None,
                                         encoding=QtGui.QApplication.UnicodeUTF8))
        self.lblConfirmNewPassword.setText(
            QtGui.QApplication.translate(u'CChangePasswordDialog', u'Повторите пароль', disambiguation=None,
                                         encoding=QtGui.QApplication.UnicodeUTF8))

    def accept(self):
        if self.edtNewPassword.text() != self.edtConfirmNewPassword.text():
            self.changeConfirmEditBackGround()
            self.blinkTimer.start()
        else:
            QtGui.QDialog.accept(self)

    @QtCore.pyqtSlot()
    def changeConfirmEditBackGround(self):
        if self.blinkCounter <= 3:
            if not self.edtConfirmNewPassword.styleSheet():
                self.edtConfirmNewPassword.setStyleSheet('QLineEdit {background-color: red;}')
            else:
                self.edtConfirmNewPassword.setStyleSheet('')
                self.blinkCounter += 1
        else:
            self.blinkTimer.stop()
            self.blinkCounter = 0

    def passwords(self):
        passwordDict = {'old': self.edtOldPassword.text(),
                        'new': self.edtNewPassword.text()}
        return passwordDict
