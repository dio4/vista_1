# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.DbComboBox import *
from PyQt4.QtGui import *
class CReferralComboBox(CDbComboBox):
    def __init__(self, parent):
        CDbComboBox.__init__(self, parent)

        self.setTable('Referral')
        #self.setNameField('number')

        if QtGui.qApp.defaultKLADR()[:2] == '23':
            self.setNameField(u'number')
        else:
            self.setNameField(u'CONCAT(\'№ \', number,\' от \', DATE_FORMAT(date, \'%d.%m.%Y\'))')
        self.setFilter('0')
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel()
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # completer, which uses filter model
        self.completer = QCompleter(self.pFilterModel, self)

        #always show all filtered completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        #self.lineEdit = QLineEdit()
        #TODO: Set input mask and/or Validator
        if QtGui.qApp.defaultKLADR()[:2] == '23':
            self.lineEdit().setInputMask('9999999999')
        #self.setAddNone(True)
        #self.lineEdit().setInputMask('9999999999;_')
        #self.setLineEdit(self.lineEdit())
        #self.__searchString = ''
#        self.connect(self.lineEdit, QtCore.SIGNAL('textEdited(QString)'), self.onTextChange)

        self.lineEdit().textEdited[unicode].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    def keyPressEvent(self, event):
        QtGui.QComboBox.keyPressEvent(self, event)

#TODO: Inherit CReferralComboBox from CCompletableComboBox
class CCompletableComboBox(QComboBox):
    def __init__(self, parent):
        QComboBox.__init__(self, parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel()
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # completer, which uses filter model
        self.completer = QCompleter(self.pFilterModel, self)

        #always show all filtered completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)


        self.lineEdit().textEdited[unicode].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    def keyPressEvent(self, event):
        QtGui.QComboBox.keyPressEvent(self, event)