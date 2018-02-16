# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getWorkEventTypeFilter
from library.Utils      import forceBool, forceInt, forceRef, forceString, getVal
from Orgs.Orgs          import selectOrganisation
from Orgs.Utils         import getOrgStructureDescendants, getOrgStructures
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase


STRICT_ADDRESS = 0
NONRESIDENT_ADDRESS = 1
FOREIGN_ADDRESS = 2

def selectData(params):
    begDate                 = params.get('begDate', QtCore.QDate())
    endDate                 = params.get('endDate', QtCore.QDate())
    eventPurposeId          = params.get('eventPurposeId', None)
    eventTypeId             = params.get('eventTypeId', None)
    orgStructureId          = params.get('orgStructureId', None)
    specialityId            = params.get('specialityId', None)
    personId                = params.get('personId', None)
    workOrgId               = params.get('workOrgId', None)
    sex                     = params.get('sex', 0)
    ageFrom                 = params.get('ageFrom', 0)
    ageTo                   = params.get('ageTo', 150)
    areaIdEnabled           = params.get('areaIdEnabled', False)
    chkOrgStructureArea     = params.get('chkOrgStructureArea', False)
    areaId                  = params.get('areaId', None)
    MKBFilter               = params.get('MKBFilter', 0)
    MKBFrom                 = params.get('MKBFrom', 'A00')
    MKBTo                   = params.get('MKBTo', 'Z99.9')
    MKBExFilter             = params.get('MKBExFilter', 0)
    MKBExFrom               = params.get('MKBExFrom', 'A00')
    MKBExTo                 = params.get('MKBExTo', 'Z99.9')
    
    addressEnabled          = params.get('addressEnabled', False)
    addressType             = params.get('addressType', 0)
    clientAddressType       = params.get('clientAddressType', 0)
    clientAddressCityCode   = params.get('clientAddressCityCode', None)
    clientAddressCityCodeList = params.get('clientAddressCityCodeList', None)
    clientAddressStreetCode = params.get('clientAddressStreetCode', None)
    clientHouse             = params.get('clientHouse', '')
    clientCorpus            = params.get('clientCorpus', '')
    clientFlat              = params.get('clientFlat', '')
    
    
    stmt="""
SELECT
    count(Event.id) AS `count`,
    Event.result_id AS result_id,
    rbResult.name   AS result,
    Event.isPrimary AS isPrimary,
    Event.execDate IS NOT NULL AS isDone,
    Event.`order`   AS `order`
FROM
    Event
    LEFT JOIN EventType ON EventType.id = Event.eventType_id
    LEFT JOIN Diagnostic ON Diagnostic.event_id = Event.id AND
                            Diagnostic.id IN (
                    SELECT D1.id
                    FROM Diagnostic AS D1 LEFT JOIN rbDiagnosisType AS DT1 ON DT1.id = D1.diagnosisType_id
                    WHERE D1.event_id = Event.id AND
                    DT1.code = (SELECT MIN(DT2.code)
                              FROM Diagnostic AS D2 LEFT JOIN rbDiagnosisType AS DT2 ON DT2.id = D2.diagnosisType_id
                              WHERE D2.event_id = Event.id)
                    )
    LEFT JOIN Client ON Client.id = Event.client_id
    LEFT JOIN ClientAddress ON ClientAddress.client_id = Event.client_id
                            AND ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA WHERE CA.Type=1 and CA.client_id = Event.client_id)
    LEFT JOIN Address ON Address.id = ClientAddress.address_id
    %s
    LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id
    LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.execPerson_id
    LEFT JOIN rbResult ON rbResult.id = Event.result_id
WHERE
    %s
GROUP BY
    result_id, isPrimary, isDone, `order`
"""
    db = QtGui.qApp.db
    tableEvent  = db.table('Event')
    tableDiagnosis  = db.table('Diagnosis')
    tableClient = db.table('Client')
    tableClientAddress = db.table('ClientAddress')
    tableOrgStructureAddress = db.table('OrgStructure_Address')
    tableAddress = db.table('Address')
    tableAddressForClient = db.table('Address').alias('AddressForCLient')
    tableAddressHouse = db.table('AddressHouse')
    tablePerson = db.table('vrbPersonWithSpeciality')
    tableDiagnostic = db.table('Diagnostic')
    tableDiseaseCharacter = db.table('rbDiseaseCharacter')
    cond = []
    cond.append(tableEvent['deleted'].eq(0))
    cond.append(tableEvent['execDate'].ge(begDate))
    cond.append(db.joinOr([tableEvent['execDate'].lt(endDate.addDays(1)), tableEvent['execDate'].isNull()]))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    elif eventPurposeId:
        cond.append(db.table('EventType')['purpose_id'].eq(eventPurposeId))
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if personId:
        cond.append(tableDiagnostic['person_id'].eq(personId))
    elif orgStructureId:
        cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    else:
        cond.append(tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()))
    if specialityId:
        cond.append(tablePerson['speciality_id'].eq(specialityId))
    if workOrgId:
        cond.append('EXISTS (SELECT * FROM ClientWork WHERE ClientWork.id = (SELECT MAX(id) FROM ClientWork AS CW WHERE CW.client_id = Client.id) and ClientWork.org_id=%d)' % (workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        date = str(QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate))
        cond.append('IF(Diagnosis.endDate IS NOT NULL, Diagnosis.endDate, DATE(\'%s\')) >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%(date, ageFrom))
        cond.append('IF(Diagnosis.endDate IS NOT NULL, Diagnosis.endDate, DATE(\'%s\')) <  SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(date, ageTo+1))
    
    additionalJoin = ''
    
    if areaIdEnabled:
        if chkOrgStructureArea:
            if areaId:
                orgStructureIdList = getOrgStructureDescendants(areaId)
            else:
                orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
            subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                        tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                      ]
            cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
        
        if addressEnabled:
            if addressType in [STRICT_ADDRESS, NONRESIDENT_ADDRESS]:
                clientAddressType = clientAddressType if addressType == STRICT_ADDRESS else 0
                additionalJoin = 'LEFT JOIN ClientAddress AS ClientAddressForClient ON ClientAddressForClient.client_id = Event.client_id AND ClientAddressForClient.id = (SELECT MAX(id) FROM ClientAddress AS CA2 WHERE CA2.Type=%d and CA2.client_id = Event.client_id) LEFT JOIN Address AS AddressForClient ON AddressForClient.id = ClientAddressForClient.address_id LEFT JOIN AddressHouse ON AddressHouse.id = AddressForClient.house_id'%clientAddressType
                if addressType == STRICT_ADDRESS:
                    if clientFlat:
                        cond.append(tableAddressForClient['flat'].eq(clientFlat))
                    if clientCorpus:
                        cond.append(tableAddressHouse['corpus'].eq(clientCorpus))
                    if clientHouse:
                        cond.append(tableAddressHouse['number'].eq(clientHouse))
                    if clientAddressStreetCode:
                        cond.append(tableAddressHouse['KLADRStreetCode'].eq(clientAddressStreetCode))
                    if clientAddressCityCodeList:
                        cond.append(tableAddressHouse['KLADRCode'].inlist(clientAddressCityCodeList))
                    else:
                        if clientAddressCityCode:
                            cond.append(tableAddressHouse['KLADRCode'].eq(clientAddressCityCode))
                else:
                    props = QtGui.qApp.preferences.appPrefs
                    kladrCodeList = [forceString(getVal(props, 'defaultKLADR', '')), forceString(getVal(props, 'provinceKLADR', ''))]
                    cond.append(tableAddressHouse['KLADRCode'].notInlist(kladrCodeList))
            else:
                foreignDocumentTypeId = forceInt(db.translate('rbDocumentType', 'code', '9', 'id'))
                documentCond = 'EXISTS(SELECT ClientDocument.`id` FROM ClientDocument WHERE ClientDocument.`documentType_id`=%d AND ClientDocument.`client_id`=Client.`id`)'%foreignDocumentTypeId
                cond.append(documentCond)
    stmt = stmt % (additionalJoin, db.joinAnd(cond))
#    print stmt
    return db.query(stmt)



class CEventResultSurvey(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setPayPeriodVisible(False)
        self.setTitle(u'Сводка по результату обращений')


    def getSetupDialog(self, parent):
        result = CEventResultSetupDialog(parent)
        result.setVisibleAdditionlOutput(False)
        result.setTitle(self.title())
        return result


    def build(self, params):
        
        query = selectData(params)

        reportData = {}
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            count  = forceInt(record.value('count'))
            resultId  = forceRef(record.value('result_id'))
            if resultId:
                result = forceString(record.value('result'))
            else:
                result = None
            isDone    = forceBool(record.value('isDone'))
            isPrimary = forceBool(record.value('isPrimary'))
            order     = forceInt(record.value('order'))

            reportLine = reportData.get(result, None)
            if not reportLine:
                reportLine = [0]*7
                reportData[result] = reportLine
            reportLine[0] += count
            reportLine[1 if isDone else 2] += count
            reportLine[3 if isPrimary else 4] += count
            if order == 1:
                reportLine[5] += count
            elif order == 2:
                reportLine[6] += count

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('5%',  [u'№' ], CReportBase.AlignRight),
            ('25%', [u'Результат',    ], CReportBase.AlignLeft),
            ('10%', [u'Всего',        ], CReportBase.AlignRight),
            ('10%', [u'В том числе', u'Закончено',    ], CReportBase.AlignRight),
            ('10%', [u'',            u'Не закончено', ], CReportBase.AlignRight),
            ('10%', [u'',            u'Первичных',    ], CReportBase.AlignRight),
            ('10%', [u'',            u'Повторных',    ], CReportBase.AlignRight),
            ('10%', [u'',            u'Плановых',     ], CReportBase.AlignRight),
            ('10%', [u'',            u'Экстренных',   ], CReportBase.AlignRight),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 1, 6)

        results = reportData.keys()
        results.sort()
        n = 0
        total = [0]*7
        for result in results:
            n += 1
            i = table.addRow()
            table.setText(i, 0, n)
            table.setText(i, 1, result if result is not None else u'-без указания-')
            for j, v in enumerate(reportData[result]):
                table.setText(i, 2+j, v)
                total[j]+=v
        i = table.addRow()
        table.setText(i, 1, u'итого', CReportBase.TableTotal)
        for j, v in enumerate(total):
            table.setText(i, 2+j, v, CReportBase.TableTotal)
            total[j]+=v
        return doc


from Ui_EventResultListSetup import Ui_EventResultSetupDialog


class CEventResultSetupDialog(QtGui.QDialog, Ui_EventResultSetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbEventPurpose.setTable('rbEventTypePurpose', True, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', True, filter=getWorkEventTypeFilter())
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.cmbArea.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbArea.setValue(QtGui.qApp.currentOrgStructureId())
        
        self.cmbResult.setTable('rbResult', addNone=True)
        
        self._visibleResult = False
        self.setVisibleResult(self._visibleResult)
        
        self._visiblePrimary = False
        self.setVisiblePrimary(self._visiblePrimary)
        
        self._visibleOrder = False
        self.setVisibleOrder(self._visibleOrder)
        
        self._visitEmergencyVisible = False
        self.setVisibleVisitEmergency(self._visitEmergencyVisible)
        
    
    def setVisibleVisitEmergency(self, visible):
        self._visitEmergencyVisible = visible
        self.chkVisitEmergency.setVisible(visible)
    
    def setVisibleResult(self, value):
        self._visibleResult = value
        self.lblResult.setVisible(value)
        self.cmbResult.setVisible(value)
    
    
    def setVisiblePrimary(self, value):
        self._visiblePrimary = value
        self.lblPrimary.setVisible(value)
        self.cmbPrimary.setVisible(value)
    

    def setVisibleOrder(self, value):
        self._visibleOrder = value
        self.lblOrder.setVisible(value)
        self.cmbOrder.setVisible(value)

    def setVisibleAdditionlOutput(self, value):
        self.chkVisitPlace.setVisible(value)
        self.chkPerson.setVisible(value)


    def setTitle(self, title):
        self.setWindowTitle(title)


    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbEventPurpose.setValue(params.get('eventPurposeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbSpeciality.setValue(params.get('specialityId', None))
        self.cmbPerson.setValue(params.get('personId', None))
        self.cmbWorkOrganisation.setValue(params.get('workOrgId', None))
        self.cmbSex.setCurrentIndex(params.get('sex', 0))
        self.edtAgeFrom.setValue(params.get('ageFrom', 0))
        self.edtAgeTo.setValue(params.get('ageTo', 150))
        areaIdEnabled = bool(params.get('areaIdEnabled', False))
        addressEnabled = params.get('addressEnabled', False)
        addressType = params.get('addressType', 0)
        self.cmbAddressType.setCurrentIndex(addressType)
        self.chkArea.setChecked(areaIdEnabled)
        chkOrgStructureArea = params.get('chkOrgStructureArea', False)
        self.chkOrgStructureArea.setEnabled(chkOrgStructureArea)
        self.cmbArea.setEnabled(areaIdEnabled and chkOrgStructureArea)
        self.cmbArea.setValue(params.get('areaId', None))
        self.setEnabledCmbAddressType(areaIdEnabled and addressEnabled)
        self.setEnabledAddress(areaIdEnabled and addressEnabled and addressType==STRICT_ADDRESS)
        MKBFilter = params.get('MKBFilter', 0)
        self.cmbMKBFilter.setCurrentIndex(MKBFilter if MKBFilter else 0)
        self.edtMKBFrom.setText(params.get('MKBFrom', 'A00'))
        self.edtMKBTo.setText(params.get('MKBTo',   'Z99.9'))
        MKBExFilter = params.get('MKBExFilter', 0)
        self.cmbMKBExFilter.setCurrentIndex(MKBExFilter if MKBExFilter else 0)
        self.edtMKBExFrom.setText(params.get('MKBExFrom', 'A00'))
        self.edtMKBExTo.setText(params.get('MKBExTo',   'Z99.9'))
        self.chkClientAddress.setChecked(addressEnabled)
        self.cmbClientAddressType.setCurrentIndex(params.get('clientAddressType', 0))
        self.cmbClientAddressCity.setCode(params.get('clientAddressCityCode', ''))
        self.cmbClientAddressStreet.setCode(params.get('clientAddressStreetCode', ''))
        self.edtAddressHouse.setText(params.get('clientHouse', ''))
        self.edtAddressCorpus.setText(params.get('clientCorpus', ''))
        self.edtAddressFlat.setText(params.get('clientFlat', ''))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbPrimary.setCurrentIndex(params.get('primary', 0))
        self.cmbResult.setValue(params.get('resultId', None))
        self.chkVisitEmergency.setChecked(params.get('visitEmergency', False))
        self.chkPerson.setChecked(params.get('person', False))
        self.chkVisitPlace.setChecked(params.get('visitPlace', False))


    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventPurposeId'] = self.cmbEventPurpose.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['specialityId'] = self.cmbSpeciality.value()
        result['personId'] = self.cmbPerson.value()
        result['workOrgId'] = self.cmbWorkOrganisation.value()
        result['sex'] = self.cmbSex.currentIndex()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['areaIdEnabled'] = self.chkArea.isChecked()
        result['chkOrgStructureArea'] = self.chkOrgStructureArea.isChecked()
        result['areaId'] = self.cmbArea.value()
        result['MKBFilter'] = self.cmbMKBFilter.currentIndex()
        result['MKBFrom']   = forceString(self.edtMKBFrom.text())
        result['MKBTo']     = forceString(self.edtMKBTo.text())
        result['MKBExFilter'] = self.cmbMKBExFilter.currentIndex()
        result['MKBExFrom']   = forceString(self.edtMKBExFrom.text())
        result['MKBExTo']     = forceString(self.edtMKBExTo.text())
        
        result['addressEnabled']  = self.chkClientAddress.isChecked()
        result['addressType'] = self.cmbAddressType.currentIndex()
        result['clientAddressType'] = self.cmbClientAddressType.currentIndex()
        result['clientAddressCityCode'] = self.cmbClientAddressCity.code()
        result['clientAddressCityCodeList'] = self.cmbClientAddressCity.getChildrenCodeList(result['clientAddressCityCode'])
        result['clientAddressStreetCode'] = self.cmbClientAddressStreet.code()
        result['clientHouse'] = self.edtAddressHouse.text()
        result['clientCorpus'] = self.edtAddressCorpus.text()
        result['clientFlat'] = self.edtAddressFlat.text()
        
        if self._visibleOrder:
            result['order'] = self.cmbOrder.currentIndex()
        if self._visiblePrimary:
            result['primary'] = self.cmbPrimary.currentIndex()
        if self._visibleResult:
            result['resultId'] = self.cmbResult.value()
        if self._visitEmergencyVisible:    
            result['visitEmergency'] = self.chkVisitEmergency.isChecked()
        result['person'] = self.chkPerson.isChecked()
        result['visitPlace'] = self.chkVisitPlace.isChecked()
        return result


    def setEnabledAddress(self, value):
        self.cmbClientAddressType.setEnabled(value)
        self.cmbClientAddressCity.setEnabled(value)
        self.cmbClientAddressStreet.setEnabled(value)
        self.lblAddressHouse.setEnabled(value)
        self.edtAddressHouse.setEnabled(value)
        self.lblAddressCorpus.setEnabled(value)
        self.edtAddressCorpus.setEnabled(value)
        self.lblAddressFlat.setEnabled(value)
        self.edtAddressFlat.setEnabled(value)
    
    def setEnabledOrgStructureArea(self, value):
        self.cmbArea.setEnabled(value)
    
    
    def setEnabledCmbAddressType(self, value):
        self.cmbAddressType.setEnabled(value)
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructureArea_clicked(self, value):
        self.setEnabledOrgStructureArea(value and self.chkArea.isChecked())
    

    @QtCore.pyqtSlot(bool)
    def on_chkArea_clicked(self, value):
        self.chkClientAddress.setEnabled(value)
        self.setEnabledCmbAddressType(value and self.chkClientAddress.isChecked())
        self.setEnabledAddress(value and self.chkClientAddress.isChecked() and self.cmbAddressType.currentIndex()==STRICT_ADDRESS)
        self.setEnabledOrgStructureArea(value and self.chkOrgStructureArea.isChecked())
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkClientAddress_clicked(self, value):
        self.setEnabledCmbAddressType(value and self.chkArea.isChecked())
        self.setEnabledAddress(value and self.chkArea.isChecked() and self.cmbAddressType.currentIndex()==STRICT_ADDRESS)


    @QtCore.pyqtSlot(int)
    def on_cmbAddressType_currentIndexChanged(self, index):
        self.setEnabledAddress(self.chkClientAddress.isChecked() and self.chkArea.isChecked() and index==STRICT_ADDRESS)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.cmbPerson.setEndDate(QtCore.QDate(date))


    @QtCore.pyqtSlot(int)
    def on_cmbClientAddressCity_currentIndexChanged(self, index):
        self.cmbClientAddressStreet.setCity(self.cmbClientAddressCity.code())


    @QtCore.pyqtSlot(int)
    def on_cmbEventPurpose_currentIndexChanged(self, index):
        eventPurposeId = self.cmbEventPurpose.value()
        if eventPurposeId:
            filter = 'EventType.purpose_id =%d' % eventPurposeId
            self.cmbResult.setFilter('eventPurpose_id=%d' % eventPurposeId)
        else:
            filter = getWorkEventTypeFilter()
            self.cmbResult.setFilter(None)
        self.cmbEventType.setFilter(filter)
        


    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)


    @QtCore.pyqtSlot()
    def on_btnSelectWorkOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbWorkOrganisation.value(), False)
        self.cmbWorkOrganisation.update()
        if orgId:
            self.cmbWorkOrganisation.setValue(orgId)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBFilter_currentIndexChanged(self, index):
        self.edtMKBFrom.setEnabled(index == 1)
        self.edtMKBTo.setEnabled(index == 1)


    @QtCore.pyqtSlot(int)
    def on_cmbMKBExFilter_currentIndexChanged(self, index):
        self.edtMKBExFrom.setEnabled(index == 1)
        self.edtMKBExTo.setEnabled(index == 1)
