#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Events.Utils import CPayStatus, getPayStatusMask
from Accounting.Utils import updateAccounts, updateDocsPayStatus

from Ui_ImportRD1 import Ui_Dialog
from Cimport import *


def ImportRD1(widget, accountId, accountItemIdList):
    dlg = CImportRD1(accountId, accountItemIdList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportRD1FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportRD1FileName'] = toVariant(dlg.edtFileName.text())


class CImportRD1(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self, accountId, accountItemIdList):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.accountId=accountId
        self.accountItemIdList=accountItemIdList
        self.progressBar.setFormat('%p%')
        self.checkName()


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
            dbfFileName = unicode(forceStringEx(self.edtFileName.text()))
            dbfRD1 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfRD1)))
            if 'TMO2' in dbfRD1.header.fields:
                self.edtAttach.setText('TMO2')
            else:
                self.edtAttach.setText('')



    def err2log(self, e):
        self.log.append(self.err_txt+e)


    def startImport(self):
        curr_acc=self.AccCheck.isChecked()
        imp_oplat=self.OplataCheck.isChecked()
        imp_otkaz=self.OtkazCheck.isChecked()
        imp_only_attach=self.chkOnlyAttach.isChecked()
        podtv=self.edtPodtv.text()
        if not podtv:
            self.log.append(u'нет подтверждения')
            return

        dbfFileName = unicode(self.edtFileName.text())
        dbfRD1 = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        imp_attach=self.chkAttach.isChecked() and forceString(self.edtAttach.text()) in dbfRD1.header.fields

        if imp_only_attach and not imp_attach:
            self.log.append(u'загрузка всех данных выключена')
            dbfRD1.close()
            return

        db = QtGui.qApp.db
        prevContractId = None
        payStatusMask = 0
        accountIdSet = set()

        n=0
        n_ld=0
        n_oplata=0
        n_otkaz=0
        n_notfound=0

        tableAccount_Item=tbl('Account_Item')
        tableAccount=tbl('Account')
        tableAcc=db.join(
            tableAccount_Item, tableAccount, 'Account_Item.master_id=Account.id')
        self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfRD1)))
#        RD1fields=get_RD1_fields()
#        RD1fields=[f[0] for f in RD1fields]
        requiredFields = ['COMMENT', 'DATE_OPLAT', 'DATE_OTKAZ', 'DR', 'ERR_S', 'FAM', 'ID', 'IM', 'KOD_OTKAZ', 'KOD_PROG', 'N_ACT', 'OT', 'POL']

        #FIXME: Нужно проверить что выбрасывается разумное исключение, которое приводит к понятному messageBox-у
#        assert dbfCheckNames(dbfRD1, RD1fields)
        assert dbfCheckNames(dbfRD1, requiredFields)
        self.progressBar.setMaximum(len(dbfRD1)-1)
        for row in dbfRD1:
            QtGui.qApp.processEvents()
            if self.abort: break
            self.progressBar.setValue(n)
            self.stat.setText(
                u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
                (n_ld, n_oplata, n_otkaz, n_notfound))
            n+=1
            self.n=n
            self.row=row
#            NUMTR=row['NUMTR']
#            DATETR=row['DATETR']
            ID=int(row['ID'])
#            KOD_ORG_OK=row['KOD_ORG_OK']
#            KOD_ORG_OG=row['KOD_ORG_OG']
#            PERIOD=row['PERIOD']
#            DATE_DOG=row['DATE_DOG']
#            NOMER_DOG=row['NOMER_DOG']
            FAM=row['FAM']
            IM=row['IM']
            OT=row['OT']
            POL=int(row['POL']) if row['POL'] else 0
            DR=row['DR']
#            SMO=row['SMO']
            ERR_S=row['ERR_S']
            if 'ID_PAT' in dbfRD1.header.fields:
                ID_PAT=row['ID_PAT']
                ID_PAT = int(ID_PAT) if ID_PAT else None
            else:
                ID_PAT = None
            if 'ERR_REM' in dbfRD1.header.fields:
                ERR_REM = row['ERR_REM']
            else:
                ERR_REM = ''

            DATE_OPLAT=row['DATE_OPLAT']
            DATE_OTKAZ=row['DATE_OTKAZ']
            N_ACT=row['N_ACT']
            KOD_OTKAZ=row['KOD_OTKAZ']
#            COMMENT=row['COMMENT']
            self.err_txt=u'ID=%s; ID_PAT=%s (%s %s %s): ' % (row['ID'], str(ID_PAT), FAM, IM, OT)

            KOD_PROG=row['KOD_PROG']
            if KOD_PROG!=4:
                continue
