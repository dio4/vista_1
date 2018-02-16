from Ui_ErrorBox import Ui_Dialog
from PyQt4 import QtGui, QtCore


class CErrorBox(Ui_Dialog, QtGui.QDialog):
    def __init__(self, parent, tb):
        super(CErrorBox, self).__init__(parent)
        self.setupUi(self)
        self.textBrowser.setVisible(False)
        self.textBrowser.setText(tb)
        self.detailsToggled()
        self.btnDetails.toggled.connect(self.detailsToggled)

    def detailsToggled(self, state=False):
        if state:
            self.setMaximumHeight((1 << 24) - 1)  # QWIDGETSIZE_MAX
            self.setMinimumHeight(self.sizeHint().height())
        else:
            self.setFixedHeight(self.sizeHint().height())


