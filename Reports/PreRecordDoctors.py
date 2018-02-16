# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDate, forceInt, forceRef, forceString, firstMonthDay, lastMonthDay, formatName
from Orgs.Utils         import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_PreRecordDoctorsDialog import Ui_PreRecordDoctorsDialog


class CPreRecord(object):
    def getVisit(self, directionDate, personId, specialityId, recordVisit, clientId):
        recordListByDate = recordVisit.get(directionDate.toString(), None)
        val = False
        eventId = None
        if recordListByDate:
            val, eventId = self.checkData(recordListByDate, 'person%d'%personId, clientId)
            if not val:
                if not specialityId:
                    return [False, None]
                val, eventId = self.checkData(recordListByDate, 'spec%s'%forceString(specialityId), clientId)
        return [val, eventId]

    def checkData(self, list, key, clientId):
        recordListByPersonOrSpec = list.get(key, None)
        if recordListByPersonOrSpec:
            for recordVisitData in recordListByPersonOrSpec:
                if clientId == forceRef(recordVisitData.value('client_id')):
                    eventId = forceRef(recordVisitData.value('eventId'))
                    return [True, eventId]
        return [False, None]

    def makeNeedfulDicts(self, query):
        db = QtGui.qApp.db
        tableVisit                = db.table('Visit')
        tableEvent                = db.table('Event')
        tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')

        self.recordVisitByDate  = {}
        specialityIdList        = []
        personIdList            = []
        clientIdlist            = []
        recordList              = []
        topDate = None
        botDate = None
        while query.next():
            record = query.record()
            recordList.append(record)
            if not botDate:
                botDate = forceDate(record.value('directionDate'))
            topDate = forceDate(record.value('directionDate'))
            specialityId  = forceRef(record.value('personSpeciality'))
            if specialityId not in specialityIdList:
                specialityIdList.append(specialityId)
            personId      = forceRef(record.value('executer'))
            if personId not in personIdList:
                personIdList.append(personId)
            clientId      = forceRef(record.value('client_id'))
            if clientId not in clientIdlist:
                clientIdlist.append(clientId)
        if specialityIdList:
            cols =      [tableVisit['date'],
                         tableVisit['person_id'],
                         tableVisit['event_id'].alias('eventId'),
                         tableEvent['client_id'],
                         tablePersonWithSpeciality['speciality_id'],
                         tablePersonWithSpeciality['name'].alias('personName')
                        ]
            condVisit =     [tableVisit['date'].between(botDate, topDate),
                             tableEvent['client_id'].inlist(clientIdlist),
                             tableVisit['deleted'].eq(0)
                            ]
            condVisit.append(db.joinOr([tablePersonWithSpeciality['speciality_id'].inlist(specialityIdList), tableVisit['person_id'].inlist(personIdList)]))
            tableQueryVisit = tableVisit
            tableQueryVisit = tableQueryVisit.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
            tableQueryVisit = tableQueryVisit.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableVisit['person_id']))
            recordVisit = db.getRecordList(tableQueryVisit, cols, condVisit, 'Visit.date')
            for record in recordVisit:
                date = forceDate(record.value('date')).toString()
                listByPersonOrSpec = self.recordVisitByDate.get(date, None)
                personId = forceRef(record.value('person_id'))
                specialityId = forceRef(record.value('speciality_id'))
                if not listByPersonOrSpec:
                    listByPersonOrSpec = {'person%d'%personId   : [record],
                                          'spec%s'%forceString(specialityId) : [record]}
                    self.recordVisitByDate[date] = listByPersonOrSpec
                else:
                    personList = listByPersonOrSpec.get('person%d'%personId, None)
                    if not personList:
                        listByPersonOrSpec['person%d'%personId] = [record]
                    else:
                        listByPersonOrSpec['person%d'%personId].append(record)
                    specList = listByPersonOrSpec.get('spec%s'%forceString(specialityId), None)
                    if not specList:
                        listByPersonOrSpec['spec%s'%forceString(specialityId)] = [record]
                    else:
                        listByPersonOrSpec['spec%s'%forceString(specialityId)].append(record)

                    self.recordVisitByDate[date] = listByPersonOrSpec
        return recordList


