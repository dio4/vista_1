from PyQt4 import QtCore

from Reports.Moscow.Dispatching.Ui_DispatchingSetupDialog import Ui_DispatchingSetupDialog
from library.DialogBase import CDialogBase


class CDispatchingSetupDialog(CDialogBase, Ui_DispatchingSetupDialog):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtDate.setDate(QtCore.QDate.currentDate())
        self.lblReportType.setVisible(False)
        self.cmbReportType.setVisible(False)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtDate.setDate(params.get('date', QtCore.QDate.currentDate()))
        self.edtBegTime.setTime(params.get('begTime', QtCore.QTime()))


    def params(self):
        return {
            'date': self.edtDate.date(),
            'begTime': self.edtBegTime.time()
        }