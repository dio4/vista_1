#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Events.Utils import *

from Ui_Import131 import Ui_Dialog
from Cimport import *
from Utils import *

def Import131(widget):
    dlg = CImport131(widget)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'Import131FileName',  '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['Import131FileName'] = toVariant(dlg.edtFileName.text())

class CImport131(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.logBrowser)
        self.progressBar.setFormat('%p%')
        self.checkName()
        self.eventTypeCache = {}
        self.resultCodeCache = {}
        self.personCache = {}
        self.spec_codeCache = {}
        self.spec_OKSOCache = {}
        self.MKB_charCache = {}
        self.tablePerson=tbl('Person')
        self.tablerbResult=tbl('rbResult')
        self.tableEventType=tbl('EventType')
        self.tableDiagnosis=tbl('Diagnosis')
        self.tableDiagnostic=tbl('Diagnostic')
        self.tableMKB=tbl('MKB')
        self.tableEvent=tbl('Event')
        self.tableAction=tbl('Action')
        self.tableVisit=tbl('Visit')
        self.tableClientWork_Hurt=tbl('ClientWork_Hurt')
        self.tableClientWork_Hurt_Factor=tbl('ClientWork_Hurt_Factor')
        self.P_LPY_NAME_Field='P_LPY_NAME'
        self.P_LPY_KOD_Field='P_LPY_KOD'
        self.P_LPY_OGRN_Field='P_LPY_OGRN'

    def err2log(self, e):
        fio=self.get_field('FAM')+' '+self.get_field('IM')+' '+self.get_field('OT')
        self.log.append(u'запись '+str(self.n)+' (id=\"'+self.get_field('ID')+u'\"; '+fio+'): '+e)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbf131 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbf131)))

    def get_field(self, name):
        col=self.header_ind[name]
        return self.row[col]

    def startImport(self):
        self.progressBar.setFormat('%p%')

        self.workNameField='shortName' if self.checkShortWork.isChecked() else 'fullName'
        self.codeField='federalCode' if self.checkFed.isChecked() else 'code'
        self.LPYnameField='shortName' if self.checkShortLPU.isChecked() else 'fullName'
        self.cur_year_only=self.checkDate.isChecked()
        self.attachOGRN=self.checkAttachOGRN.isChecked()
        self.noOwn=self.checkNoOwn.isChecked()
        self.useOGRN2=self.checkOGRN2.isChecked()
        self.OGRN2=forceStringEx(self.edtOGRN2.text())

        n=0
        self.ngood=0
        self.nbad=0
        self.nevent=0
        self.nfound=0

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbf131 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        dbf_Fields=dbfFields()
        assert dbfCheckNames(dbf131, dbf_Fields),u'не хватает полей в DBF'

        self.dbf_SMO_NAME=dbfCheckNames(dbf131, ['SMO_NAME'])
        self.dbf_ADRES=dbfCheckNames(dbf131, ['ADRES'])
        self.dbf_SMO=dbfCheckNames(dbf131, ['SMO'])
        self.dbf_Contract=dbfCheckNames(dbf131, ['NOMER_DOG', 'DATE_DOG'])
        self.dbf_DZ_MKB=dbfCheckNames(dbf131, ['DZ_MKB'])
        self.dbf_PASSPORT=dbfCheckNames(dbf131, ['PASSPORT'])
        self.dbf_DATE_BIG=dbfCheckNames(dbf131, ['DATE_BIG'])
        self.dbf_EXPWRK=dbfCheckNames(dbf131, ['EXPWRK'])
        self.dbf_INN=dbfCheckNames(dbf131, ['INN'])

        self.dbf_P_LPY_KOD=dbfCheckNames(dbf131, ['P_LPY_KOD'])
        if not self.dbf_P_LPY_KOD and dbfCheckNames(dbf131, ['P_LPU_KOD']):
            self.dbf_P_LPY_KOD=True
            self.P_LPY_KOD_Field='P_LPU_KOD'
        self.dbf_P_LPY_OGRN=dbfCheckNames(dbf131, ['P_LPY_OGRN'])
        if not self.dbf_P_LPY_OGRN and dbfCheckNames(dbf131, ['P_LPU_OGRN']):
            self.dbf_P_LPY_OGRN=True
            self.P_LPY_OGRN_Field='P_LPU_OGRN'
        self.dbf_P_LPY_NAME=dbfCheckNames(dbf131, ['P_LPY_NAME'])
        if not self.dbf_P_LPY_NAME and dbfCheckNames(dbf131, ['P_LPU_NAME']):
            self.dbf_P_LPY_NAME=True
            self.P_LPY_NAME_Field='P_LPU_NAME'

        fields=dbf131.header.fields
        header=[f.name for f in fields]
        self.header_ind={}; ind=0
        for h in header:
            self.header_ind[h]=ind
            ind+=1

        dbf_len=len(dbf131)
        self.progressBar.setMaximum(dbf_len-1)
        self.labelNum.setText(u'всего записей в источнике: '+str(dbf_len))
        for row in dbf131:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.n=n+1
            self.row=row
            self.processRow()
            n+=1
            self.progressBar.setValue(n)
            self.statusLabel.setText(u'импорт карточек: %d прошли контроль; %d не прошли контроль; %d добавлено; %d найдено' % (self.ngood, self.nbad, self.nevent, self.nfound))
        self.progressBar.setValue(n-1)


    def processPerson(self, personName, specialityId, personCode, personDate, personSl, numDiags, dbfFieldPrefix):
        if str(personDate).replace('#','').strip()=="":
            personDate=None
        if type(personDate) in [str, unicode]:
            format='dd.MM.yyyy' if len(personDate)==10 else 'dd.MM.yy'
            personDate=QDate.fromString(personDate, format)
        if personDate and personDate>self.DATE_ZAV:
            self.err2log(u'дата осмотра позже DATE_ZAV')
        if personDate:
            if personDate>self.DATE_ZAV:
                personDate=self.DATE_ZAV
            self.dateList.append(personDate)

        personId=self.getPersonId(personName, specialityId, personCode)

        for iDiag in range(1, numDiags+1):
            diag=self.get_field(dbfFieldPrefix+'_MKB_'+str(iDiag)).upper()
            specV=self.get_field(dbfFieldPrefix+'_V_'+str(iDiag))
            if specV: specV=int(specV)
            specSt=self.get_field(dbfFieldPrefix+'_ST_'+str(iDiag))
            if specSt: specSt=int(specSt)
            specGz=self.get_field(dbfFieldPrefix+'_GZ_'+str(iDiag))
            if specGz: specGz=int(specGz)
            if diag and not specGz:
                self.err2log(u'не указана группа здоровья')
            if not diag and (iDiag>1 or numDiags==1):
                continue
            specSt=specV
            characterId=None
            if specV==2 or specSt==4:
                characterId=3
            Diagnosis_diagnosisType_id=5
            stage_id=None
            if specGz==6:
                stage_id=3
                if diag[:1] in ['Z', 'z']:
                    specGz=1
                else:
                    specGz=3
            if not stage_id:
                if specSt==3:
                    stage_id=1
                elif specSt==4:
                    stage_id=2
            if len(diag)==4:
                diag=diag[0:3]
            elif len(diag)>5:
                diag=diag[0:5]
            if diag and diag[:1] not in ['Z', 'z']:
                MKBchar=self.get_MKB_char(diag)
                if MKBchar==0: characterId=None
                elif MKBchar==1:
                    characterId=1
                    if specV==1: stage_id=1
                    else: stage_id=2
                elif MKBchar<5:
                    characterId=MKBchar
                elif MKBchar==5:
                    if specV==1:
                        characterId=2
                    else:
                        characterId=3
                elif MKBchar==6:
                    if specV==1:
                        characterId=2 # острое?
                    else:
                        characterId=3
            zak=False
            if self.DZ_MKB and diag==self.DZ_MKB and iDiag!=1:
                self.err2log(u'сопутствующий диагноз назначен заключительным')
                self.DZ_MKB=None
            if iDiag==1:
                if self.DZ_MKB and diag==self.DZ_MKB:
                    zak=True;
                    self.DZ_MKB_set=True
                elif diag and not self.DZ_MKB_set:
                    Diagnosis_diagnosisType_id=2
                    if self.zakDiagNum==None:
                        zak=True
                    elif not isNull(specGz) and not isNull(self.zakDiagGZ):
                        if specialityId==78:
                            zak=True
                        elif self.zakSpec==78:
                            if specGz>self.zakDiagGZ:
                                zak=True
                        else:
                            if specGz==self.zakDiagGZ:
                                if not isNull(diag) and not isNull(self.zakDiagMKB):
                                    if diag[0]<self.zakDiagMKB[0]:
                                        zak=True
                            elif specGz>self.zakDiagGZ:
                                zak=True
            if zak:
                self.zakDiagNum=len(self.DiagList)
                self.zakDiagGZ=specGz
                self.zakDiagMKB=diag
                self.zakSpec=specialityId
                result= 31 if specGz in [3, 4, 5] else 30
                self.resultId=self.get_resultId(result)
            if diag[:1] in ['Z', 'z']:
                Diagnosis_diagnosisType_id=7
                stage_id=None
                characterId=None
            if not diag:
                characterId=None
            date = QDate(personDate) if personDate else QDate()
            Diagnosis_id, characterId = get_DiagnosisId2 (
                date, personId, self.clientId, Diagnosis_diagnosisType_id, diag, None, characterId, None, None)
            if not Diagnosis_id:
                continue

