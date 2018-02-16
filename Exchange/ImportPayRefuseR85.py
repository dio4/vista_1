# -*- coding: utf-8 -*-

from zipfile import ZipFile

from PyQt4 import QtCore, QtGui, QtXml

from Accounting.Utils   import updateAccounts, updateDocsPayStatus
from Events.Utils       import CPayStatus, getPayStatusMask
from Exchange.Cimport import CXMLimport
from library.Utils      import forceInt, forceRef, forceString, forceStringEx, toVariant, getVal

from Ui_ImportPayRefuseR29 import Ui_Dialog

#FIXME: В текущем виде отчет о количестве обработанных случаев лечения будет очень приблизительным.
# Как с нашей стороны (не всегда считаем именно SLUCH), так и со стороны посылающей стророны
# (на данный момент одному случаю лечения может соответствовать несколько SLUCH).
#TODO: отвязаться от архангельского импорта
#TODO: решить, что делать с progressbar. Сейчас он носит исключительно декоративный характер.

def ImportPayRefuseR85(widget, accountId, accountItemIdList):
    dlg = CImportPayRefuseR85(accountId, accountItemIdList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportPayRefuseR29FileName', '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportPayRefuseR29FileName'] = toVariant(dlg.edtFileName.text())


class CImportPayRefuseR85(QtGui.QDialog, Ui_Dialog, CXMLimport):
    sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}
    zglvFields = ('VERSION', 'DATA', 'FILENAME')
    pacientFields = ('ID_PAC','VPOLIS', 'SPOLIS', 'NPOLIS', 'SMO', 'SMO_OGRN', 'SMO_OK', 'SMO_NAM', 'NOVOR')
    sluchFields = ('IDCASE','USL_OK', 'VIDPOM', 'NPR_MO', 'EXTR', 'PODR','LPU','PROFIL', 'DET','NHISTORY',
                        'DATE_1', 'DATE_2', 'DS1', 'DS2', 'RSLT', 'ISHOD', 'PRVS', 'IDSP','ED_COL', 'TARIF', 'SUMV')

    def __init__(self, accountId, accountItemIdList):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        CXMLimport.__init__(self, self.log, db = QtGui.qApp.db)
        self.accountId=accountId
        self.accountItemIdList=accountItemIdList
        self.progressBar.setFormat('%p%')
        self.checkName()
        self.errorPrefix = u'Ошибка: '
        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0
        self.refuseTypeIdCache = {}
        self.mapAccountIdToPayStatusMask = {}
        self.mapIdPacToClientId = {}
        self.insurerInfis = None
        self.tblEvent = self.db.table('Event')
        self.setWindowTitle(u'Импорт отказов по счетам для Республики Крым')
        self.chkImportPayed.setVisible(False)
        self.chkImportRefused.setVisible(False)
        self.chkOnlyCurrentAccount.setVisible(False)
        self.edtConfirmation.setVisible(False)
        self.label_2.setVisible(False)
        self.btnView.setVisible(False)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы ZIP (*.zip)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)


    def err2log(self, e):
        self.log.append(self.errorPrefix+e)


    def startImport(self):

        self.nProcessed = 0
        self.nPayed = 0
        self.nRefused = 0
        self.nNotFound = 0


        zipFileName = forceStringEx(self.edtFileName.text())

        archive = ZipFile(forceString(zipFileName), "r")
        namelist = archive.namelist()
        if len(namelist) != 2:
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'Неожиданное количество файлов в архиве.')
            return
        if namelist[0].startswith('H'):
            hFileName, lFileName = namelist
        elif namelist[1].startswith('H'):
            lFileName, hFileName = namelist
        else:
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'В архиве отсутствует файл с услугами.')
            return
        if not lFileName.startswith('L'):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'В архиве отсутствует файл с персональными данными.')
            return


        if len(hFileName) < 8:
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                      u'Неверный формат имени файла с услугами')
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

        self.insurerInfis = hFileName[2:7]

        data = archive.read(hFileName) #read the binary data
        outFile.write(data)
        outFile.close()
        fileInfo = QtCore.QFileInfo(outFile)

        persData = archive.read(lFileName)
        persOutFile.write(persData)
        persOutFile.close()
        persFileInfo = QtCore.QFileInfo(persOutFile)

        hFile = QtCore.QFile(fileInfo.filePath())
        lFile = QtCore.QFile(persFileInfo.filePath())

        if not hFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл для чтения %s:\n%s.' \
                                  % (fileInfo.filePath(), hFile.errorString()))
            return
        if not lFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт данных из XML',
                                  u'Не могу открыть файл персональных данных для чтения %s:\n%s.' \
                                  % (persFileInfo.filePath(), lFile.errorString()))
            return

        self.labelNum.setText(u'размер источника: '+str(hFile.size() + lFile.size()))
        self.progressBar.setFormat('%p%')
        self.progressBar.setMaximum(hFile.size() + lFile.size() -1)

        self.readLFile(lFile)
        self.readHFile(hFile)

        self.stat.setText(
            u'обработано случаев: %d; оплаченых: %d; отказаных: %d; не найдено: %d' % \
            (self.nProcessed, self.nPayed, self.nRefused, self.nNotFound))
        hFile.close()
        lFile.close()


    def getRefuseTypeId(self, code):
        result = self.refuseTypeIdCache.get(code, -1)

        if result == -1:
            result =forceRef(self.db.translate(
                'rbPayRefuseType', 'flatCode', code, 'id'))
            self.refuseTypeIdCache[code] = result

        return result

