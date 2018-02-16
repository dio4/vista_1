# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportVisitsByClientTypeSetup import Ui_ReportVisitsByClientTypeSetupDialog
from library.Utils import forceInt, forceString, forceDate
from library.database import addDateInRange


def selectData(params):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypeId = params.get('eventTypeId', None)
    isPrimary = params.get('isPrimary', 0)
    orgStructureId = params.get('orgStructureId', None)
    MKBFilter = params.get('MKBFilter', False)
    MKBFrom = params.get('MKBFrom', 'A00')
    MKBTo = params.get('MKBTo', 'Z99.9')
    citizen = params.get('citizen', 0)

    db = QtGui.qApp.db
    tableAddress = db.table('Address')
    tableAddressHouse = db.table('AddressHouse')
    tableClient = db.table('Client')
    tableClientAddress = db.table('ClientAddress')
    tableClientDocument = db.table('ClientDocument')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableDiagnostic = db.table('Diagnostic')
    tableDocumentType = db.table('rbDocumentType')
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableVisit = db.table('Visit')

    cols = [
        u'''concat_ws(' ', Client.lastName, Client.firstName, Client.patrName) as clientFIO,
        Client.id as clientId,
        GROUP_CONCAT(DISTINCT Event.setDate ORDER BY Event.setDate) AS eventSetDates'''
    ]

    cond = [
        tableEvent['setDate'].ge(begDate),
        tableEvent['setDate'].le(endDate),
        tableClient['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
    ]
    addDateInRange(cond, tableVisit['date'], begDate, endDate)

    queryTable = tableVisit.leftJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))

    if MKBFilter:
        queryTable = queryTable.leftJoin(tableDiagnostic, [tableDiagnostic['event_id'].eq(tableEvent['id']),
                                                           tableDiagnostic['deleted'].eq(0)])
        queryTable = queryTable.leftJoin(tableDiagnosisType, [tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
                                                              tableDiagnosisType['code'].inlist(['1', '2'])]) # заключительный, основной
        queryTable = queryTable.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))

        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))

    if isPrimary != 0:
        cond.append(db.joinOr([tableVisit['isPrimary'].eq(isPrimary), tableEvent['isPrimary'].eq(isPrimary)]))

    if orgStructureId:
        queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if citizen != 0:
        queryTable = queryTable.leftJoin(tableClientDocument, tableClientDocument['client_id'].eq(tableClient['id']))
        queryTable = queryTable.leftJoin(tableDocumentType, tableDocumentType['id'].eq(tableClientDocument['documentType_id']))

        if citizen == 4: # иностранный житель
            cond.append(tableDocumentType['isForeigner'].eq(1))
        else:
            cond.append(tableDocumentType['isForeigner'].eq(0))

            queryTable = queryTable.leftJoin(tableClientAddress, 'ClientAddress.id = getClientRegAddressId(Event.client_id)')
            queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['id']))
            queryTable = queryTable.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))

            cond.append(tableClientAddress['deleted'].eq(0))
            cond.append(tableAddress['deleted'].eq(0))
            cond.append(tableAddressHouse['deleted'].eq(0))

            if citizen == 1:  # житель СПб
                cond.append('LEFT(AddressHouse.KLADRCode, 2) = 78')
            elif citizen == 2:  # житель ЛенОбласти
                cond.append('LEFT(AddressHouse.KLADRCode, 2) = 47')
            elif citizen == 3:  # иногородний
                cond.append('LEFT(AddressHouse.KLADRCode, 2) NOT IN (78, 47)')
            elif citizen == 5:  # сельский житель
                cond.append('isClientVillager(Client.id) = 1')

    group = tableClient['id'].name()
    order = ['clientFIO']

    stmt = db.selectStmt(queryTable, cols, cond, group=group, order=order)
    return db.query(stmt)


class CReportVisitsByClientTypeSetupDialog(QtGui.QDialog, Ui_ReportVisitsByClientTypeSetupDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.calendarWidget().setFirstDayOfWeek(QtCore.Qt.Monday)
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbIsPrimary.setCurrentIndex(0)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbMKBFrom.setText('')
        self.cmbMKBTo.setText('')
        self.cmbCitizen.setCurrentIndex(0)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbIsPrimary.setCurrentIndex(params.get('isPrimary', 0))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chbMKBFilter.setChecked(params.get('MKBFilter', False))
        self.cmbMKBFrom.setText(params.get('MKBFrom', ''))
        self.cmbMKBTo.setText(params.get('MKBTo', ''))
        self.cmbCitizen.setCurrentIndex(params.get('citizen', 0))

    def params(self):
        params = {}
        params['begDate'] = self.edtBegDate.date()
        params['endDate'] = self.edtEndDate.date()
        params['eventTypeId'] = self.cmbEventType.value()
        params['isPrimary'] = self.cmbIsPrimary.currentIndex()
        params['orgStructureId'] = self.cmbOrgStructure.value()
        params['MKBFilter'] = self.chbMKBFilter.isChecked()
        params['MKBFrom'] = self.cmbMKBFrom.text()
        params['MKBTo'] = self.cmbMKBTo.text()
        params['citizen'] = self.cmbCitizen.currentIndex()
        return params


class CReportVisitsByClientType(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Посещаемость по типу пациента')

    def getSetupDialog(self, parent):
        result = CReportVisitsByClientTypeSetupDialog(parent)
        result.setTitle(self.title())
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
        tableColumns = [
            ('%5', [u'№ п/п'], CReportBase.AlignLeft),
            ('%50', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('%5' , [u'Код пациента'], CReportBase.AlignLeft),
            ('%20', [u'Дата начала обращения'], CReportBase.AlignLeft)
        ]
        table = createTable(cursor, tableColumns)

        clientNumber = 1
        while query.next():
            record = query.record()
            clientFIO = forceString(record.value('clientFIO'))
            clientId = forceInt(record.value('clientId'))
            eventSetDates = QtCore.QStringList([forceDate(QtCore.QVariant(s)).toString('dd.MM.yyyy')
                                                for s in str(record.value('eventSetDates').toString()).split(',')]).join(', ')
            i = table.addRow()
            table.setText(i, 0, clientNumber)
            table.setText(i, 1, clientFIO)
            table.setText(i, 2, clientId)
            table.setText(i, 3, eventSetDates)

            clientNumber += 1

        return doc