#            if diag[:1] in ['Z', 'z'] and characterId:
#                pass

            Diagnostic_diagnosisType_id=5
            if iDiag==1: Diagnostic_diagnosisType_id=2
            if specGz==0: specGz=1
            sanatorium = 1 if personSl==1 else 0

            DiagnosticFields=[
                ('character_id', characterId), ('stage_id', stage_id), ('sanatorium', sanatorium), ('speciality_id', specialityId), ('person_id', personId), ('healthGroup_id', specGz), ('endDate', personDate), ('diagnosis_id', Diagnosis_id)]
            result= 31 if specGz in [3, 4, 5] else 30
            resultId=self.get_resultId(result)
            DiagnosticFields.append(('result_id', resultId))
            self.DiagList.append(
                (DiagnosticFields, Diagnostic_diagnosisType_id, personDate))

    def getPersonId(self, FIO, specialityId, KOD):
        key=(FIO, specialityId, KOD)
        result = self.personCache.get(key, None)
        if result:
            return result
        orgId=self.eventOrgId
        if FIO:
            FIO = FIO.split('(')[0]                     # т.к. у СВ после фио в скобках специальность
            FIO = nameCase(trim(FIO.replace('_', ' '))) # и ещё подчерки вместо пробелов
            splitedFIO=FIO.split()
            lFIO=len(splitedFIO)
            lastName, firstName, patrName = '', '', ''
            if lFIO:
                lastName=splitedFIO[0]
            if lFIO>1:
                firstName=splitedFIO[1]
            if lFIO>2:
                patrName=' '.join(splitedFIO[2:])

            personKey = (lastName, firstName, patrName, specialityId, orgId)
            result = self.mapPersonKeyToId.get(personKey, 0)
            if result==0:
                cond=[]
                cond.append(self.tablePerson['lastName'].eq(lastName))
                cond.append(self.tablePerson['firstName'].eq(firstName))
                cond.append(self.tablePerson['patrName'].eq(patrName))
                cond.append(self.tablePerson['speciality_id'].eq(specialityId))
                cond.append(self.tablePerson['org_id'].eq(orgId))
                record = self.db.getRecordEx(self.tablePerson, ['id', self.codeField], where=cond)
                if record:
                    code=forceString(record.value(self.codeField))
                    if (KOD and not code) or orgId != self.my_org_id:
                        record.setValue(self.codeField, toVariant(KOD))
                        self.db.updateRecord(self.tablePerson, record)
                    result=forceRef(record.value('id'))

                if not result:
                    record = self.tablePerson.newRecord()
                    record.setValue('lastName',  toVariant(lastName))
                    record.setValue('firstName', toVariant(firstName))
                    record.setValue('patrName', toVariant(patrName))

                    record.setValue('speciality_id', toVariant(specialityId))
                    record.setValue('org_id', toVariant(orgId))
                    if KOD:
                        record.setValue(self.codeField, toVariant(KOD))
                    record.setValue('finance_id', toVariant(2)) # magic
                    result=self.db.insertRecord(self.tablePerson, record)
                self.mapPersonKeyToId[personKey] = result
        if result:
            self.personCache[key]=result
        return result

    def get_attachType(self, TIP_DD):
        attachType=None
        if TIP_DD in TIP_DD_b:
            attachType=5
        if self.checkTIP_DD_R.isChecked():
            if attachType==None and TIP_DD in TIP_DD_r:
                attachType=5
        if self.checkTIP_DD_V.isChecked():
            if attachType==None and TIP_DD in TIP_DD_v:
                attachType=4
        return attachType

    def getEventType(self, ddType):
        endDate=self.DATE_ZAV
        ddType = unicode(ddType)
        eventType=0
        if self.checkTIP_DD_V.isChecked():
            if ddType in [u'В', '859', '869']:
