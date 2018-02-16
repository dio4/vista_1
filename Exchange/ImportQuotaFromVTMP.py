# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from Users.Rights import *

from Registry.ClientEditDialog import CClientEditDialog

from Cimport import *

from Utils  import *


from Ui_ImportQuotaFromVTMP import Ui_ImportQuotaFromVTMPDialog

#Соответствие полей при разборе входящего файла номерам в списке row в методе translateDataIntoDictionary
#0 - ID, 1 - номер талона, 2 - ФИО, 3 - СНИЛС, 4 - дата рождения, 5 - этап, 6 - дата последнего сохранения
#7 - профиль, 8 - вид при обращении, 9 - субъект РФ, 10 - диагноз, 11 - обращение, 12 - Дата создания
#13 - дата регистрации, 14 - Информация, 15 - ID пациента, 16 - Дата планируемой госпитализации
#17 - дата обращения в МУ, 18 - дата выписки, 19 - Метка, 20 - код КЭГ, 21 - код категории льготы
#22 - социальная группа, 23 - пол, 24, результат госпитализации, 25 - комментарии, 26 - направлен
#27 - место жительства, 28 - отказано, 29 - дата операции, 30 - дата повторной госпитализации

def ImportQuotaFromVTMP(parent):
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
    dlg = CImportQuotaFromVTMP(parent)
    QtGui.qApp.restoreOverrideCursor()
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportQuotaFromVTMPFileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportQuotaFromVTMPFileName'] = toVariant(dlg.edtFileName.text())

