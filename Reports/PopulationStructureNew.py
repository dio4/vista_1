# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from KLADR.KLADRModel           import getStreetName
from library.crbcombobox        import CRBComboBox
from library.Utils              import forceBool, forceInt, forceString
from Orgs.OrgStructComboBoxes   import COrgStructureModel
from Orgs.Utils                 import getOrgStructureDescendants, getOrgStructureNetId, getOrgStructures, CNet
from Reports.Report             import CReport
from Reports.ReportBase         import createTable, CReportBase


def selectDataByHouses(endDate, ageFrom, ageTo, orgSID,  socStatusTypeId,  socStatusClassId):
    stmt = """
    SELECT
	COUNT(DISTINCT Client.id) as cnt,
	AddressHouse.id as HouseID,
	AddressHouse.KLADRStreetCode as street,
	AddressHouse.number as num,
	AddressHouse.corpus as build,
    age(Client.birthDate, %(attachCheckDate)s) AS clientAge,
	IF (age(Client.birthDate, %(attachCheckDate)s) >= 60 AND Client.sex = 1, 1, 0) AS MenPensioner,
	IF (age(Client.birthDate, %(attachCheckDate)s) < 60 AND Client.sex = 1, 1, 0) AS MenNonPensioner,
	IF (age(Client.birthDate, %(attachCheckDate)s) >= 55 AND Client.sex = 2, 1, 0) AS WomPensioner,
	IF (age(Client.birthDate, %(attachCheckDate)s) < 55 AND Client.sex = 2, 1, 0) AS WomNonPensioner,
	IF (ClientAttach.orgStructure_id = OrgStructure_Address.master_id, 1, 0) AS Attached,
    IF(ClientIdentification.checkDate IS NULL,0,1) AS confirmed
FROM
	Client
	LEFT JOIN ClientAddress ON ClientAddress.client_id = Client.id
		AND ClientAddress.id = (SELECT MAX(CALocInt.id) FROM ClientAddress AS CALocInt WHERE CALocInt.type=1 AND CALocInt.client_id=Client.id)
	LEFT JOIN Address ON Address.id = ClientAddress.address_id
	LEFT JOIN AddressHouse ON AddressHouse.id = Address.house_id
	LEFT JOIN OrgStructure_Address ON OrgStructure_Address.house_id = AddressHouse.id
	LEFT JOIN ClientAttach ON ClientAttach.client_id = Client.id
            AND ClientAttach.id = (SELECT MAX(CAT.id) FROM ClientAttach AS CAT
                                               LEFT JOIN rbAttachType ON rbAttachType.id=CAT.attachType_id
                                               WHERE CAT.deleted=0
                                               AND   CAT.client_id=Client.id
                                               AND   rbAttachType.temporary=0
                                               AND   CAT.begDate<=%(attachCheckDate)s
                                               AND   (CAT.endDate IS NULL or CAT.endDate>=%(attachCheckDate)s)
                                              )
            AND ClientAttach.orgStructure_id = %(orgStructureID)d
	LEFT JOIN rbAttachType ON rbAttachType.id=ClientAttach.attachType_id
    LEFT JOIN ClientIdentification ON ClientIdentification.client_id
                                   AND ClientIdentification.id = (
        SELECT MAX(CI.id)
        FROM ClientIdentification AS CI
        LEFT JOIN rbAccountingSystem ON rbAccountingSystem.id = CI.accountingSystem_id
        WHERE rbAccountingSystem.code in (\'1\', \'2\')
        AND CI.client_id = Client.id)
WHERE
        OrgStructure_Address.master_id = %(orgStructureID)d
    AND %(mainCond)s
GROUP BY HouseID, clientAge, MenPensioner, MenNonPensioner, WomPensioner, WomNonPensioner, Attached
ORDER BY street, num
    """
    
    db = QtGui.qApp.db
    tableClient  = db.table('Client')
    tableAttachType = db.table('rbAttachType')
    cond = []
    cond.append(tableClient['deleted'].eq(0))

    if ageFrom <= ageTo:
        # для проверки логики:
        # если взять ageFrom == ageTo == 0 то
        # должны получиться дети родившиеся за последний год,
        # а годовалые уже не подходят
        cond.append(tableClient['birthDate'].gt(endDate.addYears(-ageTo-1)))
        cond.append(tableClient['birthDate'].le(endDate.addYears(-ageFrom)))
    
    cond.append( db.joinOr([ tableAttachType['outcome'].eq(0),
                            tableAttachType['outcome'].isNull()]))

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
    
    return db.query(stmt % {'orgStructureID' : orgSID,
                            'attachCheckDate': tableClient['birthDate'].formatValue(endDate),
                            'mainCond'       : db.joinAnd(cond)})