#                if endDate.year==2006: eventType=11
                if endDate.year==2007: eventType=12
        if self.checkTIP_DD_R.isChecked():
            if ddType in [u'Р', '876']:
#                if endDate.year==2006: eventType=25
                if endDate.year==2007: eventType=10
        if ddType in [u'Б', '868', '860', '921', u'921Б']:
#            if endDate.year==2006: eventType=24
            if endDate.year==2007: eventType=10
            if endDate.year==2008: eventType=29
        return eventType

    def addPassport(self, PASSPORT):
        if PASSPORT:
            serial=None; number=None
            p=PASSPORT.replace('_', ' ').split()
            if len(p)==2:
                s, n=p[0], p[1]
                if len(s)==4 and len(n)==6:
                    serial=s[0:2]+' '+s[2:4]
                    number=n
            if len(p)==3:
                s1, s2, n=p[0], p[1], p[2]
                if len(s1)==2 and len(s2)==2 and len(n)==6:
                    serial=s1+' '+s2
                    number=n
            if serial and number:
                ClientDocumentFields=[
                    ('client_id', self.clientId), ('documentType_id', 1),
                    ('serial', serial), ('number', number)]
                return getId(self.tableClientDocument, ClientDocumentFields)
        return None

    def getClientWorkId(self, INN, RABOTA, OKVED, DOLGN, stage):
        organisationId = self.getOrganisationId(INN, self.workNameField, RABOTA)
        if organisationId:
            OKVED = self.unifyOKVED(OKVED)
            ClientWorkFields=[('client_id', self.clientId), ('org_id', organisationId)]
            ClientWorkFields2=[('stage', stage), ('OKVED', OKVED), ('post', DOLGN)]
            ClientWorkId = getId(self.tableClientWork, ClientWorkFields, ClientWorkFields2)
            if stage and not forceInt(self.db.translate('ClientWork', 'id', ClientWorkId, 'stage')):
                record=self.db.getRecord(self.tableClientWork, 'id, stage', ClientWorkId)
                record.setValue('stage', toVariant(stage))
                self.db.updateRecord(self.tableClientWork, record)
            return ClientWorkId
        else:
            self.err2log(u'неопознанное место работы')
            return None

    def get_ClientAddressId(self, NAS_P, UL, DOM, KOR, KV, ADRES_TYPE, ADRES):
        KLADRCode=self.get_KLADRCode(NAS_P)
#        re_bad_np=re.compile('|'.join([u'Жители Лен. области', u'Иногородний']))
#        if NAS_P and not KLADRCode and not re_bad_np.match(NAS_P.strip()):
#            pass
        KLADRStreetCode=None
        if UL and KLADRCode:
            KLADRStreetCode=self.get_KLADRStreetCode(UL, KLADRCode, NAS_P)
#            re_bad_ul=re.compile('|'.join([
#                u'^((ул|д|кв)\.[-\?]|улица|ул\.-д\.-)$', u'без уточнения', u'микрорайон', u'МКР']))
#            if not KLADRStreetCode and not re_bad_ul.match(UL.strip()):
#                 pass
        house_id=None
        DOM=DOM.replace('|', '/')
#        if KLADRCode and KLADRStreetCode and DOM:
        if KLADRCode and DOM:
            cond=[]
            cond.append(self.tableSTREET['CODE'].like(KLADRCode[:11]+'%'))
            if KLADRStreetCode or not QtGui.qApp.db.getRecordEx(self.tableSTREET, '*', where=cond):
                AddressHouseFields=[
                    ('KLADRCode', KLADRCode), ('KLADRStreetCode', KLADRStreetCode),
                    ('number', DOM)]
                if KOR:
                    AddressHouseFields.append(('corpus', KOR))
                house_id=getId(self.tableAddressHouse, AddressHouseFields)
        address_id=None
        if house_id:
            AddressFields=[('house_id', house_id), ('flat', KV)]
            address_id=getId(self.tableAddress, AddressFields)
        freeInput=ADRES
        if isNull(freeInput):
#            address=ADRES_TYPE+NAS_P+u', ул. '+UL+u', д. '+DOM+u', к. '+KOR+u', кв. '+KV
            address = [NAS_P]
            if UL:  address.append(UL)
            if DOM: address.append(u'д. '+DOM)
            if KOR: address.append(u'к. '+KOR)
            if KV:  address.append(u'кв. '+KV)
            freeInput=', '.join(address)
        ClientAddressFields=[('client_id', self.clientId), ('type', '0')]
        ClientAddressFields2=[('freeInput', freeInput), ('address_id', address_id)]
        return getId(self.tableClientAddress, ClientAddressFields, ClientAddressFields2)

    def get_dop(self):
