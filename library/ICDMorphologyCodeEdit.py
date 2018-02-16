#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.crbcombobox import CRBModel, CRBSelectionModel
from library.TableModel import *

from Utils import *

import re

from Ui_ICDMorphologyPopup import Ui_ICDMorphologyPopup

rus = u'йцукенгшщзхъфывапролджэячсмитьбюё'
eng = u'qwertyuiop[]asdfghjkl;\'zxcvbnm,.`'
r2e = {}
e2r = {}
for i in range(len(rus)):
    r2e[rus[i]] = eng[i]
    e2r[eng[i]] = rus[i]


class CICDMorphologyCodeEdit(QtGui.QLineEdit):
    def __init__(self, parent=None, morphologyModel=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setInputMask('\M9999/9;_')
        self._morphologyModel = morphologyModel

    def isValid(self, text=u''):
        if not text:
            text = forceStringEx(self.text())
        return bool(re.match('M\d{4}/', text))

    def validText(self):
        text = forceStringEx(self.text())
        if self.isValid(text):
            return text
        return ''

    def keyPressEvent(self, event):
        oldValue = self.text()
        chr = unicode(event.text()).lower()
        if r2e.has_key(chr):
            engChr = r2e[chr].upper()
            myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(),
                                      event.count())
            QtGui.QLineEdit.keyPressEvent(self, myEvent)
        elif e2r.has_key(chr):
            engChr = chr.upper()
            myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(),
                                      event.count())
            QtGui.QLineEdit.keyPressEvent(self, myEvent)
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)

        if not event.key() in [Qt.Key_Return, Qt.Key_Backspace] and not self.existsValue(unicode(self.text())):
            self.setText(oldValue)
            lOldValue = len(oldValue)
            pos = lOldValue - 1 if lOldValue < 6 else lOldValue
            self.setCursorPosition(pos)

    def existsValue(self, value):
        if self._morphologyModel:
            findValue = self._morphologyModel.searchCodeEx(value)[1]
            lValue = len(value)
            if lValue < 6:
                return value[:lValue - 1] == findValue
            else:
                return value == findValue
        return True


class CICDMorphologyCodeEditEx(QtGui.QComboBox):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)'
                       )

    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.showFields = 2
        self.setModelColumn(self.showFields)
        self._popup = None
        self._model = CRBModel(self)
        self._lineEdit = CICDMorphologyCodeEdit(self, self._model)
        self.setLineEdit(self._lineEdit)
        self._lineEdit.setCursorPosition(0)
        self._searchString = ''
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = 600
        self._popup = CICDMorphologyPopup(self)
        self.connect(self._popup, QtCore.SIGNAL('morphologyMKBSelected(QString)'), self.setText)
        self.connect(self._lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onTextEdited)
        self.connect(self._lineEdit, QtCore.SIGNAL('textChanged(QString)'), self.onTextChanged)

    def setShowFields(self, showFields):
        self.showFields = showFields
        self.setModelColumn(self.showFields)

    def model(self):
        return self._model

    def getMKBFilter(self, MKB):
        return self._popup.getMKBFilter(MKB)

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = 600

    def setTable(self, tableName, addNone=True, filter='', order=None):
        self._popup.setTable(tableName, addNone, filter, order)

    def setMKBFilter(self, filter):
        self._popup.setMKBFilter(filter)

    def setFilter(self, filter='', order=None):
        self._popup.setFilter(filter, order)

    def reloadData(self):
        self._popup.reloadData()

    def showPopup(self):
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        selfWidth = self.size().width()
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        width = max(size.width() + 20, selfWidth, self.prefferedWidth)
        size.setWidth(width)
        pos.setX(max(min(pos.x(), screen.right() - size.width()), screen.left()))
        pos.setY(max(min(pos.y(), screen.bottom() - size.height()), screen.top()))
        #
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.setRecordsCount()
        self._popup.show()

    #        self._popup.setCurrentMorphologyMKB(self.text())

    def lookup(self):
        i, self._searchString = self._popup.searchCodeEx(self._searchString)
        if i >= 0 and i != self.currentIndex():
            self._popup.setCurrentIndex(i)

    def setText(self, text):
        self._lineEdit.setText(text)
        self._lineEdit.setCursorPosition(0)

    def selectAll(self):
        self._lineEdit.selectAll()
        self._lineEdit.setCursorPosition(0)

    def setCursorPosition(self, pos=0):
        self._lineEdit.setCursorPosition(pos)

    def text(self):
        return self._lineEdit.text()

    def validText(self):
        return self._lineEdit.validText()

    def isValid(self, text=u''):
        return self._lineEdit.isValid(text)

    def onTextChanged(self, text):
        self.emit(QtCore.SIGNAL('textChanged(QString)'), text)

    def onTextEdited(self, text):
        self.emit(QtCore.SIGNAL('textEdited(QString)'), text)


#
#
# ############################################
#
#