def selectData(endDate, ageFrom, ageTo, areaId, addressType,  socStatusTypeId,  socStatusClassId):
    stmt="""
SELECT
   COUNT(Client.id) as cnt,
   %(orgStructField)s AS repOrgStructure_id,
   age(Client.birthDate, %(attachCheckDate)s) AS clientAge,
   Client.sex AS clientSex,
   IF(ClientAttach.id IS NULL,0,1) AS attached,
   IF(ClientIdentification.checkDate IS NULL,0,1) AS confirmed
FROM Client
%(joins)s
LEFT JOIN ClientAttach  ON ClientAttach.client_id = Client.id
                        AND ClientAttach.id = (SELECT MAX(CAT.id) FROM ClientAttach AS CAT
                                               LEFT JOIN rbAttachType ON rbAttachType.id=CAT.attachType_id
                                               WHERE CAT.deleted=0
                                               AND   CAT.client_id=Client.id
                                               # AND   rbAttachType.temporary=0
                                               AND   CAT.begDate<=%(attachCheckDate)s
                                               AND   (CAT.endDate IS NULL or CAT.endDate>=%(attachCheckDate)s)
                                              )
                        AND %(attachToArea)s
LEFT JOIN rbAttachType ON rbAttachType.id=ClientAttach.attachType_id
LEFT JOIN ClientIdentification ON ClientIdentification.client_id
                               AND ClientIdentification.id = (
    SELECT MAX(CI.id)
    FROM ClientIdentification AS CI
    LEFT JOIN rbAccountingSystem ON rbAccountingSystem.id = CI.accountingSystem_id
    WHERE rbAccountingSystem.code in (\'1\', \'2\')
    AND CI.client_id = Client.id)
WHERE %(mainCond)s
GROUP BY repOrgStructure_id, clientAge, clientSex, attached, confirmed
    """
    db = QtGui.qApp.db
    tableClient  = db.table('Client')
    tableOrgStructureAddress = db.table('OrgStructure_Address')
    tableAddress = db.table('Address')
    tableClientAttach = db.table('ClientAttach')
    tableAttachType = db.table('rbAttachType')
    cond = []
    cond.append(tableClient['deleted'].eq(0))
    cond.append( db.joinOr([ tableAttachType['outcome'].eq(0),
                             tableAttachType['outcome'].isNull()]))
#    cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))

#    if eventTypeIdList:
#        cond.append(tableEvent['eventType_id'].inlist(eventTypeIdList))
    if ageFrom <= ageTo:
        # для проверки логики:
        # если взять ageFrom == ageTo == 0 то
        # должны получиться дети родившиеся за последний год,
        # а годовалые уже не подходят
        cond.append(tableClient['birthDate'].gt(endDate.addYears(-ageTo-1)))
        cond.append(tableClient['birthDate'].le(endDate.addYears(-ageFrom)))

