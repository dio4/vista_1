# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore

from library.ItemsListDialog    import CItemEditorBaseDialog, CItemsListDialog
from library.TableModel         import CTextCol
from library.Utils              import forceString, forceStringEx, toVariant

from RefBooks.Tables            import rbCode, rbName

from Ui_RBMKBMorphologyEditor   import Ui_MKBMorphologyEditor


class CRBMKBMorphologyList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 8),
            CTextCol(u'Наименование', [rbName], 40),
            CTextCol(u'Группа', ['group'], 8),
            CTextCol(u'Нижняя граница МКБ', ['bottomMKBRange1'], 8), 
            CTextCol(u'Верхняя граница МКБ', ['topMKBRange1'], 8), 
            CTextCol(u'Нижняя граница МКБ', ['bottomMKBRange2'], 8), 
            CTextCol(u'Верхняя граница МКБ', ['topMKBRange2'], 8) 
            ], 'MKB_Morphology', [rbCode, rbName])
        self.setWindowTitleEx(u'Морфология диагнозов МКБ')
        
    def getItemEditor(self):
        return CRBMKBMorphologyEditor(self)

#    def select(self, props):
#        table = self.model.table()
#        return QtGui.qApp.db.getIdList(table.name(), self.idFieldName, '`group` IS NOT NULL', self.order)

class CRBMKBMorphologyEditor(CItemEditorBaseDialog, Ui_MKBMorphologyEditor):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'MKB_Morphology')
        self.setupUi(self)
        self.cmbGroup.setTable('MKB_Morphology', addNone=True, filter='`group` IS NULL')
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Морфологтя диагноза МКБ')
        self.setupDirtyCather()
        
    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbGroup.setCode(forceString(record.value('group')))
        self.cmbDiagRangeFrom1.setText(forceString(record.value('bottomMKBRange1')))
        self.cmbDiagRangeTo1.setText(forceString(record.value('topMKBRange1')))
        self.cmbDiagRangeFrom2.setText(forceString(record.value('bottomMKBRange2')))
        self.cmbDiagRangeTo2.setText(forceString(record.value('topMKBRange2')))
        
    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,            toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,            toVariant(forceStringEx(self.edtName.text())))
        record.setValue('group',           toVariant(forceStringEx(self.cmbGroup.code())))
        record.setValue('bottomMKBRange1', toVariant(forceStringEx(self.cmbDiagRangeFrom1.text())))
        record.setValue('topMKBRange1',    toVariant(forceStringEx(self.cmbDiagRangeTo1.text())))
        record.setValue('bottomMKBRange2', toVariant(forceStringEx(self.cmbDiagRangeFrom2.text())))
        record.setValue('topMKBRange2',    toVariant(forceStringEx(self.cmbDiagRangeTo2.text())))
        return record

    def checkDataEntered(self):
        result = CItemEditorBaseDialog.checkDataEntered(self)
        result = result and self.checkCmbGroup()
        return result
        
    def badGroupCode(self):
        return self.checkValueMessage(u'Указан не подходящий код группы', False, self.cmbGroup)
        
    def checkCmbGroup(self):
        groupCode = self.cmbGroup.code()
        if bool(groupCode):
            code = forceStringEx(self.edtCode.text())
            chkCode = code[1:4]
            try:
                iChkCode = int(chkCode)
                codeRange = groupCode.split('-')
                bCode = codeRange[0]
                if len(codeRange) == 2:
                    eCode = codeRange[1]
                else:
                    eCode = None
                if bool(eCode):
                    iBegCode = int(bCode[1:4])
                    iEndCode = int(eCode[1:4])
                    if iChkCode >= iBegCode and iChkCode <= iEndCode:
                        return True
                else:
                    iCode = int(bCode[1:4])
                    if iChkCode == iCode:
                        return True
                return self.badGroupCode()
                    
            except:
                return self.badGroupCode()
        return True
