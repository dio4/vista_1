# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils           import getWorkEventTypeFilter
from library.Utils          import forceString, forceInt, forceDate
from Orgs.Utils             import getOrgStructureDescendants, getOrgStructureFullName, getOrgStructureName
from Reports.Report         import CReport, getEventTypeName
from Reports.ReportBase     import createTable, CReportBase

from Ui_ReportZNOEstablishedFirst import Ui_ReportZNOEstablishedFirst

def getDistrictName(id):
    db = QtGui.qApp.db
    query = db.query(u"Select name From rbDistrict where id = %s" % forceString(id))
    if not query.next():
        return u''
    return forceString(query.record().value('name'))

def getFinanceTypeName(id):
    db = QtGui.qApp.db
    query = db.query(u"Select name From rbFinance where id = %s" % forceString(id))
    if not query.next():
        return u''
    return forceString(query.record().value('name'))

def selectData(params):
    db = QtGui.qApp.db
    begDate             = params.get('begDate')
    endDate             = params.get('endDate')
    ZNOFirst            = params.get('ZNOFirst')
    ZNOMorph            = params.get('ZNOMorph')
    MKBFrom             = params.get('MKBFrom')
    MKBTo               = params.get('MKBTo')
    ageFrom             = params.get('ageFrom')
    ageTo               = params.get('ageTo')
    sex                 = params.get('sex')
    employment          = params.get('employment')
    eventTypeId         = params.get('eventTypeId')
    orgStructureId      = params.get('orgStructureId')
    groupOrgStructure   = params.get('groupOrgStructure')
    districtId          = params.get('districtId')
    financeTypeId       = params.get('financeTypeId')

    chkMKB              = params.get('chkMKB')
    chkAge              = params.get('chkAge')
    chkSex              = params.get('chkSex')
    chkEmployment       = params.get('chkEmployment')
    chkEventType        = params.get('chkEventType')
    chkOrgStructure     = params.get('chkOrgStructure')
    chkDistrict         = params.get('chkDistrict')
    chkFinanceType      = params.get('chkFinanceType')

    eventTypeIdMulti    = params.get('eventTypeIdMulti')
    orgStructureIdMulti = params.get('orgStructureIdMulti')
    districtIdMulti     = params.get('districtIdMulti')
    financeTypeIdMulti  = params.get('financeTypeMulti')

    currentDate = QtCore.QDate().currentDate().toString('yyyy-MM-dd')

    tableEvent = db.table('Event')
    tableContract = db.table('Contract')
    tableClient = db.table('Client')
    tableClientAddress = db.table('ClientAddress')
    tableDistrict = db.table('rbDistrict')
    tableEventType = db.table('EventType')
    tableExecPerson = db.table('vrbPerson').alias('ExecPerson')
    tableDiagnostic = db.table('Diagnostic')
    tableDiagnosis = db.table('Diagnosis')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableOrgStructure = db.table('OrgStructure')

    table = tableEvent
    table = table.innerJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
    table = table.innerJoin(tableClient, tableClient['id'].eq(tableEvent['client_id']))
    table = table.innerJoin(tableClientAddress, u"""ClientAddress.id = (Select ca.id
                                                                                From  ClientAddress as ca
                                                                                where ca.client_id = Client.id
                                                                                 and ca.type = 0
                                                                                 and ca.deleted = 0
                                                                                Order by ca.createDateTime desc
                                                                                Limit 0, 1)""")
    table = table.leftJoin(tableDistrict, tableDistrict['id'].eq(tableClientAddress['district_id']))
    table = table.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    table = table.leftJoin(tableExecPerson, tableExecPerson['id'].eq(tableEvent['execPerson_id']))
    table = table.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableExecPerson['orgStructure_id']))
    table = table.leftJoin(tableDiagnostic, u"""Diagnostic.`id` = IF((Select d.`id`
											From Diagnostic d
												inner join rbDiagnosisType dt
													on d.`diagnosisType_id` = dt.`id`
											Where d.`event_id` = Event.`id`
												and dt.`code` = 7
											Order by d.id desc
											Limit 0,1
											), (Select d.`id`
											From Diagnostic d
												inner join rbDiagnosisType dt
													on d.`diagnosisType_id` = dt.`id`
											Where d.`event_id` = Event.`id`
												and dt.`code` = 7
											Order by d.id desc
											Limit 0,1
											),(Select d.`id`
											From Diagnostic d
												inner join rbDiagnosisType dt
													on d.`diagnosisType_id` = dt.`id`
											Where d.`event_id` = Event.`id`
												and dt.`code` in (1,2)
											Order by d.id desc
											Limit 0,1
											))""")
    table = table.leftJoin(tableDiagnosis, tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']))
    table = table.leftJoin(tableDiagnosisType, tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))

    cols = [
        u"Concat_WS(' ', Client.lastName, Client.firstName, Client.patrName) as fullName",
        tableClient['id'].alias('clientId'),
        tableClient['birthDate'].alias('birthDate'),
        tableExecPerson['name'].alias('execPersonName'),
        tableDiagnosis['MKB'].alias('MKB'),
        tableEvent['execDate'].alias('execDate'),
        tableDiagnosisType['code'],
        tableEventType['name'].alias('eventType'),
        tableDistrict['name'].alias('district'),
        tableOrgStructure['id'].alias('orgStructureId')
    ]

    cond = []
    cond.append(tableEvent['execDate'].isNotNull())
    cond.append(tableClientAddress['type'].eq(0))
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableClient['deleted'].eq(0))
    cond.append(tableEvent['execDate'].dateGe(begDate))
    cond.append(tableEvent['execDate'].dateLe(endDate))
    if ZNOFirst == 1:
        cond.append(tableEvent['ZNOFirst'].eq(1))
    elif ZNOFirst == 2:
        cond.append(tableEvent['ZNOFirst'].eq(0))
    if ZNOMorph == 1:
        cond.append(tableEvent['ZNOMorph'].eq(1))
    elif ZNOMorph == 2:
        cond.append(tableEvent['ZNOMorph'].eq(0))
    if chkMKB:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if chkAge:
        cond.append(u"YEAR(%s) - YEAR(%s) >= %s" %(tableClient['birthDate'], currentDate, ageFrom))
        cond.append(u"YEAR(%s) - YEAR(%s) <= %s" %(tableClient['birthDate'], currentDate, ageTo))
    if chkSex:
        cond.append(tableClient['sex'].eq(sex))
    if chkEmployment:
        if employment == 0:
            cond.append(u"YEAR(%s) - YEAR(DATE(%s)) >= %s" %(tableClient['birthDate'], currentDate, 18))
            cond.append(u"YEAR(%s) - YEAR(DATE(%s)) < %s" %(tableClient['birthDate'], currentDate,
                                                  db.if_(tableClient['sex'].eq(1), u'60',
                                                         db.if_(tableClient['sex'].eq(2), u'55', u'150'))))
        elif employment == 1:
            cond.append(u"YEAR(%s) - YEAR(%s) < %s" %(tableClient['birthDate'], currentDate, 18))
            cond.append(u"YEAR(%s) - YEAR(%s) >= %s" %(tableClient['birthDate'], currentDate,
                                                  db.if_(tableClient['sex'].eq(1), u'60',
                                                         db.if_(tableClient['sex'].eq(2), u'55', u'150'))))
    if chkOrgStructure:
        cond.append(tableOrgStructure['id'].inlist(orgStructureIdMulti))
    elif orgStructureId:
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if chkEventType:
        cond.append(tableEventType['id'].inlist(eventTypeIdMulti))
    elif eventTypeId:
        cond.append(tableEventType['id'].eq(eventTypeId))

    if chkDistrict:
        cond.append(tableDistrict['id'].inlist(districtIdMulti))
    elif districtId:
        cond.append(tableDistrict['id'].eq(districtId))

    if chkFinanceType:
        cond.append(tableContract['finance_id'].inlist(financeTypeIdMulti))
    elif financeTypeId:
        cond.append(tableContract['finance_id'].eq(financeTypeId))

    order = []
    if groupOrgStructure:
        order.append(tableOrgStructure['name'])
    order.append(tableEvent['execDate'])
    stmt  = db.selectStmt(table, fields=cols, where=cond, order=order)
    return db.query(stmt)

