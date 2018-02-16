# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Events.Ui_AddCommentDialog          import Ui_AddCommentDialog
from library.DialogBase                    import CConstructHelperMixin
from library.TableModel                    import *

class CAddCommentSetupDialog(QtGui.QDialog, Ui_AddCommentDialog, CConstructHelperMixin):

    def __init__(self, comment = '', rlsCode = 0, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        if comment:
            self.edtPharmacyComment.clear()
            self.edtPharmacyComment.insertPlainText(comment)
        else:
            self.edtPharmacyComment.clear()
        if rlsCode:
            self.cmbRecommendRLS.setValue(rlsCode)

    def getData(self):
        return self.edtPharmacyComment.toPlainText(), forceInt(self.cmbRecommendRLS.value()) if self.cmbRecommendRLS.value() else 0

    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.accept()
        else:
            self.reject()