class CImportQuotaFromVTMP(QtGui.QDialog, CImport, Ui_ImportQuotaFromVTMPDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.tableClient          = tbl('Client')
        self.tableKLADR           = tbl('kladr.KLADR')
        self.tableClientDocument  = tbl('ClientDocument')
        self.tableClientContact   = tbl('ClientContact')
        self.tableClientAddress   = tbl('ClientAddress')
        self.tableClient_Quoting  = tbl('Client_Quoting')
        self.tableClientAttach    = tbl('ClientAttach')
        self.vtmpIdentifierId = self.toKnowVTMPAccountingSistemId()
        self.progressBar.setValue(0)
        self.isEndOfTable = False
        self.clientIdListForOpen = []
        self.importRun = False
        
    def toKnowVTMPAccountingSistemId(self):
        db = QtGui.qApp.db
        stmt = u'SELECT `id` FROM `rbAccountingSystem` WHERE `code`=\'ВТМП\''
        query = db.query(stmt)
        if query.first():
            return forceInt(query.value(0))
        else:
            return None
        
    def startImport(self):
        self.logList.clear()
        self.clientIdListForOpen = []
        fname=unicode(forceStringEx(self.edtFileName.text()))
        if fname:
            f = file(fname, 'r')
            try:
                inputText = unicode(f.read().decode('cp1251').encode('utf-8'), 'UTF-8')
            except Exception, e:
                print unicode(e)
                return
            lf = inputText.find('<table')-1
            rf = inputText.rfind('</table>')+8
            txt = inputText[lf:rf]
            self.rows    = []
            self.startParsing(txt)
            self.translateDataIntoDictionary()
            f.close()
            self.isEndOfTable = False
            self.importData()
            
    def startParsing(self, txt):
        lf = txt.find('<tr')-1
        rf = txt.find('</tr>')
        if lf >-1 and rf >-1:
            row = txt[lf:rf]
            self.tail = txt[rf+5:]
            self.column = []
            self.parsingRow(row)
        
    def parsingRow(self, row):
        lf = row.find('<td')
        rf = row.find('</td>')
        if lf >-1 and rf >-1 and not self.isEndOfTable:
            head = row[lf:rf]
            tail = row[rf+5:]
            p = head.find('>')
            val = head[p+1:].replace('<br>', ' ').replace('&nbsp;', '').replace('\n', ' ').replace('\r', '')
            val = self.checkTextOnTags(val)
            if val != None:
                self.column.append(val)
            self.parsingRow(tail)
        else:
            self.rows.append(self.column)
            if not self.isEndOfTable:
                self.startParsing(self.tail)
            
    def checkTextOnTags(self, txt):
        if u'Активные талоны' in txt:
            self.isEndOfTable = True
            return None
        lf = txt.find('<')
        rf = txt.find('>')
        if lf > -1 and rf > -1 and lf < rf:
            head = txt[:lf]
            tail = txt[rf+1:]
            result = head+tail
            return self.checkTextOnTags(result)
        else:
            return txt
            
                
                
    def translateDataIntoDictionary(self):
        data = list(self.rows)
        self.dictRows = []
        for row in data:
            try:
                int(row[0])
            except:
                continue
            d = {}
            d['idIdentifier'] = row[0]
            d['ticketNumber'] = row[1][1:]
            names = self.getNames(row[2])
            if names:
                lastName, firstName, patrName = names
            else:
                continue
            d['lastName']  = lastName
            d['firstName'] = firstName
            d['patrName']  = patrName
            d['SNILS']     = row[3].replace('-', '')
            try:
                d['birthDate'] = QDate().fromString(row[4], 'dd.MM.yyyy')
            except:
                d['birthDate'] = None
            try:
                d['stage']     = forceInt(row[5].split(' ')[0])
            except:
                d['stage'] = None
            try:
                d['lastSavingDate'] = QDate().fromString(row[6].split(' ')[0], 'dd.MM.yyyy')
            except:
                d['lastSavingDate'] = None
            d['parentQuotaCode'] = self.getQuotaCode(row[7])
            d['quotaCode']       = self.getQuotaCode(row[8])
            regionProperties = self.getRegionProperties(row[9])
            if regionProperties:
                d['regionKladrCode'] = regionProperties
                d['regionFreeInput'] = ''
            else:
                d['regionFreeInput'] = row[9]
                d['regionKladrCode'] = None
            d['MKB'] = self.checkLatin(row[10])
            d['request'] = self.getRequestValue(row[11])
            try:
                d['registrationDateTime'] = QDateTime().fromString(row[13], 'dd.MM.yyyy hh:mm:ss')
            except:
                d['registrationDateTime'] = None 
            address, document, contact = self.parseClientInfo(row[14])
            d['addressFreeInput'] = address
            d['clientDocument'] = document
            d['clientContact'] = contact
            d['VTMPClientId'] = row[15]
            d['sex'] = self.getSamsonVistaSexValue(row[23])
            self.dictRows.append(d)
            
    def getRequestValue(self, request):
        if request == u'Первичное':
            return 0
        if request == u'Повторное':
            return 1
        return None
                
                
    def getSamsonVistaSexValue(self, sex):
        if sex == u'Мужской':
            return 1
        if sex == u'Женский':
            return 2
        return None
                
    def parseClientInfo(self, info):
        fAddress  = info.find(u'Адрес')
        fDocument = info.find(u'Документ')
        fContact  = info.find(u'Контакт')
        if fAddress > -1:
            if fDocument > -1:
                if fContact > -1:
                    address  = info[fAddress+6:fDocument]
                    document = info[fDocument+9:fContact].split(',')[0]
                    contact  = info[fContact+8:]
                else:
                    address  = info[fAddress+6:fDocument]
                    document = info[fDocument+9:].split(',')[0]
                    contact  = None
            else:
                if fContact > -1:
                    address  = info[fAddress+6:fContact]
                    document = None
                    contact  = info[fContact+8:]
                else:
                    address  = info[fAddress+6]
                    document = None
                    contact  = None
        else:
            if fDocument > -1:
                if fContact > -1:
                    address  = None
                    document = info[fDocument+9:fContact].split(',')[0]
                    contact  = info[fContact+8:]
                else:
                    address  = None
                    document = info[fDocument+9:].split(',')[0]
                    contact  = None
            else:
                if fContact > -1:
                    address  = None
                    document = None
                    contact  = info[fContact+8:]
                else:
                    address  = None
                    document = None
                    contact  = None
                
        return address, document, contact
                
    def checkLatin(self, txt):
        if not check_rus(txt):
            return txt
        else:
            return None
                
    def getRegionProperties(self, region):
        r = region.split(' ')
        if len(r)>1:
            reg1 = r[0]
            reg2 = r[1]
            db = QtGui.qApp.db
            cond = db.joinOr([db.joinAnd([self.tableKLADR['NAME'].eq(reg1), 
                    self.tableKLADR['SOCR'].like(reg2[:2]+'...')]), 
                    db.joinAnd([self.tableKLADR['NAME'].eq(reg2), 
                    self.tableKLADR['SOCR'].like(reg1[:2]+'...')])])
            record = db.getRecordEx(self.tableKLADR, '*', cond)
            if record:
                return forceString(record.value('CODE'))
            else:
                return None
        return None
            
            
    def getQuotaCode(self, code):
        if code:
            if code[len(code)-1] == '.':
                return code[:-1]
            return code
        return None
            
            
    def getNames(self, names):
        names = nameCase(names).replace('\r', '').split(' ')
        i = 0
        if len(names) > 2:
            lastName = None
            firstName = None
            patrName = None
            for val in names:
                if val:
                    if i == 0:
                        lastName  = val
                    if i == 1:
                        firstName = val
                    if i == 2:
                        patrName  = val
                    i += 1
            return lastName, firstName, patrName
        else:
            return None
            
    def checkIsEmptyVal(self, val):
        if val:
            return val
        return None
        
    def importData(self):
        n  = 0
        nl = 0
        self.progressBar.setMaximum(len(self.dictRows)-1)
        for info in self.dictRows:
            QtGui.qApp.processEvents()
            if self.abort: break
            n += 1
            self.progressBar.setValue(n)
            total = u'обработано: '+str(n)
            clientId, fio, birthDate = self.getClientId(info)
            if not clientId:
                continue
            self.setClientIdentification(info, clientId)
            clientDocumentId  = self.getClientDocumentId(info, clientId)
            clientContactId   = self.getClientContactId(info,  clientId)
            clientAddressId   = self.getClientAddressId(info,  clientId)
            clientQuotingInfo = self.getClientQuotingId(info,  clientId)
            if clientQuotingInfo:
                clientQuotingId, quotaCode = clientQuotingInfo
                self.setQuotingAttach(clientId)
            else:
                clientQuotingId = quotaCode = None
            self.setQuotingDiscussionMessage(clientQuotingId)
            txt = fio+' '+forceString(birthDate)+' | '+forceString(quotaCode)
            self.clientIdListForOpen.append(clientId)
            self.addInfoItem(txt)
            nl += 1
            self.stat.setText(total)
#        self.progressBar.setValue(n-1)
    
    
    def getClientId(self, info):
        bad=False
        lastName  = info['lastName']
        firstName = info['firstName']
        patrName  = info['patrName']
        snils     = info['SNILS']
        if not snils:
            snils = ''
        if not (lastName and firstName and patrName):
            bad=True
        fio=lastName+firstName+patrName
        if not check_rus_lat(fio):
            bad=True
        sex = info['sex']
        if not sex:
            bad=True
        birthDate = info['birthDate']
        if not birthDate:
            bad=True
        if bad:
            return None, None, None
        else:
            clientFields = [
                ('lastName', lastName), ('firstName', firstName), ('patrName', patrName),
                ('sex', sex), ('birthDate', birthDate)]
            clientFields2 = [('SNILS', snils)]
            id      = getId(self.tableClient, clientFields, clientFields2)
            fio     = ' '.join([lastName, firstName, patrName])
            birthDay = birthDate.toString('dd.MM.yyyy')
            return (id, fio, birthDay)
            
            
    def setClientIdentification(self, info, clientId):
        lastSavingDate = info['lastSavingDate']
        if not (self.vtmpIdentifierId and lastSavingDate):
            return None
        identifier = info['VTMPClientId']
        if not identifier:
            return None
        db = QtGui.qApp.db
        stmt = u'SELECT * FROM `ClientIdentification` WHERE `client_id`=%d AND `accountingSystem_id`=%d AND `checkDate` = (SELECT MAX(`checkDate`) FROM `ClientIdentification` AS CI WHERE CI.`client_id`=%d AND CI.`accountingSystem_id`=%d)' %(clientId, self.vtmpIdentifierId, clientId, self.vtmpIdentifierId)
        query = db.query(stmt)
        table = db.table('ClientIdentification')
        if query.first():
            record = query.record()
        else:
            record = table.newRecord()
        checkDate = forceDate(record.value('checkDate'))
        if lastSavingDate > checkDate:
            record.setValue('client_id', QVariant(clientId))
            record.setValue('accountingSystem_id', QVariant(self.vtmpIdentifierId))
            record.setValue('identifier', QVariant(identifier))
            record.setValue('checkDate', QVariant(lastSavingDate))
            db.insertOrUpdate(table, record)
            
            
    def getClientDocumentId(self, info, clientId):
        fullDocument = info['clientDocument'].replace(u'№', ' ')
        if fullDocument:
            serial = ''
            number = ''
            i = 0
            for c in fullDocument:
                if c and c != ' ':
                    i += 1
                    if i < 5:
                        if i == 3:
                            serial += ' '
                        serial += c
                    if i >= 5 and i < 11:
                        number += c
                    if i >= 11:
                        return None
            clientDocumentFields=[
                ('client_id', clientId), ('documentType_id', '1')]
            clientDocumentFields2 = [
                ('serial', serial), ('number', number)]
            return getId(self.tableClientDocument, clientDocumentFields, clientDocumentFields2)
        return None
        
    def getClientContactId(self, info, clientId):
        contact = info['clientContact']
        if contact:
            contactTypeId = self.getContactTypeId(contact)
            if not contactTypeId:
                return None
            clientContactFields = [('client_id', clientId)]
            clientContactFields2 = [('contactType_id', contactTypeId), ('contact', contact)]
            return getId(self.tableClientContact, clientContactFields, clientContactFields2)
        return None
        
    def getContactTypeId(self, contact):
        if contact.isdigit():
            record = QtGui.qApp.db.getRecordEx('rbContactType', 'MIN(id)', 'name LIKE \'%s\''%u'%тел%')
            id = forceInt(record.value(0))
            return id
        return None
        
    def getClientAddressId(self, info, clientId):
        addressFreeInput = info['addressFreeInput']
        if addressFreeInput:
            clientAddressFields = [('client_id', clientId)]
            clientAddressFields2 = [('freeInput', addressFreeInput)]
            return getId(self.tableClientAddress, clientAddressFields, clientAddressFields2)
        return None
        
    def getClientQuotingId(self, info, clientId):
        quotaCode   = info['quotaCode']
        quotaTypeId = self.getQuotaTypeId(quotaCode)
        if not quotaTypeId:
            quotaCode   = info['parentQuotaCode']
            quotaTypeId = self.getQuotaTypeId(quotaCode)
            if not quotaTypeId:
                return None
        stage       = info['stage']
        MKB         = info['MKB']
        request     = info['request']
        identifier  = info['idIdentifier']
        quotaTicket = info['ticketNumber']
        dateRegistration = info['registrationDateTime']
        regionKladrCode = info['regionKladrCode']
        client_QuotingFields  = [('master_id', clientId), ('quotaType_id', quotaTypeId), 
                                 ('deleted', 0)]
        client_QuotingFields2 = [('stage', stage), ('MKB', MKB),('request', request), 
                                 ('identifier', identifier), ('quotaTicket', quotaTicket), 
                                 ('status', 12), ('dateRegistration', dateRegistration), 
                                 ('amount', 1), ('regionCode', regionKladrCode)]
        return getId(self.tableClient_Quoting, client_QuotingFields, client_QuotingFields2), quotaCode
        
    def setQuotingDiscussionMessage(self, quotingId):
        if quotingId:
            db = QtGui.qApp.db
            stmt = 'SELECT * FROM Client_QuotingDiscussion WHERE  Client_QuotingDiscussion.`id` = (SELECT MAX(`id`) FROM Client_QuotingDiscussion AS CQD WHERE CQD.`master_id`=%d)'%quotingId
            query  = db.query(stmt)
            query.first()
            record = query.record()
            agreementTypeId = forceInt(record.value('agreementType_id'))
            stmt = u'SELECT `id` FROM rbAgreementType WHERE code = \'ВТМП\''
            query  = db.query(stmt)
            if query.first():
                VTMPAgreementTypeId = forceInt(query.value(0))
            else:
                return None
            if agreementTypeId == VTMPAgreementTypeId:
                return None
            else:
                table  = db.table('Client_QuotingDiscussion')
                record = table.newRecord()
                record.setValue('master_id', QVariant(quotingId))
                record.setValue('agreementType_id', QVariant(VTMPAgreementTypeId))
                record.setValue('dateMessage', QVariant(QDateTime().currentDateTime()))
                record.setValue('responsiblePerson_id', QVariant(QtGui.qApp.userId))
                db.insertRecord(table, record)
          
    def setQuotingAttach(self, clientId):
        db = QtGui.qApp.db
        attachTypeId = db.translate('rbAttachType', 'code', '9', 'id')
        cond = [self.tableClientAttach['attachType_id'].eq(attachTypeId), 
                self.tableClientAttach['client_id'].eq(clientId), 
                self.tableClientAttach['deleted'].eq(0)]
        cond.append(db.joinOr([self.tableClientAttach['endDate'].isNull(), 
                               self.tableClientAttach['endDate'].gt(QDate.currentDate())]))
        record = db.getRecordEx(self.tableClientAttach, '*', cond)
        if record:
            return
        else:
            record = self.tableClientAttach.newRecord()
            record.setValue('client_id', QVariant(clientId))
            record.setValue('attachType_id', attachTypeId)
            record.setValue('LPU_id', QVariant(QtGui.qApp.currentOrgId()))
            record.setValue('begDate', QVariant(QDate.currentDate()))
        return db.insertOrUpdate('ClientAttach', record)
            
        
        
        
        
    def getQuotaTypeId(self, code):
        id = QtGui.qApp.db.translate('QuotaType', 'code', code, 'id')
        if id:
            id = forceInt(id)
        return id
            
            
    def addInfoItem(self, info):
        self.logList.addItem(info)
        
    def editClient(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            dialog = CClientEditDialog(self)
            if clientId:
                dialog.load(clientId)
            if dialog.exec_() :
                clientId = dialog.itemId()
        
            
    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XLS (*.xls);; Все файлы (*.*)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
        
    @QtCore.pyqtSlot(QModelIndex)
    def on_logList_doubleClicked(self, index):
        row = self.logList.currentRow()
        clientId = self.clientIdListForOpen[row]
        self.editClient(clientId)