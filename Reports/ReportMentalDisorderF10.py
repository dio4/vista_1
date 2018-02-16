# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from copy                   import deepcopy

from PyQt4 import QtCore, QtGui

from library.crbcombobox                import CRBComboBox
from Events.Utils                       import getWorkEventTypeFilter
from library.Utils                      import forceBool, forceInt, forceRef, forceString, getVal
from Orgs.Utils                         import getOrganisationInfo
from Reports.Report                     import CReport
from Reports.ReportBase                 import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Ui_ReportMentalDisorderSetup       import Ui_ReportMentalDisorderSetupDialog

def selectData(params, firstDiscovered = False):
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventTypePurposeId = params.get('purposeId', None)
    eventTypeId = params.get('eventTypeId', None)
    personId = params.get('personId', None)
    orgId = params.get('orgId', None)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)

    db = QtGui.qApp.db

    stmt = u'''
    SELECT DISTINCT
        Client.id as clientId,
        age(Client.birthDate, Event.setDate) as clientAge,
        isClientVillager(Client.id) as isVillager,
        Client.sex,
        IF(rbAttachType.name LIKE '%%Д%%', 1, IF(rbAttachType.name LIKE 'К%%', 2, 0)) AS attachType,
        Diagnosis.MKB

    FROM
        Client
        INNER JOIN Event ON Event.client_id = Client.id AND Event.deleted = 0 AND Client.deleted = 0
        INNER JOIN Diagnostic ON Diagnostic.event_id = Event.id AND Diagnostic.deleted = 0
        INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0
        INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.deleted = 0
        LEFT JOIN rbDiseaseCharacter ON Diagnostic.character_id = rbDiseaseCharacter.id
        LEFT JOIN ClientAttach ON ClientAttach.client_id = Client.id AND ClientAttach.deleted = 0 AND ClientAttach.endDate IS NULL
        LEFT JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id
    WHERE %s
    '''

    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableDiagnosis = db.table('Diagnosis')
    cond = [tableEvent['setDate'].dateGe(begDate),
            tableEvent['execDate'].dateLe(endDate)]
    cond.append('''NOT EXISTS (SELECT * FROM ClientAttach ca INNER JOIN rbAttachType at ON at.id = ca.attachType_id AND ca.deleted = 0 WHERE at.code IN ('7', '8') AND ca.client_id = Client.id AND ca.begDate < %s)''' % begDate.toString(QtCore.Qt.ISODate))
    if firstDiscovered:
        cond.append(tableDiagnosis['setDate'].dateGe(begDate))
        cond.append(tableDiagnosis['setDate'].dateLe(endDate))

    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventTypePurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventTypePurposeId))

    if personId:
        cond.append(tableEvent['execPerson_id'].eq(personId))
    if orgId:
        cond.append(tableEvent['org_id'].eq(orgId))
    # Исходим из того, что соц. статусов может быть несколько
    if socStatusTypeId:
        cond.append(u'EXISTS (SELECT css.id FROM ClientSocStatus css WHERE css.client_id = Client.id AND css.deleted = 0 AND css.socStatusType_id = %s)' % socStatusTypeId)
    elif socStatusClassId:
        cond.append(u'EXISTS (SELECT css.id FROM ClientSocStatus css WHERE css.client_id = Client.id AND css.deleted = 0 AND css.socStatusClass_id = %s)' % socStatusClassId)

    return db.query(stmt % db.joinAnd(cond))


