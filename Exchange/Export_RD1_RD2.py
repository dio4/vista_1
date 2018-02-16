# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import tempfile
import shutil

from library import SendMailDialog
from library.dbfpy import dbf
from library.CalcCheckSum import *
from library.subst import substFields
from library.DialogBase  import CDialogBase
from Exchange.Utils import *
from DBFFormats import *
from Reports.Report     import *
from Reports.ReportBase import *
from Reports.ReportView import CReportViewDialog
from KLADR.KLADRModel import getCityName, getStreetName
from Accounting.Utils import *
from Accounting.FormProgressDialog import CFormProgressDialog
from Events.Action import ActionStatus

from Ui_ExportRD2_Wizard_1 import Ui_ExportRD2_Wizard_1
from Ui_ExportRD2_Wizard_2 import Ui_ExportRD2_Wizard_2
from Ui_PervDoc import Ui_PervDocDialog


def smartInt(v):
    try:
        return int(v) if v else 0
    except:
        return 0


class CMyWizardPage1(QtGui.QWizardPage, Ui_ExportRD2_Wizard_1):
    def __init__(self, parent, pervDoc, period=None, weekNumber=None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.pervDoc=pervDoc
        self.period=period
        self.weekNumber=weekNumber
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.abort=False
        self.exportRun=False
        self.done=False

        if self.parent.useXML:
            self.cmbExportFormat.addItem(u'XML', toVariant('XML'))
        else:
            self.cmbExportFormat.addItem(u'РД1', toVariant('RD1'))
            self.cmbExportFormat.addItem(u'РД2', toVariant('RD2'))
            self.cmbExportFormat.addItem(u'ЕИС', toVariant('EISOMS'))
            self.cmbExportFormat.addItem(u'РД-ДС', toVariant('RD3'))
            self.cmbExportFormat.addItem(u'РД1 2008', toVariant('RD4'))
            self.cmbExportFormat.addItem(u'РД1 2009', toVariant('RD5'))
            self.cmbExportFormat.addItem(u'РД1 2010', toVariant('RD6'))
            self.cmbExportFormat.addItem(u'РД1 2011', toVariant('RD6'))
            self.cmbExportFormat.addItem(u'РД1 2012', toVariant('RD7'))
            self.cmbExportFormat.addItem(u'РД-ДС 2011', toVariant('RD-DS'))
            exportInfo = getAccountExportFormat(self.parent.accountId).split()
            if exportInfo:
                exportFormat = exportInfo[0]
                index = self.cmbExportFormat.findData(toVariant(exportFormat), Qt.UserRole, Qt.MatchFixedString)
            else:
                index = -1
            self.cmbExportFormat.setCurrentIndex(index)


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.exportRun:
            self.abort=True

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        if self.parent.useXML:
            self.exportXML()
        else:
            self.export()

    def get_record(self, accountId):
        q='''
SELECT
Account.number AS account_num, Account.date AS accountDate, Account.settleDate AS settleDate,
lpu.INN AS lpu_INN, lpu.KPP AS lpu_KPP, lpu.fullName AS lpu_name, lpu.OKPO AS lpu_OKPO,
lpu.OGRN AS lpu_OGRN, lpu.OKVED AS lpu_OKVED, lpu.infisCode AS lpu_infis,
lpu_rbOKVED.name AS lpu_OKVED_name, lpu_rbOKPF.code AS lpu_OKPF, lpu_rbOKFS.code AS lpu_OKFS,
lpu_rbOKFS.name AS lpu_OKFS_name, lpu.FSS AS lpu_FSS,
payer.FSS AS payer_FSS, payer.fullName AS payer_name, payer.OKPO AS payer_OKPO,
payer.OGRN AS payer_OGRN, payer.INN AS payer_INN, payer.KPP AS payer_KPP,
recipient.fullName AS recipient_name, recipient.OKPO AS recipient_OKPO,
recipient.OGRN AS recipient_OGRN, recipient.infisCode AS recipient_infis,
Contract.number AS contract_num, Contract.date AS contract_date,
Contract.resolution AS contract_resolution
FROM
Account
LEFT JOIN Contract on Contract.id=Account.contract_id AND Contract.deleted = 0
LEFT JOIN Organisation AS payer ON payer.id=Account.payer_id AND payer.deleted = 0
LEFT JOIN Organisation AS lpu ON lpu.id=Contract.recipient_id AND lpu.deleted = 0
LEFT JOIN Organisation AS recipient ON recipient.id=Contract.recipient_id AND recipient.deleted = 0
LEFT JOIN rbOKVED AS lpu_rbOKVED ON lpu_rbOKVED.code=lpu.OKVED
LEFT JOIN rbOKPF AS lpu_rbOKPF ON lpu_rbOKPF.id=lpu.OKPF_id
LEFT JOIN rbOKFS AS lpu_rbOKFS ON lpu_rbOKFS.id=lpu.OKFS_id
WHERE Account.deleted = 0 AND Account.id=%d''' % accountId
        query=QtGui.qApp.db.query(q)
        ok=query.next()
        if ok: return query.record()
        else: return None

    def export(self):
        self.parent.export_type=forceString(self.cmbExportFormat.itemData(self.cmbExportFormat.currentIndex()))
        if self.parent.export_type not in ('RD1', 'RD2', 'RD3', 'RD4', 'RD-DS', 'RD5', 'RD6', 'RD7', ):
            QtGui.QMessageBox.critical(self,
                u'Внимание!',
                u'Невозможно экспортировать данные в этом формате.',
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok)
            return

        self.btnExport.setEnabled(False)
        self.abort=False; self.exportRun=True
        accountId=self.parent.accountId
        db=QtGui.qApp.db

        try:
            record=self.get_record(self.parent.accountId)
            if not record: return
            account_num=forceString(record.value('account_num'))
            accountDate=forceDate(record.value('accountDate'))
            settleDate=get_date(record.value('settleDate'))
            settleDate1=forceDate(record.value('settleDate'))
            lpu_INN=forceString(record.value('lpu_INN'))
            lpu_KPP=forceString(record.value('lpu_KPP'))
            lpu_name=forceString(record.value('lpu_name'))
            lpu_OKPO=forceString(record.value('lpu_OKPO'))
            lpu_OGRN=forceString(record.value('lpu_OGRN'))
            lpu_OKVED=forceString(record.value('lpu_OKVED'))
            lpu_OKVED_name=forceString(record.value('lpu_OKVED_name'))
            lpu_infis=forceString(record.value('lpu_infis'))
            lpu_OKPF=forceString(record.value('lpu_OKPF'))
            lpu_OKFS=forceString(record.value('lpu_OKFS'))
            lpu_OKFS_name=forceString(record.value('lpu_OKFS_name'))
            lpu_FSS=forceString(record.value('lpu_FSS'))
            payer_FSS=forceString(record.value('payer_FSS'))
            payer_name=forceString(record.value('payer_name'))
            payer_OKPO=forceString(record.value('payer_OKPO'))
            payer_OGRN=forceString(record.value('payer_OGRN'))
            payer_INN=forceString(record.value('payer_INN'))
            payer_KPP=forceString(record.value('payer_KPP'))
            recipient_name=forceString(record.value('recipient_name'))
            recipient_OKPO=forceString(record.value('recipient_OKPO'))
            recipient_OGRN=forceString(record.value('recipient_OGRN'))
            recipient_infis=forceString(record.value('recipient_infis'))
            PERIOD=accountDate.month() if not accountDate.isNull() else None
            contract_num=forceString(record.value('contract_num'))
            contract_date=get_date(record.value('contract_date'))
            contract_resolution=forceString(record.value('contract_resolution'))
            self.parent.account_num=account_num
            self.parent.accountDate=accountDate
            self.parent.lpu_name=lpu_name
            self.parent.lpu_INN=lpu_INN
            self.parent.lpu_KPP=lpu_KPP
            self.parent.lpu_FSS=lpu_FSS
            self.parent.lpu_OGRN=lpu_OGRN
            self.parent.recipient_name=recipient_name
            self.parent.payer_name=payer_name
            self.parent.payer_INN=payer_INN
            self.parent.payer_KPP=payer_KPP
            self.parent.payer_FSS=payer_FSS
            self.parent.payer_OGRN=payer_OGRN
            self.parent.settleDate=settleDate

            dbf_name=''
            if self.parent.export_type=='RD1':
                dbf_name=''
                if contract_resolution in ['868', '860']:
                    dbf_name+='DB'
                elif contract_resolution=='876':
                    dbf_name+='DR'
                dbf_name+='_'+lpu_infis+'_'
                dbf_name+=forceString(accountDate.toString('yyMM'))
            if self.parent.export_type=='RD2':
                dbf_name=u'UMO%010s%02d%d'% (
                    payer_FSS, settleDate.year % 100, (settleDate.month+2)/3)
            if self.parent.export_type in ['RD3', 'RD-DS']:
                dbf_name='DS'
                dbf_name+='_'+lpu_infis+'_'
                dbf_name+=forceString(accountDate.toString('yyMM'))
            if self.parent.export_type=='RD4':
                dbf_name='DB'
                dbf_name+='_'+lpu_infis+'_'
                dbf_name+=forceString(accountDate.toString('yyMM'))
            if self.parent.export_type in  ('RD5', 'RD6', 'RD7'):
                dbf_name='DB'
                dbf_name+='_'+lpu_infis+'_'
                dbf_name+=forceString(accountDate.toString('yyMM'))
            if self.pervDoc:
                dbf_name='m'+dbf_name
            tmp_dir=self.parent.tmp_dir
            self.parent.fname=dbf_name
            dbfFileName=os.path.join(tmp_dir, dbf_name+u'.dbf')
            rarFileName=os.path.join(tmp_dir, dbf_name+u'.rar')
            self.parent.rarname=rarFileName
            self.dbf=dbf.Dbf(dbfFileName, new=True, encoding='cp866')
            dbfRD2=self.dbf
            dbfFields=[]
            SPOLICYField='SPOLICY'
            DIAGField='DIAG'; SUMMAField='SUMMA'; ADATEField='ADATE'
            if self.parent.export_type=='RD1':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD1_fields()
            elif self.parent.export_type=='RD2':
                dbfFields=get_RD2_fields()
            elif self.parent.export_type=='RD3':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD3_fields()
            elif self.parent.export_type=='RD4':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD4_fields()
            elif self.parent.export_type == 'RD5':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD5_fields()
            elif self.parent.export_type == 'RD6':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD6_fields()
            elif self.parent.export_type == 'RD7':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD7_fields()
            elif self.parent.export_type=='RD-DS':
                SPOLICYField='S_POL'
                DIAGField='DZ_MKB'; SUMMAField='NORMA'; ADATEField='DATE_P'
                dbfFields=get_RD_DS_2011_fields()
            dbfRD2.addField(*dbfFields)
            header=[f[0] for f in dbfFields]
            header_ind={}; ind=0
            for h in header:
                header_ind[h]=ind
                ind+=1

            r1=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=1')
            id1=forceInt(r1.value(0)) if r1 else 0
            r2=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'1-2\' and class=1')
            id2=forceInt(r2.value(0)) if r2 else 0
            r3=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=0')
            id3=forceInt(r3.value(0)) if r3 else 0

            def addAccount(AccountItemsId, n):
                def get_stmt():
                    q_select='''
                        SELECT      Account_Item.sum,
                                        Event.execDate,
                                        Event.client_id,
                                        Event.id as event_id,
                                        Diagnosis.MKB
                        '''
                    q_from='''
                        FROM         Account_Item
                        LEFT JOIN   Event       ON (Event.id = Account_Item.event_id AND Event.deleted = 0)
                        LEFT JOIN   Diagnostic ON (Diagnostic.event_id = Event.id AND Diagnostic.diagnosisType_id = 1
                                                                AND Diagnostic.deleted = 0)
                        LEFT JOIN   Diagnosis   ON (Diagnostic.diagnosis_id = Diagnosis.id AND Diagnosis.deleted = 0)
                        '''
                    q_where=' where Account_Item.id=\"'+forceString(AccountItemsId)+'\"'

                    if self.parent.export_type in ('RD1', 'RD3', 'RD4', 'RD-DS', 'RD5', 'RD6', 'RD7'):
                        q_select+=''',work.OKVED as work_OKVED,
                                        work.fullName as work_name,
                                        ClientWork.post,
                                        work.INN as work_INN,
                                        rbHealthGroup.code as hg,
                                        insurer.shortName as insurer_name,
                                        insurer.infisCode as insurer_infis,
                                        Account_Item.id as Account_ItemId,
                                        (SELECT     COUNT(*)
                                            FROM    Account_Item AS ai
                                            WHERE   ai.event_id = Account_Item.event_id
                                                AND   ai.master_id IN (
                                            SELECT id
                                            FROM Account AS a
                                            WHERE  a.createDatetime <= Account.createDatetime
                                                AND  a.contract_id = Account.contract_id)
                                        ) AS ai_num
                                        '''
                        q_from+=u'''
                            LEFT JOIN ClientWork ON ClientWork.client_id=Event.client_id
                                    AND ClientWork.deleted = 0
                                    AND ClientWork.id = (
                                        SELECT max(CW.id) FROM ClientWork AS CW where CW.client_id=Event.client_id)
                            LEFT JOIN Organisation AS work ON work.id=ClientWork.org_id
                                    AND work.deleted = 0
                            LEFT JOIN rbHealthGroup ON Diagnostic.healthGroup_id=rbHealthGroup.id
                            LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Event.client_id
                                    AND ClientPolicy.id = (
                                        SELECT max(CP.id)
                                        FROM ClientPolicy AS CP
                                        LEFT JOIN rbPolicyType ON rbPolicyType.id = CP.policyType_id
                                        WHERE CP.deleted = 0 AND CP.client_id = Event.client_id AND (CP.policyType_id IS NULL OR rbPolicyType.name LIKE \'ОМС%%\'))
                            LEFT JOIN Organisation AS insurer ON insurer.id=ClientPolicy.insurer_id
                                    AND insurer.deleted = 0
                            LEFT JOIN Account ON Account.id = %d
                            ''' % accountId
                        q_where+=''

                    if self.parent.export_type=='RD2':
                        q_select+=', Event.prevEventDate, Diagnostic.healthGroup_id'
                        q_from+=''
                        q_where+=''

                    return q_select+q_from+q_where

                q=get_stmt()
                query=db.query(q)