#        POL_dop=None
#        if self.get_field('POL')==1:
#            if self.get_field('UPROST_DI') and self.get_field('UPROST_DP'):
#                POL_dop=('UPROST', 10)
#        else:
#            if self.get_field('M_DI') and self.get_field('M_DP'):
#                MU_VB=9 if self.get_field('MU_VB')==2 else 6
#                POL_dop=('M', MU_VB)
#        dop=[('H', 2), ('G', 3), ('KAK', 4), ('KAM', 5)]
#        if POL_dop: dop.append(POL_dop)
#        dop+=[('F', 7), ('EKG', 8)]
#        return dop

        r1=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code="1-1" and class=1')
        id1=forceInt(r1.value(0))
        r2=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code="1-2" and class=1')
        id2=forceInt(r2.value(0))

        dop0=[
            ('H', '01', id1), ('L', '05', id1), ('T', '06', id1), ('O_CA', '07', id1),
            ('O_PSI', '08', id1), ('G', '02', id1), ('KAK', '03', id1),
            ('KAM', '04', id1), ('F', '06', id2), ('EKG', '07', id2)]
        POL_dop=None
        POL=self.get_field('POL')
        if POL==1:
            if self.get_field('UPROST_DI') and self.get_field('UPROST_DP'):
                POL_dop=('UPROST', '09', id2)
        elif POL==2:
            if self.get_field('M_DI') and self.get_field('M_DP'):
                MU_VB='08' if self.get_field('MU_VB')==2 else '05'
                POL_dop=('M', MU_VB, id2)
        if POL_dop: dop0.append(POL_dop)
        dop = get_dop(dop0)
        return dop

    def get_resultId(self, resultCode):
        result = self.resultCodeCache.get(resultCode, 0)
        if result == 0:
            cond=[]
            cond.append(self.tablerbResult['code'].eq(resultCode))
            cond.append(self.tablerbResult['eventPurpose_id'].eq(3))
            idList=self.db.getIdList(self.tablerbResult, where=cond)
            if idList:
                result = idList[0]
            else:
                result = None
            self.resultCodeCache[resultCode] = result
        return result

    def getEventInfo(self, eventTypeCode):
        result = self.eventTypeCache.get(eventTypeCode, None)
        if not result:
            record = self.db.getRecordEx(
                self.tableEventType, 'id, period, singleInPeriod',
                self.tableEventType['code'].eq(eventTypeCode))
            if record:
                result = (forceInt(record.value(0)), forceInt(record.value(1)), forceInt(record.value(2)))
            else:
                result = (None, 0, 0)
            self.eventTypeCache[eventTypeCode] = result
        return result

    def getAttachLpuId(self):
        lpuId=None
        if self.attachOGRN:
            if self.dbf_P_LPY_OGRN:
                P_LPY_OGRN=self.get_field(self.P_LPY_OGRN_Field)
                if not isNull(P_LPY_OGRN):
                    lpuId=forceInt(self.db.translate('Organisation', 'OGRN', P_LPY_OGRN, 'id'))
        else:
            P_LPY_NAME=self.get_field(self.P_LPY_NAME_Field)
            if self.dbf_P_LPY_KOD:
                P_LPY_KOD=self.get_field(self.P_LPY_KOD_Field)
                if not isNull(P_LPY_KOD):
                    lpuId=self.infis2orgId(P_LPY_KOD)
                    if isNotNull(lpuId):
                        f2=[(self.LPYnameField, P_LPY_NAME)]
                        if self.dbf_P_LPY_OGRN:
                            f2.append(('OGRN', self.get_field(self.P_LPY_OGRN_Field)))
                        getId(self.tableOrganisation, [('id', lpuId)], f2)
            if isNull(lpuId):
                if self.dbf_P_LPY_OGRN:
                    P_LPY_OGRN=self.get_field(self.P_LPY_OGRN_Field)
                    if not isNull(P_LPY_OGRN):
                        lpuId=forceInt(self.db.translate(
                            'Organisation', 'OGRN', P_LPY_OGRN, 'id'))
                if isNull(lpuId) and not isNull(P_LPY_NAME):
                    lpuId=forceInt(self.db.translate(
                        'Organisation', self.LPYnameField, P_LPY_NAME, 'id'))
                    if isNull(lpuId):
                        P_LPY=P_LPY_NAME.split()
                        if P_LPY: lpuId=self.infis2orgId(P_LPY[0])
                if isNotNull(lpuId):
                    f2=[(self.LPYnameField, P_LPY_NAME)]
                    if self.dbf_P_LPY_OGRN:
                        f2.append(('OGRN', self.get_field(self.P_LPY_OGRN_Field)))
                    getId(self.tableOrganisation, [('id', lpuId)], f2)
        if isNull(lpuId):
            self.err2log(u'неопознанное базовое ЛПУ')
        return lpuId

    def get_insurerId(self):
        if not self.dbf_SMO:
            return None
        SMO=self.get_field('SMO')
        if not SMO:
            return None
        insurerId=self.infis2orgId(SMO)
        if insurerId and self.dbf_SMO_NAME:
            SMO_NAME=self.get_field('SMO_NAME')
            getId(self.tableOrganisation, [('id', insurerId)], [('title', SMO_NAME)])
        return insurerId

    def get_contractId(self, lpuId, ClientWorkId):
        if lpuId!=self.my_org_id:
            return None
        query=QtSql.QSqlQuery(QtGui.qApp.db.db)
        q_select='select Contract.id'
        q_from=' from Contract'
        ZAV='\"'+str(self.DATE_ZAV)+'\"'
        q_where=' where ('+ZAV+' between begDate and endDate) and finance_id=5'
        def e():
            stmt=q_select+q_from+q_where
            query.exec_(stmt)
            return query.size()
        def get_id():
            query.next()
            num=query.record().indexOf('id')
            return query.value(num).toInt()[0]
        s=e()
        if s==0: return None
        if s==1: return get_id()
        if self.dbf_Contract:
            NOMER_DOG=self.get_field('NOMER_DOG')
            if NOMER_DOG:
                q_where+=' and number=\"'+NOMER_DOG+'\"'
                s=e()
                if s==0: return None
                if s==1: return get_id()
            DATE_DOG=self.get_field('DATE_DOG')
            if DATE_DOG:
                q_where+=' and date=\"'+str(DATE_DOG)+'\"'
                s=e()
                if s==0: return None
                if s==1: return get_id()
        if isNotNull(self.eventType):
            q_from+=' join Contract_Specification on Contract_Specification.master_id=Contract.id'
            q_where+=' and Contract_Specification.eventType_id=\"'+str(self.eventType)+'\"'
            q_where+=' and Contract_Specification.deleted = 0'
            s=e()
            if s==0: return None
            if s==1: return get_id()
        if ClientWorkId:
            q_from+=' join Contract_Contingent on Contract_Contingent.master_id=Contract.id'
            q_where+=' and Contract_Contingent.org_id=\"'+str(ClientWorkId)+'\"'
            s=e()
            if s==0: return None
            if s==1: return get_id()
        return None

    def getEventId(self, noAdd=False):
        eventId=None
        if self.eventType and self.datemax:
            eventTypeId, period, singleInPeriod = self.getEventInfo(self.eventType)
            self.eventTypeId = eventTypeId
            date = QDate(self.datemax)
            nextEventDate = countNextDate(date, getEventPeriod(period, singleInPeriod), date)
            org_id = self.eventOrgId
            if org_id:
                canCreateEvent, eventId = checkEventPosibility(
                    self.clientId, eventTypeId, None, QDate(self.datemin), QDate(self.datemin))
                if not canCreateEvent and not eventId:
                    self.err2log(u'событие не может быть добавлено')
                    return None
                if eventId:
                    return eventId

                def get_EventId():
                    if noAdd:
                        return None
                    EventRecord=self.tableEvent.newRecord()
                    EventRecord.setValue('externalId', toVariant(self.get_field('ID')))
                    EventRecord.setValue('eventType_id', toVariant(eventTypeId))
                    EventRecord.setValue('org_id', toVariant(org_id))
                    EventRecord.setValue('client_id', toVariant(self.clientId))
                    EventRecord.setValue('contract_id', toVariant(self.contractId))
                    EventRecord.setValue('setDate', toVariant(self.datemin))
                    EventRecord.setValue('setPerson_id', toVariant(self.eventPersonId))
                    EventRecord.setValue('execDate', toVariant(self.datemax))
                    EventRecord.setValue('execPerson_id', toVariant(self.eventPersonId))
                    EventRecord.setValue('isPrimary', toVariant(1))
                    EventRecord.setValue('order', toVariant(1))
                    EventRecord.setValue('nextEventDate', toVariant(nextEventDate))
                    EventRecord.setValue('result_id', toVariant(self.resultId))
                    if self.prevEventDate:
                        EventRecord.setValue('prevEventDate', toVariant(self.prevEventDate))
                    return self.db.insertRecord(self.tableEvent, EventRecord)

                cond=[]
                cond.append(self.tableEvent['eventType_id'].eq(eventTypeId))
                cond.append(self.tableEvent['org_id'].eq(org_id))
                cond.append(self.tableEvent['client_id'].eq(self.clientId))
                cond.append(self.tableEvent['setDate'].eq(self.datemin))
                cond.append(self.tableEvent['execDate'].eq(self.datemax))
                cond.append(self.tableEvent['isPrimary'].eq(1))
                cond.append(self.tableEvent['order'].eq(1))
                eventIdList=self.db.getIdList(self.tableEvent, where=cond)
                if eventIdList:
                    self.nfound+=1
                    self.err2log(u'запись найдена')
                    if org_id==self.my_org_id:
                        record=self.db.getRecord(self.tableEvent, '*', eventIdList[0])
                        if self.prevEventDate and record.isNull('prevEventDate'):
                            record.setValue('prevEventDate', toVariant(self.prevEventDate))
                            self.db.updateRecord(self.tableEvent, record)
                    elif not noAdd:
                        eventId=eventIdList[0]
                        cond=[]
                        cond.append(self.tableVisit['event_id'].eq(eventId))
                        if not self.db.getIdList(self.tableVisit, where=cond):
                            cond=[]
                            cond.append(self.tableEvent['id'].eq(eventId))
                            self.db.deleteRecord(self.tableEvent, where=cond)
                            eventId=get_EventId()
                else:
                    if noAdd:
                        return None
                    eventId=get_EventId()
                    self.nevent+=1
                    if org_id==self.my_org_id:
                        self.make_visits=True
        return eventId

    def getDateRange(self, begDate):
        endDate=self.DATE_ZAV
        maxDate=None
        minDate=None
        if begDate:
            minDate, maxDate = begDate,  endDate
        else:
            if self.dateList:
                maxDate=max(self.dateList)
                if maxDate>endDate:
                    maxDate=endDate
                minDate=min([d for d in self.dateList if maxDate-d<=datetime.timedelta(30)])
        return minDate, maxDate

    def processRow(self):
        self.DATE_ZAV=self.get_field('DATE_ZAV')
        if isNull(self.DATE_ZAV):
            self.err2log(u'не указана дата завершения ДД')
            self.nbad+=1
            return

        d=currentYearBeg<=self.DATE_ZAV and self.DATE_ZAV<=currentYearEnd
        if (not d and self.cur_year_only):
            self.err2log(u'не текущий год')
            self.nbad+=1
            return

        TIP_DD=self.get_field('TIP_DD')
        if TIP_DD not in TIP_DD_b+TIP_DD_r+TIP_DD_v:
            self.err2log(u'неизвестный тип карточки')
            self.nbad+=1
            return

        attachLpuId=self.getAttachLpuId()

        OGRN = self.get_field('OGRN')
        if not OGRN:
            self.err2log(u'ОГРН не указан')
            self.nbad+=1
            return

        self.eventOrgId=self.OGRN2orgId(OGRN)
        if not self.eventOrgId:
            self.err2log(u'в справочнике организаций не найдено ЛПУ с ОГРН '+OGRN)
            self.nbad+=1
            return

        if self.noOwn and self.eventOrgId==self.my_org_id:
            self.err2log(u'карточка этого ЛПУ')
            self.nbad+=1
            return

        noAdd = self.eventOrgId!=self.my_org_id
        if self.useOGRN2 and OGRN==self.OGRN2:
            self.eventOrgId=self.my_org_id
            noAdd = self.eventOrgId!=self.my_org_id

        if self.my_org_id not in [attachLpuId, self.eventOrgId]:
            self.err2log(u'прикрепление и ДД не в этом ЛПУ')
            self.nbad+=1
            return

        self.clientId=self.getClientId('FAM', 'IM', 'OT', 'POL', 'DR')
        if isNull(self.clientId):
            self.err2log(u'пациент не найден и не добавлен')
            self.nbad+=1
            return

        insurerId=self.get_insurerId()
        clientPolicy_id=None
        polis=self.get_field('SN_POLIS').replace('_', ' ').split()
        if len(polis)==2:
            clientPolicy_id=self.get_clientPolicy_id(
                self.clientId, polis[0], polis[1], insurerId)
        else:
            self.err2log(u'неправильный полис')
            self.nbad+=1
            return

        SNILS=unformatSNILS(self.get_field('SNILS'))
        if SNILS:
            getId(self.tableClient, [('id', self.clientId)], [('SNILS', SNILS)])
        else:
            self.err2log(u'не указан СНИЛС')
