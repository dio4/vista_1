# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Reports.Ui_ReportAnalizeBillOnDirectionsSetup import Ui_ReportAnalizeBillOnDirectionSetup
from library.Utils import forceString, forceRef, forceDouble


def selectData(params):
    db = QtGui.qApp.db

    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    contractIds = params.get('contractIds', None)

    tableEvent = db.table('Event')
    tableAccountItem = db.table('Account_Item')
    tableService = db.table('rbService')
    tablePerson = db.table('vrbPerson')
    tableOrgStructure = db.table('OrgStructure')
    tableAccount = db.table('Account')
    tableContract = db.table('Contract')
    tableRbServiceSpecification = db.table('rbServiceSpecification')
    tableRbServiceSpecificationPost = db.table('rbServiceSpecification_Post')
    tableRbPost = db.table('rbPost')

    queryTable = tableEvent
    queryTable = queryTable.innerJoin(tableAccountItem, tableAccountItem['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableService, tableService['id'].eq(tableAccountItem['service_id']))
    queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tablePerson['orgStructure_id']))
    queryTable = queryTable.innerJoin(tableRbServiceSpecification, tableService['id'].eq(tableRbServiceSpecification['service_id']))
    queryTable = queryTable.innerJoin(tableRbServiceSpecificationPost, tableRbServiceSpecification['id'].eq(tableRbServiceSpecificationPost['specification_id']))
    queryTable = queryTable.innerJoin(tableRbPost, tableRbServiceSpecificationPost['post_id'].eq(tableRbPost['id']))

    fields = [
        tableEvent['id'].alias('eventId'),
        tableEvent['externalId'],
        tableAccountItem['master_id'].alias('accountId'),
        tablePerson['name'].alias('personName'),
        tableService['name'].alias('serviceName'),
        tableAccountItem['amount'],
        tableAccountItem['price'],
        tableAccountItem['sum'],
        u'''IF (OrgStructure.name like '%методы исследования%', 0,
            SUM(rbServiceSpecification_Post.`price`)) AS `postPriceSum`''',
    ]

    cond = [
        tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()),
        tableEvent['deleted'].eq(0),
        tableAccountItem['deleted'].eq(0)
    ]
    if begDate:
        cond.append(tableEvent['execDate'].dateGe(begDate))
    if endDate:
        cond.append(tableEvent['execDate'].dateLe(endDate))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if personId:
        cond.append(tablePerson['id'].eq(personId))
    if contractIds:
        queryTable = queryTable.innerJoin(tableAccount, [tableAccountItem['master_id'].eq(tableAccount['id'])])
        queryTable = queryTable.innerJoin(tableContract, [tableAccount['contract_id'].eq(tableContract['id'])])
        cond.append(tableContract['id'].inlist(contractIds))
        cond.append(tableContract['deleted'].eq(0))
        cond.append(tableAccount['deleted'].eq(0))

    stmt = db.selectStmt(queryTable, fields, cond, order=[tableAccountItem['master_id'], tableEvent['id']], group=[tableAccountItem['master_id'], tableEvent['id']])

    return db.query(stmt)


class CReportAnalizeBillOnDirectionsSetupDialog(QtGui.QDialog, Ui_ReportAnalizeBillOnDirectionSetup):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)
        self.needUpdateContract = False
        self.defaultContractPath = ''
        self.endDateYear = QtCore.QDate.currentDate().year()
        self.begDateYear = QtCore.QDate.currentDate().year()

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.needUpdateContract = True
        self.defaultContractPath = params.get('contractPath', None)
        self.setContractDates()


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['contractIds'] = self.cmbContract.getIdList()
        result['contractPath'] = self.cmbContract.getPath()
        result['contractText'] = forceString(self.cmbContract.currentText())
        return result

    def setContractDates(self):
        if self.needUpdateContract:
            self.cmbContract._model.setContractDates(QtCore.QDate(self.edtBegDate.date().year(), 1, 1),
                                                     QtCore.QDate(self.edtEndDate.date().year(), 12, 31))
        self.cmbContract.setPath(self.defaultContractPath)

    def on_cmbOrgStructure_currentIndexChanged(self, index):
        if self.cmbOrgStructure.value():
            self.cmbPerson.setFilter('orgStructure_id in (%s)' %(', '.join(['%d'%id for id in getOrgStructureDescendants(self.cmbOrgStructure.value())])))

    def on_edtBegDate_dateChanged(self, date):
        if self.begDateYear != self.edtBegDate.date().year():
            self.begDateYear = self.edtBegDate.date().year()
            self.setContractDates()

    def on_edtEndDate_dateChanged(self, date):
        if self.endDateYear != self.edtEndDate.date().year():
            self.endDateYear = self.edtEndDate.date().year()
            self.setContractDates()