#               assert query.size() == 1,u'Странно, должна быть одна запись, а получено %d' % query.numRowsAffected()
                self.dbf_recs=[]

                while query.next():
                    record=query.record()
                    rec=dbfRD2.newRecord()
                    def val(name): return record.value(name)
                    def set_field(name, val):
                        rec[name]=val
                        col=header_ind[name]
                        item=QtGui.QTableWidgetItem(forceString(val))
                        self.tableWidget.setItem(n, col, item)
                    clientId=forceRef(val('client_id'))
                    client=getClientInfo(clientId)
                    sexCode=forceInt(client['sexCode'])
                    age = calcAgeInYears(client['birthDate'], forceDate(val('execDate')))

                    def set_client_info(LNAMEField, FNAMEField, MNAMEField, BDATEField):
                        set_field(LNAMEField, forceString(client['lastName']))
                        set_field(FNAMEField, forceString(client['firstName']))
                        set_field(MNAMEField, forceString(client['patrName']))
                        set_field(BDATEField, get_date(client['birthDate']))

                    def set_address():
                        TYPEADDR=''
                        regAddressRecord=getClientAddress(clientId, 0)
                        freeInput, KLADRCode, KLADRStreetCode, house, corpus, flat = \
                            getClientAddressEx(clientId)

                        if KLADRCode:
                            set_field('ADRES_REG', getCityName(KLADRCode))
                            if KLADRCode[:2]=='78':
                                TYPEADDR=u'г'
                            elif KLADRCode[:2]=='47':
                                TYPEADDR=u'о'
                            else:
                                TYPEADDR=u'и'
                            if KLADRStreetCode:
                                set_field('UL', getStreetName(KLADRStreetCode))
                            else:
                                set_field('UL', u'населенный пункт улиц не имеет')
                            set_field('DOM', house if house not in ['', '-'] else '1')
                            set_field('KOR', corpus)
                            set_field('KV', flat)
                            area, region, npunkt, street, streettype = getInfisCodes(
                                KLADRCode, KLADRStreetCode, house, corpus)
                            set_field('AREA', area)
                            set_field('REGION', region)
                            set_field('NPUNKT', npunkt)
                            set_field('STREET', street)
                            set_field('STREETYPE', streettype)
                        elif freeInput:
                            if re.match(u'^(г(\. | |\.))?(СПб|(С|Санкт)-Петербург)', freeInput):
                                TYPEADDR=u'г'
                            elif re.match(u'^Лен(\.| |\. )обл[\. ]', freeInput):
                                TYPEADDR=u'о'
                                set_field('AREA', u'ЛО')
                            else:
                                TYPEADDR=u'и'
                            l=len(freeInput)
                            nt_list=[
                                (u'ул.', u'ул'), (u'ул ', u'ул'), (u'улица', u'ул'),
                                (u'проспект', u'пр'), (u'пр-кт', u'пр'), (u'пр.', u'пр'),
                                (u'переулок', u'пу'), (u'пер.', u'пу'),
                                (u'набережная', u'н'), (u'наб.', u'н'),
                                (u'шоссе', u'ш'), (u'ш.', u'ш'),
                                (u'бульвар', u'б'), (u'б-р', u'б'), (u'б.', u'б'),
                                (u'площадь', u'пл'), (u'пл.', u'пл'),
                                (u'аллея', u'ал'), (u'ал.', u'ал'),
                                (u'проезд', u'пз'),
                                (u'линия', u'л'), (u'лин.', u'л')]
                            def get_pt():
                                for (n, t) in nt_list:
                                    pos=freeInput.find(n)
                                    if pos>=0:
                                        return (pos, t)
                                return (-1, '')
                            (ul_pos, STREETYPE)=get_pt()
                            if ul_pos>=0:
                                ul1=ul_pos; ul2=ul_pos
                                for p in range(ul_pos, -1, -1):
                                    if freeInput[p]==',': break
                                    else: ul1=p
                                for p in range(ul_pos, l):
                                    if freeInput[p]==',': break
                                    else: ul2=p
                                ADRES_REG = freeInput[:ul1].rstrip(',')
                                set_field('ADRES_REG', ADRES_REG)
                                set_field('NPUNKT',    ADRES_REG.split(',')[-1].strip())
                                UL=freeInput[ul1:ul2+1].strip()
                                if not UL:
                                    UL=u'населенный пункт улиц не имеет'
                                set_field('UL', UL)
                                set_field('STREETYPE', STREETYPE)
                            DOM, KOR, KV = get_dom_korp_kv(freeInput)
                            if DOM:
                                set_field('DOM', DOM.strip())
                            if KOR:
                                set_field('KOR', KOR.strip())
                            if KV:
                                set_field('KV', KV.strip())
                        if TYPEADDR: set_field('TYPEADDR', TYPEADDR)
                        if TYPEADDR!=u'г':
                            set_field('STREET', '*')
                            set_field('STREETYPE', '')

                    Policy=getClientPolicy(clientId)
                    set_field(DIAGField, forceString(val('MKB')))
                    if self.parent.export_type=='RD-DS':
                        set_field(SUMMAField, forceDouble(val('sum')))
                    else:
                        set_field(SUMMAField, forceInt(val('sum')))
                    set_field(ADATEField, get_date(val('execDate')))
                    eventId=forceInt(val('event_id'))
                    SNILS=formatSNILS(forceString(client['SNILS']))

                    if self.parent.export_type=='RD2':
                        set_client_info('LNAME', 'FNAME', 'MNAME', 'BDATE')
                        set_field('SEX', formatSex(sexCode))
                        set_field('PDATE', get_date(val('prevEventDate')))
                        set_field('SNILS', SNILS)
                        set_field('INN', lpu_INN)
                        set_field('REGNUM', smartInt(lpu_FSS))
                        set_field('GROUP', forceInt(val('healthGroup_id')))
                        set_field('KPP', smartInt(lpu_KPP))
                        if Policy:
                            serial=forceString(Policy.value('serial'))
                            number=forceString(Policy.value('number'))
                            if serial and number:
                                set_field(SPOLICYField, serial)
                                set_field('NPOLICY', number)
                        postCodes=getPostCodes(eventId)
                        pcNum=min(len(postCodes), 6)
                        for sc in range(pcNum):
                            set_field('DOCTOR'+str(sc+1), postCodes[sc])
                        work=getClientWork(clientId)
                        if work:
                            clientWorkId=forceRef(work.value('id'))
                            hurt, stage, factors = getWorkHurt(clientWorkId)
                            if hurt or stage or factors:
                                set_field('WORKV', smartInt(hurt))
                                set_field('WORKS', stage)
                                factors = factors.replace(',', ' ').split() # так как ''.split(',') => ['']
                                hfNum=min(len(factors), 6)
                                set_field('FQNT', hfNum)
                                for hf in range(hfNum):
                                    set_field('FACTOR'+str(hf+1), factors[hf])

                    if self.parent.export_type in ('RD1', 'RD3', 'RD4', 'RD-DS', 'RD5', 'RD6', 'RD7'):
                        if self.weekNumber and self.parent.export_type in ('RD1','RD-DS','RD4'):
                            set_field('NUMTR', self.weekNumber)
                        else:
                            set_field('NUMTR', account_num)
                        KOD_OKUD = { 'RD1': u'РД1', 'RD3': u'РД3', 'RD4': u'РД1', 'RD-DS':u'РД-ДС', 'RD5': u'РД-1', 'RD6': u'РД-1', 'RD7': u'РД-1' }.get(self.parent.export_type, self.parent.export_type)
                        set_client_info('FAM', 'IM', 'OT', 'DR')
                        set_field('POL', sexCode)
                        if self.parent.export_type in ('RD7'):
                            document=client['documentRecord']
                            documentTypeId=document.value('documentType_id')
                            documentTypeCode = forceString(db.translate('rbDocumentType', 'id', documentTypeId, 'code'))
                            serial = forceString(document.value('serial'))
                            number = forceString(document.value('number'))
                            if documentTypeCode == '1' and ' ' in serial:
                                left, right = serial.split(' ', 1)
                                set_field('PASS_LF', left)
                                set_field('PASS_RI', right)
                                set_field('PASS_DOC', number)
                            set_field('SNILS', SNILS)
                        if self.parent.export_type in ('RD-DS'):
                            document=client['documentRecord']
                            serial = forceString(document.value('serial'))
                            number = forceString(document.value('number'))
                            if ' ' in serial:
                                left, right = serial.split(' ', 1)
                            elif '-' in serial:
                                left, right = serial.split('-', 1)
                            else:
                                left, right = serial, ''
                            set_field('SV_PS_LF', left)
                            set_field('SV_PS_RI', right)
                            set_field('SV_PS_NUM', number)
                            set_field('SNILS', SNILS)

                        set_field('DATETR', get_date(accountDate))
                        set_field('ID', forceString(eventId))
                        set_field('KOD_OKUD', KOD_OKUD)
                        set_field('NAME_ORG', lpu_name)
                        set_field('KOD_ORG_OK', lpu_OKPO)
                        set_field('KOD_ORG_OG', lpu_OGRN)
                        set_field('KOD_ORG_OD', lpu_OKVED)
                        set_field('NAME_OKVED', lpu_OKVED_name)
                        if lpu_OKPF and lpu_OKFS:
                            set_field('KOD_OKOPF', lpu_OKPF+'/'+lpu_OKFS)
                        set_field('NAME_FS', lpu_OKFS_name)
                        set_field('NAME_ORG_P', payer_name)
                        if self.parent.export_type=='RD-DS':
                            set_field('KOD_ORG_1', payer_OKPO)
                            set_field('KOD_ORG_2', payer_OGRN)
                        else:
                            set_field('KOD_ORG_1', smartInt(payer_OKPO))
                            set_field('KOD_ORG_2', smartInt(payer_OGRN))
                        if self.parent.export_type in ('RD1', 'RD3', 'RD4', 'RD-DS'):
                            set_field('PERIOD_OKU', '362')
                        set_field('KOD_OKEI', '383')
                        set_field('PERIOD', PERIOD)
                        set_field('DATE_DOG', contract_date)
                        set_field('NOMER_DOG', contract_num)
                        if Policy:
                            serial=forceString(Policy.value('serial'))
                            number=Policy.value('number')
                            N_POL = forceString(number) if self.parent.export_type in ('RD4', 'RD-DS', 'RD5', 'RD6', 'RD7') else forceInt(number)
                            if serial and number:
                                set_field(SPOLICYField, serial)
                                set_field('N_POL', N_POL)
                        specs=[]
                        dop=[]
                        if self.parent.export_type=='RD1':
                            specs = [('T', '78'), ('N', '40'), ('H', '89'), ('O', '49'), ('E', '91')]
                            POL_spec1=('U', '84'); POL_spec2=('A', '02')
                            specs.append(POL_spec2 if sexCode==2 else POL_spec1)
                            dop0=[
                                ('H', '01', id1), ('G', '02', id1), ('KAK', '03', id1),
                                ('KAM', '04', id1), ('F', '06', id2), ('EKG', '07', id2)]
                            dop = get_dop(dop0)
                            for (dop_name, actionTypeId) in dop:
                                set_field(dop_name+'_DI', get_date(get_DI(actionTypeId, eventId)))
                            if sexCode==2:
                                M_DI=get_date(get_DI(9, eventId))
                                if M_DI:
                                    set_field('MU_VB', 2)
                                    set_field('M_DI', M_DI)
                                else:
                                    M_DI=get_date(get_DI(6, eventId))
                                    if M_DI:
                                        set_field('MU_VB', 1)
                                        set_field('M_DI', M_DI)
                        elif self.parent.export_type=='RD3':
                            specs = [
                                ('T', '52'), ('N', '40'), ('O', '49'), ('H', '19'), ('L', '48'),
                                ('S', '71'), ('OT', '81'), ('P', '54'), ('E', '20')]
                            POL_spec1=('U', '18'); POL_spec2=('G', '02')
                            specs.append(POL_spec2 if sexCode==2 else POL_spec1)
                            dop=[
                                ('UZI_DI1', 11), ('UZI_DI2', 12), ('UZI_DI3', 13),
                                ('EKG_DI', 8), ('KAK_DI', 4), ('KAM_DI', 5)]
                            for (dop_name, actionTypeId) in dop:
                                set_field(dop_name, get_date(get_DI(actionTypeId, eventId)))
                        elif self.parent.export_type=='RD4':
                            specs = [('T', '78'), ('N', '40'), ('H', '89'), ('O', '49'), ('E', '91')]
                            POL_spec1=('U', '84'); POL_spec2=('A', '02')
                            specs.append(POL_spec2 if sexCode==2 else POL_spec1)
                            dop0=[
                                ('F_DI', '06', id2), ('EKG_DI', '07', id2), ('H_DI', '01', id1),
                                ('L_DI', '05', id1), ('G_DI', '02', id1), ('KAK_DI', '03', id1),
                                ('KAM_DI', '04', id1), ('T_DI', '06', id1), ('O_CA', '07', id1),
                                ('O_PSI', '08', id1)]
                            dop = get_dop(dop0)
                            for (dop_name, actionTypeId) in dop:
                                set_field(dop_name, get_date(get_DI(actionTypeId, eventId)))
                            if sexCode==2:
                                M_DI = get_date(get_DI(6, eventId))
                                if M_DI:
                                    set_field('MU_VB', 1)
                                    set_field('M_DI', M_DI)
                        elif self.parent.export_type=='RD-DS':
                            specs = [
                                ('T', '52'), ('N', '40'), ('O', '49'), ('H', '19'), ('L', '48'),
                                ('S', '71'), ('OT', '81'), ('P', '54'), ('E', '20')]
                            POL_spec1=('U', '18'); POL_spec2=('G', '02')
                            specs.append(POL_spec2 if sexCode==2 else POL_spec1)
                            dop=[
                                ('UZI_1DI', 11), ('UZI_2DI', 12), ('UZI_3DI', 12), ('UZI_4DI', 13),
                                ('EKG_DI', 8), ('KAK_DI', 4), ('KAM_DI', 5)]
                            for (dop_name, actionTypeId) in dop:
                                set_field(dop_name, get_date(get_DI(actionTypeId, eventId)))
                        elif self.parent.export_type in ('RD5', 'RD6', 'RD7'):
                            specs = [('T', ['78', '45']), ('H', '89'), ('O', '49'), ('N', '40')]
                            POL_spec2=('A', '02')
                            if sexCode==2:
                                specs.append(POL_spec2)
                            if self.parent.export_type == 'RD5':
                                dop0=[
                                    ('ZIM_ZK', '35', id1),
                                    ('KAK_DI', '03', id1),
                                    ('KAM_DI', '04', id1),
                                    ('B_DI',   '30', id1),
                                    ('H_DI',   '01', id1),
                                    ('L_DI',   '05', id1),
                                    ('T_DI',   '06', id1),
                                    ('KM_DI',  '31', id1),
                                    ('BA_DI',  '33', id1),
                                    ('G_DI',   '02', id1),
                                    ('O_CA',   '07', id1),
                                    ('O_PSI',  '08', id1),
                                    ('EKG_DI', '07', id2),
                                    ('F_DI',   '06', id2),
                                    ]
                            elif self.parent.export_type in ('RD6', 'RD7'):
                                dop0=[
                                    ('ZIM_ZK', '35', id1),
                                    ('KAK_DI', '03', id1),
                                    ('KAM_DI', '04', id1),
                                    ('B_DI',   '30', id1),
                                    ('H_DI',   '01', id1),
                                    ('L_DI',   '05', id1),
                                    ('T_DI',   '06', id1),
                                    ('KR_DI', '31', id1),
                                    ('MK_DI', '32', id1),
                                    ('BL_DI', '33', id1),
                                    ('AM_DI', '34', id1),
                                    ('DATE_PZ',  u'пз1',  id3),
                                    ('G_DI',   '02', id1),
                                    ('O_CA',   '07', id1),
                                    ('O_PSI',  '08', id1),
                                    ('EKG_DI', '07', id2),
                                    ('F_DI',   '06', id2),
                                    ]
                            dop = get_dop(dop0)
                            for dop_name, actionTypeId in dop:
                                set_field(dop_name, get_date(get_DI(actionTypeId, eventId)))
                            if sexCode==2:
                                M_DI = get_date(get_DI(6, eventId))
                                if M_DI:
                                    set_field('MU_VB', 1)
                                    set_field('M_DI', M_DI)

                                if self.parent.export_type == 'RD7':
                                    dopDict = dict(dop)
                                    ZIM_ST = get_CancelationCause(dopDict.get('ZIM_ZK', 0), eventId)
                                    if ZIM_ST:
                                        set_field('ZIM_ZK', None)
                                        set_field('ZIM_ST', ZIM_ST)
                                        set_field('DZ_MKB', '%s, %s' % (forceString(rec['DZ_MKB']), ZIM_ST))

                                    M_ST = get_CancelationCause(6, eventId)
                                    if M_ST and age>=40:
                                        set_field('M_DI', None)
                                        set_field('M_ST', M_ST)
                                        set_field('DZ_MKB', '%s, %s' % (forceString(rec['DZ_MKB']), M_ST))

                        for spec, specialityCodeOrList in specs:
                            DO=get_DO(specialityCodeOrList, eventId)
                            set_field(spec+'_DO', get_date(DO))

                        set_field('RECEIVER', recipient_infis)
                        set_field('SMO', forceString(val('insurer_infis')))
                        PRIK_lpu=get_PRIK_lpu(clientId)
                        set_field('PRIK', 1 if PRIK_lpu==lpu_infis else 2)
                        if self.parent.export_type in ('RD5', 'RD6', 'RD7'):
                            if PRIK_lpu: set_field('TMO1', PRIK_lpu)
                        else:
                            if PRIK_lpu: set_field('TMO', PRIK_lpu)
                        set_field('RES_G', forceInt(val('hg')))
                        set_field('ID', forceString(eventId))
# при экспорте RD1 поля DATE_OTKAZ и т.п. должны быть пустыми, т.к.
# в принципе их должны заполнить на той стороне и вернуть нам.
#                        Account_Item=get_Account_Item(eventId)
#                        if Account_Item:
#                            Account_Item_date=get_date(Account_Item.value('date'))
#                            RefuseCode=forceString(Account_Item.value('code'))
#                            RefuseName=forceString(Account_Item.value('name'))
#                            if RefuseCode:
#                                set_field('DATE_OTKAZ', Account_Item_date)
#                                KOD_OTKAZ=100
#                                if RefuseCode=='': KOD_OTKAZ=1
#                                elif RefuseCode=='': KOD_OTKAZ=2
#                                elif RefuseCode=='': KOD_OTKAZ=3
#                                else:
#                                    set_field('COMMENT', RefuseName)
#                                set_field('KOD_OTKAZ', KOD_OTKAZ)
#                            else:
#                                set_field('DATE_OPLAT', Account_Item_date)

                        set_address()

                        if self.parent.export_type in ('RD6', 'RD7'):
                            set_field('NUM_PZ', clientId)

                        if self.parent.export_type in ('RD1', 'RD3'):
                            set_field('ID_PAT', forceString(clientId))

                        if self.parent.export_type in ('RD1', 'RD3', 'RD4', 'RD-DS', 'RD4', 'RD5', 'RD6', 'RD7'):
                            set_field('O_NAME', forceString(val('insurer_name')))

                        if self.parent.export_type in ('RD1', 'RD4'):
                            if SNILS:
                                set_field('SS', SNILS)
                            set_field('OKVED', forceString(val('work_OKVED')))
                            set_field('ORG', forceString(val('work_name')))
                            set_field('OKVD', forceString(val('post')))
                            set_field('INN', forceString(val('work_INN')))
                            set_field('KOD_PROG', 4)
                        elif self.parent.export_type in ('RD5', 'RD6', 'RD7'):
                            set_field('OKVED', forceString(val('work_OKVED')))
                            set_field('ORG', forceString(val('work_name')))
                            set_field('OKVD', forceString(val('post')))
                            set_field('INN', forceString(val('work_INN')))
                            set_field('KOD_PROG', 4)
                            if self.parent.export_type == 'RD7':
                                    set_field('STATUS_G', u'работающий' if forceString(val('work_name')) else u'неработающий')
                        elif self.parent.export_type=='RD3':
                            work=getClientWork(clientId)
                            if work:
                                orgId=forceRef(work.value('org_id'))
                                if orgId:
                                    set_field('DET_U', getOrganisationShortName(orgId))
                                    infisCode=forceString(QtGui.qApp.db.translate(
                                        'Organisation', 'id', orgId, 'infisCode'))
                                    set_field('KOD_DET_U', infisCode)
                                set_field('KOD_S_U', forceString(work.value('OKVED')))
                            set_field('KOD_PROG', 3)

                        if self.parent.export_type=='RD-DS':
                            work=getClientWork(clientId)
                            if work:
                                orgId=forceRef(work.value('org_id'))
                                if orgId:
                                    set_field('DET_U', getOrganisationShortName(orgId))
                                    OGRN=forceString(QtGui.qApp.db.translate('Organisation', 'id', orgId, 'OGRN'))
                                    set_field('OGRN_U', forceString(OGRN))
                            set_field('KOD_PROG', 4)

                        if self.parent.export_type  in ('RD4', 'RD-DS', 'RD5', 'RD6', 'RD7'):
                            PERIOD1=settleDate1.month() if not settleDate1.isNull() else None
                            set_field('PERIOD', PERIOD1)
                            ai_num=val('ai_num').toInt()[0]
                            set_field('NUM_V', ai_num)
                            set_field('DATE_V', pyDate(accountDate))