#    if areaId:
#        cond.append(tableOrgStructureAddress['master_id'].inlist(getOrgStructureDescendants(areaId)))

    if areaId:
        areaIdList = getOrgStructureDescendants(areaId)
    else:
        areaIdList = getOrgStructures(QtGui.qApp.currentOrgId())
    reg = (addressType+1) & 1
    loc = (addressType+1) & 2
    attach = (addressType+1) & 4
    condAddr = []
    joins = ''
    if reg:
        tableOrgStructureAddress = db.table('OrgStructure_Address').alias('OSAReg')
        condAddr.append(tableOrgStructureAddress['master_id'].inlist(areaIdList))
        joins += '''
LEFT JOIN ClientAddress AS CAReg ON CAReg.client_id = Client.id
                        AND CAReg.id = (SELECT MAX(CARegInt.id) FROM ClientAddress AS CARegInt WHERE CARegInt.type=0 AND CARegInt.client_id=Client.id)
LEFT JOIN Address       AS AReg ON AReg.id = CAReg.address_id
LEFT JOIN OrgStructure_Address AS OSAReg ON OSAReg.house_id = AReg.house_id AND %s
''' % tableOrgStructureAddress['master_id'].inlist(areaIdList)

    if loc:
        tableOrgStructureAddress = db.table('OrgStructure_Address').alias('OSALoc')
        condAddr.append(tableOrgStructureAddress['master_id'].inlist(areaIdList))
        joins += '''
LEFT JOIN ClientAddress AS CALoc ON CALoc.client_id = Client.id
                        AND CALoc.id = (SELECT MAX(CALocInt.id) FROM ClientAddress AS CALocInt WHERE CALocInt.type=1 AND CALocInt.client_id=Client.id)
LEFT JOIN Address       AS ALoc ON ALoc.id = CALoc.address_id
LEFT JOIN OrgStructure_Address AS OSALoc ON OSALoc.house_id = ALoc.house_id AND %s
''' % tableOrgStructureAddress['master_id'].inlist(areaIdList)
    if attach:
        condAddr.append(db.joinAnd([tableClientAttach['orgStructure_id'].inlist(areaIdList),
                                    tableClientAttach['deleted'].eq(0)
                                   ]))
    if condAddr:
        cond.append(db.joinOr(condAddr))

    if attach:
        if loc:
            if reg:
                orgStructField = 'IF(ClientAttach.orgStructure_id IS NOT NULL, ClientAttach.orgStructure_id, IF(OSALoc.master_id IS NOT NULL, OSALoc.master_id, OSAReg.master_id))'
            else:
                orgStructField = 'IF(ClientAttach.orgStructure_id IS NOT NULL, ClientAttach.orgStructure_id, OSALoc.master_id)'
        else:
            if reg:
                orgStructField = 'IF(ClientAttach.orgStructure_id IS NOT NULL, ClientAttach.orgStructure_id, OSAReg.master_id)'
            else:
                orgStructField = 'ClientAttach.orgStructure_id'
    else:
        if loc:
            if reg:
                orgStructField = 'IF(OSALoc.master_id IS NOT NULL, OSALoc.master_id, OSAReg.master_id)'
            else:
                orgStructField = 'OSALoc.master_id'
        else:
            if reg:
                orgStructField = 'OSAReg.master_id'
            else:
                orgStructField = 'NULL'
    
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

    return db.query(stmt % {'orgStructField' : orgStructField,
                            'attachCheckDate': tableClient['birthDate'].formatValue(endDate),
                            'attachToArea'   : tableClientAttach['orgStructure_id'].inlist(areaIdList),
                            'joins'          : joins,
                            'mainCond'       : db.joinAnd(cond)})

def fakeAgeTuple(age):
    return (age*365,
            age*365/7,
            age*12,
            age
           )


