#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import shutil
import tempfile

from Orgs.Utils import getOrganisationInfo
from library import SendMailDialog
from library.subst import substFields
from library.CalcCheckSum import *
from Reports.ReportBase import *
from Reports.ReportView import CReportViewDialog
from Utils import *
from DBFFormats import *

from Exchange.ExportActionTemplate import getActionPropertyValue

from Ui_Export131_Wizard_1 import Ui_Export131_Wizard_1
from Ui_Export131_Wizard_2 import Ui_Export131_Wizard_2

class CMyWizardPage1(QtGui.QWizardPage, Ui_Export131_Wizard_1):
    def __init__(self, parent):
        global EventTypes
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.tblEventType.setTable('EventType')
        self.parent=parent
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.abort=False
        self.exportRun=False
        self.done=False
        EventTypes_str=forceString(getVal(
            QtGui.qApp.preferences.appPrefs, 'EventTypes', '1, 12, 25, 27, 26'))
        EventTypes=[int(x) for x in EventTypes_str.split(', ') if EventTypes_str]
        self.tblEventType.setValues(EventTypes)

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        if self.exportRun:
            self.abort=True

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        if self.checkXML.isChecked():
            self.exportXML()
        else:
            self.export()

    def export(self):
        global EventTypes
        self.btnExport.setEnabled(False)
        self.abort=False
        self.exportRun=True
        finished_only=self.checkFinished.isChecked()
        db=QtGui.qApp.db
        documentTypeTable = db.table('rbDocumentType')
        tableAction=tbl('Action')
        n=0
        try:
            OGRN = forceString(QtGui.qApp.db.translate(
                'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))
            tmp_dir=self.parent.tmp_dir
            dbf_name=OGRN+u'_Р131_0'
            self.parent.fname=dbf_name
            dbfFileName = os.path.join(tmp_dir, dbf_name+'.dbf')
            rarFileName = os.path.join(tmp_dir, dbf_name+'.rar')

            self.parent.rarname=rarFileName
            dbf131=dbf.Dbf(dbfFileName, new=True, encoding='cp866')
            dbfFields=get_131_Fields_new()
            dbf131.addField(*dbfFields)
            header=[f[0] for f in dbfFields]
            header_ind={}; ind=0
            for h in header:
                header_ind[h]=ind
                ind+=1

            q='''
                SELECT
                    Event.client_id,
                    Event.id as eventId,
                    Event.eventType_id,
                    Event.prevEventDate,
                    Contract.number as dog_number,
                    Contract.date as dog_date,
                    Contract.resolution as resolution
                FROM
                    Event
                    LEFT JOIN Contract ON Contract.id=Event.contract_id
                WHERE
                    Event.org_id = %d
                ''' % (QtGui.qApp.currentOrgId())
            date1=forceString(self.dateEdit_1.date().toString('yyyy-MM-dd'))
            date2=forceString(self.dateEdit_2.date().toString('yyyy-MM-dd'))
            self.parent.date1=self.dateEdit_1.date()
            self.parent.date2=self.dateEdit_2.date()
            q+=' and (Event.execDate between "'+date1+'" and "'+date2+'")'
            if finished_only:
                q+=' and Event.execDate is not null'
            EventTypes=self.tblEventType.values()
            if EventTypes:
                q+=' and Event.eventType_id in ('+', '.join([str(et) for et in EventTypes])+')'
            if self.checkPayed.isChecked():
                q+=' and isEventPayed(Event.id)'
            query=db.query(q)
            query.setForwardOnly(True)
            n=0
            s=query.size()
            self.parent.rec_num=s
            self.tableWidget.setRowCount(s)
            self.tableWidget.setColumnCount(len(header))
            self.tableWidget.setHorizontalHeaderLabels(header)
            if s>0:
                self.progressBar.setMaximum(s-1)

            r1=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=1')
            id1=forceInt(r1.value(0))
            r2=QtGui.qApp.db.getRecordEx('ActionType', 'id', 'code=\'1-2\' and class=1')
            id2=forceInt(r2.value(0))

            while query.next():
                def set_field(name, val):
                    rec[name]=val
                    col=header_ind[name]
                    item=QtGui.QTableWidgetItem(forceString(val))
                    self.tableWidget.setItem(n-1, col, item)
                QtGui.qApp.processEvents()
                if self.abort: break
                self.progressBar.setValue(n)
                n+=1
                record=query.record()
                rec=dbf131.newRecord()
                def val(name): return record.value(name)
                eventId=forceInt(val('eventId'))
                clientId=forceInt(val('client_id'))
                Client=getClientInfo(clientId)
                set_field('OGRN', OGRN)
                set_field('ID', forceString(eventId))
                set_field('DATE_DOG', get_date(val('dog_date')))
                set_field('NOMER_DOG', forceString(val('dog_number')))
                set_field('PROG', u'САМСОН-ВИСТА')
                set_field('N_MK', str(clientId))

                set_field('FAM', Client['lastName'])
                set_field('IM', Client['firstName'])
                set_field('OT', Client['patrName'])
                sexCode=Client['sexCode']
                set_field('POL', sexCode)
                set_field('DR', get_date(Client['birthDate']))
                set_field('SNILS', formatSNILS(Client['SNILS']))
#                ClientAttaches=Client['attaches']
                clientAddress=getClientAddress(clientId, 0)
                address_id=clientAddress.value('address_id') if clientAddress else None
                address=getAddress(address_id)
                KLADRCode=address.KLADRCode
                if KLADRCode:
                    socr=forceString(db.translate('kladr.KLADR', 'CODE', KLADRCode, 'SOCR', idFieldName='CODE'))
                    set_field('ADRES_TYPE',  1 if socr==u'г' else 2)
                else:
                    set_field('ADRES_TYPE', 1)
                if KLADRCode:
                    set_field('NAS_P', getCityName(KLADRCode))
                KLADRStreetCode=address.KLADRStreetCode
                if KLADRStreetCode:
                    set_field('UL', getStreetName(KLADRStreetCode))
                else:
                    set_field('UL', u'населенный пункт улиц не имеет')
                set_field('DOM', address.number)
                set_field('KOR', address.corpus)
                set_field('KV', address.flat)
                documentRecord = getClientDocument(clientId)
                if documentRecord:
                    documentType_id=forceInt(documentRecord.value('documentType_id'))
                    documentTypeRecord = db.getRecord(documentTypeTable, 'name', documentType_id)
                    if documentTypeRecord:
                        set_field('TYPE_DOC', forceString(documentTypeRecord.value(0)))
                    serial=forceString(documentRecord.value('serial'))
                    number=forceString(documentRecord.value('number'))
                    set_field('PASSPORT', serial+' '+number)
                policyRecord = getClientPolicy(clientId)
                if policyRecord:
                    insurer_id=policyRecord.value('insurer_id')
                    set_field('SMO_NAME', getOrganisationShortName(forceRef(insurer_id)))
                    SMO=forceString(db.translate('Organisation', 'id', insurer_id, 'infisCode'))
                    set_field('SMO', SMO)
                    serial=forceString(policyRecord.value('serial'))
                    number=forceString(policyRecord.value('number'))
                    set_field('SN_POLIS', serial+' '+number)
                TIP_DD=forceString(val('resolution'))
                workRecord = getClientWork(clientId)
                if workRecord:
                    orgId = forceRef(workRecord.value('org_id'))
                    work_info=getOrganisationInfo(orgId)
                    set_field('RABOTA', getOrganisationShortName(orgId))
                    if work_info:
                        set_field('INN', work_info['INN'])
                        set_field('KPP', work_info['KPP'])
                    set_field('OKVED', forceString(workRecord.value('OKVED')))
                    set_field('DOLGN', forceString(workRecord.value('post')))
                    hurt, stage, factors = getWorkHurt(forceRef(workRecord.value('id')))
                    set_field('WORKV', hurt)
                    set_field('WORKS', stage)
                    set_field('FAKTOR', factors)
                    if TIP_DD==u'921':
                        OKFS_id=forceInt(QtGui.qApp.db.translate(
                            'Organisation', 'id', orgId, 'OKFS_id'))
                        if OKFS_id not in [7, 9, 15]:
                            TIP_DD=u'921Б'
                set_field('TIP_DD', TIP_DD)
                set_field('PDATE', get_date(record.value('prevEventDate')))

                AttachRecord=getAttachRecord(clientId, 0)
                if AttachRecord:
                    LPU_id=AttachRecord['LPU_id']
                    if LPU_id:
                        P_LPY_KOD=forceString(db.translate('Organisation', 'id', LPU_id, 'infisCode'))
                        set_field('P_LPY_KOD', P_LPY_KOD)
                        LPU_info=getOrganisationInfo(LPU_id)
                        if LPU_info:
                            set_field('P_LPY_NAME', LPU_info['shortName'])
                            set_field('P_LPY_OGRN', LPU_info['OGRN'])

                attachCode = 2
                if AttachRecord and AttachRecord['LPU_id'] == QtGui.qApp.currentOrgId() and AttachRecord['code'] in ['1', '2']:
                    attachCode = 1
                else:
                    tmpAttachRecord=getAttachRecord(clientId, 1)
                    if tmpAttachRecord and tmpAttachRecord['LPU_id'] == QtGui.qApp.currentOrgId():
                        tmpAttachCode = tmpAttachRecord['code']
                        if tmpAttachCode == '5':
                            attachCode = 2
                        elif tmpAttachCode == '3':
                            attachCode = 3
                        elif tmpAttachCode == '4':
                            attachCode = 4
                set_field('PRIK', attachCode)

                DATE_ZAV=None

                specs=get_specs(sexCode)
                for (spec, speciality, diagNum) in specs:
                    diags=getDiags(eventId, speciality)
                    diagNum=min(diagNum, len(diags))
                    san=2
                    for iDiag in range(1, diagNum+1):
                        diag=diags[iDiag-1]
                        lastName=forceString(diag.value('lastName'))
                        firstName=forceString(diag.value('firstName'))
                        patrName=forceString(diag.value('patrName'))
                        set_field(spec+'_NAME', lastName+' '+firstName+' '+patrName)
                        set_field(spec+'_KOD', forceString(diag.value('code')))
                        endDate=diag.value('endDate')
                        if endDate and not DATE_ZAV:
                            DATE_ZAV=max(DATE_ZAV, endDate)
                        set_field(spec+'_DO', get_date(endDate))
                        sanatorium=forceInt(diag.value('sanatorium'))
                        if sanatorium in [1, 2]:
                            san=1
                        set_field(spec+'_MKB_'+str(iDiag), forceString(diag.value('MKB')))
                        character_id = forceInt(diag.value('character_id'))
                        set_field(spec+'_V_'+str(iDiag), 1 if character_id<=2 else 2)
                        stage_id = forceInt(diag.value('stage_id'))
                        set_field(spec+'_ST_'+str(iDiag), 3 if stage_id==1 else 4)
                        set_field(spec+'_GZ_'+str(iDiag), forceInt(diag.value('healthGroup_id')))
                    set_field(spec+'_SL', san)

                ds=0
                OtherDiags=getOtherDiags(eventId, specs)
                for otherDiag in OtherDiags:
                    ds+=1
                    if ds>3: break
                    dss=str(ds)
                    lastName=forceString(otherDiag.value('lastName'))
                    firstName=forceString(otherDiag.value('firstName'))
                    patrName=forceString(otherDiag.value('patrName'))
                    set_field('NAME_'+dss, lastName+' '+firstName+' '+patrName)
                    spec_code=forceString(otherDiag.value('spec_code'))
                    OKSOCode=forceString(otherDiag.value('OKSOCode'))
                    spec_name=forceString(otherDiag.value('spec_name'))
                    set_field('SPEC_'+dss, '['+OKSOCode+']'+spec_name)
                    set_field('KOD_'+dss, forceString(otherDiag.value('code')))
                    set_field('DO_'+dss, get_date(otherDiag.value('endDate')))
                    set_field('S_'+dss+'_MKB_1', forceString(otherDiag.value('MKB')))
                    character_id=forceInt(otherDiag.value('character_id'))
                    set_field('S_'+dss+'_V_1', 1 if character_id<=2 else 2)
                    stage_id=forceInt(otherDiag.value('stage_id'))
                    set_field('S_'+dss+'_ST_1', 3 if stage_id==1 else 4)
                    set_field('S_'+dss+'_GZ_1', forceInt(otherDiag.value('healthGroup_id')))
                    sanatorium=forceInt(otherDiag.value('sanatorium'))
                    set_field('SL_'+dss, 1 if sanatorium in [1, 2] else 2)

                dop0=[
                    ('H', '01', id1), ('L', '05', id1), ('T', '06', id1), ('O_CA', '07', id1),
                    ('O_PSI', '08', id1), ('G', '02', id1), ('KAK', '03', id1),
                    ('KAM', '04', id1), ('F', '06', id2), ('EKG', '07', id2),
                    ('UPROST', '09', id2), ('M', '05', id2), ('M', '08', id2)]
                dop = get_dop(dop0)
                for (name, actionTypeId) in dop:
#                    actionTypeId=forceInt(db.translate('ActionType', 'code', actionType, 'id'))
                    cond=[]
                    cond.append(tableAction['event_id'].eq(eventId))
                    cond.append(tableAction['actionType_id'].eq(actionTypeId))
                    actList=db.getRecordList(tableAction, where=cond)
                    if actList:
                        act=actList[0]
                        set_field(name+'_DI', get_date(act.value('begDate')))
                        set_field(name+'_DP', get_date(act.value('endDate')))
                        if actionTypeId==dop[-2][1]:
                            set_field('MU_VB', 1)
                        if actionTypeId==dop[-1][1]:
                            set_field('MU_VB', 2)

                dn=0
                for other_act in get_other_act(eventId, dop):
                    dn+=1
                    if dn>2: break
                    dns=str(dn)
                    set_field('DOP_'+dns+'_NAME', forceString(other_act.value('name')))
                    set_field('DI_'+dns, get_date(other_act.value('begDate')))
                    set_field('DP_'+dns, get_date(other_act.value('endDate')))

                set_field('DATE_ZAV', get_date(DATE_ZAV))

                rec.store()
            dbf131.close()
            self.parent.n=n
            if self.checkRAR.isChecked():
                self.parent.ext='.rar'

                try:
                    compressFileInRar(dbfFileName, rarFileName)
                except CRarException as e:
                    QtGui.QMessageBox.critical(self, u"Ошибка при архивации", unicode(e), QtGui.QMessageBox.Close)
                    self.progressBar.setValue(unicode(e))
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
        self.progressBar.setValue(n-1)
        self.btnExport.setEnabled(False)
        self.btnClose.setEnabled(False)
        EventTypes=self.tblEventType.values()
        if not self.abort and self.parent.rarname:
            self.done=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        self.abort=False
        self.exportRun=False

    def exportXML(self):
        global EventTypes
        self.btnExport.setEnabled(False)
        self.abort=False
        self.exportRun=True
        finished_only=self.checkFinished.isChecked()
        db=QtGui.qApp.db
        OGRN = forceString(db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))
        tmp_dir = self.parent.tmp_dir
        fileName = OGRN+u'_Р131_0'
        self.parent.fname = fileName
        xmlFileName = os.path.join(tmp_dir, fileName+'.xml')
        rarFileName = os.path.join(tmp_dir, fileName+'.rar')
        self.parent.rarname = rarFileName
        done = False

        outFile = QtCore.QFile(xmlFileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Экспорт формы 131',
                                      u'Не могу открыть файл для записи %s:\n%s.'  %\
                                      (xmlFileName, outFile.errorString()))

        myXmlStreamWriter = CMyXmlStreamWriter(self, OGRN)
        if (myXmlStreamWriter.writeFile(outFile,  self.progressBar)):
            self.progressBar.setText(u'Готово')
            done = True
        else:
            self.progressBar.setText(u'Прервано')

        outFile.close()

        if done:
            if self.checkRAR.isChecked():
                self.parent.ext='.rar'
                self.progressBar.setText(u'Сжатие')
                try:
                    compressFileInRar(xmlFileName, rarFileName)
                    self.progressBar.setText(u'Сжато успешно')
                except CRarException as e:
                    self.progressBar.setText(unicode(e))
                    QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)
            else:
                self.parent.ext='.xml'
                self.parent.rarname=xmlFileName


        self.btnExport.setEnabled(False)
        self.btnClose.setEnabled(False)
        EventTypes=self.tblEventType.values()
        if not self.abort and self.parent.rarname:
            self.done=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        self.abort=False
        self.exportRun=False


    def isComplete(self):
        return self.done