#            if not ID or not ID_PAT:
#                self.err2log(u'отсутствует ID или ID_PAT')
#                continue
            if not ID:
                self.err2log(u'отсутствует ID')
                continue

            if not imp_only_attach:
                if not DATE_OPLAT and not DATE_OTKAZ:
                    self.err2log(u'отсутствуют даты оплаты и отказа')
                    continue
                if DATE_OPLAT and DATE_OTKAZ:
                    self.err2log(u'есть и дата оплаты, и дата отказа')
                    continue
                if DATE_OTKAZ and not ERR_S:
                    self.err2log(u'нет кода отказа')
                    continue
                if not DATE_OTKAZ and ERR_S:
                    self.err2log(u'нет даты отказа')
                    continue
                if DATE_OPLAT and not imp_oplat:
                    continue
                if DATE_OTKAZ and not imp_otkaz:
                    continue

            Event=db.getRecord('Event', '*', ID)
            if not Event:
                self.err2log(u'Event не найден')
                continue
            if ID_PAT:
                if Event.value('client_id').toInt()[0]!=ID_PAT:
                    self.err2log(u'Event.client_id не совпадает с ID_PAT')
                    continue
            else:
                ID_PAT=Event.value('client_id').toInt()[0]

            Client=db.getRecord('Client', '*', ID_PAT)
            if not Client:
                self.err2log(u'пациент не найден')
                continue
            if ( (FAM or IM or OT or DR or POL)
                and( forceString(Client.value('lastName')).upper()!=FAM.upper()
                     or forceString(Client.value('firstName')).upper()!=IM.upper()
                     or forceString(Client.value('patrName')).upper()!=OT.upper()
                     or get_date(Client.value('birthDate'))!=DR
                     or Client.value('sex').toInt()[0]!=POL)):
                self.err2log(u'информация о пациенте не совпадает')
#                continue

            if imp_attach:
                attachField=forceString(self.edtAttach.text())
                attach=row[attachField]
                if attach:
                    lpuId=self.infis2orgId(attach)
                    if lpuId:
                        ClientAttachFields=[
                            ('client_id', ID_PAT), ('attachType_id', 2), ('LPU_id', lpuId)]
                        getId(self.tableClientAttach, ClientAttachFields)

            if not imp_only_attach:
                cond=[]
                cond.append(tableAccount_Item['event_id'].eq(toVariant(ID)))
                if curr_acc:
                    cond.append(tableAccount['id'].eq(toVariant(self.accountId)))
    #                cond.append(tableAccount_Item['date'].isNull())
                DATE=DATE_OPLAT if DATE_OPLAT else DATE_OTKAZ
    #                cond.append(tableAccount['date'].le(toVariant(DATE)))
                fields='Account_Item.id, Account.date as Account_date, Account_Item.date as Account_Item_date, Account_Item.master_id as Account_id, Account.contract_id as contract_id'
                AccRecord=db.getRecordEx(tableAcc, fields, where=cond)
                if AccRecord:
                    accountIdSet.add(forceRef(AccRecord.value('Account_id')))
                    contractId = forceRef(AccRecord.value('contract_id'))
                    if prevContractId != contractId:
                        prevContractId = contractId
                        financeId = forceRef(db.translate('Contract', 'id', contractId, 'finance_id'))
                        payStatusMask = getPayStatusMask(financeId)

                    Account_date=get_date(AccRecord.value('Account_date'))
                    Account_Item_date=get_date(AccRecord.value('Account_Item_date'))
                    if Account_Item_date:
                        self.err2log(u'счёт уже оплачен или отказан')
                        continue
                    if Account_date>DATE:
                        self.err2log(u'счёт уже оплачен или отказан')
                        continue

                    n_ld+=1

                    Account_ItemId=AccRecord.value('id').toInt()[0]
                    Account_Item=db.getRecord('Account_Item', '*', Account_ItemId)
                    Account_Item.setValue('date', toVariant(DATE))
                    refuseType_id=None
    #                    if DATE_OTKAZ and KOD_OTKAZ:
    #                        refuseType_id={}.get(KOD_OTKAZ, 61)
                    if DATE_OTKAZ:
                        n_otkaz+=1
                        ERR_S=ERR_S.replace(';', ',').split(',')[0]
                        refuseType_id=forceInt(db.translate(
                            'rbPayRefuseType', 'code', ERR_S, 'id'))
                        if not refuseType_id:
    #                        refuseType_id=61
                            table=tbl('rbPayRefuseType')
                            record = table.newRecord()
                            record.setValue('code', toVariant(ERR_S))
                            record.setValue('name ', toVariant(u'неизвестная причина с кодом "%s"' % ERR_S))
                            record.setValue('finance_id', toVariant(5))
                            record.setValue('rerun', toVariant(1))
                            refuseType_id=db.insertRecord(table, record)
                        Account_Item.setValue('refuseType_id', toVariant(refuseType_id))
                        updateDocsPayStatus(Account_Item, payStatusMask, CPayStatus.refusedBits)
                    else:
                        n_oplata+=1
                        updateDocsPayStatus(Account_Item, payStatusMask, CPayStatus.payedBits)
                    Account_Item.setValue('number', toVariant(str(N_ACT) if N_ACT else podtv))
                    Account_Item.setValue('note', toVariant(row['ERR_S']+';'+ERR_REM+' '+row['COMMENT']))
                    db.updateRecord(tableAccount_Item, Account_Item)
                else:
                    n_notfound+=1
                    self.err2log(u'счёт не найден')

        self.progressBar.setValue(n)
        self.stat.setText(
            u'обработано: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
            (n_ld, n_oplata, n_otkaz, n_notfound))
        self.progressBar.setValue(n-1)
        updateAccounts(list(accountIdSet))