class CReportAnalizeBillOnDirections(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Отчёт по направлениям для ЦЛиП")

    def getSetupDialog(self, parent):
        result = CReportAnalizeBillOnDirectionsSetupDialog(parent)
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
            ('15%', [u'№ Направления'],                 CReportBase.AlignLeft),
            ('15%', [u'Врач'],                          CReportBase.AlignLeft),
            ('50%', [u'Услуги'],                        CReportBase.AlignLeft),
            ('5%',  [u'Количество'],                    CReportBase.AlignLeft),
            ('5%',  [u'Стоимость'],                     CReportBase.AlignLeft),
            ('5%',  [u'Сумма'],                         CReportBase.AlignLeft),
            ('5%',  [u'Сумма зарплат исполнителей'],    CReportBase.AlignLeft),
        ]

        table = createTable(cursor, tableColumns)

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        total = 0
        postPriceTotal = 0
        currentDate = QtCore.QDate.currentDate()
        currentEventId = None
        currentAccountId = None
        first = True
        count = 0
        eventRow = 0
        row = 0
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            accountId = forceRef(record.value('accountId'))
            if currentEventId != eventId or currentAccountId != accountId:
                count += 1
                if not first:
                    for service in serviceList:
                        row = table.addRow()
                        fields = (
                            {'name': u'', 'align': CReportBase.AlignLeft},
                            {'name': u'', 'align': CReportBase.AlignLeft},
                            {'name': service[0], 'align': CReportBase.AlignLeft},
                            {'name': service[1], 'align': CReportBase.AlignLeft},
                            {'name': service[2], 'align': CReportBase.AlignLeft},
                            {'name': service[3], 'align': CReportBase.AlignLeft},
                            {'name': service[4], 'align': CReportBase.AlignLeft},
                        )
                        for col, val in enumerate(fields):
                            table.setText(row, col, val['name'], CReportBase.TableBody, val['align'])
                    table.mergeCells(eventRow, 0, serviceCount, 1)
                    table.mergeCells(eventRow, 1, serviceCount, 1)
                    table.setText(eventRow, 0, code, CReportBase.TableBody, CReportBase.AlignLeft)
                    table.setText(eventRow, 1, personName, CReportBase.TableBody, CReportBase.AlignLeft)
                first = False
                externalId = forceString(record.value('externalId'))

                code = u'%s/(%d)/%d/%d' %(externalId, count, currentDate.year()%100, accountId)
                personName = forceString(record.value('personName'))
                serviceName = forceString(record.value('serviceName'))
                amount = forceDouble(record.value('amount'))
                price = forceDouble(record.value('price'))
                sum = forceDouble(record.value('sum'))
                postPriceSum = forceDouble(record.value('postPriceSum'))
                serviceList = [(serviceName, u'%.2f'%amount, u'%.2f'%price, u'%.2f'%sum, u'%.2f'%postPriceSum)]
                currentEventId = eventId
                currentAccountId = accountId
                serviceCount = 1
                eventRow = row + 1
            else:
                serviceList.append((serviceName, u'%.2f'%amount, u'%.2f'%price, u'%.2f'%sum, u'%.2f'%postPriceSum))
                serviceCount += 1
            total += sum
            postPriceTotal += postPriceSum

        if not first:
            if not first:
                for service in serviceList:
                    row = table.addRow()
                    fields = (
                        {'name': u'', 'align': CReportBase.AlignLeft},
                        {'name': u'', 'align': CReportBase.AlignLeft},
                        {'name': service[0], 'align': CReportBase.AlignLeft},
                        {'name': service[1], 'align': CReportBase.AlignLeft},
                        {'name': service[2], 'align': CReportBase.AlignLeft},
                        {'name': service[3], 'align': CReportBase.AlignLeft},
                        {'name': service[4], 'align': CReportBase.AlignLeft},
                    )
                    for col, val in enumerate(fields):
                        table.setText(row, col, val['name'], CReportBase.TableBody, val['align'])
                table.mergeCells(eventRow, 0, serviceCount, 1)
                table.mergeCells(eventRow, 1, serviceCount, 1)
                table.setText(eventRow, 0, code, CReportBase.TableBody, CReportBase.AlignLeft)
                table.setText(eventRow, 1, personName, CReportBase.TableBody, CReportBase.AlignLeft)

            row = table.addRow()
            table.mergeCells(row, 0, 1, 3)
            table.mergeCells(row, 3, 1, 3)
            table.setText(row, 2, u'Всего', CReportBase.TableTotal, CReportBase.AlignRight)
            table.setText(row, 5, u'%.2f'%total, CReportBase.TableTotal, CReportBase.AlignLeft)
            table.setText(row, 6, u'%.2f'%postPriceTotal, CReportBase.TableTotal, CReportBase.AlignLeft)
        return doc