class CMyWizardPage2(QtGui.QWizardPage, Ui_Export131_Wizard_2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        OGRN = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId(), 'OGRN'))
        self.nameEdit.setText(OGRN+u'_Р131_0')
        self.edtFileDir.setText(save_dir)

    def checkName(self):
        self.saveButton.setEnabled(
            self.nameEdit.text()!='' and self.edtFileDir.text()!='')

    @QtCore.pyqtSlot(QString)
    def on_nameEdit_textChanged(self, string):
        self.checkName()

    @QtCore.pyqtSlot(QString)
    def on_edtFileDir_textChanged(self, string):
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
            db = QtGui.qApp.db
            record = db.getRecordEx('rbAccountExportFormat', '*', 'prog=\'F131\'')
            if record:
                emailTo = forceString(record.value('emailTo'))
                subject = forceString(record.value('subject'))
                message = forceString(record.value('message'))
            else:
                emailTo = u'dd.data@miac.zdrav.spb.ru'
                subject = u'ДД: 131/у-ДД'
                message = u'Уважаемые господа,\n'                       \
                          u'зацените результаты доп. диспансеризации\n' \
                          u'в {shortName}, ОГРН: {OGRN}\n'              \
                          u'за период с {begDate} по {endDate}\n'       \
                          u'в приложении {NR} записей\n'                \
                          u'\n'                                         \
                          u'--\n'                                       \
                          u'WBR\n'                                      \
                          u'{shortName}\n'
