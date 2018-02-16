#!/usr/bin/env python
# -*- coding: utf-8 -*-
from library.LoggingModule import Logger
from library.DbfViewDialog import CDbfViewDialog
from Utils import *
from library.dbfpy import dbf


class CImport():
    def __init__(self, log=None, edtFile=None, db = None, progressBar = None, btnImport=None, btnClose=None):
        Logger.logWindowAccess(windowName=type(self).__name__, notes=u'Импорт')
        if not hasattr(self, 'edtFileName'):
            self.edtFileName = edtFile
        if not hasattr(self, 'db'):
            self.db = db
        if not self.db:
            self.db = QtGui.qApp.db
        if not hasattr(self, 'log'):
            self.log = log
        if not hasattr(self, 'progressBar'):
            self.progressBar = progressBar
        if self.progressBar:
            self.progressBar.setValue(0)
        if not hasattr(self, 'btnImport'):
            self.btnImport = btnImport
        if not hasattr(self, 'btnClose'):
            self.btnClose = btnClose
        self.n=0
        self.row=None
        self.abort=False
        self.importRun=False
        if self.edtFileName:
            QtCore.QObject.connect(
                self.edtFileName, QtCore.SIGNAL("textChanged(QString)"), self.checkName)

        # FIXME: разве это нужно при любом импорте? Может быть, лучше перенести в отдельный класс?
        if hasattr(QtGui.qApp, 'preferences'):
            self.my_org_id=forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', None))
        else:
            self.mu_org_id = None
        self.lpuOrg={}
        self.infisOrg={}
        self.OGRN_Org={}
        self.mapOKVEDtoUnified = {}
        self.mapINNToId = {}
        self.mapOrganisationNameToId = {}
        self.mapPersonKeyToId = {}
        self.np_KLADR={}
        self.ul_KLADR={}
        self.smo_ins={}
        self.tableClient=tbl('Client')
        self.tableClientPolicy=tbl('ClientPolicy')
        self.tableClientAddress=tbl('ClientAddress')
        self.tableClientAttach=tbl('ClientAttach')
        self.tableOrganisation=tbl('Organisation')
        self.tableOrgStructure=tbl('OrgStructure')
        self.tablePerson=tbl('Person')
        self.tableClientWork=tbl('ClientWork')
        self.tableClientDocument=tbl('ClientDocument')
        self.tableAddress=tbl('Address')
        self.tableAddressHouse=tbl('AddressHouse')
        self.tableKLADR=tbl('kladr.KLADR')
        self.tableSTREET=tbl('kladr.STREET')
        self.tableDOMA=tbl('kladr.DOMA')

    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='')

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.importRun:
            self.abort=True
        else:
            self.close()

    def err2log(self, e):
        if hasattr(self.log, 'append'):
            self.log.append(u'запись '+str(self.n)+' (id=\"'+str(self.row['ID'])+u'\"): '+e)

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.btnImport.setEnabled(False)
        self.btnClose.setText(u'Прервать')
        if self.progressBar:
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'выполняется %v/%m')
        self.abort=False
        self.importRun=True
        try:
            self.beforeStart()
            self.startImport()
            self.abort=False
            self.importRun=False
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
            QtGui.QMessageBox.critical (self,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.abort = True
        finally:
            self.afterEnd()
        if self.progressBar:
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'прервано' if self.abort else u'готово')
        
        self.btnImport.setEnabled(True)
        self.btnClose.setText(u'Закрыть')
    
    def beforeStart(self):
        pass

    def startImport(self):
        raise NotImplementedError()
    
    def afterEnd(self):
        pass    
    
    def getClientId(self, lastNameField, firstNameField, patrNameField, sexField, birthDateField):
        bad=False
        lastName=nameCase(self.row[lastNameField])
        firstName=nameCase(self.row[firstNameField])
        patrName=nameCase(self.row[patrNameField])
        if not (lastName and firstName and patrName):
            bad=True
            self.err2log(u'нет полного Ф?О')
        fio=lastName+firstName+patrName
        if not check_rus_lat(fio):
            bad=True
            self.err2log(u'недопустимое Ф?О')
        sex=self.row[sexField]
        if not sex:
            bad=True
            self.err2log(u'не указан пол')
        else:
            if sex in [u'м', u'М']: sex=1
            if sex in [u'ж', u'Ж']: sex=2
        birthDate=self.row[birthDateField]
        if not birthDate:
            bad=True
            self.err2log(u'не указан день рождения')
        if bad:
            return None
        else:
            clientFields=[
                ('lastName', lastName), ('firstName', firstName), ('patrName', patrName),
                ('sex', sex), ('birthDate', birthDate)]
            return getId(self.tableClient, clientFields)

    def getCodeFromId(self, orgStructureSailId, fieldCode):
        db = QtGui.qApp.db
        if orgStructureSailId:
            dbfFileName = unicode(self.edtFileNameOrgStructure.text())
            if not dbfFileName:
                res = QtGui.QMessageBox.warning( self,
                                     u'Внимание!',
                                     u'Выберите соответствующий ORGSTRUCTURE файл DBF %s'%(self.edtFileNameOrgStructure.text()),
                                     QtGui.QMessageBox.Cancel,
                                     QtGui.QMessageBox.Cancel)
            else:
                dbfSailOrgStructure = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp1251')
                for i, row in enumerate(dbfSailOrgStructure):
                    if orgStructureSailId == forceString(row['ID']):
                        orgStructureSailCode = forceString(row['CODE'])
                        record = db.getRecordEx('OrgStructure', 'id', 'deleted = 0 AND %s = \'%s\''%(fieldCode, orgStructureSailCode))
                        if record:
                            return forceRef(record.value('id'))
        return None

    def getOrgStructureId(self, code, field, orgStructureFields, updateOrgStructure = False, attachOrgStructure = False):
        if updateOrgStructure or attachOrgStructure:
            codeOrgStructure = nameCase(forceString(self.row[code]))
            if updateOrgStructure and attachOrgStructure:
                return getId(self.tableOrgStructure, [(field, codeOrgStructure), ('deleted', 0)], orgStructureFields)
            elif updateOrgStructure:
                return self.getUpdateId(self.tableOrgStructure, [(field, codeOrgStructure), ('deleted', 0)], True, orgStructureFields)
            elif attachOrgStructure:
                return self.getUpdateId(self.tableOrgStructure, [(field, codeOrgStructure), ('deleted', 0)], False, orgStructureFields)
        return None

    def getUpdateId(self, table, fields, updateOrgStructure, fields2=None):
        if not fields2:
            fields2 = []
        db = QtGui.qApp.db
        cond=[]
        for (name, val) in fields:
            if val==None:
                cond.append(table[name].isNull())
            else:
                cond.append(table[name].eq(toVariant(val)))
        record=db.getRecordEx(table, '*', where=cond)
        if record and updateOrgStructure:
            updateRecord = False
            for (name, val) in fields2:
                recVal=record.value(name)
                if (recVal.isNull() or forceString(recVal)=='') and isNotNull(val):
                    record.setValue(name, toVariant(val))
                    updateRecord = True
            if updateRecord:
                db.updateRecord(table, record)
            return forceInt(record.value('id'))
        elif not updateOrgStructure:
            record = table.newRecord()
            for (name, val) in fields+fields2:
                record.setValue(name, toVariant(val))
            return db.insertRecord(table, record)
        return None

    def get_clientPolicy_id(self, client_id, serial, number, insurer_id, policyType_id=None):
        if isNull(serial) or isNull(number):
            self.err2log(u'не указан полис')
            return None
        clientPolicyFields=[('client_id', client_id), ('serial', serial), ('number', number)]
        clientPolicyFields2=[('insurer_id', insurer_id), ('policyType_id', policyType_id)]
        return getId(
            self.tableClientPolicy, clientPolicyFields, clientPolicyFields2)

    def lpuFind(self, lpu):
        if not lpu: return None
        id=self.lpuOrg.get(lpu, None)
        if id: return id
        cond='fullName like \"%'+lpu+'%\" or shortName like \"%'+lpu+'%\"'
        OrganisationList=self.db.getIdList(self.tableOrganisation, where=cond)
        if OrganisationList:
            id=OrganisationList[0]
        else:
            lpu1=lpu.replace(' ', '')
            LP=lpu1.replace(u'№', 'N')
            def name_cond(LP):
                return 'REPLACE(fullName, \" \", \"\") like \"%'+LP+\
                    '%\" or REPLACE(shortName, \" \", \"\") like \"%'+LP+'%\"'
            OrganisationList=self.db.getIdList(self.tableOrganisation, where=name_cond(LP))
            if OrganisationList:
                id=OrganisationList[0]
            else:
                LP=lpu1.replace('N', u'№')
                OrganisationList=self.db.getIdList(self.tableOrganisation, where=name_cond(LP))
                if OrganisationList:
                    id=OrganisationList[0]
        if id: self.lpuOrg[lpu]=id
        return id

    def infis2orgId(self, infis):
        if isNull(infis): return None
        id=self.infisOrg.get(infis, None)
        if id: return id
        obs='CONCAT(\",\", obsoleteInfisCode, \",\")'
        cond='infisCode=\"'+infis+'\" or '+obs+' like \"%,'+infis+',%\"'
        OrganisationList=self.db.getIdList(self.tableOrganisation, where=cond)
        if OrganisationList:
            id=OrganisationList[0]
        if id: self.infisOrg[infis]=id
        return id

    def infis2org(self, infis):
        id=self.infis2orgId(infis)
        if not id: return None
        cond=[]
        cond.append(self.tableOrganisation['id'].eq(toVariant(id)))
        OrganisationList=self.db.getRecordList(self.tableOrganisation, where=cond)
        if OrganisationList:
            id=OrganisationList[0]
        return id

    def OGRN2orgId(self, OGRN):
        if not OGRN:
            return None
        id=self.OGRN_Org.get(OGRN, 0)
        if id != 0:
            return id
        id = forceRef(self.db.translate('Organisation', 'OGRN', OGRN, 'id'))
        if id:
            self.OGRN_Org[OGRN]=id
        return id

    def unifyOKVED(self, okved):
        result = self.mapOKVEDtoUnified.get(okved, None)
        if not result and okved:
            result = okved.split('-', 1)[0] # до тире
            result = result.replace(' ',  '') # без пробелов
            if result and result[0:1].isdigit():
                result = forceString(QtGui.qApp.db.translate('rbOKVED', 'OKVED', result, 'code'))
            self.mapOKVEDtoUnified[okved] = result
        return result

    def getOrganisationId(self, INN, nameFieldName, name):
        result = None
        if INN:
            result = self.mapINNToId.get(INN, 0)
        if result==0 and name:
            result = self.mapOrganisationNameToId.get(name, 0)
        if result==0:
            if INN:
                result = forceInt(self.db.translate(self.tableOrganisation, 'INN', INN, 'id'))
            if not result and name:
                result = forceInt(self.db.translate(
                    self.tableOrganisation, nameFieldName, name, 'id'))
                if result and INN:
                    self.mapINNToId[INN] = result
                    record = self.tableOrganisation.newRecord(['id', 'INN'])
                    record.setValue('id', toVariant(result))
                    record.setValue('INN', toVariant(INN))
                    self.db.updateRecord(self.tableOrganisation, record)
            if not result:
                record = self.tableOrganisation.newRecord(['INN', nameFieldName])
                record.setValue('INN', toVariant(INN))
                record.setValue(nameFieldName, toVariant(name))
                result = self.db.insertRecord(self.tableOrganisation, record)
            if result:
                if INN:
                    self.mapINNToId[INN] = result
                if name:
                    self.mapOrganisationNameToId[name] = result
        return result

    def get_KLADRCode(self, NAS_P, noCache=False):
        if not NAS_P: return None
        KLADRCode=self.np_KLADR.get(NAS_P, None)
        if KLADRCode != None:
            return KLADRCode
        (NAME, SOCR)=(None, None)
        cond=[]
        m=re_spb.match(NAS_P)
        if m:
            ns=(None, None)
            pos=m.end()
            if pos>=0:
                ns=obl(NAS_P[pos:])
            if ns==(None, None):
                if len(NAS_P)>pos+2:
                    name=NAS_P[pos+1:].split(',')[0].strip()
                    if name:
                        inf=self.db.translate('kladr.OKATO', 'NAME', name, 'infis')
                        if inf:
                            n=self.db.translate('kladr.KLADR', 'infis', inf, 'NAME')
                            s=self.db.translate('kladr.KLADR', 'infis', inf, 'SOCR')
                            if n and s:
                                ns=(n, s)
            if ns==(None, None):
                (NAME, SOCR)=(u'Санкт-Петербург', u'г')
            else:
                (NAME, SOCR)=ns
                cond.append(self.tableKLADR['parent'].like('78%'))
        else:
            m=re_obl.match(NAS_P)
            if m:
                (NAME, SOCR)=obl(NAS_P[m.end():])
                cond.append(self.tableKLADR['parent'].like('47%'))
            elif re.match(u'^респ[\. ]', NAS_P):
                (NAME, SOCR)=(NAS_P[5:len(NAS_P)].strip(), u'Респ')
            else:
                m=re.match(u'респ\.?$', NAS_P)
                if m:
                    (NAME, SOCR)=(NAS_P[:m.start()].strip(), u'Респ')
        if NAME and SOCR:
            cond.append(self.tableKLADR['NAME'].eq(toVariant(NAME)))
            cond.append(self.tableKLADR['SOCR'].eq(toVariant(SOCR)))
            KLADRRecord=QtGui.qApp.db.getRecordEx(self.tableKLADR, 'CODE', where=cond)
            if KLADRRecord:
                KLADRCode=forceString(KLADRRecord.value('CODE'))
        if not KLADRCode:
            KLADRCode=''
        if not noCache:
            self.np_KLADR[NAS_P]=KLADRCode
        return KLADRCode

    def get_KLADRStreetCode(self, UL, KLADRCode, NAS_P, noCache=False):
        if not UL or not KLADRCode:
            return None
        key=(UL, KLADRCode, NAS_P)
        KLADRStreetCode=self.ul_KLADR.get(key, None)
        if KLADRStreetCode != None:
            return KLADRStreetCode
        (NAME, SOCR)=get_street_ns(UL)
        if NAME and SOCR:
            cond=[]
            cond.append(self.tableSTREET['NAME'].eq(toVariant(NAME)))
            cond.append(self.tableSTREET['SOCR'].eq(toVariant(SOCR)))
            cond.append(self.tableSTREET['CODE'].like(KLADRCode[:11]+'%'))
            STREETList=QtGui.qApp.db.getRecordList(self.tableSTREET, where=cond)
            if STREETList:
                KLADRStreetCode = forceString(STREETList[0].value('CODE'))
            else:
                kladr=forceString(QtGui.qApp.db.translate(
                    'kladr.infisSTREET', 'name', NAME, 'KLADR'))
                STREET_SOCR=forceString(QtGui.qApp.db.translate('kladr.STREET', 'CODE', kladr, 'SOCR'))
                if kladr and STREET_SOCR==SOCR:
                    KLADRStreetCode = kladr
                else:
                    infis=forceString(QtGui.qApp.db.translate(
                        'kladr.infisSTREET', 'name', NAME, 'code'))
                    if not infis:
                        cond=[]
                        cond.append(self.tableSTREET['NAME'].like(NAME+'%'))
                        cond.append(self.tableSTREET['SOCR'].eq(toVariant(SOCR)))
                        cond.append(self.tableSTREET['CODE'].like('78%'))
                        STREETList=QtGui.qApp.db.getRecordList(self.tableSTREET, where=cond)
                        if STREETList:
                            infis=forceString(STREETList[0].value('infis'))
                    if not infis:
                        pass
                    if infis:
                        cond=[]
                        cond.append(self.tableSTREET['SOCR'].eq(toVariant(SOCR)))
                        cond.append(self.tableSTREET['CODE'].like(KLADRCode[:11]+'%'))
                        cond.append(self.tableSTREET['infis'].eq(toVariant(infis)))
                        STREETList=QtGui.qApp.db.getRecordList(self.tableSTREET, where=cond)
                        CODE_list=[forceString(x.value('CODE')) for x in STREETList]
                        l=len(STREETList)
                        if not l:
                            pass
                        if l==1:
                            KLADRStreetCode = CODE_list[0]
                        elif l>1 and NAS_P:
                            pos=NAS_P.rfind(',')
                            if pos>=0:
                                if NAS_P[-4:]==u' р-н':
                                    raion=NAS_P[pos+1:-4]
                                else:
                                    raion=NAS_P[pos+1:]
                                OKATO=forceString(QtGui.qApp.db.translate(
                                    'kladr.OKATO', 'NAME', raion.strip(), 'CODE'))
                                if OKATO:
                                    cond=[]
                                    cond.append(self.tableSTREET['OCATD'].like(OKATO+'%'))
                                    STREETList=QtGui.qApp.db.getRecordList(
                                        self.tableSTREET, where=cond)
                                    if len(STREETList)==1:
                                        KLADRStreetCode = forceString(STREETList[0].value('CODE'))
                                    else:
                                        cond=[]
                                        cond.append(self.tableSTREET['SOCR'].eq(toVariant(SOCR)))
                                        cond.append(self.tableSTREET['infis'].eq(toVariant(infis)))
                                        cond.append(
                                            'kladr.STREET.OCATD is null or kladr.STREET.OCATD=""')
                                        STREETList=QtGui.qApp.db.getRecordList(
                                            self.tableSTREET, where=cond)
                                        if STREETList:
                                            CODE_list=[forceString(x.value('CODE')) for x in STREETList]
                                            CODE_like_list=[
                                                'kladr.DOMA.CODE like "'+c+'%"' for c in CODE_list]
                                            CODE_cond='('+' or '.join(CODE_like_list)+')'
                                            cond=[]
                                            cond.append(self.tableDOMA['OCATD'].like(OKATO+'%'))
                                            cond.append(CODE_cond)
                                            DOMA_list=QtGui.qApp.db.getRecordList(
                                                self.tableDOMA, where=cond)
                                            if DOMA_list:
                                                KLADRStreetCode = forceString(
                                                    DOMA_list[0].value('CODE'))[:17]
        if not KLADRStreetCode:
            KLADRStreetCode=''
        if not noCache:
            self.ul_KLADR[key]=KLADRStreetCode
        return KLADRStreetCode

    def get_insurerId(self, SMO_SHORT_):
        if isNull(SMO_SHORT_):
            return None
        id=self.smo_ins.get(SMO_SHORT_, -1)
        if id != -1:
            return id
        id=None
        cond=[]
        cond.append(self.tableOrganisation['title'].eq(toVariant(SMO_SHORT_)))
        cond.append(self.tableOrganisation['isInsurer'].eq(toVariant(1)))
        insurerList=self.db.getIdList(self.tableOrganisation, where=cond)
        if insurerList!=[]:
            id=insurerList[0]
        if not id:
            cond=[]
            cond.append(self.tableOrganisation['infisCode'].eq(toVariant(SMO_SHORT_)))
            cond.append(self.tableOrganisation['isInsurer'].eq(toVariant(1)))
            insurerList=self.db.getIdList(self.tableOrganisation, where=cond)
            if insurerList!=[]:
                id=insurerList[0]
        self.smo_ins[SMO_SHORT_]=id
        return id

    def logQueryResult(self, query):
        u"""Записывает результат выполнения запроса query в лог по строкам"""
        if self.log:
            logQueryResult(self.log, query)

    def setSqlVariable(self, name, value):
        u"""Устанавливает значение переменной в запросе на SQL"""
        setSqlVariable(self.db, name, value)

    def runScript(self, instream, dict=None):
        u"""Выполняет последовательность запросов к базе данных self.db, считанную из входного потока instream.
        instream - это произвольный контейнер со строками
        dict - набор пар (имя, значение) для установки переменных в SQL
        """
        if not dict:
            dict = {}
        return runScript(self.db, self.log, instream, dict)


