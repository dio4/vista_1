# -*- coding: utf-8 -*-
import re
from PyQt4 import QtGui, QtCore

from RefBooks.SelectService import selectService
from RefBooks.Tables import rbService
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog
from Ui_MKBEditor import Ui_ItemEditorDialog
from Ui_MKBFinder import Ui_ItemFinderDialog
from library.AgeSelector import composeAgeSelector, parseAgeSelector
from library.DialogBase import CDialogBase
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.ICDTree import CICDTreeModel
from library.InDocTable import CInDocTableModel, CRBInDocTableCol, CRBInDocTableColSearch
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CTableModel, CEnumCol, CRefBookCol, CTextCol, CDesignationCol
from library.Utils import forceBool, forceDate, forceInt, forceString, forceStringEx, toVariant, forceRef
from library.interchange import getComboBoxValue, getLineEditValue, getRBComboBoxValue, getSpinBoxValue, \
    getTextEditValue, setComboBoxValue, setLineEditValue, setRBComboBoxValue, \
    setSpinBoxValue, setTextEditValue

# 1 острое
# 2 хроническое впервые установленное
# 3 хроническое известное
# 4 обострение хронического

MapMKBCharactersToCharacterCode = [
    (u'нет', []),                                            # 0
    (u'острое', ['1', '5']),                                 # 1
    (u'хроническое впервые выявленное', ['2', '5']),         # 2
    (u'хроническое ранее известное', ['3', '5']),            # 3
    (u'обострение хронического', ['4', '5']),                # 4
    (u'хроническое', ['3', '2', '4', '5']),                  # 5 такой порядок - для выбора 3 "по умолчанию"
    (u'хроническое или острое', ['3', '1', '2', '4', '5']),  # 6 idem
    (u'все', ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])  # 7
]

MapMKBCharactersToCharacterCodeForDiagnosis = [
    (u'нет', []),                                      # 0
    (u'острое', ['1']),                                # 1
    (u'хроническое впервые выявленное', ['3']),        # 2
    (u'хроническое ранее известное', ['3']),           # 3
    (u'обострение хронического', ['3']),               # 4
    (u'хроническое', ['3']),                           # 5 такой порядок - для выбора 3 "по умолчанию"
    (u'хроническое или острое', ['3', '1']),           # 6 idem
    (u'все', ['1', '3'])                               # 7
]

MKBCharacters = [t[0] for t in MapMKBCharactersToCharacterCode]
MKBCharactersForDiagnosis = [t[0] for t in MapMKBCharactersToCharacterCodeForDiagnosis]

SexList = ['', u'М', u'Ж']