#            ОГРН и название учреждения, направившего посылку, период, за который передаются данные, количество передаваемых записей, ФИО и контактный телефон ответственного лица
            orgRec=QtGui.qApp.db.getRecord(
                'Organisation', 'INN, OGRN, shortName', QtGui.qApp.currentOrgId())
            data = {}
            data['INN'] = forceString(orgRec.value('INN'))
            data['OGRN'] = forceString(orgRec.value('OGRN'))
            data['shortName'] = forceString(orgRec.value('shortName'))
            data['begDate'] = forceString(self.parent.date1)
            data['endDate'] = forceString(self.parent.date2)
            data['NR'] = self.parent.rec_num
            subject = substFields(subject, data)
            message = substFields(message, data)
            SendMailDialog.sendMail(self, emailTo, subject, message, [self.parent.rarname])

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        global save_dir
        self.saveButton.setEnabled(False)
        dir=forceString(self.edtFileDir.text())
        save_name = os.path.join(dir, forceString(self.nameEdit.text())+self.parent.ext)
        shutil.copy(self.parent.rarname, save_name)
        save_dir=self.edtFileDir.text()

    @QtCore.pyqtSlot()
    def on_reportButton_clicked(self):
        fname=self.parent.fname+self.parent.ext
        fsize=os.path.getsize(self.parent.rarname)
        md5=calcCheckSum(self.parent.rarname)
        rep=C131Report(
            self, fname, fsize, md5, self.parent.n, self.parent.date1, self.parent.date2,
#            self.parent.lpu_name, self.parent.lpu_INN, self.parent.lpu_KPP, self.parent.lpu_FSS, self.parent.lpu_OGRN, self.parent.recipient_name, self.parent.payer_name, self.parent.payer_INN, self.parent.payer_KPP, self.parent.payer_FSS, self.parent.payer_OGRN
            )
        rep.exec_()


class Export131(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт формы 131')
        self.addPage(CMyWizardPage1(self))
        self.addPage(CMyWizardPage2(self))
        self.rarname=''
        self.ext=''
        self.date1=forceDate(getVal(QtGui.qApp.preferences.appPrefs, 'Export131begDate',  None))
        self.date2=forceDate(getVal(QtGui.qApp.preferences.appPrefs, 'Export131endDate',  None))

        if self.date1:
            self.page(0).dateEdit_1.setDate(self.date1)

        if self.date2:
            self.page(0).dateEdit_2.setDate(self.date2)

        self.rec_num=0
        self.tmp_dir = unicode(tempfile.mkdtemp('','vista-med_dbf_'), locale.getpreferredencoding())
        self.page(0).checkFinished.setChecked(forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'Export131Finished', 'False')))
        self.page(0).checkPayed.setChecked(forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'Export131Payed', 'False')))
        self.page(0).checkRAR.setChecked(forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'Export131RAR', 'False')))
        self.page(0).checkXML.setChecked(forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'Export131XML', 'False')))
        self.page(0).chkUseDefaultAnalysisValue.setChecked(forceBool(getVal(
            QtGui.qApp.preferences.appPrefs, 'Export131UseDefaultAnalysisValue', 'False')))

    def exec_(self):
        global EventTypes
        QtGui.QWizard.exec_(self)
        EventTypes_str=', '.join([str(x) for x in EventTypes])
        QtGui.qApp.preferences.appPrefs['EventTypes'] = toVariant(EventTypes_str)
        QtGui.qApp.preferences.appPrefs['Export131Finished'] = toVariant(self.page(0).checkFinished.isChecked())
        QtGui.qApp.preferences.appPrefs['Export131Payed'] = toVariant(self.page(0).checkPayed.isChecked())
        QtGui.qApp.preferences.appPrefs['Export131RAR'] = toVariant(self.page(0).checkRAR.isChecked())
        QtGui.qApp.preferences.appPrefs['Export131XML'] = toVariant(self.page(0).checkXML.isChecked())
        QtGui.qApp.preferences.appPrefs['Export131UseDefaultAnalysisValue'] = \
            toVariant(self.page(0).chkUseDefaultAnalysisValue.isChecked())
        QtGui.qApp.preferences.appPrefs['Export131begDate'] = toVariant(self.date1)
        QtGui.qApp.preferences.appPrefs['Export131endDate'] = toVariant(self.date2)
        shutil.rmtree(self.tmp_dir)


def get_other_act(event_id, dop):
    dp=' and ActionType.id not in ('+', '.join([str(d[1]) for d in dop])+')'
    stmt='''
select
    ActionType.name, Action.begDate, Action.endDate, Action.id
from
    Action
    join ActionType on ActionType.id=Action.actionType_id
where Action.event_id='''+str(event_id)+dp
    query=QtGui.qApp.db.query(stmt)
    acts=[]
    while query.next():
        acts.append(query.record())
    return acts

save_dir=''
EventTypes=[]

class C131Report(CReportViewDialog):
    def __init__(self, parent, fname, fsize, md5, n, date1, date2,
#    lpu_name, lpu_INN, lpu_KPP, lpu_FSS, lpu_OGRN, recipient_name, payer_name, payer_INN, payer_KPP, payer_FSS, payer_OGRN
    ):
        CReportViewDialog.__init__(self, parent)
        self.fname=fname
        self.fsize=fsize
        self.md5=md5
        self.n=n
        self.date1=date1
        self.date2=date2
#        self.lpu_name=lpu_name
#        self.lpu_INN=lpu_INN
#        self.lpu_KPP=lpu_KPP
#        self.lpu_FSS=lpu_FSS
#        self.lpu_OGRN=lpu_OGRN
#        self.recipient_name=recipient_name
#        self.payer_name=payer_name
#        self.payer_INN=payer_INN
#        self.payer_KPP=payer_KPP
#        self.payer_FSS=payer_FSS
#        self.payer_OGRN=payer_OGRN
#        self.setTitle(u'Акт приёма-передачи', u'')
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
            object = self.build()
        finally:
            QtGui.qApp.restoreOverrideCursor()
        self.setWindowTitle(u'Акт приёма-передачи')
        self.setText(object)

    def build(self):
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        text0=u'''Акт приёма-передачи
файла со сведениями о результатах дополнительной диспансеризации
'''

        cursor.setCharFormat(CReportBase.ReportBody)
#        text0+=u'\n\nк реестру счёта '+self.account_num+u' от '+self.accountDate.toString('dd.MM.yyyy')+'\n\n'
        text0+=u'\nза период с '+self.date1.toString('dd.MM.yyyy')+u' по '+self.date2.toString('dd.MM.yyyy')+u', содержащего '+str(self.n)+u' записей\n'
#        text0+=u'получатель: '+self.recipient_name+'\n'
#        text0+=u'исполнитель: '+self.lpu_name+u' (ИНН '+self.lpu_INN+u', КПП '+self.lpu_KPP+u', ФСС '+self.lpu_FSS+u', ОГРН '+self.lpu_OGRN+u')\n'
#        text0+=u'плательщик: '+self.payer_name+u' (ИНН '+self.payer_INN+u', КПП '+self.payer_KPP+u', ФСС '+self.payer_FSS+u', ОГРН '+self.payer_OGRN+u')\n\n'

        cursor.insertText(text0)
        cursor.insertBlock()

        tableColumns = [
            ('20%', [u'Имя файла'], CReportBase.AlignLeft),
            ('10%', [u'Размер файла (байт)'], CReportBase.AlignLeft),
            ('20%', [u'Контрольная сумма'], CReportBase.AlignLeft),
            ('20%', [u'Дата создания'], CReportBase.AlignRight),
            ('10%', [u'Количество записей'], CReportBase.AlignRight),
            ('20%', [u'Количество записей, прошедших логический контроль'], CReportBase.AlignRight),
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
        text1=''

        my_org_id=QtGui.qApp.currentOrgId()
        org_info=getOrganisationInfo(my_org_id)
        if org_info:
            text1+=u'\n\nЛПУ: '+org_info['shortName']+u' (ИНН '+org_info['INN']+u', КПП '+org_info['KPP']+u', ОГРН '+org_info['OGRN']+u')\n'

#        text1+=u'''\n\n\n
#           от исполнителя                                          от плательщика
#
#
#   _____________________________________              ________________________________________
#    (должность, подпись) расшифровка                 (должность, подпись) расшифровка
#
#          '__'____________200_г.                                       '__'____________200_г.
#         '''
        cursor.insertText(text1)

        return doc.toHtml(QByteArray('utf-8'))


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, OGRN):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._OGRN = OGRN
        self.db = QtGui.qApp.db
        self.documentTypeTable = self.db.table('rbDocumentType')
        self.tableAction = tbl('Action')
        self.nameSpace = u'http://schemas.microsoft.com/office/infopath/2003/myXSD/2009-03-30T08:53:35'
        self.ddEventTypeIdList = self.getDDEventTypeIdList()


    def writeTextElement(self, elementName, val, len=None):
        if val is None:
            text = ''
        elif not isinstance(val, basestring):
            text = unicode(val)
        else:
            text = val
        if len:
            text = text[:len]
        QXmlStreamWriter.writeTextElement(self, self.nameSpace, elementName, text)


    def createQuery(self):
        global EventTypes
        stmt = '''
            SELECT  Event.client_id,
                        Event.id AS eventId,
                        Event.eventType_id,
                        Event.prevEventDate,
                        Contract.number AS dog_number,
                        Contract.date AS dog_date,
                        Contract.resolution AS resolution
            FROM         Event
            LEFT JOIN   Contract ON Contract.id = Event.contract_id
            WHERE       Event.org_id = %d
            AND           Event.deleted = 0
            ''' % (QtGui.qApp.currentOrgId())

        date1=forceString(self.parent.dateEdit_1.date().toString('yyyy-MM-dd'))
        date2=forceString(self.parent.dateEdit_2.date().toString('yyyy-MM-dd'))
        self.parent.parent.date1=self.parent.dateEdit_1.date()
        self.parent.parent.date2=self.parent.dateEdit_2.date()
        stmt += ' and (Event.execDate between "'+date1+'" and "'+date2+'")'

        if self.parent.checkFinished.isChecked():
            stmt += ' and Event.execDate is not null'

        EventTypes = self.parent.tblEventType.values()

        if EventTypes:
            stmt += ' and Event.eventType_id in ('+', '.join([str(et) for et in EventTypes])+')'

        if self.parent.checkPayed.isChecked():
            stmt += ' and isEventPayed(Event.id)'

        query = self.db.query(stmt)
        query.setForwardOnly(True)
        return query

# *****************************************************************************************

    cacheOwnershipCode = {}

    def getOrgOwnershipCode(self,  orgId):
        result = self.cacheOwnershipCode.get(orgId)

        if (not result) and orgId:
            stmt = """
            SELECT rbOKFS.ownership
            FROM Organisation
            LEFT JOIN rbOKFS ON rbOKFS.id = Organisation.OKFS_id
            WHERE Organisation.id = '%d'
            """ % orgId
            query = self.db.query(stmt)
            while query.next():
                record = query.record()

                if record:
                    result = forceInt(record.value(0))
                    self.cacheOwnershipCode[orgId] = result
                    break

        return result

# *****************************************************************************************

    def getDDEventTypeIdList(self):
        table = tbl('EventType')
        return self.db.getIdList(table, where=self.db.joinOr([table['name'].like(u'...ДД...'),
                                                             table['name'].like(u'Доп.диспансеризация')]))

