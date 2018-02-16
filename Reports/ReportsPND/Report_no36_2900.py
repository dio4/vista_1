# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportReHospitalization import Ui_ReportReHospitalizationSetupDialog
from library.Utils import forceString, forceDate
from datetime import date

def selectData(params):
    stmt = u'''
    SELECT id AS ID, name AS NAME, parent_id AS PARENT_ID FROM OrgStructure os;
    '''
    db = QtGui.qApp.db
    return db.query(stmt)

def selectData_reab(params):
    stmt=u'''
    SELECT id AS id_reab FROM OrgStructure o
    WHERE o.name LIKE '%реабилитацион%';
    '''
    db = QtGui.qApp.db
    return db.query(stmt)

def selectData_stac(params):
    stmt=u'''
    SELECT id AS id_stac FROM OrgStructure o
    WHERE o.name LIKE '%Дневной стационар%';
    '''
    db = QtGui.qApp.db
    return db.query(stmt)

class CReportReHospitalizationSetupDialog(QtGui.QDialog, Ui_ReportReHospitalizationSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date()
        }


class CReportReHospitalization(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Организации, имеющие полустационары и реабилитационные подразделения "
                      u"для пвциентов, больных психическими расстройствами")

    def getSetupDialog(self, parent):
        result = CReportReHospitalizationSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('17%', [u'Виды подразделений'], CReportBase.AlignLeft),
            ('3%', [u'№ строки'], CReportBase.AlignLeft),
            ('10%', [u'ПНД (диспансерные отделения и кабинеты)'], CReportBase.AlignLeft),
            ('10%', [u'ПБ и другие стационары'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        query_reab = selectData_reab(params)
        query_stac = selectData_stac(params)

        self.setQueryText(forceString(query.lastQuery()))  #
        self.setQueryText(forceString(query_reab.lastQuery()))
        self.setQueryText(forceString(query_stac.lastQuery()))

        lst_naimenovanie = [u'', u'',
                            u'Дневной стационар',
                            u"Ночной стационар",
                            u"Стационар на дому",
                            u'Реабилитационное отделение стационара',
                            u"Клиника 1-го психиатрического эпизода",
                            u"ЛТМ (ЛПМ)"]

        lst_numbers = [u'', u'', u'1', u'2', u'3', u'4', u'5', u'6']

        for i in range(0, 1):
            i = table.addRow()
            table.setText(i, 0, u'1')
            table.setText(i, 1, u'2')
            table.setText(i, 2, u'3')
            table.setText(i, 3, u'4')

        for i in range(0, 6):
            i = table.addRow()
            table.setText(i, 0, lst_naimenovanie[i])
            table.setText(i, 1, lst_numbers[i])

        ii = 0
        count_daily_stat=0
        count_med_reab = 0

        query_reab.next()
        query_stac.next()
        record_reab = query_reab.record()
        record_stac = query_stac.record()

        id_med_reab = forceString(record_reab.value("id_reab"))
        id_daily_stac = forceString(record_stac.value("id_stac"))
        if id_med_reab != str(0):
            count_med_reab = count_med_reab + 1
        if id_daily_stac != str(0):
            count_daily_stat = count_daily_stat + 1

        while query.next():
            record = query.record()
            if forceString(record.value("PARENT_ID")) == str(id_med_reab):
                count_med_reab = count_med_reab + 1
            if forceString(record.value("PARENT_ID")) == str(id_daily_stac):
                count_daily_stat = count_daily_stat + 1
        table.setText(ii + 2, 2, forceString(count_daily_stat))
        ii = ii + 1

        return doc


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147
    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.3',
                      'port' : 3306,
                      'database' : 'pnd5',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportReHospitalization(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()