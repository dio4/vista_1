# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ExposedServicesReportsSetup import Ui_ExposedServicesReportsSetupDialog
from library.Utils import forceDate, forceInt, forceString, forceDouble


def dumpParams(self, cursor):
    currentDate = QtCore.QDate.currentDate()
    cursor.insertText(u'Дата предоставления информации: ' + currentDate.toString('dd.MM.yyyy'))
    cursor.insertBlock()
    orgId = QtGui.qApp.currentOrgId()
    db = QtGui.qApp.db
    tableOrganisation = db.table('Organisation')
    stmt = db.selectStmt(tableOrganisation, tableOrganisation['fullName'], '`id` = %s' %orgId)
    query = QtGui.qApp.db.query(stmt)
    if query.first():
        record = query.record()
        cursor.insertText(u'Наименование медицинской организации: ' + forceString(record.value('fullName')))
        cursor.insertBlock()
    cursor.insertText(u'Реестровый номер медицинской организации: ' + forceString(orgId))


class CExposedServicesReportsSetupDialog(QtGui.QDialog, Ui_ExposedServicesReportsSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', False)#, QtGui.qApp.db.joinAnd(cond))
        self.cmbFinance.setTable('rbFinance', False)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))

        self.cmbOrgStructure.setValue(params.get('orgStructure_id', date))
        self.cmbFinance.setValue(params.get('finance_id', date))
        self.cmbContract.setPath(params.get('contractPath', date))
        self.cmbEventType.setValue(params.get('eventType_id', date))

    def params(self):
        result = {}
        result['orgStructure_id'] = self.cmbOrgStructure.value()
        result['finance_id'] = self.cmbFinance.value()
        result['contract_id'] = self.cmbContract.getIdList()
        result['contractPath'] = self.cmbContract.getPath()
        result['eventType_id'] = self.cmbEventType.value()

        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        return result


