# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore, QtGui

from library.Utils                      import forceString


from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase

from Ui_ReportBaseSetup import Ui_ReportBaseSetup

def selectData(params, clientId):
    db = QtGui.qApp.db
    begDate        = params.get('begDate').toString(QtCore.Qt.ISODate)
    endDate        = params.get('endDate').toString(QtCore.Qt.ISODate)

    stmt = u'''SELECT
                     IF(rbService.name IS NULL, EventType.name, rbService.name) AS service,
                     IF(rbService.code IS NULL, '',             rbService.code) AS serviceCode,
                     Account_Item.amount * Account_Item.price AS cost
               FROM
                    Account_Item
                    LEFT JOIN Event         ON  Event.id  = Account_Item.event_id
                    LEFT JOIN EventType     ON  EventType.id = Event.eventType_id
                    LEFT JOIN Visit         ON  Visit.id  = Account_Item.visit_id
                    LEFT JOIN Action        ON  Action.id  = Account_Item.action_id
                    LEFT JOIN ActionType    ON  ActionType.id = Action.actionType_id
                    LEFT JOIN Client        ON  Client.id = Event.client_id
                    LEFT JOIN rbService ON rbService.id = IF(Account_Item.service_id IS NOT NULL,
                                                             Account_Item.service_id,
                                                          IF(Account_Item.visit_id IS NOT NULL,
                                                             Visit.service_id,
                                                             EventType.service_id))
               WHERE ((DATE(Visit.date) >= DATE('%s') AND DATE(Visit.date) <= DATE('%s'))
                    OR (date(Action.endDate) >= date('%s') AND DATE(Action.endDate) <= date('%s'))
                    OR (date(Event.execDate) >= date('%s') AND date(Event.execDate) <= date('%s')))
                    AND Client.id = %s ''' % (begDate, endDate, begDate, endDate, begDate, endDate, clientId)

    return db.query(stmt)

class CReportInformationCost(CReport):
    def __init__(self, parent, clientId):
        CReport.__init__(self, parent)
        self.setTitle(u'Справка о стоимости лечения')
        self.clientId = clientId

    def getSetupDialog(self, parent):
        result = CReportBaseSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate        = params.get('begDate').toString('dd.MM.yyyy')
        endDate        = params.get('endDate').toString('dd.MM.yyyy')
        query = selectData(params, self.clientId)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        format = QtGui.QTextCharFormat()
        cursor = QtGui.QTextCursor(doc)
        cursor.insertBlock(CReportBase.AlignCenter)
        cursor.insertText(u'Справка о стоимости (тарифе) медицинской помощи, оказанной застрахованному лицу в рамках программ обязательного медицинского страхования ', CReportBase.TableTotal)
        format.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(0))
        format.setFontItalic(True)
        cursor.insertBlock()
        cursor.insertText(forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'fullName')), format)
        format.setFontItalic(False)
        format.setFontWeight(QtGui.QFont.StyleNormal)
        cursor.insertBlock()
        cursor.insertText(u'(штамп с наименованием и адресом учреждения выдающего справку)', QtGui.QTextCharFormat())
        cursor.insertBlock(CReportBase.AlignRight)
        cursor.insertBlock()
        cursor.insertText(u'от %s г.' % (QtCore.QDate().currentDate().toString('dd.MM.yyyy')), QtGui.QTextCharFormat())
        cursor.insertBlock(CReportBase.AlignLeft)
        cursor.insertText(u'(Ф.И.О.) %s' %(forceString(QtGui.qApp.db.translate('Client', 'id', self.clientId, '''CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName)'''))), QtGui.QTextCharFormat())
        cursor.insertBlock()
        cursor.insertText(u'в период с %s г. по %s г.' % (begDate, endDate), QtGui.QTextCharFormat())
        cursor.insertBlock()
        cursor.insertText(u'оказаны медицинские услуги:', QtGui.QTextCharFormat())
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('100%',  [u'наименование медицинской услуги'], CReportBase.AlignCenter),
            ('100%',  [u'стоимость(руб.)'                 ], CReportBase.AlignCenter)]
        table = createTable(cursor, tableColumns)
        while query.next():
            record = query.record()
            code = forceString(record.value('serviceCode'))
            name = forceString(record.value('service'))
            cost = forceString(record.value('cost'))
            i = table.addRow()
            table.setText(i, 0, u'(%s) %s' % (code, name), blockFormat=CReportBase.AlignLeft)
            table.setText(i, 1, cost)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText(u'Внимание! Настоящая справка носит уведомительный характер, оплате за счет личных средств не подлежит.', QtGui.QTextCharFormat())
        return doc


class CReportBaseSetup(QtGui.QDialog, Ui_ReportBaseSetup):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        return params