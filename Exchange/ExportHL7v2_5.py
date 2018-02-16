#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

from Orgs.Utils import getPersonInfo
from library.DialogBase import CConstructHelperMixin

from Utils import *
from KLADR.KLADRModel import getStreetName
from Exchange.ExportActionTemplate import getActionPropertyValue
from Ui_ExportHL7v2_5_Wizard_1 import Ui_ExportHL7v2_5_Wizard_1
from Ui_ExportHL7v2_5_Wizard_2 import Ui_ExportHL7v2_5_Wizard_2
from Reports.StatReport1NPUtil import havePermanentAttach


def ExportHL7v2_5(parent):
    dirName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7v2_5DirName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7v2_5ExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7v2_5CompressRAR', 'False'))
    exportOnlyOwn = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7v2_5ExportOnlyOwn', 'True'))
    dlg = CExportHL7v2_5(dirName, exportAll, compressRAR,  exportOnlyOwn)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportHL7v2_5ExportAll'] = toVariant(
                                                                            dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportHL7v2_5DirName'] = toVariant(
                                                                            dlg.dirName)
    QtGui.qApp.preferences.appPrefs['ExportHL7v2_5CompressRAR'] = toVariant(
                                                                            dlg.compressRAR)
    QtGui.qApp.preferences.appPrefs['ExportHL7v2_5ExportOnlyOwn'] = toVariant(
                                                                            dlg.exportOnlyOwn)


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeFile(self,  device,  record,  msgType, msgSubType):
        try:
            self.setDevice(device)
            self.writeStartDocument()
            self.writeStartElement('n:%s' % msgType)
            self.writeAttribute('xmlns:n', 'urn:hl7-org:v2xml')
            self.writeAttribute('xmlns:jaxb', 'http://java.sun.com/xml/ns/jaxb')
            self.writeAttribute('xmlns:n1', 'urn:com.sun:encoder')
            self.writeAttribute('xmlns:hl7', 'urn:com.sun:encoder-hl7-1.0')
            self.writeAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            self.writeAttribute('xsi:schemaLocation', \
                'urn:hl7-org:v2xml..\HL7-2.5-XML\%s.xsd' % msgType)
            if msgType == 'ADT':
                self.writeADT_A08(record)
            elif msgType == 'MDM':
                self.writeMDM_T02(record) # Жалобы
            self.writeEndDocument()

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True

    def writeADT_A08(self, record):
        self.writeMessageHeader('ADT','A08')
        self.writeEventType('A08')
        self.writePID(record)
        self.writePV1(record)
        self.writeOBX_temp(record)
        self.writeDG1(record)
        self.writeAL1(record)


    def writeMDM_T02(self,  record):
        self.writeMessageHeader('MDM','T02')
        self.writeEventType('T02')
        self.writePID(record)
        self.writePV1(record)
        self.writeTXA(record)


    def writeDG1(self,  record):
        self.writeStartElement('n:DG1')
        self.writeTextElement('n:DG1.3',  forceString(record.value('MKB')))
        self.writeTextElement('n:DG1.3',  forceString(record.value('MKBEx')))
        self.writeStartElement('n:DG1.5')
        date = forceDate(record.value('Date'))
        self.writeTextElement(u'n:TS.1', date.toString('yyyyMMdd'))
        self.writeEndElement()
        self.writeEndElement()


    def writeAL1(self,  record):
        self.writeStartElement('n:AL1')
        self.writeTextElement('n:AL1.2',  'DA')
        self.writeTextElement('n:AL1.3',  u'PC Пенициллин')
        self.writeEndElement()


    def writeTXA(self,  record):
        personId = forceRef(record.value('person_id'))
        personInfo = getPersonInfo(personId)

        if personInfo:
            self.writeStartElement('n:TXA')
            self.writeTextElement('n:TXA.2',  u'Жалобы')
            date = forceDateTime(record.value('Date'))
            self.writeStartElement('n:TXA.3')
            self.writeTextElement(u'n:TS.1', date.toString('yyyyMMddhhmmss'))
            self.writeEndElement()
            self.writeTextElement('n:TXA.4',  u'BJ0001 %s' % personInfo['fullName'])
            self.writeEndElement()
            self.writeStartElement('n:OBX')
            self.writeTextElement('n:OBX.2',  'FT')
            self.writeTextElement('n:OBX.3',  'Rec111')
            self.writeTextElement('n:OBX.5',  '')
            self.writeTextElement('n:OBX.11',  'R')


    def writePV1(self,  record):
        personId = forceRef(record.value('visitPersonId'))
        personInfo = getPersonInfo(personId)

        if personInfo:
            self.writeStartElement('n:PV1')
            self.writeTextElement('n:PV1.2',  'I')
            self.writeTextElement('n:PV1.7',  u'BJ0001 %s' % personInfo['fullName'])
            self.writeTextElement('n:PV1.14',  'SM')
            self.writeTextElement('n:PV1.19',  u'SVST_%d' % forceInt(record.value('visit_id')))
            date = forceDate(record.value('Date'))
            self.writeStartElement('n:PV1.44')
            self.writeTextElement(u'n:TS.1', date.toString('yyyyMMdd'))
            self.writeEndElement()
            self.writeStartElement('n:PV1.45')
            self.writeTextElement(u'n:TS.1', date.toString('yyyyMMdd'))
            self.writeEndElement()
            self.writeEndElement()

    def writeOBX_temp(self,  record):
        self.writeStartElement('n:OBX')
        self.writeTextElement('n:OBX.2',  'NM')
        self.writeTextElement('n:OBX.3',  'Temp Temp')
        self.writeTextElement('n:OBX.5',  '37.6')
        self.writeTextElement('n:OBX.11',  'C')
        self.writeStartElement('n:OBX.14')
        date = forceDate(record.value('Date'))
        self.writeTextElement(u'n:TS.1', date.toString('yyyyMMdd'))
        self.writeEndElement()
        self.writeEndElement()

    def writePID(self,  record):
        clientId = forceRef(record.value('client_id'))
        clientInfo = getClientInfo(clientId)

        if clientInfo:
            self.writeStartElement('n:PID')
            self.writeTextElement('n:PID.2', u'%d' % clientId)
            self.writeTextElement('n:PID.5',  u'%s^%s^%s' % \
                                  (clientInfo['lastName'], clientInfo['firstName'],
                                   clientInfo['patrName']))
            self.writeStartElement('n:PID.7')
            self.writeTextElement('n:TS.1',  clientInfo['birthDate'].toString('yyyyMMdd'))
            self.writeEndElement()
            self.writeTextElement('n:PID.8', formatSex(clientInfo['sexCode']))
            self.writeStartElement('n:PID.11')
            self.writeTextElement('n:XAD.8',  clientInfo.get('locAddress', ''))
            self.writeEndElement() # pid.11
            self.writeTextElement('n:PID.19',  clientInfo['SNILS'])
            self.writeEndElement() #pid


    def writeMessageHeader(self,  msgType,  msgSubType):
        timeStamp = QtCore.QDateTime.currentDateTime()
        self.writeStartElement(u'n:MSH')
        self.writeTextElement(u'n:MSH.1', u'|')
        self.writeTextElement(u'n:MSH.2', u'^~\&')
        self.writeStartElement(u'n:MSH.7')
        self.writeTextElement(u'n:TS.1', timeStamp.toString('yyyyMMddhhmmss'))
        self.writeEndElement() # msh.7
        self.writeStartElement(u'n:MSH.9')
        #self.writeTextElement(u'n:MSG.1', 'PMU')
        self.writeTextElement(u'n:MSG.2', 'BP1')
        self.writeTextElement(u'n:MSG.3', '%s_%s' (msgType,  msgSubType))
        self.writeEndElement() # msh.9
        self.writeTextElement(u'n:MSH.10', u'%d' % random.randrange(100000, 99999999999999999))
        self.writeStartElement(u'n:MSH.11')
        self.writeTextElement(u'n:PT.1',  'P')
        self.writeEndElement() # msh.11
        self.writeStartElement(u'n:MSH.12')
        self.writeTextElement(u'n:VID.1',  '2.5')
        self.writeEndElement() # msh.12
        self.writeTextElement(u'n:MSG.17', 'RUS')
        self.writeEndElement() # msh


    def writeEventType(self,  eventTypeString):
        self.writeStartElement(u'n:EVN')
        self.writeTextElement(u'n:EVN.1',  eventTypeString)
        self.writeStartElement(u'n:EVN.2')
        self.writeTextElement(u'n:TS.1', QtCore.QDateTime.currentDateTime().toString('yyyyMMddhhmmss'))
        self.writeEndElement() # evn.2
        self.writeEndElement()


class CMyHL7MsgStreamWriter():
    def __init__(self,  parent = None,  encoding = 'cp1251',  personCode=0):
        self.encoding = encoding
        self.parent = parent
        self.personCode = personCode
        self.mapPersonFullName = {}
        self.mapClientAddress = {}
        self.mapClientAllergy = {}
        self.tableDiagnosisType = QtGui.qApp.db.table('rbDiagnosisType')


    def writeFile(self,  outFile,  record,  msgType,  msgSubType):
        if outFile and record and msgType and outFile.isWritable():
            self.device = outFile

            if msgType == 'ADT':
                id = forceRef(record.value('tempId'))
                typeName = forceString(record.value('tempTypeName'))
                temp = getActionPropertyValue(id, typeName)
                self.writeMessageHeader(msgType, msgSubType)
                self.writeEventType(msgSubType,  record)
                self.writePID(record)
                self.writePV1(record)

                if temp and temp != '':
                    self.writeOBX(record,  'NM',  'Temp^Temp',  temp,  'C')

                self.writeAL1(record)
                eventId = forceRef(record.value('id'))
                diagList = self.getDiagList(eventId)
                for x in diagList:
                    self.writeDG1(x)
            elif msgType == 'MDM':
                id = forceRef(record.value('complainId'))
                typeName = forceString(record.value('complainTypeName'))
                complain = getActionPropertyValue(id, typeName)

                if complain and complain != '':
                    self.writeMessageHeader(msgType, msgSubType)
                    self.writeEventType(msgSubType,  record)
                    self.writePID(record)
                    self.writePV1(record)
                    self.writeTXA(record,  u'Жалобы')
                    self.writeOBX(record,  'FT',  '%d' % id,  complain,  'R')
            return True

        return False


    def writeStr(self,  str):
        if self.device:
            return self.device.writeData(str.encode(self.encoding))


    def writePID(self,  record):
        clientId = forceRef(record.value('client_id'))
        clientInfo = getClientInfo(clientId)

        if clientInfo:
            self.writeStr('PID|||%d^^^^MR||%s^%s^%s' \
                '||%s|%s|||%s' \
                '||||||||%s\x0D' % \
                (clientId,    clientInfo.get('lastName', ''),
                                clientInfo.get('firstName', ''),
                                clientInfo.get('patrName', ''),
                                clientInfo.get('birthDate',  QDate()).toString('yyyyMMdd'),
                                formatSexEng(clientInfo.get('sexCode', 0)),
                                self.getClientAddress(clientId),
                                clientInfo.get('SNILS',  '')))


    def writeDG1(self,  record):
        diagCode = forceString(record.value('diagCode'))
        diagName = forceString(record.value('diagName'))
        diagDate = forceDate(record.value('diagDate')).toString('yyyyMMdd')
        diagPersonId = forceRef(record.value('diagPersonId'))
        diagPerson = self.getPersonFullNameStr(diagPersonId)
        diagTypeCode = forceInt(record.value('diagTypeCode'))

        if diagTypeCode == 1:
            diagType = 'F'
        elif diagTypeCode == 7:
            diagType = 'A'
        else:
            diagType = 'W'

        self.writeStr('DG1|||%s^%s|%s|%s' \
                            '|%s||||||||||%s\x0D' % \
                            (diagCode,  diagName,  diagName,  diagDate,  diagType,
                             diagPerson))


    def writeAL1(self,  record):
        clientId = forceRef(record.value('client_id'))
        infoList = self.getClientAllergyInfo(clientId)
        for type,  name,  power,  createDate,  notes in infoList:
            dateStr = createDate.toString('yyyyMMdd')
            self.writeStr(u'AL1||%s|%s|%s|%s|%s\x0D' % \
                          (type, name,  power,  notes,  dateStr))


    def writeTXA(self,  record,  str):
        personId = forceRef(record.value('visitPersonId'))
        date = forceDateTime(record.value('visitDate')).toString('yyyyMMddhhmmss')
        personFullName = self.getPersonFullNameStr(personId)
        self.writeStr('TXA||%s||%s|%s\x0D' % \
                      (str,  date,  personFullName))


    def writeOBX(self,  record, type,  name,  value,  param):
        date = forceDate(record.value('Date')).toString('yyyyMMdd')

        self.writeStr('OBX||%s|%s||%s||||||%s|||%s\x0D'% \
                      (type,  name,  value,  param,  date))


    def writePV1(self,  record):
        personId = forceRef(record.value('visitPersonId'))

        if personId:
            visitDateStr = forceDateTime(record.value('visitDate')).toString('yyyyMMddhhmmss')
            changeDateStr = forceDateTime(record.value('visitCreateDate')).toString('yyyyMMddhhmmss')

            personName = self.getPersonFullNameStr(personId)
            self.writeStr('PV1||O|||||%s|||||||SM|||||%s|||||||||||||||||||||||||%s|%s\x0D' % \
                             (personName,
                            ('%d' % forceInt(record.value('visitId'))),
                            visitDateStr, changeDateStr))


    def writeMessageHeader(self,  msgType,  msgSubType):
        #Название ЛПУ хотелосьбы иметь ввиде 'Название для печати'+'^'+'ИНФИС-код'
        titleStr = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'title'))
        infisCode = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
        self.writeStr('MSH|^~\&||SAMSON-VISTA|%s^%s||||%s^%s|||2.5\x0D' % \
                      (titleStr,  infisCode,  msgType,  msgSubType))


    def writeEventType(self,  eventTypeString, record):
        dateStr = forceDateTime(record.value('setDate')).toString('yyyyMMddhhmmss')
        self.writeStr(u'EVN|%s|%s\x0D' % (eventTypeString, dateStr))

    def getPersonFullNameStr(self,  personId):
        if self.mapPersonFullName.has_key(personId):
            return self.mapPersonFullName[personId]
        else:
            personInfo = getPersonInfo(personId)
            str = formatFullPersonNameHL7(personInfo,  self.personCode)
            self.mapPersonFullName[personId] = str
            return str

    def getClientAddress(self,  clientId):
        if self.mapClientAddress.has_key(clientId):
            return self.mapClientAddress[clientId]
        else:
            str = formatAddressHL7(clientId)
            self.mapClientAddress[clientId] = str
            return str

    def getClientAllergyInfo(self,  clientId):
        if self.mapClientAllergy.has_key(clientId):
            return self.mapClientAllergy[clientId]
        else:
            info = getClientAllergyInfo(clientId)
            if info:
                self.mapClientAllergy[clientId] = info
            return info

    def getDiagList(self,  eventId):
        list = []
        if eventId:
            db = QtGui.qApp.db
            cond = []
            cond.append(self.tableDiagnosisType['code'].inlist(['1', '2',  '7',  '9']))
            stmt = '''
            SELECT  Diagnosis.`MKB` AS `diagCode` ,
                        Diagnosis.`person_id` AS `diagPersonId`,
                        Diagnosis.`endDate` AS `diagDate`,
                        MKB_Tree.DiagName AS `diagName`,
                        rbDiagnosisType.code AS `diagTypeCode`
            FROM Diagnostic
            LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
            LEFT JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id
            LEFT JOIN MKB_Tree ON Diagnosis.MKB = MKB_Tree.DiagID
            WHERE Diagnostic.event_id = %d AND
            ''' % eventId
            stmt += db.joinAnd(cond)
            query = db.query(stmt)

            while query.next():
                list.append(query.record())

        return list

class CExportHL7v2_5WizardPage1(QtGui.QWizardPage, Ui_ExportHL7v2_5_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Фильтр событий для экспорта')

    def preSetupUi(self):
        pass


    def postSetupUi(self):
        self.cmbEventType.setTable('EventType', True)



class CExportHL7v2_5WizardPage2(QtGui.QWizardPage, Ui_ExportHL7v2_5_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.edtDirName.setText(self.parent.dirName)
        self.btnExport.setEnabled(self.parent.dirName != '')
        self.checkRAR.setChecked(self.parent.compressRAR)
        self.done = False
        self.aborted = False
        self.db = QtGui.qApp.db
        self.complainTypeIdList = self.db.getIdList('ActionPropertyType',
                                            where=u'name = \'Жалобы\'')
        self.tempTypeIdList = self.db.getIdList('ActionPropertyType',
                                        where=u'name in (\'t°\', \'Температура\')')


    def initializePage(self):
        self.done = False
        self.aborted = False


    def isComplete(self):
        return self.done


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, \
            u'Укажите директорию для экспорта', self.edtDirName.text())
        if dirName != '' :
            self.edtDirName.setText(dirName)
            self.parent.dirName = dirName
            self.btnExport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.doExport()


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.aborted = True


    @QtCore.pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


    def cleanupPage(self):
        self.btnExport.setEnabled(True)
        self.btnAbort.setEnabled(False)
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.done = False
        self.aborted = False


    def doExport(self):
        try:
            begDate = self.parent.page(0).edtBegDate.date()
            endDate = self.parent.page(0).edtEndDate.date()
            eventTypeId = self.parent.page(0).cmbEventType.value()
            onlyPermanentAttach = self.parent.page(0).chkOnlyPermanentAttach.isChecked()
            self.progressBar.setMaximum(1)
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setText(u'Запрос данных...')
            QtGui.qApp.processEvents()
            query = self.createQuery(begDate,  endDate,  eventTypeId,  onlyPermanentAttach)
            QtGui.qApp.processEvents()
            self.progressBar.step()
            self.progressBar.setMaximum(max(query.size(), 1))
            self.progressBar.setFormat('%p%')
            self.progressBar.reset()
            self.progressBar.setValue(0)
            dirName = self.edtDirName.text()

            if self.parent.page(0).chkXML.isChecked():
                myStreamWriter = CMyXmlStreamWriter(self)
                fileExt = 'xml'
            else:
                encoding = forceString(self.parent.page(0).cmbEncoding.currentText())
                personCode = forceInt(self.parent.page(0).cmbPersonCode.currentIndex())
                myStreamWriter = CMyHL7MsgStreamWriter(self,  encoding,  personCode)
                fileExt = 'msg'

            self.btnAbort.setEnabled(True)
            self.btnExport.setEnabled(False)

            while (query.next()):
                if self.aborted:
                    break

                record = query.record()
                QtGui.qApp.processEvents()

                fileName = '%s/hl7-%d.%s' % (dirName, \
                    QtCore.QDateTime.currentDateTime().toTime_t(),  fileExt)

                while QtCore.QFile.exists(fileName):
                    fileName = '%s/hl7-%d.%s' % (dirName, \
                        QtCore.QDateTime.currentDateTime().toTime_t(),  fileExt)

                outFile = QtCore.QFile(fileName)

                if self.parent.page(0).chkXML.isChecked():
                    flags = QtCore.QFile.WriteOnly | QtCore.QFile.Text
                else:
                    flags = QtCore.QFile.WriteOnly

                if not outFile.open(flags):
                    QtGui.QMessageBox.warning(self, u'Экспорт HL7 v2.5',
                                      u'Не могу открыть файл для записи %s:\n%s.' %
                                      (fileName, outFile.errorString()))
                    return

                for msgType, msgSubType in (('ADT', 'A08'),  ('MDM', 'T02')):
                    if not myStreamWriter.writeFile(outFile,  record,  msgType,  msgSubType):
                        self.progressBar.setText(u'Прервано')
                        outFile.close()
                        return

                outFile.close()

                if self.checkRAR.isChecked():
                    self.progressBar.setText(u'Сжатие')
                    try:
                        compressFileInRar(fileName, fileName+'.rar')
                        self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
                    except CRarException as e:
                        self.progressBar.setText(unicode(e))
                        QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)

                self.progressBar.step()

        except IOError, e:
            QtGui.qApp.logCurrentException()
            self.progressBar.setText(u'Прервано')
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.btnAbort.setEnabled(False)
            self.btnExport.setEnabled(True)
            return

        except Exception, e:
            self.progressBar.setText(u'Прервано')
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.btnAbort.setEnabled(False)
            self.btnExport.setEnabled(True)
            return

        if not self.aborted:
            self.done = True
            self.progressBar.setText(u'Готово')

        self.btnAbort.setEnabled(False)
        self.btnExport.setEnabled(True)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    def createQuery(self,  begDate,  endDate,  eventTypeId,  onlyPermanentAttach):
        """ Запрос информации по событиям"""

        db = self.db
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableActionType = db.table('ActionType')
        cond = []

        if begDate:
            cond.append(db.joinOr([
                tableEvent['execDate'].ge(begDate), tableEvent['execDate'].isNull()]))
        if endDate:
            cond.append(tableEvent['setDate'].le(endDate))
        if eventTypeId:
            cond.append(tableEvent['eventType_id'].eq(eventTypeId))

        if onlyPermanentAttach:
            cond.append(havePermanentAttach(endDate))

        condStr = db.joinAnd(cond)
        stmt = '''
        SELECT  Event.`id`,
                    Event.`client_id`,
                    Event.`setDate`,
                    Visit.`createDatetime` AS `visitCreateDate`,
                    Visit.`Date` AS `visitDate`,
                    Visit.`person_id` AS `visitPersonId`,
                    Visit.`id` as `visitId`,
                    ActionProperty.id AS `complainId`,
                    ActionPropertyType.typeName AS `complainTypeName`,
                    AP2.id AS `tempId`,
                    APT2.typeName AS `tempTypeName`
        FROM Event
        LEFT JOIN Visit ON Visit.event_id = Event.id
        LEFT JOIN `Action` ON Event.id = `Action`.event_id
        LEFT JOIN ActionProperty ON `Action`.id = ActionProperty.action_id
        LEFT JOIN ActionPropertyType ON ActionProperty.type_id = ActionPropertyType.id
        LEFT JOIN ActionProperty AP2 ON `Action`.id = AP2.action_id
        LEFT JOIN ActionPropertyType APT2 ON AP2.type_id = APT2.id
        WHERE `Action`.deleted = 0 AND ActionProperty.deleted = 0 AND AP2.deleted = 0
            AND %s ''' % condStr

        stmt += ' AND ActionProperty.type_id IN (' \
                            + ', '.join('%d' % x for x in self.complainTypeIdList) + ')'
        stmt += ' AND AP2.type_id IN (' \
                            + ', '.join('%d' % x for x in self.tempTypeIdList) + ')'

        query = db.query(stmt)
        return query


