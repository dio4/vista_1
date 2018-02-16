# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.interchange        import getCheckBoxValue, getLineEditValue, getTextEditHTML, setCheckBoxValue, \
                                       setLineEditValue, setTextEditHTML
from library.ItemsListDialog    import CItemsListDialog, CItemEditorDialog
from library.TableModel         import CTextCol

from RefBooks.Tables            import rbCode, rbName, rbAccountExportFormat

from Ui_RBAccountExportFormatEditor import Ui_ItemEditorDialog


class CRBAccountExportFormatList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 8),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Подпрограмма', ['prog'], 8),
            ], rbAccountExportFormat, [rbCode, rbName])
        self.setWindowTitleEx(u'Форматы экспорта счетов')

    def getItemEditor(self):
        return CRBAccountExportFormatEditor(self)



class CRBAccountExportFormatEditor(CItemEditorDialog, Ui_ItemEditorDialog):
    setupUi = Ui_ItemEditorDialog.setupUi
    retranslateUi = Ui_ItemEditorDialog.retranslateUi

    def __init__(self,  parent):
        CItemEditorDialog.__init__(self, parent, rbAccountExportFormat)
        self.setWindowTitleEx(u'Формат экспорта счетов')
        self.setupDirtyCather()


    def setRecord(self, record):
        CItemEditorDialog.setRecord(self, record)
        setLineEditValue(self.edtProg, record, 'prog')
        setLineEditValue(self.edtPreferentArchiver, record, 'preferentArchiver')
        setCheckBoxValue(self.chkEmailRequired, record, 'emailRequired')
        setLineEditValue(self.edtEmailTo, record, 'emailTo')
        setLineEditValue(self.edtSubject, record, 'subject')
        setTextEditHTML(self.edtMessage, record, 'message')


    def getRecord(self):
        record = CItemEditorDialog.getRecord(self)
        getLineEditValue(self.edtProg, record, 'prog')
        getLineEditValue(self.edtPreferentArchiver, record, 'preferentArchiver')
        getCheckBoxValue(self.chkEmailRequired, record, 'emailRequired')
        getLineEditValue(self.edtEmailTo, record, 'emailTo')
        getLineEditValue(self.edtSubject, record, 'subject')
        getTextEditHTML(self.edtMessage, record, 'message')
        return record
