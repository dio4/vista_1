# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils              import forceDate, forceInt, forceRef, forceString, forceStringEx, formatName, \
                                       firstMonthDay, lastMonthDay
from Orgs.Utils                 import getOrgStructureFullName, getOrgStructureDescendants, getPersonInfo
from Reports.PreRecordDoctors   import CPreRecord
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_PreRecordUsersSetupDialog  import Ui_PreRecordUsersSetupDialog


def selectData(params,  groupBySpeciality = False):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePerson = db.table('Person')
    tableAction = db.table('Action')
    tableAction = tableAction.alias('NeedAction')
    tableExecPerson = db.table('Person').alias('ExecPerson')

    cond = []
    begDate = params.get('begDate', None)
    endDate = params.get('endDate', None)
    begDateRecord = params.get('begDateBeforeRecord', None)
    endDateRecord = params.get('endDateBeforeRecord', None)
    personId = params.get('personId', None)
    orgStructureId = params.get('orgStructureId', None)
    specialityId = params.get('specialityId', 0)
    chkOrgStructure = params.get('chkOrgStructure', None)
    chkPeriodRecord = params.get('chkPeriodRecord', None)
    showWithoutOverTime = params.get('showWithoutOverTime', None)
    chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)

    statusId = forceRef(QtGui.qApp.db.translate('rbDeferredQueueStatus', 'code', u'2', 'id'))
    
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
    if chkOrgStructure:
        if personId:
            cond.append(tableAction['setPerson_id'].eq(personId))
        if orgStructureId:
            cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        else:
            if not personId:
                cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if showWithoutOverTime:
        cond.append('APTime.value IS NOT NULL')
    if ignoreRehabilitation:
        cond.append(db.joinOr([tablePerson['orgStructure_id'].isNull(),
                               tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where = u'name LIKE "%реабилитац%"' ))]))
    if params.get('onlyWithExternalQuota', False):
        cond.append(tableExecPerson['availableForExternal'].eq(1))
    specialityCond = 'ExecPerson.speciality_id = %d' % specialityId if specialityId else '1'
    
    stmt = '''
    SELECT
Person.id, Person.lastName, Person.firstName, Person.patrName,
ActionType.code AS ambOrHome, Event.client_id, NeedAction.note AS actionNote,
NeedAction.person_id AS executer, NeedAction.setPerson_id, NeedAction.directionDate,
ExecPerson.speciality_id AS personSpecialyty,
DeferredQueue.id as zhos

FROM ActionProperty_Action
LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
LEFT JOIN Action ON Action.id = ActionProperty.action_id
LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
LEFT JOIN Action AS NeedAction ON NeedAction.id = ActionProperty_Action.value
LEFT JOIN Event ON Event.id = NeedAction.event_id
LEFT JOIN Person ON Person.id = NeedAction.setPerson_id
LEFT JOIN Person AS ExecPerson ON ExecPerson.id = NeedAction.person_id
LEFT JOIN ActionProperty AS APTimes ON APTimes.action_id = Action.id 
                                        AND APTimes.type_id = (SELECT id 
                                                               FROM ActionPropertyType AS APT 
                                                               WHERE APT.name LIKE 'times' AND APT.actionType_id = ActionType.id 
                                                               LIMIT 1)
LEFT JOIN ActionProperty_Time AS APTime ON APTime.id = APTimes.id AND APTime.index = ActionProperty_Action.index
LEFT JOIN DeferredQueue ON NeedAction.id = DeferredQueue.action_id AND DeferredQueue.status_id = %s
WHERE
ActionProperty_Action.value IS NOT NULL
AND %s AND %s ORDER BY NeedAction.`directionDate''' % (statusId, db.joinAnd(cond),  specialityCond)
    
    if groupBySpeciality:
        stmt = '''
            SELECT
    ExecPerson.speciality_id AS specialityID,
    rbSpeciality.name AS specName,
    DeferredQueue.id as zhos
    FROM ActionProperty_Action
    LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
    LEFT JOIN Action ON Action.id = ActionProperty.action_id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN Action AS NeedAction ON NeedAction.id = ActionProperty_Action.value
    LEFT JOIN Event ON Event.id = NeedAction.event_id
    LEFT JOIN Person ON Person.id = NeedAction.setPerson_id
    LEFT JOIN Person AS ExecPerson ON ExecPerson.id = NeedAction.person_id
    LEFT JOIN rbSpeciality ON ExecPerson.speciality_id = rbSpeciality.id
    LEFT JOIN ActionProperty AS APTimes ON APTimes.action_id = Action.id 
                                        AND APTimes.type_id = (SELECT id 
                                                               FROM ActionPropertyType AS APT 
                                                               WHERE APT.name LIKE 'times' AND APT.actionType_id = ActionType.id 
                                                               LIMIT 1)
    LEFT JOIN ActionProperty_Time AS APTime ON APTime.id = APTimes.id AND APTime.index = ActionProperty_Action.index
    LEFT JOIN DeferredQueue ON NeedAction.id = DeferredQueue.action_id AND DeferredQueue.status_id = %s
    WHERE
    ActionProperty_Action.value IS NOT NULL
    AND %s GROUP BY specialityID''' % (statusId, db.joinAnd(cond))

    return db.query(stmt)

