# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils                       import getWorkEventTypeFilter
from library.crbcombobox                import CRBComboBox
from library.PrintInfo                  import CInfoContext
from library.Utils                      import forceDate, forceInt, forceRef, forceString, getVal, pyDate
from Orgs.Utils                         import getOrgStructureDescendants
from Registry.Utils                     import CClientInfo
from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.Ui_ReportPatientsAtHome    import Ui_ReportPatientAtHome


def select(begDate, endDate, orgStructureId, personId, rowGrouping, sex, socStatusClassId, socStatusTypeId, group):

    db = QtGui.qApp.db

    tableVisit  = db.table('Visit')
    tableEvent  = db.table('Event')
    tablePerson = db.table('Person')
    tableClient = db.table('Client')
    tableScene  = db.table('rbScene')
#    tableClientAddress = db.table('ClientAddress')

    queryTable = tableVisit.leftJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
    queryTable = queryTable.leftJoin(tablePerson, tablePerson['id'].eq(tableVisit['person_id']))
    queryTable = queryTable.leftJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    queryTable = queryTable.leftJoin(tableScene, tableScene['id'].eq(tableVisit['scene_id']))
#    queryTable = queryTable.leftJoin(tableClientAddress, tableClient['id'].eq(tableClientAddress['client_id']))

    cond = [tableVisit['date'].dateLe(endDate),
            tableVisit['date'].dateGe(begDate),
            tableVisit['deleted'].eq(0),
            tableEvent['deleted'].eq(0)]

    if rowGrouping == 5: #by client_id
        groupField = 'Event.client_id'
    elif rowGrouping == 4: # by post_id
        groupField = 'Person.post_id'
    elif rowGrouping == 3: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by personId
        groupField = 'Visit.person_id'
    else:
        groupField = 'DATE(Visit.date)'

    cols = [u'''COUNT(*) AS cnt,
                %s AS rowKey ,
                sum(IF(rbScene.code = '2' OR rbScene.code = '3',1,0)) AS atHome %s''' % (groupField, u', Person.orgStructure_id AS orgGroup' if group else '')]


    if personId:
        cond.append(tableVisit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))

    if sex:
        cond.append(tableClient['sex'].eq(sex))

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
    groupTable = u'rowKey'

    order = []

    if group:
        order.append('orgGroup')

    stmt = db.selectStmt(queryTable, cols, cond, groupTable, order)
    query = db.query(stmt)
    return query

