# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt

from library.RLS.ui.Ui_RLSComboBoxPopup import Ui_RLSComboBoxPopup
from library.TableModel import CDateCol, CTableModel, CTextCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, withWaitCursor


class CRLSComboBoxPopup(QtGui.QFrame, Ui_RLSComboBoxPopup):
    __pyqtSignals__ = ('RLSCodeSelected(int)',
                       )

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(Qt.WA_WindowPropagation)
        self.tableModel = CRLSTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblRLS.setModel(self.tableModel)
        self.tblRLS.setSelectionModel(self.tableSelectionModel)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setDefault(True)
#       к сожалению в данном случае setDefault обеспечивает рамочку вокруг кнопочки
#       но enter не работает...
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setShortcut(Qt.Key_Return)
        self.date = None
        self.code = None
        self.tblRLS.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CRLSComboBoxPopup', {})
        # self.tblRLS.loadPreferences(preferences)

    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent is not None:
            opt = QtGui.QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QtGui.QStyle.CC_ComboBox, opt, QtGui.QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)

    # def closeEvent(self, event):
    #     preferences = self.tblRLS.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CRLSComboBoxPopup', preferences)
    #     QFrame.closeEvent(self, event)

    def eventFilter(self, watched, event):
        if watched == self.tblRLS:
            if event.type() == QtCore.QEvent.KeyPress and event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Select]:
                event.accept()
                index = self.tblRLS.currentIndex()
                self.tblRLS.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QFrame.eventFilter(self, watched, event)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()

    def on_buttonBox_reset(self):
        self.edtTradeName.setText('')
        self.edtINN.setText('')
        self.cmbPharmGroup.setValue(None)
        self.cmbATC.setValue(None)
        self.chkShowAnnulated.setChecked(False)
        self.chkShowDisabled.setChecked(False)

    def on_buttonBox_apply(self):
        tradeName = forceString(self.edtTradeName.text())
        inn = forceString(self.edtINN.text())
        pharmGroupId = self.cmbPharmGroup.value()
        ATCid = self.cmbATC.value()
        if self.chkShowAnnulated.isChecked():
            date = None
        else:
            date = self.tableModel.date
        showDisabled = self.chkShowDisabled.isChecked()
        rlsIdList = self.getRLSIdList(tradeName, inn, pharmGroupId, ATCid, date, showDisabled, self.code)
        self.setRLSIdList(rlsIdList, None)

    def setRLSIdList(self, idList, posToId):
        if idList:
            self.tblRLS.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblRLS.setFocus(Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.edtTradeName.setFocus(Qt.OtherFocusReason)

    @withWaitCursor
    def getRLSIdList(self, tradeName, INN, pharmGroupId, ATCId, date, showDisabled, forceCode):
        u"""
        :param tradeName: Торговое наименование
        :param INN: МНН
        :param pharmGroupId: Фарм. группа
        :param ATCId: АТХ
        :param date: Дата, на которую ищутся актуальные записи
        :param showDisabled: Показывать записи с пометкой "Скрывать при выборе для рецепта"
        :param forceCode: Выбранный ранее vNomen.code
        :return: [list of vNomen.id]
        :rtype: list[int]
        """
        db = QtGui.qApp.db
        table = self.tableModel.table()
        queryTable = table
        cond = []
        if tradeName:
            cond.append(db.joinOr([table['tradeName'].like(u'%{0}%'.format(tradeName)),
                                   table['tradeNameLat'].like(u'%{0}%'.format(tradeName))]))
        if INN:
            cond.append(db.joinOr([table['INPName'].like(u'%{0}%'.format(INN)),
                                   table['INPNameLat'].like(u'%{0}%'.format(INN))]))
        if pharmGroupId:
            pharmGroupIdList = self.getPharmGroupDescendantIdList(pharmGroupId)
            tablePharmGroupToCode = db.table('rls.rlsPharmGroupToCode')
            queryTable = queryTable.leftJoin(tablePharmGroupToCode,
                                             tablePharmGroupToCode['code'].eq(table['code']))
            cond.append(tablePharmGroupToCode['rlsPharmGroup_id'].inlist(pharmGroupIdList))
        if ATCId:
            ATCIdList = self.getATCDescendantIdList(ATCId)
            tableATCToCode = db.table('rls.rlsATCGroupToCode')
            queryTable = queryTable.leftJoin(tableATCToCode,
                                             tableATCToCode['code'].eq(table['code']))
            cond.append(tableATCToCode['rlsATCGroup_id'].inlist(ATCIdList))
        if date:
            subCond = db.joinAnd([db.joinOr([table['regDate'].isNull(),
                                             table['regDate'].le(date)]),
                                  db.joinOr([table['annDate'].isNull(),
                                             table['annDate'].gt(date)])])
            if forceCode:
                subCond = db.joinOr([subCond,
                                     table['code'].eq(forceCode)])
            cond.append(subCond)
        if not showDisabled:
            subCond = table['disabledForPrescription'].eq(0)
            if forceCode:
                subCond = db.joinOr([subCond,
                                     table['code'].eq(forceCode)])
            cond.append(subCond)
        idList = db.getIdList(queryTable, table['id'],
                              where=cond,
                              order='tradeName, INPName, form, dosage, filling',
                              limit=1000)
        return idList

    def getPharmGroupDescendantIdList(self, pharmGroupId):
        return QtGui.qApp.db.getDescendants('rls.rlsPharmGroup', 'group_id', pharmGroupId)

    def getATCDescendantIdList(self, ATCid):
        return QtGui.qApp.db.getDescendants('rls.rlsATCGroup', 'group_id', ATCid)

    def setDate(self, date):
        self.tableModel.date = date

    def setRLSCode(self, code):
        self.code = code
        idList = []
        id = None
        db = QtGui.qApp.db
        if code:
            table = db.table('rls.vNomen')
            record = db.getRecordEx(table, 'id, tradeName_id, INPName_id', table['code'].eq(code))
            if record:
                id = forceRef(record.value('id'))
                tradeNameId = forceRef(record.value('tradeName_id'))
                INPNameId = forceRef(record.value('INPName_id'))
                cond = []
                if tradeNameId:
                    cond.append(table['tradeName_id'].eq(tradeNameId))
                if INPNameId:
                    cond.append(table['INPName_id'].eq(INPNameId))
                cond = [db.joinOr(cond)]
                if self.tableModel.date:
                    subCond = db.joinAnd([db.joinOr([table['regDate'].isNull(),
                                                     table['regDate'].le(self.tableModel.date)]),
                                          db.joinOr([table['annDate'].isNull(),
                                                     table['annDate'].gt(self.tableModel.date)])])
                    if self.code:
                        subCond = db.joinOr([subCond,
                                             table['code'].eq(self.code)])
                    cond.append(subCond)
                subCond = table['disabledForPrescription'].eq(0)
                if self.code:
                    subCond = db.joinOr([subCond,
                                         table['code'].eq(self.code)])
                cond.append(subCond)

                if cond:
                    idList = db.getIdList(table,
                                          where=cond,
                                          order='tradeName, INPName, form, dosage, filling',
                                          limit=1000)
                else:
                    idList = [id]
        self.setRLSIdList(idList, id)

    def selectRLSCode(self, code):
        self.code = code
        self.emit(QtCore.SIGNAL('RLSCodeSelected(int)'), code)
        self.close()

    def getCurrentRLSCode(self):
        id = self.tblRLS.currentItemId()
        if id:
            code = forceInt(QtGui.qApp.db.translate('rls.rlsNomen', 'id', id, 'code'))
            return code
        return None

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblRLS_doubleClicked(self, index):
        def selectionConfirmed():
            req = QtGui.QMessageBox.question(self, u'Внимание!',
                                             u'Это средство в настоящий момент не разрешено к применению.\nПодтверждаете выбор?',
                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            return req == QtGui.QMessageBox.Yes

        if index.isValid():
            if (Qt.ItemIsEnabled & self.tableModel.flags(index)) or selectionConfirmed():
                code = self.getCurrentRLSCode()
                self.selectRLSCode(code)


class CRLSTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Наименование', ['tradeName'], 20))
        self.addColumn(CTextCol(u'Лат.наименование', ['tradeNameLat'], 20))
        # self.addColumn(CTextCol(u'НДВ', ['INPName'], 20))
        self.addColumn(CTextCol(u'Лек.форма', ['form'], 20))
        self.addColumn(CTextCol(u'Доза единицы лек.формы', ['dosage'], 20))
        self.addColumn(CTextCol(u'Фасовка', ['filling'], 20))
        self.addColumn(CTextCol(u'Упаковка', ['packing'], 20))
        self.addColumn(CDateCol(u'Рег.', ['regDate'], 10))
        self.addColumn(CDateCol(u'Аннулировано', ['annDate'], 10))
        self.loadField('disabledForPrescription')
        self.setTable('rls.vNomen')
        self.date = QtCore.QDate.currentDate()

    def flags(self, index):
        row = index.row()
        record = self.getRecordByRow(row)

        enabled = not forceBool(record.value('disabledForPrescription'))
        if enabled:
            if self.date:
                regDate = forceDate(record.value('regDate'))
                annDate = forceDate(record.value('annDate'))
                enabled = (not regDate or regDate <= self.date) and (not annDate or self.date < annDate)
        if enabled:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsSelectable
