# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.SendMailDialog import sendMail

from Events.Utils import getEventName, getWorkEventTypeFilter

from library.Utils  import *
from Utils          import tbl, checkEmail, compressFileInRar
from Registry.Utils import getClientInfoEx, getInfisForStreetKLADRCode, getInfisForKLADRCode

from Ui_ExportPrimaryDocInXml import Ui_ExportPrimaryDocInXmlDialog
from library.exception import CRarException


def ExportPrimaryDocInXml(parent):
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
    dlg = CExportPrimaryDocInXml(parent)
    dlg.edtFilePath.setText(forceString(QtGui.qApp.preferences.appPrefs.get('ExportPrimaryDocInXml', '')))
    QtGui.qApp.restoreOverrideCursor()
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportPrimaryDocInXml'] = toVariant(dlg.edtFilePath.text())


class CXmlStreamWriter(QXmlStreamWriter):
    def __init__(self, parent=None):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.currentTypeNeedForceEnd = None #???
        self.setAutoFormatting(True)

    def writeElement(self, elementName, value=None):
        if not value is None:
            self.writeTextElement(elementName, value)
            self.currentTypeNeedForceEnd = False
        else:
            self.writeStartElement(elementName)
            self.currentTypeNeedForceEnd = True

    def writeNamespace(self, nameSpace, prefix):
        QXmlStreamWriter.writeNamespace(self, nameSpace, prefix)

    def endElement(self):
        self.writeEndElement()

    def stopWriting(self):
        self.device().close()


class CBaseExport(object):

    def badFile(self):
        QtGui.QMessageBox.critical(self,
                                   u'Внимание!',
                                   u'Не удалось открыть файл экспорта на запись!',
                                   QtGui.QMessageBox.Close)

    def getWriter(self):
        return self.writer

    def setWriter(self, writer):
        self.writer = writer

    def writeAttribute(self, attrName, value):
        self.writer.writeAttribute(attrName, value)

    def writeElement(self, elementName, value=None):
        self.writer.writeElement(elementName, value)

    def writeNamespace(self, nameSpace, prefix):
        self.writer.writeNamespace(nameSpace, prefix)

    def setDevice(self, device):
        self.writer.setDevice(device)

    def getDevice(self):
        return self.writer.device()

    def endElement(self):
        self.writer.endElement()

    def startWriting(self):
        self.writer.writeStartDocument()

    def stopWriting(self):
        self.endElement()
        self.writer.writeEndDocument()
        self.writer.stopWriting()

    def makeRar(self, filePath, rarFilePath=''):
        try:
            compressFileInRar(filePath, rarFilePath)
        except CRarException as e:
            QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)

    def sendMail(self, email, subject, text='', attach=None):
        if not attach:
            attach = []
        sendMail(self, email, subject, text, attach)



