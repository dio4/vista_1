# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddCommentDialog.ui'
#
# Created: Tue Nov 18 16:03:57 2014
#      by: PyQt4 UI code generator 4.11
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AddCommentDialog(object):
    def setupUi(self, AddCommentDialog):
        AddCommentDialog.setObjectName(_fromUtf8("AddCommentDialog"))
        AddCommentDialog.resize(339, 250)
        self.gridLayout = QtGui.QGridLayout(AddCommentDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(AddCommentDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.edtPharmacyComment = QtGui.QPlainTextEdit(AddCommentDialog)
        self.edtPharmacyComment.setObjectName(_fromUtf8("edtPharmacyComment"))
        self.gridLayout.addWidget(self.edtPharmacyComment, 1, 0, 1, 2)
        self.lblPharmacy = QtGui.QLabel(AddCommentDialog)
        self.lblPharmacy.setObjectName(_fromUtf8("lblPharmacy"))
        self.gridLayout.addWidget(self.lblPharmacy, 0, 0, 1, 2)
        self.lblRecommendRLS = QtGui.QLabel(AddCommentDialog)
        self.lblRecommendRLS.setObjectName(_fromUtf8("lblRecommendRLS"))
        self.gridLayout.addWidget(self.lblRecommendRLS, 2, 0, 1, 2)
        self.cmbRecommendRLS = CRLSComboBox(AddCommentDialog)
        self.cmbRecommendRLS.setObjectName(_fromUtf8("cmbRecommendRLS"))
        self.gridLayout.addWidget(self.cmbRecommendRLS, 3, 0, 1, 2)

        self.retranslateUi(AddCommentDialog)
        QtCore.QMetaObject.connectSlotsByName(AddCommentDialog)

    def retranslateUi(self, AddCommentDialog):
        AddCommentDialog.setWindowTitle(_translate("AddCommentDialog", "Добавить комментарий", None))
        self.lblPharmacy.setText(_translate("AddCommentDialog", "Для аптеки:", None))
        self.lblRecommendRLS.setText(_translate("AddCommentDialog", "Рекомендованный РЛС:", None))

from library.RLS.RLSComboBox import CRLSComboBox
