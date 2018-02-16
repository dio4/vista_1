# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceDate, forceRef, forceString, forceInt
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureFullName, getPersonInfo
from Reports.PreRecordUsers import CPreRecordUsersSetupDialog
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase

# ###########################################################################
# ###                     АЛГОРИТМ ОПИСАН В i3600                         ###
# ###           http://client.ivista.ru/view.php?id=3600#c13935           ###
# ###########################################################################


def selectData(params):
    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tableExecPerson = db.table('Person').alias('ExecPerson')
    tableAction = db.table('Action')
    tableAction = tableAction.alias('NeedAction')

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
    chkPeriodBeforeRecord = params.get('chkPeriodBeforeRecord', None)
    ignoreRehabilitation = params.get('ignoreRehabilitation', None)

    statusId = forceRef(QtGui.qApp.db.translate('rbDeferredQueueStatus', 'code', u'2', 'id'))

    cond = []
    if chkPeriodRecord:
        if begDate:
            cond.append(tableAction['createDatetime'].dateGe(begDate))
        if endDate:
            cond.append(tableAction['createDatetime'].dateLe(endDate))
    if chkPeriodBeforeRecord:
        if begDateRecord:
            cond.append(tableAction['directionDate'].dateGe(begDateRecord))
        if endDateRecord:
            cond.append(tableAction['directionDate'].dateLe(endDateRecord))
    if personId:
        cond.append(tableAction['person_id'].eq(personId))
    if chkOrgStructure:
        if orgStructureId:
            cond.append(tableExecPerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        else:
            if not personId:
                cond.append(tableExecPerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tableExecPerson['speciality_id'].eq(specialityId))
    if showWithoutOverTime:
        cond.append('APTime.value IS NOT NULL')
    if ignoreRehabilitation:
        cond.append(db.joinOr([tablePerson['orgStructure_id'].isNull(),
                               tablePerson['orgStructure_id'].notInlist(db.getIdList('OrgStructure', where=u'name LIKE "%реабилитац%"'))]))

    if params.get('onlyWithExternalQuota', False):
        cond.append(tableExecPerson['availableForExternal'].eq(1))

    stmt = '''
    SELECT
    Person.lastName AS lastName,
    Person.firstName AS firstName,
    Person.patrName AS patrName,
    Person.post_id AS setPersonPost,
    Person.speciality_id AS setPersonSpeciality,
    NeedAction.note AS note,
    ExecPerson.speciality_id AS execPersonSpeciality,
    DATE(NeedAction.directionDate) AS directionDate,
    ExecPerson.orgStructure_id as orgStructure,
    DeferredQueue.id as zhos,

    IF(EXISTS(
        SELECT
        *
        FROM
            Visit V
            INNER JOIN Event E ON E.`id` = V.`event_id`
            INNER JOIN Person P ON V.person_id = P.id
        WHERE
            (DATE(V.date) = DATE(NeedAction.directionDate))
            AND (E.client_id = Event.client_id)
            AND (E.deleted = 0)
            AND (V.deleted = 0)
            AND (P.speciality_id = ExecPerson.speciality_id)
    ), 1, 0) as visited

    FROM ActionProperty_Action
    LEFT JOIN ActionProperty ON ActionProperty.id = ActionProperty_Action.id
    LEFT JOIN Action ON Action.id = ActionProperty.action_id
    LEFT JOIN ActionType ON ActionType.id = Action.actionType_id
    LEFT JOIN Action AS NeedAction ON NeedAction.id = ActionProperty_Action.value
    LEFT JOIN Event ON Event.id = NeedAction.event_id
    LEFT JOIN Person ON Person.id = NeedAction.setPerson_id
    LEFT JOIN Person AS ExecPerson ON ExecPerson.id = NeedAction.person_id
    LEFT JOIN  ActionProperty AS APTimes ON APTimes.action_id = Action.id
                                    AND APTimes.type_id = (SELECT id
                                                            FROM ActionPropertyType AS APT
                                                            WHERE APT.name LIKE 'times' AND APT.actionType_id = ActionType.id
                                                            LIMIT 1)
    LEFT JOIN ActionProperty_Time AS APTime ON APTime.id = APTimes.id AND APTime.index = ActionProperty_Action.index
    LEFT JOIN DeferredQueue ON NeedAction.id = DeferredQueue.action_id AND DeferredQueue.status_id = %s
    WHERE
    ActionProperty_Action.value IS NOT NULL
    AND %s ORDER BY NeedAction.`directionDate`
    ''' % (statusId, db.joinAnd(cond))
    return db.query(stmt)


class CPreRecordReport(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.resultDict = {}
        self.setTitle(u'Предварительная запись')
        self.orgStructureCache = {}
        self.specialityCache = {}
        self.postCache = {}
        self.resume = [0] * 8
        self.visitsResume = [0] * 8

    def getSetupDialog(self, parent):
        result = CPreRecordUsersSetupDialog(parent)
        result.setTitle(self.title())
        result.chkWrittenFromZhos.setVisible(True)
        result.chkOnlyWithExternalQuota.setVisible(True)
        return result

    def dumpParams(self, cursor, params):

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' c ' + forceString(begDate)
            if endDate:
                result += u' по ' + forceString(endDate)
            return result

        description = []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begDateBeforeRecord = params.get('begDateBeforeRecord', QtCore.QDate())
        endDateBeforeRecord = params.get('endDateBeforeRecord', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        # specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        chkPeriodRecord = params.get('chkPeriodRecord', None)
        chkPeriodBeforeRecord = params.get('chkPeriodBeforeRecord', None)
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
        if personId:
            personInfo = getPersonInfo(personId)
            description.append(u'врач: ' + personInfo['shortName'] + ', ' + personInfo['specialityName'])
        description.append(u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        columns = [('100%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def build(self, params):
        writtenFromZhos = params.get('writtenFromZhos')
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
        self.makeTable(cursor, doc, query, writtenFromZhos)

        return doc

    # TODO: atronah: реализовать в CReport метод addColumn() для инициализации инфы о таблице.
    def makeTable(self, cursor, doc, query, writtenFromZhos):
        tableColumns = [
            ('10%', [u'Поликлиническое отделение', u''], CReportBase.AlignLeft),
            ('10%', [u'Дата', u''], CReportBase.AlignLeft),
            ('10%', [u'Всего записано', u'Центр'], CReportBase.AlignCenter),
            ('10%', [u'', u'Регистратура'], CReportBase.AlignCenter),
            ('10%', [u'', u'Рабочее место врача'], CReportBase.AlignRight),
            ('10%', [u'', u'Инфомат'], CReportBase.AlignRight),
            ('10%', [u'', u'Интернет'], CReportBase.AlignRight),
            ('10%', [u'Центр, в том числе', u'Всего записано'], CReportBase.AlignRight),
            ('10%', [u'', u'Врачи-специалисты'], CReportBase.AlignRight),
            ('10%', [u'', u'Терапевты'], CReportBase.AlignRight)
        ]

        table = createTable(cursor, tableColumns)

        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 1, 5)
        table.mergeCells(0, 7, 1, 3)

        self.parseQueryInfo(query, writtenFromZhos)

        formatBold = QtGui.QTextCharFormat()
        formatBold.setFontWeight(QtGui.QFont.Bold)
        for key in sorted(self.resultDict.iterkeys()):
            first = True
            orgStruct = self.resultDict[key]
            osResume = orgStruct.pop(u'resume')
            dates = orgStruct.keys()
            dates.sort()
            for d in dates:
                row = orgStruct[d]
                i = table.addRow()
                if first:
                    table.setText(i, 0, key, formatBold)
                    first = False
                table.setText(i, 1, d.strftime('%d.%m.%Y'))
                for col in xrange(8):
                    table.setText(i, col + 2, row[col])
            i = table.addRow()
            table.setText(i, 0, u'Итого:', formatBold)
            for col in range(0, 8):
                table.setText(i, col + 2, osResume[col], formatBold)
        i = table.addRow()
        table.setText(i, 0, u'Итого пришло:', formatBold)
        for col in range(0, 8):
            table.setText(i, col + 2, self.visitsResume[col], formatBold)
        i = table.addRow()
        table.setText(i, 0, u'Итого по ЛПУ:', formatBold)
        for col in range(0, 8):
            table.setText(i, col + 2, self.resume[col], formatBold)

    def getPostName(self, postId):
        name = self.postCache.get(postId, None)
        if not name:
            db = QtGui.qApp.db
            name = forceString(db.translate('rbPost', 'id', postId, 'name')).lower()
            self.postCache[postId] = name
        return name

    def getSpecialityName(self, specId):
        name = self.specialityCache.get(specId, None)
        if not name:
            db = QtGui.qApp.db
            name = forceString(db.translate('rbSpeciality', 'id', specId, 'name')).lower()
            self.specialityCache[specId] = name
        return name

    def getOrgStructureName(self, orgStructureId):
        name = self.orgStructureCache.get(orgStructureId, None)
        if not name:
            name = getOrgStructureFullName(orgStructureId)
            self.orgStructureCache[orgStructureId] = name
        return name

    def parseQueryInfo(self, query, writtenFromZhos):
        self.resultDict.clear()
        self.resume = [0] * 8
        self.visitsResume = [0] * 8
        while query.next():
            record = query.record()

            # translate record values to python objects
            actionNote = forceString(record.value('note')).lower()
            personLastName = forceString(record.value('lastName')).lower()
            firstName = forceString(record.value('lastName'))
            patrName = forceString(record.value('patrName'))
            orgStructure = forceRef(record.value('orgStructure'))
            directionDate = forceDate(record.value('directionDate')).toPyDate()
            personPostId = forceRef(record.value('setPersonPost'))
            personSpecialityId = forceRef(record.value('setPersonSpeciality'))
            execPersonSpecialityId = forceRef(record.value('execPersonSpeciality'))
            fromZhos = forceRef(record.value('zhos'))
            visited = forceInt(record.value('visited'))

            # Get all used names from cache
            if personPostId:
                postName = self.getPostName(personPostId)
            else:
                postName = ''

            if execPersonSpecialityId:
                execPersonSpecialityName = self.getSpecialityName(execPersonSpecialityId)
            else:
                execPersonSpecialityName = ''

            if orgStructure:
                orgStructureName = self.getOrgStructureName(orgStructure)
            else:
                orgStructureName = u'Не определено'

            # Find or initialize working row
            if not orgStructureName in self.resultDict:
                self.resultDict[orgStructureName] = {u'resume': [0] * 8}
            byDates = self.resultDict[orgStructureName]
            if not directionDate in byDates:
                byDates[directionDate] = [0] * 8
            resultSet = byDates[directionDate]
            orgStructureSet = byDates[u'resume']
            # Update working row
            if (u'call-центр' in actionNote) or (u'callcenter' in actionNote) or \
               (u'оператор колл-центра' in personLastName) or (u'call-центр' in personLastName) or \
               (u'менеджер колл-центра' in postName) or (writtenFromZhos and fromZhos):
                resultSet[0] += 1
                resultSet[5] += 1
                orgStructureSet[0] += 1
                orgStructureSet[5] += 1
                self.resume[0] += 1
                self.resume[5] += 1
                self.visitsResume[0] += 1 if visited else 0
                self.visitsResume[5] += 1 if visited else 0
                if (u'терапевт' in execPersonSpecialityName) or (u'общая практика' in execPersonSpecialityName) or (
                    u'педиатр' in execPersonSpecialityName):
                    resultSet[7] += 1
                    orgStructureSet[7] += 1
                    self.resume[7] += 1
                    self.visitsResume[7] += 1 if visited else 0
                elif execPersonSpecialityId:
                    resultSet[6] += 1
                    orgStructureSet[6] += 1
                    self.resume[6] += 1
                    self.visitsResume[6] += 1 if visited else 0
            elif u'инфомат' in actionNote:
                resultSet[3] += 1
                orgStructureSet[3] += 1
                self.resume[3] += 1
                self.visitsResume[3] += 1 if visited else 0
            elif (u'запись через веб-регистратуру' in actionNote) or \
                 (u'e-mail' in actionNote) or \
                 (u'ivista web medical service' in actionNote) or \
                 (u'апись осуществлена через систему "нетрика"' in actionNote) or \
                 not (personLastName or firstName or patrName or personPostId or personSpecialityId):
                resultSet[4] += 1
                orgStructureSet[4] += 1
                self.resume[4] += 1
                self.visitsResume[4] += 1 if visited else 0
            elif u'врач' in postName:
                resultSet[2] += 1
                orgStructureSet[2] += 1
                self.resume[2] += 1
                self.visitsResume[2] += 1 if visited else 0
            else:
                resultSet[1] += 1
                orgStructureSet[1] += 1
                self.resume[1] += 1
                self.visitsResume[1] += 1 if visited else 0
