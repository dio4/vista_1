# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.Utils import forceInt, forceString
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportBedspacePEOForm5Setup import Ui_ReportBedspacePEOForm5Setup

def selectData(params):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    typeFinanceId       = params.get('typeFinanceId', None)

    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyType = db.table('ActionPropertyType')

    tableActionPropertyReceived = tableActionProperty.alias('apReceived')
    tableActionPropertyTypeReceived = tableActionPropertyType.alias('aptReceived')
    tableActionPropertyOrgStructure = db.table('ActionProperty_OrgStructure')
    tableOrgStructure = db.table('OrgStructure')

    tableActionPropertyRefuse = tableActionProperty.alias('apRefuse')
    tableActionPropertyTypeRefuse = tableActionPropertyType.alias('aptRefuse')
    tableActionPropertyString = db.table('ActionProperty_String')

    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableClient = db.table('Client')
    tableClientDocument = db.table('ClientDocument')
    tableClientPolicy = db.table('ClientPolicy')
    tableDocumentType = db.table('rbDocumentType')



    cols = [u'Count(%s) as quantity' %tableEvent['id']]
    queryTable = tableEvent
    queryTable = queryTable.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
    queryTable = queryTable.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))

    queryTable = queryTable.innerJoin(tableActionPropertyReceived, tableActionPropertyReceived['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableActionPropertyTypeReceived, tableActionPropertyTypeReceived['id'].eq(tableActionPropertyReceived['type_id']))
    queryTable = queryTable.innerJoin(tableActionPropertyOrgStructure, tableActionPropertyOrgStructure['id'].eq(tableActionPropertyReceived['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableActionPropertyOrgStructure['value']))

    queryTable = queryTable.innerJoin(tableActionPropertyRefuse, tableActionPropertyRefuse['action_id'].eq(tableAction['id']))
    queryTable = queryTable.innerJoin(tableActionPropertyTypeRefuse, tableActionPropertyTypeRefuse['id'].eq(tableActionPropertyRefuse['type_id']))
    queryTable = queryTable.innerJoin(tableActionPropertyString, tableActionPropertyString['id'].eq(tableActionPropertyRefuse['id']))

    cond = [tableOrgStructure['name'].eq(u"'Приемное отделение'"),
            tableAction['deleted'].eq(0),
            tableEvent['deleted'].eq(0),
            tableActionType['flatCode'].eq(u"'received'"),
            tableActionPropertyTypeReceived['name'].eq(u"'Направлен в отделение'"),
            u"Locate('причина отказа', %s)" %tableActionPropertyTypeRefuse['name']]
    if typeFinanceId > 0:
        queryTable = queryTable.innerJoin(tableContract, tableContract['id'].eq(tableAction['contract_id']))
        cond.append(tableContract['finance_id'].eq(typeFinanceId))
    elif typeFinanceId == -1:
        queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
        queryTable = queryTable.leftJoin(tableClientDocument, tableClientDocument['client_id'].eq(tableClient['id']))
        queryTable = queryTable.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, u'%s = getClientPolicy(%s, 1)' %(tableClientPolicy['id'], tableClient['id']))
        cond.append(db.joinOr([
                tableDocumentType['id'].isNull(),
                tableDocumentType['code'].eq(21)
            ]))
        cond.append(tableClientPolicy['id'].isNull())
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(tableEvent['execDate'].le(endDate))
    cond.append(tableEvent['org_id'].eq(QtGui.qApp.currentOrgId()))

    stmt = db.selectStmt(queryTable, cols, cond)

    return db.query(stmt)

def getOrgName(orgID):
    db = QtGui.qApp.db
    table = db.table('Organisation')
    return forceString(db.translate(table,'id',orgID, 'shortName'))

class CReportBedspacePEOForm5(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по использованию коченого фонда. Форма 5. Амбулаторные услуги Приёмное отделение')

    def getSetupDialog(self, parent):
        result = CReportBedspacePEOForm5Dialog(parent)
        result.setTitle(u'Отчёт по использованию коченого фонда. Форма 5. Амбулаторные услуги Приёмное отделение')
        return result

    def build(self, params):
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        u'''Отделения
        Проведенео операций (кол-во)
        Прооперировано больных(чел.) - ...
        '''
        tableColumns = [
            ('60%', [u'Наименование услуги'], CReportBase.AlignCenter),
            ('20%', [u'Количество услуг'], CReportBase.AlignCenter),
            ]
        table = createTable(cursor, tableColumns)
        while query.next():
            record = query.record()
            row = table.addRow()
            fields = (
                {'name': u'Посещения', 'format': CReportBase.TableTotal, 'align': CReportBase.AlignLeft},
                {'name': forceInt(record.value('quantity')),'format': CReportBase.TableBody,  'align': CReportBase.AlignRight},
            )

            for col, val in enumerate(fields):
                table.setText(row, col, val['name'], val['format'], val['align'])
        return doc

class CReportBedspacePEOForm5Dialog(QtGui.QDialog, Ui_ReportBedspacePEOForm5Setup):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbFinance.setTable('rbFinance')
        self.cmbFinance.model().d.addItem(-1,'-1', u'Иностранные граждане')
        #self.cmbFinance.addItem('Иностранцы')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        curDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(curDate.year(), curDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(curDate.year(), curDate.month(), curDate.daysInMonth())))
        self.cmbFinance.setValue(params.get('typeFinanceId', 2))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['typeFinanceId'] = self.cmbFinance.value()
        return result