# *****************************************************************************************

    def getSpecs(self,  sex):
        global EventTypes

        if sex not in [1, u'м', u'М']:
            POL_spec1, POL_spec2 = [('A', '02', 3)], []
        else:
            POL_spec1, POL_spec2 = [], []

        specList = [('T', '78', 5)] + POL_spec1 + [('N', '40', 3), \
                        ('H', '89', 3)] + POL_spec2 + [('O', '49', 3)]

        dd2009Id = forceRef(self.db.translate('EventType', 'code','40', 'id'))
        dd2010Id = forceRef(self.db.translate('EventType', 'code','49', 'id'))

        if (dd2009Id and (dd2009Id in EventTypes)) or \
            (dd2010Id and (dd2010Id in EventTypes)):
            # в ДД2009,2010 вместо терапевта может быть врач общей практики.
            specList.insert(0, ('T', '44', 5))
            specList.insert(0, ('T', '45', 5))

        return specList


    def getAnalysis(self, analysisTypes):
        analysis = []

        for (name, code, groupId,  values,  template,  resultLen) in analysisTypes:
            rec = self.db.getRecordEx('ActionType', 'id',
                'code=\'%s\' and group_id=%d' % (code, groupId))
            if rec:
                id = forceRef(rec.value(0))
                if id:
                    analysis.append((name, id, values,  template,  resultLen))

        return analysis


    def getActionPropertyList(self, actionId,  typeNameList):
        result = []
        stmt = u'''
        SELECT  A.id AS id,
                    AP.typeName AS typeName,
                    AP.name AS name,
                    A.type_id AS typeId,
                    U.name AS unitName,
                    A.evaluation AS evaluation
        FROM    ActionProperty A
        LEFT JOIN ActionPropertyType AP ON A.type_id = AP.id
        LEFT JOIN rbUnit U ON A.unit_id = U.id
        WHERE A.action_id = %d AND A.deleted = 0
        ''' % actionId

        if typeNameList and typeNameList != []:
            stmt += u' AND AP.name IN (' + \
                    ', '.join(['\''+t+'\'' for t in typeNameList])+')'

        query = self.db.query(stmt)

        while query.next():
            result.append(query.record())

        return result


    def getActionPropertyResultStr(self, actionId, nameList, template,
                                        equivalentPropertyNameList,  showNames = False):
        valueDict = {}
        unitDict = {}

        recordList = self.getActionPropertyList(actionId, nameList)

        if recordList:
            for record in recordList:
                id = forceRef(record.value('id'))
                typeId = forceRef(record.value('typeId'))
                typeName = forceString(record.value('typeName'))
                name = forceString(record.value('name'))
                evaluation = forceString(record.value('evaluation'))

                if typeId and name and typeName:
                    val = getActionPropertyValue(id, typeName)
                    if val:
                        valueDict[name] = val
                    elif evaluation:
                        valueDict[name] = u'норма' if evaluation == '0' else u'патология'
                    else:
                        valueDict[name] = ''
                    unitDict[name] = forceString(record.value('unitName'))

        if template:
            # заменяем ненайденные поля их эквивалентами.
            for x in nameList:
                if equivalentPropertyNameList.has_key(x) and \
                    (not valueDict.has_key(x)):
                        template = template.replace(x, equivalentPropertyNameList[x])

            # заменяем отсутствующие поля пустыми строчками
            for x in nameList:
                if (not valueDict.has_key(x)) or (not valueDict[x]):
                    valueDict[x] = ''

            return substFields(template, valueDict) if any(valueDict.itervalues()) else None
        else:
            if showNames:
                list = []
                for key, val  in valueDict.items():
                    str = u'%s: %s' % (key, val)
                    unitName = unitDict.get(key, None)
                    if unitName and val.isdigit():
                        str += u' %s' % unitName
                    list.append(str)
                return ', '.join(list)
            else:
                return ', '.join([val for val in valueDict.values()])


    def formatDate(self,  date):
        return forceDate(date).toString('dd.MM.yyyy') if date else ''


    def writeRecord(self, record,  id1,  id2):
        # По распоряжению 186-р от 01.04.09
        eventId = forceInt(record.value('eventId'))
        clientId = forceInt(record.value('client_id'))
        eventTypeId = forceRef(record.value('eventType_id'))
        client = getClientInfo(clientId)
        sexCode = client['sexCode']
        clientAddress = getClientAddress(clientId, 0)
        addressId = clientAddress.value('address_id') if clientAddress else None
        address = getAddress(addressId)
        documentRecord = getClientDocument(clientId)
        policyRecord = getClientPolicy(clientId)
        workRecord = getClientWork(clientId)
        attachRecord=getAttachRecord(clientId, 0)
        #TIP_DD = forceString(record.value('resolution'))
        KLADRCode = address.KLADRCode
        KLADRStreetCode = address.KLADRStreetCode
        DATE_ZAV = None
        DATE_DU = None
        ourClient = False

        # Тип карточки.  Может иметь значения "Р" - работающие, "Б" - бюджет, "В" - вредники.
        # Определить тип "Р"/"Б" возможно по значаению ОКФС места работы.
        # "Бюджет" - дает тип "Б", остальное тип "Р" для событий "ДД" (ДД 2010 в частности).
        # Остальные относятся к Вредникам (тип "В").
        ddType = u'V'

        if workRecord and (eventTypeId in self.ddEventTypeIdList):
            orgId = forceRef(workRecord.value('org_id'))
            ownershipCode = self.getOrgOwnershipCode(orgId)

            if ownershipCode:
                ddType = u'B' if ownershipCode == 1 else u'R'