#                            Account_ItemId=forceString(val('Account_ItemId'))
#                            set_field('COMMENT', '[%s]' % Account_ItemId)

                        if self.pervDoc:
                            set_field('PERIOD', self.period)

                    rec.store()

            n=0
            acc_num=len(self.parent.AccountItemsIdList)
            self.tableWidget.setRowCount(acc_num)
            self.tableWidget.setColumnCount(len(header))
            self.tableWidget.setHorizontalHeaderLabels(header)
            self.progressBar.setMaximum(acc_num-1)
            for AccountItemId in self.parent.AccountItemsIdList:
                QtGui.qApp.processEvents()
                if self.abort: break
                self.progressBar.setValue(n)
                n+=1
                addAccount(AccountItemId, n-1)
            dbfRD2.close()
            self.parent.n=n

            if self.checkRAR.isChecked():
                self.parent.ext='.rar'
                prg=QtGui.qApp.execProgram('"%s" a -ep "%s" "%s"'% (rarArchiver(), rarFileName, dbfFileName))
                if not prg[0]:
                    self.parent.rarname=''
                    raise CException(u'не удалось запустить rar')
                if prg[2]:
                    self.parent.rarname=''
                    raise CException(u'ошибка при выполнении rar')
            else:
                self.parent.ext='.dbf'
                self.parent.rarname=dbfFileName

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
        self.progressBar.setValue(0)
        self.progressBar.setFormat(u'прервано' if self.abort else u'готово')
        self.progressBar.setValue(self.progressBar.maximum())
        self.btnExport.setEnabled(False)
        self.btnClose.setEnabled(False)
        if not self.abort and self.parent.rarname:
            self.done=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        self.abort=False; self.exportRun=False

    def exportXML(self):
        AccountItemsIdList=self.parent.AccountItemsIdList
        if not AccountItemsIdList:
            QtGui.QMessageBox.warning(
                self, u'Внимание!', u'Нечего выгружать', QtGui.QMessageBox.Close)
            return
        self.parent.export_type='XML'

        self.btnExport.setEnabled(False)
        self.abort=False; self.exportRun=True
        accountId=self.parent.accountId
        dialog = self.parent.XMLDialog
        db=QtGui.qApp.db

        try:
            record=self.get_record(self.parent.accountId)
            if not record: return
            account_num=forceString(record.value('account_num'))
            accountDate=forceDate(record.value('accountDate'))
            settleDate=get_date(record.value('settleDate'))
            settleDate1=forceDate(record.value('settleDate'))
            lpu_INN=forceString(record.value('lpu_INN'))
            lpu_KPP=forceString(record.value('lpu_KPP'))
            lpu_name=forceString(record.value('lpu_name'))
            lpu_OKPO=forceString(record.value('lpu_OKPO'))
            lpu_OGRN=forceString(record.value('lpu_OGRN'))
            lpu_OKVED=forceString(record.value('lpu_OKVED'))
            lpu_OKVED_name=forceString(record.value('lpu_OKVED_name'))
            lpu_infis=forceString(record.value('lpu_infis'))
            lpu_OKPF=forceString(record.value('lpu_OKPF'))
            lpu_OKFS=forceString(record.value('lpu_OKFS'))
            lpu_OKFS_name=forceString(record.value('lpu_OKFS_name'))
            lpu_FSS=forceString(record.value('lpu_FSS'))
            payer_FSS=forceString(record.value('payer_FSS'))
            payer_name=forceString(record.value('payer_name'))
            payer_OKPO=forceString(record.value('payer_OKPO'))
            payer_OGRN=forceString(record.value('payer_OGRN'))
            payer_INN=forceString(record.value('payer_INN'))
            payer_KPP=forceString(record.value('payer_KPP'))
            recipient_name=forceString(record.value('recipient_name'))
            recipient_OKPO=forceString(record.value('recipient_OKPO'))
            recipient_OGRN=forceString(record.value('recipient_OGRN'))
            recipient_infis=forceString(record.value('recipient_infis'))
            PERIOD=accountDate.month() if not accountDate.isNull() else None
            contract_num=forceString(record.value('contract_num'))
            contract_date=get_date(record.value('contract_date'))
            contract_resolution=forceString(record.value('contract_resolution'))
            self.parent.account_num=account_num
            self.parent.accountDate=accountDate
            self.parent.lpu_name=lpu_name
            self.parent.lpu_INN=lpu_INN
            self.parent.lpu_KPP=lpu_KPP
            self.parent.lpu_FSS=lpu_FSS
            self.parent.lpu_OGRN=lpu_OGRN
            self.parent.recipient_name=recipient_name
            self.parent.payer_name=payer_name
            self.parent.payer_INN=payer_INN
            self.parent.payer_KPP=payer_KPP
            self.parent.payer_FSS=payer_FSS
            self.parent.payer_OGRN=payer_OGRN
            self.parent.settleDate=settleDate

            dbf_name='result'
            tmp_dir=self.parent.tmp_dir
            self.parent.fname=dbf_name
            dbfFileName=os.path.join(tmp_dir, dbf_name+u'.xml')
            rarFileName=os.path.join(tmp_dir, dbf_name+u'.rar')
            self.parent.rarname=rarFileName
            file=QFile(dbfFileName)
            file.open(QIODevice.WriteOnly|QIODevice.Text)
            xml=QXmlStreamWriter(file)

            def putFIO(last, first, mid):
                xml.writeEmptyElement('name')
                xml.writeAttribute('last', last)
                xml.writeAttribute('first', first)
                xml.writeAttribute('mid', mid)

            def putDate(name, date):
                if date:
                    xml.writeEmptyElement(name)
                    xml.writeAttribute('year', str(date.year()))
                    xml.writeAttribute('month', str(date.month()))
                    xml.writeAttribute('day', str(date.day()))

            def putClienInfo(clientId):
                if not clientId:
                    return
                Client=getClientInfo(clientId)
                xml.writeStartElement('info')
                putFIO(Client['lastName'], Client['firstName'], Client['patrName'])

                birthDate=Client['birthDate']
                if birthDate:
                    putDate('birth_date', birthDate)

                xml.writeStartElement('sex')
                xml.writeCharacters(formatSex(Client['sexCode']))
                xml.writeEndElement() #sex

                document=getClientDocument(clientId)
                if document:
                    documentTypeId=forceInt(document.value('documentType_id'))
                    if documentTypeId:
                        xml.writeEmptyElement('document')
                        documentType = db.translate('rbDocumentType', 'id', documentTypeId, 'name')
                        xml.writeAttribute('type', forceString(documentType))
                        xml.writeAttribute('serial', forceString(document.value('serial')))
                        xml.writeAttribute('number', forceString(document.value('number')))

                Policy=getClientPolicy(clientId)
                if Policy:
                    serial=forceString(Policy.value('serial'))
                    number=forceString(Policy.value('number'))
                    if serial and number:
                        xml.writeEmptyElement('polis')
                        insurerId=forceInt(Policy.value('serial'))
                        insurer=getOrganisationShortName(insurerId)
                        xml.writeAttribute('insurer', insurer)
                        xml.writeAttribute('serial', serial)
                        xml.writeAttribute('number', number)

                xml.writeStartElement('snils')
                xml.writeCharacters(formatSNILS(Client['SNILS']))
                xml.writeEndElement() # snils

                workRecord = getClientWork(clientId)
                if workRecord:
                    orgId = forceRef(workRecord.value('org_id'))
                    work_info=getOrganisationInfo(orgId)
                    if work_info:
                        xml.writeStartElement('inn')
                        xml.writeCharacters(work_info['INN'])
                        xml.writeEndElement() # inn

                xml.writeEndElement() # info

            def putPersonInfo(personId):
                if not personId:
                    return
                personInfo = getPersonInfo(personId)
                xml.writeStartElement('person_info')

                xml.writeStartElement('id')
                xml.writeCharacters(str(personId))
                xml.writeEndElement() # id

                putFIO(personInfo['lastName'], personInfo['firstName'], personInfo['patrName'])

                xml.writeStartElement('spec')
                xml.writeCharacters(personInfo['specialityName'])
                xml.writeEndElement() # spec

                xml.writeStartElement('post')
                xml.writeCharacters(personInfo['postName'])
                xml.writeEndElement() # post

                def getOrgNames(orgStructure_id):
                    if not orgStructure_id:
                        return []
                    orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
                    parent_id=forceInt(db.translate('OrgStructure', 'id', orgStructure_id, 'parent_id'))
                    return getOrgNames(parent_id)+[orgStructureName]

                orgStructure_id = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
                orgNames=getOrgNames(orgStructure_id)
                xml.writeStartElement('org_structure')
                xml.writeCharacters(u'; '.join(orgNames))
                xml.writeEndElement() # org_structure

                xml.writeEndElement() # person_info

            def putActionProperties(actionId):
                if not actionId:
                    return
                stmt='''
                select
                rbUnit.code AS unit_code, rbUnit.name AS unit_name, ActionPropertyType.typeName, ActionProperty.id as ActionPropertyId
                from
                ActionProperty
                join ActionPropertyType on ActionPropertyType.id=ActionProperty.type_id
                join rbUnit on rbUnit.id=ActionProperty.unit_id
                where ActionProperty.action_id=%d
                ''' % actionId
                xml.writeStartElement('action_properties')

                query=db.query(q)
                while query.next():
                    record=query.record()
                    def val(name): return record.value(name)
                    typeName=forceString(val('typeName'))
                    if typeName not in ['Time', 'String', 'Integer', 'Double', 'Date']:
                        continue
                    tableName='ActionProperty_'+typeName
                    xml.writeStartElement('property')

                    ActionPropertyId=forceInt(val('ActionPropertyId'))
                    value=forceString(db.translate(tableName, 'id', ActionPropertyId, 'value'))
                    xml.writeStartElement('value')
                    xml.writeCharacters(value)
                    xml.writeEndElement() # value

                    xml.writeStartElement('unit')
                    xml.writeCharacters(forceString(val('unit_code')))
                    xml.writeEndElement() # unit

                    xml.writeEndElement() # property

                xml.writeEndElement() # action_properties

            xml.writeStartDocument()
            xml.writeStartElement('actions_result')
            curClientId=None
            curEventId=None

            q='''
select
Event.client_id, Event.id as event_id, Event.execDate, Diagnosis.MKB,
ActionType.name as action_name, Action.begDate, Action.endDate, Action.status, Action.person_id,
rbResult.name as result, Action.id as action_id

from
Account_Item
join Event on Event.id=Account_Item.event_id
left join Diagnostic on (Diagnostic.event_id=Event.id and Diagnostic.diagnosisType_id=1)
left join Diagnosis on Diagnostic.diagnosis_id=Diagnosis.id
join Action on Action.event_id=Event.id
left join ActionType on ActionType.id=Action.actionType_id
left join rbResult ON rbResult.id=Event.result_id
where
Account_Item.id in ('''+", ".join(str(x) for x in AccountItemsIdList)+''')
            '''
            date1=forceString(dialog.edtBegDate.date().toString('yyyy-MM-dd'))
            date2=forceString(dialog.edtEndDate.date().toString('yyyy-MM-dd'))
            q+=' and (Event.execDate between "'+date1+'" and "'+date2+'")'
            tableAction  = db.table('Action')
            tableEvent  = db.table('Event')
            tablePerson = db.table('Person')
            tableActionType = db.table('ActionType')
            personId=dialog.cmbPerson.value()
            cond = []
            if personId:
                cond.append(tableAction['person_id'].eq(personId))
            eventTypeId=dialog.cmbEventType.value()
            if eventTypeId:
                cond.append(tableEvent['eventType_id'].eq(eventTypeId))
            orgStructureId=dialog.cmbOrgStructure.value()
            if orgStructureId:
                cond.append(tablePerson['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
            actionTypeClass=dialog.cmbClass.currentIndex()
            actionTypeId=dialog.cmbActionType.value()
#            if actionTypeClass:
#                cond.append('ActionType.class=%d' % actionTypeClass)
#            if actionTypeId:
#                cond.append('ActionType.id=%d' % actionTypeId)
            if actionTypeId:
                cond.append(tableActionType['id'].inlist(getActionTypeDescendants(actionTypeId, actionTypeClass)))
            elif actionTypeClass is not None:
                cond.append(tableActionType['class'].eq(actionTypeClass))
            if cond:
                q+=('and '+QtGui.qApp.db.joinAnd(cond))
            q+=' order by Event.client_id, Event.id'
            query=db.query(q)
            s=query.size()
            if s>0:
                self.progressBar.setMaximum(s-1)
            n=0
            while query.next():
                QtGui.qApp.processEvents()
                if self.abort: break
                self.progressBar.setValue(n)
                n+=1
                record=query.record()
                def val(name): return record.value(name)

                def putEventInfo():
                    xml.writeStartElement('event_info')

                    execDate=forceDate(val('execDate'))
                    putDate('date', execDate)

                    MKB=val('MKB').toString()
                    xml.writeStartElement('MKB')
                    xml.writeCharacters(MKB)
                    xml.writeEndElement() # MKB

                    result=forceString(val('result'))
                    xml.writeStartElement('result')
                    xml.writeCharacters(result)
                    xml.writeEndElement() # result

                    xml.writeEndElement() # event_info

                def putActionInfo():
                    xml.writeStartElement('action')

                    personId=val('person_id').toInt()[0]
                    putPersonInfo(personId)

                    action_name=val('action_name').toString()
                    xml.writeStartElement('type')
                    xml.writeCharacters(action_name)
                    xml.writeEndElement() # type

                    begDate=val('begDate').toDate()
                    putDate('beg_date', begDate)
                    endDate=val('endDate').toDate()
                    putDate('end_date', endDate)

                    actionId=val('action_id').toInt()[0]
                    putActionProperties(actionId)

                    xml.writeEndElement() # action

                clientId=val('client_id').toInt()[0]
                eventId=val('event_id').toInt()[0]
                if clientId!=curClientId:
                    if curEventId:
                        xml.writeEndElement() # event
                        curEventId=None
                    if curClientId:
                        xml.writeEndElement() # events
                        xml.writeEndElement() # client
                    curClientId=clientId
                    xml.writeStartElement('client')
                    putClienInfo(clientId)
                    xml.writeStartElement('events')
                if eventId!=curEventId:
                    if curEventId:
                        xml.writeEndElement() # event
                    curEventId=eventId
                    xml.writeStartElement('event')
                    putEventInfo()
                putActionInfo()

            xml.writeEndDocument()

            if self.checkRAR.isChecked():
                self.parent.ext='.rar'
                prg=QtGui.qApp.execProgram('"%s" a -ep "%s" "%s"'% (rarArchiver(), rarFileName, dbfFileName))
                if not prg[0]:
                    self.parent.rarname=''
                    raise CException(u'не удалось запустить rar')
                if prg[2]:
                    self.parent.rarname=''
                    raise CException(u'ошибка при выполнении rar')
            else:
                self.parent.ext='.xml'
                self.parent.rarname=dbfFileName

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
        self.progressBar.setValue(0)
        self.progressBar.setFormat(u'прервано' if self.abort else u'готово')
        self.progressBar.setValue(self.progressBar.maximum())
        self.btnExport.setEnabled(False)
        self.btnClose.setEnabled(False)
        if not self.abort and self.parent.rarname:
            self.done=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        self.abort=False; self.exportRun=False

    def isComplete(self):
        return self.done


class CMyWizardPage2(QtGui.QWizardPage, Ui_ExportRD2_Wizard_2):
    def __init__(self, parent, pervDoc):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
#        if pervDoc:
#            self.btnSendMail.setEnabled(False)
#            self.reportButton.setEnabled(False)
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.nameEdit.setText(self.parent.fname)
        self.edtFileDir.setText(save_dir)

    def checkName(self):
        self.saveButton.setEnabled(
            self.nameEdit.text()!='' and self.edtFileDir.text()!='')
#        self.saveButton.setEnabled(self.edtFileDir.text()!='')

    @QtCore.pyqtSlot(QString)
    def on_nameEdit_textChanged(self, string):
        self.checkName()

    @QtCore.pyqtSlot(QString)
    def on_edtFileDir_textChanged(self, string):
        self.nameEdit.setText(self.parent.fname)
        self.checkName()

    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dirName = forceString(QtGui.QFileDialog.getExistingDirectory(
            self, u'Укажите каталог', self.edtFileDir.text()))
        if dirName != '':
            self.edtFileDir.setText(dirName)
            self.checkName()

    @QtCore.pyqtSlot()
    def on_btnSendMail_clicked(self):
        if self.parent.rarname:
            export_type=self.parent.export_type
            if export_type=='RD1':
                prog='RD1 860'
            elif export_type=='RD2':
                prog='RD2 859'
            else:
                prog=export_type
            db = QtGui.qApp.db
            record = db.getRecordEx('rbAccountExportFormat', '*', 'prog=\''+prog+'\'')
            if record:
                emailTo = forceString(record.value('emailTo'))
                subject = forceString(record.value('subject'))
                message = forceString(record.value('message'))
            else:
                emailTo = u'dd.data@miac.zdrav.spb.ru'
                subject = ''
                if export_type=='RD1': subject=u'форма РД1'
                if export_type=='RD2': subject=u'форма РД2'
                message = u'Уважаемые господа,\n'                       \
                          u'зацените результаты доп. диспансеризации\n' \
                          u'в {shortName}, ОГРН: {OGRN}\n'              \
                          u'за период с {begDate} по {endDate}\n'       \
                          u'в приложении {NR} записей\n'                \
                          u'\n'                                         \
                          u'--\n'                                       \
                          u'WBR\n'                                      \
                          u'{shortName}\n'
            data = {}
            orgRec=QtGui.qApp.db.getRecord(
                'Organisation', 'INN, OGRN, shortName', QtGui.qApp.currentOrgId())
            data['INN'] = forceString(orgRec.value('INN'))
            data['OGRN'] = forceString(orgRec.value('OGRN'))
            data['shortName'] = forceString(orgRec.value('shortName'))
            data['NR'] = self.parent.n
            endDate=self.parent.settleDate
            year = endDate.year
            month = endDate.month
            if export_type in ('RD1', 'RD3', 'RD4', 'RD5', 'RD6', 'RD7'):
                begDate=QDate(year, month, 1)
                data['begDate'] = forceString(begDate)
                data['endDate'] = forceString(QDate(endDate))
            elif export_type=='RD2':
                k=(month-1)/3
                begDate=QDate(year, k*3+1, 1)
                data['begDate'] = forceString(begDate)
                data['endDate'] = forceString(QDate(endDate))
            subject = substFields(subject, data)
            message = substFields(message, data)
            SendMailDialog.sendMail(self, emailTo, subject, message, [self.parent.rarname])

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        global save_dir
        self.nameEdit.setText(self.parent.fname)
        self.saveButton.setEnabled(False)
        dir=forceString(self.edtFileDir.text())
        save_name=os.path.join(dir, forceString(self.nameEdit.text())+self.parent.ext)
        shutil.copy(self.parent.rarname, save_name)
        save_dir=self.edtFileDir.text()

    @QtCore.pyqtSlot()
    def on_reportButton_clicked(self):
        fname=self.parent.fname+self.parent.ext
        fsize=os.path.getsize(self.parent.rarname)
        md5=calcCheckSum(self.parent.rarname)
        rep=CRD2Report(
            self, fname, fsize, md5, self.parent.n, self.parent.export_type, self.parent.account_num, self.parent.accountDate, self.parent.lpu_name, self.parent.lpu_INN, self.parent.lpu_KPP, self.parent.lpu_FSS, self.parent.lpu_OGRN, self.parent.recipient_name, self.parent.payer_name, self.parent.payer_INN, self.parent.payer_KPP, self.parent.payer_FSS, self.parent.payer_OGRN, self.parent.settleDate)
        rep.exec_()

    def initializePage(self):
        self.nameEdit.setText(self.parent.fname)

class Export_RD1_RD2(QtGui.QWizard):
    def __init__(self, AccountItemsIdList, accountIdList, parent=None, pervDoc=False, period=None, weekNumber=None, useXML=False, XMLDialog=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт реестра')
        self.AccountItemsIdList=AccountItemsIdList
        self.accountIdList=accountIdList
        self.accountId=accountIdList[0]
        self.pervDoc=pervDoc
        self.useXML=useXML
        self.XMLDialog=XMLDialog
        self.rarname=''
        self.fname=''
        self.ext=''
        self.n=0
        self.addPage(CMyWizardPage1(self, pervDoc, period, weekNumber))
        self.addPage(CMyWizardPage2(self, pervDoc))
        self.rec_num=0
        self.tmp_dir=unicode(tempfile.mkdtemp('','vista-med_mail_'), locale.getpreferredencoding())
        self.dbf=None
        self.dbf_recs=None


    def exec_(self):
        QtGui.QWizard.exec_(self)
        try:
            shutil.rmtree(self.tmp_dir)
        except:
            pass


def getPostCodes(event):
    stmt='''
SELECT rbPost.regionalCode
FROM Diagnostic
LEFT JOIN rbDiagnosisType ON rbDiagnosisType.id = Diagnostic.diagnosisType_id
LEFT JOIN Person ON Person.id = Diagnostic.person_id
LEFT JOIN rbPost ON rbPost.id = Person.post_id
WHERE Diagnostic.event_id ="'''+forceString(event)+'''"
AND rbDiagnosisType.code IN ('1', '2')
AND Diagnostic.endDate IS NOT NULL
AND Diagnostic.person_id IS NOT NULL'''
    query=QtGui.qApp.db.query(stmt)
    f=[]
    while query.next():
        record=query.record()
        f.append(forceInt(record.value(0)))
    return f


def get_DO(specialityCodeOrList, eventId):
    db = QtGui.qApp.db
    tableDiagnostic=db.table('Diagnostic')
    tableSpeciality = db.table('rbSpeciality')
    table = tableDiagnostic.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tableDiagnostic['speciality_id']))
    cond=[tableDiagnostic['event_id'].eq(eventId),
          tableDiagnostic['deleted'].eq(0),
          tableDiagnostic['diagnosisType_id'].le(2), #!!!
         ]
    if isinstance(specialityCodeOrList, (list, tuple)):
        cond.append(tableSpeciality['code'].inlist(specialityCodeOrList))
    else:
        cond.append(tableSpeciality['code'].eq(specialityCodeOrList))
    rec = db.getRecordEx(table, tableDiagnostic['endDate'], cond)
    return rec.value(0) if rec else None


def get_Action(actionTypeId, eventId):
    tableAction=tbl('Action')
    cond=[tableAction['event_id'].eq(eventId),
          tableAction['deleted'].eq(0),
          tableAction['actionType_id'].eq(actionTypeId)
         ]
    return QtGui.qApp.db.getRecordEx(tableAction, 'status, endDate, MKB, note', where=cond)


def get_DI(actionTypeId, eventId):
    rec=get_Action(actionTypeId, eventId)
    return rec.value('endDate') if rec else None


def get_CancelationCause(actionTypeId, eventId):
    rec=get_Action(actionTypeId, eventId)
    if rec:
        status = forceInt(rec.value('status'))
        if status == ActionStatus.Cancelled:
            return forceStringEx(rec.value('MKB')) or forceStringEx(rec.value('note'))
    return ''


def get_PRIK_lpu(clientId):
    tableClientAttach=tbl('ClientAttach')
    tableAttachType  =tbl('rbAttachType')
    tableOrganisation=tbl('Organisation')
    cond=[
        tableClientAttach['client_id'].eq(clientId),
        tableAttachType['temporary'].eq(0),
        tableAttachType['outcome'].eq(0)
         ]
#    cond.append(tableClientAttach['attachType_id'].eq(2)) # это дурно - писать в программе id записей!

    recList=QtGui.qApp.db.getRecordList(tableClientAttach.leftJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id'])), where=cond, order=tableClientAttach['id'].name()+' DESC')
    if recList:
        LPU_id=forceInt(recList[0].value('LPU_id'))
        infisCode=QtGui.qApp.db.translate(tableOrganisation, 'id', LPU_id, 'infisCode')
        return forceString(infisCode)
    else: return None


save_dir=''

class CRD2Report(CReportViewDialog):
    def __init__(self, parent, fname, fsize, md5, n, export_type, account_num, accountDate, lpu_name, lpu_INN, lpu_KPP, lpu_FSS, lpu_OGRN, recipient_name, payer_name, payer_INN, payer_KPP, payer_FSS, payer_OGRN, settleDate):
        CReportViewDialog.__init__(self, parent)
        self.fname=fname
        self.fsize=fsize
        self.md5=md5
        self.n=n
        self.export_type=export_type
        self.account_num=account_num
        self.accountDate=accountDate
        self.lpu_name=lpu_name
        self.lpu_INN=lpu_INN
        self.lpu_KPP=lpu_KPP
        self.lpu_FSS=lpu_FSS
        self.lpu_OGRN=lpu_OGRN
        self.recipient_name=recipient_name
        self.payer_name=payer_name
        self.payer_INN=payer_INN
        self.payer_KPP=payer_KPP
        self.payer_FSS=payer_FSS
        self.payer_OGRN=payer_OGRN
        self.settleDate=settleDate
#        self.setTitle(u'Акт приёма-передачи', u'')
        if export_type in ('RD5', 'RD6', 'RD7'):
            object = self.buildRD5()
        else:
            object = self.build()
        self.setWindowTitle(u'Акт приёма-передачи')
        self.setText(object)

    def build(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        text0=u'''Акт приёма-передачи
файла со сведениями о результатах '''
        text_res_type=u''
        if self.export_type in ['RD1', 'RD3']: text_res_type=u'дополнительной диспансеризации'
        if self.export_type=='RD2': text_res_type=u'углублённых медицинских осмотров'
        text0+=text_res_type+u'\n'
        text0=text0.upper()
        cursor.insertText(text0)
        cursor.insertBlock()
        text0=u''

#        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        text0+=u'\n\nк реестру счёта %s от %s\n' \
            % (self.account_num, self.accountDate.toString('dd.MM.yyyy'))
        text0+=u'за период с '
        endDate=self.settleDate
        year = endDate.year
        month = endDate.month
        if self.export_type in ['RD1', 'RD3']:
            begDate=QDate(year, month, 1)
            text0+=forceString(begDate)
        if self.export_type=='RD2':
            k=(month-1)/3
            begDate=QDate(year, k*3+1, 1)
            text0+=forceString(begDate)
        text0+=u' по '+endDate.strftime('%d.%m.%Y')+u'\n\n'
#        text0+=u'получатель: '+self.recipient_name+'\n'
        text0+=u'исполнитель: %s\nИНН %s\nКПП %s\nФСС %s\nОГРН %s\n\n' \
            % (self.lpu_name, self.lpu_INN, self.lpu_KPP, self.lpu_FSS, self.lpu_OGRN)
        text0+=u'плательщик: %s\nИНН %s\nКПП %s\nФСС %s\nОГРН %s\n\n' \
            % (self.payer_name, self.payer_INN, self.payer_KPP, self.payer_FSS, self.payer_OGRN)

        text0+=u'Представленный файл содержит сведения о результатах '+text_res_type+u', проведённых в %d году.\n\n' % year

        cursor.insertText(text0)
        cursor.insertBlock()

        tableColumns = [
          ('20%', [ u'Имя файла' ], CReportBase.AlignLeft),
          ('10%', [ u'Размер файла (байт)' ], CReportBase.AlignLeft),
          ('20%', [ u'Контрольная сумма' ], CReportBase.AlignLeft),
          ('20%', [ u'Дата создания' ], CReportBase.AlignRight),
          ('10%', [ u'Количество записей' ], CReportBase.AlignRight),
          ('20%', [ u'Количество записей, прошедших логический контроль'], CReportBase.AlignRight),
                       ]

        table = createTable(cursor, tableColumns)

        i = table.addRow()
        table.setText(i, 0, self.fname)
        table.setText(i, 1, str(self.fsize))
        table.setText(i, 2, str(self.md5))
        table.setText(i, 3, datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        table.setText(i, 4, str(self.n))
        table.setText(i, 5, str(self.n))

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText('\n\n\n')
        cursor.insertBlock()

        rows = []
        rows.append([u'от плательщика', u'от исполнителя (поликлиника)'])
        rows.append([u'\n\n', u'\n\n'])
        rows.append([u'________________________________', u'________________________________'])
        rows.append([u'(должность, подпись) расшифровка', u'(должность, подпись) расшифровка'])
        rows.append([u'\n', u'\n'])
        rows.append([u'"__"____________2007г.', u'"__"____________2007г.'])
        columnDescrs = [('50%', [], CReportBase.AlignCenter), ('50%', [], CReportBase.AlignCenter)]
        table1 = createTable (
            cursor, columnDescrs, headerRowCount=len(rows), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(rows):
            table1.setText(i, 0, row[0])
            table1.setText(i, 1, row[1])
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        return doc.toHtml(QByteArray('utf-8'))


    def buildRD5(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        right = QtGui.QTextBlockFormat()
        right.setAlignment(Qt.AlignRight)
        cursor.setBlockFormat(right)
        text0=u'Исполнительному директору\nТерриториального фонда обязательного\nмедицинского страхования Санкт-Петербурга\nВ.М. Колабутину'
        cursor.insertText(text0)
        cursor.insertBlock()
        cursor.setBlockFormat(QtGui.QTextBlockFormat())
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Исх. № ________ от ____________')
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        text0 = u'%s в рамках мониторинга направляет в электронном виде (в формате dbf) информацию по форме реестра счетов, содержащую сведения о %d законченных случаях дополнительной диспансеризации на  %s.' % (
                 self.lpu_name, self.n, forceString(QDate(self.settleDate)))
        cursor.insertText(text0)
        cursor.insertBlock()
        endDate=self.settleDate
        year = endDate.year
        month = endDate.month
        begDate=QDate(year, month, 1)
        text0 = u'Информация представлена за период с %s по %s г.' % (forceString(begDate), forceString(QDate(self.settleDate)))
        cursor.insertText(text0)
        cursor.insertBlock()
        cursor.insertBlock()

        text0 = u'Приложение: ______________________________________в 1 экз.'
        cursor.insertText(text0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        text0 = u'Руководитель учреждения здравоохранения\n\n\n______________\n\n\n\nМ.П.'
        cursor.insertText(text0)
        cursor.insertBlock()
        return doc.toHtml(QByteArray('utf-8'))


def isTariffApplicable(tariff, eventId, date=None):
    db = QtGui.qApp.db
    sex = tariff.sex
    ageSelector = tariff.ageSelector
    eventTypeId = tariff.eventTypeId
    if sex or ageSelector or eventTypeId:
        eventRecord = db.getRecord('Event', '*', eventId)
        if eventRecord:
            if eventTypeId and eventTypeId != forceRef(eventRecord.value('eventType_id')):
                return False
            if not date:
                date = forceDate(eventRecord.value('execDate'))
            clientId = forceRef(eventRecord.value('client_id'))
            if clientId:
                clientRecord = db.getRecord('Client', '*', clientId)
                if clientRecord:
                    clientSex = forceInt(clientRecord.value('sex'))
                    if sex and sex != clientSex :
                        return False
                    if ageSelector:
                        clientBirthDate = forceDate(clientRecord.value('birthDate'))
                        clientAge = calcAgeTuple(clientBirthDate, date)
                        if not clientAge:
                            clientAge = (0, 0, 0, 0)
                        return checkAgeSelector(ageSelector, clientAge)
                    return True
        return False
    else:
        return True

def exposeByEvents(progressDialog, eventIdList, contractInfo, accountId, accountItemIdList):
    totalAmount = 0.0
    totalSum    = 0.0

    def exposeEvent(contractInfo, accountId, eventId):
        db = QtGui.qApp.db
        event = db.getRecord('Event', 'id, eventType_id, payStatus', eventId)
        eventTypeId = forceRef(event.value('eventType_id'))
        totalAmount = 0.0
        totalSum    = 0.0
        tariffList = contractInfo.tariffByEventType.get(eventTypeId, None)
        if tariffList:
            for tariff in tariffList:
               if isTariffApplicable(tariff, eventId):
                    price  = tariff.price
                    amount = 1.0
                    sum    = price*amount
                    tableAccountItem = db.table('Account_Item')
                    acountItem = tableAccountItem.newRecord()
                    acountItem.setValue('master_id',  toVariant(accountId))
                    acountItem.setValue('event_id',   toVariant(eventId))
                    acountItem.setValue('price',      toVariant(price))
                    acountItem.setValue('unit_id',    toVariant(tariff.unitId))
                    acountItem.setValue('amount',     toVariant(amount))
                    acountItem.setValue('sum',        toVariant(sum))
                    accountItemIdList.append(db.insertRecord(tableAccountItem, acountItem))
                    totalAmount += amount
                    totalSum    += sum
                    break
        return totalAmount, totalSum

    def exposeEventAsCoupleVisit(contractInfo, accountId, eventId):
        db = QtGui.qApp.db
        event = db.getRecord('Event', 'id, eventType_id, payStatus', eventId)
        eventTypeId = forceRef(event.value('eventType_id'))
        totalAmount = 0.0
        totalSum    = 0.0
        tariffList = contractInfo.tariffByCoupleVisitEventType.get(eventTypeId, None)
        if tariffList:
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId):
                    serviceId = tariff.serviceId
                    countRecord = db.getRecordEx('Visit', 'COUNT(*)', 'event_id=%d AND service_id=%d'%(eventId, serviceId))
                    count = forceInt(countRecord.value(0))
                    price  = tariff.price
                    amount = float(count)
                    sum    = price*min(amount, tariff.amount)
                    tableAccountItem = db.table('Account_Item')
                    acountItem = tableAccountItem.newRecord()
                    acountItem.setValue('master_id',  toVariant(accountId))
                    acountItem.setValue('event_id',   toVariant(eventId))
                    acountItem.setValue('price',      toVariant(price))
                    acountItem.setValue('unit_id',    toVariant(tariff.unitId))
                    acountItem.setValue('amount',     toVariant(amount))
                    acountItem.setValue('sum',        toVariant(sum))
                    accountItemIdList.append(db.insertRecord(tableAccountItem, acountItem))
                    totalAmount += amount
                    totalSum    += sum
                    break
        return totalAmount, totalSum

    for eventId in eventIdList:
        progressDialog.step()
        amount, sum = exposeEvent(contractInfo, accountId, eventId)
        totalAmount += amount
        totalSum += sum
        amount, sum = exposeEventAsCoupleVisit(contractInfo, accountId, eventId)
        totalAmount += amount
        totalSum += sum
    return totalAmount, totalSum


def exposeByVisitsByActionServices(progressDialog, visitIdList, contractInfo, accountId, accountItemIdList):
    totalAmount = 0.0
    totalSum    = 0.0

    def exposeVisitByActionServices(contractInfo, accountId, serviceId, visitId):
        db = QtGui.qApp.db
        visit = db.getRecord('Visit', 'id, event_id, date, service_id, payStatus', visitId)
#        serviceId = forceRef(visit.value('service_id'))
        totalAmount = 0.0
        totalSum    = 0.0
        tariffList = contractInfo.tariffByVisitService.get(serviceId, None)
        if tariffList:
            eventId = forceRef(visit.value('event_id'))
            visitDate = forceDate(visit.value('date'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, visitDate):
                    price  = tariff.price
                    amount = 1.0
                    sum    = price*amount
                    tableAccountItem = db.table('Account_Item')
                    acountItem = tableAccountItem.newRecord()
                    acountItem.setValue('master_id',  toVariant(accountId))
                    acountItem.setValue('event_id',   visit.value('event_id'))
                    acountItem.setValue('visit_id',   toVariant(visitId))
                    acountItem.setValue('price',      toVariant(price))
                    acountItem.setValue('unit_id',    toVariant(tariff.unitId))
                    acountItem.setValue('amount',     toVariant(amount))
                    acountItem.setValue('sum',        toVariant(sum))
                    acountItem.setValue('service_id', toVariant(serviceId))
                    accountItemIdList.append(db.insertRecord(tableAccountItem, acountItem))
                    totalAmount += amount
                    totalSum    += sum
                    break
        return totalAmount, totalSum

    mapServiceIdToVisitIdList = selectVisitsByActionServices(contractInfo, None, QDate.currentDate())
    for serviceId, visitIdList in mapServiceIdToVisitIdList.items():
        for visitId in visitIdList:
            progressDialog.step()
            amount, sum = exposeVisitByActionServices(contractInfo, accountId, serviceId, visitId)
            totalAmount += amount
            totalSum += sum
    return totalAmount, totalSum


def exposeByVisits(progressDialog, visitIdList, contractInfo, accountId, accountItemIdList):
    totalAmount = 0.0
    totalSum    = 0.0

    def exposeVisit(contractInfo, accountId, visitId):
        db = QtGui.qApp.db
        visit = db.getRecord('Visit', 'id, event_id, date, service_id, payStatus', visitId)
        serviceId = forceRef(visit.value('service_id'))
        totalAmount = 0.0
        totalSum    = 0.0
        tariffList = contractInfo.tariffByVisitService.get(serviceId, None)
        if tariffList:
            eventId = forceRef(visit.value('event_id'))
            visitDate = forceDate(visit.value('date'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, visitDate):
                    price  = tariff.price
                    amount = 1.0
                    sum    = price*amount
                    tableAccountItem = db.table('Account_Item')
                    acountItem = tableAccountItem.newRecord()
                    acountItem.setValue('master_id',  toVariant(accountId))
                    acountItem.setValue('event_id',   visit.value('event_id'))
                    acountItem.setValue('visit_id',   toVariant(visitId))
                    acountItem.setValue('price',      toVariant(price))
                    acountItem.setValue('unit_id',    toVariant(tariff.unitId))
                    acountItem.setValue('amount',     toVariant(amount))
                    acountItem.setValue('sum',        toVariant(sum))
                    accountItemIdList.append(db.insertRecord(tableAccountItem, acountItem))
                    totalAmount += amount
                    totalSum    += sum
                    break
        return totalAmount, totalSum

    for visitId in visitIdList:
        progressDialog.step()
        amount, sum = exposeVisit(contractInfo, accountId, visitId)
        totalAmount += amount
        totalSum += sum
    return totalAmount, totalSum

def exposeByActions(progressDialog, actionIdList, contractInfo, accountId, accountItemIdList):
    totalAmount = 0.0
    totalSum    = 0.0

    def exposeAction(contractInfo, accountId, actionId):
        db = QtGui.qApp.db
        action = db.getRecord('Action', 'id, actionType_id, event_id, endDate, payStatus, amount', actionId)
        serviceId = getActionService(forceRef(action.value('actionType_id')))
        amount = forceDouble(action.value('amount'))
        totalAmount = 0.0
        totalSum    = 0.0
        tariffList = contractInfo.tariffByActionService.get(serviceId, None)
        if tariffList:
            eventId = forceRef(action.value('event_id'))
            endDate = forceDate(action.value('endDate'))
            for tariff in tariffList:
                if isTariffApplicable(tariff, eventId, endDate):
                    price  = tariff.price
                    sum    = price*amount
                    tableAccountItem = db.table('Account_Item')
                    acountItem = tableAccountItem.newRecord()
                    acountItem.setValue('master_id',  toVariant(accountId))
                    acountItem.setValue('event_id',   action.value('event_id'))
                    acountItem.setValue('action_id',  toVariant(actionId))
                    acountItem.setValue('price',      toVariant(price))
                    acountItem.setValue('unit_id',    toVariant(tariff.unitId))
                    acountItem.setValue('amount',     toVariant(amount))
                    acountItem.setValue('sum',        toVariant(sum))
                    accountItemIdList.append(db.insertRecord(tableAccountItem, acountItem))
                    totalAmount += amount
                    totalSum    += sum
                    break
        return totalAmount, totalSum

    for actionId in actionIdList:
        progressDialog.step()
        amount, sum = exposeAction(contractInfo, accountId, actionId)
        totalAmount += amount
        totalSum += sum
    return totalAmount, totalSum

def reExpose(progressDialog, idList, contractInfo, orgStructureId, date, accountId, accountRecord, accountItemIdList):
    db = QtGui.qApp.db

    if idList and not accountId:
        accountId, accountRecord = createAccountRecord(
            contractInfo, QtGui.qApp.currentOrgId, orgStructureId, date, reexpose=True)

    tableAccountItem = db.table('Account_Item')
    totalAmount = 0.0
    totalSum    = 0.0
    for oldId in idList:
        progressDialog.step()
        oldAccountItem = db.getRecord(tableAccountItem, '*', oldId)
        newAcountItem = tableAccountItem.newRecord()
        newAcountItem.setValue('master_id',  toVariant(accountId))
        newAcountItem.setValue('event_id',   oldAccountItem.value('event_id'))
        newAcountItem.setValue('visit_id',   oldAccountItem.value('visit_id'))
        newAcountItem.setValue('action_id',  oldAccountItem.value('action_id'))
        newAcountItem.setValue('price',      oldAccountItem.value('price'))
        newAcountItem.setValue('unit_id',    oldAccountItem.value('unit_id'))
        updateDocsPayStatus(oldAccountItem, contractInfo.payStatusMask, CPayStatus.exposedBits)
        varAmount = oldAccountItem.value('amount')
        varSum    = oldAccountItem.value('sum')
        newAcountItem.setValue('amount',     varAmount)
        newAcountItem.setValue('sum',        varSum)
        newId = db.insertRecord(tableAccountItem, newAcountItem)
        oldAccountItem.setValue('reexposeItem_id', toVariant(newId))
        db.updateRecord(tableAccountItem, oldAccountItem)
        totalAmount += forceDouble(varAmount)
        totalSum    += forceDouble(varSum)
    return accountId, accountRecord, totalAmount, totalSum

def getAccountList(parent, dialog, contractIdList):
    accountItemIdList=[]
    accountIdList=[]
    begDate=dialog.edtBegDate.date()
    endDate=dialog.edtEndDate.date()
    date=dialog.edtDate.date()
    perevystavl=dialog.chkPerevystavl.isChecked()
    period=dialog.boxPeriod.value()
    db = QtGui.qApp.db
    try:
        progressDialog = CFormProgressDialog(parent)
        progressDialog.setNumContracts(len(contractIdList))
        progressDialog.show()
        for contractId in contractIdList:
            contractInfo = getContractInfo(contractId)
            progressDialog.setContractName(contractInfo.number+' '+forceString(contractInfo.date))
            eventIdList = selectEvents(contractInfo, None, date)
            mapServiceIdToVisitIdList = selectVisitsByActionServices(contractInfo, None, date)
            visitIdList = selectVisits(contractInfo, None, date)
            actionIdList = selectActions(contractInfo, None, date)
            if perevystavl:
                reexposableIdList = selectReexposableAccountItems(contractInfo,  date)
            else:
                reexposableIdList = []
            progressDialog.setNumContractSteps(len(eventIdList)+
                                               sum(len(idList) for idList in mapServiceIdToVisitIdList.values())+
                                               len(visitIdList)+
                                               len(actionIdList)+
                                               #len(actionPropertyIdList)+
                                               len(reexposableIdList))
            accountId, accountRecord = createAccountRecord(contractInfo, QtGui.qApp.currentOrgId, None, date)
            accountIdList.append(accountId)
            totalAmount = 0.0
            totalSum = 0.0
            amount, s = exposeByEvents(progressDialog, eventIdList, contractInfo, accountId, accountItemIdList)
            totalAmount += amount
            totalSum += s
            amount, s = exposeByVisitsByActionServices(progressDialog, mapServiceIdToVisitIdList, contractInfo, accountId, accountItemIdList)
            totalAmount += amount
            totalSum    += s
            amount, s = exposeByVisits(progressDialog, visitIdList, contractInfo, accountId, accountItemIdList)
            totalAmount += amount
            totalSum += s
            amount, s = exposeByActions(progressDialog, actionIdList, contractInfo, accountId, accountItemIdList)
            totalAmount += amount
            totalSum += s
            if perevystavl:
#                reexposableIdList = selectReexposableAccountItems(contractInfo)
                accountItemIdList+=reexposableIdList
                accountId, accountRecord, amount, s = reExpose(
                    progressDialog, reexposableIdList, contractInfo, QtGui.qApp.currentOrgId, date, accountId, accountRecord, accountItemIdList)
                accountIdList.append(accountId)
                totalAmount += amount
                totalSum += s
        progressDialog.close()
    except:
        progressDialog.close()
        db.rollback()
        raise
    return accountIdList, accountItemIdList


def exportPervDoc(parent=None):
    dialog = CPervDocDialog(parent)
    if dialog.exec_():
        treeIndex=dialog.treeContracts.currentIndex()
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        contractIdList=treeItem.idList if treeItem else []
        if not contractIdList:
            QtGui.QMessageBox.warning(
                parent, u'Внимание!', u'Необходимо выбрать договор', QtGui.QMessageBox.Close)
            return
        period=dialog.boxPeriod.value()
        date=dialog.edtDate.date()
        db = QtGui.qApp.db
        db.transaction()
        try:
            accountIdList, accountItemIdList = getAccountList(parent, dialog, contractIdList)
            Export_RD1_RD2(accountItemIdList, accountIdList, parent, True, period, date.weekNumber()).exec_()
        finally:
            db.rollback()


class CPervDocDialog(CDialogBase, Ui_PervDocDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.modelContracts = CContractTreeModel(self)
        self.modelContracts.setObjectName('modelContracts')
        self.selectionModelContracts = QtGui.QItemSelectionModel(self.modelContracts, self)
        self.selectionModelContracts.setObjectName('selectionModelContracts')

        self.selectionModelContracts.setCurrentIndex(
            self.modelContracts.index(0, 0) , QtGui.QItemSelectionModel.SelectCurrent)

        self.setupUi(self)

        self.treeContracts.setModel(self.modelContracts)
        self.treeContracts.setSelectionModel(self.selectionModelContracts)
        self.treeContracts.setRootIsDecorated(False)
        self.treeContracts.setAlternatingRowColors(True)
        self.treeContracts.header().hide()
        self.treeContracts.expandAll()

        yesterday = QDate.currentDate().addDays(-1)
        self.edtBegDate.setDate(firstMonthDay(yesterday))
        self.edtEndDate.setDate(lastMonthDay(yesterday))
        self.edtDate.setDate(QDate.currentDate())
        self.boxPeriod.setValue(QDate.currentDate().month())


    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelContracts_currentChanged(self, current, previous):
        db = QtGui.qApp.db
        table = db.table('Account')
        tableEx = table
        treeIndex=self.treeContracts.currentIndex()
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        contractIdList=treeItem.idList if treeItem else []
        if contractIdList:
            contractId=contractIdList[0]
            contractInfo = getContractInfo(contractId)
            self.edtBegDate.setDate(contractInfo.begDate)
            self.edtEndDate.setDate(contractInfo.endDate)

mapactionTypeIdToServiceId= {}

def getActionService(actionTypeId):
    result = mapactionTypeIdToServiceId.get(actionTypeId, False)
    if result == False:
        db = QtGui.qApp.db
        result = forceRef(db.translate('ActionType', 'id', actionTypeId, 'service_id'))
        mapactionTypeIdToServiceId[actionTypeId] = result
    return result
