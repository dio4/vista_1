# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4.QtGui import *

from library.TableModel import *
from library.Utils import *
from Registry.Utils import *

from Ui_ModelPatientComboBoxPopup import Ui_ModelPatientComboBoxPopup


class CModelPatientComboBoxPopup(QtGui.QFrame, Ui_ModelPatientComboBoxPopup):
    __pyqtSignals__ = ('modelPatientSelected(int)'
                      )

    def __init__(self, parent, eventEditor = None):
        QFrame.__init__(self, parent, Qt.Popup)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_WindowPropagation)
        self.tableModel = CModelPatientTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.tblModelPatient.setModel(self.tableModel)
        self.tblModelPatient.setSelectionModel(self.tableSelectionModel)
        self.buttonBox.button(QDialogButtonBox.Apply).setDefault(True)
        self.buttonBox.button(QDialogButtonBox.Apply).setShortcut(Qt.Key_Return)
        self.code = None
        self.parent = parent
        self.eventEditor = eventEditor
        self.tblModelPatient.installEventFilter(self)
        # preferences = getPref(QtGui.qApp.preferences.windowPrefs, 'CModelPatientComboBoxPopup', {})
        # self.tblModelPatient.loadPreferences(preferences)
        self.cmbQuoting.setShowFields(CRBComboBox.showCodeAndName)
        if self.eventEditor:
            self.cmbQuoting.setBegDate(self.eventEditor.eventSetDateTime.date())
            self.cmbQuoting.setEndDate(self.eventEditor.eventDate)
            self.cmbQuoting.setClientId(self.eventEditor.clientId)
            self.cmbQuoting.popupView.setTable('QuotaType')
            self.cmbQuoting.setCurrentIndex(0)


    @QtCore.pyqtSlot(bool)
    def on_chkQuotingPatientOnly_toggled(self, value):
        if value and self.eventEditor:
            self.cmbQuoting.setBegDate(self.eventEditor.eventSetDateTime.date())
            self.cmbQuoting.setEndDate(self.eventEditor.eventDate)
            self.cmbQuoting.setClientId(self.eventEditor.clientId)
        else:
            self.cmbQuoting.setBegDate(QDate())
            self.cmbQuoting.setEndDate(QDate())
            self.cmbQuoting.setClientId(None)
        self.cmbQuoting.popupView.setTable('QuotaType')
        self.cmbQuoting.setCurrentIndex(0)


    def getPreliminaryDiagnostics(self):
        if hasattr(self.eventEditor, 'modelPreliminaryDiagnostics'):
            for row, record in enumerate(self.eventEditor.modelPreliminaryDiagnostics.items()):
                return forceString(record.value('MKB'))
        else:
            return None


    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent!=None:
            opt=QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(Qt.WA_NoMouseReplay)
        QFrame.mousePressEvent(self, event)


    # def closeEvent(self, event):
    #     preferences = self.tblModelPatient.savePreferences()
    #     setPref(QtGui.qApp.preferences.windowPrefs, 'CModelPatientComboBoxPopup', preferences)
    #     QFrame.closeEvent(self, event)


    def eventFilter(self, watched, event):
        if watched == self.tblModelPatient:
            if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Select]:
                event.accept()
                index = self.tblModelPatient.currentIndex()
                self.tblModelPatient.emit(SIGNAL('doubleClicked(QModelIndex)'), index)
                return True
        return QtGui.QFrame.eventFilter(self, watched, event)


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QDialogButtonBox.Apply:
            self.on_buttonBox_apply()
        elif buttonCode == QDialogButtonBox.Reset:
            self.on_buttonBox_reset()


    def on_buttonBox_reset(self):
        self.chkPreviousMKB.setChecked(True)
        self.chkQuotingEvent.setChecked(True)
        self.on_chkQuotingEvent_clicked(True)
        self.on_buttonBox_apply()


    def on_buttonBox_apply(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            quotaTypeId = forceString(self.cmbQuoting.value())
            crIdList = self.getModelPatientIdList(quotaTypeId)
            self.setModelPatientIdList(crIdList, None)
        finally:
            QtGui.qApp.restoreOverrideCursor()


    def setModelPatientIdList(self, idList, posToId):
        if idList:
            self.tblModelPatient.setIdList(idList, posToId)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabEnabled(0, True)
            self.tblModelPatient.setFocus(Qt.OtherFocusReason)
        else:
            self.tabWidget.setCurrentIndex(1)
            self.tabWidget.setTabEnabled(0, False)
            self.cmbQuoting.setFocus(Qt.OtherFocusReason)


    def getModelPatientIdList(self, quotaTypeId):
        db = QtGui.qApp.db
        tableRBModelPatient = db.table('rbPatientModel')
        cond = [tableRBModelPatient['isObsolete'].eq(0)]
        if quotaTypeId:
            cond.append(tableRBModelPatient['quotaType_id'].eq(quotaTypeId))
        if self.chkPreviousMKB.isChecked():
            MKB = self.getPreliminaryDiagnostics()
            if MKB:
                if len(MKB) > 3:
                    mkbTrunc = QString(MKB)
                    mkbTrunc.truncate(3)
                    strMKB = str(mkbTrunc)
                else:
                    strMKB = MKB
                cond.append(tableRBModelPatient['MKB'].like('%' + strMKB + '%'))
        if self.chkQuotingEvent.isChecked():
            if hasattr(self.parent, 'getQuotaTypeId'):
                quotaTypeId = self.parent.getQuotaTypeId()
                if quotaTypeId:
                    cond.append(tableRBModelPatient['quotaType_id'].eq(quotaTypeId))
        idList = db.getDistinctIdList(tableRBModelPatient, [tableRBModelPatient['id'].name()], cond)
        return idList


    @pyqtSlot(bool)
    def on_chkQuotingEvent_clicked(self, checked):
        quotaTypeId = None
        if checked:
            if hasattr(self.parent, 'getQuotaTypeId'):
                quotaTypeId = self.parent.getQuotaTypeId()
        self.cmbQuoting.setValue(quotaTypeId)


    def setModelPatientCode(self, code):
        db = QtGui.qApp.db
        tableRBModelPatient = db.table('rbPatientModel')
        self.code = code
        idList = []
        id = None
        if code:
            record = db.getRecordEx(tableRBModelPatient, [tableRBModelPatient['id']], [tableRBModelPatient['id'].eq(id)])
            if record:
                id = forceInt(record.value(0))
            if id:
                idList = [id]
        self.setModelPatientIdList(idList, id)


    def selectModelPatientCode(self, code):
        self.code = code
        self.emit(SIGNAL('modelPatientSelected(int)'), code)
        self.close()


    def getCurrentModelPatientCode(self):
        db = QtGui.qApp.db
        tableRBModelPatient = db.table('rbPatientModel')
        id = self.tblModelPatient.currentItemId()
        code = None
        if id:
            record = db.getRecordEx(tableRBModelPatient, [tableRBModelPatient['id']], [tableRBModelPatient['id'].eq(id)])
            if record:
                code = forceInt(record.value(0))
            return code
        return None


    @pyqtSlot(QModelIndex)
    def on_tblModelPatient_doubleClicked(self, index):
        if index.isValid():
            if (Qt.ItemIsEnabled & self.tableModel.flags(index)):
                code = self.getCurrentModelPatientCode()
                self.selectModelPatientCode(code)
                if self.parent is not None:
                    self.parent.onCurrentIndexChanged(None)


class CModelPatientTableModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self.addColumn(CTextCol(u'Код', ['code'],  10))
        self.addColumn(CTextCol(u'Модель пациента', ['name'], 30))
        self.addColumn(CTextCol(u'Диагнозы', ['MKB'], 30))
        self.addColumn(CRefBookCol(u'Квота', ['quotaType_id'], 'QuotaType', 50))
        self.setTable('rbPatientModel')


    def flags(self, index):
        row = index.row()
        record = self.getRecordByRow(row)
        enabled = True
        if enabled:
            return Qt.ItemIsEnabled|Qt.ItemIsSelectable
        else:
            return Qt.ItemIsSelectable


class CModelPatientComboBox(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                      )

    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.parent = parent
        self._popup=None
        self.code = None
        self.quotingId = None
        self.previousMKB = False
        self.eventEditor = None
        self.isObsolete = False
#        self.updateObsolete()
        self.connect(self, QtCore.SIGNAL('currentIndexChanged(int)'), self.onCurrentIndexChanged)


    def showPopup(self):
        if self.isObsolete:
            return
        if not self._popup:
            self._popup = CModelPatientComboBoxPopup(self, self.eventEditor)
            self.connect(self._popup, SIGNAL('modelPatientSelected(int)'), self.setValue)

        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        #width= max(size.width(), self.width())
        #size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        size.setWidth(screen.width()) # распахиваем на весь экран
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.eventEditor = self.eventEditor
        self._popup.cmbQuoting.setClientId(None)
        self._popup.cmbQuoting.setBegDate(QDate())
        self._popup.cmbQuoting.setEndDate(QDate())
        self._popup.on_chkQuotingEvent_clicked(True)
        self._popup.show()
        self._popup.setModelPatientCode(self.code)
        self._popup.on_buttonBox_apply()


    def onCurrentIndexChanged(self, index):
        if self.parent:
            self.parent.on_cmbPatientModel_currentIndexChanged(index)


    def getQuotaTypeId(self):
        return self.parent.getQuotaTypeId() if (self.parent and hasattr(self.parent, 'getQuotaTypeId')) else None


    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor


    def setValue(self, code):
        self.code = code
        self.updateText()


    def value(self):
        return self.code


    def updateText(self):
        db = QtGui.qApp.db
        tableRBModelPatient = db.table('rbPatientModel')
        record = db.getRecordEx(tableRBModelPatient, [tableRBModelPatient['code'], tableRBModelPatient['name'], tableRBModelPatient['isObsolete']], [tableRBModelPatient['id'].eq(self.code)])
        text = ''
        if record:
            text = ' - '.join([field for field in [forceString(record.value('code')), forceString(record.value('name'))] if field])
        self.setEditText(text)
        self.isObsolete = forceBool(record.value('isObsolete')) if record else False


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Delete:
            self.setValue(None)
            self.onCurrentIndexChanged(None)
            event.accept()
        elif key == Qt.Key_Backspace: # BS
            self.setValue(None)
            self.onCurrentIndexChanged(None)
            event.accept()
        else:
            QtGui.QComboBox.keyPressEvent(self, event)


class CModelPatientComboBoxF027(CModelPatientComboBox):
    def onCurrentIndexChanged(self, index):
        if self.eventEditor:
            self.eventEditor.on_cmbPatientModel_currentIndexChanged(index)


    def getQuotaTypeId(self):
        return self.eventEditor.getQuotaTypeId() if (self.eventEditor and hasattr(self.eventEditor, 'getQuotaTypeId')) else None

