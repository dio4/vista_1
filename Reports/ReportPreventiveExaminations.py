# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceInt, forceString, forceDate
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase
from Orgs.Orgs          import selectOrganisation

from Ui_ReportPreventiveExaminationsSetup import Ui_ReportPreventiveExaminationsSetupDialog

def selectData(params):
    db = QtGui.qApp.db
    begDate      = params.get('begDate', None)
    endDate      = params.get('endDate', None)
    eventTypeId  = params.get('eventTypeId', None)
    clientOrgId = params.get('clientOrgId', None)
    tableEvent      = db.table('Event')
    tableClientWork = db.table('ClientWork')
    cond=[db.joinOr([tableEvent['execDate'].datetimeLe(endDate),tableEvent['execDate'].isNull()]),tableEvent['setDate'].datetimeGe(begDate)]
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if clientOrgId:
        cond.append(tableClientWork['org_id'].eq(clientOrgId))

    stmt = u'''SELECT DISTINCT Client.birthDate, CONCAT(lastName,' ', firstName,' ', patrName) as FIO,
     ClientWork.post, Event.setDate, Event.execDate, Client.sex
        FROM ClientWork INNER JOIN Client ON ClientWork.client_id = Client.id
        INNER JOIN Event ON Event.client_id = Client.id
        WHERE %s''' % (db.joinAnd(cond))
    return db.query(stmt)


class CReportPreventiveExaminations(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Профилактические осмотры')

    def getSetupDialog(self, parent):
        result = CPreventiveExaminationsSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self,params):
        query=selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%2',  [u'№'], CReportBase.AlignRight),
                        ('%30', [u'Фамилия, Имя, Отчество'], CReportBase.AlignLeft),
                        ('%2',  [u'Пол'], CReportBase.AlignLeft),
                        ('%16',  [u'Дата рождения'], CReportBase.AlignLeft),
                        ('%20',  [u'Должность'], CReportBase.AlignLeft),
                        ('%16',  [u'Дата начала осмотра'], CReportBase.AlignLeft),
                        ('%16',  [u'Дата окончания осмотра'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        while query.next():
            record=query.record()
            FIO = forceString(record.value('FIO'))
            sex = u'не указан'
            if forceInt(record.value('sex')) == 1:
                sex=u'М'
            elif forceInt(record.value('sex'))== 2:
                sex=u'Ж'
            birthDate=forceString(record.value('birthDate'))
            post = forceString(record.value('post'))
            begDate = forceString(forceDate(record.value('setDate')))
            endDate = forceString(forceDate(record.value('execDate')))
            i=table.addRow()
            table.setText(i,0,i)
            table.setText(i,1,FIO)
            table.setText(i,2,sex)
            table.setText(i,3,birthDate)
            table.setText(i,4,post)
            table.setText(i,5,begDate)
            table.setText(i,6,endDate)
        return doc


class CPreventiveExaminationsSetup(QtGui.QDialog, Ui_ReportPreventiveExaminationsSetupDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbWorkOrganisation.setValue(params.get('clientOrgId',None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))

    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        params['eventTypeId']   = self.cmbEventType.value()
        params['clientOrgId']  = self.cmbWorkOrganisation.value()
        return params

    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)