# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils               import getWorkEventTypeFilter
from library.database           import addDateInRange
from library.Utils              import forceBool, forceDate, forceInt, forceRef, forceString, pyDate
from Orgs.OrgStructComboBoxes   import COrgStructureModel
from Orgs.Utils                 import getOrgStructureDescendants
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase

from Ui_ReportF39ForPNDSetup import Ui_ReportF39SetupDialog

def selectData(begDate, endDate, eventPurposeIds, eventTypeId, orgStructureId, personId, rowGrouping, visitHospital, sex, ageFrom, ageTo, visitDisp, ambVisits, visitNurse, combine):
    stmt=u"""
SELECT
    COUNT(*) AS cnt,
    %s AS rowKey,
    IF(rbScene.code = '2' OR rbScene.code = '3',0,1)  AS atAmbulance,
    rbEventTypePurpose.code AS purpose,
    age(Client.birthDate, Visit.date) as clientAge,
    count(if(EventType.code = 14, Visit.id, NULL)) AS callVisit,
    count(ClientMonitoring.id) AS adn
    %s
FROM Visit
LEFT JOIN Event     ON Event.id = Visit.event_id
LEFT JOIN EventType ON EventType.id = Event.eventType_id
LEFT JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
LEFT JOIN Client    ON Client.id = Event.client_id
LEFT JOIN rbScene   ON rbScene.id = Visit.scene_id
LEFT JOIN ClientMonitoring ON ClientMonitoring.client_id AND ClientMonitoring.id = (SELECT max(clMonitoring.id)
                                                                                    FROM ClientMonitoring clMonitoring
                                                                                    INNER JOIN rbClientMonitoringKind ON clMonitoring.kind_id = rbClientMonitoringKind.id
                                                                                    WHERE (rbClientMonitoringKind.code = 'АДН' OR rbClientMonitoringKind.code = 'АПЛ') AND clMonitoring.client_id = Client.id)
%s
WHERE rbEventTypePurpose.code != \'0\'
AND Visit.deleted=0
AND Event.deleted=0
AND %s
GROUP BY
    rowKey,
    %s
    atAmbulance,
    purpose,
    clientAge
ORDER BY
  rowKey
    """
    db = QtGui.qApp.db
    tableVisit  = db.table('Visit')
    tableEvent  = db.table('Event')
    tableEventType = db.table('EventType')
    tablePerson = db.table('Person')
    tableClient = db.table('Client')
    cond = []
    addDateInRange(cond, tableVisit['date'], begDate, endDate)
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIds:
        cond.append(tableEventType['purpose_id'].inlist(eventPurposeIds))
    if personId:
        if ambVisits:
           personQuery = db.query(u'''SELECT Person.id
                          FROM Person
                          INNER JOIN rbSpeciality ON Person.speciality_id = rbSpeciality.id
                          WHERE Person.orgStructure_id = (SELECT pr.orgStructure_id
                                                          FROM Person pr
                                                          WHERE pr.id = %s)
                          AND rbSpeciality.code NOT IN ('000', '16', '2015', '2016', '2026')'''  % personId)
           if personQuery.next():
               record = personQuery.record()
               personDocId = forceRef(record.value('id'))
           cond.append(tableVisit['person_id'].inlist([personId, personDocId]))
        else:
           cond.append(tableVisit['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if visitNurse:
        nurseSpecialityIdList = db.getDistinctIdList('rbSpeciality', where='rbSpeciality.code IN (16, 2015, 2016)')
        cond.append(tablePerson['speciality_id'].notInlist(nurseSpecialityIdList))
    additionalSelect = ''
    additionalFrom = 'LEFT JOIN Person    ON Person.id = Visit.person_id'
    if rowGrouping == 6:
        groupField = 'Person.id'
        additionalFrom = u'''LEFT JOIN Person  ON Person.id = Visit.person_id  AND Person.speciality_id = (SELECT rbSpeciality.id
                                                                                                           FROM Person pr
                                                                                                           INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                                                                           WHERE rbSpeciality.code IN ('16', '2015', '2016') AND pr.id = Visit.person_id )'''
        if ambVisits:
            groupField = 'Person.id'

            additionalFrom = u'''
             LEFT JOIN Person tmpPerson ON tmpPerson.id = Visit.person_id AND if(rbScene.code = '2' OR rbScene.code = '3', tmpPerson.speciality_id = (SELECT rbSpeciality.id
                                                                                                           FROM Person pr
                                                                                                           INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                                                                           WHERE rbSpeciality.code IN ('16', '2015', '2016') AND pr.id = Visit.person_id),
                                                                                                           tmpPerson.speciality_id = (SELECT rbSpeciality.id
                                                                                                           FROM Person pr
                                                                                                           INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                                                                           INNER JOIN OrgStructure ON OrgStructure.id = pr.orgStructure_id
                                                                                                           WHERE rbSpeciality.code NOT IN ('000', '2026') AND pr.id = Visit.person_id AND OrgStructure.name LIKE '%%участок'))
            LEFT JOIN Person ON if(Person.id NOT IN (SELECT rbSpeciality.id
                                                     FROM Person pr
                                                     INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                         WHERE rbSpeciality.code NOT IN ('000', '16', '2015', '2016', '2026')),
                                   Person.id IN (SELECT pr.id
                                                 FROM Person pr
                                                 INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                 INNER JOIN OrgStructure ON OrgStructure.id = pr.orgStructure_id
                                                 WHERE rbSpeciality.code IN ('16', '2015', '2016') AND OrgStructure.id = tmpPerson.orgStructure_id),
                                   Person.id = tmpPerson.id)


                                                                                                           '''
    elif rowGrouping == 5:
        groupField = 'Person.id'
        additionalFrom = u'''LEFT JOIN Person  ON Person.id = Visit.person_id  AND Person.speciality_id = (SELECT rbSpeciality.id
                                                                                                           FROM Person pr
                                                                                                           INNER JOIN rbSpeciality ON rbSpeciality.id = pr.speciality_id
                                                                                                           WHERE rbSpeciality.code NOT IN ('000', '16', '2015', '2016', '2026') AND pr.id = Visit.person_id )'''
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
    if combine:
        additionalSelect += ', ClientAttach.orgStructure_id AS clientOrgStructure'
        attachTypeId = forceRef(db.translate('rbAttachType', 'id', '1', 'code'))
        additionalFrom += ' INNER JOIN ClientAttach ON ClientAttach.attachType_id = %s AND ClientAttach.client_id = Client.id AND ClientAttach.deleted = 0' % attachTypeId
    if not visitHospital:
        cond.append(u'''EventType.medicalAidType_id IS NULL OR (EventType.medicalAidType_id NOT IN (SELECT rbMedicalAidType.id from rbMedicalAidType where rbMedicalAidType.code IN (\'7\')))''')
    if not visitDisp:
        cond.append(u'''EventType.code NOT IN ('dd2013_1', 'dd2013_2', 'ДДВет')''')
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Visit.date >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Visit.date < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    #print stmt % (groupField, aditionalFrom, db.joinAnd(cond))
    return db.query(stmt % (groupField, additionalSelect, additionalFrom, db.joinAnd(cond), u'ClientAttach.orgStructure_id,' if combine else ''))


class CReportF39ForPND(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Форма 39 - ПНД')


    def getSetupDialog(self, parent):
        result = CReportF39SetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleForPND(True)
        result.setVisibled(False)
        result.chkDetailChildren.setVisible(True)
        result.chkCountCall.setEnabled(True)
        result.chkADN.setEnabled(True)
        result.addRowGrouping()
        return result

    def calculateReportData(self, record, reportData, rowKey, detailChildren):

        def fieldAge():
            if age <=14 and detailChildren:
                return 'from0to14'
            elif age >=15 and age <=17 and detailChildren:
                return 'from15to17'
            elif age<=17 and not detailChildren:
                    return 'from0to17'
            elif age>=60:
                return 'from60'
            else:
                return None

        cnt       = forceInt(record.value('cnt'))
        atAmbulance = forceBool(record.value('atAmbulance'))
        purpose   = forceString(record.value('purpose'))
        age       = forceInt(record.value('clientAge'))
        #financeId = forceInt(record.value('finance_id'))
        callVisit = forceInt(record.value('callVisit'))
        adn       = forceInt(record.value('adn'))

        row = reportData.get(rowKey, None)
        if not row:
            row = {'atAmbulance': {'count': 0,
                                   'countCure': 0,
                                   'from0to14': 0,
                                   'from15to17': 0,
                                   'from0to17': 0,
                                   'from60': 0,
                                   'from0to14Prophylaxy': 0,
                                   'from15to17Prophylaxy': 0,
                                   'from0to17Prophylaxy': 0,
                                   'from60Prophylaxy': 0,
                                   'adn': 0},
                   'atHome': {'count': 0,
                              'countCure': 0,
                              'from0to14': 0,
                              'from15to17': 0,
                              'from0to17': 0,
                              'from60':0,
                              'from0to14Prophylaxy': 0,
                              'from15to17Prophylaxy': 0,
                              'from0to17Prophylaxy': 0,
                              'from60Prophylaxy': 0,
                              'adn': 0},
                   'count': 0,
                   'call': 0,
                   'adn': 0}#[0]*rowSize
            reportData[rowKey] = row
        cure = purpose == '1'
        prophylaxy = purpose == '2'
        row['count'] += cnt
        if atAmbulance:
            row['atAmbulance']['count'] += cnt
            if cure:
                row['atAmbulance']['countCure'] += cnt
                field = fieldAge()
                if field:
                    row['atAmbulance'][field] += cnt
            if prophylaxy:
                field = fieldAge()
                if field:
                    row['atAmbulance'][field + 'Prophylaxy'] += cnt
            if adn:
                row['atAmbulance']['adn'] += adn
        else:
            row['atHome']['count'] += cnt
            if cure:
                row['atHome']['countCure'] += cnt
                field = fieldAge()
                if field:
                    row['atHome'][field] += cnt
            if prophylaxy:
                field = fieldAge()
                if field:
                    row['atHome'][field + 'Prophylaxy'] += cnt
            if adn:
                row['atHome']['adn'] += adn
        if callVisit:
            row['call'] += cnt
        if adn:
            row['adn'] += adn

    def calculateCount(self, record, reportData, forceKeyVal, detailChildren):
        rowKey    = forceKeyVal(record.value('rowKey'))
        cnt       = forceInt(record.value('cnt'))

        row = reportData.get(rowKey, None)
        if detailChildren:
            row[22] += cnt
        else:
            row[19] += cnt


    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat()):
        description = self.getDescription(params)
        columns = [ ('33%', [], CReportBase.AlignLeft), ('33%', [], CReportBase.AlignLeft), ('33%', [], CReportBase.AlignLeft) ]
        if len(description)%3==0:
            length=len(description)/3
        else:
            length=len(description)/3 + 1
        table = createTable(cursor, columns, headerRowCount=length, border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i/3, i % 3, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventPurposeIds = params.get('eventPurposeIds', [])
        eventTypeId = params.get('eventTypeId', None)
        orgStructureId = params.get('orgStructureId', None)
        personId = params.get('personId', None)
        rowGrouping = params.get('advancedRowGrouping', 0)
        detailChildren = params.get('detailChildren', False)
        visitHospital = params.get('visitHospital', False)
        visitDisp = params.get('visitDisp', False)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        self.adn = params.get('ADN', False)
        self.countCall = params.get('countCall', False)
        ambVisits = params.get('ambVisits', False)
        visitNurse = params.get('visitNurse', False)
        combine = params.get('combine', False)
        if rowGrouping == 6:
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyValToSort = None
            keyName = u'Мед.сестра'
        elif rowGrouping == 5:
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyValToSort = None
            keyName = u'Врач'
        elif rowGrouping == 4: # by post_id
            postId = None
            forceKeyVal = forceRef
            keyValToString = lambda postId: forceString(QtGui.qApp.db.translate('rbPost', 'id', postId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Должность'
        elif rowGrouping == 3: # by speciality_id
            specialityId = None
            forceKeyVal = forceRef
            keyValToString = lambda specialityId: forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Специальность'
        elif rowGrouping == 2: # by orgStructureId
            forceKeyVal = forceRef
            keyValToString = None
            keyValToSort = None
            keyName = u'Подразделение'
        elif rowGrouping == 1: # by personId
            forceKeyVal = forceRef
            keyValToString = lambda personId: forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name'))
            keyValToSort = keyValToString
            keyName = u'Персонал'
        else:
            forceKeyVal = lambda x: pyDate(forceDate(x))
            keyValToSort = None
            keyValToString = lambda x: forceString(QtCore.QDate(x))
            keyName = u'Дата'

        db = QtGui.qApp.db
        # financeNames   = []
        # financeIndexes = {}
        # for index, record in enumerate(db.getRecordList('rbFinance', 'id, name', '', 'code')):
        #     financeId = forceRef(record.value(0))
        #     financeName = forceString(record.value(1))
        #     financeIndexes[financeId] = index
        #     financeNames.append(financeName)
        # if not(financeNames):
        #     financeNames.append(u'не определено')
        # if not self.countCall:
        #     rowSize = 22 if detailChildren else 18
        # if self.countCall:
        #     rowSize = 23 if detailChildren else 19
        # if self.adn and self.countCall:
        #     rowSize = 24 if detailChildren else 20
        # if self.adn and not self.countCall:
        #     rowSize = 23 if detailChildren else 19
        query = selectData(begDate, endDate, eventPurposeIds, eventTypeId, orgStructureId, personId, rowGrouping, visitHospital, sex, ageFrom, ageTo, visitDisp, ambVisits, visitNurse, combine)
        reportData = {}
        #calculate = self.calculateReportDataIfDetailaChildren if detailChildren else self.calculateReportData
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            rowKey    = forceKeyVal(record.value('rowKey'))
            if combine:
                clientOrgStructure = forceString(db.translate('OrgStructure', 'id', forceString(record.value('clientOrgStructure')), 'name'))
                rowKey = keyValToString(rowKey) + ' ' + (clientOrgStructure if clientOrgStructure else u'у пациентов не указано подразделение прикрепления!')
            if rowKey:
                self.calculateReportData(record, reportData, rowKey, detailChildren)
        # if self.countCall:
        #     queryCountCall = selectDataCountCall(begDate, endDate, eventPurposeId, eventTypeId, orgStructureId, personId, rowGrouping, visitHospital, sex, ageFrom, ageTo, visitDisp, ambVisits)
        #     while queryCountCall.next():
        #         recordCountCall = queryCountCall.record()
        #         rowKey    = forceKeyVal(recordCountCall.value('rowKey'))
        #         if rowKey:
        #             self.calculateCount(recordCountCall, reportData, forceKeyVal, detailChildren)

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.TableTotal)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        self.orderColumn = ['atAmbulance', ['count', 'countCure', 'from60', 'from60Prophylaxy'] , 'atHome', ['count', 'countCure', 'from60', 'from60Prophylaxy'], 'count']

        tableColumns = [
            ( '10%', [keyName], CReportBase.AlignLeft),
            ( '5%', [u'Амбулаторно', u'все-\nго'         ], CReportBase.AlignRight),
            ( '5%', [u'',            u'по поводу заболеваний', u'все-\nго'], CReportBase.AlignRight),
            ( '5%', [u'',            u'', u'60 лет и ст.'], CReportBase.AlignRight),
            ( '5%', [u'',            u'',  u'60 лет и ст.'], CReportBase.AlignRight),
            ( '5%', [u'На дому',     u'все-\nго'         ], CReportBase.AlignRight),
            ( '5%', [u'',            u'по поводу заболеваний', u'все-\nго'], CReportBase.AlignRight),
            ( '5%', [u'',            u'',  u'60 лет и ст.'], CReportBase.AlignRight),
            ( '5%', [u'',            u'',  u'60 лет и ст.'], CReportBase.AlignRight),
            ( '5%', [u'Всего'], CReportBase.AlignRight)
            ]


        if detailChildren:
            tableColumns.insert(3,  ( '5%', [u'', u'',       u'0-14 лет'], CReportBase.AlignRight))
            tableColumns.insert(4,  ( '5%', [u'', u'',       u'15-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(6,  ( '5%', [u'', u'проф.',  u'0-14 лет'], CReportBase.AlignRight))
            tableColumns.insert(7,  ( '5%', [u'', u'',       u'15-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(11 if self.adn else 11,  ( '5%', [u'', u'',       u'0-14 лет'], CReportBase.AlignRight))
            tableColumns.insert(12 if self.adn else 12, ( '5%', [u'', u'',       u'15-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(14 if self.adn else 14, ( '5%', [u'', u'проф.',  u'0-14 лет'], CReportBase.AlignRight))
            tableColumns.insert(15 if self.adn else 15, ( '5%', [u'', u'',       u'15-17 лет'], CReportBase.AlignRight),)
            for index in xrange(3):
                if index + 1 == 2:
                    continue
                self.orderColumn[index + 1].insert(2, 'from0to14')
                self.orderColumn[index + 1].insert(3, 'from15to17')
                self.orderColumn[index + 1].insert(5, 'from0to14Prophylaxy')
                self.orderColumn[index + 1].insert(6, 'from15to17Prophylaxy')

            if self.countCall:
                tableColumns.append(( '5%', [u'вызовов', u'',  u''], CReportBase.AlignRight))
                self.orderColumn.append('call')
            if self.adn:
                tableColumns.insert( 9, ( '5%', [u'', u'АДН/АПЛ',  u''], CReportBase.AlignRight))
                tableColumns.insert(18, ( '5%', [u'', u'АДН/АПЛ',  u''], CReportBase.AlignRight))
                tableColumns.append(( '5%', [u'АДН/АПЛ', u'', u''], CReportBase.AlignRight))
                self.orderColumn[1].append('adn')
                self.orderColumn[3].append('adn')
                self.orderColumn.append('adn')

        else:
            tableColumns.insert(3,  ( '5%', [u'', u'', u'0-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(5, ( '5%', [u'', u'проф.',  u'0-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(9,  ( '5%', [u'', u'',  u'0-17 лет'], CReportBase.AlignRight))
            tableColumns.insert(11, ( '5%', [u'', u'проф.', u'0-17 лет'], CReportBase.AlignRight))
            for index in xrange(3):
                if index + 1 == 2:
                    continue
                self.orderColumn[index + 1].insert(2, 'from0to17')
                self.orderColumn[index + 1].insert(4, 'from0to17Prophylaxy')
            if self.countCall:
                tableColumns.append(( '5%', [u'вызовов', u'', u'', u''], CReportBase.AlignRight))
                self.orderColumn.append('call')
            if self.adn:
                tableColumns.insert( 7, ( '5%', [u'', u'АДН/АПЛ', u'', u''], CReportBase.AlignRight))
                tableColumns.insert( 14 if self.adn else 13, ( '5%', [u'', u'АДН/АПЛ', u'', u''], CReportBase.AlignRight))
                tableColumns.append(( '5%', [u'АДН/АПЛ', u'', u'', u''], CReportBase.AlignRight))
                self.orderColumn[1].append('adn')
                self.orderColumn[3].append('adn')
                self.orderColumn.append('adn')

        rowSize = len(tableColumns) - 1

        table = createTable(cursor, tableColumns)

        if detailChildren:
            self.mergeCellsIfDetailChildren(table)
        else:
            self.mergeCells(table)


#        prevSpecName = None
#        total = None
#        grandTotal = [0]*rowSize

        if rowGrouping == 2: # by orgStructureId
            self.genOrgStructureReport(table, reportData, rowSize, orgStructureId)
        else:
            keys = reportData.keys()
            if keyValToSort:
                keys.sort(key=keyValToSort)
            else:
                keys.sort()
            total = [0]*rowSize
            field = None
            for key in keys:
                i = table.addRow()
                table.setText(i, 0, key if combine else keyValToString(key))
                row = reportData[key]
                j = -1
                for column in self.orderColumn:
                    if column == 'atAmbulance' or column == 'atHome':
                        field = column
                        continue
                    if field:
                        for index in column:
                            j += 1
                            table.setText(i, j + 1, row[field][index])
                            total[j] += row[field][index]
                        field = None
                    else:
                        j += 1
                        table.setText(i, j + 1, row[column])
                        total[j] += row[column]
            i = table.addRow()
            table.setText(i, 0, u'всего', CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)
        return doc

    def mergeCellsIfDetailChildren(self, table):

         table.mergeCells(0, 0, 3, 1) # key
         table.mergeCells(0, 1, 1, 9 if self.adn else 8) # Амбулаторно
         table.mergeCells(1, 1, 2, 1) # всего
         #table.mergeCells(1, 2, 3, 1) # с.ж.
         table.mergeCells(1, 2, 1, 4) # в возрасте
         table.mergeCells(1, 6, 1, 3) # по забол.
         table.mergeCells(1, 10 if self.adn else 9, 2, 1) # всего
         table.mergeCells(0, 10 if self.adn else 9, 1, 9 if self.adn else 8)# профилактических
         table.mergeCells(1, 2, 1, 3) # 0-14
         table.mergeCells(1, 11 if self.adn else 10, 1, 4) # 15-17
         table.mergeCells(1, 15 if self.adn else 14, 1, 3) # <=1
         table.mergeCells(0, 19 if self.adn else 17, 3, 1) # >=60
         if self.adn:
            table.mergeCells(0, 20, 3, 1)
            table.mergeCells(1, 9, 2, 1)
            table.mergeCells(1, 18, 2, 1)
         if self.countCall:
            table.mergeCells(0, 21 if self.adn else 18, 3, 1)

    def mergeCells(self, table):
         table.mergeCells(0, 0, 3, 1)
         table.mergeCells(0, 1, 1, 7 if self.adn else 6)
         table.mergeCells(1, 1, 2, 1)
         table.mergeCells(1, 2, 1, 3)
         table.mergeCells(1, 3, 1, 3)
        #
         table.mergeCells(1, 4, 1, 5)
         table.mergeCells(0, 8 if self.adn else 7, 1, 7 if self.adn else 6)
         table.mergeCells(1, 8 if self.adn else 7, 2, 1)
        #
         table.mergeCells(1, 9 if self.adn else 8, 1, 3)
         table.mergeCells(1, 12 if self.adn else 11, 1, 2)
         table.mergeCells(0, 15 if self.adn else 13, 3, 1)
         table.mergeCells(1, 5, 1, 2)
         if self.adn:
            table.mergeCells(0, 16, 3, 1)
            table.mergeCells(1, 7, 2, 1)
            table.mergeCells(1, 14, 2, 1)
         if self.countCall:
            table.mergeCells(0, 17 if self.adn else 16, 3, 1)


    def genOrgStructureReport(self, table, reportData, rowSize, orgStructureId):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        index = model.findItemId(orgStructureId)
        if index:
            item = index.internalPointer()
        else:
            item = model.getRootItem()
        self.genOrgStructureReportForItem(table, reportData, item, rowSize, [0]*rowSize)


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize, total):
        i = table.addRow()
        if item.childCount() == 0:
            table.setText(i, 0, item.name())
            row = reportData.get(item.id(), None)
            if row:
                j = -1
                field = None
                for column in self.orderColumn:
                    if column == 'atAmbulance' or column == 'atHome':
                        field = column
                        continue
                    if field:
                        for index in column:
                            j += 1
                            table.setText(i, j + 1, row[field][index])
                            total[j] += row[field][index]
                        field = None
                    else:
                        j += 1
                        table.setText(i, j + 1, row[column])
                        total[j] += row[column]
            return row
        else:
            table.mergeCells(i,0, 1, rowSize+1)
            table.setText(i, 0, item.name(), CReportBase.TableHeader)
            row = reportData.get(item.id(), None)
            if row:
                i = table.addRow()
                table.setText(i, 0, '-', CReportBase.TableHeader)
                j = -1
                field = None
                for column in self.orderColumn:
                    if column == 'atAmbulance' or column == 'atHome':
                        field = column
                        continue
                    if field:
                        for index in column:
                            j += 1
                            table.setText(i, j + 1, row[field][index])
                            total[j] += row[field][index]
                        field = None
                    else:
                        j += 1
                        table.setText(i, j + 1, row[column])
                        total[j] += row[column]
            for subitem in item.items():
                self.genOrgStructureReportForItem(table, reportData, subitem, rowSize, total)
            i = table.addRow()
            table.setText(i, 0, u'всего по '+item.name(), CReportBase.TableTotal)
            for j in xrange(rowSize):
                table.setText(i, j+1, total[j], CReportBase.TableTotal)
            return total


class CReportF39SetupDialog(QtGui.QDialog, Ui_ReportF39SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbVisitPayStatus.setCurrentIndex(0)
        self.chkAmbVisits.setEnabled(True) if self.cmbRowGrouping.currentIndex() == 6 else self.chkAmbVisits.setEnabled(False)
        self.chkCombine.setEnabled(True) if self.cmbRowGrouping.currentIndex() == 6 else self.chkCombine.setEnabled(False)
        self.chkDetailChildren.setVisible(False)


    def setVisibleForPND(self, value):
        self.chkADN.setVisible(value)
        self.chkCountCall.setVisible(value)
        self.chkAmbVisits.setVisible(value)
        self.chkCombine.setVisible(value)
        self.chkVisitDisp.setVisible(not value)


    def setVisibled(self, value):
        self.lblVisitPayStatus.setVisible(value)
        self.cmbVisitPayStatus.setVisible(value)


    def addRowGrouping(self):
        self.cmbRowGrouping.setItemText(1, u'Персоналу')
        self.cmbRowGrouping.addItem(u'Врачам')
        self.cmbRowGrouping.addItem(u'Мед.сестрам')


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', []))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbRowGrouping.setCurrentIndex(params.get('advancedRowGrouping', 0))
        if self.cmbVisitPayStatus.isVisible():
            self.cmbVisitPayStatus.setCurrentIndex(params.get('visitPayStatus', 0))
        self.chkDetailChildren.setChecked(params.get('detailChildren', False))
        self.chkVisitHospital.setChecked(params.get('visitHospital', False))
        self.chkVisitDisp.setChecked(params.get('visitDisp', False))
        self.chkCountCall.setChecked(params.get('countCall', False))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.chkADN.setChecked(params.get('ADN', False))
        self.chkAmbVisits.setChecked(params.get('ambVisits', False))
        self.chkCombine.setChecked(params.get('combine', False))
        self.edtEventBegDatetime.setDateTime(params.get('eventBegDatetime', QtCore.QDateTime.currentDateTime()))
        self.edtEventEndDatetime.setDateTime(params.get('eventEndDatetime', QtCore.QDateTime.currentDateTime()))
        self.gbEventDatetimeParams.setChecked(params.get('isEventCreateParams', False))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeIds'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['advancedRowGrouping'] = self.cmbRowGrouping.currentIndex()
        if self.cmbVisitPayStatus.isVisible():
            result['visitPayStatus'] = self.cmbVisitPayStatus.currentIndex()
        result['detailChildren'] = self.chkDetailChildren.isChecked()
        result['visitHospital'] = self.chkVisitHospital.isChecked()
        result['visitDisp'] = self.chkVisitDisp.isChecked()
        result['countCall'] = self.chkCountCall.isChecked()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['ADN'] = self.chkADN.isChecked()
        result['ambVisits'] = self.chkAmbVisits.isChecked()
        result['combine'] = self.chkCombine.isChecked()
        result['isEventCreateParams'] = self.gbEventDatetimeParams.isChecked()
        result['eventBegDatetime'] = self.edtEventBegDatetime.dateTime()
        result['eventEndDatetime'] = self.edtEventEndDatetime.dateTime()
        return result


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbRowGrouping_currentIndexChanged(self, index):
        if self.cmbRowGrouping.currentIndex() == 6 or self.cmbRowGrouping.currentIndex() == 5:
            self.chkCombine.setEnabled(True)
            if self.cmbRowGrouping.currentIndex() == 6:
                self.chkAmbVisits.setEnabled(True)
        else:
            self.chkAmbVisits.setEnabled(False)
            self.chkCombine.setEnabled(False)
            self.chkAmbVisits.setChecked(False)
            self.chkCombine.setChecked(False)