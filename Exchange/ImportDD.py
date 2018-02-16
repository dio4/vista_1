#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Ui_ImportDD import Ui_Dialog
from Cimport import *
from Utils  import *
from DBFFormats import *

def ImportDD():
    dlg = CImportDD()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportDDFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportDDFileName'] = toVariant(dlg.edtFileName.text())

class CImportDD(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CImport.__init__(self)
        self.progressBar.setFormat('%p%')
        self.fillComboBox()
        self.cmbPolis.addItem(u'производственный', toVariant('pro'))
        self.cmbPolis.addItem(u'территориальный', toVariant('ter'))
        self.cmbPolis.addItem(u'не задано', toVariant('nz'))
        self.checkName()
    
    def fillComboBox(self):
        startYear = 2007
        endYear   = QtCore.QDate().currentDate().year()
        for y in range(startYear, endYear+1):
            self.comboBox.addItem(
                u'для ДД с 01.01.%d по 31.12.%d'%(y, y),
                toVariant('%d'%y))
        self.comboBox.addItem(u'не подлежат ДД', toVariant(''))
        self.comboBox.addItem(u'без ДД', toVariant(u'без ДД'))

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
            
    @QtCore.pyqtSlot(int)
    def on_chkAddNewPatients_stateChanged(self, state):
        updatePatients = self.chkUpdatePatients.isChecked()
        addNewPatients = self.chkAddNewPatients.isChecked()
        self.btnImport.setEnabled(updatePatients or addNewPatients)
    @QtCore.pyqtSlot(int)
    def on_chkUpdatePatients_stateChanged(self, state):
        updatePatients = self.chkUpdatePatients.isChecked()
        addNewPatients = self.chkAddNewPatients.isChecked()
        self.btnImport.setEnabled(updatePatients or addNewPatients)
        
    def startImport(self):
        n    = 0
        n_ld = 0
        attachYear = None 
        attachType = None
        atbx=forceString(self.comboBox.itemData(self.comboBox.currentIndex()))
        if atbx and atbx != u'без ДД':
            attachYear = forceInt(atbx)
            attachType = 5
        polisType=forceString(self.cmbPolis.itemData(self.cmbPolis.currentIndex()))
        INN_import=''
        if self.checkINN.isChecked():
            INN_import=self.edtINN.text()
            
        addPatients    = self.chkAddNewPatients.isChecked()
        updatePatients = self.chkUpdatePatients.isChecked()
        if updatePatients:
            dependentGetId = findAndUpdateOrCreateRecord
        else:
            dependentGetId = getId

        dbfFileName = unicode(self.edtFileName.text())
        dbfDD       = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')

        DDfields=get_DD_fields()
        assert dbfCheckNames(dbfDD, DDfields)
        dbf_SMO_SHORT=dbfCheckNames(dbfDD, ['SMO_SHORT'])

        tableinfisSTREET = tbl('kladr.infisSTREET')
        tableinfisAREA   = tbl('kladr.infisAREA')

        self.progressBar.setMaximum(len(dbfDD)-1)
        dbfFields = dbfDD.fieldNames
        for row in dbfDD:
            QtGui.qApp.processEvents()
            if self.abort: break
            self.progressBar.setValue(n)
            self.stat.setText(u'обработано: '+str(n_ld))
            n += 1
            self.n   = n
            self.row = row
            if polisType == 'pro':
                if isNull(row['INN_N']):
                    continue
            if isNull(row['POLIS_SERI']) or isNull(row['POLIS_NUMB']):
                continue
            if row['SURNAME'] == u'Быков':
                pass
            if updatePatients and not addPatients:
                if not checkPatientData(self, 'SURNAME', 'NAME', 'SECOND_NAM', 'SEX', 'BIRTHDAY'):
                    continue
            if addPatients and not updatePatients:
                if checkPatientData(self, 'SURNAME', 'NAME', 'SECOND_NAM', 'SEX', 'BIRTHDAY'):
                    continue
            if INN_import:
                if row['INN_N'] != INN_import:
                    continue
            elif atbx and attachType:
                if row['P_DD']:
                    continue
            elif not atbx:
                if not row['P_DD']:
                    continue
            n_ld += 1
            #id клиента
            
            clientId = self.getClientId(
                'SURNAME', 'NAME', 'SECOND_NAM', 'SEX', 'BIRTHDAY')
            if isNull(clientId): 
                continue
            # id документа клиента
            clientDocumentId = None
            if 'DOC_TYPE' in dbfFields:
                clientDocumentId = self._getClientDocumentId(row, clientId, dependentGetId)
            #id страховщика
            insurerId = None
            if 'SMO_CODE' in dbfFields:
                insurerId = self._getInsurerId(row, dependentGetId)
            if isNull(insurerId):
                insurerId = self.get_insurerId(row['SMO_SHORT']) if dbf_SMO_SHORT else None

            if polisType == 'pro':
                policyType_id = 2
            elif polisType == 'ter':
                policyType_id = 1
            elif polisType == 'nz':
                policyType_id = None
            
            #id страхового полиса
            clientPolicyId = self._getClientPolicyId(
                clientId, row['POLIS_SERI'], row['POLIS_NUMB'], insurerId, policyType_id, dependentGetId)

            UNSTRUCT_A = row['UNSTRUCT_A']
            AREA_INF   = forceString(row['AREA_INF'])
            
            #КЛАДР код района
            KLADRCode = ''
            if not isNull(AREA_INF):
                KLADRCode = self._getKLADRCode(row, AREA_INF)
            if not KLADRCode and UNSTRUCT_A:
                KLADRCode = forceString(self.get_KLADRCode(UNSTRUCT_A))

            CODE_INF = row['CODE_INF']
            
            #КЛАДР код улицы
            KLADRStreetCode = ''
            if not isNull(CODE_INF):
                KLADRStreetCode = self._getKLADRStreetCode(row, CODE_INF)
            if not KLADRStreetCode and KLADRCode and UNSTRUCT_A:
                KLADRStreetCode = forceString(self.get_KLADRStreetCode(
                                              UNSTRUCT_A, KLADRCode, UNSTRUCT_A))
            if not KLADRStreetCode and UNSTRUCT_A:
                pos1 = UNSTRUCT_A.find(u'СПб')
                if pos1 >= 0:
                    pos1 += 3
                else:
                    pos1 = UNSTRUCT_A.find(u'Петербург')
                    if pos1 >= 0:
                        pos1 += 9
                pos2 = UNSTRUCT_A.rfind(u'д.')
                if pos1 >= 0 and pos2 >= 0:
                    UL = UNSTRUCT_A[pos1:pos2].strip()
                    if UL and UL[0] in ['.', ',']: 
                        UL = UL[1:]
                    UL = UL.split(',')[0].strip()
                    KLADRStreetCode = forceString(self.get_KLADRStreetCode(UL, '7800000000000', ''))
                    
            #id дома, id -> Address.house_id
            houseId = None
            if KLADRStreetCode not in [None, '*', ''] and KLADRCode not in [None, '*', '']:
                houseId = self._getHouseId(row, KLADRCode, KLADRStreetCode)

            FLAT = row['FLAT']
            #id адреса, id -> ClientAddress.address_id
            addressId = None
            if not isNull(houseId) and not isNull(FLAT):
                addressFields = [('house_id', houseId), ('flat', FLAT)]
                addressId = getId(self.tableAddress, addressFields)

            UNSTRUCT_A = row['UNSTRUCT_A']
#            UNSTRUCT_A = forceString(UNSTRUCT_A)+'; '+forceString(CODE_INF) #test
#            UNSTRUCT_A += '; '+forceString(row['TYPE_INF']) #test

            # адрес мог поменяться, поэтому допускается поменять address_id на NULL
            clientAddressFields  = [('client_id', clientId), ('type', 0), ('address_id', addressId)]
            clientAddressFields2 = [('freeInput', UNSTRUCT_A)]
            clientAddressId = dependentGetId(
                self.tableClientAddress, clientAddressFields, clientAddressFields2)


#            нет такого поля сейчас
#            GR_OKVED=getOKVED(row['GR_OKVED'])
            OKVED = getOKVED(row['OKVED'])
            INN_N = row['INN_N']
            #id работодателя
            Organisation_id = None
            if not isNull(INN_N):
                OrganisationFields=[('INN', INN_N)]
                NAME_KR = row['NAME_KR']
                if isNull(NAME_KR) or NAME_KR == '-':
                    NAME_KR = row['NAME_PKC']
                OrganisationFields2=[
                        ('fullName', row['NAME_PKC']), ('shortName', NAME_KR), ('title', NAME_KR), 
                        ('OKVED', OKVED),
                        ('KPP', row['KPP_N'].strip()),
    #                    ('region', row['RAION']), НЕТУ!!!
                        ('Address', row['UR_ADR'])]
                Organisation_id=dependentGetId(
                    self.tableOrganisation, OrganisationFields, OrganisationFields2)
                    
            if not isNull(Organisation_id):   #Изменения, раньше был ОКВЭД работы и работника? 
#                OKVED=getOKVED(row['OKVED'])  #Теперь только работы
                ClientWorkFields=[
                    ('client_id', clientId), 
                    ('org_id', Organisation_id) 
#                    ('OKVED', OKVED)
                    ]
                ClientWorkFields2=[('post', ''), ('stage', 0)]
                ClientWorkId=getId(self.tableClientWork, ClientWorkFields, ClientWorkFields2)
            #id LPU
            Organisation_id=None
            OrganisationRecord=None
            CODE=forceString(toVariant(row['CODE']))
            org_inf_found=False
            if not isNull(CODE):
                OrganisationRecord=self.infis2org(CODE)
                if OrganisationRecord: 
                    org_inf_found=True
            LPU_PRINT = forceString(toVariant(row['LPU_PRINT']))
            if isNull(OrganisationRecord):
                Organisation_id=self.lpuFind(LPU_PRINT)
                if isNotNull(Organisation_id):
                    cond=[]
                    cond.append(self.tableOrganisation['id'].eq(toVariant(Organisation_id)))
                    OrganisationList=self.db.getRecordList(self.tableOrganisation, where=cond)
                    if OrganisationList:
                        OrganisationRecord=OrganisationList[0]
            if not isNull(OrganisationRecord):
                if isNull(forceString(OrganisationRecord.value('title'))):
                    OrganisationRecord.setValue(QString('title'), toVariant(LPU_PRINT))
                obsoleteInfisCode=forceString(OrganisationRecord.value('obsoleteInfisCode'))
                infisCode=forceString(OrganisationRecord.value('infisCode'))
                if not org_inf_found:
                    if isNull(infisCode):
                        OrganisationRecord.setValue(QString('infisCode'), toVariant(CODE))
                    elif infisCode!=CODE:
                        if isNull(obsoleteInfisCode):
                            OrganisationRecord.setValue(
                                QString('obsoleteInfisCode'), toVariant(CODE))
                        elif not re.match('.*,'+CODE+',.*', ','+obsoleteInfisCode+','):
                            OrganisationRecord.setValue(
                                QString('obsoleteInfisCode'), toVariant(obsoleteInfisCode+','+CODE))
                self.db.updateRecord(self.tableOrganisation, OrganisationRecord)
                Organisation_id=OrganisationRecord.value('id').toInt()[0] 
            lpuId=Organisation_id

            if not isNull(Organisation_id):
                ClientAttachFields  = [
                    ('client_id', clientId), ('attachType_id', 2), ('LPU_id', Organisation_id)]
                ClientAttachFields2 = [('LPU_id', Organisation_id)]
                if not isNull(clientDocumentId):
                    ClientAttachFields2.append(('document_id', clientDocumentId))
                dependentGetId(self.tableClientAttach, ClientAttachFields, ClientAttachFields2)
            if attachType and attachYear != u'без ДД':
                if Organisation_id != self.my_org_id:
                    begDate=datetime.date(attachYear, 1, 1)
                    endDate=datetime.date(attachYear, 12, 31)
                    ClientAttachFields  = [
                        ('client_id', clientId), ('attachType_id', attachType), ('begDate', begDate), ('endDate', endDate), ('LPU_id', self.my_org_id)]
                    ClientAttachFields2 = [('LPU_id', self.my_org_id)]
                    if not isNull(clientDocumentId):
                        ClientAttachFields2.append(('document_id', clientDocumentId))
                    dependentGetId(self.tableClientAttach, ClientAttachFields)
        self.progressBar.setValue(n-1)
        
    def _getClientDocumentId(self, row, clientId,  getId):
        DOC_TYPE=row['DOC_TYPE']
        if DOC_TYPE==u'н':
            serial_value=toVariant(
            ' '.join([row['SERIA_LEFT'], row['SERIA_RIGH']]))
            clientDocumentFields=[
                ('client_id', clientId), ('documentType_id', '1')]
            clientDocumentFields2 = [
                ('serial', serial_value), ('number', row['DOC_NUMBER'])]
            return getId(self.tableClientDocument, clientDocumentFields, clientDocumentFields2)
        return None
        
    def _getKLADRCode(self, row, AREA_INF):
        KLADRCode = ''
        cond = []
        cond.append(self.tableKLADR['infis'].eq(toVariant(AREA_INF)))
        cond.append(self.tableKLADR['CODE'].like('78%'))
        KLADRList=self.db.getRecordList(self.tableKLADR, where=cond)
        if KLADRList:
            KLADRCode=forceString(KLADRList[0].value('CODE'))
        else:
            if len(AREA_INF)==2:
                KLADRCode='7800000000000' #Спб
        return KLADRCode
        
    def _getKLADRStreetCode(self, row, CODE_INF):
        KLADRStreetCode = ''
        cond=[]
        GEONIM_TYP=row['GEONIM_TYP']
        if GEONIM_TYP:
            cond.append(self.tableSTREET['SOCR'].eq(toVariant(GEONIM_TYP[:-1])))
        cond.append(self.tableSTREET['CODE'].like('78000000000%'))
        cond.append(self.tableSTREET['infis'].eq(toVariant(CODE_INF)))
        STREETList=QtGui.qApp.db.getRecordList(self.tableSTREET, where=cond)
        CODE_list=[forceString(x.value('CODE')) for x in STREETList]
        if CODE_list:
            KLADRStreetCode=CODE_list[0]
        return KLADRStreetCode
        
    def _getHouseId(self, row, KLADRCode, KLADRStreetCode):
        houseId = None
        HOUSE   = row['HOUSE']
        KORPUS  = row['KORPUS']
        if not isNull(HOUSE):
            houseFields = [
                ('KLADRCode', KLADRCode), ('KLADRStreetCode', KLADRStreetCode), ('number', HOUSE)]
            if KORPUS:
                houseFields.append(('corpus', KORPUS))
            houseId = getId(self.tableAddressHouse, houseFields)
        return houseId
        
    def _getClientPolicyId(self, client_id, serial, number, insurer_id, policyType_id, getId):
        if isNull(serial) or isNull(number):
            self.err2log(u'не указан полис')
            return None
        clientPolicyFields=[('client_id', client_id), ('serial', serial), ('number', number)]
        clientPolicyFields2=[('insurer_id', insurer_id), ('policyType_id', policyType_id)]
        return getId(
            self.tableClientPolicy, clientPolicyFields, clientPolicyFields2)
            
    def _getInsurerId(self, row, getId):
        SMO_CODE = row['SMO_CODE']
        if isNull(SMO_CODE):
            return None
        id=self.smo_ins.get(SMO_CODE, -1)
        if id != -1:
            return id
        id=None
        cond=[]
        cond.append(self.tableOrganisation['title'].eq(toVariant(SMO_CODE)))
        cond.append(self.tableOrganisation['isInsurer'].eq(toVariant(1)))
        insurerList=self.db.getIdList(self.tableOrganisation, where=cond)
        if insurerList!=[]:
            id=insurerList[0]
        if not id:
            cond=[]
            cond.append(self.tableOrganisation['infisCode'].eq(toVariant(SMO_CODE)))
            cond.append(self.tableOrganisation['isInsurer'].eq(toVariant(1)))
            insurerList=self.db.getIdList(self.tableOrganisation, where=cond)
            if insurerList!=[]:
                id=insurerList[0]
        self.smo_ins[SMO_CODE]=id
        return id
