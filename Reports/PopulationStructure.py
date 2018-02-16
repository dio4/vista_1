# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceBool, forceInt, forceString
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.Utils         import getOrgStructureDescendants, getOrgStructureNetId, getOrgStructures, CNet
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


def selectData(endDate, ageFrom, ageTo, areaId, addressType):
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
                                               AND   rbAttachType.temporary=0
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

        db = QtGui.qApp.db
        rowSize = 5
        query = selectData(endDate, ageFrom, ageTo, orgStructureId, addressType)

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
                if sex == 1:
                    reportRow[1] += cnt
                else:
                    reportRow[2] += cnt
                if attached:
                    reportRow[3] += cnt
                if confirmed:
                    reportRow[4] += cnt

        # now text
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('30%', [u'Подразделение'], CReportBase.AlignLeft),
            ('10%', [u'всего'], CReportBase.AlignRight),
            ('10%', [u'М'], CReportBase.AlignRight),
            ('10%', [u'Ж'], CReportBase.AlignRight),
            ('10%', [u'Прикр.'], CReportBase.AlignRight),
            ('10%', [u'Подтв. ЕИС'], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        self.genOrgStructureReport(table, reportData, rowSize, orgStructureId)
        return doc


    def genOrgStructureReport(self, table, reportData, rowSize, orgStructureId):
        model = COrgStructureModel(None, QtGui.qApp.currentOrgId())
        index = model.findItemId(orgStructureId)
        if index:
            item = index.internalPointer()
        else:
            item = model.getRootItem()
        self.genOrgStructureReportForItem(table, reportData, item, rowSize)


    def dataPresent(self, reportData, item):
        row = reportData.get(item.id(), None)
        if item.isArea() or (row and any(row)):
            return True
        for subitem in item.items():
            if self.dataPresent(reportData, subitem):
                return True
        return False


    def genOrgStructureReportForItem(self, table, reportData, item, rowSize):
        if self.dataPresent(reportData, item):
            i = table.addRow()
            if item.childCount() == 0:
                row = reportData.get(item.id(), None)
                table.setText(i, 0, item.name())
                if row:
                    for j in xrange(rowSize):
                        table.setText(i, j+1, row[j])
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
                    row = self.genOrgStructureReportForItem(table, reportData, subitem, rowSize)
                    if row:
                        for j in xrange(rowSize):
                            total[j] += row[j]
                i = table.addRow()
                table.setText(i, 0, u'всего по '+item.name(), CReportBase.TableTotal)
                for j in xrange(rowSize):
                    table.setText(i, j+1, total[j], CReportBase.TableTotal)
                return total
        else:
            return None



from Ui_PopulationStructureSetup import Ui_PopulationStructureSetupDialog


class CPopulationStructureSetupDialog(QtGui.QDialog, Ui_PopulationStructureSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.patientRequired = False
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbAddressOrgStructureType.setCurrentIndex(params.get('addressType', 0))


    def params(self):
        result = {}
        result['endDate'] = self.edtEndDate.date()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['addressType'] = self.cmbAddressOrgStructureType.currentIndex()
        return result