class CPreRecordUsers(CReport, CPreRecord):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Предварительная запись по пользователям')
        self.doctorsDict = {}
        self.callCentrDict = {}


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
        #specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        chkPeriodRecord = params.get('chkPeriodRecord', None)
        chkPeriodBeforeRecord =  params.get('chkPeriodBeforeRecord', None)
        chkOrgStructure = params.get('chkOrgStructure', None)
        chkDetailCallCentr = params.get('detailCallCentr', None)

        if chkPeriodRecord:
            if begDate or endDate:
                description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        if chkPeriodBeforeRecord:
            if begDateBeforeRecord or endDateBeforeRecord:
                description.append(u'период предварительной записи' + dateRangeAsStr(begDateBeforeRecord, endDateBeforeRecord))
        if chkOrgStructure:
            if orgStructureId:
                description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
            else:
                description.append(u'подразделение: ЛПУ')
#            if specialityId:
#                description.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
            if personId:
                personInfo = getPersonInfo(personId)
                description.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if chkDetailCallCentr:
            description.append(u'Детализировать Call-центр')
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
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
        self.detailCallCentr = params.get('detailCallCentr', False)
        self.makeTable(cursor, doc, params)
        return doc

    def makeTable(self, cursor, doc, params):
        _params = params #atronah: непонятные телодвижения, так как новый список не создается и все действия продолжают менять params
        _params['specialityId'] = 0
        writtenFromZhos = params.get('writtenFromZhos')
        
        tableColumns = [
            ('2%', [u'№', u''], CReportBase.AlignLeft),
            ('17%', [u'Пользователь', u''], CReportBase.AlignLeft),
            ('13,5%', [u'Амбулаторно', u'Всего'], CReportBase.AlignLeft),
            ('13,5%', [u'', u'Выполнено'], CReportBase.AlignLeft),
            ('13,5%', [u'', u'Актив'], CReportBase.AlignLeft),
            ('13,5%', [u'На дому', u'Всего'], CReportBase.AlignLeft),
            ('13,5%', [u'', u'Выполнено'], CReportBase.AlignLeft),
            ('13,5%', [u'', u'Актив'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 3)
        table.mergeCells(0, 5, 1, 3)

        number = [1]
        allTotal = [u'Итого', 0, 0, 0, 0, 0, 0]
        formatBold = QtGui.QTextCharFormat()
        formatBold.setFontWeight(QtGui.QFont.Bold)

        def continueTable(specialityName, writtenFromZhos):
            query = selectData(_params)
            self.setQueryText(forceString(query.lastQuery()))
            self.parseQueryInfo(query, writtenFromZhos)
            for key in self.doctorsDict.keys():
                d = True
                x = 1
                for val in self.doctorsDict[key][1:]:
                    if val:
                        d = False
                    x += 1
                if d:
                    self.doctorsDict.pop(key)
            i = table.addRow()
            table.setText(i,  0,  number[0])
            table.setText(i,  1,  specialityName,  formatBold)
            number[0] += 1
            total = [u'Итого (' + specialityName + u')', 0, 0, 0, 0, 0, 0]
            keys = self.doctorsDict.keys()
            keys.sort()
    #        for val in  self.doctorsDict.values():
            for k in keys:
                val = self.doctorsDict[k]
                i = table.addRow()
                table.setText(i, 0, number[0])
                for column in range(7):
                    table.setText(i, column+1, val[column])
                    if column:
                        if self.detailCallCentr:
                            if val[0] != u'Call-центр':
                                total[column]+= val[column]
                        else:
                            total[column]+= val[column]
                number[0] += 1
                if u'Call-центр' in val[0]:
                    if self.detailCallCentr:
                        cKeys = self.callCentrDict.keys()
                        cKeys.sort()
                        for cK in cKeys:
                            val = self.callCentrDict[cK]
                            i = table.addRow()
                            table.setText(i, 0, number[0])
                            for column in range(7):
                                table.setText(i, column+1, val[column])
                                if column:
                                    total[column]+= val[column]
                            number[0] += 1
            i = table.addRow()
            table.setText(i, 0, number[0])
            for column in range(7):
                table.setText(i, column+1, total[column],  formatBold)
                if column > 0:
                    allTotal[column] += total[column]
            self.doctorsDict.clear()
            self.callCentrDict.clear()
        
        if _params.get('isGroupBySpeciality', False):
            querySpec = selectData(_params, groupBySpeciality = True)
            while querySpec.next():
                record = querySpec.record()
                _params['specialityId'] = forceInt(record.value('specialityID'))
                specName = forceString(record.value('specName'))
                continueTable(specName, writtenFromZhos)
                number[0] += 1
        else:
            _params['specialityId'] = 0
            continueTable(u'Все специальности', writtenFromZhos)
        
        
        i = table.addRow()
        table.setText(i, 0, number[0])
        for column in range(7):
            table.setText(i, column+1, allTotal[column],  formatBold)
    
    def parseQueryInfo(self, query, writtenFromZhos):
        recordList = self.makeNeedfulDicts(query)
        for record in recordList:
            actionNote  = forceString(record.value('actionNote'))
            personId    = forceInt(record.value('id'))
            fromZhos    = forceRef(record.value('zhos'))
            name = None
            if not personId:
                name = self.getincognitoName(actionNote, writtenFromZhos, fromZhos)
                personId = 0
            if not name:
                name = formatName(record.value('lastName'),
                                  record.value('firstName'),
                                  record.value('patrName'))
            setPersonId = forceRef(record.value('setPerson_id'))
            key = name + '%d' % personId
            
            afore = self.doctorsDict.get(key, None)
            if afore:
                self.addInfo(record, key)
            else:
                self.doctorsDict[key] = [name]+([0]*6)
                self.addInfo(record, key)

    def getincognitoName(self, actionNote, writtenFromZhos, fromZhos):
        actionNoteLowerCase = actionNote.lower()
        if u'инфомат' in actionNoteLowerCase:
            name = u'Инфомат'
        elif (u'call-центр' in actionNoteLowerCase) or (u'callcenter' in actionNoteLowerCase) or (writtenFromZhos and fromZhos):
            name = u'Call-центр'
        elif (u'запись через веб-регистратуру' in actionNoteLowerCase) or \
             (u'iVista Web Medical Service' in actionNote) or \
             (u'ЗАПИСЬ ОСУЩЕСТВЛЕНА ЧЕРЕЗ СИСТЕМУ "НЕТРИКА"' in actionNote) or \
                (u'Записано через РФ ЕГИСЗ' in actionNote):
            name = u'Интернет'
        else:
            return None
        return name

    def addInfo(self, record, key):
        detailCallCentr = self.detailCallCentr
        callCentrUser   = None
        personId            = forceInt(record.value('id'))
#        if not personId:
#            personId = self.getincognitoName(forceString(record.value('actionNote')))
        actionType          = forceString(record.value('ambOrHome'))
        executer            = forceRef(record.value('executer'))
        directionDateAction = forceDate(record.value('directionDate'))
        personSpecialyty    = forceRef(record.value('personSpecialyty'))
        clientId            = forceRef(record.value('client_id'))
        if actionType == 'amb':
            column = 1
        elif actionType == 'home':
            column = 4
        else:
            return
        self.doctorsDict[key][column] += 1
        if u'Call-центр' in key:
            if detailCallCentr:
                note = forceString(record.value('actionNote'))
                p = note.find(u'администратор')
                if p > -1:
                    callCentrUserTmp = note[p:].split(':')
                    if len(callCentrUserTmp) == 2:
                        callCentrUser = forceStringEx(callCentrUserTmp[1])
                        self.addCallCentrDetail(callCentrUser, column)
        visit, eventId = self.getVisit(directionDateAction, executer, personSpecialyty, self.recordVisitByDate, clientId)
        if visit:
            self.doctorsDict[key][column+1] += 1
            if detailCallCentr:
                self.addCallCentrDetail(callCentrUser, column+1)
        if executer == personId:
            column += 2
            self.doctorsDict[key][column] += 1
            if detailCallCentr:
                self.addCallCentrDetail(callCentrUser, column)

    def addCallCentrDetail(self, callCentrUser, column):
        if callCentrUser:
            nameCallCentr = u'Call-центр: '+callCentrUser
            value = self.callCentrDict.get(nameCallCentr)
            if value:
                self.callCentrDict[nameCallCentr][column] += 1
            else:
                self.callCentrDict[nameCallCentr] = [nameCallCentr]+([0]*6)
                self.callCentrDict[nameCallCentr][column] += 1



class CPreRecordUsersEx(CPreRecordUsers):
    def exec_(self):
        CPreRecordUsers.exec_(self)

    def getSetupDialog(self, parent):
        result = CPreRecordUsersSetupDialog(parent)
        result.setTitle(self.title())
        return result


class CPreRecordUsersSetupDialog(QtGui.QDialog, Ui_PreRecordUsersSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.chkWrittenFromZhos.setVisible(True)
        self.chkOnlyWithExternalQuota.setVisible(True)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        date = QtCore.QDate.currentDate().addDays(-3)
        self.edtBegDate.setDate(params.get('begDate', firstMonthDay(date)))
        self.edtEndDate.setDate(params.get('endDate', lastMonthDay(date)))
        self.edtBegDateRecord.setDate(params.get('begDateBeforeRecord', firstMonthDay(date)))
        self.edtEndDateRecord.setDate(params.get('endDateBeforeRecord', lastMonthDay(date)))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkIsGroupBySpeciality.setChecked(params.get('isGroupBySpeciality', False))
        self.chkWrittenFromZhos.setChecked(params.get('writtenFromZhos', False))
        self.chkOnlyWithExternalQuota.setChecked(params.get('onlyWithExternalQuota', False))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['begDateBeforeRecord'] = self.edtBegDateRecord.date()
        result['endDateBeforeRecord'] = self.edtEndDateRecord.date()
        result['chkPeriodRecord'] = self.chkPeriodRecord.isChecked()
        result['chkPeriodBeforeRecord'] = self.chkPeriodBeforeRecord.isChecked()
        chkOrgStructure = self.chkOrgStructure.isChecked()
        result['chkOrgStructure'] = chkOrgStructure
        if chkOrgStructure:
            result['orgStructureId'] = self.cmbOrgStructure.value()
            result['personId'] = self.cmbPerson.value()
        result['detailCallCentr'] = self.chkDetailCallCentr.isChecked()
        result['showWithoutOverTime'] = self.chkShowWithoutOverTime.isChecked()
        result['ignoreRehabilitation'] = self.chkIgnoreRehabilitation.isChecked()
        result['isGroupBySpeciality'] = self.chkIsGroupBySpeciality.isChecked()
        result['writtenFromZhos'] = self.chkWrittenFromZhos.isChecked()
        result['onlyWithExternalQuota'] = self.chkOnlyWithExternalQuota.isChecked()
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
