#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

from library.TableModel import *
from library.DialogBase import CConstructHelperMixin

from Utils import *
from ExportEvents import  checkPropertyList
from RefBooks.Person import getPersonDocument,  getPersonAddress, selectLatestRecord
from Registry.Utils import getAddress
from KLADR.KLADRModel import getStreetName
from Ui_ExportHL7_Wizard_1 import Ui_ExportHL7_Wizard_1
from Ui_ExportHL7_Wizard_2 import Ui_ExportHL7_Wizard_2


def ExportHL7():
    dirName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7DirName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7ExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7CompressRAR', 'False'))
    exportOnlyOwn = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportHL7ExportOnlyOwn', 'True'))
    dlg = CExportHL7(dirName, exportAll, compressRAR,  exportOnlyOwn)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportHL7ExportAll'] = toVariant(
                                                                            dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportHL7DirName'] = toVariant(
                                                                            dlg.dirName)
    QtGui.qApp.preferences.appPrefs['ExportHL7CompressRAR'] = toVariant(
                                                                            dlg.compressRAR)
    QtGui.qApp.preferences.appPrefs['ExportHL7ExportOnlyOwn'] = toVariant(
                                                                            dlg.exportOnlyOwn)


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent,  propsList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.propsList = propsList
        self.setAutoFormatting(True)
        self.msgType = ''


    def writeFile(self,  device,  record,  eventType):
        self.msgType = u'PMU_B01 ' if eventType < 3 else u'PMU_B04'
        try:
            self.setDevice(device)
            self.writeStartDocument()
            self.writeStartElement('n:%s' % self.msgType)
            self.writeAttribute('xmlns:n', 'urn:hl7-org:v2xml')
            self.writeAttribute('xmlns:jaxb', 'http://java.sun.com/xml/ns/jaxb')
            self.writeAttribute('xmlns:n1', 'urn:com.sun:encoder')
            self.writeAttribute('xmlns:hl7', 'urn:com.sun:encoder-hl7-1.0')
            self.writeAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            self.writeAttribute('xsi:schemaLocation', \
                'urn:hl7-org:v2xml..\HL7-2.5-XML\%s.xsd' % self.msgType)
            self.writeMessageHeader(eventType)
            self.writeEventType(eventType)
            self.writeStaffId(record,  eventType)

            if eventType in (1, 2):
                self.writeOrganizationUnit(record,  eventType)
                self.writeEducationalDetail(record,  eventType)
                self.writeCertificateDetail(record, eventType)

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


    def writeMessageHeader(self,  eventType):
        timeStamp = QtCore.QDateTime.currentDateTime()
        self.writeStartElement(u'n:MSH')
        self.writeTextElement(u'n:MSH.1', u'|')
        self.writeTextElement(u'n:MSH.2', u'^~\&')
        self.writeStartElement(u'n:MSH.7')
        self.writeTextElement(u'n:TS.1', timeStamp.toString(u'n:MSH.10''yyyyMMddhhmmss'))
        self.writeEndElement() # msh.7
        self.writeStartElement(u'n:MSH.9')
        self.writeTextElement(u'n:MSG.1', 'PMU')
        self.writeTextElement(u'n:MSG.2', 'B0%d' % eventType)
        self.writeTextElement(u'n:MSG.3', self.msgType)
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


    def writeEventType(self,  eventType):
        self.writeStartElement(u'n:EVN')
        self.writeStartElement(u'n:EVN.2')
        self.writeTextElement(u'n:TS.1', QtCore.QDateTime.currentDateTime().toString('yyyyMMddhhmmss'))
        self.writeEndElement() # evn.2
        self.writeEndElement()

    def writeStaffId(self, record,  eventType):
        isRetired = forceBool(record.value('retired'))
        id = forceInt(record.value('id'))
        INN = forceString(record.value('INN'))
        SNILS = forceString(record.value('SNILS'))
        document = getPersonDocument(id)
        regAddress = getPersonAddress(id,  0)
        localAddress = getPersonAddress(id,  1)
        self.writeStartElement('n:STF')
        sex = forceString(record.value('sex'))

        if INN:
            self.writeStartElement('n:STF.2')
            self.writeTextElement('n:CX.1',  INN)
            self.writeTextElement('n:CX.5',  'TAX')
            self.writeEndElement() # stf.2

        if SNILS:
            self.writeStartElement('n:STF.2')
            self.writeTextElement('n:CX.1',  SNILS)
            self.writeTextElement('n:CX.5',  'PEN')
            self.writeEndElement() # stf.2

        if forceString(record.value('federalCode')):
            self.writeStartElement('n:STF.2')
            self.writeTextElement('n:CX.1',  forceString(record.value('federalCode')))
            self.writeTextElement('n:CX.5',  'SR')
            self.writeEndElement() # stf.2

        if forceString(record.value('regionalCode')):
            self.writeStartElement('n:STF.2')
            self.writeTextElement('n:CX.1',  forceString(record.value('regionalCode')))
            self.writeTextElement('n:CX.5',  'RRI')
            self.writeEndElement() # stf.2

        if document:
            docNumber = u'%s %s' % (forceString(document.value('serial')),\
                forceString(document.value('number')))
            docDate = forceDate(document.value('date'))
            self.writeStartElement('n:STF.2')
            self.writeTextElement('n:CX.1',  docNumber)
            self.writeTextElement('n:CX.5',  'PPN')

            if document.value('origin'):
                self.writeStartElement('n:CX.6')
                self.writeTextElement('n:HD.1', forceString(document.value('origin')))
                self.writeEndElement() #cx.6

            dateStr = forceDate(document.value('date')).toString('yyyyMMdd')
            if dateStr:
                self.writeStartElement('n:CX.7')
                self.writeTextElement('n:TS.1',  dateStr)
                self.writeEndElement() # cx.7

            self.writeTextElement('n:CX.7',  'PPN')
            self.writeEndElement() # stf.2

        if sex:
            self.writeTextElement('n:STF.5',  sex)


        self.writeStartElement('n:STF.3')
        self.writeStartElement('n:XPN.1')
        self.writeTextElement('n:FN.1',  forceString(record.value('lastName')))
        self.writeEndElement() # xpn.1
        self.writeTextElement('n:XPN.2', forceString(record.value('firstName')))
        self.writeTextElement('n:XPN.3', forceString(record.value('patrName')))
        self.writeTextElement('n:XPN.7', 'L')
        self.writeEndElement() # stf.3

        dateStr = forceDate(record.value('birthDate')).toString('yyyyMMdd')
        if dateStr:
            self.writeStartElement('n:STF.6')
            self.writeTextElement('n:TS.1',  dateStr)
            self.writeEndElement() # stf.6

        self.writeTextElement('n:STF.7',  'I' if isRetired else 'A')

        if regAddress:
            regAddressId = forceRef(regAddress.value('address_id'))
            if regAddressId:
                address = getAddress(regAddressId)
                self.writeStartElement('n:STF.11')
                #self.writeTextElement('n:XAD.5', ) # zip code (index)
                self.writeTextElement('n:XAD.7', 'L')
                if address.freeInput:
                    self.writeTextElement('n:XAD.8', u'%s' % (address.freeInput))
                else:
                    self.writeTextElement('n:XAD.8',  u'%s, %s, д.%s, корпус. %s, кв. %s' % (
                        getCityName(address.KLADRCode),
                        getStreetName(address.KLADRStreetCode),
                        address.number,
                        address.corpus,
                        address.flat))
                self.writeEndElement() # stf.11

        if localAddress:
            localAddressId = forceRef(localAddress.value('address_id'))
            if localAddressId:
                address = getAddress(localAddressId)
                self.writeStartElement('n:STF.11')
                #self.writeTextElement('n:XAD.5', ) # zip code (index)
                self.writeTextElement('n:XAD.7', 'H')
                if address.freeInput:
                    self.writeTextElement('n:XAD.8', u'%s' % (address.freeInput))
                else:
                    self.writeTextElement('n:XAD.8',  u'%s, %s, д.%s, корпус. %s, кв. %s' % (
                        getCityName(address.KLADRCode),
                        getStreetName(address.KLADRStreetCode),
                        address.number,
                        address.corpus,
                        address.flat))
                self.writeEndElement() # stf.11

        if forceString(record.value('birthPlace')):
            self.writeStartElement('n:STF.11')
            #self.writeTextElement('n:XAD.5', ) # zip code (index)
            self.writeTextElement('n:XAD.3', forceString(record.value('birthPlace')))
            self.writeTextElement('n:XAD.6', 'RUS')
            self.writeTextElement('n:XAD.7', 'N')
            self.writeEndElement() # stf.11

        if eventType == 1: # прием на работу
            if forceString(record.value('org_name')):
                hireDate = getPersonHireDate(id)
                if hireDate:
                    self.writeStartElement('n:STF.12')
                    self.writeStartElement('n:DIN.1')
                    self.writeTextElement('n:TS.1',  hireDate.toString('yyyyMMdd'))
                    self.writeEndElement() # din.1
                    self.writeStartElement('n:DIN.2')
                    self.writeTextElement('n:CE.1', forceString(record.value('org_OKPO')))
                    self.writeTextElement('n:CE.2',  forceString(record.value('org_name')))
                    self.writeTextElement('n:CE.3', '1.2.643.2.40.5.0.7')
                    self.writeTextElement('n:CE.4',  forceString(record.value('org_OGRN')))
                    self.writeTextElement('n:CE.6', '1.2.643.2.40.3.1')
                    self.writeEndElement() # din.2
                    self.writeEndElement() # stf.12
                else:
                    raise CException(u'Отсутствует приказ о приеме на работу.')

        if eventType == 6: # увольнение с работы
            if forceString(record.value('org_name')):
                fireDate = getPersonFireDate(id)
                if fireDate:
                    self.writeStartElement('n:STF.12')
                    self.writeStartElement('n:DIN.1')
                    self.writeTextElement('n:TS.1',  fireDate.toString('yyyyMMdd'))
                    self.writeEndElement() # din.1
                    self.writeStartElement('n:STF.13')
                    self.writeStartElement('n:DIN.2')
                    self.writeTextElement('n:CE.1', forceString(record.value('org_OKPO')))
                    self.writeTextElement('n:CE.2',  forceString(record.value('org_name')))
                    self.writeTextElement('n:CE.3', '1.2.643.2.40.5.0.7')
                    self.writeTextElement('n:CE.4',  forceString(record.value('org_OGRN')))
                    self.writeTextElement('n:CE.6', '1.2.643.2.40.3.1')
                    self.writeEndElement() # din.2
                    self.writeEndElement() # stf.13
                else:
                    raise CException(u'Отсутствует приказ об увольнении с работы.')

        self.writeTextElement('n:STF.18',  forceString(record.value('post_name')))

        self.writeStartElement('n:STF.19')
        self.writeTextElement('n:JCC.1',  forceString(record.value('post_code')))
        self.writeTextElement('n:JCC.3',  forceString(record.value('post_name')))
        self.writeEndElement() #stf.19

        self.writeEndElement()


    def writeEducationalDetail(self,  record,  eventType):
        id = forceInt(record.value('id'))
        query = getPersonEducationQuery(id)
        i = 1

        if query.size() > 0:
            while (query.next()):
                educationRecord = query.record()
                self.writeStartElement('n:EDU')
                self.writeTextElement('n:EDU.1',  '%d' % i)
                self.writeTextElement('n:EDU.5',  forceDate(educationRecord.value('date')).toString('yyyy'))
                self.writeStartElement('n:EDU.6') # кто выдал диплом, тот и образовательное учреждение
                self.writeTextElement('n:XON.1',  forceString(educationRecord.value('origin')))
                self.writeEndElement()#edu.6
                self.writeStartElement('n:EDU.9')
                self.writeTextElement('n:CWE.9',  forceString(educationRecord.value('status')))
                self.writeEndElement()#edu.9
                self.writeEndElement()#edu
                i += 1


    def writeCertificateDetail(self,  record,  eventType):
        id = forceInt(record.value('id'))
        query = getPersonEducationQuery(id)
        i = 1

        if query.size() > 0:
            while (query.next()):
                certificateRecord = query.record()
                self.writeStartElement('n:CER')
                self.writeTextElement('n:CER.1',  '%d' % i)
                self.writeTextElement('n:CER.2',  u'%s %s' % \
                    (forceString(certificateRecord.value('serial')), \
                     forceString(certificateRecord.value('number'))))
                self.writeStartElement('n:CER.4')
                self.writeTextElement('n:XON.1',  forceString(certificateRecord.value('origin')))
                self.writeEndElement()#cer.4
                self.writeStartElement('n:CER.10')
                self.writeTextElement('n:CWE.1',  forceString(certificateRecord.value('document_code')))
                self.writeTextElement('n:CWE.2',  forceString(certificateRecord.value('document_name')))
                self.writeTextElement('n:CWE.3',  '1.2.643.2.40.5.0.11')
                self.writeEndElement()#cer.10
                self.writeTextElement('n.CER.13',  u'%s %s %s' % \
                    (forceString(record.value('lastName')), forceString(record.value('firstName')),
                        forceString(record.value('patrName'))))
                self.writeStartElement('n:CER.24')
                self.writeTextElement('n:TS.1',  forceDate(certificateRecord.value('date')).toString('yyyyMMdd'))
                self.writeEndElement() # din.1
                self.writeEndElement()#cer
                i += 1


    def writeOrganizationUnit(self,  record,  eventType):
        id = forceInt(record.value('id'))
        hireDate = getPersonHireDate(id)
        orgSubStructName = forceString(record.value('orgSubStructure_name'))
        orgStructName = forceString(record.value('orgSubStructure_name'))

        if (not hireDate) and (orgStructName == '') and (orgSubStructName == ''):
            return

        self.writeStartElement('n:ORG')
        self.writeTextElement('n:ORG.1', '1')

        if orgSubStructName:
            self.writeStartElement('n:ORG.2') # подразделение
            self.writeTextElement('n:CE.1', forceString(record.value('orgSubStructure_code')))
            self.writeTextElement('n:CE.2', orgSubStructName)
            self.writeTextElement('n:CE.3', '1.2.643.2.40.3.1.1034637001728.3')
            self.writeEndElement()#org.2

        if orgStructName:
            self.writeStartElement('n:ORG.3') # отделение
            self.writeTextElement('n:CE.1', forceString(record.value('orgStructure_code')))
            self.writeTextElement('n:CE.2', orgStructName)
            self.writeTextElement('n:CE.3', '1.2.643.2.40.5.100.474')
            self.writeEndElement()#org.3

        self.writeTextElement('n:ORG.4',  'Y') # поcтоянка. fixme

        if hireDate: # дата найма
            self.writeStartElement('n:ORG.5')
            self.writeStartElement('n:DR.1')
            self.writeTextElement('n:TS.1', hireDate.toString('yyyyMMdd'))
            self.writeEndElement()#dr.1

            fireDate = getPersonFireDate(id)
            if fireDate: # дата увольнения
                self.writeStartElement('n:DR.2')
                self.writeTextElement('n:TS.1', fireDate.toString('yyyyMMdd'))
                self.writeEndElement()#dr.2

            self.writeEndElement()#org.5


        self.writeEndElement()#org