class CPopulationStructure(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Состав населения по участкам')


    def getSetupDialog(self, parent):
        result = CPopulationStructureSetupDialog(parent)
        result.setTitle(self.title())
        return result


    def build(self, params):
        endDate = params.get('endDate', QtCore.QDate())
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        orgStructureId = params.get('orgStructureId', None)
        addressType = params.get('addressType', 0)
        detalizeByHouses = params.get('detalizeByHouses',  None)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        if detalizeByHouses:
            rowSize = 8
        else:
            rowSize = 7

        db = QtGui.qApp.db

        query = selectData(endDate, ageFrom, ageTo, orgStructureId, addressType,  socStatusTypeId,  socStatusClassId)

        reportData = {}
        mapAreaIdToNetId = {}
        mapNetIdToNet = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record    = query.record()
            areaId    = forceInt(record.value('repOrgStructure_id'))
            if areaId in mapAreaIdToNetId:
                netId = mapAreaIdToNetId[areaId]
            else:
                netId = getOrgStructureNetId(areaId)
                mapAreaIdToNetId[areaId] = netId
            if netId in mapNetIdToNet:
                net = mapNetIdToNet[netId]
            else:
                net = CNet(netId)
                mapNetIdToNet[netId] = net

            age = forceInt(record.value('clientAge'))
            sex = forceInt(record.value('clientSex'))
            if net.applicable(sex, fakeAgeTuple(age)):
                cnt       = forceInt(record.value('cnt'))
                attached  = forceBool(record.value('attached'))
                confirmed = forceBool(record.value('confirmed'))

                reportRow = reportData.get(areaId, None)
                if not reportRow:
                    reportRow = [0]*rowSize
                    reportData[areaId] = reportRow
                reportRow[0] += cnt
                if sex == 1 and age < 60:
                    reportRow[1] += cnt
                elif sex == 1 and age >= 60:
                    reportRow[2] += cnt
                elif sex == 2 and age < 55:
                    reportRow[3] += cnt
                elif sex == 2 and age >= 55:
                    reportRow[4] += cnt
                
                if attached:
                    reportRow[5] += cnt
                if confirmed:
                    reportRow[6] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        
        if not detalizeByHouses:
            tableColumns = [
                ('30%', [u'Подразделение'], CReportBase.AlignLeft),
                ('10%', [u'всего'], CReportBase.AlignRight),
                ('10%', [u'М 18-59 лет'], CReportBase.AlignRight),
                ('10%', [u'М от 60 лет'], CReportBase.AlignRight),
                ('10%', [u'Ж 18-55 лет'], CReportBase.AlignRight),
                ('10%', [u'Ж от 55 лет'], CReportBase.AlignRight),
                ('10%', [u'Прикр.'], CReportBase.AlignRight),
                ('10%', [u'Подтв. ЕИС'], CReportBase.AlignRight),
                ]
        else:
            tableColumns = [
                ('20%', [u'Подразделение/Улица'], CReportBase.AlignLeft),
                ('10%', [u'№ дома'], CReportBase.AlignLeft),
                ('10%', [u'всего'], CReportBase.AlignRight),
                ('10%', [u'М 18-59 лет'], CReportBase.AlignRight),
                ('10%', [u'М от 60 лет'], CReportBase.AlignRight),
                ('10%', [u'Ж 18-55 лет'], CReportBase.AlignRight),
                ('10%', [u'Ж от 55 лет'], CReportBase.AlignRight),
                ('10%', [u'Прикр.'], CReportBase.AlignRight),
                ('10%', [u'Подтв. ЕИС'], CReportBase.AlignRight),
                ]
        table = createTable(cursor, tableColumns)
        self.genOrgStructureReport(table, reportData, rowSize, orgStructureId,  params)
        return doc


    def genOrgStructureReport(self, table, reportData, rowSize, orgStructureId,  params):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        index = model.findItemId(orgStructureId)
        if index:
            item = index.internalPointer()
        else:
            item = model.getRootItem()
        self.genOrgStructureReportForItem(table, reportData, item, rowSize,  params)


    def dataPresent(self, reportData, item):
        row = reportData.get(item.id(), None)
        if item.isArea() or (row and any(row)):
            return True
        for subitem in item.items():
            if self.dataPresent(reportData, subitem):
                return True
        return False


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize,  params):
        if self.dataPresent(reportData, item):
            i = table.addRow()
            if item.childCount() == 0:
                row = reportData.get(item.id(), None)
                if row:
                    if rowSize == 8:
                        table.setText(i, 0, item.name(),  CReportBase.TableTotal)
                        for j in xrange(rowSize-1):
                            table.setText(i, j+2, row[j],  CReportBase.TableTotal)
                        table.mergeCells(i, 0,  1, 2)
                        self.genDetalizationByHouses(item.id(),  table,  params, i)
                    elif rowSize == 7:
                        table.setText(i, 0, item.name())
                        for j in xrange(rowSize):
                            table.setText(i, j+1, row[j])
                else:
                    table.setText(i, 0, item.name())
                return row
            else:
                table.mergeCells(i,0, 1, rowSize+1)
                table.setText(i, 0, item.name(), CReportBase.TableHeader)
                total = [0]*rowSize
                row = reportData.get(item.id(), None)
                if row:
                    i = table.addRow()
                    table.setText(i, 0, '-', CReportBase.TableHeader)
                    for j in xrange(rowSize):
                        table.setText(i, j+1, row[j])
                        total[j] += row[j]
                for subitem in item.items():
                    row = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize,  params)
                    if row:
                        for j in xrange(rowSize):
                            total[j] += row[j]
                i = table.addRow()
                table.setText(i, 0, u'всего по '+item.name(), CReportBase.TableTotal)
                if rowSize == 7:
                    for j in xrange(rowSize):
                        table.setText(i, j+1, total[j], CReportBase.TableTotal)
                elif rowSize == 8:
                    for j in xrange(rowSize-1):
                        table.setText(i, j+2, total[j], CReportBase.TableTotal)
                    table.mergeCells(i, 0,  1, 2)
                return total
        else:
            return None

    def genDetalizationByHouses(self,  itemID, table,   params, parentRow=-1):
        endDate = params.get('endDate', QtCore.QDate())
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        query = selectDataByHouses(endDate, ageFrom, ageTo, itemID,  socStatusTypeId,  socStatusClassId)
        reportData = {}
        mapAreaIdToNetId = {}
        mapNetIdToNet = {}
        while query.next():
            record = query.record()
            age = forceInt(record.value('clientAge'))
            sex = forceInt(record.value('clientSex'))
            netId = getOrgStructureNetId(itemID)
            net = CNet(netId)
            
            if net.applicable(sex, fakeAgeTuple(age)):
                reportRow = {'street':'',  'num': '',  'total':0,  'mp':0,  'mnp':0,  'wp':0,  'wnp':0,  'attached':0,  'confirmed':0}
                houseID = forceInt(record.value('HouseID'))
                street = forceString(record.value('street'))
                num = forceString(record.value('num'))
                build = forceString(record.value('build'))
                mp = forceBool(record.value('MenPensioner'))
                wp = forceBool(record.value('WomPensioner'))
                mnp = forceBool(record.value('MenNonPensioner'))
                wnp = forceBool(record.value('WomNonPensioner'))
                cnt = forceInt(record.value('cnt'))
                attached = forceBool(record.value('Attached'))
                confirmed = forceBool(record.value('confirmed'))
                
                if not houseID in reportData.keys():
                    reportRow['street'] = getStreetName(street)
                    reportRow['num'] = num
                    if build:
                        reportRow['num'] = reportRow['num'] + u' к.' + build
                    reportData[houseID] = reportRow
                if mp:
                    reportData[houseID]['mp'] += cnt
                if mnp:
                    reportData[houseID]['mnp'] += cnt
                if wp:
                    reportData[houseID]['wp'] += cnt
                if wnp:
                    reportData[houseID]['wnp'] += cnt
                if attached:
                    reportData[houseID]['attached'] += cnt
                if confirmed:
                    reportData[houseID]['confirmed'] += cnt
                reportData[houseID]['total'] += cnt

        cnt = 0
        for house in reportData.keys():
            #распихаем всё по столбикам таблицы и дело с концом
            i = table.addRow()
            table.setText(i,  0,  reportData[house]['street'])
            table.setText(i,  1,  reportData[house]['num'])
            table.setText(i,  2,  reportData[house]['total'])
            table.setText(i,  3,  reportData[house]['mnp'])
            table.setText(i,  4,  reportData[house]['mp'])
            table.setText(i,  5,  reportData[house]['wnp'])
            table.setText(i,  6,  reportData[house]['wp'])
            table.setText(i,  7,  reportData[house]['attached'])
            table.setText(i,  8,  reportData[house]['confirmed'])
            cnt += reportData[house]['confirmed']
        if parentRow >= 0:
            table.setText(parentRow, 8, cnt, CReportBase.TableTotal, clearBefore=True)