def selectData(params):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableAction = tableAction.alias('NeedAction')

    condE  = []
    condP  = []
    condA  = []
    cond   = []
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    begDateRecord = params.get('begDateBeforeRecord', None)
    endDateRecord = params.get('endDateBeforeRecord', None)
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', None)
    chkPeriodRecord = params.get('chkPeriodRecord', None)
    chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
    showWithoutOverTime = params.get('showWithoutOverTime', None)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)
    
    if chkPeriodRecord:
        if begDate:
            cond.append(tableAction['createDatetime'].dateGe(begDate))
        if endDate:
            cond.append(tableAction['createDatetime'].dateLe(endDate))
#        if begDate:
#            cond.append(tableEvent['setDate'].ge(begDate))
#        if endDate:
#            cond.append(tableEvent['setDate'].lt(endDate.addDays(1)))
    if chkPeriodBeforeRecord:
        if begDateRecord:
            cond.append(tableAction['directionDate'].dateGe(begDateRecord))
        if endDateRecord:
            cond.append(tableAction['directionDate'].dateLe(endDateRecord))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        if not personId:
            cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if showWithoutOverTime:
        cond.append('APTime.value IS NOT NULL')
    if ignoreRehabilitation:
        cond.append(tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where = u'name LIKE "%реабилитац%"' )))


    stmt = '''
    SELECT
Person.id, Person.lastName, Person.firstName, Person.patrName,
NeedAction.id AS Action_id, ActionType.code AS ambOrHome,
NeedAction.person_id AS executer, NeedAction.setPerson_id AS setPerson,
NeedAction.directionDate, NeedAction.note AS actionNote,
Event.client_id,
Person.speciality_id AS personSpeciality, SetPerson.speciality_id AS setPersonSpeciality,
SetPerson.org_id AS setPersonOrgId
FROM ActionProperty_Action
LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
LEFT JOIN Action ON Action.id = ActionProperty.action_id
LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
LEFT JOIN Action AS NeedAction ON NeedAction.id = ActionProperty_Action.value
LEFT JOIN Event ON Event.id = NeedAction.event_id
LEFT JOIN Person ON Person.id = NeedAction.person_id
LEFT JOIN Person AS SetPerson ON SetPerson.id = NeedAction.setPerson_id
LEFT JOIN ActionProperty AS APTimes ON APTimes.action_id = Action.id 
                                        AND APTimes.type_id = (SELECT id 
                                                               FROM ActionPropertyType AS APT 
                                                               WHERE APT.name LIKE 'times' AND APT.actionType_id = ActionType.id 
                                                               LIMIT 1)
LEFT JOIN ActionProperty_Time AS APTime ON APTime.id = APTimes.id AND APTime.index = ActionProperty_Action.index
WHERE
ActionProperty_Action.value IS NOT NULL
AND Person.speciality_id IS NOT NULL
AND %s ORDER BY NeedAction.directionDate''' % (db.joinAnd(cond))
    return db.query(stmt)