# *****************************************************************************************
#  XML
# *****************************************************************************************

    def readLFile(self, device):
        """
            Обработка файла с рег данными
        """
        doc = QtXml.QDomDocument()
        doc.setContent(device)
        root = doc.documentElement()
        if root.tagName() != 'PERS_LIST':
            self.err2log(u'Некорректная структура L-файла.')
            return False

        if not self.checkVersion(root):
            self.err2log(u'Некорректная версия обмена в L-файле.')
            return False

        pers = root.firstChildElement('PERS')
        while not pers.isNull():
            QtGui.qApp.processEvents()
            self.processPers(pers)
            pers = pers.nextSiblingElement('PERS')

    def processPers(self, pers):
        id_pac = forceString(pers.firstChildElement('ID_PAC').text())
        lastName = pers.firstChildElement('FAM').text()
        firstName = pers.firstChildElement('IM').text()
        patrName = pers.firstChildElement('OT').text()
        sex = pers.firstChildElement('W').text()
        birthDate = QtCore.QDate.fromString(pers.firstChildElement('DR').text(), QtCore.Qt.ISODate)

        tblClient = self.db.table('Client')
        cond = [tblClient['lastName'].eq(lastName if lastName else ''),
                tblClient['firstName'].eq(firstName if firstName else ''),
                tblClient['patrName'].eq(patrName if patrName else ''),
                tblClient['sex'].eq(sex),
                tblClient['birthDate'].eq(birthDate)]
        clientRecord = self.db.getRecordEx(tblClient, 'id', cond)
        if not clientRecord:
            self.err2log(u'Не удалось найти пациента, ID_PAC = %s' % id_pac)
            self.mapIdPacToClientId[id_pac] = None
            return False
        self.mapIdPacToClientId[id_pac] = forceRef(clientRecord.value('id'))
        return True


    def readHFile(self, device):
        """
            Обработка с услугами
        """
        doc = QtXml.QDomDocument()
        doc.setContent(device)
        root = doc.documentElement()
        if root.tagName() != u'ZL_LIST':
            self.err2log(u'Некорректная структура H-файла.')
            return False

        if not self.checkVersion(root):
            self.err2log(u'Некорректная версия обмена в H-файле.')
            return False

        zglv = root.firstChildElement('ZGLV')
        self.date = QtCore.QDate.fromString(zglv.firstChildElement('DATA').text(), QtCore.Qt.ISODate)
        if not self.date.isValid():
            self.date = QtCore.QDate.currentDate()

        self.accountIdSet = set()
        zap = root.firstChildElement('ZAP')
        while not zap.isNull():
            QtGui.qApp.processEvents()
            self.processZap(zap)
            zap = zap.nextSiblingElement('ZAP')

        updateAccounts(self.accountIdSet)

        return 0

    def checkVersion(self, root):
        zglv = root.firstChildElement('ZGLV')
        version = zglv.firstChildElement('VERSION').text()
        if version != '2.1':
            return False
        return True

    def processZap(self, zap):
        nzap = forceString(zap.firstChildElement('N_ZAP').text())
        pacient = zap.firstChildElement('PACIENT')
        if not pacient:
            self.err2log(u'Для N_ZAP = %s отсутствует секция PACIENT' % nzap)
            self.nNotFound += 1
            self.nProcessed += 1
            return False

        id_pac = forceString(pacient.firstChildElement('ID_PAC').text())
        clientId = self.mapIdPacToClientId.get(id_pac, None)
        if clientId is None:
            self.err2log(u'Не удалось определить пациента для N_ZAP = %s, ID_PAC = %s' % (nzap, id_pac))
            self.nNotFound += 1
            self.nProcessed += 1
            return False

        sluch = zap.firstChildElement('SLUCH')
        while not sluch.isNull():
            self.processSluch(sluch, clientId)
            sluch = sluch.nextSiblingElement('SLUCH')

    def processSluch(self, sluch, clientId):
        idcase = forceString(sluch.firstChildElement('IDCASE').text())

        eventTypeIdList = self.getEventTypeIdList(sluch, idcase)
        if not eventTypeIdList:
            self.err2log(u'Не найден тип события для IDCASE = %s' % idcase)
            self.nNotFound += 1
            self.nProcessed += 1
            return False

        dateInStr = forceString(sluch.firstChildElement('DATE_1').text())
        dateOutStr = forceString(sluch.firstChildElement('DATE_2').text())

        dateIn = QtCore.QDate.fromString(dateInStr, QtCore.Qt.ISODate)
        dateOut = QtCore.QDate.fromString(dateOutStr, QtCore.Qt.ISODate)

        if not dateIn.isValid():
            self.err2log(u'Не удалось определить дату начала лечения для IDCASE = %s' % idcase)
            self.nNotFound += 1
            self.nProcessed += 1
            return False
        # if not dateOut.isValid():
        #     self.err2log(u'Не удалось определить дату окончания лечения для IDCASE = %s' % idcase)
        #     self.nNotFound += 1
        #     self.nProcessed += 1
        #     return False

        eventRecord = self.db.getRecordEx(self.tblEvent, 'id', [self.tblEvent['client_id'].eq(clientId),
                                                          self.tblEvent['eventType_id'].inlist(eventTypeIdList),
                                                          self.tblEvent['setDate'].dateEq(dateIn),
                                                          self.tblEvent['execDate'].dateEq(dateOut)
                                                            if dateOut.isValid()
                                                            else 'NOT Event.execDate',
                                                          self.tblEvent['deleted'].eq(0)])
        if not eventRecord:
            self.err2log(u'Не найден случай лечения для IDCASE = %s' % idcase)
            self.nNotFound += 1
            self.nProcessed += 1
            return False

        eventId = forceRef(eventRecord.value('id'))
        oplata = forceInt(sluch.firstChildElement('OPLATA').text())

        usl = sluch.firstChildElement('USL')
        if not usl:
            self.err2log(u'В ID_CASE = %s не указано ни одной услуги для оплаты' % idcase)

        fields = 'Account_Item.id, Account_Item.date, Account_Item.action_id, Account_Item.visit_id, Account_Item.event_id, Account_Item.master_id, Account_Item.refuseType_id, Account_Item.number, Account_Item.note'
        accountItemList = self.db.getRecordList('Account_Item', fields, 'event_id = %s' % eventId)

        tableAccountItem = self.db.table('Account_Item')
        self.db.transaction()
        try:
            for accountItem in accountItemList:
                accountItem.setValue('date', toVariant(self.date))
                if self.insurerInfis:
                    accountItem.setValue('note', '%s\n$$insurer:%s$$' % (forceStringEx(accountItem.value('note')), self.insurerInfis))
                sank = sluch.firstChildElement('SANK')
                refReason = None
                if sank:
                    refReason = forceStringEx(sank.firstChildElement('S_OSN').text())
                # refReason = forceString(sluch.firstChildElement('REFREASON').text())
                accountId = forceRef(accountItem.value('master_id'))
                payStatusMask = self.getPayStatusMask(accountId)
                if oplata > 1 and refReason:
                    refuseTypeId = self.getRefuseTypeId(refReason)
                    accountItem.setValue('refuseType_id', toVariant(refuseTypeId))
                    accountItem.setValue('number', toVariant(u'Отказ по МЭК'))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.refusedBits)
                    self.nRefused += 1
                    self.nProcessed += 1
                else:
                    accountItem.setValue('number', toVariant(u'Оплачено'))
                    updateDocsPayStatus(accountItem, payStatusMask, CPayStatus.payedBits)
                    self.nPayed += 1
                    self.nProcessed += 1
                self.db.updateRecord(tableAccountItem, accountItem)
                self.accountIdSet.add(accountId)
            self.db.commit()
        except:
            self.db.rollback()
            QtGui.qApp.logCurrentException()
            raise


    def getEventTypeIdList(self, sluch, idcase):
        uslok = forceString(sluch.firstChildElement('USL_OK').text())
        vidpom = forceString(sluch.firstChildElement('VIDPOM').text())
        if not uslok:
            self.err2log(u'Не заполнено поле USL_OK для IDCASE = %s' % idcase)
            return None
        if not vidpom:
            self.err2log(u'Не заполнено поле VIDPOM для IDCASE = %s' % idcase)
            return None
        tablePurpose = self.db.table('rbEventTypePurpose')
        uslokidList    = self.db.getIdList(
            tablePurpose, where=[tablePurpose['federalCode'].eq(uslok)])
        if not uslokidList:
            self.err2log(u'Не найдено назначение типа события с кодом %s, IDCASE = %s' % (uslok, idcase))
            return None
        tableAidKind = self.db.table('rbMedicalAidKind')
        # TODO: craz: костыль для переходного периода - запросами клиентам поменяли medicalAidKind, а в выгрузках менять уже поздно.
        vidpomList = {'1': ('11', '12', '13', '1'),
                      '2': ('21', '22', '2'),
                      '3': ('31', '32', '3')}.get(vidpom, (vidpom,))
        vidpomidList   = self.db.getIdList(
            tableAidKind,  where=tableAidKind['federalCode'].inlist(vidpomList))
        if not vidpomidList:
            self.err2log(u'Не найден вид медицинской помощи с федеральным кодом %s, IDCASE = %s' % (vidpom, idcase))
            return None

        tableEventType = self.db.table('EventType')
        result = self.db.getIdList(tableEventType,
                                  'id',
                                  [tableEventType['purpose_id'].inlist(uslokidList),
                                  tableEventType['medicalAidKind_id'].inlist(vidpomidList),
                                  ])
        return result if result else None

    def getPayStatusMask(self, accountId):
        result = self.mapAccountIdToPayStatusMask.get(accountId, None)
        if result is None:
            tblAccount = self.db.table('Account')
            tblContract = self.db.table('Contract')
            tbl = tblAccount.join(tblContract, tblContract['id'].eq(tblAccount['contract_id']))
            record = self.db.getRecordEx(tbl, tblContract['finance_id'], tblAccount['id'].eq(accountId))
            if record:
                result = getPayStatusMask(forceRef(record.value('finance_id')))
            self.mapAccountIdToPayStatusMask[accountId] = result
        return result
