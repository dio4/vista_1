# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 - 2014 Vista Software. All rights reserved.
##
#############################################################################

from Reports.Report      import CReport
from Reports.ReportBase  import *
from library.Utils       import *
from Orgs.Utils import getOrgStructureDescendants

def selectDataByCompany(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    byActionEndDate = forceBool(params.get('byActionEndDate'))
    isActionPayed = forceBool(params.get('isActionPayed'))
    whereAction = ''
    whereAccount = ''
    whereIsActionPayed = ''
    if isActionPayed:
        whereIsActionPayed += u'''isActionPayed(Action.id) AND '''
    if byActionEndDate:
        if begDate:
            whereAction += u'''DATE(Action.endDate) >= DATE('%s') AND ''' % begDate.toString('yyyy-MM-dd')
        if endDate:
            whereAction += u'''DATE(Action.endDate) <= DATE('%s') AND ''' % endDate.toString('yyyy-MM-dd')
    else:
        if begDate:
            whereAccount += u'''DATE(Account_Item.date) >= DATE('%s') AND ''' % begDate.toString('yyyy-MM-dd')
        if endDate:
            whereAccount += u'''DATE(Account_Item.date) <= DATE('%s') AND ''' % endDate.toString('yyyy-MM-dd')
    stmt = u'''
    SELECT Organisation.shortName,
      COUNT(DISTINCT Event.id) AS countEvent,
      COUNT(DISTINCT Action.id) AS countAction,
      SUM(Account_Item.sum) AS accountSum
    FROM Event
    INNER JOIN Client ON Event.client_id = Client.id AND Client.deleted = 0
    INNER JOIN ClientPolicy ON Client.id = ClientPolicy.client_id AND ClientPolicy.deleted = 0
    INNER JOIN Organisation ON ClientPolicy.insurer_id = Organisation.id AND Organisation.isInsurer = 1 AND Organisation.deleted = 0
    INNER JOIN Action ON Action.event_id = Event.id AND %s%s Action.deleted = 0
    INNER JOIN Account_Item ON Account_Item.action_id = Action.id AND %s Account_Item.deleted = 0
    WHERE  Event.deleted = 0
    GROUP BY Organisation.shortName
    ''' % (whereAction, whereIsActionPayed, whereAccount)
    return db.query(stmt)


def selectDataByDiagnosis(params):
    db = QtGui.qApp.db
    begDate = forceDate(params.get('begDate'))
    endDate = forceDate(params.get('endDate'))
    eventTypeId = forceInt(params.get('eventTypeId'))
    personId = forceInt(params.get('personId', None))
    orgStruct = forceInt(params.get('orgStructure', None))
    isActionPayed = forceBool(params.get('isActionPayed'))
    where = u''
    whereIsActionPayed = u''
    joins = u''
    if isActionPayed:
        whereIsActionPayed += u'''isActionPayed(Action.id) AND '''
    if begDate:
        where += u''' AND DATE(Event.execDate) >= DATE('%s')''' % begDate.toString('yyyy-MM-dd')
    if endDate:
        where += u''' AND DATE(Event.execDate) < DATE('%s')''' % endDate.toString('yyyy-MM-dd')
    if eventTypeId:
        where += u''' AND Event.eventType_id = %s''' % eventTypeId
    if personId:
        where += u''' AND Event.execPerson_id = %s''' % personId
    if orgStruct:
        joins += u'INNER JOIN Person ON Event.execPerson_id = Person.id AND Person.orgStructure_id in (%s)' % ", ".join(
                [forceString(i) for i in getOrgStructureDescendants(orgStruct)])


    stmt = u'''
    SELECT Diagnosis.MKB,
      COUNT(DISTINCT Event.id) AS countEvent,
      SUM(Account_Item.sum) AS accountSum
    FROM Event
    INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
    INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
    INNER JOIN Action ON Action.event_id = Event.id AND %s Action.deleted = 0
    INNER JOIN Account_Item ON Account_Item.action_id = Action.id AND Account_Item.deleted = 0
    %s
    WHERE  Event.deleted = 0 %s
    GROUP BY Diagnosis.MKB
    ''' % (whereIsActionPayed, joins, where)
    return db.query(stmt)


class CReportAnalysisServicesByCompany(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Анализ услуг по страховым компаниям')

    def getSetupDialog(self, parent):
        result = CReportAnalysisServicesSetupDialog(parent)
        result.visibleByCompany()
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '40%', [u'Страховая компания'], CReportBase.AlignCenter),
            ( '20%', [u'Количество закрытых обращений'], CReportBase.AlignCenter),
            ( '20%', [u'Количество услуг'], CReportBase.AlignCenter),
            ( '20%', [u'Рубли'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        query = selectDataByCompany(params)
        while query.next():
            i = table.addRow()
            record = query.record()
            table.setText(i, 0, forceString(record.value('shortName')))
            table.setText(i, 1, forceString(record.value('countEvent')))
            table.setText(i, 2, forceString(record.value('countAction')))
            table.setText(i, 3, forceString(record.value('accountSum')))

        return doc

class CReportAnalysisServicesByDiagnosis(CReport):
    def __init__(self, parent, suspicions = False):
        CReport.__init__(self, parent)
        self.suspicions = suspicions
        self.setPayPeriodVisible(False)
        self.setTitle(u'Анализ услуг по диагнозам')

    def getSetupDialog(self, parent):
        result = CReportAnalysisServicesSetupDialog(parent)
        result.visibleByDiagnosis()
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        tableColumns = [
            ( '40%', [u'Диагноз'], CReportBase.AlignCenter),
            ( '30%', [u'Всего обращений'], CReportBase.AlignCenter),
            ( '30%', [u'Рубли'], CReportBase.AlignCenter)
        ]

        cursor.insertBlock()

        table = createTable(cursor, tableColumns)

        query = selectDataByDiagnosis(params)
        totalCountEvent = 0
        totalCountAccountSum = 0.0
        while query.next():
            i = table.addRow()
            record = query.record()
            table.setText(i, 0, forceString(record.value('MKB')))
            table.setText(i, 1, forceString(record.value('countEvent')))
            table.setText(i, 2, forceString(record.value('accountSum')))
            totalCountEvent += forceInt(record.value('countEvent'))
            totalCountAccountSum += forceDouble(record.value('accountSum'))

        row = table.addRow()
        table.setText(row, 0, u'Итого', fontBold=True)
        table.setText(row, 1, forceString(totalCountEvent), fontBold=True)
        table.setText(row, 2, forceString(totalCountAccountSum), fontBold=True)
        return doc

from Ui_ReportAnalysisServicesSetup import Ui_ReportAnalysisServicesSetupDialog

class CReportAnalysisServicesSetupDialog(QtGui.QDialog, Ui_ReportAnalysisServicesSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', date))
        self.edtEndDate.setDate(params.get('endDate', date))
        self.rbtnByActionEndDate.setChecked(params.get('byActionEndDate', False))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkIsActionPayed.setChecked(params.get('isActionPayed', True))
        self.cmbOrgStructure.setValue(params.get('orgStructure', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['byActionEndDate'] = self.rbtnByActionEndDate.isChecked()
        result['eventTypeId'] = self.cmbEventType.value()
        result['personId'] = self.cmbPerson.value()
        result['isActionPayed'] = self.chkIsActionPayed.isChecked()
        result['orgStructure'] = self.cmbOrgStructure.value()
        return result

    def visibleByCompany(self):
        self.rbtnByActionEndDate.setVisible(True)
        self.rbtnByFormingAccountDate.setVisible(True)
        self.cmbEventType.setVisible(False)
        self.lblEventType.setVisible(False)
        self.cmbPerson.setVisible(False)
        self.lblPerson.setVisible(False)
        self.cmbOrgStructure.setVisible(False)
        self.lblOrgStructure.setVisible(False)

    def visibleByDiagnosis(self):
        self.rbtnByActionEndDate.setVisible(False)
        self.rbtnByFormingAccountDate.setVisible(False)
        self.cmbEventType.setVisible(True)
        self.lblEventType.setVisible(True)
        self.cmbPerson.setVisible(True)
        self.lblPerson.setVisible(True)
        self.cmbOrgStructure.setVisible(True)
        self.lblOrgStructure.setVisible(True)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)
