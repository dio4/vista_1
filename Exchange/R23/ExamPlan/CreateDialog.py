# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Exchange.R23.ExamPlan.Utils import ExamKind, PersonCategory
from Exchange.R23.ExamPlan.ui.Ui_CreateDialog import Ui_CreateDialog


class CCreateDialog(QtGui.QDialog, Ui_CreateDialog):
    def __init__(self, parent, selectedMap, existsMap):
        super(CCreateDialog, self).__init__(parent)
        self.setupUi(self)
        self.updateCounts(selectedMap, existsMap)
        self.setWindowTitle(u'Добавить в списки')

    def updateCounts(self, selectedMap, existsMap):
        for examKind, category, widgetCount, widgetTotal in (
                (ExamKind.Dispensary, PersonCategory.General, self.edtExtExam, self.edtExtExamTotal),
                (ExamKind.Dispensary, PersonCategory.HasBenefits, self.edtExtExamDisabled, self.edtExtExamDisabledTotal),
                (ExamKind.Preventive, PersonCategory.General, self.edtPreventiveExam, self.edtPreventiveExamTotal)
        ):
            key = (examKind, category)
            widgetCount.setText(unicode(len(selectedMap.get(key, []))))
            widgetTotal.setText(unicode(existsMap.get(key, 0)))

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.accept()
        else:
            self.reject()
