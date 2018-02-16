# encoding=utf8

from PyQt4 import QtGui

from Ui_UpdatesChecker import Ui_UpdatesCheckerDialog
from library.Utils import forceString, forceInt
from sql.updates_list import updates_list

STATUS_MAP = {
    -1: u'Отсутствует',
    0: u'Не выполнен',
    1: u'Выполнен'
}


class CUpdatesChecker(QtGui.QDialog):
    def __init__(self, parent=None):
        super(CUpdatesChecker, self).__init__(parent)
        self.ui = Ui_UpdatesCheckerDialog()
        self.ui.setupUi(self)

        self.ui.buttonBox.clicked.connect(self.close)

        self.load_list()

    def load_list(self):
        result = dict((number, -1) for number in updates_list)
        for rec in QtGui.qApp.db.iterRecordList(stmt=u'SELECT updateNumber, completed'
                                                     u' FROM DatabaseUpdateInfo'
                                                     u' WHERE updateNumber IS NOT NULL AND updateNumber != \'\''):
            result[forceString(rec.value('updateNumber'))] = forceInt(rec.value('completed'))
        for number in sorted(result.keys()):
            row = self.ui.table.rowCount()
            self.ui.table.setRowCount(row + 1)
            self.ui.table.setItem(row, 0, QtGui.QTableWidgetItem(number))
            self.ui.table.setItem(row, 1, QtGui.QTableWidgetItem(STATUS_MAP[result[number]]))


if __name__ == '__main__':
    app = QtGui.QApplication()
    w = CUpdatesChecker().show()
    app.exec_()
