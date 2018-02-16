# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт данных формуляра из справочника ДЛО
"""
from Ui_ImportFormularyDLO import Ui_Dialog
from Cimport import *

# *****************************************************************************************
from library.dbfpy import dbf


def ImportFormularyDLO(widget):
    dlg = CImportFormularyDLO(widget)
    dlg.edtFolderName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportImportFormularyDLOFolderName',  '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportImportFormularyDLOFolderName'] = toVariant(dlg.edtFolderName.text())

# *****************************************************************************************

class CImportFormularyDLO(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.parent = parent

        self.ok = False
        self.abort = False

        db = QtGui.qApp.db
        self.tableFormulary = db.table('DloDrugFormulary')
        self.tableFormularyItem = db.table('DloDrugFormulary_Item')
        self.tableMnn = db.table('dlo_rbMNN')
        self.tableIssueForm = db.table('dlo_rbIssueForm')
        self.tableDosage = db.table('dlo_rbDosage')
        self.tableTradeName = db.table('dlo_rbTradeName')

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0


# *****************************************************************************************

    def startImport(self):
        self.ok = False

        self.isUpdate = self.chkUpdate.isChecked()

        dbfTovFileName = os.path.join(forceStringEx(self.edtFolderName.text()), 'sp_tov.dbf')
        dbfMnnFileName = os.path.join(forceStringEx(self.edtFolderName.text()), 'Sp_mnn.DBF')
        dbfLfFileName = os.path.join(forceStringEx(self.edtFolderName.text()), 'Sp_lf.dbf')
        dbfTrnFileName = os.path.join(forceStringEx(self.edtFolderName.text()), 'Sp_trn.DBF')
        dbfTov = dbf.Dbf(dbfTovFileName, readOnly=True, encoding='cp866')
        dbfMnn = dbf.Dbf(dbfMnnFileName, readOnly=True, encoding='cp866')
        dbfLf = dbf.Dbf(dbfLfFileName, readOnly=True, encoding='cp866')
        dbfTrn = dbf.Dbf(dbfTrnFileName, readOnly=True, encoding='cp866')
        self.progressBar.reset()
        self.progressBar.setMaximum(len(dbfTov) - 1)
        self.progressBar.setFormat(u'%v из %m (%p%)')

        self.labelNum.setText(u'Всего записей в источнике: ' + str(len(dbfTov)))

        self.log.append(u'Импорт начат ' + QDateTime().currentDateTime().toString('dd.MM.yyyy H:mm:ss'))
        self.log.append(u'--------------------------------------- ')
        self.log.append(u'Размер источника:')
        self.log.append(u'   - основная таблица: %d' % len(dbfTov))
        self.log.append(u'   - справочник МНН: %d' % len(dbfMnn))
        self.log.append(u'   - справочник форм выпуска: %d' % len(dbfLf))
        self.log.append(u'   - справочник торговых наименований: %d' % len(dbfTrn))

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.process(dbfTov, dbfMnn, dbfLf, dbfTrn, self.processRow)
        self.ok = not self.abort

        dbfTov.close()
        dbfMnn.close()
        dbfLf.close()
        dbfTrn.close()
        self.log.append(u'--------------------------------------- ')
        self.log.append(u'Импорт завершён ' + QDateTime().currentDateTime().toString('dd.MM.yyyy H:mm:ss'))
        self.log.append(u'Добавлено: %d; изменено: %d' % (self.nAdded, self.nUpdated))
        self.log.append(u'Пропущено: %d; обработано: %d' % (self.nSkipped, self.nProcessed))
        self.log.append(u'Готово')
        self.log.append(u' ')
        self.log.append(u' ')

# *****************************************************************************************

    def process(self, dbfTov, dbfMnn, dbfLf, dbfTrn, step):
        db = QtGui.qApp.db
        db.transaction()

        try:
            self.masterId = None
            record = db.getRecordEx(self.tableFormulary, [ 'id', 'isReadOnly' ], where='type = 0 AND isActive = 1 AND deleted = 0')
            if record:
                self.masterId = forceInt(record.value(0))
                if forceInt(record.value('isReadOnly')) == 0:
                    record.setValue('isReadOnly', 1)
                    db.updateRecord(self.tableFormulary, record)
            else:
                newRecord = self.tableFormulary.newRecord()
                newRecord.setValue('type', 0)
                newRecord.setValue('begDate', QDate().currentDate())
                newRecord.setValue('endDate', QDate().fromString('2099-12-31', 'yyyy-MM-dd'))
                newRecord.setValue('isReadOnly', 1)
                self.masterId = db.insertRecord(self.tableFormulary, newRecord)

            if not self.masterId:
                raise Exception(u'ошибка при создании формуляра!')

            for row in dbfTov:
                QtGui.qApp.processEvents()
                if self.abort:
                    db.rollback()
                    self.reject()
                    return
                self.progressBar.setValue(self.progressBar.value() + 1)
                step(row, dbfMnn, dbfLf, dbfTrn)

            db.commit()

        except ValueError:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
                    u' неверное значение строки "%d" в DBF.' % \
                    (self.progressBar.value()+1))
            raise
        # except Exception as ex:
        #     self.log.append(u'<b><font color=red>ОШИБКА:</b> ' + ex.message)
        #     self.nSkipped += 1
        #     self.abort = True
        #     db.rollback()

# *****************************************************************************************

    def processRow(self,  row, dbfMnn, dbfLf, dbfTrn):
        db = QtGui.qApp.db
        existingRecord = None

        code = forceInt(row['NOMK_LS'])
        nameMed = forceString(row['NAME_MED'])
        endDate = forceDate(row['DATE_E'])
        mnnCode = forceInt(row['C_MNN'])
        issueFormCode = forceInt(row['C_LF'])
        tradeNameCode = forceInt(row['C_TRN'])
        dosageCode = forceInt(row['C_DLS'])
        dosageQnt = forceInt(row['D_LS'])
        isDevice = forceInt(row['IS_IMN'])
        dosageLs = u''
        if (forceString(row['D_LS']) == u'0') and (forceInt(row['C_VLF']) == 1) \
                and (forceDouble(row['M_LF']) == 0) and (forceInt(row['C_MLF']) == 1):
            dosageLs = u'0'
        if forceString(row['D_LS']) != u'0':
            dls = forceString(row['D_LS'])
            if ('+' in dls) or ('|'):
                c = '+' if ('+' in dls) else '|'
                dlsSplit = dls.split(c)
                if len(dlsSplit):
                    dosageLs += c.join(''.join(x) for x in zip(dlsSplit))
                else:
                    dosageLs += dls
            else:
                dosageLs += dls
            if forceInt(row['N_DOZA']) != 0:
                dosageLs += forceString(row['N_DOZA'])
                dosageLs += u'доз'
        if forceInt(row['C_VLF']) == 7:
            dosageLs += forceString('{0:g}'.format(forceDouble(row['V_LF'])))
            dosageLs += u'мл'
        if not self.isCodePresent(mnnCode, 'dlo_rbMNN'):
            mnnRow = self.findRowByCode('C_MNN', mnnCode, dbfMnn)
            mnnRecord = self.tableMnn.newRecord()
            mnnRecord.setValue('code', mnnCode)
            if mnnRow:
                mnnRecord.setValue('name', mnnRow['NAME_MNN_R'])
                mnnRecord.setValue('latinName', mnnRow['NAME_MNN_L'])
            mnnId = db.insertRecord(self.tableMnn, mnnRecord)
            if not mnnId:
                raise Exception(u'Не удалось добавить запись в dlo_rbMNN!')
        else:
            mnnId = forceInt(db.translate('dlo_rbMNN', 'code', mnnCode, 'id'))
            if self.chkUpdate.isChecked():
                tblMnn = self.db.table('dlo_rbMNN')
                mnnRow = self.findRowByCode('C_MNN', mnnCode, dbfMnn)
                if mnnRow and mnnRow['NAME_MNN_R']:
                    recMnn = self.db.getRecordEx(tblMnn, '*', tblMnn['code'].eq(mnnCode))
                    if not forceString(recMnn.value('name')) == forceString(mnnRow['NAME_MNN_R']):
                        recMnn.setValue('name', toVariant(mnnRow['NAME_MNN_R']))
                        recMnn.setValue('latinName', toVariant(mnnRow['NAME_MNN_L']))
                        self.db.updateRecord(tblMnn, recMnn)

        if not self.isCodePresent(issueFormCode, 'dlo_rbIssueForm'):
            lfRow = self.findRowByCode('C_LF', issueFormCode, dbfLf)
            issueFormRecord = self.tableIssueForm.newRecord()
            issueFormRecord.setValue('code', issueFormCode)
            issueFormRecord.setValue('name', lfRow['NAME_LF'])
            issueFormId = db.insertRecord(self.tableIssueForm, issueFormRecord)
            if not issueFormId:
                raise Exception(u'Не удалось добавить запись в dlo_rbIssueForm!')
        else:
            issueFormId = forceInt(db.translate('dlo_rbIssueForm', 'code', issueFormCode, 'id'))
            if self.chkUpdate.isChecked():
                tblLf = self.db.table('dlo_rbIssueForm')
                lfRow = self.findRowByCode('C_LF', issueFormCode, dbfLf)
                if lfRow and lfRow['NAME_LF']:
                    recLf = self.db.getRecordEx(tblLf, '*', tblLf['code'].eq(issueFormCode))
                    if not forceString(recLf.value('name')) == forceString(lfRow['NAME_LF']):
                        recLf.setValue('name', toVariant(lfRow['NAME_LF']))
                        self.db.updateRecord(tblLf, recLf)

        if not self.isCodePresent(tradeNameCode, 'dlo_rbTradeName'):
            trnRow = self.findRowByCode('C_TRN', tradeNameCode, dbfTrn)
            if trnRow:
                tnRecord = self.tableTradeName.newRecord()
                tnRecord.setValue('code', tradeNameCode)
                tnRecord.setValue('name', trnRow['NAME_TRN_R'])
                tnRecord.setValue('latinName', trnRow['NAME_TRN_L'])
                tradeNameId = db.insertRecord(self.tableTradeName, tnRecord)
            else:
                raise Exception(u'Не удалось добавить запись в dlo_rbTradeName')
            if not tradeNameId:
                raise Exception(u'Не удалось добавить запись в dlo_rbTradeName!')
        else:
            tradeNameId = forceInt(db.translate('dlo_rbTradeName', 'code', tradeNameCode, 'id'))
            if self.chkUpdate.isChecked():
                tblTrn = self.db.table('dlo_rbTradeName')
                trnRow = self.findRowByCode('C_TRN', tradeNameCode, dbfTrn)
                if trnRow and trnRow['NAME_TRN_R']:
                    recTrn = self.db.getRecordEx(tblTrn, '*', tblTrn['code'].eq(tradeNameCode))
                    if not forceString(recTrn.value('name')) == forceString(trnRow['NAME_TRN_R']):
                        recTrn.setValue('name', toVariant(trnRow['NAME_TRN_R']))
                        recTrn.setValue('latinName', toVariant(trnRow['NAME_TRN_L']))
                        self.db.updateRecord(tblTrn, recTrn)

        itemRecord = self.tableFormularyItem.newRecord()
        itemRecord.setValue('master_id', self.masterId)
        itemRecord.setValue('code', code)

        itemId = forceInt(db.translate('DloDrugFormulary_Item', 'code', code, 'id'))
        if itemId > 0:
            existingRecord = db.getRecord('DloDrugFormulary_Item', '*', itemId)
            if existingRecord:
                itemRecord.setValue('id', forceInt(existingRecord.value('id')))

        needToUpdate = False
        if not self.isCodePresent(code, 'DloDrugFormulary_Item'):
            itemRecord.setValue('name', nameMed[:250])
            itemRecord.setValue('mnn_id', mnnId)
            itemRecord.setValue('issueForm_id', issueFormId)
            itemRecord.setValue('dosageQnt', dosageQnt)
            itemRecord.setValue('dosageLs', dosageLs)
            itemRecord.setValue('tradeName_id', tradeNameId)
            itemRecord.setValue('qnt', forceInt(row['N_FV']))
            itemRecord.setValue('producer', forceString(row['NAME_FCT'])[:50])
            itemRecord.setValue('isDrugs', 0)
            itemRecord.setValue('limit', 999)
            itemRecord.setValue('federalcode', forceInt(row['NOMK_LS']))
            itemRecord.setValue('isSprPC', toVariant(1))
            itemRecord.setValue('isDevice', toVariant(isDevice))

            if not db.insertRecord(self.tableFormularyItem, itemRecord):
                raise Exception(u'Не удалось добавить запись в DloDrugFormulary_Item!')
            else:
                self.nAdded += 1
        elif self.isUpdate and existingRecord:
            itemRecord.setValue('name', existingRecord.value('name'))
            itemRecord.setValue('mnn_id', existingRecord.value('mnn_id'))
            itemRecord.setValue('issueForm_id', existingRecord.value('issueForm_id'))
            itemRecord.setValue('dosageQnt', existingRecord.value('dosageQnt'))
            itemRecord.setValue('dosageLs', existingRecord.value('dosageLs'))
            itemRecord.setValue('tradeName_id', existingRecord.value('tradeName_id'))
            itemRecord.setValue('qnt', existingRecord.value('qnt'))
            itemRecord.setValue('producer', existingRecord.value('producer'))
            itemRecord.setValue('isDrugs', existingRecord.value('isDrugs'))
            itemRecord.setValue('limit', existingRecord.value('limit'))
            itemRecord.setValue('federalCode', existingRecord.value('federalCode'))
            itemRecord.setValue('isSprPC', existingRecord.value('isSprPc'))
            itemRecord.setValue('isDevice', existingRecord.value('isDevice'))
            dosageId = existingRecord.value('dosage_id')

            if endDate > QDate().currentDate():
                itemRecord.setValue('name', nameMed)
                itemRecord.setValue('mnn_id', mnnId)
                itemRecord.setValue('issueForm_id', issueFormId)
                itemRecord.setValue('dosageQnt', dosageQnt)
                itemRecord.setValue('dosageLs', dosageLs)
                itemRecord.setValue('dosage_id', dosageId)
                itemRecord.setValue('tradeName_id', tradeNameId)
                itemRecord.setValue('qnt', forceInt(row['N_FV']))
                itemRecord.setValue('producer', forceString(row['NAME_FCT'])[:50])
                itemRecord.setValue('isDrugs', 0)
                itemRecord.setValue('limit', 999)
                itemRecord.setValue('federalCode', forceInt(row['NOMK_LS']))
                itemRecord.setValue('isSprPC', toVariant(1))
                itemRecord.setValue('isDevice', toVariant(isDevice))
                needToUpdate = True

            if not needToUpdate:
                if len(forceString(existingRecord.value('name'))) == 0 or not forceString(existingRecord.value('name')) == forceString(nameMed):
                    itemRecord.setValue('name', nameMed)
                    needToUpdate = True
                if forceInt(existingRecord.value('mnn_id')) == 0 or not forceInt(existingRecord.value('mnn_id')) == forceInt(mnnId):
                    itemRecord.setValue('mnn_id', mnnId)
                    needToUpdate = True
                if forceInt(existingRecord.value('issueForm_id')) == 0 or not forceInt(existingRecord.value('issueForm_id')) == forceInt(issueFormId):
                    itemRecord.setValue('issueForm_id', issueFormId)
                    needToUpdate = True
                if not forceInt(existingRecord.value('isDevice')) == isDevice:
                    itemRecord.setValue('isDevice', isDevice)
                    needToUpdate = True
                # if forceInt(existingRecord.value('dosageQnt')) == 0:
                #     itemRecord.setValue('dosageQnt', dosageQnt)
                #     needToUpdate = True
                if forceString(existingRecord.value('dosageLs')) == u'' or not forceString(existingRecord.value('dosageLs')) == forceString(dosageLs):
                    itemRecord.setValue('dosageLs', dosageLs)
                    needToUpdate = True
                if forceInt(existingRecord.value('tradeName_id')) == 0 or not forceInt(existingRecord.value('tradeName_id')) == forceInt(tradeNameId):
                    itemRecord.setValue('tradeName_id', tradeNameId)
                    needToUpdate = True
                if forceInt(existingRecord.value('qnt')) == 0:
                    itemRecord.setValue('qnt', forceInt(row['N_FV']))
                    needToUpdate = True
                if forceString(existingRecord.value('producer')) == 0:
                    itemRecord.setValue('producer', forceString(row['NAME_FCT'])[:50])
                    needToUpdate = True
                if forceInt(existingRecord.value('isDrugs')) == 0:
                    itemRecord.setValue('isDrugs', 0)
                    needToUpdate = True
                if forceInt(existingRecord.value('limit')) == 0:
                    itemRecord.setValue('limit', 999)
                    needToUpdate = True
                if forceInt(existingRecord.value('federalCode')) == 0:
                    itemRecord.setValue('federalCode', forceInt(row['NOMK_LS']))
                    needToUpdate = True
                if forceInt(existingRecord.value('isSprPc')) == 0:
                    itemRecord.setValue('isSprPC', forceInt(1))
                    needToUpdate = True

            if needToUpdate:
                if not db.updateRecord(self.tableFormularyItem, itemRecord):
                    raise Exception(u'Не удалось обновить запись в DloDrugFormulary_Item!')
                else:
                    self.nUpdated += 1
        else:
            self.nSkipped += 1

        self.nProcessed += 1

# *****************************************************************************************

    def isCodePresent(self, code, table):
        db = QtGui.qApp.db

        query = db.query(u'SELECT COUNT(id) FROM %s WHERE %s = %d' % (table, 'code', code))
        if query.next() and forceInt(query.record().value(0)) > 0:
            return True
        else:
            return False

# *****************************************************************************************

    def findRowByCode(self, codeField, code, dbf):
        for row in dbf:
            QtGui.qApp.processEvents()
            if self.abort:
                self.reject()
                return None

            if forceInt(row[codeField]) == code:
                return row
        return None

# *****************************************************************************************

    # def IsDrugPresent(self, mnnId, issueFormId, dosageId, tradeNameId):
    #     db = QtGui.qApp.db
    #
    #     query = db.query(u'''SELECT COUNT(id) FROM DloDrugFormulary_Item WHERE master_id = %d AND
    #                      mnn_id = %d AND issueForm_id = %d AND dosage_id = %d AND tradeName_id = %d'''
    #                      % (self.masterId, mnnId, issueFormId, dosageId, tradeNameId))
    #     if query.next() and forceInt(query.record().value(0)) > 0:
    #         return True
    #     else:
    #         return False

# *****************************************************************************************

    @QtCore.pyqtSlot()
    def on_btnSelectFolder_clicked(self):
        folderName = QtGui.QFileDialog.getExistingDirectory(self, u'Укажите папку с данными')
        if folderName != '':
            self.edtFolderName.setText(QtCore.QDir.toNativeSeparators(folderName))
            self.btnImport.setEnabled(True)
            dbfTovFileName = os.path.join(forceStringEx(self.edtFolderName.text()), 'sp_tov.dbf')
            dbfTov = dbf.Dbf(dbfTovFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'Всего записей в источнике: ' + str(len(dbfTov)))