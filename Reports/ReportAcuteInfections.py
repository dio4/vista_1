# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils import getWorkEventTypeFilter
from Orgs.Utils import getOrgStructureDescendants
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceBool, forceInt, forceString, toVariant
from library.database import addDateInRange


def selectData(MKBList, params):
#    stmt="""
#SELECT
#   MKB,
#   ageGroup,
#   sex,
#   COUNT(*) AS cnt
#   FROM (
#SELECT
#    Diagnosis.MKB AS MKB,
#    IF( ADDDATE(Client.birthDate, INTERVAL 18 YEAR)<=Diagnosis.setDate,
#        2,
#        IF ( ADDDATE(Client.birthDate, INTERVAL 15 YEAR)>Diagnosis.setDate,
#          0,
#          1)
#      ) AS ageGroup,
#    Client.sex AS sex
#FROM Diagnosis
#LEFT JOIN Client ON Client.id = Diagnosis.client_id
#LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnosis.diagnosisType_id%s
#WHERE %s
#) AS T
#GROUP BY MKB, ageGroup, sex
#ORDER BY MKB
#    """
    stmt="""
SELECT
   MKB,
   ageGroup,
   sex,
   COUNT(*) AS cnt
   FROM (
SELECT
    Diagnosis.MKB AS MKB,
    IF( ADDDATE(Client.birthDate, INTERVAL 18 YEAR)<=Diagnosis.setDate,
        2,
        IF ( ADDDATE(Client.birthDate, INTERVAL 15 YEAR)>Diagnosis.setDate,
          0,
          1)
      ) AS ageGroup,
    Client.sex AS sex
FROM %s
WHERE %s
) AS T
GROUP BY MKB, ageGroup, sex
ORDER BY MKB
    """
    
    registeredInPeriod = params.get('registeredInPeriod', False)
    chkCreateDate = params.get('chkCreateDate', False)
    createBegDate = params.get('createBegDate', QtCore.QDate())
    createEndDate = params.get('createEndDate', QtCore.QDate())
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    eventPurposeIdList = params.get('eventPurposeIdList', [])
    eventTypeId = params.get('eventTypeId', None)
    orgStructureId = params.get('orgStructureId', None)
    personId = params.get('personId', None)
    sex = params.get('sex', 0)
    ageFrom = params.get('ageFrom', 0)
    ageTo = params.get('ageTo', 150)
    socStatusClassId = params.get('socStatusClassId', None)
    socStatusTypeId = params.get('socStatusTypeId', None)
    accountAccomp = params.get('accountAccomp', False)
    locality = params.get('locality', False)
    visitEmergency = params.get('visitEmergency', False)
    specialityPerson = params.get('specialityId', None)
    hurtType = params.get('hurtType', None)
    
    db = QtGui.qApp.db
    tableDiagnosis  = db.table('Diagnosis')
    tableDiagnosisType = db.table('rbDiagnosisType')
    tableClient = db.table('Client')
    tableDiagnostic = db.table('Diagnostic')
    tablePerson = db.table('Person')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableAddressHouse = db.table('AddressHouse')
    
    queryTable = tableDiagnosis.leftJoin(tableClient, tableDiagnosis['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableDiagnosisType, tableDiagnosis['diagnosisType_id'].eq(tableDiagnosisType['id']))
    cond = []
    cond.append(tableDiagnosis['deleted'].eq(0))
    cond.append(tableDiagnosis['mod_id'].isNull())
    addDateInRange(cond, tableDiagnosis['setDate'], begDate, endDate)
    if chkCreateDate:
        addDateInRange(cond, tableDiagnosis['createDatetime'], createBegDate, createEndDate)
#    cond.append(db.joinOr([tableDiagnosis['setDate'].isNull(), tableDiagnosis['setDate'].le(endDate)]))
#    cond.append(tableDiagnosis['endDate'].ge(begDate))

    diagnosticQuery = tableDiagnostic
    diagnosticCond = [ tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']),
                       tableDiagnostic['deleted'].eq(0)
                     ]
    if registeredInPeriod:
        addDateInRange(diagnosticCond, tableDiagnostic['setDate'], begDate, endDate)
    if personId:
        diagnosticCond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        diagnosticQuery = diagnosticQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableDiagnostic['person_id']))
        diagnosticCond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))

    if specialityPerson and not personId:
        tableSpeciality = db.table('rbSpeciality')
        diagnosticQuery = diagnosticQuery.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tableDiagnostic['speciality_id']))
        diagnosticCond.append(tableSpeciality['id'].eq(specialityPerson))

    if hurtType:
        tableClientWorkHurt = db.table('ClientWork_Hurt')
        tableClientWork = db.table('ClientWork')
        diagnosticQuery = diagnosticQuery.leftJoin(tableClientWorkHurt, tableClientWorkHurt['master_id'].eq(tableClientWork['client_id'].eq(tableClient['id'])))
        diagnosticCond.append(tableClientWorkHurt['hurtType_id'].eq(hurtType))

    if eventTypeId or eventPurposeIdList or not visitEmergency:
        tableEvent = db.table('Event')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
    if eventPurposeIdList or not visitEmergency:
        tableEventType = db.table('EventType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        
    if eventTypeId:
        diagnosticCond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeIdList:
        diagnosticCond.append(tableEventType['purpose_id'].inlist(eventPurposeIdList))

    if not visitEmergency:
        tableMedicalAidType = db.table('rbMedicalAidType')
        diagnosticQuery = diagnosticQuery.leftJoin(tableMedicalAidType, tableMedicalAidType['id'].eq(tableEventType['medicalAidType_id']))
        diagnosticCond.append(db.joinOr([tableMedicalAidType['code'].isNull(), tableMedicalAidType['code'].ne('4')]))
        
    cond.append(db.existsStmt(diagnosticQuery, diagnosticCond))

    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('(Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR) OR Diagnosis.endDate IS NULL)'%ageFrom)
        cond.append('(Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1) OR Diagnosis.endDate IS NULL)'%(ageTo+1))
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
    MKBCond = []
    for MKB in MKBList:
        MKBCond.append( tableDiagnosis['MKB'].like(MKB+'%') )
    cond.append(db.joinOr(MKBCond))
    if not accountAccomp:
        cond.append(tableDiagnosisType['code'].inlist(['1', '2', '4']))

    if locality:
        # 1: горожане, isClientVillager == 0 или NULL
        # 2: сельские жители, isClientVillager == 1
        cond.append('IFNULL(isClientVillager(Client.id), 0) = %d' % (locality-1))
    
    filterAddress = params.get('isFilterAddress', False)
    if filterAddress:
        filterAddressType = params.get('filterAddressType', 0)
        filterAddressCity = params.get('filterAddressCity', None)
        filterAddressStreet = params.get('filterAddressStreet', None)
        filterAddressHouse = params.get('filterAddressHouse', u'')
        filterAddressCorpus = params.get('filterAddressCorpus', u'')
        filterAddressFlat = params.get('filterAddressFlat', u'')
        queryTable = queryTable.leftJoin(tableClientAddress, tableClient['id'].eq(tableClientAddress['client_id']))
        cond.append(tableClientAddress['type'].eq(filterAddressType))
        cond.append(db.joinOr([tableClientAddress['id'].isNull(), tableClientAddress['deleted'].eq(0)]))
        if filterAddressCity or filterAddressStreet or filterAddressHouse or filterAddressCorpus or filterAddressFlat:
            queryTable = queryTable.leftJoin(tableAddress, tableClientAddress['address_id'].eq(tableAddress['id']))
            queryTable = queryTable.leftJoin(tableAddressHouse, tableAddress['house_id'].eq(tableAddressHouse['id']))
            cond.append(db.joinOr([tableAddress['id'].isNull(), tableAddress['deleted'].eq(0)]))
            cond.append(db.joinOr([tableAddressHouse['id'].isNull(), tableAddressHouse['deleted'].eq(0)]))
        if filterAddressCity:
            cond.append(tableAddressHouse['KLADRCode'].like(filterAddressCity))
        if filterAddressStreet:
            cond.append(tableAddressHouse['KLADRStreetCode'].like(filterAddressStreet))
        if filterAddressHouse:
            cond.append(tableAddressHouse['number'].eq(filterAddressHouse))
        if filterAddressCorpus:
            cond.append(tableAddressHouse['corpus'].eq(filterAddressCorpus))
        if filterAddressFlat:
            cond.append(tableAddress['flat'].eq(filterAddressFlat))


    return db.query(stmt % (db.getTableName(queryTable), db.joinAnd(cond)))


class CReportAcuteInfections(CReport):
    rowTypes = [ (u'J10', u'Грипп, вызванный идентифицированным вирусом гриппа' ),
                 (u'J11', u'Грипп, вирус не идентифицирован' ),
                 (u'J03', u'Ангины'),
                 (u'J06', u'ОРВИ'  ),
                 (u'J18', u'Пневмония'),
                 (u'J20', u'Бронхит'),
               ]

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка по выявленным острым инфекционным заболеваниям')


    def getSetupDialog(self, parent):
        result = CReportAcuteInfectionsSetupDialog(parent)
        result.setAccountAccompEnabled(True)
        result.setCreateDateEnabled(True)
        result.setTitle(self.title())
        result.adjustSize()
        return result


    def build(self, params):

        reportRowSize = 9

        mapMKBToTypeIndex = {}
        for index, rowType in enumerate(self.rowTypes):
            mapMKBToTypeIndex[rowType[0]] = index

        reportData = {}
        MKBList = []
        query = selectData([t[0] for t in self.rowTypes], params)
        self.setQueryText(forceString(query.lastQuery()))

        while query.next() :
            record    = query.record()
            cnt       = forceInt(record.value('cnt'))
            MKB       = forceString(record.value('MKB'))
            sex       = forceInt(record.value('sex'))
            ageGroup  = forceInt(record.value('ageGroup'))

            reportRow = reportData.get(MKB, None)
            if not reportRow:
                reportRow = [0]*reportRowSize
                reportData[MKB] = reportRow
                MKBList.append(MKB)

            if sex in [1, 2]:
                reportRow[ageGroup*2+sex-1] += cnt
                reportRow[5+sex] += cnt
                reportRow[8] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        if params.get('isFilterAddress', False):
            self.dumpParamsAdress(cursor, params)
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('15%', [u'диагноз',             u''], CReportBase.AlignLeft),
            ('8%', [u'дети',                u'М'], CReportBase.AlignRight),
            ('8%', [u'',                    u'Ж'], CReportBase.AlignRight),
            ('8%', [u'подростки',           u'М'], CReportBase.AlignRight),
            ('8%', [u'',                    u'Ж'], CReportBase.AlignRight),
            ('8%', [u'взрослые',            u'М'], CReportBase.AlignRight),
            ('8%', [u'',                    u'Ж'], CReportBase.AlignRight),
            ('8%', [u'всего',               u'М'], CReportBase.AlignRight),
            ('8%', [u'',                    u'Ж'], CReportBase.AlignRight),
            ('8%', [u'всего',               u''],  CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 1, 2)
        table.mergeCells(0, 3, 1, 2)
        table.mergeCells(0, 5, 1, 2)
        table.mergeCells(0, 7, 1, 2)
        table.mergeCells(0, 9, 2, 1)

        prevTypeIndex = None
        total = [0]*reportRowSize
        for MKB in MKBList:
            typeIndex = mapMKBToTypeIndex[MKB[:3]]
            if typeIndex != prevTypeIndex:
                if prevTypeIndex != None:
                    self.produceTotalLine(table, u'всего', total)
                i = table.addRow()
                table.mergeCells(i, 0, 1, reportRowSize+1)
                table.setText(i, 0, self.rowTypes[typeIndex][1])
                prevTypeIndex = typeIndex
                total = [0]*reportRowSize
            row = reportData[MKB]
            i = table.addRow()
            table.setText(i, 0, MKB)
            for j in xrange(reportRowSize):
                table.setText(i, j+1, row[j])
                total[j] += row[j]
        if prevTypeIndex != None:
            self.produceTotalLine(table, u'всего', total)
        return doc


    def produceTotalLine(self, table, title, total):
        i = table.addRow()
        table.setText(i, 0, title, CReportBase.TableTotal)
        for j in xrange(len(total)):
            table.setText(i, j+1, total[j], CReportBase.TableTotal)


from Ui_ReportAcuteInfectionsSetup import Ui_ReportAcuteInfectionsSetupDialog


class CReportAcuteInfectionsSetupDialog(QtGui.QDialog, Ui_ReportAcuteInfectionsSetupDialog):
    
    defaultParametersByCategory = {
                                   'children' : {'cbItemName' : u'Дети',
                                                 'ageFrom' : 0,
                                                 'ageTo' : 14},
                                   'childrenUpToOneYear': {'cbItemName': u'Дети до 1 года',
                                                 'ageFrom': 0,
                                                 'ageTo': 1},
                                   'teenagers' : {'cbItemName' : u'Подростки',
                                                  'ageFrom' : 15,
                                                  'ageTo' : 17},
                                   'adults' : {'cbItemName' : u'Взрослые',
                                               'ageFrom' : 18,
                                               'ageTo' : 150},
                                   'seniors' : {'cbItemName' : u'Пожилые',
                                                'ageFrom' : 55,
                                                'ageTo' : 150},
                                   'inset2008' : {'cbItemName' : u'Вкладыш-2008',
                                                  'ageFrom' : 0,
                                                  'ageTo' : 150},
                                   'seniors4000' : {'cbItemName' : u'Взрослые 4000',
                                                   'ageFrom' : 55,
                                                   'ageTo' : 150},
                                   'adults4003' : {'cbItemName' : u'Взрослые 4003',
                                                   'ageFrom' : 18,
                                                   'ageTo' : 55},
                                   }

    usedCategory = ['children', 'childrenUpToOneYear', 'teenagers', 'adults', 'seniors', 'inset2008', 'seniors4000', 'adults4003']
    
    mapCategoryNameToIndex = {}
    
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbSpecialityPerson.setTable('rbSpeciality', True)
        self.cmbHurt.setTable('rbHurtType', True)
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.setCreateDateEnabled(False)
        self.setAreaEnabled(False)
        self.setMKBFilterEnabled(False)
        self.setAccountAccompEnabled(False)
        self.setOnlyFirstTimeEnabled(False)
        self.setNotNullTraumaTypeEnabled(False)
        self.setNotConsiderDigitsAfterDotEnabled(False)
        self.setTemplateConfigurationEnabled(False)
        self.setSpecialityPersonEnabled(False)
        self.setHurt(False)
        self.setIsPrimaryVisible(False)
        
        self.setAddressFilterVisible(True)
        
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbArea.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbArea.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbFilterAddressCity.setCode(QtGui.qApp.defaultKLADR())

        self.edtBegBirthYear.setMaximum(QtCore.QDate.currentDate().year())
        self.edtEndBirthYear.setMaximum(QtCore.QDate.currentDate().year())

        self.initCategory()
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

    
    def setTemplateConfigurationEnabled(self, value):
        for widget in [self.lblTemplate, self.cmbTemplate, self.lblCategory, self.cmbCategory]:
            widget.setVisible(value)
        self.templateConfiguration = value
        
    
    def initCategory(self):
        self.cmbCategory.clear()
        for index, categoryName in enumerate(self.usedCategory):
            categoryInfo = self.defaultParametersByCategory.get(categoryName, {})
            self.cmbCategory.addItem(categoryInfo.get('cbItemName', u'<Без имени>'), toVariant(categoryName))
            self.mapCategoryNameToIndex[categoryName] = index

    def setCreateDateEnabled(self, mode):
        for widget in [self.chkCreateDate, self.edtCreateEndDate, self.edtCreateBegDate, self.lblCreateDate]:
            widget.setVisible(mode)
        self.createDateEnabled = mode

    
    def setAreaEnabled(self, mode=True):
        for widget in [self.chkArea, self.cmbArea]:
            widget.setVisible(mode)
        self.areaEnabled = mode


    def setMKBFilterEnabled(self, mode=True):
        for widget in [self.frmMKB, self.frmMKBEx]:
            widget.setVisible(mode)
        self.MKBFilterEnabled = mode


    def setAccountAccompEnabled(self, mode=True):
        for widget in [self.chkAccountAccomp]:
            widget.setVisible(mode)
        self.accountAccompEnabled = mode


    def setOnlyFirstTimeEnabled(self, mode=True):
        for widget in [self.chkOnlyFirstTime]:
            widget.setVisible(mode)
        self.onlyFirstTimeEnabled = mode


    def setNotConsiderDigitsAfterDotEnabled(self, mode=True):
        for widget in [self.chkNotConsiderDigitsAfterDot]:
            widget.setVisible(mode)
        self.notConsiderDigitsAfterDot = mode


    def setNotNullTraumaTypeEnabled(self, mode=True):
        for widget in [self.chkNotNullTraumaType]:
            widget.setVisible(mode)
        self.notNullTraumaType = mode

    def setSpecialityPersonEnabled(self, mode=True):
        for widget in [self.lblSpecialityPerson, self.cmbSpecialityPerson]:
            widget.setVisible(mode)
        self.areaEnabled = mode

    def setHurt(self, mode=True):
        for widget in [self.lblHurt, self.cmbHurt]:
            widget.setVisible(mode)
        self.areaEnabled = mode

    def setTitle(self, title):
        self.setWindowTitle(title)
        
    def setAddressFilterVisible(self, visible = True):
        self.addressFilterVisible = visible
        self.gbFilterAddress.setVisible(visible)

    def setIsPrimaryVisible(self, visible=True):
        self.isPrimaryVisible = visible
        self.cmbIsPrimary.setVisible(visible)
        self.lblIsPrimary.setVisible(visible)

    def setEventTypeVisible(self, visible=True):
        pass


    def setParams(self, params):
        self.chkCreateDate.setChecked(params.get('chkCreateDate', False))
        self.edtCreateBegDate.setDate(params.get('createBegDate', QtCore.QDate.currentDate()))
        self.edtCreateEndDate.setDate(params.get('createEndDate', QtCore.QDate.currentDate()))
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeIdList', []))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbSpecialityPerson.setValue(params.get('specialityId', None))
        self.cmbHurt.setValue(params.get('hurtType', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))
        areaIdEnabled = bool(params.get('areaIdEnabled', False))
        self.chkArea.setChecked(areaIdEnabled)
        self.cmbArea.setEnabled(areaIdEnabled)
        self.cmbArea.setValue(params.get('areaId', None))
        MKBFilter = params.get('MKBFilter', 0)

        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))

        self.chkBirthYear.setChecked(params.get('birthYearParam', False))
        self.edtBegBirthYear.setValue(params.get('birthYearFrom', 1900))
        self.edtEndBirthYear.setValue(params.get('birthYearTo', QtCore.QDate.currentDate().year()))

        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        MKBExFilter = params.get('MKBExFilter', 0)
        self.cmbMKBExFilter.setCurrentIndex(MKBExFilter if MKBExFilter else 0)
        self.edtMKBExFrom.setText(params.get('MKBExFrom', 'A00'))
        self.edtMKBExTo.setText(params.get('MKBExTo',   'Z99.9'))
        self.chkAccountAccomp.setChecked(bool(params.get('accountAccomp', False)))
        self.chkOnlyFirstTime.setChecked(bool(params.get('onlyFirstTime', False)))
        self.chkNotConsiderDigitsAfterDot.setChecked(bool(params.get('notConsiderDigitsAfterDot', False)))
        self.chkNotNullTraumaType.setChecked(bool(params.get('notNullTraumaType', False)))
        self.chkRegisteredInPeriod.setChecked(bool(params.get('registeredInPeriod', False)))
        self.cmbLocality.setCurrentIndex(params.get('locality', 0))

        # FIXME:skkachaev: Если выставлять сразу в уишке, то ничего не работает. Возможно, дизайнер выставляет кривоватые параметры
        self.gbFilterAddress.setChecked(False)

        self.gbFilterAddress.setChecked(bool(params.get('isFilterAddress', False)))
        self.cmbFilterAddressType.setCurrentIndex(params.get('filterAddressType', 0))
        self.cmbFilterAddressCity.setCode(params.get('filterAddressCity', QtGui.qApp.defaultKLADR()))
        self.chkOnlyPermanentAttach.setChecked(forceBool(params.get('onlyPermanentAttach', False)))
        addressStreet = params.get('filterAddressStreet', u'')
        if not addressStreet:
            addressStreet = QtGui.qApp.defaultKLADR()
            self.cmbFilterAddressStreet.setCity(addressStreet)
        else:
            self.cmbFilterAddressStreet.setCode(addressStreet)
        self.edtFilterAddressHouse.setText(params.get('filterAddressHouse', u''))
        self.edtFilterAddressCorpus.setText(params.get('filterAddressCorpus', u''))
        self.edtFilterAddressFlat.setText(params.get('filterAddressFlat', u''))
        self.chkOnlyChilds.setChecked(forceBool(params.get('onlyChilds', False)))
        self.cmbIsPrimary.setCurrentIndex(forceInt(params.get('isPrimary', 0)))
        self.chkVisitEmergency.setChecked(params.get('visitEmergency', False))
        # templateIndex = params.get('templateIndex', None)
        # if self.templateConfiguration and 0 <= templateIndex <= self.cmbTemplate.count():
        #     self.cmbTemplate.setCurrentIndex(templateIndex)
        categoryName = params.get('categoryName', None)
        if self.templateConfiguration and categoryName:
            categoryIndex = self.cmbCategory.findData(categoryName, QtCore.Qt.UserRole, QtCore.Qt.MatchFixedString)
            self.cmbCategory.setCurrentIndex(categoryIndex)
        


    def params(self):
        result = {}
        result['chkCreateDate'] = self.chkCreateDate.isChecked()
        result['createBegDate'] = self.edtCreateBegDate.date()
        result['createEndDate'] = self.edtCreateEndDate.date()
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeIdList'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['specialityId'] = self.cmbSpecialityPerson.value()
        result['hurtType'] = self.cmbHurt.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['personId'] = self.cmbPerson.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['onlyChilds'] = self.chkOnlyChilds.isChecked()

        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()

        result['birthYearParam'] = self.chkBirthYear.isChecked()
        result['birthYearFrom'] = self.edtBegBirthYear.value()
        result['birthYearTo'] = self.edtEndBirthYear.value()

        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        if self.areaEnabled:
            result['areaIdEnabled'] = self.chkArea.isChecked()
            result['areaId'] = self.cmbArea.value()
        if self.MKBFilterEnabled:
            result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
            result['MKBFrom']   = forceString(self.edtMKBFrom.text())
            result['MKBTo']     = forceString(self.edtMKBTo.text())
            result['MKBExFilter']= self.cmbMKBExFilter.currentIndex()
            result['MKBExFrom']  = forceString(self.edtMKBExFrom.text())
            result['MKBExTo']    = forceString(self.edtMKBExTo.text())
        if self.accountAccompEnabled:
            result['accountAccomp'] = self.chkAccountAccomp.isChecked()
        if self.onlyFirstTimeEnabled:
            result['onlyFirstTime'] = self.chkOnlyFirstTime.isChecked()
        if self.notNullTraumaType:
            result['notNullTraumaType'] = self.chkNotNullTraumaType.isChecked()
        if self.notConsiderDigitsAfterDot:
            result['notConsiderDigitsAfterDot'] = self.chkNotConsiderDigitsAfterDot.isChecked()
        result['registeredInPeriod'] = self.chkRegisteredInPeriod.isChecked()
        result['locality'] = self.cmbLocality.currentIndex()
        result['isFilterAddress'] = self.gbFilterAddress.isChecked()
        result['filterAddressType'] = self.cmbFilterAddressType.currentIndex()
        result['filterAddressCity'] = self.cmbFilterAddressCity.code()
        result['filterAddressStreet'] = self.cmbFilterAddressStreet.code()
        result['filterAddressHouse'] = self.edtFilterAddressHouse.text()
        result['filterAddressCorpus'] = self.edtFilterAddressCorpus.text()
        result['filterAddressFlat'] = self.edtFilterAddressFlat.text()
        result['isPrimary'] = self.cmbIsPrimary.currentIndex()
        result['visitEmergency'] = self.chkVisitEmergency.isChecked()
        result['onlyPermanentAttach'] = self.chkOnlyPermanentAttach.isChecked()
        result['templateIndex'] = self.cmbTemplate.currentIndex()
        result['categoryName'] = self.cmbCategory.itemData(self.cmbCategory.currentIndex())
        return result


    @QtCore.pyqtSlot(int)
    def on_cmbFilterAddressCity_currentIndexChanged(self, index):
        code = self.cmbFilterAddressCity.code()
        self.cmbFilterAddressStreet.setCity(code)
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkOnlyChilds_toggled(self, checked):
        if checked:
            self.edtAgeTo.setMaximum(17)
            self.edtAgeFrom.setMaximum(17)
        else:
            self.edtAgeTo.setMaximum(150)
            self.edtAgeFrom.setMaximum(150)
            
            


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        tableEventType = QtGui.qApp.db.table('EventType')
        eventPurposeIdList = self.cmbEventPurpose.value()
        filter = tableEventType['purpose_id'].inlist(eventPurposeIdList) if eventPurposeIdList else getWorkEventTypeFilter()
        self.cmbEventType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id=%d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBExFilter_currentIndexChanged(self, index):
        self.edtMKBExFrom.setEnabled(index == 1)
        self.edtMKBExTo.setEnabled(index == 1)
        
    
    @QtCore.pyqtSlot(int)
    def on_cmbCategory_currentIndexChanged(self, index):
        if index >= 0:
            category = forceString(self.cmbCategory.itemData(index))
            self.edtAgeFrom.setValue(self.defaultParametersByCategory[category].get('ageFrom', 0))
            self.edtAgeTo.setValue(self.defaultParametersByCategory[category].get('ageTo', 150))
            self.setNotConsiderDigitsAfterDotEnabled(category == 'adults')

    def setLastTemplateActive(self):
        self.cmbTemplate.setCurrentIndex(self.cmbTemplate.count()-1)