class CMKBList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CDesignationCol(u'Класс', ['id'],
                            ('Select id, getMKBClassID(DiagID) as ClassID from MKB_Tree as MKB2', 'ClassID'), 10),
            CDesignationCol(u'Блок', ['id'],
                            ('Select id, getMKBBlockID(DiagID) as BlockID from MKB_Tree as MKB2', 'BlockID'), 10),
            CTextCol(u'Код', ['DiagID'], 10),
            CTextCol(u'Прим', ['Prim'], 3),
            CTextCol(u'Наименование', ['DiagName'], 40),
            CEnumCol(u'Характер', ['characters'], MKBCharacters, 10),
            CEnumCol(u'Пол', ['sex'], SexList, 10),
            CTextCol(u'Возраст', ['age'], 10),
            CTextCol(u'Длительность', ['duration'], 4),
            CRefBookCol(u'Субклассификация', ['MKBSubclass_id'], 'rbMKBSubclass', 10),
            CRefBookCol(u'Базовая услуга', ['service_id'], rbService, 30),
        ], 'MKB_Tree', ['DiagID'])
        self.expandedItemsState = {}
        self.setWindowTitleEx(u'Коды МКБ X')
        self.props = {}
        self.tblItems.addPopupDelRow()

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CICDTreeModel(self, viewAll=True))
        self.addModels('Table', CTableModel(self, self.cols, self.tableName))

        self.findClass = self.getItemFinder()

    def postSetupUi(self):
        self.setModels(self.treeItems, self.modelTree, self.selectionModelTree)
        self.setModels(self.tblItems, self.modelTable, self.selectionModelTable)
        self.btnSelect.setEnabled(self.forSelect)
        self.btnSelect.setVisible(self.forSelect)
        self.btnSelect.setDefault(self.forSelect)
        self.btnFilter.setEnabled(bool(self.filterClass))
        self.btnFilter.setVisible(bool(self.filterClass))
        self.btnFind.setEnabled(bool(self.findClass))
        self.btnFind.setVisible(bool(self.findClass))
        self.btnEdit.setDefault(not self.forSelect)
        self.btnNew.setShortcut(QtCore.Qt.Key_F9)
        self.btnEdit.setShortcut(QtCore.Qt.Key_F4)
        # self.btnPrint.setShortcut(QtCore.Qt.Key_F6)

        QtCore.QObject.connect(
            self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)

    def exec_(self):
        self.renewListAndSetTo()
        result = CDialogBase.exec_(self)
        clearCache()
        return result

    def select(self, props):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        return QtGui.qApp.db.getIdList(table.name(),
                                       'id',
                                       table['parent_code'].eq(groupId),
                                       self.order)

    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)

    def currentItemId(self):
        return self.tblItems.currentItemId()

    def currentGroupId(self):
        return self.modelTree.diag(self.treeItems.currentIndex())

    def setSort(self, col):
        name = self.modelTable.cols()[col].fields()[0]
        self.order = name
        header = self.tblItems.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)
        self.renewListAndSetTo()

    def renewListAndSetTo(self, itemId=None):
        if itemId is None:
            itemId = self.currentItemId()
        idList = self.select(self.props)
        try:
            i = idList.index(itemId)
        except:
            i = 0

        self.modelTable.setIdList(idList)
        self.tblItems.setCurrentRow(max(0, i))

    def getItemEditor(self):
        return CMKBEditor(self)

    def getItemFinder(self, isFilter=False):
        return CMKBFinder(self, isFilter)

    def updateFieldInSelectedRecord(self, fieldName, fieldValue):
        db = QtGui.qApp.db
        tableMKB = db.table('MKB_Tree')
        indexList = self.tblItems.selectedIndexes()
        rows = set()
        for index in indexList:
            rows.add(index.row())
        idList = self.modelTable.idList()
        for row in rows:
            id = idList[row]
            record = db.getRecord(tableMKB, ['id', fieldName], id)
            if record:
                record.setValue(fieldName, fieldValue)
                db.updateRecord(tableMKB, record)
        self.modelTable.invalidateRecordsCache()
        self.tblItems.clearSelection()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        self.on_btnEdit_clicked()

    @QtCore.pyqtSlot()
    def on_btnCharacters_clicked(self):
        item, ok = QtGui.QInputDialog.getItem(self, u'Выбери', u'Характер', MKBCharacters, 0, False)
        item = forceString(item)
        if ok and item in MKBCharacters:
            self.updateFieldInSelectedRecord('characters', QtCore.QVariant(MKBCharacters.index(item)))

    @QtCore.pyqtSlot()
    def on_btnSex_clicked(self):
        item, ok = QtGui.QInputDialog.getItem(self, u'Выбери', u'Пол', SexList, 0, False)
        item = forceString(item)
        if ok and item in SexList:
            self.updateFieldInSelectedRecord('sex', QtCore.QVariant(SexList.index(item)))

    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dlg = self.getItemEditor()
            dlg.load(itemId)
            if dlg.exec_():
                itemId = dlg.itemId()
                self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.parentCode = self.currentGroupId()
        if dialog.exec_():
            itemId = dialog.itemId()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        dialog = self.getItemFinder(isFilter=True)
        dialog.parentCode = self.currentGroupId()
        if dialog.exec_():
            itemId = dialog.itemId()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnFind_clicked(self):
        dialog = self.getItemFinder()
        dialog.parentCode = self.currentGroupId()
        if dialog.exec_():
            self.modelTable.setIdList(dialog.idList)
        else:
            if dialog.idList:
                self.modelTable.setIdList(dialog.idList)

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        tbl = self.tblItems
        tbl.setReportHeader(u'Коды МКБ X')
        txt = u''
        codeStart = forceString(self.edtCode.text())
        if codeStart:
            txt += u'код начинается на "%s"\n' % codeStart
        namePart = forceString(self.edtName.text())
        if namePart:
            txt += u'название диагноза содержит "%s"\n' % namePart
        tbl.setReportDescription(txt)
        tbl.printContent()

    @QtCore.pyqtSlot()
    def on_btnPrintSelected_clicked(self):
        tbl = self.tblItems

        model = tbl.model()

        report = CReportBase()
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Коды МКБ X\n')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(tbl.reportDescription())
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
                format = QtGui.QTextBlockFormat()
                format.setAlignment(QtCore.Qt.AlignmentFlag(colAlingment))
                tableColumns.append((widthInPercents, [forceString(col.title())], format))

        table = createTable(cursor, tableColumns)
        for index in tbl.selectedIndexes():
            iModelRow = index.row()
            if index.column():
                continue
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

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textChanged(self, text):
        self.renewListAndSetTo()

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtName_textChanged(self, text):
        self.renewListAndSetTo()