class CReportPatientsAtHome(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка по количеству принятых и осмотренных на дому больных (всего и по участкам)')

    def getSetupDialog(self, parent):
        result = CReportPatientAtHome(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        begDate          = params.get('begDate', QtCore.QDate())
        endDate          = params.get('endDate', QtCore.QDate())
        orgStructureId   = params.get('orgStructureId', None)
        personId         = params.get('personId', None)
        rowGrouping      = params.get('rowGrouping', 0)
        sex              = params.get('sex', 0)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId  = params.get('socStatusTypeId', None)
        group            = params.get('group', False)
        address          = params.get('address', False)
        regAddress       = params.get('regAddress', False)
        query = select(begDate, endDate, orgStructureId, personId, rowGrouping, sex, socStatusClassId, socStatusTypeId, group)
        self.setQueryText(forceString(query.lastQuery()))
        if rowGrouping == 5:
            forceKeyVal = forceRef
            keyValToString = lambda clientId: forceString(QtGui.qApp.db.translate('vrbClientInfo', 'id', clientId, 'clientName'))
            keyName = u'Пациент'
        elif rowGrouping == 4: # by post_id
            forceKeyVal = forceRef
            keyValToString = lambda postId: forceString(QtGui.qApp.db.translate('rbPost', 'id', postId, 'name'))
            keyName = u'Должность'
        elif rowGrouping == 3: # by speciality_id
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            keyName = u'Специальность'
        elif rowGrouping == 2: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = lambda orgStructureId: forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
            keyName = u'Подразделение'
        elif rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyName = u'Врач'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'


        forceKey = forceRef
        keyToString = lambda orgStructureId: forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        additional = 0
        tableColumns = [('5%', u'№п/п', CReportBase.AlignLeft),
                        ( '20%', [keyName], CReportBase.AlignLeft)]
        if regAddress:
            tableColumns.append(('10%', [u'Адрес регистрации'], CReportBase.AlignCenter))
            additional += 1
        if address:
            tableColumns.append(('10%', [u'Адрес проживания'], CReportBase.AlignCenter))
            additional += 1
        tableColumns.append(( '10%', [u'Всего'], CReportBase.AlignCenter))
        tableColumns.append(( '10%', [u'Амбулаторно'], CReportBase.AlignCenter))
        tableColumns.append(( '10%', [u'На дому'], CReportBase.AlignCenter))

        table = createTable(cursor, tableColumns)

        total = [0, 0, 0]
        totalOrg = [0]*3
        prevOrgGroup = None
        
        orderNumber = 0
        while query.next():
            record = query.record()
            orderNumber += 1
            rowKey    = forceKeyVal(record.value('rowKey'))
            cnt       = forceInt(record.value('cnt'))
            atHome    = forceInt(record.value('atHome'))
            orgGroup  = keyToString(forceKey(record.value('orgGroup')))
            clientInfo = CClientInfo(CInfoContext(), rowKey)
            regAddr = clientInfo.regAddress
            addr    = clientInfo.locAddress
            if not orgGroup:
                orgGroup = '-'
            if group:
                if prevOrgGroup and prevOrgGroup != orgGroup:
                    i = table.addRow()
                    table.setText(i, 1, u'Всего', CReportBase.TableTotal)
                    for j in xrange(3):
                        table.setText(i, j+2, totalOrg[j], CReportBase.TableTotal)
                        total[j] += totalOrg[j]
                    totalOrg = [0]*3
                if prevOrgGroup != orgGroup:
                    i = table.addRow()
                    table.setText(i, 1, orgGroup, CReportBase.TableTotal)
                    table.mergeCells(i, 0, 1, 4)
                    prevOrgGroup = orgGroup
            i = table.addRow()
            table.setText(i, 0, forceString(orderNumber))
            table.setText(i, 1, keyValToString(rowKey))
            if regAddress:
                table.setText(i, 2, regAddr)
            if address:
                table.setText(i, 1 + additional, addr)
            table.setText(i, 2 + additional, cnt)
            totalOrg[0] += cnt
            table.setText(i, 3 + additional, cnt-atHome)
            totalOrg[1] += cnt - atHome
            table.setText(i, 4 + additional, atHome)
            totalOrg[2] +=  atHome

        if group:
            i = table.addRow()
            table.setText(i, 1, u'Всего', CReportBase.TableTotal)
            for j in xrange(3):
                table.setText(i, j+2 + additional, totalOrg[j], CReportBase.TableTotal)
                total[j] += totalOrg[j]
        else:
            total = totalOrg
        i = table.addRow()
        table.setText(i, 0, u'Итого', CReportBase.TableTotal)
        for j in xrange(3):
            table.setText(i, j+2 + additional, total[j], CReportBase.TableTotal)
        return doc

class CReportPatientAtHome(QtGui.QDialog, Ui_ReportPatientAtHome):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'rowGrouping', 0))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        self.chkGroup.setChecked(params.get('group', False))
        self.chkRegAddress.setChecked(params.get('regAddress', False))
        self.chkAddress.setChecked(params.get('address', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        result['sex'] = self.cmbSex.currentIndex()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['group'] = self.chkGroup.isChecked()
        result['address'] = self.chkAddress.isChecked()
        result['regAddress'] = self.chkRegAddress.isChecked()
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)

    @QtCore.pyqtSlot(bool)
    def on_chkGroup_clicked(self):
        if self.chkGroup.isChecked():
            self.cmbRowGrouping.setCurrentIndex(1)

    @QtCore.pyqtSlot(int)
    def on_cmbRowGrouping_currentIndexChanged(self):
        if self.chkGroup.isChecked():
            self.cmbRowGrouping.setCurrentIndex(1)
        if self.cmbRowGrouping.currentIndex() == 5:
            self.chkAddress.setEnabled(True)
            self.chkRegAddress.setEnabled(True)
        else:
            self.chkAddress.setEnabled(False)
            self.chkRegAddress.setEnabled(False)
            self.chkAddress.setChecked(False)
            self.chkRegAddress.setChecked(False)