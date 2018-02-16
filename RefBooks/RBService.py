# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Exchange.Cimport           import CImport

from library.AgeSelector        import checkAgeSelectorSyntax
from library.ICDInDocTableCol import CICDExInDocTableCol
from library.crbcombobox        import CRBComboBox
from library.DialogBase         import CDialogBase
from library.InDocTable         import CInDocTableModel, CInDocTableCol, CBoolInDocTableCol, CCodeNameInDocTableCol, CEnumInDocTableCol, CRBInDocTableCol
from library.interchange        import getCheckBoxValue, getComboBoxValue, getDateEditValue, getDoubleBoxValue, getLineEditValue, getRBComboBoxValue, getTextEditValue, setCheckBoxValue, setComboBoxValue, setDateEditValue, setDoubleBoxValue, setLineEditValue, setRBComboBoxValue, setTextEditValue
from library.ItemsListDialog    import CItemsSplitListDialogEx, CItemEditorBaseDialog
from library.TableModel         import CBoolCol, CEnumCol, CRefBookCol, CTextCol
from library.Utils              import forceDate, forceRef, forceString, forceStringEx, addDots, addDotsEx

from RefBooks.Tables            import rbCode, rbName, rbService, rbServiceGroup
from RefBooks                   import synchronizeActionTypes_sql
from RefBooks                   import synchronizeActionTypes_create_sql

from Ui_RBServiceEditor         import Ui_ItemEditorDialog
from Ui_ServiceFilterDialog     import Ui_ServiceFilterDialog
from Ui_SynchronizeActionTypes  import Ui_SyncDialog


SexList = ('', u'М', u'Ж')

def isComplexService(code):
    u"""Услуга сложная, если её код начинается с В или она имеет подчинённые"""
    if unicode(code).startswith(u'В') or unicode(code).startswith('B'):
        return True
    result = QtGui.qApp.db.query("""SELECT * from rbService, rbService_Contents
                                                        where rbService_Contents.master_id = rbService.id
                                                        and rbService.code = '%s'"""%code)
    return result.size() > 0