class CMKBFinder(CItemEditorBaseDialog, Ui_ItemFinderDialog):
    def __init__(self, parent, isFilter=False):
        CItemEditorBaseDialog.__init__(self, parent, 'MKB_Tree')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Фильтр МКБ Х') if isFilter else self.setWindowTitleEx(u'Поиск МКБ Х')
        self.cmbMKBSubclass.setTable('rbMKBSubclass', True)
        self.cmbService.setTable(rbService, True)
        self.cmbCharacters.addItems(MKBCharacters)
        self.cmbCharacters.setCurrentIndex(0)
        self.cmbSex.setCurrentIndex(0)
        self.setIsDirty(False)
        self.setupDirtyCather()
        self.prevCode = None
        self.parentCode = None
        self.isFilter = isFilter
        if self.isFilter:
            self.chkName.setVisible(False)
            self.edtName.setVisible(False)
        self.props = {}

    def setRecord(self, record):
        pass

    def getRecord(self):
        pass

    def checkDataEntered(self):
        return False
        result = True
        code = forceStringEx(self.edtCode.text())
        name = forceStringEx(self.edtName.toPlainText())
        isBlock = not forceBool(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', self.parentCode, 'parent_code'))
        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and ((re.match(r'^[A-Z]\d{2}(\.\d+)?$', code) and not isBlock)
                             or (re.match(r'^\([A-Z]\d{2}\-[A-Z]\d{2}\)$', code) and isBlock)
                             or self.checkInputMessage(u'код правильно', False, self.edtCode))
        checkMKB = self.checkMKBCode(code, self.parentCode)
        result = result and (checkMKB == u'Ok' or self.checkValueMessage(checkMKB, False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and (not self.prevCode or self.prevCode == code or self.checkValueMessage(
            u'Код МКБ изменён. Предыдущее значение "%s"' % self.prevCode, True, self.edtCode))
        return result

    def checkMKBCode(self, code, parentCode):
        db = QtGui.qApp.db
        error = u'Введённый код МКБ %s не входит в группу %s' % (code, parentCode)
        duplicate = u'Ведённый код МКБ уже существует'
        success = u'Ok'

        if not forceBool(db.translate('MKB_Tree', 'DiagID', parentCode, 'parent_code')):
            if code[1:4] > code[1:8]:
                return u'%s должно быть меньше чем %s' % (code[1:4], code[1:8])

            conds = ["parent_code = '%s'" % parentCode]
            if self.itemId():
                conds.append("not id = '%s'" % forceString(self.itemId()))
            recordList = db.getRecordList(
                'MKB_Tree',
                ['Right(Left(DiagID, 4), 3) as min', 'Left(Right(DiagID, 4), 3) as max'],
                db.joinAnd(conds)
            )
            if forceString(recordList[0].value('min')) > code[1:4] or \
                            forceString(recordList[-1].value('max')) < code[5:8]:
                return u"Ведённый диапазон %s входит в диапазон данного класса с %s-%s" % (
                    code, forceString(recordList[0].value('min')), forceString(recordList[-1].value('max')))
            for record in recordList:
                minCode = forceString(record.value('min'))
                maxCode = forceString(record.value('max'))
                if not ((minCode < code[1:4] and maxCode < code[1:4]) or (minCode > code[5:8] and maxCode > code[5:8])):
                    return u"Ведённый диапазон %s прересекается с (%s-%s)" % (code, minCode, maxCode)
            return success

        cond = ["DiagID = '%s'" % code]
        if self.itemId():
            cond.append("not id = '%s'" % forceString(self.itemId()))
        if forceBool(QtGui.qApp.db.getRecordEx('MKB_Tree', 'DiagID', db.joinAnd(cond))):
            return duplicate

        if len(code) == 3:
            if parentCode[1] == code[0] \
                    and forceInt(parentCode[2:4]) <= forceInt(code[1:3]) \
                    and forceInt(parentCode[6:8]) >= forceInt((code[1:3])):
                return success

        elif len(code) > 3:
            if parentCode in code:
                return success
            return error
        return error

    def saveInternals(self, id):
        pass

    @QtCore.pyqtSlot()
    def on_btnSelectService_clicked(self):
        serviceId = selectService(self, self.cmbService)
        self.cmbService.update()
        if serviceId:
            self.cmbService.setValue(serviceId)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textChanged(self, text):
        code = forceStringEx(text)
        if not bool(re.match(r'^[A-Z]\d{2}(\.\d)?$', code)):
            self.cmbMKBSubclass.setEnabled(False)
            self.chkMKBSubclass.setEnabled(False)
            self.chkMKBSubclass.setChecked(False)
        else:
            self.cmbMKBSubclass.setEnabled(True)
            self.chkMKBSubclass.setEnabled(True)

    def canClose(self):
        self.close()

    def setCond(self, cond, newcond):
        if newcond is not None:
            if cond == '':
                return newcond + u'\n'
            else:
                return u' AND ' + newcond + u'\n'
        else:
            return u''

    def save(self):
        cond = ''
        if self.chkCode.isChecked():
            cond += self.setCond(cond, u"`DiagID` LIKE %s" % u"'%" + self.edtCode.text() + u"%'")

        if self.chkPrim.isChecked():
            cond += self.setCond(cond, u"`Prim` = '*'")

        if self.chkName.isChecked():
            cond += self.setCond(cond, u"`DiagName` LIKE %s" % u"'%" + self.edtName.toPlainText() + u"%'")

        if self.chkMKBSubclass.isChecked() and self.cmbMKBSubclass.value() is not None:
            cond += self.setCond(cond, u'`MKBSubclass_id` = %s' % self.cmbMKBSubclass.value())

        if self.chkCharacters.isChecked():
            cond += self.setCond(cond, u'`characters` = %s' % self.cmbCharacters.currentIndex())

        if self.chkSex.isChecked():
            cond += self.setCond(cond, u'`sex` = %s' % self.cmbSex.currentIndex())

        if self.chkAge.isChecked():
            cond += self.setCond(
                cond,
                u'`age` = \'%s\'' % (
                    composeAgeSelector(
                        self.cmbBegAgeUnit.currentIndex(), forceStringEx(self.edtBegAgeCount.text()),
                        self.cmbEndAgeUnit.currentIndex(), forceStringEx(self.edtEndAgeCount.text())
                    )
                )
            )

        if self.chkDuration.isChecked():
            cond += self.setCond(cond, u'`duration` = %s' % self.edtDuration.value())

        if self.chkService.isChecked() and self.cmbService.value() is not None:
            cond += self.setCond(cond, u'`service_id` = %s' % self.cmbService.value())

        if self.chkBegDate.isChecked():
            cond += self.setCond(
                cond,
                u"`begDate` = '%s-%s-%s'" % (
                    self.edtBegDate.date().year(),
                    self.edtBegDate.date().month(),
                    self.edtBegDate.date().day()
                )
            )

        if self.chkEndDate.isChecked():
            cond += self.setCond(
                cond,
                u"`endDate` = '%s-%s-%s'" % (
                    self.edtEndDate.date().year(),
                    self.edtEndDate.date().month(),
                    self.edtEndDate.date().day()
                )
            )

        if self.chkOMSMTR.isChecked():
            if self.chkOMS.isChecked():
                cond += self.setCond(cond, u'`OMS` = 1')
            else:
                cond += self.setCond(cond, u'`OMS` = 0')

            if self.chkMTR.isChecked():
                cond += self.setCond(cond, u'`MTR` = 1')
            else:
                cond += self.setCond(cond, u'`MTR` = 0')

        return cond

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        db = QtGui.qApp.db
        cond = self.save()
        self.idList = [
            forceRef(x.value('id'))
            for x in db.getRecordList(table=None, stmt=u"""
                SELECT
                    `id`
                FROM
                    MKB_Tree
                WHERE
                    %s
                """ % cond
            )
        ]
        self.close()

    def closeEvent(self, event):
        event.accept()
        return


class CServiceSpecialtyModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'MKBServiceSpeciality', 'id', 'mkb_id', parent)
        self.addCol(CRBInDocTableCol(u'Специальность', 'speciality_id', 10, 'rbSpeciality', prefferedWidth=150))
        self.addCol(CRBInDocTableColSearch(
            u'Услуга',
            'service_id',
            10,
            'rbService',
            prefferedWidth=150
        ))


class CMKBEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'MKB_Tree')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Код МКБ Х')
        self.cmbMKBSubclass.setTable('rbMKBSubclass', True)
        self.addModels('ServiceSpecialty', CServiceSpecialtyModel(self))
        self.setModels(self.tblServiceSpecialty, self.modelServiceSpecialty, self.selectionModelServiceSpecialty)
        self.tblServiceSpecialty.addMoveRow()
        self.tblServiceSpecialty.addPopupDelRow()
        self.cmbCharacters.addItems(MKBCharacters)
        self.cmbCharacters.setCurrentIndex(0)
        self.cmbSex.setCurrentIndex(0)
        self.setIsDirty(False)
        self.setupDirtyCather()
        self.prevCode = None
        self.parentCode = None
        self.connect(
            self.modelServiceSpecialty, QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
            self.on_modelServiceSpecialty_dataChanged
        )

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtCode, record, 'DiagID')
        self.chkPrim.setChecked(bool(forceString(record.value('Prim'))))
        setTextEditValue(self.edtName, record, 'DiagName')
        setRBComboBoxValue(self.cmbMKBSubclass, record, 'MKBSubclass_id')
        setComboBoxValue(self.cmbCharacters, record, 'characters')
        setComboBoxValue(self.cmbSex, record, 'sex')
        (begUnit, begCount, endUnit, endCount) = parseAgeSelector(forceString(record.value('age')))
        self.cmbBegAgeUnit.setCurrentIndex(begUnit)
        self.edtBegAgeCount.setText(str(begCount))
        self.cmbEndAgeUnit.setCurrentIndex(endUnit)
        self.edtEndAgeCount.setText(str(endCount))
        setSpinBoxValue(self.edtDuration, record, 'duration')
        self.modelServiceSpecialty.loadItems(self.itemId())
        self.edtBegDate.setDate(forceDate(record.value('begDate')))
        self.edtEndDate.setDate(forceDate(record.value('endDate')))
        self.chkOMS.setChecked(forceBool(record.value('OMS')))
        self.chkMTR.setChecked(forceBool(record.value('MTR')))
        self.prevCode = forceStringEx(self.edtCode.text())
        self.parentCode = forceString(record.value('parent_code'))

    def getRecord(self):
        db = QtGui.qApp.db
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'DiagID')
        record.setValue('Prim', QtCore.QVariant('*' if self.chkPrim.isChecked() else ''))
        getTextEditValue(self.edtName, record, 'DiagName')
        if self.cmbMKBSubclass.isEnabled():
            getRBComboBoxValue(self.cmbMKBSubclass, record, 'MKBSubclass_id')
        else:
            record.setValue('MKBSubclass_id', QtCore.QVariant())
        getComboBoxValue(self.cmbCharacters, record, 'characters')
        getComboBoxValue(self.cmbSex, record, 'sex')
        record.setValue('age', toVariant(composeAgeSelector(
            self.cmbBegAgeUnit.currentIndex(), forceStringEx(self.edtBegAgeCount.text()),
            self.cmbEndAgeUnit.currentIndex(), forceStringEx(self.edtEndAgeCount.text())
        )))
        getSpinBoxValue(self.edtDuration, record, 'duration')
        self.modelServiceSpecialty.saveItems(self.itemId())
        record.setValue('begDate', toVariant(self.edtBegDate.date()))
        record.setValue('endDate', toVariant(self.edtEndDate.date()))
        record.setValue('OMS', toVariant(self.chkOMS.isChecked()))
        record.setValue('MTR', toVariant(self.chkMTR.isChecked()))
        record.setValue('parent_code', toVariant(self.parentCode))

        clearCache()
        return record

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelServiceSpecialty_dataChanged(self, topLeft, bottomRight):
        index = topLeft.row()
        items = self.tblServiceSpecialty.model().items()[:]
        for x in range(len(items)):
            if x == index:
                continue
            elif items[index].value('speciality_id') == items[x].value('speciality_id'):
                speciality = forceString(self.modelServiceSpecialty.data(topLeft))
                QtGui.QMessageBox.warning(
                    self,
                    u'Внимание',
                    u'Нельзя добавлять для специальности "%s" разные услуги' % speciality,
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
                self.tblServiceSpecialty.model().removeRow(index)
                break

    def checkDataEntered(self):
        result = True
        code = forceStringEx(self.edtCode.text())
        name = forceStringEx(self.edtName.toPlainText())
        isBlock = not forceBool(QtGui.qApp.db.translate('MKB_Tree', 'DiagID', self.parentCode, 'parent_code'))
        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and ((re.match(r'^[A-Z]\d{2}(\.\d+)?$', code) and not isBlock)
                             or (re.match(r'^\([A-Z]\d{2}\-[A-Z]\d{2}\)$', code) and isBlock)
                             or self.checkInputMessage(u'код правильно', False, self.edtCode))
        checkMKB = self.checkMKBCode(code, self.parentCode)
        result = result and (checkMKB == u'Ok' or self.checkValueMessage(checkMKB, False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        result = result and (not self.prevCode or self.prevCode == code or self.checkValueMessage(
            u'Код МКБ изменён. Предыдущее значение "%s"' % self.prevCode, True, self.edtCode))
        return result

    def checkMKBCode(self, code, parentCode):
        db = QtGui.qApp.db
        error = u'Введённый код МКБ %s не входит в группу %s' % (code, parentCode)
        duplicate = u'Ведённый код МКБ уже существует'
        success = u'Ok'

        if not forceBool(db.translate('MKB_Tree', 'DiagID', parentCode, 'parent_code')):
            if code[1:4] > code[1:8]:
                return u'%s должно быть меньше чем %s' % (code[1:4], code[1:8])

            conds = ["parent_code = '%s'" % parentCode]
            if self.itemId():
                conds.append("not id = '%s'" % forceString(self.itemId()))
            recordList = db.getRecordList(
                'MKB_Tree',
                ['Right(Left(DiagID, 4), 3) as min', 'Left(Right(DiagID, 4), 3) as max'],
                db.joinAnd(conds)
            )
            if forceString(recordList[0].value('min')) > code[1:4] or forceString(recordList[-1].value('max')) < code[
                                                                                                                 5:8]:
                return u"Ведённый диапазон %s входит в диапазон данного класса с %s-%s" % (
                    code, forceString(recordList[0].value('min')), forceString(recordList[-1].value('max')))
            for record in recordList:
                minCode = forceString(record.value('min'))
                maxCode = forceString(record.value('max'))
                if not ((minCode < code[1:4] and maxCode < code[1:4]) or (minCode > code[5:8] and maxCode > code[5:8])):
                    return u"Ведённый диапазон %s прересекается с (%s-%s)" % (code, minCode, maxCode)
            return success

        cond = ["DiagID = '%s'" % code]
        if self.itemId():
            cond.append("not id = '%s'" % forceString(self.itemId()))
        if forceBool(QtGui.qApp.db.getRecordEx('MKB_Tree', 'DiagID', db.joinAnd(cond))):
            return duplicate

        if len(code) == 3:
            if parentCode[1] == code[0] \
                    and forceInt(parentCode[2:4]) <= forceInt(code[1:3]) \
                    and forceInt(parentCode[6:8]) >= forceInt((code[1:3])):
                return success

        elif len(code) > 3:
            if parentCode in code:
                return success
            return error
        return error

    def saveInternals(self, id):
        db = QtGui.qApp.db
        code = forceString(db.translate(self.tableName(), 'id', id, 'DiagID'))
        if code != self.prevCode:
            stmt = "Update %s set parent_code = '%s' where parent_code = '%s'" % (self.tableName(), code, self.prevCode)
            db.query(stmt)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textChanged(self, text):
        code = forceStringEx(text)
        self.cmbMKBSubclass.setEnabled(bool(re.match(r'^[A-Z]\d{2}(\.\d)?$', code)))


def clearCache():
    if hasattr(QtGui.qApp, 'MKBSubclass'):
        QtGui.qApp.MKBSubclass = {}
    if hasattr(QtGui.qApp, 'MKBRootChilds'):
        QtGui.qApp.MKBRootChilds = {}
    if hasattr(QtGui.qApp, 'MKBRootChildsCount'):
        QtGui.qApp.MKBRootChildsCount = {}
    if hasattr(QtGui.qApp, 'MKBChildsCount'):
        QtGui.qApp.MKBChildsCount = {}
    if hasattr(QtGui.qApp, 'MKBChilds'):
        QtGui.qApp.MKBChilds = {}


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo
    from PyQt4 import QtCore

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pacs',
        'port': 3306,
        'database': 's11vm',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CMKBList(None)
    w.exec_()


if __name__ == '__main__':
    main()