#            if self.newFormat: self.nbad+=1; return

        ADRES=self.get_field('ADRES').strip() if self.dbf_ADRES else ''
        ClientAddressId=self.get_ClientAddressId(
            self.get_field('NAS_P'), self.get_field('UL'), self.get_field('DOM'), self.get_field('KOR'), self.get_field('KV'), self.get_field('ADRES_TYPE'), ADRES)

        stage=0
        if self.dbf_EXPWRK:
            stage=self.get_field('EXPWRK')
        if not stage:
            stage=self.get_field('WORKS')
        ClientWorkId=None
        if self.dbf_INN:
            ClientWorkId=self.getClientWorkId(
                self.get_field('INN'), self.get_field('RABOTA'),
                self.get_field('OKVED'), self.get_field('DOLGN'), stage)
#        if self.newFormat and not ClientWorkId: self.nbad+=1; return

        if ClientWorkId:
            self.processHurt(ClientWorkId)

        self.prevEventDate=self.get_field('PDATE')

        if self.dbf_PASSPORT: self.addPassport(self.get_field('PASSPORT'))

        attachType=self.get_attachType(TIP_DD)
        begDate=datetime.date(self.DATE_ZAV.year, 1, 1)
        ClientAttachFields2=[('insurer_id', insurerId)]

