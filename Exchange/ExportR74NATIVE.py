# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil

from library.dbfpy.dbf import *
from library.Utils     import *

from Ui_ExportR74NATIVEPage1 import Ui_ExportR74NATIVEPage1
from Ui_ExportR74NATIVEPage2 import Ui_ExportR74NATIVEPage2


def getAccountInfo(accountId):
    db = QtGui.qApp.db
    accountRecord = db.getRecord('Account', 'date, number, settleDate', accountId)
    if accountRecord:
        date = forceDate(accountRecord.value('date'))
        number = forceString(accountRecord.value('number'))
        settleDate = forceDate(accountRecord.value('settleDate'))
    else:
        date = None
        number = ''
        settleDate = None
    return date, number, settleDate, 'native'

def lastDayOfMonth(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

def exportR74NATIVE(widget, accountId, accountItemIdList):
    wizard = CExportR74NATIVEWizard(widget)
    wizard.setAccountId(accountId)
    wizard.setAccountItemsIdList(accountItemIdList)
    wizard.exec_()


class CExportR74NATIVEWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportR74NATIVEPage1(self)
        self.page2 = CExportR74NATIVEPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта в native')
        self.dbfFileName = ''
        self.tmpDir = ''


    def setAccountId(self, accountId):
        self.accountId = accountId
        date, number, settleDate, fileName = getAccountInfo(accountId)
        self.dbfFileName = fileName
        strNumber = number if trim(number) else u'б/н'
        strDate = forceString(date) if date.isValid() else u'б/д'
        self.page1.setTitle(u'Экспорт данных реестра по счёту №%s от %s' %(strNumber, strDate))
        self.page2.setTitle(u'Укажите директорию для сохранения обменного файла "%s.dbf"' %(self.dbfFileName))
        self.page1.accNumber = number
        self.page1.accDate = pyDate(date)
        self.page1.settleDate = pyDate(settleDate)
        self.page1.accountId = accountId


    def setAccountExposeDate(self):
        db = QtGui.qApp.db
        accountRecord = db.table('Account').newRecord(['id', 'exposeDate'])
        accountRecord.setValue('id', toVariant(self.accountId))
        accountRecord.setValue('exposeDate', toVariant(QDate.currentDate()))
        db.updateRecord('Account', accountRecord)


    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('native')
        return self.tmpDir


    def getFullDbfFileName(self):
        return os.path.join(self.getTmpDir(), self.dbfFileName + '.dbf')


    def setAccountItemsIdList(self, accountItemIdList):
        self.page1.setAccountItemsIdList(accountItemIdList)


    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportR74NATIVEPage1(QtGui.QWizardPage, Ui_ExportR74NATIVEPage1):
    mapDocTypeToINFIS = { '1' : '1', '14': '2', '3':'3', '2':'6', '5':'7', '6':'8', '16':'8' }
    mapDocTypeToINFISName = {'1':u'РФ паспорт', '14':u'паспорт', None:u'др.док-т удост.личн.'}
    mapPolicyTypeToINFIS = {'1':u'т',  '2':u'п' }

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self.idList = []
        self.tariffCache = {}
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)

    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)


    def setAccountItemsIdList(self, accountItemIdList):
        self.idList = accountItemIdList


    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        query = self.createQuery()
        queryAttach = self.createQueryAttach()
        self.progressBar.setMaximum(max(query.size() + queryAttach.size(), 1))
