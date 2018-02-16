# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils                      import forceInt, forceRef, forceString, getVal, forceDate
from Orgs.Utils                         import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo

from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.Ui_ReportMovingDispClients import Ui_ReportMovingDispClients


def selectInRange(begDate, endDate, orgStructureId, personId, rowGrouping):
    db = QtGui.qApp.db
    tableDiagnosis       = db.table('Diagnosis')
    tableClientDispanser = db.table('rbDispanser')
    tablePerson = db.table('Person')

    additionalFrom = ''
    order = []
    if rowGrouping == 0: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by personId
        groupField = 'Diagnosis.person_id'
    elif rowGrouping == 3:
        groupField = 'CONCAT_WS(\' | \', Diagnosis.MKB, MKB_Tree.DiagName)'
        additionalFrom += u' INNER JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB'
        order.append(tableDiagnosis['MKB'])

    stmt = u'''SELECT %s as rowKey,
                      count(if(rbDispanser.code in ('2','6'),Diagnosis.client_id,NULL)) AS take,
                      count(if(rbDispanser.code not in ('2','6','1'),Diagnosis.client_id,NULL)) AS cancel
               FROM Diagnosis
                    INNER JOIN rbDispanser ON rbDispanser.id = Diagnosis.dispanser_id
                    LEFT JOIN Person ON Person.id = Diagnosis.person_id
                    %s
               WHERE %s
               GROUP BY rowKey'''

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableClientDispanser['observed'].eq(1))
    cond.append(tableDiagnosis['setDate'].dateGe(begDate))
    cond.append(tableDiagnosis['endDate'].dateLe(endDate))

    if personId:
        cond.append(tableDiagnosis['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    return db.query(stmt % (groupField, additionalFrom, (db.joinAnd(cond))))

def selectBefor(begDate, endDate, orgStructureId, personId, rowGrouping):
    db = QtGui.qApp.db
    tableDiagnosis       = db.table('Diagnosis')
    tableClientDispanser = db.table('rbDispanser')
    tablePerson = db.table('Person')

    additionalFrom = ''
    order = ''
    if rowGrouping == 0: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by personId
        groupField = 'Diagnosis.person_id'
    elif rowGrouping == 3:
        groupField = 'CONCAT_WS(\' | \', Diagnosis.MKB, MKB_Tree.DiagName)'
        additionalFrom += u' INNER JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB'
        order += 'ORDER BY  MKB_Tree.DiagID'

    stmt = u'''SELECT %s as rowKey,
                      count(if(rbDispanser.code = 1, Diagnosis.client_id, NULL)) AS takeBefore
               FROM Diagnosis
                    INNER JOIN rbDispanser ON rbDispanser.id = Diagnosis.dispanser_id
                    LEFT JOIN Person ON Person.id = Diagnosis.person_id
                    %s
               WHERE %s
               GROUP BY rowKey
               %s'''

    cond = []
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableClientDispanser['observed'].eq(1))
    cond.append(tableDiagnosis['setDate'].dateLe(begDate))
    cond.append(tableDiagnosis['endDate'].dateGe(begDate))
    cond.append(tableDiagnosis['deleted'].eq(0))

    if personId:
        cond.append(tableDiagnosis['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    return db.query(stmt % (groupField, additionalFrom, (db.joinAnd(cond)), order))

def selectAfter(begDate, endDate, orgStructureId, personId, rowGrouping):
    db = QtGui.qApp.db
    tableDiagnosis       = db.table('Diagnosis')
    tableClientDispanser = db.table('rbDispanser')
    tablePerson = db.table('Person')

    additionalFrom = ''
    order = ''
    if rowGrouping == 0: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by personId
        groupField = 'Diagnosis.person_id'
    elif rowGrouping == 3:
        groupField = 'CONCAT_WS(\' | \', Diagnosis.MKB, MKB_Tree.DiagName)'
        additionalFrom += u' INNER JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB'
        order += 'ORDER BY  MKB_Tree.DiagID'


    stmt = u'''SELECT %s as rowKey,
                      count(if(rbDispanser.code = 1,Diagnosis.client_id,NULL)) AS cancelAfter
               FROM Diagnosis
                    INNER JOIN rbDispanser ON rbDispanser.id = Diagnosis.dispanser_id
                    LEFT JOIN Person ON Person.id = Diagnosis.person_id
                    %s
               WHERE %s
               GROUP BY rowKey
               %s'''

    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    cond.append(tableClientDispanser['observed'].eq(1))
    cond.append(tableDiagnosis['setDate'].dateLe(endDate))
    cond.append(tableDiagnosis['endDate'].dateGe(endDate))

    if personId:
        cond.append(tableDiagnosis['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    return db.query(stmt % (groupField, additionalFrom, (db.joinAnd(cond)), order))

def selectEvents(begDate, endDate, orgStructureId, personId, rowGrouping):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')

    additionalFrom = ''
    order = ''
    if rowGrouping == 0: # by orgStructureId
        groupField = 'Person.orgStructure_id'
    elif rowGrouping == 1: # by speciality_id
        groupField = 'Person.speciality_id'
    elif rowGrouping == 2: # by personId
        groupField = 'Event.execPerson_id'
    elif rowGrouping == 3:
        groupField = 'CONCAT_WS(\' | \', Diagnosis.MKB, MKB_Tree.DiagName)'
        additionalFrom += u''' INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
                               INNER JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id AND Diagnosis.deleted = 0
                               INNER JOIN MKB_Tree ON MKB_Tree.DiagID = Diagnosis.MKB'''
        order += 'ORDER BY  MKB_Tree.DiagID'

    stmt = u'''SELECT %s as rowKey,
                      count(Event.id) AS event
                      FROM Event
                            INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.code = '03'
                            LEFT JOIN Person ON Person.id = Event.execPerson_id
                            %(insert)s
               WHERE %s
               GROUP BY rowKey
               %s'''

    cond = []
    cond.append(tableEvent['execDate'].dateLe(endDate))
    cond.append(tableEvent['execDate'].dateGe(begDate))
    cond.append(tableEvent['deleted'].eq(0))

    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    return db.query(stmt % (groupField, additionalFrom, (db.joinAnd(cond)), order))

def selectData(params):
    stmt = u'''
                Select
                    Result.rowKey,
                    Result.code,
                    Result.name,
                    MKB_Tree.DiagID,
                    MKB_Tree.DiagName,
                    Sum(Result.take) as take,
                    Sum(Result.cancel) as cancel,
                    Sum(Result.event) as event,
                    Sum(Result.takeBefore) as takeBefore,
                    Sum(Result.takeAfter)as takeAfter
                    From
                    (
                            Select
                                %(insertName)s.id as rowKey,
                                %(insertName)s.code as code,
                                %(insertName)s.name as name,
                                Diagnosis.MKB as MKB,
                                count(if(rbDispanser.code in ('2','6'),Diagnosis.client_id,NULL)) as take,
                                count(if(rbDispanser.code in ('3','4','5'),Diagnosis.client_id,NULL)) as cancel,
                                0 as event,
                                0 as takeBefore,
                                0 as takeAfter
                            From Diagnosis
                                inner join rbDispanser
                                    on rbDispanser.id = Diagnosis.dispanser_id
                                inner join vrbPersonWithSpeciality as PersonSpec
                                    on PersonSpec.id = Diagnosis.person_id
                                %(insertForm)s
                            Where
                                Diagnosis.deleted = 0
                                and Diagnosis.setDate >= %(insertBegDate)s
                                and Diagnosis.endDate <= %(insertEndDate)s
                                %(insertCond)s
                            Group by rowKey, Diagnosis.MKB
                        Union
                            Select
                                %(insertName)s.id as rowKey,
                                %(insertName)s.code as code,
                                %(insertName)s.name as name,
                                Diagnosis.MKB as MKB,
                                0 as take,
                                0 as cancel,
                                count(Event.id) as event,
                                0 as takeBefore,
                                0 as takeAfter
                            From Event
                                inner join EventType
                                    on EventType.id = Event.eventType_id
                                    and EventType.code = '03'
                                left join Diagnostic
                                    on Event.id = Diagnostic.event_id
                                left join Diagnosis
                                    on Diagnostic.diagnosis_id = Diagnosis.id
                                left join vrbPersonWithSpeciality as PersonSpec
                                    on PersonSpec.id = Event.execPerson_id
                                %(insertForm)s
                            Where
                                Event.deleted = 0
                                and EventType.deleted = 0
                                and Event.execDate >= %(insertBegDate)s
                                and Event.execDate <= %(insertEndDate)s
                                %(insertCond)s
                            Group by rowKey, Diagnosis.MKB
                        Union
                            Select
                                %(insertName)s.id as rowKey,
                                %(insertName)s.code as code,
                                %(insertName)s.name as name,
                                Diagnosis.MKB as MKB,
                                0 as take,
                                0 as cancel,
                                0 as event,
                                count(if(rbDispanser.code in ('1'),Diagnosis.client_id,NULL)) as takeBefore,
                                0 as takeAfter
                            From Diagnosis
                                inner join rbDispanser
                                    on rbDispanser.id = Diagnosis.dispanser_id
                                inner join vrbPersonWithSpeciality as PersonSpec
                                    on PersonSpec.id = Diagnosis.person_id
                                %(insertForm)s
                            Where
                                Diagnosis.deleted = 0
                                and Diagnosis.setDate <= %(insertBegDate)s
                                and Diagnosis.endDate >= %(insertBegDate)s
                                %(insertCond)s
                            Group by rowKey, Diagnosis.MKB
                        Union
                            Select
                                %(insertName)s.id as rowKey,
                                %(insertName)s.code as code,
                                %(insertName)s.name as name,
                                Diagnosis.MKB as MKB,
                                0 as take,
                                0 as cancel,
                                0 as event,
                                0 as takeBefore,
                                count(if(rbDispanser.code in ('1'),Diagnosis.client_id,NULL)) as takeAfter
                            From Diagnosis
                                inner join rbDispanser
                                    on rbDispanser.id = Diagnosis.dispanser_id
                                inner join vrbPersonWithSpeciality as PersonSpec
                                    on PersonSpec.id = Diagnosis.person_id
                                %(insertForm)s
                            Where
                                Diagnosis.deleted = 0
                                and Diagnosis.setDate <= %(insertEndDate)s
                                and Diagnosis.endDate >= %(insertEndDate)s
                                %(insertCond)s
                            Group by rowKey, Diagnosis.MKB
                    ) as Result
                    left join MKB_Tree
                        on MKB_Tree.DiagID = Result.MKB
                Where
                    not ((Result.take = 0) and (Result.cancel = 0) and (Result.event = 0) and (Result.takeBefore = 0) and (Result.takeAfter = 0))

                Group by Result.rowKey, MKB_Tree.DiagID
                Order by Result.rowKey, isNull(MKB_Tree.DiagID), MKB_Tree.DiagID'''

    db = QtGui.qApp.db
    begDate         = '\'' + forceDate(params.get('begDate', QtCore.QDate())).toString('yyyy-MM-dd') + '\''
    endDate         = '\'' + forceDate(params.get('endDate', QtCore.QDate())).toString('yyyy-MM-dd') + '\''
    orgStructureId  = params.get('orgStructureId', None)
    personId        = params.get('personId', None)
    rowGrouping     = params.get('rowGrouping', None)

    insertForm = ''
    if rowGrouping == 0: # by orgStructureId
        insertName = u'OrgStructure'
        insertForm = u'''left join OrgStructure
                            on PersonSpec.orgStructure_id = OrgStructure.id'''
    elif rowGrouping == 1: # by speciality_id
        insertName = u'rbSpeciality'
        insertForm = u'''inner join rbSpeciality
                            on rbSpeciality.id = PersonSpec.speciality_id'''
    elif rowGrouping == 2: # by personId
        insertName = u'PersonSpec'

    cond = []

    if personId:
        personTable = db.table('Person')
        cond.append(personTable['id'].eq(personId))
    elif orgStructureId:
        if rowGrouping != 0:
            insertForm += u'''\nleft join OrgStructure
			    		        on PersonSpec.orgStructure_id = OrgStructure.id'''
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))

    if (cond):
        cond = u'and ' + db.joinAnd(cond)
    else:
        cond = u''
    return db.query(stmt %{'insertName': insertName,
                           'insertForm': insertForm,
                           'insertBegDate': begDate,
                           'insertEndDate': endDate,
                           'insertCond': cond})

class CReportMovingDispClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Движение диспансерных больных (по нозологии)')
        self.table = []

    def getSetupDialog(self, parent):
        result = CMovingDispClients(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        rowGrouping = params.get('rowGrouping', 0)

        if rowGrouping == 0: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = lambda orgStructureId: forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'name'))
            columnName = u'Участок, кабинет'
        elif rowGrouping == 1: # by speciality_id
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            columnName = u'Специальность'
        elif rowGrouping == 2: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            columnName = u'Врач'

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
            ('30%', [columnName], CReportBase.AlignLeft),
            ('10%', [u'Состояло на нач.'], CReportBase.AlignLeft),
            ('10%', [u'Взято'], CReportBase.AlignLeft),
            ('10%', [u'Снято'], CReportBase.AlignLeft),
            ('10%', [u'Состояло на конец'], CReportBase.AlignLeft),
            ('15%', [u'Осмотрено'], CReportBase.AlignLeft)
            ]

        table = createTable(cursor, tableColumns)
        priv = -1
        t_row_takeBefore = t_row_take = t_row_cancel = t_row_takeAfter = t_row_event = 0
        total_takeBefore = total_take = total_cancel = total_takeAfter = total_event = 0
        while query.next():
            record = query.record()
            row = table.addRow()
            curr = forceInt(record.value('rowKey')),
            if (curr != priv):
                if (priv != -1):
                    fields = (u'', t_row_takeBefore, t_row_take, t_row_cancel, t_row_takeAfter, t_row_event)
                    for col, val in enumerate(fields):
                        table.setText(row, col, val, CReportBase.TableTotal)
                    table.setText(row, 0, u'Итого:', CReportBase.TableTotal, CReportBase.AlignRight)
                    row = table.addRow()
                    t_row_takeBefore = t_row_take = t_row_cancel = t_row_takeAfter = t_row_event = 0
                code = (record.value('code')).toString()
                if (code):
                    table.setText(row, 0, forceString(code + u': ' + (record.value('name')).toString()), CReportBase.TableTotal)
                else:
                    table.setText(row, 0, u'Не указано', CReportBase.TableTotal)
                table.mergeCells(row, 0, 1, 6)
                row = table.addRow()
            priv = curr

            diagID = forceString(record.value('DiagID'))
            if (diagID):
                diagName = forceString(diagID + u': ' +(record.value('DiagName')).toString())
            else:
                diagName = u'Не указано'
            takeBefore = forceInt(record.value('takeBefore'))
            take = forceInt(record.value('take'))
            cancel = forceInt(record.value('cancel'))
            takeAfter = forceInt(record.value('takeAfter'))
            event = forceInt(record.value('event'))

            t_row_takeBefore += takeBefore
            t_row_take += take
            t_row_cancel += cancel
            t_row_takeAfter += takeAfter
            t_row_event += event

            total_takeBefore += takeBefore
            total_take += take
            total_cancel += cancel
            total_takeAfter += takeAfter
            total_event += event

            fields = (diagName, takeBefore, take, cancel, takeAfter, event)
            for col, val in enumerate(fields):
                table.setText(row, col, val)

        row = table.addRow()
        fields = (u'', t_row_takeBefore, t_row_take, t_row_cancel, t_row_takeAfter, t_row_event)
        for col, val in enumerate(fields):
            table.setText(row, col, val, CReportBase.TableTotal)
        table.setText(row, 0, u'Итого:', CReportBase.TableTotal, CReportBase.AlignRight)

        row = table.addRow()
        fields = (u'', total_takeBefore, total_take, total_cancel, total_takeAfter, total_event)
        for col, val in enumerate(fields):
            table.setText(row, col, val, CReportBase.TableTotal)
        table.setText(row, 0, u'Всего:', CReportBase.TableTotal, CReportBase.AlignRight)
        return doc

    def getDescription(self, params):
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        personId = params.get('personId', None)
        if params.get('cmbOrgStructure', False):
            lstOrgStructure = params.get('lstOrgStructure', None)
            orgStructureId = None
        else:
            lstOrgStructure = None
            orgStructureId = params.get('orgStructureId', None)
        rowGrouping = params.get('rowGrouping', None)
        reportDate = params.get('reportDate', None)

        rows = []
        if begDate or endDate:
            rows.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if personId:
            personInfo = getPersonInfo(personId)
            rows.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if orgStructureId:
            rows.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        if rowGrouping != None:
            rows.append(u'группировка: '+ [u'по подразделениям', u'по специальности', u'по врачам'][rowGrouping])
        if reportDate:
            rows.append(u'отчёт составлен: '+forceString(reportDate))
        else:
            rows.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))

        return rows

class CMovingDispClients(QtGui.QDialog, Ui_ReportMovingDispClients):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(getVal(params, 'begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(getVal(params, 'endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(getVal(params, 'orgStructureId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbRowGrouping.setCurrentIndex(getVal(params, 'rowGrouping', 0))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['rowGrouping'] = self.cmbRowGrouping.currentIndex()
        return result

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        self.cmbPerson.setOrgStructureId(forceInt(self.cmbOrgStructure.value()))