nt_list=[
    (u'г.', u'г'), (u'гор.', u'г'), (u'город', u'г'),
    (u'п.', u'п'), (u'пос.', u'п'), (u'посёлок', u'п'), (u'поселок', u'п'), (u'ПОС.', u'п'),
    (u'д.', u'д'), (u'дер.', u'д'), (u'деревня', u'д')]


def obl(np):
    for (n, t) in nt_list:
        l=len(n)
        pos=np.find(n)
        if pos>=0:
            pos+=l
            pos2=pos
            for p in range(pos, len(np)):
                if np[p]==',': break
                else: pos2=p
            return (np[pos:pos2+1].strip(), t)
    return (None, None)


re_spb=re.compile(
    u'^((г|Г)(\. | |\.))?(СП(б|Б)|(С|Санкт|САНКТ)-(Петербург|ПЕТЕРБУРГ))')
re_obl=re.compile(u'^(ЛО|Лен(инградская)?( |\.|\. )[Оо]бл(асть)?)[\., ]')


ns_list=[
    (u'улица', u'ул'), (u'ул.', u'ул'), (u'ул', u'ул'), (u'УЛ.', u'ул'), (u'Ул.', u'ул'), (u'.УЛ', u'ул'), (u'УЛ?ЦА', u'ул'), (u'УЛ', u'ул'),
    (u'проспект', u'пр-кт'), (u'пр-кт', u'пр-кт'), (u'пр.', u'пр-кт'),
    (u'ПР.', u'пр-кт'), (u'П.', u'пр-кт'), (u'.ПР', u'пр-кт'),
    (u'переулок', u'пер'), (u'пер.', u'пер'), (u'ПУ.', u'пер'), (u'.ПУ', u'пер'),
    (u'набережная', u'наб'), (u'наб.', u'наб'), (u'Н.', u'наб'), (u'.Н', u'наб'), (u'НАБЕРЕЖНАЯ', u'наб'), (u'НАБ.', u'наб'), (u'НАБ', u'наб'),
    (u'шоссе', u'ш'), (u'ш.', u'ш'), (u'Ш.', u'ш'),  (u'.Ш', u'ш'),
    (u'бульвар', u'б-р'), (u'б-р', u'б-р'), (u'б.', u'б-р'), (u'Б.', u'б-р'), (u'.Б', u'б-р'),
    (u'площадь', u'пл'), (u'пл.', u'пл'),
    (u'аллея', u'аллея'), (u'ал.', u'аллея'), (u'.АЛ', u'аллея'),
    (u'проезд', u'проезд'), (u'пр-д', u'проезд'),
    (u'линия', u'линия'), (u'лин.', u'линия'), (u'.Л', u'линия'), (u'Л?Н?Я', u'линия'),
    (u'ДГ.', u'дор'), (u'дорога', u'дор'),
    (u'остров', u'о'), (u'.О', u'о')]