class CReportMentalDisorderF10(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Число заболеваний психическими расстройствами, зарегистрированными уреждением.')
        self.processedEvents = []
        self.deathEventResults = []

    def getSetupDialog(self, parent):
        result = CReportMentalDisorderSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def processRow(self, row, record):
        def processRowInt(baseCol):
            row[baseCol] += 1
            if sex == 2:
                row[baseCol+1] += 1
            if age <= 14:
                row[baseCol+2] += 1
            elif age <= 17:
                row[baseCol+3] += 1
            elif age <= 19:
                row[baseCol+4] += 1
            elif age <= 39:
                row[baseCol+5] += 1
            elif age <= 59:
                row[baseCol+6] += 1
            else:
                row[baseCol+7] += 1
            if attachType == 1:
                row[baseCol+8] += 1
            elif attachType == 2:
                row[baseCol+9] += 1


        sex = forceInt(record.value('sex'))
        age = forceInt(record.value('clientAge'))
        clientId = forceRef(record.value('clientId'))
        isVillager = forceBool(record.value('isVillager'))
        attachType = forceInt(record.value('attachType'))
        processRowInt(3)
        if isVillager:
            processRowInt(13)

    def processRecord(self, record, firstDiscovered = False):
        MKB = forceString(record.value('MKB'))
        resultSet = self.firstDiscoveredResultSet if firstDiscovered else self.resultSet
        for (i, row) in enumerate(resultSet):
            if MKBinString(MKB, row[1]):
                self.processRow(row, record)

    def build(self, params):
        self.processedEvents = []
        self.resultSet = [
            [u'Психические растройства - всего', u'F00-F09, F20-F99', u'1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Психозы и состояния слабоумия', u'', u'2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  в том числе:\n  органические психозы и (или) слабоумие', u'F00-F05, F06, F09', u'3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    из них:\n    сосудистая деменция', u'F01', u'4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    др. формы старческого слабоумия', u'F00, F02.0, F02.2, F02.3, F03', u'5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    психозы и (или) слабоумие вследствие эпилепсии', u'F02.8, F04.2, F05.2, F06', u'6', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  шизофрения', u'F20', u'7', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  шизотипические расстройства', u'F21', u'8', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  шизоаффективные психозы, аффективные психозы с неконгруентным аффекту бредом', u'F25, F30-F39', u'9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  острые и преходящие неорганические психозы', u'F23, F24', u'10', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  хронические неорганические психозы, детские психозы, неуточненные психот. рас-ва', u'F22, F28, F29, F84.0-F84.4, F99.1', u'11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  аффективные психозы', u'F30-F39', u'12', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    из них биполярные расстройства', u'F31.23, F31.28, F31.53, F31.58', u'13', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Психические рас-ва непсихотического характера', u'', u'14', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  в том числе:\n  органические непсихотические расстройства', u'F06, F07', u'15', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    в т.ч. обусловленные эпилепсией', u'F06, F07', u'16', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  аффективные непсихотические расстройства', u'F30-F39', u'17', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'    из них биполярные расстройства', u'F31.0, F31.1, F31.3, F31.4, F31.6-F31.9', u'18', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  невротические, связанные со стрессом и соматоформные расстройства', u'F40-F48', u'19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  другие непсихотические расстройства, поведенческие расстройства детского и подросткового возраста, неуточненные непсихотические расстойства', u'F50-F59, F80-F83, F84.5, F90-F98, F99.2-F99.9', u'20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  расстройства зрелой личности и поведения у взрослых', u'F60-F69', u'21', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Умственная отсталость - всего', u'F70-F79', u'22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'  в том числе:\n  легкая умственная отсталость', u'F70', u'23', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Из стр. 3 - психические расстройства, классифицированные в других рубриках МКБ-10', u'A52.1, A81.0, B22.0, G10-G40', u'24', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.firstDiscoveredResultSet = deepcopy(self.resultSet)

        query = selectData(params)
        queryParts = [forceString(query.lastQuery())]
        while query.next():
            self.processRecord(query.record())

        for i in range(3, len(self.resultSet[0])):
            self.resultSet[1][i] = self.resultSet[2][i] + self.resultSet[6][i] + self.resultSet[7][i] + self.resultSet[8][i] \
                                    + self.resultSet[9][i] + self.resultSet[10][i] + self.resultSet[11][i]
            self.resultSet[13][i] = self.resultSet[14][i] + self.resultSet[16][i] + self.resultSet[18][i] + self.resultSet[19][i] + self.resultSet[20][i]

        query = selectData(params, True)
        queryParts.append(forceString(query.lastQuery()))
        self.setQueryText(u'\n\n'.join(queryParts))
        while query.next():
            self.processRecord(query.record(), True)
        for i in range(3, len(self.resultSet[0])):
            self.firstDiscoveredResultSet[1][i] = self.firstDiscoveredResultSet[2][i] + self.firstDiscoveredResultSet[6][i] + self.firstDiscoveredResultSet[7][i] + self.firstDiscoveredResultSet[8][i] \
                                    + self.firstDiscoveredResultSet[9][i] + self.firstDiscoveredResultSet[10][i] + self.firstDiscoveredResultSet[11][i]
            self.firstDiscoveredResultSet[13][i] = self.firstDiscoveredResultSet[14][i] + self.firstDiscoveredResultSet[16][i] + self.firstDiscoveredResultSet[18][i] + self.firstDiscoveredResultSet[19][i] + self.firstDiscoveredResultSet[20][i]


        # now text
        bf = QtGui.QTextBlockFormat()
        bf.setAlignment(QtCore.Qt.AlignCenter)

        orgId = QtGui.qApp.currentOrgId()
        orgInfo = getOrganisationInfo(orgId)
        if not orgInfo:
            QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
        shortName = getVal(orgInfo, 'shortName', u'не задано')

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setBlockFormat(bf)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        #cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.insertText(u'\nЛПУ: ' + shortName)
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        self.drawDataTable(cursor)
        cursor.insertText('\n\n')
        self.drawDataTable(cursor, True)

        return doc

    def drawDataTable(self, cursor, firstDiscovered = False):
        boldFormat = QtGui.QTextCharFormat()
        boldFormat.setFontWeight(QtGui.QFont.Bold)

        plainFormat = QtGui.QTextCharFormat()

        if firstDiscovered:
            cursor.setBlockFormat(CReportBase.AlignCenter)
            cursor.setCharFormat(CReportBase.ReportSubTitle)
            cursor.insertText(u'Число заболеваний психическими расстройствами, зарегистрированных учреждением впервые в жизни')

            cursor.insertBlock()
        tableFormat = QtGui.QTextTableFormat()
        tableFormat.setBorder(0)
        tableFormat.setColumnWidthConstraints([QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50), QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 50)])
        table = cursor.insertTable(1, 2, tableFormat)

        c = table.cellAt(0, 0).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignLeft)
        c.setCharFormat(boldFormat)
        c.insertText(u'(3000)' if firstDiscovered else u'(2000)')

        c = table.cellAt(0, 1).lastCursorPosition()
        c.setBlockFormat(CReportBase.AlignRight)
        c.setCharFormat(QtGui.QTextCharFormat())
        c.insertText(u'Код по ОКЕИ: человек - ')

        cursor.movePosition(QtGui.QTextCursor.End)


        allClientsColumns = [
            ( '20%', [u'Наименование', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '15%', [u'Код по МКБ-Х (класс V, адаптированный для использования в РФ)', u'', u'', u'2'], CReportBase.AlignLeft),
            ( '5%',  [u'№ строки', u'', u'', u'3'], CReportBase.AlignCenter),
            ( '6%',  [u'Зарегистрировано больных в течение года', u'всего', u'', u'4'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'из них - женщин', u'', u'5'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'в том числе в возрасте (из гр. 4)', u'0-14 лет', u'6'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'15-17 лет', u'7'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'18-19 лет', u'8'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'20-39 лет', u'9'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'40-59 лет', u'10'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'60 лет и старше', u'11'], CReportBase.AlignCenter),
            ( '6%',  [u'Из общего числа больных (гр. 4) наблюдаются и получают конс- лечебную помощь по сост. на конец года', u'', u'диспансерные больные', u'12'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'консультативные больные', u'13'], CReportBase.AlignCenter),
        ]

        villagerClientsColumns = [
            ( '20%', [u'Наименование', u'', u'', u'1'], CReportBase.AlignLeft),
            ( '15%', [u'Код по МКБ-Х (класс V, адаптированный для использования в РФ)', u'', u'', u'2'], CReportBase.AlignLeft),
            ( '5%',  [u'№ строки', u'', u'', u'3'], CReportBase.AlignCenter),
            ( '6%',  [u'Из общего числа больных (гр. 4) - сельских жителей', u'всего', u'', u'14'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'из них - женщин', u'', u'15'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'в том числе в возрасте (из гр. 14)', u'0-14 лет', u'16'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'15-17 лет', u'17'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'18-19 лет', u'18'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'20-39 лет', u'19'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'40-59 лет', u'20'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'60 лет и старше', u'21'], CReportBase.AlignCenter),
            ( '6%',  [u'Из общего числа больных - сельски жителей (гр. 14) наблюдаются и получают конс- лечебную помощь по сост. на конец года', u'', u'диспансерные больные', u'22'], CReportBase.AlignCenter),
            ( '6%',  [u'', u'', u'консультативные больные', u'23'], CReportBase.AlignCenter),
        ]

        subRowSize = 10                  # (Длина строки - 3 первых столбца)
        table = createTable(cursor, allClientsColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 8)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 1, 6)
        table.mergeCells(0, 11, 2, 2)

        resultSet = self.firstDiscoveredResultSet if firstDiscovered else self.resultSet
        for z in range(len(resultSet)):
            row = resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            for j in range(subRowSize):
                table.setText(i, 3 + j, row[3 + j])

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertText('\n')
        table = createTable(cursor, villagerClientsColumns)

        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 8)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 1, 6)
        table.mergeCells(0, 11, 2, 2)

        for z in range(len(resultSet)):
            row = resultSet[z]
            i = table.addRow()
            table.setText(i, 0, row[0])
            table.setText(i, 1, row[1])
            table.setText(i, 2, row[2])
            for j in range(subRowSize):
                table.setText(i, 3 + j, row[13 + j])

        cursor.movePosition(QtGui.QTextCursor.End)


class CReportMentalDisorderSetupDialog(QtGui.QDialog, Ui_ReportMentalDisorderSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        self.cmbEventPurpose.setValue(params.get('purposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbPerson.setValue(getVal(params, 'personId', None))
        self.cmbOrganisation.setValue(getVal(params, 'orgId', None))



    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        result['purposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['personId'] = self.cmbPerson.value()
        result['orgId'] = self.cmbOrganisation.value()

        return result

    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
        else:
            filter = getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)