class CExportHL7WizardPage1(QtGui.QWizardPage, Ui_ExportHL7_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Фамилия', ['lastName'],   40),
            CTextCol(   u'Имя', ['firstName'],   40),
            CTextCol(   u'Отчество', ['patrName'],   40)
            ]
        self.tableName = 'Person'
        self.order = ['lastName', 'firstName', 'patrName', 'code', 'id']
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')
        QtCore.QObject.connect(
            self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)


    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        return self.parent.exportAll or self.parent.selectedItems != []


    def preSetupUi(self):
        self.addModels('Table',CTableModel(self, self.cols, self.tableName))


    def postSetupUi(self):
        self.setModels(self.tblItems,   self.modelTable, self.selectionModelTable)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        idList = self.select()
        self.modelTable.setIdList(idList)
        self.selectionModelTable.clearSelection()
        self.tblItems.setFocus(Qt.OtherFocusReason)
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.checkExportAll.setChecked(self.parent.exportAll)


    def select(self):
        table = self.modelTable.table()
        cond  = []
        if self.checkOnlyOwn.isChecked():
            cond.append(table['org_id'].eq(QtGui.qApp.currentOrgId()))

        return QtGui.qApp.db.getIdList(table.name(), where=cond,  order=self.order)


    def renewListAndSetTo(self, itemId=None):
        idList = self.select()
        self.tblItems.setIdList(idList, itemId)


    def setSort(self, col):
        name=self.modelTable.cols()[col].fields()[0]
        self.order = name
        header=self.tblItems.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, Qt.AscendingOrder)
        self.renewListAndSetTo(self.tblItems.currentItemId())


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        self.parent.selectedItems =self.tblItems.selectedItemIdList()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.parent.selectedItems = []
        self.selectionModelTable.clearSelection()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkExportAll_clicked(self):
        self.parent.exportAll = self.checkExportAll.isChecked()
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.emit(QtCore.SIGNAL('completeChanged()'))

    @QtCore.pyqtSlot()
    def on_checkOnlyOwn_clicked(self):
        self.parent.exportOnlyOwn = self.checkOnlyOwn.isChecked()
        self.renewListAndSetTo()
        self.parent.selectedItems = []
        self.selectionModelTable.clearSelection()
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportHL7WizardPage2(QtGui.QWizardPage, Ui_ExportHL7_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.edtDirName.setText(self.parent.dirName)
        self.btnExport.setEnabled(bool(self.parent.dirName))
        self.checkRAR.setChecked(self.parent.compressRAR)
        self.done = False


    def isComplete(self):
        return self.done


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dirName = QtGui.QFileDialog.getExistingDirectory(self, \
            u'Укажите директорию для экспорта', self.edtDirName.text())
        if dirName:
            self.edtDirName.setText(dirName)
            self.parent.dirName = dirName
            self.btnExport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.doExport()


    @QtCore.pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


    def cleanupPage(self):
        self.btnExport.setEnabled(True)
        self.progressBar.reset()
        self.progressBar.setValue(0)

    def doExport(self):
        assert self.parent.exportAll or self.parent.selectedItems != []
        personProps = ('id', 'code', 'federalCode', 'regionalCode', 'lastName',\
            'firstName', 'patrName', 'office', 'retireDate',  'retired',  'SNILS',  'INN', \
            'birthDate',  'bithPlace',  'sex')

        try:

            propsList = checkPropertyList('Person',  personProps)
            query = self.createQuery(self.parent.selectedItems,  propsList)
            self.progressBar.setMaximum(max(query.size(), 1))
            self.progressBar.reset()
            self.progressBar.setValue(0)
            dirName = self.edtDirName.text()
            eventType = 1 # тип сообщения B

            if self.parent.page(0).rbAddPers.isChecked():
                filePrefix = u'B01'
            elif self.parent.page(0).rbUpdatePers.isChecked():
                filePrefix = u'B02-1'
                eventType = 2
            elif self.parent.page(0).rbDeletePers.isChecked():
                filePrefix = u'B03'
                eventType = 3
            else: # B06 - Terminate Personnel
                filePrefix = u'B06'
                eventType = 6

            myXmlStreamWriter = CMyXmlStreamWriter(self,  propsList)

            while (query.next()):
                record = query.record()
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                fileName = u'%s/%s %s %s %s.xml' % (dirName, filePrefix,  \
                    lastName, firstName, patrName)

                if QtCore.QFile.exists(fileName) and eventType == 2:
                    i = 2
                    while QtCore.QFile.exists(fileName):
                        filePrefix = 'B02-%d' % i
                        i += 1
                        fileName = u'%s/%s %s %s %s.xml' % (dirName, filePrefix,  \
                            lastName, firstName, patrName)

                outFile = QtCore.QFile(fileName)

                if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
                    QtGui.QMessageBox.warning(self, u'Экспорт сведений о сотрудниках',
                                      u'Не могу открыть файл для записи %1:\n%2.'
                                      .arg(fileName)
                                      .arg(outFile.errorString()))

                if  not myXmlStreamWriter.writeFile(outFile,  record,  eventType):
                    self.progressBar.setText(u'Прервано')
                    outFile.close()
                    return

                outFile.close()
                self.progressBar.step()

            if self.checkRAR.isChecked():
                self.progressBar.setText(u'Сжатие')
                try:
                    compressFileInRar(fileName, fileName+'.rar')
                    self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
                except CRarException as e:
                    self.progressBar.setText(unicode(e))
                    QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)

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
            return
        except Exception, e:
            self.progressBar.setText(u'Прервано')
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return

        self.done = True
        self.btnExport.setEnabled(False)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    def createQuery(self,  idList,  propsList):
        """ Запрос информации о сотрудниках. Если idList пуст,
            запрашивается информация по всем сотрудникам"""

        db = QtGui.qApp.db
        stmt = """
        SELECT  rbPost.code AS `post_code`,
                    rbPost.name AS `post_name`,
                    rbFinance.code AS `finance_code`,
                    rbFinance.name AS `finance_name`,
                    rbSpeciality.code AS `speciality_code`,
                    rbSpeciality.name AS `speciality_name`,
                    Organisation.infisCode AS `org_code`,
                    Organisation.fullName AS `org_name`,
                    Organisation.OGRN AS `org_OGRN`,
                    Organisation.OKPO AS `org_OKPO`,
                    A.infisCode AS `orgSubStructure_code`,
                    A.name AS `orgSubStructure_name`,
                    B.infisCode AS `orgStructure_code`,
                    B.name AS `orgStructure_name`"""

        if propsList != []:
            stmt+= ','+ ', '.join(['p.%s' % et for et in propsList])

        stmt +=    """
        FROM Person p
        LEFT JOIN rbPost ON p.post_id = rbPost.id
        LEFT JOIN rbSpeciality ON p.speciality_id = rbSpeciality.id
        LEFT JOIN Organisation ON p.org_id = Organisation.id
        LEFT JOIN OrgStructure A ON p.orgStructure_id = A.id
        LEFT JOIN OrgStructure B ON A.parent_id = B.id
        LEFT JOIN rbFinance ON p.finance_id = rbFinance.id
        WHERE"""

        if idList:
            stmt+= ' p.id in ('+', '.join([str(et) for et in idList])+ ') AND '
        stmt += ' p.deleted = 0'

        query = db.query(stmt)
        return query


