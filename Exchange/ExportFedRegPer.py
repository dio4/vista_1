# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

import os.path
import shutil
import tempfile

from library.Utils     import *

from Ui_ExportFedRegPerPage1 import Ui_ExportFedRegPerPage1SetupDialog
from Ui_ExportFedRegPerPage2 import Ui_ExportFedRegPerPage2SetupDialog

strMarital = [u'Никогда не состоял (не состояла в браке)',
              u'Состоит в зарегистрированном браке',
              u'Состоит в незарегистрированном браке',
              u'Вдовец (вдова)',
              u'Разведен (разведена)',
              u'Разошелся (разошлась)',
              u'Брак с российским гражданином/гражданкой',
              u'Брак с российским гражданином/гражданкой, уехавшим с ним/ней за рубеж']


class CExportFedRegPerRMain(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportFedRegPerMainPage1(self)
        self.page2 = CExportFedRegPerMainPage2(self)
        self.page1.setTitle(u'Экспорт данных')
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла')
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта')
        self.tmpDir = ''
        self.fileName = 'FedRefPer' + forceString(QDateTime.currentDateTime().toString('yyyyMMddThhmmss'))
        self.tmp_dir = unicode(tempfile.mkdtemp('','vista-med_xml_'), locale.getpreferredencoding())

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('fedRegPer')
        return self.tmpDir

    def getFullFileName(self):
        return os.path.join(self.getTmpDir(), self.fileName)

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''

    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportFedRegPerMainPage1(QtGui.QWizardPage, Ui_ExportFedRegPerPage1SetupDialog):
    def __init__(self, parent=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.abort=False
        self.exportRun=False
        self.done=False

    def exportXML(self):
        self.btnExport.setEnabled(False)
        self.abort=False
        self.exportRun=True
        db=QtGui.qApp.db
        tmp_dir = src = self.wizard().getTmpDir()
        fileName = self.wizard().getFullFileName()
        xmlFileName = os.path.join(tmp_dir, fileName+'.xml')
        done = False

        orgStructureId = self.cmbOrgStructure.value()
        workOrgId = self.cmbOrganisation.value()

        outFile = QtCore.QFile(xmlFileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Экспорт',
                                      u'Не могу открыть файл для записи %s:\n%s.'  %\
                                      (xmlFileName, outFile.errorString()))

        myXmlStreamWriter = CExportFedRegPer(self)
        if (myXmlStreamWriter.writeFedRegPer(workOrgId, orgStructureId, outFile,  self.progressBar)):
            self.progressBar.setText(u'Готово')
            done = True
        else:
            self.progressBar.setText(u'Прервано')

        outFile.close()

        self.btnExport.setEnabled(False)
        self.btnClose.setEnabled(False)
        if not self.abort:
            self.done=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        self.abort=False
        self.exportRun=False

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.exportXML()


class CExportFedRegPerMainPage2(QtGui.QWizardPage, Ui_ExportFedRegPerPage2SetupDialog):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Экспорт данных')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "Завершить"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'FedRegPerDir', homePath))
        self.edtDir.setText(exportDir)

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        src = self.wizard().getFullFileName() + '.xml'
        dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
        success, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        return success


    @QtCore.pyqtSlot(QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))


class CExportFedRegPer(QXmlStreamWriter):

    def __init__(self,  parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)

    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeFedRegPer(self, orgId, orgStructId, device,  progressBar):
        try:
            self.setDevice(device)

            self.db = QtGui.qApp.db
            self.writeStartDocument()
            self.writeStartElement('ArrayOfEmployee')
            self.writeAttribute('xmlns:xsi=', 'http://www.w3.org/2001/XMLSchema-instance')
            self.writeAttribute('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
            self.writeAttribute('xmlns', 'Employee')
            self.writeAttribute('version', '1.4.11.0')

            cond = []
            orgStr = ''
            orgStrJoin = ''
            if orgId:
                orgStr += 'AND baseOrg.id = %s' % orgId
            if orgStructId:
                orgStrJoin += 'LEFT JOIN OrgStructure as orgStruct ON baseOrg.id = orgStruct.organisation_id AND orgStruct.id = %s AND orgStruct.deleted = 0' % orgStructId

            stmtPerson = '''
                SELECT
                  Person.id as personId,
                  Person.code as personCode,
                  baseOrg.miacCode as orgMiacCode,
                  baseOrg.fullName as orgFullName,
                  baseOrg.INN as orgINN,
                  baseOrg.KPP as orgKPP,
                  baseOrg.OGRN as orgOGRN,
                  Person.modifyDatetime,
                  Person.firstName as personFirstName,
                  Person.lastName as personLastName,
                  Person.patrName as personPatrName,
                  Person.sex as personSex,
                  Person.birthDate as personBirthDate,
                  documentType.federalCode as documentTypeId,
                  documentType.name as documentTypeName,
                  personDocument.serial as personDocumentSerial,
                  personDocument.number as personDocumentNumber,
                  personDocument.origin as personDocumentOrigin,
                  personDocument.date as personDocumentDate,
                  Person.SNILS as personSNILS,
                  Person.INN as personINN,
                  kladrStreet.NAME as streetName,
                  addressHouse.number as houseNumber,
                  addressHouse.corpus as corpusNumber,
                  Address.flat as apartmentNumber,
                  kladrStreet.INDEX as postIndex,
                  kladr.CODE as kladrCode,
                  kladr.NAME as kladrName,
                  kladr.parent as kladrParent,
                  kladr.INDEX as kladrIndex,
                  Person.maritalStatus,
                  personAwards.id as personAwardsId,
                  educationOrg.miacCode as educOrgMiacCode,
                  educationOrg.fullName as educOrgFullName,
                  personEducation.date as personEducationDate,
                  personEducation.serial as personEducationSerial,
                  personEducation.number as personEducationNumber,
                  educSpeciality.federalCode as educSpecialityId,
                  educSpeciality.name as educSpecialityName

                FROM Person
                LEFT JOIN Organisation as baseOrg ON baseOrg.id = Person.org_id AND baseOrg.deleted = 0 %s
                LEFT JOIN Person_Document as personDocument ON Person.id = personDocument.master_id AND personDocument.deleted = 0
                LEFT JOIN rbDocumentType as documentType ON personDocument.documentType_id = documentType.id
                LEFT JOIN Person_Address as personAddress ON personAddress.master_id = Person.id AND personAddress.deleted = 0 AND personAddress.type = 0
                LEFT JOIN Address ON Address.id = personAddress.address_id AND Address.deleted = 0
                LEFT JOIN AddressHouse as addressHouse ON Address.house_id = addressHouse.id and addressHouse.deleted = 0
                LEFT JOIN kladr.STREET as kladrStreet ON kladrStreet.CODE = addressHouse.KLADRStreetCode
                LEFT JOIN kladr.KLADR as kladr ON kladr.CODE = addressHouse.KLADRCode
                LEFT JOIN Person_Awards as personAwards ON personAwards.master_id = Person.id AND personAwards.deleted = 0
                LEFT JOIN Person_Education as personEducation ON personEducation.master_id = Person.id AND personEducation.deleted = 0
                LEFT JOIN rbDocumentType as educationDocumentType ON personEducation.documentType_id = educationDocumentType.id AND educationDocumentType.code = 20
                LEFT JOIN Organisation as educationOrg ON personEducation.org_id = educationOrg.id AND educationOrg.deleted = 0
                LEFT JOIN rbSpeciality as educSpeciality ON educSpeciality.id = personEducation.speciality_id
                %s

                WHERE Person.deleted = 0
            ''' % (orgStr, orgStrJoin)
            query = self.db.query(stmtPerson)
            s = query.size()
            if s > 0:
                progressBar.reset()
                progressBar.setFormat('%p%')
                progressBar.setValue(0)
                progressBar.setMaximum(s-1)

            n = 0

            while query.next():
                progressBar.setValue(n)
                n+=1
                record = query.record()
                self.writeStartElement('Employee')
                self.writeTextElement('ID', forceString(record.value('personId')))
                #в примере присутствовал тег Population, описания которого не было в xls
                self.writeTextElement('TabelNumber', forceString(record.value('personCode')))

                self.writeStartElement('UZ')
                self.writeTextElement('ID', forceString(record.value('orgMiacCode')))
                self.writeTextElement('Name', forceString(record.value('orgFullName')))
                self.writeTextElement('INN', forceString(record.value('orgINN')))
                self.writeTextElement('KPP', forceString(record.value('orgKPP')))
                if forceString(record.value('orgOGRN')):
                    self.writeTextElement('OGRN', forceString(record.value('orgOGRN')))
                #в примере имелся пустой тег Type, описания которого не было в xls
                #имеются теги LPULevel, Nomen и KladrMunicipality, которые нечем заполнить
                self.writeEndElement()

                modifyDatetime = forceDateTime(record.value('modifyDatetime'))
                strModifyDatetime = modifyDatetime.toString('yyyy-MM-dd') + 'T' + modifyDatetime.toString('hh:mm:ss') + '.0000000+04:00'
                self.writeTextElement('ChangeTime', strModifyDatetime)

                self.writeStartElement('Region')
                #данный тег заполнен статическими значениями
                self.writeTextElement('ID', '60')
                self.writeTextElement('Name', u'Ростовская область')
                self.writeTextElement('Parent', u'10003')
                self.writeTextElement('Order', '42')
                self.writeTextElement('OUZ', u'Министерство здравоохранения Ростовской области')
                self.writeTextElement('KLADR', '6100000000000')
                self.writeEndElement()

                self.writeTextElement('Name', forceString('personFirstName'))
                self.writeTextElement('Surname', forceString('personLastName'))
                self.writeTextElement('Patroname', forceString('personPatrName'))
                if forceInt(record.value('personSex')) == 2:
                    strSex = 'Female'
                else:
                    strSex = 'Male'
                self.writeTextElement('Sex', strSex)
                self.writeTextElement('Birthdate', forceDate(record.value('personBirthDate')).toString('yyyy-MM-dd') + 'T00:00:00')
                #дата смерти всегда пустая
                self.writeStartElement('Deathdate')
                self.writeAttribute('xsi:nil=', 'true')
                self.writeEndElement();

                self.writeStartElement('Document')
                self.writeStartElement('Type')
                self.writeTextElement('ID', forceString(record.value('documentTypeId')))
                self.writeTextElement('Name', forceString(record.value('documentTypeName')))
                self.writeEndElement()
                self.writeTextElement('Serie', forceString(record.value('personDocumentSerial')))
                self.writeTextElement('Number', forceString(record.value('personDocumentNumber')))
                self.writeTextElement('Issued', forceString(record.value('personDocumentOrigin')))
                self.writeTextElement('IssueDate', forceString(record.value('personDocumentDate')))
                self.writeEndElement()

                self.writeTextElement('SNILS', forceString(record.value('personSNILS')))
                #ИНН отсутствует в примере, но прописан в документации
                if forceString(record.value('personINN')):
                    self.writeTextElement('INN', forceString(record.value('personINN')))

                self.writeStartElement('Addresses')
                self.writeStartElement('AddressEntity')
                if forceString(record.value('streetName')):
                    self.writeTextElement('Street', forceString(record.value('streetName')))
                if forceString(record.value('houseNumber')):
                    self.writeTextElement('House', forceString(record.value('houseNumber')))
                if forceString(record.value('corpusNumber')):
                    self.writeTextElement('Building', forceString(record.value('corpusNumber')))
                #номер строения не выгружается, потому что в базе это значение нигде не хранится
                if forceString(record.value('apartmentNumber')):
                    self.writeTextElement('Apartment', forceString(record.value('apartmentNumber')))
                self.writeStartElement('Registration')
                self.writeTextElement('ID', '1')
                self.writeTextElement('Name', u'Постоянная регистрация')
                self.writeEndElement()
                #дата регистрации места жительства в базе не хранится
                self.writeTextElement('RegistrationDate', u'0001-01-01T00:00:00')
                #почтовый индекс берётся для улицы, поскольку соединения с таблицей KLADR.DOMA у базы нет и для отдельного дома индекс не получить
                self.writeTextElement('PostIndex', forceString(record.value('postIndex')))
                self.writeStartElement('KladrExport')
                self.writeTextElement('ID', forceString(record.value('kladrCode')))
                self.writeTextElement('Name', forceString(record.value('kladrName')))
                strParentId = forceString(record.value('kladrParent'))
                while len(strParentId) < 13:
                    strParentId += '0'
                self.writeTextElement('Parent', strParentId)
                strKladr = forceString(record.value('kladrCode'))
                if forceInt(strKladr[2:4]) == 0:
                    kladrLevel = 1
                elif forceInt(strKladr[5:7]) == 0:
                    kladrLevel = 2
                elif forceInt(strKladr[8:10]) == 0:
                    kladrLevel = 3
                else:
                    kladrLevel = 4
                self.writeTextElement('KladrLevel', forceString(kladrLevel))
                if forceString(record.value('kladrIndex')):
                    self.writeTextElement('IndexCode', forceString(record.value('kladrIndex')))
                #смысл ParentType не отражён в документации, поэтому он заполняется статически значением из примера
                self.writeTextElement('ParentType', u'-16')
                self.writeEndElement()
                self.writeEndElement()
                self.writeEndElement()

                self.writeStartElement('MarriageState')
                self.writeTextElement('ID', forceString(record.value('maritalStatus')))
                self.writeTextElement('Name', strMarital[forceInt(record.value('maritalStatus')) - 1])
                self.writeEndElement()

                #гражданство заполняется статически
                self.writeStartElement('CitezenshipState')
                self.writeTextElement('ID', '1')
                self.writeTextElement('Name', u'Гражданин Российской Федерации')
                self.writeEndElement()

                self.writeTextElement('IsRealPerson','')
                self.writeTextElement('HasAuto', '')
                self.writeTextElement('HasChildren', '')

                #значений для EmployeeSkipPayment в базе не хранится

                if forceString(record.value('personAwardsId')):
                    stmtAwards = '''
                    SELECT
                        personAwards.number,
                        personAwards.name,
                        personAwards.date
                    FROM Person_Awards as personAwards
                    WHERE personAwards.deleted = 0 AND personAwards.master_id = %s
                    ''' % forceString(record.value('personId'))
                    queryAwards = self.db.query(stmtAwards)

                    self.writeStartElement('EmployeeAwards')
                    while queryAwards.next():
                        recordAwards = queryAwards.record()
                        self.writeStartElement('Award')
                        self.writeTextElement('Number', forceString(recordAwards.value('number')))
                        self.writeTextElement('Name', forceString(recordAwards.value('name')))
                        self.writeTextElement('Issued', forceDate(recordAwards.value('date')).toString('yyyy-MM-dd') + 'T00:00:00')
                        self.writeEndElement()
                    self.writeEndElement()

                #тег EmployeeRecords не заполняется, потому что несколько обязательных вложенных тегов не заполнить

                self.writeStartElement('EmployeeSpecialities')
                self.writeStartElement('DiplomaEducation')
                self.writeStartElement('GraduatedFrom')
                self.writeTextElement('ID', forceString(record.value('educOrgMiacCode')))
                #значение Parent в базе не хранится
                self.writeTextElement('Parent', '')
                self.writeTextElement('Name', forceString(record.value('educOrgFullName')))
                self.writeEndElement()
                #значения для типа образования в базе не соотнесены с необходимыми значениями
                self.writeTextElement('GraduationDate', forceDate(record.value('personEducationDate')).toString('yyyy'))
                self.writeTextElement('DiplomaSeria', forceString(record.value('personEducationSerial')))
                self.writeTextElement('DiplomaNumber', forceString(record.value('personEducationNumber')))
                self.writeEndElement()
                self.writeStartElement('GraduationSpeciality')
                self.writeTextElement('ID', forceString(record.value('educSpecialityId')))
                #значение Parent в базе не хранится
                self.writeTextElement('Parent', '')
                self.writeTextElement('Name', forceString(record.value('educSpecialityName')))
                self.writeEndElement()
                self.writeEndElement()

                #данные в базе, для тегов EmployeePostGraduateEducation, EmployeeSertificateEducation, EmployeeSkillImprovement, EmployeeRetrainment, EmployeeQualification отсутствуют

                self.writeEndElement()

            self.writeEndElement()
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
            progressBar.setText(u'Прервано')
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            progressBar.setText(u'Прервано')
            return False

        return True