# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Action      import CActionTypeCache
from library.crbcombobox import CRBComboBox
from library.database   import addDateInRange
from library.Utils      import forceBool, forceDate, forceInt, forceString, calcAge, formatName
from Orgs.Utils         import getOrgStructureDescendants
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(params):
    
    begDate   = params.get('begDate', QtCore.QDate())
    endDate   = params.get('endDate', QtCore.QDate())
    busyness  = params.get('busyness', 0)
    MKBFilter = params.get('MKBFilter', 0)
    MKBFrom   = params.get('MKBFrom', 'A00')
    MKBTo     = params.get('MKBTo', 'Z99.9')
    attachmentOrgStructureId = params.get('attachmentOrgStructureId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)

    place = params.get('deathPlace', '')
    cause = params.get('deathCause', '')
    foundBy = params.get('deathFoundBy', '')
    foundation = params.get('deathFoundation', '')
    
    stmt="""
SELECT
  Client.lastName,
  Client.firstName,
  Client.patrName,
  Client.birthDate,
  Client.sex,
  formatClientAddress(ClientAddress.id) AS address,
  IF(ClientWork.org_id IS NULL, ClientWork.freeInput, Organisation.shortName) AS workName,
  ClientWork.post AS workPost,
  Event.setDate AS date,
  Event.externalId AS number,
  (Event.isPrimary = 1) AS autopsy,
  PDiagnosis.MKB AS PMKB,
  PDiagnosis.MKBEx AS PMKBEx,
  FDiagnosis.MKB AS FMKB,
  FDiagnosis.MKBEx AS FMKBEx,
  rbResult.name AS result
FROM
  Event
  LEFT JOIN EventType ON EventType.id = Event.eventType_id
  LEFT JOIN Client ON Client.id = Event.client_id
  LEFT JOIN ClientAddress ON ClientAddress.client_id = Client.id
                             AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=0 AND CA.client_id = Client.id)
  LEFT JOIN ClientWork ON ClientWork.client_id = Client.id
                             AND ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE ClientWork.deleted=0 AND CW.client_id = Client.id)
  LEFT JOIN Organisation ON Organisation.id = ClientWork.org_id
  LEFT JOIN Diagnostic AS PDiagnostic ON PDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS PDiagnosisType ON PDiagnosisType.id = PDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS PDiagnosis ON PDiagnosis.id = PDiagnostic.diagnosis_id
  LEFT JOIN Diagnostic AS FDiagnostic ON FDiagnostic.event_id = Event.id
  LEFT JOIN rbDiagnosisType AS FDiagnosisType ON FDiagnosisType.id = FDiagnostic.diagnosisType_id
  LEFT JOIN Diagnosis  AS FDiagnosis ON FDiagnosis.id = FDiagnostic.diagnosis_id
  LEFT JOIN rbResult ON rbResult.id = Event.result_id
  LEFT JOIN Person ON Person.id = Event.execPerson_id

WHERE
  EventType.code = '15'
  AND PDiagnosisType.code = '8'
  AND FDiagnosisType.code = '4'
  AND %s
ORDER BY Client.lastName, Client.firstName, Client.patrName, Client.sex, Event.setDate, Event.id
    """
    db = QtGui.qApp.db
    tableEvent     = db.table('Event')
    tableWork      = db.table('ClientWork')
    tableDiagnosis = db.table('Diagnosis').alias('FDiagnosis')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    addDateInRange(cond, tableEvent['setDate'], begDate, endDate)
    if busyness == 1:
        cond.append(tableWork['id'].isNotNull())
    elif busyness == 2:
        cond.append(tableWork['id'].isNull())
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if place or cause or foundBy or foundation:
        addCondForDeathCurcumstance(cond, tableEvent, place, cause, foundBy, foundation)
    if attachmentOrgStructureId:
        tableClientAttach = db.table('ClientAttach')
        tableClient = db.table('Client')
        cond.append(db.existsStmt(tableClientAttach, [tableClientAttach['orgStructure_id'].inlist(getOrgStructureDescendants(attachmentOrgStructureId)),
                                                      tableClientAttach['client_id'].eq(tableClient['id']),
                                                      tableClientAttach['begDate'].le(tableEvent['setDate']),
                                                      db.joinOr([tableClientAttach['endDate'].isNull(),
                                                                 tableClientAttach['endDate'].ge(tableEvent['setDate'])])
                                                      ]))
    if socStatusTypeId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusType_id=%d' % socStatusTypeId)
        cond.append('EXISTS('+subStmt+')')
    elif socStatusClassId:
        subStmt = ('SELECT ClientSocStatus.id FROM ClientSocStatus WHERE '
                  +'ClientSocStatus.deleted=0 AND ClientSocStatus.client_id=Client.id AND '
                  +'ClientSocStatus.socStatusClass_id=%d' % socStatusClassId)
        cond.append('EXISTS('+subStmt+')')
    return db.query(stmt % (db.joinAnd(cond)))


def addCondForDeathCurcumstance(cond, tableEvent, place, cause, foundBy, foundation):
    db = QtGui.qApp.db
    try:
        actionType = CActionTypeCache.getByFlatCode('deathCurcumstance')
    except:
        actionType = None
    tableAction = db.table('Action')
    table = tableAction
    condActionProperties = []
    table, condActionProperties = addCondActionProperties(tableAction, table, condActionProperties, actionType, u'Смерть последовала', place)
    table, condActionProperties = addCondActionProperties(tableAction, table, condActionProperties, actionType, u'Смерть произошла', cause)
    table, condActionProperties = addCondActionProperties(tableAction, table, condActionProperties, actionType, u'Причина установлена', foundBy)
    table, condActionProperties = addCondActionProperties(tableAction, table, condActionProperties, actionType, u'Основание', foundation)
    if condActionProperties:
        condActionProperties.append(tableAction['event_id'].eq(tableEvent['id']))
        cond.append(db.existsStmt(table, condActionProperties))


def addCondActionProperties(tableAction, table, cond, actionType, propertyName, value):
    db = QtGui.qApp.db
    actionPropertyType = actionType.getPropertyType(propertyName) if actionType and actionType.containsPropertyWithName(propertyName) else None
    if actionPropertyType and value:
        n = len(cond)
        tableActionProperty = db.table('ActionProperty').alias('AP_%d'%n)
        tableActionPropertyValue = db.table(actionPropertyType.getValueTableName()).alias('APV_%d'%n)
        cond.append(tableActionPropertyValue['value'].eq(value))
        table = table.join(tableActionProperty, [tableActionProperty['action_id'].eq(tableAction['id']),
                                                 tableActionProperty['type_id'].eq(actionPropertyType.id)
                                                ])
        table = table.join(tableActionPropertyValue, tableActionPropertyValue['id'].eq(tableActionProperty['id']))
    return table, cond



class CDeathList(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Журнал регистрации умерших')


    def getSetupDialog(self, parent):
        result = CDeathReportSetupDialog(parent)
        result.setBusynessEnabled(True)
        result.setMKBFilterEnabled(True)
        result.setTitle(self.title())
        return result


    def build(self, params):

        tableColumns = [
            ('5%', [u'№'],       CReportBase.AlignRight),
            ('5%', [u'№ спр.'],  CReportBase.AlignRight),
            ('25%',[u'ФИО'],     CReportBase.AlignLeft),
            ('25%',[u'Адрес,\nЗанятость'],      CReportBase.AlignLeft),
            ('10%',[u'дата смерти и\nвозраст'], CReportBase.AlignLeft),
            ('15%',[u'предварительный\nи заключительный\nдиагноз'], CReportBase.AlignLeft),
            ('15%',[u'вскрытие,\nрезультат'],  CReportBase.AlignLeft),
            ]

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        table = createTable(cursor, tableColumns)

        n = 0
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            n += 1
            i = table.addRow()
            record   = query.record()

            autopsy  = forceBool(record.value('autopsy'))
            table.setText(i, 0, n)
            table.setText(i, 1, forceString(record.value('number')))
            table.setText(i, 2, formatName(record.value('lastName'),
                                           record.value('firstName'),
                                           record.value('patrName')))
            work = ', '.join(filter(None, [forceString(record.value('workName')), forceString(record.value('workPost'))]))
            table.setText(i, 3, forceString(record.value('address'))+'\n'+work)
            birthDate = forceDate(record.value('birthDate'))
            date  = forceDate(record.value('date'))
            age   = calcAge(birthDate, date)
            table.setText(i, 4, u'%s\n%s' % (forceString(date), age))
            table.setText(i, 5, u'%s\n%s' % (forceString(record.value('PMKB')),
                                             forceString(record.value('FMKB'))))
            table.setText(i, 6, u'%s\n%s' % (u'проводилось' if autopsy else u'не проводилось',
                                             forceString(record.value('result'))))
        return doc


from Ui_DeathReportSetup import Ui_DeathReportSetupDialog


class CDeathReportSetupDialog(QtGui.QDialog, Ui_DeathReportSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setBusynessEnabled(False)
        self.setMKBFilterEnabled(False)
        try:
            actionType = CActionTypeCache.getByFlatCode('deathCurcumstance')
        except:
            actionType = None
        self.preparePropertyComboBox(self.cmbPlace, actionType, u'Смерть последовала')
        self.preparePropertyComboBox(self.cmbCause, actionType, u'Смерть произошла')
        self.preparePropertyComboBox(self.cmbFoundBy,    actionType, u'Причина установлена')
        self.preparePropertyComboBox(self.cmbFoundation, actionType, u'Основание')
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)


    def setBusynessEnabled(self, mode=True):
        for widget in [self.lblBusyness, self.cmbBusyness]:
            widget.setVisible(mode)
        self.busynessEnabled = mode


    def setMKBFilterEnabled(self, mode=True):
        for widget in [self.lblMKB, self.frmMKB]:
            widget.setVisible(mode)
        self.MKBFilterEnabled = mode


    def preparePropertyComboBox(self, comboBox, actionType, propertyName):
        actionPropertyType = actionType.getPropertyType(propertyName) if actionType and actionType.containsPropertyWithName(propertyName) else None
        if actionPropertyType:
            comboBox.setDomain('\'\','+actionPropertyType.valueDomain)
            comboBox.setEnabled(True)
        else:
            comboBox.setEnabled(False)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        if self.busynessEnabled:
            self.cmbBusyness.setCurrentIndex(forceInt(params.get('busyness', 0)))
        if self.MKBFilterEnabled:
            MKBFilter = params.get('MKBFilter', 0)
            self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
            self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
            self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))

        self.cmbPlace.setValue(params.get('deathPlace', ''))
        self.cmbCause.setValue(params.get('deathCause', ''))
        self.cmbFoundBy.setValue(params.get('deathFoundBy', ''))
        self.cmbFoundation.setValue(params.get('deathFoundation', ''))
        self.cmbAttachmentOrgStructureId.setValue(params.get('attachmentOrgStructureId', None))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        if self.busynessEnabled:
            result['busyness'] = self.cmbBusyness.currentIndex()
        if self.MKBFilterEnabled:
            result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
            result['MKBFrom']   = forceString(self.edtMKBFrom.text())
            result['MKBTo']     = forceString(self.edtMKBTo.text())
        result['deathPlace']      = self.cmbPlace.value()
        result['deathCause']      = self.cmbCause.value()
        result['deathFoundBy']    = self.cmbFoundBy.value()
        result['deathFoundation'] = self.cmbFoundation.value()
        result['attachmentOrgStructureId'] = self.cmbAttachmentOrgStructureId.value()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)
    
    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)