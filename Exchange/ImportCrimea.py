# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   16.12.2014
'''
from PyQt4 import QtGui, QtCore

from Exchange.ImportClients     import XLSXReader
from Exchange.Ui_ImportCrimea   import Ui_ImportCrimea

from library.Utils              import forceRef, forceString, getVal


class CImportCrimea(QtGui.QDialog, Ui_ImportCrimea):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtFilePath.setReadOnly(True)
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.mapOrgStructures = {}
        self.mapHeadOrgStructures = {}
        self.mapSpecialities = {}
        self.mapPosts = {}
        self.countOrgStructureCodes = {}
        self.countPersonCodes = {}
        self.setTitle(u'Импорт списка врачей и структуры организации из XLSX')
        self.edtFilePath.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'importCrimea', '')))

    def accept(self):
        if not self.edtFilePath.text():
            QtGui.QMessageBox.warning(None, u'Ошибка', u'Файл не выбран.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return
        rows = list(XLSXReader(unicode(self.edtFilePath.text()), self.progressBar))
        if rows:
            self.progressBar.setMaximum(len(rows))
            self.progressBar.setValue(0)
        db = QtGui.qApp.db
        QtGui.qApp.processEvents()
        try:
            # self.columns = [line.upper() for line in tmpList[2]]
            # tmpList.remove(tmpList[0])
            db.transaction()
            tblPerson = db.table('Person')
            startImport = False
            currentOrg = None
            currentOrgId = None
            currentOrgStructure = None
            currentOrgStructureId = None
            for row in rows:
                if len(row) < 9:
                    # Что-то пошло не так.
                    continue
                self.progressBar.step()
                QtGui.qApp.processEvents()
                if row[0] == u'Код МО':
                    startImport = True
                    continue
                if startImport:
                    if row[0] and currentOrg != row[0]:
                        currentOrg = row[0]
                        currentOrgStructure = None
                        currentOrgId = forceRef(db.translate('Organisation', 'miacCode', currentOrg, 'id'))
                    if not (currentOrgId and row[3]):
                        # Если нет фамилии, идем лесом
                        continue
                    if row[2] and row[2] != currentOrgStructure:
                        currentOrgStructure = row[2]
                        currentOrgStructureId = self.getOrgStructureId(currentOrgStructure, currentOrgId, currentOrg)
                    personRecord = tblPerson.newRecord()
                    personRecord.setValue('lastName', QtCore.QVariant(row[3]))
                    personRecord.setValue('firstName', QtCore.QVariant(row[4]))
                    personRecord.setValue('patrName', QtCore.QVariant(row[5]))
                    personRecord.setValue('speciality_id', self.getSpecialityId(row[7]))
                    personRecord.setValue('post_id', self.getPostId(row[8]))
                    c = '%s.%s' % (currentOrg, self.getNextPersonCode(currentOrgId))
                    personRecord.setValue('code', QtCore.QVariant(c))
                    personRecord.setValue('regionalCode', QtCore.QVariant(c))
                    personRecord.setValue('federalCode', QtCore.QVariant(c))
                    personRecord.setValue('orgStructure_id', QtCore.QVariant(currentOrgStructureId))
                    personRecord.setValue('org_id', QtCore.QVariant(currentOrgId))
                    db.insertRecord(tblPerson, personRecord)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
        QtGui.qApp.preferences.appPrefs['importCrimea'] = self.edtFilePath.text()
        QtGui.QDialog.accept(self)

    def getOrgStructureId(self, orgStructure, organisationId, organisationCode):
        orgStructureId = self.mapOrgStructures.get((orgStructure, organisationId), None)
        if not orgStructureId:
            orgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure', 'name', orgStructure, 'id'))
            if not orgStructureId:
                db = QtGui.qApp.db
                table = db.table('OrgStructure')
                orgStructureRecord = table.newRecord()
                orgStructureRecord.setValue('name', QtCore.QVariant(orgStructure))
                orgStructureRecord.setValue('organisation_id', QtCore.QVariant(organisationId))
                orgStructureRecord.setValue('code', QtCore.QVariant('%s.%s' % (organisationCode, self.getNextOSCode(organisationId))))
                orgStructureId = forceRef(db.insertRecord(table, orgStructureRecord))
            self.mapOrgStructures[(orgStructure, organisationId)] = orgStructureId
        return orgStructureId

        # def getHeadOrgStuctureId(self, organisationId):
        #     orgStructureId = self.mapHeadOrgStructures.get(organisationId, None)
        #     if orgStructureId is None:
        #         orgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure', 'name', orgStructure, 'id'))
        #         if not orgStructureId:
        #             db = QtGui.qApp.db
        #             table = db.table('OrgStructure')
        #             orgStructureRecord = table.newRecord()
        #             orgStructureRecord.setValue('name', QtCore.QVariant(orgStructure))
        #             orgStructureRecord.setValue('organisation_id', QtCore.QVariant(organisationId))
        #             orgStructureRecord.setValue('code', QtCore.QVariant(self.getNextOSCode(organisationId)))
        #             orgStructureId = db.insertRecord(orgStructureRecord)
        #         self.mapOrgStructures[organisationId] = orgStructureId
        #     return orgStructureId

    def getNextOSCode(self, organisationId):
        value = self.countOrgStructureCodes.get(organisationId, 0) + 1
        self.countOrgStructureCodes[organisationId] = value
        return value

    def getNextPersonCode(self, organisationId):
        value = self.countPersonCodes.get(organisationId, 0) + 1
        self.countPersonCodes[organisationId] = value
        return value

    def getSpecialityId(self, specialityCode):
        """@return: QVariant"""
        specialityId = self.mapSpecialities.get(specialityCode, None)
        if specialityId is None:
            specialityId = QtGui.qApp.db.translate('rbSpeciality', 'code', specialityCode, 'id')
            self.mapSpecialities[specialityCode] = specialityId
        return specialityId

    def getPostId(self, postName):
        """@return: QVariant"""
        postId = self.mapPosts.get(postName, None)
        if postId is None:
            postId = QtGui.qApp.db.translate('rbPost', 'name', postName, 'id')
            self.mapPosts[postName] = postId
        return postId

    def setTitle(self, title):
        self.setWindowTitle(title)

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(self, u'Укажите файл с данными', self.edtFilePath.text(), u'Файлы XSLX(*.xlsx)')
        if fileName[0] != '':
            self.edtFilePath.setText(QtCore.QDir.toNativeSeparators(fileName[0]))