class CExportHL7(QtGui.QWizard):
    def __init__(self, dirName,  exportAll, compressRAR,  exportOnlyOwn,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт информации о сотрудника в формате ISO/HL7 DIS 27931 (v2.5)')
        self.selectedItems = []
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.dirName = dirName
        self.exportOnlyOwn = exportOnlyOwn
        self.addPage(CExportHL7WizardPage1(self))
        self.addPage(CExportHL7WizardPage2(self))


def getPersonHireDate(personId):
    """ Возвращает дату приема сотрудника на работу. Поиск крайнего приказа
        типа Т-1(a) (прием на работу) в таблице Person_Order """

    filter = """Tmp.documentType_id IN
        (SELECT rbDocumentType.id FROM rbDocumentType
        LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id=rbDocumentType.group_id
        WHERE rbDocumentTypeGroup.code = '4' AND rbDocumentType.code IN ('T-1', 'T-1a'))"""
    record = selectLatestRecord('Person_Order',  personId,  filter)
    return forceDate(record.value('documentDate')) if record else None

def getPersonFireDate(personId):
    """ Возвращает дату увольнения сотрудника с работы. Поиск крайнего приказа
        типа Т-8(a) (прием на работу) в таблице Person_Order """

    filter = """Tmp.documentType_id IN
        (SELECT rbDocumentType.id FROM rbDocumentType
        LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id=rbDocumentType.group_id
        WHERE rbDocumentTypeGroup.code = '4' AND rbDocumentType.code IN ('T-8', 'T-8a'))"""
    record = selectLatestRecord('Person_Order',  personId,  filter)

    return forceDate(record.value('documentDate')) if record else None


def getPersonEducationQuery(personId):
        """ Запрос документов об образовании сотрудников"""

        db = QtGui.qApp.db
        stmt = """
        SELECT  dt.code AS `document_code`,
                    dt.name AS `document_name`,
                    serial, number, date, origin, status, validFromDate, validToDate
        FROM Person_Education p
        LEFT JOIN rbDocumentType dt ON p.documentType_id =dt.id
        WHERE p.deleted = '0' AND p.master_id = %d AND p.documentType_id IN
        (SELECT r.id FROM rbDocumentType r
        LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id=r.group_id
        WHERE rbDocumentTypeGroup.code = '3')""" % personId

        query = db.query(stmt)
        return query
