# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore

from library.interchange import setLineEditValue, getLineEditValue, setCheckBoxValue, getCheckBoxValue

from library.ItemsListDialog import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel import CTextCol, CBoolCol
from RefBooks.Ui_AdditionalFeaturesUrlEditor import Ui_ItemEditorDialog as Ui

class CRBAdditionalFeaturesUrlList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(   u'Наименование', ['name'], 30),
            CTextCol(   u'Шаблон',       ['template'], 50),
            CBoolCol(   u'Картотека',    ['tabRegistry'], 5),
            CBoolCol(   u'Обращения',    ['tabEvents'], 5),
            CBoolCol(   u'Медкарта',     ['tabAmbCard'], 5),
            CBoolCol(   u'Обслуживание', ['tabActions'], 5),
            ], 'AdditionalFeaturesUrl', ['id'])
        self.setWindowTitleEx(u'Связанные URL')

    def getItemEditor(self):
        return CRBAdditionalFeaturesUrlEditor(self)
#
# ##########################################################################
#

class CRBAdditionalFeaturesUrlEditor(CItemEditorBaseDialog, Ui):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'AdditionalFeaturesUrl')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Связанные URL')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(   self.edtName,         record, 'name')
        setLineEditValue(   self.edtTemplate,     record, 'template')
        setCheckBoxValue(   self.chkTabRegistry,  record, 'tabRegistry')
        setCheckBoxValue(   self.chkTabEvents,    record, 'tabEvents')
        setCheckBoxValue(   self.chkTabAmbCard,   record, 'tabAmbCard')
        setCheckBoxValue(   self.chkTabActions,   record, 'tabActions')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(   self.edtName,         record, 'name')
        getLineEditValue(   self.edtTemplate,     record, 'template')
        getCheckBoxValue(   self.chkTabRegistry,  record, 'tabRegistry')
        getCheckBoxValue(   self.chkTabEvents,    record, 'tabEvents')
        getCheckBoxValue(   self.chkTabAmbCard,   record, 'tabAmbCard')
        getCheckBoxValue(   self.chkTabActions,   record, 'tabActions')
        return record
