# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
from socket import error as SocketError

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QDate, QDateTime
from ZSI import ParsedSoap

from DrugstoreService_services import *
from UploadService_services import *
from library.Recipe.Utils import recipeStatusNames
from library.Utils import forceString, forceInt, forceBool, forceDouble, forceDateTime, toVariant, formatSNILS, unformatSNILS
from library.database import connectDataBaseByInfo


class CR23ClientPrivilege:
    def __init__(self, serial, number, name, code, begDate, endDate):
        self.serial = serial
        self.number = number
        self.name = name
        self.code = code
        self.begDate = begDate
        self.endDate = endDate
        self.found = False


class CR23RecipeService:

    def __init__(self, clientId, url='http://10.0.1.154/', db=None, tracefilename=None):
        if db is None:
            db = QtGui.qApp.db
        self.db = db
        parsedUrl = urlparse.urlparse(url)
        self.url = parsedUrl.scheme + '://' + parsedUrl.netloc
        self.clientId = clientId
        self.tracefilename = tracefilename

    #TODO: mdldml: заменить велосипед функцией из проекта или стандартной библиотеки, я знаю, он должен существовать!
    @staticmethod
    def toDateTuple(datetime, date=None):
        if date is None:
            date = datetime.date()
        time = datetime.time()
        return date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), 0

    def toCorrectBegDate(self, datetime):
        res = self.toDateTuple(datetime)
        today = QDate.currentDate()
        if (res[0] < 0) or (res[0] > today.year()):
            res = self.toDateTuple(datetime, today)
        return res

    def toCorrectEndDate(self, datetime):
        res = self.toDateTuple(datetime)
        if res[0] < 0: #-4713
            res = self.toDateTuple(datetime, QDate.fromString('2199-12-31', 'yyyy-MM-dd'))
        return res


    @staticmethod
    def getYear(datetime):
        return datetime.date().year()


    def downloadRemains(self):
        loc = DrugstoreServiceLocator()
        tracefile = open(self.tracefilename, 'a') if self.tracefilename is not None else None
        port = loc.getDrugstoreServiceSoap(url=(self.url + '/drugstore/DrugstoreService.asmx'), tracefile=tracefile)
        failures = []

        db = self.db
        table = db.table('dlo_DrugstoreRemains')

        msg = None
        try:
            msg = RemainDownloadSoapIn()
            msg._clientId = self.clientId
            resp = port.RemainDownload(msg)
            dateTime = QDateTime.currentDateTime()
            query = db.query(u'SELECT * FROM dlo_DrugstoreRemains')
            while query.next():
                record = query.record()
                record.setValue('syncDateTime', toVariant(dateTime))
                db.updateRecord(table, record)
            if not hasattr(resp, '_RemainDownloadResult'):
                return True

            listDoneRemains = []
            for remainResponse in resp._RemainDownloadResult._RemainOutput:
                print remainResponse._ProductUnifyId
                record = db.getRecordEx(table, '*',
                                        db.joinAnd([table['productUnifyId'].eq(remainResponse._ProductUnifyId),
                                                   table['drugstore_id'].eq(remainResponse._DrugstoreId)]))
                if not record:
                    record = table.newRecord()
                    record.setValue('syncDateTime', toVariant(dateTime))
                    if hasattr(remainResponse, '_DrugstoreId'):
                        record.setValue('drugstore_id', toVariant(remainResponse._DrugstoreId))
                    if hasattr(remainResponse, '_DrugstoreName'):
                        record.setValue('drugstoreName', toVariant(remainResponse._DrugstoreName.decode('utf-8')))
                    if hasattr(remainResponse, '_ProductUnifyId'):
                        record.setValue('productUnifyId', toVariant(remainResponse._ProductUnifyId))
                    if hasattr(remainResponse, '_ProductName'):
                        record.setValue('productName', toVariant(remainResponse._ProductName.decode('utf-8')))
                    if hasattr(remainResponse, '_ProducerName'):
                        record.setValue('producerName', toVariant(remainResponse._ProducerName.decode('utf-8')))
                    if hasattr(remainResponse, '_CountryName'):
                        record.setValue('countryName', toVariant(remainResponse._CountryName.decode('utf-8')))
                    if hasattr(remainResponse, '_Mnn'):
                        record.setValue('mnn', toVariant(remainResponse._Mnn.decode('utf-8')))
                    if hasattr(remainResponse, '_Trn'):
                        record.setValue('trn', toVariant(remainResponse._Trn.decode('utf-8')))
                    if hasattr(remainResponse, '_Cureform'):
                        record.setValue('cureform', toVariant(remainResponse._Cureform.decode('utf-8')))
                    if hasattr(remainResponse, '_Dosage'):
                        record.setValue('dosage', toVariant(remainResponse._Dosage.decode('utf-8')))
                    record.setValue('package', toVariant(remainResponse._Package))
                    record.setValue('denominator', toVariant(remainResponse._Denominator))
                #TODO: может, ещё что-то может меняться? Название аптеки, например?
                record.setValue('price', toVariant(remainResponse._Price))
                # record.setValue('quantity', toVariant(forceInt(record.value('quantity')) + forceInt(remainResponse._Quantity)))
                if not forceString(remainResponse._ProductName.decode('utf-8')) in listDoneRemains:
                    if forceDouble(remainResponse._Denominator):
                        record.setValue('quantity', toVariant(forceDouble(remainResponse._Quantity) / forceDouble(remainResponse._Denominator)))
                    else:
                        record.setValue('quantity', toVariant(forceDouble(remainResponse._Quantity)))
                else:
                    if forceDouble(remainResponse._Denominator):
                        record.setValue('quantity', toVariant((forceDouble(remainResponse._Quantity) / forceDouble(remainResponse._Denominator)) + forceDouble(record.value('quantity'))))
                    else:
                        record.setValue('quantity', toVariant(forceDouble(record.value('quantity')) + forceDouble(remainResponse._Quantity)))
                db.insertOrUpdate(table, record)
                listDoneRemains.append(forceString(remainResponse._ProductName.decode('utf-8')))
            return True

        except Exception, e:
            print e
            return False


    def checkPrivilege(self, resp, query):
        documents = []
        while query.next():
            documentRecord = query.record()
            documents.append(CR23ClientPrivilege(forceString(documentRecord.value('serial')),
                                                 forceString(documentRecord.value('number')),
                                                 forceString(documentRecord.value('name')),
                                                 forceString(documentRecord.value('code')),
                                                 self.toCorrectBegDate(forceDateTime(documentRecord.value('begDate'))),
                                                 self.toCorrectEndDate(forceDateTime(documentRecord.value('endDate')))))
        if not hasattr(resp._PersonClientCheckResult._PersonClient[0], '_PrivilegeDocuments'):
            return False
        for documentResponse in resp._PersonClientCheckResult._PersonClient[0]._PrivilegeDocuments._PrivilegeDocumentClient:
            found = False
            for document in documents:
                if (not hasattr(documentResponse, '_PrivilegeDocumentSeria') or (documentResponse._PrivilegeDocumentSeria.decode('utf-8') == document.serial)) \
                        and documentResponse._PrivilegeDocumentNumber.decode('utf-8') == document.number \
                        and documentResponse._PrivilegeDocumentName.decode('utf-8') == document.name \
                        and documentResponse._PrivilegeCategoryCode.decode('utf-8') == document.code \
                        and documentResponse._PrivilegeDocumentStart[0:7] == document.begDate \
                        and documentResponse._PrivilegeDocumentEnd[0:7] == document.endDate:
                    document.found = True
                    found = True
            if not found:
                return False
        for document in documents:
            if not document.found:
                return False
        return True

    #TODO: mdldml: заменить clientId на clientIdList
    # метод проверяет, есть ли льготник в МИАЦ
    def checkClient(self, clientId):
        loc = UploadServiceLocator()
        tracefile = open(self.tracefilename, 'a') if self.tracefilename is not None else None
        port = loc.getUploadServiceSoap(url=(self.url + '/drugstore/UploadService.asmx'), tracefile=tracefile, transdict={'timeout': 5})
        failures = []

        db = self.db
        tableClient = db.table('Client')
        clientRecord = db.getRecord(tableClient, '*', clientId)

        msg = None
        try:
            msg = PersonClientCheckSoapIn()
            msg._clientId = self.clientId
            msg._persons = ns0.ArrayOfPersonClient_Def('_persons')
            person = ns0.PersonClient_Def('_PersonClient')
            msg._persons._PersonClient = [person]

            person._Uploaded = False
            person._PersonFound = False
            if forceString(clientRecord.value('SNILS')):
                person._Snils = formatSNILS(forceString(clientRecord.value('SNILS')))
            else:
                tableFakeSNILS = db.table('ClientFakeSNILS')
                fakeSnilsRecord = db.getRecordEx(tableFakeSNILS, '*', where='client_id = %d' % clientId)
                if fakeSnilsRecord:
                    person._Snils = formatSNILS(forceString(fakeSnilsRecord.value('fakeSNILS')))
                else:
                    person._Firstname = forceString(clientRecord.value('firstName'))
                    person._Lastname = forceString(clientRecord.value('lastName'))
                    person._Patronymic = forceString(clientRecord.value('patrName'))
                    person._Sex = [u'', u'М', u'Ж'][forceInt(clientRecord.value('sex'))]
                    person._Birthday = self.toDateTuple(forceDateTime(clientRecord.value('birthDate')))

            resp = port.PersonClientCheck(msg)
            if (hasattr(resp._PersonClientCheckResult._PersonClient[0], '_PersonFound') and
                    not resp._PersonClientCheckResult._PersonClient[0]._PersonFound) or \
                    hasattr(resp._PersonClientCheckResult._PersonClient[0], '_Check'):
                return False

            if (hasattr(resp._PersonClientCheckResult._PersonClient[0]), '_PrivilegeDocuments'):
                documents = resp._PersonClientCheckResult._PersonClient[0]._PrivilegeDocuments
                for doc in documents:
                    if (hasattr(doc, '_PrivilegeDocumentDeleted')):
                        tDocuments = self.db.table('ClientDocument')
                        docNumber = forceString(doc._PrivilegeDocumentNumber)
                        docSerial = forceString(doc._PrivilegeDocumentSeria)
                        docEndDate = forceDateTime(doc._PrivilegeDocumentDeleted)
                        recDoc = self.db.getRecordEx(tDocuments, '*', [tDocuments['client_id'].eq(clientId), tDocuments['number'].eq(docNumber), tDocuments['serial'].eq(docSerial)])
                        if recDoc:
                            if not forceString(docEndDate) == forceString(recDoc.value('endDate')):
                                recDoc.setValue('endDate', docEndDate)
                                self.db.updateRecord(tDocuments, recDoc)

            return self.checkPrivilege(resp, self.getPrivilege(clientId))

        except Exception as e:
            print e
            return False

    def getPrivilege(self, clientId):
        db = self.db
        tableClientSocStatus = db.table('ClientSocStatus')
        socStatusStmt = u'''
        SELECT
            ClientDocument.serial,
            ClientDocument.number,
            rbDocumentType.name,
            rbSocStatusType.code,
            ClientSocStatus.begDate,
            ClientSocStatus.endDate,
            ClientSocStatus.deleted,
            ClientSocStatus.modifyDatetime
        FROM
            ClientSocStatus
            INNER JOIN rbSocStatusType ON ClientSocStatus.socStatusType_id = rbSocStatusType.id
            INNER JOIN ClientDocument ON ClientSocStatus.document_id = ClientDocument.id
            INNER JOIN rbDocumentType ON ClientDocument.documentType_id = rbDocumentType.id
            INNER JOIN rbSocStatusClass ON ClientSocStatus.socStatusClass_id = rbSocStatusClass.id AND rbSocStatusClass.flatCode = 'benefits'
        WHERE
            %s
        ''' % db.joinAnd([tableClientSocStatus['client_id'].eq(clientId), tableClientSocStatus['deleted'].eq(0)])
        return db.query(socStatusStmt)


    #TODO: mdldml: заменить clientId на clientIdList
    def sendClient(self, clientId):
        loc = UploadServiceLocator()
        tracefile = open(self.tracefilename, 'a') if self.tracefilename is not None else None
        port = loc.getUploadServiceSoap(url=(self.url + '/drugstore/UploadService.asmx'), tracefile=tracefile, transdict={'timeout': 5})
        failures = []
        db = self.db
        tableClient = db.table('Client')
        tableClientRecipeExport = db.table('ClientRecipeExport')
        clientRecord = db.getRecord(tableClient, '*', clientId)
        query = self.getPrivilege(clientId)
        errorList = []
        msg = None
        try:
            msg = PersonClientSaveSoapIn()
            msg._clientId = self.clientId
            msg._persons = ns0.ArrayOfPersonClient_Def('_persons')
            person = ns0.PersonClient_Def('_PersonClient')
            msg._persons._PersonClient = [person]

            person._Firstname = forceString(clientRecord.value('firstName'))
            person._Lastname = forceString(clientRecord.value('lastName'))
            person._Patronymic = forceString(clientRecord.value('patrName'))
            SNILS = clientRecord.value('SNILS')
            if not forceString(clientRecord.value('SNILS')):
                tableFakeSNILS = db.table('ClientFakeSNILS')
                fakeSnilsRecord = db.getRecordEx(tableFakeSNILS, '*', where='client_id = %d' % clientId)
                if fakeSnilsRecord:
                    SNILS = fakeSnilsRecord.value('fakeSNILS')
            person._Snils = formatSNILS(forceString(SNILS))
            person._Sex = [u'', u'М', u'Ж'][forceInt(clientRecord.value('sex'))]
            person._Birthday = self.toDateTuple(forceDateTime(clientRecord.value('birthDate')))
            person._CredentialTypeName = u'ПАСПОРТ'  # ?
            person._PersonFound = False
            person._Uploaded = False
            person._PrivilegeDocuments = ns0.ArrayOfPrivilegeDocumentClient_Def('_PrivilegeDocuments')
            person._PrivilegeDocuments._PrivilegeDocumentClient = []
            while query.next():
                documentRecord = query.record()
                privilegeDocumentClient = ns0.PrivilegeDocumentClient_Def('_PrivilegeDocumentClient')
                privilegeDocumentClient._PrivilegeDocumentSeria = forceString(documentRecord.value('serial'))
                privilegeDocumentClient._PrivilegeDocumentNumber = forceString(documentRecord.value('number'))
                privilegeDocumentClient._PrivilegeDocumentName = forceString(documentRecord.value('name'))
                privilegeDocumentClient._PrivilegeCategoryCode = forceString(documentRecord.value('code'))
                privilegeDocumentClient._PrivilegeDocumentStart = self.toCorrectBegDate(forceDateTime(documentRecord.value('begDate')))
                privilegeDocumentClient._PrivilegeDocumentEnd = self.toCorrectEndDate(forceDateTime(documentRecord.value('endDate')))
                if forceBool(documentRecord.value('deleted')):
                    privilegeDocumentClient._PrivilegeDocumentDeleted = self.toDateTuple(forceDateTime(documentRecord.value('modifyDatetime')))
                privilegeDocumentClient._Uploaded = False
                person._PrivilegeDocuments._PrivilegeDocumentClient.append(privilegeDocumentClient)

            resp = port.PersonClientSave(msg)

            if not forceString(clientRecord.value('SNILS')):
                tableFakeSNILS = db.table('ClientFakeSNILS')
                fakeSnilsRecord = db.getRecordEx(tableFakeSNILS, '*', where='client_id = %d' % clientId)
                if not fakeSnilsRecord:
                    fakeSnilsRecord = tableFakeSNILS.newRecord()
                    fakeSnilsRecord.setValue('client_id', toVariant(clientId))
                    fakeSnilsRecord.setValue('fakeSNILS',
                                             toVariant(unformatSNILS(resp._PersonClientSaveResult._PersonClient[0]._Snils)))
                    db.insertRecord(tableFakeSNILS, fakeSnilsRecord)

            if forceString(resp._PersonClientSaveResult._PersonClient[0]._Uploaded) == u'true':
                clientExportRecord = db.getRecordEx(tableClientRecipeExport, '*', where='client_id = %d' % clientId)
                if clientExportRecord is None:
                    clientExportRecord = tableClientRecipeExport.newRecord()
                clientExportRecord.setValue('client_id', toVariant(clientId))
                clientExportRecord.setValue('sentToMiac', toVariant(1))
                clientExportRecord.setValue('errorList', toVariant(''))
                db.insertOrUpdate(tableClientRecipeExport, clientExportRecord)
            else:
                errorList.append(u'<Check>' + resp._PersonClientSaveResult._PersonClient[0]._Check.decode('utf8') + u'</Check>; ')

        except SocketError:
            errorList.append(u'не удалось установить соединение')
        except Exception, e:
            errorList.append(u'неизвестная ошибка: {0}'.format(forceString(e)))
        if errorList:
            clientExportRecord = db.getRecordEx(tableClientRecipeExport, '*', where='client_id = %d' % clientId)
            if clientExportRecord is None:
                clientExportRecord = tableClientRecipeExport.newRecord()
            clientExportRecord.setValue('client_id', toVariant(clientId))
            clientExportRecord.setValue('sentToMiac', toVariant(0))
            clientExportRecord.setValue('errorList', toVariant(', '.join(errorList)))
            db.insertOrUpdate(tableClientRecipeExport, clientExportRecord)
            failures.append(msg)
        if self.tracefilename is not None:
            tracefile.close()
        return failures

    def sendRecipes(self, recipesIdList):
        loc = UploadServiceLocator()
        tracefile = open(self.tracefilename, 'a') if self.tracefilename is not None else None
        port = loc.getUploadServiceSoap(url=(self.url + '/drugstore/UploadService.asmx'), tracefile=tracefile, transdict={'timeout': 5})
        failures = False  # Возможно лучше словарь и возвращать сразу список ошибок

        db = self.db
        tableDrugRecipe = db.table('DrugRecipe')
        stmt = u'''
        SELECT
            DrugRecipe.*,
            Client.SNILS,
            Client.id AS clientId,
            Organisation.OGRN,
            OrgStructure.bookkeeperCode AS FOMS,
            rbFinance.code AS typeFinanceCode,
            Person.federalCode AS personCode,
            dlo_rbMNN.code AS mnnCode,
            dlo_rbTradeName.code AS trnCode,
            dlo_rbMNN.name AS mnnName,
            dlo_rbTradeName.name AS trnName,
            dlo_rbIssueForm.code AS cureFormCode,
            DloDrugFormulary_Item.dosageLs AS dosageLs,
            DloDrugFormulary_Item.qnt AS packQnt
        FROM
            DrugRecipe
            INNER JOIN Event ON DrugRecipe.event_id = Event.id
            INNER JOIN Client ON Event.client_id = Client.id
            INNER JOIN Person ON Event.execPerson_id = Person.id
            INNER JOIN Organisation ON Event.org_id = Organisation.id
            INNER JOIN OrgStructure ON Person.orgStructure_id = OrgStructure.id
            INNER JOIN DloDrugFormulary_Item ON DrugRecipe.formularyItem_id = DloDrugFormulary_Item.id
            INNER JOIN dlo_rbMNN ON DloDrugFormulary_Item.mnn_id = dlo_rbMNN.id
            INNER JOIN dlo_rbTradeName ON DloDrugFormulary_Item.tradename_id=dlo_rbTradeName.id
            INNER JOIN dlo_rbIssueForm ON DloDrugFormulary_Item.issueForm_id = dlo_rbIssueForm.id
            INNER JOIN rbFinance ON DrugRecipe.finance_id = rbFinance.id
        WHERE
            %s
        '''
        query = db.query(stmt % tableDrugRecipe['id'].inlist(recipesIdList))
        drugRecords = []
        try:
            # msg = None
            msg = RecipesClientSaveSoapIn()
            msg._clientId = self.clientId
            msg._recipes = ns0.ArrayOfRecipeClient_Def('_recipes')
            msg._recipes._RecipeClient = []
            while query.next():
                record = query.record()
                drugRecord = db.getRecord(tableDrugRecipe, '*', forceInt(record.value('id')))
                drugRecords.append(drugRecord)
                recipe = ns0.RecipeClient_Def('_RecipeClient')
                msg._recipes._RecipeClient.append(recipe)

                recipe._Seria, recipe._Number = forceString(record.value('number')).split('#')
                SNILS = record.value('SNILS')
                if not forceString(record.value('SNILS')):
                    tableFakeSNILS = db.table('ClientFakeSNILS')
                    fakeSnilsRecord = db.getRecordEx(tableFakeSNILS, '*',
                                                     where='client_id = %s' % forceString(record.value('clientId')))
                    if fakeSnilsRecord:
                        SNILS = fakeSnilsRecord.value('fakeSNILS')
                recipe._Snils = formatSNILS(forceString(SNILS))
                recipe._LpuOgrn = forceString(record.value('OGRN'))
                recipe._LpuFoms = forceString(record.value('FOMS'))
                recipe._DoctorCode = forceString(record.value('personCode'))
                recipe._MkbCode = forceString(record.value('mkb'))
                recipe._FundingSourceCode = {'70': 1, '71': 2, '72': 3, '73': 0}[forceString(record.value('typeFinanceCode'))]
                recipe._PrivilegeCode = forceString(record.value('socCode'))
                periods = [u'5d', u'10d', u'1m', u'3m'] if self.getYear(forceDateTime(record.value('dateTime'))) < 2016 else [u'5d', u'15d', u'30d', u'90d']
                recipe._ValidPeriodCode = periods[forceInt(record.value('term'))]
                recipe._PayPercent = {100: 0, 50: 1}[forceInt(record.value('percentage'))]
                recipe._IsVk = forceBool(record.value('isVk'))
                recipe._Dosage = forceString(record.value('dosageLs'))  # dlo_rbDosage.miacCode
                recipe._Quantity = 1000 * forceDouble(record.value('qnt')) / forceDouble(record.value('packQnt'))
                if not record.value('cureFormCode').isNull():
                    recipe._CureformCode = forceString(record.value('cureFormCode'))
                # recipe._UnitCode = forceString(record.value('unitCode'))

                if forceBool(record.value('printMnn')) and forceString(record.value('mnnName')) != '~' or record.value('trnName').isNull():
                    recipe._IsTrn = False
                    recipe._MnnCode = forceString(record.value('mnnCode')) if not record.value('mnnCode').isNull() else forceString(record.value('mnnName'))
                else:
                    recipe._IsTrn = True
                    recipe._TrnCode = forceString(record.value('trnCode')) if not record.value('trnCode').isNull() else forceString(record.value('trnName'))

                recipe._IssueDate = self.toDateTuple(forceDateTime(record.value('dateTime')))

                recipeStatus = forceInt(record.value('status'))
                recipe._IsAnnulled = False if not recipeStatus else True
                if recipeStatus:
                    recipe._CauseOfAnnulment = recipeStatusNames[recipeStatus]

                recipe._PatientFound = False
                recipe._LpuFound = False
                recipe._DoctorFound = False
                recipe._MkbFound = False
                recipe._FundingSourceFound = False
                recipe._PrivilegeCodeFound = False
                recipe._NosologyFound = False
                recipe._ProgramFound = False
                recipe._ValidPeriodFound = False
                recipe._PayPercentFound = False
                recipe._TrnFound = False
                recipe._MnnFound = False
                recipe._CureformFound = False
                recipe._UnitFound = False
                recipe._CauseOfAnnulmentFound = False
                recipe._Uploaded = False

                # recipe._IsDeleted = False

            if not drugRecords:
                return failures

            resp = port.RecipesClientSave(msg)

            for index, recipeResponse in enumerate(resp._RecipesClientSaveResult._RecipeClient):
                errorList = []
                drugRecord = drugRecords[index]

                if recipeResponse._Uploaded:
                    drugRecord.setValue('sentToMiac', toVariant(1))
                    drugRecord.setValue('errorList', toVariant(''))
                    db.updateRecord(tableDrugRecipe, drugRecord)
                else:
                    if hasattr(recipeResponse, '_RecipeCheck'):
                        if forceString(recipeResponse._RecipeCheck).startswith(u'Статус рецепта'):
                            drugRecord.setValue('sentToMiac', toVariant(1))
                            drugRecord.setValue('errorList', toVariant(''))
                            db.updateRecord(tableDrugRecipe, drugRecord)
                            return
                        errorList.append(forceString(recipeResponse._RecipeCheck))
                    if not recipeResponse._PatientFound:
                        errorList.append(u'пациент не найден')
                    if not recipeResponse._LpuFound:
                        errorList.append(u'ЛПУ не найдено')
                    if not recipeResponse._DoctorFound:
                        errorList.append(u'врач не найден')
                    if not recipeResponse._MkbFound:
                        errorList.append(u'код МКБ не найден')
                    if not recipeResponse._FundingSourceFound:
                        errorList.append(u'источник финансирования не найден')
                    if not recipeResponse._ValidPeriodFound:
                        errorList.append(u'срок действия рецепта не найден')
                    if not recipeResponse._PayPercentFound:
                        errorList.append(u'процент оплаты не найден')
                    if not recipeResponse._CureformFound:
                        errorList.append(u'код формы выпуска препарата не найден')
                    if recipeResponse._IsTrn:
                        if not recipeResponse._TrnFound:
                            errorList.append(u'торговое название не найдено')
                    else:
                        if not recipeResponse._MnnFound:
                            errorList.append(u'МНН не найдено')

                if errorList:
                    drugRecord.setValue('sentToMiac', toVariant(0))
                    drugRecord.setValue('errorCode', toVariant(', '.join(errorList)))
                    db.updateRecord(tableDrugRecipe, drugRecord)
                    failures = True

        except SocketError:
            for drugRecord in drugRecords:
                drugRecord.setValue('sentToMiac', toVariant(0))
                drugRecord.setValue('errorCode', toVariant(u'не удалось установить соединение'))
                db.updateRecord(tableDrugRecipe, drugRecord)
            failures = True
        except Exception, e:
            for drugRecord in drugRecords:
                drugRecord.setValue('sentToMiac', toVariant(0))
                drugRecord.setValue('errorCode', toVariant(u'неизвестная ошибка: {0}'.format(forceString(e))))
                db.updateRecord(tableDrugRecipe, drugRecord)
            failures = True
        if self.tracefilename is not None:
            tracefile.close()

        return failures

def main():
    import sys
    app = QtCore.QCoreApplication(sys.argv)

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '10.226.1.130',
                      'port' : 3306,
                      'database' : 's11vm2',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}


    db = connectDataBaseByInfo(connectionInfo)
    sender = CR23RecipeService(4134, url='http://10.0.1.154/', db=db, tracefilename='recipesDebug.log')
    try:
        sender.checkClient(2112605)
        sender.sendClient(2112605)
        sender.sendRecipes([13940])
    except SocketError:
        print 'connection problem!'
    db.close()

if __name__ == '__main__':
    main()