class CPreRecordDoctors(CReport, CPreRecord):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Предварительная запись по врачам')
        self.doctorsDict = {}


    def dumpParams(self, cursor, params):
        description = []
        db = QtGui.qApp.db
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begDateBeforeRecord = params.get('begDateBeforeRecord', QtCore.QDate())
        endDateBeforeRecord = params.get('endDateBeforeRecord', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        chkPeriodRecord = params.get('chkPeriodRecord', None)
        chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
        if chkPeriodRecord:
            if begDate or endDate:
                description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if chkPeriodBeforeRecord:
            if begDateBeforeRecord or endDateBeforeRecord:
                description.append(u'период предварительной записи' + dateRangeAsStr(begDateBeforeRecord, endDateBeforeRecord))
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if specialityId:
            description.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
        if personId:
            personInfo = getPersonInfo(personId)
            description.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100?', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        self.makeTable(cursor, doc, query)

        return doc

    def makeTable(self, cursor, doc, query):
        tableColumns = [
            ('2?', [u'№', u'', u'', u''], CReportBase.AlignLeft),
            ('10?', [u'Врачи', u'', u'', u''], CReportBase.AlignLeft),
            ('10?', [u'Амбулаторно', u'Всего', u'', u''], CReportBase.AlignCenter),
            ('10?', [u'', u'Выполнено', u'', u''], CReportBase.AlignCenter),
            ('10?', [u'', u'Актив', u'', u''], CReportBase.AlignRight),
            ('10?', [u'', u'Консультация', u'', u''], CReportBase.AlignRight),
            ('10?', [u'', u'', u'Сотр. ЛПУ', u''], CReportBase.AlignRight),
            ('10?', [u'', u'Первично', u'Не свои', u'Инфомат'], CReportBase.AlignRight),
            ('10?', [u'', u'', u'', u'Call-центр'], CReportBase.AlignRight),
            ('10?', [u'', u'', u'', u'Интернет'], CReportBase.AlignRight),
            ('10?', [u'На дому', u'Всего', u'', u''], CReportBase.AlignCenter),
            ('10?', [u'', u'Выполнено', u'', u''], CReportBase.AlignCenter),
            ('10?', [u'', u'Актив', u'', u''], CReportBase.AlignRight),
            ('10?', [u'', u'Консультация', u'', u''], CReportBase.AlignRight),
            ('10?', [u'', u'Первично', u'Сотр. ЛПУ'], CReportBase.AlignRight),
            ('10?', [u'', u'', u'Не свои', u'Инфомат'], CReportBase.AlignRight),
            ('10?', [u'', u'', u'', u'Call-центр'], CReportBase.AlignRight),
            ('10?', [u'', u'', u'', u'Интернет'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 1, 8)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 3, 1)
        table.mergeCells(1, 4, 3, 1)
        table.mergeCells(1, 5, 3, 1)
        table.mergeCells(1, 6, 1, 4)
        table.mergeCells(2, 6, 2, 1)
        table.mergeCells(2, 7, 1, 3)

        table.mergeCells(0, 10, 1, 8)
        table.mergeCells(1, 10, 3, 1)
        table.mergeCells(1, 11, 3, 1)
        table.mergeCells(1, 12, 3, 1)
        table.mergeCells(1, 13, 3, 1)
        table.mergeCells(1, 14, 1, 4)
        table.mergeCells(2, 14, 2, 1)
        table.mergeCells(2, 15, 1, 3)

        self.parseQueryInfo(query)
        resume = [u'Итого']+[0]*16
        for key in self.doctorsDict.keys():
            d = True
            x = 1
            for val in self.doctorsDict[key][1:]:
                if val:
                    d = False
                resume[x] += val
                x += 1
            if d:
                self.doctorsDict.pop(key)
        n = 1
        keys = self.doctorsDict.keys()
        keys.sort()
#        for val in  self.doctorsDict.values():
        for k in keys:
            val = self.doctorsDict[k]
            i = table.addRow()
            table.setText(i, 0, n)
            for column in range(17):
                table.setText(i, column+1, val[column])
            n += 1
        i  = table.addRow()
        table.setText(i, 0, n)
        for column in range(17):
            table.setText(i, column+1, resume[column])
        self.doctorsDict.clear()

    def parseQueryInfo(self, query):
        self.a = 0
        recordList = self.makeNeedfulDicts(query)
        for record in recordList:
            personId = forceInt(record.value('id'))
            name = formatName(record.value('lastName'),
                              record.value('firstName'),
                              record.value('patrName'))
            key = name+'%d'%personId
#            afore = self.doctorsDict.get(personId, None)
            afore = self.doctorsDict.get(key, None)
            if afore:
                self.addInfo(record, key)
            else:
                self.doctorsDict[key] = [name]+([0]*16)
                self.addInfo(record, key)


    def addInfo(self, record, key):
        personId            = forceInt(record.value('id'))
        actionId            = forceInt(record.value('Action_id'))
        actionType          = forceString(record.value('ambOrHome'))
        executer            = forceInt(record.value('executer'))
        setPerson           = forceInt(record.value('setPerson'))
        personSpecialyty    = forceInt(record.value('personSpeciality'))
        setPersonSpeciality = forceInt(record.value('setPersonSpeciality'))
        setPersonOrgId      = forceInt(record.value('setPersonOrgId'))
        clientId            = forceRef(record.value('client_id'))
        directionDateAction = forceDate(record.value('directionDate'))
        actionNote          = forceString(record.value('actionNote'))
        actionNoteLowerCase = actionNote.lower()
        if actionType == 'amb':
            column = 1
        elif actionType == 'home':
            column = 9
        else:
            column = None
        if column:
            self.doctorsDict[key][column] += 1
            visit, eventId = self.getVisit(directionDateAction, personId, personSpecialyty, self.recordVisitByDate, clientId)
            if visit:
                self.doctorsDict[key][column+1] += 1
            if setPerson and setPersonOrgId == QtGui.qApp.currentOrgId():
                if setPersonSpeciality:
                    if executer == setPerson:
                        column += 2
                    else:
                        column += 3
                else:
                    column += 4
            else:
                if u'инфомат' in actionNoteLowerCase:
                    add = 1
                elif (u'call-центр' in actionNoteLowerCase) or (u'callcenter' in actionNoteLowerCase):
                    add = 2
                elif (u'запись через веб-регистратуру' in actionNoteLowerCase) or \
                     (u'iVista Web Medical Service' in actionNote) or \
                     (u'ЗАПИСЬ ОСУЩЕСТВЛЕНА ЧЕРЕЗ СИСТЕМУ "НЕТРИКА"' in actionNote):
                    add = 3
                else:
                    return
                column += (4 + add)
            self.doctorsDict[key][column] += 1


class CPreRecordDoctorsEx(CPreRecordDoctors):
    def exec_(self):
        CPreRecordDoctors.exec_(self)

    def getSetupDialog(self, parent):
        result = CPreRecordDoctorsDialog(parent)
        result.setTitle(self.title())
        return result



class CPreRecordDoctorsDialog(QtGui.QDialog, Ui_PreRecordDoctorsDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.edtBegDateRecord.setDate(params.get('begDateBeforeRecord', firstMonthDay(date)))
        self.edtEndDateRecord.setDate(params.get('endDateBeforeRecord', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['begDateBeforeRecord'] = self.edtBegDateRecord.date()
        result['endDateBeforeRecord'] = self.edtEndDateRecord.date()
        result['chkPeriodRecord'] = self.chkPeriodRecord.isChecked()
        result['chkPeriodBeforeRecord'] = self.chkPeriodBeforeRecord.isChecked()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['showWithoutOverTime'] = self.chkShowWithoutOverTime.isChecked()
        result['ignoreRehabilitation'] = self.chkIgnoreRehabilitation.isChecked()
        return result


    @QtCore.pyqtSlot(bool)
    def on_chkPeriodRecord_clicked(self, checked):
        self.edtBegDate.setEnabled(checked)
        self.edtEndDate.setEnabled(checked)
        if checked:
            self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)


    @QtCore.pyqtSlot(bool)
    def on_chkPeriodBeforeRecord_clicked(self, checked):
        self.edtBegDateRecord.setEnabled(checked)
        self.edtEndDateRecord.setEnabled(checked)


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
