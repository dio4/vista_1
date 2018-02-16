#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from zipfile import ZipFile

from PyQt4 import QtCore, QtGui

from Accounting.Utils   import updateAccounts
from Events.Utils       import getEventLengthDays
from library.database   import decorateString
from library.exception import CDatabaseException
from library.Utils      import forceDate, forceInt, forceDouble, forceRef, forceString, forceStringEx, toVariant, getVal, calcAgeInDays, calcAgeInYears, nameCase, \
    MKBwithoutSubclassification
from Registry.Utils     import selectLatestRecord

from Import131XML import CXMLimport
from Utils import CExportHelperMixin, tbl

from Ui_ImportR46XML import Ui_Dialog


def ImportR46XML(widget, contractId):
    dlg = CImportR46XML(contractId)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR53FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR53FileName'] = toVariant(dlg.edtFileName.text())


class CImportR46XML(QtGui.QDialog, Ui_Dialog, CXMLimport):
    version = '1,02'
    version201112 = '2.1'

    importNormal = 0
    import201112 = 1

    persZglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True, 'FILENAME1' : True}
    zglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True}
    schetFields = {'CODE': True, 'CODE_MO': True, 'YEAR': True, 'MONTH': True, 'NSCHET': True, 'DSCHET': True, 'SUMMAV': True,
                            'COMENTS': False, 'SUMMAP': False, 'SANK_MEK': False, 'SANK_MEE': False, 'SANK_EKMP': False, 'PLAT': False}
    pacientFields = {'ID_PAC': True, 'SMO': False, 'VPOLIS': True, 'SPOLIS': False, 'NPOLIS': False, 'NOVOR': True,
                            'SMO_OGRN': False, 'SMO_OK': False, 'SMO_NAM': False}
    sluchFields = {'PODR': False, 'IDDOKT': True, 'IDCASE': True, 'USL_OK': True, 'VIDPOM': True, 'FOR_POM': False, 'EXTR': False, 'LPU': False, 'PROFIL': False, 'DET': True,
                            'NHISTORY': True, 'DATE_1': True, 'DATE_2': True, 'DS0': False, 'DS1': True, 'DS2': False, 'CODE_MES1': False, 'CODE_MES2': False, 'RSLT': True,
                            'ISHOD': True, 'VERS_SPEC': False, 'PRVS': True, 'IDSP': True, 'ED_COL': False, 'TARIF': False, 'SUMV': True,
                            'OPLATA': False, 'SUMP': False, 'REFREASON': False, 'CODE_MES1': False, 'CODE_MES2': False,
                            'SANK_MEK': False, 'SANK_MEE': False, 'SANK_EKMP': False, 'COMENTSL': False, 'OS_SLUCH': False, 'LPU_1': False, 'NPR_MO': False}
    uslFields = {'PROFIL': False, 'IDSERV': True, 'LPU': False, 'DET': True, 'DATE_IN': True, 'DATE_OUT': True, 'DS': True, 'KOL_USL': True,
                        'TARIF': True, 'SUMV_USL': True, 'PRVS': True, 'COMENTU': False, 'PODR': False, 'CODE_USL': True, 'CODE_MD': True, 'LPU_1': False}

    persFields = {'ID_PAC': True, 'FAM': True, 'IM': True, 'OT': False, 'W': True, 'DR': True, 'FAM_P': False, 'IM_P': False,
                        'OT_P': False, 'W_P': False, 'DR_P': False, 'MR': False, 'DOCTYPE': False, 'DOCSER': False, 'DOCNUM': False, 'DOCSERIAL': False, 'DOCNUMBER': False, 'SNILS': False,
                        'OKATOG': False, 'OKATOP': False, 'COMENTP': False, 'COMENTZ': False, 'DOST': False}

    sexMap = {u'М':1,  u'Ж':2}
    idmap = {}

    def __init__(self, contractId):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CXMLimport.__init__(self, self.log)
        self.currcontractid = None
        self.accountId=-1 #accountId
        self.accountItemIdList={} #accountItemIdList
        self.progressBar.setFormat('%p%')
        self.checkName()
        self.errorPrefix = ''
        self.nProcessed = 0
        self.nProcessedSum = 0.0
        self.nAccepted = 0
        self.nAcceptedSum = 0
        self.nPayed = 0
        self.contractId = contractId
        self.nRefused = 0
        self.nNotFound = 0
        self.tblContractTariff = tbl('Contract_Tariff')
        self.tblAction = tbl('Action')
        self.tblActionType = tbl('ActionType')
        self.tblPayRefuseType = tbl('rbPayRefuseType')
        self.tblEventType = tbl('EventType')
        self.tblDiagnosis = tbl('Diagnosis')
        self.tblDiagnostic = tbl('Diagnostic')
        self.tblEvent = tbl('Event')
        self.tblContract = tbl('Contract')
        self.tblContractSpec = tbl('Contract_Specification')
        self.tableAccountItem = tbl('Account_Item')
        self.tableAccount = tbl('Account')
        self.tableClient = tbl('Client')
        self.tblClientDocument = tbl('ClientDocument')
        self.tblClientPolicy = tbl('ClientPolicy')
        self.tblRbService = tbl('rbService')
        self.tblVisit = tbl('Visit')
        self.tblLittleStranger = tbl('Event_LittleStranger')
        self.tableAcc=self.db.join(self.tableAccountItem, self.tableAccount,
            'Account_Item.master_id=Account.id')
        self.prevContractId = None
        self.financeTypeOMS = forceRef(self.db.translate('rbFinance',
            'code', '2', 'id'))
        self.policyTypeTerritorial = forceRef(self.db.translate('rbPolicyType',
            'code', '1', 'id'))
        self.policyTypeIndustrial = forceRef(self.db.translate('rbPolicyType',
            'code', '2', 'id'))
        self.currentAccountOnly = False
        self.confirmation = ''
        self.serviceCache = {}
        self.accountItemIdListCache = {}
        self.clientCache = {}
        self.clientByAccountItemIdCache = {}
        self.refuseTypeIdCache = {}
        self.insurerArea = QtGui.qApp.defaultKLADR()[:2]
        self.insurerCache = {}
        self.policyKindIdCache = {}
        self.mapMkbDesc = {}
        self.chkOnlyCurrentAccount.setVisible(False)
        self.chkImportPayed.setVisible(False)
        self.chkImportRefused.setVisible(False)
        self.edtConfirmation.setVisible(False)
        self.label_2.setVisible(False)
        self.accMonth = None
        self.accYear = None
        self.accSum = 0
        self.curaccid = None
        self.eventHasVisit = False
        self.dummyPerson = None
        record = self.db.getRecordEx('Person', 'id', 'federalCode = \'\' AND speciality_id IS NULL', order='code != \'-1\'')
        if record: self.dummyPerson = forceRef(record.value('id'))

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (HM*.zip)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)


    def err2log(self, e):
        self.log.append(self.errorPrefix+e)

    def afterEnd(self):
        if self.tempInfisCode:
            logFile = QtCore.QFile('%s.txt' % self.tempInfisCode)
            logFile.open(QtCore.QFile.Append)
            logFile.write(self.log.toPlainText().toUtf8())
            logFile.close()
        try:
            self.db.record('r85ImportLog')
        except CDatabaseException:
            stmt = u'''CREATE TABLE r85ImportLog (
                importDate DATETIME NOT NULL COMMENT "Время проведения импорта",
                payerInfis VARCHAR(20) DEFAULT NULL COMMENT "инфис-код плательщика",
                recipientInfis VARCHAR(20) DEFAULT NULL COMMENT "инфис-код получателя",
                contract_id INT(11) NOT NULL COMMENT 'Договор, по которому произведен импорт {Contract}',
                account_id INT(11) NOT NULL COMMENT 'Счет {Account}',
                errors TEXT NOT NULL DEFAULT '' COMMENT 'Список ошибок',
                accepted INT(11) NOT NULL DEFAULT 0 COMMENT 'Принято',
                accepted_sum DOUBLE NOT NULL DEFAULT 0.0 COMMENT 'Принято на сумму',
                refused INT(11) NOT NULL DEFAULT 0 COMMENT 'Отказано',
                refused_sum DOUBLE NOT NULL DEFAULT 0.0 COMMENT 'Отказано на сумму'
            ) COMMENT='Временная таблица для хранения результатов импорта счетов в Республике Крым' ENGINE=InnoDB;
            '''
            self.db.query(stmt)

        insertStmt = '''
        INSERT INTO r85ImportLog
        (`importDate`, `contract_id`, `payerInfis`, `recipientInfis`, `account_id`, `errors`, `accepted`, `accepted_sum`, `refused`, `refused_sum`)
        VALUES ('%s', %d, %s, %s, %d, %s, %d, %.2f, %d, %.2f)
        ''' % (forceString(QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)),
        self.contractId, self.plat, self.lpu,
        self.accountId, decorateString(forceString(self.log.toPlainText())),
        self.nAccepted, self.nAcceptedSum, self.nProcessed - self.nAccepted, self.nProcessedSum - self.nAcceptedSum)
        self.db.query(insertStmt)


    def startImport(self):
        self.progressBar.setFormat('%p%')
        self.lpu = ''
        self.plat = ''
        n=0
        self.currosn = None
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0
        self.nProcessedSum = 0.0
        self.nAcceptedSum = 0.0
        self.nRegAcceptedSum = 0.0
        self.nRegRejectedSum = 0.0
        self.nAccepted = 0
        self.xmlErrorsList = []
        self.mekErrorsList = []
        self.curnzap = ''
        self.accSum = 0
        self.accMonth = None
        self.accYear = None
        self.idmap = {}
        self.smomap = {}
        self.idmeklist = {}
        zipFileName = forceStringEx(self.edtFileName.text())
        fn = QtCore.QFileInfo(zipFileName)
        baseName = fn.baseName()
        persZipFileName = '%s/L%s.zip' % (fn.dir().absolutePath(), baseName[1:])
        fileName = '%s.xml' % baseName
        persFileName = 'L%s.xml' % baseName[1:]
        archive = ZipFile(forceString(zipFileName), "r")
        persArchive = ZipFile(forceString(persZipFileName), 'r')
        if not fileName in archive.namelist():
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'В архиве отсутствует файл с услугами %s.' % fileName)
            return
        if not persFileName in persArchive.namelist():
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'В архиве с персональными данными отсутствует файл %s.' % persFileName)
            return
        outFile = QtCore.QTemporaryFile()
        persOutFile = QtCore.QTemporaryFile()

        if not outFile.open(QtCore.QFile.WriteOnly):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'Не удаётся открыть временный файл для записи %s:\n%s.' % (outFile, outFile.errorString()))
            return
        if not persOutFile.open(QtCore.QFile.WriteOnly):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'Не удаётся открыть временный файл для записи %s:\n%s.' % (outFile, persOutFile.errorString()))
            return

        data = archive.read(fileName) #read the binary data
        outFile.write(data)
        outFile.close()
        fileInfo = QtCore.QFileInfo(outFile)

        persData = persArchive.read(persFileName)
        persOutFile.write(persData)
        persOutFile.close()
        persFileInfo = QtCore.QFileInfo(persOutFile)

        # (name,  fileExt) = os.path.splitext(fileName)
        # isDBF = (fileExt.lower() == '.dbf')
        self.currentAccountOnly = self.chkOnlyCurrentAccount.isChecked()
        self.confirmation = self.edtConfirmation.text()
        self.accountIdSet = set()
        self.currosn = None #current MEK code
        self.currperosn = None #current MEK code for person file
        self.kolusl = 0
        self.koluslacc = 0

        if not self.confirmation:
            self.log.append(u'нет подтверждения')
            return

        # if not isDBF:
        inFile = QtCore.QFile(fileInfo.filePath())
        fn = QtCore.QFileInfo(fileName)
        self.tempInfisCode = forceString(baseName[2:baseName.indexOf('S')])
        if self.tempInfisCode.startswith('460'):
            self.tempInfisCode = self.tempInfisCode[3:]
        self.filename = baseName
        self.persfilename = 'L%s' % baseName[1:]

        persInFile = QtCore.QFile(persFileInfo.filePath())

        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл для чтения %s:\n%s.' \
                                  % (fileInfo.filePath(), inFile.errorString()))
            return
        if not persInFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл персональных данных для чтения %s:\n%s.' \
                                  % (persFileInfo.filePath(), persInFile.errorString()))
            return

        self.progressBar.reset()
        self.progressBar.setValue(0)
        # self.progressBar.setFormat(u'%v записей' if isDBF else u'%v байт')
        self.progressBar.setFormat(u'%v байт')
        self.stat.setText("")
        # size = max(len(inFile) if isDBF else inFile.size(), 1)
        size = max(inFile.size(), 1)
        self.progressBar.setMaximum(size)
        self.labelNum.setText(u'размер источника: '+str(size))
        self.btnImport.setEnabled(False)

        # if not isDBF:
        if self.readFile(persInFile):
            proc = self.readFile
        if (not proc(inFile)):
            if self.abort:
                self.err2log(u'! Прервано пользователем.')
            else:
                self.err2log(u'! Ошибка: файл %s, %s' % (fileName,
                                            self.errorString()))
        persInFile.close()
        inFile.close()
        self.stat.setText(
            u'обработано: %d; принято: %d; отказано: %d' % \
            (self.nProcessed, self.nAccepted, self.nProcessed - self.nAccepted))

        rec = None
        if self.curaccid:
            rec = self.db.getRecord('Account', '*', self.curaccid)
        if rec:
            rec.setValue('amount', toVariant(self.kolusl))
            rec.setValue('payedSum', toVariant(self.nRegAcceptedSum)) #self.nAcceptedSum
            rec.setValue('sum', toVariant(self.nRegAcceptedSum + self.nRegRejectedSum))
            rec.setValue('payedAmount', toVariant(self.koluslacc)) #self.nAccepted
            rec.setValue('refusedAmount', toVariant(self.kolusl - self.koluslacc)) #self.nProcessed - self.nAccepted
            rec.setValue('refusedSum', toVariant(self.nRegRejectedSum)) #self.nProcessedSum - self.nAcceptedSum
            self.db.updateRecord('Account', rec)

        self.err2log(u"""<table>
	      <tr><td bgcolor='#EEEEEE' colspan=4 align=center><B><BR>Отчет по файлу %s</BR></B></td></tr>
          <tr><td bgcolor='#EEEEEE' align=left><nobr>обработано записей</nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %d </B></td>
          <td bgcolor='#EEEEEE' align=center><nobr>на сумму</nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %0.2f </B></td></tr>
	      <tr><td bgcolor='#EEEEEE' align=left><nobr>приняты к оплате, то есть прошедшие МЭК: </nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %d </B></nobr></td>
          <td bgcolor='#EEEEEE' align=center><nobr>на сумму</nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %0.2f </B></td></tr>
          <tr><td bgcolor='#EEEEEE' align=left><nobr>не приняты к оплате, то есть не прошедшие МЭК: </nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %d </B></nobr></td>
          <td bgcolor='#EEEEEE' align=center><nobr>на сумму</nobr></td><td bgcolor='#EEEEEE' align=center><nobr><B> %0.2f </B></td></tr>
          </table>""" % (self.filename, self.nProcessed, self.nProcessedSum, self.nAccepted, self.nAcceptedSum,
                                    self.nProcessed - self.nAccepted, self.nProcessedSum - self.nAcceptedSum))

        #generate error xml file
        if len(self.xmlErrorsList):
            flkfilename = '%s/F%s.xml' % (fn.dir().absolutePath(), self.filename[1:26])

            outFile = QtCore.QFile(flkfilename)
            outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)

            out = C79XmlStreamWriter(self)
            out.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
            out.writeFileHeader(outFile, self.filename, 'F%s' % self.filename[1:26])

            for val in self.xmlErrorsList:
                out.writeRecord(val)

            out.writeFileFooter()
            outFile.close()
            self.err2log(u'Сгенерирован файл с протоколом ФЛК: %s' % flkfilename)
            self.err2log(u'Лог ошибок по ФЛК:')
            for val in self.xmlErrorsList:
                self.err2log(val['COMMENT'])

        if len(self.mekErrorsList):
            self.err2log(u'Лог ошибок по МЭК:')
            for val in self.mekErrorsList:
                self.err2log(val['COMMENT'])

        updateAccounts(list(self.accountIdSet))


    def readFile(self, device):
        self.setDevice(device)

        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'ZL_LIST' or self.name() == 'PERS_LIST':
                    self.readList() # Новый формат
                else:
                    self.readUnknownElement()
                    self.addFLKError(904, None, None, None, u'Неизвестный элемент: ' + self.name().toString())

            if self.hasError():
                self.addFLKError(904, None, None, None, u'Ошибка в xml файле.')
                return False

        return True


    def addFLKError(self, code, name=None, base=None, nzap=None, comment=None):
        error = {}
        error['OSHIB'] = code
        if name:
            error['IM_POL'] = name
        if base:
            error['BAS_EL'] = base
        if nzap:
            error['N_ZAP'] = nzap
        if comment:
            error['COMMENT'] = comment

        self.xmlErrorsList.append(error)

    def getMEKErrorId(self, OSNtext):
        #atronah: простите за столь адекватное название переменной, мне так проще понять, о чем речь, чем через MEKError =)
        #FIXME: точка здесь - корень зла.
        result = self.refuseTypeIdCache.get(OSNtext, None)
        if result is None:
            result = self.db.translate('rbPayRefuseType', 'code', '%s.' % OSNtext, 'id') #OSN
            if not result:
                 result = self.db.translate('rbPayRefuseType', 'flatCode', 'default', 'id')
            self.refuseTypeIdCache[OSNtext] = result
        return result

    def addMEKError(self, OSNtext, name=None, base=None, nzap=None, comment=None):
        error = {'OSHIB': self.getMEKErrorId(OSNtext)}
        self.currosn = OSNtext
        if name:
            error['IM_POL'] = name
        if base:
            error['BAS_EL'] = base
        if nzap:
            error['N_ZAP'] = nzap
        if comment:
            error['COMMENT'] = comment
        else:
            error['COMMENT'] = u'%s, имя: %s, базовый элемент: %s, номер записи: %s' % (OSNtext, name, base, nzap) #TODO: find comment text by OSN

        self.mekErrorsList.append(error)


    def checkXMLGroup(self, row, itemsmap, base, nzap):
        proc = True
        for key, val in itemsmap.iteritems():
            if val:
                if not row.has_key(key):
                    self.addFLKError(901, key, base, nzap, u'Отсутствует обязательное поле %s, базовый элемент: %s, номер записи: %s' % (key, base, nzap))
                    self.addMEKError('5.1.3', key, base, nzap)
                    proc = False
                elif not row[key] or row[key] == '':
                    self.addMEKError('5.1.3', key, base, nzap)
                    self.addFLKError(902, key, base, nzap, u'Не заполнено обязательное поле %s, базовый элемент: %s, номер записи: %s' % (key, base, nzap))
                    proc = False
        return proc

    def readList(self):
        assert self.isStartElement() and (self.name() == 'ZL_LIST' or self.name() == 'PERS_LIST')
        bPersFile = self.name() == 'PERS_LIST'
        procPers = True
        curSchetOsn = None


        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'ZGLV':
                    result = {}
                    processed = True
                    result, processed = self.readGroup('ZGLV', self.zglvFields if not bPersFile else self.persZglvFields, result, processed)
                    if not self.hasError():
                        self.processHeader(result, self.import201112)
                elif self.name() == 'SCHET':
                    self.currosn = None
                    curSchetOsn = None
                    result = {}
                    processed = True
                    result, processed = self.readGroup('SCHET', self.schetFields, result, processed)
                    self.accSum = forceDouble(result.get('SUMMAV', 0))
                    self.accYear  = forceInt(result.get('YEAR', ''))
                    self.accMonth = forceInt(result.get('MONTH', ''))
                    self.processAccount(result)
                    curSchetOsn = self.currosn
                elif self.name() == 'ZAP':
                    self.currosn = curSchetOsn
                    (processed, summa) = self.readZap()
                    if processed:
                        self.nAccepted += 1
                        self.nAcceptedSum += summa
                    self.nProcessed += 1
                    self.nProcessedSum += summa
                elif self.name() == 'PERS':
                    self.currosn = None
                    result = {}
                    processed = True
                    result, processed = self.readGroup('PERS', self.persFields, result, processed)
                    procPers = self.processPatientPers(result)
                    self.currosn = None
                else:
                    self.readUnknownElement()
                    self.addFLKError(904, None, None, None, u'Неизвестный элемент: ' + self.name().toString())

            if self.hasError():
                self.addFLKError(904, None, None, None, u'Ошибка в xml файле.')

        if self.accSum and self.nProcessedSum != self.accSum:
            self.addMEKError('5.1.2', 'SUMV', 'SLUCH')
            self.nAccepted = 0
            self.nAcceptedSum = 0
        if not procPers:
            self.nAccepted = 0
            self.nAcceptedSum = 0


    def readZap(self):
        assert self.isStartElement() and self.name() == 'ZAP'
        result = {}
        summa = 0.0
        processed = True

        self.mapEventMesAi = {} # Для пересчета цен
        self.mapEventAge = {}
        self.mapEventAction = {} # Храним все коды услуг в каждом обращении
        self.mapEventVisitAi = {} # Храним id первого визита в обращении
        self.mapEventUet = {} # Все уеты по обращению
        self.mapAiToAmbService = {} # Для проверки "законченных случаев по поликлинике"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'N_ZAP':
                    result['N_ZAP'] = forceString(self.readElementText())
                    self.curnzap = result['N_ZAP']
                elif self.name() == 'PR_NOV':
                    result['PR_NOV'] = forceString(self.readElementText())
                elif self.name() == 'PACIENT':
                    proc = True
                    result, proc = self.readGroup('PACIENT', self.pacientFields, result, proc)
                    if not proc:
                        processed = False
                    if not self.processPatient(result):
                        processed = False
                    self.clientBirthday = forceDate(QtGui.qApp.db.translate('Client', 'id', self.idpac, 'birthDate'))
                    self.clientSex = forceInt(QtGui.qApp.db.translate('Client', 'id', self.idpac, 'sex'))
                elif self.name() == 'SLUCH':
                    (proc, summasl) = self.readSluch()
                    summa += summasl
                    if not proc:
                        processed = False
                else:
                    self.readUnknownElement()
                    self.addFLKError(904, None, None, None, u'Неизвестный элемент: ' + self.name().toString())

            if self.hasError():
                self.addFLKError(904, None, None, None, u'Ошибка в xml файле.')
        for eventId, aiId in self.mapEventMesAi.items():
            coeff = 1
            age = self.mapEventAge.get(eventId, -1)
            if age >= 0:
                if age < 5:
                    coeff += 0.2
                elif age >= 75:
                    coeff += 0.3
            actions = self.mapEventAction.get(eventId, [])
            if '1.1.0050' in actions or '1.2.0050' in actions:
                coeff += 0.1
            if '1.1.1121' in actions or '1.2.1121' in actions or filter(lambda x: x.lower().startswith('a16.'), actions): #AZ
                coeff += 0.05

            if coeff > 1:
                r = self.db.getRecordEx('Account_Item', 'id, price, sum', 'id = %s' % aiId)
                r.setValue('sum', toVariant(forceDouble(r.value('sum'))*coeff))
                self.db.updateRecord('Account_Item', r)
        for eventId, uet in self.mapEventUet.items():
            visitAiId = self.mapEventVisitAi.get(eventId, None)
            if visitAiId:
                r = self.db.getRecordEx('Account_Item', 'id, price, sum, uet', 'id=%s' % visitAiId)
                r.setValue('sum', toVariant(forceDouble(r.value('price')) * forceDouble(uet)))
                r.setValue('uet', toVariant(uet))
                self.db.updateRecord('Account_Item', r)

        for (eventId, codeusl), itemList in self.mapAiToAmbService.items():
            # FIXME: craz: Это все надо переписать, так жить нельзя.
            if len(itemList) > 1:
                itemList.sort(key=lambda x: 0 if not x[1] else 1 if x[1] == '6.18.7' else 2)
                aiId, refuse = itemList[0]
                # refuseTypeId = self.getMEKErrorId('5.1.4')
                # if forceRef(refuseTypeId):
                self.db.query(u'UPDATE Account_Item ai set ai.refuseType_id = NULL, number = \'Оплачено\', note=\'\' WHERE ai.event_id = %s and ai.master_id = %s AND ai.note LIKE \'%%Несоответствие кода услуги диагнозу, полу, возрасту, профилю отделения%%\'' % (eventId, self.curaccid))
                # elif refuse == '6.18.7':
                #     self.db.query(u'UPDATE Account_Item ai set refuseType_id = NULL, number = \'Оплачено\', note=\'\' WHERE ai.id = %s' % aiId)
                for aiId, refuse in itemList[1:]:
                    cond = u'ai.price = 0, ai.sum = 0'
                    if refuse == '6.18.7':
                        cond += u', ai.refuseType_id = NULL, ai.number = \'Оплачено\', ai.note=\'\''
                    stmt = u'UPDATE Account_Item ai SET %s WHERE ai.id = %s' % (cond, aiId)
                    self.db.query(stmt)

        return processed, summa


    def readSluch(self):
        self.currosn = None
        assert self.isStartElement() and self.name() == 'SLUCH'
        if not self.idpac:
            return False, 0.0
        result = {}
        resultusllist = []
        summa = 0.0
        processed = True
        self.eventHasVisit = False
        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'USL':
                    resultusl = {}
                    proc = True
                    resultusl, processed = self.readGroup('USL', self.uslFields, resultusl, proc)
                    if not proc:
                        processed = False
                    resultusllist.append(resultusl)
                elif self.name() in self.sluchFields.keys():
                    result[forceString(self.name().toString())] = forceString(self.readElementText())
                else:
                    self.readUnknownElement()
                    self.addFLKError(904, None, None, None, u'Неизвестный элемент: ' + self.name().toString())

            if self.hasError():
                self.addFLKError(904, None, None, None, u'Ошибка в xml файле.')

        if not self.checkXMLGroup(result, self.sluchFields, 'SLUCH', self.curnzap):
            processed = False
        eventid, lpuid, bProc, isNew = self.processSluch(result, len(resultusllist) > 0)
        if not bProc:
            processed = False
        sumv = forceDouble(result.get('SUMV', '0'))
        # FIXME: Временно закомментировано для Крыма.
        # if not sumv:
        #     self.addMEKError('5.1.5', 'SUMV', 'SLUCH', self.curnzap)
        #     processed = False
        summa += sumv
        if not eventid:
            self.err2log(u'Ошибка. пустой eventid.')
        elif not lpuid:
            self.err2log(u'Ошибка. пустой lpuid.')
        else:
            if len(resultusllist):
                summAllUsl = 0
                for usl in resultusllist:
                    susl = usl.get('SUMV_USL', '')
                    summUsl = forceDouble(susl) if susl else 0
                    # FIXME: Временно закомментировано для Крыма.
                    # if not summUsl:
                    #     self.addMEKError('5.1.5', 'SUMV_USL', 'USL', self.curnzap)
                    #     processed = False
                    summAllUsl += summUsl
                    if not self.processUsl(usl,
                                           eventid,
                                           lpuid,
                                           result.get('IDSP', ''),
                                           result.get('USL_OK', ''), isNew):
                        processed = False
                if summAllUsl and (not summAllUsl == forceDouble(result.get('SUMV', 0))):
                    self.addMEKError('5.1.2', 'SUMV_USL', 'USL', self.curnzap)
                    processed = False
            if not self.eventHasVisit:
                self.createDummyVisit(eventid, result, isNew)
        return processed, summa

    def readGroup(self, name, fields, result=None, processed=False):
        if not result:
            result = {}
        fieldslist = fields.keys()
        r = CXMLimport.readGroup(self, name, fieldslist)
        if processed:
            processed = self.checkXMLGroup(r, fields, name, self.curnzap)
        for key, val in r.iteritems():
            result[key] = val

        return result, processed

    def getMkbDesc(self, mkb):
        mkb = MKBwithoutSubclassification(mkb)
        result = self.mapMkbDesc.get(mkb, None)
        if result is None:
            tblMKB = self.db.table('MKB_Tree')
            record = self.db.getRecordEx('MKB', 'sex, MTR, OMS', tblMKB['DiagID'].eq(mkb))
            sex, mtr, oms = 0, 0, 0
            if record:
                sex = forceInt(record.value('sex'))
                oms = forceInt(record.value('OMS'))
                mtr = forceInt(record.value('MTR'))
            result = (sex, oms, mtr)
            self.mapMkbDesc[mkb] = result
        return result

    def processUsl(self, row, eventid, lpuid, sluchidsp, uslok, isNewSluch):
        processed = True
        #creating rbservice
        codeusl = row.get('CODE_USL', '')
        if codeusl:
            rbserviceid = self.db.translate('rbService', 'code', codeusl, 'id')
            if not rbserviceid:
                self.addMEKError('5.3.1', 'CODE_USL', 'USL', self.curnzap)
                return False
            if re.match('^3\..\.1\.', codeusl) and forceDouble(row.get('KOL_USL', 0)) == 1 and codeusl not in ('3.1.1.171', '3.2.1.171', '3.1.1.089', '3.1.1.090'):
                self.addMEKError('6.18.7', 'CODE_USL', 'USL', self.curnzap)
            if re.match('^3\..\.2\.', codeusl) and forceDouble(row.get('KOL_USL', 0)) != 1 and codeusl not in ('3.1.2.171', '3.2.2.171', '3.1.2.089', '3.1.2.090'):
                self.addMEKError('6.18.7', 'CODE_USL', 'USL', self.curnzap)
            dateIn = QtCore.QDate.fromString(row.get('DATE_IN', ''), QtCore.Qt.ISODate)

            ageDays = calcAgeInDays(self.clientBirthday, dateIn)
            if codeusl == '1.2.0550' and ageDays > 28:
                self.addMEKError('6.18.7', 'CODE_USL', 'USL', self.curnzap)
            elif codeusl == '1.2.0680' and ageDays <= 28:
                self.addMEKError('6.18.7', 'CODE_USL', 'USL', self.curnzap)

            uet = forceDouble(self.db.translate('rbService', 'id', rbserviceid, 'adultUetDoctor'))
            # FIXME: craz: Предположим, что у всех интересующих нас услуг стоит УЕТ. Если это не так, то придется проверять по коду услуги (и еще учесть, что все это в рамках законченного случая и уеты могут стоять не у всех услуг..)
            # 3.1.1.085, 3.1.1.089, 3.1.1.090, 3.1.1.171, 3.1.2.085, 3.1.2.089, 3.1.2.090, 3.1.2.171, 3.1.3.085, 3.1.3.089, 3.1.3.090, 3.1.3.171, 3.1.4.089, 3.1.4.090, 3.1.4.171, 3.2.1.085, 3.2.1.086, 3.2.1.171, 3.2.2.085, 3.2.2.086, 3.2.2.171, 3.2.3.085, 3.2.3.086, 3.2.3.171, 3.2.4.086, 3.2.4.171
            if uet:
                self.mapEventUet.setdefault(eventid, 0.0)
                self.mapEventUet[eventid] += forceDouble(self.db.translate('rbService', 'id', rbserviceid, 'adultUetDoctor')) * forceDouble(row.get('KOL_USL', 0.0))

            tarif = row.get('TARIF', '')
            contarrec = None
            if tarif and self.currcontractid:
                # contarrec = self.db.getRecordEx('Contract_Tariff', 'id, tariffType, unit_id', 'master_id=%s and price=%0.2f and service_id=%s and deleted=0' %
                #                                      (self.currcontractid, forceDouble(tarif), forceString(rbserviceid)))
                contarrec = self.db.getRecordEx('Contract_Tariff', 'id, tariffType, unit_id, price, federalPrice', 'master_id=%s and service_id=%s and deleted=0' %
                                                      (self.currcontractid, forceString(rbserviceid)))
                if not contarrec:
                    self.addMEKError('5.4.1', 'TARIF', 'USL', self.curnzap)
                    processed = False
                else:
                    #creating action item
                    #checking tarifftype
                    smo = self.smomap.get(self.idpac)
                    if smo and smo not in ('85001', '85002', '85003') and \
                                    sluchidsp in ('25','26','27','31','35','36','37','38','39'):
                        tarif = forceDouble(contarrec.value('federalPrice'))
                    else:
                        tarif = forceDouble(contarrec.value('price'))

                    tariftype = forceInt(contarrec.value('tariffType'))
                    if tariftype in (2,5):
                        actiontype = self.db.getRecordEx('ActionType', 'id', 'code = \'%s\' and deleted=0' % codeusl)
                        #self.db.translate('ActionType', 'code', codeusl, 'id')
                        if not actiontype:
                            #TODO: error
                            return False

                        actiontypeid = forceRef(actiontype.value('id'))

                        #TODO: code doctor
                        persid = None
                        code_md = row.get('CODE_MD', '')
                        if code_md:
                            persRecord = self.db.getRecordEx('Person', 'id', 'code=\'%s\' and deleted = 0' % code_md)
                            if persRecord: persid = forceString(persRecord.value('id'))
                        if not persid:
                            self.addMEKError('5.1.3', 'CODE_MD', 'USL', self.curnzap)

                        oldAction = None
                        actionid = None
                        if not isNewSluch:
                            dateOut = QtCore.QDate.fromString(row.get('DATE_OUT', ''), QtCore.Qt.ISODate)
                            dateIn = QtCore.QDate.fromString(row.get('DATE_IN', ''), QtCore.Qt.ISODate)
                            oldAction = self.db.getRecordEx(self.tblAction, 'id, begDate, directionDate, person_id, setPerson_id, amount',
                                                            [self.tblAction['event_id'].eq(eventid),
                                                           self.tblAction['actionType_id'].eq(actiontypeid),
                                                           self.tblAction['endDate'].dateEq(dateOut),
                                                           self.tblAction['deleted'].eq(0)])
                            if oldAction:
                                # self.log.append('oldAction')
                                actionid = forceRef(oldAction.value('id'))
                                oldAction.setValue('begDate', toVariant(dateIn))
                                oldAction.setValue('directionDate', toVariant(dateIn))
                                oldAction.setValue('person_id', toVariant(persid))
                                oldAction.setValue('setPerson_id', toVariant(persid or self.dummyPerson))
                                oldAction.setValue('amount', toVariant(row.get('KOL_USL', '')))
                                self.db.updateRecord(self.tblAction, oldAction)

                        if not oldAction:
                            reca = {}
                            reca['deleted'] = 0
                            reca['actionType_id'] = actiontypeid
                            reca['event_id'] = eventid
                            reca['idx'] = 0
                            reca['directionDate'] = row.get('DATE_IN', '')
                            reca['status'] = 2
                            reca['setPerson_id'] = persid or self.dummyPerson
                            reca['isUrgent'] = 0
                            reca['begDate']   = row.get('DATE_IN', '')
                            reca['plannedEndDate'] = row.get('DSCHET', '') #'0000-00-00 00:00:00'
                            reca['endDate']  = row.get('DATE_OUT', '')

                            date1 = QtCore.QDate().fromString(reca['begDate'], QtCore.Qt.ISODate)
                            date2 = QtCore.QDate().fromString(reca['endDate'], QtCore.Qt.ISODate)

                            #FIXME: Временно отключено
                            # if date1.year() != self.accYear or date1.month() != self.accMonth:
                            #     self.addMEKError('5.1.6', 'DATE_IN', 'USL', self.curnzap)
                            #     processed = False
                            # if date2.year() != self.accYear or date2.month() != self.accMonth:
                            #     self.addMEKError('5.1.6', 'DATE_OUT', 'USL', self.curnzap)
                            #     processed = False
                            reca['person_id'] = persid or self.dummyPerson
                            reca['amount'] =  row.get('KOL_USL', '')
                            reca['uet'] = uet
                            reca['expose'] = 1
                            reca['payStatus']  = 0
                            reca['account'] = 0
                            reca['MKB']  = row.get('DS', '')
                            reca['finance_id'] = 2
                            reca['contract_id'] = self.currcontractid
                            reca['org_id'] = lpuid
                            reca['preliminaryResult'] = 0
                            reca['duration'] = 0
                            reca['periodicity'] = 0
                            reca['aliquoticity'] = 0
                            record = self.tblAction.newRecord()
                            for key, val in reca.iteritems():
                                record.setValue(key, toVariant(val))
                            actionid = self.db.insertRecord(self.tblAction, record)

                        self.mapEventAction.setdefault(eventid, []).append(codeusl)
                        #if not oldAction or not forceRef(self.db.translate('Account_Item', 'action_id', actionid, 'id')):
                        recai = {}
                        recai['deleted'] = 0
                        recai['master_id']  = self.curaccid
                        recai['event_id'] = eventid
                        recai['action_id'] = actionid
                        recai['price'] = tarif
                        recai['tariff_id'] = forceString(contarrec.value('id'))
                        if sluchidsp:
                            recai['unit_id'] = forceString(self.db.translate(
                                        'rbMedicalAidUnit', 'federalCode', sluchidsp, 'id'))
                        else:
                            recai['unit_id'] = forceRef(contarrec.value('unit_id'))
                        recai['amount'] = row.get('KOL_USL', '')
                        recai['uet'] = 0
                        if codeusl.startswith('3.'):
                            recai['sum'] = tarif
                        else:
                            recai['sum'] = round(forceDouble(tarif) * forceDouble(recai['amount']), 2) #row.get('SUMV_USL', '')
                        recai['service_id'] = rbserviceid
                        # FIXME: Временно закомментировано для Крыма.
                        # if not recai['sum']:
                        #     self.addMEKError('5.1.5', 'SUMV_USL', 'USL', self.curnzap)

                        oldAI = self.db.getRecordEx(self.tableAccountItem, 'id', [self.tableAccountItem['action_id'].eq(actionid),
                                                                          self.tableAccountItem['deleted'].eq(0),
                                                                          self.tableAccountItem['date'].isNotNull(),
                                                                          self.tableAccountItem['refuseType_id'].isNull()])

                        if oldAI:
                            mekid = self.getMEKErrorId('5.7.1')
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        elif self.currosn:
                            if self.currosn == '6.18.7':
                                mekid = self.getMEKErrorId('5.1.4')
                                recai['note'] = u'Несоответствие кода услуги диагнозу, полу, возрасту, профилю отделения'
                            else:
                                mekid = self.getMEKErrorId(self.currosn)
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        else:
                            recai['number'] = u'Оплачено'
                        recai['date'] = QtCore.QDate().currentDate()
                        newusl = None
                        if recai.get('unit_id', ''):
                            record = self.tableAccountItem.newRecord()
                            for key, val in recai.iteritems():
                                record.setValue(key, toVariant(val))
                            newusl = self.db.insertRecord(self.tableAccountItem, record)
                            if self.currosn:
                                self.nRegRejectedSum += forceDouble(recai['sum'])
                            else:
                                self.nRegAcceptedSum += forceDouble(recai['sum'])
                                self.koluslacc += 1
                            self.kolusl += 1
                        # else:
                            # self.addMEKError('5.4.1', 'IDSP', 'SLUCH', self.idpac)
                            # processed = False
                            #self.err2log(u'Ошибка. Не найден unit_id. IDSP = \'%s\'' % sluchidsp)
                    elif tariftype == 10:
                        #TODO:
                        dateOut = QtCore.QDate.fromString(row.get('DATE_OUT', ''), QtCore.Qt.ISODate)
                        dateIn = QtCore.QDate.fromString(row.get('DATE_IN', ''), QtCore.Qt.ISODate)
                        mesRecord = self.db.getRecordEx('mes.MES', 'id, avgDuration', 'code = \'%s\' and deleted = 0' % codeusl)
                        eventTypeId = forceRef(self.db.translate('Event', 'id', eventid, 'eventType_id'))
                        eventLength = getEventLengthDays(dateIn, dateOut, False, eventTypeId)

                        sum = None
                        if mesRecord:
                            mesId = mesRecord.value('id')
                            mesSpecificationId = self.db.translate('rbMesSpecification', 'code', '0', 'id')
                            eventRecord = self.db.getRecordEx('Event', 'id, MES_id, mesSpecification_id', 'id=%s' % eventid)
                            eventRecord.setValue('MES_id', mesId)
                            eventRecord.setValue('mesSpecification_id', mesSpecificationId)
                            self.db.updateRecord(self.tblEvent, eventRecord)
                            avgDuration = forceDouble(mesRecord.value('avgDuration'))
                            sum = tarif
                            if ((codeusl.startswith('1') and eventLength < round(avgDuration * 0.7, 0)) or \
                                (codeusl.startswith('2') and eventLength < round(avgDuration * 0.9, 0))) \
                                    and codeusl not in ('1.1.1362', '1.2.1362'):
                                tarif = tarif / avgDuration
                                sum = round(tarif * eventLength, 2)

                        recai = {}
                        recai['deleted'] = 0
                        recai['master_id']  = self.curaccid
                        recai['event_id'] = eventid
                        recai['price'] = tarif
                        if sluchidsp:
                            recai['unit_id'] = forceString(self.db.translate(
                                'rbMedicalAidUnit', 'federalCode', sluchidsp, 'id'))
                        else:
                            recai['unit_id'] = forceRef(contarrec.value('unit_id'))
                        #FIXME: Нужно правильно заполнять на экспортирующей стороне, а не творить магию здесь
                        if uslok == '2':    # Дневной стационар
                            recai['amount'] = eventLength
                        else:
                            recai['amount'] = row.get('KOL_USL', '')
                        recai['uet'] = 0
                        recai['sum'] = row.get('SUMV_USL', '') if sum is None else sum
                        recai['service_id'] = rbserviceid
                        recai['tariff_id'] = forceString(contarrec.value('id'))
                        # FIXME: Временно закомментировано для Крыма.
                        # if not recai['sum']:
                        #     self.addMEKError('5.1.5', 'SUMV_USL', 'USL', self.curnzap)

                        oldAI = self.db.getRecordEx(self.tableAccountItem, 'id',
                                                        [self.tableAccountItem['event_id'].eq(eventid),
                                                        self.tableAccountItem['action_id'].isNull(),
                                                        self.tableAccountItem['visit_id'].isNull(),
                                                        self.tableAccountItem['service_id'].eq(forceRef(rbserviceid)),
                                                        self.tableAccountItem['deleted'].eq(0),
                                                        self.tableAccountItem['date'].isNotNull(),
                                                        self.tableAccountItem['refuseType_id'].isNull()])

                        if oldAI:
                            mekid = self.getMEKErrorId('5.7.1')
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        elif self.currosn:
                            if self.currosn == '6.18.7':
                                mekid = self.getMEKErrorId('5.1.4')
                                recai['note'] = u'Несоответствие кода услуги диагнозу, полу, возрасту, профилю отделения'
                            else:
                                mekid = self.getMEKErrorId(self.currosn)
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        else:
                            recai['number'] = u'Оплачено'
                        recai['date'] = QtCore.QDate().currentDate()
                        if recai.get('unit_id', ''):
                            record = self.tableAccountItem.newRecord()
                            for key, val in recai.iteritems():
                                record.setValue(key, toVariant(val))
                            newAiId = self.db.insertRecord(self.tableAccountItem, record)
                            if codeusl[:2] == '1.': #AZ
                                self.mapEventMesAi[eventid] = newAiId
                            if self.currosn:
                                self.nRegRejectedSum += forceDouble(recai['sum'])
                            else:
                                self.nRegAcceptedSum += forceDouble(recai['sum'])
                                self.koluslacc += 1
                            self.kolusl += 1
                        # else:
                        #     self.addMEKError('5.4.1', 'IDSP', 'SLUCH', self.idpac)
                        #     processed = False
                        #     #self.err2log(u'Ошибка. Не найден unit_id. IDSP = \'%s\'' % sluchidsp)
                    elif tariftype in (0, 14):
                        self.eventHasVisit = True

                        #TODO: code doctor
                        code_md = row.get('CODE_MD', '')
                        persid = None
                        if code_md:
                            persRecord = self.db.getRecordEx('Person', 'id', 'code=\'%s\' and deleted = 0' % code_md)
                            if persRecord: persid = forceString(persRecord.value('id'))
                        if not persid:
                            self.addMEKError('5.1.3', 'CODE_MD', 'USL', self.curnzap)

                        oldVisit = None
                        visitid = None
                        if not isNewSluch:
                            dateOut = QtCore.QDate.fromString(row.get('DATE_OUT', ''), QtCore.Qt.ISODate)
                            dateIn = QtCore.QDate.fromString(row.get('DATE_IN', ''), QtCore.Qt.ISODate)
                            oldVisit = self.db.getRecordEx(self.tblVisit, 'id, person_id', [self.tblVisit['event_id'].eq(eventid),
                                                           self.db.joinOr([self.tblVisit['service_id'].eq(rbserviceid), self.tblVisit['service_id'].isNull()]),
                                                           self.tblVisit['date'].dateEq(dateIn),
                                                           self.tblVisit['deleted'].eq(0)])
                            if oldVisit:
                                # self.log.append('oldVisit')
                                visitid = forceRef(oldVisit.value('id'))
                                oldVisit.setValue('person_id', toVariant(persid or self.dummyPerson))
                                self.db.updateRecord(self.tblVisit, oldVisit)

                        if not oldVisit:
                            recv = {}
                            recv['deleted'] = 0
                            recv['event_id'] = eventid
                            recv['scene_id'] = 1 # FIXME
                            recv['date'] = row.get('DATE_IN', '')
                            recv['visitType_id'] = 1 # FIXME
                            recv['person_id'] = persid or self.dummyPerson
                            recv['isPrimary'] = 1
                            recv['finance_id'] = 2
                            recv['service_id'] = rbserviceid
                            recv['payStatus']  = 0
                            recv['MKB']  = row.get('DS', '')

                            date1 = QtCore.QDate().fromString(recv['date'], QtCore.Qt.ISODate)

                            # FIXME: Временно отключено
                            # if date1.year() != self.accYear or date1.month() != self.accMonth:
                            #     self.addMEKError('5.1.6', 'DATE_IN', 'USL', self.curnzap)
                            #     processed = False

                            record = self.tblVisit.newRecord()
                            for key, val in recv.iteritems():
                                record.setValue(key, toVariant(val))
                            visitid = self.db.insertRecord(self.tblVisit, record)

                        # if not oldVisit or not forceRef(self.db.translate('Account_Item', 'visit_id', visitid, 'id')):
                        recai = {}
                        recai['deleted'] = 0
                        recai['master_id']  = self.curaccid
                        recai['event_id'] = eventid
                        recai['visit_id'] = visitid
                        recai['price'] = tarif
                        recai['tariff_id'] = forceString(contarrec.value('id'))
                        if sluchidsp:
                            recai['unit_id'] = forceString(self.db.translate(
                                'rbMedicalAidUnit', 'federalCode', sluchidsp, 'id'))
                        else:
                            recai['unit_id'] = forceRef(contarrec.value('unit_id'))
                        recai['amount'] = row.get('KOL_USL', '')
                        recai['uet'] = uet
                        if codeusl.startswith('3.') and not codeusl in ('3.1.0562', '3.1.0563'):
                            recai['sum'] = tarif
                        else:
                            recai['sum'] = round(tarif*forceDouble(recai['amount']), 2)#row.get('SUMV_USL', '')
                        recai['service_id'] = rbserviceid
                        # FIXME: Временно закомментировано для Крыма.
                        # if not recai['sum']:
                        #     self.addMEKError('5.1.5', 'SUMV_USL', 'USL', self.curnzap)

                        oldAI = self.db.getRecordEx(self.tableAccountItem, 'id', [self.tableAccountItem['visit_id'].eq(visitid),
                                                                          self.tableAccountItem['deleted'].eq(0),
                                                                          self.tableAccountItem['date'].isNotNull(),
                                                                          self.tableAccountItem['refuseType_id'].isNull()])

                        if oldAI:
                            mekid = self.getMEKErrorId('5.7.1')
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        elif self.currosn:
                            if self.currosn == '6.18.7':
                                mekid = self.getMEKErrorId('5.1.4')
                                recai['note'] = u'Несоответствие кода услуги диагнозу, полу, возрасту, профилю отделения'
                            else:
                                mekid = self.getMEKErrorId(self.currosn)
                            if mekid:
                                recai['refuseType_id'] = mekid
                            recai['number'] = u'Отказ по МЭК'
                        else:
                            recai['number'] = u'Оплачено'
                        recai['date'] = QtCore.QDate().currentDate()
                        newusl = None
                        if recai.get('unit_id', ''):
                            record = self.tableAccountItem.newRecord()
                            for key, val in recai.iteritems():
                                record.setValue(key, toVariant(val))
                            newAiId = self.db.insertRecord(self.tableAccountItem, record)
                            if not eventid in self.mapEventVisitAi:
                                self.mapEventVisitAi[eventid] = newAiId
                            if self.currosn:
                                self.nRegRejectedSum += forceDouble(recai['sum'])
                            else:
                                self.nRegAcceptedSum += forceDouble(recai['sum'])
                                self.koluslacc += 1
                            self.kolusl += 1
                            if re.match('^3\..\.1\.', codeusl) and codeusl not in ('3.1.1.171', '3.2.1.171', '3.1.1.089', '3.1.1.090'):
                                self.mapAiToAmbService.setdefault((eventid, codeusl), []).append((newAiId, self.currosn))
                        # else:
                        #     self.addMEKError('5.4.1', 'IDSP', 'SLUCH', self.idpac)
                        #     processed = False
                            #self.err2log(u'Ошибка. Не найден unit_id. IDSP = \'%s\'' % sluchidsp)


        return processed

    def createDummyVisit(self, eventid, row, isNewSluch):
        recv = {}
        iddokt = row.get('IDDOKT', '')
        persid = None
        if iddokt:
            persid = forceString(self.db.translate(
                    'Person', 'federalCode', iddokt, 'id'))
        dateIn = QtCore.QDate.fromString(row.get('DATE_1', ''), QtCore.Qt.ISODate)
        if not isNewSluch:
            oldVisit = self.db.getRecordEx(self.tblVisit, 'id, person_id', [self.tblVisit['event_id'].eq(eventid),
                                                           self.tblVisit['service_id'].isNull(),
                                                           self.tblVisit['date'].dateEq(dateIn),
                                                           self.tblVisit['deleted'].eq(0)])
            if oldVisit:
                oldVisit.setValue('person_id', toVariant(persid or self.dummyPerson))
                self.db.updateRecord(self.tblVisit, oldVisit)
                return

        recv['deleted'] = 0
        recv['event_id'] = eventid
        recv['scene_id'] = 1 # FIXME
        recv['date'] = row.get('DATE_1', '')
        recv['visitType_id'] = 1 # FIXME
        recv['person_id'] = persid or self.dummyPerson
        recv['isPrimary'] = 1
        recv['finance_id'] = 2
        recv['payStatus']  = 0

        # date1 = QtCore.QDate().fromString(recv['date'], QtCore.Qt.ISODate)

        # if date1.year() != self.accYear or date1.month() != self.accMonth:
        #     self.addMEKError('5.1.6', 'DATE_IN', 'USL', self.curnzap)
        #     processed = False

        record = self.tblVisit.newRecord()
        for key, val in recv.iteritems():
            record.setValue(key, toVariant(val))
        visitid = self.db.insertRecord(self.tblVisit, record)


    def processSluch(self, row, hasUsl):
        processed = True
        #checking EventType
        vidpom = row.get('VIDPOM', '')
        uslok = row.get('USL_OK', '')
        vidpomid = None
        uslokid = None
        eventid = None
        vidpomname = ''
        uslokname = ''
        isNewSluch = True
        if vidpom:
            vidpomid   = forceInt(self.db.translate(
                       'rbMedicalAidKind', 'federalCode', vidpom, 'id'))

            vidpomname = forceString(self.db.translate(
                       'rbMedicalAidKind', 'federalCode', vidpom, 'name'))
        if uslok:
            uslokid    = forceInt(self.db.translate(
                        'rbEventTypePurpose', 'federalCode', uslok, 'id'))
                       #'rbMedicalAidType', 'federalCode', uslok, 'id'))
            # uslokname  = forceString(self.db.translate(
            #            'rbMedicalAidType', 'federalCode', uslok, 'name'))
        eventtypeid = None
        if uslokid and vidpomid:
            #recet = self.db.getRecordEx('EventType', 'id', 'medicalAidType_id=%d and medicalAidKind_id=%d and deleted=0' % (uslokid, vidpomid))
            recet = self.db.getRecordEx('EventType', 'id', 'purpose_id=%d and medicalAidKind_id=%d and deleted=0' % (uslokid, vidpomid))
            eventtypeid = recet.value('id') if recet else None
        elif not uslokid:
            self.err2log(u'Ошибка. Не найден purpose_id. USL_OK = \'%s\'' % uslok)
        elif not vidpomid:
            self.err2log(u'Ошибка. Не найден medicalAidKind_id. VIDPOM = \'%s\'' % vidpomid)

        if not eventtypeid and vidpomid and uslokid:
            #creating new eventtype
            self.err2log(u'не найден eventtypeid usl_ok=%s, vidpom=%s' % (uslokid, vidpomid))

        lpu = row.get('LPU', '')
        if not lpu:
            lpu = self.tempInfisCode
        lpuid  = forceString(self.db.translate(
                 'Organisation', 'infisCode', lpu, 'id')) if lpu else None
        if not lpuid:
            self.err2log(u'Ошибка. Не найден lpu_id. LPU = \'%s\'' % lpu)

        if eventtypeid and self.currcontractid:
            recspec = self.db.getRecordEx('Contract_Specification', 'id', 'master_id=%s and deleted=0' % self.currcontractid)
            contractspecid = recspec.value('id') if recspec else None
            if not contractspecid:
                self.err2log(u'не найден  contract specification %s' % self.currcontractid)

            purposeId = forceRef(self.db.translate('EventType', 'id', eventtypeid, 'purpose_id'))
            defaultResultFedCode = forceString(self.db.translate('rbResult', 'eventPurpose_id', purposeId, 'federalCode'))
            diagnosticResultId = forceString(self.db.translate('rbDiagnosticResult', 'eventPurpose_id', purposeId, 'id'))
            #creating event
            recevent = {}
            recevent['eventType_id'] = eventtypeid
            recevent['org_id'] = lpuid #QtGui.qApp.currentOrgId()
            recevent['client_id'] = self.idpac
            recevent['contract_id'] = self.currcontractid
            recevent['setDate'] = row.get('DATE_1', '')
            recevent['execDate'] = row.get('DATE_2', '')

            date1 = QtCore.QDate.fromString(recevent['setDate'], QtCore.Qt.ISODate)
            date2 = QtCore.QDate.fromString(recevent['execDate'], QtCore.Qt.ISODate)

            # FIXME: Временно отключено
            # if date1.year() != self.accYear or date1.month() != self.accMonth:
            #     self.addMEKError('5.1.6', 'DATE_1', 'SLUCH', self.curnzap)
            #     processed = False
            # if date2.year() != self.accYear or date2.month() != self.accMonth:
            #     self.addMEKError('5.1.6', 'DATE_2', 'SLUCH', self.curnzap)
            #     processed = False

            recevent['isPrimary'] = 1
            recevent['externalId'] = '%s#%s' % (row.get('NHISTORY', ''), self.idpac2)
            recevent['order'] = row.get('EXTR', '')
            rslt = row.get('RSLT', defaultResultFedCode)
            if rslt == '0':
                rslt = defaultResultFedCode
            bOk = True
            if rslt:
                recevent['result_id'] = forceString(self.db.translate(
                        'rbResult', 'federalCode', rslt, 'id'))
            if not recevent.get('result_id', ''):
                self.err2log(u'Ошибка. Не найден result_id. RSLT = \'%s\'' % rslt)
                bOk = False

            #FIXME
            # drr = self.db.getRecordEx('rbDiagnosticResult', 'federalCode', 'eventPurpose_id = %s -- and result_id = %s' % (recevent.get('result_id', ''), purposeId))
            # defaultDiagnosticResultFedCode = forceString(drr.value('federalCode')) if drr else ''
            recevent['payStatus'] = 0
            recevent['pregnancyWeek'] = 0
            recevent['totalCost'] = 0
            iddokt = row.get('IDDOKT', '')
            persid = None
            if iddokt:
                persid = forceString(self.db.translate(
                        'Person', 'federalCode', iddokt, 'id'))
            #if not recevent.get('iddokt', '');
            #    self.err2log(u'Ошибка. Не найден result_id. RSLT = \'%s\'' % rslt)
            #    bOk = False
            prvs = row.get('PRVS', '')
            if not persid:
                self.addMEKError('5.1.3', 'IDDOKT', 'SLUCH', self.curnzap)
                # tblPerson = self.db.table('Person')
                # tblSpeciality = self.db.table('rbSpeciality')
                # persRecord = self.db.getRecordEx(tblPerson.leftJoin(tblSpeciality, tblSpeciality['id'].eq(tblPerson['speciality_id'])),
                #                                  tblPerson['id'],
                #                                  [tblPerson['deleted'].eq(0)],
                #                                   order=u'rbSpeciality.federalCode = \'%s\' DESC, Person.org_id = %s DESC' % (prvs, lpuid))
                #
                # persid = forceString(persRecord.value('id'))
            if persid: recevent['execPerson_id'] = persid
            recevent['setPerson_id'] = persid or self.dummyPerson
            recevent['relegateOrg_id'] = self.orgId
            if bOk:
                record = self.tblEvent.newRecord()
                for key, val in recevent.iteritems():
                    record.setValue(key, toVariant(val))
                oldRecord = self.db.getRecordEx(self.tblEvent, 'id', [self.tblEvent['client_id'].eq(forceInt(record.value('client_id'))),
                                                          self.db.joinOr([self.tblEvent['externalId'].eq('%s#%s' % (row.get('NHISTORY', ''), self.idpac)), self.tblEvent['externalId'].eq(row.get('NHISTORY', ''))]), # Обратная совместимость. От второго варианта со временем можно избавиться.
                                                          self.tblEvent['org_id'].eq(lpuid),
                                                          self.tblEvent['deleted'].eq(0)])
                if oldRecord:
                    record.setValue('id', oldRecord.value('id'))
                    eventId = forceInt(oldRecord.value('id'))
                    self.db.deleteRecord(self.tblDiagnostic, 'event_id = %s' % eventId)
                    isNewSluch = False
                if isNewSluch and self.novor and self.novor != '0':
                    littleStrangerRecord = self.tblLittleStranger.newRecord()
                    littleStrangerRecord.setValue('sex', toVariant(forceInt(self.novor[0])))
                    littleStrangerRecord.setValue('birthDate', toVariant(QtCore.QDate().fromString(self.novor[1:7], 'ddMMyy')))
                    littleStrangerRecord.setValue('currentNumber', toVariant(forceInt(self.novor[7])))
                    littleStrangerId = self.db.insertRecord(self.tblLittleStranger, littleStrangerRecord)
                    record.setValue('littleStranger_id', littleStrangerId)
                eventid = self.db.insertOrUpdate(self.tblEvent, record)
                self.mapEventAge[eventid] = calcAgeInYears(self.clientBirthday, forceDate(record.value('setDate')))
                #create diagnosis
                mkb = row.get('DS1', '')
                if not mkb:
                    self.addMEKError('5.1.3', 'DS1', 'SLUCH', self.curnzap)
                else:
                    sex, oms, mtr = self.getMkbDesc(mkb)
                    if sex and sex != self.clientSex:
                        self.addMEKError('5.1.4', 'DS1', 'SLUCH', self.curnzap)
                    smo = self.smomap.get(self.idpac)
                    if smo and smo not in ('85001', '85002', '85003'):
                        if not mtr:
                            self.addMEKError('5.1.4', 'DS1', 'SLUCH', self.curnzap)
                    else:
                        if not oms:
                            self.addMEKError('5.1.4', 'DS1', 'SLUCH', self.curnzap)

                recdiag = {}
                recdiag['client_id'] = self.idpac
                recdiag['diagnosisType_id'] = 1
                recdiag['character_id'] = 3
                recdiag['MKB'] = mkb
                recdiag['person_id'] = persid or self.dummyPerson
                recdiag['endDate'] = row.get('DATE_1', '')

                record = self.tblDiagnosis.newRecord()
                for key, val in recdiag.iteritems():
                    record.setValue(key, toVariant(val))
                diagid1 = self.db.insertRecord(self.tblDiagnosis, record)

                ds2 = row.get('DS2', '')
                if ds2:
                    recdiag['diagnosisType_id'] = 9
                    recdiag['MKB'] = ds2

                    record = self.tblDiagnosis.newRecord()
                    for key, val in recdiag.iteritems():
                        record.setValue(key, toVariant(val))
                    diagid2 = self.db.insertRecord(self.tblDiagnosis, record)
                #create diagnostic
                recdiag = {}
                recdiag['event_id'] = eventid
                recdiag['diagnosis_id'] = diagid1
                recdiag['diagnosisType_id'] = 1
                recdiag['character_id'] = 3

                if prvs:
                    recdiag['speciality_id'] = forceString(self.db.translate(
                        'rbSpeciality', 'federalCode', prvs, 'id'))
                if not recdiag.get('speciality_id', ''):
                    self.err2log(u'Ошибка. Не найден speciality_id. PRVS = \'%s\'' % prvs)
                    bOk = False
                recdiag['person_id'] = persid or self.dummyPerson
                recdiag['sanatorium'] = 0
                recdiag['hospital'] = 0
                recdiag['healthGroup_id'] = 1

                ishod = row.get('ISHOD', '')
                if forceInt(ishod):
                    recdiag['result_id'] = forceString(self.db.translate(
                        'rbDiagnosticResult', 'federalCode', ishod, 'id')) if ishod else diagnosticResultId
                # if not recdiag.get('result_id', ''):
                #     self.err2log(u'Ошибка. Не найден result_id. ISHOD = \'%s\', %s' % (ishod, diagnosticResultId))
                #     #FIXME
                    #bOk = False
                recdiag['setDate'] = row.get('DATE_1', '')
                recdiag['endDate'] = row.get('DATE_2', '')

                if bOk:
                    record = self.tblDiagnostic.newRecord()
                    for key, val in recdiag.iteritems():
                        record.setValue(key, toVariant(val))
                    self.db.insertRecord(self.tblDiagnostic, record)
                    if ds2:
                        recdiag['diagnosis_id'] = diagid2
                        recdiag['diagnosisType_id'] = 9

                        record = self.tblDiagnostic.newRecord()
                        for key, val in recdiag.iteritems():
                            record.setValue(key, toVariant(val))
                        self.db.insertRecord(self.tblDiagnostic, record)



        if not hasUsl:
            #TODO: self.addMEKError('5.4.1', 'TARIF', 'SLUCH', self.curnzap)
            processed = False

        return eventid, lpuid, processed, isNewSluch


    def processAccount(self, row):
        processed = True
        rec = {}
        payerId = row.get('PLAT', u'85')
        self.plat = payerId

        rec['settleDate'] = QtCore.QDate().fromString('%4d-%2d-28' % (forceInt(row['YEAR']), forceInt(row['MONTH'])), QtCore.Qt.ISODate) if (row.has_key('YEAR') and row.has_key('MONTH')) else QtCore.QDate()
        rec['exposeDate'] = QtCore.QDate().fromString(row['DSCHET'], QtCore.Qt.ISODate) if row.has_key('DSCHET') else QtCore.QDate()
        rec['date'] = rec['exposeDate']
        if payerId:
            rec['payer_id'] = forceString(self.db.translate('Organisation', 'infisCode', payerId, 'id'))

        orgInfisCode = row.get('CODE_MO', self.tempInfisCode)
        self.lpu = orgInfisCode
        if not rec.get('payer_id', ''):
            self.err2log(u'Ошибка. Не найден payer_id. PLAT = \'%s\'' % payerId)
        elif orgInfisCode:
            orgId = forceString(self.db.translate(
                    'Organisation', 'infisCode', orgInfisCode, 'id'))
            self.orgId = orgId
            if not orgId:
                self.err2log(u'Ошибка. Не найден orgid. miacCode = \'%s\'' % orgInfisCode)
            else:
                db = QtGui.qApp.db
                tblContract = db.table('Contract')
                contractRecord = QtGui.qApp.db.getRecordEx('Contract', 'id',
                                                           [tblContract['recipient_id'].eq(orgId),
                                                            tblContract['endDate'].dateGt(QtCore.QDate.currentDate())])
                if contractRecord:
                    rec['contract_id'] = forceString(contractRecord.value('id'))
                else:
                    self.err2log(u'Ошибка. Не найден contractid. payer_id = \'%s\'' % orgId)
                    processed = False
        else:
            self.addMEKError('5.1.1', 'CODE_MO', 'SCHET', self.curnzap)
            processed = False
        if rec.get('contract_id', ''):

            self.currcontractid = rec['contract_id']

            rec['number'] = row.get('NSCHET', '')

            self.db.deleteRecord('Account', 'contract_id=%s and number=\'%s\'' % (self.currcontractid, rec['number']))

            #TODO: check number
            rec['sum'] = row.get('SUMMAV', '')
            rec['payedSum'] = row.get('SUMMAP', '')

            record = self.tableAccount.newRecord()
            for key, val in rec.iteritems():
                record.setValue(key, toVariant(val))
            self.curaccid = self.db.insertRecord(self.tableAccount, record)
            self.accountIdSet.add(self.curaccid)
        else:
            self.err2log(u'Ошибка. Не найден или не создан contract_id')
        return processed

    def processPatient(self, row):
        rec = {}
        processed = True
        idpac = row['ID_PAC']
        self.novor = row.get('NOVOR', None)
        if idpac in self.idmap:
            self.idpac = self.idmap[idpac]
            self.idpac2 = idpac
            #checking policy data
            vpolis = row.get('VPOLIS', '')
            npolis = row.get('NPOLIS', '')
            if vpolis:
                vpolisid = forceString(self.db.translate('rbPolicyKind', 'federalCode', vpolis, 'id'))
                if vpolisid:
                    #record = self.db.getRecordEx('ClientPolicy', '*', 'client_id=%s and policyType_id=%s and number=%s' % (self.idmap[idpac], vpolisid, npolis))
                    record = selectLatestRecord('ClientPolicy', forceInt(self.idmap[idpac]), 'policyKind_id=%s and number LIKE \'%s\'' % (vpolisid, npolis))
                    if not record or (row.has_key('SPOLIS') and (forceString(record.value('serial')) != row.get('SPOLIS', ''))):
                        # self.addMEKError('5.2.4', 'SPOLIS', 'PACIENT', self.idmap[idpac])
                        # processed = False
                        #TODO: ckeck SMO if fields exist
                        SMO = row.get('SMO', '')
                        tblOrg = self.db.table('Organisation')
                        insurerRecord = self.db.getRecordEx('Organisation', 'id', [tblOrg['infisCode'].eq(SMO), tblOrg['deleted'].eq(0), tblOrg['isInsurer'].eq(1)])
                        if insurerRecord:
                            insurerId = forceRef(insurerRecord.value('id'))
                            #OGRN = row.get('SMO_OGRN', '')
                            #insurerId = self.findInsurerByOGRNandOKATO(OGRN, row.get('SMO_OK', '')) if OGRN else None
                            vpolis = row.get('VPOLIS', '')
                            if vpolis == '2' or len(npolis) == 9:
                                spolis = ''
                                npolis = row.get('SPOLIS', '') + row.get('NPOLIS', '')
                            else:
                                spolis = row.get('SPOLIS', '')
                                npolis = row.get('NPOLIS', '')
                            self.updateClientPolicy(self.idpac, insurerId, spolis, npolis, vpolis)
                            self.smomap[self.idpac] = SMO
                        # else:
                        #     self.addMEKError('5.2.4', 'SMO', 'PACIENT', self.idmap[idpac])
                else:
                    self.addMEKError('5.2.4', 'VPOLIS', 'PERS', idpac)
            self.processClientPolicyERZ(self.idpac)
        else:
            self.idpac = None
            self.idpac2 = None
            self.addMEKError('5.2.4', 'ID_PAC', 'PERS', idpac, u'отсутствует идентификатор в файле персональных данных')
            processed = False
        if idpac in self.idmeklist:
            print idpac, self.idmeklist[idpac]
            self.currosn = self.idmeklist[idpac]
            processed = False
        return processed


    def processPatientPers(self, row):
        processed = True
        record = {}
        record['lastName'] = nameCase(row.get('FAM', ''))
        record['firstName'] = nameCase(row.get('IM', ''))
        record['patrName'] = nameCase(row.get('OT', ''))
        record['sex'] = row.get('W');
        sex = self.sexMap.get(row.get('W'), 0)
        record['birthDate'] = QtCore.QDate().fromString(row['DR'], QtCore.Qt.ISODate) if row.has_key('DR') else QtCore.QDate()
        # FIXME: craz: Далее идет обработка новорожденных. На данном этапе мы не можем гарантировать, что это именно новорожденный - сам флаг хранится в H файле.
        if not (record['lastName'] and record['firstName']): #AZ
            record['lastName'] = nameCase(row.get('FAM_P', ''))
            record['firstName'] = nameCase(row.get('IM_P', ''))
            record['patrName'] = nameCase(row.get('OT_P', ''))
            record['sex'] = row.get('W_P')
            record['birthDate'] = QtCore.QDate().fromString(row['DR'], QtCore.Qt.ISODate) if row.has_key('DR') else QtCore.QDate()
        record['birthPlace'] = nameCase(row.get('MR', ''))
        record['snils'] = nameCase(row.get('SNILS', '')).replace('-', '').replace(' ', '')
        idpac = row['ID_PAC']
        clientId = self.findClientId(record['lastName'], record['firstName'],
                                                         record['patrName'], record['sex'], record['birthDate'])

        if clientId:
            # if forceString(clientrec.value('SNILS')) != record['snils']:
            #     self.addMEKError('5.2.4', 'SNILS', 'PERS', clientId)
            #     self.idmeklist[idpac] = '5.2.4'
            #     processed = False
            self.idmap[idpac] = clientId
            #checking existing client documents
            # doctype = row.get('DOCTYPE', '')
            # if doctype:
            #     doctypeid = forceString(self.db.translate('rbDocumentType', 'federalCode', doctype, 'id'))
            #     if doctypeid:
            #         if row.get('DOCSER', '') and row.get('DOCNUM', ''):
            #             docrecord = selectLatestRecord('ClientDocument', forceInt(clientId), 'documentType_id = %s and number LIKE \'%s\' and serial LIKE \'%s\''
            #                                            % (doctypeid, row.get('DOCNUM', ''), row.get('DOCSER', '')))
            #         elif row.get('DOCSERIAL', '') and row.get('DOCNUMBER', ''):
            #             docrecord = selectLatestRecord('ClientDocument', forceInt(clientId), 'documentType_id = %s and number LIKE \'%s\' and serial LIKE \'%s\''
            #                                            % (doctypeid, row.get('DOCNUMBER', ''), row.get('DOCSERIAL', '')))
                        # if not docrecord:
                        #     self.addMEKError('5.2.4', 'DOCNUM', 'PERS', clientId)
                        #     self.idmeklist[idpac] = '5.2.4'
                # else:
                #     self.addMEKError('5.2.4', 'DOCTYPE', 'PERS', idpac)
                #     self.idmeklist[idpac] = '5.2.4'
                #     processed = False
        else:
            #self.addMEKError('5.2.4', 'ID_PAC', 'PERS', idpac)
            #self.idmeklist[idpac] = '5.2.4'

            #creating new person
            rec = self.tableClient.newRecord()
            for key, val in record.iteritems():
                rec.setValue(key, toVariant(val))
            self.idmap[idpac] = self.db.insertRecord(self.tableClient, rec)

            doctype = row.get('DOCTYPE', '')
            if doctype:
                doctypeid = forceInt(self.db.translate('rbDocumentType', 'federalCode', doctype, 'id'))
                if doctypeid:
                    docrecord = {}
                    docrecord['documentType_id'] = doctypeid
                    #check type in db
                    docrecord['serial'] = nameCase(row.get('DOCSER', row.get('DOCSERIAL', '')))
                    docrecord['number'] = nameCase(row.get('DOCNUM', row.get('DOCNUMBER', '')))
                    docrecord['client_id'] = self.idmap[idpac]
                    docrec = self.tblClientDocument.newRecord()
                    for key, val in docrecord.iteritems():
                        docrec.setValue(key, toVariant(val))
                    self.db.insertRecord(self.tblClientDocument, docrec)
            # else:
            #     self.addMEKError('5.2.4', 'DOCTYPE', 'PERS', idpac)
            #     self.idmeklist[idpac] = '5.2.4'
            #     processed = False


    def findInsurerByOGRN(self, OGRN):
        u"""Поиск по ОГРН с учётом области страхования"""

        result = self.insurerCache.get(OGRN, -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrganisation, 'id',
                                      [self.tableOrganisation['OGRN'].eq(OGRN),
                                      self.tableOrganisation['area'].like(self.insurerArea+'...')])
            result = forceRef(record.value(0)) if record else self.OGRN2orgId(OGRN)
            self.insurerCache[OGRN] = result

        return result


    def findInsurerByOGRNandOKATO(self, OGRN, OKATO):
        u"""Поиск по ОГРН и ОКАТО с учётом области страхования"""

        key = (OGRN,  OKATO)
        result = self.insurerCache.get(key, -1)

        if result == -1:
            record = self.db.getRecordEx(self.tableOrganisation, 'id',
                                      [self.tableOrganisation['OGRN'].eq(OGRN),
                                      self.tableOrganisation['OKATO'].eq(OKATO),
                                      self.tableOrganisation['area'].like(self.insurerArea+'...')])
            result = forceRef(record.value(0)) if record else self.findInsurerByOGRN(OGRN)
            self.insurerCache[key] = result

        return result


    def findClientId(self, lastName, firstName, patrName, sex, birthDate):
        # Предполагатся, что двух записей с одинаковым idpac мы не получим, так что кэшировать его бесполезно. Да и вообще не уверен, что кэш нужен.
        # key = (lastName, firstName, patrName, sex, birthDate)
        # result = self.clientCache.get(key, -1)

        # if result == -1:
        clientId = None
        table = self.db.table('Client')
        filter = [table['deleted'].eq(0),
                    table['lastName'].eq(lastName),
                    table['firstName'].eq(firstName),
                    table['patrName'].eq(patrName),
                    table['birthDate'].eq(birthDate)]

        if sex != 0:
            filter.append(table['sex'].eq(sex))

        record = self.db.getRecordEx(table, 'id',  filter, 'id')

        if record:
            clientId = forceRef(record.value('id'))

        # self.clientCache[key] = result

        return clientId

    def addClientPolicy(self, clientId, insurerId, serial, number, policyTypeId, policyKindId):
        table = self.db.table('ClientPolicy')
        record = table.newRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('insurer_id', toVariant(insurerId))

        if policyTypeId:
            record.setValue('policyType_id', toVariant(policyTypeId))

        if policyKindId:
            record.setValue('policyKind_id', toVariant(policyKindId))

        record.setValue('serial', toVariant(serial))
        record.setValue('number', toVariant(number))
        self.db.insertRecord(table, record)


    def updateClientPolicy(self, clientId, insurerId, serial, number, policyKindId):
        record = selectLatestRecord('ClientPolicy', clientId,
            '(Tmp.`policyType_id` IN (%d,%d))' % \
              (self.policyTypeIndustrial, self.policyTypeTerritorial))

        # if record:
        #     oldInsurerId = forceRef(record.value('insurer_id'))
        #     oldInsurerOGRN = forceString(self.db.translate('Organisation', 'id', oldInsurerId, 'OGRN'))

        if not record or (
                (insurerId and (forceRef(record.value('insurer_id')) != insurerId)) or
                (forceString(record.value('serial')) != serial) or
                (forceString(record.value('number')) != number)
            ):
            newInsurer = forceRef(record.value('insurer_id')) if record else None
            newSerial = forceString(record.value('serial')) if record else None
            newNumber = forceString(record.value('number')) if record else None
            self.addClientPolicy(clientId, insurerId, serial, number,  self.policyTypeTerritorial, policyKindId
                                 #forceRef(record.value('policyKind_id')) if record else None
                                 )
            # self.err2log(u'обновлен полис: `%s№%s (%d)` на `%s№%s (%d)`' % (
            #              newSerial if newSerial else '', newNumber if newNumber else '',
            #              newInsurer if newInsurer else 0, serial, number, insurerId if insurerId else 0))

    def processClientPolicyERZ(self, clientId):
        record = selectLatestRecord('ClientPolicy', clientId)
        if not record:
            # self.err2log(u'Не удалось найти полис пациента')
            return False

        # if forceString(record.value('note')) == 'erz':
        #     return 1

        db = QtGui.qApp.db
        erz = db.table('erz.erz')
        erzFields = [erz['ENP'], erz['OPDOC'], erz['Q']]
        erzRecord = db.getRecordEx(erz, erzFields, erz['ENP'].eq(record.value('number')))
        if erzRecord:
            record.setValue('note', toVariant('erz'))
            record.setValue('policyKind_id', erzRecord.value('OPDOC'))
            q = forceString(erzRecord.value('Q'))
            if q:
                record.setValue('insurer_id', toVariant(forceInt(q[-1]) + 1))
            db.updateRecord('ClientPolicy', record)
            return 1

        client = db.table('Client')
        cd = db.table('ClientDocument')
        tbl = client.leftJoin(cd, cd['id'].eq('getClientDocumentId(Client.id)'))
        clientInfo = db.getRecordEx(tbl, [client['id'], client['notes'], client['lastName'], client['firstName'],
                                               client['patrName'], client['birthDate'], client['SNILS'], cd['serial'],
                                               cd['number']],
                                    client['id'].eq(clientId))
        found = False
        if forceString(clientInfo.value('SNILS')):
            erzRecord = db.getRecordEx(erz, erzFields, erz['SS'].eq(clientInfo.value('SNILS')))
            if erzRecord: found = True

        if not found and not forceDate(clientInfo.value('birthDate')).isNull():
            erzRecord = db.getRecordEx(erz, erzFields, [erz['FAM'].eq(clientInfo.value('lastName')),
                                                        erz['IM'].eq(clientInfo.value('firstName')),
                                                        erz['OT'].eq(clientInfo.value('patrName')),
                                                        erz['DR'].eq(clientInfo.value('birthDate'))])
            if erzRecord: found = True

        docs = forceStringEx(clientInfo.value('serial'))
        docn = forceStringEx(clientInfo.value('number'))
        if not found and forceStringEx(clientInfo.value('number')):
            erzRecord = db.getRecordEx(erz, erzFields, [erz['DOCN'].eq(docn),
                                                        erz['DOCS'].eq(docs)])
            if erzRecord: found = True

        if not found and docn and docs:
            erzRecord = db.getRecordEx(erz, erzFields, [erz['DOCN'].eq(docs+docn),
                                                        erz['DOCS'].isNotNull()])
            if erzRecord: found = True

        pols = forceStringEx(record.value('serial'))
        poln = forceStringEx(record.value('number'))

        if not found and pols and poln:
            erzRecord = db.getRecordEx(erz, erzFields, [erz['NPOL'].eq(pols + poln),
                                                        erz['SPOL'].isNull()])
            if erzRecord: found = True

        if not found:
            # self.err2log(u'Не удалось найти пациента в ЕРЗ.')
            return False

        insurerId = forceInt(forceString(erzRecord.value('Q'))[-1]) + 1
        newRecord = db.table('ClientPolicy').newRecord()
        newRecord.setValue('client_id', toVariant(clientId))
        newRecord.setValue('insurer_id', toVariant(insurerId))
        newRecord.setValue('policyKind_id', erzRecord.value('OPDOC'))
        newRecord.setValue('policyType_id', toVariant(self.policyTypeTerritorial))
        newRecord.setValue('serial', toVariant(''))
        newRecord.setValue('number', erzRecord.value('ENP'))
        newRecord.setValue('note', toVariant('erz'))
        db.insertRecord('ClientPolicy', newRecord)
        self.smomap['idpac'] = forceString(db.translate('Organisation', 'id', insurerId, 'infisCode'))

        #TODO: заполнять Client.notes

        return True



    def checkClientPolicy(self, clientId, policySN, OGRN, OKATO, policyKindId):
        policy = policySN.split(u'№')
        insurerId = self.findInsurerByOGRNandOKATO(OGRN, OKATO) if OGRN else None

        if policy == []:
            return

        policySerial = ''
        policyNumber = policy[0].strip()

        if len(policy)>1:
            policySerial = policy[0].strip()
            policyNumber = policy[1].strip()

        self.updateClientPolicy(clientId, insurerId, policySerial, policyNumber, OGRN, policyKindId)


    def processHeader(self, row, importType):
        if importType == self.importNormal:
            ver = row.get('Version', '')

            if ver != self.version:
                self.err2log(u'Формат версии `%s` не поддерживается.'
                                    u' Должен быть `%s`.' % (ver, self.version))
        elif importType == self.import201112:
            ver = row.get('VERSION', '')

            if ver != self.version201112:
                self.err2log(u'Формат версии `%s` не поддерживается.'
                                    u' Должен быть `%s`.' % (ver, self.version201112))
            else:
                #checking filenames
                #TODO: check LPU and month from filename
                if row.has_key('FILENAME1'):
                    if row.get('FILENAME') != self.persfilename:
                        self.addFLKError(904, None, None, None, u'имя файла не соотвествует полю FILENAME')
                    if row.get('FILENAME1') != self.filename:
                        self.addFLKError(904, None, None, None, u'имя файла не соотвествует полю FILENAME1')
                else:
                    if row.get('FILENAME') != self.filename:
                        self.addFLKError(904, None, None, None, u'имя файла не соотвествует полю FILENAME')

class C79XmlStreamWriter(QtCore.QXmlStreamWriter, CExportHelperMixin):
    def __init__(self, parent):
        QtCore.QXmlStreamWriter.__init__(self)
        CExportHelperMixin.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self._lastClientId = None


    def writeTextElement(self, element,  value, writeEmtpyTag = True):
        if not writeEmtpyTag and (not value or value == ''):
            return
        QtCore.QXmlStreamWriter.writeTextElement(self, element, value)


    def writeRecord(self, errxmlrec):
        self.writeStartElement('PR')
        for key, val in errxmlrec.iteritems():
            self.writeTextElement(key, forceString(val))
        self.writeEndElement()


    def writeFileHeader(self, device, fileNameI, fileName):
        self._lastClientId = None
        self.recNum = 1
        self.caseNum = 1
        self.serviceNum = 1
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('FLK_P')
        self.writeTextElement('FNAME', fileName)
        self.writeTextElement('FNAME_I', fileNameI)


    def writeFileFooter(self):
        self.writeEndElement() # root
        self.writeEndDocument()