#        self.progressBar.setMaximum(max(query.numRowsAffected() + queryAttach.numRowsAffected(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query, queryAttach


    def export(self):
        QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def exportInt(self):
        infisCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
        dbf, query, queryAttach = self.prepareToExport()
        if self.idList:
            # номер и дата счета
            dbfRecord = dbf.newRecord()
            dbfRecord['FAMILY']   = forceString(self.accNumber)
            dbfRecord['DATE']   = self.accDate #pyDate(forceDate(self.accDate))
            dbfRecord.store()
            # данные по счету
            while query.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, query.record(), infisCode, False)
            # данные по прикреплению
            while queryAttach.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                self.process(dbf, queryAttach.record(), infisCode, True)
        else:
            self.progressBar.step()
        dbf.close()


    def createDbf(self):
        dbf = Dbf(self.wizard().getFullDbfFileName(), new=True, encoding='cp866')
        dbf.addField(
                        ('NUMBER','N',8),
                        ('FAMILY','C',25),
                        ('NAME','C',25),
                        ('FATHER','C',25),
                        ('DATE','D'),
                        ('SEX','N',1),
                        ('STATUS','N',2),
                        ('CITYSTREET','C',15),
                        ('HOUSE','N',4),
                        ('IND_HOUSE','C',3),
                        ('ROOM','N',4),
                        ('IND_ROOM','C',1),
                        ('NSDOC','C',10),
                        ('SDOC','C',10),
                        ('NDOC','C',20),
                        ('TELEPHONE','N',7),
                        ('COD_LPU','N',4),
                        ('COD_SMO','N',2),
                        ('COD_SPEC','N',4),
                        ('DOCTOR','C',25),
                        ('PLACE','N',2),
                        ('PURPOSE','C',2),
                        ('UET','N',5,2),
                        ('TARIF','N',10,2),
                        ('DATE_TAR','D'),
                        ('VISIT_DATE','D'),
                        ('FIRST','N',1),
                        ('DATE_BEG','D'),
                        ('DATE_END','D'),
                        ('ISHOD','N',2),
                        ('COD_MKB','C',5),
                        ('COD_MKB1','C',5),
                        ('CHARACTER','N',2),
                        ('RESULT','N',2),
                        ('PERS_NUM','C',11),
                        ('PENS','C',1),
                        ('SPECDOLG','N',3),
                        ('SPECPNUM','C',11),
                        ('COD_HELP','N',2),
                        ('BEG_BL','D'),
                        ('END_BL','D'),
                        ('KVAL','C',1),
                        ('DELETED','N',1),
                        ('ATTACH','N',4),
                        ('DATE_ATTCH','D'),
                        ('N_ATTCH','C',7),
                        ('FSS_TRAUMA','N',1),
                    )
        return dbf

    def createQuery(self):
        db = QtGui.qApp.db
        stmt = u"""
            select
              cp.number number,
              upper(c.lastName) family,
              upper(c.firstName) `name`,
              upper(c.patrName) father,
              c.birthdate `date`,
              (case c.sex when 2 then 0 else c.sex end) sex,
              sst.code `status`,
              adh.KLADRStreetCode citystreet,
              adh.number house,
              adh.corpus ind_house,
              ad.flat room,
              null ind_room,
              cd.serial nsdoc,
              cd.number ndoc,
              null telephone,
              lpu.shortName,
              lpu.infisCode cod_lpu,
              cpi.infisCode cod_smo,
              doctorspec.name,
              doctorspec.regionalcode cod_spec,
              upper(concat(doctor.lastName, ' ', substr(doctor.firstName, 1, 1), '.', substr(doctor.patrName, 1, 1), '.')) doctor,
              place.name,
              place.code place,
              vt.name,
              vt.code purpose,
              se.infis service_infis,
              (select sum(uets.amount) from action uets where uets.event_id = e.id) uet,
              ct.price tarif,
              ct.begDate date_tar,
              cast(v.date as date) visit_date,
              case when e.isPrimary = 1 then 1 else 0 end `first`,
              cast(e.setDate as date) date_beg,
              cast(e.execDate as date) date_end,
              null ishod,
              diag.MKB cod_mkb,
              diag.MKBEx cod_mkb1,
              charac.name,
              charac.code `character`,
              res.name,
              res.regionalCode result,
              c.SNILS pers_num,
              '' pens,
              doctorpost.name,
              doctorpost.regionalCode specdolg,
              doctor.SNILS specpnum,
              null cod_help,
              inv.begDate beg_bl,
              inv.endDate end_bl,
              (case when doctorpost.name like '%%фельдшер%%' then 'Ф' else 'В' end) kval,
              cp.deleted deleted,
              cattlpu.infisCode attach,
              catt.begdate date_attch
            from account_item ai
            left join visit v on v.id = ai.visit_id
            left join rbvisittype vt on vt.id = v.visittype_id
            left join rbservice se on se.id = v.service_id
            left join rbfinance vf on vf.id = v.finance_id
            left join event e on e.id = v.event_id
            left join client c on c.id = e.client_id
            left join clientpolicy cp on cp.id = (
              select
                a.id
              from clientpolicy a
              where
                a.client_id = c.id and a.policyType_id = 1 and
                a.begDate <= v.`date`
              order by a.begDate desc
              limit 1
            )
            left join organisation cpi on cpi.id = cp.insurer_id
            left join rbsocstatustype sst on sst.id = (
              select
                sstt.id
              from clientsocstatus a
              join rbsocstatusclass ssc on ssc.id = a.socStatusClass_id
              join rbsocstatustype sstt on sstt.id = a.socStatusType_id
              where
                a.client_id = c.id and a.deleted = 0 and ssc.code = '74' and
                a.begDate <= v.`date`
              order by a.begDate desc
              limit 1
            )
            left join clientaddress ca on ca.id = (
              select
                max(a.id)
              from clientaddress a
              where
                a.client_id = c.id and a.type = 0 and a.deleted = 0
            )
            left join address ad on ad.id = ca.address_id
            left join addresshouse adh on adh.id = ad.house_id
            left join clientdocument cd on cd.id = (
              select
                max(a.id)
              from clientdocument a
              where
                a.client_id = c.id and
                a.documenttype_id = (select id from rbDocumentType where code = '1' limit 1) and
                a.deleted = 0
            )
            left join clientattach catt on catt.id = (
              select
                a.id
              from clientattach a
              where
                a.client_id = c.id and
                a.attachtype_id = (select id from rbattachtype where code = '2' limit 1) and
                a.begDate <= v.`date`
              order by a.begDate desc
              limit 1
            )
            left join organisation cattlpu on cattlpu.id = catt.lpu_id
            left join organisation lpu on lpu.id = e.org_id
            left join rbscene place on place.id = v.scene_id
            left join person doctor on doctor.id = e.execPerson_id
            left join rbspeciality doctorspec on doctorspec.id = doctor.speciality_id
            left join rbpost doctorpost on doctorpost.id = doctor.post_id
            left join eventtype et on et.id = e.eventType_id
            left join rbeventtypepurpose etp on etp.id = et.purpose_id
            left join diagnostic dia on dia.id = (
              select
                a.id
              from diagnostic a
              where
                a.event_id = e.id and a.deleted = 0
              limit 1
            )
            left join diagnosis diag on diag.id = dia.diagnosis_id
            left join rbdiseasecharacter charac on charac.id = diag.character_id
            left join rbDiagnosticResult res on res.id = dia.result_id
            -- мероприятие
            -- left join action act on act.event_id = e.id
            -- больничный
            left join tempinvalid inv on inv.id = (
              select
                a.id
              from tempinvalid a
              where
                a.client_id = c.id and a.deleted = 0 and
                v.date between a.begDate and a.endDate
              limit 1
            )
            left join contract_tariff ct on ct.id = ai.tariff_id

            where
              -- vf.name = 'ОМС' and cp.id is not null and
              ai.master_id = %i
        """ % self.accountId
        query = db.query(stmt)
        return query

    def createQueryAttach(self):
        db = QtGui.qApp.db
        firstDate = self.settleDate.replace(day=1).isoformat()
        lastDate = lastDayOfMonth(self.settleDate).isoformat()
        stmt = u"""
            select
              cp.number number,
              upper(c.lastName) family,
              upper(c.firstName) `name`,
              upper(c.patrName) father,
              c.birthdate `date`,
              (case c.sex when 2 then 0 else c.sex end) sex,
              sst.code `status`,
              adh.KLADRStreetCode citystreet,
              adh.number house,
              adh.corpus ind_house,
              ad.flat room,
              null ind_room,
              cd.serial nsdoc,
              cd.number ndoc,
              null telephone,
              cpi.infisCode cod_smo,
              cattlpu.infisCode attach,
              catt.begdate date_attch
            from client c
            left join clientpolicy cp on cp.id = (
              select
                a.id
              from clientpolicy a
              where
                a.client_id = c.id and a.policyType_id = 1 and
                date(a.begDate) <= date('%s')
              order by a.begDate desc
              limit 1
            )
            left join organisation cpi on cpi.id = cp.insurer_id
            left join rbsocstatustype sst on sst.id = (
              select
                sstt.id
              from clientsocstatus a
              join rbsocstatusclass ssc on ssc.id = a.socStatusClass_id
              join rbsocstatustype sstt on sstt.id = a.socStatusType_id
              where
                a.client_id = c.id and a.deleted = 0 and ssc.code = '74' and
                date(a.begDate) <= date('%s')
              order by a.begDate desc
              limit 1
            )
            left join clientaddress ca on ca.id = (
              select
                max(a.id)
              from clientaddress a
              where
                a.client_id = c.id and a.type = 0 and a.deleted = 0
            )
            left join address ad on ad.id = ca.address_id
            left join addresshouse adh on adh.id = ad.house_id
            left join clientdocument cd on cd.id = (
              select
                max(a.id)
              from clientdocument a
              where
                a.client_id = c.id and
                a.documenttype_id = (select id from rbDocumentType where code = '1' limit 1) and
                a.deleted = 0
            )
            left join clientattach catt on catt.client_id = c.id
            left join organisation cattlpu on cattlpu.id = catt.lpu_id
            where
              catt.attachtype_id = (select id from rbattachtype where code = '2' limit 1) and
              date(catt.begDate) between date('%s') and date('%s')
        """ % (lastDate, lastDate, firstDate, lastDate)
        stmt = u"""
            select
              cp.number number,
              upper(c.lastName) family,
              upper(c.firstName) `name`,
              upper(c.patrName) father,
              c.birthdate `date`,
              (case c.sex when 2 then 0 else c.sex end) sex,
              sst.code `status`,
              adh.KLADRStreetCode citystreet,
              adh.number house,
              adh.corpus ind_house,
              ad.flat room,
              null ind_room,
              cd.serial nsdoc,
              cd.number ndoc,
              null telephone,
              cpi.infisCode cod_smo,
              lpu.infisCode attach,
              e.execDate date_attch,
              act.note n_attch,
              upper(concat(pers.lastName, ' ', substr(pers.firstName, 1, 1), '.', substr(pers.patrName, 1, 1), '.')) doctor
            from event e
            left join eventtype et on et.id = e.eventType_id
            left join organisation lpu on lpu.id = e.org_id
            left join action act on act.event_id = e.id
            left join person pers on pers.id = act.person_id
            left join client c on c.id = e.client_id
            left join clientpolicy cp on cp.id = (
              select
                a.id
              from clientpolicy a
              where
                a.client_id = c.id and a.policyType_id = 1 and
                date(a.begDate) <= date('%s')
              order by a.begDate desc
              limit 1
            )
            left join organisation cpi on cpi.id = cp.insurer_id
            left join rbsocstatustype sst on sst.id = (
              select
                sstt.id
              from clientsocstatus a
              join rbsocstatusclass ssc on ssc.id = a.socStatusClass_id
              join rbsocstatustype sstt on sstt.id = a.socStatusType_id
              where
                a.client_id = c.id and a.deleted = 0 and ssc.code = '74' and
                date(a.begDate) <= date('%s')
              order by a.begDate desc
              limit 1
            )
            left join clientaddress ca on ca.id = (
              select
                max(a.id)
              from clientaddress a
              where
                a.client_id = c.id and a.type = 0 and a.deleted = 0
            )
            left join address ad on ad.id = ca.address_id
            left join addresshouse adh on adh.id = ad.house_id
            left join clientdocument cd on cd.id = (
              select
                max(a.id)
              from clientdocument a
              where
                a.client_id = c.id and
                a.documenttype_id = (select id from rbDocumentType where code = '1' limit 1) and
                a.deleted = 0
            )
            where
              et.code = '7401' and
              date(e.execDate) between date('%s') and date('%s')
        """ % (lastDate, lastDate, firstDate, lastDate)
        query = db.query(stmt)
        return query

    def process(self, dbf, record, infisCode, attachments):
        policyNumber = -1 if forceInt(record.value('number')) == 0 else forceInt(record.value('number'))

        room = forceString(record.value('room')).split(" ")
        if (room[0] == "") or (not room[0].isdigit()):
            room[0] = 0
        else:
            room[0] = int(room[0])

        sdoc = forceString(record.value('nsdoc')).split(" ")

        if not attachments:
            mkb = MKBwithoutSubclassification(forceString(record.value('cod_mkb')))
            if len(mkb) == 3:
                mkb += '.'
            mkb1 = MKBwithoutSubclassification(forceString(record.value('cod_mkb1')))
            if len(mkb1) == 3:
                mkb1 += '.'
            serviceInfis = forceString(record.value('service_infis'))
            place = 0
            purpose = ''
            if serviceInfis:
                serviceInfis = serviceInfis.split('.')
                if len(serviceInfis) == 2:
                    place = forceInt(serviceInfis[0])
                    purpose = serviceInfis[1]
            tarif = forceDouble(record.value('tarif'))
            if forceString(record.value('kval')) == u'Ф':
                tarif = tarif * 0.8

            uet = forceDouble(record.value('uet')) if (place == 7) and (purpose == u'У') else 0
            ishod = 1 if place == 1 else 0
            visitDate = pyDate(forceDate(record.value('visit_date'))) if place in [1,2,3,7,10] else None
            dateBeg = pyDate(forceDate(record.value('date_beg'))) if place in [4,5,6,8,9,11,12] else None
            charac = 0 if place in [4,5,6,8,9,11,12] else forceInt(record.value('character'))

        dbfRecord = dbf.newRecord()

        dbfRecord['NUMBER'] = policyNumber
        dbfRecord['FAMILY']   = forceString(record.value('family'))
        dbfRecord['NAME']   = forceString(record.value('name'))
        dbfRecord['FATHER']   = forceString(record.value('father'))
        dbfRecord['DATE']   = pyDate(forceDate(record.value('date')))
        dbfRecord['SEX']   = forceInt(record.value('sex'))
        dbfRecord['STATUS']   = forceInt(record.value('status'))
        dbfRecord['CITYSTREET']   = forceString(record.value('citystreet'))
        dbfRecord['HOUSE']   = forceInt(record.value('house'))
        dbfRecord['IND_HOUSE']   = forceString(record.value('ind_house'))
        dbfRecord['ROOM']   = room[0]
        dbfRecord['IND_ROOM']   = "" if len(room) < 2 else room[1]
        dbfRecord['NSDOC']   = sdoc[0]
        dbfRecord['SDOC']   = "" if len(sdoc) < 2 else sdoc[1]
        dbfRecord['NDOC']   = forceString(record.value('ndoc'))
        dbfRecord['TELEPHONE']   = forceInt(record.value('telephone'))
        dbfRecord['COD_SMO']   = forceInt(record.value('cod_smo'))
        dbfRecord['ATTACH']   = forceInt(record.value('attach'))
        dbfRecord['DOCTOR']   = forceString(record.value('doctor'))
        if not attachments:
            dbfRecord['COD_LPU']   = forceInt(record.value('cod_lpu'))
            dbfRecord['COD_SPEC']   = forceInt(record.value('cod_spec'))
            dbfRecord['PLACE']   = place
            dbfRecord['PURPOSE']   = purpose
            dbfRecord['UET']   = uet
            dbfRecord['TARIF']   = forceDouble(record.value('tarif'))
            dbfRecord['DATE_TAR']   = pyDate(forceDate(record.value('date_tar')))
            dbfRecord['VISIT_DATE']   = visitDate
            dbfRecord['FIRST']   = forceInt(record.value('first'))
            dbfRecord['DATE_BEG']   = dateBeg
            dbfRecord['DATE_END']   = pyDate(forceDate(record.value('date_end')))
            dbfRecord['ISHOD']   = ishod
            dbfRecord['COD_MKB']   = mkb
            dbfRecord['COD_MKB1']   = mkb1
            dbfRecord['CHARACTER']   = charac
            dbfRecord['RESULT']   = forceInt(record.value('result'))
            dbfRecord['PERS_NUM']   = forceString(record.value('pers_num'))
            dbfRecord['PENS']   = forceString(record.value('pens'))
            dbfRecord['SPECDOLG']   = forceInt(record.value('specdolg'))
            dbfRecord['SPECPNUM']   = forceString(record.value('specpnum'))
            dbfRecord['COD_HELP']   = forceInt(record.value('cod_help'))
            dbfRecord['BEG_BL']   = pyDate(forceDate(record.value('beg_bl')))
            dbfRecord['END_BL']   = pyDate(forceDate(record.value('end_bl')))
            dbfRecord['KVAL']   = forceString(record.value('kval'))
            dbfRecord['DELETED']   = forceInt(record.value('deleted'))
        else:
            dbfRecord['DATE_ATTCH']   = pyDate(forceDate(record.value('date_attch')))
            dbfRecord['N_ATTCH']   = forceString(record.value('n_attch'))


        dbfRecord.store()


    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()


class CExportR74NATIVEPage2(QtGui.QWizardPage, Ui_ExportR74NATIVEPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.setTitle(u'Экспорт данных реестра по счёту')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R74NATIVEExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):
        src = self.wizard().getFullDbfFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()), os.path.basename(src))
        success, result = QtGui.qApp.call(self, shutil.move, (src, dst))
        if success:
            QtGui.qApp.preferences.appPrefs['R74NATIVEExportDir'] = toVariant(self.edtDir.text())
            self.wizard().setAccountExposeDate()
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