class CExportHL7v2_5(QtGui.QWizard):
    def __init__(self, dirName,  exportAll, compressRAR,  exportOnlyOwn,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт сообщения о визите пациента в формате ISO/HL7')
        self.selectedItems = []
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.dirName = dirName
        self.exportOnlyOwn = exportOnlyOwn
        self.begDate = QDate()
        self.endDate = QDate()
        self.eventTypeId = None
        self.onlyPermanentAttach = False
        self.addPage(CExportHL7v2_5WizardPage1(self))
        self.addPage(CExportHL7v2_5WizardPage2(self))

def formatSexEng(sex):
    sex = forceInt(sex)
    if sex == 1:
        return 'M'
    elif sex == 2:
        return 'F'
    else:
        return 'O'


def formatFullPersonNameHL7(personInfo,  codeType=0):
    personId = forceRef(personInfo.get('id', None))
    personCode = getPersonCodes(personId)[codeType]
    return '%s^%s^%s^%s' % (personCode,
        personInfo.get('lastName', ''), personInfo.get('firstName', ''),
        personInfo.get('patrName', '')) if personInfo else ''


def formatAddressHL7(clientId):
    if forceRef(clientId):
    # <улица> ^ <другое указание> ^ <город> ^ <штат, провинция или другая административная единица> ^
    # <почтовый индекс> ^ <страна> ^ <тип> ^ <другие географические указания>
        parts = []
        freeInput, KLADRCode, KLADRStreetCode, number, corpus, flat = \
            getClientAddressEx(clientId)
        other = []

        if KLADRStreetCode:
            parts.append(getStreetName(KLADRStreetCode))
        if number:
            other.append(u'д. '+number)
        if corpus:
            other.append(u'к. '+corpus)
        if flat:
            other.append(u'кв. '+flat)
        if other != []:
            parts.append(' ,'.join(other))
        if KLADRCode:
            parts.append(getCityName(KLADRCode))
        return '^'.join(parts)

    return ''

def getPersonCodes(personId):
    if personId:
        db = QtGui.qApp.db
        record = db.getRecord('Person', 'code, federalCode, regionalCode', personId)
        if record:
            return (forceString(record.value(0)),
                        forceString(record.value(1)),
                         forceString(record.value(2)))

    return None

def getClientAllergyInfo(clientId):
    list = []

    if clientId:
        recordList = QtGui.qApp.db.getRecordList('ClientAllergy',
            'nameSubstance, power, createDate, notes',
            where='client_id = %d' % clientId)
        for r in recordList:
            list.append(('MA',  forceString(r.value(0)),
                            formatAllergyPowerHL7(forceInt(r.value(1))),
                            forceDate(r.value(2)),  forceString(r.value(3))))

        recordList = QtGui.qApp.db.getRecordList('ClientIntoleranceMedicament',
            'nameMedicament, power, createDate, notes',
            where='client_id = %d' % clientId)

        for r in recordList:
            list.append(('DA',  forceString(r.value(0)),
                                formatAllergyPowerHL7(forceInt(r.value(1))),
                                forceDate(r.value(2)),  forceString(r.value(3))))

    return list

def formatAllergyPowerHL7(power):
    if forceInt(power) < 2:
        return 'MI'
    elif forceInt(power) > 2:
        return 'SV'

    return 'MO'

