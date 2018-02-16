#!/usr/bin/env python
# -*- coding: utf-8 -*-
from library.exception import CDbfImportException

from Ui_ImportLgot import Ui_Dialog
from Cimport import *
from Utils import *
from Registry.Utils import selectLatestRecord

def ImportLgot(widget):
    dlg = CImportLgot(widget)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportLgotFileName',  '')))
    dlg.edtPersonalDataFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitPersonalDataFileName',  '')))
    dlg.edtDocumentDataFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitDocumentDataFileName',  '')))
    dlg.chkFederalBenefit.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitTypeFederal', True)))
    dlg.chkRegionalBenefit.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitTypeRegional', False)))
    dlg.chkAddMissingClients.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitAddMissingClients', False)))
    dlg.chkAddDocumentType.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs,
        'ImportBenefitAddDocumentType',  True)))
    dlg.checkName()
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportLgotFileName'] = toVariant(dlg.edtFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportBenefitPersonalDataFileName'] = \
        toVariant(dlg.edtPersonalDataFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportBenefitDocumentDataFileName'] = \
        toVariant(dlg.edtDocumentDataFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportBenefitTypeFederal'] = \
        toVariant(dlg.chkFederalBenefit.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportBenefitTypeRegional'] = \
        toVariant(dlg.chkRegionalBenefit.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportBenefitAddMissingClients'] = \
        toVariant(dlg.chkAddMissingClients.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportBenefitAddDocumentType'] = \
        toVariant(dlg.chkAddDocumentType.isChecked())


class CImportLgot(QtGui.QDialog, Ui_Dialog, CDBFimport):
    # номера вкладок в tabExportType
    tabEMSRN = 0
    tabFSS = 1
    sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.lgotTypes={}
        self.lgotDocTypes={}
        self.paspDocTypes={}
        self.documentTypeCache = {}
        self.documentTypeNameCache = {}
        self.mapPolicySerialToInsurerId = {}
        self.policyTypeId = None
        self.docTypeGroupId = None
        self.clientNppToIdMap = {}
        self.krasClientSnilsToIdMap = {}
        self.socStatusTypeCache = {}
        self.isKrasnodar = QtGui.qApp.region() == u'23'
        self.tbl_rbSocStatusType=tbl('rbSocStatusType')
        self.tbl_ClientSocStatus=tbl('ClientSocStatus')
        self.tbl_rbDocumentType=tbl('rbDocumentType')
        self.tableOrgPolicySerial = tbl('Organisation_PolicySerial')


    def err2log(self, e):
        fio=self.row['FAM']+' '+self.row['IM']+' '+self.row['OT']
        self.log.append(u'запись '+str(self.n)+' ('+fio+'): '+e)


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.checkName()
            self.updateLabelNum()


    @QtCore.pyqtSlot()
    def on_btnSelectDocumentDataFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными о документах', self.edtDocumentDataFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtDocumentDataFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.checkName()
            self.updateLabelNum()


    @QtCore.pyqtSlot()
    def on_btnSelectPersonalDataFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с персональными данными', self.edtPersonalDataFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtPersonalDataFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.checkName()


    @QtCore.pyqtSlot()
    def on_btnViewDocumentDataFile_clicked(self):
        fname=unicode(forceStringEx(self.edtDocumentDataFileName.text()))
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()


    @QtCore.pyqtSlot()
    def on_btnViewPersonalDataFile_clicked(self):
        fname=unicode(forceStringEx(self.edtPersonalDataFileName.text()))
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()


    @QtCore.pyqtSlot(int)
    def on_tabExportType_currentChanged(self, index):
        self.updateLabelNum()


    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='' or \
            (self.edtDocumentDataFileName.text() != '' and \
            self.edtPersonalDataFileName.text() != ''))


    def updateLabelNum(self):
        fileName = ''

        if self.tabExportType.currentIndex() == self.tabEMSRN:
            fileName = forceStringEx(self.edtFileName.text())
        elif self.tabExportType.currentIndex() == self.tabFSS:
            fileName = forceStringEx(self.edtDocumentDataFileName.text())

        if fileName:
            dbfLgot = dbf.Dbf(fileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfLgot)))
        else:
            self.labelNum.setText(u'нет записей в источнике')


    def startImport(self):
        if self.tabExportType.currentIndex() == self.tabEMSRN:
            self.startImportEMSRN()
        else:
            self.startImportFSS()


    def startImportEMSRN(self):
        self.loadAdr=self.chkAdr.isChecked()
        self.docMsg=self.chkDoc.isChecked()

        n=0
        self.n_client=0
        self.n_adr_r=0
        self.n_adr_f=0

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbfLgot = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        assert dbfCheckNames(dbfLgot, dbfFields())


        dbf_len=len(dbfLgot)
        self.progressBar.setMaximum(dbf_len-1)
        self.labelNum.setText(u'всего записей в источнике: '+str(dbf_len))
        for row in dbfLgot:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.n=n+1
            self.row=row
            self.processRow()
            n+=1
            self.progressBar.setValue(n)
            if self.loadAdr:
                self.statusLabel.setText(
                    u'найдено: льготников - %d; адресов (рег./прож.) - %d/%d' \
                    % (self.n_client, self.n_adr_r, self.n_adr_f))
            else:
                self.statusLabel.setText(u'найдено: %d' % self.n_client)
        self.progressBar.setValue(n-1)


    def startImportFSS(self):
        self.addMissingClients = self.chkAddMissingClients.isChecked()
        self.addNewDocumentType = self.chkAddDocumentType.isChecked()

        dbfPersonalDataFileName = forceStringEx(self.edtPersonalDataFileName.text())
        dbfPersonalData = dbf.Dbf(dbfPersonalDataFileName, readOnly=True, encoding='cp866')

        dbfDocumentDataFileName = forceStringEx(self.edtDocumentDataFileName.text())
        dbfDocumentData = dbf.Dbf(dbfDocumentDataFileName, readOnly=True, encoding='cp866')

        dbfLen=len(dbfDocumentData)+len(dbfPersonalData)
        self.progressBar.setFormat('%v')
        self.progressBar.setMaximum(dbfLen-1)
        self.labelNum.setText(u'всего записей в источнике: %d' % dbfLen)
        self.policyTypeId = forceRef(self.db.translate('rbPolicyType', 'code', '1', 'id'))
        self.socStatusClassId = forceRef(self.db.translate('rbSocStatusClass', 'name', u'льгота', 'id'))
        self.docTypeGroupId = forceRef(self.db.translate('rbDocumentTypeGroup', 'code', '2', 'id'))
        isRegional = self.chkRegionalBenefit.isChecked()

        if isRegional:
            validDbf = dbfCheckNames(dbfPersonalData, ['DOC_SER','DOC_NOM', 'POLIS_NOM', 'POLIS_SER'])
        else:
            validDbf = dbfCheckNames(dbfPersonalData, ['SN_DOC', 'SN_POL'])
            actualDate = QFileInfo(dbfDocumentDataFileName).lastModified().date()

            if actualDate.isValid():
                day = actualDate.day()
                day = 20 if day >= 20 else (10 if day >= 10 else 1)
                actualDate.setDate(actualDate.year(), actualDate.month(), day)

        if not validDbf:
            self.log.append(u'<b><font color=red>ОШИБКА</b>:Неправильный формат DBF файла персональных данных.')
            return

        if not self.socStatusClassId:
            self.log.append(u'В справочнике классов социальных статусов (rbSocStatusClass)'\
                u' отсутствует элемент с наименованием `льгота`.')
            return

        if not self.policyTypeId:
            self.log.append(u'В справочнике типов полисов (rbPolicyType)'\
                u' отсутствует элемент с кодом `1`.')
            return


        if not self.docTypeGroupId:
            self.log.append(u'В справочнике групп типов документов (rbDocumentTypeGroup)'\
                u' отсутствует элемент с кодом `2` (льготы).')
            return

        self.clientNppToIdMap = {}
        n = 0

        for row in dbfPersonalData:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.processPersonalDataRow(row,  isRegional)
            n+=1
            self.progressBar.setValue(n)

        federalBenefitInfo = None if isRegional else self.getFederalBenefitClientDict(actualDate)

        for row in dbfDocumentData:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.processDocumentDataRow(row, federalBenefitInfo)
            n+=1
            self.progressBar.setValue(n)

        if federalBenefitInfo:
            self.closeFederalBenefit(federalBenefitInfo, actualDate)


    def processPersonalDataRow(self,  row,  isRegional):
        clientRecord = None #raipc: позволит сэкономить запрос к таблице Client, если будем обновлять СНИЛС
        SNILS = unformatSNILS(forceString(row['SS']))
        if not SNILS:
            message = u'Поле СНИЛС в строке %d пусто. Возможно, файл с персональными данными повреждён' % (row.index + 1)
            self.log.append(u'<b><font color=red>ОШИБКА</b>: %s' % message)
            raise CDbfImportException(message)

        clientId = self.findClientBySNILS(SNILS)

        if not clientId:
            lastName = nameCase(forceString(row['FAM']).strip())
            firstName = nameCase(forceString(row['IM']).strip())
            patrName = nameCase(forceString(row['OT']).strip())
            sex = self.sexMap.get(forceString(row['W']).strip())

            #FIXME raipc: Возможно, это баг и стоит использовать str2date не только в Краснодаре
            if self.isKrasnodar:
                birthDate = str2date(row['DR'])
            else:
                birthDate = QDate.fromString(forceString(row['DR']), 'dd/MM/yyyy')

            clientId, clientRecord = self.findClientByNameSexAndBirthDate(lastName, firstName, patrName, sex, birthDate)

            if not clientId:
                if isRegional:
                    documentSerial = forceString(row['DOC_SER'])
                    documentNumber = forceString(row['DOC_NOM'])
                else:
                    documentSN = row['SN_DOC'].strip().split(' ')
                    documentNumber = documentSN[-1:]
                    documentSerial = ' '.join(documentSN[:-1])

                documentTypeId = self.getDocumentTypeId(row['C_DOC'])
                clientId = self.findClientByDocument(documentTypeId, documentSerial, documentNumber)

                if not clientId:
                    if isRegional:
                        policySerial = forceString(row['POLIS_SER']).strip()
                        policyNumber = forceString(row['POLIS_NOM']).strip()
                    else:
                        policySN = forceString(row['SN_POL']).strip().split(' ')
                        policySerial = policyNumber = None

                        if policySN != []:
                            policySerial = policySN[0] if len(policySN) > 1 else ''
                            policyNumber = policySN[1] if len(policySN) > 1 else policySN[0]

                        if policyNumber:
                            clientId = self.findClientByPolicy(policySerial, policyNumber)

                    if not clientId:
                        if self.addMissingClients:
                            self.log.append(u'Добавляем нового пациента %s %s %s' % (lastName, firstName, patrName))
                            clientId = self.addClient(lastName, firstName, patrName, birthDate, sex, SNILS)
                            self.addClientDocument(clientId, documentTypeId, documentSerial, documentNumber)

                            if policySerial or policyNumber:
                                policyInsurer = self.adviseInsurerId(policySerial)
                                self.addClientPolicy(clientId, policyInsurer, self.policyTypeId, policySerial, \
                                    policyNumber, None, None,  None)
                        else:
                            self.log.append(u'Пропускаем нового пациента %s %s %s' % (lastName, firstName, patrName))

        if clientId:
            self.ensureClientSNILS(clientId, SNILS, clientRecord)
            if self.isKrasnodar:
                self.krasClientSnilsToIdMap[SNILS] = clientId
            else:
                npp = forceInt(row['NPP'])
                self.clientNppToIdMap[npp] = clientId


    def processDocumentDataRow(self,  row, federalBenefitInfo=None):
        if self.isKrasnodar:
            SNILS = unformatSNILS(forceString(row['SS']))
            clientId = self.krasClientSnilsToIdMap.get(SNILS) if SNILS else None
        else:
            npp = forceInt(row['NPP'])
            clientId = self.clientNppToIdMap.get(npp)


        if not clientId :
            SNILS = unformatSNILS(forceString(row['SS']))
            if not SNILS:
                message = u'Поле СНИЛС в строке %d пусто. Возможно, файл с данными о документах повреждён.' % (row.index + 1)
                self.log.append(u'<b><font color=red>ОШИБКА</b>: %s' % message)
                raise CDbfImportException(message)

            clientId = self.findClientBySNILS(SNILS)

            if not clientId:
                self.log.append(u'<b><font color=red>ВНИМАНИЕ</b>: пациент не найден' \
                    u' для записи %s.' % (u'со СНИЛС ' + SNILS if self.isKrasnodar else npp))
                return

        socStatusTypeCode = row['C_KAT'].strip()
        socStatusTypeId = self.getSocStatusTypeId(socStatusTypeCode)

        if not socStatusTypeId:
            self.log.append(u'<b><font color=red>ОШИБКА</b>: для записи %s' \
                u' информация о соц. статусе `%s`' \
                u' отсутствует в БД.' % (u'со СНИЛС ' + SNILS if self.isKrasnodar else npp, socStatusTypeCode))
            return

        documentName = row['NAME_DL'].strip()
        documentTypeId = self.getDocumentTypeIdByName(documentName)
        documentId = None

        if not documentTypeId and documentName and self.addNewDocumentType:
            self.log.append(u'<b><font color=green>Добавляем</b>' \
                u'новый тип документа `%s`.' % (documentName))
            documentTypeId = self.addDocumentType(documentName)

        if documentTypeId:
            documentSN = forceString(row['SN_DL']).strip().split()

            if documentSN != []:
                documentNumber = documentSN[-1]
                documentSerial = ' '.join(documentSN[:-1]) if len(documentSN) > 1 else ''
                documentId = self.ensureClientDocument(clientId, documentTypeId, documentSerial, documentNumber)

