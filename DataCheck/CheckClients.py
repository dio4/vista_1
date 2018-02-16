# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils             import forceInt, forceRef, forceString, get_date
from Orgs.Utils                import getOrganisationInfo
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils            import getAddress, getAttachRecord, getClientAddress, getClientDocument, getClientPolicy, getClientWork
from Users.Rights              import urAdmin, urRegTabWriteRegistry

from Ui_Clients import Ui_ClientsCheckDialog
from CCheck import CCheck

class ClientsCheck(QtGui.QDialog, Ui_ClientsCheckDialog, CCheck):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)

    def check(self):
        db=QtGui.qApp.db
#        my_org_id=QtGui.qApp.currentOrgId()
        n=0
        q='''
            select
                Client.id as client_id,
                Client.lastName, Client.firstName, Client.patrName,
                Client.birthDate, Client.sex, Client.SNILS
            from
                Client
            where
                1
            '''
        query=db.query(q)
        query.setForwardOnly(True)
        n=0
        n_bad=0
        s=query.size()
        if s>0:
            self.progressBar.setMaximum(s-1)
        while query.next():
            QtGui.qApp.processEvents()
            if self.abort: break
            self.progressBar.setValue(n)
            n+=1
            self.item_bad=False
            record=query.record()
            def val(name): return record.value(name)
            client_id=forceInt(val('client_id'))
            self.client_id=client_id
            self.itemId=client_id
            lastName=forceString(val('lastName'))
            firstName=forceString(val('firstName'))
            patrName=forceString(val('patrName'))
            fio=' '.join([lastName, firstName, patrName])
            birthDate=get_date(val('birthDate'))
            bd_err=''
            if birthDate:
                bd_err=', '+forceString(birthDate.strftime('%d.%m.%Y'))
            self.err_str='client '+forceString(client_id)+' ('+fio+bd_err+') '
            if not lastName or not firstName or not patrName:
                self.err2log(u'неполный ФИО')
            sex=forceInt(val('sex'))
            if sex not in [1, 2]:
                self.err2log(u'нет пола')
            SNILS=forceString(val('SNILS')).strip()
            if SNILS:
                if len(db.getRecordList('Client', where='SNILS=\"'+SNILS+'\"'))>1:
                    self.err2log(u'двойной СНИЛС '+SNILS)
            else:
                self.err2log(u'отсутствует СНИЛС')
            policy=getClientPolicy(client_id)
            if policy:
                self.checkPolicy(policy)
            else:
                self.err2log(u'отсутствует полис')
            work=getClientWork(client_id)
            if work:
                self.checkWork(work)
            else:
                self.err2log(u'отсутствует работа')
            if policy and not work:
                self.err2log(u'указан полис неработающего гражданина')
            self.checkDocument(client_id)
            self.checkAddress(client_id)
            AttachRecord=getAttachRecord(client_id, 0)
            if not AttachRecord:
                self.err2log(u'отсутствует постоянное прикрепление')
            else:
                LPU_id=AttachRecord['LPU_id']
                LPU=QtGui.qApp.db.getRecord('Organisation', 'title, infisCode, net_id', LPU_id)
                title=forceString(LPU.value('title'))
                infisCode=LPU.value('infisCode')
                net_id=LPU.value('net_id')
                if not infisCode:
                    self.err2log(u'отсутствует код ИНФИС у '+title)
                if not net_id:
                    self.err2log(u'отсутствует сеть у '+title)
            Event=QtGui.qApp.db.getRecordEx('Event', '*', 'client_id=\''+str(client_id)+'\'')
            if not Event:
                self.err2log(u'отсутствуют event\'ы')
            if self.item_bad:
                n_bad+=1
            self.label.setText(u'%d клиентов всего; %d с ошибками' % (s, n_bad))

    def checkAddress(self, client_id):
        regAddressRecord = getClientAddress(client_id, 0)
        if regAddressRecord:
            address=getAddress(regAddressRecord.value('address_id'))
            if not address.KLADRStreetCode:
                self.err2log(u'отсутствует название улицы')
            if not address.number:
                self.err2log(u'отсутствует номер дома')
        else:
            self.err2log(u'отсутствует адрес')

    def checkWork(self, work):
        orgId = forceRef(work.value('org_id'))
        work_info=getOrganisationInfo(orgId)
        if work_info:
            if not work_info['INN']:
                self.err2log(u'отсутствует ИНН')
            if not work_info['KPP']:
                self.err2log(u'отсутствует КПП')
        else:
            self.err2log(u'отсутствует работа')


    def openItem(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            return dialog
        else:
            return None


    def checkDocument(self, client_id):
        document=getClientDocument(client_id)
        if document:
            serial=forceString(document.value('serial'))
            number=forceString(document.value('number'))
            cond='serial=\''+serial+'\' and number=\''+number+'\''
            if len(QtGui.qApp.db.getRecordList('ClientDocument', where=cond))>1:
                self.err2log(u'двойной документ '+serial+' '+number)
        else:
            self.err2log(u'отсутствует документ')

    def checkPolicy(self, policy):
        serial=forceString(policy.value('serial'))
        number=forceString(policy.value('number'))
        cond='serial=\''+serial+'\' and number=\''+number+'\''
        if len(QtGui.qApp.db.getRecordList('ClientPolicy', where=cond))>1:
            self.err2log(u'двойной полис '+serial+' '+number)