#                if (lpuId!=self.my_org_id or TIP_DD not in TIP_DD_b) and attachType:
        if (attachLpuId!=self.my_org_id or attachType!=5) and attachType:
            ClientAttachFields=[
                ('client_id', self.clientId), ('attachType_id', attachType),
                ('begDate', begDate), ('endDate', self.DATE_ZAV), ('LPU_id', self.eventOrgId)]
            getId(self.tableClientAttach, ClientAttachFields, ClientAttachFields2)

        if attachLpuId:
            ClientAttachFields=[
                ('client_id', self.clientId), ('attachType_id', 2), ('LPU_id', attachLpuId)]
            getId(self.tableClientAttach, ClientAttachFields, ClientAttachFields2)

        self.eventPersonId=self.getPersonId(
            self.get_field('T_NAME'), 78, self.get_field('T_KOD'))

        specs=get_specs(self.get_field('POL'))
        self.zakDiagNum=None
        self.zakDiagGZ=None
        self.zakDiagMKB=None
        self.zakSpec=None
        self.resultId=None
        self.DZ_MKB_set=False
        self.DZ_MKB=None
        if self.dbf_DZ_MKB:
            self.DZ_MKB=self.get_field('DZ_MKB')
            if self.DZ_MKB[:1] in ['Z', 'z']:
                self.DZ_MKB=None
        self.DiagList=[]
        self.dateList=[]
        for (spec, speciality, numDiags) in specs:
            specialityId=self.spec_code2id(speciality)
            personName=self.get_field(spec+'_NAME')
            personCode=self.get_field(spec+'_KOD')
            personDate=self.get_field(spec+'_DO')
            personSl=self.get_field(spec+'_SL')
            self.processPerson(
                personName, specialityId, personCode, personDate, personSl, numDiags, spec)

        for dsnum in ['1', '2', '3']:
            spec=self.get_field('SPEC_'+dsnum)
            OKSO=None
            if spec and spec[0]=='[':
                os=spec[1:].split(']')
                if len(os)>1: OKSO=os[0]
            if not OKSO: continue
            specialityId=self.spec_OKSO2id(OKSO)
            if not specialityId: continue

            personName=self.get_field('NAME_'+dsnum)
            personKod=self.get_field('KOD_'+dsnum)
            personDate=self.get_field('DO_'+dsnum)
            personSl=self.get_field('SL_'+dsnum)
            self.processPerson(
                personName, specialityId, personCode, personDate, personSl, 1, 'S_'+dsnum)

        if not self.DiagList:
            self.err2log(u'нет диагнозов')
            self.nbad+=1
            return

        (self.datemin, self.datemax)=self.getDateRange(
            self.get_field('DATE_BIG') if self.dbf_DATE_BIG else None)
        self.eventType=self.getEventType(TIP_DD)

        record = QtGui.qApp.db.getRecord(self.tableClient, 'sex, birthDate', self.clientId)
        if record:
            self.clientSex       = forceInt(record.value('sex'))
            self.clientBirthDate = forceDate(record.value('birthDate'))
            self.clientAge       = calcAgeTuple(self.clientBirthDate, QDate(self.datemin))
            if not self.clientAge:
                self.clientAge = (0, 0, 0, 0)

        if self.eventOrgId==self.my_org_id:
            self.contractId=self.get_contractId(self.eventOrgId, ClientWorkId)
