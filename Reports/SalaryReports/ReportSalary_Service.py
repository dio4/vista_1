# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Orgs.Utils import getOrgStructureFullName
from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from Reports.SalaryReports.Ui_ReportSalary_ServiceSetup import Ui_ReportSalary_ServiceSetupDialog
from library.Utils import forceString, forceInt


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate')
    endDate = params.get('endDate')
    serviceId = params.get('serviceId')
    chkGroup = params.get('chkGroup')

    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAccountItem = db.table('Account_Item')
    tableOrgStructureActionType = db.table('OrgStructure_ActionType')
    tableVrbPersonWithSpeciality = db.table('vrbPersonWithSpeciality')
    tableClient = db.table('Client')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')

    cols = [
        tableActionType['name'].alias('serviceName'),
        tableAccountItem['amount'].alias('serviceAmount'),
        tableAccountItem['price'].alias('servicePrice'),
        db.CONCAT_WS([tableVrbPersonWithSpeciality['code'], tableVrbPersonWithSpeciality['name']], alias='doctorName'),
        tableOrgStructureActionType['master_id'].alias('orgStructId'),
        db.CONCAT_WS([tableClient['lastName'], tableClient['firstName'], tableClient['patrName']], alias='clientName'),
        tableAccountItem['refuseType_id'].alias('refuseType')
    ]

    queryTable = tableEvent.innerJoin(tableAction, [tableEvent['id'].eq(tableAction['event_id'])])
    queryTable = queryTable.innerJoin(tableActionType, [tableAction['actionType_id'].eq(tableActionType['id'])])
    queryTable = queryTable.innerJoin(tableAccountItem, [tableAction['id'].eq(tableAccountItem['action_id']), tableAccountItem['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableOrgStructureActionType, [tableActionType['id'].eq(tableOrgStructureActionType['actionType_id'])])
    queryTable = queryTable.innerJoin(tableAccount, [tableAccountItem['master_id'].eq(tableAccount['id'])])
    queryTable = queryTable.innerJoin(tableContract, [tableAccount['contract_id'].eq(tableContract['id'])])
    queryTable = queryTable.leftJoin(tableVrbPersonWithSpeciality, [tableAction['person_id'].eq(tableVrbPersonWithSpeciality['id'])])
    queryTable = queryTable.leftJoin(tableClient, [tableEvent['client_id'].eq(tableClient['id'])])

    where = [
        tableEvent['deleted'].eq(0),
        tableAccount['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]
    if begDate and endDate:
        where.append(tableAccountItem['date'].dateGe(begDate))
        where.append(tableAccountItem['date'].dateLe(endDate))
    where.append(tableActionType['id'].eq(serviceId))
    where.append(tableAccountItem['refuseType_id'].isNull())
    where.append(db.joinOr([
        tableContract['ignorePayStatusForJobs'].eq(1),
        tableAccountItem['date'].isNotNull()
    ]))

    order = []
    if chkGroup:
        order.append(tableClient['id'])
    order.append(tableVrbPersonWithSpeciality['id'])

    stmt = db.selectStmt(queryTable, cols, where=where, order=order)
    return db.query(stmt)

class CReportSalary_Service(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по заработной плате по услуге')

    def getSetupDialog(self, parent):
        return CReportSalary_ServiceSetupDialog(parent=parent, title=self.title())

    @staticmethod
    def getServiceParams(params):
        return QtGui.qApp.db.query(
            '''
            SELECT
                ActionType.`name`                       AS serviceName,
                OrgStructure_ActionType.`master_id`     AS orgStructId
            FROM
                ActionType
                INNER JOIN OrgStructure_ActionType ON OrgStructure_ActionType.`actionType_id` = ActionType.`id`
            WHERE
                ActionType.`id` = %i
            ''' % params.get('serviceId')
        )

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)

        query = self.getServiceParams(params)
        while query.next():
            record = query.record()
            description.append(u'Подразделение: ' + getOrgStructureFullName(record.value('orgStructId')))
            description.append(u'Услуга: ' + forceString(record.value('serviceName')))

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        chkGroup = params.get('chkGroup')
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()

        self.dumpParams(cursor, params)
        cursor.insertBlock()

        if chkGroup:
            tableColumns = [
                (' 2%',         [u'№'],                    CReportBase.AlignLeft),
                ('10%',         [u'Пациент'],               CReportBase.AlignLeft),
                ('10%',         [u'ФИО исполнителя'],       CReportBase.AlignLeft),
                (' 3%',         [u'Кол-во'],                CReportBase.AlignLeft),
                (' 3%',         [u'Цена'],                  CReportBase.AlignLeft),
                (' 3%',         [u'Сумма'],                 CReportBase.AlignLeft)
            ]

            table = createTable(cursor, tableColumns)

            # real add row
            def addDoctor(sumAmountDoc, sumDoc, table, currClient, currDoctor, index):
                row = table.addRow()
                fields = [
                    index[0],
                    currClient,
                    '' if currDoctor == '!!!' else currDoctor,
                    sumAmountDoc,
                    sumDoc,
                    sumDoc * sumAmountDoc
                ]
                for col, val in enumerate(fields):
                    table.setText(row, col, val)

                index[0] += 1

                return row

            def splitClient(row, streakClient, currClient, index):
                table.mergeCells(row-streakClient+1, 1, streakClient, 1)
                for i in xrange(row-streakClient+1, row+1):
                    table.setText(i, 1, '', clearBefore=True)
                table.setText(row-streakClient+1, 1, currClient, clearBefore=True)

                index[0] -= (streakClient - 1)
                table.mergeCells(row-streakClient+1, 0, streakClient, 1)
                for i in xrange(row-streakClient+1, row+1):
                    table.setText(i, 0, '', clearBefore=True)
                table.setText(row-streakClient+1, 0, index[0], clearBefore=True)
                index[0] += 1

            sumAmount = 0
            sum = 0
            currClient = ''
            currDoctor = '!!!' #Потому что пустая строка с именем доктора — валидные данные
            sumDoc = 0
            sumAmountDoc = 0
            streakClient = 0
            index = [1] #Потому что примитивные типы передаются по значению, а мне нужно по ссылке
            while query.next():
                record = query.record()

                client = forceString(record.value('clientName'))
                doctor = forceString(record.value('doctorName'))

                if currClient == client:

                    if currDoctor == doctor:
                        sumAmountDoc += forceInt(record.value('serviceAmount'))
                        sumDoc += forceInt(record.value('servicePrice'))
                    else:
                        if currDoctor != '!!!':
                            addDoctor(sumAmountDoc, sumDoc, table, currClient, currDoctor, index)
                            streakClient += 1
                        currDoctor = doctor
                        sumDoc = forceInt(record.value('servicePrice'))
                        sumAmountDoc = forceInt(record.value('serviceAmount'))
                else:
                    if currClient != '':
                        sum += sumDoc * sumAmountDoc
                        sumAmount += sumAmountDoc
                        row = addDoctor(sumAmountDoc, sumDoc, table, currClient, currDoctor, index)
                        streakClient += 1

                        if streakClient > 1:
                            splitClient(row, streakClient, currClient, index)
                        streakClient = 0
                    currClient = client
                    currDoctor = doctor
                    sumDoc = forceInt(record.value('servicePrice'))
                    sumAmountDoc = forceInt(record.value('serviceAmount'))

            sum += sumDoc * sumAmountDoc
            sumAmount += sumAmountDoc
            row = addDoctor(sumAmountDoc, sumDoc, table, currClient, currDoctor, index)
            streakClient += 1
            if streakClient > 1:
                splitClient(row, streakClient, currClient, index)

            row = table.addRow()
            table.mergeCells(row, 0, 1, 3)
            table.setText(row, 0, u'ИТОГО')
            table.setText(row, 3, sumAmount)
            table.setText(row, 5, sum)

        else:
            tableColumns = [
                ('10%',         [u''],       CReportBase.AlignLeft),
                (' 3%',         [u'Кол-во'],                CReportBase.AlignLeft),
                (' 3%',         [u'Сумма'],                 CReportBase.AlignLeft)
            ]
            table = createTable(cursor, tableColumns)

            sum = 0
            sumAmount = 0
            while query.next():
                record = query.record()
                sumAmount += forceInt(record.value('serviceAmount'))
                sum += forceInt(record.value('servicePrice')) * sumAmount


            row = table.addRow()
            table.setText(row, 0, u'ИТОГО')
            table.setText(row, 1, sumAmount)
            table.setText(row, 2, sum)

        return doc


class CReportSalary_ServiceSetupDialog(QtGui.QDialog, Ui_ReportSalary_ServiceSetupDialog):
    def __init__(self, parent=None, title=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(title)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.cmbService.setValue(params.get('serviceId', None))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.chkGroup.setChecked(params.get('chkGroup', False))

    def params(self):
        return \
        {
            'begDate'       : self.edtBegDate.date(),
            'endDate'       : self.edtEndDate.date(),
            'serviceId'     : self.cmbService.value(),
            'chkGroup'      : self.chkGroup.isChecked()
        }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        if not self.cmbService.value():
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Необходимо выбрать услугу!')
        else:
            self.accept()


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 3147

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pes',
                      'port' : 3306,
                      'database' : 's12',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CReportSalary_Service(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()