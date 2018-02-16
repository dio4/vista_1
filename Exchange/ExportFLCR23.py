# -*- coding: utf-8 -*-

import os.path
import shutil
from PyQt4 import QtCore, QtGui
from zipfile import ZIP_DEFLATED, ZipFile

from Exchange.R23.attach.Utils import CBookkeeperCode
from Exchange.Utils import CExportHelperMixin
from Ui_ExportFLCR23Page1 import Ui_ExportFLCR23Page1
from Ui_ExportFLCR23Page2 import Ui_ExportFLCR23Page2
from library.Utils import calcAgeInDays, calcAgeInYears, forceDate, forceInt, forceRef, forceString, forceStringEx, formatSNILS, formatSex, nameCase, pyDate, toVariant, trim
from library.database import CUnionTable
from library.dbfpy.dbf import Dbf


def exportFLCR23(widget):
    wizard = CExportWizard(widget)
    wizard.exec_()


class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта ФЛК (Краснодарский край)')
        self.tmpDir = ''
        self.lpuCode = None

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R23FLC')
        return self.tmpDir

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            self.validateCurrentPage()
            self.restart()
        else:
            QtGui.QWizard.done(self, result)

    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportPage1(QtGui.QWizardPage, Ui_ExportFLCR23Page1, CExportHelperMixin):
    TF_OGRN = '1022301607393'  # ОГРН ТФОМС КК

    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        CExportHelperMixin.__init__(self)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт данных ФЛК')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.aborted = False
        self.done = False
        self.parent = parent
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.exportedClients = set()

    def initializePage(self):
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setExportMode(False)

        currentDate = QtCore.QDate.currentDate()
        prevMonthDate = currentDate.addMonths(-1)
        if currentDate.day() <= 10:  # с вероятностью 99.9% в начале месяца выгружаются данные за предыдущий месяц
            begDate = QtCore.QDate(prevMonthDate.year(), prevMonthDate.month(), 1)
            endDate = QtCore.QDate(prevMonthDate.year(), prevMonthDate.month(), prevMonthDate.daysInMonth())
        else:
            begDate = QtCore.QDate(currentDate.year(), currentDate.month(), 1)
            endDate = currentDate

        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)

        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

        self.logBrowser.clear()

    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)

    def log(self, str, forceLog=False):
        self.logBrowser.append(str)
        self.logBrowser.update()

    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.lpuCode = None
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query

    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

    def getDbfBaseName(self):
        return u'P%s.DBF' % forceString(self.edtOrgCode.text())

    def getZipFileName(self):
        endDate = self.edtEndDate.date()
        return '%s%s.zip' % (forceString(endDate.toString('yyMM')), forceString(self.edtOrgCode.text()))

    def exportInt(self):
        dbf, query = self.prepareToExport()

        lpuCode = forceString(self.edtOrgCode.text())
        self.log(u'ЛПУ: код инфис: "%s".' % lpuCode)

        if not lpuCode:
            self.log(u'<b><font color=red>ОШИБКА</font></b>:'
                     u'Для текущего ЛПУ не задан код инфис', True)

        self.exportedClients = set()

        # Составляем множество событий, содержащих услуги с модернизацией
        query.exec_()  # встаем перед первой записью

        while query.next():
            QtGui.qApp.processEvents()
            if self.aborted:
                break
            self.progressBar.step()
            self.process(dbf, query.record(), lpuCode)

        dbf.close()

    def createDbf(self):
        u"""Создает структуру для паспортной части реестра счетов."""
        dbfName = os.path.join(self.parent.getTmpDir(), self.getDbfBaseName())
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('NS', 'N', 5, 0),  # номер реестра счетов (п. 1 примечаний) обязательное
            ('VS', 'C', 1),  # тип реестра счетов (п. 2;4 примечаний) обязательное SPR21
            ('DATS', 'D'),  # дата формирования реестра счетов (п. 3 примечаний) обязательное
            ('SN', 'N', 12, 0),  # номер персонального счета	обязательное
            ('DATPS', 'D'),  # дата формирования персонального счета обязательное
            ('CODE_MO', 'C', 5),  # код МО, оказавшей медицинскую помощь обязательное SPR01
            ('PL_OGRN', 'C', 15),  # ОГРН плательщика
            ('FIO', 'C', 30),  # фамилия (п. 5 примечаний) обязательное
            ('IMA', 'C', 20),  # имя (п. 5 примечаний) обязательное
            ('OTCH', 'C', 30),  # отчество (п. 5 примечаний)
            ('POL', 'C', 1),  # символьное (1)	пол (М/Ж) (п. 6 примечаний) обязательное
            ('DATR', 'D'),  # дата рождения (п. 7 примечаний) обязательное
            ('SNILS', 'C', 14),  # СНИЛС
            ('OKATO_OMS', 'C', 5),  # код ОКАТО территории страхования по ОМС обязательное для инокраевых SPR39
            ('SPV', 'N', 1),  # вид полиса
            ('SPS', 'C', 10),  # серия полиса ОМС обязательное
            ('SPN', 'C', 20),  # номер полиса ОМС обязательное
            # ('STAT_P', 'C', 1),     # статус представителя пациента обязательное SPR41
            ('Q_G', 'C', 10),  # признак "Особый случай" при регистрации обращения за медицинской помощью (п. 8 примечаний) SPR42
            # ('NOVOR', 'C', 9),      # признак новорожденного (п. 18 примечаний)
            ('FAMP', 'C', 30),  # фамилия родителя (представителя) пациента (п. 5 примечаний) обязательное
            ('IMP', 'C', 20),  # имя родителя (представителя) пациента (п. 5 примечаний) обязательное
            ('OTP', 'C', 30),  # отчество родителя (представителя) пациента (п. 5 примечаний)
            ('POLP', 'C', 1),  # пол представителя пациента (М/Ж) (п. 6 примечаний) Да (при STAT_P <> “0”)
            ('DATRP', 'D'),  # дата рождения представителя пациента (п. 7 примечаний) Да (при STAT_P <> “0”)
            ('C_DOC', 'N', 2, 0),  # код типа документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний) SPR43
            ('S_DOC', 'C', 10),  # серия документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
            ('N_DOC', 'C', 15),  # номер документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
            ('DATN', 'D'),  # дата начала лечения обязательное
            ('DATO', 'D'),  # дата окончания лечения обязательное
        )

        return dbf

    def createQuery(self):
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        tblClientPolicy = db.table('ClientPolicy')
        tblClientDocument = db.table('ClientDocument')
        tblClientRelation = db.table('ClientRelation')
        tblInsurer = db.table('Organisation').alias('Insurer')
        tblDocumentType = db.table('rbDocumentType')
        tblPolicyType = db.table('rbPolicyType')
        tblPolicyKind = db.table('rbPolicyKind')
        tblRelationType = db.table('rbRelationType')
        tblRelative = db.table('Client').alias('Relative')
        tblRelativeDocument = db.table('ClientDocument').alias('RelativeDocument')
        tblRelativeDocumentType = db.table('rbDocumentType').alias('RelativeDocumentType')

        relStmt1 = db.selectStmt(table=tblClientRelation.innerJoin(tblRelationType, [tblRelationType['id'].eq(tblClientRelation['relativeType_id']),
                                                                                     tblRelationType['isBackwardRepresentative'].eq(1)]),
                                 fields=[tblClientRelation['client_id'].alias('currClientId'),
                                         tblClientRelation['relative_id'].alias('relativeId'),
                                         tblClientRelation['freeInput'].alias('relativeFreeInput'),
                                         tblRelationType['code'].alias('relationCode'),
                                         tblRelationType['id'].alias('relationType_id')],
                                 where=tblClientRelation['deleted'].eq(0))

        relStmt2 = db.selectStmt(table=tblClientRelation.innerJoin(tblRelationType, [tblRelationType['id'].eq(tblClientRelation['relativeType_id']),
                                                                                     tblRelationType['isDirectRepresentative'].eq(1)]),
                                 fields=[tblClientRelation['relative_id'].alias('currClientId'),
                                         tblClientRelation['client_id'].alias('relativeId'),
                                         tblClientRelation['freeInput'].alias('relativeFreeInput'),
                                         tblRelationType['code'].alias('relationCode'),
                                         tblRelationType['id'].alias('relationType_id')],
                                 where=tblClientRelation['deleted'].eq(0))

        tblRel = CUnionTable(db, relStmt1, relStmt2, 'rel')

        cols = [tblClient['id'].alias('clientId'),
                tblClient['lastName'].alias('clientLastName'),
                tblClient['firstName'].alias('clientFirstName'),
                tblClient['patrName'].alias('clientPatrName'),
                tblClient['birthDate'].alias('clientBirthDate'),
                tblClient['sex'].alias('clientSex'),
                tblClient['SNILS'].alias('clientSNILS'),
                tblClientPolicy['serial'].alias('policySerial'),
                tblClientPolicy['number'].alias('policyNumber'),
                tblClientPolicy['insuranceArea'].alias('policyInsuranceArea'),
                tblPolicyType['code'].alias('policyTypeCode'),
                tblPolicyKind['code'].alias('policyKindCode'),
                tblInsurer['shortName'].alias('insurerName'),
                tblInsurer['OGRN'].alias('insurerOGRN'),
                tblInsurer['OKATO'].alias('insurerOKATO'),
                tblInsurer['area'].alias('insurerArea'),
                tblDocumentType['code'].alias('documentTypeCode'),
                tblDocumentType['regionalCode'].alias('documentTypeRegionalCode'),
                tblClientDocument['serial'].alias('documentSerial'),
                tblClientDocument['number'].alias('documentNumber'),
                tblRelative['id'].alias('relativeId'),
                tblRelative['lastName'].alias('relativeLastName'),
                tblRelative['firstName'].alias('relativeFirstName'),
                tblRelative['patrName'].alias('relativePatrName'),
                tblRelative['sex'].alias('relativeSex'),
                tblRelative['birthDate'].alias('relativeBirthDate'),
                tblRelativeDocument['serial'].alias('relativeDocumentSerial'),
                tblRelativeDocument['number'].alias('relativeDocumentNumber'),
                tblRelativeDocumentType['code'].alias('relativeDocTypeCode'),
                tblRelativeDocumentType['regionalCode'].alias('relativeDocTypeRegCode'),
                tblRelationType['code'].alias('relationTypeCode'),
                'rel.relativeFreeInput as relativeFreeInput',
                ]

        queryTable = tblClient.leftJoin(tblClientDocument, tblClientDocument['id'].eqEx('getClientDocumentId(Client.id)'))
        queryTable = queryTable.leftJoin(tblDocumentType, tblDocumentType['id'].eq(tblClientDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tblRel, tblClient['id'].eqEx('rel.currClientId'))
        queryTable = queryTable.leftJoin(tblRelative, tblRelative['id'].eqEx('rel.relativeId'))
        queryTable = queryTable.leftJoin(tblRelativeDocument, tblRelativeDocument['id'].eqEx('getClientDocument(rel.relativeId)'))
        queryTable = queryTable.leftJoin(tblRelativeDocumentType, tblRelativeDocumentType['id'].eq(tblRelativeDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tblRelationType, tblRelationType['id'].eqEx('rel.relationType_id'))

        orgStructureId = self.cmbOrgStructure.value()
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()

        cond = []
        group = [tblClient['id']]

        tblEvent = db.table('Event')
        queryTable = queryTable.innerJoin(tblEvent, tblEvent['client_id'].eq(tblClient['id']))
        cols.extend([tblEvent['id'].alias('eventId'),
                     tblEvent['setDate'].alias('eventSetDate'),
                     tblEvent['execDate'].alias('eventExecDate')])
        cond.extend([tblEvent['deleted'].eq(0),
                     tblEvent['execDate'].dateBetween(begDate, endDate)])

        if orgStructureId:
            tblPerson = db.table('Person')
            tblOrgStructureAncestors = db.table('OrgStructure_Ancestors')
            queryTable = queryTable.innerJoin(tblPerson, tblPerson['id'].eq(tblEvent['execPerson_id']))
            queryTable = queryTable.innerJoin(tblOrgStructureAncestors, tblOrgStructureAncestors['id'].eq(tblPerson['orgStructure_id']))
            cond.append('isOrgStructureDescendant(%s, OrgStructure_Ancestors.fullPath, Person.orgStructure_id)' % orgStructureId)

        group.append(tblEvent['id'])

        queryTable = queryTable.leftJoin(tblClientPolicy, tblClientPolicy['id'].eq(tblEvent['clientPolicy_id']))
        queryTable = queryTable.leftJoin(tblPolicyType, tblPolicyType['id'].eq(tblClientPolicy['policyType_id']))
        queryTable = queryTable.leftJoin(tblPolicyKind, tblPolicyKind['id'].eq(tblClientPolicy['policyKind_id']))
        queryTable = queryTable.leftJoin(tblInsurer, tblInsurer['id'].eq(tblClientPolicy['insurer_id']))

        order = [tblClient['id'], tblRelationType['code']]

        stmt = db.selectStmt(queryTable, cols, cond, group, order)
        return db.query(stmt)

    @staticmethod
    def getSocStatusFederalCode(clientId):
        db = QtGui.qApp.db
        tableSocStatus = db.table('ClientSocStatus')
        tableSocStatusClass = db.table('rbSocStatusClass')
        tableSocStatusType = db.table('rbSocStatusType')

        table = tableSocStatus.innerJoin(tableSocStatusClass, [tableSocStatusClass['id'].eq(tableSocStatus['socStatusClass_id']),
                                                               tableSocStatusClass['code'].eq('12')])
        table = table.innerJoin(tableSocStatusType, tableSocStatusType['id'].eq(tableSocStatus['socStatusType_id']))
        cols = [
            tableSocStatusType['regionalCode'].alias('fedCode')
        ]
        cond = [
            tableSocStatus['client_id'].eq(clientId),
            tableSocStatus['deleted'].eq(0)
        ]

        rec = db.getRecordEx(table, cols, cond)
        return forceString(rec.value('fedCode')) if rec is not None else ''

    def process(self, dbfP, record, codeLPU):
        db = QtGui.qApp.db
        birthDate = forceDate(record.value('clientBirthDate'))
        # Номер стат.талона
        clientId = forceRef(record.value('clientId'))
        eventId = forceRef(record.value('eventId'))

        insurerArea = forceString(record.value('insurerArea'))
        isAlien = insurerArea[:2] != QtGui.qApp.defaultKLADR()[:2]

        if not ((clientId, eventId) in self.exportedClients):
            dbfRecord = dbfP.newRecord()
            # номер реестра счетов (п. 1 примечаний) обязательное
            # dbfRecord['NS'] = 123 #self.edtRegistryNumber.value()
            # тип реестра счетов (п. 2;4 примечаний) обязательное SPR21
            # dbfRecord['VS'] = accType
            # дата формирования реестра счетов (п. 3 примечаний) обязательное
            dbfRecord['DATS'] = pyDate(QtCore.QDate())
            # номер персонального счета	обязательное
            dbfRecord['SN'] = eventId  # В импорте ФЛК в этом поле ожидается Event.id
            # дата формирования персонального счета обязательное
            dbfRecord['DATPS'] = pyDate(QtCore.QDate())
            # код медицинской организации в системе ОМС,
            # предоставившей медицинскую помощь обязательное SPR01
            dbfRecord['CODE_MO'] = codeLPU
            # ОГРН плательщика
            dbfRecord['PL_OGRN'] = forceString(record.value('insurerOGRN')) or (self.TF_OGRN if isAlien else '')
            #  фамилия (п. 5 примечаний) обязательное
            dbfRecord['FIO'] = nameCase(forceString(record.value('clientLastName')))
            # имя (п. 5 примечаний) обязательное
            dbfRecord['IMA'] = nameCase(forceString(record.value('clientFirstName')))
            # отчество (п. 5 примечаний)
            patrName = forceString(record.value('clientPatrName'))
            dbfRecord['OTCH'] = nameCase(patrName)
            # пол (М/Ж) (п. 6 примечаний) обязательное
            dbfRecord['POL'] = formatSex(record.value('clientSex')).upper()
            # дата рождения (п. 7 примечаний) обязательное
            dbfRecord['DATR'] = pyDate(birthDate)
            # СНИЛС
            dbfRecord['SNILS'] = formatSNILS(forceString(record.value('clientSNILS')))
            # статус пациента обязательное SPR40
            age = calcAgeInYears(birthDate, QtCore.QDate.currentDate())

            # код ОКАТО территории страхования по ОМС обязательное для инокраевых SPR39
            dbfRecord['OKATO_OMS'] = forceStringEx(record.value('insurerOKATO'))

            if not dbfRecord['OKATO_OMS']:
                insurerName = forceString(record.value('insurerName'))
                self.log(u'<b><font color=orange>Внимание</font></b>:' \
                         u' ОКАТО для ОМС "%s" не задан, пытаюсь определить по области страхования!' % insurerName)

                dbfRecord['OKATO_OMS'] = forceString(db.translate('kladr.KLADR', 'CODE', insurerArea, 'OCATD', idFieldName='CODE'))
                if not dbfRecord['OKATO_OMS']:
                    self.log(u'<b><font color=red>Внимание</font></b>:' \
                             u' ОКАТО для ОМС "%s" не задан!' % forceString(record.value('insurerName')))

                    policyInsuranceArea = forceString(record.value('policyInsuranceArea'))
                    if policyInsuranceArea:
                        dbfRecord['OKATO_OMS'] = forceString(db.translate('kladr.KLADR', 'CODE', policyInsuranceArea, 'OCATD', idFieldName='CODE'))

            # серия полиса ОМС обязательное
            dbfRecord['SPS'] = forceString(record.value('policySerial'))
            # номер полиса ОМС обязательное
            dbfRecord['SPN'] = forceString(record.value('policyNumber'))
            # дата начала действия полиса ОМС (п. 8 примечаний) обязательное для инокраевых

            # серия документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
            documentSerial = forceString(record.value('documentSerial'))
            if documentSerial:
                dbfRecord['S_DOC'] = documentSerial
            # номер документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
            documentNumber = forceString(record.value('documentNumber'))
            if documentNumber:
                dbfRecord['N_DOC'] = documentNumber

            # Признак новорожденого
            isLittleStrangerAge = calcAgeInDays(birthDate, forceDate(record.value('eventSetDate'))) < 90
            exportAsLittleStranger = isLittleStrangerAge and (dbfRecord['S_DOC'] == '' and dbfRecord['N_DOC'] == '')
            # (dbfRecord['SPS'] == '' and dbfRecord['SPN'] == '') and \

            # признак "Особый случай" при регистрации обращения
            # за медицинской помощью (п. 9 примечаний) SPR42
            flags = ''
            if dbfRecord['SPS'] == '' and dbfRecord['SPN'] == '' and forceDate(record.value('eventExecDate')) <= QtCore.QDate(2016, 9, 30):  # нет данных по полису:
                flags += ' 1'
            if exportAsLittleStranger:  # новорождённый:
                flags += ' 2'
            if patrName == '':
                flags += ' 4'
            flags += ' ' + self.getSocStatusFederalCode(clientId)

            dbfRecord['Q_G'] = trim(flags)

            representativeInfo = self.getClientRepresentativeInfo(clientId)
            if exportAsLittleStranger and representativeInfo:
                # статус представителя пациента  обязательное для инокраевых SPR41
                # dbfRecord['STAT_P'] = representativeInfo.get('relationTypeCode', '0')[:1] # 'C', 1),
                # фамилия родителя (представителя) пациента (п. 5 примечаний) обязательное для инокраевых
                dbfRecord['FAMP'] = representativeInfo.get('lastName', '')
                # имя родителя (представителя) пациента (п. 5 примечаний) обязательное для инокраевых
                dbfRecord['IMP'] = representativeInfo.get('firstName', '')
                # отчество родителя (представителя) пациента (п. 5 примечаний)
                dbfRecord['OTP'] = representativeInfo.get('patrName', '')
                s = representativeInfo.get('serial', '')
                n = representativeInfo.get('number', '')

                # код типа документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний) SPR43
                dbfRecord['C_DOC'] = representativeInfo.get('documentTypeRegionalCode', 18 if s or n else 0) % 100
                # серия документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
                dbfRecord['S_DOC'] = s
                # номер документа, удостоверяющего личность пациента (представителя) (п. 10 примечаний)
                dbfRecord['N_DOC'] = n

                sexp = representativeInfo.get('sex', 0)
                dbfRecord['POLP'] = u'М' if sexp == 1 else u'Ж' if sexp == 2 else u'0'

                dbfRecord['DATRP'] = pyDate(representativeInfo.get('birthDate', None))

                dbfRecord['FIO'] = dbfRecord['FAMP']
                dbfRecord['IMA'] = dbfRecord['IMP']
                dbfRecord['OTCH'] = dbfRecord['OTP']
                dbfRecord['POL'] = dbfRecord['POLP']
                dbfRecord['DATR'] = dbfRecord['DATRP']
                dbfRecord['SNILS'] = formatSNILS(representativeInfo.get('SNILS', ''))
                dbfRecord['SPS'] = representativeInfo.get('policySerial', '')
                dbfRecord['SPN'] = representativeInfo.get('policyNumber', '')

            # код типа документа, удостоверяющего личность пациента (представителя)
            # (п. 10 примечаний) SPR43
            documentRegionalCode = forceInt(record.value('documentTypeRegionalCode')) % 100
            if documentRegionalCode and (documentSerial or documentNumber):
                dbfRecord['C_DOC'] = documentRegionalCode

            dbfRecord['SPV'] = forceInt(record.value('policyKindCode')) % 10
            setDate = forceDate(record.value('eventSetDate')).toPyDate()
            execDate = forceDate(record.value('eventExecDate')).toPyDate()
            dbfRecord['DATN'] = setDate
            dbfRecord['DATO'] = execDate

            dbfRecord.store()
            self.exportedClients.add((clientId, eventId))

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

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self):
        orgStructureId = self.cmbOrgStructure.value()
        orgCode, sectionCode = CBookkeeperCode.getOrgCode(orgStructureId)
        self.edtOrgCode.setText(orgCode or '')

        # @QtCore.pyqtSlot(QtCore.QDate)
        # def on_edtBegDate_dateChanged(self, date):
        #     begDate = self.edtBegDate.date()
        #     endDate = QtCore.QDate(begDate.year(), begDate.month(), begDate.daysInMonth())
        #     self.edtEndDate.setMinimumDate(begDate.addDays(1))
        #     self.edtEndDate.setMinimumDate(endDate)
        #     self.edtEndDate.setDate(endDate)

        # @QtCore.pyqtSlot(QtCore.QDate)
        # def on_edtEndDate_dateChanged(self, date):
        #     pass


class CExportPage2(QtGui.QWizardPage, Ui_ExportFLCR23Page2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт данных ФЛК')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "Завершить"')

        self.pathIsValid = True

    def initializePage(self):
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(QtGui.qApp.preferences.appPrefs.get('ExportR23FLCExportDir', homePath))
        self.edtDir.setText(exportDir)

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        u"""
            Завершение экспорта. Создание архива и добавление в него файла выгрузки.
        """
        baseName = self.parent.page1.getDbfBaseName()
        zipFileName = self.parent.page1.getZipFileName()
        zipFilePath = os.path.join(forceStringEx(self.parent.getTmpDir()), zipFileName)

        zf = ZipFile(zipFilePath, 'w', allowZip64=True)
        filePath = os.path.join(forceStringEx(self.parent.getTmpDir()), os.path.basename(baseName))
        zf.write(filePath, os.path.basename(self.parent.page1.getDbfBaseName()), ZIP_DEFLATED)
        zf.close()

        dst = os.path.join(forceStringEx(self.edtDir.text()), zipFileName)
        success, result = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))

        if success:
            QtGui.qApp.preferences.appPrefs['ExportR23FLCExportDir'] = toVariant(self.edtDir.text())
        return success

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))

    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                                                     u'Выберите директорию для сохранения файла выгрузки в ОМС Краснодарского края',
                                                     forceStringEx(self.edtDir.text()),
                                                     QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

# if __name__ == '__main__':
#     import sys
#     from library.database import connectDataBaseByInfo
#     from s11main import CS11mainApp
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp = app
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#     connectionInfo = {'driverName'      : 'mysql',
#                       'host'            : '192.168.0.207',
#                       'port'            : 3306,
#                       'database'        : 's11vm22',
#                       'user'            : 'dbuser',
#                       'password'        : 'dbpassword',
#                       'connectionName'  : 'vista-med',
#                       'compressData'    : True,
#                       'afterConnectFunc': None}
#     QtGui.qApp.currentOrgId = lambda: 230493
#     QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
#     exportFLCR23(None)