#            if not self.contractId:
#                self.err2log(u'нет договора')
#                self.nbad+=1
#                return
        else:
            self.contractId=None

        self.make_visits=False

        eventId=self.getEventId(noAdd)

        if self.eventOrgId!=self.my_org_id:
            return

        if not eventId and not noAdd:
            self.err2log(u'не удалось найти и добавить событие')

        if not eventId:
            return

        ActionList=[]
        dop=self.get_dop()
        for (name, ActionType) in dop:
            DI=self.get_field(name+'_DI');
            if str(DI).replace('#','').strip()=="":
                DI=None
            DP=self.get_field(name+'_DP')
            if str(DP).replace('#','').strip()=="":
                DP=None
            if not DI and not DP:
                continue
            if not self.checkAction(ActionType):
                continue
#            if DP:
#                if DP>self.DATE_ZAV:
#                    DP=self.DATE_ZAV
#                self.dateList.append(DP)
            directionDate=None
            if DP:
                if DP>self.DATE_ZAV:
                    self.err2log(u'дата окончания исследования позже DATE_ZAV')
                if self.datemin and DP>self.datemin:
                    directionDate=self.datemin
                    if not DI:
                        DI=self.datemin
                else:
                    if DI:
                        directionDate=DI
                    else:
                        directionDate=DP
                        DI=DP
            else:
                if DI:
                    if DI>self.DATE_ZAV:
                        self.err2log(u'дата начала исследования позже DATE_ZAV')
                    if DI>self.datemin:
                        directionDate=self.datemin
                    else:
                        directionDate=DI
            ActionFields=[
                ('actionType_id', ActionType), ('directionDate', directionDate),
                ('status', 2), ('begDate', DI), ('endDate', DP)]
            ActionList.append(ActionFields)

        if self.zakDiagNum==None:
            self.err2log(u'заключительный диагноз не найден')
            return

        for d in range(len(self.DiagList)):
            (DiagnosticFields, diagnosisType_id, setDate)=self.DiagList[d]
            if d==self.zakDiagNum:
                diagnosisType_id=1
            if isNull(setDate) or isNull(self.datemin) or setDate<self.datemin:
                DiagnosticFields.append(('setDate', None))
            else:
                DiagnosticFields.append(('setDate', self.datemin))
            DiagnosticFields+=[
                ('event_id', eventId), ('diagnosisType_id', diagnosisType_id)]
            getId(self.tableDiagnostic, DiagnosticFields)

        for ActionFields in ActionList:
            ActionFields.append(('event_id', eventId))
            getId(self.tableAction, ActionFields)

        if self.make_visits:
            createVisits(eventId)
        self.ngood+=1

    def spec_code2id(self, code):
        specialityId=self.spec_codeCache.get(code, None)
        if specialityId: return specialityId
        specialityId=forceRef(self.db.translate('rbSpeciality', 'code', code, 'id'))
        if specialityId: self.spec_codeCache[code]=specialityId
        return specialityId

    def spec_OKSO2id(self, OKSO):
        specialityId=self.spec_OKSOCache.get(OKSO, None)
        if specialityId: return specialityId
        specialityId=forceRef(self.db.translate('rbSpeciality', 'OKSOCode', OKSO, 'id'))
        if specialityId: self.spec_OKSOCache[OKSO]=specialityId
        return specialityId

    def get_MKB_char(self, diag):
        MKBchar=self.MKB_charCache.get(diag, None)
        if MKBchar: return MKBchar
        MKBchar=forceInt(self.db.translate('MKB_Tree', 'DiagID', diag, 'characters'))
        if MKBchar: self.MKB_charCache[diag]=MKBchar
        return MKBchar

    def processHurt(self, ClientWorkId):
        db = QtGui.qApp.db
        WORKV=trim(self.get_field('WORKV'))
        WORKS=trim(self.get_field('WORKS'))
        FAKTOR=trim(self.get_field('FAKTOR'))
        hurtType_id=forceRef(db.translate('rbHurtType', 'code', WORKV, 'id'))
        Hurt_id=None
        if hurtType_id and (WORKS or FAKTOR):
            HurtFields=[('master_id', ClientWorkId), ('hurtType_id', hurtType_id)]
            Hurt_id=getId(self.tableClientWork_Hurt, HurtFields,  [('stage', WORKS)])
        if not FAKTOR:
            return
        FAKTOR=FAKTOR.replace(';', ' ').replace(',', ' ').replace('|', ' ')
        factors=FAKTOR.split()
        if factors:
            if not Hurt_id:
                hurtType_id=forceRef(db.translate('rbHurtType', 'code', '', 'id'))
                HurtFields=[
                    ('master_id', ClientWorkId), ('hurtType_id', hurtType_id), ('stage', WORKS)]
                Hurt_id=getId(self.tableClientWork_Hurt, HurtFields)
            for factor in factors:
                if factor:
                    factorType_id=forceRef(db.translate('rbHurtFactorType', 'code', factor,'id'))
                    if factorType_id:
                        Hurt_FactorFields=[
                            ('master_id', ClientWorkId), ('factorType_id', factorType_id)]
                        Hurt_Factor_id=getId(self.tableClientWork_Hurt_Factor, Hurt_FactorFields)

    def checkAction(self, actionType):
        name=forceString(QtGui.qApp.db.translate('ActionType', 'id', actionType, 'name'))
        cond='eventType_id=\'%d\' and actionType_id=\'%d\'' % (self.eventTypeId, actionType)
        record=QtGui.qApp.db.getRecordEx('EventType_Action', cols='sex, age', where=cond)
        if not record:
            return False
        age=forceString(record.value('age'))
        if age and self.clientAge:
            ageSelector = parseAgeSelector(age)
            if not checkAgeSelector(ageSelector, self.clientAge):
                self.err2log(u'исслед. '+name+u' не подходит по возрасту')
                return False
        sex=forceInt(record.value('sex'))
        if sex and self.clientSex and self.clientSex!=sex:
            self.err2log(u'исслед. '+name+u' не подходит по полу')
            return False
        return True