def get_street_ns(UL):
    UL_len=len(UL)
    for (n, s) in ns_list:
        l=len(n)
        if l>=UL_len:
            continue
        if UL[0:l]==n and (UL[l]==u' ' or n[-1]==u'.'):
            return((UL[l:UL_len].strip(), s))
        if UL[UL_len-l-1:UL_len]==(u' '+n):
            return((UL[0:UL_len-l].strip(), s))
    return (None, None)


class CEISimport(CImport):
    def exec_(self):
        props=QtGui.qApp.preferences.appPrefs
        EIS_dbDatabaseName=forceStringEx(getVal(props, 'EIS_databaseName', QVariant()))
        self.edtFileName.setText(EIS_dbDatabaseName)
        EIS_dbServerName=forceStringEx(getVal(props, 'EIS_serverName', QVariant()))
        self.edtIP.setText(EIS_dbServerName)
        self.checkName()
        QtGui.QDialog.exec_(self)
        QtGui.qApp.EIS_db.close()
        QtGui.qApp.EIS_db=None

    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='' and self.edtIP.text()!='')


class CDBFimport(CImport):
    @QtCore.pyqtSlot()
    def on_btnView_clicked(self):
        fname=forceStringEx(self.edtFileName.text())
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()

    def insertTableDataFromDbf(self, tablename, filename, encoding, binaries=None, fields=None):
        if not binaries:
            binaries = []
        insertTableDataFromDbf(self.db, tablename, filename, encoding, binaries, fields)

    def fullTable(self, filename, tablename, binaries, fields=None):
        self.log.append(u'Заполняется таблица %s из файла %s...'%(tablename, filename))
        QtGui.qApp.processEvents()
        self.insertTableDataFromDbf(tablename, unicode(filename), 'ibm866', binaries, fields)

    def addDuplicateAlertToLog(self, table, code, ids):
        message = u'В базе обнаружено несколько одинаковых %s. Code: %s . Ids: %s \n' % (unicode(table), unicode(code), u' '.join(ids))
        self.log.append(message)