class CRBServiceList(CItemsSplitListDialogEx):
    def __init__(self, parent, forSelect=False, uniqueCode=True):
        CItemsSplitListDialogEx.__init__(self, parent,
            rbService,
            [
            CRefBookCol(u'Группа', ['group_id'], rbServiceGroup, 20, showFields=CRBComboBox.showName),
            CTextCol(u'Код',                 [rbCode], 20),
            CTextCol(u'Наименование',        [rbName], 50),
            CBoolCol(u'Унаследовано из ЕИС', ['eisLegacy'], 10),
            CTextCol(u'ИНФИС код',           ['infis'], 20),
            CEnumCol(u'Лицензирование',      ['license'], [u'не требуется', u'требуется лицензия', u'требуется персональный сертификат'], 30),
            ],
            [rbCode, rbName],
            'rbService_Contents',
            [
            CRefBookCol(u'Код', ['service_id'], rbService, 20, showFields=CRBComboBox.showCode),
            CRefBookCol(u'Наименование', ['service_id'], rbService, 50, showFields=CRBComboBox.showName),
            CBoolCol(u'Обязательно', ['required'], 10),
            ],
            'master_id', 'service_id', forSelect=forSelect, filterClass=CServiceFilterDialog)
        self.setWindowTitleEx(u'Услуги')
        self.addPopupAction('actImport2ActionType', u'Преобразовать выделенные услуги в типы действий', self.importSelected2ActionType)


    def getItemEditor(self):
        return CRBServiceEditor(self)


    def select(self, props):
        table = self.model.table()
        cond = []

        group = props.get('group', None)
        if group:
            cond.append(table['group_id'].eq(group))

        section = props.get('section', 0)
        type = props.get('type', 0)
        class_ = props.get('class', 0)
        if section:
            sectionRecord = QtGui.qApp.db.getRecord('rbServiceSection', ['code'], section)
            sectionCode = forceString(sectionRecord.value('code'))
            cond.append("""left(rbService.code, %d) = '%s'"""%(len(sectionCode), sectionCode))

            if type:
                cond.append("""(select code
                            from rbServiceType
                            where id = %s)
                            = substr(rbService.code from %d for 2)"""%(type, len(sectionCode)+1))

            if class_:
                cond.append("""rbService.code like concat("___.",
            (select code
                            from rbServiceClass
                            where id = %s), "%%")
                            """%class_)

        code= props.get('code', '')
        if code:
            cond.append(table['code'].likeBinary(addDots(code)))

        name = props.get('name', '')
        if name:
            cond.append(table['name'].like(addDotsEx(name)))

        flagEIS = props.get('EIS', QtCore.Qt.PartiallyChecked)
        if flagEIS != QtCore.Qt.PartiallyChecked:
            cond.append(table['eisLegacy'].eq(flagEIS != QtCore.Qt.Unchecked))

        flagNomenclature = props.get('nomenclature', QtCore.Qt.PartiallyChecked)
        if flagNomenclature != QtCore.Qt.PartiallyChecked:
            cond.append(table['nomenclatureLegacy'].eq(flagNomenclature!= QtCore.Qt.Unchecked))

        begDate = props.get('begDate',  QtCore.QDate())
        if not begDate.isNull():
            cond.append(table['begDate'].ge(forceString(begDate.toString(QtCore.Qt.ISODate))))

        endDate = props.get('endDate',  QtCore.QDate())
        if not endDate.isNull():
            cond.append(table['endDate'].le(forceString(endDate.toString(QtCore.Qt.ISODate))))

        return QtGui.qApp.db.getIdList(table.name(),
                           'id',
                           cond,
                           self.order)

    def importSelected2ActionType(self):
        selectedIdList = self.tblItems.selectedItemIdList()
        CSynchronizeActionTypesDialog(self, selectedIdList).exec_()


#
# ##########################################################################
#


class CSynchronizeActionTypesDialog(CDialogBase, CImport, Ui_SyncDialog):
    def __init__(self, parent, services):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self)
        self.services = services
        query = """
                SELECT concat(code, ' - ', name)
                FROM rbService
                WHERE id IN (%s)
                """%', '.join([str(id) for id in self.services])
        result = QtGui.qApp.db.query(query)
        while result.next():
            self.serviceList.addItem(result.record().value(0).toString())


    def startImport(self):
        db = QtGui.qApp.db
        error = self.runScript(synchronizeActionTypes_create_sql.COMMAND.split('\n'))
        if not error:
            self.log.append(u'Определение номенклатурных услуг...')
            result = db.query("""
                            INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
                            SELECT  rbService.code AS code,
                                    rbService.name AS name,
                                    NULL AS `parentCode`,
                                    0 AS `level`,
                                    rbServiceType.`class` AS `class`
                            FROM rbService
                            LEFT JOIN rbServiceType ON rbServiceType.section = LEFT(rbService.code, 1) AND rbServiceType.code = SUBSTR(rbService.code FROM 2 FOR 2)
                            WHERE rbService.nomenclatureLegacy = 1
                            AND rbService.id IN (%s)
                          """%', '.join([str(id) for id in self.services]))
            self.log.append(u'Определение прочих услуг...')
            result = db.query("""
                            INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
                            SELECT  rbService.code AS code,
                                    rbService.name AS name,
                                    '-' AS `parentCode`,
                                    2 AS `level`,
                                    3 AS `class`
                            FROM rbService
                            WHERE rbService.nomenclatureLegacy = 0
                            AND rbService.id IN (%s)
                          """%', '.join([str(id) for id in self.services]))
            error = self.runScript(synchronizeActionTypes_sql.COMMAND.split('\n'), {'person_id':QtGui.qApp.userId,
         'updateNames': int(self.checkUpdateNames.isChecked()),
         'compareDeleted': int(self.checkCompareDeleted.isChecked())})
        if error != None:
            QtGui.QMessageBox.warning(self, u'Импорт услуг',
                        u'Ошибка при импорте услуг:\n%s.'%error.text())
            self.log.append(unicode(error.text()))