def dbfFields():
    fields131=[
        'ID', 'FAM', 'IM', 'OT', 'POL', 'DR', 'SNILS', 'TIP_DD', 'SN_POLIS', 'RABOTA', 'OKVED', 'DOLGN', 'ADRES_TYPE', 'NAS_P', 'UL', 'DOM', 'KOR', 'KV', 'OGRN', 'DATE_ZAV', 'POL', 'MU_VB']
    for (spec, diagNum) in [('T', 5), ('A', 3), ('N', 3), ('H', 3), ('U', 3), ('O', 3), ('E', 3)]:
        fields131.append(spec+'_NAME')
        fields131.append(spec+'_KOD')
        fields131.append(spec+'_DO')
        fields131.append(spec+'_SL')
        for iDiag in range(1, diagNum+1):
            fields131.append(spec+'_MKB_'+str(iDiag))
            fields131.append(spec+'_V_'+str(iDiag))
            fields131.append(spec+'_ST_'+str(iDiag))
            fields131.append(spec+'_GZ_'+str(iDiag))
    for name in ['H', 'G', 'KAK', 'KAM', 'UPROST', 'M', 'F', 'EKG']:
        fields131.append(name+'_DI')
        fields131.append(name+'_DP')
    return fields131

TIP_DD_b=[u'B', u'Б', 868, '868', 860, '860', '921', u'921Б']
TIP_DD_r=[u'R', u'Р', 860, '860', 876, '876']
TIP_DD_v=[u'V', u'В', 859, '859', 869, '869']

def get_DiagnosisId2(
    date, personId, clientId, diagnosisTypeId, MKB, MKBEx, characterId,
    dispanserId, traumaTypeId,suggestedDiagnosisId=None, ownerId=None):
    db = QtGui.qApp.db
    if MKB[:1] == 'Z':
        diagnosisTypeCode = '98' # magic!!!
    else:
        diagnosisTypeCode = forceString(db.translate('rbDiagnosisType', 'id', diagnosisTypeId, 'replaceInDiagnosis'))
    characterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'replaceInDiagnosis'))
    table = db.table('Diagnosis')
    result = None

    if diagnosisTypeCode == '98':
#        result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId)

        clientCond = table['client_id'].eq(clientId)
        diagCond = table['MKB'].eq(MKB)
        commonCond = db.joinAnd([table['deleted'].eq(0), table['mod_id'].isNull(), clientCond, diagCond])
        setDate = date

        record = findDiagnosisRecord(db, table, commonCond, date, 0)
        if record:
#            result = record
            return result, characterId
        else:
            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId)


    else:
        assert diagnosisTypeCode in ['2', '9']

        clientCond = table['client_id'].eq(clientId)
        diagCond = table['MKB'].eq(MKB)
        commonCond = db.joinAnd([table['deleted'].eq(0), table['mod_id'].isNull(), clientCond, diagCond])
        setDate = date

        if characterCode == '3' : # хроническое
            record = findDiagnosisRecord(db, table, commonCond, date, 0)
            docCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', characterId, 'code'))
            if docCharacterCode in ['3', '4']: # "хроническое" или "обострение хронического"
                setDate = QDate()
            if record:
                oldCharacterId = forceRef(record.value('character_id'))
                oldCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', oldCharacterId, 'code'))
                oldSetDate = forceDate(record.value('setDate'))
                oldEndDate = forceDate(record.value('endDate'))

                countUsage = countUsageDiagnosis(suggestedDiagnosisId, ownerId, False)
                if countUsage:
                    if oldCharacterCode == '3':
                        # и раньше было хроническим, обновляем документ
                        if (oldSetDate.isNull() or oldSetDate<date) and docCharacterCode == '2':
                            # при наличии уже установленного хрон. и выставлении впервые установленного
                            characterId = oldCharacterId # меняем в документе на хроническое
                    else:
                        # раньше было острым
                        if oldEndDate.year()>=date.year():
                            # меняем на хроническое
                            characterId = db.translate('rbDiseaseCharacter', 'code', characterCode, 'id')
                            record.setValue('character_id', toVariant(characterId))
                            characterId = db.translate('rbDiseaseCharacter', 'code', '4', 'id') # меняем в документе на обострение
                        else:
                            # прошлогодние данные не меняем.
                            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId)
                else:
                    result = modifyDiagnosisRecord(record, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId)
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId)
        else: # это острое заболевание
            duration = forceInt(db.translate('MKB_Tree', 'DiagID', MKBwithoutSubclassification(MKB), 'duration'))
            if not duration:
                duration = QtGui.qApp.averageDuration()
            if not duration:
                duration = 28 # magic!!!
            record = findDiagnosisRecord(db, table, commonCond, date, duration)
            if record:
                oldCharacterId = forceRef(record.value('character_id'))
                oldCharacterCode = forceString(db.translate('rbDiseaseCharacter', 'id', oldCharacterId, 'code'))
                countUsage = countUsageDiagnosis(suggestedDiagnosisId, ownerId, False)
                if countUsage:
                    if oldCharacterCode == '3':
                        # раньше было хроническим, обновляем в документе на обострение
                        characterId = db.translate('rbDiseaseCharacter', 'code', '4', 'id') # меняем в документе на обострение
                        updateDiagnosisRecord(record, date, date, MKBEx, dispanserId, traumaTypeId, personId)
                    else:
                        oldSetDate = forceDate(record.value('setDate'))
                        oldEndDate = forceDate(record.value('endDate'))
                        if oldSetDate.addDays(-duration)>date or date>oldEndDate.addDays(duration):
                            result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId)
                else:
                    result = modifyDiagnosisRecord(record, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, setDate, date, personId)
            else:
                result = createDiagnosisRecord(clientId, diagnosisTypeCode, characterCode, MKB, MKBEx, dispanserId, traumaTypeId, date, date, personId)
        if result == None:
            if diagnosisTypeCode == '2':
                diagnosisTypeId = db.translate('rbDiagnosisType', 'code', diagnosisTypeCode, 'id')
                record.setValue('diagnosisType_id', diagnosisTypeId)
            updateDiagnosisRecord(record, setDate, date, MKBEx, dispanserId, traumaTypeId, personId)
            result = forceRef(record.value('id'))
    if suggestedDiagnosisId != result:
        if countUsageDiagnosis(suggestedDiagnosisId, ownerId, True) == 0:
            db.deleteRecord(table, table['id'].eq(suggestedDiagnosisId))
    return result, characterId
