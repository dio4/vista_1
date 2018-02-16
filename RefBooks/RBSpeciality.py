# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from RefBooks.SelectService import selectService
from RefBooks.Tables import rbCode, rbName, rbService, rbSpeciality
from Ui_RBSpecialityEditor import Ui_ItemEditorDialog
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.ItemCol import CIntColEditor, CItemCol, Index
from library.ItemListModel import CItemListModel
from library.ItemsListDialog import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel import CEnumCol, CRefBookCol, CTextCol
from library.Utils import forceInt, forceString, forceStringEx, toVariant
from library.interchange import getComboBoxValue, getLineEditValue, getRBComboBoxValue, setComboBoxValue, \
    setLineEditValue, setRBComboBoxValue


class CRBSpecialityList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', [rbCode], 10),
            CTextCol(u'Наименование', [rbName], 30),
            CTextCol(u'Краткое наименование', ['shortName'], 30),
            CTextCol(u'Код ОКСО', ['OKSOCode'], 10),
            CTextCol(u'Наименование ОКСО', ['OKSOName'], 30),
            CTextCol(u'Федеральный код', ['federalCode'], 10),
            CTextCol(u'Региональный код', ['regionalCode'], 10),
            CRefBookCol(u'Услуга', ['service_id'], 'rbService', 30),
            CEnumCol(u'Пол', ['sex'], ['', u'М', u'Ж'], 10),
            CTextCol(u'Возраст', ['age'], 10),
            CTextCol(u'Фильтр по МКБ', ['mkbFilter'], 20),
            CTextCol(u'Версия справочника', ['versSpec'], 20),
        ], rbSpeciality, [rbCode, rbName])
        self.setWindowTitleEx(u'Специальности врачей')

    def getItemEditor(self):
        return CRBSpecialityEditor(self)


class CRBSpecialityQueueShareModel(CItemListModel):
    u""" Доступная доля номерков по дням начиная с текущей даты (в %)
         для данной специальности """
    DayCount = 14

    def __init__(self, parent):
        super(CRBSpecialityQueueShareModel, self).__init__(parent)
        self.setCols([CItemCol(unicode(day + 1),
                               handler=Index(day),
                               editor=CIntColEditor(min=0, max=100),
                               editable=True)
                      for day in range(self.DayCount)])
        self.addCol(CItemCol(u''))
        self.setEditable(True)

    def newItem(self):
        return [100] * self.DayCount

    def rowCount(self, parentIndex=None, *args, **kwargs):
        return 1

    def save(self, specialityId):
        if specialityId:
            db = QtGui.qApp.db
            tableSpecialityQS = db.table('rbSpecialityQueueShare')
            values = self.items()[0] if self.items() else []

            db.deleteRecord(tableSpecialityQS, tableSpecialityQS['speciality_id'].eq(specialityId))
            db.insertFromDictList(tableSpecialityQS, [{'day'          : day,
                                                       'available'    : available,
                                                       'speciality_id': specialityId}
                                                      for day, available in enumerate(values)])

    def load(self, specialityId):
        if specialityId:
            db = QtGui.qApp.db
            tableSpecialityQS = db.table('rbSpecialityQueueShare')

            available = [forceInt(rec.value('available'))
                         for rec in db.iterRecordList(tableSpecialityQS,
                                                      cols=tableSpecialityQS['available'],
                                                      where=tableSpecialityQS['speciality_id'].eq(specialityId),
                                                      order=tableSpecialityQS['day'])]
            if available:
                available.extend([0] * (self.DayCount - len(available)))
                self.setItems([available])


class CRBSpecialityEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, rbSpeciality)
        self.addModels('QueueShare', CRBSpecialityQueueShareModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Специальность врача')
        self.cmbLocalService.setTable(rbService, True)
        self.cmbLocalService.setCurrentIndex(0)
        self.cmbProvinceService.setTable(rbService, True)
        self.cmbProvinceService.setCurrentIndex(0)
        self.cmbOtherService.setTable(rbService, True)
        self.cmbOtherService.setCurrentIndex(0)
        self.cmbFundingService.setTable(rbService, True)
        self.cmbFundingService.setCurrentIndex(0)
        self.cmbVersSpec.setCurrentIndex(0)
        self.cmbSex.setCurrentIndex(0)
        self.setModels(self.tblQueueShare, self.modelQueueShare, self.selectionModelQueueShare)
        self.tblQueueShare.resizeColumnsToContents()
        self.tblQueueShare.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setupDirtyCather()

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'code')
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtShortName, record, 'shortName')
        setLineEditValue(self.edtOKSOName, record, 'OKSOName')
        setLineEditValue(self.edtOKSOCode, record, 'OKSOCode')
        setLineEditValue(self.edtFederalCode, record, 'federalCode')
        setLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        setLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        setRBComboBoxValue(self.cmbLocalService, record, 'service_id')
        setRBComboBoxValue(self.cmbProvinceService, record, 'provinceService_id')
        setRBComboBoxValue(self.cmbOtherService, record, 'otherService_id')
        setRBComboBoxValue(self.cmbFundingService, record, 'fundingService_id')
        setComboBoxValue(self.cmbSex, record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        versSpec = forceStringEx(record.value('versSpec'))
        self.cmbVersSpec.setCurrentIndex({'v004': 1,
                                          'v015': 2}.get(versSpec.lower(), 0))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))
        setLineEditValue(self.edtMKBFilter, record, 'mkbFilter')
        self.modelQueueShare.load(self.itemId())

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtShortName, record, 'shortName')
        getLineEditValue(self.edtOKSOName, record, 'OKSOName')
        getLineEditValue(self.edtOKSOCode, record, 'OKSOCode')
        getLineEditValue(self.edtFederalCode, record, 'federalCode')
        getLineEditValue(self.edtRegionalCode, record, 'regionalCode')
        getLineEditValue(self.edtSyncGUID, record, 'syncGUID')
        getRBComboBoxValue(self.cmbLocalService, record, 'service_id')
        getRBComboBoxValue(self.cmbProvinceService, record, 'provinceService_id')
        getRBComboBoxValue(self.cmbOtherService, record, 'otherService_id')
        getRBComboBoxValue(self.cmbFundingService, record, 'fundingService_id')
        getComboBoxValue(self.cmbSex, record, 'sex')
        record.setValue('age', toVariant(composeAgeSelector(
            self.cmbBegAgeUnit.currentIndex(),
            forceStringEx(self.edtBegAgeCount.text()),
            self.cmbEndAgeUnit.currentIndex(),
            forceStringEx(self.edtEndAgeCount.text())
        )))
        record.setValue('versSpec', toVariant({0: '',
                                               1: 'V004',
                                               2: 'V015'}.get(self.cmbVersSpec.currentIndex(), '')))
        getLineEditValue(self.edtMKBFilter, record, 'mkbFilter')
        return record

    def saveInternals(self, specialityId):
        self.modelQueueShare.save(specialityId)

    def selectService(self, cmbService):
        serviceId = selectService(self, cmbService)
        cmbService.update()
        if serviceId:
            cmbService.setValue(serviceId)

    @QtCore.pyqtSlot()
    def on_btnSelectLocalService_clicked(self):
        self.selectService(self.cmbLocalService)

    @QtCore.pyqtSlot()
    def on_btnSelectProvinceService_clicked(self):
        self.selectService(self.cmbProvinceService)

    @QtCore.pyqtSlot()
    def on_btnSelectOtherService_clicked(self):
        self.selectService(self.cmbOtherService)

    @QtCore.pyqtSlot()
    def on_btnSelectFundingService_clicked(self):
        self.selectService(self.cmbFundingService)