class CExportPrimaryDocInXml(QtGui.QDialog, CBaseExport, Ui_ExportPrimaryDocInXmlDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.checkRun = False
        self.abort = False
        self.cmbSpeciality.setTable('rbSpeciality', True)
        self.progressBar.setFormat('%v')
        self.progressBar.setValue(0)
        self.tableEvent = tbl('Event')
        self.tableEventType = tbl('EventType')
        self.tableAction = tbl('Action')
        self.tableActionType = tbl('ActionType')
        self.tableClient = tbl('Client')
        self.tableVisit = tbl('Visit')
        self.tablePerson = tbl('vrbPersonWithSpeciality').alias('ExecPerson')
        self.tableTempInvalidPeriod = tbl('TempInvalid_Period')
        self.setWriter(CXmlStreamWriter())
        self.filePath = ''
        self.cmbEventPurpose.setTable('rbEventTypePurpose', False, filter='code != \'0\'')
        self.cmbEventType.setTable('EventType', False, filter=getWorkEventTypeFilter())
        self.cmbEventProfile.setTable('rbEventProfile', True)
        self.setWindowTitle(u'Экспорт первичных документов в XML')
        self.tempInvalidCond =  []
        self.xsdFile = None
        self.defaultSpecialityCodeFieldName = 'OKSOCode'
        self.cmbPersonSpecialityCode.addItem(u'ОКСО', QVariant('OKSOCode'))
        self.cmbPersonSpecialityCode.addItem(u'Региональный', QVariant('regionalCode'))
        self.cmbPersonSpecialityCode.addItem(u'МИС (внутрениий)', QVariant('code'))
        self.cmbMes._popup.setCheckBoxes('exportPrimaryDocInXml')

    def makeQuery(self, params):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        def calcBirthDate(cnt):
            result = QDate.currentDate()
            return result.addYears(-cnt)
        self.btnClose.setText(u'Стоп')
        db = QtGui.qApp.db
        dateFrom = params.get('dateFrom', None)
        dateTo   = params.get('dateTo', None)
        specialityId = params.get('specialityId', None)
        doctorPersonId = params.get('doctorPersonId', None)
        ageBegin = params.get('ageBegin', None)
        ageEnd = params.get('ageEnd', None)
        sex = params.get('sex', None)
        onlyMes = params.get('onlyMes', None)

        cond = []
        cond.append(self.tableEvent['execDate'].le(dateTo))
        cond.append(self.tableEvent['execDate'].ge(dateFrom))
        cond.append(self.tableEvent['deleted'].eq(0))
        if specialityId:
            cond.append(self.tablePerson['speciality_id'].eq(specialityId))
        if doctorPersonId:
            cond.append(self.tablePerson['id'].eq(doctorPersonId))
        if sex:
            cond.append(self.tableClient['sex'].eq(sex))
        if ageBegin:
            cond.append(self.tableClient['birthDate'].le(calcBirthDate(ageBegin)))
            cond.append(self.tableClient['birthDate'].ge(calcBirthDate(ageEnd)))
        if onlyMes:
            cond.append(self.tableEvent['MES_id'].isNotNull())
            purposeId      = params.get('purposeId', None)
            eventTypeId    = params.get('eventTypeId', None)
            eventProfileId = params.get('eventProfileId', None)
            mesId          = params.get('mesId', None)
            if purposeId:
                cond.append(self.tableEventType['purpose_id'].eq(purposeId))
            if eventTypeId:
                cond.append(self.tableEventType['id'].eq(eventTypeId))
            if eventProfileId:
                cond.append(self.tableEventType['eventProfile_id'].eq(eventProfileId))
            if mesId:
                cond.append(self.tableEvent['MES_id'].eq(mesId))
        if params.get('isPolicy', None):
            insurerId = params.get('insurerId', None)
            policyType = params.get('policyType', None)
            if policyType:
                if policyType == u'ОМС':
                    if insurerId:
                        cond.append('ClientPolicyCompulsory.`insurer_id`=%d'%insurerId)
                    else:
                        cond.append('ClientPolicyCompulsory.`insurer_id` IS NULL')
                else:
                    if insurerId:
                        cond.append('ClientPolicyVoluntary.`insurer_id`=%d'%insurerId)
                    else:
                        cond.append('ClientPolicyVoluntary.`insurer_id` IS NULL')
            else:
                if insurerId:
                    cond.append(db.joinOr(['ClientPolicyCompulsory.`insurer_id`=%d'%insurerId, 'ClientPolicyVoluntary.`insurer_id`=%d'%insurerId]))
                else:
                    cond.append(db.joinAnd(['ClientPolicyCompulsory.`insurer_id` IS NULL', 'ClientPolicyVoluntary.`insurer_id` IS NULL']))

        specialityCodeFieldName = params.get('specialityCodeFieldName', '')
        if not specialityCodeFieldName:
            specialityCodeFieldName = self.defaultSpecialityCodeFieldName

        stmt = '''
SELECT
    Client.`id` AS clientId,
    Event.`id` AS eventId, Event.`setDate`, Event.`execDate`, Event.`isPrimary`,
    Event.`order`,Event.`externalId`,
    Contract.`number` AS contractNumber,
    EventType.`code` AS eventTypeCode, EventType.`name` AS eventTypeName,
    rbFinance.`name` as eventFinanceName, rbFinance.`code` as eventFinanceCode,
    rbResult.`code` AS resultCode,
    ExecPerson.`id` AS eventExecPersonId, ExecPerson.`code` AS execPersonCode, ExecPerson.`lastName`, ExecPerson.`firstName`, ExecPerson.`patrName`,
    rbSpeciality.`%s` AS specialityCode, rbSpeciality.`name` AS specialityName,
    mes.MES.`name` AS mesName, mes.MES.`code` AS mesCode,
    rbMesSpecification.`name` AS mesSpecificationName, rbMesSpecification.`code` AS mesSpecificationCode,
    ClientPolicyCompulsory.`insurer_id` AS ClientCompulsoryInsurerId,
    ClientPolicyVoluntary.`insurer_id` AS ClientVoluntaryInsurerId
FROM Event
    LEFT OUTER JOIN Contract ON Event.`contract_id`=Contract.`id`
    INNER JOIN Client ON Client.`id`=Event.`client_id`
    INNER JOIN EventType ON EventType.`id`=Event.`eventType_id`
    LEFT OUTER JOIN rbFinance ON EventType.`finance_id`=rbFinance.`id`
    INNER JOIN rbResult ON rbResult.`id`=Event.`result_id`
    INNER JOIN Person AS ExecPerson ON ExecPerson.`id`=Event.`execPerson_id`
    INNER JOIN rbSpeciality ON rbSpeciality.`id`= ExecPerson.`speciality_id`
    LEFT OUTER JOIN mes.MES ON Event.`MES_id`=mes.MES.`id`
    LEFT OUTER JOIN rbMesSpecification ON Event.`mesSpecification_id`=rbMesSpecification.`id`
    LEFT OUTER JOIN ClientPolicy AS ClientPolicyCompulsory ON ClientPolicyCompulsory.`id`=getClientPolicyId(Client.`id`, 1)
    LEFT OUTER JOIN ClientPolicy AS ClientPolicyVoluntary ON ClientPolicyVoluntary.`id`=getClientPolicyId(Client.`id`, 0)
WHERE %s
        ''' % (specialityCodeFieldName, db.joinAnd(cond))
        query = db.query(stmt)
        QtGui.qApp.restoreOverrideCursor()
        self.parseQuery(query, params)

    def writeXsdFile(self, params):
        xsdFilePath = self.filePath[:-3]+'xsd'
        _file = QFile(xsdFilePath)
        _file.open(QIODevice.WriteOnly | QIODevice.Text)

        _file.close()



    def parseQuery(self, query, params):
        self.checkRun = True
        count = query.size()
        self.progressBar.setMaximum(count)
        n = 0
        self.filePath = forceStringEx(self.edtFilePath.text())
        if self.filePath[-4:] != '.xml':
            self.filePath = self.filePath+'.xml'
        _file = QFile(self.filePath)
        if not _file.open(QIODevice.WriteOnly | QIODevice.Text):
            self.badFile()
            return
        else:
            self.setDevice(_file)
#        if count > 0:
#            self.writeXsdFile(params)
        self.startWriting()
        self.writeElement('Export')
#        self.writeNamespace('Export', 'qweasdzxc')
        self.writeAttribute('exportVersion', '1.1')
        self.writeAttribute('date', forceString(QDate.currentDate()))
        self.writeElement('MIS', 'SAMSON-VISTA')
        try:
            from buildInfo import lastChangedRev, lastChangedDate
            self.writeElement('revision', 'v2.0/'+lastChangedRev)
        except:
            self.writeElement('revision', 'v2.0/')
        self.writeHeader(params)
        while query.next():
            QtGui.qApp.processEvents()
            if self.abort:
                self.checkRun = False
                break
            record = query.record()
            clientId = forceRef(record.value('clientId'))
            clientInfo = getClientInfoEx(clientId)
            eventId = forceRef(record.value('eventId'))
            eventExecPersonId = forceRef(record.value('eventExecPersonId'))
            self.writeElement('Event')
            self.writeAttribute('id', str(eventId))
            self.writeElement('setDate', forceString(record.value('setDate')))
            self.writeElement('execDate', forceString(record.value('execDate')))
            self.writeElement('isPrimary', forceString(record.value('isPrimary')))
            self.writeElement('order', forceString(record.value('order')))
            self.writeElement('externalId', forceString(record.value('externalId')))
            self.writeElement('eventTypeCode', forceString(record.value('eventTypeCode')))
            self.writeElement('eventTypeName', forceString(record.value('eventTypeName')))
            self.writeElement('eventFinanceCode', forceString(record.value('eventFinanceCode')))
            self.writeElement('eventFinanceName', forceString(record.value('eventFinanceName')))
            self.writeElement('contractNumber', forceString(record.value('contractNumber')))
            self.writeElement('resultCode', forceString(record.value('resultCode')))
            self.writeElement('ExecPerson')
            execPersonName = formatName(record.value('lastName'),
                                        record.value('firstName'),
                                        record.value('patrName'))
            self.writeElement('personName', execPersonName)
            self.writeElement('personCode', forceString(record.value('execPersonCode')))
            self.writeElement('specialityName', forceString(record.value('specialityName')))
            self.writeElement('specialityCode', forceString(record.value('specialityCode')))
            self.endElement() #close execPerson
            self.writeElement('MES')
            self.writeElement('mesName', forceString(record.value('mesName')))
            self.writeElement('mesCode', forceString(record.value('mesCode')))
            self.writeElement('mesSpecificationName', forceString(record.value('mesSpecificationName')))
            self.writeElement('mesSpecificationCode', forceString(record.value('mesSpecificationCode')))
            self.endElement() #close MES
            self.writeElement('Client')
            self.writeAttribute('id', record.value('clientId').toString())
            self.writeElement('sex', clientInfo.get('sex', ''))
            self.writeElement('birthDate', clientInfo.get('birthDate', ''))
            identificationRecords = self.getClientIdentification(clientId)
            for idntRecord in identificationRecords:
                self.writeElement('identifier')
                self.writeAttribute('type',  forceString(idntRecord.value('name')))
                self.writeAttribute('code',  forceString(idntRecord.value('code')))
                self.writeElement('value', forceString(idntRecord.value('identifier')))
                self.endElement() #close identifier
            if params.get('exportClientData'):
#                self.writeElement('fullName', clientInfo.get('fullName', ''))
                self.writeElement('lastName', clientInfo.lastName)
                self.writeElement('firstName', clientInfo.firstName)
                self.writeElement('patrName', clientInfo.patrName)
                self.writeElement('SNILS', clientInfo.SNILS)
                self.writeElement('document')
                self.writeElement('documentFormated', clientInfo.get('document', ''))
                documentRecord = clientInfo.get('documentRecord', None)
                if documentRecord and params.get('detailDocument'):
                    documentTypeId = forceRef(documentRecord.value('documentType_id'))
                    if documentTypeId:
                        documentTypeRecord = QtGui.qApp.db.getRecord('rbDocumentType', '*', documentTypeId)
                        if documentTypeRecord:
                            self.writeElement('documentTypeName', forceString(documentTypeRecord.value('name')))
                            self.writeElement('documentTypeCode', forceString(documentTypeRecord.value('code')))
                        self.writeElement('documentSerial', forceString(documentRecord.value('serial')))
                        self.writeElement('documentNumber', forceString(documentRecord.value('number')))
                self.endElement() #close document
#                self.writeElement('policy', clientInfo.get('policy', ''))
                self.writeElement('policy')
                compulsoryPolicyRecord = clientInfo.get('compulsoryPolicyRecord', None)
                voluntaryPolicyRecord  = clientInfo.get('voluntaryPolicyRecord', None)
                if compulsoryPolicyRecord:
                    policyRecord = compulsoryPolicyRecord
                    self.writeElement('compulsoryPolicyFormated', clientInfo.get('compulsoryPolicy', ''))
                    if params.get('detailPolicy'):
#                        self.writeElement('compulsoryPolicyName', forceString(policyRecord.value('name')))
                        self.writeElement('compulsoryPolicyInsurer', forceString(QtGui.qApp.db.translate('Organisation', 'id', policyRecord.value('insurer_id'), 'shortName')))
                        policyTypeName = forceString(QtGui.qApp.db.translate('rbPolicyType', 'id', policyRecord.value('policyType_id'), 'name'))
                        self.writeElement('compulsoryPolicyType', policyTypeName)
                        self.writeElement('compulsoryPolicySerial', forceString(policyRecord.value('serial')))
                        self.writeElement('compulsoryPolicyNumber', forceString(policyRecord.value('number')))
                        self.writeElement('compulsoryPolicyBegDate', forceString(policyRecord.value('begDate')))
                        self.writeElement('compulsoryPolicyEndDate', forceString(policyRecord.value('endDate')))

                if voluntaryPolicyRecord:
                    policyRecord = voluntaryPolicyRecord
                    self.writeElement('voluntaryPolicyFormated', clientInfo.get('voluntaryPolicy', ''))
                    if params.get('detailPolicy'):
#                        self.writeElement('voluntaryPolicyName', forceString(policyRecord.value('name')))
                        self.writeElement('voluntaryPolicyInsurer', forceString(QtGui.qApp.db.translate('Organisation', 'id', policyRecord.value('insurer_id'), 'shortName')))
                        policyTypeName = forceString(QtGui.qApp.db.translate('rbPolicyType', 'id', policyRecord.value('policyType_id'), 'name'))
                        self.writeElement('voluntaryPolicyType', policyTypeName)
                        self.writeElement('voluntaryPolicySerial', forceString(policyRecord.value('serial')))
                        self.writeElement('voluntaryPolicyNumber', forceString(policyRecord.value('number')))
                        self.writeElement('voluntaryPolicyBegDate', forceString(policyRecord.value('begDate')))
                        self.writeElement('voluntaryPolicyEndDate', forceString(policyRecord.value('endDate')))
                self.endElement() #close policy
                self.writeElement('regAddress')
                self.writeElement('regAddressFormated', clientInfo.get('regAddress', ''))
                regAdressInfo = clientInfo.get('regAddressInfo', None)
                if regAdressInfo and params.get('detailAddress'):
                    self.writeElement('regAddressKLADRCode', regAdressInfo.KLADRCode)
                    self.writeElement('regAddressKLADRStreetCode', regAdressInfo.KLADRStreetCode)
                    self.writeElement('regAddressKLADRCodeInfis', getInfisForKLADRCode(regAdressInfo.KLADRCode))
                    self.writeElement('regAddressKLADRStreetCodeInfis', getInfisForStreetKLADRCode(regAdressInfo.KLADRStreetCode))
                    self.writeElement('regAddressNumber', regAdressInfo.number)
                    self.writeElement('regAddressCorpus', regAdressInfo.corpus)
                    self.writeElement('regAddressFlat', regAdressInfo.flat)
                self.endElement() #close regAddress
                self.writeElement('locAddress')
                self.writeElement('locAddressFormated', clientInfo.get('locAddress', ''))
                locAdressInfo = clientInfo.get('locAddressInfo', None)
                if locAdressInfo and params.get('detailAddress'):
                    self.writeElement('locAddressKLADRCode', locAdressInfo.KLADRCode)
                    self.writeElement('locAddressKLADRStreetCode', locAdressInfo.KLADRStreetCode)
                    self.writeElement('locAddressKLADRCodeInfis', getInfisForKLADRCode(locAdressInfo.KLADRCode))
                    self.writeElement('locAddressKLADRStreetCodeInfis', getInfisForStreetKLADRCode(locAdressInfo.KLADRStreetCode))
                    self.writeElement('locAddressNumber', locAdressInfo.number)
                    self.writeElement('locAddressCorpus', locAdressInfo.corpus)
                    self.writeElement('locAddressFlat', locAdressInfo.flat)
                self.endElement() #close locAddress
            self.endElement() #close client
            if params.get('exportTempInvalid'):
                tempInvalidRecords = self.getClientTempInvalid(clientId, params)
                for tempInvalidRecord in tempInvalidRecords:
                    self.writeElement('TempInvalid')
                    self.writeElement('begDate', forceString(tempInvalidRecord.value('begDate')))
                    self.writeElement('endDate', forceString(tempInvalidRecord.value('endDate')))
                    self.writeElement('closed', forceString(tempInvalidRecord.value('closed')))
                    self.writeElement('invalidReasonCode', forceString(tempInvalidRecord.value('invalidReasonCode')))
                    self.writeElement('invalidReasonName', forceString(tempInvalidRecord.value('invalidReasonName')))
                    self.endElement() #close tempInvalid
            if params.get('exportActions'):
                actionRecords = self.getActionsInfo(eventId, params)
                for record in actionRecords:
                    self.writeElement('Action')
                    self.writeAttribute('id', record.value('actionId').toString())
                    actionExecPersonId = forceRef(record.value('actionExecPersonId'))
                    if actionExecPersonId:
                        if actionExecPersonId == eventExecPersonId:
                            self.writeElement('healer', 'yes')
                        else:
                            self.writeElement('healer', 'no')
                        if forceRef(record.value('execPersonOrgId')) == QtGui.qApp.currentOrgId():
                            self.writeElement('externalHealer', 'no')
                        else:
                            self.writeElement('externalHealer', 'yes')
                    else:
                        self.writeElement('healer', '')
                        self.writeElement('externalHealer', '')
                    if params.get('exportActionExecPerson', None):
                        self.writeElement('ExecPerson')
                        execPersonName = formatName(record.value('lastName'),
                                                    record.value('firstName'),
                                                    record.value('patrName'))
                        self.writeElement('personName', execPersonName)
                        self.writeElement('personCode', forceString(record.value('execPersonCode')))
                        self.writeElement('specialityName', forceString(record.value('specialityName')))
                        self.writeElement('specialityCode', forceString(record.value('specialityCode')))
                        self.endElement() #close Action execPerson
                    self.writeElement('directionDate', forceString(record.value('actionDirectionDate')))
                    self.writeElement('begDate', forceString(record.value('actionBegDate')))
                    self.writeElement('endDate', forceString(record.value('actionEndDate')))
                    self.writeElement('status', forceString(record.value('status')))
                    self.writeElement('uet', forceString(record.value('uet')))
                    self.writeElement('amount', forceString(record.value('amount')))
                    self.writeElement('note', forceString(record.value('note')))
                    self.writeElement('actionTypeClass', forceString(record.value('actionTypeClass')))
                    self.writeElement('actionTypeCode', forceString(record.value('actionTypeCode')))
                    self.writeElement('actionTypeName', forceString(record.value('actionTypeName')))
                    self.writeElement('financeCode', forceString(record.value('actionFinanceCode')))
                    self.writeElement('financeName', forceString(record.value('actionFinanceName')))
                    self.endElement() #close action
            if params.get('exportVisits'):
                visitRecords = self.getVisitsInfo(eventId, params)
                for record in visitRecords:
                    self.writeElement('Visit')
                    self.writeAttribute('id', record.value('id').toString())
                    self.writeElement('date', forceString(record.value('date')))
                    personName = formatName(record.value('lastName'),
                                        record.value('firstName'),
                                        record.value('patrName'))
                    self.writeElement('personName', personName)
                    self.writeElement('personCode', forceString(record.value('personCode')))
                    self.writeElement('specialityName', forceString(record.value('specialityName')))
                    self.writeElement('specialityCode', forceString(record.value('specialityCode')))
                    self.writeElement('sceneName', forceString(record.value('sceneName')))
                    self.writeElement('sceneCode', forceString(record.value('sceneCode')))
                    self.writeElement('visitTypeName', forceString(record.value('visitTypeName')))
                    self.writeElement('visitTypeCode', forceString(record.value('visitTypeCode')))
                    self.writeElement('isPrimary', forceString(record.value('isPrimary')))
                    self.writeElement('financeCode', forceString(record.value('visitFinanceCode')))
                    self.writeElement('financeName', forceString(record.value('visitFinanceName')))
                    self.writeElement('serviceCode', forceString(record.value('visitServiceCode')))
                    self.writeElement('serviceName', forceString(record.value('visitServiceName')))
                    self.endElement() #close visit
            diagnosticsRecords = self.getDiagnosticsInfo(eventId, params)
            for record in diagnosticsRecords:
                mkb = forceString(record.value('MKB'))
                if mkb:
                    name = formatName(record.value('lastName'),
                                        record.value('firstName'),
                                        record.value('patrName'))
                    self.writeElement('diagnostic')
                    self.writeElement('personCode', forceString(record.value('personCode')))
                    self.writeElement('personName', name)
                    self.writeElement('specialityCode', forceString(record.value('specialityCode')))
                    self.writeElement('specialityName', forceString(record.value('specialityName')))
                    self.writeElement('MKB', mkb)
                    self.writeElement('MKBEx', forceString(record.value('MKBEx')))
                    self.writeElement('diagnosisTypeName', forceString(record.value('diagnosisTypeName')))
                    self.writeElement('characterCode', forceString(record.value('characterCode')))
                    self.writeElement('characterName', forceString(record.value('characterName')))
                    self.endElement() #close diagnostic
            self.endElement() #close event
            n += 1
            self.progressBar.setValue(n)
        self.endElement() #close export
        self.stopWriting()
        self.checkRun = False
        sendRar = False
        if params.get('makeRar', None):
            sendRar = self.makeRar(self.filePath)
        email = params.get('e-mail', None)
        if email:
            if sendRar:
                whatSend = self.filePath+'.rar'
            else:
                whatSend = self.filePath
            self.sendMail(email, u'Экспорт первичных документов', '', [whatSend])
        self.btnClose.setText(u'Закрыть')
        self.tempInvalidCond =  []

    def getVisitsInfo(self, eventId, params):
        specialityCodeFieldName = params.get('specialityCodeFieldName', '')
        if not specialityCodeFieldName:
            specialityCodeFieldName = self.defaultSpecialityCodeFieldName
        stmt = '''
SELECT
    Visit.`id`, Visit.`date`, Visit.`isPrimary`, rbScene.`name` AS sceneName,
    rbScene.`code` AS sceneCode, PersonTable.`code` AS personCode, PersonTable.`lastName`,
    PersonTable.`firstName`, PersonTable.`patrName`, rbSpeciality.`%s` AS specialityCode,
    rbSpeciality.`name` AS specialityName, rbVisitType.`name` AS visitTypeName,
    rbVisitType.`code` AS visitTypeCode, rbFinance.`code` AS visitFinanceCode,
    rbFinance.`name` AS visitFinanceName, rbService.`code` AS visitServiceCode,
    rbService.`name` AS visitServiceName
FROM Visit
LEFT OUTER JOIN Person AS PersonTable ON PersonTable.`id`=Visit.`person_id`
LEFT OUTER JOIN rbSpeciality ON rbSpeciality.`id`= PersonTable.`speciality_id`
INNER JOIN rbScene ON rbScene.`id`=Visit.scene_id
INNER JOIN rbVisitType ON rbVisitType.`id`=Visit.`visitType_id`
LEFT OUTER JOIN rbFinance ON Visit.`finance_id`=rbFinance.`id`
LEFT OUTER JOIN rbService ON Visit.`service_id`=rbService.`id`
WHERE Visit.`event_id`=%d''' % (specialityCodeFieldName, eventId)
        return self.execStmt(stmt)

    def getActionsInfo(self, eventId, params):
        cond = [self.tableAction['event_id'].eq(eventId),
                self.tableAction['deleted'].eq(0)]
        if params.get('onlyNomenclativeActions', None):
            cond.append(self.tableActionType['nomenclativeService_id'].isNotNull())

        specialityCodeFieldName = params.get('specialityCodeFieldName', '')
        if not specialityCodeFieldName:
            specialityCodeFieldName = self.defaultSpecialityCodeFieldName

        stmt = '''
SELECT
    Action.`id` AS actionId, Action.`uet`, Action.`amount`, Action.`directionDate` AS actionDirectionDate,
    Action.`begDate` AS actionBegDate, Action.`endDate` AS actionEndDate, Action.`status`, Action.`note`,
    ActionType.`class` AS actionTypeClass,ActionType.`nomenclativeService_id`,
    ActionType.`code` AS actionTypeCode, ActionType.`name` AS actionTypeName,
    rbFinance.`code` AS actionFinanceCode, rbFinance.`name` AS actionFinanceName,
    ExecPerson.`id` AS actionExecPersonId ,ExecPerson.`org_id` AS execPersonOrgId,
    ExecPerson.`lastName`, ExecPerson.`firstName`, ExecPerson.`patrName`, ExecPerson.`code` AS execPersonCode,
    rbSpeciality.`name` AS specialityName, rbSpeciality.`%s` AS specialityCode
FROM Action
INNER JOIN ActionType ON ActionType.`id`=Action.`actionType_id`
LEFT OUTER JOIN rbFinance ON Action.`finance_id`=rbFinance.`id`
LEFT OUTER JOIN Person AS ExecPerson ON Action.`person_id`=ExecPerson.`id`
LEFT OUTER JOIN rbSpeciality ON rbSpeciality.`id`=ExecPerson.`speciality_id`
WHERE %s''' % (specialityCodeFieldName, QtGui.qApp.db.joinAnd(cond))
        return self.execStmt(stmt)

    def getClientIdentification(self, clientId):
        stmt = 'SELECT r.code, r.name, ci.identifier FROM ClientIdentification ci LEFT JOIN rbAccountingSystem r ON r.id = ci.accountingSystem_id WHERE ci.deleted = 0 AND ci.client_id = %d' % clientId
        return self.execStmt(stmt)

    def getClientTempInvalid(self, clientId, params):
        dateFrom = params.get('dateFrom', None)
        dateTo   = params.get('dateTo', None)
        if not self.tempInvalidCond:
            self.tempInvalidCond.append(self.tableTempInvalidPeriod['begDate'].le(dateTo))
            self.tempInvalidCond.append(self.tableTempInvalidPeriod['endDate'].ge(dateFrom))
            if params.get('exportOnlyClosedTempInvalid', None):
                self.tempInvalidCond.append('TempInvalid.`closed`=1')
        stmt = '''
SELECT
    TempInvalid_Period.`begDate`, TempInvalid_Period.`endDate`, TempInvalid.`closed`,
    rbTempInvalidReason.`code` AS invalidReasonCode, rbTempInvalidReason.`name` AS invalidReasonName
FROM TempInvalid
INNER JOIN rbTempInvalidReason ON rbTempInvalidReason.`id` = TempInvalid.`tempInvalidReason_id`
INNER JOIN TempInvalid_Period ON TempInvalid_Period.`master_id`=TempInvalid.`id`
WHERE TempInvalid.`client_id`=%d and %s''' % (clientId, QtGui.qApp.db.joinAnd(self.tempInvalidCond))
        return self.execStmt(stmt)

    def getDiagnosticsInfo(self, eventId, params):
        specialityCodeFieldName = params.get('specialityCodeFieldName', '')
        onlyEndDiagnostic = params.get('onlyEndDiagnostic', None)
        if not specialityCodeFieldName:
            specialityCodeFieldName = self.defaultSpecialityCodeFieldName
        if onlyEndDiagnostic:
            endDiagnosticCond = ' AND rbDiagnosisType.`code` in (\'1\',\'2\',\'7\') ORDER BY rbDiagnosisType.`code` '
        else:
            endDiagnosticCond = ''
        stmt = '''
SELECT
    CreatePerson.`lastName`, CreatePerson.`firstName`, CreatePerson.`patrName`,
    CreatePerson.`code` AS personCode, rbSpeciality.`%s` AS specialityCode,
    rbSpeciality.`name` AS specialityName, Diagnosis.`MKB`, Diagnosis.`MKBEx`,
    rbDiagnosisType.`name` AS diagnosisTypeName, rbDiagnosisType.`code` AS diagnosisTypeCode,
    rbDiseaseCharacter.`name` AS characterName, rbDiseaseCharacter.`code` AS characterCode
FROM Diagnostic
LEFT OUTER JOIN Person AS CreatePerson ON Diagnostic.`person_id`=CreatePerson.`id`
LEFT OUTER JOIN rbSpeciality ON rbSpeciality.`id`=CreatePerson.`speciality_id`
INNER JOIN Diagnosis ON Diagnosis.`id`=Diagnostic.`diagnosis_id`
INNER JOIN rbDiagnosisType ON rbDiagnosisType.`id`=Diagnostic.`diagnosisType_id`
LEFT OUTER JOIN rbDiseaseCharacter ON Diagnostic.`character_id`=rbDiseaseCharacter.`id`
WHERE Diagnostic.`event_id`=%d AND Diagnostic.`deleted`=0 AND Diagnosis.`deleted`=0 %s''' % (specialityCodeFieldName, eventId, endDiagnosticCond)
        if onlyEndDiagnostic:
            return self.execStmt(stmt)[:1]
        return self.execStmt(stmt)

    def execStmt(self, stmt):
        query = QtGui.qApp.db.query(stmt)
        records = []
        while query.next():
            records.append(query.record())
        return records

    def writeHeader(self, params):
        orgId = QtGui.qApp.currentOrgId()
        record = QtGui.qApp.db.getRecord('Organisation', '*', orgId)
        if record:
            shortName = forceString(record.value('shortName'))
            infisCode = forceString(record.value('infisCode'))
            INN       = forceString(record.value('INN'))
            OGRN      = forceString(record.value('OGRN'))
            miacCode  = forceString(record.value('miacCode'))

            self.writeElement('Header')
            self.writeElement('Organisation')
            self.writeAttribute('id', str(orgId))
            self.writeElement('shortName', shortName)
            self.writeElement('infisCode', infisCode)
            self.writeElement('INN', INN)
            self.writeElement('OGRN', OGRN)
            self.writeElement('miacCode', miacCode)
            self.endElement()

            dateFrom = params.get('dateFrom', None)
            dateTo   = params.get('dateTo', None)
            specialityId = params.get('specialityId', None)
            doctorPersonId = params.get('doctorPersonId', None)
            ageBegin = params.get('ageBegin', None)
            ageEnd = params.get('ageEnd', None)
            sex = params.get('sex', None)
            if sex:
                sex = u'M' if sex == 1 else u'Ж'
            onlyMes = params.get('onlyMes', None)
            purposeId      = params.get('purposeId', None)
            eventTypeId    = params.get('eventTypeId', None)
            eventProfileId = params.get('eventProfileId', None)
            mesId          = params.get('mesId', None)
            self.writeElement('QuerySettings')
            if dateFrom:
                self.writeElement('dateFrom', forceString(dateFrom))
            if dateTo:
                self.writeElement('dateTo', forceString(dateTo))
            self.writeElement('personSpecialityCodeType', self.cmbPersonSpecialityCode.currentText())
            if ageBegin != None:
                self.writeElement('ageBegin', str(ageBegin))
            if ageEnd != None:
                self.writeElement('ageEnd', str(ageEnd))
            if sex:
                self.writeElement('sex', sex)
            if purposeId:
                self.writeElement('purpose', forceString(QtGui.qApp.db.translate('rbEventTypePurpose', 'id', purposeId, 'name')))
            if eventTypeId:
                self.writeElement('eventType', getEventName(eventTypeId))
            if eventProfileId:
                self.writeElement('eventProfile', forceString(QtGui.qApp.db.translate('rbEventProfile', 'id', eventProfileId, 'name')))
            if mesId:
                self.writeElement('mes', forceString(QtGui.qApp.db.translate('mes.MES', 'id', mesId, 'name')))
            self.endElement()
            self.endElement()

    @QtCore.pyqtSlot()
    def on_btnOpenFilePath_clicked(self):
        filePath = QtGui.QFileDialog.getSaveFileName(
            self, u'Укажите каталог и название файла', self.edtFilePath.text(), u'Файлы XML (*.xml)')
        if filePath:
            self.edtFilePath.setText(QtCore.QDir.toNativeSeparators(filePath))

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        if not forceStringEx(self.edtFilePath.text()):
            QtGui.QMessageBox.critical(self,
                                   u'Внимание!',
                                   u'Укажите каталог и название файла!',
                                   QtGui.QMessageBox.Close)
            return
        params = {}
        params['dateFrom'] = self.edtDateFrom.date()
        params['dateTo']   = self.edtDateTo.date()
        params['specialityCodeFieldName'] = forceString(self.cmbPersonSpecialityCode.itemData(self.cmbPersonSpecialityCode.currentIndex()))
        params['onlyMes'] = self.chkOnlyMes.isChecked()
        params['exportClientData'] = self.chkExportClientData.isChecked()
        params['exportActions'] = self.chkExportActions.isChecked()
        params['onlyNomenclativeActions'] = self.chkOnlyNomenclativeActions.isChecked()
        params['onlyEndDiagnostic'] = self.chkOnlyEndDiagnostic.isChecked()
        params['exportActionExecPerson'] = self.chkActionExecPerson.isChecked()
        params['exportVisits'] = self.chkExportVisits.isChecked()
        params['exportTempInvalid'] = self.chkExportTempInvalid.isChecked()
        params['detailAddress'] = self.chkAddressDetail.isChecked()
        params['detailPolicy'] = self.chkPolicyDetail.isChecked()
        params['detailDocument'] = self.chkDocumentDetail.isChecked()
        if self.chkExportTempInvalid.isChecked():
            params['exportOnlyClosedTempInvalid'] = self.chkExportOnlyExecutedTempInvalid.isChecked()
        if params['onlyMes']:
            params['purposeId'] = self.cmbEventPurpose.value()
            params['eventTypeId'] = self.cmbEventType.value()
            params['eventProfileId'] = self.cmbEventProfile.value()
            params['mesId'] = self.cmbMes.value()
        params['isPolicy'] = self.chkInsurer.isChecked()
        if params['isPolicy']:
            params['insurerId'] = self.cmbInsurer.value()
            policyType = self.cmbPolicyType.currentIndex()
            if policyType:
                params['policyType'] = self.cmbPolicyType.currentText()
            else:
                params['policyType'] = None
        if self.chkSpeciality.isChecked():
            params['specialityId'] = self.cmbSpeciality.value()
        if self.chkDoctor.isChecked():
            params['doctorPersonId'] = self.cmbDoctor.value()
        if self.chkAge.isChecked():
            params['ageBegin'] = self.edtAgeBegin.value()
            params['ageEnd'] = self.edtAgeEnd.value()
        if self.chkSex.isChecked():
            params['sex'] = self.cmbSex.currentIndex()
        params['makeRar'] = self.chkMakeRar.isChecked()
        if self.chkSendEmail.isChecked():
            email = self.edtSendEmail.text()
            if checkEmail(email):
                params['e-mail'] = self.edtSendEmail.text()
            else:
                QtGui.QMessageBox.critical(self,
                                   u'Внимание!',
                                   u'Указан не корректный адрес электронной почты!',
                                   QtGui.QMessageBox.Close)
                return
        self.makeQuery(params)


    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbDoctor.setSpecialityId(specialityId)


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.checkRun:
            self.abort = True
            self.btnClose.setText(u'Закрыть')
        else:
            self.close()

    @QtCore.pyqtSlot(int)
    def on_cmbEventProfile_currentIndexChanged(self, index):
        self.cmbMes.setEventProfile(self.cmbEventProfile.value())