class CReportZNOEstablishedFirst(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'ЗНО установлен впервые')


    def getSetupDialog(self, parent):
        result = CZNOEstablishedFirst(parent)
        result.setTitle(self.title())
        return result

    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        rows = []
        if params.get('begDate'):
            rows.append(u'за период с %s по %s' %(forceString(params.get('begDate')), forceString(params.get('endDate'))))
        rows.append(u'ЗНО:')
        if params.get('ZNOFirst') == 1:
            rows.append(u'ЗНО установлен впервые')
        if params.get('ZNOFirst') == 2:
            rows.append(u'ЗНО установлен впервые не выставлено')
        if params.get('ZNOMorph') == 1:
            rows.append(u'ЗНО подтверждён морфологически')
        if params.get('ZNOMorph') == 2:
            rows.append(u'ЗНО подтверждён морфологически не выставлено')
        if params.get('chkAge'):
            rows.append(u'возраст: с %s по %s' %(forceString(params.get('ageFrom')), forceString(params.get('ageTo'))))
        if params.get('chkSex'):
            rows.append(u'пол: %s' %{0: u'не указано', 1: u'М', 2: u'Ж'}[params.get('sex')])
        if params.get('chkEmployment'):
            rows.append(u'трудоспособность: %s' %{0: u'да', 1: u'нет'}[params.get('employment')])
        if params.get('chkMKB'):
            rows.append(u'Коды диагноов по МКБ: с %s по %s' %(params.get('MKBFrom'), params.get('MKBTo')))
        if params.get('chkEventType'):
            eventTypeNames = [getEventTypeName(eventTypeId) for eventTypeId in params.get('eventTypeIdMulti')]
            rows.append(u'тип обращения: %s' %u', '.join(eventTypeNames))
        elif params.get('eventTypeId'):
            rows.append(u'тип обращения: %s' %getEventTypeName(params.get('eventTypeId')))
        if params.get('chkOrgStructure'):
            orgStructureNames = [getOrgStructureName(orgStructureId) for orgStructureId in params.get('orgStructureIdMulti')]
            rows.append(u'подразделения: %s' %u', '.join(orgStructureNames))
        elif params.get('orgStructureId'):
            rows.append(u'подразделение: %s' %getOrgStructureName(params.get('orgStructureId')))
        if params.get('groupOrgStructure'):
            rows.append(u'группировка: по отделениям')
        if params.get('chkDistrict'):
            districtNames = [getDistrictName(districtId) for districtId in params.get('districtIdMulti')]
            rows.append(u'район: %s' %u', '.join(districtNames))
        elif params.get('districtId'):
            rows.append(u'район: %s' %getDistrictName(params.get('districtId')))
        if params.get('chkFinanceType'):
            financeTypeNames = [getFinanceTypeName(financeTypeId) for financeTypeId in params.get('financeTypeIdMulti')]
            rows.append(u'тип финансирования: %s' %u', '.join(financeTypeNames))
        elif params.get('financeTypeId'):
            rows.append(u'тип финансирования: %s' %getFinanceTypeName(params.get('financeTypeId')))
        rows.append((u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime())))

        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self,params):
        group = params.get('groupOrgStructure')
        query = selectData(params)
        outputColumns = params.get('outputColumns')
        groupOrgStructure = params.get('chkGroupOrgStructure')
        query = selectData(params)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        self.setQueryText(forceString(query.lastQuery()))
        if groupOrgStructure:
            cursor.insertText(u'Группировка: по отделениям')
        cursor.insertBlock()
        tableColumns = [
            (' 4%', [u'№ п/п'], CReportBase.AlignLeft),
            ('20%', [u'ФИО'], CReportBase.AlignLeft),
            ('10%', [u'Номер амб.карты'], CReportBase.AlignLeft),
            (' 8%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('20%', [u'Врач'], CReportBase.AlignLeft),
            (' 8%', [u'МКБ'], CReportBase.AlignLeft),
            (' 8%', [u'Дата выполнения'], CReportBase.AlignLeft),
            ('10%', [u'Тип обращения'], CReportBase.AlignLeft),
            ('10%', [u'Район'], CReportBase.AlignLeft),
            ]

        table = createTable(cursor, tableColumns)
        currentOrgStructureId = 0
        orgStructureRow = 0
        totalOrgStructure = 0
        total = 0
        count = 1
        while query.next():
            record = query.record()
            if currentOrgStructureId != record.value('orgStructureId') and group:
                row = table.addRow()
                currentOrgStructureId = record.value('orgStructureId')
                table.setText(row, 1, getOrgStructureFullName(currentOrgStructureId), CReportBase.TableTotal, CReportBase.AlignLeft)
                if orgStructureRow:
                    table.setText(orgStructureRow, 5, u'Итого поподразделению: %s' %forceString(totalOrgStructure), CReportBase.TableTotal, CReportBase.AlignLeft)
                    totalOrgStructure = 0
                orgStructureRow = row
                table.mergeCells(row, 0, 1, 5)
                table.mergeCells(row, 5, 1, 4)

            row = table.addRow()
            fields = (
                count,
                forceString(record.value('fullName')),
                forceString(record.value('clientId')),
                forceString(forceDate(record.value('birthDate')).toString('dd.MM.yyyy')),
                forceString(record.value('execPersonName')),
                forceString(record.value('MKB')),
                forceString(forceDate(record.value('execDate')).toString('dd.MM.yyyy')),
                forceString(record.value('eventType')),
                forceString(record.value('district')) if forceString(record.value('district')) else u'не указано',
            )
            count += 1
            totalOrgStructure += 1
            total += 1
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        if orgStructureRow and group:
            table.setText(orgStructureRow, 5, u'Итого поподразделению: %s' %forceString(totalOrgStructure), CReportBase.TableTotal, CReportBase.AlignLeft)

        row = table.addRow()
        table.setText(row, 1, u'Итого: %s' % forceString(total), CReportBase.TableTotal, CReportBase.AlignLeft)
        table.mergeCells(row, 1, 1, 9)
        return doc


class CZNOEstablishedFirst(QtGui.QDialog, Ui_ReportZNOEstablishedFirst):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventType.setTable('EventType', True, filter = getWorkEventTypeFilter())
        self.cmbDistrict.setTable('rbDistrict', True)
        self.cmbFinanceType.setTable('rbFinance', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.lstEventType.setTable('EventType', filter = getWorkEventTypeFilter())
        self.lstEventType.setVisible(False)
        self.lstOrgStructure.setTable('OrgStructure')
        self.lstOrgStructure.setVisible(False)
        self.lstDistrict.setTable('rbDistrict')
        self.lstDistrict.setVisible(False)
        self.lstFinanceType.setTable('rbFinance')
        self.lstFinanceType.setVisible(False)
        self.cmbZNOValueList = [
            u'не задано',
            u'выбрано',
            u'не выбрано'
        ]
        for value in self.cmbZNOValueList:
            self.cmbZNOFirst.addItem(value)
            self.cmbZNOMorph.addItem(value)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbZNOFirst.setCurrentIndex(params.get('ZNOFirst', 1))
        self.cmbZNOMorph.setCurrentIndex(params.get('ZNOMorph', 1))
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo', 'Z99.9'))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.cmbEmployment.setCurrentIndex(params.get('employment', 0))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.chkGroupOrgStructure.setChecked(params.get('groupOrgStructure', False))
        self.cmbDistrict.setValue(params.get('districtId', None))
        self.cmbFinanceType.setValue(params.get('financeType', 0))

        self.chkMKB.setChecked(params.get('chkMKB', False))
        self.chkAge.setChecked(params.get('chkAge', False))
        self.chkSex.setChecked(params.get('chkSex', False))
        self.chkEmployment.setChecked(params.get('chkEmployment', False))
        # self.chkEventTypeMulti.setChecked(params.get('chkEventType', False))
        # self.chkOrgStructureMulti.setChecked(params.get('chkOrgStructure', False))
        # self.chkDistrictMulti.setChecked(params.get('chkDistrict', False))


    def params(self):
        params = {}
        params['begDate']           = self.edtBegDate.date()
        params['endDate']           = self.edtEndDate.date()
        params['ZNOFirst']          = self.cmbZNOFirst.currentIndex()
        params['ZNOMorph']          = self.cmbZNOMorph.currentIndex()
        params['MKBFrom']           = forceString(self.edtMKBFrom.text())
        params['MKBTo']             = forceString(self.edtMKBTo.text())
        params['ageFrom']           = forceInt(self.edtAgeFrom.value())
        params['ageTo']             = forceInt(self.edtAgeTo.value())
        params['sex']               = self.cmbSex.currentIndex()
        params['employment']        = self.cmbEmployment.currentIndex()
        params['eventTypeId']       = self.cmbEventType.value()
        params['orgStructureId']    = self.cmbOrgStructure.value()
        params['groupOrgStructure'] = self.chkGroupOrgStructure.isChecked()
        params['districtId']        = self.cmbDistrict.value()
        params['financeTypeId']     = self.cmbFinanceType.value()

        params['chkMKB']            = self.chkMKB.isChecked()
        params['chkAge']            = self.chkAge.isChecked()
        params['chkSex']            = self.chkSex.isChecked()
        params['chkEmployment']     = self.chkEmployment.isChecked()
        params['chkEventType']      = self.chkEventTypeMulti.isChecked()
        params['chkOrgStructure']   = self.chkOrgStructureMulti.isChecked()
        params['chkDistrict']       = self.chkDistrictMulti.isChecked()
        params['chkFinanceType']    = self.chkFinanceTypeMulti.isChecked()

        params['eventTypeIdMulti']    = self.lstEventType.nameValues()
        params['orgStructureIdMulti'] = self.lstOrgStructure.nameValues()
        params['districtIdMulti']     = self.lstDistrict.nameValues()
        params['financeTypeIdMulti']  = self.lstFinanceType.nameValues()
        return params

    @QtCore.pyqtSlot(int)
    def on_chkEmployment_stateChanged(self, state):
        if state and self.chkAge.isChecked():
            self.chkAge.setChecked(False)
            self.edtAgeFrom.setEnabled(False)
            self.edtAgeTo.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_chkAge_stateChanged(self, state):
        if state and self.chkEmployment.isChecked():
            self.chkEmployment.setChecked(False)
            self.cmbEmployment.setEnabled(False)

    @QtCore.pyqtSlot(int)
    def on_cmbZNOFirst_currentIndexChanged(self, index):
        self.cmbZNOMorph.setDisabled(not (index in [1, 2]))

    @QtCore.pyqtSlot(int)
    def on_cmbZNOMorph_currentIndexChanged(self, index):
        self.cmbZNOFirst.setDisabled(not (index in [1, 2]))