class CExposedServicesReports(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setTitle(u'Отчет по выставленным услугам и расчету з/п')

    def getSetupDialog(self, parent):
        result = CExposedServicesReportsSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def selectData(self, params):
        def get_sql_list(lst):
            y = ''
            for x in lst:
                y += '%s' %x
                if x != lst[-1]:
                    y += ','
            return y

        stmt = u"""
            SELECT DISTINCT
              CONCAT(c.lastName, ' ', CONCAT(c.firstName, ' ', c.patrName)) AS 'clientName',
              e.externalId AS 'ibNumber',
              at.title AS 'serviceName',
              a.begDate,
              a.endDate,
              a.payStatus,
              ai.sum,
              os.name AS 'OrgStructName',
              vrbp.name AS 'personName',
              p.lastName AS 'guidPersonName',
              cce.percent AS 'tariffPercent',
              os.salaryPercentage,
              at.serviceType,
              os.infisDepTypeCode,
              e.eventType_id,
              a.finance_id,
              a.contract_id,
              p.orgStructure_id
            FROM
              Action a
              INNER JOIN ActionType at ON a.actionType_id = at.id

              INNER JOIN Event e ON a.event_id = e.id
              INNER JOIN Client c ON e.client_id = c.id

              INNER JOIN Account_Item ai ON a.id = ai.action_id AND ai.deleted = 0

              INNER JOIN vrbPersonWithSpeciality vrbp ON a.person_id = vrbp.id
              INNER JOIN OrgStructure os ON vrbp.orgStructure_id = os.id

              INNER JOIN Person p ON a.createPerson_id = p.id # a.setPerson_id = p.id

              LEFT JOIN Contract c1 ON e.contract_id = c1.id
              LEFT JOIN rbContractType ct1 ON c1.typeId = ct1.id
              LEFT JOIN Contract_Tariff ct ON ct.master_id = c1.id
              LEFT JOIN Contract_CompositionExpense cce ON ct.id = cce.master_id
            WHERE
              ct.service_id = at.nomenclativeService_id
              AND a.payStatus = 64

              AND DATEDIFF(a.begDate, DATE(%s)) >= 0
              AND DATEDIFF(a.endDate, DATE(%s)) <= 0
              %s
              %s
              %s
              %s
            LIMIT 10
            ;
        """ % (
            "'" + forceDate(params['begDate']).toString('yyyy-MM-dd') + "'",
            "'" + forceDate(params['endDate']).toString('yyyy-MM-dd') + "'",

            "AND e.eventType_id = %s" % params['eventType_id'] if params['eventType_id'] else "",
            "AND a.finance_id = %s" % params['finance_id'] if params['finance_id'] else "",
            "AND p.orgStructure_id = %s" % params['orgStructure_id'] if params['orgStructure_id'] else "",
            "AND a.contract_id in (%s)" % get_sql_list(params['contract_id']) if params['contract_id'] else ""
        )

        """
            Search template:
                    -- Period: [begDate; endDate]
                    AND DATEDIFF(a.begDate, DATE('2016-03-29')) >= 0
                    AND DATEDIFF(a.endDate, DATE('2016-04-29')) <= 0
                    -- Type of event: eventType_id
                    AND e.eventType_id = 91
                    -- Financer: finance_id
                    AND a.finance_id = 3
                    -- Contract: contract_id
                    AND a.contract_id = 18
                    -- Departament: orgStructure_id
                    AND p.orgStructure_id = 43
        """
        return stmt

    def build(self, params):
        tableColumns = [
            ('5%', u'№', CReportBase.AlignCenter),
            ('10%', u'ФИО', CReportBase.AlignCenter),
            ('5%', u'№ ИБ', CReportBase.AlignCenter),
            ('20%', u'Услуга', CReportBase.AlignCenter),
            ('6%', u'Начато', CReportBase.AlignCenter),
            ('6%', u'Закончено', CReportBase.AlignCenter),
            ('6%', u'Сумма', CReportBase.AlignCenter),
            ('10%', u'Подразделение оказавшие услугу ', CReportBase.AlignCenter),
            ('15%', u'ФИО исполнителя', CReportBase.AlignCenter),
            ('10%', u'Направитель', CReportBase.AlignCenter),
            ('10%', u'% Исполнителю', CReportBase.AlignCenter),
            ('10%', u'11%', CReportBase.AlignCenter),
            ('10%', u'Итого к распределению', CReportBase.AlignCenter),
            ('10%', u'% исполнителю операции', CReportBase.AlignCenter),
            ('10%', u'11% резерв отпусков ', CReportBase.AlignCenter),
            ('10%', u'Итого  к распределению', CReportBase.AlignCenter),
            ('10%', u'По всем отделениям 10% - исполнителям оперблока', CReportBase.AlignCenter),
            ('10%', u'Итого  к распределению', CReportBase.AlignCenter),
            ('10%', u'3% направителю', CReportBase.AlignCenter),
            ('10%', u'11% резерв отпусков', CReportBase.AlignCenter)
        ]

        bf = QtGui.QTextCharFormat()
        bf.setFontWeight(QtGui.QFont.Bold)

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Отчет по выставленным услугам и расчету з/п:')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        dumpParams(self, cursor)
        cursor.insertBlock()
        cursor.insertBlock()

        table = createTable(cursor, tableColumns)
        #table_part = createTable(cursor, tableColumns)

        query = QtGui.qApp.db.query(self.selectData(params))
        self.setQueryText(forceString(query.lastQuery()))
        counter = 0
        while query.next():
            counter += 1
            record = query.record()
            i = table.addRow()

            table.setText(i, 0, counter)
            table.setText(i, 1, forceString(record.value('clientName')))
            table.setText(i, 2, forceInt(record.value('ibNumber')))
            table.setText(i, 3, forceString(record.value('serviceName')))
            table.setText(i, 4, forceDate(record.value('begDate')).toString('MM/dd/yyyy'))
            table.setText(i, 5, forceDate(record.value('endDate')).toString('MM/dd/yyyy'))
            table.setText(i, 6, forceDouble(record.value('sum')))
            table.setText(i, 7, forceString(record.value('OrgStructName')))
            table.setText(i, 8, forceString(record.value('personName')))
            table.setText(i, 9, forceString(record.value('guidPersonName')))

            sum = forceDouble(record.value('sum'))
            tariffPercent = forceDouble(record.value('tariffPercent'))
            salaryPercentage = forceDouble(record.value('salaryPercentage'))

            temp_value = None
            if tariffPercent:
                temp_value = sum * (tariffPercent / 100.0)
                table.setText(i, 10, temp_value)
            elif salaryPercentage:
                temp_value = sum * (salaryPercentage / 100.0)
                table.setText(i, 10, temp_value)

            if temp_value:
                table.setText(i, 11, temp_value * 0.11)
                table.setText(i, 12, temp_value * 0.89) # temp_value - temp_value * 0.11

            if forceInt(record.value('serviceType')) == 4 and salaryPercentage:
                temp_value = sum * (salaryPercentage / 100.0)
                table.setText(i, 13, temp_value)
                table.setText(i, 14, temp_value * 0.11)
                table.setText(i, 15, temp_value * 0.89)  # temp_value - temp_value * 0.11

            table.setText(i, 16, sum * 0.1)
            table.setText(i, 17, sum * 0.011) # 11% от sum * 0.1
            table.setText(i, 18, sum * 0.0033) # 3% от sum * 0.011
            table.setText(i, 19, sum * 0.000363)  # 11% от sum * 0.0033
        return doc
