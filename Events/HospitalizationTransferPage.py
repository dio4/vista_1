#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Events.EventInfo import CEventHospTransferInfo
from Events.Ui_HospitalizationTransferPage import Ui_HospitalizationTransferPage
from library.DialogBase import CConstructHelperMixin
from library.InDocTable import CInDocTableModel, CDateInDocTableCol, CRBInDocTableCol, CInDocTableCol
from library.crbcombobox import CRBComboBox


class CHospitalizationTransferPage(QtGui.QWidget, Ui_HospitalizationTransferPage, CConstructHelperMixin):
    def __init__(self, parent, eventId):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.addModels('HospTransfer', CHospTransferTableModel(self))
        self.setModels(self.tblHospitalizationTransfer, self.modelHospTransfer, self.selectionModelHospTransfer)

        if eventId:
            self.modelHospTransfer.loadItems(eventId)

        self.modelHospTransfer.setEditable(False)
        self.tblHospitalizationTransfer.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)


class CHospTransferTableModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, CEventHospTransferInfo.tableName, 'id', 'event_id', parent)
        self.addCol(CDateInDocTableCol(
            u'Предыдущая дата', 'dateFrom', 15))
        self.addCol(CDateInDocTableCol(
            u'Новая дата', 'dateTo', 15))
        self.addCol(CRBInDocTableCol(
            u'Инициатор переноса', 'person_id', 20, 'vrbPersonWithSpeciality', showFields=CRBComboBox.showName))
        self.addCol(CInDocTableCol(
            u'Причина переноса', 'comment', 20))
        self.addCol(CInDocTableCol(
            u'Диагноз', 'diagnosis', 20))
        self.addCol(CInDocTableCol(
            u'Метод лечения', 'treatmentMethod', 20))
        self.addCol(CInDocTableCol(
            u'Рекомендуемое лечение', 'recommendedTreatment', 20))
        self.addCol(CInDocTableCol(
            u'Лечебное отделение', 'treatmentOrgStructure', 20))


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pes',
        'port': 3306,
        'database': 's12',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    QtGui.qApp.userId = 1

    w = CHospitalizationTransferPage(None, 1243474)
    w.show()
    QtGui.qApp.exec_()


if __name__ == '__main__':
    main()
