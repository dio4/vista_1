# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString, forceDouble

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportRecommendations import Ui_ReportRecommendations


def selectData(params):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    contractIdList = params.get('contractId', None)
    eventType = params.get('eventType', None)
    orgStructure = params.get('orgStructure', None)

    stmt = u'''
    SELECT
        vrbPerson.name AS person,
        ActionType.code AS serviceCode,
        ActionType.name AS serviceName,
        ActionType.amount AS recAmount,
        Account_Item.amount,
        Account_Item.price
    FROM
        Recommendation
        INNER JOIN ActionType ON Recommendation.actionType_id = ActionType.id
        INNER JOIN Event ON Recommendation.setEvent_id = Event.id
        INNER JOIN EventType ON Event.eventType_id = EventType.id
        INNER JOIN vrbPerson ON Event.execPerson_id = vrbPerson.id
        LEFT JOIN Account_Item ON Recommendation.execAction_id = Account_Item.action_id
    WHERE
        %s
    '''

    tableRecommendation = db.table('Recommendation')
    tableAccountItem = db.table('Account_Item')
    tableActionType = db.table('ActionType')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableVrbPerson = db.table('vrbPerson')

    cond = [
        tableRecommendation['deleted'].eq(0),
        tableActionType['deleted'].eq(0),
        tableEvent['deleted'].eq(0),

        db.joinOr([
            tableAccountItem['id'].isNull(),
            db.joinAnd([
                tableAccountItem['deleted'].eq(0),
                tableAccountItem['refuseType_id'].isNull(),
                tableAccountItem['date'].isNotNull(),
            ])
        ]),

        tableRecommendation['setDate'].dateGe(begDate),
        tableRecommendation['setDate'].dateLe(endDate),
    ]
    if contractIdList is not None:
        cond.append(tableEvent['contract_id'].inlist(contractIdList))
    if eventType is not None:
        cond.append(tableEventType['id'].eq(eventType))
    if orgStructure is not None:
        cond.append(tableVrbPerson['orgStructure_id'].eq(orgStructure))
    query = db.query(stmt % db.joinAnd(cond))

    data = {}
    while query.next():
        record = query.record()
        personData = data.setdefault(forceString(record.value('person')), {})
        stats = personData
        serviceData = personData.setdefault((forceString(record.value('serviceCode')), forceString(record.value('serviceName'))), {})
        stats = serviceData
        for param in ['price', 'recommendedAmount', 'paidAmount', 'paidSum']:
            stats.setdefault(param, 0)
        stats['price'] = forceDouble(record.value('price')) if not record.value('price').isNull() else None
        stats['recommendedAmount'] += forceInt(record.value('recAmount'))
        stats['paidAmount'] += forceInt(record.value('amount'))
        stats['paidSum'] += forceDouble(record.value('price')) * stats['paidAmount']
    return query, data


class CReportRecommendationsSetupDialog(QtGui.QDialog, Ui_ReportRecommendations):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', addNone=True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbContract.setPath(params.get('contract', u''))
        self.cmbEventType.setValue(params.get('eventType', None))
        self.cmbOrgStructure.setValue(params.get('orgStructure', None))
        self.chkExtendedReport.setChecked(params.get('extendedReport', False))

    def accept(self):
        if not self.edtBegDate.date().isValid() or not self.edtEndDate.date().isValid() or self.edtBegDate.date() > self.edtEndDate.date():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Неверно задан период. ',
                QtGui.QMessageBox.Ok
            )
            return
        QtGui.QDialog.accept(self)

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'contract': self.cmbContract.getPath(),
            'contractId': self.cmbContract.getIdList(),
            'extendedReport': self.chkExtendedReport.isChecked(),
            'orgStructure': self.cmbOrgStructure.value(),
            'eventType': self.cmbEventType.value()
        }


class CReportRecommendations(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Отчет по направлениям")

    def getSetupDialog(self, parent):
        result = CReportRecommendationsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        agentShare = 0.05
        extendedReport = params.get('extendedReport')

        def printAll(data):
            for person in data:
                printService(person, data[person])

        def printService(person, data):
            for serviceCode, serviceName in data:
                i = table.addRow()
                table.setText(i, 0, person)
                if extendedReport:
                    table.setText(i, 1, serviceCode)
                table.setText(i, 2 if extendedReport else 1, serviceName)
                printSum(data[(serviceCode, serviceName)], i)

        def printSum(data, row):
            if extendedReport:
                if data['price'] is not None:
                    table.setText(row, len(tableColumns) - 5, data['price'])
                table.setText(row, len(tableColumns) - 4, data['recommendedAmount'])
            table.setText(row, len(tableColumns) - 3, data['paidAmount'])
            table.setText(row, len(tableColumns) - 2, "%.2f" % data['paidSum'], blockFormat=CReportBase.AlignRight)
            table.setText(row, len(tableColumns) - 1, "%.2f" % (agentShare * data['paidSum']), blockFormat=CReportBase.AlignRight)

        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Отчет по направителям')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('20?', [u'ФИО врача'], CReportBase.AlignLeft)
        ]
        if extendedReport:
            tableColumns.append(('10?', [u'Код услуги'], CReportBase.AlignLeft))
        tableColumns.append(('30?', [u'Наименование услуги'], CReportBase.AlignLeft))
        if extendedReport:
            tableColumns += [
                ('10?', [u'Цена услуги'], CReportBase.AlignRight),
                ('10?', [u'Количество назначенных услуг'], CReportBase.AlignLeft)
            ]
        tableColumns += [
            ('10?', [u'Количество оплаченных услуг'], CReportBase.AlignLeft),
            ('10?', [u'Сумма оплаченных услуг'], CReportBase.AlignRight),
            ('10?', [u'Агентское вознаграждение'], CReportBase.AlignRight)
        ]
        table = createTable(cursor, tableColumns)

        query, data = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))

        printAll(data)

        return doc

