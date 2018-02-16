# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.database   import addDateInRange
from library.Utils      import forceDate, forceRef, forceString
from Registry.Utils     import getClientBanner

from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(begDate, endDate, personId, orgStructureId, specialityId, clientIdType):
    stmt="""
SELECT
    Action.endDate, Action.event_id, Action.actionType_id,
   (SELECT Diagnosis.MKB
    FROM Diagnostic
    INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
    INNER JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
    WHERE Action.event_id IS NOT NULL AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0 AND Diagnostic.event_id = Action.event_id AND (rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Action.event_id LIMIT 1))))
    LIMIT 1) AS MKB,
    Event.client_id, ActionType.code AS actionTypeCode, ActionType.name AS actionTypeName, EventType.code AS eventTypeCode, EventType.name AS eventTypeName%s

FROM Action
INNER JOIN Event ON Event.id = Action.event_id
INNER JOIN EventType ON EventType.id = Event.eventType_id
INNER JOIN ActionType ON ActionType.id = Action.actionType_id
%s

WHERE Action.deleted = 0 AND Event.deleted = 0 AND EventType.deleted = 0 AND ActionType.deleted = 0 %s

GROUP BY Action.id
ORDER BY Action.event_id, Action.endDate
    """
    db = QtGui.qApp.db
    tableAction  = db.table('Action')
    tableEvent  = db.table('Event')
    tablePerson = db.table('Person')
    tableOrgStructure = db.table('OrgStructure')
    cond = []
    addDateInRange(cond, tableAction['endDate'], begDate, endDate)
    if personId:
        cond.append(tableAction['setPerson_id'].eq(personId))
    if orgStructureId or specialityId:
        stmtFrom = u'''INNER JOIN Person ON Person.id = Action.person_id'''
        cond.append(tablePerson['deleted'].eq(0))
    else:
        stmtFrom = u''''''
    if orgStructureId:
        orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
        if orgStructureIdList:
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))

    if clientIdType:
        stmtCols = u''',
   (SELECT CONCAT(rbAccountingSystem.code, ' - ', rbAccountingSystem.name, ': ', ClientIdentification.identifier)
    FROM ClientIdentification
    INNER JOIN rbAccountingSystem ON rbAccountingSystem.id = ClientIdentification.accountingSystem_id
    WHERE Event.client_id IS NOT NULL AND ClientIdentification.client_id = Event.client_id AND (ClientIdentification.id IS NULL OR ClientIdentification.deleted = 0)
    LIMIT 1) AS identifier'''
    else:
        stmtCols = u''
    return db.query(stmt % (stmtCols, stmtFrom, u'AND ' + db.joinAnd(cond)))


class CReportOnPerson(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка на врача', u'Сводка на врача')


    def getSetupDialog(self, parent):
        result = CReportOnPersonSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        clientIdType = params.get('clientIdType', 0)

        query = selectData(begDate, endDate, personId, orgStructureId, specialityId, clientIdType)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
            ('10%',  [u'Дата'],          CReportBase.AlignLeft),
            ( '5%',  [u'№'],             CReportBase.AlignRight),
            ( '50%', [u'Пациент'],       CReportBase.AlignLeft),
            ( '10%', [u'Тип обращения'], CReportBase.AlignLeft),
            ( '10%', [u'Услуга'       ], CReportBase.AlignLeft),
            ( '5%',  [u'Закл. диагноз'], CReportBase.AlignLeft),
            ( '10%',  [u'Идентификатор во внешней учётной системе' if clientIdType else u'Идентификатор клиента'], CReportBase.AlignLeft)
            ]
        table = createTable(cursor, tableColumns)
        cnt = 0
        total = 0
        while query.next() :
            record = query.record()
            endDate = forceDate(record.value('endDate'))
            clientId = forceRef(record.value('client_id'))
            eventTypeName = forceString(record.value('eventTypeName'))
            actionTypeCode = forceString(record.value('actionTypeCode'))
            actionTypeName = forceString(record.value('actionTypeName'))
            MKB = forceString(record.value('MKB'))
            if clientIdType:
                identifier = forceString(record.value('identifier'))
            else:
                identifier = forceString(clientId)
            cnt += 1
            i = table.addRow()
            table.setText(i, 0, forceString(endDate))
            table.setText(i, 1, cnt)
            table.setHtml(i, 2, getClientBanner(clientId, endDate))
            table.setText(i, 3, eventTypeName)
            table.setText(i, 4, actionTypeCode + u' - ' + actionTypeName)
            table.setText(i, 5, MKB)
            table.setText(i, 6, identifier)
        total += cnt
        i = table.addRow()
        table.setText(i, 0, u'ВСЕГО', CReportBase.TableTotal)
        table.setText(i, 1, total, CReportBase.TableTotal)
        return doc


from Ui_ReportOnPersonSetupDialog import Ui_ReportOnPersonSetupDialog


class CReportOnPersonSetupDialog(QtGui.QDialog, Ui_ReportOnPersonSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbIdentifierType.setCurrentIndex(0)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbIdentifierType.setCurrentIndex(params.get('clientIdType', 0))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['clientIdType'] = self.cmbIdentifierType.currentIndex()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)