class CICDMorphologyPopup(QtGui.QFrame, Ui_ICDMorphologyPopup):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setupUi(self)
        self._parent = parent
        self._model = parent._model
        self._selectionModel = CRBSelectionModel(self._model)
        self.tblMorphology.setModel(self._model)

        self.tableModel = CTableModel(self, [
            CTextCol(u'Код', ['code'], 6),
            CTextCol(u'Наименование', ['name'], 40)],
                                      'MKB_Morphology')
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel, self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self._addNone = True
        self._tableName = 'MKB_Morphology'
        self._filier = ''
        self._order = ''
        self.id = None
        self._searchString = ''
        self.tblMorphology.setSelectionModel(self._selectionModel)
        self.tblSearch.setModel(self.tableModel)
        self.tblSearch.setSelectionModel(self.tableSelectionModel)
        self._model.setTable(self._tableName, self._addNone, self._filier, self._order)
        self.tblMorphology.hideColumn(2)
        self.lastMKBValue = ''
        self.edtSearch.installEventFilter(self)
        self.btnSearch.installEventFilter(self)
        self.tblSearch.installEventFilter(self)

    def searchCodeEx(self, searchString):
        self._searchString = searchString
        return self._model.searchCodeEx(self._searchString)

    def setCurrentIndex(self, rowIndex):
        index = self._model.index(rowIndex, 1)
        self.tblMorphology.setCurrentIndex(index)

    def currentIndex(self):
        return self.tblMorphology.currentIndex()

    def setRecordsCount(self):
        n = self._model.rowCount()
        self.lblCount.setText(u'Количество записей: %d' % n)

    def model(self):
        return self.tblMorphology.model()

    def view(self):
        return self.tblMorphology

    def setTable(self, tableName, addNone=True, filter='', order=None):
        self._tableName = tableName
        self._addNone = addNone
        self._filier = filter
        self._order = order
        self._model.setTable(tableName, addNone, filter, order)

    def setFilter(self, filter='', order=None):
        self._filier = filter
        self._order = order
        self.setTable(self._tableName, self._addNone, filter, order)

    def getMKBFilter(self, MKB):
        if bool(self._filier):
            cond = [self._filier]
        else:
            cond = []
        db = QtGui.qApp.db
        if bool(MKB):
            self.lastMKBValue = MKB
            table = db.table('MKB_Morphology')
            if MKB.endswith('.'):
                MKB = MKB[:-1]
            condAnd1 = db.joinAnd([table['bottomMKBRange1'].le(MKB[:3]),
                                   table['topMKBRange1'].ge(MKB[:3])])
            condAnd2 = db.joinAnd([table['bottomMKBRange1'].le(MKB),
                                   table['topMKBRange1'].ge(MKB)])
            condAnd3 = db.joinAnd([table['bottomMKBRange2'].le(MKB[:3]),
                                   table['topMKBRange2'].ge(MKB[:3])])
            condAnd4 = db.joinAnd([table['bottomMKBRange2'].le(MKB),
                                   table['topMKBRange2'].ge(MKB)])
            condOr = db.joinOr([condAnd1, condAnd2, condAnd3, condAnd4])
            cond.append(condOr)
        else:
            self.lastMKBValue = ''
        filter = db.joinAnd(cond)
        return filter

    def setMKBFilter(self, filter):
        self._model.setTable(self._tableName, self._addNone, filter, self._order)

    def reloadData(self):
        self._model.setTable(self._tableName, self._addNone, self._filier, self._order)

    def selectItemByIndex(self, index):
        row = index.row()
        morphologyCode = self._model.getCode(row)
        self.selectItemByCode(morphologyCode)

    def selectItemByCode(self, code):
        self.emit(QtCore.SIGNAL('morphologyMKBSelected(QString)'), code)
        self.hide()

    def setCurrentMorphology(self, morphologyId):
        row = self._model.searchId(morphologyId)
        index = self._model.index(row, 1)
        self.tblMorphology.setCurrentIndex(index)

    #        self._selectionModel.setCurrentIndex(index, QtGui.QItemSelectionModel.Select)


    def restoreByFilterMKB(self):
        filter = self.getMKBFilter(self.lastMKBValue)
        self.setMKBFilter(filter)

    @pyqtSlot(QModelIndex)
    def on_tblMorphology_clicked(self, index):
        self.selectItemByIndex(index)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if index == 0:
            morphologyId = self.tblSearch.currentItemId()
            if morphologyId:
                if self.chkForCurrentMKB.isChecked():
                    self.restoreByFilterMKB()
                self.setCurrentMorphology(morphologyId)
            else:
                self.restoreByFilterMKB()
        if index == 1:
            self.reloadData()
        self.setRecordsCount()

    @QtCore.pyqtSlot()
    def on_btnSearch_clicked(self):
        words = forceStringEx(self.edtSearch.text()).split()
        table = self.tableModel.table()
        cond = [table['name'].like('%' + word + '%') for word in words]
        cond.append(table['group'].isNotNull())
        if self.chkForCurrentMKB.isChecked():
            cond.append(self.getMKBFilter(self.lastMKBValue))
        idList = QtGui.qApp.db.getIdList(table, 'id',
                                         where=cond,
                                         order='code')
        self.tableModel.setIdList(idList)
        self.edtSearch.setFocus(Qt.OtherFocusReason)

    @QtCore.pyqtSlot(QModelIndex)
    def on_tblSearch_doubleClicked(self, index):
        morphologyItem = self.tblSearch.currentItem()
        if morphologyItem:
            code = forceString(morphologyItem.value('code'))
            self.selectItemByCode(code)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress and event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Select]:
            event.accept()
            if watched == self.tblSearch:
                self.on_tblSearch_doubleClicked(None)
            else:
                self.on_btnSearch_clicked()
            return True
        return QtGui.QFrame.eventFilter(self, watched, event)

