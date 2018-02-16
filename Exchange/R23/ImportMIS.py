# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
from zipfile    import ZipFile, is_zipfile
from library.Utils import forceInt, \
                            forceString, forceBool, forceDate, forceRef
from library.dbfpy.dbf  import Dbf
from s11main import CS11mainApp
from Ui_ImportMIS import Ui_Dialog
from Reports.ReportView    import CReportViewDialog
from Reports.ReportBase import CReportBase, createTable

from PyQt4 import QtCore, QtGui
from library.DialogBase import CConstructHelperMixin

class CImportMIS(QtGui.QDialog, CConstructHelperMixin, Ui_Dialog):
    translateSex = {u'М': 1, u'Ж': 2,
                    u'м': 1, u'ж': 2}

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.btnImport.setEnabled(False)
        self.btnShowErrors.setEnabled(False)
        self.errors = 0
        self.lblNumSetVale()
        self.codesDict = {}
        self.prikFileNames = []
        self.importDBFs = []
        self.uchFileNames = []
        self.importUchDBFs = []
        self.importChks = []
        self.importChks.append(self.chkReplaceClientInfo)
        self.importChks.append(self.chkReplaceSNILS)
        self.importChks.append(self.chkReplaceUDL)
        self.importChks.append(self.chkReplacePolice)
        self.importChks.append(self.chkDetachDead)
        self.disableList = []
        self.disableList.append(self.chkReplaceClientInfo)
        self.disableList.append(self.chkReplaceSNILS)
        self.disableList.append(self.chkReplaceUDL)
        self.disableList.append(self.chkReplacePolice)
        self.disableList.append(self.chkDetachDead)
        self.disableList.append(self.btnImport)
        self.disableList.append(self.btnClose)
        self.chkDetachDeadEnable = True
        self.rbAttachTypeDead = None
        self.updateFlag = False
        self.packageSize = 1000
        self.packageIndex = 0
        self.package = {}
        self.updateQuantity = {}
        self.initTextHelp()

    def initTextHelp(self):
        self.txtHelp.insertHtml(u"""
<p>
Импорту подлежат файлы, возвращенные из МИАЦ после проведения контроля сверки численности застрахованного населения. Каждый раз при выполнении импорта, сохраненные данные от предыдущего импорта очищаются
</p>
<p>
Файлы импортируются в составе zip-архива без предварительной распаковки (обязательное наличие файла vPRIKXXXXX.dbf). При указании пути к файлу импорта, выбрать можно одновременно несколько файлов (ограничено только техническими характеристиками оборудования и ОС), обработка которых продет как единого массива данных
</p>
<p>
При импорте доступна замена данных в БД МИС, данными из импортируемого файла. Доступные варианты замены:  <br>
- Заменить данные пациента<br>
- Заменить СНИЛС<br>
- Заменить документ УДЛ<br>
- Заменить полисные данные<br>
- Открепить умерших<br>
</p>
<p>
Варианты могут быть выбраны в любой комбинации или выключены. При выборе любого из вариантов замены система выдаст дополнительное предупреждение:
</p>
<p>
<b>
 «ВНИМАНИЕ! При импорте выбранные данные будут перезаписаны без возможности восстановления. Продолжить импорт?»
</b>
 </p>
<p>
Замене в БД МИС подлежат только «подтвержденные» записи из импортируемого файла. Подтвержденным считается запись, для которой в импортируемом файле:<br>
MIACRES = 001<br>
TFOMSRES = (пустое)<br>
OTKR_D = (пустое)<br>
F_DSTOP = (пустое)<br>
F_DATS = (пустое)<br>
</p>
<p>
При выборе варианта <b>«Заменить данные пациента»</b> обновляются ФИО, пол, дата рождения. Если хоть одно из указанных полей в файле импорта не заполнено (кроме отчества), данные в БД не обновляются
</p>
<p>
При выборе варианта <b>«Заменить СНИЛС»</b> обновляется номер СНИЛС если он указан в импортируемом файле
</p>
<p>
При выборе варианта <b>«Заменить документ УДЛ»</b> обновляется тип документа, удостоверяющего личность, его серия и номер. Дата выдачи документа в регистрационной карте не обновляется. Если хоть одно из указанных полей в файле импорта не заполнено (даже при отсутствии в документе серии в принципе), данные в БД не обновляются
</p>
<p>
При выборе варианта <b>«Заменить полисные данные»</b> обновляются вид полиса, его серия и номер, СМО. Даты начала и окончания полиса в регистрационной карте не изменяются. Если хоть одно из указанных полей в файле импорта не заполнено (кроме серии), данные в БД не обновляются
</p>
<p>
При выборе варианта <b>«Открепить умерших»</b> пациенты в БД МИС, для которых в импортируемом файле указана дата смерти, будут откреплены от подразделений и прикреплены к типу «умер», код «8». При отсутствии в БД типа прикрепления «умер» с кодом «8», значения обработаны не будут
</p>
<p>
Не зависимо от выбранных вариантов замены информации в БД МИС, для всех «подтвержденных» пациентов будут обновлены данные идентификаторов РИС и ЕНП
</p>
        """)


    def openZip(self, zipFileName):
        if not is_zipfile(forceString(zipFileName)):
            self.logBrowser.append(u'Файл %s не является архивом.' %QtCore.QDir.toNativeSeparators(zipFileName))
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            return False

        archive = ZipFile(forceString(zipFileName), "r")
        names = archive.namelist()
        isDbfFile = True

        prikFileName, importDBF = None, None
        uchFileName, importUchDBF = None, None

        for fileName in names:
            if unicode(fileName.lower()).startswith('vprik') or unicode(fileName.lower()).startswith('prik'):
                prikFileName, importDBF = self.openFile(archive, fileName)
            elif unicode(fileName.lower()).startswith('vuch') or unicode(fileName.lower()).startswith('uch'):
                uchFileName, importUchDBF = self.openFile(archive, fileName)

        if not importDBF:
            self.logBrowser.append(u'В архиве %s нет обязательного файла vPRIK*.dbf. Выберите другой архив.' %QtCore.QDir.toNativeSeparators(zipFileName))
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            return False
        self.prikFileNames.append(prikFileName)
        self.importDBFs.append(importDBF)
        if importUchDBF:
            self.uchFileNames.append(uchFileName)
            self.importUchDBFs.append(importUchDBF)
        self.logBrowser.append(u'Архив %s' %QtCore.QDir.toNativeSeparators(zipFileName))
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        return True


    def openFile(self, archive, fileName):
        isDbfFile = True
        varFileName = fileName
        if not unicode(fileName.lower()).endswith('.dbf'):
            isDbfFile = False
            if not isDbfFile:
                self.logBrowser.append(u'Файл %s не является dbf-файлом.')
                self.logBrowser.update()
                return None, None
        outFile = QtCore.QTemporaryFile()

        if not outFile.open(QtCore.QFile.WriteOnly):
            self.logBrowser.append(u'Не удаётся открыть файл для записи %s:\n%s.' % (outFile, outFile.errorString()))
            self.logBrowser.update()
            return None, None

        data = archive.read(fileName)
        outFile.write(data)
        outFile.close()
        fileInfo = QtCore.QFileInfo(outFile)

        dbf = Dbf(forceString(fileInfo.filePath()), encoding='cp866')
        return fileName, dbf

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileNames = QtGui.QFileDialog.getOpenFileNames(
            self, u'Укажите файлы с данными', self.edtFileName.text(), u'Файлы ZIP (*.zip)')
        self.importDBFs = []
        self.prikFileNames = []
        self.importUchDBFs = []
        self.uchFileNames = []
        if fileNames:
            isValid = True
            self.logBrowser.append(u'Список файлов:')
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            for fileName in fileNames:
                isValid &= self.openZip(fileName)
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(u'; '.join([forceString(fileName) for fileName in fileNames])))
            self.btnImport.setEnabled(isValid)
            self.lblNumSetVale()
            self.btnShowErrors.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.setEnabledAll(False)
        self.updateFlag = any([chk.isChecked() for chk in self.importChks])
        if self.updateFlag:
            result = QtGui.QMessageBox.warning(self,
                                               u'Внимание!', u'При импорте выбранные данные будут перезаписаны без возможности восстановления. Продолжить импорт?',
                                               QtGui.QMessageBox.Ok | QtGui.QMessageBox.Close, QtGui.QMessageBox.Close)
            if result == QtGui.QMessageBox.Close:
                self.setEnabledAll(True)
                return
        self.printImportBegin()
        if not self.checkOrgstructureCodes():
            return
        if not self.checkAccountingSystem():
            return
        self.checkRbAttachTypeDead()

        self.clientsReset()

        self.initRefBooks()

        self.createTmpTables()
        self.initUpdateFieldsSets()
        self.initUpdateQuantity()
        self.updateFieldsByClient = {}
        self.existDict = {}
        self.clientData = {}

        for i, importDBF in enumerate(self.importDBFs):
            self.importClients(importDBF, i)

        self.updateClientData()

        for i, importUchDBF in enumerate(self.importUchDBFs):
            self.importUchs(importUchDBF, i)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        QtGui.qApp.processEvents()

        self.updateTables()

        self.deleteTmpTables()

        self.lblNumSetVale(sum([len(importDBF) for importDBF in self.importDBFs]), self.errors)
        self.printImportEnd()
        self.btnShowErrors.setEnabled(True)
        self.setEnabledAll(True)
        QtGui.qApp.processEvents()

    def updateClientData(self):
        db = QtGui.qApp.db
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(self.clientData))
        self.progressBar.setValue(0)
        self.logBrowser.append(u'Сохранение подтверждённых записей')
        self.logBrowser.update()
        self.packageData = self.setUpdateClientCheckingHeader()
        def submit():
            if len(self.packageData) > 1:
                stmt = u'%s\n%s' %(self.packageData[0], u',\n'.join(self.packageData[1:]))
                if stmt:
                    db.query(stmt)
            self.packageData = self.setUpdateClientCheckingHeader()

        QtGui.qApp.processEvents()
        for id, record in self.clientData.items():
            self.packageData += self.getClientCheckingValue(record)
            if len(self.packageData) > self.packageSize:
                submit()
            self.progressBar.step()
            QtGui.qApp.processEvents()
        submit()
        self.logBrowser.append(u'Сохранение подтверждённых записей - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def importClients(self, importDBF, index):
        self.logBrowser.append(u'Файл %s' %self.prikFileNames[index])
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        self.existDict.update(self.checkClientsExist(importDBF))
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(importDBF))
        self.progressBar.setValue(0)
        self.logBrowser.append(u'Проверка данных о клиентах')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        self.initPackage()
        for i, record in enumerate(importDBF):
            checkResult = self.checkClient(record)
            if checkResult in ['Error', 'Dead']:
                self.errors += 1
                self.errorIdLists[index].append(i)
            if checkResult in ['Accept', 'Dead']:
                self.updateClient(record, checkResult)

            self.progressBar.step()
            QtGui.qApp.processEvents()
        self.submitPackage()

        self.logBrowser.append(u'Проверка данных о клиентах - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def importUchs(self, importDBF, index):
        if importDBF:
            self.logBrowser.append(u'Проверка данных об участках. Файл %s' %self.uchFileNames[index])
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            for i, record in enumerate(importDBF):
                if not self.checkUch(record):
                    self.errorUchIdLists[index].append(i)
            self.logBrowser.append(u'Проверка данных об участках - Завершено')
            self.logBrowser.update()

    def checkClientsExist(self, importDBF):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(len(importDBF))
        self.progressBar.setValue(0)
        self.logBrowser.append(u'Проверка наличия клиентов в базе')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        check = {}
        dict = {}
        for i, record in enumerate(importDBF):
            if not self.existDict.has_key(record['ID']):
                dict[record['ID']] = 0
            if len(dict.keys()) > self.packageSize:
                check.update(self.submitExistsPackage(dict))
                dict = {}
            self.progressBar.step()
            QtGui.qApp.processEvents()
        check.update(self.submitExistsPackage(dict))
        self.logBrowser.append(u'Проверка наличия клиентов в базе - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        return check

    def submitExistsPackage(self, dict):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        if not len(dict.keys()) > 0:
            return {}
        cond = [tableClient['id'].inlist(dict.keys()),
                tableClient['deleted'].eq(0)]
        query = db.query(db.selectStmt(tableClient, 'id', cond))
        while query.next():
            id = forceRef(query.record().value('id'))
            dict[id] = 1
        return dict

    def checkClient(self, record):
        db = QtGui.qApp.db
        otkrDate = forceDate(record['OTKR_D'])
        if otkrDate.isValid():
            return 'Ignore'     # Not an error, we just ignore such records
        clientExists = self.existDict.get(record['ID'], 0)
        if not clientExists:
            self.logBrowser.append(u'ВНИМАНИЕ!!! Пациент с кодом %s не найден в базе данных' %record['ID'])
            self.logBrowser.update()
            return 'Ignore'
        MIACRES = forceBool(record['MIACRES'] == '001')
        TFOMSRES = forceBool(not record['TFOMSRES'])
        F_DSTOP = forceBool(not record['F_DSTOP'])
        F_DATS = forceBool(not record['F_DATS'])
        if not F_DATS and MIACRES:
            return 'Dead'
        if not all([MIACRES, TFOMSRES, F_DSTOP, F_DATS]):
            return 'Error'
        return 'Accept'

    def updateClient(self, record, type):
        if not self.packageIndex < self.packageSize:
            self.submitPackage()
            self.initPackage()
        self.updateFieldsByClient.setdefault(record['ID'], {'Ident': {'IDSTR': 0, 'F_ENP': 0}, 'Checking': 0, 'Info': 0, 'SNILS': 0, 'Document': 0, 'Policy': 0, 'Dead': 0})
        if not self.clientData.has_key(record['ID']):
            dict = {}
            for field in self.updateClientCheckingFields:
                dict[field] = ''
            dict['ID'] = record['ID']
            self.clientData[record['ID']] = dict

        if type == 'Accept':
            accountingSystemInfoList = [{'id': self.risId, 'field': 'IDSTR'},
                                        {'id': self.enpId, 'field': 'F_ENP'}]
            self.package['clientIdent'] += self.getClientIdentValue(record, accountingSystemInfoList)
            self.package['clientInfo'] += self.getClientInfoValue(record)
            self.package['clientSNILS'] += self.getClientSNILSValue(record)
            self.package['clientDocument'] += self.getClientDocumentValue(record)
            self.package['clientPolicy'] += self.getClientPolicyValue(record)
        elif type == 'Dead':
            if self.chkDetachDead.isChecked() and self.chkDetachDeadEnable:
                self.package['clientDetachDead'] += self.getClientDetachDeadValue(record)
        self.packageIndex += 1

    def initPackage(self):
        self.package['clientIdent'] = self.setUpdateClientIdentHeader()
        self.package['clientInfo'] = self.setUpdateClientInfoHeader()
        self.package['clientSNILS'] = self.setUpdateClientSNILSHeader()
        self.package['clientDocument'] = self.setUpdateClientDocumentHeader()
        self.package['clientPolicy'] = self.setUpdateClientPolicyHeader()
        self.package['clientDetachDead'] = self.setUpdateClientDetachDeadHeader()
        self.packageIndex = 0

    def submitPackage(self):
        db = QtGui.qApp.db
        self.packageKeys = ['clientIdent', 'clientInfo', 'clientSNILS', 'clientDocument', 'clientPolicy', 'clientDetachDead']
        queryList = []
        for key in self.packageKeys:
            packageItem = self.package.get(key, [])
            if len(packageItem) > 1:
                stmt = u'%s\n%s' %(packageItem[0], u',\n'.join(packageItem[1:]))
                if stmt:
                    queryList.append(stmt)
                    self.updateQuantity[key] = self.updateQuantity.get(key, 0) + len(packageItem) - 1
        if queryList:
            db.query(u';\n'.join(queryList))
        self.package = {}

    #Формирование запросов для вставки во временные таблицы

    def getClientIdentValue(self, record, accountingSystemInfoList):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        currentDate = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd'))
        result = []
        for ASInfo in accountingSystemInfoList:
            if not self.updateFieldsByClient[record['ID']]['Ident'][ASInfo['field']]:
                if forceBool(record[ASInfo['field']]):
                    updateData = {
                                'client_id': u"'%d'" % record['ID'],
                                'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                                'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                                'accountingSystem_id': u"'%s'" %ASInfo['id'],
                                'identifier': u"'%s'" %record[ASInfo['field']],
                                'checkDate': u"'%s'" %forceString(currentDate)
                    }
                    result += [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateClientIdentFields])]
                    self.updateFieldsByClient[record['ID']]['Ident'][ASInfo['field']] = 1
                    if self.clientData[record['ID']].has_key(ASInfo['field']):
                       self.clientData[record['ID']][ASInfo['field']] = record[ASInfo['field']]
        return result

    def getClientCheckingValue(self, record):
        if self.updateFieldsByClient[record['ID']]['Checking']:
            return []
        values = ['ID'] + self.updateClientCheckingFields[:]
        self.updateFieldsByClient[record['ID']]['Checking'] = 1
        return [u'(%s)' %u', '.join([u"'%s'" %forceString(record[value]) for value in values])]

    def getClientInfoValue(self, record):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if self.updateFieldsByClient[record['ID']]['Info']:
            return []
        self.clientData[record['ID']].update({'F_FAM': u"%s" %record['F_FAM'],
                                              'F_IM': u"%s" %record['F_IM'],
                                              'F_OT': u"%s" %record['F_OT'],
                                              'F_DATR': u"%s" %forceString(record['F_DATR']),
                                              'F_SEX': u"%d" %self.translateSex.get(record['F_SEX'], 0)
                                              })
        if not self.chkReplaceClientInfo.isChecked():
            return []
        if not all([
                forceBool(record['F_FAM']),
                forceBool(record['F_IM']),
                forceBool(record['F_DATR']),
                forceBool(record['F_SEX']),
            ]):
            return []
        updateData = {
                    'client_id': u"'%d'" % record['ID'],
                    'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                    'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                    'lastName': u"'%s'" %record['F_FAM'],
                    'firstName': u"'%s'" %record['F_IM'],
                    'patrName': u"'%s'" %record['F_OT'],
                    'birthdate': u"'%s'" %forceString(record['F_DATR']),
                    'sex': u"'%d'" %self.translateSex.get(record['F_SEX'], 0)
        }
        self.updateFieldsByClient[record['ID']]['Info'] = 1
        return [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateClientInfoFields])]

    def getClientSNILSValue(self, record):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if self.updateFieldsByClient[record['ID']]['SNILS']:
            return []
        self.clientData[record['ID']].update({'F_SNILS': u"%s" %record['F_SNILS']})

        if not self.chkReplaceSNILS.isChecked():
            return []
        if not forceBool(record['F_SNILS']):
            return []
        snils = record['F_SNILS']
        snils = snils[0:3] + snils[4:7] + snils[8:11] + snils[12:14]
        updateData = {
                    'client_id': u"'%d'" % record['ID'],
                    'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                    'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                    'snils': u"'%s'" %snils,
        }
        self.updateFieldsByClient[record['ID']]['SNILS'] = 1
        return [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateClientSNILSFields])]

    def getClientDocumentValue(self, record):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if self.updateFieldsByClient[record['ID']]['Document']:
            return []
        self.clientData[record['ID']].update({'F_DOC': u"%s" %forceString(record['F_DOC']),
                                              'F_DOC_N': u"%s" %forceString(record['F_DOC_N']),
                                              'F_DOC_S': u"%s" %forceString(record['F_DOC_S'])
                                              })

        if not self.chkReplaceUDL.isChecked():
            return []
        if not all([
                forceBool(record['F_DOC']),
                forceBool(record['F_DOC_S']),
                forceBool(record['F_DOC_N']),
            ]):
            return []
        if not record['F_DOC'] in self.rbDocumentType.keys():
            self.logBrowser.append(u'Для пациента %d %s %s %s %s не удалось определить тип документа УДЛ' %(
                record['ID'],
                record['FAM'],
                record['IM'],
                record['OT'],
                forceString(forceDate(record['DATR']).toString('dd.MM.yyyy')),
            ))
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            return []
        updateData = {
                    'client_id': u"'%d'" % record['ID'],
                    'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                    'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                    'documentType_id': u"'%s'" %self.rbDocumentType.get(forceString(record['F_DOC']), 0),
                    'serial': u"'%s'" %record['F_DOC_S'],
                    'number': u"'%s'" %record['F_DOC_N'],
        }
        self.updateFieldsByClient[record['ID']]['Document'] = 1
        return [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateCientDocumentFields])]

    def getClientPolicyValue(self, record):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if self.updateFieldsByClient[record['ID']]['Policy']:
            return []
        self.clientData[record['ID']].update({'F_DPFS': u"%s" %forceString(record['F_DPFS']),
                                              'F_DPFS_N': u"%s" %forceString(record['F_DPFS_N']),
                                              'F_DPFS_S': u"%s" %forceString(record['F_DPFS_S']),
                                              'F_SMO': u"%s" %forceString(record['F_SMO']),
                                              })

        if not self.chkReplacePolice.isChecked():
            return []
        if not all([
                forceBool(record['F_SMO']),
                forceBool(record['F_DPFS']),
                forceBool(record['F_DPFS_N']),
            ]):
            return []

        if not record['F_SMO'] in self.rbInsurer:
            self.logBrowser.append(u'Для пациента %d %s %s %s %s не удалось определить СМО' %(
                record['ID'],
                record['FAM'],
                record['IM'],
                record['OT'],
                forceString(forceDate(record['DATR']).toString('dd.MM.yyyy')),
            ))
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            return []

        if not record['F_DPFS'] in self.rbPolicyKind:
            self.logBrowser.append(u'Для пациента %d %s %s %s %s не удалось определить вид полиса' %(
                record['ID'],
                record['FAM'],
                record['IM'],
                record['OT'],
                forceString(forceDate(record['DATR']).toString('dd.MM.yyyy')),
            ))
            self.logBrowser.update()
            QtGui.qApp.processEvents()
            return []
        updateData = {
                    'client_id': u"'%d'" % record['ID'],
                    'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                    'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                    'policyKind_id': u"'%s'" %self.rbPolicyKind.get(forceString(record['F_DPFS']), '0'),
                    'serial': u"'%s'" %record['F_DPFS_S'],
                    'number': u"'%s'" %record['F_DPFS_N'],
                    'insurer_id': u"'%s'" %forceString(self.rbInsurer.get(record['F_SMO'], 0))
        }
        self.updateFieldsByClient[record['ID']]['Policy'] = 1
        return [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateCientPolicyFields])]

    def getClientDetachDeadValue(self, record):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        if self.updateFieldsByClient[record['ID']]['Dead']:
            return []
        if not forceBool(record['F_DATS']):
            return []
        updateData = {
                    'client_id': u"'%d'" % record['ID'],
                    'modifyDatetime': u"'%s'" %forceString(currentDateTime),
                    'modifyPerson_id': u"'%d'" %(QtGui.qApp.userId),
                    'LPU_id': u"'%s'" %forceString(self.rbOrgStructure.get(record['UCH'], {}).get('orgId', u'0')),
                    'orgStructure_id': u"'%s'" %forceString(self.rbOrgStructure.get(record['UCH'], {}).get('id', u'0')),
                    'date': u"'%s'" %forceString(record['F_DATS']),
                    'attachType_id': u"'%d'" %self.rbAttachTypeDead,
        }
        self.updateFieldsByClient[record['ID']]['Dead'] = 1
        return [u'(%s)' %u', '.join([updateData.get(field, '') for field in self.updateClientDetachDeadFields])]

    def setUpdateClientIdentHeader(self):
        fields = self.updateClientIdentFields[:]
        header = u"""
        Insert Into `tmpClientIdent` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientCheckingHeader(self):
        fields = ['client_id'] + self.updateClientCheckingFields[:]
        header = u"""
        Insert Into `client_MIACControlKrasnodar` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientInfoHeader(self):
        fields = self.updateClientInfoFields[:]
        header = u"""
        Insert Into `tmpClientInfo` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientSNILSHeader(self):
        fields = self.updateClientSNILSFields[:]
        header = u"""
        Insert Into `tmpClientSNILS` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientDocumentHeader(self):
        fields = self.updateCientDocumentFields[:]
        header = u"""
        Insert Into `tmpClientDocument` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientPolicyHeader(self):
        fields = self.updateCientPolicyFields[:]
        header = u"""
        Insert Into `tmpClientPolicy` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    def setUpdateClientDetachDeadHeader(self):
        fields = self.updateClientDetachDeadFields[:]
        header = u"""
        Insert Into `tmpClientDetachDead` (%s) values
	    """ %(u', '.join(fields))
        return [header]

    #Формирование запросов для вставки во временные таблицы - END

    #Проверка базы и исходных данных
    def checkUch(self, record):
        miacres = forceBool(record['MIACRES'] == '001') or not record['MIACRES']
        if not (miacres):
            return False
        return True

    def checkAccountingSystem(self):
        self.logBrowser.append(u'Проверка внешних учетных систем РИС и ЕНП')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

        db = QtGui.qApp.db
        table = db.table('rbAccountingSystem')

        cond = [table['code'].eq(u'РИС')]
        self.risId = forceRef(db.getRecordEx(table, 'id', cond).value('id'))

        cond = [table['code'].eq(u'ЕНП')]
        self.enpId = forceRef(db.getRecordEx(table, 'id', cond).value('id'))

        if self.risId and self.enpId:
            self.logBrowser.append(u'Внешние учетные системы РИС и ЕНП присутствуют в базе данных')
        if not self.risId:
            self.logBrowser.append(u'Внешняя учетная система РИС отсутствует в базе данных')
        if not self.enpId:
            self.logBrowser.append(u'Внешняя учетная система ЕНП отсутствует в базе данных')

        self.logBrowser.update()
        QtGui.qApp.processEvents()
        return self.risId and self.enpId

    def checkOrgstructureCodes(self):
        self.logBrowser.append(u'Проверка внешних кодов ИНФИС')
        self.logBrowser.update()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(sum([len(importDBF)for importDBF in self.importDBFs]))
        self.progressBar.setValue(0)
        QtGui.qApp.processEvents()
        db = QtGui.qApp.db
        self.orgFullNameById = {}
        stmt = u"""
            Select
                if (head.infisCode, head.infisCode, (SELECT getOrgStructureInfisCode(os.id))) as code,
                org.id as id,
                org.fullName as fullName
            From OrgStructure os
	            inner join Organisation  org
		            on org.id = os.organisation_id
		        left join OrgStructure head
                    on os.miacHead_id = head.id
                        and head.infisCode is not Null
                        and head.infisCode != ''

            Group by code, org.id"""
        query = db.query(stmt)
        while query.next():
            record = query.record()
            code = forceString(record.value('code'))
            if not self.orgFullNameById.has_key(code):
                self.orgFullNameById[code] = forceString(record.value('fullName'))
        for importDBF in self.importDBFs:
            for i, record in enumerate(importDBF):
                if not record['CODE_MO'] in self.orgFullNameById.keys():
                    self.logBrowser.append(u'ОШИБКА! Значение поля CODE_MO отсутствует в базе данных')
                    self.logBrowser.update()
                    return False
                self.progressBar.step()
                QtGui.qApp.processEvents()
        self.logBrowser.append(u'Проверка внешних кодов ИНФИС успешно завершена')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        return True

    def checkRbAttachTypeDead(self):
        db = QtGui.qApp.db
        record = db.getRecordEx('rbAttachType', 'id', u"code = 8 and lower(name) = 'умер'")
        if record:
            self.rbAttachTypeDead = forceRef(record.value('id'))
            return
        self.chkDetachDeadEnable = False;
        self.logBrowser.append(u'В базе данных отсутствует тип прикрепления «умер» с кодом 8')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    #Проверка базы и исходных данных - END

    def updateTables(self):
        self.updateTableClientIdent()
        if self.chkReplaceClientInfo.isChecked():
            self.updateTableClientInfo()
        if self.chkReplaceSNILS.isChecked():
            self.updateTableClientSNILS()
        if self.chkReplaceUDL.isChecked():
            self.updateTableClientDocument()
        if self.chkReplacePolice.isChecked():
            self.updateTableClientPolicy()
        if self.chkDetachDead.isChecked() and self.chkDetachDeadEnable:
            self.updateTableClientAttach()

    def updateTableClientInfo(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление данных о клиентах')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        stmt = u'''
            Update Client c, tmpClientInfo t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.lastName = t.lastName,
                c.firstName = t.firstName,
                c.patrName = t.patrName,
                c.birthdate = t.birthdate,
                c.sex = t.sex
            Where c.id = t.client_id
        '''
        db.query(stmt)
        self.logBrowser.append(u'Обновление данных о клиентах - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def updateTableClientSNILS(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление данных о СНИЛС')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        stmt = u'''
            Update Client c, tmpClientSNILS t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.snils = t.snils
            Where c.id = t.client_id
        '''
        db.query(stmt)
        self.logBrowser.append(u'Обновление данных о СНИЛС - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def updateTableClientIdent(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление идентификаторов внешних информационных систем')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        stmt = u'''
            Drop Temporary Table If Exists `tmpClientIdentUpdate`;
            Create Temporary Table tmpClientIdentUpdate
            (
                `id` INT(11),
                `temp_id` INT(11),
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `identifier` varchar(16),
                `checkDate` date,
                PRIMARY KEY (`id`),
                INDEX (`temp_id`)
            )
            Select m.* From
            (
                Select c.id, t.id as temp_id, t.modifyDatetime, t.modifyPerson_id, t.identifier, t.checkDate From tmpClientIdent t
                    inner join ClientIdentification c
                    on c.client_id = t.client_id
                        and c.accountingSystem_id = t.accountingSystem_id
                        and c.deleted = 0
            ) m
            where m.id;

            Update ClientIdentification c, tmpClientIdentUpdate t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.identifier = t.identifier,
                c.checkDate = t.checkDate
            Where c.id = t.id;

            Insert into ClientIdentification
                (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, client_id, accountingSystem_id, identifier, checkDate)
                Select modifyDatetime as createDatetime, modifyPerson_id as createPerson_id, modifyDatetime, modifyPerson_id, client_id, accountingSystem_id, identifier, checkDate From tmpClientIdent
                Where id not in (Select temp_id From tmpClientIdentUpdate);

            Drop Temporary Table tmpClientIdentUpdate;
        '''
        db.query(stmt)
        self.logBrowser.append(u'Обновление идентификаторов внешних информационных систем - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def updateTableClientDocument(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление данных УДЛ')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        listDocumentTypeUDL = u', '.join([ u"'%d'" % id for id in self.listDocumentTypeUDL])
        stmt = u'''
            Drop Temporary Table If Exists `tmpClientDocumentUpdate`;
            Create Temporary Table tmpClientDocumentUpdate
            (
                `id` INT(11),
                `temp_id` INT(11),
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `documentType_id` INT(11),
                `serial` varchar(8),
                `number` varchar(16),
                PRIMARY KEY (`id`),
                INDEX (`temp_id`)
            )
            select m.* From
            (
                Select (
                    Select c.id
                    From ClientDocument c
                    Where c.client_id = t.client_id
                        and c.deleted = 0
                        and c.documentType_id in (%s)
                    Order by c.id desc
                    Limit 1) as id, t.id as temp_id, t.modifyDatetime, t.modifyPerson_id, t.documentType_id, t.serial, t.number  From tmpClientDocument t
            ) m
            where m.id;

            Update ClientDocument c, tmpClientDocumentUpdate t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.serial = t.serial,
                c.number = t.number,
                c.documentType_id = t.documentType_id
            Where c.id = t.id
                and (c.serial != t.serial
                    or c.number != t.number
                    or c.documentType_id != t.documentType_id);

            Insert into ClientDocument
                (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, client_id, documentType_id, serial, number)
                Select modifyDatetime as createDatetime, modifyPerson_id as createPerson_id, modifyDatetime, modifyPerson_id, client_id, documentType_id, serial, number From tmpClientDocument
                Where id not in (Select temp_id From tmpClientDocumentUpdate);

            Drop Temporary Table If Exists `tmpClientDocumentUpdate`;
        ''' %(listDocumentTypeUDL)
        db.query(stmt)
        self.logBrowser.append(u'Обновление данных УДЛ - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def updateTableClientPolicy(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление данных полисов')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        stmt = u'''
            Drop Temporary Table If Exists `tmpClientPolicyUpdate`;
            Create Temporary Table tmpClientPolicyUpdate
            (
                `id` INT(11),
                `temp_id` INT(11),
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `policyKind_id` INT(11),
                `serial` varchar(8),
                `number` varchar(16),
                `insurer_id` int(11),
                PRIMARY KEY (`id`),
                INDEX (`temp_id`)
            )
            select m.* From
            (
                Select (
                    Select c.id
                    From ClientPolicy c
                    Where c.client_id = t.client_id
                        and c.deleted = 0
                    Order by c.id desc
                    Limit 1) as id, t.id as temp_id, t.modifyDatetime, t.modifyPerson_id, t.policyKind_id, t.serial, t.number, t.insurer_id  From tmpClientPolicy t
            ) m
            where m.id;

            Update ClientPolicy c, tmpClientPolicyUpdate t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.policyKind_id = t.policyKind_id,
                c.serial = t.serial,
                c.number = t.number,
                c.insurer_id = t.insurer_id
            Where c.id = t.id
                and (c.number != t.number
                    or c.policyKind_id != t.policyKind_id
                    or c.insurer_id != t.insurer_id);


            Insert into ClientPolicy
                (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, client_id, policyKind_id, serial, number, insurer_id)
                Select modifyDatetime as createDatetime, modifyPerson_id as createPerson_id, modifyDatetime, modifyPerson_id, client_id, '1', serial, number, insurer_id From tmpClientPolicy
                Where id not in (Select temp_id From tmpClientPolicyUpdate);

            Drop Temporary Table If Exists `tmpClientPolicyUpdate`;
        '''
        db.query(stmt)
        self.logBrowser.append(u'Обновление данных полисов - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def updateTableClientAttach(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Обновление данных прикрепления')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        stmt = u'''
            Drop Temporary Table If Exists `tmpClientDetachDeadUpdate`;
            Create Temporary Table tmpClientDetachDeadUpdate
            (
                `id` INT(11),
                `temp_id` INT(11),
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `LPU_id` INT(11),
                `orgStructure_id` INT(11),
                `date` date,
                `attachType_id` INT(11),
                PRIMARY KEY (`id`),
                INDEX (`temp_id`)
            )
            Select m.* From
            (
                Select (
                        Select c.id
                        From ClientAttach c
                        Where c.client_id = t.client_id
                            and c.attachType_id = t.attachType_id
                            and c.deleted = 0
                        Order by c.id desc
                        Limit 1) as id, t.id as temp_id, t.modifyDatetime, t.modifyPerson_id, t.LPU_id, t.orgStructure_id, t.date, t.attachType_id
                From tmpClientDetachDead t
            ) m
            Where m.id;


            Update ClientAttach c, tmpClientDetachDeadUpdate t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.begDate = t.date,
                c.endDate = Null
            Where c.id = t.id;

            Insert into ClientAttach
                (createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, client_id, attachType_id, LPU_id, orgStructure_id, begDate, endDate, document_id, detachment_id)
                Select modifyDatetime as createDatetime, modifyPerson_id as createPerson_id, modifyDatetime, modifyPerson_id, client_id, attachType_id, if(LPU_id = 0, Null, LPU_id), if(orgStructure_id = 0, Null, orgStructure_id), date, NULL, NULL, NULL
                From tmpClientDetachDead
                Where id not in (Select temp_id From tmpClientDetachDeadUpdate);

            Drop Temporary Table If Exists `tmpClientAttachUpdate`;
            Create Temporary Table tmpClientAttachUpdate
            (
                `id` INT(11),
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `date` date,
                `attachType_id` INT(11),
                PRIMARY KEY (`id`)
            )
            Select c.id, t.modifyDatetime, t.modifyPerson_id, t.date, t.attachType_id
            From tmpClientDetachDead t
                inner join ClientAttach c
                Where c.client_id = t.client_id
                    and c.attachType_id != t.attachType_id
                    and c.deleted = 0
                    and (c.endDate is Null or not c.endDate);

            Update ClientAttach c, tmpClientAttachUpdate t
                set c.modifyDatetime = t.modifyDatetime,
                c.modifyPerson_id = t.modifyPerson_id,
                c.endDate = t.date
            Where c.id = t.id;

            Drop Temporary Table If Exists `tmpClientDetachDeadUpdate`;
            Drop Temporary Table If Exists `tmpClientAttachUpdate`;
        '''
        db.query(stmt)
        self.logBrowser.append(u'Обновление данных прикрепления - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def lblNumSetVale(self, all = 0, errors = 0):
        self.lblNum.setText(u"Всего записей в источнике/не прошли контроль МИАЦ-ТФОМС: %s/%s" %(forceString(all), forceString(errors)))

    def clientsReset(self):
        self.errors = 0
        self.errorIdLists = []
        for importDBF in self.importDBFs:
            self.errorIdLists.append([])
        self.errorUchIdLists = []
        for importUchDBF in self.importUchDBFs:
            self.errorUchIdLists.append([])
        db = QtGui.qApp.db
        stmt = u"""
        Drop Table if Exists `client_MIACControlKrasnodar`;
        CREATE TABLE IF NOT EXISTS `client_MIACControlKrasnodar` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `client_id` INT(11) NOT NULL,
          `F_ENP` varchar(16),
          `F_SMO` varchar(4),
          `F_DPFS` varchar(1),
          `F_DPFS_S` varchar(12),
          `F_DPFS_N` varchar(20),
          `F_FAM` varchar(40),
          `F_IM` varchar(40),
          `F_OT` varchar(40),
          `F_SEX` varchar(1),
          `F_DATR` date,
          `F_SNILS` varchar(14),
          `F_DOC` varchar(2),
          `F_DOC_S` varchar(10),
          `F_DOC_N` varchar(15),
          PRIMARY KEY (`id`))
        COMMENT = 'таблица для хранения прошедших контроль пациентов';"""
        db.query(stmt)
        stmt = u"""TRUNCATE TABLE `client_MIACControlKrasnodar`"""
        db.query(stmt)

    def createTmpTables(self):
        db = QtGui.qApp.db
        stmt = u'''
            Drop Temporary Table If Exists `tmpClientIdent`;
            CREATE TEMPORARY TABLE tmpClientIdent
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `accountingSystem_id` INT(11),
                `identifier` varchar(16),
                `checkDate` date,
                PRIMARY KEY (`id`)
            );'''
        if self.chkReplaceClientInfo.isChecked():
            stmt += u'''
            Drop Temporary Table If Exists `tmpClientInfo`;
            CREATE  TEMPORARY TABLE tmpClientInfo
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `lastName` varchar(30),
                `firstName` varchar(30),
                `patrName` varchar(30),
                `birthdate` date,
                `sex`  tinyint(4),
                PRIMARY KEY (`id`)
            );'''
        if self.chkReplaceSNILS.isChecked():
            stmt += u'''
            Drop Temporary Table If Exists `tmpClientSNILS`;
            CREATE  TEMPORARY TABLE tmpClientSNILS
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `snils` varchar(11),
                PRIMARY KEY (`id`)
            );'''
        if self.chkReplaceUDL.isChecked():
            stmt += u'''
            Drop Temporary Table If Exists `tmpClientDocument`;
            CREATE  TEMPORARY TABLE tmpClientDocument
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `documentType_id` INT(11),
                `serial` varchar(8),
                `number` varchar(16),
                PRIMARY KEY (`id`)
            );'''
        if self.chkReplacePolice.isChecked():
            stmt += u'''
            Drop Temporary Table If Exists `tmpClientPolicy`;
            CREATE  TEMPORARY TABLE tmpClientPolicy
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `policyKind_id` INT(11),
                `serial` varchar(8),
                `number` varchar(16),
                `insurer_id` int(11),
                PRIMARY KEY (`id`)
            );
            '''
        if self.chkDetachDead.isChecked() and self.chkDetachDeadEnable:
            stmt += u'''
            Drop Temporary Table If Exists `tmpClientDetachDead`;
            CREATE  TEMPORARY TABLE tmpClientDetachDead
            (
                `id` INT(11) NOT NULL AUTO_INCREMENT,
                `client_id` INT(11) NOT NULL,
                `modifyDatetime` datetime,
                `modifyPerson_id` INT(11),
                `LPU_id` INT(11),
                `orgStructure_id` INT(11),
                `date` date,
                `attachType_id` INT(11),
                PRIMARY KEY (`id`)
            );
            '''

        db.query(stmt)

    def deleteTmpTables(self):
        db = QtGui.qApp.db
        stmt = u'''
        Drop Temporary Table If Exists `tmpClientIdent`, `tmpClientInfo`, `tmpClientSNILS`, `tmpClientDocument`, `tmpClientPolicy`, `tmpClientDetachDead`;
        '''
        db.query(stmt)

    def initUpdateFieldsSets(self):
        self.updateClientIdentFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'accountingSystem_id',
            'identifier',
            'checkDate',
        ]

        self.updateClientCheckingFields = [
            'F_ENP',
            'F_SMO',
            'F_DPFS',
            'F_DPFS_S',
            'F_DPFS_N',
            'F_FAM',
            'F_IM',
            'F_OT',
            'F_SEX',
            'F_DATR',
            'F_SNILS',
            'F_DOC',
            'F_DOC_S',
            'F_DOC_N',
        ]

        self.updateClientInfoFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'lastName',
            'firstName',
            'patrName',
            'birthdate',
            'sex',
            ]

        self.updateClientSNILSFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'snils',
        ]

        self.updateCientDocumentFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'documentType_id',
            'serial',
            'number',
        ]

        self.updateCientPolicyFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'policyKind_id',
            'serial',
            'number',
            'insurer_id',
        ]

        self.updateClientDetachDeadFields = [
            'client_id',
            'modifyDatetime',
            'modifyPerson_id',
            'LPU_id',
            'orgStructure_id',
            'date',
            'attachType_id'
        ]

    def initRefBooks(self):
        db = QtGui.qApp.db
        self.logBrowser.append(u'Загрузка справочников')
        self.logBrowser.update()
        QtGui.qApp.processEvents()
        self.rbDocumentType = {}
        self.rbInsurer = {}
        self.rbOrgStructure = {}
        self.rbPolicyKind = {}
        self.listDocumentTypeUDL = {}
        policyKind = {u'П': 3,
                       u'Э': 4,
                       u'В': 2,
                       u'С': 1
                       }
        for key, value in policyKind.items():
            self.rbPolicyKind[key] = forceInt(db.getRecordEx('rbPolicyKind', 'id', where="code = '%d'" %value).value('id'))

        query = db.query(db.selectStmt('rbDocumentType', ['id', 'regionalCode']))
        while query.next():
            record = query.record()
            self.rbDocumentType[forceString(record.value('regionalCode'))] = forceInt(record.value('id'))

        query = db.query(db.selectStmt('Organisation', ['id', 'infisCode'], 'isInsurer = 1'))
        while query.next():
            record = query.record()
            self.rbInsurer[forceString(record.value('infisCode'))] = forceInt(record.value('id'))

        self.listDocumentTypeUDL = db.getIdList(u'rbDocumentType', u'id', u'''group_id = (select id from rbDocumentTypeGroup where code = '1')''')

        stmt = u'''Select OrgStructure.id as orgStructureId,
                           Organisation.id as orgId,
                           OrgStructure.infisCode,
                           count(OrgStructure.infisCode) as counter
                    From OrgStructure
                        inner join Organisation
                            on Organisation.id = OrgStructure.organisation_id
                    Where (not OrgStructure.infisCode = '') or not OrgStructure.infisCode is Null
                    Group by OrgStructure.infisCode'''
        db.query(stmt)
        while query.next():
            record = query.record()
            if forceInt(record.value['counter']) == 1:
                self.rbOrgStructure[forceString(record.value('infisCode'))] = {'id': forceInt(record.value('orgStructure_id')),
                                                                               'orgId': forceInt(record.value('orgId'))}

        self.logBrowser.append(u'Загрузка справочников - Завершено')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def initUpdateQuantity(self):
        if self.chkReplaceClientInfo.isChecked():
            self.updateQuantity['clientInfo'] = 0
        if self.chkReplaceSNILS.isChecked():
            self.updateQuantity['clientSNILS'] = 0
        if self.chkReplaceUDL.isChecked():
            self.updateQuantity['clientDocument'] = 0
        if self.chkReplacePolice.isChecked():
            self.updateQuantity['clientPolicy'] = 0
        if self.chkDetachDead.isChecked() and self.chkDetachDeadEnable:
            self.updateQuantity['clientDetachDead'] = 0

    def setEnabledAll(self, enable):
        for item in self.disableList:
            item.setEnabled(enable)

    def printImportBegin(self):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('dd-MM-yyyy hh:mm:ss'))
        self.logBrowser.append(u'Начало импорта %s' %currentDateTime)
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    def printImportEnd(self):
        currentDateTime = forceString(QtCore.QDateTime.currentDateTime().toString('dd-MM-yyyy hh:mm:ss'))
        self.logBrowser.append(u'Окончание импорта %s.' %currentDateTime)
        if self.chkReplaceClientInfo.isChecked():
            self.logBrowser.append(u"'Заменить данные пациента' обновлено %d записей" %self.updateQuantity.get('clientInfo', 0))
        if self.chkReplaceSNILS.isChecked():
            self.logBrowser.append(u"'Заменить СНИЛС' обновлено %d записей" %self.updateQuantity.get('clientSNILS', 0))
        if self.chkReplaceUDL.isChecked():
            self.logBrowser.append(u"'Заменить документ УДЛ' обновлено %d записей" %self.updateQuantity.get('clientDocument', 0))
        if self.chkReplacePolice.isChecked():
            self.logBrowser.append(u"'Заменить полисные данные' обновлено %d записей" %self.updateQuantity.get('clientPolicy', 0))
        if self.chkDetachDead.isChecked() and self.chkDetachDeadEnable:
            self.logBrowser.append(u"'Открепить умерших' обновлено %d записей" %self.updateQuantity.get('clientDetachDead', 0))
        self.logBrowser.append(u'=============================================================')
        self.logBrowser.update()
        QtGui.qApp.processEvents()

    @QtCore.pyqtSlot()
    def on_btnShowErrors_clicked(self):
        viewDialog = CReportViewDialog(self)
        viewDialog.setWindowTitle(u'Список прикрепленных пациентов, не прошедших первичный контроль в МИАЦ и ТФОМС')
        viewDialog.setText(self.build())
        viewDialog.exec_()

    def build(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Список прикрепленных пациентов, не прошедших первичный контроль в МИАЦ и ТФОМС')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        self.dumpParams(cursor)
        cursor.insertBlock()
        tableColumns = [
            ('2%', [u'№ п/п'], CReportBase.AlignLeft),
            ('4%', [u'Код пациента'], CReportBase.AlignLeft),
            ('4%', [u'ФИО пациента'], CReportBase.AlignLeft),
            ('4%', [u'Пол'], CReportBase.AlignLeft),
            ('4%', [u'Дата рождения'], CReportBase.AlignLeft),
            ('4%', [u'Результат сверки МИАЦ'], CReportBase.AlignLeft),
            ('4%', [u'Комментарий МИАЦ'], CReportBase.AlignLeft),
            ('4%', [u'Результат сверки ТФОМС'], CReportBase.AlignLeft),
            ('4%', [u'Комментарий ТФОМС'], CReportBase.AlignLeft),
            ('4%', [u'Данные из Регионального сегмента застрахованных лиц', u'Код СМО в системе ОМС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Тип полиса ОМС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Серия полиса ОМС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Номер полиса ОМС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Фамилия'], CReportBase.AlignLeft),
            ('4%', [u'', u'Имя'], CReportBase.AlignLeft),
            ('4%', [u'', u'Отчество'], CReportBase.AlignLeft),
            ('4%', [u'', u'Пол'], CReportBase.AlignLeft),
            ('4%', [u'', u'Дата рождения'], CReportBase.AlignLeft),
            ('4%', [u'', u'Дата окончания действия полиса ОМС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Дата смерти по данным ЗАГС'], CReportBase.AlignLeft),
            ('4%', [u'', u'СНИЛС'], CReportBase.AlignLeft),
            ('4%', [u'', u'Тип документа УДЛ'], CReportBase.AlignLeft),
            ('4%', [u'', u'Серия документа УДЛ'], CReportBase.AlignLeft),
            ('4%', [u'', u'Номер документа УДЛ'], CReportBase.AlignLeft),
            ]
        table = createTable(cursor, tableColumns)
        for i in range(9):
            table.mergeCells(0, i, 2, 1)
        table.mergeCells(0, 9, 1, 15)
        for ind, importDBF in enumerate(self.importDBFs):
            errorIdList = self.errorIdLists[ind]
            for i in errorIdList:
                record = importDBF[i]
                row = table.addRow()
                fields = (
                    row - 1,
                    record['ID'],
                    record['FAM'] + ' ' + record['IM'] + ' ' + record['OT'],
                    record['SEX'],
                    forceString(forceDate(record['DATR']).toString('dd.MM.yyyy')),
                    self.parceComm(record['MIACRES']),
                    record['M_COMM'],
                    self.parceComm(record['TFOMSRES']),
                    record['F_COMM'],
                    record['F_SMO'],
                    record['F_DPFS'],
                    record['F_DPFS_S'],
                    record['F_DPFS_N'],
                    record['F_FAM'],
                    record['F_IM'],
                    record['F_OT'],
                    record['F_SEX'],
                    forceString(forceDate(record['F_DATR']).toString('dd.MM.yyyy')),
                    forceString(forceDate(record['F_DSTOP']).toString('dd.MM.yyyy')),
                    forceString(forceDate(record['F_DATS']).toString('dd.MM.yyyy')),
                    record['F_SNILS'],
                    record['F_DOC'],
                    record['F_DOC_S'],
                    record['F_DOC_N']
                )
                for col, val in enumerate(fields):
                    table.setText(row, col, val)

        if not sum([sum(uchIdList) for uchIdList in self.errorUchIdLists]):
            return doc

        cursor.movePosition(cursor.End)
        cursor.insertText(u'Таблица ошибок по врачам', CReportBase.ReportTitle)
        cursor.insertBlock()
        tableColumns = [
            ('2%', [u'№ п/п'], CReportBase.AlignLeft),
            ('5%', [u'Код ЛПУ'], CReportBase.AlignLeft),
            ('5%', [u'Участок'], CReportBase.AlignLeft),
            ('25%', [u'ФИО медработника'], CReportBase.AlignLeft),
            ('5%', [u'СНИЛС медработника'], CReportBase.AlignLeft),
            ('55%', [u'Причина отклонения МИАЦ'], CReportBase.AlignLeft),
            ]
        table = createTable(cursor, tableColumns)
        for ind, importUchDBF in enumerate(self.importUchDBFs):
            errorUchIdList = self.errorUchIdLists[ind]
        for i in errorUchIdList:
            record = importUchDBF[i]
            row = table.addRow()
            fields = (
                row - 1,
                record['CODE_MO'],
                record['UCH'],
                record['D_FAM'] + ' ' + record['D_IM'] + ' ' + record['D_OT'],
                record['D_SNILS'],
                self.parceComm(record['MIACRES']),
            )
            for col, val in enumerate(fields):
                table.setText(row, col, val)
        return doc

    def parceComm(self, comments):
        if not self.codesDict:
            db = QtGui.qApp.db
            stmt = u"Select CODE, NAME From rbcheckaccountsspr64"
            query = db.query(stmt)
            while query.next():
                record = query.record()
                self.codesDict[forceString(record.value('CODE'))] = forceString(record.value('NAME'))
        if not comments:
            return u''
        list = comments.split(' ')
        result = []
        for item in list:
            if not self.codesDict.has_key(item):
                return u'неверный формат кодов'
            result.append(self.codesDict[item])
        return u'\n'.join(result)


    def dumpParams(self, cursor):
        description = []
        db = QtGui.qApp.db

        description.append(u'Импортированы файлы: %s' %u', '.join(self.prikFileNames))
        description.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        charFormat = QtGui.QTextCharFormat()
        charFormat.setFontPointSize(8)
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0, charFormat=charFormat)
        for i, row in enumerate(description):
            table.setText(i, 0, row)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    @QtCore.pyqtSlot(bool)
    def on_btnImportSelect_toggled(self, checked):
        if checked:
            self.btnImport.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_btnNotImportSelect_toggled(self, checked):
        if checked:
            self.btnImport.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_btnImportAll_toggled(self, checked):
        if checked:
            self.btnImport.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.showWindowRef()

    def closeEvent(self, event):
        if hasattr(QtGui.qApp.mainWindow, 'registry'):
            if hasattr(QtGui.qApp.mainWindow.registry, 'updateRegistryContent'):
                QtGui.qApp.mainWindow.registry.updateRegistryContent()
        QtGui.QDialog.closeEvent(self, event)
        event.accept()


def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 229917

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.207',
                      'port' : 3306,
                      'database' : 'sochigp2',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CImportMIS(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()