#            if TIP_DD==u'921':
#                OKFS_id = forceInt(self.db.translate(
#                    'Organisation', 'id', orgId, 'OKFS_id'))
#                if OKFS_id not in [7, 9, 15]:
#                    TIP_DD=u'921Б'

        attachCode = 2

        if attachRecord and attachRecord['LPU_id'] == QtGui.qApp.currentOrgId():
            if attachRecord['code'] in ['1', '2']:
                attachCode = 1

            ourClient =  True
            # 'Свои' клиенты
            # имеют постоянное прикрепление к базовому ЛПУ т.е. ЛПУ по месту
            # прикрепления совпадает с ЛПУ проведения ДД
        else:
            tmpAttachRecord=getAttachRecord(clientId, 1)
            if tmpAttachRecord and tmpAttachRecord['LPU_id'] == QtGui.qApp.currentOrgId():
                tmpAttachCode = tmpAttachRecord['code']
                if tmpAttachCode == '5':
                    attachCode = 2
                elif tmpAttachCode == '3':
                    attachCode = 3
                elif tmpAttachCode == '4':
                    attachCode = 4

        self.writeStartElement('patient')
        self.writeStartElement('General')
        self.writeTextElement('OGRN', self._OGRN,  15)
        self.writeTextElement('ID', forceString(eventId), 25)
        self.writeTextElement('PROG', u'САМСОН-ВИСТА', 15)
        self.writeTextElement('TIP_DD', ddType, 5)

        if documentRecord:
            serial = forceString(documentRecord.value('serial'))
            number = forceString(documentRecord.value('number'))
            self.writeTextElement('PASSPORT', serial+' '+number)
        else:
            self.writeTextElement('PASSPORT', '')

        self.writeTextElement('FAM', client['lastName'], 40)
        self.writeTextElement('IM', client['firstName'], 40)
        self.writeTextElement('OT', client['patrName'], 40)
        self.writeTextElement('POL', forceString(sexCode), 1)
        self.writeTextElement('DR', forceString(self.formatDate(client['birthDate'])), 10)

        if KLADRCode:
            socr = forceString(self.db.translate('kladr.KLADR', 'CODE', KLADRCode, 'SOCR', idFieldName='CODE'))
            self.writeTextElement('ADRES_TYPE', '1' if socr==u'г' else '2', 1)
            self.writeTextElement('NAS_P', getCityName(KLADRCode), 70)
        else:
            self.writeTextElement('ADRES_TYPE', '1', 1)
            self.writeTextElement('NAS_P', '')

        if KLADRStreetCode:
            self.writeTextElement('UL', getStreetName(KLADRStreetCode), 70)
        else:
            self.writeTextElement('UL', u'населенный пункт улиц не имеет', 70)

        self.writeTextElement('DOM', address.number, 7)
        self.writeTextElement('KOR', address.corpus, 5)
        self.writeTextElement('KV', address.flat, 5)

        if policyRecord:
            insurerId = policyRecord.value('insurer_id')
            self.writeTextElement('SMO_NAME', getOrganisationShortName(forceRef(insurerId)), 70)
            SMO = forceString(self.db.translate('Organisation', 'id', insurerId, 'infisCode'))
            self.writeTextElement('SMO', SMO, 5)
            serial = forceString(policyRecord.value('serial'))
            number = forceString(policyRecord.value('number'))
            self.writeTextElement('SN_POLIS', serial+' '+number, 35)
        else:
            self.writeTextElement('SMO_NAME', '')
            self.writeTextElement('SMO', '')
            self.writeTextElement('SN_POLIS','')


        self.writeTextElement('SNILS', formatSNILS(client['SNILS']), 14)

        if workRecord:
            workInfo = getOrganisationInfo(orgId)
            self.writeTextElement('RABOTA', getOrganisationShortName(orgId), 70)
            self.writeTextElement('DOLGN', forceString(workRecord.value('post')), 30)
        else:
            self.writeTextElement('RABOTA', '')
            self.writeTextElement('DOLGN', '')

        self.writeTextElement('N_MK', str(clientId), 20)

        if workRecord:
            hurt, stage, factors = getWorkHurt(forceRef(workRecord.value('id')))
            strHurt = forceString(hurt)
            strStage = forceString(stage)
            self.writeTextElement('WORKV', strHurt if strHurt else '0', 10)
            self.writeTextElement('WORKS', strStage if strStage else '0', 2)
            strFactors = forceString(factors)
            self.writeTextElement('FAKTOR', strFactors if strFactors != '' else '', 10)
        else:
            self.writeTextElement('WORKV', '0', 10)
            self.writeTextElement('WORKS', '0', 2)
            self.writeTextElement('FAKTOR', '', 10)


        self.writeTextElement('PDATE', forceString(self.formatDate(record.value('prevEventDate'))), 10)
        self.writeTextElement('PRIK', forceString(attachCode), 1)

        lpuShortName = ''
        lpuOGRN = ''
        if attachRecord:
            LPU_id = attachRecord['LPU_id']
            if LPU_id:
                LPU_info = getOrganisationInfo(LPU_id)
                if LPU_info:
                    lpuShortName = LPU_info['shortName']
                    lpuOGRN = LPU_info['OGRN']

        self.writeTextElement('P_LPY_NAME', lpuShortName, 50)
        self.writeTextElement('P_LPY_OGRN', lpuOGRN, 15)
        self.writeEndElement() # General

        specs = self.getSpecs(sexCode)

        specTagNames = {'T':'Therapeutist', 'A':'Gynaecologist', \
                                'N':'Neurologist', 'H':'Surgeon', \
                                'O':'Ophthalmologist'}
        specDiagNum = { 'T':5,  'A':3,  'N':3,  'H':3, 'O':3}
        strDiags = {}
        for x in specTagNames.keys():
            strDiags[x+'tag'] = specTagNames[x]
            strDiags[x+'_NAME'] = ''
            strDiags[x+'_DO'] = ''
            strDiags[x+'_SL'] = ''
            for i in range(1, specDiagNum[x]+1):
                strDiags[x+'_MKB_'+str(i)] = ''
                strDiags[x+'_V_'+str(i)] = ''
                strDiags[x+'_ST_'+str(i)] = ''
                strDiags[x+'_GZ_'+str(i)] = ''

        for (spec, speciality, diagNum) in specs:
            diags = getDiags(eventId, speciality)
            maxDiagNum = diagNum
            diagNum = min(diagNum, len(diags))
            san = 2

            if diags:
                lastName = forceString(diags[0].value('lastName') if diags and diags[0] else '')
                firstName = forceString(diags[0].value('firstName') if diags and diags[0] else '')
                patrName = forceString(diags[0].value('patrName') if diags and diags[0] else '')
                strDiags[spec+'_NAME'] = lastName+' '+firstName+' '+patrName

                for iDiag in range(1, diagNum+1):
                    diag = diags[iDiag-1]
                    #self.writeTextElement(spec+'_KOD', forceString(diag.value('code')))
                    endDate = diag.value('endDate')

                    if endDate and not DATE_ZAV:
                        DATE_ZAV = max(DATE_ZAV, endDate)

                    if ourClient:
                        # Дата взятия на Дисп.Учет. может быть определена для 'своих' пациентов
                        # это максимальная дата из основных диагностиков имеющих в поле
                        # ДН (дисп.наблюдение) код 2 - взят на дисп.учет
                        dispancerCode = forceInt(diag.value('dispancer_code'))

                        if dispancerCode and dispancerCode == 2:
                            DATE_DU = max(DATE_DU,  endDate)

                    strDiags[spec+'_DO'] = forceString(self.formatDate(endDate))
                    sanatorium = forceInt(diag.value('sanatorium'))

                    if sanatorium in [1, 2]:
                        san=1

                    strDiags[spec+'_MKB_'+str(iDiag)] = forceString(diag.value('MKB'))
                    character_id = forceInt(diag.value('character_id'))
                    strDiags[spec+'_V_'+str(iDiag)] = forceString(1 if character_id<=2 else 2)
                    stage_id = forceInt(diag.value('stage_id'))
                    strDiags[spec+'_ST_'+str(iDiag)] = forceString(3 if stage_id==1 else 4)
                    strDiags[spec+'_GZ_'+str(iDiag)] = forceString(diag.value('healthGroup_id'))

                strDiags[spec+'_SL'] =  forceString(san)

        for x in ('T','A', 'N', 'H', 'O'):
            self.writeStartElement(strDiags[x+'tag'])
            self.writeTextElement(x+'_NAME',  strDiags[x+'_NAME'], 70)
            self.writeTextElement(x+'_DO', strDiags[x+'_DO'], 10)
            for i in range(1, specDiagNum[x]+1):
                self.writeTextElement(x+'_MKB_'+str(i),  strDiags[x+'_MKB_'+str(i)], 7)
                self.writeTextElement(x+'_V_'+str(i),  strDiags[x+'_V_'+str(i)], 1)
                self.writeTextElement(x+'_ST_'+str(i),  strDiags[x+'_ST_'+str(i)], 1)
                self.writeTextElement(x+'_GZ_'+str(i),  strDiags[x+'_GZ_'+str(i)], 1)
            self.writeTextElement(x+ '_SL',  strDiags[x+'_SL'], 1)
            self.writeEndElement()

        ds=0
        otherDiags = getOtherDiags(eventId, specs)

        self.writeStartElement('Specialist')
        specDiags = {}

        for i in range(1, 3+1):
            specDiags['NAME_'+str(i)] = ''
            specDiags['SPEC_'+str(i)] = ''
            specDiags['DO_'+str(i)] = ''
            specDiags['S_'+str(i)+'_MKB_1'] = ''
            specDiags['S_'+str(i)+'_V_1'] = ''
            specDiags['S_'+str(i)+'_ST_1'] = ''
            specDiags['S_'+str(i)+'_GZ_1'] = ''
            specDiags['SL_'+str(i)] = ''

        if otherDiags:
            for otherDiag in otherDiags:
                ds += 1

                if ds > 3:
                    break

                dss = str(ds)
                lastName = forceString(otherDiag.value('lastName'))
                firstName = forceString(otherDiag.value('firstName'))
                patrName = forceString(otherDiag.value('patrName'))
                specDiags['NAME_'+dss ] = lastName+' '+firstName+' '+patrName

                spec_code = forceString(otherDiag.value('spec_code'))
                OKSOCode = forceString(otherDiag.value('OKSOCode'))
                spec_name = forceString(otherDiag.value('spec_name'))
                specDiags['SPEC_'+dss] = '['+OKSOCode+']'+spec_name
                specDiags['DO_'+dss]= forceString(self.formatDate(otherDiag.value('endDate')))
                specDiags['S_'+dss+'_MKB_1'] = forceString(otherDiag.value('MKB'))

                character_id = forceInt(otherDiag.value('character_id'))
                specDiags['S_'+dss+'_V_1']= forceString(1 if character_id<=2 else 2)
                stage_id = forceInt(otherDiag.value('stage_id'))
                specDiags['S_'+dss+'_ST_1'] = forceString(3 if stage_id==1 else 4)
                specDiags['S_'+dss+'_GZ_1'] = forceString(otherDiag.value('healthGroup_id'))

                sanatorium = forceInt(otherDiag.value('sanatorium'))
                specDiags['SL_' + dss] = forceString(1 if sanatorium in [1, 2] else 2)

        for i in range(1, 3+1):
            self.writeTextElement('NAME_'+str(i),  specDiags['NAME_'+str(i)],  70)
            self.writeTextElement('SPEC_'+str(i),  specDiags['SPEC_'+str(i)],  20)
            self.writeTextElement('DO_'+str(i),  specDiags['DO_'+str(i)] , 10)
            self.writeTextElement('S_'+str(i)+'_MKB_1', specDiags['S_'+str(i)+'_MKB_1'],  7)
            self.writeTextElement('S_'+str(i)+'_V_1', specDiags['S_'+str(i)+'_V_1'] , 1)
            self.writeTextElement('S_'+str(i)+'_ST_1',  specDiags['S_'+str(i)+'_ST_1'] , 1)
            self.writeTextElement('S_'+str(i)+'_GZ_1',  specDiags['S_'+str(i)+'_GZ_1'] , 1)
            self.writeTextElement('SL_'+str(i),  specDiags['SL_'+str(i)], 1)

        self.writeEndElement() # Specialist

        analysisTypes = [
            # name, code, group_id, [property_name, .. ], template
            ('KAK', '03', id1,                    # Клинический анализ крови
                [u'Число эритроцитов', u'Гемоглобин',
                 u'Скорость оседания (СОЭ)',  u'Число лейкоцитов',
                 u'Палочкоядерные нейтрофилы', u'Сегментоядерные нейтрофилы',
                 u'Эозинофилы', u'Базофилы',  u'Лимфоциты',
                 u'Миелоциты', u'Метамиелоциты', u'Моноциты'],
                u'{Число эритроцитов}, {Гемоглобин}, {Скорость оседания (СОЭ)}, {Число лейкоцитов} ( {Палочкоядерные нейтрофилы}/{Сегментоядерные нейтрофилы}, {Эозинофилы}, {Базофилы}, {Лимфоциты}, {Миелоциты}/{Метамиелоциты}/{Моноциты} )',  50),
            ('OB', '30', id1,  [],  u'', 15),       # Общий белок крови
            ('H', '01', id1,  [],  u'', 15),         # Холестерин
            ('L', '05', id1,  [],  u'', 15),         # Холестерин липопротеидов низкой плотности
            ('T', '06', id1,  [],  u'', 15),        # Триглицериды
            ('KR', '31', id1,  [],  u'', 15),       # Креатинин крови
            ('MK', '32', id1,  [],  u'', 15),       # Мочевая кислота
            ('BN', '33', id1,  [],  u'', 15),       # Билирубин крови
            ('AM', '34', id1,  [],  u'', 15),       # Амилаза крови
            ('G', '02', id1,  [u'Глюкоза'],  u'{Глюкоза}', 15),         # Сахар крови
            ('KAM', '04', id1,                    # Клинический анализ мочи
                [u'Относительная плотность', u'Удельный вес',
                 u'Лейкоциты', u'Число лейкоцитов',  u'pH',
                 u'Число эритроцитов', u'Осадок',
                 u'Неизмененные эритроциты',  u'Измененные эритроциты'],
                u'{Удельный вес}, {pH}, {Лейкоциты}, {Число эритроцитов}, {Осадок}', 80),
            ('O_CA', '07', id1,  [],  u'', 15),     # Онкомаркер специфический CA-125
            ('O_PSI', '08', id1,  [],  u'', 15),   # Онкомаркер специфический PSI
            #('EKG', '07', id2,  [u'р-т'],  u'{р-т}', 100),      # ЭКГ
            #('F', '06', id2,  [u'флюорография р-т'],  u'{флюорография р-т}', 100),         # Флюорография
            ('EKG', '07', id2,  [],  u'', 100),      # ЭКГ
            ('F', '06', id2,  [],  u'', 100),         # Флюорография
            ('M', '05', id2,  [],  u'', 100),         # Маммография
            ('MC', '35', id1,  [],  u'', 50),         # Цитологическое исследование мазка из цервикального канала
            ('UPROST', '09', id2,  [],  u'', 100)]  # УЗИ предстательной железы

        # словарь эквивалентных значений свойств. заменяются в шаблоне, если значение свойства
        # с именем из ключа словаря пустое =)
        equivalentPropertyNameList = {'KAM': \
            {  u'Лейкоциты' :  u'Число лейкоцитов',
                u'Удельный вес' :  u'Относительная плотность',
                u'Число эритроцитов' :  u'Неизмененные эритроциты}/{Измененные эритроциты' }
        }

        analysis = self.getAnalysis(analysisTypes)
        strAnalysis = {}
        allAnalysisAreBlank = True

        for (name, actionTypeId,  id,  values,  template,  resultLen) in analysisTypes:
            for x in ('DI', 'DP', 'R'):
                strAnalysis[name+'_'+ x] = ''

        if analysis and analysis != []:

            for (name, actionTypeId,  values,  template,  resultLen) in analysis:
                cond = []
                cond.append(self.tableAction['event_id'].eq(eventId))
                cond.append(self.tableAction['actionType_id'].eq(actionTypeId))
                action = self.db.getRecordEx(self.tableAction, 'id, begDate, endDate', cond)
                if action:
                    strAnalysis[name+'_DI'] = forceString(self.formatDate(action.value('begDate')))
                    strAnalysis[name+'_DP'] = forceString(self.formatDate(action.value('endDate')))
                    actionId = forceRef(action.value('id'))
                    equivProp = equivalentPropertyNameList.get(name, {})
                    resultStr = self.getActionPropertyResultStr(actionId, values,  template, equivProp)
                    strAnalysis[name+'_R'] = resultStr  # Результат.

                    if ((not resultStr) or resultStr == '')  \
                            and self.parent.chkUseDefaultAnalysisValue.isChecked() and \
                            strAnalysis.get(name+'_DI', '') != '' and \
                            strAnalysis.get(name+'_DP', '') != '':
                        strAnalysis[name+'_R'] = u'норма'

        dn=0
        addTests = get_other_act(eventId, analysis)
        strAddTest = {}
        for i in range(1, 2+1):
            sI = str(i)
            strAddTest['DOP_'+sI+'_NAME'] = ''
            strAddTest['DI_'+sI] = ''
            strAddTest['DP_'+sI] = ''
            strAddTest['DOP_'+sI+'R'] = ''

        if addTests and addTests != []:
            for otherAct in addTests:
                dn+=1
                if dn>2: break
                dns=str(dn)
                strAddTest['DOP_'+dns+'_NAME'] = forceString(otherAct.value('name'))
                strAddTest['DI_'+dns] =  forceString(self.formatDate(otherAct.value('begDate')))
                strAddTest['DP_'+dns] = forceString(self.formatDate(otherAct.value('endDate')))
                actionId = forceRef(otherAct.value('id'))
                resultStr = self.getActionPropertyResultStr(actionId, [],  '', {},  True)
                strAddTest['DOP_'+dns+'R'] = resultStr

                if ((not resultStr) or resultStr == '') \
                        and self.parent.chkUseDefaultAnalysisValue.isChecked() and \
                        strAddTest.get('DI_'+dns, '') != '' and \
                        strAddTest.get('DP_'+dns, '') != '':
                    strAddTest['DOP_'+dns+'R'] = u'норма'

        self.writeStartElement('Analysis')
        for (name, actionTypeId,  id,  values,  template,  resultLen) in analysisTypes:
            # заполнять пустые DI, значением DP.
            if not strAnalysis[name+'_DI']:
                strAnalysis[name+'_DI'] = strAnalysis[name+'_DP']

            self.writeTextElement(name+'_DI', strAnalysis[name+'_DI'],  10)
            self.writeTextElement(name+'_DP', strAnalysis[name+'_DP'],  10)
            self.writeTextElement(name+'_R',strAnalysis[name+'_R'],  resultLen)
        self.writeEndElement() # Analysis

        self.writeStartElement('AddTest')
        for i in range(1, 2+1):
            sI = str(i)

            if not strAddTest['DI_'+sI]:
                # заполнять пустые DI, значением DP.
                strAddTest['DI_'+sI] = strAddTest['DP_'+sI]

            self.writeTextElement('DOP_'+sI+'_NAME',  strAddTest['DOP_'+sI+'_NAME'],  200)
            self.writeTextElement('DI_'+sI,  strAddTest['DI_'+sI], 10)
            self.writeTextElement('DP_'+sI,  strAddTest['DP_'+sI], 10 )
            self.writeTextElement('DOP_'+sI+'R',  strAddTest['DOP_'+sI+'R'],  100)
        self.writeEndElement() # AddTest

        self.writeStartElement('Conclusion')
        # Дата взятия пациента  на  диспансерный  учет. (заполняется в конце года в поликлинике по месту жительства)
        self.writeTextElement('DATE_DU', forceString(self.formatDate(DATE_DU)), 10)
        # Дата осмотра, проведенного через 6 месяцев после взятия на диспансерный учет
        self.writeTextElement('DATE_OSM_6', '', 10)
        # Диагноз (код по МКБ-10) через 6 месяцев после взятия на диспансерный учет.
        # Указываются  все диагнозы, имеющиеся у пациента, через  разделитель запятая
        self.writeTextElement('DZ_MKB_6', '', 70)
        # Пациент снят с  диспансерного  наблюдения  по причине:
        # 1 – выздоровление;
        # 2 -  выбыл;
        # 3 -  умер;
        # 4 -  умер в течение 6 мес. после  диспансеризации
        self.writeTextElement('S_DN', '', 1)
        # Причина смерти (указать код диагноза по  МКБ-10).
        self.writeTextElement('PS', '', 70)
        # Дата завершения дополнительной  диспансеризации
        self.writeTextElement('DATE_ZAV', forceString(self.formatDate(DATE_ZAV)), 10)
        # Дата оплаты счета за дополнительную диспансеризацию ТФОМС либо СПб РО ФСС  РФ.
        # Если  день оплаты неизвестен - указывается последний день месяца, в котором  произведена оплата
        self.writeTextElement('DATE_OPLAT', '', 10)
        # Дата отказа в оплате счета,  выставленного  в ТФОМС (по форме РД-1) либо СПб РО ФСС  РФ.
        # Если  день отказа неизвестен - указывается последний день месяца, в  котором произведен отказ
        self.writeTextElement('DATE_OTKAZ', '', 10)
        self.writeEndElement() # Conclusion
        self.writeEndElement() # patient

    def writeStartElement(self, str):
        return QXmlStreamWriter.writeStartElement(self,  self.nameSpace, str)

    def writeFile(self,  device,  progressBar):
        try:
            progressBar.setText(u'Запрос событий по выбранному интервалу')
            query = self.createQuery()
            self.setDevice(device)
            progressBar.setMaximum(max(query.size(), 1))
            progressBar.reset()
            progressBar.setValue(0)

            self.writeStartDocument()
            #self.writeDTD('<!DOCTYPE xEventType>')
            self.writeNamespace('http://www.w3.org/2001/XMLSchema-instance',  'xsi')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003/dataFormSolution' ,  'dfs')
            self.writeNamespace('http://tempuri.org/',  'tns')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003/changeTracking',  '_xdns0')
            self.writeNamespace('http://schemas.xmlsoap.org/soap/envelope/',  'soap')
            self.writeNamespace('urn:schemas-microsoft-com:xml-diffgram-v1',  'diffgr')
            self.writeNamespace('urn:schemas-microsoft-com:xml-msdata',  'msdata')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/http/',  'http')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/soap12/',  'soap12')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/mime/',  'mime')
            self.writeNamespace('http://schemas.xmlsoap.org/soap/encoding/',  'soapenc')
            self.writeNamespace('http://microsoft.com/wsdl/mime/textMatching/',  'tm')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/soap/',  'ns1')
            self.writeNamespace('http://schemas.xmlsoap.org/wsdl/',  'wsdl')
            self.writeNamespace(self.nameSpace,  'my')
            self.writeNamespace('http://schemas.microsoft.com/office/infopath/2003',  'xd')
            self.writeStartElement(u'моиПоля')
            self.writeAttribute(u'xml:lang', 'ru')
            n = 0
            s = query.size()
            self.parent.parent.rec_num = s
            r1 = self.db.getRecordEx('ActionType', 'id', 'code=\'1-1\' and class=1')
            id1 = forceInt(r1.value(0)) # id лабораторных исследований
            r2 = self.db.getRecordEx('ActionType', 'id', 'code=\'1-2\' and class=1')
            id2 = forceInt(r2.value(0)) # id лучевой диагностики

            while (query.next()):
                QtGui.qApp.processEvents()

                if self.parent.abort:
                    return False

                self.writeRecord(query.record(),  id1,  id2)
                progressBar.step()
                n += 1

            self.writeEndDocument()
            self.parent.parent.n=n

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


def isNumber(n):
    try:
        int(n);
        return True
    except ValueError: pass
