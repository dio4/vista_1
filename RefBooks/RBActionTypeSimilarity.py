# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action              import CActionTypeCache

from library.crbcombobox        import CRBComboBox
from library.ItemsListDialog    import CItemsListDialog, CItemEditorBaseDialog
from library.TableModel         import CRefBookCol
from library.Utils              import forceRef, toVariant, forceInt

from RefBooks.ActionType        import CFindDialog
from RefBooks.Tables            import rbActionTypeSimilarity

from Ui_RBActionTypeSimilarityEditor import Ui_ItemEditorDialog


class CRBActionTypeSimilarityList(CItemsListDialog):
    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CRefBookCol(    u'Код',              ['firstActionType_id'], 'ActionType', 30, CRBComboBox.showCodeAndName),
            CRefBookCol(    u'Код',              ['secondActionType_id'], 'ActionType', 30, CRBComboBox.showCodeAndName)
            ], rbActionTypeSimilarity, [])
        self.setWindowTitleEx(u'Взаимозаменяемые типы действий')


    def getItemEditor(self):
        return CRBActionTypeSimilarityEditor(self)

#
# ##########################################################################
#

class CRBActionTypeSimilarityEditor(CItemEditorBaseDialog, Ui_ItemEditorDialog):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, rbActionTypeSimilarity)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Взаимозаменяемые типы действий')
        self.setupDirtyCather()
        self.firstAT = None
        self.secondAT = None
        self.props = {}

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.firstAT = CActionTypeCache.getById(forceRef(record.value('firstActionType_id')))
        self.secondAT = CActionTypeCache.getById(forceRef(record.value('secondActionType_id')))
        self.cmbSimilarityType.setCurrentIndex(forceInt(record.value('similarityType')))
        self.updateLabels()
        self.setIsDirty(False)


    def getRecord(self):
        if self.firstAT is None or self.secondAT is None:
            return None
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('firstActionType_id', toVariant(self.firstAT.id))
        record.setValue('secondActionType_id', toVariant(self.secondAT.id))
        record.setValue('similarityType', toVariant(self.cmbSimilarityType.currentIndex()))
        return record

    def checkDataEntered(self):
        result = True
        result = result and (self.firstAT or self.checkInputMessage(u'тип действия', False, self.btnFirstAT))
        result = result and (self.secondAT or self.checkInputMessage(u'тип действия', False, self.btnSecondAT))
        return result

    def updateLabels(self):
        if self.firstAT:
            self.lblFirstAT.setText(u'%s | %s' % (self.firstAT.code, self.firstAT.name))
        else:
            self.lblFirstAT.setText(u'Не задано')
        if self.secondAT:
            self.lblSecondAT.setText(u'%s | %s' % (self.secondAT.code, self.secondAT.name))
        else:
            self.lblSecondAT.setText(u'Не задано')

    @QtCore.pyqtSlot()
    def on_btnFirstAT_clicked(self):
        dialog = CFindDialog(self)
        while True:
            dialog.setProps(self.props)
            if dialog.exec_():
                self.props = dialog.getProps()
                firstATid = dialog.id()
                if firstATid:
                    firstAT = CActionTypeCache.getById(firstATid)
                    if firstAT and self.secondAT and not firstAT.isSimilar(self.secondAT) and self.cmbSimilarityType.currentIndex() != 1:
                        QtGui.QMessageBox.warning(self, self, u'Внимание!',
                                            u'Пожалуйста, убедитесь, что вы выбираете идентичные по структуре типы действий.')
                        continue
                    self.firstAT = firstAT
                else:
                    self.fistAT = None
            self.updateLabels()
            break

    @QtCore.pyqtSlot()
    def on_btnSecondAT_clicked(self):
        dialog = CFindDialog(self)
        while True:
            dialog.setProps(self.props)
            if dialog.exec_():
                self.props = dialog.getProps()
                secondATid = dialog.id()
                if secondATid:
                    secondAT = CActionTypeCache.getById(secondATid)
                    if self.firstAT and secondAT and not self.firstAT.isSimilar(secondAT) and self.cmbSimilarityType.currentIndex() != 1:
                        QtGui.QMessageBox.warning(self, u'Внимание!',
                                            u'Пожалуйста, убедитесь, что вы выбираете идентичные по структуре типы действий.')
                        continue
                    self.secondAT = secondAT

                else:
                    self.secondAT = None
            self.updateLabels()
            break
