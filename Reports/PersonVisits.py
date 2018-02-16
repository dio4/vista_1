# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.database   import addDateInRange
from library.Utils      import forceDate, forceRef, forceString, getVal
from Orgs.Orgs          import selectOrganisation
from Orgs.Utils         import getOrgStructureDescendants
from Registry.Utils     import getClientBanner
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(begDate, endDate, orgStructureId, personId, eventPurposeId, eventTypeId, sceneId, workOrgId, sex, ageFrom, ageTo):
    stmt="""
SELECT
    Visit.id AS visit_id,
    Visit.date AS date,
    Event.client_id AS client_id,
    EventType.name AS eventType,
    rbScene.name AS scene,
    Diagnosis.MKB AS MKB,
    rbDispanser.name AS dispanser
FROM Visit
LEFT JOIN Event     ON Event.id = Visit.event_id
LEFT JOIN EventType ON EventType.id = Event.eventType_id
LEFT JOIN Person    ON Person.id = Visit.person_id
LEFT JOIN Client    ON Client.id = Event.client_id
LEFT JOIN rbScene   ON rbScene.id = Visit.scene_id
LEFT JOIN Diagnostic d1   ON d1.event_id = Visit.event_id AND d1.person_id = Visit.person_id
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = d1.diagnosisType_id
LEFT JOIN Diagnosis       ON Diagnosis.id = d1.diagnosis_id
LEFT JOIN rbDispanser     ON rbDispanser.id = d1.dispanser_id
LEFT JOIN Diagnostic d2   ON d1.event_id = d2.event_id AND d2.person_id = Visit.person_id
	                        AND (d1.diagnosisType_id > d2.diagnosisType_id
	                        OR (d1.diagnosisType_id = d2.diagnosisType_id AND d1.id < d2.id))
WHERE d2.event_id IS NULL
AND Visit.deleted = 0
AND Event.deleted = 0
AND %s
ORDER BY Visit.date, Client.lastName, Client.firstName, Client.patrName, Client.birthDate, Client.sex
    """
    db = QtGui.qApp.db
    tableVisit  = db.table('Visit')
    tableEvent  = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    cond = []

    addDateInRange(cond, tableVisit['date'], begDate, endDate)
    if personId:
        cond.append(tableVisit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if sceneId:
        cond.append(tableVisit['scene_id'].eq(sceneId))
    if workOrgId:
        cond.append('EXISTS (SELECT * FROM ClientWork WHERE ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id) and ClientWork.org_id=%d)' % (workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    return db.query(stmt % (db.joinAnd(cond)))


class CPersonVisits(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка на врача', u'Сводка на врача')


    def getSetupDialog(self, parent):
        result = CPersonVisitsSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        sceneId = params.get('sceneId', None)
        workOrgId = params.get('workOrgId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)

        db = QtGui.qApp.db
        query = selectData(begDate, endDate, orgStructureId, personId, eventPurposeId, eventTypeId, sceneId, workOrgId, sex, ageFrom, ageTo)

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
            ( '45%', [u'Пациент'],       CReportBase.AlignLeft),
            ( '10%', [u'Тип обращения'], CReportBase.AlignLeft),
            ( '10%', [u'Место'       ],  CReportBase.AlignLeft),
            ( '5%',  [u'Закл. диагноз'], CReportBase.AlignLeft),
            ( '5%',  [u'ДН'],            CReportBase.AlignLeft),
            ]
        table = createTable(cursor, tableColumns)

        prevVisitId = None
        prevDate = None
        cnt = 0
        total = 0
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record    = query.record()
            visitId   = forceRef(record.value('visit_id'))
            date      = forceDate(record.value('date'))
            clientId  = forceRef(record.value('client_id'))
            eventType = forceString(record.value('eventType'))
            scene     = forceString(record.value('scene'))
            MKB       = forceString(record.value('MKB'))
            dispanser = forceString(record.value('dispanser'))

            if date != prevDate:
                self.produceTotalLine(table, prevDate, cnt)
                prevDate = date
                total += cnt
                cnt = 0
                prevVisitId = None

            if prevVisitId != visitId:
                cnt += 1
                i = table.addRow()
                table.setText(i, 0, forceString(date))
                table.setText(i, 1, cnt)
                table.setHtml(i, 2, getClientBanner(clientId, date))
                table.setText(i, 3, eventType)
                table.setText(i, 4, scene)
                table.setText(i, 5, MKB)
                table.setText(i, 6, dispanser)
            else:
                i = table.addRow()
                for j in xrange(7):
                    if j != 5:
                        table.mergeCells(i-1, j, 2, 1)
                table.setText(i, 5, MKB)
        self.produceTotalLine(table, prevDate, cnt)
        total += cnt
        i = table.addRow()
        table.setText(i, 0, u'ВСЕГО', CReportBase.TableTotal)
        table.setText(i, 1, total, CReportBase.TableTotal)
        return doc


    def produceTotalLine(self, table, date, cnt):
        if cnt != 0:
            i = table.addRow()
            table.setText(i, 0, u'всего за '+forceString(date), CReportBase.TableTotal)
            table.setText(i, 1, cnt, CReportBase.TableTotal)


from Ui_PersonVisitsSetup import Ui_PersonVisitsSetupDialog


class CPersonVisitsSetupDialog(QtGui.QDialog, Ui_PersonVisitsSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbScene.setTable('rbScene', True)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbScene.setValue(params.get('sceneId', None))
        self.cmbWorkOrganisation.setValue(params.get('workOrgId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['sceneId'] = self.cmbScene.value()
        result['workOrgId'] = self.cmbWorkOrganisation.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)
