# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils  import forceDate, forceInt, forceRef, forceString, toVariant
from Reports.Report import normalizeMKB
from Registry.Utils import getClientBanner

from Ui_LocalLogicalControlDiagnosisLUD import Ui_LocalLogicalControlDiagnosisLUD


class CLocalLogicalControlDiagnosisLUD(QtGui.QDialog, Ui_LocalLogicalControlDiagnosisLUD):
    def __init__(self, parent, Chronical = False, Acute = False):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.clientId = parent.clientId
        self.Chronical = Chronical
        self.Acute = Acute
        if self.clientId:
            self.txtClientInfoControlLocalLUD.setHtml(getClientBanner(self.clientId))
        else:
            self.txtClientInfoControlLocalLUD.setText('')
        self.rows = 0
        self.errorStr = u''
        self.abortProcess = False
        self.checkRun = False
        self.prbControlDiagnosisLocalLUD.setFormat('%v')
        self.prbControlDiagnosisLocalLUD.setValue(0)
        self.lblCountLineLocalLUD.setText(u'всего строк: 0')
        self.duration = 0
        self.recordBuffer = []
        self.recordBufferError = []
        self.recordBufferCorrect = []
        self.recordBufferClientId = []
        self.recordBufferErrorClientId = []
        self.recordBufferCorrectClientId = []
        self.bufferCorrectClientIds = []
        self.recSelectCorrect = u''
        self.recSelectClient = u''
        self.diagnosisId = None


    @QtCore.pyqtSlot()
    def on_btnEndControlLocalLUD_clicked(self):
        if self.checkRun:
            self.abortProcess = True
            self.listResultControlDiagnosisLocalLUD.reset()
            self.lblCountLineLocalLUD.setText(u'всего строк: %d' % self.listResultControlDiagnosisLocalLUD.count())
        else:
            self.close()
            QtGui.qApp.emitCurrentClientInfoChanged()


    @QtCore.pyqtSlot(bool)
    def on_chkMKB_clicked(self, checked):
        self.edtMKBFrom.setEnabled(checked)
        self.edtMKBTo.setEnabled(checked)


    @QtCore.pyqtSlot()
    def on_btnStartControlLocalLUD_clicked(self):
        self.duration = 0
        self.recordBuffer = []
        self.recordBufferError = []
        self.recordBufferCorrect = []
        self.recordBufferClientId = []
        self.recordBufferErrorClientId = []
        self.recordBufferCorrectClientId = []
        self.bufferCorrectClientIds = []
        self.recSelectCorrect = u''
        self.recSelectClient = u''
        self.diagnosisId = None
        self.checkRun = False
        self.abortProcess = False
        self.chkMKB.setEnabled(False)
        self.edtMKBFrom.setEnabled(self.chkMKB.isChecked())
        self.edtMKBTo.setEnabled(self.chkMKB.isChecked())
        self.btnCorrectControlLocalLUD.setText(u'исправить')
        try:
            self.loadDataDiagnosis()
        finally:
            self.chkMKB.setEnabled(True)
            self.edtMKBFrom.setEnabled(self.chkMKB.isChecked())
            self.edtMKBTo.setEnabled(self.chkMKB.isChecked())


    @QtCore.pyqtSlot()
    def on_btnCorrectControlLocalLUD_clicked(self):
        if self.checkRun:
            self.abortProcess = True
        else:
            self.checkRun = True
            self.btnCorrectControlLocalLUD.setFocus(QtCore.Qt.OtherFocusReason)
            self.btnCorrectControlLocalLUD.setText(u'прервать исправление')
            self.btnStartControlLocalLUD.setEnabled(False)
            QtGui.qApp.callWithWaitCursor(self, self.correctDataDiagnosis)
            self.btnCorrectControlLocalLUD.setText(u'исправить')
            self.checkRun = False
            self.abortProcess = False
            self.btnStartControlLocalLUD.setEnabled(True)
            self.prbControlDiagnosisLocalLUD.setText(u'готово')


    def recordReadChronicDisease(self, client_id, MKB, MKBEx, traumaType_id, character_id):
        db = QtGui.qApp.db
        stmt = None
        stmtCharacter_id = None
        records = []
        characterId = forceRef(character_id)
        clientId = forceRef(client_id)
        stringMKB = forceString(MKB)
        stringMKBEx = forceString(MKBEx)
        if characterId is None:
            stmtCharacter_id = u'''character_id IS NULL'''
        else:
            stmtCharacter_id = u'''character_id = %d''' % (characterId)
        if stmtCharacter_id:
            #Min setDate
            stmt = u'''SELECT D2.setDate, D2.endDate, D2.id AS id, D2.client_id, D2.MKB, D2.character_id
                       FROM Diagnosis AS D2
                       WHERE D2.deleted = 0 AND IF((SELECT MIN(IF (D1.setDate IS NULL, 0, D1.setDate)) AS setDate
                                 FROM Diagnosis AS D1
                                 WHERE D1.deleted = 0 AND D1.`client_id`= %d AND D1.`MKB`= \'%s\' AND D1.`MKBEx`= \'%s\' AND D1.%s) = 0, D2.setDate IS NULL, D2.setDate = (SELECT MIN(D3.setDate)
                                               FROM Diagnosis AS D3
                                               WHERE D3.deleted = 0 AND D3.`client_id`= %d AND D3.`MKB`= \'%s\' AND D3.`MKBEx`= \'%s\' AND D3.%s)
)
                             AND (D2.`client_id`= %d AND D2.`MKB`= \'%s\' AND D2.`MKBEx`= \'%s\' AND D2.%s)
                       ORDER BY D2.id
                       LIMIT 0,1''' % (clientId, stringMKB, stringMKBEx, stmtCharacter_id, clientId, stringMKB, stringMKBEx, stmtCharacter_id, clientId, stringMKB, stringMKBEx, stmtCharacter_id)
            if stmt:
                result = db.query(stmt)
                while result.next():
                    records.append(result.record())
            #MAX endDate
            stmt = u'''SELECT D2.endDate, D2.setDate, D2.id AS id, D2.client_id, D2.MKB, D2.character_id
                       FROM Diagnosis AS D2
                       WHERE D2.deleted = 0 AND (D2.endDate = (SELECT MAX(D1.endDate) AS endDate
                                            FROM Diagnosis AS D1
                                            WHERE D1.deleted = 0 AND (D1.`client_id`= %d AND D1.`MKB`= \'%s\' AND D1.`MKBEx`= \'%s\' AND D1.%s))
                              AND (D2.`client_id`= %d AND D2.`MKB`= \'%s\' AND D2.`MKBEx`= \'%s\' AND D2.%s))
                       ORDER BY D2.id
                       LIMIT 0,1''' % (clientId, stringMKB, stringMKBEx, stmtCharacter_id, clientId, stringMKB, stringMKBEx, stmtCharacter_id)
            if stmt:
                result = db.query(stmt)
                while result.next():
                    records.append(result.record())
        return records


    def recordReadAcuteDisease(self, client_id, MKB, MKBEx, traumaType_id, character_id, setDateBuffer, endDateBuffer):
        db = QtGui.qApp.db
        tabDiagnos = db.table('Diagnosis')
        cols = [tabDiagnos['id'],
                tabDiagnos['client_id'],
                tabDiagnos['MKB'],
                tabDiagnos['character_id'],
                tabDiagnos['setDate'],
                tabDiagnos['endDate']
                ]

        cond = [tabDiagnos['deleted'].eq(0),
                tabDiagnos['client_id'].eq(client_id),
                tabDiagnos['MKB'].eq(MKB),
                tabDiagnos['MKBEx'].eq(MKBEx)
                ]
        characterId = forceRef(character_id)
        if characterId is None:
            cond.append(u'Diagnosis.character_id IS NULL')
        else:
            cond.append(tabDiagnos['character_id'].eq(character_id))
        durationMKB = self.setDurationMKB(MKB)
        durationDate = forceDate(endDateBuffer)
        if durationDate:
            durationEndDate = durationDate.addDays(durationMKB)
        else:
            durationEndDate = durationDate
        durationEndDateString = forceString(durationEndDate.toString('yyyy-MM-dd'))
        setDateFormat = forceDate(setDateBuffer)
        endDateFormat = forceDate(endDateBuffer)
        setDate = forceString(setDateFormat.toString('yyyy-MM-dd'))
        endDate = forceString(endDateFormat.toString('yyyy-MM-dd'))

        cond.append(u'''(Diagnosis.setDate IS NOT NULL AND ((Diagnosis.setDate < \'%s\' AND Diagnosis.endDate > \'%s\') OR ((Diagnosis.setDate < \'%s\' AND (Diagnosis.endDate >= \'%s\' OR (ADDDATE(Diagnosis.endDate, %d) >= \'%s\'))) OR (Diagnosis.endDate > \'%s\' AND (Diagnosis.setDate <= \'%s\' OR Diagnosis.setDate <= \'%s\')))))
        OR (Diagnosis.setDate IS NULL AND ((0 < \'%s\' AND Diagnosis.endDate > \'%s\') OR ((0 < \'%s\' AND (Diagnosis.endDate >= \'%s\' OR (ADDDATE(Diagnosis.endDate, %d) >= \'%s\'))) OR (Diagnosis.endDate > \'%s\' AND (0 <= \'%s\' OR 0 <= \'%s\')))))''' % (setDate, endDate, setDate, setDate, durationMKB, setDate, endDate, endDate, durationEndDateString, setDate, endDate, setDate, setDate, durationMKB, setDate, endDate, endDate, durationEndDateString))
        records = db.getRecordList(tabDiagnos, cols, cond, tabDiagnos['client_id'].name() +' ASC, ' + tabDiagnos['MKB'].name() + ' ASC')
        return records


    def setDurationMKB(self, MKB = None):
        durationMKB = 0
        if MKB:
            tabMKB = QtGui.qApp.db.table('MKB_Tree')
            condMKB = [tabMKB['DiagID'].eq(MKB)]
            recDurationMKB = QtGui.qApp.db.getIdList(tabMKB, 'duration', condMKB)
            if recDurationMKB:
                durationMKB = forceRef(recDurationMKB[0])
            if not durationMKB or durationMKB == 0:
                durationMKB = self.duration
        return durationMKB


    def messageInsertDiagnosis(self, correctDiagnosId, clientId, MKB, MKBEx):
        message = self.recSelectClient + u'\n\nОбнаружен диагноз с интервалом, превышающим среднюю продолжительность заболевания, до следующего диагноза:\n' + self.recSelectCorrect + u'\n\n Создать отдельную запись в ЛУД?'
        res = QtGui.QMessageBox.warning(self,
                                        u'Внимание!',
                                        message,
                                        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Abort,
                                        QtGui.QMessageBox.Cancel)
        if res == QtGui.QMessageBox.Ok:
            db = QtGui.qApp.db
            tableDiagnostic = db.table('Diagnostic')
            tableDiagnosis = db.table('Diagnosis')
            cols = [tableDiagnostic['deleted'],
                    tableDiagnostic['diagnosisType_id'],
                    tableDiagnostic['character_id'],
                    tableDiagnostic['dispanser_id'],
                    tableDiagnostic['traumaType_id'],
                    tableDiagnostic['setDate'],
                    tableDiagnostic['endDate'],
                    tableDiagnostic['person_id']
                    ]
            recordDiagnostic = db.getRecordList(tableDiagnostic, cols, [tableDiagnostic['deleted'].eq(0), tableDiagnostic['id'].eq(correctDiagnosId)])
            for recordIns in recordDiagnostic:
                insertRecordDiagnosis  = tableDiagnosis.newRecord()
                insertRecordDiagnosis.setValue('deleted', toVariant(forceDate(recordIns.value('deleted'))))
                insertRecordDiagnosis.setValue('client_id', toVariant(clientId))
                insertRecordDiagnosis.setValue('diagnosisType_id', toVariant(forceRef(recordIns.value('diagnosisType_id'))))
                insertRecordDiagnosis.setValue('character_id', toVariant(forceRef(recordIns.value('character_id'))))
                insertRecordDiagnosis.setValue('MKB', toVariant(MKB))
                insertRecordDiagnosis.setValue('MKBEx', toVariant(MKBEx))
                insertRecordDiagnosis.setValue('dispanser_id', toVariant(forceRef(recordIns.value('dispanser_id'))))
                insertRecordDiagnosis.setValue('traumaType_id', toVariant(forceRef(recordIns.value('traumaType_id'))))
                insertSetDate = forceDate(recordIns.value('setDate'))
                insertEndDate = forceDate(recordIns.value('endDate'))
                insertRecordDiagnosis.setValue('setDate', toVariant(forceString(insertSetDate.toString('yyyy-MM-dd'))))
                insertRecordDiagnosis.setValue('endDate', toVariant(forceString(insertEndDate.toString('yyyy-MM-dd'))))
                insertRecordDiagnosis.setValue('mod_id', toVariant(None))
                insertRecordDiagnosis.setValue('person_id', toVariant(forceRef(recordIns.value('person_id'))))
                insertId = db.insertRecord(tableDiagnosis, insertRecordDiagnosis)
                if insertId:
                    recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['diagnosis_id'].eq(insertId), [tableDiagnostic['id'].eq(correctDiagnosId), tableDiagnostic['deleted'].eq(0)])
            self.listResultControlDiagnosisLocalLUD.reset()
            self.lblCountLineLocalLUD.setText(u'всего строк: %d' % self.listResultControlDiagnosisLocalLUD.count())
        return res


    def updateDateAcuteChronicDisease(self, recordCorrectBuffer=None, row=-1):
        if not recordCorrectBuffer:
            recordCorrectBuffer = []
        if recordCorrectBuffer:
            correctDiagnosId = forceRef(recordCorrectBuffer.value('diagnostic_id'))
            correctDiagnosisId = forceRef(recordCorrectBuffer.value('diagnosis_id'))
            correctClientId = forceString(recordCorrectBuffer.value('client_id'))
            correctMKB = forceString(recordCorrectBuffer.value('MKB'))
            correctMKBEx = forceString(recordCorrectBuffer.value('MKBEx'))
            correctCharacterId = forceRef(recordCorrectBuffer.value('character_id'))
            diagnosticCharacterId = forceRef(recordCorrectBuffer.value('diagnosticCharacterId'))
            correctSetDate = forceDate(recordCorrectBuffer.value('setDate'))
            correctSetDateString = forceString(correctSetDate.toString('yyyy-MM-dd'))
            correctEndDate = forceDate(recordCorrectBuffer.value('endDate'))
            correctEndDateString = forceString(correctEndDate.toString('yyyy-MM-dd'))
            if correctSetDate <= correctEndDate:
                db = QtGui.qApp.db
                tableDiagnosis = db.table('Diagnosis')
                cols = [tableDiagnosis['id'],
                        tableDiagnosis['setDate'],
                        tableDiagnosis['endDate']
                        ]
                cond = [tableDiagnosis['deleted'].eq(0), tableDiagnosis['id'].eq(correctDiagnosisId)]
                records = db.getRecordList(tableDiagnosis, cols, cond)
                for record in records:
                    diagnosisId = forceRef(record.value('id'))
                    if correctDiagnosisId == diagnosisId:
                        setDateDiagnosis = forceDate(record.value('setDate'))
                        endDateDiagnosis = forceDate(record.value('endDate'))
                        if correctSetDate < setDateDiagnosis and correctEndDate > endDateDiagnosis:
                            #в Diagnosis уменьшаем SetDate до SetDate Diagnostic
                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(correctSetDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                            #в Diagnosis увеличиваем EndDate до EndDate Diagnostic
                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['endDate'].eq(correctEndDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                        else:
                            if correctSetDate < setDateDiagnosis:
                                if diagnosticCharacterId < 2:
                                    durationMKB = self.setDurationMKB(correctMKB)
                                    if correctEndDate.addDays(durationMKB) < setDateDiagnosis:
                                        self.viewMessageInsertDiagnosisEvent(recordCorrectBuffer, row)
                                        QtGui.qApp.restoreOverrideCursor()
                                        try:
                                            messageButtonClick = self.messageInsertDiagnosis(correctDiagnosId, correctClientId, correctMKB, correctMKBEx)
                                        finally:
                                            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                                        if messageButtonClick == QtGui.QMessageBox.Ignore:
                                            #в Diagnosis уменьшаем SetDate до SetDate Diagnostic
                                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(correctSetDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                                        elif messageButtonClick == QtGui.QMessageBox.Cancel:
                                            return False
                                        elif messageButtonClick == QtGui.QMessageBox.Abort:
                                            self.abortProcess = True
                                            return False
                                    else:
                                        #в Diagnosis уменьшаем SetDate до SetDate Diagnostic
                                        recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(correctSetDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                                else:
                                    #в Diagnosis уменьшаем SetDate до SetDate Diagnostic
                                    recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(correctSetDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                            else:
                                if correctEndDate > endDateDiagnosis:
                                    if diagnosticCharacterId < 2:
                                        durationMKB = self.setDurationMKB(correctMKB)
                                        if endDateDiagnosis.addDays(durationMKB) < correctSetDate:
                                            self.viewMessageInsertDiagnosisEvent(recordCorrectBuffer, row)
                                            QtGui.qApp.restoreOverrideCursor()
                                            try:
                                                messageButtonClick = self.messageInsertDiagnosis(correctDiagnosId, correctClientId, correctMKB, correctMKBEx)
                                            finally:
                                                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                                            if messageButtonClick == QtGui.QMessageBox.Ignore:
                                                #в Diagnosis увеличиваем EndDate до EndDate Diagnostic
                                                recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['endDate'].eq(correctEndDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                                            elif messageButtonClick == QtGui.QMessageBox.Cancel:
                                                return False
                                            elif messageButtonClick == QtGui.QMessageBox.Abort:
                                                self.abortProcess = True
                                                return False
                                        else:
                                            #в Diagnosis увеличиваем EndDate до EndDate Diagnostic
                                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['endDate'].eq(correctEndDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                                    else:
                                        #в Diagnosis увеличиваем EndDate до EndDate Diagnostic
                                        recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['endDate'].eq(correctEndDateString), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
        return True


#controlIntegrity()                                         # 1 Нет целостности.
#controlCodingTraumaType()                                  # 4 Несоответствие типа травмы.
#controlDiseaseDiagnostic(character_id)                     # 5 Минимальная дата начала. Максимальная дата окончания.
#controlCharacterChronicFirstDisease()                      # 6 Некорректная дата начала хронического заболевания.
#loadDataDiagnosis()                                        # 7 Проблема длительности периода.
#controlCharacterChronicKnowDisease()                       # 8 Некорректный характер хронического заболевания.
#controlDiseaseDiagnostic(character_id)                     # 9 Минимальная дата окончания.


    def correctDataDiagnosis(self):
        self.bufferCorrectClientIds = []
        booleanActionsCorrect = False
        listItemsSelectControl = self.listResultControlDiagnosisLocalLUD.selectedItems()
        listItemsSelectControl.sort()
        correctSelect = []
        resSelect = []
        itemsSelect = []
        resetClientId = []
        rowList = -1
        self.prbControlDiagnosisLocalLUD.setFormat('%v')
        self.prbControlDiagnosisLocalLUD.setValue(0)
        prbControlPercent = 0
        lenStr = len(listItemsSelectControl)
        if lenStr > 1:
            self.prbControlDiagnosisLocalLUD.setMaximum(lenStr - 1)
        for itemsSelect in listItemsSelectControl:
            rowList = self.listResultControlDiagnosisLocalLUD.row(itemsSelect)
            correctSelect.append([self.recordBuffer[rowList], rowList])
        for resSelect, row in correctSelect:
            QtGui.qApp.processEvents()
            if self.abortProcess:
                self.checkRun = False
                self.prbControlDiagnosisLocalLUD.setValue(lenStr - 1)
                break
            self.prbControlDiagnosisLocalLUD.setValue(prbControlPercent)
            prbControlPercent += 1
            correctDiagnosId = forceString(resSelect.value('id'))
            correctDiagnosisId = forceRef(resSelect.value('diagnosis_id'))
            correctClientId = forceRef(resSelect.value('client_id'))
            if correctClientId not in self.bufferCorrectClientIds:
                self.bufferCorrectClientIds.append(correctClientId)
            correctMKB = forceString(resSelect.value('MKB'))
            correctMKBEx = forceString(resSelect.value('MKBEx'))
            correctTraumaType_id = forceRef(resSelect.value('traumaType_id'))
            correctCharacterId = forceRef(resSelect.value('character_id'))
            correctSetDate = forceDate(resSelect.value('setDate'))
            correctEndDate = forceDate(resSelect.value('endDate'))
            db = QtGui.qApp.db
            tableDiagnosis = db.table('Diagnosis')
            tableDiagnostic = db.table('Diagnostic')
            tableTempInvalid_Period = db.table('TempInvalid_Period')
            tableTempInvalid = db.table('TempInvalid')

            if self.recordBufferCorrect[row] == 1: # 1 Нет целостности.
                #удаляем запись из {Diagnosis}
                booleanActionsCorrect = True
                deleteDiagnosId = forceString(resSelect.value('id'))
                db.deleteRecord(tableDiagnosis, tableDiagnosis['id'].eq(deleteDiagnosId))
                self.listWidgetItemEnabled(row)

            if self.recordBufferCorrect[row] == 4: # 4 Несоответствие типа травмы.
                booleanActionsCorrect = True
                recordTraumaType = db.getIdList(tableDiagnosis, 'traumaType_id', [tableDiagnosis['deleted'].eq(0), tableDiagnosis['id'].eq(correctDiagnosisId)])
                traumaType_id = forceRef(recordTraumaType[0]) if recordTraumaType else None
                # Заменяем traumaType_id в {Diagnostic} в соответствии с traumaType_id из {Diagnosis}
                if (traumaType_id != None) or (traumaType_id > 0):
                    recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['traumaType_id'].eq(traumaType_id), [tableDiagnostic['id'].eq(correctDiagnosId), tableDiagnostic['deleted'].eq(0)])
                self.listWidgetItemEnabled(row)

            if self.recordBufferCorrect[row] == 5: # 5 Минимальная дата начала. Максимальная дата окончания.
                booleanActionsCorrect = True
                if self.updateDateAcuteChronicDisease(resSelect, row):
                    self.listWidgetItemEnabled(row)

            if self.recordBufferCorrect[row] == 6: # 6 Некорректная дата начала.
                # Заменяем setDate в {Diagnosis} в соответствии с хроническим впервые установленным setDate из {Diagnostic}
                booleanActionsCorrect = True
                setDateModif = None
                setDateModif = forceString(correctSetDate.toString('yyyy-MM-dd'))
                if setDateModif:
                    recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(setDateModif), [tableDiagnosis['id'].eq(correctDiagnosisId), tableDiagnosis['deleted'].eq(0)])
                    condDateModif = [tableDiagnostic['deleted'].eq(0), tableDiagnostic['diagnosis_id'].eq(correctDiagnosisId)]
                    recordModif = db.getRecordList(tableDiagnostic, 'MIN(Diagnostic.setDate) AS setDate, Diagnostic.character_id', condDateModif)
                    recordDateModif = recordModif[0]
                    minSetDateDiagnostic = forceDate(recordDateModif.value('setDate'))
                    minCharacterId = forceInt(recordDateModif.value('character_id'))
                    if (not minSetDateDiagnostic.isNull()) and (minSetDateDiagnostic > 0) and (correctSetDate > minSetDateDiagnostic and minCharacterId > 1):
                        recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['character_id'].eq(3), [tableDiagnostic['id'].eq(correctDiagnosId), tableDiagnostic['deleted'].eq(0)])
                    self.listWidgetItemEnabled(row)

            if self.recordBufferCorrect[row] == 8: # 8 Некорректный характер хронического заболевания.
                # Заменяем хроническое впервые установленное на хроническое известное
                booleanActionsCorrect = True
                recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['character_id'].eq(3), [tableDiagnostic['id'].eq(correctDiagnosId), tableDiagnostic['deleted'].eq(0)])
                self.listWidgetItemEnabled(row)

            if self.recordBufferCorrect[row] == 7: # 7 Проблема длительности периода.
                booleanActionsCorrect = True
                minSetDate = None
                minSetDateId = None
                maxEndDate = None
                maxEndDateId = None
                listDiagnosId = []
                if correctCharacterId == 1:
                    records = self.recordReadAcuteDisease(resSelect.value('client_id'), resSelect.value('MKB'), resSelect.value('MKBEx'), resSelect.value('traumaType_id'), resSelect.value('character_id'), resSelect.value('setDate'), resSelect.value('endDate'))
                else:
                    if correctCharacterId > 1:
                        records = self.recordReadChronicDisease(resSelect.value('client_id'), resSelect.value('MKB'), resSelect.value('MKBEx'), resSelect.value('traumaType_id'), resSelect.value('character_id'))
                for record in records:
                    diagnos_id = forceString(record.value('id'))
                    client_id = forceString(record.value('client_id'))
                    MKB = forceString(record.value('MKB'))
                    character_id = forceString(record.value('character_id'))
                    setDate = forceDate(record.value('setDate'))
                    endDate = forceDate(record.value('endDate'))
                    if forceRef(record.value('id')) > 0 and forceRef(record.value('client_id')) > 0:
                        if minSetDate:
                            if minSetDate > setDate:
                                minSetDate = setDate
                                minSetDateId = diagnos_id
                        else:
                            if minSetDate is None:
                                minSetDate = setDate
                                minSetDateId = diagnos_id

                        if maxEndDate:
                            if maxEndDate < endDate:
                                maxEndDate = endDate
                                maxEndDateId = diagnos_id
                        else:
                            if maxEndDate is None:
                                maxEndDate = endDate
                                maxEndDateId = diagnos_id

                if correctDiagnosId != maxEndDateId:
                    if minSetDate > correctSetDate:
                        minSetDate = correctSetDate
                        minSetDateId = correctDiagnosId
                    else:
                        listDiagnosId.append(correctDiagnosId)

                if correctCharacterId > 1:
                    setDateModif = None
                    if minSetDate == correctSetDate and maxEndDate == correctEndDate:
                        cond = [tableDiagnostic['deleted'].eq(0),
                                tableDiagnostic['diagnosis_id'].eq(correctDiagnosId),
                                tableDiagnostic['character_id'].gt(1)
                                ]
                        minRecordDiagnostic = db.getRecordList(tableDiagnostic, 'MIN(setDate) AS setDate, character_id AS minCharacter_id, MAX(endDate) AS endDate', cond)
                        minDiagnostic = minRecordDiagnostic[0]
                        setDateDiagnostic = forceDate(minDiagnostic.value('setDate'))
                        characterIdMinSetDate = forceRef(minDiagnostic.value('minCharacter_id'))
                        endDateDiagnostic = forceDate(minDiagnostic.value('endDate'))
                        correctdiagnosIdBuffer = None
                        if characterIdMinSetDate > 2:
                            if setDateDiagnostic < correctSetDate:
                                setDateModif = forceString(setDateDiagnostic.toString('yyyy-MM-dd'))
                                recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(setDateModif), [tableDiagnosis['id'].eq(correctDiagnosId), tableDiagnosis['deleted'].eq(0)])
                                minSetDate = setDateDiagnostic
                                correctdiagnosIdBuffer = minSetDateId
                                minSetDateId = correctDiagnosId
                        else:
                            if characterIdMinSetDate == 2:
                                if setDateDiagnostic != correctSetDate:
                                    setDateModif = forceString(setDateDiagnostic.toString('yyyy-MM-dd'))
                                    recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(setDateModif), [tableDiagnosis['id'].eq(correctDiagnosId), tableDiagnosis['deleted'].eq(0)])
                                    minSetDate = setDateDiagnostic
                                    correctdiagnosIdBuffer = minSetDateId
                                    minSetDateId = correctDiagnosId
                        if endDateDiagnostic > correctEndDate:
                            endDateModif = forceString(endDateDiagnostic.toString('yyyy-MM-dd'))
                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['endDate'].eq(endDateModif), [tableDiagnosis['id'].eq(correctDiagnosId), tableDiagnosis['deleted'].eq(0)])
                            maxEndDate = endDateDiagnostic
                            correctdiagnosIdBuffer = maxEndDateId
                            maxEndDateId = correctDiagnosId
                        if maxEndDateId == correctDiagnosId and minSetDateId == correctDiagnosId:
                            listDiagnosId = []

                if minSetDateId and maxEndDateId:
                    if minSetDateId != maxEndDateId:
                        if minSetDateId != correctDiagnosId and maxEndDateId != correctDiagnosId:
                            #изменяем correctDiagnosId на maxEndDateId в {Diagnostic}, {TempInvalid_Period}, {TempInvalid}.
                            recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['diagnosis_id'].eq(maxEndDateId), [tableDiagnostic['diagnosis_id'].eq(correctDiagnosId), tableDiagnostic['deleted'].eq(0)])
                            recQuery = db.updateRecords(tableTempInvalid_Period.name(), tableTempInvalid_Period['diagnosis_id'].eq(maxEndDateId), tableTempInvalid_Period['diagnosis_id'].eq(correctDiagnosId))
                            recQuery = db.updateRecords(tableTempInvalid.name(), tableTempInvalid['diagnosis_id'].eq(maxEndDateId), [tableTempInvalid['diagnosis_id'].eq(correctDiagnosId), tableTempInvalid['deleted'].eq(0)])
                            #удаляем запись из {Diagnosis}
                            db.deleteRecord(tableDiagnosis, tableDiagnosis['id'].eq(correctDiagnosId))
                        else:
                            #в maxEndDateId уменьшаем SetDate до minSetDateId
                            minSetDateString = forceString(minSetDate.toString('yyyy-MM-dd'))
                            recQuery = db.updateRecords(tableDiagnosis.name(), tableDiagnosis['setDate'].eq(minSetDateString), [tableDiagnosis['id'].eq(maxEndDateId), tableDiagnosis['deleted'].eq(0)])
                            #изменяем minSetDateId на maxEndDateId в {Diagnostic}, {TempInvalid_Period}, {TempInvalid}.
                            recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['diagnosis_id'].eq(maxEndDateId), [tableDiagnostic['diagnosis_id'].eq(minSetDateId), tableDiagnostic['deleted'].eq(0)])
                            recQuery = db.updateRecords(tableTempInvalid_Period.name(), tableTempInvalid_Period['diagnosis_id'].eq(maxEndDateId), tableTempInvalid_Period['diagnosis_id'].eq(minSetDateId))
                            recQuery = db.updateRecords(tableTempInvalid.name(), tableTempInvalid['diagnosis_id'].eq(maxEndDateId), [tableTempInvalid['diagnosis_id'].eq(minSetDateId), tableTempInvalid['deleted'].eq(0)])
                            #удаляем запись из {Diagnosis}
                            db.deleteRecord(tableDiagnosis, tableDiagnosis['id'].eq(minSetDateId))
                    else:
                        if listDiagnosId:
                            for DiagnosId in listDiagnosId:
                                #изменяем correctDiagnosId на maxEndDateId в {Diagnostic}, {TempInvalid_Period}, {TempInvalid}.
                                recQuery = db.updateRecords(tableDiagnostic.name(), tableDiagnostic['diagnosis_id'].eq(maxEndDateId), [tableDiagnostic['diagnosis_id'].eq(DiagnosId), tableDiagnostic['deleted'].eq(0)])
                                recQuery = db.updateRecords(tableTempInvalid_Period.name(), tableTempInvalid_Period['diagnosis_id'].eq(maxEndDateId), tableTempInvalid_Period['diagnosis_id'].eq(DiagnosId))
                                recQuery = db.updateRecords(tableTempInvalid.name(), tableTempInvalid['diagnosis_id'].eq(maxEndDateId), [tableTempInvalid['diagnosis_id'].eq(DiagnosId), tableTempInvalid['deleted'].eq(0)])
                                #удаляем запись из {Diagnosis}
                                db.deleteRecord(tableDiagnosis, tableDiagnosis['id'].eq(DiagnosId))
                self.listWidgetItemEnabled(row)
            self.listResultControlDiagnosisLocalLUD.reset()
            self.lblCountLineLocalLUD.setText(u'всего строк: %d' % self.listResultControlDiagnosisLocalLUD.count())
        if booleanActionsCorrect:
            self.changeDataClientsId()
        else:
            self.bufferCorrectClientIds = []


    def changeDataClientsId(self):
        if self.bufferCorrectClientIds:
            self.chkMKB.setEnabled(False)
            self.edtMKBFrom.setEnabled(self.chkMKB.isChecked())
            self.edtMKBTo.setEnabled(self.chkMKB.isChecked())
            if self.chkMKB.isChecked():
                MKBFrom = normalizeMKB(self.edtMKBFrom.text())
                MKBTo = normalizeMKB(self.edtMKBTo.text())
            else:
                MKBFrom = None
                MKBTo = None
            for clientId in self.bufferCorrectClientIds:
                self.recordBufferClientId = []
                self.recordBufferErrorClientId = []
                self.recordBufferCorrectClientId = []
                findLikeStings = []
                self.controlDiseaseLUD(clientId, MKBFrom, MKBTo)
                stringClientId = forceString(clientId)
                if stringClientId != u'':
                    findLikeStings = self.listResultControlDiagnosisLocalLUD.findItems(stringClientId, QtCore.Qt.MatchContains)
                    for likeString in findLikeStings:
                        row = self.listResultControlDiagnosisLocalLUD.row(likeString)
                        if forceRef(self.recordBuffer[row].value('client_id')) == clientId:
                            if len(self.recordBuffer) > row and len(self.recordBufferCorrect) > row and len(self.recordBufferError) > row:
                                if (int(likeString.flags()) & QtCore.Qt.NoItemFlags) == 0:
                                    likeString.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsEnabled)
                                self.listResultControlDiagnosisLocalLUD.takeItem(row)
                                self.recordBuffer.pop(row)
                                self.recordBufferCorrect.pop(row)
                                self.recordBufferError.pop(row)
                    findLikeStings = []
                    for bufferCorrectClientId, bufferClientId, bufferErrorClientId in zip(self.recordBufferCorrectClientId, self.recordBufferClientId, self.recordBufferErrorClientId):
                        resultStr = u''
                        resultStr = self.aggregateString(bufferClientId, bufferErrorClientId)
                        findLikeStings = self.listResultControlDiagnosisLocalLUD.findItems(bufferErrorClientId, QtCore.Qt.MatchContains)
                        if findLikeStings:
                            rowCurrentError = -1
                            rowCurrentError = self.listResultControlDiagnosisLocalLUD.row(findLikeStings[0])
                            if rowCurrentError >= 0:
                                self.listResultControlDiagnosisLocalLUD.insertItem(rowCurrentError, resultStr)
                                self.recordBuffer.insert(rowCurrentError, bufferClientId)
                                self.recordBufferCorrect.insert(rowCurrentError, bufferCorrectClientId)
                                self.recordBufferError.insert(rowCurrentError, bufferErrorClientId)
                            else:
                                self.listResultControlDiagnosisLocalLUD.addItem(resultStr)
                                self.recordBuffer.append(bufferClientId)
                                self.recordBufferCorrect.append(bufferCorrectClientId)
                                self.recordBufferError.append(bufferErrorClientId)
                        else:
                            self.listResultControlDiagnosisLocalLUD.addItem(resultStr)
                            self.recordBuffer.append(bufferClientId)
                            self.recordBufferCorrect.append(bufferCorrectClientId)
                            self.recordBufferError.append(bufferErrorClientId)
                self.listResultControlDiagnosisLocalLUD.reset()
                self.rows = self.listResultControlDiagnosisLocalLUD.count()
                self.lblCountLineLocalLUD.setText(u'всего строк: %d' % self.rows)
            self.checkRun = False
            self.abortProcess = False
            self.chkMKB.setEnabled(True)
            self.edtMKBFrom.setEnabled(self.chkMKB.isChecked())
            self.edtMKBTo.setEnabled(self.chkMKB.isChecked())


    def aggregateString(self, record = None,  recordError = None):
        resultStr = u''
        if record and recordError:
            character_id = u''
            client_id = u''
            lastName = u''
            firstName = u''
            patrName = u''
            birthDate = u''
            diagnos_id = u''
            MKB = u''
            MKBEx = u''
            traumaType_id = u''
            setDate = u''
            endDate = u''
            recordBufferError = u''
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            client_id = forceString(record.value('client_id'))
            diagnos_id = forceString(record.value('id'))
            MKB = forceString(record.value('MKB'))
            MKBEx = forceString(record.value('MKBEx'))
            character_id = forceString(record.value('character_id'))
            traumaType_id = forceString(record.value('name'))
            setDate = forceString(forceDate(record.value('setDate')))
            endDate = forceString(forceDate(record.value('endDate')))
            recordBufferError = recordError
            strCharacter = u''
            if character_id == u'1':
                strCharacter = u' Заболевание острое. '
            if character_id == u'2':
                strCharacter = u' Заболевание хроническое впервые установленное. '
            if character_id == u'3':
                strCharacter = u' Заболевание хроническое известное. '
            if character_id == u'4':
                strCharacter = u' Обострение хронического заболевания. '
            resultStr = u''
            resultStr = u' Клиент: ' + client_id + u'(' + lastName + ' ' + firstName + ' ' + patrName + u' ,' + birthDate + u')'
            if MKB != u'':
                resultStr += u'  MKB: ' + MKB
            if MKBEx != u'':
                resultStr += u'  MKBEx: ' + MKBEx
            if traumaType_id != u'':
                resultStr += u'  тип травмы: ' + traumaType_id
            if  setDate != u'':
                resultStr += u'  Начальная дата: ' + setDate
            if  endDate != u'':
                resultStr += u'  Конечная дата: ' + endDate
            resultStr += recordBufferError + strCharacter
        return resultStr
    def createCharacterLine(self, characterId):
        strCharacter = u''
        if characterId == u'1':
            strCharacter = u' Заболевание острое. '
        elif characterId == u'2':
            strCharacter = u' Заболевание хроническое впервые установленное. '
        elif characterId == u'3':
            strCharacter = u' Заболевание хроническое известное. '
        elif characterId == u'4':
            strCharacter = u' Обострение хронического заболевания. '
        return strCharacter


    def assembleLine(self, resSelect = None, row = -1):
        self.diagnosisId = None
        self.diagnosticId = None
        self.diagnosisId = forceRef(resSelect.value('id'))
        strCharacter = self.createCharacterLine(forceString(resSelect.value('character_id')))
        self.recSelectCorrect = u''
        self.recSelectClient = u''
        self.recSelectClient = u'Клиент: ' + forceString(resSelect.value('client_id')) + u'(' + forceString(resSelect.value('lastName')) + u' ' + forceString(resSelect.value('firstName')) + u' ' + forceString(resSelect.value('patrName')) + u' ,' + forceString(resSelect.value('birthDate')) + u')'
        self.recSelectCorrect = u''
        eventMKB = forceString(resSelect.value('MKB'))
        eventMKBEx = forceString(resSelect.value('MKBEx'))
        eventTrauma = forceString(resSelect.value('name'))
        eventSetDate = forceString(forceDate(resSelect.value('setDate')))
        eventEndDate = forceString(forceDate(resSelect.value('endDate')))
        if eventMKB != u'':
            self.recSelectCorrect += u'  MKB: ' + eventMKB
        if eventMKBEx != u'':
            self.recSelectCorrect += u'  MKBEx: ' + eventMKBEx
        if eventTrauma != u'':
            self.recSelectCorrect += u'  Тип травмы: ' + eventTrauma
        if eventSetDate != u'':
            self.recSelectCorrect += u'  Начальная дата: ' + eventSetDate
        if eventEndDate != u'':
            self.recSelectCorrect += u'  Конечная дата: ' + eventEndDate
        self.recSelectCorrect += self.recordBufferError[row] + strCharacter


    def viewMessageInsertDiagnosisEvent(self, resSelect = None, row = -1):
        if resSelect and row > -1:
            self.assembleLine(resSelect, row)
            self.diagnosticId = forceRef(resSelect.value('diagnostic_id'))
            db = QtGui.qApp.db
            tableDiagnosis = db.table('Diagnosis')
            record = db.getRecordEx(tableDiagnosis, 'Diagnosis.*', [tableDiagnosis['id'].eq(forceRef(resSelect.value('diagnosis_id'))), tableDiagnosis['deleted'].eq(0)])
            if record:
                eventMKB = forceString(record.value('MKB'))
                eventMKBEx = forceString(record.value('MKBEx'))
                eventTrauma = forceString(record.value('name'))
                eventSetDate = forceString(forceDate(record.value('setDate')))
                eventEndDate = forceString(forceDate(record.value('endDate')))
                self.recSelectCorrect += u'\nСуществующая запись в ЛУДе:\n'
                if eventMKB != u'':
                    self.recSelectCorrect += u'  MKB: ' + eventMKB
                if eventMKBEx != u'':
                    self.recSelectCorrect += u'  MKBEx: ' + eventMKBEx
                if eventTrauma != u'':
                    self.recSelectCorrect += u'  Тип травмы: ' + eventTrauma
                if eventSetDate != u'':
                    self.recSelectCorrect += u'  Начальная дата: ' + eventSetDate
                if eventEndDate != u'':
                    self.recSelectCorrect += u'  Конечная дата: ' + eventEndDate
                strCharacter = self.createCharacterLine(forceString(record.value('character_id')))
                self.recSelectCorrect += strCharacter


    def listWidgetItemEnabled(self, row = -1):
        if row > -1:
            listWidgetItem = self.listResultControlDiagnosisLocalLUD.item(row)
            if listWidgetItem:
                listWidgetItem.setFlags(QtCore.Qt.NoItemFlags)


    def controlIntegrity(self, clientId = None, MKBFrom = None, MKBTo = None):
        #Проверка целостности.
        if clientId:
            stmt = u'''SELECT Diagnosis.client_id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.id, Diagnosis.character_id, Diagnosis.traumaType_id, rbTraumaType.name, Diagnosis.setDate, Diagnosis.endDate,Client.lastName, Client.firstName, Client.patrName, Client.birthDate
    FROM Diagnosis LEFT JOIN Client ON Diagnosis.client_id = Client.id LEFT JOIN rbTraumaType ON Diagnosis.traumaType_id = rbTraumaType.id
    WHERE Diagnosis.client_id = %d
    AND (%s)
    AND (NOT EXISTS (SELECT  DS.id FROM Diagnosis AS DS WHERE DS.mod_id = Diagnosis.id)
    AND NOT EXISTS (SELECT  Diagnostic.id FROM Diagnostic WHERE Diagnostic.diagnosis_id = Diagnosis.id)
    AND NOT EXISTS (SELECT  TempInvalid.id FROM TempInvalid WHERE TempInvalid.diagnosis_id = Diagnosis.id)
    AND NOT EXISTS (SELECT  TempInvalid_Period.id FROM TempInvalid_Period WHERE TempInvalid_Period.diagnosis_id = Diagnosis.id))
    ORDER BY Diagnosis.client_id ASC, Diagnosis.MKB ASC''' % (clientId, 'Diagnosis.MKB >= \'%s\' AND Diagnosis.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'Diagnosis.MKB >= \'A\' AND Diagnosis.MKB < \'U\'')
            query = QtGui.qApp.db.query(stmt)
            while query.next():
                self.recordBufferClientId.append(query.record())
                self.recordBufferErrorClientId.append(u' Нет целостности. ')
                self.recordBufferCorrectClientId.append(1)
                self.recordBuffer.append(query.record())
                self.recordBufferError.append(u' Нет целостности. ')
                self.recordBufferCorrect.append(1)


    def controlCharacterChronicFirstDisease(self, clientId = None, MKBFrom = None, MKBTo = None):
        #Проверка даты начала хронического заболевания.
        stmtCharacterChronicDisease = None
        if clientId:
            stmtCharacterChronicDisease = u'''SELECT B.setDate, B.endDate, B.diagnosis_id, B.id, B.character_id, A.client_id, A.MKB, A.MKBEx, T.name, Client.lastName,Client.firstName,Client.patrName,Client.birthDate
    FROM Diagnosis AS A INNER JOIN Diagnostic AS B ON A.id = B.diagnosis_id
                        INNER JOIN Client ON A.client_id = Client.id
                        LEFT JOIN rbTraumaType AS T ON A.traumaType_id = T.id
    WHERE A.client_id = %d
          AND A.deleted = 0
          AND B.deleted = 0
          AND Client.deleted = 0
          AND (%s)
          AND (B.character_id = 2
          AND ((A.setDate != B.setDate OR (A.setDate IS NULL AND B.setDate != 0))
          AND B.setDate <= (SELECT MIN(B2.setDate)
                            FROM Diagnostic AS B2
                            WHERE B2.deleted = 0 AND B.deleted = 0 AND B2.diagnosis_id = B.diagnosis_id AND (B2.character_id = 3 OR B2.character_id = 4))))
    ORDER BY B.diagnosis_id ASC''' % (clientId, 'A.MKB >= \'%s\' AND A.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'A.MKB >= \'A\' AND A.MKB < \'U\'')
            if stmtCharacterChronicDisease:
                query = QtGui.qApp.db.query(stmtCharacterChronicDisease)
                while query.next():
                    self.recordBufferClientId.append(query.record())
                    self.recordBufferErrorClientId.append(u' Некорректная дата начала. ')
                    self.recordBufferCorrectClientId.append(6)
                    self.recordBuffer.append(query.record())
                    self.recordBufferError.append(u' Некорректная дата начала. ')
                    self.recordBufferCorrect.append(6)


    def controlCharacterChronicKnowDisease(self, clientId = None, MKBFrom = None, MKBTo = None):
        #Проверка характера хронического заболевания.
        stmtCharacterChronicKnowDisease = None
        if clientId:
            stmtCharacterChronicKnowDisease = u'''SELECT B.setDate, B.endDate, B.diagnosis_id, B.id, B.character_id,A.client_id, A.MKB, A.MKBEx, T.name, Client.lastName,Client.firstName,Client.patrName,Client.birthDate
    FROM Diagnosis AS A INNER JOIN Diagnostic AS B ON A.id = B.diagnosis_id
                        INNER JOIN Client ON A.client_id = Client.id
                        LEFT JOIN rbTraumaType AS T ON A.traumaType_id = T.id
    WHERE A.client_id = %d
          AND A.deleted = 0
          AND B.deleted = 0
          AND Client.deleted = 0
          AND (%s)
          AND (B.character_id = 2
          AND ((A.setDate != B.setDate OR (A.setDate IS NULL AND B.setDate != 0))
          AND B.setDate > (SELECT MIN(B2.setDate)
                           FROM Diagnostic AS B2
                           WHERE B2.deleted = 0 AND B.deleted = 0 AND B2.diagnosis_id = B.diagnosis_id AND (B2.character_id = 3 OR B2.character_id = 4))))
    ORDER BY B.diagnosis_id ASC''' % (clientId, 'A.MKB >= \'%s\' AND A.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'A.MKB >= \'A\' AND A.MKB < \'U\'')
            if stmtCharacterChronicKnowDisease:
                query = QtGui.qApp.db.query(stmtCharacterChronicKnowDisease)
                while query.next():
                    self.recordBufferClientId.append(query.record())
                    self.recordBufferErrorClientId.append(u' Некорректный характер хронического заболевания. ')
                    self.recordBufferCorrectClientId.append(8)
                    self.recordBuffer.append(query.record())
                    self.recordBufferError.append(u' Некорректный характер хронического заболевания. ')
                    self.recordBufferCorrect.append(8)


    def controlDiseaseDiagnostic(self, characterId = u'', clientId = None, MKBFrom = None, MKBTo = None):
        stmtDiagnosticSetDate = None
        if clientId:
            stmtDiagnosticSetDate = u'''SELECT MIN(Diagnostic.setDate) AS setDate, Diagnostic.endDate, Diagnostic.diagnosis_id, Diagnosis.id, Diagnostic.id AS diagnostic_id, Diagnosis.character_id, Diagnostic.character_id AS diagnosticCharacterId, Diagnosis.client_id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.traumaType_id, rbTraumaType.name, Client.lastName, Client.firstName, Client.patrName, Client.birthDate
    FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id AND (Diagnosis.setDate IS NOT NULL AND Diagnostic.setDate < Diagnosis.setDate) AND (%s)
    AND (Diagnosis.character_id = \'%s\')
    INNER JOIN Client ON Diagnosis.client_id = Client.id
    LEFT JOIN rbTraumaType ON Diagnosis.traumaType_id = rbTraumaType.id
    WHERE Diagnosis.deleted = 0 AND Diagnostic.deleted = 0 AND Client.deleted = 0 AND Diagnosis.client_id = %d
    GROUP BY Diagnosis.id
    ORDER BY Diagnosis.client_id ASC, Diagnosis.MKB ASC''' % ('Diagnosis.MKB >= \'%s\' AND Diagnosis.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'Diagnosis.MKB >= \'A\' AND Diagnosis.MKB < \'U\'', characterId, clientId)
            if stmtDiagnosticSetDate:
                queryDiagnosticSetDate = QtGui.qApp.db.query(stmtDiagnosticSetDate)
                while queryDiagnosticSetDate.next():
                    self.recordBufferClientId.append(queryDiagnosticSetDate.record())
                    self.recordBufferErrorClientId.append(u' Минимальная дата начала. ')
                    self.recordBufferCorrectClientId.append(5)
                    self.recordBuffer.append(queryDiagnosticSetDate.record())
                    self.recordBufferError.append(u' Минимальная дата начала. ')
                    self.recordBufferCorrect.append(5)

            stmtDiagnosticMinEndDate = None
            stmtDiagnosticMinEndDate = u'''SELECT Diagnostic.setDate, MIN(Diagnostic.endDate) AS endDate, Diagnostic.diagnosis_id, Diagnosis.id, Diagnostic.id AS diagnostic_id, Diagnosis.character_id, Diagnosis.client_id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.traumaType_id, rbTraumaType.name, Client.lastName, Client.firstName, Client.patrName, Client.birthDate
    FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id AND (Diagnostic.endDate IS NOT NULL AND Diagnostic.endDate < Diagnosis.endDate AND Diagnostic.endDate < Diagnostic.setDate) AND (%s) AND (Diagnosis.character_id = \'%s\')
    INNER JOIN Client ON Diagnosis.client_id = Client.id
    LEFT JOIN rbTraumaType ON Diagnosis.traumaType_id = rbTraumaType.id
    WHERE Diagnosis.deleted = 0 AND Diagnostic.deleted = 0 AND Client.deleted = 0 AND Diagnosis.client_id = %d
    GROUP BY Diagnosis.id
    ORDER BY Diagnosis.client_id ASC, Diagnosis.MKB ASC''' % ('Diagnosis.MKB >= \'%s\' AND Diagnosis.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'Diagnosis.MKB >= \'A\' AND Diagnosis.MKB < \'U\'', characterId, clientId)
            if stmtDiagnosticMinEndDate:
                queryDiagnosticMinEndDate = QtGui.qApp.db.query(stmtDiagnosticMinEndDate)
                while queryDiagnosticMinEndDate.next():
                    self.recordBufferClientId.append(queryDiagnosticMinEndDate.record())
                    self.recordBufferErrorClientId.append(u' Минимальная дата окончания. ')
                    self.recordBufferCorrectClientId.append(9)
                    self.recordBuffer.append(queryDiagnosticMinEndDate.record())
                    self.recordBufferError.append(u' Минимальная дата окончания. ')
                    self.recordBufferCorrect.append(9)

            stmtDiagnosticMaxEndDate = None
            stmtDiagnosticMaxEndDate = u'''SELECT Diagnostic.setDate, MAX(Diagnostic.endDate) AS endDate, Diagnostic.diagnosis_id, Diagnosis.id, Diagnostic.id AS diagnostic_id, Diagnosis.character_id, Diagnostic.character_id AS diagnosticCharacterId, Diagnosis.client_id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnosis.traumaType_id, rbTraumaType.name, Client.lastName, Client.firstName, Client.patrName, Client.birthDate
    FROM Diagnosis INNER JOIN Diagnostic ON Diagnostic.diagnosis_id = Diagnosis.id AND (Diagnostic.endDate IS NOT NULL AND Diagnostic.endDate > Diagnosis.endDate) AND (%s)
    AND (Diagnosis.character_id = \'%s\')
    INNER JOIN Client ON Diagnosis.client_id = Client.id
    LEFT JOIN rbTraumaType ON Diagnosis.traumaType_id = rbTraumaType.id
    WHERE Diagnosis.deleted = 0 AND Diagnostic.deleted = 0 AND Client.deleted = 0 AND Diagnosis.client_id = %d
    GROUP BY Diagnosis.id
    ORDER BY Diagnosis.client_id ASC, Diagnosis.MKB ASC''' % ('Diagnosis.MKB >= \'%s\' AND Diagnosis.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'Diagnosis.MKB >= \'A\' AND Diagnosis.MKB < \'U\'', characterId, clientId)
            if stmtDiagnosticMaxEndDate:
                queryDiagnosticMaxEndDate = QtGui.qApp.db.query(stmtDiagnosticMaxEndDate)
                while queryDiagnosticMaxEndDate.next():
                    self.recordBufferClientId.append(queryDiagnosticMaxEndDate.record())
                    self.recordBufferErrorClientId.append(u' Максимальная дата окончания. ')
                    self.recordBufferCorrectClientId.append(5)
                    self.recordBuffer.append(queryDiagnosticMaxEndDate.record())
                    self.recordBufferError.append(u' Максимальная дата окончания. ')
                    self.recordBufferCorrect.append(5)


    def controlCodingTraumaType(self, clientId = None):
        #Проверка несоответствия типа травмы.
        stmtDiagnosticTraumaType = None
        if clientId:
            stmtDiagnosticTraumaType = u'''SELECT Diagnosis.client_id, Diagnosis.MKB, Diagnosis.MKBEx, Diagnostic.diagnosis_id, Diagnostic.id, Diagnosis.character_id, Diagnostic.traumaType_id, rbTraumaType.name, Diagnostic.event_id, Diagnostic.setDate, Diagnostic.endDate, Client.lastName, Client.firstName, Client.patrName, Client.birthDate
    FROM Diagnostic INNER JOIN Diagnosis ON Diagnostic.diagnosis_id = Diagnosis.id INNER JOIN Client ON Diagnosis.client_id = Client.id INNER JOIN Event ON Diagnostic.event_id = Event.id LEFT JOIN rbTraumaType ON Diagnostic.traumaType_id = rbTraumaType.id
    WHERE Diagnosis.client_id = %d AND Diagnosis.traumaType_id IS NOT NULL AND Diagnosis.traumaType_id != Diagnostic.traumaType_id AND Diagnosis.deleted = 0 AND Diagnostic.deleted = 0 AND Client.deleted = 0
    GROUP BY Diagnostic.id
    ORDER BY Diagnosis.client_id ASC, Diagnosis.MKB ASC''' % (clientId)
            if stmtDiagnosticTraumaType:
                queryDiagnosticTraumaType = QtGui.qApp.db.query(stmtDiagnosticTraumaType)
                while queryDiagnosticTraumaType.next():
                    self.recordBufferClientId.append(queryDiagnosticTraumaType.record())
                    self.recordBufferErrorClientId.append(u' Несоответствие типа травмы. ')
                    self.recordBufferCorrectClientId.append(4)
                    self.recordBuffer.append(queryDiagnosticTraumaType.record())
                    self.recordBufferError.append(u' Несоответствие типа травмы. ')
                    self.recordBufferCorrect.append(4)


    def controlDiseaseLUD(self, clientId = None, MKBFrom = None, MKBTo = None):
        if clientId and (self.Chronical or self.Acute):
            if self.duration == 0:
                self.duration = QtGui.qApp.averageDuration()
            self.checkRun = True
            self.controlIntegrity(clientId, MKBFrom, MKBTo) # 1
            db = QtGui.qApp.db
            self.controlCodingTraumaType(clientId)  # 4
            stmt = u'''SELECT D1.client_id, D1.MKB, D1.MKBEx, D1.id, D1.character_id, D1.setDate, D1.traumaType_id, T.name, D1.endDate, C.lastName, C.firstName, C.patrName, C.birthDate
                        FROM Diagnosis AS D1 LEFT JOIN Client AS C ON D1.client_id = C.id LEFT JOIN rbTraumaType AS T ON D1.traumaType_id = T.id, Diagnosis AS D2
                        WHERE D1.client_id = %d AND
                        D1.deleted = 0 AND
                        C.deleted = 0 AND
                        D2.deleted = 0 AND
                        D1.id != D2.id AND
                        D1.client_id = D2.client_id AND
                        (D1.MKB = D2.MKB AND
                        %s) AND

                        (D1.character_id IS NOT NULL AND

                        ('''% (clientId, 'D1.MKB >= \'%s\' AND D1.MKB <= \'%s\''%(MKBFrom, MKBTo) if MKBFrom and MKBTo else 'D1.MKB >= \'A\' AND D1.MKB < \'U\'')#D1.MKB >= 'A' AND D1.MKB < 'U'
            if self.Chronical:
                #хронические заболевания
                self.controlCharacterChronicFirstDisease(clientId, MKBFrom, MKBTo) # 6
                self.controlCharacterChronicKnowDisease(clientId, MKBFrom, MKBTo)  # 8
                self.controlDiseaseDiagnostic(u'2', clientId, MKBFrom, MKBTo)      # 5, 9
                stmt += u'''(D1.character_id = D2.character_id AND (D1.character_id = 3 AND ((D1.endDate <= D2.endDate) OR ((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND (D1.setDate >= D2.setDate)) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NOT NULL AND D2.setDate IS NULL AND D1.setDate != 0)))))'''

            else:
                if self.Acute:
                    #острые заболевания
                    self.controlDiseaseDiagnostic(u'1', clientId, MKBFrom, MKBTo) # 5, 9
                    stmt += u'''(D1.character_id = D2.character_id AND
                    (
                    D1.character_id = 1 AND
                    (
                    (D1.endDate <= D2.endDate AND ((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND (D1.setDate >= D2.setDate)) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NOT NULL AND D2.setDate IS NULL AND D1.setDate != 0)))
                    OR ((D1.endDate <= D2.endDate AND ((D2.setDate IS NOT NULL AND D1.endDate >= D2.setDate) OR (D2.setDate IS NULL AND D1.endDate >= 0))) AND ((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND D1.setDate <= D2.setDate) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NULL AND D2.setDate IS NOT NULL AND D2.setDate != 0)))
                    OR (D1.endDate >= D2.endDate AND (((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND (D1.setDate >= D2.setDate)) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NOT NULL AND D2.setDate IS NULL AND D1.setDate != 0)) AND ((D1.setDate IS NOT NULL AND D1.setDate <= D2.endDate) OR D1.setDate IS NULL)))
                    )
                    OR ((D2.setDate IS NOT NULL AND ((D2.endDate > (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d))) > D2.setDate)
OR (D1.endDate < D2.endDate AND D2.endDate < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (D2.endDate - D1.endDate) < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
(SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB), %d))))

OR (D2.setDate IS NULL AND ((D2.endDate > (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0, ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)),
ADDDATE(D1.endDate, %d))) > 0)
OR (D1.endDate < D2.endDate AND D2.endDate < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (D2.endDate - D1.endDate) < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
(SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB), %d))))))
                    )
                    ))'''% (self.duration, self.duration, self.duration, self.duration, self.duration, self.duration, self.duration, self.duration)
            if (self.Chronical and self.Acute):
                #острые заболевания, если и хронические и острые заболевания
                self.controlDiseaseDiagnostic(u'1', clientId, MKBFrom, MKBTo) # 5, 9
                stmt += u''' OR (D1.character_id = D2.character_id AND
                    (
                    D1.character_id = 1 AND
                    (
                    (D1.endDate <= D2.endDate AND ((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND (D1.setDate >= D2.setDate)) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NOT NULL AND D2.setDate IS NULL AND D1.setDate != 0)))
                    OR ((D1.endDate <= D2.endDate AND ((D2.setDate IS NOT NULL AND D1.endDate >= D2.setDate) OR (D2.setDate IS NULL AND D1.endDate >= 0))) AND ((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND D1.setDate <= D2.setDate) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NULL AND D2.setDate IS NOT NULL AND D2.setDate != 0)))
                    OR (D1.endDate >= D2.endDate AND (((D1.setDate IS NOT NULL AND D2.setDate IS NOT NULL AND (D1.setDate >= D2.setDate)) OR (D1.setDate IS NULL AND D2.setDate IS NULL) OR (D1.setDate IS NOT NULL AND D2.setDate IS NULL AND D1.setDate != 0)) AND ((D1.setDate IS NOT NULL AND D1.setDate <= D2.endDate) OR D1.setDate IS NULL)))
                    )
                    OR ((D2.setDate IS NOT NULL AND ((D2.endDate > (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d))) > D2.setDate)
OR (D1.endDate < D2.endDate AND D2.endDate < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (D2.endDate - D1.endDate) < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
(SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB), %d))))

OR (D2.setDate IS NULL AND ((D2.endDate > (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0, ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)),
ADDDATE(D1.endDate, %d))) > 0)
OR (D1.endDate < D2.endDate AND D2.endDate < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
ADDDATE(D1.endDate, (SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB)), ADDDATE(D1.endDate, %d)))
AND (D2.endDate - D1.endDate) < (IF((SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB) != 0,
(SELECT MKB_Tree.duration FROM MKB_Tree WHERE MKB_Tree.DiagID = D1.MKB), %d))))))
                    )
                    ))'''% (self.duration, self.duration, self.duration, self.duration, self.duration, self.duration, self.duration, self.duration)

            stmt += u'''))
                    GROUP BY D1.id
                    ORDER BY D1.client_id ASC, D1.MKB ASC'''
            query = db.query(stmt)
            while query.next():
                self.recordBufferClientId.append(query.record())
                self.recordBufferErrorClientId.append(u' Проблема длительности периода. ')
                self.recordBufferCorrectClientId.append(7)                           # 7
                self.recordBuffer.append(query.record())
                self.recordBufferError.append(u' Проблема длительности периода. ')
                self.recordBufferCorrect.append(7)                           # 7


    def loadDataDiagnosis(self):
        self.listResultControlDiagnosisLocalLUD.checkRunListWidget = False
        self.listResultControlDiagnosisLocalLUD.selectAll()
        self.listResultControlDiagnosisLocalLUD.clear()
        self.rows = 0
        self.lblCountLineLocalLUD.setText(u'всего строк: 0')
        self.btnCorrectControlLocalLUD.setEnabled(False)
        self.prbControlDiagnosisLocalLUD.setFormat('%v')
        self.prbControlDiagnosisLocalLUD.setValue(0)
        self.btnEndControlLocalLUD.setText(u'прервать')
        self.btnStartControlLocalLUD.setEnabled(False)
        lenStr = 0
        stmt = u''
        try:
            if self.chkMKB.isChecked():
                MKBFrom = normalizeMKB(self.edtMKBFrom.text())
                MKBTo = normalizeMKB(self.edtMKBTo.text())
            else:
                MKBFrom = None
                MKBTo = None
            QtGui.qApp.callWithWaitCursor(self, self.controlDiseaseLUD, self.clientId, MKBFrom, MKBTo)
            self.lblCountLineLocalLUD.setText(u'всего строк: %d' % len(self.recordBuffer))
            lenStr = self.selectDataDiagnosis(self.recordBuffer)
        except Exception, e:
            self.abortProcess = True
        if self.abortProcess:
            self.listResultControlDiagnosisLocalLUD.reset()
            self.lblCountLineLocalLUD.setText(u'всего строк: %d' % self.listResultControlDiagnosisLocalLUD.count())
        self.prbControlDiagnosisLocalLUD.setText(u'прервано' if self.abortProcess else u'готово')
        self.btnEndControlLocalLUD.setText(u'закрыть')
        if lenStr > 0:
           self.btnCorrectControlLocalLUD.setEnabled(True)
        self.btnStartControlLocalLUD.setEnabled(True)
        self.checkRun = False
        self.abortProcess = False
        self.listResultControlDiagnosisLocalLUD.recordBufferCorrectLW = self.recordBufferCorrect
        self.listResultControlDiagnosisLocalLUD.checkRunListWidget = True


    def printDataDiagnosis(self, valStr):
        self.listResultControlDiagnosisLocalLUD.addItem(self.errorStr + valStr)
        item = self.listResultControlDiagnosisLocalLUD.item(self.rows)
        self.listResultControlDiagnosisLocalLUD.scrollToItem(item)
        self.rows += 1


    def selectDataDiagnosis(self, records):
        prbControlPercent = 0
        lenStr = len(records)
        if lenStr > 1:
            self.prbControlDiagnosisLocalLUD.setMaximum(lenStr - 1)
        i = 0
        for record in records:
            QtGui.qApp.processEvents()
            if self.abortProcess:
                self.checkRun = False
                break
            self.prbControlDiagnosisLocalLUD.setValue(prbControlPercent)
            prbControlPercent += 1
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            client_id = forceString(record.value('client_id'))
            diagnos_id = forceString(record.value('id'))
            MKB = forceString(record.value('MKB'))
            MKBEx = forceString(record.value('MKBEx'))
            character_id = forceString(record.value('character_id'))
            traumaType_id = forceString(record.value('name'))
            setDate = forceString(forceDate(record.value('setDate')))
            endDate = forceString(forceDate(record.value('endDate')))
            self.createStrDiagnosis(character_id, client_id, lastName, firstName, patrName, birthDate, diagnos_id, MKB, MKBEx, traumaType_id, setDate, endDate, self.recordBufferError[i])
            i += 1
        return lenStr


    def createStrDiagnosis(self, character_id = u'', client_id = u'', lastName = u'', firstName = u'', patrName = u'', birthDate = u'', diagnos_id = u'', MKB = u'', MKBEx = u'', traumaType_id = u'', setDate = u'', endDate = u'', recordBufferError = u''):
        strCharacter = u''
        if character_id == u'1':
            strCharacter = u' Заболевание острое. '
        if character_id == u'2':
            strCharacter = u' Заболевание хроническое впервые установленное. '
        if character_id == u'3':
            strCharacter = u' Заболевание хроническое известное. '
        if character_id == u'4':
            strCharacter = u' Обострение хронического заболевания. '
        resultStr = u''
        resultStr = u' Клиент: ' + client_id + u'(' + lastName + ' ' + firstName + ' ' + patrName + u' ,' + birthDate + u')'
        if MKB != u'':
            resultStr += u'  MKB: ' + MKB
        if MKBEx != u'':
            resultStr += u'  MKBEx: ' + MKBEx
        if traumaType_id != u'':
            resultStr += u'  тип травмы: ' + traumaType_id
        if  setDate != u'':
            resultStr += u'  Начальная дата: ' + setDate
        if  endDate != u'':
            resultStr += u'  Конечная дата: ' + endDate
        resultStr += recordBufferError + strCharacter
        self.printDataDiagnosis(resultStr)