from Ui_PopulationStructureSetup import Ui_PopulationStructureSetupDialog


class CPopulationStructureSetupDialog(QtGui.QDialog, Ui_PopulationStructureSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.chkDetalizeByHouses.setChecked(False)
        self.cmbSocStatusType.setTable('vrbSocStatusType', True)
        self.cmbSocStatusType.setShowFields(CRBComboBox.showNameAndCode)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbAddressOrgStructureType.setCurrentIndex(params.get('addressType', 0))
        self.cmbSocStatusClass.setValue(params.get('socStatusClassId', None))
        self.cmbSocStatusType.setValue(params.get('socStatusTypeId', None))


    def params(self):
        result = {}
        result['endDate'] = self.edtEndDate.date()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['addressType'] = self.cmbAddressOrgStructureType.currentIndex()
        result['detalizeByHouses'] = self.chkDetalizeByHouses.isChecked()
        result['socStatusClassId'] = self.cmbSocStatusClass.value()
        result['socStatusTypeId'] = self.cmbSocStatusType.value()
        return result
        
    @QtCore.pyqtSlot(bool)
    def on_chkDetalizeByHouses_clicked(self, value):
        if value:
            self.cmbAddressOrgStructureType.setCurrentIndex(1)
            self.cmbAddressOrgStructureType.setVisible(False)
            self.lblAddressOrgStructureType.setVisible(False)
        else:
            self.cmbAddressOrgStructureType.setVisible(True)
            self.lblAddressOrgStructureType.setVisible(True)
            
    @QtCore.pyqtSlot(int)
    def on_cmbSocStatusClass_currentIndexChanged(self, index):
        socStatusClassId = self.cmbSocStatusClass.value()
        filter = ('class_id = %d' % socStatusClassId) if socStatusClassId else ''
        self.cmbSocStatusType.setFilter(filter)