#
# ##########################################################################
#

class CServiceContentsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbService_Contents', 'id', 'master_id', parent)
        self.addCol(CCodeNameInDocTableCol(u'Услуга', 'service_id', 40, rbService, prefferedWidth=100))
        self.addCol(CBoolInDocTableCol(u'Обязательно', 'required', 10))


class CMedicalAidProfilesModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbService_Profile', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Специальность',  'speciality_id', 20, 'rbSpeciality', showFields=CRBComboBox.showName))
        self.addCol(CEnumInDocTableCol(u'Пол', 'sex', 5, SexList))
        self.addCol(CInDocTableCol(u'Возраст', 'age', 12))
        self.addCol(CInDocTableCol(u'Код МКБ', 'mkbRegExp', 12))
        self.addCol(CRBInDocTableCol(u'Профиль', 'medicalAidProfile_id', 20, 'rbMedicalAidProfile', showFields=CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(u'Вид', 'medicalAidKind_id', 20, 'rbMedicalAidKind', showFields=CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(u'Тип', 'medicalAidType_id', 20, 'rbMedicalAidType', showFields=CRBComboBox.showName))
        self.addCol(CRBInDocTableCol(u'Профиль события', 'eventProfile_id', 20, 'rbEventProfile', showFields=CRBComboBox.showName))

class CServiceGoalModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbService_Goal', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(   u'Цель',  'goal_id', 20, 'rbEventGoal', showFields = CRBComboBox.showName))

class CMKBModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbService_MKB', 'id', 'master_id', parent)
        self.addCol(CICDExInDocTableCol(u'МКБ', 'mkb', 10,))
#
# ##########################################################################
#

class CRBServiceEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbService)
        self.addModels('Services', CServiceContentsModel(self))
        self.addModels('MedicalAidProfiles', CMedicalAidProfilesModel(self))
        self.addModels('Goals', CServiceGoalModel(self))
        self.addModels('MKB', CMKBModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Услуга')
        self.cmbServiceGroup.setTable('rbServiceGroup')
        self.cmbMedicalAidProfile.setTable('rbMedicalAidProfile')
        self.cmbMedicalAidKind.setTable('rbMedicalAidKind')
        self.cmbMedicalAidType.setTable('rbMedicalAidType')
        self.cmbServiceCategory.setTable('rbServiceCategory')
        self.setModels(self.tblServices, self.modelServices, self.selectionModelServices)
        self.setModels(self.tblMedicalAidProfiles, self.modelMedicalAidProfiles, self.selectionModelMedicalAidProfiles)
        self.setModels(self.tblGoals, self.modelGoals, self.selectionModelGoals)
        self.setModels(self.tblMKB, self.modelMKB, self.selectionModelMKB)
        self.tblMedicalAidProfiles.addMoveRow()
        self.tblMedicalAidProfiles.addPopupDelRow()
        self.tblGoals.addMoveRow()
        self.tblGoals.addPopupDelRow()
        self.tblMKB.addMoveRow()
        self.tblMKB.addPopupDelRow()
        self.tblServices.addMoveRow()
        self.tblServices.addPopupDelRow()
        self.cmbCaseCast.setTable('rbCaseCast')

        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setRBComboBoxValue(self.cmbServiceGroup, record, 'group_id')
        setLineEditValue(self.edtCode, record, rbCode)
        setTextEditValue(self.edtName, record, rbName)
        setCheckBoxValue(self.chkeisLegacy, record, 'eisLegacy')
        setCheckBoxValue(self.chkNomenclatureLegacy, record, 'nomenclatureLegacy')
        setComboBoxValue(self.cmbLicense, record, 'license')
        setRBComboBoxValue(self.cmbCaseCast, record, 'caseCast_id')
        setLineEditValue(self.edtInfis, record, 'infis')
        setDateEditValue(self.edtBegDate, record, 'begDate')
        setDateEditValue(self.edtEndDate, record, 'endDate')
        setDoubleBoxValue(self.edtUetAdultDoctor,           record, 'adultUetDoctor')
        setDoubleBoxValue(self.edtUetChildDoctor,           record, 'childUetDoctor')
        setDoubleBoxValue(self.edtUetAdultAvarageMedWorker, record, 'adultUetAverageMedWorker')
        setDoubleBoxValue(self.edtUetChildAvarageMedWorker, record, 'childUetAverageMedWorker')
        setDoubleBoxValue(self.edtQualityLevel,             record, 'qualityLevel')
        setDoubleBoxValue(self.edtSuperviseComplexityFactor,record, 'superviseComplexityFactor')

        if isComplexService(self.edtCode.text()):
            self.modelServices.loadItems(self.itemId())
            self.tblServices.show()
        else:
            self.tblServices.hide()

        setRBComboBoxValue(self.cmbMedicalAidProfile, record, 'medicalAidProfile_id')
        setRBComboBoxValue(self.cmbMedicalAidKind,    record, 'medicalAidKind_id')
        setRBComboBoxValue(self.cmbMedicalAidType,    record, 'medicalAidType_id')
        setRBComboBoxValue(self.cmbServiceCategory, record, 'category_id')
        self.modelMedicalAidProfiles.loadItems(self.itemId())
        self.modelGoals.loadItems(self.itemId())
        self.modelMKB.loadItems(self.itemId())

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)

        getRBComboBoxValue(self.cmbServiceGroup, record, 'group_id')
        getLineEditValue(self.edtCode, record, rbCode)
        getTextEditValue(self.edtName, record, rbName)
        getCheckBoxValue(self.chkeisLegacy, record, 'eisLegacy')
        getCheckBoxValue(self.chkNomenclatureLegacy, record, 'nomenclatureLegacy')
        getComboBoxValue(self.cmbLicense, record, 'license')
        getRBComboBoxValue(self.cmbCaseCast, record, 'caseCast_id')
        getLineEditValue(self.edtInfis, record, 'infis')
        getDateEditValue(self.edtBegDate, record, 'begDate')
        getDateEditValue(self.edtEndDate, record, 'endDate')
        getDoubleBoxValue(self.edtUetAdultDoctor,           record, 'adultUetDoctor')
        getDoubleBoxValue(self.edtUetChildDoctor,           record, 'childUetDoctor')
        getDoubleBoxValue(self.edtUetAdultAvarageMedWorker, record, 'adultUetAverageMedWorker')
        getDoubleBoxValue(self.edtUetChildAvarageMedWorker, record, 'childUetAverageMedWorker')
        getDoubleBoxValue(self.edtQualityLevel, record, 'qualityLevel')
        getDoubleBoxValue(self.edtSuperviseComplexityFactor,  record, 'superviseComplexityFactor')
        getRBComboBoxValue(self.cmbMedicalAidProfile, record, 'medicalAidProfile_id')
        getRBComboBoxValue(self.cmbMedicalAidKind,    record, 'medicalAidKind_id')
        getRBComboBoxValue(self.cmbMedicalAidType, record, 'medicalAidType_id')
        getRBComboBoxValue(self.cmbServiceCategory, record, 'category_id')
        return record

    def saveInternals(self, id):
        self.modelServices.saveItems(id)
        self.modelMedicalAidProfiles.saveItems(id)
        self.modelGoals.saveItems(id)
        self.modelMKB.saveItems(id)

    def checkDataEntered(self):
        result = True
        code    = forceStringEx(self.edtCode.text())
        name    = forceStringEx(self.edtName.toPlainText())
        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and self.checkMedicalAidProfiles()
        return result

    def checkMedicalAidProfiles(self):
        result = True
        for i, item in enumerate(self.modelMedicalAidProfiles.items()):
            age = forceString(item.value('age'))
            mkbRegExp = forceString(item.value('mkbRegExp'))
            mkbRegExpIsValid = not mkbRegExp or QtCore.QRegExp(mkbRegExp).isValid()
            profileId = forceRef(item.value('medicalAidProfile_id'))
            result = result and (checkAgeSelectorSyntax(age) or self.checkValueMessage(u'Диапазон возрастов указан неверно', False, self.tblMedicalAidProfiles, i, 1))
            result = result and (mkbRegExpIsValid or self.checkValueMessage(u'Регулярное выражение кода МКБ указано неверно', False, self.tblMedicalAidProfiles, i, 2))
            result = result and (profileId or self.checkInputMessage(u'профиль', False, self.tblMedicalAidProfiles, i, 3))
            if not result:
                break
        return  result

#
# ##########################################################################
#


class CServiceFilterDialog(QtGui.QDialog, Ui_ServiceFilterDialog):
    def __init__(self,  parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbServiceGroup.setTable('rbServiceGroup')
        self.cmbSection.setTable('rbServiceSection')
        self.cmbSection.setFilter(order='id') # чтобы русские А и В не шли после D и F
        self.cmbType.setTable('rbServiceType')
        self.cmbClass.setTable('rbServiceClass')
        self.edtBegDate.canBeEmpty(True)
        self.edtEndDate.canBeEmpty(True)
        self.edtCode.setFocus(QtCore.Qt.ShortcutFocusReason)
        QtCore.QObject.connect(self.cmbSection, QtCore.SIGNAL('currentIndexChanged(int)'), self.on_cmbSection_currentIndexChanged)
        self.updateTypesClasses()


    def setProps(self,  props):
        self.cmbServiceGroup.setValue(props.get('group', 0))
        self.cmbSection.setValue(props.get('section', 0))
        self.cmbType.setValue(props.get('type', 0))
        self.cmbClass.setValue(props.get('class', 0))
        self.edtCode.setText(props.get('code', ''))
        self.edtName.setText(props.get('name', ''))
        self.chkEIS.setCheckState(props.get('EIS', QtCore.Qt.PartiallyChecked))
        self.chkNomenclature.setCheckState(props.get('nomenclature', QtCore.Qt.PartiallyChecked))
        self.edtBegDate.setDate(props.get('begDate', QtCore.QDate()))
        self.edtEndDate.setDate(props.get('endDate', QtCore.QDate()))


    def props(self):
        result = {}
        result['group'] = forceRef(self.cmbServiceGroup.value())
        result['section'] = forceRef(self.cmbSection.value())
        result['type'] = forceRef(self.cmbType.value())
        result['class'] = forceRef(self.cmbClass.value())
        result['code'] = forceStringEx(self.edtCode.text())
        result['name'] = forceStringEx(self.edtName.text())
        result['EIS'] = self.chkEIS.checkState()
        result['nomenclature'] = self.chkNomenclature.checkState()
        result['begDate'] = forceDate(self.edtBegDate.date())
        result['endDate'] = forceDate(self.edtEndDate.date())
        return result


    def updateTypesClasses(self):
        code = self.cmbSection.code()
        if code and code != "0":
            self.edtCode.setText(code)
            self.cmbType.setEnabled(True)
            self.cmbType.setFilter('section="%s"'%code)
            if code in (u'А', u'В'):
                self.cmbClass.setEnabled(True)
                self.cmbClass.setFilter('section="%s"'%code)
            else:
                self.cmbClass.setEnabled(False)
        else:
            self.cmbType.setValue(0)
            self.cmbType.setEnabled(False)
            self.cmbClass.setValue(0)
            self.cmbClass.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_cmbSection_currentIndexChanged(self):
        self.updateTypesClasses()