class CXMLimport(CImport):
    def __init__(self, log=None, edtFile=None, db = None, progressBar = None, btnImport=None, btnClose=None):
        CImport.__init__(self, log, edtFile, db, progressBar, btnImport, btnClose)
        self._xmlReader = QXmlStreamReader()

    def readElementText(self):
        return self._xmlReader.readElementText()

    def errorString(self):
        return self._xmlReader.errorString()


    def atEnd(self):
        return self._xmlReader.atEnd()


    def name(self):
        return self._xmlReader.name()


    def setDevice(self,  device):
        return self._xmlReader.setDevice(device)

    def hasError(self):
        return self._xmlReader.hasError() or self.abort

    def raiseError(self,  str):
        self._xmlReader.raiseError(u'[%d:%d] %s' %\
            (self._xmlReader.lineNumber(), self._xmlReader.columnNumber(), str))

    def readNext(self):
        QtGui.qApp.processEvents()
        self._xmlReader.readNext()

        if self.progressBar:
            self.progressBar.setValue(self._xmlReader.device().pos())

    def err2log(self, e):
        if self.log:
            self.log.append(u'[%d:%d] %s' % (self._xmlReader.lineNumber(), \
                                             self._xmlReader.columnNumber(), e))

    def isEndElement(self):
        return self._xmlReader.isEndElement()

    def isStartElement(self):
        return self._xmlReader.isStartElement()

    def readUnknownElement(self, silent=False):
        assert self.isStartElement()

        if not silent:
            self.err2log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(silent)

            if self.hasError():
                break

    def readGroup(self, groupName, fieldsList, silent=False):
        assert self.isStartElement() and self.name() == groupName
        result = {}

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                name = forceString(self.name().toString())
                if (name in fieldsList):
                    result[name] = forceString(self.readElementText())
                else:
                    self.readUnknownElement(silent)

            if self.hasError():
                break

        return result

    def lookupIdByCodeName(self, code, name,  table,  cache):
        if code and name:
            key = (code, name)
            id = cache.get(key,  None)

            if id:
                return id

            cond = []
            cond.append(table['code'].eq(toVariant(code)))
            cond.append(table['name'].eq(toVariant(name)))
            record = self.db.getRecordEx(table, ['id'], where=cond)

            if record:
                id = forceRef(record.value('id'))
                cache[key] = id
                return id
        return None

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.checkName()

