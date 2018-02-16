# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Reports.Moscow.Ui_NonPaidEventsSetupDialog import Ui_NonPaidEventsSetupDialog
from Reports.Report import CReport
from Reports.ReportBase import createTable
from library.DialogBase import CDialogBase
from library.Utils import forceString
from library.constants import dateLeftInfinity, dateRightInfinity


def selectData(begDate, endDate, contractIds):
    db = QtGui.qApp.db

    moreFilters = u'1=1'

    if contractIds:
        moreFilters += u' AND c.id IN ({})'.format(u', '.join(str(x) for x in contractIds))

    stmt = u'''
    SELECT
      CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS client_name,
      e.id AS event_id,
      SUM(a.amount * ct.price) AS sum
    FROM Event e
      LEFT JOIN Client ON e.client_id = Client.id AND Client.deleted = 0
      LEFT JOIN Contract c ON e.contract_id = c.id AND c.deleted = 0
      LEFT JOIN rbFinance cf ON c.finance_id = cf.id AND cf.name = 'ПМУ'
      LEFT JOIN Action a ON e.id = a.event_id AND a.deleted = 0
      LEFT JOIN Contract ac ON a.contract_id = ac.id AND ac.deleted = 0
      LEFT JOIN rbFinance acf ON ac.finance_id = acf.id AND acf.name = 'ПМУ'
      LEFT JOIN rbFinance af ON a.finance_id = af.id AND af.name = 'ПМУ'
      LEFT JOIN ActionType at ON a.actionType_id = at.id AND at.deleted = 0
      LEFT JOIN ActionType_Service ats ON at.id = ats.master_id
      LEFT JOIN rbService s ON ats.service_id = s.id
      LEFT JOIN Contract_Tariff ct ON s.id = ct.service_id AND ct.master_id = IF(a.contract_id IS NOT NULL, a.contract_id, e.contract_id)
    WHERE
      (acf.id IS NOT NULL OR
       af.id IS NOT NULL OR
       cf.id IS NOT NULL) AND
      a.payStatus NOT IN (512, 768) AND
      a.amount > 0 AND ct.price IS NOT NULL AND
      e.execDate BETWEEN '{startDate}' AND '{endDate}' AND
      ({moreFilters})
    GROUP BY e.id
    '''.format(startDate=begDate, endDate=endDate, moreFilters=moreFilters)

    return db.query(stmt)


class CNonPaidEventsReport(CReport):
    def __init__(self, parent=None):
        CReport.__init__(self, parent)
        self.setTitle(u'Неоплаченность событий')

    def getSetupDialog(self, parent):
        result = CSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate().currentDate().addYears(-1)).toString('yyyy-MM-dd')
        endDate = params.get('endDate', QtCore.QTime().currentTime()).toString('yyyy-MM-dd')
        contractIds = params.get('contractIds', None)

        doc = QtGui.QTextDocument()

        bfLeft = QtGui.QTextBlockFormat()
        bfLeft.setAlignment(QtCore.Qt.AlignLeft)

        bfCenter = QtGui.QTextBlockFormat()
        bfCenter.setAlignment(QtCore.Qt.AlignCenter)

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReport.ReportTitle)
        cursor.setBlockFormat(bfCenter)
        cursor.insertText(u'Отчет по неоплаченности событий')
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('60%', u'ФИО клиента', CReport.AlignLeft),
            ('20%', u'ID события', CReport.AlignLeft),
            ('20%', u'Сумма', CReport.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        queryData = selectData(begDate, endDate, contractIds)
        self.addQueryText(forceString(queryData.lastQuery()))
        while queryData.next():
            record = queryData.record()
            table.addRowWithContent(
                forceString(record.value('client_name')),
                forceString(record.value('event_id')),
                forceString(record.value('sum'))
            )

        return doc


class CSetupDialog(CDialogBase, Ui_NonPaidEventsSetupDialog):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.begDate.setDate(QtCore.QDate().currentDate().addYears(-1))
        self.endDate.setDate(QtCore.QDate().currentDate())
        self.cmbContract._model.setContractDates(dateLeftInfinity, dateRightInfinity)
        self.lblOrgStructure.setVisible(False)
        self.cmbOrgStructure.setVisible(False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.begDate.setDate(params.get('begDate', QtCore.QDate().currentDate().addYears(-1)))
        self.endDate.setDate(params.get('endDate', QtCore.QDate().currentDate()))

    def params(self):
        return {
            'begDate': self.begDate.date(),
            'endDate': self.endDate.date(),
            'contractIds': self.cmbContract.getIdList(),
            'orgStructureId': self.cmbOrgStructure.value()
        }
