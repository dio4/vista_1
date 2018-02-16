#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Utils import *
from ICDTree import CICDTreePopup
from ICDTreeViews import CICDTreeView

# """Редакторы для кодов МКБ"""

rus = u'йцукенгшщзхъфывапролджэячсмитьбюё'
eng = u'qwertyuiop[]asdfghjkl;\'zxcvbnm,.`'
r2e = {}
e2r = {}
for i in range(len(rus)):
    r2e[ rus[i] ] = eng[i]
    e2r[ eng[i] ] = rus[i]


class CICDCodeEdit(QtGui.QLineEdit):
    # """Редактор кодов МКБ"""
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)
        if (QtGui.qApp.isAllowedExtendedMKB()):
            self.setInputMask('A99.00000;_')
        else:
            self.setInputMask('A99.X0;_')


    def keyPressEvent(self, event):
        chr = unicode(event.text()).lower()
        if r2e.has_key(chr):
            engChr = r2e[chr].upper()
            myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(), event.count())
            QtGui.QLineEdit.keyPressEvent(self, myEvent)
        elif e2r.has_key(chr):
            engChr = chr.upper()
            myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(), event.count())
            QtGui.QLineEdit.keyPressEvent(self, myEvent)
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)

    def text(self):
        val = trim(QtGui.QLineEdit.text(self))
        if val.endswith('.'):
            val = val[0:-1]
        return val


class CICDCodeEditEx(QtGui.QComboBox):
    # """Редактор кодов МКБ с выпадающим деревом"""
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)',
                       'editingFinished()'
                      )

    def __init__(self, parent = None):
        QtGui.QComboBox.__init__(self, parent)
        self._lineEdit=CICDCodeEdit(self)
        self._popup = CICDTreePopup(self)
        self.setLineEdit(self._lineEdit)
        self._lineEdit.setCursorPosition(0)
        self.showFlag = True
        self.connect(self._lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onTextEdited)
        self.connect(self._lineEdit, QtCore.SIGNAL('textChanged(QString)'), self.onTextChanged)
        self.connect(self._lineEdit, QtCore.SIGNAL('editingFinished()'), self.onEditingFinished)
        self.connect(self._popup,    QtCore.SIGNAL('diagSelected(QString)'), self.setText)

    def setMKBFilter(self, filter=''):
        self._popup.setMKBFilter(filter)

    def showPopup(self):
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self._popup.sizeHint()
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
#        size.setWidth(size.width()+20) # magic. похоже, что sizeHint считается неправильно. русские буквы виноваты?
        size.setWidth(screen.width()) # наименования длинные, распахиваем на весь экран
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
#
##        if (pos.y() + size.height() > screen.bottom()):
##            pos.setY(pos2.y() - size.height())
##        elif (pos.y() < screen.top()):
##            pos.setY(screen.top())
##        if (pos.y() < screen.top()):
##            pos.setY(screen.top())
##        if (pos.y()+size.height() > screen.bottom()):
##            pos.setY(screen.bottom()-size.height())
        self.showFlag = True
        self._popup.move(pos)
        self._popup.resize(size)
        self._popup.show()
        self._popup.setCurrentDiag(self.text())


    def hidePopup(self):
        self.showFlag = False
        QtGui.QComboBox.hidePopup(self)

#    def focusInEvent(self, event):
#        QtGui.QComboBox.focusInEvent(event)
#        self.setCursorPosition(0)



    def setText(self, text):
        self._lineEdit.setText(text)
        self._lineEdit.setCursorPosition(0)


    def selectAll(self):
        self._lineEdit.selectAll()
        self._lineEdit.setCursorPosition(0)


    def setCursorPosition(self,  pos=0):
        self._lineEdit.setCursorPosition(pos)


    def text(self):
        return self._lineEdit.text()

    def onTextChanged(self, text):
        self.emit(QtCore.SIGNAL('textChanged(QString)'), text)

    def onTextEdited(self, text):
        self.emit(QtCore.SIGNAL('textEdited(QString)'), text)

    def onEditingFinished(self):
        if not self.showFlag:
            self.emit(SIGNAL('editingFinished()'))