#        if not documentId:
#            self.log.append(u'<b><font color=red>ОШИБКА</b>: для записи %d' \
#                u' в БД отсутствует тип документа `%s`.' % (npp, documentName))
#            return

        begDate = str2date(row['DATE_BL'])
        endDate = str2date(row['DATE_EL'])

        if not begDate.isValid():
            self.log.append(u'<b><font color=red>ОШИБКА</b>: для записи со СНИЛС %s' \
                    u' отсутствует дата начала действия НСУ.' % SNILS if self.isKrasnodar else npp)
            return

        self.ensureClientSocStatus(clientId, socStatusTypeId, begDate, endDate, documentId)

        if federalBenefitInfo and federalBenefitInfo.has_key(clientId):
            federalBenefitInfo.pop(clientId)


    def ensureClientDocument(self, clientId, documentTypeId, documentSerial, documentNumber):
        result = self.findClientDocument(clientId, documentTypeId, documentSerial, documentNumber)

        if not result:
            result = self.addClientDocument(clientId, documentTypeId, documentSerial, documentNumber)

        return result


    def ensureClientSocStatus(self, clientId, socStatusTypeId,  begDate, endDate, documentId):

        record = selectLatestRecord('ClientSocStatus', clientId,
                '(Tmp.`socStatusClass_id`=%d AND Tmp.`socStatusType_id`=%d)' % \
                (self.socStatusClassId, socStatusTypeId))

        if record:
            oldBegDate = forceDate(record.value('begDate'))
            oldEndDate = forceDate(record.value('endDate'))

            if begDate == oldBegDate and endDate == oldEndDate:
                oldDocumentId = forceRef(record.value('document_id'))

                if oldDocumentId != documentId:
                    record.setValue('document_id',  documentId)
                    self.db.updateRecord(self.tbl_ClientSocStatus, record)

                return

        self.addClientSocStatus(clientId, self.socStatusClassId, socStatusTypeId, begDate, endDate, documentId)


    def ensureClientSNILS(self, clientId, SNILS, record=None):
        if not record:
            record = self.db.getRecordEx(self.tableClient, 'id, SNILS',
                [self.tableClient['deleted'].eq(0),
                self.tableClient['id'].eq(clientId)], 'id')
        if record and forceString(record.value('SNILS')).strip() == '':
            record.setValue('SNILS', toVariant(SNILS))
        QtGui.qApp.db.updateRecord(self.tableClient, record)


    def processRow(self):
        row=self.row

        clientId=self.processClientId()

        SS=forceString(row['SS'])
        SNILS=unformatSNILS(SS)
        if SNILS and not clientId:
            clientId=forceInt(QtGui.qApp.db.translate(self.tableClient, 'SNILS', SNILS, 'id'))

        doc_bad=False

        documentType_id=self.get_pasp_documentType_id(forceString(row['NAME_P']))
        if not documentType_id:
            doc_bad=True

        SER_P=forceString(row['SER_P'])
        serial=formatSerial(SER_P)
        if not re.match(u'^\d\d \d\d$', serial):
            if self.docMsg:
                self.err2log(u'неправильная серия паспорта "%s"' % SER_P)
            doc_bad=True

        NUMB_P=forceString(row['NUMB_P'])
        number=formatNumber(NUMB_P)
        if len(number)!=6:
            if self.docMsg:
                self.err2log(u'неправильный номер паспорта "%s"' % NUMB_P)
            doc_bad=True

        if not clientId and not doc_bad:
            DATE_VP=str2date(row['DATE_VP'])
            cond=[
                self.tableClientDocument['documentType_id'].eq(toVariant(documentType_id)),
                self.tableClientDocument['serial'].eq(toVariant(serial)),
                self.tableClientDocument['number'].eq(toVariant(number)),
#                self.tableClientDocument['date'].eq(toVariant(DATE_VP))
                ]
            ClientDocument=QtGui.qApp.db.getRecordEx(
                self.tableClientDocument, 'client_id', where=cond)
            if ClientDocument:
                clientId=ClientDocument.value('client_id').toInt()[0]

        if not clientId:
            return

        self.n_client+=1

        if SNILS:
            id = getId(self.tableClient, [('id', clientId)], [('SNILS', SNILS)])

        if not doc_bad:
            self.processPaspDoc(clientId, serial, number, documentType_id)

        LKN1=forceString(row['LKN1'])
        socStatusType_id=self.get_socStatusType_id(LKN1)
        if not socStatusType_id:
            self.err2log(u'не удалось найти или добавить тип льготы "%s"' % LKN1)
            return

        DATE_BL=str2date(row['DATE_BL'])
        DATE_EL=str2date(row['DATE_EL'])
        if not DATE_BL:
            self.err2log(u'отсутствует дата начала действия льготы')
            return

        LgotDocId=self.getLgotDocId(clientId)

        cond=[
            self.tbl_ClientSocStatus['client_id'].eq(toVariant(clientId)),
            self.tbl_ClientSocStatus['socStatusType_id'].eq(toVariant(socStatusType_id)),
            self.tbl_ClientSocStatus['endDate'].ge(toVariant(DATE_BL)),
            ]
        ClientSocStatus=QtGui.qApp.db.getRecordEx(
            self.tbl_ClientSocStatus, cols='*', where=cond)
        if ClientSocStatus:
            endDate=forceDate(ClientSocStatus.value('endDate'))
            upd=False
            if DATE_EL and (DATE_EL>endDate or not endDate):
                ClientSocStatus.setValue('endDate', toVariant(DATE_EL))
                upd=True
            if LgotDocId:
                ClientSocStatus.setValue('document_id', toVariant(LgotDocId))
                upd=True
            if upd:
                QtGui.qApp.db.updateRecord(self.tbl_ClientSocStatus, ClientSocStatus)
        else:
            ClientSocStatusFields=[
                ('client_id', clientId), ('socStatusType_id', socStatusType_id), ('begDate', DATE_BL)]
            ClientSocStatusFields2=[('endDate', DATE_EL), ('document_id', LgotDocId)]
            ClientSocStatusId=getId(
                self.tbl_ClientSocStatus, ClientSocStatusFields, ClientSocStatusFields2)
            if not ClientSocStatusId:
                self.err2log(u'не удалось добавить льготу')
                return

        if self.loadAdr:
            ADRES_R=forceString(row['ADRES_R'])
            self.processAddress(clientId, ADRES_R, 0)
            ADRES_F=forceString(row['ADRES_F'])
            self.processAddress(clientId, ADRES_F, 1)

    def processClientId(self):
        row=self.row
        FAM=nameCase(self.row['FAM'])
        IM=nameCase(self.row['IM'])
        OT=nameCase(self.row['OT'])
        if not (FAM and IM and OT):
            if not (FAM and IM):
                self.err2log(u'нет полного ФИО')
            return None
        fio=FAM+IM+OT
        if not check_rus_lat(fio):
            self.err2log(u'недопустимое ФИО')
            return None
        sex=self.row['W']
        if not sex:
            self.err2log(u'не указан пол')
            return None
        else:
            if sex in [u'м', u'М']: sex=1
            elif sex in [u'ж', u'Ж']: sex=2
            else:
                self.err2log(u'неправильный пол')
                return None
        DR=self.row['DR']
        if not DR:
            self.err2log(u'не указан день рождения')
            return None
        cond=[]
        cond.append(self.tableClient['lastName'].eq(toVariant(FAM)))
        cond.append(self.tableClient['firstName'].eq(toVariant(IM)))
        cond.append(self.tableClient['patrName'].eq(toVariant(OT)))
        cond.append(self.tableClient['sex'].eq(toVariant(sex)))
        cond.append(self.tableClient['birthDate'].eq(toVariant(DR)))
        client=QtGui.qApp.db.getRecordEx(self.tableClient, '*', where=cond)
        if client:
            return client.value('id').toInt()[0]
        return None

    def get_socStatusType_id(self, LKN1):
        if not LKN1:
            self.err2log(u'отсутствует тип льготы')
            return
        id=self.lgotTypes.get(LKN1, None)
        if id: return id

        rbSocStatusTypeFields=[('code', LKN1)]
        rbSocStatusTypeFields2=[('name', LKN1)]
        id=getId(self.tbl_rbSocStatusType, rbSocStatusTypeFields, rbSocStatusTypeFields2)

        if id: self.lgotTypes[LKN1]=id
        return id

    def get_lgot_documentType_id(self, NAME_DL):
        if not NAME_DL:
            self.err2log(u'отсутствует тип подтверждающего документа')
            return
        id=self.lgotDocTypes.get(NAME_DL, None)
        if id: return id

        rbDocumentTypeFields=[('name', NAME_DL), ('group_id', 2)]
        rbDocumentTypeFields2=[('serial_format', 0), ('number_format', 0)]
        id=getId(self.tbl_rbDocumentType, rbDocumentTypeFields, rbDocumentTypeFields2)

        if id: self.lgotDocTypes[NAME_DL]=id
        return id

    def getLgotDocId(self, clientId):
        row=self.row
        NAME_DL=forceString(row['NAME_DL'])
        documentType_id=self.get_lgot_documentType_id(NAME_DL)
        if not documentType_id:
            self.err2log(u'не удалось найти или добавить тип подтверждающего документа')
            return None

        SER_DL=forceString(row['SER_DL'])
        NUMB_DL=forceString(row['NUMB_DL'])
        DATE_VD=str2date(row['DATE_VD'])
        ClientDocumentFields=[
            ('client_id', clientId), ('documentType_id', documentType_id),
            ('serial', SER_DL), ('number', NUMB_DL), ('date', DATE_VD)]
        return getId(self.tableClientDocument, ClientDocumentFields)

    def get_pasp_documentType_id(self, NAME_P):
        if not NAME_P:
            if self.docMsg:
                self.err2log(u'отсутствует тип удостоверения личности')
            return
        id=self.paspDocTypes.get(NAME_P, None)
        if id: return id

        name={
            u'Паспорт гражданина России':u'ПАСПОРТ РФ',
            u'ПАСПОРТ':u'ПАСПОРТ РФ',
            u'ПАСПОРТ ГРАЖДАНИНА РОССИИ':u'ПАСПОРТ РФ',
            u'Паспорт гражданина СССР':u'ПАСПОРТ СССР',
            u'ПАСПОРТ ГРАЖДАНИНА СССР':u'ПАСПОРТ СССР',
            u'Временное удостоверение личности граждан':u'ВРЕМ УДОСТ',
            u'Свидетельство о рождении':u'СВИД О РОЖД',
            u'СВИДЕТЕЛЬСТВО О РОЖДЕНИИ':u'СВИД О РОЖД',
            u'Вид на жительство':u'ВИД НА ЖИТЕЛЬ',
            u'Загранпаспорт гражданина России':u'ЗГПАСПОРТ',
            u'Справка об освобождении из мест лишения':u'СПРАВКА ОБ ОСВ',
            u'Иностранный паспорт':u'ИНПАСПОРТ',
            u'Паспорт Минморфлота':u'ПАСПОРТ МОРФЛТ',
            u'Военный билет офицера запаса':u'ВОЕННЫЙ БИЛЕТ',
            }.get(NAME_P, NAME_P)
        cond=[]
        cond.append(self.tbl_rbDocumentType['name'].eq(toVariant(name)))
        cond.append(self.tbl_rbDocumentType['group_id'].eq(toVariant(1)))
        record=QtGui.qApp.db.getRecordEx(self.tbl_rbDocumentType, '*', where=cond)
        if record:
            id=forceInt(record.value('id'))
        else:
            if self.docMsg:
                self.err2log(u'не найден тип удостоверения личности "%s"' % NAME_P)

        if id: self.paspDocTypes[NAME_P]=id
        return id

    def processPaspDoc(self, clientId, serial, number, documentType_id):
        row=self.row

        DATE_VP=str2date(row['DATE_VP'])
        NAME_VP=forceString(row['NAME_VP'])
        ClientDocumentFields=[
            ('client_id', clientId), ('documentType_id', documentType_id),
            ('serial', serial), ('number', number)]
        ClientDocumentFields2=[('origin', NAME_VP), ('date', DATE_VP)]
        ClientDocumentId=getId(
            self.tableClientDocument, ClientDocumentFields, ClientDocumentFields2)

    def processAddress(self, clientId, ADRES, type):
        if not ADRES:
            return
        m=re.match('^[0-9,]+( |,|, )', ADRES)
        if m:
            pos=m.end()
            if pos>=0:
                ADRES=ADRES[pos:].strip()
        KLADRCode=self.get_KLADRCode(ADRES, noCache=True)
        if not KLADRCode:
            return

        m=re_spb.match(ADRES)
        if m:
            pos=m.end()
            if pos>=0:
                ADRES=ADRES[pos:]
        ul=ADRES.split(',')[0].strip()
        m=re.search(u' Д ', ul)
        if m:
            pos=m.start()
            if pos>=0:
                ul=ul[:pos].strip()
        KLADRStreetCode=self.get_KLADRStreetCode(ul, KLADRCode, ul, noCache=True)
        if not KLADRStreetCode:
            return

        number, corpus, flat = get_dom_korp_kv(ADRES)
        if not (number and flat):
            return

        houseFields=[
            ('KLADRCode', KLADRCode), ('KLADRStreetCode', KLADRStreetCode), ('number', number)]
        if corpus:
            houseFields.append(('corpus', corpus))
        houseId=getId(self.tableAddressHouse, houseFields)
        if not houseId:
            return

        addressFields=[('house_id', houseId), ('flat', flat)]
        addressId=getId(self.tableAddress, addressFields)
        if not addressId:
            return

        clientAddressFields=[('client_id', clientId), ('type', type), ('address_id', addressId)]
        clientAddressFields2=[('freeInput', ADRES)]
        clientAddressId=getId(
            self.tableClientAddress, clientAddressFields, clientAddressFields2)
        if not clientAddressId:
            return

        if type:
            self.n_adr_f+=1
        else:
            self.n_adr_r+=1

    def findClientBySNILS(self, SNILS):
        record = self.db.getRecordEx(self.tableClient, 'id',
            [self.tableClient['deleted'].eq(0),
            self.tableClient['SNILS'].eq(SNILS)], 'id')
        if record:
            return forceRef(record.value(0))
        else:
            return None


    def findClientByNameSexAndBirthDate(self, lastName, firstName, patrName, sex, birthDate):
        record = self.db.getRecordEx(self.tableClient, 'id, SNILS',
            [self.tableClient['deleted'].eq(0),
                self.tableClient['lastName'].eq(lastName),
                self.tableClient['firstName'].eq(firstName),
                self.tableClient['patrName'].eq(patrName),
                self.tableClient['sex'].eq(sex),
                self.tableClient['birthDate'].eq(birthDate)], 'id')
        if record:
            return forceRef(record.value('id')), record
        else:
            return None, None


    def findClientByPolicy(self, policySerial,  policyNumber):
        record = self.db.getRecordEx(self.tableClientPolicy, 'client_id',
            [self.tableClientPolicy['deleted'].eq(0),
            self.tableClientPolicy['serial'].eq(policySerial),
            self.tableClientPolicy['number'].eq(policyNumber)], 'client_id')
        if record:
            return forceRef(record.value(0))
        else:
            return None


    def findClientByDocument(self, documentTypeId, serial, number):
        record = self.db.getRecordEx(self.tableClientDocument, 'client_id',
            [self.tableClientDocument['deleted'].eq(0),
            self.tableClientDocument['documentType_id'].eq(documentTypeId),
            self.tableClientDocument['serial'].eq(serial),
            self.tableClientDocument['number'].eq(number)], 'client_id')
        if record:
            return forceRef(record.value(0))
        else:
            return None


    def findClientDocument(self, clientId, documentTypeId, serial, number):
        record = self.db.getRecordEx(self.tableClientDocument, 'id',
            [self.tableClientDocument['deleted'].eq(0),
            self.tableClientDocument['documentType_id'].eq(documentTypeId),
            self.tableClientDocument['client_id'].eq(clientId),
            self.tableClientDocument['serial'].eq(serial),
            self.tableClientDocument['number'].eq(number)], 'id')
        if record:
            return forceRef(record.value(0))
        else:
            return None


    def getDocumentTypeId(self, regionalCode):
        result = self.documentTypeCache.get(regionalCode,  -1)

        if result == -1:
            result = forceRef(self.db.translate(self.tbl_rbDocumentType, 'regionalCode', regionalCode, 'id'))
            self.documentTypeCache[regionalCode] = result

        return result


    def getDocumentTypeIdByName(self, name):
        result = self.documentTypeNameCache.get(name,  -1)

        if result == -1:
            result = forceRef(self.db.translate(self.tbl_rbDocumentType, 'name', name, 'id'))
            self.documentTypeNameCache[name] = result

        return result


    def addDocumentType(self, name):
        record = self.tbl_rbDocumentType.newRecord()
        record.setValue('name', toVariant(name))
        record.setValue('group_id', toVariant(self.docTypeGroupId))
        self.documentTypeNameCache[name] = self.db.insertRecord(self.tbl_rbDocumentType, record)
        return self.documentTypeNameCache.get(name)


    def getSocStatusTypeId(self, regionalCode):
        result = self.socStatusTypeCache.get(regionalCode,  -1)

        if result == -1:
            record = self.db.getRecordEx(self.tbl_rbSocStatusType, 'id',
                self.tbl_rbSocStatusType['regionalCode'].eq(regionalCode), 'id')

            if record:
                result = forceRef(record.value(0))
            else:
                self.log.append(u'<b><font color=red>ОШИБКА</b>:'\
                    u' Соц. статус с региональным кодом `%s` не найден в БД' % regionalCode)
                result = None

            self.socStatusTypeCache[regionalCode] = result

        return result


    def adviseInsurerId(self, serial):
        u""" подобрать с.к. по серии полиса """
        result = self.mapPolicySerialToInsurerId.get(serial,  -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrgPolicySerial, 'organisation_id',
                                    self.tableOrgPolicySerial['serial'].eq(serial))
            result = forceRef(record.value(0)) if record else None
            self.mapPolicySerialToInsurerId[serial] = result

        return result


    def addClient(self, lastName, firstName, patrName, birthDate, sex, SNILS):
        record = self.tableClient.newRecord()
        record.setValue('lastName',  toVariant(lastName))
        record.setValue('firstName', toVariant(firstName))
        record.setValue('patrName',  toVariant(patrName))
        record.setValue('birthDate', toVariant(birthDate))
        record.setValue('sex',       toVariant(sex))
        record.setValue('SNILS',     toVariant(SNILS))
        clientId =self.db.insertRecord(self.tableClient, record)
        return clientId


    def addClientDocument(self, clientId, documentTypeId, serial, number):
        if documentTypeId:
            record = self.tableClientDocument.newRecord()
            record.setValue('client_id', toVariant(clientId))
            record.setValue('documentType_id', toVariant(documentTypeId))
            record.setValue('serial', toVariant(serial))
            record.setValue('number', toVariant(number))
            return self.db.insertRecord(self.tableClientDocument, record)


    def addClientPolicy(self, clientId, insurerId, policyTypeId, serial, number, begDate, endDate,  note):
        record = self.tableClientPolicy.newRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('insurer_id', toVariant(insurerId))
        record.setValue('policyType_id', toVariant(policyTypeId))
        record.setValue('serial', toVariant(serial))
        record.setValue('number', toVariant(number))
        record.setValue('begDate', toVariant(begDate))
        record.setValue('endDate', toVariant(endDate))
        record.setValue('note',  toVariant(note))
        self.db.insertRecord(self.tableClientPolicy, record)


    def addClientSocStatus(self,  clientId,  classId,  statusTypeId, begDate, endDate, documentId):
        if classId and statusTypeId:
            record = self.tbl_ClientSocStatus.newRecord()
            record.setValue('socStatusType_id',  toVariant(statusTypeId))
            record.setValue('socStatusClass_id',  toVariant(classId))
            record.setValue('client_id',  toVariant(clientId))
            record.setValue('begDate',  toVariant(begDate))
            record.setValue('endDate',  toVariant(endDate))
            record.setValue('document_id', toVariant(documentId))
            self.db.insertRecord(self.tbl_ClientSocStatus,  record)


    def getFederalBenefitClientDict(self, actualDate):
        u"""Получает словарь client_id->set([id льготы]), имеющих федеральную льготу на актуальнную дату."""

        dateStr = actualDate.toString(Qt.ISODate)
        result = {}

        stmt = """SELECT ClientSocStatus.id, ClientSocStatus.client_id
        FROM ClientSocStatus
        LEFT JOIN rbSocStatusClass ON rbSocStatusClass.id = ClientSocStatus.socStatusClass_id
        WHERE ClientSocStatus.deleted = 0 AND rbSocStatusClass.group_id = %d AND
            ClientSocStatus.begDate <= '%s' AND ClientSocStatus.endDate >= '%s'
        """ % (self.socStatusClassId,  dateStr, dateStr)

        query = self.db.query(stmt)

        if query:

            while query.next():
                record = query.record()

                if record:
                    id = forceRef(record.value(0))
                    clientId = forceRef(record.value(1))

                    if result.has_key(clientId):
                        result[clientId].add(id)
                    else:
                        result[clientId] = set([id])

        return result


    def closeFederalBenefit(self, federalBenefitInfo, actualDate):
        for item in federalBenefitInfo.itervalues():
            for id in item:
                record = self.db.getRecord(self.tbl_ClientSocStatus, 'endDate', id)
                if record:
                    record.setValue(0, actualDate)
                    self.db.updateRecord(self.tbl_ClientSocStatus, record)


def dbfFields():
    fields=[
        'SS', 'LKN1', 'DATE_BL', 'DATE_EL', 'NAME_DL', 'SER_DL', 'NUMB_DL', 'DATE_VD',
        'FAM', 'IM', 'OT', 'DR', 'W', 'ADRES_R', 'ADRES_F',
        'NAME_P', 'SER_P', 'NUMB_P', 'DATE_VP', 'NAME_VP']
    return fields

def str2date(s):
    return QDate.fromString(s, 'yyyy/MM/dd')

def formatSerial(SER_P):
    if re.match(u'^\d{4}$', SER_P):
        return SER_P[:2]+' '+SER_P[2:]
    else:
        return SER_P

def formatNumber(NUMB_P):
    if NUMB_P[:1]==u'0':
        return formatNumber(NUMB_P[1:])
    else:
        return NUMB_P

re_spb=re.compile(u'^(СПБ|Г САНКТ-ПЕТЕРБУРГ|Г.САНКТ-ПЕТЕРБУРГ|Г. САНКТ-ПЕТЕРБУРГ|САНКТ-ПЕТЕРБУРГ Г|САНКТ-ПЕТЕРБУРГ)( |,)')
