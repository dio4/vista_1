# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.dbfpy import dbf

from Ui_ImportFromSailDialog import Ui_ImportFromSailDialog
from Cimport import *
from Utils  import *
from DBFFormats import *


def ImportFromSail():
    dlg = CImportFromSail()
    dlg.edtFileNameOrgStructure.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportOSFromSail', '')))
    dlg.edtFileNamePerson.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPFromSail', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportOSFromSail'] = toVariant(dlg.edtFileNameOrgStructure.text())
    QtGui.qApp.preferences.appPrefs['ImportPFromSail'] = toVariant(dlg.edtFileNamePerson.text())


class CImportFromSail(CImport, QtGui.QDialog, Ui_ImportFromSailDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.prbImport.setFormat('%v')
        self.prbImport.setValue(0)
        self.abort = False
        self.importRun = False
        self.updateOS = False
        self.orgId = QtGui.qApp.currentOrgId()


    @QtCore.pyqtSlot()
    def on_btnSelectFileOrgStructure_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными на подразделения', self.edtFileNameOrgStructure.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileNameOrgStructure.setText(fileName)
            self.btnImport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnSelectFilePerson_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными на сотрудников', self.edtFileNamePerson.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileNamePerson.setText(fileName)
            self.btnImport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnViewOrgStructure_clicked(self):
        fname=unicode(forceStringEx(self.edtFileNameOrgStructure.text()))
        if fname:
            CDbfViewDialog(self, fileName=fname, encoding='cp1251').exec_()


    @QtCore.pyqtSlot()
    def on_btnViewPerson_clicked(self):
        fname=unicode(forceStringEx(self.edtFileNamePerson.text()))
        if fname:
            CDbfViewDialog(self, fileName=fname, encoding='cp1251').exec_()


    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.btnImport.setEnabled(False)
        self.btnClose.setText(u'Прервать')
        if self.prbImport:
            self.prbImport.setValue(0)
        self.abort=False
        self.importRun=True
        try:
            self.startImport()
        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.qApp.db.rollback()
            QtGui.QMessageBox.critical (self,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.abort = True
        if self.prbImport:
            self.prbImport.setValue(0)
            self.prbImport.setFormat(u'прервано' if self.abort else u'готово')
        self.btnImport.setEnabled(True)
        self.btnClose.setText(u'Закрыть')
        self.abort=False
        self.importRun=False


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.importRun:
            self.abort=True
        else:
            self.close()


    def startImport(self):
        self.n = 0
        self.personImportIdList = []
        self.importOrgStructure()
        self.importPerson()
        self.prbImport.setValue(self.n-1)


    def importOrgStructure(self):
        self.updateOS = True
        updateOrgStructure = self.chkUpdateOrgStructure.isChecked()
        attachOrgStructure = self.chkAttachOrgStructure.isChecked()
        orgStructureCodeType = self.cmbOrgStructureCodeType.currentIndex()
        orgStructureIdType = self.cmbOrgstructureId.currentIndex()
        db = QtGui.qApp.db
        tableOrgStructure = db.table('OrgStructure')
        db.transaction()
        try:
            if self.grpImportOrgStructure.isChecked() and (updateOrgStructure or attachOrgStructure):
                dbfFileName = unicode(self.edtFileNameOrgStructure.text())
                dbfSailOrgStructure = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp1251')
                sailOrgStructureFields = get_SailOrgStructure_fields()
                self.prbImport.setMaximum(len(dbfSailOrgStructure)-1)
                dbfFields = dbfSailOrgStructure.fieldNames
                for row in dbfSailOrgStructure:
                    QtGui.qApp.processEvents()
                    if self.abort: break
                    self.prbImport.setValue(self.n)
                    self.stat.setText(u'обработано: '+str(self.n))
                    self.n += 1
                    self.row = row
                    if forceInt(row['DELETED']) == 0:
                        orgStructureFields = [('organisation_id', self.orgId)]
                        for fieldName in row.dbf.fieldNames:
                            if fieldName.lower() != 'id' and fieldName.lower() != 'parent_id' and fieldName.lower() != 'type' and fieldName.lower() != 'hashospita' and fieldName.lower() != 'code':
                                orgStructureFields.append((fieldName, row[fieldName]))
                        if self.chkTypeOrgStructure.isChecked():
                            orgStructureFields.append(('type', row['TYPE']))
                        if self.chkHasHospitalBeds.isChecked():
                            orgStructureFields.append(('hasHospitalBeds', row['HASHOSPITA']))
                        if orgStructureCodeType:
                            orgStructureId = self.getOrgStructureId('CODE', 'bookkeeperCode', orgStructureFields, updateOrgStructure,  attachOrgStructure)
                            orgStructureFields.append(('bookkeeperCode', row['CODE']))
                        else:
                            orgStructureId = self.getOrgStructureId('CODE', 'code', orgStructureFields, updateOrgStructure,  attachOrgStructure)
                            orgStructureFields.append(('code', row['CODE']))
                        if orgStructureId:
                            orgStructureSailId = forceRef(row['CODE'])
                for i, row in enumerate(dbfSailOrgStructure):
                    orgStructureSailCode = forceString(row['CODE'])
                    if forceInt(row['DELETED']) == 0 and orgStructureSailCode:
                        if orgStructureCodeType:
                            fieldCodeType = 'bookkeeperCode'
                        else:
                            fieldCodeType = 'code'
                        parentCode = forceString(row['PARENT_ID'])
                        if parentCode:
                            if orgStructureIdType:
                                recordParentId = db.getRecordEx(tableOrgStructure, 'id', 'deleted = 0 AND %s = %s'%(fieldCodeType, parentCode))
                                parentId = forceRef(recordParentId.value('id')) if recordParentId else None
                            else:
                                parentId = self.getCodeFromId(parentCode, fieldCodeType)
                            if  parentId:
                                record = db.getRecordEx(tableOrgStructure, '*', '%s = \'%s\''%(fieldCodeType, orgStructureSailCode))
                                if record:
                                    record.setValue('parent_id', toVariant(parentId))
                                    orgStructureId = db.updateRecord(tableOrgStructure, record)
                            if not orgStructureId:
                                if self.log:
                                    self.log.append(u'запись '+str(i)+' (id=\"' + str(row['ID']) +u'\"): '+ u' PARENT_ID подразделения не соответствует ID подразделениям БД')
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise


    def importPerson(self):
        updateOrgStructure = self.chkUpdateOrgStructure.isChecked()
        attachOrgStructure = self.chkAttachOrgStructure.isChecked()
        orgStructureCodeType = self.cmbOrgStructureCodeType.currentIndex()
        orgStructureIdType = self.cmbOrgstructureId.currentIndex()
        specialityCodeType = self.cmbSpecialityCodeType.currentIndex()
        postCodeType = self.cmbPostCodeType.currentIndex()
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        db.transaction()
        try:
            if self.grpImportPerson.isChecked():
                if not self.updateOS and (updateOrgStructure or attachOrgStructure):
                    res = QtGui.QMessageBox.warning( self,
                                         u'Внимание!',
                                         u'Необходимо сначала импортировать данные из файла %s'%(self.edtFileNameOrgStructure.text()),
                                         QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                         QtGui.QMessageBox.Ok)
                    if res == QtGui.QMessageBox.Ok:
                        self.grpImportOrgStructure.setChecked(True)
                        self.importOrgStructure()
                dbfFileName = unicode(self.edtFileNamePerson.text())
                dbfSailPerson = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp1251')
                sailPersonFields = get_SailPerson_fields()
                self.prbImport.setMaximum(len(dbfSailPerson)-1)
                dbfFields = dbfSailPerson.fieldNames
                for i, row in enumerate(dbfSailPerson):
                    QtGui.qApp.processEvents()
                    if self.abort: break
                    self.prbImport.setValue(self.n)
                    self.stat.setText(u'обработано: '+str(self.n))
                    self.n += 1
                    self.row = row
                    personFields=[('deleted', 0), ('retireDate', None)]
                    personFields2 = [('org_id', self.orgId)]
                    for fieldName in row.dbf.fieldNames:
                        if fieldName.lower() != 'id':
                            if fieldName.lower() == 'RETIREDATE'.lower():
                                retireDate = row[fieldName] if row[fieldName] else None
                                if retireDate:
                                    retireDate = self.getDateFromUnicod(retireDate)
                                personFields2.append((fieldName, retireDate))
                            elif fieldName.lower() == 'BIRTHDATE'.lower():
                                birthDate = row[fieldName] if row[fieldName] else None
                                if birthDate:
                                    birthDate = self.getDateFromUnicod(birthDate)
                                personFields2.append((fieldName, birthDate))
                            elif fieldName.lower() == 'sex':
                                sex = 0
                                if row[fieldName].lower() == u'М'.lower():
                                    sex = 1
                                elif row[fieldName].lower() == u'Ж'.lower():
                                    sex = 2
                                personFields2.append((fieldName, sex))
                            elif fieldName.lower() == 'post_id':
                                postId = None
                                postSailId = row[fieldName]
                                if postSailId:
                                    if postCodeType:
                                        postId = forceRef(QtGui.qApp.db.translate('rbPost', 'regionalCode', postSailId, 'id'))
                                    else:
                                        postId = forceRef(QtGui.qApp.db.translate('rbPost', 'code', postSailId, 'id'))
                                    if not postId:
                                        self.log.append(u'запись '+str(i)+' (' + str(fieldName) + ' = ' + str(row[fieldName]) +u'): '+ u' должность сотрудника не соответствует должности БД')
                                personFields2.append((fieldName, postId))
                            elif fieldName.lower() == 'speciality':
                                specialityId = None
                                specialityCode = forceString(row[fieldName])
                                if not specialityCode:
                                    self.log.append(u'запись '+str(i)+' (' + str(fieldName) + ' = ' + str(row[fieldName]) +u'): '+ u'у сотрудника нет специальности')
                                else:
                                    if specialityCodeType:
                                        specialityId = forceRef(QtGui.qApp.db.translate('rbSpeciality', 'regionalCode', '%s'%(specialityCode), 'id'))
                                    else:
                                        specialityId = forceRef(QtGui.qApp.db.translate('rbSpeciality', 'OKSOCode', '%s%s'%(u'' if specialityCode.startswith('0') else u'0', specialityCode), 'id'))
                                    if not specialityId:
                                        self.log.append(u'запись '+str(i)+' (' + str(fieldName) + ' = ' + str(row[fieldName]) +u'): '+ u'специальность сотрудника не соответствует специальности БД')
                                personFields.append(('speciality_id', specialityId))
                                personFields2.append((fieldName, specialityId))
                            elif fieldName.lower() == 'code':
                                codePerson = forceString(row[fieldName])
                                if not codePerson:
                                    self.log.append(u'запись '+str(i)+' (' + str(fieldName) + ' = ' + str(row[fieldName]) +u'): '+ u'нет кода сотрудника')
                                personFields.append(('code', codePerson))
                                personFields2.append((fieldName, codePerson))
                            elif fieldName.lower() == 'orgstructu':
                                orgStructureSail = forceString(row[fieldName])
                                orgStructureId = None
                                if orgStructureSail:
                                    if orgStructureIdType:
                                        record = db.getRecordEx(self.tableOrgStructure, 'id', 'deleted = 0 AND %s = %s'%('bookkeeperCode' if orgStructureCodeType else 'code', orgStructureSail))
                                        orgStructureId = forceRef(record.value('id')) if record else None
                                    else:
                                        orgStructureId = self.getCodeFromId(orgStructureSail, 'bookkeeperCode' if orgStructureCodeType else 'code')
                                if not orgStructureId:
                                    self.log.append(u'запись '+str(i)+' (' + str(fieldName) + ' = ' + str(row[fieldName]) +u'): '+ u'у сотрудника нет подразделения')
                                personFields.append(('orgStructure_id', orgStructureId))
                                personFields2.append((fieldName, orgStructureId))
                            else:
                                personFields2.append((fieldName, row[fieldName]))
                    personId = getId(tablePerson, personFields, personFields2)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            raise


    def getDateFromUnicod(self, value):
        date = None
        def getDate(parts):
            if len(parts) == 3:
                begParts = parts[0].strip()
                medParts = parts[1].strip()
                endParts = parts[2].strip()
                if len(begParts) == 4:
                    year = int(begParts)
                    month =  int(medParts)
                    day =  int(endParts)
                    return QDate(year, month, day)
                elif len(endParts) == 4:
                    year = int(endParts)
                    month =  int(medParts)
                    day =  int(begParts)
                    return QDate(year, month, day)
            return None
        if 'T' in value:
            dateTimeBuffer = value.split('T')
        else:
            dateTimeBuffer = value.split(' ')
        if len(dateTimeBuffer) > 0:
            word = dateTimeBuffer[0].strip()
            if ':' in word:
                date = getDate(word.split(':'))
            elif '.' in word:
                date = getDate(word.split('.'))
            elif '-' in word:
                date = getDate(word.split('-'))
        return date