class CICDTempInvalidCodeEditEx(CICDCodeEditEx):
    __pyqtSignals__ = ('textChanged(QString)',
                       'textEdited(QString)',
                       'editingFinished()'
                      )

    def __init__(self, parent = None):
        CICDCodeEditEx.__init__(self, parent)
        #self.connect(self._lineEdit, QtCore.SIGNAL('editingFinished()'), self.onEditingFinished)
        self.editingFinishedProcessing = False
        self.popupHidden = True

    def showPopup(self):
        self.popupHidden = False
        CICDCodeEditEx.showPopup(self)

    def hidePopup(self):
        self.popupHidden = True
        CICDCodeEditEx.hidePopup(self)

    #def focusOutEvent(self, event):
    #    CICDCodeEditEx.focusOutEvent(self, event)
    #    self.onEditingFinished()


    def onEditingFinished(self):
        #if not self.popupHidden:
        #    return
        if type(QtGui.qApp.focusWidget()) == CICDTreeView:
            return
        if not self.editingFinishedProcessing:
            self.editingFinishedProcessing = True
            newMKB = self.text()
            def checkNewMKB(newMKB):
                if not newMKB:
                    specifiedMKB = ''
                    specifiedMKBEx = ''
                    specifiedCharacterId = None
                    specifiedTraumaTypeId = None
                else:
                    acceptable, specifiedMKB, specifiedMKBEx, specifiedCharacterId, specifiedTraumaTypeId = QObject.parent(self).specifyDiagnosis(newMKB)
                    QObject.parent(self).setEditorDataTI()
                    QObject.parent(self).updateCharacterByMKB(specifiedMKB, specifiedCharacterId)
                    if not acceptable:
                        return toVariant(newMKB)
                return toVariant(specifiedMKB)

            self.setText(forceString(checkNewMKB(newMKB)))
            self.editingFinishedProcessing = False

class CICDCodeComboBoxEx(QtGui.QComboBox):
    # """Редактор кодов МКБ ComboBox"""
    textChanged = pyqtSignal(QString)
    textEdited = pyqtSignal(QString)
    editingFinished = pyqtSignal()

    def __init__(self, parent = None):
        QtGui.QComboBox.__init__(self, parent)
        self._lineEdit=CICDCodeEdit(self)
        self.setLineEdit(self._lineEdit)
        self._lineEdit.setCursorPosition(0)
        self.ICDTreePopup=None
#        self.connect(self._lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onTextEdited)
#        self.connect(self._lineEdit, QtCore.SIGNAL('textChanged(QString)'), self.onTextChanged)
#        self.connect(self._lineEdit, QtCore.SIGNAL('editingFinished()'), self.onEditingFinished)
        self.lineEdit().textEdited.connect(self.onTextEdited)
        self.lineEdit().textChanged.connect(self.onTextChanged)
        self.lineEdit().editingFinished.connect(self.onEditingFinished)


    def onTextChanged(self, text):
        self.textChanged.emit(text)


    def onTextEdited(self, text):
        self.textEdited.emit(text)

    def setText(self, text):
        self._lineEdit.setText(text)
        self._lineEdit.setCursorPosition(0)


    def selectAll(self):
        self._lineEdit.selectAll()
        self._lineEdit.setCursorPosition(0)


    def setCursorPosition(self,  pos=0):
        self._lineEdit.setCursorPosition(pos)


    def text(self):
        return self._lineEdit.text()

    @pyqtSlot()
    def onEditingFinished(self):
        newMKB = self.text()
        if newMKB and self.findText(newMKB) > -1:
            self.setText(newMKB)
        else:
            self.setText('')

